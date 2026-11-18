# Owner decisions on simplifying the schematic for one-sided placement (2026-11-18)

Owner request: "Be creative, simplify the schematic to strive for single side placement." The assistant measured part areas and
ran placement experiments (scratch copies of the generator, 46 mm board, all parts on top, vendor antenna keep-out on, 16 seeds
of 160000 iterations; journal `2026-11-18-overnight.md` for the method):

| Set | Changes | Best overlap (mm2, 0 = fits) |
|---|---|---|
| today | | 25.1 |
| X2 | step 3 = both ILIM switches on (U13 out); FAULT_N wired onto the hold-off node (U10 out); zeners SOD-323 | 10.5 |
| X4 | X2 + hold-off and spare capacitors 0805 + logic U2, U3, U4, U11 in SC-70 | 1.7 |
| X6 | X4 + 13 non-critical resistors 0402 + one pull-up fewer + button on the internal pull-up | **0.0** |

Movable-part area before the change: 469 mm2 (60 parts). Step-window calculation for "step 3 = both switches on"
(`hw/kicad/spike-gate/sim/ilim_steps.py`, 0.1 % resistors, TMUX1101 limits): with R_ILIM3 = 56.2 k (same part as R_ILIM2):
step 1 504.2 to 616.6 mA, step 2 934.9 to 1091.7 mA, step 3 1368.8 to 1553.5 mA (margins 2.8 and 23.5 mA); no switch state
exceeds the step-3 maximum (today "both on" gives 1817 to 2020 mA and only the NOR gate prevents it).

## Answers (owner, Ben Spoor, 2026-11-18, in the working session)
| # | Question | Answer |
|---|---|---|
| 1 | Step 3 = both ILIM switches on, R_ILIM3 = 56.2 k (U13 out; firmware sets both selects for step 3; SW-009 "never both" changes) | **Yes, R3 = 56.2 k** (recommended) |
| 2 | Wire FAULT_N onto the hold-off node, one pull-up to 3V3 (U10 and one pull-up out; a limiter fault now also closes the hardware gate) | **Yes, fault closes the gate** (recommended) |
| 3 | Package changes: SOD-323 zeners, 0805 capacitors, SC-70 logic, 0402 resistors, button pull-up removed | Free text: "What you recommend maybe lookup info" |

Assistant's choice for answer 3 (answer 19 of 2026-11-17: reversible, logged): all four package changes, because only the full
set X6 reached overlap 0 in the measurement. Part numbers for the new packages are looked up on the web (distributor listings,
snippets; datasheet and shop sites are blocked from this container) and marked as lookups, not verified sourcing.

## Effects (to be written into the controlled documents)
- ADR-0023 (new): records decisions 1 and 2 with alternatives; amends ADR-0016 (gate logic) and ADR-0018 (FAULT_N now gates).
- HW-010: steps no longer exclusive; step 3 = both switches; R_ILIM3 = 56.2 k (replaces trim T1, 27.7 k); fault-injection table
  rows change; HOLD_OK node pulled up to 3V3 and shared with FAULT_N.
- SW-009 / SW-005: firmware drives both selects for step 3; the "never both" rule and the "EN2 and EN3 both high is unknown"
  state change; gate.c and its tests follow (sw/ change after the requirement text is approved).
- HW-016: spare size [1206] becomes [0805]; HW-007: button pull-up internal.

## Implemented 2026-11-18 (commits `94ce2cf`, `8573614`)
- Generator (`layout_full.py`): U13, U10, R6, R13 removed; GATE_OK_RB wired node (U5 RESET, U7 FAULT, R8 10 k to 3V3, U3/U4 pin 6,
  GPIO6); both ANDs take CC_OK_1A5; R_ILIM3 56.2 k 0603; zeners BZT52C5V1S SOD-323 (D_Zener pins 1 K, 2 A); U2 in TI DCK-5
  (`Texas_R-PDSO-G5_DCK-5`, the 74LVC1G04 symbol's footprint filter rejects the generic SOT-353), U11 SC-70-5, U3/U4 SC-70-6;
  15 resistors in 0402 (R1, R2, R3, R4, R5, R9, R10, R11, R12, R14, R15, R16, R17, R18, R19); C4, C32 0805. 97 parts.
  Strict ERC 0 findings, 52 nets equal to the intent table, deterministic.
- Sourcing (`sourcing.py`, package-aware since the same value can be two parts): SN74LVC1G04DCKR C8207, SN74LVC1G11DCKR C529281,
  SN74AHCT1G125DCKR C350557, BZT52C5V1S (LGE) C545356, Uni-Royal 0402WGF 100 k C25741, 10 k C25744, 1 k C11702, 330 C25104
  (JLCPCB basic). Web-search snippets of LCSC/JLCPCB/distributor pages; no datasheet or shop page opened. **No 0805 C0G 100 nF
  part was found, so the six hold-off capacitors stay 1206** (the scratch result X6 used 0805 there).
- Model: `sim/ilim_steps.py::both_on_windows`, test `BothOnStep3`; requirement and ADR texts: ADR-0023, HW-010 amendment,
  HW-016 and HW-007 and SW-009 proposed changes.
- Tests (spike-gate suite) pass apart from the 15 known `GATE_NET` errors.

## Real-generator placement (P1=1, 46 mm, keep-out on, 16 seeds)
- Before the four pull-downs moved to 0402: overlap **0.468 mm2** (close; not zero).
- Placed DRC of that board: 29 courtyard overlaps, **28 with U9**: the ESP32-C3-MINI-1 library courtyard is 43 x 20 mm (antenna
  keep-out plus a wide lateral band); the placer avoids only the module body and the vendor antenna keep-out. The strict gate's
  waiver allows 14 overlaps with U9 (DEV-004). **Owner decision needed:** a body-only courtyard for U9 (the antenna copper keep-out
  and the vendor no-parts zone stay; DEV-004 update), or the full courtyard as a placer obstacle (then one side does not fit).
- A 3-run batch with the pull-downs in 0402 (full flow: placement, routing at 0.15 mm, stitching, clean-up, strict gate) was
  started at about 17:45 UTC; its result follows in this file or in the P1 report.

## Owner answer on the U9 courtyard (2026-11-18, in the working session)
Question: body-only courtyard (recommended), raise the waiver to about 30, or keep the full library courtyard as a placer obstacle.
**Answer: courtyard as obstacle.** Measured consequences (real P1 placement board, `u9cy.py` in the scratchpad):
- the U9 front courtyard spans x -23.4 to +8.5 mm and y -21.6 to +21.6 mm around the board centre; of the 1063 mm2 movable disc
  (r 18.4 mm) 576 mm2 lie inside it, so about 490 mm2 remain for about 360 mm2 of part bounding boxes;
- 15 fixed ring parts lie inside it whatever the placer does: the LEDs D6 to D12 and the LED capacitors C12 to C19; the waiver
  allows 14 overlaps with U9 (DEV-004), so the strict gate fails on the ring alone unless one capacitor leaves the courtyard or the
  owner changes the waiver.

## Owner answer on the module position (2026-11-18, in the working session)
Measured with the U9 courtyard as a placer obstacle (scratch copy, P1, 46 mm, keep-out on): module offset +1 mm (today) 12.6 mm2,
-2 mm 2.1 mm2, -4 mm 0.24 mm2; -4 mm plus 0402 for C7, C24, C25, C26, R_SU1, R_SU14, R_SU15, R8: **0.0 mm2**, and exactly 14 fixed
parts touch the U9 courtyard (D6 to D12, C13 to C18, SW1; the waiver allows 14). Question: move the module 5 mm towards the
antenna-side edge (MOD_OFF 1.0 to -4.0 mm)? **Answer: yes, shift 5 mm** (recommended). The antenna end then sits about 6.5 mm from
the LED ring; range is not verified either way (spike 7.2, TC-205). Parts for the extra 0402 swaps (web search, JLCPCB basic):
Samsung CL05B104KO5NNNC C1525 (100 nF 16 V X7R), CL05A105KA5NQNC C52923 (1 uF 25 V X5R), Uni-Royal 0402WGF4700TCE C25117 (470 ohm).

## Routing batch on the final design (p1b2, 2026-11-18, 19:19 to 20:03 UTC)
Settings: P1=1, 46 mm, module offset -4 mm, U9 courtyard as placer obstacle, 0.15 mm, 4 layers, router sees the In1 GND plane
(`planes inner`), KEYFIRST two-stage, Freerouting 2.5.0 (Maven jar), 3 runs, strict gate with SPIKE_ALLOW_KNOWN_OPEN=0.

| Run | Unconnected after clean-up | Strict gate FAIL classes | Power check FAIL |
|---|---|---|---|
| run1 | 6 | 2 | 1 |
| run2 | 6 | 2 | 1 |
| run3 (best) | 4 | 2 | 1 |

Best run (run3), findings that still fail:
- `unconnected_items` 4: plane pads without a via to their plane: TPS2553 OUT U7.6 (+5V), regulator input capacitor C5.1 (+5V),
  ESD part U6.2 (GND), plus one GND track piece. The stitcher found no free straight track to a via spot: the router had wrapped
  the /ILIM and VBUS_IC tracks around U7.6 and the USB data tracks around U6.2 (it does not know that a plane pad still needs a via).
- `footprint_symbol_mismatch` 2: C4 and C32 are excluded from the BOM on the P1 footprints, not on the schematic symbols. **Fixed:**
  the generator now writes `in_bom no` for the DNP spares (`test_spare_footprints_are_dnp_and_not_in_the_bom`).
- Power check: +5V from U7 to the regulator input has no path (infinite), because U7.6 is not stitched. VBUS 18.3 mV, VBUS_IC
  29.5 mV, +3V3 45.3 mV at their analyst currents (all within 50 mV).
- Tolerated by the waiver: 14 U9 courtyard overlaps (max 14), 1 U9 rule-area finding (max 1). No clearance finding after clean-up.

Two changes to the routing flow (spike-gate, tests in `tests/test_pcb_check_stitch.py`):
1. **Dogleg stitch:** when every straight track to a via spot is blocked, the stitcher tries one corner. Replayed on run3's routed
   board it stitches U11.5; U7.6, C5.1 and U6.2 still fail (no free first leg at 0.6 mm for U7.6; one at 0.25 mm for U6.2).
2. **Fan-out first (`PRESTITCH=1`, default off):** the plane pads get their via before the router runs and the vias are locked,
   so the router routes around them. Smoke test on run3's ring board: 100 of 102 plane pads get a via (the two misses are the
   0.4 mm-pitch GND pads of U1, which the router or the post-route stitch handle). A batch with the same placement seeds (p1b3)
   is running; its result decides whether P1 uses this.
