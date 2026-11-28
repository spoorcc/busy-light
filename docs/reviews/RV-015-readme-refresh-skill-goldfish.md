# Review Record RV-015

- **Subject:** `.claude/skills/readme-refresh/SKILL.md` (new skill, first version in commit `7300672`) with
  `scripts/readme_facts.py`
- **Type:** Design
- **Date:** 2026-11-21  **Reviewer(s):** one stateless goldfish subagent (implementation readiness)  **Independent?** yes
  (the goldfish got only the file path and the readiness question; the author resolved the findings and checked the
  claims against the repository)

## Findings
| # | Severity | Finding | Resolution | Status |
|---|----------|---------|------------|--------|
| 1 | High | `scripts/fab_p1.sh` cannot run where KiCad is only in the container: the wrapper covered only the render script, and the container has no KiKit, numpy or scipy. scipy was pinned only in `requirements-fab-test.txt`, so the fab-release build job (which installs only `requirements-fab.txt`) would also stop at the power check. | Step 4 gives the recipe: pins installed with the host pip into a folder, `fab_p1.sh` run in the container with `PYTHONPATH`. scipy moved to `requirements-fab.txt`; regression test `test_fab_requirements_cover_what_fab_p1_runs` (failed before with `['scipy']`). Run on 2026-11-21 with only `requirements-fab.txt`: exit 0, all gates passed, panel byte-identical to the one the images came from. | Fixed |
| 2 | Medium | The exit code of `fab_p1.sh` is not checked | Step 4: exit 0 required; exit 1 no render, report the gate; exit 2 stop | Fixed |
| 3 | Medium | "A defect is fixed in the script" conflicts with CLAUDE.md rules 1 and 6; `render_p1_images.sh` cited HW-009 (Draft) | Step 5: trace to an Approved requirement (HW-008) and a failing test where testable without KiCad; the script header now cites HW-008 only | Fixed |
| 4 | Medium | Step 3 "when ... changed" has no command or baseline, and leaves out the render script | Step 3: `git log` of the image commit, then the commits to the board, panel preset, `fab_p1.sh` and the render script since | Fixed |
| 5 | Low | Step 7 says the test proves the images are committed; it checked only that the files exist | The test now checks `git ls-files` in a git checkout (fails for an untracked image, checked); step 7 adds `git status --short` | Fixed |
| 6 | Low | No check that the README numbers match `readme_facts.py` | Step 7: give the counts in the report. An automatic check would tie the README wording to a pattern; not added | Fixed (by hand) |
| 7 | Low | The skill, script and test were untracked | Committed in `7300672` before the review result came back | Fixed |
| 8 | Low | Housing render needs matplotlib and numpy; no NOT RUN rule for a missing tool; the wrapper needs `-w "$PWD"` | Added to steps 3 and 4; the wrapper line was run once as written (2026-11-21) | Fixed |
| 9 | Low | "Newest journal file" and "many commits" are loose | Step 1: newest dated file with the command; `readme_facts.py` now counts the commits to each README's own folder, and step 6 reads every README with one or more | Fixed |

## Outcome
Approved with actions. The goldfish answered NO-GO because of finding 1; findings 1 to 9 are resolved, but a second
readiness pass was not run. The owner approves the skill by committing it. Not verified: a full refresh run by
following the final text (the P1 renders and `fab_p1.sh` were run in this session while the skill was written;
the housing render and the diagram build were not run, FreeCAD is not installed here).
