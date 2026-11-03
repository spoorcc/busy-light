# ADR-0001: Coding standard basis for project C code

- **Status:** Proposed
- **Date:** 2026-11-03
- **Deciders / reviewers:** (maintainer to accept)
- **Related:** `docs/standards/coding-sw.md`

## Context and problem
Zephyr C firmware must be developed to a recognised standard to support robustness, security and audit.
Requirement IDs for this do not exist yet (no SYS requirements written) -- criteria below are provisional and
must be re-based on SYS-level safety/security requirements once those exist.

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
Qualitative: A best balances automation, cost and credibility; B best on recognition but worst on openness; C cheapest, weakest evidence.
Scores to be completed when criteria are linked to requirements.

## Decision
Proposed: A. Awaiting maintainer acceptance.

## Consequences
- Positive: automatable evidence (clang-tidy, warnings-as-errors), freely reproducible by contributors.
- **Negative:** dual-standard overhead; MISRA claim requires a compliance report and deviation process; possible need for a paid tool later.
- New risks: false confidence from partial checking -> do not claim MISRA compliance without report.

## Verification and revisit
CI shows clean `cert-*` on `sw/app`; MISRA tool selection reviewed before first release; revisit if safety classification requirement appears.

## Critical review notes
Strongest objection: "dual standards is bureaucracy for a busy light." Answer: scope is project-owned code only, mostly automated; the
user explicitly asked for regulated-company rigour, and retrofitting is costlier than starting compliant.
