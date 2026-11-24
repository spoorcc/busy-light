# Review Record RV-019

- **Subject:** `docs/plans/08-p1-one-sided-board.md` section R (revision 6, 2026-11-24): re-placement and routing of P1 after the owner decisions
- **Type:** Implementation readiness (DEV-008 closing condition: a readiness GO before the re-placement runs)
- **Date:** 2026-11-24  **Reviewer(s):** one stateless goldfish (pass 1), a second fresh goldfish on the revised section (pass 2, recorded below when it returns);
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

## Pass 2 (fresh goldfish on the revised section)
Pending when this record was written; the result and the verdict are appended below.
