# SPDX-License-Identifier: Apache-2.0
"""TPS2553 (U7) current-limit steps: worst case over resistor tolerance, MOSFET Rds(on) and off-leakage.

Traces to HW-010, SYS-020, ADR-0010 (E1-E4, open points 1-2), ADR-0016. Deterministic, no inputs.
Usage: python3 ilim_steps.py   (prints the table; exit 1 if a requirement check fails)

Source labels: [DS] TPS2553 datasheet SLVS841G eq. (1)-(3), recommended RILIM 15..232 kohm;
[ADR] ADR-0010; [HW] HW-010; [ASSUME] assumption, not read from a source in this repository.
"""
import sys

# ---- [DS] limit equations, mA, R in kohm. They include temperature and process, not the resistor tolerance.
def ios_max(r_k): return 22980.0 / r_k ** 0.94
def ios_nom(r_k): return 23950.0 / r_k ** 0.977
def ios_min(r_k): return 25230.0 / r_k ** 1.016

R_MIN_K, R_MAX_K = 15.0, 232.0          # [DS] recommended range for the total RILIM

# ---- [HW]/[ADR] requirement numbers
STEP1_MAX_MA = 623.0                     # [HW] HW-010: at most 623 mA at step 1
STEP1_MIN_MA = 500.0                     # [ADR] ADR-0010 table: "min at or above 500 mA"; HW-010 says [500] mA start value
STEP3_MIN_MA = 1366.0                    # [HW] HW-010 top step lower bound
STEP3_MAX_MA = 1577.0                    # [HW] HW-010 top step upper bound
STEP2_NOM_TARGET_MA = 1000.0             # [ASSUME] ADR-0010 gives "for a 1.0 A class value", no requirement states it
STEP2_BAND_MA = (850.0, 1150.0)          # [ASSUME] window used only to flag the middle step; the owner sets it
TOL_1PCT, TOL_01PCT = 0.01, 0.001        # resistor tolerance, initial; temperature coefficient not modelled [ASSUME]

# ---- 2N7002 (Q2, Q3), all [ASSUME]: no 2N7002 datasheet is stored in the repository
RDS_ON_MAX_OHM = 15.0                    # [ASSUME] conservative at Vgs 3.3 V (usual datasheet value 7.5 ohm max at Vgs 5 V)
RDS_ON_MIN_OHM = 0.0                     # [ASSUME] worst case for the maximum current
I_LEAK_A = 1e-6                          # [ASSUME] IDSS max 1 uA at 25 C (Vds 60 V, Vgs 0) as commonly listed; far above the true value at Vds ~1 V
I_LEAK_HOT_A = 10e-6                     # [ASSUME] sensitivity case, hot, not a datasheet number
# ---- TMUX1101 (U14, U15; owner decision 2026-11-05 (a)), [DS] SCDS410D tab. 6.6 (VDD 3.3 V +-10 %), -40 to +85 degC
TMUX_RDS_ON_MAX_OHM = 9.5                # [DS] ron max at 85 degC, ISD 10 mA (8.8 ohm at 25 degC)
TMUX_LEAK_A = 0.2e-9                     # [DS] IS(OFF), ID(OFF) max to 85 degC, VD 3 V / VS 1 V and swapped (2 V across the open switch)
V_ILIM_V = 1.0                           # [ASSUME] ILIM regulation voltage: not stated in the SLVS841G text read; sensitivity 0.8 .. 1.2 V

E96 = [100, 102, 105, 107, 110, 113, 115, 118, 121, 124, 127, 130, 133, 137, 140, 143, 147, 150, 154, 158, 162,
       165, 169, 174, 178, 182, 187, 191, 196, 200, 205, 210, 215, 221, 226, 232, 237, 243, 249, 255, 261, 267,
       274, 280, 287, 294, 301, 309, 316, 324, 332, 340, 348, 357, 365, 374, 383, 392, 402, 412, 422, 432, 442,
       453, 464, 475, 487, 499, 511, 523, 536, 549, 562, 576, 590, 604, 619, 634, 649, 665, 681, 698, 715, 732,
       750, 768, 787, 806, 825, 845, 866, 887, 909, 931, 953, 976]



def _series(mantissas, lo, hi):
    out = []
    for dec in (1.0, 10.0, 100.0):
        for m in mantissas:
            v = round(m * dec, 3)
            if lo <= v <= hi:
                out.append(v)
    return out


E96_M = [m / 100.0 for m in E96]
# E192 by the IEC 60063 rule 10^(i/192) rounded to 3 digits; the values chosen in this report (4.70, 2.77, 4.75) are in the standard table.
E192_M = sorted({round(10 ** (i / 192.0), 2) for i in range(192)})


def e96(lo, hi): return _series(E96_M, lo, hi)
def e192(lo, hi): return _series(E192_M, lo, hi)


def r_total_k(r1_k, tol, branch_k=(), rds=RDS_ON_MAX_OHM, sign=+1):
    """Total resistance ILIM-GND in kohm. sign +1: all resistors high (min current), -1: low (max current)."""
    g = 1.0 / (r1_k * (1 + sign * tol))
    for rk in branch_k:
        g += 1.0 / (rk * (1 + sign * tol) + rds / 1e3)
    return 1.0 / g


def limits(r1_k, tol, branches=(), n_off=0, leak_a=I_LEAK_A, v_ilim=V_ILIM_V, rds_max=RDS_ON_MAX_OHM):
    """(min, nom, max, (R_hi, R_nom, R_lo_eff)) in mA / kohm.
    branches: kohm values of the branches switched ON (each with its series Rds). n_off: off MOSFETs that leak.
    Leakage is a current sink from ILIM to GND of leak_a at v_ilim, which only raises the limit."""
    r_hi = r_total_k(r1_k, tol, branches, rds_max, +1)
    r_lo = r_total_k(r1_k, tol, branches, RDS_ON_MIN_OHM, -1)
    r_nom = r_total_k(r1_k, 0.0, branches, 0.5 * rds_max, +1)
    g_lo = 1.0 / (r_lo * 1e3) + n_off * leak_a / v_ilim
    r_lo_eff = 1e-3 / g_lo
    return ios_min(r_hi), ios_nom(r_nom), ios_max(r_lo_eff), (r_hi, r_nom, r_lo_eff)


def three_steps(r1, r2, r3, tol, **kw):
    """Step 1: both select switches off. Step 2: switch 2 on. Step 3: switch 3 on (switch 2 off, ADR-0010 table). "Both": extra state."""
    return {"1": limits(r1, tol, (), 2, **kw),
            "2": limits(r1, tol, (r2,), 1, **kw),
            "3": limits(r1, tol, (r3,), 1, **kw),
            "both": limits(r1, tol, (r2, r3), 0, **kw)}


def step_windows(r1, r2, r3, tol, **kw):
    """{step: (min mA, max mA)} for steps 1, 2 and 3 (the extra 'both' state is left out)."""
    t = three_steps(r1, r2, r3, tol, **kw)
    return {k: (t[k][0], t[k][2]) for k in ("1", "2", "3")}


def margins(r1, r2, r3, tol, **kw):
    """Margins in mA to each HW-010 number; negative means the number is not met."""
    t = three_steps(r1, r2, r3, tol, **kw)
    return {"s1_min": t["1"][0] - STEP1_MIN_MA, "s1_max": STEP1_MAX_MA - t["1"][2],
            "s3_min": t["3"][0] - STEP3_MIN_MA, "s3_max": STEP3_MAX_MA - t["3"][2]}


def best_r2(r1, tol, series, **kw):
    """E-series value that puts the nominal step 2 limit closest to the assumed target."""
    return min(series(15.0, 232.0), key=lambda r2: abs(limits(r1, tol, (r2,), 1, **kw)[1] - STEP2_NOM_TARGET_MA))


def search(tol, series, **kw):
    """Best (R1, R3) by the smallest relative margin over the four HW-010 numbers, or None when no pair meets all."""
    best = None
    for r1 in series(44.0, 50.0):
        a = limits(r1, tol, (), 2, **kw)
        if a[0] < STEP1_MIN_MA or a[2] > STEP1_MAX_MA:
            continue
        for r3 in series(10.0, 232.0):
            c = limits(r1, tol, (r3,), 1, **kw)
            if c[0] < STEP3_MIN_MA or c[2] > STEP3_MAX_MA:
                continue
            m = min(a[0] / STEP1_MIN_MA - 1, 1 - a[2] / STEP1_MAX_MA, c[0] / STEP3_MIN_MA - 1, 1 - c[2] / STEP3_MAX_MA)
            if best is None or m > best[0]:
                best = (m, r1, r3)
    return best


def leakage_budget_a(r1, r2, r3, tol, v_ilim=V_ILIM_V):
    """Largest leakage per off MOSFET (A, at v_ilim) for which step 1 max and step 3 max still meet HW-010 (bisection)."""
    lo, hi = 0.0, 50e-6
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        mg = margins(r1, r2, r3, tol, leak_a=mid, v_ilim=v_ilim)
        if mg["s1_max"] >= 0 and mg["s3_max"] >= 0:
            lo = mid
        else:
            hi = mid
    return lo


def rule_of_thumb_row(name, v):
    rr = v[3]
    return f"  {name:22s}{rr[0]:7.2f}/{rr[1]:7.2f}/{rr[2]:7.2f}   {v[0]:8.1f}{v[1]:8.1f}{v[2]:8.1f}"


def print_table(r1, r2, r3, tol, label, **kw):
    t = three_steps(r1, r2, r3, tol, **kw)
    print(f"{label}: R1={r1:g}k R2={r2:g}k R3={r3:g}k tol +-{tol*100:g} %")
    print(f"  {'state':22s}{'Rtot kohm hi/nom/lo':25s}{'min mA':>8s}{'nom mA':>8s}{'max mA':>8s}")
    for k, nm in (("1", "step 1 (both off)"), ("2", "step 2 (S2 on)"), ("3", "step 3 (S3 on)"), ("both", "S2+S3 on (extra)")):
        print(rule_of_thumb_row(nm, t[k]))


# Candidate A: smallest-margin-best pair of the search with E192 and 0.1 %, no leakage; R2 from the assumed target
def candidate_a():
    _, r1, r3 = search(TOL_01PCT, e192, leak_a=0.0)
    return r1, best_r2(r1, TOL_01PCT, e192, leak_a=0.0), r3


# Candidate B: E96 1 %. R1 is the smallest value whose step 1 maximum meets 623 mA; R3 the largest value whose step 3 minimum reaches the floor
# Candidate C: the owner decision of 2026-11-05 (b): R1 47.0 k, R2 56.9 k, R3 27.7 k (all 0.1 %, 0603; owner decision 2026-11-06; 56.9 k and 27.7 k unsourced)
R3_PARTS_K = (27.7,)


def candidate_c():
    return 47.0, 56.9, round(sum(R3_PARTS_K), 6)


def candidate_b():
    r1 = min(r for r in e96(44.0, 50.0) if limits(r, TOL_1PCT, (), 2, leak_a=0.0)[2] <= STEP1_MAX_MA)
    r3 = max(r for r in e96(10.0, 232.0) if limits(r1, TOL_1PCT, (r,), 1, leak_a=0.0)[0] >= STEP3_MIN_MA)
    return r1, best_r2(r1, TOL_1PCT, e96, leak_a=0.0), r3


def main():
    print("TPS2553 ILIM steps. Source labels and assumptions: see header and docs/verification/reports/analysis-ilim-steps.md")
    print(f"HW-010: step 1 max {STEP1_MAX_MA:g} mA (min {STEP1_MIN_MA:g} from ADR-0010 table), step 3 {STEP3_MIN_MA:g}..{STEP3_MAX_MA:g} mA")
    print(f"Assumed: Rds(on) {RDS_ON_MIN_OHM:g}..{RDS_ON_MAX_OHM:g} ohm, leak {I_LEAK_A*1e6:g} uA/off MOSFET at V_ILIM {V_ILIM_V:g} V, step 2 nominal {STEP2_NOM_TARGET_MA:g} mA")

    print("\n-- cross check of the equations against the datasheet table (min/nom/max mA)")
    for r, tab in ((15.0, (1610, 1700, 1800)), (20.0, (1200, 1295, 1375)), (49.9, (475, 520, 565)), (210.0, (110, 130, 150))):
        print(f"  R={r:g}k: table {tab}, equations {ios_min(r):.0f}/{ios_nom(r):.0f}/{ios_max(r):.0f}")

    print("\n-- ADR-0010 reference (R1 46.4k, R3 28.0k), 1 %, no Rds, no leakage")
    a = limits(46.4, TOL_1PCT, (), 0, leak_a=0.0)
    c = limits(46.4, TOL_1PCT, (28.0,), 0, leak_a=0.0)
    print(f"  step 1: {a[0]:.0f}/{a[1]:.0f}/{a[2]:.0f} mA   (ADR text: 506..623 max)")
    print(f"  step 3 (ideal switch): {c[0]:.0f}/{c[1]:.0f}/{c[2]:.0f} mA   (ADR text: 1366..1577)")

    print("\n-- search: any E-series pair meeting all four HW-010 numbers (Rds as assumed, no leakage)")
    for nm, tol, ser in (("E96 1 %", TOL_1PCT, e96), ("E96 0.1 %", TOL_01PCT, e96), ("E192 1 %", TOL_1PCT, e192), ("E192 0.1 %", TOL_01PCT, e192)):
        b = search(tol, ser, leak_a=0.0)
        print(f"  {nm}: " + ("none" if b is None else f"R1={b[1]:g}k R3={b[2]:g}k worst relative margin {b[0]*100:.2f} %"))

    ca, cb = candidate_a(), candidate_b()
    print()
    print_table(*ca, TOL_01PCT, "Candidate A (E192 0.1 %), no leakage", leak_a=0.0)
    for lk in (1e-7, 1e-6):
        print_table(*ca, TOL_01PCT, f"Candidate A, {lk*1e6:g} uA per off MOSFET at {V_ILIM_V:g} V", leak_a=lk)
    print(f"  leakage budget per off MOSFET at V_ILIM 1.0 V / 0.8 V / 1.2 V: "
          + " / ".join(f"{leakage_budget_a(*ca, TOL_01PCT, v_ilim=v)*1e9:.0f} nA" for v in (1.0, 0.8, 1.2)))
    mg = margins(*ca, TOL_01PCT, leak_a=0.0)
    print("  margins mA (no leakage): " + ", ".join(f"{k} {v:.1f}" for k, v in mg.items()))
    print()
    print_table(*cb, TOL_1PCT, "Candidate B (E96 1 %), no leakage", leak_a=0.0)
    mg = margins(*cb, TOL_1PCT, leak_a=0.0)
    print("  margins mA (negative = number not met): " + ", ".join(f"{k} {v:.1f}" for k, v in mg.items()))
    print("\nRds(on) sensitivity, candidate A, step 3 min/max with Rds 0 / 15 ohm:")
    for rds in (0.0, RDS_ON_MAX_OHM):
        t = limits(ca[0], TOL_01PCT, (ca[2],), 1, leak_a=0.0, rds_max=rds)
        print(f"  Rds {rds:g} ohm: {t[0]:.1f} / {t[2]:.1f} mA")
    ok = all(v >= 0 for v in margins(*ca, TOL_01PCT, leak_a=0.0).values())
    print("\ncandidate A meets all four HW-010 numbers with no leakage:", ok)

    print("\n-- candidate C (owner decision 2026-11-06): R1 47.0k, R2 56.9k, R3 27.7k, 0.1 %, TMUX1101 switches")
    cc = candidate_c()
    kw = dict(leak_a=TMUX_LEAK_A, rds_max=TMUX_RDS_ON_MAX_OHM)
    print(f"  switch: leakage {TMUX_LEAK_A*1e9:g} nA per off switch at V_ILIM {V_ILIM_V:g} V, Rds(on) max {TMUX_RDS_ON_MAX_OHM:g} ohm [DS SCDS410D]")
    for lbl, kws in (("ideal switch (no leakage, Rds 0)", dict(leak_a=0.0, rds_max=0.0)), ("TMUX1101 limits", kw)):
        print_table(*cc, TOL_01PCT, f"Candidate C, {lbl}", **kws)
        w = step_windows(*cc, TOL_01PCT, **kws)
        for k, req in (("1", f"HW-010: max {STEP1_MAX_MA:g}, min {STEP1_MIN_MA:g} (ADR-0010)"),
                       ("2", f"proposed window {STEP2_BAND_MA[0]:g}..{STEP2_BAND_MA[1]:g}"),
                       ("3", f"HW-010: {STEP3_MIN_MA:g}..{STEP3_MAX_MA:g}")):
            print(f"  step {k} window {w[k][0]:.1f} .. {w[k][1]:.1f} mA   ({req})")
        mg = margins(*cc, TOL_01PCT, **kws)
        print("  margins mA (negative = number not met): " + ", ".join(f"{k} {v:.1f}" for k, v in mg.items()))
        print(f"  step 2 inside the proposed window: {STEP2_BAND_MA[0] <= w['2'][0] and w['2'][1] <= STEP2_BAND_MA[1]} "
              f"(margin {w['2'][0]-STEP2_BAND_MA[0]:.1f} mA low side, {STEP2_BAND_MA[1]-w['2'][1]:.1f} mA high side)")
    print("  leakage budget per off switch at V_ILIM 1.0 V / 0.8 V / 1.2 V: "
          + " / ".join(f"{leakage_budget_a(*cc, TOL_01PCT, v_ilim=v)*1e9:.0f} nA" for v in (1.0, 0.8, 1.2)))
    okc = all(v >= 0 for v in margins(*cc, TOL_01PCT, **kw).values())
    print("candidate C meets all four HW-010 numbers with the TMUX1101 limits:", okc)
    return 0 if ok and okc else 1


if __name__ == "__main__":
    sys.exit(main())
