# SPDX-License-Identifier: Apache-2.0
"""Worst-case timing chain: VBUS connection -> hold-off -> stable CC reading -> step raised (SW-005, SW-009, SYS-020).

Interval arithmetic: every stage is (min, max) in ms. Labels in STAGES say where a number comes from:
spec (requirement text), read (datasheet evidence report), derived (other script), ASSUMED (no source; owner or
bench must supply). Nothing here was measured. Run: python3 -I sw005_holdoff_timing.py
"""
import math

SYS020_LIMIT_MS = 1000.0     # SYS-020: limit set within [1] s of connection
W_SPEC = (200.0, 600.0)      # HW-010 hold-off window (spec)
W_BUILT = (210.3, 576.0)     # analysis-n4 set 220+220+150+33 nF C0G 5 % (derived, holdoff_cap.py)
K_RATIO = 875.6 / 357.6      # TPS3840 tD max/min from RCT and the ln constants (datasheet-evidence-supervisor A6)


def add(*xs):
    return (sum(x[0] for x in xs), sum(x[1] for x in xs))


def stable_window_ms(n_reads, window_ms, period_ms):
    """Time from the first valid read to the decision: 'n consecutive reads over at least window' needs
    max(n-1, ceil(window/period)) read intervals. period_ms is the (maximum) read period."""
    return max(n_reads - 1, math.ceil(window_ms / period_ms)) * period_ms


def reads_needed(n_reads, window_ms, period_ms):
    return max(n_reads - 1, math.ceil(window_ms / period_ms)) + 1


def raise_time(holdoff, period_ms=100.0, n_reads=5, window_ms=500.0, boot=(100.0, 500.0),
               vbus_ramp=(0.0, 10.0), t_strt=(0.1, 0.35), gpio=(0.0, 10.0), ilim_settle=(0.0, 2.0)):
    """Time from connection to the raised step when the count starts at the HOLD_OK_RB rising edge (M2 rule).
    Returns (min, max) in ms. The count cannot start before the firmware runs (boot) either."""
    gate_open = add(vbus_ramp, t_strt, holdoff)
    first_valid = (max(gate_open[0], boot[0]), max(gate_open[1], boot[1]))
    phase = (0.0, period_ms)                      # first read after the edge is 0..period later
    win = stable_window_ms(n_reads, window_ms, period_ms)
    return add(first_valid, phase, (win, win), gpio, ilim_settle)


def max_holdoff_for_budget(budget=SYS020_LIMIT_MS, **kw):
    """Largest hold-off maximum (ms) that keeps the worst case at or below budget."""
    kw.setdefault("boot", (0.0, 0.0))     # boot overlaps the hold-off; it only matters if it is longer
    base = raise_time((0.0, 0.0), **kw)[1]
    return budget - base


def window_for_budget(holdoff_max, budget=SYS020_LIMIT_MS, period_ms=100.0):
    """Longest stable window (ms, multiples of period) that fits when the hold-off maximum is holdoff_max."""
    w = 0.0
    while raise_time((0.0, holdoff_max), period_ms=period_ms, n_reads=2, window_ms=w + period_ms)[1] <= budget:
        w += period_ms
    return w


def min_max_for_min(t_min_ms, tol=0.053):
    """Smallest hold-off maximum (ms) that a TPS3840 with C0G tolerance tol can give for a given minimum."""
    return t_min_ms * K_RATIO * (1 + tol) / (1 - tol)


def rail_holdup_ms(c_uf, i_load_a, i_limit_a, v0=5.0, vmin=4.5):
    """Time the bulk capacitance carries the deficit before the rail falls from v0 to vmin (constant-current limit,
    constant-current load; a buck is a constant-power load, so this is optimistic)."""
    return 1e3 * (c_uf * 1e-6) * (v0 - vmin) / (i_load_a - i_limit_a)


def min_cap_uf(t_ms, i_load_a, i_limit_a, v0=5.0, vmin=4.5):
    return 1e6 * (i_load_a - i_limit_a) * t_ms * 1e-3 / (v0 - vmin)


def report():
    for name, w in (("spec 200-600", W_SPEC), ("built 210-576", W_BUILT)):
        for p in (100.0, 125.0):
            lo, hi = raise_time(w, period_ms=p)
            print(f"{name:14s} period {p:5.0f} ms reads {reads_needed(5, 500, p)}: raised {lo:7.1f} to {hi:7.1f} ms "
                  f"({'fits' if hi <= SYS020_LIMIT_MS else 'EXCEEDS'} 1000 ms)")
    print(f"max hold-off maximum for 1 s at period 100: {max_holdoff_for_budget():.1f} ms")
    print(f"max stable window for 1 s with hold-off max 600: {window_for_budget(600.0):.0f} ms")
    print(f"hold-off max for min 200 ms (TPS3840, 5 %): {min_max_for_min(200):.0f} ms")
    for c in (47.0, 100.0):
        print(f"rail hold-up C={c:5.0f} uF, 1350 mA vs 623 mA: {rail_holdup_ms(c, 1.35, 0.623):7.4f} ms")
    print(f"C for 50 ms: {min_cap_uf(50, 1.35, 0.623):.0f} uF (= {min_cap_uf(50, 1.35, 0.623)/1e3:.1f} mF)")


if __name__ == "__main__":
    report()
