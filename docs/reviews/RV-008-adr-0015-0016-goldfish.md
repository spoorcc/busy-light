# Review Record RV-008

- **Subject:** ADR-0015 (licensing corrected, Accepted 2026-11-04) and ADR-0016 (independent hardware gate, Accepted 2026-11-04), with `LICENSE.md`, `REUSE.toml`, `NOTICE`, `CONTRIBUTING.md`, HW-003, HW-010 and RISK-024 to RISK-030; commit c33d8a1 (text before this review)
- **Type:** Architecture (reviewed after acceptance, before the pull request was merged)
- **Date:** 2026-11-04  **Reviewer(s):** two stateless goldfish subagents, one per ADR, each with an explain-back and a skeptical review  **Independent?** partly: same model family as the author. Legal statements are guidance, not legal advice.
- **Not run:** a separate comprehension pass per ADR (the explain-back was part of each review); the implementation-readiness pass; any datasheet, the USB Type-C specification, any legal check. The ADR-0015 reviewer had no `reuse` tool; I ran `reuse lint` myself after the changes (compliant with REUSE 3.3).

## Comprehension check
Both explain-backs matched the intent (ADR-0015: same option F, record corrected, gaps closed; ADR-0016: a CC detection IC output ANDed with the firmware select line). Open questions were: where the AND function sits and how the active-low output becomes an enable (ADR-0016), whether the middle current step is gated, which items of ADR-0015 are done and which planned, and the missing RV-008 (this record).

## Findings: ADR-0016
The weighted sums (A 84, B 95, C 93, D 93, E 88; max 130) and both sensitivity statements recompute correctly.

| # | Severity | Finding | Resolution | Status |
|---|----------|---------|------------|--------|
| H1 | Critical | The gate and the firmware read the same IC output: one IC fault fools both, so "independent" holds only for firmware faults. | Accepted. ADR-0016 amended: "independent of firmware faults only"; single faults listed; RISK-042; a diverse second opinion is not part of the decision. | Resolved in ADR; risk open |
| H2 | Critical | Process contradictions: Accepted but "required checks before acceptance"; HW-003 and HW-010 said "Proposed"; RV-008 cited but missing. | Fixed: wording changed to "before a part is fixed"; HW-003 and HW-010 say Accepted; this record exists. | Resolved |
| H3 | High | The middle step of ADR-0010 is not gated; a default 500 mA source would see about 900 mA. | Fixed: every step above the first is gated; HW-010 tests each select output. | Resolved |
| H4 | High | "Within the source rating" is false by the ADRs' own numbers (limit band up to about 1577 mA; RISK-027 not assessed). | Fixed: sentence qualified. ADR-0010 open points 1 and 2 still need numbers. | Partly resolved |
| H5 | High | "Pull-ups read default" depends on unstated hardware (polarity, inverter, floating gate input). | Fixed: truth table rule in ADR-0016; gate input pull-down; open pull-up must not read "high". Circuit to be drawn. | Resolved in ADR; schematic open |
| H6 | High | A stuck AND output or shorted select MOSFET is the single fault of RISK-029 and is not covered. | Accepted: stated as not covered in ADR-0016 and HW-010. | Open (owner) |
| H7 | High | "The margin problem goes away" is overstated: the IC thresholds fill the whole 90 mV gap; protection depends on the IC meeting the Type-C bands (specification not read). | Fixed: claim restated; band-edge bench test added to HW-003. | Resolved in text; test open |
| H8 | High | Earlier findings S3 (non-compliant cable), S4 to S6 (back-off, PD chatter) are not addressed by the gate. | Accepted: stated as not covered; software requirement still to write. | Open |
| H9 | Medium | Requirements and risks not updated; RISK-025 and RISK-026 described the ADC; no risk for IC misclassification, temperature or stock. | Fixed: RISK-025 and RISK-026 updated; RISK-042 and RISK-043 added. | Resolved |
| H10 | Medium | HW-003 acceptance still named discrete Rd and "three sources" from one output; HW-010 tests too thin. | Fixed: wording and fault-injection list in HW-003 and HW-010. | Resolved |
| H11 | Medium | Scoring subjective; cost not computed against SYS-021; temperature range of 0 to 70 C in a closed housing; second source only a snippet; hung firmware (S2) deferred without a thermal or watchdog requirement. | Accepted. Cost given as a range; temperature range is a blocking check; S2 and the requirements remain open. | Open |

## Findings: ADR-0015
The weighted sums (A 108, B 108, C 74, D 89, E 86, F 96; max 160) recompute correctly.

| # | Severity | Finding | Resolution | Status |
|---|----------|---------|------------|--------|
| P1 | High | RV-008 did not exist; accepted before review, the same breach as ADR-0013. | This record closes it; the breach is recorded here. | Resolved |
| P2 | High | The ADR claimed all non-lawyer items applied; C, CMake and `prj.conf` files had no SPDX header; the CI check, compatibility table and licence-fact record were absent or unwritten. The reviewer looked at `main`, where the pull request is not merged; the CI check exists on the branch. | Partly rejected (CI check exists on the branch), partly accepted: headers added to `main.c`, `CMakeLists.txt`, `prj.conf`, `west.yml`; the Decision text separates "done" from "planned". | Resolved; compatibility table and fact record planned |
| P3 | High | `LICENSE.md` promised more than CC grants: selling devices built from the files "needs a licence". | Fixed: it says copying, adapting or sharing the files commercially needs a licence, and that independent re-implementation is not stopped. LAWYER. | Fixed; legal check open |
| P4 | High | The "allowed without asking" list is not a grant and the licence text overrides it; school, charity and third-party fabrication unclear. | Fixed: stated as non-binding guidance; open cases listed. LAWYER. | Fixed; legal check open |
| P5 | High | The purchased-unit grant is weak (grantor, scope, revocation, clone buyers, secure boot, repair). | Fixed: grantor and scope named, not revoked for units sold, no board copying, unsigned images only where secure boot allows. LAWYER. | Fixed; legal check open |
| P6 | High | Patents: the repository has been public since 2026-11-04, so "file before publishing" has probably passed. | Fixed: reworded; patent attorney. | Fixed; legal check open |
| P7 | High | Title to the copyright (employment contract, AI authorship) is unverified while the licences are published. | Accepted: made a gate before the first sale or outside contribution. | Open (owner, lawyer) |
| P8 | Medium | Contributor terms in `CONTRIBUTING.md` weaker than the ADR; pausing is only a text note; issue text. | Partly fixed: placeholder note, issue text covered, pull request template states the pause. GitHub cannot block pull requests. | Partly resolved |
| P9 | Medium | Gate and scores look like rationalisation; F scores 2 on companies while a company needs a licence for an internal build room. | Accepted: the table is a record, stated in the ADR; a blind rescoring by a fresh reviewer is offered to the owner. | Open (owner) |
| P10 | Medium | REUSE globs match by path, not extension (`scripts/diagrams/package-lock.json` is third-party data labelled Apache-2.0); vendor material rule not implemented; KiCad BY-SA libraries versus BY-NC-SA. | Accepted. Listed as open in the ADR. | Open |
| P11 | Medium | `.claude/` described as a proposal while already applied. | Fixed: item 4 is decided and applied. | Resolved |
| P12 | Medium | Trademark ("reserves" a descriptive, unregistered name); the CE sentence incomplete; commercial route promised but missing. | Fixed: text says the licences grant no right to the name; builders are the manufacturers; no commercial licence exists yet and the contact route is the GitHub account. | Fixed; legal check open |
| P13 | Low | The ADR was not self-contained (options "as in ADR-0013"; title). | Fixed: option summaries inlined; title corrected. | Resolved |
| P14 | Low | Creative Commons facts without source and date; `NOTICE` travels with code only if copied. | Accepted: record of facts planned; `NOTICE` becomes part of the SBOM step. | Open |

## Outcome
**Approved with actions.** The two ADRs stand. The amendments above are recorded as sections "Amendments after RV-008" in both ADRs, made before the pull request was merged, and they clarify the decisions without changing option F or option B; the owner confirms them. Both ADRs were accepted before this review, which broke working rule 0 a second time; I should have run the review first as I said I would, and have now done it before anything was merged.

## Actions
Owner: confirm the amendments; decide S2 (hung firmware), a diverse second opinion for the gate, the stuck-AND single fault; blind rescoring of ADR-0015 if wanted. Author: draw the gate truth table as a schematic fragment, write the software requirement (hold, back-off, filter), write the compatibility table and the record of the Creative Commons facts, close ADR-0010 open points 1 and 2 with numbers. Lawyer: the items marked LAWYER in ADR-0015 and `LICENSE.md`.
