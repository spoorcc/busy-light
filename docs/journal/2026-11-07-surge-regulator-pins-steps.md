# 2026-11-07: surge protection, 3V3 regulator, sensor pins, step table

Owner decisions taken in the session after a plain-language walkthrough (the assistant recorded them; only the owner approves requirement text).

| Item | Decision | Consequence |
|---|---|---|
| Surge on VBUS_IC | Add a series resistor and a 5.1 V zener at the supply pins of the switch (TMUX1101) and of the TUSB321 (both 6 V absolute maximum, datasheets read). TPS3840 (12 V) is not affected. | Values are not derived yet; the assistant derives them, checks them against the TVS clamp and puts the test in TC-210. TVS1 stays a standard 5 V part. HW-010 criterion 4 is reworded as a Proposed amendment. |
| 3V3 regulator | TLV75733P (TI, 1 A, SOT-23-5) with a Wi-Fi duty-cycle heat estimate added to the thermal case. If the estimate is bad, a buck converter is considered. | LCSC number, stock and the HW-012 entry are still to do. The heat estimate goes into HW-013 and TC-213. |
| Sensor pins | Give up the FAULT_N input: GPIO1 and GPIO4 are reserved for the orientation sensor (I2C). | FAULT_N of the TPS2553 is no longer read by the processor. SW-009 mentions FAULT_N (ignored while HOLD_OK_RB is low), so that text and the pin map change; the effect on a short-circuit report to the user is not assessed. HW-011 has no part yet. |
| SW-005 step table | A 1.5 A and a 3 A charger both give the middle step until TC-213 shows that the top step is thermally safe. | The top step is unlocked by a later documented change. SW-005 criterion 3 and ADR-0010 open point 3 are updated as Proposed amendments. |

Not run: no calculation of the resistor and zener values, no bench, no build.
