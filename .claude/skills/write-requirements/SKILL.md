---
name: write-requirements
description: Draft or review requirements (NEED/SYS/SW/HW/MECH) to this project's standard - atomic, testable, traceable, with rationale and the non-functional checklist. Use before any implementation work.
---

# Write requirements

1. Read `docs/process/README.md` (sections 4 and 5) and `docs/templates/requirement.md`.
2. Identify the parent (NEED/SYS/ARCH). If none exists, stop and create/ask for it first.
3. Write each requirement using the template: one "shall", measurable acceptance criteria,
   rationale, verification method, `Parent`, and a `Verified by` TC (create the TC stub too).
4. Walk the NFR checklist (testability, auditability, safety, security, reliability, ...) and
   add requirements or record "not applicable because ...".
5. Be critical: list ambiguities, unstated assumptions, conflicting or missing requirements and
   open questions for the user *before* marking anything `In Review`. Never mark `Approved` yourself.
6. Run `python3 scripts/check_traceability.py` and fix errors.
