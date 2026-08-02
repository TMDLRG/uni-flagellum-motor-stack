"""Mark-field validation and preparation (D6).

The mark channel is {nextStateN, direction, jump}. Two constraints make naive use unsafe:

D6_INGEST_NEXTSTATE_NOT_RANGE_CHECKED
    2 events record nextStateN = -1 (physically impossible). The ingest range-checks the dwell's
    own state but writes next_state through unchecked. The frozen dataset is NOT edited; this
    module forces an explicit decision instead of a silent drop.

OPEN ALPHABET
    15.1% of training and 16.7% of holdout marks point OUTSIDE the modelled state set {1..8}, so
    the process is not a closed Markov chain on the cohort. A mark-bearing likelihood is a
    one-step-ahead conditional, NOT a trajectory likelihood.

D5 REMINDER: the holdout mark channel is BURNED. Anything built on it is
RETROSPECTIVE_EXPLORATORY_ON_THIS_DATASET and can never be labelled PROSPECTIVE.
"""
from __future__ import annotations

PHYSICAL_MIN_STATORS = 0
PHYSICAL_MAX_STATORS = 11

VALID_POLICIES = ("strict", "quarantine", "retain_labelled")


class ImpossibleMarkError(ValueError):
    """Raised when physically impossible marks are present and policy='strict'."""


class OpenMarkAlphabetError(ValueError):
    """Raised when a closed-alphabet assumption is asserted but marks leave the state set."""


def flag_impossible_marks(events, min_state=PHYSICAL_MIN_STATORS, max_state=PHYSICAL_MAX_STATORS):
    """Return records for every event whose mark points at a physically impossible state."""
    out = []
    for e in events:
        ns = e.get("nextStateN")
        if ns is None:
            continue  # right-censored: no mark by construction
        if ns < min_state:
            reason = "NEXT_STATE_BELOW_PHYSICAL_MINIMUM"
        elif ns > max_state:
            reason = "NEXT_STATE_ABOVE_PHYSICAL_MAXIMUM"
        else:
            continue
        out.append({
            "eventId": e["eventId"],
            "motorId": e.get("motorId"),
            "stateN": e.get("stateN"),
            "nextStateN": ns,
            "jump": e.get("jump"),
            "partition": e.get("partition"),
            "reason": reason,
        })
    return out


def prepare_mark_dataset(events, policy="strict"):
    """Prepare events for mark modelling under an EXPLICIT impossible-mark policy.

    strict          -> raise ImpossibleMarkError (default; refuses to proceed silently)
    quarantine      -> (kept, quarantined) with quarantineReason on each quarantined event
    retain_labelled -> (kept, []) with rawDataDefect=True on the affected events

    There is deliberately no policy that drops them silently.
    """
    if policy not in VALID_POLICIES:
        raise ValueError("unknown policy %r; expected one of %r" % (policy, VALID_POLICIES))

    flagged = flag_impossible_marks(events)
    bad_ids = {f["eventId"]: f for f in flagged}

    if policy == "strict":
        if flagged:
            raise ImpossibleMarkError(
                "%d event(s) carry physically impossible marks (D6): %s. Choose policy="
                "'quarantine' or 'retain_labelled' and record the choice in the artifact."
                % (len(flagged), sorted(bad_ids)))
        return list(events), []

    if policy == "quarantine":
        kept, quarantined = [], []
        for e in events:
            if e["eventId"] in bad_ids:
                e2 = dict(e)
                e2["quarantineReason"] = bad_ids[e["eventId"]]["reason"]
                e2["quarantineDefect"] = "D6_INGEST_NEXTSTATE_NOT_RANGE_CHECKED"
                quarantined.append(e2)
            else:
                kept.append(e)
        return kept, quarantined

    kept = []
    for e in events:
        e2 = dict(e)
        if e["eventId"] in bad_ids:
            e2["rawDataDefect"] = "D6_INGEST_NEXTSTATE_NOT_RANGE_CHECKED"
            e2["rawDataDefectReason"] = bad_ids[e["eventId"]]["reason"]
        kept.append(e2)
    return kept, []


def mark_alphabet_escape(events, states=tuple(range(1, 9)), partition=None):
    """Count marks that leave the modelled state set."""
    sset = set(states)
    rows = [e for e in events
            if (not e.get("rightCensored"))
            and e.get("stateN") in sset
            and (partition is None or e.get("partition") == partition)]
    escaped = [e for e in rows if e.get("nextStateN") is not None and e["nextStateN"] not in sset]
    targets = {}
    for e in escaped:
        targets[e["nextStateN"]] = targets.get(e["nextStateN"], 0) + 1
    return {
        "n_events": len(rows),
        "n_escaped": len(escaped),
        "frac_escaped": (len(escaped) / len(rows)) if rows else None,
        "targets": dict(sorted(targets.items())),
    }


def assert_closed_alphabet(events, states=tuple(range(1, 9)), partition=None):
    """Refuse a closed-chain assumption when marks demonstrably leave the state set."""
    info = mark_alphabet_escape(events, states=states, partition=partition)
    if info["n_escaped"] > 0:
        raise OpenMarkAlphabetError(
            "%d/%d (%.1f%%) marks leave states %r (targets=%r). The process is NOT a closed "
            "Markov chain on this cohort; a mark-bearing likelihood here is a one-step-ahead "
            "conditional, not a trajectory likelihood."
            % (info["n_escaped"], info["n_events"], 100.0 * info["frac_escaped"],
               tuple(states), info["targets"]))
    return info
