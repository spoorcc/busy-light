# Overnight work on the P1 board, 2026-11-17 to 2026-11-18 (hand-off)

Status at about 07:30 CET, 2026-11-18 (after the morning follow-up). Branch `ccr-fff92b31-b7kqlu`. Owner answers: `2026-11-17-p1-order-owner-decisions.md`.
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
| Baseline with 4x iterations (640000 per seed) | 25.2 (no gain: the parts do not fit; not a placer limit) |
| Board 50 mm, parts also allowed in the annulus outside the LED ring (keep-out on) | 9.7 |
| Board 54 mm, same | **0.0 (fits)** |

The growth runs used a scratch copy of `mech_outline.py` with `D_PCB` 50 or 54 mm and the hook lugs as top obstacles. Their
`largest_dim_mm` (59.24) is **not** valid: it uses the constant `R_OUT` 26.5 mm. With today's housing formula (outer diameter
= board + 7 mm, `housing_params.py`) a 54 mm board gives a housing of about 61 mm against the 58 mm of MECH-001 (estimate).

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

## Step 4 (no via-in-pad), merged 2026-11-18 06:10 UTC
Made by an agent in a separate worktree (commit `63fd71a`), merged: one helper `via_hits_smd_pad` used by the stitcher, the grid
router of `pcb_fix.py` (and so `pcb_ring.py`), and a `via_in_smd_pad` count in `pcb_fabcheck.py` with a `--no-via-in-pad`
flag that fails on a non-zero count; 26 new tests. On the stored board the count is **35** (32 in the LED ring cells, 2 at DZ15,
1 at C32; none at U9): the plan's "via-in-pad under U9" was wrong and is corrected.

## Side work done by agents (2026-11-18, 06:00 to 06:12 UTC)
- **Firmware target build** (`docs/verification/reports/sw-target-build-2026-11-18.md`, `c88ad64`): `sw/app` builds for
  `esp32c3_devkitm` with Zephyr v4.5.0 and SDK 1.0.1, 0 warnings, flash 134 884 B (3.22 %); host tests 20 of 20 on native_sim.
  The target image does **not** contain the gate logic yet (`sw/app/CMakeLists.txt` adds only `main.c`); `gate.c` compiled alone
  for the target: 0 warnings, 884 B text. No flashing, no hardware.
- **Regulatory check** (`docs/regulatory/compliance-matrix.md`, technical-file index, `3f9bd7e`): no applicability input changed;
  findings for you: HW-017 and HW-003 have `Regulatory: none` (proposed: RED 3(1)(a) / EN 62368-1 and 3(1)(b), verify); no EMC/ESD
  requirement exists (open since 2026-11-03); RoHS declarations and the lead-free hand-soldering of J1 are not in TC-208; the order
  checklist lacks the prototype label. Its finding on the power check is fixed (`706ba3e`).

## Routing experiment on the 54 mm one-sided placement (06:13 to 06:30 UTC, one run, scratch copy)
`run_pcb.sh`, 0.15 mm default profile, 4 layers, `KEYFIRST=1`, Freerouting 2.5.0 (Maven jar; **needs Java 25**, Java 21 fails).
Result: M1 unrouted 0; after stitching 17 unconnected; after the clean-up **5 unconnected**; strict gate FAIL on
`courtyards_overlap` 33 (waiver max 14, the U9 courtyard) and the 5 unconnected; LED ring cells 47 links, none failed.
One run only (Freerouting varies). Reading: a 54 mm one-sided board is close to routable at 0.15 mm; the U9 courtyard waiver is
the other blocker. 54 mm means a housing of about 61 mm (MECH-001: 58 mm).

## Agents stopped by the usage limit at about 06:20 UTC: their work is now committed (owner request, 2026-11-18 morning)
The main session ran the tests on the partial work and committed it:
- **P1 placement switch (plan 08 step 5):** `P1=1`, off by default; commit `45a1d01`, merged. Full spike-gate suite after the merge
  of the worktree: 360 passed, 1 skipped, 15 known `GATE_NET` errors.
- **Order package scripts (plan 08 section 4.5):** `scripts/fab_p1.sh`, `fab_package.py`, `fab_check.py`, `panel_tabs.py`,
  `panel_p1.json`, `fab_missing_lcsc.txt`, `requirements-fab.txt` and 38 tests (pass on the host and in the KiCad image; ruff and
  `reuse lint` clean). **Not run end to end on any board**, and the CI release workflow (section 4.6) was not written.

## ADR-0022 proposed (2026-11-18 morning)
`docs/decisions/ADR-0022-p1-board-fit.md` (Proposed): five options weighed with the measurements above. Recommendation: two-sided
Standard PCBA for P1 (the only configuration with complete routing in the record; needs a P1 exception to HW-008 and a price within
your limit), and part reduction (switch with selectable current limit, fixed-delay supervisor) as the direction for the next board.
This goes against your answer 1 (one side); the placement measurements are the reason. Not goldfish-reviewed yet.

## Owner question 2026-11-18 07:00 CET: fewer components?
Yes, but each option changes an Accepted ADR (ADR-0010, ADR-0016, ADR-0004) and needs datasheets read; nothing below is checked.
Rough savings against today's 101 footprints:
| Option | Parts saved (about) | Cost / risk |
|---|---|---|
| A USB power switch with two current-limit inputs selected by a pin (TI's USB charging-port-controller family has ILIM_HI/ILIM_LO pins; fit to our step windows not checked) instead of TPS2553 + two TMUX1101 + their protection and pull-downs | 8 to 10 | ADR-0010/0016 amendment; three steps become two unless the part has three |
| One configurable mixed-signal logic IC (GreenPAK class) for U2, U3, U4, U10, U13, maybe also the hold-off timer | 5 to 11 | needs NVM programming (JLCPCB cannot), new verification of the "independent hardware gate" argument |
| A supervisor with a fixed internal delay inside 200 to 600 ms instead of TPS3840DL + six 100 nF C0G | 6 | part to find; delay tolerance against the HW-010 window |
| Fewer LED bypass capacitors (one per 2 or 4 LEDs) | 8 to 12 | ADR-0004 / LED datasheet; supply ripple at the LEDs |
| Option T2 (shared supply protection) | 2 | rejected: one fault unpowers both switches (RV-014) |
Recommendation: look at the switch with selectable limits first (largest saving, simplest safety argument, stays all-hardware),
then the fixed-delay supervisor. Together about 15 parts, which may be enough for one side at 46 to 50 mm.

## Not done
(Updated in the morning; the items once listed here that are now done are in the sections above.)
Routing batches and finishing of a P1 board and `board-p1/` (they wait for the ADR-0022 decision); an end-to-end run of the order
package on a real board; the CI release workflow; the housing check (no FreeCAD here); a goldfish review of ADR-0022.

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
