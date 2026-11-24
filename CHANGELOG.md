# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Scope: the changelog covers the product as a whole (software, hardware, mechanical and user-visible documentation).
Hardware and mechanical revisions are named in the entries (for example "hardware rev A").

## [Unreleased]

### Added
- Plan 09 (Draft): the centre of the LED ring as the button (owner decision 9 of 2026-11-22, interview of 2026-11-23): separate
  centre disc, switch place and disc support still open (S1 off-centre switch against S2 moved module; guided disc against
  three switches in parallel), first-order checks, test plan TC-310 to TC-313; journal `2026-11-23-centre-button-interview.md`.
  No requirement, ADR or CAD changed yet. Revision 2 after the goldfish review RV-018: the antenna baseline is corrected to 5.06 mm (revision 1 said 7.6 mm), a switch-by-support feasibility matrix replaces the "lean S1" (one off-centre switch on soft supports fails; centred switch with bridges passes only in a narrow band; three switches work), the stuck-press rule is redone, requirement texts MECH-010 to MECH-013 are drafted, and a pre-order gate is added. Revision 3 after the readiness NO-GO: the TL3342 body is 6.4 x 5.2 mm (not 4.5 x 3.5 mm), so with the real switch the module-moved option keeps only 50 to 60 % of the antenna margin; step 0 (switch evidence and a smaller-switch search) and step 1 (tested analysis scripts) are specified to the signature. Revision 4 after the second readiness NO-GO: the three-switch concept does not fit around the stored module at r = 11 with the real switch, the M3 maximum force is 4.8 N at the centre, step 0 gets a recording rule for the one-page datasheet.
- Plan 09 step 0 (revision 5): switch datasheets and stock for the centre button. Evidence `hw/evidence/parts/sw-tl3342.yaml` (updated), new `sw-b3u-1000p.yaml` and `sw-ksc221.yaml`
  (`check_part_evidence.py` on the three files: 3 hashes, 15 quotes, 0 errors; dimensions are drawing-only and not text-checked), report `docs/verification/reports/stock-check-button-switches.md`.
  Finding: no listed part meets all criteria and none publishes a force-travel curve; the Omron B3U-1000P (3.0 x 2.5 mm, 1.50 +- 0.49 N, pre-travel 0.15 mm) keeps 77 % of the antenna margin in option S2
  on the assistant's scratch search; the TL3342F160QG has LCSC stock 1 and no published travel. No requirement, ADR, CAD or board file changed. Licence map allows the two new evidence files.
- Plan 09 revision 6: owner decisions D1 to D3 of 2026-11-24 ("Do your recommendations"): direction S2 with the Omron B3U-1000P, S3 as fallback, no scissor study; steps 0 and 1 as analysis; step 1 rescoped
  to the B3U values (`s2_click_force`, `click_force_extremes`, `bridge_band` in `button_disc.py`, B3U cases in the pose search). No requirement, ADR, CAD or board file changed.
- Plan 09 step 1 (revision 7): analysis scripts with tests: `mech/analysis/button_disc.py` (rigid disc on springs and switches, S2 click force, bridge stiffness bands, beam, plate and guide formulas), `button_light.py`
  (ring spill onto the disc), `check_tolerance.py` (informational vertical and lateral button chains), `hw/kicad/spike-gate/src/button_zone.py` (outlines from the stored board text, S2 pose search, S3 scan, fill) and their
  tests; report `docs/verification/reports/analysis-button-disc.md`; ADR-0026 (Proposed): S2 with the Omron B3U-1000P recommended (weighted sum 96 against 89 for S3 and 73 for S2 with the TL3342),
  S3 as fallback; RV-018 records the third readiness NO-GO and the review of plan and code (NOT READY, resolved in revision 8). After the review ADR-0026 scores S2 84, S3 87 and S2 with the TL3342 66 (S2 and S3 within noise; both go to the coupon gate). Results: S2 with the B3U keeps 3.64 mm (72 %) of the 5.06 mm antenna margin with the antenna end away from the switch (3.90 mm at the best pose, 1.35 mm from the switch); the bridge band is 2.20 to 6.69 N/mm (B3U) against 2.83 to 3.92 N/mm
  (TL3342); over the B3U pre-travel tolerance no bridge stiffness holds the 2 to 5 N window, so the click travel must be measured; three switches in parallel miss the window at both ends. No requirement, CAD or board file changed.
- Plan 09 revision 9: owner answers of 2026-11-24 (D4 to D8): both S2 and S3 go to the coupon gate, the force window is good enough to start, the button is used very rarely (life [2 000] presses derived), the light comes
  from the ring and rim and the disc stays dark, the product looks Apple-grade. The disc becomes a separate opaque part with a [0.4] mm gap and a light-tight lip; proposals MECH-014 (appearance) and a MECH-002 change (disc dark),
  TC-302 and TC-316 rows; open questions 10 (process for the look) and 11 (disc material and finish). `button_light.required_transmission`: the disc transmission must be at most 4.5 % at r = 15 mm for 3 % of the ring luminance
  (optical density 1.35). ADR-0026 gains the criteria "look and feel" and "disc dark"; the assistant's scores are S2 94, S3 107, S2 with the TL3342 71 (S3 leads on look); the decision is to build both in the gate. No requirement, CAD or board file changed.
- Owner decisions of 2026-11-24 applied: ADR-0024 Accepted; ADR-0025 option B Accepted (TPS3808G01DBVR, divider 910 k / 100 k because no 931 k is stocked, one 68 nF C0G on CT, supply on VDD_U1); R_ILIM3 54.9 k (option A). Schematic generator
  (`layout_full.py`: U5 SOT-23-6 box symbol, R26, R27, C27 to C31 removed, strict ERC 0 findings, 102 parts, 58 nets), sourcing, placement rules (`pcb_full.LAYOUT_RULES`, `pcb_rules.BLOCKS`), `fab_check` (ILIM value, must-place set), `sim/ilim_steps.py`
  (54.9 k window 1379.1 to 1564.3 mA), `sim/supervisor_options.py` (910 k row), `sim/gate_rework_levels.py` (HOLD_OK high level 2.03 V with the pull-up on VDD_U1), `tests/data/full.net`, the missing-LCSC list (empty), HW-010 amendment text for the owner
  to confirm, ADR-0025 amendment. Plan 08 revision 6 (section R) and its readiness review RV-019 prepare the re-placement that closes the `fab-release` failure.
- Plan 09: owner agreement D9 of 2026-11-24 to the recommendations for questions 10 and 11 (appearance sample in a finer process, FDM for function; matt opaque disc in the lid colour family). Disc size (question 7) stays open at 30 mm.
- ADR-0024 (Proposed): gate rework after RV-017 (owner decisions 1, 2 and 4 of 2026-11-22): the hold-off AND gate U10 with R6 on VBUS_IC and R8 on FAULT_N is restored (ADR-0018 option E), GPIO0 gets a 10 kohm resistor (R23), each CC line gets an ESD diode and a 100 ohm resistor (TVS3, TVS4, R24, R25), FAULT_N gets a test pad (TP7). The schematic generator draws it (57 nets, strict ERC 0 findings); the stored board-p1 is stale until the re-placement (plan 08 revision 6). New tests: `test_gate_logic_full.py` (truth table and single faults on the generated netlist), `test_gate_rework_levels.py`, layout tests for the gate and the CC protection (HW-010, HW-003, HW-006, SW-009 proposals in the requirement files).
- ADR-0025 (Proposed): stocked replacement for the supervisor U5; recommended TPS3808G01 with a 931 k / 100 k divider and one 68 nF C0G (hold-off 221.8 to 572.7 ms); `sim/supervisor_options.py`, `holdoff_cap.py` TPS3808 window, evidence `tps3808g01.yaml`.
- `docs/verification/reports/analysis-ilim-drift.md` and `sim/ilim_steps.py`: SLVS841G table anchor and resistor TCR, soldering and life drift; with step 3 = both switches R_ILIM3 = 56.2 k has a drift budget of 0.17 % (below tolerance + TCR 0.25 %), 54.9 k has 0.91 %; the owner decides the value. Evidence `ilim-resistors.yaml` (Yageo RT and AT, Vishay MCT).
- HW-017: R22 is the TA-I Tech RLM12FTCMR005 5 mohm 1206 current-sense resistor (LCSC C316225, evidence `rlm12.yaml`); the owner confirms.
- Skill `readme-refresh` (`.claude/skills/readme-refresh/SKILL.md`): order of work to bring the READMEs and their images
  up to date (count, decide what to re-render, P1 renders with the panel of the same board, look at each image, edit,
  check), wording rules and lessons. New `scripts/readme_facts.py` prints the counts the README quotes (requirements and
  approvals, ADRs per status, reviews, plan statuses, host test cases), images that no page shows, and the READMEs with
  the commits to its folder since its last change; test `scripts/tests/test_readme_facts.py` (fixture tree; the
  own-Status rule checked by mutation). Goldfish readiness review RV-015 (NO-GO on the first pass, findings resolved).
- README images of the P1 board and its order panel (plan 08, HW-008, HW-009): new
  `hw/kicad/spike-gate/render_p1_images.sh` exports the schematic in two crops, the four copper layers, top and bottom 3D
  renders of `board-p1/` and a 3D render of the KiKit panel from `scripts/fab_p1.sh` into
  `docs/verification/reports/images/p1-*.png`. Test `scripts/tests/test_readme_images.py`: every image a README shows
  exists, and the six P1 images are committed and shown.
- Stored P1 board `hw/kicad/spike-gate/board-p1/` (plan 08 section 5 step 8, ADR-0023): batch p1b8 run 3 completed by the
  second router pass; every assembled part on the top. Strict ERC 0 findings, strict DRC only the tolerated U9 classes
  (DEV-004), no unconnected item, no via in a pad, power check within 50 mV with full-width paths, `tests/test_board_p1.py`
  6 passed, `scripts/fab_p1.sh` all gates passed. Not reviewed or approved; not ready to order (U5 source, R22 part, owner
  review). README in the folder (HW-008, HW-010, HW-016, HW-017).
- Spike routing flow: `run_repass.sh`, a second Freerouting pass over the cleaned-up board with every track and via locked,
  then stitch, clean-up and strict DRC again; it replaces `final.*` only when fewer connections stay open. `run_pcb.sh` runs
  it when the clean-up leaves an unconnected item (`REPASS=1`, the default). On p1b8 run 3 it closed the last open
  connection (1 to 0). Tests `tests/test_run_repass.py` (HW-008).
- `scripts/ci_hw.sh` runs `pcb_fabcheck --no-via-in-pad` and the power check on `board-p1/` (plan 08 asked for the fab
  check; it was not there). The CI `hardware` job installs pip from apt and the pinned numpy and scipy for it. Test
  `scripts/tests/test_ci_hw_script.py` (HW-008, HW-010).
- Spike power check: `full_width_path` per supply case, the case solved again without tracks narrower than 0.75 x the net's
  current-based width; the board picker counts a failing case like a drop over target. It fails batch p1b7 run3 and the
  p1b3 board (+5V current through 0.15 mm clean-up track) and passes batch p1b8 run3. Tests `FullWidthPath` and
  `test_power_fails_counts_a_path_through_thin_track` (HW-008, HW-010).
- CI workflow `.github/workflows/fab-release.yml` (plan 08 section 4.6, owner answer 17): test, build and publish jobs; on a push
  to `main` it refreshes the draft release `fab-latest` with the P1 order package, on a published release it attaches the files;
  without a stored `board-p1/` it reports NOT RUN. Hash-pinned test tools `scripts/requirements-fab-test.txt`; structure test
  `scripts/tests/test_fab_release_workflow.py`; proposed DEV-007 (release instead of a committed `hw/fabrication/<rev>/`). Not
  run on GitHub yet (HW-008, HW-009).
- Spike routing flow: `run_pcb.sh` switch `PRESTITCH=1` (default off) gives the plane pads their via before the router runs and
  locks it (fan-out first); `pcb_stitch.py --reuse-max` limits the track to an existing via; the stitcher tries a track with one
  corner when every straight escape is blocked (P1 batch of 2026-11-18; plan 08, HW-008).
- P1 placement keeps the full ESP32-C3-MINI-1 courtyard (antenna keep-out included) free of movable parts (owner decision 2026-11-18), the module moves 5 mm towards the antenna-side edge (MOD_OFF -4.0 mm, owner decision 2026-11-18), and C7, C24, C25, C26, R_SU1, R_SU14, R_SU15, R8 are 0402 (JLCPCB basic parts by web lookup); surge test uses the 0402 power rating (ADR-0023, HW-005, HW-010).
- Simplified schematic for one-sided placement (ADR-0023, owner decisions 2026-11-18): step 3 = both ILIM switches on with R_ILIM3 = 56.2 k (no switch state above the step 3 maximum; NOR gate U13 removed; replaces trim T1), TPS3840 RESET and TPS2553 FAULT wired on GATE_OK_RB with one 3V3 pull-up (U10 and R6 removed; a limiter fault now closes the gate), SOD-323 zeners, SC-70 logic, eleven 0402 resistors, button on the GPIO internal pull-up (R13 removed), 0805 spare footprints; package-aware sourcing with web-looked-up LCSC numbers; 97 parts instead of 101; strict ERC 0 findings (HW-010, HW-016, HW-007, SW-009).
- Proposed ADR-0022 (how P1 gets its parts onto the board): the measured one-sided placement does not fit on 46 mm; proposed two-sided Standard PCBA for P1 and part reduction (switch with selectable current limit, fixed-delay supervisor) for the next revision; the owner decides (HW-008, MECH-001, HW-010).
- Order package scripts for P1 (plan 08 section 4.5; not yet run on a P1 board): `scripts/fab_p1.sh`, `scripts/fab_package.py`, `scripts/fab_check.py` (BOM/CPL checks, missing-LCSC list policy, reproducibility compare), `scripts/panel_tabs.py` and `scripts/panel_p1.json` (KiKit 1 x 1 panel, tabs at chosen azimuths), `scripts/fab_missing_lcsc.txt`, hash-pinned `scripts/requirements-fab.txt`; 38 tests. The CI release workflow (plan 08 section 4.6) is not written yet (HW-008, HW-009).
- Spike generator switch `P1=1` (off by default): every assembled part on the top side, LED capacitors beside their LEDs, movable radius 18.4 mm, top-side tab region, ring links on the capacitor's layer, sourcing fields and DNP marks on the board; 16 tests (plan 08 step 5, HW-008).
- Power check of the spike board follows the HW-017 split: cases VBUS (J1 to R22) and VBUS_IC (R22 to the TPS2553 input), with a test (HW-010, HW-017, plan 08 step 3).
- Evidence report `sw-target-build-2026-11-18.md`: `sw/app` builds for `esp32c3_devkitm` with Zephyr v4.5.0 and SDK 1.0.1 (FLASH 134 884 B, 3.22 %, 0 warnings; simple boot, no MCUboot); host tests 20 of 20 pass on `native_sim/native/64`. The gate logic is not linked into the target image; nothing flashed or run on hardware (plan 07, SW-005, SW-009).
- Spike generator for the P1 board (plan 08): HW-017 damping link R22 (0 ohm 1206) between the connector-side net VBUS (J1, TVS1, U6) and VBUS_IC, with per-net main-path routing rules; trim T1 under the owner rule (R_ILIM3 27.7 k 0.1 % 0805 replaces 27.4 k + R20 301 ohm, windows recalculated). The stored two-sided board is not regenerated (HW-010, HW-017).
- Owner decisions of 2026-11-17 for the prototype board P1 (journal `2026-11-17-p1-order-owner-decisions.md`): one-sided SMD assembly at JLCPCB Economic PCBA, 0.15 mm tracks, 4 layers HASL lead-free, own KiKit panel, CI draft release of the order files. HW-008 (amended: hand-soldered through-hole J1 allowed), HW-016 (spares within [10] mm), HW-017 and ADR-0021 approved or accepted by the owner; HW-010 gets an owner rule for part trims; ADR-0020 option B not accepted (HW-008, HW-010, HW-016, HW-017, ADR-0020, ADR-0021).
- Spike board: real capacitor parts for C2 (4.7 uF 16 V), C3 (10 uF 25 V), C5 (2.2 uF 16 V), C6 (10 uF 10 V) with MPN and LCSC numbers, and a DC-bias bound script `hw/sim/scripts/dc_bias_caps.py` (Samsung DC-bias curves read for each part; HW-014, HW-015, HW-010). BOM references without MPN: 2 (J1, TVS2; closed by a later entry).
- DC-bias analysis extended to the 100 nF X7R capacitors (CL10B104KB8NNN, retention 0.998 at 5.6 V) and to the room for the spares C4 and C32 (65 uF nominal together); protection-part capacitance bounded at 1 nF against 3.67 uF of room on VBUS_IC (snippets); a real spare value still open (HW-014, HW-015).
- Spike board TVS1 chosen by the owner under surge option S1 (measure the real hot-plug surge first, RV-013 finding 9): Nexperia PESD5V0S1BA,115 (LCSC C19224) in the sourcing table; a plain 5 V TVS clamps at 10 to 14 V, so the 6 V and 7 V parts rely on the supply-pin resistors and zeners and on the TC-210 step 4 measurement (HW-010).
- Part evidence for TVS1 (`hw/evidence/parts/pesd5v0s1ba.yaml`, 11 claims) and the Nexperia BZX84-C5V1 (11 claims added to `bzx84c5v1.yaml`) from the downloaded datasheets; a source-missing claim for the USBLC6-2P6 VBUS pin capacitance; all claims unverified (HW-012, HW-010).
- Spike board J1 and TVS2 have an MPN now: J1 GCT USB4085-GF-A (LCSC C7095263; no edge-mount variant exists, the project footprint is the USB4085 pad pattern at the board edge), TVS2 Nexperia PESD3V3L1BA,115 (LCSC C51450, owner choice 2026-11-09); evidence files `usb-c-receptacle.yaml` and `pesd3v3l1ba.yaml` (unverified), the placeholder `tvs-sod323.yaml` is removed. BOM references without MPN: 0 (HW-008, HW-010, HW-012). The USBLC6-2P6 VBUS-pin capacitance is not published; the sensitivity shows 3.67 uF would be needed to matter (HW-015).
- Draft ADR-0021 (surge option S1, measure first), draft requirement HW-017 (damping footprint in the VBUS path of the prototype), TC-217 and RISK-046; nothing Approved or Accepted, no board change yet.
- Spike board capacitor values (owner decisions 2026-11-08, finding 4 of `spike-fab-review.md`): C2 4.7u, C3 10u 0805, C5 2.2u, C6 10u, C4 and new C32 are 1206 do-not-populate spares on +5V (HW-014, HW-015, HW-016, proposal report `proposal-tbd-capacitor-values.md`); `pcb_spare_caps.py` with tests applies them to the stored board (C32 on the bottom side, routed by `pcb_fix.py`); no tbd value is left and the C3/C4 footprint-mismatch waiver is gone. Fix: the sourcing fields of the previous change were missing on the board footprints, which gave 100 `footprint_symbol_field_mismatch` warnings in the strict DRC; they are now written to the footprints.
- Spike board BOM sourcing fields (finding 5 of `spike-fab-review.md`): hidden `MPN`, `Manufacturer` and `LCSC` fields on every schematic part from `hw/kicad/spike-gate/src/sourcing.py` (only parts with a recorded source: 28 part groups, web lookups of 2026-11-08, to be re-checked at order time; 7 of the BOM references have none yet: C2, C3, C5, C6, J1, TVS1, TVS2) and a `pcb_fabreview.py` finding that lists parts without an MPN; stored schematic regenerated (ERC 0, no other change). Numbers for the other parts need datasheet or shop evidence (HW-008, HW-010).
- Spike board tooling: tidiness score `pcb_quality.py` (vias, off-45 length, sharp corners, rows, ring spread, passive distance) as tie-break of the run picker, placement grid `PLACE_GRID`, antenna keep-out `PLACE_ANT_KEEPOUT`, `SEED_OFFSET` for `run_best.sh`; batches ring8 to ring10 recorded (HW-010). One of 12 ring10 runs passes the strict gate. Batches ring11 to ring14: regulator pin ties, functional blocks and orientation costs in the placer (`PLACE_BLOCKS`, `PLACE_ORIENT`, off by default), and a clean-up fix (`snap_to_vias` is now called); two of 12 ring14 runs pass the strict gate. Batch ring15 (`PLACE_ROWS=0.5` soft test-point row): three of 12 runs pass the strict gate, none better than ring14 run 9; the run picker now ranks power-check failures before tidiness. Assembly check `pcb_fabreview.py` and the report `spike-fab-review.md` (4 findings). Fixes: seven parts renamed to numbered references (C27 to C31, R20, R21), silkscreen designators for 73 of 100 parts and four fiducials by script (`pcb_finish.py`, `pcb_rename.py`); still not ready to order (tbd values, no part numbers). CI: `scripts/ci_hw.sh` checks the stored spike board through the strict wrapper (waiver list, DEV-004) instead of the raw kicad-cli exit code; the board project now switches on the four default-ignored ERC checks; ruff line-length and format fixes in `bulk_cap_bounds.py`. The routed board (ring14 run 9) is stored in `hw/kicad/spike-gate/board/` and the README images are re-rendered from it. Fabricator-minimum check `pcb_fabcheck.py` (JLCPCB numbers of ADR-0020; run 9 passes, ring at the absolute minimum; partial, ADR-0020 still Proposed).
- Skill `pcb-route-and-gate` (order of work, gate and lessons for the spike board), reviewed by goldfish (RV-012).
- Draft requirement HW-014 (bulk capacitance of the +5V rail, [10] to [100] uF effective) with TC-214, the analysis `analysis-5v-bulk-capacitance.md` and the script `hw/sim/scripts/bulk_cap_bounds.py` with tests (HW-004, HW-010).
- Draft requirement HW-015 (capacitance on VBUS before the switch, 1.0 to 10.0 uF effective, USB 2.0 Device Capacitance ECN) with TC-215.
- Goldfish review RV-013 of HW-014 and HW-015: rejected for In Review; the HW-014 lower bound is not sound as drafted.
- HW-014 redrafted after the owner decision of 2026-11-08 (lower bound = part makers' minimum, upper bound [100] uF); draft requirement HW-016 (spare capacitor footprints on +5V) with TC-216; bound script with a sensitivity table.

### Changed
- The BOM names the Yageo RT0603BRD0747KL (C326725) and RT0603BRD0756K2L (C705784) for the ILIM resistors of the approved HW-010 table; the FH TD03G parts had 0 stock on 2026-11-22. `scripts/fab_missing_lcsc.txt` no longer lists R22. `tests/data/full.net` refreshed (105 components).
- Owner decisions of 2026-11-22 on the P1 rework (journal `2026-11-22-owner-decisions-p1-rework.md`): restore U10 and R6
  in the gate, a 10 k resistor on GPIO0, add the P3 CC-pin protection, another supervisor part instead of U5, keep R_ILIM3
  at 56.2 k until the model includes drift and ageing, R22 as a 1206 shunt of 2 to 5 mohm, the whole centre of the ring as
  the button, enforce the input-path rules. Recorded now: MECH-001 upper limit 60 mm (approved amendment; placer limit
  `MAX_DIM_MECH001` 60.0; board test against it, board-p1 59.24 mm); HW-017 amendment: J1 to U7 at most [100] mV at
  1.5 A with the link at [10] mohm, gated by `pcb_power_check.py` `input_path.within_budget`, `fab_p1.sh` and
  `test_board_p1.py` (board-p1: 83.0 mV); ADR-0022 Superseded; DEV-004 approved for the spike and P1; DEV-007 approved;
  DEV-008 accepted as a record (HW-017, MECH-001, ADR-0022, DEV-004, DEV-007, DEV-008).
- Placement and finishing tools for the next P1 board (RV-016 rows 12, 14, 15, 18). The placer enforces the plan 08
  input-path rules with P1 (TVS1, U6 and R22 to the nearest J1 VBUS pad; R22 to U7): a rule to a fixed part costs per mm
  beyond the limit to the nearest of its points (`pcb_place.Placer`, `pcb_full.resolve_rules`); the two-sided default
  build keeps its old rules. `pcb_power_check.py` reports the J1-to-U7 drop (`input_path`: board-p1 68.0 mV in copper,
  83.0 mV with R22 at 10 mohm, 98.0 mV at 20 mohm, at 1.5 A); report only, the budget is an owner decision; `fab_p1.sh`
  prints it. `pcb_finish.py` writes the bottom silkscreen map of owner answer 13 (each top part's reference mirrored on
  B.SilkS, moved up to 2 mm to clear bottom pads, vias, the edge and other texts; a later pass replaces the earlier texts)
  and an identification text "busy-light P1 <commit>", or "P1 <commit>" at 0.8 mm when that is all that fits (two passes on
  a copy of board-p1: 65 of 89 top parts mapped, "P1 5550e96" placed, no silkscreen finding from the new texts; board-p1
  itself is unchanged). Tests:
  `test_pcb_place.py::FixedPartnerRules`, `test_pcb_full.py::RuleMisses`, `test_pcb_power_check.py`,
  `test_pcb_finish.py` (HW-003, HW-008, HW-017, RV-016).
- Records after RV-016 and RV-017: RISK-047 to RISK-053 (U5 missing makes the gate fail open; firmware can hold the gate
  open through GPIO6; gate node reads "OK" with VBUS gone and 3V3 up; reset loop under overload; HASL at the 0.4 mm-pitch
  U1; R22 resistance or not placed; part availability) and RISK-044 updated; DEV-008 (Proposed: P1 built before the
  readiness GO and partly before the requirement texts were approved); DEV-007 updated (no `--clobber` on a published
  release); journal `2026-11-22-reviews-and-gates-board-p1.md` with the CI run IDs and results. The P1 placer gives the DNP
  spares no solder paste, so the bottom paste layer of the next board is empty (test `test_dnp_spares_have_no_solder_paste`,
  failed before) (HW-008, HW-010, HW-017, SW-007, SW-009, SYS-020, RV-016, RV-017).
- Goldfish review RV-017 of ADR-0023 (asked for by RV-016 row 6): **rejected as written**. Decision 1 (step 3 = both
  switches) holds up, but its 2.8 mA lower margin is inside the model error; decision 2 (FAULT and RESET on one node pulled
  up to 3V3) puts GPIO6 directly on the gate node, breaks the read TPS3840 pull-up rule, gives a reset loop that SW-007 does
  not count and latches at step 1 under overload; the firmware maps select 3 alone to the top step, which is the step-2
  current on P1; no test models the as-built gate (`test_gate_logic.py` models the old one). ADR-0023 gets a review line,
  its status is unchanged; the owner decides rows 1, 2, 6 and 12 (HW-010, SW-005, SW-007, SW-009, SYS-020, ADR-0018,
  ADR-0023, RV-017).
- Order package and release workflow after review RV-016 (rows 1, 16, 27). `scripts/fab_package.py full-bom --schematic`
  adds the schematic symbols that kicad-cli 10 leaves out of the BOM: the full BOM of board-p1 now lists C4 and C32 as DNP
  (HW-016, TC-216) and the test points as "excluded from BOM". `fab-release.yml`: runs test and build on pull requests
  (never publish); the build job fails after the upload when a gate failed (before: green, publish skipped silently); new
  `scripts/fab_release_notes.sh` writes the fab_check result, the missing-LCSC list and the owner waivers into the job
  summary and the release notes (plan 08 4.5 promised the list; the notes were a fixed text); the notes are made in the
  build job, so the publish job still runs only `gh`; a published release that already has files is not overwritten (no
  `--clobber`). The pin test of `requirements-fab.txt` counts only imports that run at load time (an import inside a
  function, kiutils in `lib_tables.py`, is not needed; `pcb_layout_check.py` ran without kiutils) and still fails without
  scipy. Tests: `test_fab_check.py::test_full_bom_keeps_the_dnp_spares_of_the_schematic` (real board-p1 schematic),
  `test_fab_release_workflow.py` (HW-008, HW-009, HW-016, RV-016).
- Order and board gates after review RV-016 (rows 1, 11, 12, 13, 17, 19, 20, 26, 28, 41, 43). `scripts/fab_check.py`: the
  ILIM resistors must have exactly the ADR-0023 values (`ILIM_VALUES`; "27.7k 0.1%" passed the old "0.1%" test); a
  must-place part (the HW-010 gate parts and the HW-017 link R22, `MUST_PLACE`) without an LCSC number fails even when
  `fab_missing_lcsc.txt` lists it, unless the new owner file `scripts/fab_owner_waivers.txt` names it (no waiver given);
  the bottom paste Gerber must be empty. New `hw/kicad/spike-gate/src/pcb_layout_check.py` measures the ADR-0016
  proximity rules and the plan 08 input-path rules on a board file (board-p1: 9 rules missed); `scripts/fab_p1.sh` runs it
  as a gate, so the order script now fails on board-p1 (placement rules, and fab_check on U5 and R22). The placer records
  the rules it misses in `placement.json` and prints them (`pcb_full.rule_misses`); the HW-016 rule is 7.0 mm (7.5 mm
  allowed 10.455 mm). `tests/test_board_p1.py`: the U9 courtyard overlaps must be exactly the 14 fixed ring parts; only
  C4 and C32 may be DNP parts on the bottom; two tests record the known defects of board-p1 as expected failures (the
  placement rules; the main path at 0.6 mm, which has 0.45 mm segments). The `ci.yml` hardware job runs the 430 spike-gate
  tests on every push and pull request (before: only `fab-release.yml` on `main`), with ngspice, in the image pinned by the
  digest that `fab-release.yml` uses. Tests: `test_pcb_layout_check.py`, `test_fab_check.py`, `test_fab_p1_script.py`,
  `test_ci_workflow.py`, `test_pcb_full.py::RuleMisses` (each new test failed on the old code where it checks a change)
  (HW-008, HW-010, HW-016, HW-017, ADR-0016, ADR-0023, RV-016).
- Plan 08 revision 5 (section 0: the state after the build) and goldfish review RV-016 of the plan and the stored P1 board:
  **not ready to order** (45 findings; readiness pass not run). Blocking: a missing U5 makes the gate fail open and the order
  check allows it; GPIO6 sits directly on the gate node; the hold-off pull-up moved to 3V3 against the TPS3840 evidence; the
  CC-pin protection chosen on 2026-11-07 is not on the board; 5 of 15 placement rules and the 4 input-path rules are missed;
  the main path has 0.45 mm segments; the full BOM leaves out C4 and C32; MECH-001 is exceeded; PR CI does not run the
  spike-gate tests. The README and `board-p1/README.md` now say "not ready to order" (HW-003, HW-008, HW-009, HW-010,
  HW-016, HW-017, MECH-001, ADR-0023, RV-016).
- The default `pytest` run (and so the `ci.yml` python-tools job) includes the 54 analysis tests of `hw/sim/scripts`;
  before, only the fab-release workflow on `main` ran them. The job installs ngspice: without it the 16 surge tests
  skip (CI run 44904291971: 167 passed, 16 skipped). Test `scripts/tests/test_ci_workflow.py` (HW-010, HW-013, HW-014).
- Images without a page (found by `scripts/readme_facts.py`): the four spike-board images are shown in the frozen board's
  `hw/kicad/spike-gate/board/README.md`, the pipeline report links its render, and the housing concept image of
  2026-11-04 (replaced in the README by the generated housing model on 2026-11-07, named nowhere) is deleted; git keeps
  it. Test `test_every_report_image_is_shown_somewhere` fails for an image that no Markdown file shows.
- README updated to the state of 2026-11-21: P1 board, panel and checks in the gallery instead of the frozen spike board;
  status table with 105 requirements (21 approved), 23 ADRs (19 accepted, 2 proposed, 2 superseded), 15 reviews, the target
  build of `sw/app` and the checks of `scripts/ci_hw.sh`; how to build the P1 order package. `board-p1/README.md` shows the
  renders. `hw/sim/`, `mech/analysis/` and `sw/app/tests/` READMEs list their files and how to run them.
- P1 placement (plan 08, HW-016, HW-008): the do-not-populate spares C4 and C32 go on the bottom side (not assembled, so the
  assembly stays one-sided) in 1206 again, held within 7.5 mm of U7 by a hard layout rule and pin ties (batch p1b3 put C4 24.8 mm
  from U7 pin 6, against HW-016's [10] mm); the LED capacitors keep out of boxes around four panel tabs at 105, 217.5, 285 and
  330 deg (`pcb_rules.P1_TAB_AZIMUTHS`, new `scripts/fab_p1.sh` default), so the 3 mm capacitor-to-tab rule can hold (it could
  not before: best 2.42 mm). `run_meta.json` records the real router thread count. `scripts/ci_hw.sh` gates `board-p1/` with
  the strict wrapper. New `src/pcb_sourcing.py` copies sourcing fields from the schematic to a stored board.
- Sourcing: U6 USBLC6-2P6 has LCSC C15999 (web search 2026-11-18); `scripts/fab_missing_lcsc.txt` now lists only R22 (candidate
  C190124, 20 mohm max against HW-017's [10] mohm) and U5 (no listing found) (HW-008, HW-017, HW-010).
- Spike board tooling, no via-in-pad (plan 08 step 4, HW-008, RV-014): one rule `pcb_rules.via_hits_smd_pad` (any net, pad box grown by 0.05 mm) used by the stitcher (the U9 via-in-pad shortcut is removed; the via goes beside the pad with a short track) and by the grid router of `pcb_fix.py` (and so the LED ring cells of `pcb_ring.py`); `pcb_fabcheck.py` reports `via_in_smd_pad` and fails on it with `--no-via-in-pad`. The stored board `board/` has 35 such vias (32 in the LED ring cells, 2 at DZ15, 1 at C32; none at U9) and is not regenerated.
- Strict waiver limits of the spike profile `stitched-4l` lowered to the observed counts (owner decision 2026-11-08): `net_conflict` 0, `footprint_symbol_mismatch` 2 (C3, C4 only), `courtyards_overlap` 14 (U9 only); test added (DEV-002, DEV-004).
- Spike board: U1 and U9 schematic symbols carry the datasheet pad numbers (`layout_full.PAD`), `pcb_full.PADMAP` deleted, test points out of the BOM in the schematic; batch ring7 removes all 77 `net_conflict` findings (98 to 16 findings), no run passes the strict gate (HW-010, DEV-002).
- README images and captions of the hardware spike regenerated from the best of 12 runs (HW-010).
- Hardware spike PCB placement: soft ties pull the VBUS_IC and +3V3 current paths together (weights 1.5 and 3.0; in one 12-run batch two boards pass the strict gate and all power drops are under the 50 mV assumption); clean-up re-routes `connection_width` findings (HW-010).

### Fixed
- ADR-0026 lost its criteria, alternatives and comparison sections in the revision 8 commit (`7064a1f`) through a slicing error in an edit script; restored in full with the revision 9 content (plan 09 revision 9, RV-018 note).
- CI regressions of the follow-up commit f7850ce: `scripts/check_license_map.py` now lists the evidence files `ilim-resistors.yaml`, `rlm12.yaml` and `tps3808g01.yaml` (the check failed for them), and a docstring in `scripts/tests/test_fab_check.py` is wrapped to the line limit (two E501 findings and a format finding). `ruff check .`, `ruff format --check .`, `check_license_map.py` and the root pytest (197 passed) pass.
- `scripts/requirements-fab.txt` now pins scipy (moved from `requirements-fab-test.txt`): the power check of
  `scripts/fab_p1.sh` imports it, and the fab-release build job installs only `requirements-fab.txt`, so that job would
  have stopped at the power check. Found by RV-015. Test `test_fab_requirements_cover_what_fab_p1_runs` (fails before);
  `fab_p1.sh` run on 2026-11-21 with only `requirements-fab.txt`: exit 0 (HW-008).
- Spike finishing (`pcb_finish.py`): fiducials are placed before the reference designators, and the designators avoid them.
  Placed after the texts, a fiducial took a designator's spot in each of three passes on the p1b13 board
  (`silk_over_copper`). Test `OnABoard.test_no_designator_on_a_fiducial` (HW-010).
- CI workflows: the `kicad/kicad:10.0` image has no pip; the jobs of `fab-release.yml` and the `hardware` job of `ci.yml`
  install `python3-pip` with apt before `pip install`, and install the pins with `--ignore-installed` (CI run 44827760397:
  pip could not uninstall Debian's `typing_extensions`). Found 2026-11-20; `fab-release.yml` has not run on GitHub yet.
  Tests `test_pip_comes_from_apt_before_it_is_used`, `test_pip_leaves_the_debian_packages_alone` (HW-008, HW-009).
- Spike clean-up grid router (`pcb_fix.py`, also used by the LED ring generator): grid points, and so its vias, sit on the
  0.1 um Specctra grid like the stitch vias. Batch p1b10: ring vias at y = ...8913 mm came back from the router with
  off-centre track ends and the clean-up broke ring stubs it could not lay again. Test
  `test_grid_points_sit_on_the_session_grid` (HW-008).
- Order script `scripts/fab_p1.sh`: `pcb_fabcheck` now runs with `--no-via-in-pad` (owner answer 9; before, a via in a pad
  was reported but did not fail the package), and the power check (drop and full-width path) is a gate. The stored-board
  test runs the power check too. Tests `scripts/tests/test_fab_p1_script.py` (fail on the old script),
  `test_supply_drops_and_full_width_paths` (HW-008, HW-010).
- Spike LED ring generator (`pcb_ring.py`): the data chain is laid before the power and ground stubs. With the stubs first,
  the capacitors turned away from the panel tabs closed four data gaps; the router then left D14 to D15 open in all four
  routings of one placement. Data first completes all 47 ring links on the four P1 placements. Test
  `test_data_chain_is_laid_before_the_power_stubs` (plan 08 section 4.5, HW-008).
- Spike clean-up (`pcb_fix.py`): pieces of the supply nets re-routed by the clean-up took the 0.15 mm default width; on batch
  p1b7 run3 the TPS2553 output current ran through 0.15 mm track to the regulator. Supply nets now keep their current-based
  width (`NET_WIDTH`); +5V pieces at LED ring cell pads keep the 0.25 mm ring stub width. Tests `CleanupWidths` (HW-008,
  HW-010). Boards cleaned up before this change are not checked for thin supply tracks.
- Spike stitcher: new stitch vias sit on the 0.1 um Specctra grid, so router tracks end on their centre (batch p1b6: 18 to 28
  `track_not_centered_on_via` per run made the clean-up rip up good pre-route vias, among them the +5V via of U7 pin 6); a
  plane net without a current rating (GND) is retried at the 0.15 mm default width, so the 0.4 mm-pitch GND pads of U1
  (TUSB321) can be stitched. Regression tests `StitcherViaOnTheSessionGrid`, `StitcherFinePitchGround` (plan 08, HW-008).
- Spike routing flow: the copper reader of the stitcher and of `pcb_check.layout_rules` skipped every locked track (KiCad 10
  writes `(locked yes)` between `width` and `layer`). With `PRESTITCH=1` the pre-route stitch therefore put vias on locked LED
  ring tracks (batch p1b5: shorts and crossing tracks). One reader `pcb_rules.read_segments` for both; regression tests
  `StitcherSeesLockedTracks` and `ReadSegments` (plan 08 section 4.3, HW-008).
- Spike schematic: the DNP spare capacitors C4 and C32 are excluded from the BOM on the symbol too, as on the P1 footprint
  (strict DRC `footprint_symbol_mismatch`, HW-016).
- Hardware spike PCB gate: wires under 0.15 mm (default track now 0.15 mm), dangling vias (removed), hole-to-hole of stitch vias, silk findings (waiver DEV-006, declined by the owner 2026-11-08, off by default); the stitcher joins pads to existing ground vias, layer by layer, in retry passes; 6 new tests. Antenna strip set to the 4.6 mm of the ESP32-C3-MINI-1 datasheet and the module pad area placed outside it (the 21 unconnected module ground pads are gone); 1 mm slot beside the antenna end with a copper keep-out. Placement: VBUS_IC weight and movable-part radius 17.3 mm; +3V3 track 0.3 mm; optional two-pass routing (`KEYFIRST`, `FR_THREADS` in `run_pcb.sh`). VBUS_IC main path (J1, TPS2553 input, C2, TVS1) routed first at 0.6 mm and locked, branches at 0.2 mm (`KEYFIRST=1`); via removal keeps layer changes. Post-route clean-up `src/pcb_fix.py` (grid router for the leftover connections, rip-up of clearance findings, stub removal), 6 tests: on run pl8 the final board has 1 unconnected item (/ILIM) and only the tolerated known findings; the Freerouting step still varies between runs, so the board is not complete and the full flow is not proven repeatable (HW-010, HW-005, ADR-0003, ADR-0012).
- Hardware spike gate: ERC and DRC project files switch on the default-ignored checks (ignored-check maxima now 0); ERC has 0 findings; six repeat routing runs gave 2 complete boards (0 open items) and 4 with 1 to 3 open items; the LED stand-in footprint-filter finding is waived under DEV-002 (HW-010, ADR-0012, DEV-002).
- Hardware spike board uses datasheet-based footprints: ESP32-C3-MINI-1 (figure 11-1 numbers tested), TUSB321 X2QFN-12 redrawn from the TI drawing (the old pattern was wrong), TLV75733P SOT-23-5 for the 3.3 V regulator (ADR-0019, enable tied to input), WS2812B-2020 LED symbol with matching pin numbers (the old pairing mismatched the pins). New: `run_best.sh` (best of N routing runs), `pcb_power_check.py` (voltage drop and plane cuts), router rule to keep VBUS_IC and +3V3 off the plane layers (`OUTER_ONLY`). With the real footprints no run passes the strict gate yet (best: 1 open item); the VBUS_IC path drops 85 mV at 1.5 A in the best run (HW-010, ADR-0004, ADR-0019, DEV-002).
- Hardware spike board: experiment profile `SPIKE_PROFILE=fine` (0.1 mm track and space, vias 0.5 / 0.2 mm, within the JLCPCB multilayer minimums read 2026-11-08), ground plane In1 kept free of signals, J1 footprint copy without edge silk, `run_best.sh` copies the libraries; best of 4 runs is complete, strict-gate clean (waived findings only), ground plane in 1 piece; VBUS_IC drops 59 mV at 1.5 A (above the 50 mV analyst target). ADR-0020 drafted (Proposed, the owner decides) (HW-010, ADR-0020, DEV-006).
- CI: the licence-map check lists the TLV75733P and TMUX1101 evidence files as data (HW-012, ADR-0015).

### Added
- README: status table, schematic and board images and captions refreshed for the spike board with the AND gate and the supply-pin protection (one routed run, strict check fails), new housing model images (exploded and back view) drawn by `mech/render_readme_images.sh`; FreeCAD views are tool output (HW-010, MECH-007, ADR-0014).
- Hardware spike schematic: SN74LVC1G08 AND gate for GATE_OK_RB (HOLD_OK and FAULT_N), GPIO4 and GPIO1 freed, series resistor, 100 nF and BZX84C5V1 zener at the TUSB321 and TMUX1101 supply pins; six new tests; PCB stage not rerun (HW-010, HW-012, ADR-0016, ADR-0018).
- Hardware: datasheet evidence for the BZX84C5V1 zener and the SN74LVC1G08 AND gate (quotes checked against the PDF pages); surge analysis rerun with the zener datasheet corners (HW-010, HW-012, ADR-0016, ADR-0018).
- Mechanics: housing model completed with lid spigot and snap bumps, PCB posts, button hole and a bayonet detent; tolerance check for the spigot, skirt and ledge (MECH-001, MECH-004, MECH-005, MECH-007, MECH-009).
- Mechanics: FreeCAD coupon generator for the diffuser (3 plates, 3 spacer rings) and the bayonet floor; bayonet lock concept (entry sector, lips, stop) with a mating accessory ring and a model check of the lock action (MECH-002, MECH-007, ADR-0014).
- Mechanics: first FreeCAD housing generator (base with USB-C window, annular bayonet recess, three PCB snap hooks, lid), shared dimension file and a tolerance check with tests; evidence report `mech-housing-first-model.md` (MECH-001, MECH-004, MECH-006, MECH-007, MECH-009).
- HW-012 evidence files for the TLV75733P (supply, current and thermal-resistance ratings) and the TMUX1101 (supply ratings): 9 claims, all `unverified` (AI-extracted, quotes checked against the PDF pages by `scripts/check_part_evidence.py`, 0 errors); the PDFs are in the local datasheets folder, not in the repository (HW-012, ADR-0017, ADR-0019, ADR-0016).
- Gate logic `sw/app/src/gate.c` with 20 unit tests on native_sim (SW-005, SW-006, SW-007, SW-009, SW-010; host level only, 20 of 20 pass, mutation check 8 of 20 fail, gcc and clang-tidy clean); evidence report `docs/verification/reports/sw-gate-unit-tests.md`; no Zephyr binding, no target build, no bench (plan 07).
- Plan 07 increment 1: ztest smoke test under `sw/app/tests/gate/` (builds and passes on native_sim/native/64 with Zephyr v4.5.0 locally; tests no requirement); `scripts/ci_sw.sh` runs twister on `native_sim/native/64` (plan 07, SW-005, SW-009).
- Owner accepted ADR-0014 (annular bayonet, coupon test as the gate, dovetail fallback) and approved MECH-006, MECH-007 and MECH-008 on 2026-11-07 (ADR-0014, MECH-006, MECH-007, MECH-008).
- Owner approved MECH-001, MECH-002, MECH-003, MECH-004, MECH-005 and MECH-009 on 2026-11-07; MECH-006 to MECH-008 wait for ADR-0014 (MECH-001 to MECH-009).
- Mechanical requirements MECH-001 to MECH-008 redrafted (version 0.2, all Draft) to match ADR-0003, ADR-0011 and ADR-0014 (PETG, off-centre module, annular bayonet, thermal limit, window and label), new MECH-009 (PCB snap hooks and reopening) with stub TC-309; open items are listed in the journal (MECH-001 to MECH-009, ADR-0011, ADR-0014).
- TC-210 step 4 extended: peak of VBUS_IC and +5V at hot-plug against the part ratings, with a trigger for the fallback options; owner chose to measure first (HW-010, TC-210, ADR-0010).
- Part-rating table for VBUS_IC and +5V (`docs/verification/reports/analysis-vbus-5v-part-ratings.md`): the TPS2553 (7 V), the 3V3 regulator (6 V) and the LED placeholder (5.3 V) are not safe against an 8 to 15 V TVS clamp, so the surge problem is wider than the two pins that got a resistor and a zener; three options for the owner, nothing decided (HW-010, ADR-0010, ADR-0016, RV-011).
- Owner approvals of 2026-11-07 (second round): SW-009 and HW-010 amendments folded in as Approved, the TC-105, TC-106, TC-107, TC-109, TC-110, TC-210 and TC-213 procedures approved as working procedures (nothing run), plan 07 approved with conditions; RV-011 resolution record (SW-009, HW-010, RV-011, TC-105, TC-210).
- ADR-0018 Accepted by the owner as option E: FAULT_N is combined with the hold-off readback by an AND gate that replaces the buffer, so GPIO1 and GPIO4 are free for the orientation sensor and the firmware still sheds on a limiter fault; SW-009 and HW-010 text changes are Proposed (ADR-0018, SW-009, HW-010, HW-011).
- Owner approvals of 2026-11-07 recorded: ADR-0019 Accepted (standard-package regulator with a firmware limit); SW-005 single-input table and unknown states, SW-007 flag, clock and watchdog counting, SW-010 timeout of [8] s folded into the requirements; ADR-0010 update for open points 3 and 4 (ADR-0019, ADR-0010, SW-005, SW-007, SW-010).
- Proposed single-input rewrite of SW-005 criterion 4 and TC-105 cases (g) and (h): one CC input, unknown states are readback inconsistencies (SW-005, RV-011 findings 8 and 9).
- ADR-0018 (FAULT_N input removed for the sensor pins; the assistant recommended keeping it, the owner chose removal) and ADR-0019 (3V3 regulator, standard package with a firmware limit; the assistant recommended the pad package), both Proposed; Proposed amendments of SW-007 and SW-010 for the flag, elapsed-time clock and watchdog resets (ADR-0018, ADR-0019, SW-007, SW-010, SW-009, HW-010).
- Goldfish review RV-011 of plan 07, the draft test procedures and the supply-pin, regulator and CC-pin analyses: 17 merged findings, outcome "approved with actions"; fixes to the surge script (zener corners, 27 tests), TC-106, TC-107, TC-109, TC-110 and TC-210 (RV-011, HW-010, SW-005, SW-006, SW-007, SW-009, SW-010).
- Regulator heat analysis (`hw/sim/scripts/regulator_heat.py`, tests): the TLV75733P is cool in normal Wi-Fi use; a firmware download is marginal in the standard package; continuous transmit fails. DYD (exposed pad) variant recommended. Owner approved the supply-pin surge values on 2026-11-07. Options note for the TUSB321 CC pins (HW-010, HW-013, ADR-0016; `docs/verification/reports/analysis-regulator-heat.md`, `analysis-cc-pin-protection.md`).
- Supply-pin surge analysis: ngspice script and tests derive 1 kohm (TMUX1101) and 470 ohm (TUSB321) series resistors with 100 nF and a 5.1 V zener at the pins; Proposed amendment of HW-010 updated; zener datasheet not read, nothing measured (HW-010, ADR-0016, DEV-001; `docs/verification/reports/analysis-supply-pin-surge.md`).
- Owner decisions of 2026-11-07 recorded as Proposed amendments: series resistor and 5.1 V zener at the TMUX1101 and TUSB321 supply pins, TLV75733P as the 3V3 regulator candidate, FAULT_N given up for the orientation sensor pins, SW-005 gives the middle step for 1.5 A and 3 A chargers until TC-213 (HW-010, HW-011, SW-005, SW-009, HW-013; `docs/journal/2026-11-07-surge-regulator-pins-steps.md`).
- Firmware plan 07 for the gate logic slice (Draft, not reviewed) with the spike GPIO pin map taken from the generator, and a draft TC-107 procedure; the shortlist report now carries the TUSB321, TPS3840 and TLV757P datasheet readings (SW-005, SW-006, SW-007, SW-009, SW-010, HW-010; `docs/plans/07-gate-firmware.md`).
- Draft test procedures for TC-210, TC-213, TC-105, TC-109 and TC-110 (HW-010, HW-013, SW-005, SW-009, SW-010; Draft, not reviewed, not run) and a shortlist report for TVS1 and the 3V3 regulator with the finding that a plain 5 V TVS cannot clamp below the 6 V switch supply rating (`docs/verification/reports/shortlist-tvs1-3v3-regulator.md`; HW-010, HW-012, ADR-0016).
- Owner decisions of 2026-11-07 recorded: ADR-0003 Accepted (antenna option A first, spike 7.2 as a hard gate), ADR-0011 Accepted for the prototype only (concept B, FDM, PETG); ADR-0014 stays Proposed; M4 sag band to be measured first. Record: `docs/journal/2026-11-07-adr-0003-0011-decisions.md` (ADR-0003, ADR-0011, ADR-0014, HW-010).
- Spike generators and test fixtures brought to the approved HW-010 values: E96 ILIM resistors, six 100 nF hold-off capacitors, TMUX1101 supply from VBUS_IC, CC_OK_3A path deleted; 185 spike tests pass; routing and the routed DRC fixtures are not regenerated (HW-010, ADR-0016, ADR-0012).
- ADR walkthrough of 2026-11-07: ADR-0001, ADR-0002, ADR-0004, ADR-0005, ADR-0006, ADR-0007, ADR-0008, ADR-0010, ADR-0012, ADR-0017 and ADR-0016 Amendment 2 Accepted by the owner (with the open conditions recorded in each ADR); ADR-0003, ADR-0011 and ADR-0014 revised and not accepted. Record: `docs/journal/2026-11-07-adr-approval-walkthrough.md`.
- Goldfish review RV-010 of the HW-010 gate bundle (HW-010, SYS-020, SW-005 to SW-009, ADR-0016 Amendment 2): 29 findings, outcome "rejected for approval as written" until the open actions close; no approval. `hw/sim/scripts/amendment2_numbers.py` reproduces the Amendment 2 hold-off and ILIM numbers. Corrections: ADR-0016 option C score 57 and Related list, SYS-020 worst case about 1175 ms for the six 100 nF set. HW-010 Proposed text is consolidated into one revision (current-values table, acceptance criteria to add, open owner decisions); notes added to the 2026-11-05 owner record and DEV-001 for the E96 resistor decision. Proposed drafts for RV-010 findings 15 and 26: SYS-020 reset wording, SW-005 count as the normative criterion, SW-006 time base, SW-007 retained-flag options, SW-009 shed and reset handling. Owner decisions of 2026-11-07 recorded in the journal; Draft HW-013 (thermal limit at the top step) and SW-010 (watchdog restart to the lowest step) with TC-213 and TC-110; Proposed DEV-005 (ADR-0016 accepted before its review); SYS-020 Proposed text for the three steps; TUSB321 debounce note (datasheet states 133 ms typical, no maximum). Owner decision 3 (TMUX1101 over-voltage removed by design): analysis `analysis-tmux1101-supply-from-vbus.md`, ADR-0016 update, HW-010 Proposed revision, DEV-001 and RISK-045 notes (switch supply from VBUS_IC; Proposed, nothing built or measured).
- Spike library tables (plan 06 A-11; spike only, nothing Approved): the generators write the project file, `sym-lib-table`, `fp-lib-table`, a `busylight_gate` symbol library and a `CUSTOM` footprint library next to the generated schematic and board, so kicad-cli resolves every library nickname. ERC `footprint_link_issues` 96 to 0 and `lib_symbol_issues` 241 to 0, placed DRC `lib_footprint_issues` 93 to 0; the matching caps are removed from `known-open-violations.json` (HW-010, ADR-0012).
- PCB spike G3 second run and plan 06 amendments A-8 to A-10 (Proposed, owner-decided 2026-11-06; nothing Approved): `planes=inner` for the router (only the inner GND plane visible; `pcb_rules.router_keeps_zone`, early argument check in `run_pcb.sh`, tests first), cap investigation (ERC and DRC caps not raised; the excess is +7 net parts and the missing library table) and the observed `inner` run: M1 = 16, M2 = 92, M3 = 0 (gate not met). Spike only.
- ADR-0016 Amendment 2 (Proposed, nothing Accepted): ILIM select switch TMUX1101DCKR (fallback TS5A3166DBVR), 0.1 % ILIM resistors 47.0 k / 56.2 k / 27.4 k + 301 ohm and hold-off capacitor set 6 x 100 nF C0G (owner choice 2026-11-06; earlier 220 + 220 + 100 + 68 nF), with four alternatives, weighted criteria from `analysis-ilim-switch-replacement.md`, the open 3V3-off condition (DEV-001, RISK-045), bench check TC-210 (d) and critical review (ADR-0016, HW-010, SYS-020).
- Owner decisions of 2026-11-05 (second record, `docs/verification/reports/owner-decisions-2026-11-05-b.md`) as Proposed amendments only, nothing Approved: SYS-020 time to the raised limit [2] s; HW-010 ILIM select switch TMUX1101DCKR (fallback TS5A3166), ILIM resistors 47.0 k / 56.2 k / 27.4 k + 301 ohm, hold-off capacitor 220 + 220 + 100 + 68 nF C0G; SW-005, SW-006, SW-007 and SW-009 amendments; Draft outlines of TC-105, TC-109 and TC-210; DEV-001 (Proposed) and RISK-045 for the 3V3-off ILIM condition (SYS-020, HW-010, SW-005, SW-006, SW-007, SW-009, ADR-0016).
- PCB spike clean-route plan 06 (Approved by the owner 2026-11-05 for the spike only), goldfish review RV-009 (readiness NO-GO three times; last fixes not re-reviewed) and the G1 geometry work: 16 smaller LED stand-in footprints, largest-dimension check (59.8 mm spike limit), placement acceptance rules and DRC fixtures. Work in progress: strict placed DRC still fails (29 `footprint_symbol_mismatch` against a cap of 13), T13 and the overlap-penalty floor are not written, nothing is routed.
- PCB spike G2: all PCB rule numbers in `pcb_rules.py` (pure Python), a generated `.kicad_dru`, `net_class_widths`, a per-ref DRC allow-list with DEV-002 (proposed, not approved) and a placement overlap floor (plan 06; spike only; nothing Approved).
- PCB spike G3 (first run, plan 06 amendment A-7; spike only, nothing Approved): `run_pcb.sh` checks the pinned Freerouting jar hash, stitches, writes `run_meta.json` and runs the `stitched-4l` DRC; metric helpers `count_unrouted` (M1) and `count_unconnected` (M2); the stitcher exits non-zero when a pad fails. Result of the run: M1 = 0, M2 = 71 (GND), so the G3 pass criterion is not met. DEV-003 and DEV-004 proposed, not approved.
- README gallery shows the spike schematic (two legible crops) and the 4-layer spike board (3D view and copper layers), exported by `hw/kicad/spike-gate/render_readme_images.sh`; the captions state the numbers of that run (Freerouting left 40 nets unrouted; after stitching 252 DRC violations and 57 unconnected items on 4 nets; the strict waiver check of 475 items was not rerun on this routing) and that nothing is approved (README, ADR-0012).
- Datasheet evidence format (ADR-0017 Proposed, HW-012 Draft, TC-212 stub): `hw/evidence/` with a JSON Schema and per-part YAML files for the components of the full-board schematic, `scripts/check_part_evidence.py` and `scripts/part_evidence.py`. All 348 entries are `unverified` or `source-missing`; none is verified (`docs/verification/reports/part-evidence-fill-report.md`).
- Spike (ADR-0012 Proposed, nothing Approved): full-board schematic, exclusive current-limit steps (U13), E192 0.1 % ILIM values, parallel C0G hold-off capacitors, and a script-generated PCB with placement, a mechanical outline taken from the `spike/mech-concept` spike and a Freerouting run, in `hw/kicad/spike-gate/`; the board is not DRC clean and not fully routed (`docs/verification/reports/spike-pcb-placement-routing.md`).
- Draft process rules for generated hardware designs (`docs/process/hw-generated-design-guardrails.md`): strict ERC/DRC, independent checks, protected paths, sign-off gates; the spike ERC/DRC scripts now fail on any finding that is not on a visible waiver list (`hw/kicad/spike-gate/known-open-violations.json`).
- Consolidation record of the branches `docs/review-actions`, `spike/hw-gate` and `feature/part-evidence` (`docs/verification/reports/consolidation-2026-11-05.md`) with the open owner decisions.
- HW-006 (Draft) no longer lists UART test points; HW-010 proposed amendment names GPIO20 and GPIO21 for the two gate-enable readbacks (owner choice "test point route", 2026-11-04; module datasheet read: pins 30 and 31 are not strapping pins; GPIO21 outputs ROM messages at start-up) (HW-006, HW-010, SW-009).
- Reports of the gate spike moved from branch `spike/hw-gate` into `docs/verification/reports/`: gate fragment, own schematic writer, goldfish reviews of versions 2 and 3a, datasheet evidence for the gate logic, the supervisor and the inverter (HW-010, ADR-0016). The spike code stays on the branch and is not merged (ADR-0012 is Proposed).
- Proposed amendment to HW-010 (readback inputs of the hold-off and gate enable states for SW-009); the Approved text is unchanged until the owner confirms.
- SW-009 (follow the hardware gate state and shed load when the gate closes, Draft, needs a readback line that HW-010 does not have yet) and TC-109 stub; RISK-044 extended with the findings of the second goldfish review of the gate (SW-005, HW-010).
- RISK-044 (hold-off supervisor of the current-limit gate fails or is mis-set) and a TC-210 extension (VBUS dip restart, shorted or open delay capacitor, supervisor output forced high); candidate supervisor and datasheet evidence are on branch `spike/hw-gate` (HW-010, RISK-042).
- Re-run of the ADR-0012 gate G1 stand-in spike (`docs/verification/reports/hw-flow-g1-rerun.md`, Draft): ERC, parity, DRC 0 and identical dumps reproduced locally; CI, Freerouting run, pinning and the peg-azimuth decision still open; ADR-0012 stays Proposed on the owner's choice "not yet".
- HW-010 (hardware current limit on the USB input) Approved by the owner 2026-11-04 on instruction in the session; uncovered faults stay listed (RISK-029, RISK-042).
- HW-003 (USB-C power input) Approved by the owner 2026-11-04 on instruction in the session.
- CC detection IC chosen by the owner: TUSB321, PTN5150A as fallback if the IC ambient exceeds 70 C (ADR-0016, HW-003, RISK-043).
- Licence record: per-file licence tag counts of the pinned Zephyr, MCUboot, hal_espressif and Mbed TLS trees, NonCommercial definition from the licence text; HW-010 hold-off upper limit of [600] ms (spike finding F7: a plain CMOS threshold is too loose for the timer).
- Start-up hold-off of at least [200] ms on the high-step gate: HW-010 acceptance criteria, TC-210 procedure points, ADR-0016 amendment (owner to confirm) and RISK-042 (reason: the IC output level before its first debounce is not stated in the datasheet).
- Datasheet evidence record for the CC detection IC (`docs/verification/reports/cc-ic-datasheet-evidence.md`, Draft): TUSB321 Rev C read (supply from VBUS, 0 to 70 C, CC pins 6 V, thresholds, OUT1 and PORT behaviour; power-up output level not stated); PTN5150 Rev 1 (older) as a second-source hint; RISK-026 and RISK-043 updated.
- Spike on branch `spike/hw-gate`: owner decisions of 2026-11-05 (b) implemented in the schematic generators (TMUX1101 ILIM select switches U14 and U15 with 100 kohm pull-downs on SEL, ILIM resistors 47.0 k / 56.2 k / 27.4 k + 301 ohm at 0.1 %, hold-off set 220 + 220 + 100 + 68 nF C0G), placer weights for the gate rules, analysis re-run (step windows, hold-off window, readback margin) and report `docs/verification/reports/spike-decisions-2026-11-05-b-implementation.md` (Draft; no bench run, stock and 3V3-off open item not closed).
- Desk reports of 2026-11-05 on the hardware gate spike (all Draft, nothing Approved): ILIM select switch replacement for the 2N7002 with a 3V3-off sequencing addendum (TMUX1101 recommended, open item), JLCPCB stock and purchasable C0G hold-off sets, Zephyr USB-Serial-JTAG console and GPIO pull facts for SW-009, and a SW-005 against hold-off timing analysis (SYS-020 1 s not met) with script and test (`hw/kicad/spike-gate/sim/sw005_holdoff_timing.py`). Not bench-run; stock figures unconfirmed.
- Spike on branch `spike/hw-gate`: the ADR-0016 gate fragment built from code (SKiDL), checked with KiCad ERC, a netlist parity check and a truth-table test; report `docs/verification/reports/spike-hw-gate-fragment.md` (Draft; exploratory, no design content for `main`).
- ADR-0010 open points 1 and 2 decided by owner instruction (recommended options: first step 506 to 623 mA with a 500 mA firmware budget; top step 1366 to 1577 mA with a 1350 mA firmware value); HW-010 and RISK-027 carry the numbers. ADR status stays Proposed.
- Licence compatibility table and record of licence facts (`docs/regulatory/technical-file/05-cybersecurity/licence-compatibility.md`, Draft): KiCad libraries, Mbed TLS, Noto Sans and Creative Commons facts checked against sources on 2026-11-04; Zephyr and MCUboot top-level licence files read, Mbed TLS pinned commit and the Espressif binary module declaration (Apache-2.0) read; Espressif's own terms not verified (ADR-0015 item 8, RV-008 P14).
- Draft software requirements SW-005 to SW-008 (raise the USB current step only after a stable reading, reduce load before lowering, back-off after brown-out, tolerance of Power Delivery traffic) and test stubs TC-105 to TC-108; closes the RV-008 action "write the software requirement" (RV-006 S3 to S6). Status Draft; owner approval needed.
- Goldfish review RV-008 of ADR-0015 and ADR-0016 with amendments (gate covers every step above the first; independence only against firmware faults; RISK-042 and RISK-043; `LICENSE.md` reworded to what the licences grant; SPDX headers on the remaining `sw/` files; outside pull requests paused in the template).
- ADR-0015 (licensing corrected and completed) and ADR-0016 (independent hardware gate for the high current step) Accepted by the owner 2026-11-04; ADR-0013 and ADR-0009 are Superseded. Applied: `.claude/` under Apache-2.0, `NOTICE` file, SPDX headers on code files, `LICENSE.md` with the purchased-unit grant, the non-commercial reading, name, patents and authorship points (not legal advice).
- Options sheet for the back layout (five options with the accessory mounted); `scripts/check_license_map.py` (fails when a code file falls under the documentation licence, in CI); HW-003 and HW-010 drafted for the CC detection IC gate of ADR-0016; NEED-012 renamed with an acceptance criterion. Owner instruction to follow the recommended options recorded in ADR-0015 and ADR-0016 (status stays Proposed).
- Review actions: spike report on the layout of the back (annular bayonet proposed; spike code on `spike/mech-back-layout`), ADR-0015 (licensing corrected and completed; would supersede ADR-0013), ADR-0016 (independent hardware gate for the high current step; recommends a CC detection IC ANDed with the firmware GPIO).
- Goldfish reviews RV-005 (ADR-0013 licensing), RV-006 (ADR-0009 and ADR-0010 USB power) and RV-007 (ADR-0014 and the orientation and mounting requirements); RISK-035 to RISK-041; outside contributions paused until the contributor terms have a legal check; REUSE code globs extended.
- Diagram check (`scripts/build_diagrams.sh --check`) compares structure, labels and colours, not coordinates, because text widths depend on the machine's font metrics (`scripts/svg_normalize.py`, with tests).
- Diagrams use an explicit font (Noto Sans) and CI installs it, so box sizes do not depend on the machine's default font.
- README gallery: architecture block diagram, stand-in KiCad board render and placeholder housing concept preview (image of the mechanical spike under `docs/verification/reports/images/`).
- CI docs job: PlantUML 1.2026.8 pinned by SHA-256 (the Ubuntu package draws differently); block diagram uses the built-in layout engine so Graphviz versions cannot change it.
- Draft requirements NEED-020 to NEED-022 (orientation, clock mode later, mounting), SYS-047, HW-011, MECH-007, MECH-008 and test-case stubs TC-047, TC-211, TC-307, TC-308; MECH-006 rewritten for the label on the back.
- ADR-0014 (mounting interface on the back; Proposed: printed bayonet, fallback dovetail). Owner decisions recorded 2026-11-04: unit mounted horizontal and vertical, label on the back, orientation sensor added, clock mode in a later release.
- Goldfish review RV-004 of plan 05 and ADR-0011 (housing): not ready for approval; 30 findings with resolutions and owner decisions listed. Plan 05 section 3 scores corrected to the ADR values.
- CI fixes after the first GitHub run: npm lockfile for the diagram tools, root user in the KiCad container, pinned FreeCAD AppImage, virtual environment for the software job.
- Risk register: RISK-027 to RISK-030 (hardware current limit band, 5 V rail collapse, limit step stuck high, limit switch availability) from ADR-0010.
- Continuous integration (`.github/workflows/ci.yml`): documentation checks, Python tool checks, hardware (`scripts/ci_hw.sh`), mechanical (`scripts/ci_mech.sh`) and software (`scripts/ci_sw.sh`) jobs; `pyproject.toml` for the tool environment. Hardware and mechanical jobs report NOT RUN until sources exist.
- README rewritten as a project front page (honest status, planned features, roadmap); licences added: Apache-2.0 for code, CC BY-NC-SA 4.0 for documentation, hardware and mechanics (`LICENSE.md`, `LICENSES/`, `REUSE.toml`, `reuse lint` in CI); ADR-0013 (licensing, Accepted by the owner 2026-11-04); draft contribution terms in `CONTRIBUTING.md`.
- ADR-0012 (hardware design flow, Proposed) with goldfish review RV-003, a KiCad feasibility spike report (Draft) and RISK-032 to RISK-034.

### Changed
- HW-010 revision: the pull-down sentence now describes the network that the spike draws (10 kohm and 100 kohm in parallel on each gate enable net); no part change (HW-010, SW-009).
- DEV-005 (ADR-0016 accepted before its own goldfish review) Approved by the owner on 2026-11-07 with updated compensating measures; DEV-001 stays Proposed until TC-210 (d) (DEV-005, DEV-001, ADR-0016).
- HW-013 Approved by the owner on 2026-11-07 (thermal limit in the closed housing at the top current step); bracketed figures stay open and the TC-213 procedure is still to be written (HW-013, SYS-020, RISK-005).
- SW-010 Approved by the owner on 2026-11-07 (watchdog serviced only from the select loop, restart returns the select outputs to low within [10] s); the select pin state at reset is checked on the prototype (SW-010, SYS-020, SYS-027).
- SW-009 Approved by the owner on 2026-11-07 with all three amendments folded in (HOLD_OK_RB validity, GPIO20 and GPIO21 without pulls, USB-Serial-JTAG console, shed in [X] ms, reset after a gate closure tolerated); [X] is set from a measured rail hold-up and the Kconfig symbols are not verified by a build (SW-009, SW-007, SYS-020).
- SW-007 Approved by the owner on 2026-11-07 with both amendments folded in (hold-off brown-out definition, retained flag with HOLD_OK_RB-only fallback); retention of the flag is checked on the prototype (SW-007, SW-009).
- SW-006 Approved by the owner on 2026-11-07 with both amendments folded in (shed within [50] ms of the stable fall or an enable readback fall, select low after; reset wording aligned with SYS-020); the [50] ms stays open until a latency is measured (SW-006, SYS-020, SW-009).
- SW-005 Approved by the owner on 2026-11-07 with both amendments folded in (6 equal reads at 100 ms, 700 ms from HOLD_OK_RB rising, restart after every falling edge, value table); bracketed values stay open until measured (SW-005, SYS-020).
- HW-010 revision approved by the owner on 2026-11-07 (TMUX1101 switches on VBUS_IC, E96 resistors, six 100 nF hold-off, nine bench criteria, CC_OK_3A deleted); the debounce margin, the M4 sag band and the unchosen TVS1 and 3V3 regulator stay open (HW-010, ADR-0016).
- SYS-020 Approved by the owner on 2026-11-07 with the three amendments folded in: [2] s to the raised limit, a reset after the gate closes is allowed with restart at the lowest step, and three current steps with step 2 as the thermal cap. Bracketed values stay open until measured (SYS-020, HW-010, HW-013).
- Spike on branch `spike/hw-gate-pcb-g3`, owner decision 2026-11-06: ILIM resistors in the schematic generators are now one 56.9 k (R_ILIM2) and one 27.7 k (R_ILIM3), 0.1 % 0603, R_ILIM1 stays 47.0 k; R_ILIM3B (301 ohm) and its net are removed (53 nets, 92 components); fixtures, tests, `sim/ilim_steps.py` and the implementation report are updated. These two values have no confirmed LCSC or JLCPCB source at 0.1 % 0603. Windows 504.2 to 616.6, 929.6 to 1085.9 and 1381.2 to 1566.7 mA; Freerouting and bench not run; nothing Approved (HW-010, SW-009, ADR-0016).
- Zephyr pin in `sw/west.yml` moved from v4.2.0 to v4.5.0 (owner approval 2026-11-03).

### Added
- FreeCAD spike model results (branch `spike/mech-concept`, not merged): skirt fixed, module offset 1.0 mm gives about 15 mm antenna clearance, USB-C variant V1 (board tab) passes all checks at 57.43 mm.
- RISK-031: the FreeCAD spike model shows the USB-C receptacle collides with the LED ring; options listed in the owner guide.
- Mechanical plan 05 revised (Draft): label on the underside and a flat-lying unit assumed (owner confirms), housing 53.0 x 16.5 mm with PCB 46 mm, antenna rules split between MECH-003 and an ADR-0003 finding; analysis re-run in the concept report (section 8).
- Draft mechanical plan 05, ADR-0011 (housing concept: opaque base plus translucent lid, FDM, PLA excluded) and the concept analysis report (light, thermal, tolerance); no CAD yet.
- Owner input recorded: read USB-C CC with the ADC (ADR-0009) and have a hardware current limit; draft HW-010 and TC-210; ADR-0004 item 4 updated.
- ADR-0010 (Proposed): hardware current limit on the USB input, recommends TPS2553 with a firmware-switched limit resistor (HW-010).
- Draft RISK-024..026 from ADR-0009; ADR-0009 summarised in the owner guide.
- Draft ADR-0009 (Proposed): USB-C power input and detection of the advertised source current; ADC read of the CC lines recommended, dedicated CC IC as fallback; cap value and ADC-or-IC choice left to the owner (SYS-020, HW-003).
- Power budget addendum for 900 and 1350 mA limits; SYS-001 rationale notes that the brightness figure depends on the source's current.
- Owner decision recorded: allow a higher USB current when the source advertises it (SYS-020, HW-003, ADR-0004, RISK-003); default stays [500] mA.
- PC prototype record for the ADR-0004 current limiter (scratchpad only): 41.7 M test frames without failure, 532 B code on rv32imc; proposals for level mode and the below-dark-current case noted in ADR-0004.
- PC prototype of the ADR-0005 extractor and mapper (scratchpad only): 27 tests, 5 million fuzz executions without crash, 4057 B and 512 B stack on rv32imc; document nesting limit and number wording added to SW-001 and ADR-0005 (Draft/Proposed).
- Spike 7.5 paper power budget with datasheet sources: at 500 mA the Wi-Fi TX peak leaves 46 mA (LDO) to 148 mA (buck) for 16 LEDs; USB current-limit decision added to the owner guide.
- Spike 7.1 E12 and E2b follow-up (build only): WPA2-Enterprise costs about +70 KB flash and +6 KB static RAM; the step-7 jump is flash padding; TLS heap can be reduced in builds that link.
- Draft vulnerability handling and disclosure process (`05-cybersecurity/vulnerability-handling.md`); contact and legal entity open.
- Owner review guide (`docs/plans/04-owner-review-guide.md`): approvals waiting, open decisions with recommendations, findings so far, side effects.
- Spike 7.1 E2b size ladder (build only): throw-away product-like image is 792 KB signed (43 % of the default slot), static RAM 285 KB of 360 KB; flash looks less critical than RAM.
- ADR-0007 evidence update and RISK-023: secure boot and flash encryption are not available in the Zephyr sysbuild MCUboot for the C3; the standalone Espressif port with a pinned ESP-IDF HAL is the only route found (owner decision pending).
- Draft spike 7.1 runbook for the first hardware session (read-only kit checks, flashing the two E1 images, log format); not run.
- Consistency pass over ADRs, key-management draft, SYS-036, RISK-006/008/009 and the spike reports (stale text and contradictions fixed after a fresh-reviewer check).
- Consistency pass over plans 02/03, ADR headers and spike reports.
- Spike 7.1 E2a paper flash budget: default 4 MB layout leaves 128 KiB unassigned; image limit at 75 % of a slot is about 1.31 MiB (1.38 MiB with unused areas reclaimed).
- Chip revision >= v0.3 (secure boot) added to HW-008 and ADR-0007; virtual-eFuse rehearsal noted in ADR-0007 and RISK-022.
- Spike 7.1 E11a partial record: ECDSA P-256 build works (bootloader 5 KB smaller than RSA-2048); virtual eFuse option and ESP32-C3 revision >= v0.3 requirement for secure boot found in source; secure boot and encryption not yet built.
- Spike 7.1 E1 build record: hello_world and Wi-Fi shell build for `esp32c3_devkitm` with Zephyr v4.5.0 and SDK 1.0.1 (build only; nothing flashed or run); default 4 MB flash layout and default signing key noted.
- Desk-survey findings applied to the Proposed ADR-0004, 0006, 0007, 0008 and the key-management draft: SPI LED route, radio-first rule for keys and passphrases, PSA key handling, one-client access point, RSA-3072 secure-boot key vs EC256 release key, flash `write-block-size` and swap-mode checks.
- Owner decision recorded: a lost or leaked release key means a recall of locked units (no second key in the bootloader); ADR-0007, key-management document and RISK-006 updated.
- Spike 7.1 E0 pass 2: Zephyr v4.5.0 source read (AP+STA in the driver, WPA2-Enterprise mapped to the Espressif blob, SPI LED route, hardware random source needs the radio on, EC256 signing fits secure boot plus encryption).
- Spike 7.1 E0 desk survey report (documentation only, nothing built): ROM secure boot signs the bootloader with RSA-3072, only an SPI `ws2812` route found for the LEDs, AP+STA, captive-portal DNS and WPA2-Enterprise unconfirmed on the C3.
- Goldfish review RV-002 of plan 03 (spike 7.1); plan 03 revised: desk survey E0, split E2/E11, power experiment E14, secrets handling, kit accounting and evidence rules.
- Draft plan 03 for spike 7.1 (Zephyr on ESP32-C3): 13 experiments with pass rules and fallbacks, shopping list, branch and report rules.
- Draft hardware requirements HW-001..009 and mechanical requirements MECH-001..006 with test case stubs TC-201..209 and TC-301..306 (no CAD work done; values in brackets are proposals).
- Goldfish readiness pass recorded in RV-001: verdict NO-GO with ranked blockers; plan 02 header and ARCH note brought up to date.
- Draft key-management document (`docs/regulatory/technical-file/05-cybersecurity/key-management.md`): key inventory, signing rules, production steps, rotation and recovery; owner review pending.
- Draft requirements SYS-043 (secure boot and flash encryption), SYS-044 (SBOM), SYS-045 (vulnerability handling, 5-year support), SYS-046 (recovery of locked units), SW-001..004 (input limits, session limit, fuzz tests, image confirmation) with test case stubs TC-043..046 and TC-101..104; SYS-026 now says what the 25 % margin refers to.
- Owner input on market (EU), distribution (open source first, sellable later), support period (5 years) and security (secure boot and flash encryption wanted) recorded in the regulatory applicability, ADR-0007 (revised to a staged secure boot and flash encryption plan, still Proposed) and RISK-022.
- Risk register with 21 draft risks (RISK-001..021), architecture blocks ARCH-001..019 in `docs/architecture/blocks.md`, and a first regulatory applicability assessment with open compliance questions and draft compliance-matrix rows (none verified, owner has not reviewed).
- Project structure for Zephyr software (`sw/`), KiCad hardware (`hw/`) and FreeCAD mechanics (`mech/`).
- Engineering process: lifecycle with gates, Elephant-Goldfish planning, document control, verification strategy.
- Standards: C coding (CERT C and MISRA C subset), hardware and mechanical design-for-X, writing (ASD-STE100 based), diagrams as code.
- Regulatory scaffolding for EU market access: applicability assessment, compliance matrix, technical-file index.
- Traceability check (`scripts/check_traceability.py`), documentation style check (`scripts/check_docs_style.py`), diagram build (`scripts/build_diagrams.sh`).
- Stakeholder needs (NEED-001 to NEED-019) and draft system requirements (SYS-001 to SYS-031) for the first release:
  Jenkins status by push and by REST polling, 16-LED RGB ring, Wi-Fi provisioning with web interface, OTA update,
  user-uploaded CA certificates, per-unit password, 3D printed housing.
- Draft user documentation skeleton, `CONTRIBUTING.md` and `SECURITY.md`.
- System design plan 02 with ADR-0002 to ADR-0008 (platform ESP32-C3, antenna, LED drive, mapping model, provisioning, update and boot security, transport protection) and goldfish review record RV-001. All ADRs are Proposed (ADR-0007 was Accepted and set back by the owner after the review).
- Draft system requirements SYS-032 to SYS-042 (level display, push liveness, LAN transport protection, own certificate, WPA2-Enterprise headroom, PC simulation, Wi-Fi range, web password rules, push request format, factory reset scope, device name) with test case stubs.
- Claude Code project instructions and skills (`CLAUDE.md`, `.claude/skills/`).
