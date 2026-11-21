# Review Record RV-014

- **Subject:** plan 08 `docs/plans/08-p1-one-sided-board.md` (revision 1 at commit `a58ef4a`, revisions 2 and 3 in the working tree of 2026-11-17)
- **Type:** Design
- **Date:** 2026-11-17  **Reviewer(s):** four stateless goldfish subagents (comprehension; failure modes and safety, "S";
  testability and process, "T"; integration and manufacturability, "M"); resolution by the assistant (Elephant); readiness goldfish
  (step 4, below)  **Independent?** no (AI reviewers of an AI-written plan; the owner has not reviewed)

## Protocol
1. Comprehension: the restatement matched the intent. It listed 13 points it could not match with the files; the main ones (the
   stored board's 0.1 mm rules, the housing dimension, the HW-016 geometry, the T1 part, the batch settings) are findings below.
2. Antagonistic review: three goldfish in parallel, 72 rows in total, merged below (lens in brackets).
3. Resolve: the assistant checked the main claims against the repository: `board/README.md` (`SPIKE_PROFILE=fine`),
   `board/busy_light_spike.placement.json` (`largest_dim_mm` 59.24), `stock-check-ilim-holdoff.md` (27.7 k 0.1 % in 0805 and 0402
   only), `analysis-ilim-switch-replacement.md` (unpowered TMUX1101 not specified), `pcb_power_check.CASES`, `pcb_ring.py`
   (capacitors on B.Cu), the SOT-23-6 pad 6 position (1.48 mm from the origin), the CI image facts. All were confirmed. The Maven
   jar's MD5 equals Maven Central's published `.md5` (`8b7b807c2f01dd5e09706cb3cb8d536b`); the `.sha1` request was rate-limited.
4. Implementation readiness: see the end of this record.

**Process finding recorded here (T, M): implementation started before this review.** Step 1 (jar hashes) was committed with the
draft plan in `a58ef4a`. During steps 1 and 2 the assistant also changed, uncommitted, the generator (T1, T2, R22), the main-path
rules and their tests. T1 had the owner's rule (answer 5); R22 traces to HW-017 (Approved); but answer 16 made implementation
conditional on a readiness GO. Those changes stay uncommitted until the GO; T2 is reverted; tests are rerun after the GO.

## Findings
| # | Severity | Finding | Resolution | Status |
|---|----------|---------|------------|--------|
| 1 | Critical | T2 (shared supply protection of U14/U15) turns one fault (R_SU14 open, DZ14 short, C24/C25 short) into "both switches unpowered", an unspecified TMUX1101 state that can raise the limit (S: about 1190 mA against 623 mA with the repo's 0.6 V clamp assumption); outside the owner rule (no window touched); changes Approved HW-010 text (S, T) | Accepted. T2 reverted in the generator; kept only as an analysis option for the owner. `analysis-supply-pin-surge.md` open point 4 ("fails safe") to be corrected (owner list) | Closed (T2 not applied) |
| 2 | Critical | T1 used a 0603 27.7 k 0.1 % part that the repo already showed does not exist, with a derived MPN that `pcb_fabreview` would accept (T, S, comprehension) | Accepted. R_ILIM3 is 0805, Yageo RT0805BRD0727K7L, LCSC C865349 (repo-recorded mirror query, stock not confirmed); no derived MPN anywhere; the order check fails empty LCSC lines and checks the R_ILIM values | Closed (plan 4.1, 4.5) |
| 3 | Critical | Baseline misstated: the stored board used 0.1 mm (`SPIKE_PROFILE=fine`); at 0.15 mm no two-sided run ever completed (M, T, S) | Accepted. Section 1 corrected, with a correction to the owner's "0.15 if I'm not mistaken"; comparison batch b3 at 0.1 mm for the owner | Closed (text); outcome open |
| 4 | Critical | Growth fallback measured the wrong dimension; MECH-001 (58 mm) is already exceeded at 59.24 mm and growth adds about 1 mm per 2 mm (M, T, S) | Accepted. No growth tonight (A4): it changes an Approved requirement's conformance, answer 19. Owner decision | Closed (no growth); owner |
| 5 | High | Code written before the readiness GO (T, M) | Accepted; recorded above | Closed (recorded) |
| 6 | High | U9 library courtyard (43 x 20 mm) vs waiver `courtyards_overlap` max 14 refs U9: may fail by construction with all parts on top (M); the waiver also stops protecting the antenna area (T) | Accepted. Placement gate before routing counts it; a waiver or courtyard change is the owner's; `PLACE_ANT_KEEPOUT=1` in the baseline; the report lists every U9 overlap pair | Open (measured at the placement gate) |
| 7 | High | Density: courtyards about 430 mm2 in about 650 mm2; no check before routing (M) | Accepted. Placement gate (overlap 0, rules met); LED capacitors beside the LEDs and `R_MOVE` 18.4 mm for P1 (+about 120 mm2) | Closed (plan); outcome open |
| 8 | High | LED capacitors on top: the 3.0 mm test cannot pass; `pcb_ring.py` assumes bottom capacitors and is missing from the plan (M, S) | Accepted. Capacitors in the gap beside the LED (about 3.1 mm), test limit 3.5 mm; `pcb_ring.py` follows the capacitor's layer | Closed (plan) |
| 9 | High | VBUS split breaks the power check (`J1` no longer on VBUS_IC; every run gets the same "no path" failure) (S, M, T) | Accepted. Two cases (VBUS J1 to R22.1, VBUS_IC R22.2 to U7.1) and their sum; jumper resistance unknown (A8) | Closed (plan) |
| 10 | High | R22: a typical 1206 jumper may miss [10] mohm and [3] A; no part chosen; empty LCSC (S, M, T) | Accepted. No part is invented; listed for O2 and the owner (R7); the order check fails on it unless named | Open, owner |
| 11 | High | Main-path width only checked at R22; stage 2 can close gaps at 0.2 mm; HW-003 rating not in the plan (S) | Accepted. Board test: every track on the J1-R22-U7 main path >= 0.6 mm; HW-003 added; rating note in the report | Closed (plan) |
| 12 | High | HW-016 arithmetic wrong (pad 6 at 1.48 mm, 1206 pad 1.475 mm) (all) | Accepted. Rule 7.0 mm (9.96 mm worst case); board test of the real distance; C4 out of the U8 block | Closed (plan) |
| 13 | High | Tests not in CI; release not gated (T, M, S) | Accepted. CI test job runs `hw/kicad/spike-gate/tests` and `hw/sim/scripts` in the KiCad image with ngspice; build needs test; `ci_hw.sh` checks `board-p1` with `--no-via-in-pad` | Closed (plan) |
| 14 | High | CI security: write token with unpinned PyPI code (T, M) | Accepted. Build read-only, image by digest, KiKit with `--require-hashes`; publish job only downloads the artifact and runs `gh` | Closed (plan) |
| 15 | High | CI image has no pip, venv or `gh`; user `kicad` (M) | Accepted. apt as root in build; publish on `ubuntu-24.04` | Closed (plan) |
| 16 | High | Order package: CPL from the board vs Gerbers from the panel; J1 not excluded (T, M, S) | Accepted. `kikit fab jlcpcb --assembly` on the panel; J1 excluded by attribute and bought separately (O8); CPL inside the panel outline, top layer only | Closed (plan) |
| 17 | High | Ordered files not kept; process section 9 (T) | Accepted. Order only from a published tagged release (O0); DRC/ERC/fabcheck JSON as assets; DEV entry (Proposed) for answer 17 | Closed (plan) |
| 18 | High | Seven part types without LCSC (U5, U6, U3, U4, U10, U11, U13) besides R22; a missing U5 defeats the hold-off (M, S) | Accepted. A8, R9, listed by the order check; safety-relevant refs listed for the bring-up check (O7) | Open, owner (O2) |
| 19 | Medium | Via-in-pad only fixed in the stitcher; same-net pads skipped; gate from an environment variable (T, S, M) | Accepted. One helper used by every via producer, any net; the gate is a CLI flag for `board-p1`; vias tented | Closed (plan) |
| 20 | Medium | Via-in-pad change after routing (T) | Accepted. Moved before batch 1 | Closed (plan) |
| 21 | Medium | Run reproducibility: baseline environment not defined; run metadata not stored; `fr_threads` a literal 4 (T, comprehension) | Accepted. Baseline = ring14 knobs plus P1; b1/b2/b3 one change each; metadata stored in `board-p1/`; `fr_threads` from the environment | Closed (plan) |
| 22 | Medium | Rollback claim false: the netlist changed for both boards (T, M, S) | Accepted. `board/` frozen at `1d2a1a6` sources and noted as pre-HW-017 and not meeting HW-016/HW-017 | Closed (text) |
| 23 | Medium | Step 1 test passes on the comment text; Maven origin not checked (T) | Accepted. Test reads the `JAR_SHAS` line; MD5 compared with Maven Central | Closed |
| 24 | Medium | No placement rule keeps TVS1/U6 at J1 or R22 between J1 and U7 (S) | Accepted. Rules with fixed partner J1; ties J1-R22, R22-U7 | Closed (plan) |
| 25 | Medium | HW-010/HW-015/TC-210 name VBUS_IC where it is now VBUS; probe access for the surge measurement (S) | Accepted in part. Proposed text updates drafted for the owner (R10). Bench-access table maps every measurement to a top-side part pad; no new test point (density). Rejected: extra probe pads, for now (they cost vias on a board that may not route) | Partly open, owner |
| 26 | Medium | Capacitors near panel tabs may crack (S); tab positions unspecified (M) | Accepted. Explicit tab positions; no capacitor within 3 mm of a tab, checked | Closed (plan) |
| 27 | Medium | Heat sources all on top (U1 near U7, U8, LEDs) (S) | Accepted in part. Distances reported for TC-213; no rule (the placer has none) | Open (TC-213) |
| 28 | Medium | No bring-up step (S) | Accepted. O7 | Closed (plan) |
| 29 | Medium | Fiducials: 3 per side may not fit (M) | Accepted. Rails carry 3; board fiducials counted where room exists | Closed (plan) |
| 30 | Medium | U1 has no F.Fab reference, so the assembly drawing misses it (M) | Accepted. `custom_fp.py` fix | Closed (plan) |
| 31 | Medium | Bottom silk: no text-to-text rule; 0.8 mm likely below the fab minimum (M, T) | Accepted. 1.0 mm / 0.15 mm stroke, placed texts as obstacles, vias too; strict gate after finishing | Closed (plan) |
| 32 | Medium | P1 and P1_DIAM read from the environment at import (M, T) | Accepted. P1_DIAM dropped (no growth); P1 and R_MOVE written to `placement.json` and read from there downstream | Closed (plan) |
| 33 | Medium | Housing models disagree (post azimuths); FreeCAD not installed (M) | Accepted. Recorded (R11); no housing check claimed | Open, owner |
| 34 | Medium | "Reproducible" undefined; manifest incomplete; KiCad and KiKit versions (T, M) | Accepted. Definition (same content without date lines), `--compare` test; manifest fields; image digest | Closed (plan) |
| 35 | Medium | Release workflow races and is untested (T, M) | Accepted. concurrency group, `--clobber`, `workflow_dispatch`, `fab-latest` excluded from the published trigger; actionlint not available, stated | Closed (plan) |
| 36 | Medium | Traceability: TC-208/216/217 "TBD"; order package traces to no requirement (T) | Accepted. Procedures written; tests cite TC IDs; package traced to HW-008 and HW-009 | Closed (plan) |
| 37 | Medium | ADR-0012 G1 and ADR-0020 status (T) | Accepted. A9 and "unaccepted inputs" stated; owner confirms | Open, owner |
| 38 | Medium | CPL rotations rely on the owner's preview (M) | Rejected for tonight: a correction table would be invented without JLCPCB's data; O4 stays | Rejected (reason given) |
| 39 | Low | T1 criterion ambiguous (T) | Accepted. All four margins and step 2 | Closed |
| 40 | Low | One-side test wording inconsistent (T, M) | Accepted. One rule, subprocess | Closed |
| 41 | Low | Regulatory note inaccurate (R22 changes the input path) (T, S) | Accepted. 4.7 corrected; `regulatory-check` in step 12 | Closed (plan) |
| 42 | Low | Tolerated classes incomplete (M, comprehension) | Accepted. All classes of `stitched-4l` listed | Closed |
| 43 | Low | Full BOM with DNP and extended/basic column (M) | Accepted. Full BOM next to the JLCPCB BOM; extended/basic "not known" | Closed (plan) |
| 44 | Low | Batch V without criterion; no via-size switch (M, comprehension) | Accepted. Batch V dropped; the 0.7 / 0.3 mm via profile is an owner item | Closed |

## Implementation readiness (step 4, 2026-11-18 05:45 UTC, after a usage-limit stop)
Verdict: **NO-GO** for the plan as written; steps 1 to 4 (tooling, T1, HW-017 split, no via-in-pad) ready. Blocking gaps:
B1 no step writes the LCSC fields and the DNP marks onto the P1 board; B2 the CI order check would always fail on the eight
known missing LCSC numbers and the policy was not stated; B3 the LED-capacitor side rule ignored J1's courtyard. Minor gaps:
weak T1 and R22 tests (fixed), batch baseline wording (ring14 used `SEED_OFFSET=200` and the fine profile), several deliverables
without a named test, the fixed-partner rule needs placer support, panel and CI details. Resolution: B1 to B3 fixed in plan
revision 4 (not re-reviewed); minor gaps are listed for the implementing step.

**Placement feasibility measured after the review (scratch experiment, not a plan step):** with every movable part on the top
side, LED capacitors beside the LEDs, `R_MOVE` 18.4 mm and the ring14 placer knobs (`PLACE_GRID=1.0 PLACE_ANT_KEEPOUT=1
PLACE_BLOCKS=3 PLACE_ORIENT=1.5`), the best of 16 seeds still has 25.1 mm2 of part overlap; its placed DRC shows 61
`courtyards_overlap` (waiver max 14) and 268 unconnected items (expected before routing). On the 46 mm outline the one-sided
placement does not fit with this placer. This is finding R1 measured, and an owner decision (plan 08 section 7).

## Outcome
Plan revised to revision 4. Steps 1 to 4 implemented; steps 5 and later wait for the owner's decision on R1.
