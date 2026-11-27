# Review Record RV-019

- **Subject:** `docs/plans/08-p1-one-sided-board.md` section R (revision 6, 2026-11-24): re-placement and routing of P1 after the owner decisions
- **Type:** Implementation readiness (DEV-008 closing condition: a readiness GO before the re-placement runs)
- **Date:** 2026-11-24  **Reviewer(s):** one stateless goldfish (pass 1), a second fresh goldfish on the revised section (pass 2, 2026-11-27, below) and a third on the section as revised after pass 2 (pass 3, below);
  resolution by the assistant. **Independent?** no (AI reviewer of an AI-written plan). The goldfish read the plan and the repository, recomputed numbers with the
  standard library, ran the unit tests and made no repository change.

## Pass 1: NO-GO for steps R2 to R5 as written
Verified correct by the goldfish: the schematic regenerates (strict ERC 0, deterministic); U5 pins match SBVS050N table 5-1; every LCSC number equals the netlist field and `sourcing.py`; the divider thresholds, the hold-off window
(221.8 to 572.7 ms), the ILIM windows (1379.1 to 1564.3 mA), the HW-016 distance (9.955 mm); the spike-gate suite 521 passed; the Freerouting jar hash.
| # | Severity | Finding | Resolution | Status |
|---|---|---|---|---|
| G1 | Blocker | The CC input-path rules named `J1:CC1` and `J1:CC2`; the netlist nets are `/CC1` and `/CC2`; the placer dropped TVS3 and TVS4 and `pcb_layout_check.py` exited 2, so `fab_p1.sh` could never pass | Two failing tests first (partner nets exist in the real `full.net`; all six rules resolve); rules changed to `J1:/CC1` and `J1:/CC2`; 4 of 6 became 6 of 6 | Resolved |
| G2 | Blocker (process) | RV-019 did not exist | This record | Resolved |
| G3 | High | The three-pass finishing and the store copy existed only in a scratch script | `run_finish.sh`, `store_p1.sh`, `src/merge_drc.py` with `scripts/tests/test_p1_finish_scripts.py`; commands in plan 08 R3b and R5 | Resolved |
| G4 | High | Two `@unittest.expectedFailure` markers in `tests/test_board_p1.py` would turn a good board into "unexpected success" failures | R5 removes them in the same change when the measurements pass | Resolved in the plan; done at R5 |
| G5 | High | `run_repass.sh` needs the run's `a/` folder, not `best/`; `run_pcb.sh` already runs the second pass | R3 states both and which `repass_meta.json` counts | Resolved |
| G6 | Medium | The picker ignored the placement rules; runs 2 to 4 and batches c2 and c3 were never rule-checked | `pcb_pick.layout_misses` and `layout=` in the ranking (after hard findings, before power), with tests; R2 defines the stop when no run meets the rules | Resolved |
| G7 | Medium | The plan said the winner is chosen by three numbers; the code uses more | R3 lists the real key | Resolved |
| G8 | Medium | R4 mixed up the 0.6 mm criterion and the 0.45 mm full-width rule, and called pass/fail limits "reported" | R4 (e) names `test_main_path_is_0_6_mm_wide` and the pass/fail scripts | Resolved |
| G9 | Medium | The HOLD_OK margin used the TPS3840 leakage (90 nA); the TPS3808 gives 300 nA; at 4.399 V the level is 2.0001 V against VIH 2.0 V | Model parametrised (`TPS3808_ILKG`), claim added to the evidence, owner chose R6 = 100 k: 2.77 V; ADR-0025 amendment, HW-010 amendment, plan text and test updated | Resolved |
| G10 | Medium | SBVS050N recommends 1 to 10 nF on SENSE and 100 nF close to VDD; neither was drawn; adding later costs another cycle | Owner chose to add both: C33 (100 nF, VDD_U1), C34 (1 nF, SUP_SENSE; C14442); rules, tests, netlist (104 parts) | Resolved |
| G11 | Medium | `ruff check .` failed with E501 in `test_fab_check.py` | Wrapped | Resolved |
| G12 | Medium | 910 k instead of 931 k was the assistant's substitution | Owner confirmed 910 k / 100 k on 2026-11-24 | Resolved |
| G13 | Low | R2's strict `placed-4l` DRC had no pass criterion and the U9 pair list had no script | R2 no longer has a separate unrouted DRC gate; R4 (a) names the finished-board criterion and the tolerated classes | Resolved |
| G14 | Low | The evidence yaml lacked the pin table, the MR pull-up, the RESET leakage and the bypass claims | Eight claims added and checked against the PDF (19 quotes, 0 errors) | Resolved |
| G15 | Low | "9 rules missed" on board-p1 | 6 missed and 4 unmeasurable of 20 (22 rules now) | Resolved |
| G16 | Low | `p1-board.md` did not exist ("updated"), stored metadata had no check, the environment was not recorded | R5 says "created", the store script is tested, the README records the environment | Resolved in the plan; done at R5 |
| G17 | Low | RISK-044, the compliance matrix and the R26 and R27 fault rows were stale | Listed in R5 | Open until R5 |
| G18 | Low | The container recipe lived in scratch | `run_in_kicad.sh` (digest equal to the workflow, tested) | Resolved |
| G19 | Low | Stale comments and names in code and tests | Tidied where touched; the rest is cosmetic | Partly resolved |
| G20 | Info | Strict tolerances, the placement feasibility at full effort, the wider part change | R4 keeps the "best partial result" fallback; risks section | Noted |

## Pass 2 (fresh goldfish, 2026-11-27): NO-GO for R3 to R5 as written
Verified correct by the goldfish: `full.net` (104 parts, 58 named nets), the 12 added and 5 removed parts, the U5 pins, the CC nets, every LCSC number, 22 rules (16 + 6), `SA_ITERS` 160000, `MUST_PLACE`, `ILIM_VALUES`, the jar hash, the HOLD_OK numbers
(2.7651 V with 100 k, 2.0001 V with 150 k), the thresholds, the HW-016 distance 9.955 mm, the seed ranges of the three batches (no overlap), the picker key and exit rule, `store_p1.sh`, `merge_drc.py`, the pass order of `run_finish.sh`. It ran the root pytest
(247 passed, 1 failed: the gate this revision closes), `ruff`, the traceability and docs checks, and the spike-gate suite without `pcbnew` (its failures and errors are the missing module). It did not run Freerouting, a batch or a container (the Docker daemon start was denied to it).
| # | Severity | Finding | Resolution | Status |
|---|---|---|---|---|
| P2-1 | High | `run_in_kicad.sh` mounted only the JDK directory; the JDK config files are symlinks into `/etc/java-25-openjdk` | Reproduced in the image (`InternalError: Error loading java.security file`). Test first (`test_container_mounts_the_etc_target_of_java_symlinks`, fake `docker`); the wrapper mounts the `/etc/<name>` targets of the JDK symlinks. Smoke test in the real image prints the security settings | Resolved |
| P2-2 | High | `run_pcb.sh` and `run_repass.sh` overwrote the `PYTHONPATH` of the wrapper (numpy, scipy are not in the image) | Test first (`test_router_scripts_keep_the_python_path_they_were_given`); both scripts keep the inherited path. In the image, `pcb_dsn` imports with `KC_PYTHONPATH` | Resolved |
| P2-3 | Medium | The plan did not list the inputs of R3 (scratch mount, packages, jar, daemon) | New step R0 with the commands and a smoke test (run, all packages import) | Resolved |
| P2-4 | Medium | R4 (c) to (f), (h) and the R5 tests had no command lines or environment; `git describe` fails in the root container | Commands for (c) to (f) and the test lines in R4; `safe.directory` set inside the command | Resolved in the plan; runs at R4 |
| P2-5 | Medium | `run_finish.sh` hid the exit status of `pcb_finish.py` (pipe to `tail`) and reported success after a crash | Behavioural tests with a fake Python (`test_finish_stops_when_a_finishing_pass_crashes`, `..._the_strict_drc_did_not_run`); each pass is checked | Resolved |
| P2-6 | Low | `repass_meta.json` was copied when the second pass was not taken | Copied only when `final_pass1.*` exists; test | Resolved |
| P2-7 | Low | "DRC NOT RUN" contains no "FAIL" | The exit code of `kicad_strict.py` is read (2 stops the run); test | Resolved |
| P2-8 | Low | No trigger for c2 and c3, no cross-batch choice, the 0.6 mm criterion is not in the picker | R3 states the trigger, `pcb_pick.py` over all batches, and that R4 (e) is measured on the winner | Resolved |
| P2-9 | Low | R5 kept a marker "on a failing measurement", against R4 | R5 runs only when R4 (a) to (i) hold; the clause is gone | Resolved |
| P2-10 | Low | HW-009: no ERC report stored; the reports sit in `board-p1/`; plan 0.2 row 8 calls them build output (CLAUDE.md rule 12) | The ERC result is quoted in `p1-board.md`. Where the reports live, and the change of 0.2 row 8, are the owner's | Open (owner) |
| P2-11 | Low | R26 and R27 fault rows promised by G17 were not in R5 | Added to R5 | Resolved |
| P2-12 | Low | Counts: "20 rules" against 22; "nine small parts" against 12 | Corrected; the 21 mm2 estimate is marked as not recomputed | Resolved |
| P2-13 | Low | The silkscreen identification may lack the commit; R4 does not check it | `BOARD_ID` set on the host in R0; R4 (i) and `test_board_carries_identification_text_and_fiducials` (fails on the stored board, checked in the image, marker removed at R5) | Resolved |
| P2-14 | Low | `.kicad_prl` is git-ignored but a hard requirement of the finish and store scripts | Optional in both; tests | Resolved |
| P2-15 | Low | The goal (green `fab-release`) has no verification step; the `lib_footprint_issues` maximum and the U9 overlap set are untested with the new footprints | R5 reads `ci` and `fab-release` after the push (else NOT RUN); R4 (a) measures the real board | Resolved in the plan |
| P2-16 | Info | Stale: the journal of 2026-11-24 says HOLD_OK 2.03 V; `check_part_evidence.py --netlist` flags `used_in` C27 (capacitors) and U5 (the superseded TPS3840 file); the check is not in CI | Journal gets a dated correction; the evidence `used_in` lists are tidied at R5 | Partly resolved |
| P2-17 | Info | Not verifiable by the goldfish: R1 claims, the TPS3808 datasheet quotes, the jar file, stock | Rest on pass 1 and on the container runs of R0 and R3 | Noted |

**Verdict of pass 2: NO-GO.** The two blockers (P2-1, P2-2) and the script and plan findings are resolved above (tests: `scripts/tests/test_p1_finish_scripts.py` 22 passed; `tests/test_board_p1.py` in the image 8 passed, 3 expected failures). DEV-008 still requires a GO: pass 3 on the revised section follows.

## Pass 3 (fresh goldfish on the section as revised after pass 2)
Pending when this record was written; the result and the verdict are appended below.
