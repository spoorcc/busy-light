# Review Record RV-005

- **Subject:** ADR-0013 licensing (Accepted by the owner 2026-11-04 without a goldfish review), with `LICENSE.md`, `REUSE.toml`, `CONTRIBUTING.md`, README licence section, NEED-012, `docs/regulatory/applicability.md`; commit d4f0d57 (text before this review)
- **Type:** Architecture (reviewed after acceptance)
- **Date:** 2026-11-04  **Reviewer(s):** three stateless goldfish subagents (comprehension; legal and risk lens; consistency and implementation lens)  **Independent?** partly: same model family as the author. Legal statements are guidance, not legal advice; items marked LAWYER need a professional.
- **Not run:** the implementation-readiness pass. `reuse lint` was run by me after the review (see L9).

## Comprehension check
The comprehension goldfish restated the decision correctly (Apache-2.0 for code, CC BY-NC-SA 4.0 for documents, hardware, mechanics and images; owner chose option F). Its open questions are findings L1 to L4 and L10.

## Findings
ADR-0013 is Accepted and immutable, so findings against its text are resolved by a superseding ADR (action A1), not by editing it.

| # | Severity | Finding | Resolution | Status |
|---|----------|---------|------------|--------|
| L1 | High | Critical review notes still say "PolyForm is used instead"; the decision is Apache-2.0. Option F is not in the comparison table and was scored after the owner chose it. Verified by reading the ADR. | Accepted. Cannot be edited in an Accepted ADR. Action A1: superseding ADR with a rewritten critical review, F in the table, and a statement that the owner overrode the recommendation. | Open (owner) |
| L2 | High | The gate "others cannot profit" is waived for the code (F lets anyone sell the Apache code) but the ADR does not say so plainly; a competitor can take the code and only redo the hardware. | Accepted. A1 states the gate applies to the device design, not the code, and records the competitor case. | Open (owner) |
| L3 | High | Outside contributions invited ("PRs welcome") while the contributor terms are a draft: a sign-off certifies origin but is not a licence grant; no patent grant for hardware contributors; employer release not covered. | Fixed now: `CONTRIBUTING.md` and README say outside code and document contributions are not accepted until a legal check; badge changed. RISK-037. Legal check LAWYER. | Fixed; legal check open |
| L4 | High | The meaning of "non-commercial" is vague (hobbyist selling a unit, school, charity, company build room, employee at home). "Use of a purchased unit is not restricted" is a promise not backed by licence text. | Accepted. RISK-036. Action A2: FAQ with examples and a written grant for purchased units. LAWYER. | Open |
| L5 | High | CC licences cover copyright, not the function of a board or the product made from it; README and LICENSE.md claim that selling devices built from the files needs a separate licence, which the licence text may not support. No trademark policy; patents not covered. | Accepted. LAWYER. Action A3: align the wording with what the licence grants; trademark and design-rights policy. | Open (lawyer) |
| L6 | High | The CRA role was scored without analysis; `applicability.md` still assumed the steward path. A commercial licence for the hardware is itself a commercial activity. | Fixed now: `applicability.md` question 4 states that the steward path cannot be assumed. RISK-038. LAWYER. | Fixed; legal check open |
| L7 | High | The four new risks the ADR promised are not in the risk register. Verified. | Fixed now: RISK-035 to RISK-038 added. | Resolved |
| L8 | Medium | `REUSE.toml` code globs miss paths where code will land (`hw/sim/`, `mech/analysis/`, other `hw/kicad` scripts); such code silently becomes CC BY-NC-SA. Third-party material under `hw/datasheets/` and `hw/kicad/libs/` would be relabelled by the catch-all. | Partly fixed now: globs added for `hw/sim`, `mech/analysis`, `hw/kicad/**/*.py`. Open: a CI check that fails when a code extension falls under the CC default; a rule that vendor material keeps its own licence. | Partly resolved |
| L9 | Low | Claim that the `LicenseRef-license-text` annotation fails `reuse lint`; and the "123 files" count cannot be reproduced. | Rejected the first: I ran `reuse lint` after the edits and it reports compliant with REUSE 3.3 (129 of 129 files with licence information). Accepted the second: counts go stale; cite a date and command, not a number. | Resolved |
| L10 | Medium | No NOTICE file; per-file SPDX headers missing for code (a path map does not travel with a file that moves upstream, for example into Zephyr). | Accepted. Action A4. | Open |
| L11 | Medium | Compatibility table for third-party parts (Wi-Fi blobs, Mbed TLS dual licence, KiCad libraries, Noto Sans) does not exist. | Accepted. RISK-035. Action A5, with SYS-044. | Open |
| L12 | Medium | Generated KiCad files are CC BY-NC-SA while their generators are Apache-2.0; the licence of generated output and of code inside documents is not stated. | Accepted. Action A1 states it. LAWYER. | Open |
| L13 | Medium | `.claude/` falls under the CC default (open item without an owner or date); NEED-012 is titled "Open source" but is two licences. | Accepted. Owner to decide `.claude/`; rename NEED-012. | Open (owner) |
| L14 | Medium | Copyright claim "2026 Ben Spoor" for AI-assisted content; employment contract not checked. | Accepted. LAWYER. | Open (lawyer) |
| L15 | Low | Wording ("open source" for the Apache code only); CC facts "to be checked" were never recorded. | Accepted. Record the check with URL and date in A1. | Open |

## Outcome
**Approved with actions, after the fact.** ADR-0013 stays Accepted. It was accepted without this review, which broke working rule 0 of CLAUDE.md; this record closes that gap, and the findings that need ADR changes go into a superseding ADR if the owner agrees.

## Actions
A1 superseding ADR (owner decides whether to write it); A2 FAQ and purchased-unit grant; A3 wording of README and LICENSE.md; A4 NOTICE file and SPDX headers; A5 compatibility table; the lawyer items L3, L4, L5, L6, L12, L14 before the first outside contribution or sale.
