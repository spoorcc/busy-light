# Analysis: effective capacitance of C2, C3, C5, C6 under DC bias (HW-014, HW-015, HW-010)

- **Date:** 2026-11-09. **Author:** assistant. **Status:** Draft analysis. Nothing Approved. Nothing measured on the bench.
- **Script and tests:** `hw/sim/scripts/dc_bias_caps.py`, `hw/sim/scripts/test_dc_bias_caps.py` (11 tests pass; `test_bulk_cap_bounds.py` still passes, 20 in total).

## Data: Samsung curves read in the browser (update 2026-11-09)
The first version of this analysis assumed a retention of 0.40 because no part-specific curve was at hand. The curves were then read from the Samsung Electro-Mechanics Component Library (`weblib.samsungsem.com/mlcc/mlcc-ec.do`, graph "DC Bias", condition 25 degC, AC 1 Vrms, 1 kHz) with Claude in Chrome: the page keeps the chart data points, which were read for each of the four parts (91 points from 0 V up). They are the maker's typical values, not guaranteed limits.

| Ref | Part | Check point | Reading | Retention |
|---|---|---|---|---|
| C2 | CL10A475KO8NNNC | 5.36 V (first point at or above 5.25 V) | 2.008 uF of 4.268 uF at 0 V | 0.4705 |
| C3 | CL21A106KAYNNNE | 5.48 V | dC -54.6 % | 0.4539 |
| C5 | CL10A225KO8NNNC | 5.48 V | dC -60.0 % | 0.4003 |
| C6 | CL10A106KP8NNNC | 3.34 V | dC -56.2 % | 0.4377 |

| 100n (C8 to C26) | CL10B104KB8NNN (X7R, 50 V) | 5.61 V (first point at or above 5.5 V) | 0.10187 uF of 0.10204 uF at 0 V | 0.9983 |

The 100 nF row was read in the same way on 2026-11-09 (141 points, 0 V to 50 V). At 5.12 V the retention is 1.0016, so the bias loss of the X7R part is negligible at 5 V; the low case is 76.4 nF (tolerance and X7R spread only). Because the real part is 0.102 uF at 0 V, the 0 V high case is not made lower by this.

The retention is applied to the nominal value, then tolerance (-10 %) and the X5R spread (-15 %) are applied. This is conservative where the maker's 0 V reading is above nominal (C5: 2.385 uF against 2.2 uF). The curve is a typical value at 25 degC, so criterion 1 is met with the maker's curve; the bench measurement (criterion 2) is still open. The page lists the part names without the last letter (for example CL10A475KO8NNN); the orderable suffix was not checked.

## Parts chosen (lookups of 2026-11-09, listings only, no datasheet opened)
| Ref | Net | Value text | MPN | LCSC | Note |
|---|---|---|---|---|---|
| C2 | VBUS_IC | 4.7u 16V X5R 0603 | CL10A475KO8NNNC | C19666 | JLCPCB basic part |
| C3 | +5V | 10u 25V X5R 0805 | CL21A106KAYNNNE | C15850 | listing showed 0 stock |
| C5 | +5V | 2.2u 16V X5R 0603 | CL10A225KO8NNNC | C23630 | JLCPCB basic part |
| C6 | +3V3 | 10u 10V X5R 0603 | CL10A106KP8NNNC | C19702 | one LCSC page: not recommended for new designs |

Value texts now carry the voltage rating, so that C3 (0805, 25 V) and C6 (0603, 10 V) have different sourcing entries.

## Result (script output, retention 0.40)
| Check | Result | Limit | Break-even retention |
|---|---|---|---|
| HW-015: C2 at 5.25 V | 1.69 uF | at least 1.0 uF | 0.28 |
| HW-015: VBUS_IC at 0 V (C2 plus C24 to C26, high tolerance and temperature) | 6.32 uF | at most 10.0 uF | - |
| HW-014: C5 at 5.5 V (TLV757P input) | 0.67 uF | more than 0.47 uF | 0.28 |
| HW-014: populated +5V sum at 0 V (C3, C5, 16 x 100n) | 17.5 uF | at most 100 uF | - |
| HW-014: room for the spares C4 and C32 | 82.5 uF | - | - |
| Start-up bound with C6 at its high value | 102.7 uF | above the sum | - |

Reading: both lower bounds hold while the real retention stays above 0.28. The maker's retention is 0.47 for C2 and 0.40 for C5, so the margin is 1.7 times for C2 and 1.4 times for C5 on the typical curve; the margin against part-to-part spread and the bench (HW-015 criterion 2, TC-215) is not shown.

## Not counted or not done
- Protection parts on VBUS_IC (TVS1, U6, zeners): their junction capacitance must fit in the 3.7 uF room; TVS1 has no part yet.
- The capacitance inside the ESP32-C3 module on +3V3 is not known; the start-up bound of 102.7 uF excludes it.
- C6 is not checked against the output-capacitor rule of the TLV757P (datasheet not read in this analysis).
- The 100 nF capacitors (X7R) are now covered (curve above). C3 and the 100 nF capacitors are still not counted towards the TLV757P input minimum (C5 alone is used).
- Spares C4 and C32 (1206, do not populate, value text "DNP spare"): no part and no curve. Only the room is computed: together at most 65 uF nominal at 0 V keeps the populated sum within 100 uF (82.5 uF / 1.265). A real spare value needs its own curve, because a large 1206 X5R loses more than 50 % at 5 V.
- Protection parts: USBLC6-2P6 (U6) and TVS1 are not read: datasheets not opened in this analysis, TVS1 has no part. The 3.7 uF room on VBUS_IC is unchanged and unchecked.
- The 25 V and 16 V ratings are chosen for low derating, not calculated against the surge decision S1 to S3 (RV-013).
- Bias on C24 to C26 is taken as 0 V (the 0 V value is the high case).
