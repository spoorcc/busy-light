# SPDX-License-Identifier: Apache-2.0
"""N1: worst-case voltage on ILIM_STEPn_EN when the gate output is open and the MCU readback pin
drives or pulls up the net, versus the 2N7002 Vgs(th). Analysis, not a measurement.
Sources: ESP32-C3 datasheet Table 5-4 (VIH 0.75 VDD, VIL 0.25 VDD, VOH 0.8 VDD, RPU 45 kohm typ),
TRM Table 5.12-1 (GPIO20 reset 3 = IE+WPU, GPIO21 reset 4 = OE+WPU); 2N7002 Vgs(th) from a
secondary copy of the Nexperia datasheet (1.0 / 2.0 / 2.5 V at 25 C, 0.6 V min at 150 C): ASSUMPTION."""
VTH_MIN_HOT = 0.6
VTH_MIN = 1.0
VTH_MAX_COLD = 2.75


def open_gate_cases(r_series, r_pd, vdd=3.6, rpu=(30e3, 45e3, 70e3)):
    """Net voltage with the gate output open. Returns {case: volts} (worst case VDD)."""
    out = {"GPIO21 drives high (ROM TX idle), VOH ideal": vdd * r_pd / (r_pd + r_series)}
    for r in rpu:
        out[f"GPIO20/21 input with WPU {r / 1e3:.0f}k"] = vdd * r_pd / (r_pd + r_series + r)
    out["R_series shorted, input with WPU 45k"] = vdd * r_pd / (r_pd + 45e3)
    return out


def pin_level_gate_low(r_series, vdd=3.0, rpu=45e3, vnet=0.1):
    """Pin voltage when the gate drives low and the internal pull-up is still on."""
    return vnet + (vdd - vnet) * r_series / (r_series + rpu)


if __name__ == "__main__":
    for rs, rpd in ((1e3, 100e3), (100e3, 10e3)):
        print(f"R_series {rs / 1e3:g}k, R_pulldown {rpd / 1e3:g}k")
        for k, v in open_gate_cases(rs, rpd).items():
            print(f"  {k}: {v:.2f} V")
        print(f"  gate low, pull-up on: pin {pin_level_gate_low(rs):.2f} V (VIL 0.75 V at 3.0 V, VIH 2.25 V)")
