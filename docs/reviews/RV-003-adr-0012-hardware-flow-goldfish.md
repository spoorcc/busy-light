# Review Record RV-003

- **Subject:** ADR-0012 hardware design flow, Proposed, commit 9de06fa (text before this review), and `docs/verification/reports/spike-hw-kicad-pipeline.md`
- **Type:** Architecture
- **Date:** 2026-11-04  **Reviewer(s):** three stateless goldfish subagents (comprehension; failure modes, safety, security and regulatory lens; testability, auditability and evidence lens)  **Independent?** partly: the reviewers share a model family with the author, so shared blind spots are possible. Not a substitute for the owner's review.

## Comprehension check
The comprehension goldfish restated intent, architecture and scope correctly (generator code is the source, KiCad files are outputs, the owner reviews and accepts). Its open questions are findings C1 to C5 below.

## Findings
| # | Severity | Finding | Resolution | Status |
|---|----------|---------|------------|--------|
| C1 | Medium | KiCad 8 syntax and GUI save upgrade: effect on the "no GUI edits" rule unclear | Accepted as pin risk. ADR item 1 (marker, hand-maintained list), item 11 (regeneration gate), RISK-034 | Resolved in ADR |
| C2 | Medium | SKiDL and own writer: two generators for one schematic | Accepted. SKiDL removed; one connectivity source (item 1); `skidl` removed from `pyproject.toml` | Resolved |
| C3 | Low | 36 parity issues missing from the ADR | Accepted. Parity 0 is part of acceptance (item 3) and gate G1 (item 9) | Resolved in ADR |
| C4 | Low | Scores: reasoning for owner-review-effort and tool-change rows | Partly accepted: sensitivity analysis added; the "owner review effort" row kept (generated output is harder to review than a drawn schematic, not easier) | Resolved |
| C5 | Medium | Antenna topology (ADR-0003) undecided, keep-out assumption unstated | Accepted. Item 8 lists it as an owner decision that sets the keep-out | Open (owner) |
| F1 | High | Pins declared but not enforced (floating CI tag, unpinned Python and apt packages) | Accepted. Item 4 requires digest and hash pins before acceptance; `kiutils` pinned to 1.4.8 now. CI image digest and hashes are not yet set | Open (before acceptance) |
| F2 | High | Supply chain of generator tools unassessed | Accepted. Tool-qualification table, SBOM entry (item 4); RISK-033 | Open (table not written) |
| F3 | High | Semantic dump too narrow, no CI gate | Accepted. Item 11 widened; regeneration gate and negative tests | Open (not implemented) |
| F4 | High | "Outputs only" model vs scripted routing | Accepted. The `.ses` result is a stored, reviewed input (item 11); placement change requires a new run and a diff review | Resolved in ADR |
| F5 | High | RF and antenna control weak (viewer review) | Accepted. DRC rule area, review set, pre-compliance scan and range test (items 3, 5); RISK-032. Viewer review is stated not to be RF evidence | Open (G2) |
| F6 | Medium | Human review gap, shared blind spots | Accepted. Review set signed by the owner (item 5) | Resolved in ADR |
| F7 | Medium | No enforcement of "no GUI edits" | Accepted. Marker plus regeneration gate | Open (not implemented) |
| F8 | Medium | Traceability check proves only presence; nets have no fields | Accepted. `nets.toml` and ID validation (item 2) | Resolved in ADR |
| F9 | Medium | Acceptance asked while prerequisites can fail | Accepted. ADR stays Proposed until G1 (item 9). Owner may still accept earlier | Resolved in ADR |
| F10 | Medium | Score not robust; safety and compliance not criteria | Accepted. Gates before scoring; sensitivity analysis; one score lowered | Resolved in ADR |
| F11 | Medium | Library provenance | Accepted. Project-local reviewed libraries for the critical parts (item 4) | Resolved in ADR |
| F12 | Medium | Mechanical coupling weaker than described | Accepted. "One source" scores lowered; item 10 states the consistency-check status | Resolved in ADR |
| F13 | Medium | No power, thermal, current-density verification | Accepted in part: design rules from requirements and ngspice flow in item 3 (not evidenced). Thermal and creepage checks are not added here; they belong in the HW requirements | Partly resolved |
| F14 | Low | No waiver process | Accepted. `waivers.toml` (item 3) | Resolved in ADR |
| F15 | Low | Dev and CI environments differ; no tool-change procedure | Accepted. Item 12 | Resolved in ADR |
| F16 | Low | Rule 12 wording drops the human gate for non-generated CAD; FreeCAD generator does not exist | Accepted. Item 7 rewritten | Resolved in ADR |
| F17 | Low | CI runs third-party code and a downloaded jar | Accepted. Jar pinned by hash and not downloaded unchecked (item 4) | Resolved in ADR |
| T1 | High | ADR cites a SKiDL reproducibility run not in the report | Verified: the run was made (netlist identical, placement differed); added to report section 6 as an observation without archived log | Resolved |
| T2 | High | Context and Comparison stale after round 3 | Accepted and rewritten | Resolved |
| T3 | High | Routing not scripted, not covered by the check | Accepted. Gate G1(d) and item 11 | Open (not implemented) |
| T4 | High | No detection for GUI edits beyond the narrow dump | Same as F3 and F7 | Open |
| T5 | High | Per-net requirement tracing untested; IDs not validated | Same as F8 | Resolved in ADR |
| T6 | High | Scores favour B beyond the spike | Accepted. B 101 to 95, C 96 to 93, sensitivity added; lead 2 points, stated as not robust | Resolved |
| T7 | High | RF and USB review not measurable | Same as F5 | Open (G2) |
| T8 | Medium | Gate wording ambiguous (before first file vs on first board) | Accepted. G1 and G2 split with numeric criteria | Resolved in ADR |
| T9 | Medium | Acceptance numbers and waivers undefined | Same as F14 | Resolved |
| T10 | Medium | CI pin unverified; CI image never run | Accepted. Open until the image is run and pinned | Open |
| T11 | Medium | Two connectivity sources | Same as C2 | Resolved |
| T12 | Medium | Rule 12 rewrite beyond the evidence; build output committed | Accepted. Exception recorded (item 1), FreeCAD wording limited (item 7) | Resolved in ADR |
| T13 | Medium | Interference check has no tolerance; notch cause unverified | Accepted. Numbers named in item 10; cause stays open | Open |
| T14 | Medium | Evidence provenance weak; logs not archived | Accepted in part: logs of the spike runs are not archived and the code is on an unmerged spike branch. Logs to be archived when the checks are scripted | Open |
| T15 | Medium | Simulation not part of the decision | Accepted. Stated as not evidenced (item 3) | Open |
| T16 | Low | Alternatives thin | Accepted in part: "not evaluated" note on other tools and the IPC API; no extra alternative written | Partly resolved |
| T17 | Low | Criteria sources loose; owner goal has no measure | Accepted. Metric: share of generated artefacts (verification section) | Resolved |
| T18 | Low | Fallback hides cost; trigger subjective | Accepted. Numeric trigger (item 6) | Resolved |
| T19 | Low | Risks not registered; no review | Accepted. RISK-032 to RISK-034 added; this record | Resolved |

## Not done
- The implementation-readiness goldfish (egm-review step 4) was not run: there is no implementation to judge, the ADR is a decision record, and gate G1 is open.
- The three reviewers did not run any tool or open the spike branch code; their evidence claims were checked against the documents only.

## Outcome
Approved with actions. Open actions before the owner accepts ADR-0012: pin the CI image and Python packages by digest and hash (F1, T10); write the tool-qualification table (F2); implement the widened dump and the regeneration gate (F3, F7); script the Freerouting steps (T3); decide the antenna topology (C5). The owner may accept earlier at their own risk; gate G1 stays a condition for generating product files.
