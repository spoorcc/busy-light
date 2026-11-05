# SPDX-License-Identifier: Apache-2.0
"""N4: worst-case TPS3840 hold-off tD = k * C1 for parallel C0G capacitor sets (HW-010 window 200 to 600 ms).

k_min/k_max from docs/verification/reports/datasheet-evidence-supervisor.md (A6); tD(no cap) neglected.
C0G: 0 +/- 30 ppm/degC (EIA class I definition, reference 25 degC; the per-part datasheet was NOT retrieved).
Tolerance is applied per part (worst case: all parts at the same limit). Ageing, DC bias and leakage are
taken as 0 (not checked). Run: python3 -I holdoff_cap.py
"""
K_MIN, K_MAX = 357.6e3, 875.6e3     # ohm
T_MIN, T_MAX = 0.200, 0.600         # s
TC_PPM = 30e-6                      # per degC, C0G
T_REF, T_LO, T_HI = 25.0, -55.0, 125.0   # degC; rated range of the candidate parts (DigiKey, read)

# name: [(nominal farad, tolerance fraction, label)]
SETS = {
    "470+150 (2 parts)": [(470e-9, .05, "GRM31C5C1E474JE01L"), (150e-9, .05, "GRM31C5C1H154JE02L")],
    "330+150+150 (3 parts)": [(330e-9, .05, "GRM31C5C1E334JE01L"), (150e-9, .05, "GRM31C5C1H154JE02L"),
                              (150e-9, .05, "GRM31C5C1H154JE02L")],
    "330+220+68 (3 parts)": [(330e-9, .05, "GRM31C5C1E334JE01L"), (220e-9, .05, "GRM31C5C1H224JE02L"),
                             (68e-9, .05, "68n C0G not checked")],
    "220+220+150+33 (4 parts)": [(220e-9, .05, "GRM31C5C1H224JE02L")] * 2 +
                                [(150e-9, .05, "GRM31C5C1H154JE02L"), (33e-9, .05, "33n C0G not checked")],
    "220+220+100+68 (4 parts)": [(220e-9, .05, "GRM31C5C1H224JE02L")] * 2 +
                                [(100e-9, .05, "GRM31C5C1H104JA01K"), (68e-9, .05, "68n C0G not checked")],
    "3x220 (3 parts)": [(220e-9, .05, "GRM31C5C1H224JE02L")] * 3,
}


def temp_frac(t_lo=T_LO, t_hi=T_HI, t_ref=T_REF, tc=TC_PPM):
    """Largest fractional capacitance change over the temperature range."""
    return tc * max(abs(t_lo - t_ref), abs(t_hi - t_ref))


def c_window(parts, temp=None):
    """Return (c_min, c_max, c_nom) of a parallel set, farad."""
    tf = temp_frac() if temp is None else temp
    nom = sum(c for c, _, _ in parts)
    lo = sum(c * (1 - tol - tf) for c, tol, _ in parts)
    hi = sum(c * (1 + tol + tf) for c, tol, _ in parts)
    return lo, hi, nom


def td_window(parts, temp=None):
    lo, hi, _ = c_window(parts, temp)
    return K_MIN * lo, K_MAX * hi


def fits(parts, temp=None):
    a, b = td_window(parts, temp)
    return a >= T_MIN and b <= T_MAX


def report():
    for name, parts in SETS.items():
        for label, temp in (("datasheet range", None), ("0.6 % (earlier N4 allowance)", 0.006)):
            a, b = td_window(parts, temp)
            print(f"{name:28s} {sum(p[0] for p in parts)*1e9:6.0f} nF  temp {label:28s} "
                  f"tD {a*1e3:6.1f} to {b*1e3:6.1f} ms  {'in window' if fits(parts, temp) else 'OUT'}")


if __name__ == "__main__":
    report()
