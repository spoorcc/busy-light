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

## Implementation readiness (R)
(pending)
