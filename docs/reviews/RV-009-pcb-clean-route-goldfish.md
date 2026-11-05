# Review Record RV-009

- **Subject:** `docs/plans/06-pcb-spike-clean-route.md`, revision 2 (branch `spike/pcb-clean-route`, base `a4ec0fb`)
- **Type:** Design
- **Date:** 2026-11-05  **Reviewer(s):** five stateless goldfish subagents (comprehension 1, antagonistic 3, readiness 2 runs); resolutions by the Elephant (main Claude session)  **Independent?** no for the resolutions (same session as the author); the goldfish saw only the plan and the repository. Not a human review. Only the owner approves the plan.

## Passes
1. Comprehension: the explain-back matched the intent. It found 14 ambiguities (branch name, waiver classes, J1 offset, stitching, metrics, file names). All were fixed in the redraft.
2. Antagonistic: three lenses (failure modes and feasibility; testability, process and traceability; integration, manufacturability and mechanics). About 70 findings in total, many duplicates.
3. Readiness, run 1: NO-GO (specification gaps and plan not approved). Run 2 after fixes: NO-GO. Run 3 after fixes: NO-GO with 6 blocking and about 12 minor items, all checked against the code (the claims were true) and fixed in the plan (findings 19 to 24). The plan owner stops are not counted as defects.

## Findings and resolutions (grouped)
| # | Severity | Finding | Resolution | Status |
|---|----------|---------|------------|--------|
| 1 | High | Plan sits on `plan/*`; process allows spikes only on `spike/*` | Branch renamed `spike/pcb-clean-route`; "never merged as-is"; R6(b) | Fixed |
| 2 | High | Base commit and branch contradiction; `expected/` convention elsewhere | Base `a4ec0fb` stated; `expected/` created in G6 with its own metadata | Fixed |
| 3 | High | "Unrouted" and "unconnected" measured differently; log line not a metric | M1, M2, M3 defined; `count_unrouted`; fixtures; `PLANE_NETS` as stitcher set | Fixed |
| 4 | High | Via-in-pad forbidden in plan but done by the stitcher | A8: kept, recorded as unvalidated manufacturing assumption; stitcher exits non-zero on failed pads | Fixed |
| 5 | High | G3/G4 loop and stop rule not closed | Loop budget (4 placements, 3 runs each, `-mp` at most 200, 30 min); stop report; no "clean" claim | Fixed |
| 6 | High | Waiver classes hide real faults; no `DEV-nnn`, no per-ref list, no `stitched` profile | Per-ref allow-list, `strict_allow`, `max: 0`, `stitched-4l`, DEV entries, owner expiry decision | Fixed |
| 7 | High | DRU, generator and waiver edited together (guardrails) | G2 as separate commit; owner reviews values; DRU never looser than the floor (T4); DRU canary (T11) | Fixed |
| 8 | High | `run_pcb.sh` swallows failures (`|| true`), no stitch step, no jar hash | Specified in files list and G3; T5 | Fixed |
| 9 | High | LED swap affects housing, helpers and mech numbers | Size gate (not above 59.8 mm), T12, helper functions listed, `mech/` stated as not updated | Fixed |
| 10 | Med | A2 unchecked (LED footprint) | Checked: footprints exist; `FOOTPRINT_OVERRIDE` mechanism chosen; second check of vendor drawing is not a stop | Fixed |
| 11 | Med | Reproducibility of the stored session | `routed.meta.json` with hashes and versions; stale-session check; `dump_board` schema | Fixed |
| 12 | Med | Silk classes, power width, antenna strip after routing | G4 silk rule and stop; width listing (T17, finding not pass); T15 | Fixed |
| 13 | Med | Traceability lists, regulatory check not run, README wording | Lists equalised; regulatory check recorded in section 4; caption wording fixed; G7 greps and checks | Fixed |
| 14 | Med | Fixture source for T6 and T10, schemas, DRU syntax, parsing of refs | Specification details section | Fixed |
| 15 | Low | `LED_PAD_X` does not exist; `pcb_rules.py` already exists; cost term "hard" undefined | Corrected; `OVERLAP_PEN_HARD`; T13 regression design | Fixed |
| 19 | High | `OVERLAP_PEN_HARD`: no fixed `pen` exists (annealing schedule 2.0 to 60.0) | `OVERLAP_PEN_FLOOR = 2000.0` used as `max(pen, floor)`; T13 calls with `pen=2.0` | Fixed |
| 20 | High | `ignored_checks` pseudo-class counted but not allowed | Added to the allowed classes (number only) | Fixed |
| 21 | High | Allow-list lacks D1 to D16, TP and H refs; an existing test pins the override list | Allow-list with patterns; test update listed | Fixed |
| 22 | High | `pcb_dsn.py` has no net-class code; `inner` planes undefined | Classes live in `write_project`; `inner` removed from the deliverables | Fixed |
| 23 | High | No code home for replay, meta and stale check; SWIG track iterator broken | New `src/pcb_replay.py`; `dump_board` and `count_unrouted` parse board text | Fixed |
| 24 | High | `+5V` width 0.4 (stitcher) against 0.6 (rating) | Stitcher takes `NET_WIDTH`; neck-downs listed by T17 | Fixed |
| 16 | Info | Plan is Draft; R6 and stops need the owner | Intended. Not a defect: only the owner approves | Open (owner) |
| 17 | Info | Up to 12 router runs of 30 minutes | Accepted as cost; stated | Accepted |
| 18 | Low | Geometry for the 2.0 mm LED (pad map, ring, J1 offset) is found by running G1 | Bounded by the gates and the loop budget; the readiness reviewer accepted this | Accepted |

## Not done
- A fourth readiness run after the fixes of run 3 (the previous runs each found new gaps; the owner decides whether another run is worth it). The edits were checked only by `check_traceability.py` (250 items, 0 errors) and `check_docs_style.py` (no findings).
- Final checks on the worktree: `check_traceability.py` 250 items 0 errors; `check_docs_style.py` no findings; `build_diagrams.sh --check` up to date.
- Nothing from the plan is implemented; no router or DRC run was made.

## Outcome
Approved with actions: **not approved.** The goldfish gave NO-GO on readiness three times; each round's items were resolved in the plan, the last round's not re-reviewed. The plan is Draft. Owner decision 2026-11-05: R6 (a, b, c) confirmed, plan approved without a fourth readiness run. Remaining owner actions: decide the DRU values and the waiver-list expiry when the work reaches those gates.
