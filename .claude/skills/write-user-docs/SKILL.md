---
name: write-user-docs
description: Write or review user-facing documentation (manual, quick start, procedures, safety messages) to the project's ASD-STE100-based standard.
---

# Write user documentation

1. Read `docs/standards/writing.md` and `docs/templates/procedure.md`; use terms from `docs/user/glossary.md` (add new terms there first).
2. Source facts only from Approved requirements and verified behaviour. Do not invent specifications; mark gaps `TBD` and ask.
3. Write task-based procedures: imperative, one instruction per step, max 20 words, expected result, failure path.
   Put WARNING/CAUTION/NOTE before the step. Do not rely on colour alone.
4. Run `python3 -I scripts/check_docs_style.py`; fix findings. Then review for STE principles manually (the script is partial).
5. Add a usability `TC-nnn` per procedure (executed verbatim by a person who did not write it). Update the technical-file index.
