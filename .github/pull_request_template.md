> Outside pull requests with code or documents are not accepted yet (contributor terms need a legal check, see CONTRIBUTING.md).

## Summary
What and why. Link requirement/ADR IDs: 

## Traceability
- [ ] Requirement(s) Approved and referenced (e.g. `SW-012`)
- [ ] ADR added/updated for any significant design decision (>= 2 alternatives)
- [ ] **Every code change has an accompanying test** (cites `TC-nnn`); regression test for bug fixes
- [ ] HW: simulation/analysis results in `hw/sim/` (or justification why not feasible)
- [ ] Non-trivial change: design doc approved after EGM review (`RV-nnn`)
- [ ] Verification added/updated (`TC-nnn`) and evidence attached
- [ ] `python3 scripts/check_traceability.py` passes

## Critical review checklist
- [ ] Does this solve the stated requirement -- and *only* that (no scope creep)?
- [ ] Failure modes considered; fail-safe behaviour defined and tested
- [ ] Non-functional impact assessed: testability, auditability, security, power, resources, EMC, manufacturability
- [ ] Alternatives genuinely considered, not strawmen
- [ ] No unreviewed generated/binary artefacts; build is reproducible
- [ ] Warnings clean (-Werror / ERC / DRC / interference check)
- [ ] SW: CERT C / MISRA subset clean (clang-tidy, MISRA check), suppressions carry `DEV-nnn`
- [ ] HW: DFx checklist (`docs/standards/design-hw.md` s.8) -- DFT/DFM/DFA/DFR/EMC/supply chain; ERC/DRC clean
- [ ] MECH: DFx checklist (`docs/standards/design-mech.md` s.8) -- process rules, tolerances, test/service access, STEP interference check
- [ ] Regulatory: applicability inputs unchanged (or `applicability.md` updated); `Regulatory:` fields, compliance matrix and technical-file index updated; SBOM refreshed if dependencies changed
- [ ] User-visible change: `docs/user/` updated to `docs/standards/writing.md`; `check_docs_style.py` passes; procedure usability TC added
- [ ] Diagrams are code (`docs/standards/diagrams.md`); `scripts/build_diagrams.sh --check` passes
- [ ] `CHANGELOG.md` updated under `[Unreleased]` (user-visible or release-relevant change)
- [ ] Docs updated; version/identity strings updated if applicable

## Review type
- [ ] Independent review  - [ ] Self-review after cooling-off (state why)
