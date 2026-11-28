# Review Record RV-020

- **Subject:** `docs/plans/08-p1-one-sided-board.md` section S (revision 7, 2026-11-28): round 58.5 mm board, split ring, module at the edge (ADR-0027 Accepted)
- **Type:** Design and implementation readiness (DEV-008 closing condition: a readiness GO before implementation and routing)
- **Date:** 2026-11-28  **Reviewer(s):** one comprehension goldfish, three antagonistic goldfish (failure modes and safety; testability and NFRs; dependencies and manufacturability), one readiness goldfish (pass 3, below); resolution by the assistant. **Independent?** no (AI reviewers of an AI-written plan). The goldfish read the plan and the repository, recomputed numbers with the standard library and changed no file. The assistant verified each claim against the repository before it changed the plan; the owner answered the one blocking question.

## Pass 1: comprehension (first draft of section S)
The goldfish explained the architecture, the intent and the scope as intended (profile switch in `mech_outline.py`, one netlist, fixed parts first, annealer for the rest, grid router for 33 links, Freerouting for the long links, R3b and R4 as before). It listed 11 points it could not reconcile. Verdict: no mismatch of intent; the text had gaps.
| # | Finding | Verified | Resolution in section S | Status |
|---|---|---|---|---|
| C1 | The caps cannot sit beside the LEDs at a 3.96 mm pitch | Yes (gap under 1 mm; computed) | Caps radially inside, long axis tangential, search with slide; `place_led_cap_top` changed | Resolved in the plan |
| C2 | The wall feet at |y| 8.8 touch the end LED courtyards | Yes (0 mm; the end LED then has no cap position) | Foot position computed (face at 8.36, centre line 7.76); datum defined | Resolved; light-edge gate added |
| C3 | Panel tab candidates 15/345/165/195 fail the tab model; the azimuths live in `fab_p1.sh` and `pcb_rules`; "4-up" unclear | Yes | The azimuths stay (105, 217.5, 285, 330) with computed edge gaps; panel 1 x 1; "4-up" removed | Resolved |
| C4 | The netlist is replaced while `r46` stays default | Yes | One netlist per profile; loader; determinism test; `r46` removed at S6b | Resolved |
| C5 | Consumers of `tab_r`, the slot and the empty vendor keep-out are not listed | Yes (`pcb_fix`, `pcb_stitch`, `pcb_ring`, `pcb_full`) | Item 3 names them; `tab_r` null exactly under `r58`; no slot; sliver test | Resolved |
| C6 | Origin of 22.3 mm, vacuous subtractions, input-path land | 22.3 was not derived | `R_MOVE` 22.92 derived; land computed; J1-side metric | Resolved |
| C7 | The 3 mm antenna clearance and "3.4 mm" cannot be reproduced | Yes (2.40 / 2.71 / 2.95) | Three values pinned; the [3] mm is not met by any measure | Resolved |
| C8 | The notch estimate of 0.2 mm is wrong | Yes (0.54 / 0.96) | Computed values; check 6 passes | Resolved |
| C9 | End chord 21.58 and `MOD_OFF` -20.2 typed | Yes (21.564; -20.196) | Derived, tested at 2 decimals and 1e-6 | Resolved |
| C10 | "Until S9", item 6 without a step, `cell_refs` module unnamed | Yes | S6a to S6c; item 6 in S2; `src/led_cells.py` | Resolved |
| C11 | Other 16-LED users (`dc_bias_caps.py`, `button_light.py`, `test_kicad_strict.py`) | Yes | Items 2 and 6; grep test for literal `D1`/`D16` | Resolved |

## Pass 2: antagonistic (three lenses on the redraft of 2026-11-28)
Verified by the assistant: strict DRC waiver (footprint_filters_mismatch max 16, D1 to D16); schematic LED block 2 x 8 on A3; `check_part_evidence --netlist` exits 1 with 10 errors today; centre LEDs overlap the SW1 courtyard at r 6.0 to 6.3; the U9 library courtyard (land 910 mm2); J1 mouth is the courtyard front (Fab front 0.5 mm in); wall at the module corners 1.90 mm; module with margin 149 mm2; CI runs no `P1_PROFILE`; `pcb_power_check` has no ring case. Not reproduced: the reviewer's 11 end-LED cap positions (the plan keeps its figure of 3 and says so); a "stale" footprint-filter entry (to be checked at S1).
| # | Severity | Finding (lens: S safety, T testability, D dependencies) | Resolution | Status |
|---|---|---|---|---|
| 1 | High (S, T, D) | Strict DRC waiver tied to 16 LEDs and 14 U9 overlaps; "no waiver" would fail at R4(a) | Owner gate (a): S1 tries to remove the cause in the generator, else the owner decides before S4; gate (b): predicted 0 and 0 with the body courtyard | Open: owner, if the generator fix fails |
| 2 | High (S) | The U9 library courtyard (x -44.6 to -12.75) covers about 20 ring parts and 273 mm2 of land | **Owner decision 2026-11-28: body courtyard for U9** (DEV-009); land 1035 mm2 | Resolved by the owner |
| 3 | High (S, T, D) | Power check "carries 540 mA" with no code | Item 4: ring cases at the highest HW-010 step limit, test first; 540 mA not verified | Resolved in the plan |
| 4 | High (D) | The schematic LED block cannot hold 36 cells | A2 sheet, 4 x 9 block, symbols-inside-frame test | Resolved in the plan |
| 5 | High (T) | Profile switch: no tests, import-time loops, "both profiles in one process" impossible | `build_parts(profile)`, `profile=` arguments, subprocess tests for unset/empty/unknown, no `r46` constants after an `r58` import | Resolved in the plan |
| 6 | High (S, T, D) | r58 tests not in CI; "green" against "no skip" | `r58` marker and a second CI step; workflow test; explicit-profile tests run in the default step | Resolved in the plan |
| 7 | High (T) | Baseline already red; "green on every commit" cannot be audited; tests first against green | Baseline test IDs listed in the first commit, "no new failure"; red run pasted in the commit message | Resolved in the plan |
| 8 | High (T, S) | Traceability: HW-001 (16 LEDs), HW-005, header; no RV before code | HW-001 and HW-005 amendment texts drafted (Draft, owner approves); S1 traces to MECH-001/002/015, ADR-0027 and the owner's "go"; this record | Open: owner approves HW-001/HW-005 |
| 9 | High (D) | Profile is an ambient variable, not recorded; silent downstream | Stamp in `placement.json`, assertions in every stage, `panel_tabs` infers, `-e P1_PROFILE`, prefix on S3 to S5 commands | Resolved in the plan |
| 10 | Medium (S, D) | 540 mA basis unverified (5 mA vs 12 mA per channel; 1.3 A) | Owner gate (d); risk 10; no figure verified | Open: owner (budget decision stands) |
| 11 | Medium (S, T, D) | Light-edge shift compares different datums (0.44 or 1.04 mm); `light_edge.py` has no offset parameter | Datum defined (LED-side face); both shifts stated; parameter added test first; gate before S2 | Resolved in the plan |
| 12 | Medium (S) | Antenna numbers: [3] mm missed; wall 1.90 mm at the corners; ADR "about 5 mm" | Text corrected; ADR note at S6c; pins are not a pass criterion | Resolved |
| 13 | Medium (S) | Antenna risk decided only by a range test on hardware; failure restarts at S1 | Risk 5 states it; no cheaper gate exists in this plan | Accepted risk |
| 14 | Medium (S) | Stop rule under-specified; `NOTCH_AZ` move pre-authorised | Penalty sweep 40/300/3000, S1/S2 stop rule, report path, `NOTCH_AZ` is an owner decision | Resolved |
| 15 | Medium (S, T) | S6 big-bang, rollback incomplete, hidden readers of `board-p1` | S6a to S6c with own reverts; readers listed; section 8 rollback reworded | Resolved |
| 16 | Medium (S, D) | Centre LEDs overlap SW1 at r 6; cap radius hard-coded | `CENTRE_R` derived (6.4), cap centre 8.4 | Resolved |
| 17 | Medium (S, D) | The notch is invisible to the copper masks | Notch modelled in `inside_pcb` and both masks; test | Resolved |
| 18 | Medium (S, D) | Hook and post azimuths (housing 60/180/300 against board 30/150/270), `R_POST`, button 240 | `R_POST` follows the board; button dropped from `r58` features; housing items listed as open for plan 05 revision | Open item (plan 05) |
| 19 | Medium (T, D) | Cap feasibility (DP) and the greedy placer may differ; end LEDs have 3 positions | `led_cap_candidates` used by the placer, replica-vs-placer test, perturbation test | Resolved in the plan |
| 20 | Medium (T) | Computed numbers come from an unkept script | S1 repeats each as a test; S1 closing commit updates the section and lists the differences | Resolved |
| 21 | Medium (T) | Movable-land test pins its own formula; margins mixed; module 141 vs 149 | Numerical integration oracle; named margins; module with 0.3 mm margin 149 | Resolved |
| 22 | Medium (T, D) | Netlist fixtures: five readers, no staleness check | Loader keyed by profile; determinism test per profile | Resolved |
| 23 | Medium (T) | Board-level checks are characterisation tests (U9 overlap set, 66 mm gate) | Expected overlaps from geometry (predicted 0); `largest_dim_mm` from the placed J1 extent | Resolved |
| 24 | Medium (T, D) | `check_part_evidence --netlist` "passes" is false (10 errors); `used_in` of 40 new parts | Wording corrected; tidy and reverse check moved to S1 | Resolved |
| 25 | Medium (D) | J1 mouth is the courtyard front; body overhang 1.9 mm, flush with the wall | Mouth = Fab front R 31.65; rear pad edge about 22.7; shell pins 0.6 mm inside the edge | Resolved |
| 26 | Medium (D, T) | Mouse-bite check missing (`--no-drc`, only C pads); 2.4 mm should be about 2.3 | `--min-pad-mm` check, test first; figure corrected | Resolved |
| 27 | Medium (D) | Economic 100 x 100 limit unsourced; panel size from a formula | Assumption A1 stated; bounding box printed from the KiKit output; not a gate | Resolved |
| 28 | Medium (S) | Chain order weakly justified; D16 to D17 runs along the antenna strip | Order is a parameter; criteria and three candidates decided at S1 | Resolved in the plan |
| 29 | Medium (S, D) | Via room for the 72 cell pads, stand-in LED footprint with 0.1 mm slack | Risk 8; perturbation test; vendor-drawing comparison before S3 | Accepted risk |
| 30 | Medium (S) | Hard-coded D1/D16 sites, U9 pose wording | Items 2 and 3 list the sites; pose by the pad area with a placed-corner test | Resolved |
| 31 | Medium (S) | Regulatory and safety deltas (photobiological, antenna, EMC, thermal, start-up load) | `regulatory-check` at S0; omitted items in "Not run" | Open: recorded at S0 |
| 32 | Low | Foot margins to the window (0.06 mm) and module (0.56 mm); module body on the circle with no margin; stale panel inputs; diameter typed in two places; parts count about 100; line numbers rot; outline and mask tolerances | Open items, risks 9, a diameter test, 69 parts, symbols instead of lines, sagitta test | Resolved or listed |

## Pass 3: implementation readiness (third draft): NO-GO for S1 and S2 as written
The goldfish recomputed the geometry independently and found it sound (ring, module, edge distances, caps, foot, land, counts, J1 rows all reproduced). It found the plan inconsistent with itself or the repository in four places and several deliverables without a stated test. All fixes were text edits.
| # | Severity | Finding | Resolution (fourth draft) | Status |
|---|---|---|---|---|
| 1 | High | S0 gate open; the "owner's go" had no record; `regulatory-check` not recorded | This pass is entered here; the owner's pre-approval after a GO (answer 16 of 2026-11-17) and the "Yes go" of 2026-11-28 are recorded in the journal and cited in gate (c); `regulatory-check` run (below) | Resolved |
| 2 | High | The diameter-tie test could pass only after item 6 | Test moved to S2; `housing_params.PROFILE_R58` (the generators keep 46 and 53) | Resolved |
| 3 | High | "The ref list follows `cell_refs`" contradicts the waiver data (D1 to D16) | `test_kicad_strict.py` line 135 stays `cell_refs("r46")` | Resolved |
| 4 | High | Profile switch and `-e P1_PROFILE` had no step, test or generation command | Switch tests in item 1; `-e P1_PROFILE` and the exact generation command in item 2 | Resolved |
| 5 | High | Chain order not decidable; criteria contradicted the netlist paragraph | Decided: input, D17 to D32, J1 gap, D1 to D16, D16 to D33, D33 to D36 (the only candidate meeting criteria 1 and 2); `cell_refs` and `chain_links` return types and ownership defined; three excluded links named | Resolved |
| 6 | Medium | The grep test could not pass at S1 and had no scope | Scope fixed (S1 files, code only); S2 extends it | Resolved |
| 7 | Medium | Light-edge gate had no criterion or wall model | Mirror wall, luminance 1.0 mm inside at least 90 % of the plateau; computed 0.93 at 2.42 mm; absorbing wall about 0.55 (why the faces are white); other two MECH-015 figures not computable; gate is the first S1 task | Resolved |
| 8 | Medium | "ADR foot position" test ambiguous; the claim held for one reading only | Two readings named: none at 9.9 mm, fewer positions than at the computed foot at 9.3 mm (reviewer: 3 against 11) | Resolved |
| 9 | Medium | Deliverables without a test (notch `inside_pcb`, outline, `R_POST`, loader, `pcb_dsn`, `pcb_quality`, evidence reverse check, `layout_sch`, footprint filter, land metrics) | One stated check each; `pcb_dsn` and `pcb_quality` move to S2 with a per-arc spread definition; the footprint filter finding is measured on the stored board first | Resolved |
| A | High (S2) | Largest dimension: courtyard front gives 66.0 mm, the Fab front 65.5 mm | Mouth = F.Fab front; helper `fab_front_mm(fp)`; test | Resolved |
| B | High (S2) | Item 4 had no load model | Eight cases `+5V:<ref>`, whole ring current 1.577 A as a screening bound, test on a synthetic board | Resolved |
| C | Medium (S2) | `mechanical` CI job outcome after item 6 | The generators and `ci_mech.sh` are not touched; baseline read before S2; a new red is a defect | Resolved |
| D | Medium (S2) | Second CI step and its workflow test were in no step | Moved into item 3 | Resolved |
| E | Medium (S2) | "3 excluded by name" had no rule | `chain_links` kinds `laid`, `long`, `input`; the three links named | Resolved |
Non-blocking remarks taken into the text: centre LEDs use the tangent rule; module area 147.8 or 149 mm2 (a test value wins); ruff and mypy scope (the spike-gate files stay outside the lint configuration); `layout_full` global state (separate processes); check 6 and check 7 named as tests; "pass 4" removed from the plan header; `render_p1_images.sh` follows at S6c.

## Regulatory check (skill `regulatory-check`, S0)
Recorded in `docs/regulatory/compliance-matrix.md` (section of 2026-11-28, findings F10 to F14) and three dated notes in `applicability.md`. Inputs that change: light output (36 LEDs), antenna environment (edge, 2.40 to 2.95 mm, wall 1.90 mm), housing size; the conformity route does not change. Findings: the LED current is limited by firmware only (F10, ADR-0004 review), HW-005 cannot be met as written (F11), applicability consequences 7 and 12 out of date (F12, fixed), EMC of two long data links (F13), no technical-file evidence produced (F14). Not run: any measurement.

## Pass 3b: readiness of the fourth draft
Pending: a fresh goldfish answers GO or NO-GO for S1 and for S2; the result is entered here.

## Outcome
Pending pass 3b. Open for the owner whatever the verdict: HW-001 and HW-005 amendment texts, SYS-001/028/032 texts, the waiver extension if the generator cannot remove the LED footprint filter finding (gate a), the LED current basis (gate d), the housing hook and post azimuths (plan 05 revision), DEV-009 is recorded as accepted from the answer of 2026-11-28.
