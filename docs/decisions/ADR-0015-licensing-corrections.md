# ADR-0015: Licensing, corrected and completed (supersedes ADR-0013)

- **Status:** Accepted (by the owner, Ben Spoor, 2026-11-04, on explicit instruction in the session, after the options were presented as recommendations). Supersedes ADR-0013. Accepted before its own goldfish review; the review RV-008 followed and its amendments are listed below.
- **Date:** 2026-11-04
- **Deciders / reviewers:** Ben Spoor (owner); reviewed as RV-005 (goldfish review of ADR-0013, 2026-11-04); this ADR itself was accepted before its own review; a goldfish review of ADR-0015 and ADR-0016 is recorded as RV-008. Not legal advice; the items marked LAWYER need a professional before the first outside contribution or commercial sale.
- **Related:** NEED-012, SYS-044, RISK-020, RISK-035, RISK-036, RISK-037, RISK-038, ADR-0013, ADR-0012; RV-005; `docs/regulatory/applicability.md`

## Context and problem
ADR-0013 was accepted by the owner on 2026-11-04 without a goldfish review. The review RV-005 found that the decision (option F: Apache-2.0 for code, CC BY-NC-SA 4.0 for documents, hardware, mechanics and images) can stand, but that the ADR text has defects that an Accepted ADR cannot fix by editing:
- the critical review notes still describe a PolyForm licence that the decision does not use;
- option F is not in the comparison table and was scored after the owner chose it;
- the owner wish "others cannot profit" is waived for the code without saying so;
- several promises have no basis in the licence text (purchased units, the meaning of "non-commercial", generated output, code inside documents);
- the contributor terms, trademark, patents, the NOTICE file, third-party material and `.claude/` are open or unstated.
This ADR restates the decision, corrects the record, and closes the gaps. It changes **no licence** of any file in the repository.

Not known: how the CRA treats a source-available project with a commercial licence (LAWYER); whether the non-commercial boundary holds in each EU country (LAWYER); copyright in AI-assisted content (LAWYER).

## Decision criteria
Unchanged from ADR-0013 (weights 1 to 5), so the scores can be compared.
| Criterion | Weight | Source |
|-----------|--------|--------|
| Others cannot profit from copies (owner wish) | 5 | owner 2026-11-04 |
| Counts as open source (OSI and OSHWA) | 3 | NEED-012 |
| Attracts contributors and reviewers | 3 | process README |
| Compatible with upstreaming drivers to Zephyr (Apache-2.0) | 4 | owner |
| Simple CRA position (low confidence for every option, RV-005 L6) | 3 | `applicability.md` |
| Licence text is mature and unambiguous | 4 | legal risk |
| Companies can use or build units for internal use | 3 | target users |
| Reversible once published | 3 | grants cannot be withdrawn |
| Keeps the option of a commercial licence by the owner | 4 | owner |

**Gate, stated precisely (correction of ADR-0013):** an option passes if others cannot sell copies **of the device design** (board, housing, manual) without a licence from the owner. The gate is **not** applied to the code. Options A and B fail it; they are scored for reference. Option F passes for the device design and fails for the code, which the owner accepted on 2026-11-04.

## Alternatives considered
The six options are those of ADR-0013: **A** permissive open licences (Apache-2.0, CERN-OHL-P, CC BY 4.0); **B** copyleft open licences (AGPL or GPL, CERN-OHL-S, CC BY-SA 4.0); **C** non-commercial source-available (PolyForm Noncommercial for code, CC BY-NC-SA 4.0 for the rest); **D** option C plus a commercial licence by the owner and a CLA; **E** all rights reserved (defer); **F** Apache-2.0 for code and CC BY-NC-SA 4.0 for the rest. The full descriptions and their strongest cases are in ADR-0013. One change: **E** (all rights reserved) scores 5 on "others cannot profit", because nobody may copy anything; ADR-0013 gave it 3.

## Comparison
Scores 0 to 5, my judgement. **F was scored by the author after the owner chose it** (ADR-0013); the table is a record, not the input of the decision. Max 160.
| Criterion (weight) | A | B | C | D | E | F |
|--------------------|---|---|---|---|---|---|
| Others cannot profit (5) | 0 | 2 | 5 | 5 | 5 | 3 |
| Counts as open source (3) | 5 | 5 | 0 | 0 | 0 | 2 |
| Attracts contributors (3) | 5 | 4 | 2 | 2 | 0 | 3 |
| Zephyr upstream compatible (4) | 5 | 3 | 2 | 2 | 0 | 5 |
| Simple CRA position (3) | 4 | 4 | 3 | 3 | 2 | 3 |
| Mature, unambiguous text (4) | 5 | 5 | 3 | 3 | 5 | 4 |
| Companies can use or build (3) | 5 | 4 | 1 | 2 | 0 | 2 |
| Reversible (3) | 1 | 1 | 1 | 1 | 5 | 1 |
| Commercial option for the owner (4) | 2 | 3 | 2 | 5 | 5 | 3 |
| **Weighted sum (max 160)** | 108 | 108 | 74 | 89 | 86 | 96 |

Among the options that pass the corrected gate (C, D, E, F), F scores 96, D 89, E 86 and C 74. The lead of F over D is 7 points, which is inside my scoring error. F's advantage is the Zephyr criterion (weight 4, score 5) and the mature text; D's is the commercial option. The owner decided F; this table does not overturn that and does not prove it.

## Decision
**Owner decision 2026-11-04: Accepted with the recommended options.** Done with the acceptance: items 1, 2, 4, the SPDX headers and the CI check of item 8, `NOTICE`, and the written positions of items 3, 5, 6, 9, 10 and 11 in `LICENSE.md` (flagged as not legal advice). Planned, not done: the compatibility table, the record of the Creative Commons facts (source and date), and the legal check of items 3, 5, 6, 7, 9, 10 and 11. Items 1 and 2 restate ADR-0013; items 3 to 11 are new.
1. **Code is Apache-2.0** (firmware in `sw/`, scripts, generators, build files, CI). **Documents, hardware files, mechanics and images are CC BY-NC-SA 4.0.** (Unchanged.)
2. **Wording:** the code is "open source"; the rest is "source-available" and not open source hardware. (Unchanged.)
3. **Generated output.** A file produced by an Apache-2.0 generator (KiCad or FreeCAD files, rendered SVG) belongs to the design and is CC BY-NC-SA 4.0; the generator stays Apache-2.0. Code in a document (snippets, examples) is Apache-2.0 and carries an SPDX line. Diagram sources are documentation (CC BY-NC-SA 4.0). LAWYER: whether the generator licence reaches the output.
4. **`.claude/` (skills and instructions): proposal Apache-2.0**, because they are instructions for automation and the repository's code licence fits them better; the owner decides. (ADR-0013 left it open.)
5. **Purchased units.** The owner states in `LICENSE.md` that a buyer may use, repair and operate a unit, run and reflash the published firmware, and print the user manual for internal use of that unit. This grant is written down; ADR-0013 only promised it. LAWYER.
6. **Meaning of "non-commercial" (the owner's reading, to be published as an FAQ, LAWYER):**
   - Allowed: a person builds one unit for their own use; a school, club or charity builds units for teaching or its own use; a researcher builds units for a study; sharing changes under the same licence.
   - Needs a commercial licence: selling units, kits or services built from the files; a company building units from the files for its own business (including a build room); a distributor or contract manufacturer building units for others.
   - Unclear, ask the owner: a hobbyist selling a single unit at cost; an employee building one unit at home with company help.
7. **Contributor terms.** No outside contribution is accepted until a lawyer checks them (`CONTRIBUTING.md` says so since 2026-11-04). Intended terms: a DCO sign-off (`git commit -s`), code under Apache-2.0 including its patent grant, other work under CC BY-NC-SA 4.0 plus a perpetual, irrevocable, sublicensable grant to the owner to license it commercially, a patent licence for hardware and mechanical contributions, and a statement that employee contributions need the employer's release. A CLA bot is optional.
8. **Source headers, NOTICE and third-party material.** Every code file gets an SPDX header (a path map does not travel with a file that moves, for example upstream into Zephyr). A `NOTICE` file lists third-party attributions required by Apache-2.0 section 4. Third-party material keeps its own licence: vendor datasheets are linked, not committed; imported KiCad libraries keep their upstream licence through their own REUSE entries; a compatibility table of every SBOM component (Wi-Fi blobs, Mbed TLS licence choice, KiCad libraries, Noto Sans under the SIL OFL) is part of the technical file. A CI check fails when a code file falls under the CC default.
9. **Trademark and CE.** The name "busy-light" and its logo are not licensed by any of these licences; the owner reserves them (name availability in the EU to check, LAWYER). Units built by others are not covered by any CE claim of the owner.
10. **Patents.** No patent is held or claimed by the owner today. CC licences do not grant patent rights; the Apache-2.0 patent grant covers the code. The owner decides whether to file anything before publishing designs.
11. **Authorship.** The repository is written with an AI assistant. The licences apply to the extent that copyright exists. The owner checks their employment contract for any claim on side projects (LAWYER).

## Consequences
- Positive: the record matches the repository; the unstated promises are written down or removed; contributors and users know the rules; the ADR can be audited.
- **Negative / trade-offs accepted:** F still lets anyone sell the code, including a competitor who redoes only the hardware; the hardware and documents are not open source; companies cannot build units from the files without a licence; the non-commercial boundary can still be disputed; contributions are paused until the legal check; the owner takes on maintaining an FAQ and a commercial licence.
- New risks: RISK-035 to RISK-038 (already in the register, from RV-005).
- Requirements created or changed: NEED-012 (rename to "Licensing and publication", with an acceptance criterion: `reuse lint` passes and the compatibility table exists); `LICENSE.md` (purchased-unit grant, FAQ); `CONTRIBUTING.md`; `REUSE.toml` (`.claude/`, third-party entries); NOTICE file; `applicability.md` question 4 (done in RV-005 actions).

## Amendments after RV-008 (made before the pull request was merged; the owner confirms)
The goldfish review RV-008 found points in this text and in `LICENSE.md` that promised more than the licences grant. They are corrected; option F stays.
- **Selling devices.** `LICENSE.md` no longer says that selling a device built from the files "needs a licence". It says that copying, adapting or sharing the **files** for commercial purposes needs a licence, and that CC BY-NC-SA does not stop someone who re-implements a design independently or who builds from their own drawings. LAWYER.
- **The "allowed without asking" list** is stated as the owner's non-binding reading; the licence texts rule. It is not an extra grant. Open: whether a school that charges tuition, a charity that sells units for fundraising, or a hobbyist who uses a commercial PCB house is non-commercial.
- **Purchased-unit grant.** It names the grantor (the owner) and its scope (units sold by the owner or an authorised seller), is stated as not revocable for units already sold, and moves into the sale terms and the manual when they exist. It does not allow copying a board; unsigned images are allowed only where secure boot allows them (ADR-0007, Proposed), and modified firmware ends any conformity claim of the owner. LAWYER.
- **Patents.** The repository has been public since 2026-11-04. In the EU, public disclosure generally ends the novelty of what was disclosed, so the choice "file before publishing" has probably passed for the published designs. LAWYER (a patent attorney).
- **Title to the copyright.** The employment-contract check (item 11) is a **gate before the first sale or the first outside contribution**, with the owner as holder; the licences are already published, so a claim by an employer would affect every grant.
- **Trademark.** "busy-light" is a descriptive name and not registered; the text says the licences grant no right to the name and logo, not that the owner "reserves" a protected mark. Whoever builds and sells a unit becomes its manufacturer with their own conformity duties (RED, CRA); `LICENSE.md` says so.
- **Commercial route.** No commercial licence, template or price exists yet; `LICENSE.md` says so and gives the owner's GitHub account as the contact route (link RISK-038).
- **Status clarifications.** Item 4 (`.claude/` under Apache-2.0) is decided and applied. `CONTRIBUTING.md` is a placeholder until the lawyer aligns it with item 7; issue and comment text are contributions under the same terms. The pull request template now states that outside pull requests are not accepted yet.
- **Open, not closed by this ADR:** `sw/**` and `scripts/**` are matched by path, not by extension, so a document or a third-party file placed there would be labelled Apache-2.0 (`scripts/diagrams/package-lock.json` is third-party dependency data labelled Apache-2.0 today); KiCad libraries under CC BY-SA 4.0 and a BY-NC-SA design need the compatibility table before any import.

## Verification and revisit
- `reuse lint` in CI (exists); a CI check for code files under the CC default (to write); the compatibility table (to write); a lawyer reads `LICENSE.md`, the FAQ and `CONTRIBUTING.md` before the first outside contribution or commercial sale.
- Revisit when: the first outside contribution arrives; a foundation or distribution offers a home; volume production starts; the owner decides the real concern is a closed clone (then option B copyleft).

## Critical review notes
Strongest objection: "With free Apache code and CC files that only forbid commercial building, a competitor needs little more than a PCB shop: the licence protects little, and CC does not even reach the function of a board or the patents."
Answer: accepted as a limit. What the scheme protects is the design documents and files as copyright works, not the idea. The owner's real moats are the commercial licence, the trademark (item 9), security updates and support, and speed. If the owner wants stronger protection, option D with a CLA and a stricter code licence is the alternative; if the owner's real concern is a closed clone, option B is.
Second objection: "Non-commercial is the licence's weakest word; companies and schools will not know what they may do." Answer: item 6 publishes the owner's reading as an FAQ, and a lawyer checks it; the FAQ is guidance, and the licence text rules.
Third objection: "A superseding ADR written by the same author who wrote ADR-0013 will rationalise it." Answer: the table is marked as scored after the choice, the gate is stated as it really worked, and the review RV-005 was by independent goldfish; the owner may ask for a blind rescoring by a fresh reviewer.
