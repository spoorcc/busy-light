# Review Record RV-018

- **Subject:** `docs/plans/09-centre-button.md` revision 1 (commit `bcf5263`), resolved in revision 2
- **Type:** Design
- **Date:** 2026-11-23  **Reviewer(s):** four stateless goldfish subagents (comprehension "C"; antagonistic: testability and
  requirements "T", mechanics and failure modes "M", hidden dependencies and integration "I"), then one implementation-readiness
  goldfish "R"; resolution by the assistant (Elephant). **Independent?** no (AI reviewers of an AI-written plan; the owner has
  read the interview questions but not the plan text)

## Protocol
1. Comprehension (C): the restatement matched the intent (separate centre disc, three open axes: switch place, support concept, switch
   part; ADR-0026 decides). It listed 20 points it could not reconcile; they are rows C1 to C20 below.
2. Antagonistic review: three goldfish in parallel, 26 + 26 + 22 rows. They recomputed the geometry and statics independently.
3. Resolve: the assistant checked the blocking claims against the repository and by calculation. **Confirmed:** the footprint origin of U9 is not
   the body centre (F.Fab outline local y -11.0 to 5.6, rotation 90: body x = -13.4 to +3.2 mm from the board centre), so the antenna-strip
   to nearest-LED distance is **5.06 mm** on the stored board, not 7.6 mm (the assistant's error: it took the origin as the body centre);
   `mech_outline.py` MOD_OFF = -4.0 gives 6.07 mm. A sweep of the support stiffness with the press points restricted to R_use = 13 mm (not the
   16 mm disc edge used in revision 1) gives: S2 with three bridges passes at 3 N/mm (3.85 N, 0.99 mm); an off-centre switch fails at every
   stiffness (press-point travel 3.6 mm or more); three switches give 1.43 to 4.37 N at 0.43 mm. Not re-checked by the assistant: the plate
   deflection estimates, the arm-stress and light figures (the light centre value 18 to 19 % was checked), the 50 degC and fatigue statements.
4. Implementation readiness (R): see the outcome.

## Findings
Reviewer numbers are kept (C1 to C20, T1 to T26, M1 to M26, I1 to I22); related rows share one resolution.
| # | Severity | Finding | Resolution | Status |
|---|---|---|---|---|
| T2, M8, I1, C13 | High | The 7.6 mm antenna baseline does not match the stored board or the repository models | Confirmed. Revision 2 states 5.06 mm (stored footprint body), 6.07 mm (`mech_outline`), and the 1.0 mm model difference; S2's 3.6 mm is 71 % of the margin. The test pins physical properties, not 7.6 | Fixed (plan 2, 3.3, 5) |
| M1, M2, M3, M4, I2, M15, T12 | High | The "lean S1" and the centroid rule are unworkable; M2 does not constrain rocking; M1 is a strawman or narrow; M3 misses the force window; M4 contradicts S2 | Confirmed by the matrix. Lean removed. S1 fails at every stiffness; S2 + M1 passes in a narrow band that FDM tolerance does not allow; M3 works with a 1.4 to 4.4 N window; M2 rejected with the jam rule; M4 dropped unless M1 and M3 fail. ADR-0026 decides between S2 + M1 and S3 + M3 | Fixed (3.2, 3.3) |
| T6, M5, M14, I3, I19 | High | The vertical stack (+-0.8 mm) is wrong, not closed, and mixes lateral terms; a soft series spring cannot fix a gap error; a clear click conflicts with a soft tab | Stack restated as +-1.2 to +-1.4 mm worst case (estimate), three closing mechanisms named, lateral chain added, worst case governs safety criteria, `check_tolerance.py` extended with named datums | Fixed (3.4, 5) |
| T1, M6, I6, T24 | High | The stuck-press rule (30 s) fires after the 3 s and 10 s functions; ADR-0006 item 7 interplay | Rule withdrawn. New rules: a press at boot or without a prior release starts nothing; reset needs a second deliberate action; ADR-0006 note | Fixed (4.5); SYS-017 text for the owner |
| T3, I21, C17 | High | Code in `mech/` and `hw/` before approval (rule 1) | Steps 0 and 1 are analysis and evidence under Approved MECH-004, MECH-002, MECH-003, HW-008, adding documents only; the owner confirms (question 6). Plan section 5 rewritten | Fixed; owner confirms |
| T4, C18 | High | No requirement text; no parent; TCs without "Verifies" | Section 4.7 drafts MECH-010 to MECH-013 with parents, SYS-017 and HW-007 and MECH-004 changes; table has a Verifies column | Fixed |
| T5, I17, M13 | High | Pass criteria unset or subjective; TC procedures missing | Section 6 gives probe, speed, gauge, detection, conditions and numbers; every bracketed value is flagged and the sources are stated in section 7 | Fixed (values remain proposals) |
| T7, I11, M25 | High | "Centre not lit on its own" conflicts with the optics; TC-302 wording | Spill lights the disc (19 % centre, 54 % at r = 13, 71 to 81 % at r = 15 to 16, checked at the centre); options for the owner; criterion as luminance ratio; TC-302 gets a procedure first | Fixed; owner question 1 |
| T8, I5 | High | Consumers of BTN_* and SW1 missing from "Files to change" | Listed: `panel_tabs.py`, `test_panel_tabs.py`, `mech_outline.py`, `test_mech_outline.py`, `pcb_full.py`, `pcb_quality.py`, `test_board_p1.py`, `test_pcb_full.py`, `pcb_rules.py`, `known-open-violations.json`, `housing.py`, DEV-004; full pytest as acceptance | Fixed (5) |
| T9 | High | No user documentation, glossary or usability deliverable | Added to "Files to change" (quick start, guide, troubleshooting, glossary); a usability check enters TC-304 at step 2 | Fixed |
| T10, I16, M17 | High | Regulatory impact unassessed; the ESD claim has no basis; no ingress requirement | ESD claim withdrawn; new TC-314; `regulatory-check` at step 2; matrix and technical file listed; ingress is owner question 8 | Fixed |
| T11, M7, I9, M9 | High | A3 (rigid disc) is probably false; lid compliance; disc thickness ambiguous | A3 marked doubtful; plate-bending model and coupon gate in step 1; disc defined as the 1.2 mm plate lowered 0.3 mm; lid compliance and a band-press check added to the model list | Fixed |
| I7 | High | P1 is ordered before the first real click test | Pre-order gate added (printed lids, stand-in board, TC-310 at coupon level) before the re-placement | Fixed (5, step 3) |
| M10 | Medium | Overload load path and the stop location undefined | Stop is inside the lid (disc rim against a band lip), not on the PCB or the switch; TC-315; the click before the stop at every point | Fixed (4.1) |
| T13, I12, M12, M18, T19, C14, C19 | Medium | The switch part is not compared; the evidence file duplicates a placeholder; the part search width is unclear | Step 0 reads TL3342 and two alternatives, checks stock and class, updates `sw-tl3342.yaml` (no second file); ADR-0026 covers the part | Fixed (4.9) |
| T14, I17 | Medium | Test gaps: overload, orientation, warm press, coupons without IDs; "TC-310 step 1" dangling | TC-310 covers orientation and 25/50 degC; TC-315 overload; TC-313 extended; the dangling reference is removed (A2 points to the coupon level) | Fixed |
| T15, M21, I20 | Medium | Unit tests lock in a scratch output; signatures and locations incomplete; random points unseeded | Physical-property tests, seed 7, signatures typed, file locations fixed; the pose count is reported, not asserted | Fixed (5, 6) |
| T16 | Medium | No SW follow-through (debounce, boot with the button, pull-up EMC, RV-017 row 27, TC-207 method) | 4.5 and the file list; RV-017 row 27 closed against the new exposure at step 2 | Fixed |
| T17, I13, M15 | Medium | Finger over the antenna: baseline TC-303 is a stub; limit unset | TC-312 uses the TC-038 baseline and a hand phantom, interim limit [6] dB; owner question 3; metal in the MECH-003 box needs wording or a DEV | Fixed; owner decides |
| T18, M24, I18 | Medium | The rollback is not a working state; part structure per concept | Fallback is a rim switch with the side hole, SW1 re-placed at the rim; part structure per concept in 4.6 | Fixed |
| T20, M11, M12 | Medium | Creep, fatigue, DFM of the supports | Score-line option deleted (18 kN/mm); arm stress and a fatigue limit named; coupons for gap, seal, arms; warm test in TC-310 | Fixed |
| T21, I20 | Low | Wrong CI claim | Root pytest runs `mech/analysis` tests; the stack check extends `check_tolerance.py` | Fixed |
| T22 | Low | New code in lint-exempt spike code | Pure statics go to linted `mech/analysis`; geometry stays in spike-gate with the exception recorded | Fixed |
| T23 | Low | ADR-0026 has no criteria | Weights in 4.8 | Fixed |
| T25 | Low | ID bookkeeping | Reserved list in section 8; entered in the checked files at step 2 | Fixed |
| T26, I4 | Medium | M3 stuck-closed and antenna proximity | In findings 3 of 3.2, 4.5, the risks and the fault table | Fixed |
| M16 | Medium | Accidental press and chatter | TC-313 extended (soft, convex, 60 s, vertical); debounce requirement | Fixed |
| M19, M13, C4 to C6 | Low | Z reference planes, the 4.0 mm rule, 8.65 mm, disc thickness | Disc top Z 16.15, underside Z 14.95, 8.35 mm above the PCB, parts at most 6.15 mm, contact plane 7.15 mm above the module top | Fixed (4.1, 4.3) |
| M20, I8 | Medium | Area budget and the placer rule do not fit | Exact switch coordinates from ADR-0026; keep-outs listed; area fill before and after | Fixed (4.6) |
| M22, C11 | Low | Reproducibility of 320 and 3.6; search definition; check 2 radius | Definition given in 3.3; "an independent search gave 3.2 to 3.7"; the radius statement corrected (the numbers were for a press at 16 mm; the matrix now uses R_use) | Fixed |
| M23 | Low | `POST_AZ` 30/150/270 against `POST_DEG` 60/180/300 | Reconciled at step 1 | Open (step 1) |
| I22, M25, C2, C3 | Low | Owner expectation; R_use and R_disc undefined | Definitions in section 2; areas 62 % and 47 %; owner question 7 | Fixed |
| C1, C7 to C10, C12, C15, C16, C20 | Low | Header wording, stack numbers, M3 window, support placement, load path, free circle (19 against 17.3), CI, ESD TC | Header says ADR-0026 decides; stack and load path rewritten; free circle reconciled with plan 08 (18.4 and 18.75); CI fixed; ESD TC-314 | Fixed |
| I10, C13 | Medium | Z claims leave out the recess | The recess is in the Z chain (4.1) | Fixed |

## Outcome
Approved with actions (the review outcome only; plan 09 stays Draft and only the owner approves it): revision 2 resolves every row above except M23 (step 1) and the owner questions. The implementation-readiness pass (R) is
recorded below once it has run.

## Implementation readiness (R), first pass on revision 2: NO-GO for steps 0 and 1 as written
The goldfish confirmed the facts of revision 2 (files, Z chain, ring, 5.06 and 6.07 mm baselines, U9 and SW1 positions, statuses, the S2 and M3 matrix rows,
324 poses and 3.64 mm in its own search, `pytest mech/analysis` 10 passed, traceability 281 items 0 errors, `check_part_evidence.py` 27 files 0 errors) and
returned six blocking gaps. The assistant checked the switch geometry in the stored board (`SW_SPST_TL3342`: F.Fab 6.4 x 5.2 mm, courtyard 8.5 x 6.0 mm, four
pads) and re-ran the pose search with the real switch: 10 poses and 2.51 mm (body, 1.0 mm clearance), 58 poses and 3.04 mm (courtyard, no clearance); with a
5.2 x 5.2 mm body 36 poses and 2.51 mm.
| # | Severity | Finding | Resolution | Status |
|---|---|---|---|---|
| R1 | Blocking | No recorded owner approval for steps 0 and 1 (rule 1) | Not a plan defect: the plan says the owner confirms (question 6) and now states that steps 0 and 1 start only after that | Open: owner |
| R2 | Blocking | The switch body is 6.4 x 5.2 mm (5.2 x 5.2 body), not 4.5 x 3.5 mm; the S2 search, the 71 % claim, the 2.5 mm column and the S3 distance depend on it; the evidence file has `pin_count: 2` | Confirmed. Plan 2, 3.2, 3.3 rewritten: S2 keeps 50 to 60 % of the margin with the real switch; the revision 2 figures are withdrawn; step 0 corrects the evidence file | Fixed (revision 3) |
| R3 | Blocking | Step 1 code is not specified exactly (signatures, return types, formulas, board reader, seed generator, matrix inputs, M3 azimuths, informational chain, numpy) | Section 5 now gives typed signatures, formulas, the stdlib `random.Random(7)`, the matrix definitions in 3.2, a stdlib `.kicad_pcb` reader, and states that the chains are informational and not in `run()` | Fixed |
| R4 | Blocking | Step 0 inputs and outputs undefined; the TL3342 datasheet has no travel and no curve; the force tolerance (+-50 gf) is not in the model | Selection criteria and file names given (4.9, 5); the travel and the click drop are measured in TC-310; the window becomes [2] to [5] N and the matrix notes the +-0.49 N; the snap dome is excluded (HW-008) | Fixed |
| R5 | Blocking | Deliverables without a test, a location or with a circular dependency (light, scissor, coupon gate, area check, POST_AZ reconciliation, step 0 verification) | `button_light.py` and its test added; the scissor study only if the owner asks; the coupon gate moves to step 3; the area check is a capacity estimate in step 1 and the placer run in step 4; the reconciliation is a report item with no file change; step 0 runs `check_part_evidence.py` | Fixed |
| R6 | Blocking | Traceability trap: ADR-0026 naming proposed IDs fails the checker | 4.8: ADR-0026's Related field names only existing IDs | Fixed |
| R7 | Low | Arm stiffness spread arithmetic; M3 "works" against the 2 N bound; ruff exception location; SPDX and `reuse lint`; README rows; the rotation range valid by symmetry | Corrected or stated in 3.2, 3.3 and 5 (the spread is 0.32x to 2.4x with w and t both +-0.3 mm, 0.42x to 1.95x for t alone) | Fixed |
| R8 | Info | Missing for later steps: the probe definition for "within 13 mm", the stand-in board script, coupon path (`mech/freecad/coupons.py`), PETG brand and print settings, rig and sample sizes, failed-gate action, `SW1_POS` structure, area criterion, test equipment | Probe defined as a 4 mm pad on the force resultant; steps 3 to 5 list the rest; the area criterion stays open until plan 08 revision 6 | Fixed or open (step 4) |

The plan is in revision 3. A second readiness pass follows; its result is recorded below.

## Implementation readiness (R), second pass on revision 3: NO-GO for steps 0 and 1 as written (three text blockers)
The goldfish assumed the owner gate (question 6) and confirmed paths, baselines (5.0629 and 6.0683 mm), the switch outline, the pose search (10 poses and 2.512 mm; 58 and 3.043 mm;
324 and 3.644 mm; 36 poses for 5.2 x 5.2), the formulas (0.1991 N/mm, 0.0423 mm/N, 7.8 mm, 0.32x to 2.44x) and the light values (0.182 at r = 0, 0.529 at 13, 0.698 at 15, 0.792 at 16);
the rows of the matrix reproduce except for the sample and angle items below.
| # | Severity | Finding | Resolution | Status |
|---|---|---|---|---|
| R9 | Blocking | Step 0: the TL3342 sheet is one page and its dimensions are only in the drawing; the checker needs a quote with the number (it rejects "100,000" for 100000 and the newton values) | Recording rule in step 0: force as `typ: 160` gf with a separate 50 gf claim, life as a statement-only claim, "no travel" as `source-missing`, geometry in `notes` marked not machine-checked; the plan states what "0 errors" then means | Fixed (revision 4) |
| R10 | Blocking | Step 1: the matrix test cannot pass: the plan's numbers came from numpy `default_rng(7)`, not stdlib `random.Random(7)`; "78.5 degrees" is not the centroid angle (acos(0.2) = 78.463); the table is rounded coarser than the test tolerance; the boundary start angle is unspecified; the sample omits the centre, so M3's maximum is 4.80 N at the centre, not 4.37 N | Sampler, draw order, centre and switch points and the boundary start are pinned; exact angle; tests assert analytic values (S2 rows, the 4.80 N centre) and the sampled rows within 5 %; the M3 row now says 4.80 N and that the centre exceeds the [5] N window with +50 gf | Fixed |
| R11 | Blocking | `s3_conflicts` has no semantics or test; the S3 claim (touching the module, 3 mm from the strip) cannot be reproduced: with the real body only 7 of 480 triplet poses clear the module, none with the courtyard | Signatures, return formats and `s3_scan` defined; finding 3 of 3.2 rewritten: three switches at r = 11 do **not fit** around the stored module; the test asserts "small" | Fixed |
| R12 | Non-blocking | The licence-map check fails for `ilim-resistors.yaml`, `rlm12.yaml` and `tps3808g01.yaml`; two E501 lint findings; a format finding; missing CHANGELOG line; `plate_deflection` needs a `noqa`; missing tests for helper functions; `Pose`, the corner radius, the board-centre parameter and the lateral-chain keys undefined; the owner confirmation understates the change set; the capacity estimate has no method; `check_docs_style.py` reads only `docs/user/` | **The first three were caused by the assistant's commit f7850ce and are fixed now** (ALLOW list, docstring, format; ruff and the root pytest pass). The rest is in steps 0 and 1 of revision 4 (change set listed in 5; capacity estimate = quoted plan 08 figures plus 51 mm2 per switch; `check_docs_style.py` removed from the list) | Fixed |

The plan is in revision 4. No third readiness pass runs now: steps 0 and 1 cannot start before the owner answers section 7, and the answers (direction, light, switch size) change what they contain.
A third pass runs on the plan as it stands after those answers.

## Implementation readiness (R), third pass on revision 6: NO-GO for step 1 as written (four blockers, resolved in revision 7)
Run on 2026-11-24 after the owner direction D1 to D3 (plan 09 section 0). The fresh goldfish read the plan and the repository, rebuilt the matrix, the band, the pose search and the S3 scan with the standard
library, and confirmed paths, statuses, baselines (5.0628 and 6.0683 mm), the Z chain, the matrix rows, the bands (2.83 to 3.92 and 2.20 to 6.69 N/mm), the pose counts for the TL3342 cases and the S3 count of
7 of 480. Verdict NO-GO for step 1 "exactly, without asking questions": G1 to G4 force a guess, G5 breaks `ruff check .`. Resolutions below; the pass was **not repeated on the text alone**: revision 7 pins the
conventions to the code as built, and a goldfish reviews plan and code together (row R28).
| # | Severity | Finding | Resolution | Status |
|---|---|---|---|---|
| R13 (G1) | Blocking | The tolerance chains had no values, datums or formulas | Values, datum and formulas are in plan 09 step 1 and in `check_tolerance.py` (`BUTTON_VERTICAL`, `BUTTON_LATERAL`, `recess_worst_case` = nominal - `lid_ledge` - `lid_plate`); hand values in `test_check_tolerance.py` | Resolved |
| R14 (G2) | High | `best_antenna_distance(poses)` could not be computed; `Pose` flip field unclear | `Pose` is (x, y, angle); the antenna end is chosen inside `best_antenna_distance(poses, module_size, strip_mm, leds)` over both ends; counts are per (x, y, angle) | Resolved |
| R15 (G3) | High | `main()` prints a band for the KSC221 where `bridge_band` must raise | `bridge_band` raises `ValueError` when the travel limit is not met up to 20 N/mm; `main()` prints "no band"; rows and the B3U extremes line are specified | Resolved |
| R16 (G4) | High | `s3_scan` orientations, clearance and "best gap" unspecified | Four absolute orientations 0, 45, 90, 135 degrees, clearance 0 (touching conflicts), best gap = largest over feasible configurations of the smallest gap, two independent maxima; test uses the stored board | Resolved |
| R17 (G5) | Medium | `ruff check .` failed on signatures (PLR0913/0917) and test literals (PLR2004) | `noqa` on every function with more than five arguments; named constants in tests; `ruff check .` and `ruff format --check .` pass | Resolved |
| R18 (G6) | Medium | B3U pre-travel tolerance was an unverified reading | Read from the rendered catalogue page on 2026-11-24: 0.15 +0.2/-0.1 mm (typeset). The PDF text layer shows "0.15 +- 0.1"; the report and `main()` print both readings | Resolved |
| R19 (G7) | Medium | The capacity estimate had no method | `fill_fraction` with the plan 08 A3 figures (430 on 650 mm2): 66 % today, 63 % S2 with the B3U courtyard (assumed 4.0 x 3.5 mm), 82 % S3 with two more TL3342 courtyards; the 650 and 430 mm2 are not recomputed | Resolved |
| R20 (G8) | Medium | B3U height 1.2 or 1.6 mm; land pattern not read | Step 1 needs the body and a gap only; `switch_height` is a tolerance value (0.15 mm, assumption); the height question stays for the footprint step | Resolved |
| R21 (G9) | Medium | Revision 6 uncommitted; RV-018 had no entry; D2 rests on "Do your recommendations" | Revision 6 committed (commit `bd59b6c`); this entry; the owner's words and the recommendation list are in the journal of 2026-11-23 and plan 09 section 0 | Resolved |
| R22 (G10) | Medium | `test_button_zone.py` pins the stored board and step 4 re-places it | Added to the step 4 file list | Resolved |
| R23 (G11) | Medium | `ring_irradiance` formula, azimuth and normalisation unspecified; 0.182 sits near the 0.18 test bound | Formula and normalisation pinned in plan 09 step 1; test bound 0.17 to 0.20; 54 % and 71 to 81 % restated as 53 % and 70 to 79 % and not asserted | Resolved |
| R24 (G12) | Low | Figures: B3U 1,330 not 1,322 poses, 428 not 424; without the corner limit 134 poses and 3.57 mm, at 19.0 mm 12 poses and 2.86 mm; gap 0 needs a strict test | Corrected in plan 09 and the report; the distance test is Euclidean and a touching pose conflicts | Resolved |
| R25 (G13) | Low | Stale plan text (placeholder `pin_count: 2`, allow-list line, five files, test placement, traceability claim) | Edited | Resolved |
| R26 (G14) | Low | `main()` and `s3_conflicts` strings untested; arm stress length missing; report fields missing | Smoke tests for the three `main()` functions and a string test; arm length 10.1 mm and 53 MPa for k = 3 N/mm; the report names tools, revision and raw output | Resolved |
| R27 (G15) | Low | `press_metrics` lift handling and the y-axis frames were unstated | Stated in plan 09 step 1 | Resolved |
| Extra | Note | The TC-310 probe at r = 13 mm reaches the disc edge with no margin | Outer ring of the force map moved to r = 12 mm (plan 09 TC-310) | Resolved |
| R28 | Process | A fourth readiness pass on the text alone was not run | A fresh goldfish reviewed plan 09 revision 7 against the implemented files (commit `1f5a014`); result below | Resolved |

## Review of plan 09 revision 7 against the step 1 files: NOT READY, resolved in revision 8
Fresh goldfish, 2026-11-24, commit `1f5a014`. It recomputed every headline number with its own solvers (S2 rows, bands, pose counts, S3 scan, light, chains, scores) and found them correct; its findings are about the reasoning
built on them and about test strength. No repository file was edited by the goldfish.
| # | Severity | Finding | Resolution | Status |
|---|---|---|---|---|
| R29 (F1) | High | The ADR sensitivity sentence "C with antenna 4 scores 94 and leads A" was false (A scored 96); the ranking does not hang on two numbers | Scores redone (R30 to R33); sensitivity rewritten: any one weight-5 point moves a sum by 5 | Resolved |
| R30 (F2) | High | The 77 % headline puts the strip 1.35 mm from the metal switch and breaks plan 09 4.3 ("switch on the side away from the antenna") | `best_antenna_distance` gets `switch_size`, `min_switch_strip_mm`, `away_from_switch`; plan, ADR and report quote 3.64 mm (72 %; 60 % of the `mech_outline` 6.07 mm) and 3.55 mm (3 mm rule); pinned in tests | Resolved |
| R31 (F3) | High | No bridge stiffness holds the force window or the 1.0 mm travel over the datasheet pre-travel tolerance; the plan and ADR never said so | `tolerance_band` added (k >= 6.60 and k <= 2.87 N/mm, empty), printed by `main()`, tested; stated in plan 09 3.3, ADR A and the report; travel 1.08 to 1.47 mm at 0.35 mm pre-travel recomputed | Resolved |
| R32 (F4) | High | S2 tests were partly vacuous (the TL3342 case was empty on the coarse grid) and none of the S2 results was pinned | Full 0.5 mm and 3 degree grid: counts 10, 58, 1,330, 428, 134 and 12 and best distances pinned; gaps, corner limit and angle range checked for every pose; stored pose gives 5.0628 mm; both antenna ends tested (the S2 tests take about 30 s) | Resolved |
| R33 (F5) | Medium | The ADR numbers for C had no code; three switches pressed at the centre need 3 x OF (3.03 to 5.97 N), so the 5 N bound fails too | B3U M3 row and the centre values added to `main()` and the report; ADR C and the scores corrected (C force score 2) | Resolved |
| R34 (F6) | Medium | The lift branch was never exercised; M3 minimum and travel were unpinned | A real lift case (supports left, switch right, press at (-14, 0)); `bridge_band` raises when the plunger lifts (monkeypatched test); M3 minimum 1.427 N and travel 0.435 mm pinned | Resolved |
| R35 (F7) | Medium | The rigid-disc rows ignore the plate flexibility (0.042 mm/N against the 0.10 mm/N switch) and the ADR did not list it | Plate line in `main()` (+0.10 mm at 2.4 N, +0.21 mm at 5 N); ADR "Not known" and report | Resolved |
| R36 (F8) | Medium | Chains not carried into the ADR; plan 3.4 text said 1.38 mm; `recess_worst_case` subtracted the ledge although disc and band are one print; `switch_actuation` ignored the +0.20 mm side | Chains cited in ADR A; plan 3.4 text fixed (code uses the 1.90 mm nominal gap); recess = nominal - `lid_plate` (placeholder, +0.10 mm), a test shows the ledge is ignored; `switch_actuation` 0.20; constants tied to `housing_params` | Resolved |
| R37 (F9) | Medium | Fill figures used two methods; the ADR called 66 to 63 % a firm positive | One method (switches as fixed parts): 66, 63, 65 (three B3U), 78 (three TL3342) %; plan 08's 82 % noted; ADR marks the figure as an estimate | Resolved |
| R38 (F10) | Medium | Plan text disagreed with the code (2.5 to 3.2 N/mm; 19 %, 54 %, 71 to 81 %); S1 rows and the corner sweep were not in committed code | Text fixed; S1 rows, the corner-limit sweep and both S3 clearances added to the `main()` output | Resolved |
| R39 (F11) | Low | S3 "92 of 480" is at clearance 0 while S2 uses 1.0 mm to the switch | Both clearances printed and pinned (22 of 480 at 1.0 mm); the two maxima are said to be independent | Resolved |
| R40 (F12) | Low | The ADR omitted the `mech_outline` baseline (6.07 mm) and the reopened decisions | Both baselines in ADR A; ADR-0003, ADR-0023 and DEV-004 in Related and in the consequences | Resolved |
| R41 (F13) | Low | The light model used 8.0 mm; the disc underside is 7.7 mm above the LED top; off-centre values and the azimuth and phase parameters were untested | `HEIGHT_MM` 7.7 (0.165, 0.500, 0.672, 0.771); values pinned, azimuth and phase tested, a single-LED analytic test | Resolved |
| R42 (F14) | Low | A k = 3 N/mm arm exceeds the assumed yield; the `arm_stress` test mirrored the formula; travel is checked at the nominal force only | Warning in ADR A; test against 3 F L / (w t^2); the nominal-force convention is in the `bridge_band` docstring | Resolved |
| R43 (F15) | Low | Unpinned constants; sampler uniformity untested; no rotated-polygon or edge-crossing test; `SIX_PCT` name | Uniformity, rotated-square and crossing-bar tests; vertical constants tied to `housing_params`; `FIVE_PCT` | Resolved |
| R44 (F16) | Info | Stale revision text in the report; "four new Python files" then six named; the CHANGELOG test count included old tests | Fixed; the owner's words "Do your recommendations" stand verbatim in plan 09 section 0 | Resolved |
| R45 (F17) | Info | The B3U result is stable under the search assumptions (corner limit, LED clearance, plunger keep-out) | None needed | Checked |
Consequence: with the corrected scores ADR-0026 puts S2 (84) and S3 (87) within noise and S2 with the TL3342 last (66); plan 09 revision 8 recommends taking S2 and S3 to the coupon gate. The owner's direction D1 (S2 with the B3U)
stays the working direction for step 1, but the review did not support the first claim that S2 leads. Open: plan 09 question 9 (S2, S3 or both to the gate).
