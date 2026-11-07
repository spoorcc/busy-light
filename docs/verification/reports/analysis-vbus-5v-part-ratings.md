# Analysis: absolute maximum of every part on VBUS_IC and +5V against a hot-plug surge (RV-011 findings 2 and 9; HW-010, ADR-0010, ADR-0016)

- **Date:** 2026-11-07. **Author:** assistant. **Status:** Draft analysis. Nothing Approved, nothing measured.
- **Sources:** the netlist of the spike (`hw/kicad/spike-gate/tests/data/full.net`, 93 parts, 63 nets) for the part list; the HW-012 evidence files `hw/evidence/parts/*.yaml` for the ratings (their status is `unverified`: extracted by an AI from datasheets, not yet checked by a person; the WS2812B file comes from a document of unknown origin); the TUSB321, TPS3840, TMUX1101 and TLV757P datasheets that I read as text today; ADR-0010 E11 for the TPS25200.

## Result
The "surge" below is the voltage that TVS1 lets through. Search snippets give 8 to 15 V for a 5 V TVS at 1 to 8 A (`shortlist-tvs1-3v3-regulator.md`). The real hot-plug current is unknown, so the real clamp voltage is unknown; the table shows which parts survive which clamp voltage.

| Net | Part (ref) | Pin | Absolute maximum | Normal supply | Survives a clamp of 8 V? | Source |
|---|---|---|---|---|---|---|
| VBUS_IC | TPS2553 (U7) | IN, OUT, EN, ILIM, FAULT | 7 V | up to 5.5 V (6.5 V recommended maximum) | **no** | evidence file (ADR-0010 E1) |
| VBUS_IC | TUSB321 (U1) | VDD | 6 V | 4.5 to 5.5 V | no (Proposed fix: 470 ohm + zener) | datasheet read |
| VBUS_IC | TUSB321 (U1) | CC1, CC2 | 6 V | up to about 2 V | no (P3, open) | datasheet read |
| VBUS_IC | TUSB321 (U1) | VBUS_DET | 4 V | through 887 kohm | yes by the resistor | datasheet read |
| VBUS_IC | TMUX1101 (U14, U15) | VDD | 6 V | 1.08 to 5.5 V | no (Proposed fix: 1 kohm + zener) | datasheet read |
| VBUS_IC | TPS3840DL40 (U5) | VDD, RESET | 12 V | 1.5 to 10 V | yes | datasheet read |
| VBUS_IC | USBLC6-2P6 (U6) | VBUS | not found in the evidence file | not found | unknown | evidence: source-missing |
| VBUS_IC | TVS1 | - | not chosen | - | unknown | not chosen |
| +5V | TLV75733P (U8) | VIN | 6 V | 1.45 to 5.5 V | **no** | datasheet read |
| +5V | WS2812B placeholder (D1 to D16) | VDD | 5.3 V | 4.5 to 5.5 V (the document contradicts itself) | **no, and the normal rail may already exceed it** | evidence file, unknown-origin document; LED part not chosen (ADR-0004) |
| +5V | SN74AHCT1G125 (U11) | VCC | 7 V | up to 5.5 V | marginal (7 V) | evidence file |
| +5V | capacitors (C3 to C23) | - | 50 V class (C0G/X7R) | - | yes | evidence file (not checked per part) |

## What this shows
1. **The surge problem is wider than the two pins that got a resistor and a zener.** The current limiter itself (TPS2553, 7 V) sits on VBUS_IC without any series part, and the +5V rail passes the surge on: the TPS2553 is a switch (about 85 mohm), so the output capacitors charge to nearly the clamp voltage within microseconds. The regulator (6 V), the LEDs (5.3 V) and possibly the buffer (7 V) then see it too.
2. **ADR-0010 decision 5** ("over-voltage on VBUS is handled by the TVS requirement") cannot be met by a plain 5 V TVS for the TPS2553 either: 7 V is below the 8 to 15 V snippets.
3. **The ADR-0010 alternative TPS25200** (E11: 2.5 to 6.5 V operating, input withstands 20 V, over-voltage lockout 7.6 V, output clamp 5.4 V) was rejected for other reasons; it fixes the +5V rail side in one part. Its 5.4 V clamp is above the 5.3 V of the WS2812B placeholder (an LED part is not chosen).
4. **The WS2812B placeholder shows a conflict that needs an LED decision anyway:** a maximum of 5.3 V against a rail that can be 5.5 V.
5. **The real hot-plug surge is unknown.** The 8 to 15 V clamp is for a standard 8/20 us test current of 1 to 8 A. A cable hot-plug may produce far less current. The measurement (TC-210 step 4, scope on VBUS_IC and +5V at plug-in) decides how large the problem is.

## Options for the owner (not decided)
| # | Option | For | Against |
|---|---|---|---|
| S1 | Measure the real hot-plug surge first (TC-210 step 4 on a spike board with the parts), and decide with data | cheap; may show the surge is small | no protection decision until a board exists |
| S2 | Replace the TPS2553 by the TPS25200 (20 V input, 5.4 V output clamp) | one part protects VBUS_IC side and +5V | reopens ADR-0010 point 5 (accepted today for the TPS2553); different limit range and resistor values; stock and fee not checked |
| S3 | Add a series element before the TPS2553 (ferrite bead or a few ohm resistor) and a bigger low-clamp TVS | keeps the TPS2553; reduces the surge current | adds voltage drop in the 1.5 A path (a 0.1 ohm part drops 0.15 V) and one or two parts; not simulated |

## Not done
No datasheet of the TPS2553, USBLC6-2P6, SN74AHCT1G125 or TPS25200 was read today (their ratings are the unverified evidence values); no simulation of the +5V rail during a hot-plug; no bench measurement; the LED part is not chosen.
