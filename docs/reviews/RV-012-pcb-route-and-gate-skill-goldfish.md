# Review Record RV-012

- **Subject:** `.claude/skills/pcb-route-and-gate/SKILL.md` (new skill, uncommitted)
- **Type:** Design
- **Date:** 2026-11-08  **Reviewer(s):** four stateless goldfish subagents (comprehension, accuracy, usability, implementation readiness)  **Independent?** yes (the goldfish got only the file path; the author resolved the findings and checked claims against the repo)

## Findings
| # | Severity | Finding | Resolution | Status |
|---|----------|---------|------------|--------|
| 1 | High | Exit code of `run_best.sh` also counts strict-gate FAIL lines (not only open items and hard findings); exit 1 also covers "no run finished" | Rewritten from `pcb_pick.py` | Fixed |
| 2 | High | Gate mode unclear; run scripts default `SPIKE_ALLOW_KNOWN_OPEN=1` | Step 3 sets the variable to 0; step 4 gives literal commands (DRC and ERC) | Fixed |
| 3 | High | No failure handling | Section "If it fails" added | Fixed |
| 4 | High | "Each waiver has a DEV-nnn" is wrong: zero-max entries are limits | Wording corrected; pass still tolerates DEV classes, report them | Fixed |
| 5 | Medium | No trace to an Approved requirement (CLAUDE.md rule 1) | Step 0 (HW-010) | Fixed |
| 6 | Medium | Numbers and weights in the skill would go stale | Removed; pointers to the report and `PIN_TIES` keys | Fixed |
| 7 | Medium | Missing prerequisites (jar, Java, `PCB_PYTHON`), input directory, `run_full.sh` argument order, ERC command | Added | Fixed |
| 8 | Medium | Trigger description too broad | Narrowed; excludes schematic capture, outline, production board | Fixed |
| 9 | Low | Test command path, `\cp -f`, journal, scratchpad, report heading format, "last table by position" | Added | Fixed |
| 10 | Low | Dirty tree, runtime and load of 12 parallel runs | Added (record `git status`) | Fixed |
| 11 | Info | Test that greps the skill's named symbols for renames | Rejected: over-engineering for one file | Rejected |
| 12 | Info | Move "worked once" section into the report | Kept as a short pointer; the evidence is already in the report | Rejected |
| 13 | Low | `pcb_pick` ranks by three counts only; `track_dangling` and similar findings do not rank | Stated in step 3 | Fixed |

## Outcome
Approved with actions. Re-check: the readiness goldfish answered NO-GO on its first pass because of findings 7 and 10; those are fixed, but a second readiness pass was not run. The owner approves the skill by committing it. Not verified: no batch was run by following the skill.
