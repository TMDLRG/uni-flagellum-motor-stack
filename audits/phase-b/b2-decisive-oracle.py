"""
DECISIVE Phase B test: is the committed two-timescale mixture globally fitted?

Method: calibrate an independent implementation until it reproduces the COMMITTED
held-out scores (which proves it computes the same quantity), then evaluate the
committed parameters and the independently-optimal parameters under that SAME
likelihood on the SAME event set. Whichever has lower training NLL wins.

Reads only data + protocol. Does not import repository model code.
"""
import json, math, hashlib
import numpy as np
from scipy.optimize import minimize
from scipy.special import gammaln

ROOT = "C:/Users/mpolz/Documents/UNI-Flagellum/UNI-FLAGELLUM"
events = json.load(open(f"{ROOT}/experiments/data/wadhwa-2022-events.json"))["events"]

COMMITTED = dict(w=0.6066448974609373, lf=5.239865393555934,
                 wb_shape=0.625088844276203, ln_sigma=1.5783076021679734)
COMMITTED_HELDOUT = dict(exponential=-3.259938023731547, weibull=-3.0962841768378104,
                         lognormal=-3.012890170946554, mixture=-3.0497565695441344)

# ---------- model log densities on normalized y, all mean-one ----------
def log_exp(y):
    return -y

def log_weibull(y, k):
    log_sw = -gammaln(1.0 + 1.0 / k)          # scale_w = 1/Gamma(1+1/k)
    z = np.log(y) - log_sw
    return np.log(k) - log_sw + (k - 1.0) * z - np.exp(k * z)

def log_lognormal(y, s):
    mu = -0.5 * s * s
    return -np.log(y * s * math.sqrt(2 * math.pi)) - (np.log(y) - mu) ** 2 / (2 * s * s)

def log_mixture(y, w, lf):
    denom = 1.0 - w / lf
    if denom <= 0:
        return np.full_like(y, -1e12)
    ls = (1.0 - w) / denom
    a = np.log(w) + np.log(lf) - lf * y
    b = np.log1p(-w) + np.log(ls) - ls * y
    m = np.maximum(a, b)
    return m + np.log(np.exp(a - m) + np.exp(b - m))

def build(eligible_only, scale_from_eligible_only):
    """Return (train_y, holdout_y, holdout_logscale) under one interpretation."""
    elig = set(range(1, 9))
    def keep(e):
        return (e["stateN"] in elig) if eligible_only else True
    tr = [e for e in events if e["partition"] == "train" and not e["rightCensored"]]
    ho = [e for e in events if e["partition"] == "holdout" and not e["rightCensored"]]
    # scale_N from TRAINING only
    src = [e for e in tr if (e["stateN"] in elig)] if scale_from_eligible_only else tr
    sums, cnts = {}, {}
    for e in src:
        sums[e["stateN"]] = sums.get(e["stateN"], 0.0) + e["durationS"]
        cnts[e["stateN"]] = cnts.get(e["stateN"], 0) + 1
    scale = {n: sums[n] / cnts[n] for n in sums}
    tr2 = [e for e in tr if keep(e) and e["stateN"] in scale]
    ho2 = [e for e in ho if keep(e) and e["stateN"] in scale]
    ty = np.array([e["durationS"] / scale[e["stateN"]] for e in tr2])
    hy = np.array([e["durationS"] / scale[e["stateN"]] for e in ho2])
    hls = np.array([math.log(scale[e["stateN"]]) for e in ho2])
    return ty, hy, hls, len(tr2), len(ho2)

def heldout_scores(hy, hls, k, s, w, lf):
    return dict(
        exponential=float(np.mean(log_exp(hy) - hls)),
        weibull=float(np.mean(log_weibull(hy, k) - hls)),
        lognormal=float(np.mean(log_lognormal(hy, s) - hls)),
        mixture=float(np.mean(log_mixture(hy, w, lf) - hls)),
    )

# ---------- find which interpretation reproduces the committed numbers ----------
print("=== CALIBRATION: which event-set interpretation reproduces the committed scores? ===")
best_interp, best_err = None, 1e9
for eo in (False, True):
    for se in (False, True):
        ty, hy, hls, ntr, nho = build(eo, se)
        sc = heldout_scores(hy, hls, COMMITTED["wb_shape"], COMMITTED["ln_sigma"],
                            COMMITTED["w"], COMMITTED["lf"])
        err = max(abs(sc[m] - COMMITTED_HELDOUT[m]) for m in sc)
        print(f"  eligible_only={eo!s:<5} scale_from_eligible={se!s:<5} "
              f"ntrain={ntr:<4} nhold={nho:<4} maxAbsErr_vs_committed={err:.3e}")
        if err < best_err:
            best_err, best_interp = err, (eo, se)
print(f"\n  BEST INTERPRETATION: eligible_only={best_interp[0]}, "
      f"scale_from_eligible={best_interp[1]}  (max abs err {best_err:.3e})")

ty, hy, hls, ntr, nho = build(*best_interp)
print(f"  train uncensored events used: {ntr}   holdout uncensored events used: {nho}")

# ---------- DECISIVE: committed vs independently-optimal, SAME likelihood ----------
def nll_mix(p):
    return -float(np.sum(log_mixture(ty, p[0], p[1])))

print("\n=== DECISIVE COMPARISON — same likelihood, same event set ===")
nll_committed = nll_mix([COMMITTED["w"], COMMITTED["lf"]])
print(f"  training NLL at COMMITTED (w={COMMITTED['w']}, lf={COMMITTED['lf']}):")
print(f"    {nll_committed!r}")

best = None
rng = np.random.default_rng(20260717)
starts = [(w, lf) for w in np.linspace(0.05, 0.95, 10) for lf in np.logspace(-1, 2.3, 10)]
starts += [(float(rng.uniform(0.02, 0.98)), float(np.exp(rng.uniform(-2, 5)))) for _ in range(200)]
for m in ("Nelder-Mead", "L-BFGS-B"):
    for s0 in starts:
        if 1.0 - s0[0] / s0[1] <= 0:
            continue
        try:
            r = minimize(nll_mix, s0, method=m,
                         bounds=[(1e-9, 1 - 1e-9), (1e-9, 1e4)] if m == "L-BFGS-B" else None,
                         options={"maxiter": 20000, "maxfev": 20000} if m == "Nelder-Mead" else {"maxiter": 20000})
        except Exception:
            continue
        if np.isfinite(r.fun) and 0 < r.x[0] < 1 and r.x[1] > r.x[0] and (best is None or r.fun < best[0]):
            best = (float(r.fun), float(r.x[0]), float(r.x[1]), m)

print(f"\n  training NLL at INDEPENDENT OPTIMUM (w={best[1]!r}, lf={best[2]!r}) via {best[3]}:")
print(f"    {best[0]!r}")

delta = nll_committed - best[0]
print(f"\n  DELTA (committed NLL - optimal NLL) = {delta!r} nats")
if delta > 1e-6:
    print(f"  VERDICT: the committed mixture is NOT at the optimum. It is {delta:.6f} nats WORSE.")
else:
    print(f"  VERDICT: the committed mixture IS at the optimum (within {abs(delta):.2e} nats).")

# ---------- does a better fit change the ranking? ----------
print("\n=== DOES THE BETTER FIT OVERTURN THE ADVERSE LOGNORMAL RESULT? ===")
sc_committed = heldout_scores(hy, hls, COMMITTED["wb_shape"], COMMITTED["ln_sigma"],
                              COMMITTED["w"], COMMITTED["lf"])
sc_better = heldout_scores(hy, hls, COMMITTED["wb_shape"], COMMITTED["ln_sigma"],
                           best[1], best[2])
print("  with COMMITTED mixture params:")
for k, v in sorted(sc_committed.items(), key=lambda kv: -kv[1]):
    print(f"    {k:<12} {v!r}")
print("  with BEST-FIT mixture params:")
for k, v in sorted(sc_better.items(), key=lambda kv: -kv[1]):
    print(f"    {k:<12} {v!r}")
print(f"\n  lognormal - mixture (committed fit): {sc_committed['lognormal'] - sc_committed['mixture']!r}")
print(f"  lognormal - mixture (best fit)     : {sc_better['lognormal'] - sc_better['mixture']!r}")
print("  ADVERSE RESULT SURVIVES" if sc_better["lognormal"] > sc_better["mixture"]
      else "  ADVERSE RESULT OVERTURNED — INTEGRITY FINDING")
