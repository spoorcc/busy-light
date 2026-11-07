# 2026-11-07: surge protection, 3V3 regulator, sensor pins, step table

Owner decisions taken in the session after a plain-language walkthrough (the assistant recorded them; only the owner approves requirement text).

| Item | Decision | Consequence |
|---|---|---|
| Surge on VBUS_IC | Add a series resistor and a 5.1 V zener at the supply pins of the switch (TMUX1101) and of the TUSB321 (both 6 V absolute maximum, datasheets read). TPS3840 (12 V) is not affected. | Values are not derived yet; the assistant derives them, checks them against the TVS clamp and puts the test in TC-210. TVS1 stays a standard 5 V part. HW-010 criterion 4 is reworded as a Proposed amendment. |
| 3V3 regulator | TLV75733P (TI, 1 A, SOT-23-5) with a Wi-Fi duty-cycle heat estimate added to the thermal case. If the estimate is bad, a buck converter is considered. | LCSC number, stock and the HW-012 entry are still to do. The heat estimate goes into HW-013 and TC-213. |
| Sensor pins | Give up the FAULT_N input: GPIO1 and GPIO4 are reserved for the orientation sensor (I2C). | FAULT_N of the TPS2553 is no longer read by the processor. SW-009 mentions FAULT_N (ignored while HOLD_OK_RB is low), so that text and the pin map change; the effect on a short-circuit report to the user is not assessed. HW-011 has no part yet. |
| SW-005 step table | A 1.5 A and a 3 A charger both give the middle step until TC-213 shows that the top step is thermally safe. | The top step is unlocked by a later documented change. SW-005 criterion 3 and ADR-0010 open point 3 are updated as Proposed amendments. |

Not run: no calculation of the resistor and zener values, no bench, no build.

Follow-up (same day): values derived in `docs/verification/reports/analysis-supply-pin-surge.md`: 1 kohm for the TMUX1101 and 470 ohm for the TUSB321, each with 100 nF and a 5.1 V zener. Assumptions: zener model, surge shapes. Not run: no bench, no zener datasheet.

Owner answers (same day, later): the surge values (1 kohm, 470 ohm, 100 nF, 5.1 V zener) are approved; the CC-pin options were asked for and are in `analysis-cc-pin-protection.md`; the regulator heat estimate was asked for and is in `analysis-regulator-heat.md`. Not run: no bench, no zener datasheet.

Owner choices (same day, later): regulator in the standard DBV package with a firmware limit only (the limit is about 70 mA average at the worst board and case; see `analysis-regulator-heat.md`); CC pins: ESD part plus series resistors (P3), with the caution recorded in `analysis-cc-pin-protection.md` that a series resistor alone does not keep the pin under 6 V. Not run: no bench, no ESD test, no requirement for the transmit-duty limit yet.

Approval walkthrough (same day, later): the owner accepted ADR-0019 and approved the SW-005, SW-007 and SW-010 amendment text. On ADR-0018 the owner asked about a pin multiplexer and about combining FAULT_N with another fault input; the assistant answered that the GPIO matrix adds no pins, and proposed an AND gate in place of the HOLD_OK_RB buffer (no new part). Decision on ADR-0018 pending. Not run: no firmware, no bench.

Owner choice (same day, later): the surge on the whole 5 V side is measured first on the spike board (TC-210 step 4); TPS25200 stays the prepared fallback (option S2 of `analysis-vbus-5v-part-ratings.md`); no design change now. A board has to be built before this can be measured; no hardware was built in this session.
