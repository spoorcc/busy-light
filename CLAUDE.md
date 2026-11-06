# busy-light

Embedded product: Zephyr software (`sw/`), KiCad hardware (`hw/kicad/`), FreeCAD mechanics (`mech/freecad/`).
Run like a regulated-company project. **Read `docs/process/README.md` before doing design or implementation work.**

## Non-negotiable working rules
0. **Plan with the Elephant-Goldfish Model** (`docs/process/planning-egm.md`; skills `egm-plan`, `egm-review`). During
   planning you are the Elephant: no code, interview the user, draft the design doc, then have stateless goldfish
   subagents review it. Skip only for trivial fixes.
1. **Specification before implementation.** Do not write or change `sw/`, `hw/` or `mech/` content unless it
   traces to an `Approved` requirement. If none exists, draft the requirement (skill `write-requirements`) and ask
   the user to approve it. Only the user approves documents; never set `Approved`/`Accepted` yourself.
2. **Decisions are recorded.** Any significant or hard-to-reverse choice gets an ADR with >= 2 real alternatives
   (skill `write-adr`). Present a recommendation with reasoning, not a survey.
3. **Be critical.** Challenge assumptions, point out ambiguity, risks, missing requirements and weak alternatives
   - including in the user's own proposals - before proceeding. Skill: `design-review`.
4. **Non-functional by default.** Always consider testability, auditability, safety, security, power/resource
   margins, manufacturability (checklist: process doc section 5).
5. **Follow `docs/standards/`.** C code: CERT C + MISRA C subset (never claim MISRA compliance without a report);
   hardware and mechanical: DFx (testability/DFT first). Record deviations as `DEV-nnn`.
6. **Tests with all code.** No code without an accompanying test in the same change (bug fix = failing regression test
   first). Hardware: verify by simulation/analysis (ngspice, worst-case, power budget, ERC/DRC, thermal...) wherever
   feasible, results in `hw/sim/`; mechanical: interference/tolerance/FEM in `mech/analysis/`. See
   `docs/process/verification-strategy.md`. Say plainly what was not run.
7. **Design for CE/market access from the start.** Follow `docs/regulatory/` (CRA, RED/LVD/EMCD, RoHS...). Check changes
   with skill `regulatory-check`, keep the compliance matrix and technical file (`docs/regulatory/technical-file/`) current as evidence
   is produced. Never state the product "is compliant"; state which evidence exists. Legal statements are guidance, not legal advice.
8. **User documentation is part of the product.** Follow `docs/standards/writing.md` (ASD-STE100 principles: imperative steps,
   one instruction per step, max 20 words; safety messages before the step; one term per concept via `docs/user/glossary.md`).
   Skill `write-user-docs`. Run `python3 -I scripts/check_docs_style.py`. Never invent specifications in manuals.
9. **Diagrams as code.** Every diagram/graphic is text source (PlantUML, Mermaid, WaveDrom; KiCad/FreeCAD exports via CLI),
   never hand-drawn or hand-edited SVG/PNG. Skill `write-diagrams`; run `scripts/build_diagrams.sh --check`. Diagrams show only facts that exist in requirements/architecture.
10. **Traceability.** Reference IDs (`SW-012`, `ADR-0003`) in commits and PRs; run
   `python3 -I scripts/check_traceability.py` after touching `docs/`.
11. **Evidence over claims.** Report test/build results exactly as observed. Never claim something is verified
   without recorded evidence; say what was not run.
12. Never hand-edit `.kicad_*` or `.FCStd` files, and do not ask the user for GUI edits. Make CAD changes only through
    the KiCad and FreeCAD scripting APIs (pcbnew, kicad-cli, FreeCAD Python), with the scripts kept in `scripts/` so the
    change is reproducible. Do not commit build output.
13. Add an entry to `CHANGELOG.md` (Keep a Changelog, section `[Unreleased]`) for every user-visible or release-relevant change.
14. Commit only when asked. Do not rewrite history on `main`.

## Layout
`docs/` (process, requirements, architecture, decisions, risk, verification, reviews, plans, templates),
`sw/` (west manifest + `app/`), `hw/` (kicad, fabrication, datasheets), `mech/` (freecad, exports, drawings),
`scripts/`, `.claude/skills/`.

## Build
`west init -l sw && west update`, then `west build -b <board> sw/app`.
