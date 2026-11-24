# SPDX-License-Identifier: Apache-2.0
"""ADR-0025 (owner decision 5 of 2026-11-22): falling threshold and release voltage of the U5 supervisor options.

Sources (hw/evidence/parts): TPS3840 family SNVSB03E (tps3840dl40.yaml: VIT- accuracy +-1.5 %, hysteresis 175 to 225 mV for
VIT- 3.1 to 4.9 V); TPS3808G01 SBVS050N (tps3808g01.yaml: 0.405 V +-2 %, hysteresis 1.5 % typ / 3 % max of VIT, SENSE current
+-25 nA). The hysteresis minimum of the TPS3808G01 is not given; 0 is used (conservative for the lower release edge).
Run: python3 -I supervisor_options.py
"""
VBUS_MIN_ASSUMED = 4.5   # V, the VBUS minimum assumed in HW-010 criterion 5 (M4); not a datasheet value


def tps3840(vit_typ):
    """(falling min, falling max, release min, release max) in V for a TPS3840 threshold option."""
    lo, hi = vit_typ * 0.985, vit_typ * 1.015
    return lo, hi, lo + 0.175, hi + 0.225


def tps3808_divider(r1_k, r2_k, r_tol=0.01, vref=0.405, ref_tol=0.02, i_sense=25e-9, hys_max=0.03):
    """(falling min, falling max, release min, release max) in V for the TPS3808G01 with R1 (top) and R2 (bottom)."""
    def vit(r1, r2, ref, i):
        rpar = r1 * r2 / (r1 + r2) * 1e3
        return (ref + i * rpar) * (1 + r1 / r2)       # a SENSE current out of the pin (i > 0) raises the threshold
    lo = vit(r1_k * (1 - r_tol), r2_k * (1 + r_tol), vref * (1 - ref_tol), -i_sense)
    hi = vit(r1_k * (1 + r_tol), r2_k * (1 - r_tol), vref * (1 + ref_tol), i_sense)
    return lo, hi, lo, hi * (1 + hys_max)


OPTIONS = {
    "TPS3840DL40 (today, no LCSC stock)": tps3840(4.0),
    "TPS3840PL42 (push-pull)": tps3840(4.2),
    "TPS3840PL43 (push-pull)": tps3840(4.3),
    "TPS3808G01, 931k/100k 1 %": tps3808_divider(931.0, 100.0),
    "TPS3808G01, 910k/100k 1 % (as built)": tps3808_divider(910.0, 100.0),   # 931 k is not stocked (ADR-0025, 2026-11-24)
}


def main():
    print(f"{'option':38s} falling V        release V   (VBUS minimum assumed {VBUS_MIN_ASSUMED} V)")
    for name, (a, b, c, d) in OPTIONS.items():
        flag = "release above the VBUS minimum" if d > VBUS_MIN_ASSUMED else ""
        print(f"{name:38s} {a:.3f}-{b:.3f}   {c:.3f}-{d:.3f}  {flag}")


if __name__ == "__main__":
    main()
