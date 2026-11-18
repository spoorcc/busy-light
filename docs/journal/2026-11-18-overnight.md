# Overnight work on the P1 board, 2026-11-17 to 2026-11-18 (hand-off)

Status at 05:52 UTC, 2026-11-18 (updated through the morning). Branch `ccr-fff92b31-b7kqlu`. Owner answers: `2026-11-17-p1-order-owner-decisions.md`.
**The P1 board does not exist yet. No routing run was made tonight. Nothing is ready to order.**

## Headline (05:52 UTC)
**With every assembled part on the top side, the 46 mm board does not fit: the placer finds no overlap-free placement**,
before any routing. Scratch experiments (copy of `pcb_full.py` with P1 sides, LED capacitors beside the LEDs, `R_MOVE` 18.4 mm,
ring14 knobs `PLACE_GRID=1.0 PLACE_BLOCKS=3 PLACE_ORIENT=1.5`, 16 seeds of 160000 iterations each; netlist with T1 and R22):

| Variant | Best overlap (mm2, 0 = fits) |
|---|---|
| Baseline, vendor antenna keep-out on | 25.1 (placed DRC: 61 `courtyards_overlap`, waiver max 14) |
| Keep-out off | 6.6 |
| Keep-out on, five of the six hold-off capacitors removed (as if one part) | 9.0 |
| Both (keep-out off, five capacitors removed) | 0.57 (closest; still not overlap-free, and at that density routing on one side at 0.15 mm is not likely) |
| Baseline with 4x iterations | see the update below |

Reading: one-sided P1 on 46 mm needs a decision from you before routing makes sense. The levers, each yours:
grow the board (MECH-001 is already exceeded), fewer parts (hold-off capacitors, LED capacitors, logic), give up the vendor
antenna keep-out (DEV-004), or go two-sided (Standard PCBA, the stored board's layout family).

## Time line
- 21:50 to 22:15 UTC: 20 owner questions; set-up of this container (KiCad 10.0.8 in the `kicad/kicad:10.0` Docker image,
  Freerouting 2.5.0 from Maven Central, ngspice from apt, KiKit 1.8.1 with pip).
- 22:15 to 23:20 UTC: plan 08 drafted, four goldfish reviews (RV-014), plan revised twice; schematic changes made (uncommitted).
- 23:20 to 05:40 UTC: **stopped by the account's 5-hour usage limit** (the readiness goldfish failed with HTTP 429; the session
  resumed at 05:41 UTC). About 6 hours of the night were lost here.

## Done and pushed (commits on the branch)
| Commit | What |
|---|---|
| `3f79d0a` | Owner decisions recorded; HW-008 (amended), HW-016 ([10] mm), HW-017 Approved and ADR-0021 Accepted **as answered by the owner**; HW-010 owner rule for trims; ADR-0020 update (option B not accepted) |
| `a58ef4a` | `run_pcb.sh` accepts the Maven Central Freerouting jar (sha256 `7f8c6247...`) next to the GitHub one; plan 08 draft |
| `fd03b6d` | Plan 08 revision 3 and review record RV-014 (44 merged findings, resolutions) |
| `d901a5c` | TC-208, TC-216, TC-217 procedures (drafted, not run) |

## Done after the readiness review (RV-014 step 4: NO-GO overall, steps 1 to 4 ready; committed `aa4438a`, `9fc37cb`)
In `hw/kicad/spike-gate` and `hw/sim/scripts`; all tests pass (318 passed, 1 skipped for the jar variable, 15 known `GATE_NET`
errors; strict ERC 0 findings, 55 nets equal to the intent table, deterministic):
- **Trim T1:** R_ILIM3 27.4 k + R20 301 ohm replaced by one 27.7 k 0.1 % in 0805 (Yageo RT0805BRD0727K7L, LCSC C865349, from the
  repo's stock-check report; stock not confirmed). Step 3 window 1381.2 to 1566.7 mA (margins 15.22 and 10.33 mA). Test `TrimT1`.
- **HW-017:** new net VBUS (J1, TVS1, U6) and R22 (0 ohm 1206) to VBUS_IC; main-path routing rules per net; tests.
- Jar-pin test tightened.
- **Trim T2 (shared zener for U14/U15) was made and then reverted:** RV-014 showed one fault would then unpower both switches,
  an unspecified state that may raise the limit. Its surge tests stay as an analysis option only.

## Not done
P1 placement (all parts on top), via-in-pad removal, routing batches, finishing, `board-p1/`, order package, KiKit panel, CI
release workflow, housing check, firmware target build (Zephyr fetch started 05:45 UTC), regulatory update. Plan 08 section 5
lists the order of work.

## Findings that need the owner (most important first)
1. **0.15 mm vs 0.1 mm.** The stored board was routed with 0.1 mm rules (`SPIKE_PROFILE=fine`), not 0.15 mm. At 0.15 mm no
   two-sided run ever completed. One side at 0.15 mm is likely not routable on 46 mm (plan 08 R1). Decide: 0.1 mm for P1
   (ADR-0020 option B), or remove parts, or two-sided Standard PCBA.
2. **MECH-001 is already exceeded:** `largest_dim_mm` 59.24 against 58 mm; growing the board (answer 7) makes it worse. No growth
   was made (answer 19). Decide whether growth is allowed.
3. **U9 courtyard (43 x 20 mm)** vs the waiver `courtyards_overlap` max 14: may fail the gate with all parts on top. A courtyard
   or waiver change (DEV-004) is yours.
4. **Seven part types have no LCSC number** (U5 TPS3840, U6 USBLC6-2P6, U3/U4 74LVC1G11, U10 74LVC1G08, U11 74AHCT1G125,
   U13 74LVC1G02) plus R22. Economic PCBA does not place them; a missing U5 defeats the HW-010 hold-off.
5. **R22 rating:** HW-017 asks [3] A and at most [10] mohm; common 1206 jumpers may be about 2 A and 50 mohm (not verified).
6. The housing models disagree on the post azimuths (30/150/270 vs 60/180/300).
7. Plan 08 A9: P1 files are prototype order files, not "product files" of ADR-0012 G1 (assistant's reading; confirm).
8. HW-010 / HW-015 texts name VBUS_IC where the connector side is now VBUS.

## Decisions taken by the assistant (answer 19: reversible, to confirm)
- KiKit panel 1 x 1 with two 5 mm rails (5 PCBs, 2 assembled fits a 1 x 1 panel; a 2 x 1 panel would force 4 assembled).
- Hash-pinned KiKit requirements generated (not yet committed).
- No CPL rotation table (it would be invented); you check rotations in the JLCPCB preview.

## Next steps (in order)
Readiness GO (RV-014 step 4), commit the uncommitted changes, then plan 08 section 5 steps 4 to 12.
