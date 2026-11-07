# ADR-0001: Coding standard basis for project C code

- **Status:** Accepted (by the owner, Ben Spoor, 2026-11-07, in the working session, option A, after the gaps in the text were fixed; recorded by the assistant)
- **Date:** 2026-11-03
- **Deciders / reviewers:** Ben Spoor (owner, the only one who accepts); gaps fixed 2026-11-07 before acceptance (criteria linked, scores completed)
- **Related:** NEED-011, SYS-025, SYS-043, SYS-044, SYS-045; `docs/standards/coding-sw.md`; `docs/regulatory/applicability.md` (CRA)

## Context and problem
Zephyr C firmware must be developed to a recognised standard to support robustness, security and audit.
The criteria below are derived from NEED-011 (engineered like a product from a regulated company: testable and auditable),
SYS-025 (logic testable on the host, so a tool-checked standard fits CI), SYS-043 to SYS-045 (secure boot, software bill of materials,
vulnerability handling: security coverage and audit evidence) and the CRA applicability record (`docs/regulatory/applicability.md`).
No SYS requirement names a coding standard; this ADR is the decision that `docs/standards/coding-sw.md` implements.

## Decision criteria
| Criterion | Weight (1-5) |
|-----------|--------------|
| Tool support that is automatable in CI at zero/low cost | 5 |
| Alignment with Zephyr (we integrate with its APIs) | 4 |
| Recognised in regulated industries (audit credibility) | 4 |
| Freely accessible to open-source contributors | 4 |
| Security coverage | 3 |

## Alternatives considered
### A. CERT C primary + MISRA C subset aligned with Zephyr (proposed)
Free standard, clang-tidy `cert-*` in CI; MISRA subset for credibility. Cons: two rule sets, MISRA checking needs cppcheck addon
with locally-sourced rule text or commercial tool; some overlap/conflicts to manage.
### B. MISRA C only
Strong industry recognition. Cons: document is paid and not redistributable (barrier for contributors); good free tooling is limited;
Zephyr itself only partly compliant, so friction with upstream APIs.
### C. Zephyr style/guidelines only
Lowest effort and friction. Cons: weakest audit story; no formal rule-level compliance evidence.
### D. Defer
Risks inconsistent early code that is expensive to retrofit.

## Comparison
Scores 0 to 5 per criterion, the author's judgement from the alternative descriptions above (not measured; no tool was run for this ADR). Maximum 100.

| Criterion (weight) | A CERT C + MISRA subset | B MISRA only | C Zephyr style only | D Defer |
|---|---|---|---|---|
| CI automation at low cost (5) | 4 | 2 | 3 | 0 |
| Alignment with Zephyr (4) | 4 | 2 | 5 | 3 |
| Recognised in regulated industries (4) | 3 | 5 | 1 | 0 |
| Free for open-source contributors (4) | 5 | 1 | 5 | 5 |
| Security coverage (3) | 5 | 3 | 1 | 0 |
| **Weighted sum (max 100)** | **83** | 51 | 62 | 32 |

A leads C by 21 points, more than the scoring error. B scores highest on recognition and lowest on openness. Qualitative reading: A best balances automation, cost and credibility; B best on recognition but worst on openness; C cheapest, weakest evidence.

## Decision
A: CERT C primary plus a MISRA C subset aligned with Zephyr. Accepted by the owner on 2026-11-07.

## Consequences
- Positive: automatable evidence (clang-tidy, warnings-as-errors), freely reproducible by contributors.
- **Negative:** dual-standard overhead; MISRA claim requires a compliance report and deviation process; possible need for a paid tool later.
- New risks: false confidence from partial checking -> do not claim MISRA compliance without report.

## Verification and revisit
CI shows clean `cert-*` on `sw/app`; MISRA tool selection reviewed before first release; revisit if safety classification requirement appears.

## Critical review notes
Strongest objection: "dual standards is bureaucracy for a busy light." Answer: scope is project-owned code only, mostly automated; the
user explicitly asked for regulated-company rigour, and retrofitting is costlier than starting compliant.
