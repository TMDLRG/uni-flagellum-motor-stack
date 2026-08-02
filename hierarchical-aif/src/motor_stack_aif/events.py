"""Lmotor-0 observed blanket — typed event records.

Three modes enforce the D5/D6 quarantines at the type level rather than by convention:

  duration_only      : dwell + state + censor. The ONLY mode permitted to touch holdout.
  mark_retrospective : adds nextStateN/direction/jump. TRAIN-safe; on holdout it is
                       RETROSPECTIVE_EXPLORATORY_ON_THIS_DATASET (D5) and never prospective.
  mark_quarantine    : mark mode with D6-impossible marks removed via marks.prepare_mark_dataset.

`load_events(mode=...)` refuses to hand back holdout mark fields unless the caller explicitly
acknowledges the retrospective status. That is the D5 firewall expressed in code.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import _bridge

DURATION_ONLY = "duration_only"
MARK_RETROSPECTIVE = "mark_retrospective"
MARK_QUARANTINE = "mark_quarantine"
MODES = (DURATION_ONLY, MARK_RETROSPECTIVE, MARK_QUARANTINE)


class HoldoutMarkAccessError(RuntimeError):
    """Raised when holdout mark fields are requested without acknowledging D5."""


@dataclass(frozen=True)
class ObservedEvent:
    """One dwell observation. Mark fields are None unless a mark mode was requested."""
    event_id: str
    motor_id: str
    partition: str
    state_n: int
    duration_s: float
    right_censored: bool
    next_state_n: int | None = None
    direction: str | None = None
    jump: int | None = None
    meta: dict = field(default_factory=dict)

    @property
    def is_holdout(self) -> bool:
        return self.partition == "holdout"

    @property
    def has_mark(self) -> bool:
        return self.next_state_n is not None


def _to_event(raw: dict, with_mark: bool) -> ObservedEvent:
    return ObservedEvent(
        event_id=raw["eventId"],
        motor_id=raw["motorId"],
        partition=raw["partition"],
        state_n=raw["stateN"],
        duration_s=float(raw["durationS"]),
        right_censored=bool(raw["rightCensored"]),
        next_state_n=raw.get("nextStateN") if with_mark else None,
        direction=raw.get("direction") if with_mark else None,
        jump=raw.get("jump") if with_mark else None,
        meta={k: raw[k] for k in ("rawDataDefect", "quarantineReason") if k in raw},
    )


def load_events(mode: str = DURATION_ONLY, *,
                acknowledge_retrospective_holdout_marks: bool = False,
                states=None, partition=None) -> list[ObservedEvent]:
    """Load typed events under an explicit mode.

    Requesting mark fields on the holdout partition raises unless the caller passes
    acknowledge_retrospective_holdout_marks=True, which is a written acknowledgement that the
    resulting analysis is RETROSPECTIVE_EXPLORATORY_ON_THIS_DATASET (D5).
    """
    if mode not in MODES:
        raise ValueError("unknown mode %r; expected one of %r" % (mode, MODES))

    raw = _bridge.b3().load_events()

    if mode == MARK_QUARANTINE:
        from . import marks
        raw, _quarantined = marks.prepare_mark_dataset(raw, policy="quarantine")

    with_mark = mode in (MARK_RETROSPECTIVE, MARK_QUARANTINE)

    rows = raw
    if states is not None:
        sset = set(states)
        rows = [e for e in rows if e["stateN"] in sset]
    if partition is not None:
        rows = [e for e in rows if e["partition"] == partition]

    if with_mark and any(e["partition"] == "holdout" for e in rows) \
            and not acknowledge_retrospective_holdout_marks:
        raise HoldoutMarkAccessError(
            "Refusing to return holdout mark fields. The holdout nextStateN/jump channel was "
            "burned on 2026-07-21 (D5); any analysis using it is RETROSPECTIVE_EXPLORATORY_ON_"
            "THIS_DATASET and can never be PROSPECTIVE. Pass "
            "acknowledge_retrospective_holdout_marks=True to proceed, or restrict to "
            "partition='train', or use mode='duration_only'.")

    return [_to_event(e, with_mark) for e in rows]


def split_by_motor(events) -> dict:
    """Group events by motor - the experimental unit. Never group by event."""
    out: dict[str, list[ObservedEvent]] = {}
    for e in events:
        out.setdefault(e.motor_id, []).append(e)
    return out
