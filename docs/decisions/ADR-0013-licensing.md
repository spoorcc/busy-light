# ADR-0013: Licensing of software, hardware, mechanics and documentation

- **Status:** Proposed (only the owner sets Accepted)
- **Date:** 2026-11-04
- **Deciders / reviewers:** Ben Spoor (owner); no goldfish review yet; not legal advice, a lawyer should check the final texts before the first commercial sale
- **Related:** NEED-012, SYS-044, ADR-0002, ADR-0012; `docs/regulatory/applicability.md`

## Context and problem
The repository became public on 2026-11-04 with **no licence file**. Without a licence all rights are reserved: people can read the files but not copy, change or build from them.
Owner wish (2026-11-04): use open licences such as Creative Commons, so that "people can copy but not profit". NEED-012 says "published as open source". Earlier owner statements: start as open source, keep the option to develop it into a professional product that can be sold, volume about 1000 units per year later.

Two parts of the wish pull apart: a licence that forbids commercial use is **not open source** by the Open Source Definition (OSI) and not "open source hardware" by the OSHWA definition; both require commercial use to be allowed. The honest label for such a licence is "source-available".
Facts about the licences (to be checked against the texts): Creative Commons recommends **against** its licences for software, and says its licences do not cover patent rights (relevant for hardware); CERN-OHL has no non-commercial variant; PolyForm Noncommercial 1.0.0 is written for source code and allows personal, research, hobby, educational and charitable use.
Not known: how the CRA open-source steward role applies to a source-available project (verify, `applicability.md` open question 4); whether non-commercial licences deter the contributors the project wants.

## Decision criteria
| Criterion | Weight (1-5) | Source |
|-----------|--------------|--------|
| Others cannot profit from copies (owner wish) | 5 | owner 2026-11-04 |
| Counts as open source (OSI and OSHWA) | 3 | NEED-012 |
| Attracts contributors and reviewers | 3 | process README (review culture) |
| Compatible with upstreaming drivers to Zephyr (Apache-2.0) | 4 | owner: upstream missing drivers |
| Simple CRA position | 3 | `applicability.md` |
| Licence text is mature and unambiguous | 4 | legal risk |
| Companies can use or build units for internal use | 3 | target users (build rooms) |
| Reversible once published | 3 | grants cannot be withdrawn for copies already made |
| Keeps the option of a commercial licence by the owner | 4 | owner: professional product |

Owner wish as a **gate**: an option that allows others to sell copies without a licence from the owner does not meet the wish. Options A and B fail the gate; they are scored for reference.

## Alternatives considered

### A. Permissive open licences
Apache-2.0 (software, same as Zephyr), CERN-OHL-P (hardware), CC BY 4.0 (documents and mechanics).
Strongest case: the largest community, no friction with Zephyr or companies, simplest CRA position.
Cons: anyone may sell copies and keep their changes private. Fails the owner wish.

### B. Copyleft open licences
AGPL-3.0 or GPL-3.0 (software), CERN-OHL-S (hardware), CC BY-SA 4.0 (documents and mechanics).
Strongest case: others may copy and even sell, but every derivative must stay open, so a closed clone cannot undercut the project. This answers most real fears of "profiting" and stays open source. Cons: commercial copies are allowed, so it fails the stated wish; GPL-family code cannot be upstreamed into Zephyr.

### C. Non-commercial, source-available
PolyForm Noncommercial 1.0.0 (software), CC BY-NC-SA 4.0 (hardware files, mechanics, documents, images).
Strongest case: exactly the owner wish: copy, study, change and build for non-commercial purposes; ShareAlike keeps derivatives under the same terms.
Cons: not open source; "non-commercial" is vague at the edges (a company building units for its own build room is likely commercial use); CC advises against its licences for software and hardware; some contributors and distributions will avoid the project; contributions made under the same licence cannot be sold commercially by the owner later without the contributors' consent.

### D. Option C plus a commercial licence by the owner
As C, and the owner offers a separate paid licence to manufacturers. Needs a contributor licence agreement (CLA) or copyright assignment, so that contributions can be relicensed.
Strongest case: keeps the "professional product" route and the volume plan open while still meeting the wish.
Cons: the CLA adds friction for contributors; the owner takes on licence management; same non-open-source label as C.

### E. Do nothing / defer
Keep all rights reserved (today's state). Reversible, but nobody may reuse anything, which contradicts NEED-012, and contributors cannot send patches safely.

## Comparison
Scores 0 to 5, my judgement. Weighted sums over the nine criteria, max 160.

| Criterion (weight) | A | B | C | D | E |
|--------------------|---|---|---|---|---|
| Others cannot profit (5) | 0 | 2 | 5 | 5 | 3 |
| Counts as open source (3) | 5 | 5 | 0 | 0 | 0 |
| Attracts contributors (3) | 5 | 4 | 2 | 2 | 0 |
| Zephyr upstream compatible (4) | 5 | 3 | 2 | 2 | 0 |
| Simple CRA position (3) | 4 | 4 | 3 | 3 | 2 |
| Mature, unambiguous text (4) | 5 | 5 | 3 | 3 | 5 |
| Companies can use or build (3) | 5 | 4 | 1 | 2 | 0 |
| Reversible (3) | 1 | 1 | 1 | 1 | 5 |
| Commercial option for the owner (4) | 2 | 3 | 2 | 5 | 5 |
| **Weighted sum (max 160)** | 108 | 108 | 74 | 89 | 76 |

A and B score highest overall and fail the gate. Among the options that meet the owner wish, D leads C by 15 points and E by 13.

## Decision
Recommendation: choose **D**, in this form; the owner decides, and nothing is licensed until the owner accepts and adds the licence files.
1. **Software** (`sw/`, `scripts/`, tooling): PolyForm Noncommercial 1.0.0. Files that are meant for upstream Zephyr (drivers) are kept in separate files or modules under Apache-2.0, so that they can be contributed.
2. **Hardware files, mechanics, documentation, images:** CC BY-NC-SA 4.0. The repository says plainly that CC does not cover patents and that CC recommends other licences for hardware; this is accepted because no non-commercial hardware licence of comparable maturity exists.
3. **Wording:** the project calls itself "source-available" and not "open source", and does not use the OSHWA mark. NEED-012 ("published as open source") no longer holds as written. **Owner decision needed** to change NEED-012 to "published source-available for non-commercial use" or to accept option B instead.
4. **Commercial licence:** the owner may grant separate paid licences. Before the repository takes outside contributions, a CLA (or a DCO plus a relicensing grant) is put in `CONTRIBUTING.md`, because without it contributed code cannot be relicensed.
5. **Third-party parts keep their own licences:** Zephyr, MCUboot, Mbed TLS, the Wi-Fi binary blobs (RISK-020), KiCad libraries and others; the SBOM (SYS-044) lists them, and a licence-compatibility review is part of the technical file.
6. **Use of a purchased unit is not restricted:** the non-commercial terms cover copying, changing and building, not using a unit that someone bought from the owner. This is written in the README in plain words.
7. A `LICENSE` file for each part, an SPDX header policy and the README licence section are added only after acceptance.

## Consequences
- Positive: meets the stated wish; keeps the commercial route; the repository becomes legally reusable for non-commercial purposes.
- **Negative / trade-offs accepted:** not open source, so the project loses OSI and OSHWA recognition, and contributors who need an open-source licence will stay away; companies cannot build units for internal use without a licence from the owner; the non-commercial boundary can be disputed; a CLA adds friction.
- New risks (to add to the risk register): licence-incompatible dependency in the build; ambiguity of "non-commercial" leads to a dispute; contributors refuse the CLA; CRA role differs from the open-source steward assumption.
- Requirements created or changed: NEED-012 (see item 3); `docs/regulatory/applicability.md` question 4 (CRA role); `CONTRIBUTING.md`; README licence section.

## Verification and revisit
- A licence-compatibility table of all components in the SBOM, checked at each release (tool check to be written when the SBOM exists).
- A lawyer reads the final text before the first commercial sale or the first paid commercial licence.
- Revisit when: the first outside contribution arrives, the project is offered a place in an open-source foundation or distribution, volume production starts, or option B (copyleft) looks better to the owner after reading this ADR.

## Critical review notes
Strongest objection: "Non-commercial licences are the worst of both worlds: not open source, vague at the edges, and they shut out companies, which are the target users of a build light."
Answer: partly accepted. Companies can still buy finished units; only building units from the files for company use needs a licence. If that cost is too high, option B is the better fit, because it allows commercial use but forces derivatives to stay open.
Second objection: "CC licences are not meant for software or hardware." Answer: accepted for software (PolyForm is used instead); for hardware no non-commercial licence of comparable maturity exists, and the limit about patents is stated in the README.
Third objection: "The wish 'people can copy but not profit' may really be 'a competitor must not sell a closed clone'." Answer: that is what option B does, without the non-commercial label; the owner should decide which concern is the real one.
