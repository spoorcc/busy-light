---
name: write-adr
description: Write an architecture decision record with weighted criteria, real alternatives, trade-offs and critical review. Use for any costly-to-reverse or cross-domain design choice.
---

# Write an ADR

1. Next number: highest `docs/decisions/ADR-nnnn-*.md` + 1. File: `docs/decisions/ADR-nnnn-kebab-title.md`
   from `docs/templates/adr.md`. Heading must be `# ADR-nnnn: Title` (the trace checker reads it).
2. Derive criteria and weights from existing requirements (cite IDs). If requirements are missing, flag it.
3. Research alternatives with evidence (datasheets, measurements, docs). Include >= 2 viable options
   plus "do nothing/defer". No strawmen: state the strongest case for each rejected option.
4. Fill the comparison table, then decide. Record negative consequences, new risks, and how/when to revisit.
5. Add "Critical review notes": the strongest objection and the answer.
6. Status stays `Proposed` until the user accepts. Accepted ADRs are immutable - supersede, don't edit.
