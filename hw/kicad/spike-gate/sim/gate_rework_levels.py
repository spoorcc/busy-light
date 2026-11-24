# SPDX-License-Identifier: Apache-2.0
"""ADR-0024 (owner decisions 1, 2, 4 of 2026-11-22): logic levels of the restored HOLD_OK pull-up, the GPIO0 series resistor
and the CC series resistors. Analysis, not a measurement. Run: python3 -I gate_rework_levels.py

Sources: SN74LVC1G08 SCES217AA (VIH 2 V and VIL 0.8 V at VCC 3 to 3.6 V, II +-5 uA, Ioff +-10 uA; the LVC1G11 is taken
as equal, not re-read); TPS3840 SNVSB03E (tps3840dl40.yaml: open-drain leakage 90 nA, VOL 0.2 V at 2 mA, VPOR 0.95 V at
5.6 uA); TUSB321 SLLSEO6C (RCC_D 4.6 to 5.6 kohm); ESP32-C3 (readback_margin.py: VIL 0.25 VDD, VIH 0.75 VDD, internal
pull-up 30 to 70 kohm).
"""
LVC_VIH, LVC_VIL, LVC_II = 2.0, 0.8, 5e-6          # V, V, A at VCC 3.0 to 3.6 V
TPS3840_ILKG, TPS3840_VPOR, TPS3840_I_POR = 90e-9, 0.95, 5.6e-6
RD_MIN, RD_MAX = 4.6e3, 5.6e3                       # ohm, TUSB321 RCC_D


def hold_ok_high(vbus, r6=150e3, n_inputs=3):
    """Worst-case HOLD_OK level with U5 released: every LVC input (U3, U4, U10) sinks II and U5 leaks."""
    return vbus - r6 * (n_inputs * LVC_II + TPS3840_ILKG)


TPS3808_ILKG = 300e-9      # A, RESET leakage at 6.5 V (SBVS050N section 6.5: 300 nA maximum; the TPS3840 value is 90 nA)
TPS3808_VPOR, TPS3808_VOL, TPS3808_I_POR = 0.8, 0.2, 15e-6   # V, V, A (SBVS050N: VOL 0.2 V at 15 uA while VDD is at VPOR 0.8 V)


def hold_ok_high_vdd_u1(vbus_ic, r6=100e3, n_inputs=3, r_su1=470.0, i_u1=200e-6, i_u5=6e-6):
    """ADR-0025: HOLD_OK high level with the pull-up on VDD_U1 (VBUS_IC behind R_SU1 and the 5.1 V zener). The drop over R_SU1
    carries the TUSB321 supply (100 uA unattached, TUSB321.i_unattached_ufp; 200 uA is an ASSUMPTION for an attached cable),
    the TPS3808 supply (6 uA is an ASSUMPTION, its table was not read) and the pull-up current of the three inputs. The
    zener clamp is not reached below 5.1 V."""
    i_load = i_u1 + i_u5 + n_inputs * LVC_II
    v_vdd_u1 = min(vbus_ic - r_su1 * i_load, 5.1)
    return v_vdd_u1 - r6 * (n_inputs * LVC_II + TPS3808_ILKG)


def hold_ok_r6_min_tps3808():
    """Smallest pull-up that keeps a valid low while VDD is at VPOR (the pull-up follows VDD_U1, so the current at VPOR is VPOR / R6)."""
    return (TPS3808_VPOR - TPS3808_VOL) / TPS3808_I_POR


def hold_ok_r6_min(vol=0.2):
    """Smallest pull-up to VBUS_IC that keeps a valid low at VPOR (datasheet-evidence-supervisor.md, A10)."""
    return (TPS3840_VPOR - vol) / TPS3840_I_POR


def gpio0_pin_with_pullup(r_series=10e3, vdd=3.0, rpu=30e3, vnet=0.0):
    """GPIO0 pin voltage when U2 drives CC_OK_1A5 low and the firmware left the internal pull-up on (smallest pull-up)."""
    return vnet + (vdd - vnet) * r_series / (r_series + rpu)


def gpio0_drive_current(r_series=10e3, voh=3.6):
    """Current from a GPIO0 driven high into the U2 output low, through the series resistor (A)."""
    return voh / r_series


def cc_shift(rp, r_series=100.0, rd=RD_MIN):
    """Relative change of the CC voltage the TUSB321 sees with a series resistor, for a resistor Rp to the source rail
    (a current-source Rp gives no change). Negative: lower."""
    return (rp + rd) / (rp + rd + r_series) - 1.0


def rd_seen_by_source(r_series=100.0):
    """(min, max) ohm of the sink pull-down that the source sees at the connector."""
    return RD_MIN + r_series, RD_MAX + r_series


def main():
    for v in (4.3, 4.5, 4.75):
        print(f"HOLD_OK high, VBUS_IC {v} V, R6 150k, worst leakage: {hold_ok_high(v):.2f} V (VIH {LVC_VIH} V)")
    for v in (4.399, 4.5, 4.75):
        print(f"HOLD_OK high with R6 on VDD_U1 (ADR-0025), VBUS_IC {v} V, worst leakage: {hold_ok_high_vdd_u1(v):.2f} V (VIH {LVC_VIH} V)")
    print(f"R6 minimum for a valid low at VPOR: {hold_ok_r6_min() / 1e3:.0f} kohm (TPS3840); {hold_ok_r6_min_tps3808() / 1e3:.0f} kohm (TPS3808 on VDD_U1)")
    print(f"GPIO0 with the 10 k resistor, U2 low, internal pull-up 30 k on: {gpio0_pin_with_pullup():.2f} V (VIL 0.75 V at 3.0 V)")
    print(f"GPIO0 driven high into U2 low: {gpio0_drive_current() * 1e3:.2f} mA")
    for rp in (10e3, 22e3, 56e3):
        print(f"CC series 100 ohm, resistor Rp {rp / 1e3:g} k: {cc_shift(rp) * 100:.2f} % at the TUSB321")
    lo, hi = rd_seen_by_source()
    print(f"Rd seen by the source: {lo / 1e3:.2f} to {hi / 1e3:.2f} kohm")


if __name__ == "__main__":
    main()
