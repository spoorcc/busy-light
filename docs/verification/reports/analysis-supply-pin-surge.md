# Analysis: series resistor and zener at the 6 V-limited supply pins on VBUS_IC (HW-010 proposed amendment, ADR-0016)

- **Date:** 2026-11-07. **Author:** assistant. **Status:** Draft analysis. Nothing Approved, nothing measured.
- **Script and tests:** `hw/sim/scripts/surge_supply_pin.py` (ngspice batch, run with `python3 -I hw/sim/scripts/surge_supply_pin.py`), `hw/sim/scripts/test_surge_supply_pin.py` (5 tests, pass; skipped when ngspice is missing). ruff clean.

## Question
The owner chose on 2026-11-07 to protect the supply pins of the TMUX1101 and the TUSB321 with a series resistor and a 5.1 V zener, because a TVS clamps at 8 to 15 V and both parts have a 6 V absolute maximum on the supply pin (`shortlist-tvs1-3v3-regulator.md`). Which resistor values work?

## Facts read (TI datasheets, text extracted 2026-11-07)
| Part | VDD absolute maximum | VDD recommended | Supply current |
|---|---|---|---|
| TMUX1101 (SCDS410D) | 6 V | 1.08 to 5.5 V | 0.003 uA typ, 1 uA max at 125 degC |
| TUSB321 (SLLSEO6C, tables 6.1, 6.3, 6.5) | 6 V | 4.5 to 5.5 V | 100 uA max (active and unattached) |

## Model and assumptions
Circuit per pin: VBUS_IC, series R, pin with C_pin to GND, 5.1 V zener, load current of the part. The surge comes from a source of 0.1 ohm. Assumptions (not from a datasheet): zener Vz 4.85 to 5.35 V, dynamic resistance 60 ohm (zener datasheet not read); surge S1 8/20 us at 15 V peak (highest clamp in the search snippets), S2 a hot-plug ring of 10 V with 1 us decay, S3 a sustained 9 V; C_pin 100 nF nominal and 50 nF worst case (X7R tolerance and DC bias, unverified). Pass limit: peak pin voltage at most 5.7 V (0.3 V below the 6 V maximum), and power in the resistor and the zener at most half of the rating (100 mW for a 0603 resistor, 300 mW for a zener of the SOD-123 class).

## Result (script output)
| R (ohm) | part | C | S1 peak (V) | S2 peak (V) | DC drop at max load (mV) | S3 R power (mW) | S3 zener power (mW) |
|---|---|---|---|---|---|---|---|
| 100 | TMUX1101 | 100 nF | 7.30 | 3.31 | 0.1 | 133 | 195 |
| 100 | TMUX1101 | 50 nF | 8.12 | 4.42 | 0.1 | 133 | 195 |
| 100 | TUSB321 | 100 nF | 7.29 | 3.30 | 10.0 | 133 | 195 |
| 100 | TUSB321 | 50 nF | 8.12 | 4.41 | 10.0 | 133 | 195 |
| 220 | TMUX1101 | 100 nF | 5.66 | 1.96 | 0.2 | 61 | 89 |
| 220 | TMUX1101 | 50 nF | 6.50 | 3.13 | 0.2 | 61 | 89 |
| 220 | TUSB321 | 100 nF | 5.65 | 1.94 | 22.0 | 61 | 89 |
| 220 | TUSB321 | 50 nF | 6.49 | 3.11 | 22.0 | 61 | 89 |
| 470 | TMUX1101 | 100 nF | 4.15 | 1.04 | 0.5 | 28 | 42 |
| 470 | TMUX1101 | 50 nF | 5.41 | 1.86 | 0.5 | 28 | 42 |
| 470 | TUSB321 | 100 nF | 4.11 | 1.00 | 47.0 | 28 | 42 |
| 470 | TUSB321 | 50 nF | 5.40 | 1.81 | 47.0 | 28 | 42 |
| 1000 | TMUX1101 | 100 nF | 2.51 | 0.52 | 1.0 | 13 | 20 |
| 1000 | TMUX1101 | 50 nF | 4.00 | 0.99 | 1.0 | 13 | 20 |
| 1000 | TUSB321 | 100 nF | 2.41 | 0.42 | 100.0 | 13 | 20 |
| 1000 | TUSB321 | 50 nF | 3.90 | 0.89 | 100.0 | 13 | 20 |

## Reading
- Without enough resistance the zener alone cannot hold the pin: 100 ohm gives 7.3 to 8.1 V in S1 and 220 ohm gives 6.5 V at the worst-case capacitor. The resistor and the capacitor form the main defence for short surges; the zener takes the long ones.
- **470 ohm passes S1 and S2 at the worst-case capacitor (5.41 V, margin 0.59 V). 1 kohm passes with more margin (4.00 V).** The sustained 9 V case stays within half of the ratings for both (28 and 42 mW at 470 ohm).
- The TMUX1101 draws at most 1 uA, so 1 kohm costs 1 mV: **1 kohm for the TMUX1101.**
- The TUSB321 draws up to 100 uA, so 470 ohm costs up to 47 mV: **470 ohm for the TUSB321.** The recommended minimum for its VDD is 4.5 V. With VBUS_IC at the assumed 4.5 V sag floor the pin sits at 4.453 V, which is 47 mV under the recommended minimum. This adds to the open M4 question (HW-010 criterion 5) and has to be measured in TC-210 case 5 with the real part. It is not a new failure of the gate (a low supply fails safe: no enable output), but it moves the point at which the CC IC starts to work.

## Zener voltage corners (added after goldfish review RV-011)
The script now runs the assumed zener corners 4.85, 5.1 and 5.35 V (worst-case capacitor 50 nF, surge S1). 470 ohm / TUSB321: 5.23, 5.40 and 5.56 V, so the margin to the 5.7 V pass limit is **0.14 V at the highest zener voltage** (not 0.3 V). 1 kohm / TMUX1101: 4.00 V at all three. The 5.7 V limit is a project choice (0.3 V under the 6 V absolute maximum), not a datasheet value. The sustained 9 V case S3 assumes a source that negotiated 9 V; the CC analysis says a sink that does not negotiate stays at 5 V, so S3 is a bound for a failed TVS1, not a normal event. Tests: 27 in `hw/sim/scripts` pass.

## Recommended values for the owner's approval
| Pin | R | C at the pin | Zener |
|---|---|---|---|
| TMUX1101 VDD (Q2, Q3 supply) | 1 kohm 1 % 0603 | 100 nF (the capacitor already in HW-010) | 5.1 V, SOD-123 class |
| TUSB321 VDD | 470 ohm 1 % 0603 | 100 nF at the pin (value of the existing decoupling capacitor, to confirm) | 5.1 V, SOD-123 class |

## Open points
1. The zener datasheet is not read; Vz tolerance, leakage near 4.5 V and dynamic resistance are assumptions. Choose the part, read it, add it to HW-012, rerun the script with its numbers.
2. With the supply at 5.25 V or 5.5 V the 5.1 V zener (Vz down to 4.85 V) conducts a small current through the resistor and holds the pin at about the zener voltage (inside 4.5 to 5.5 V). The effect on the supervisor and on the hold-off is none (they read VBUS_IC directly); the extra continuous load on VBUS_IC is about 0.4 to 0.8 mA per branch at the nominal 5.1 V zener and up to about 1.4 mA on the 470 ohm branch at the lowest zener voltage (5.5 V - 4.85 V over 470 ohm; reviewer finding). Not simulated for the DC case.
3. The surge shapes are assumptions. The TVS1 part is not chosen; a part with a lower clamp relaxes the result, a higher one tightens it. The result is only valid for the surge on VBUS_IC; the TUSB321 CC1 and CC2 pins also have a 6 V maximum and face the cable directly. That is a separate protection question and is not covered here (to be added to HW-010 or HW-014 after the owner decides).
4. The shorted and the open resistor, and a failed zener, are fault cases for TC-210 (the fault table). A zener that fails short pulls the pin low and the part fails safe; a resistor that fails open removes the supply and also fails safe. Not simulated.

## Not done
No bench, no zener datasheet, no DC simulation, no Monte Carlo of the resistor tolerance. No `hw/` file changed.
