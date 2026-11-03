---
name: egm-plan
description: Plan a feature or design change using the Elephant-Goldfish Model - brainstorm and draft a design doc with no code, then hand it to goldfish review. Use before any non-trivial implementation.
---

# EGM planning (you are the Elephant)

Read `docs/process/planning-egm.md` first.

1. **Brainstorm (no code).** Load context: requirements, ADRs, risks, standards. Interview the user: ask about goals,
   constraints, assumptions, failure modes, non-functional needs. Debate trade-offs; challenge weak assumptions,
   including the user's. Do not create or edit anything under `sw/`, `hw/`, `mech/`.
2. **Draft** `docs/plans/NN-title.md` from `docs/templates/plan.md`. Include a concrete implementation plan (exact files,
   signatures, nets, features) and a test/verification plan: tests for all code, simulation/analysis for hardware
   (`docs/process/verification-strategy.md`).
3. Run the `egm-review` skill. Resolve every critique in writing. Present the result and the open questions to the user.
4. Only the user sets the plan to `Approved`. Do not start implementation before that.
