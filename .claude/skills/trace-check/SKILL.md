---
name: trace-check
description: Run and interpret the traceability check over docs/ (requirements, ADRs, risks, test cases).
---

Run `python3 -I scripts/check_traceability.py` (add `--strict` before a release: warnings become errors).
Errors: duplicate IDs, links to undefined IDs, requirements without `Parent`, test cases without `Verifies`.
Warnings: requirements without a verifying TC, risks without mitigation. Fix the docs, never the checker, unless
the checker itself is wrong (then say so explicitly).
