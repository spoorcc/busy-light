# ADR-0017: Datasheet evidence format (per-part YAML, JSON Schema, checked by a script)

- **Status:** Proposed (only the owner sets Accepted)
- **Date:** 2026-11-05
- **Deciders / reviewers:** Ben Spoor (owner). No goldfish review has been run on this ADR.
- **Related:** HW-012, HW-009, ADR-0012; `hw/evidence/README.md`. The rule that vendor documents are linked, not committed is item 8 of the licensing-corrections ADR on branch `docs/review-actions` (not yet on `main`).
- **Numbering note:** ADR-0015 and ADR-0016 exist on branches that are not merged to `main` yet. This ADR takes 0017 so the numbers do not clash. HW-012 and TC-212 are the next free IDs on `main`; check for a clash before merging.

## Context and problem
Hardware analyses (current-limit steps, readback margin, hold-off capacitor) use numbers from vendor datasheets.
Earlier reports (`docs/verification/reports/datasheet-evidence-*.md`) copied the numbers into Markdown tables and into
constants in analysis scripts. A reader cannot tell which values a second person checked, a script cannot ask "is this value verified",
and nothing checks that a stated page and quote exist in the document.
Constraints:
- Vendor PDFs stay outside the public repository (ADR-0015 item 8). A claim file may hold a hash, a page and a short quote only
  (one sentence or one table row).
- The owner asked for an extensible, well-known format: YAML validated by JSON Schema (draft 2020-12), a `source` object modelled on
  W3C Web Annotation selectors, provenance modelled on W3C PROV, and unit strings that `pint` or UCUM can parse.
- Every number needs a status. Values that an AI agent extracted must start `unverified`; only a human or another agent may verify them.
- The checks must run in the existing CI (`pytest`, Python tooling in `pyproject.toml`) and locally with the PDFs present.
- Unknown today: how many parts and claims the project needs in the end; whether a supplier tool will want the data later.

## Decision criteria
| Criterion | Weight (1-5) | Source requirement |
|-----------|--------------|--------------------|
| Each value traceable to document, page and quote; verification status machine-readable | 5 | process rules 6, 11; HW-012 |
| Works without publishing vendor documents | 5 | ADR-0015 item 8 |
| Checkable in CI with existing tooling; scripts can read it | 4 | process rule 6; `pyproject.toml` |
| Reviewable as a text diff by the owner | 4 | process rule 3 |
| Extensible and well known (owner request) | 4 | owner instruction 2026-11-05 |
| Low set-up and maintenance effort for a one-person project | 3 | project size |
| No dependence on a third party's service, licence or data | 3 | CRA support period, process rule 7 |

## Alternatives considered

### A. Per-part YAML files with a JSON Schema, a `source` object and PROV-style provenance (recommended)
One file per part under `hw/evidence/parts/`. A JSON Schema (draft 2020-12) defines the structure.
A script validates it, checks units with `pint`, checks hashes and quotes against the PDFs when they exist, and compares pin tables with the netlist.
Pros: text diffs; reuses Python tooling already in CI; extends by adding optional fields; the format maps to Web Annotation and PROV without their complexity; works offline.
Cons: the project owns the schema and the checker; the "modelled on" mapping is informal, not an interchange format; a quote on the right page can still sit in the wrong column.

### B. IEC 61360 / ECLASS property model
Describe each parameter as a property of a standard data dictionary (IEC Common Data Dictionary, ECLASS) with a class, a property ID and a unit.
Pros: international standards; supplier and PLM tools understand the property IDs; units are standardised.
Cons: it models *what a parameter is*, not *where this number was read and who checked it*; our parameters (for example "ILIM source current absolute maximum") often have no class property; access to the dictionaries may need a licence or a fee (not checked here); heavy for about twenty parts.
It could be mapped later: the `parameter` field is free text now and could carry a dictionary ID.

### C. Distributor or aggregator parametric data (API or CSV)
Pull parameters from a distributor's catalogue API.
Pros: no manual extraction; many parts at once.
Cons: the data is a secondary copy of the datasheet and has no page or quote, so it cannot show where a value came from; it can change without notice; the terms of use and the accuracy are the supplier's; it needs accounts and a network in the build. It cannot meet the traceability criterion.
It may still be used later to *find* a value that a human then reads in the datasheet.

### D. Full JSON-LD with PROV-O and the Web Annotation vocabulary
Write each claim as an RDF graph in JSON-LD with `oa:` and `prov:` terms and validate it with SHACL or the contexts.
Pros: the strictest interpretation of the standards; machine-mergeable with other graphs; the best long-term interchange.
Cons: needs an `@context`, RDF tooling and SHACL knowledge that the project does not use today; verbose diffs; the owner and the assistant must learn it; the benefit appears only if another tool consumes the graph. Nothing does.
The YAML can be converted to JSON-LD later because the field mapping is documented.

### E. SQLite (or another database) file
Claims in tables; scripts query with SQL.
Pros: strong queries and constraints; one file.
Cons: a binary file in git (no useful diff, merge conflicts); the owner cannot review changes without a tool; the schema checks live in SQL. It fails the reviewability criterion.

### F. Do nothing: keep Markdown reports and constants in scripts
Pros: no new tool.
Cons: the problems in the context stay: no machine-readable status, no page/quote check, hand copying errors. Not acceptable for values in a safety function (HW-010).

## Comparison
Scores 1 (poor) to 5 (good). Weighted sum in brackets (maximum 140).

| Criterion (weight) | A YAML + schema | B IEC 61360 / ECLASS | C Distributor data | D JSON-LD full | E SQLite | F Do nothing |
|--------------------|-----------------|----------------------|--------------------|----------------|----------|--------------|
| Traceable value, status (5) | 5 | 2 | 1 | 5 | 4 | 2 |
| Works without publishing PDFs (5) | 5 | 5 | 5 | 5 | 5 | 5 |
| Checkable in CI, scripts can read (4) | 5 | 3 | 2 | 3 | 4 | 1 |
| Reviewable text diff (4) | 5 | 3 | 2 | 3 | 1 | 4 |
| Extensible, well known (4) | 4 | 5 | 2 | 5 | 3 | 1 |
| Low effort (3) | 4 | 2 | 3 | 1 | 3 | 5 |
| No third-party dependence (3) | 5 | 2 | 1 | 4 | 5 | 5 |
| **Weighted sum** | **[133]** | **[91]** | **[66]** | **[109]** | **[101]** | **[89]** |

The scores are the author's judgement and are not measured. The ranking is stable for A first and D second; the gap between D and E (8 points) is small.

## Decision
Recommendation: choose **A**. It is the only option that gives traceable values, a verification status and a CI check with the tools the project already uses,
and it keeps the owner's standards (JSON Schema 2020-12, Web Annotation selectors, PROV, `pint`) as the model for the fields.
Units: **pint** strings, not UCUM, because the consumers are Python scripts and pint parses the strings without a table. A UCUM export is mechanical if needed.
The verified rule: an extracted value starts `unverified`; only a human or an agent with a different name than the extractor may set `verified`; the checker enforces it.

## Consequences
- Positive: each analysis value can point to document, page and quote; `load_claim()` refuses unverified values; pin tables can be compared with the netlist.
- **Negative / trade-offs accepted:** the project maintains a schema and a checker; extraction takes effort (about 350 entries for 19 files in the first fill);
  the quote check proves presence on a page, not correctness of the column or variant; a revision of a datasheet changes the hash and needs a new check;
  the PDFs are outside git, so CI cannot run the quote and hash checks (CI runs the schema and format checks through `pytest`).
- New risks: a false sense of safety from `unverified` numbers that look official (mitigated: scripts refuse them); a wrong value marked `verified` by a careless check
  (mitigated by the independent-verifier rule, not eliminated). Add to the risk register when the owner accepts the ADR.
- Requirements created or changed: HW-012 (Draft).

## Verification and revisit
- `scripts/test_check_part_evidence.py` tests the checker (schema, duplicate ids, units, order, verified rule, quote shape, netlist, consumer function).
- Revisit when: a second tool needs the data (then map to JSON-LD or the ECLASS property IDs); the number of parts exceeds what a person can review; a supplier asks for IEC 61360 data.
- Not run: no goldfish review; the comparison scores are not independently checked; the access terms of IEC CDD and ECLASS were not checked.

## Critical review notes
Strongest objection: "a quote on the right page proves nothing, so the checker gives false comfort". Answer: correct. The checker proves hash, page and quote presence
and that each stored number occurs in the quote. The `verified` status needs a human or another agent to read the page again. The README states this limit.
Second objection: "inventing a schema is not 'well known'". Answer: the structure is plain YAML and JSON Schema; the `source` and provenance fields follow named W3C models.
Full RDF (option D) is kept as a later conversion, not rejected as an end state.
