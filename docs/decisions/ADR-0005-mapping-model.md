# ADR-0005: Mapping model from source data to ring state and level

- **Status:** Proposed (only the owner sets Accepted)
- **Date:** 2026-11-03
- **Deciders / reviewers:** Ben Spoor (owner); Reviewed in RV-001 (as referenced by plan 02); no separate ADR review
- **Related:** NEED-004, NEED-006, NEED-007, SYS-004, SYS-005, SYS-006, SYS-007, SYS-008, SYS-009, SYS-025, SYS-026, SYS-032; design doc `docs/plans/02-system-design.md` (section 4.9)

## Context and problem
A source (Jenkins push, REST poll, later others) delivers data. The ring shows either a **state** (running, success, unstable, failed, aborted, unknown) or a **level** (0-100 %, SYS-032).
Something must turn raw data into state or level. This choice decides how easy new sources are (NEED-007), how large the code is, how much input can attack the device (SYS-005), and how much can be tested on the PC (SYS-025).

What the requirements need today: take one field out of a JSON text (SYS-006), map the value through an editable table to a state (SYS-008), or scale a number between a user minimum and maximum to a level (SYS-032).
Not needed today: combining several fields, arithmetic, text matching with patterns.

Not known: how large Jenkins answers are without a filter (a Jenkins URL can use `?tree=building,result` to return only two fields; the preset should use it, to confirm in spike 7.1); how much RAM the Zephyr JSON library needs in the pinned revision.

## Decision criteria
| Criterion | Weight (1-5) | Source requirement |
|-----------|--------------|--------------------|
| Covers the first-release needs (state table, level scaling) | 5 | SYS-006, 007, 008, 032 |
| Small input cannot crash or hang the device (bounded memory and time) | 5 | SYS-005 |
| New source without firmware change where practical | 3 | NEED-007 |
| Small flash and RAM | 4 | SYS-026 |
| Fully testable on the PC, fuzzable | 4 | SYS-025 |
| User can configure without programming | 4 | NEED-016 |
| Room to grow later | 3 | NEED-007 |

## Alternatives considered

### A. Path plus table plus linear scale (M1)
Config per source: a path to one value in the JSON (JSON Pointer style, for example `/result`), then either a table of value-to-state rows or numeric min and max for a level. A small streaming extractor reads the text once with fixed depth and size limits, no allocation.
Strongest case: it is exactly what the requirements ask for and nothing more; small, deterministic, easy to fuzz. Cons: cannot combine fields (for example "building and result") in one rule; the Jenkins preset therefore needs two paths or a small special rule for `building` before `result`. Cannot compute levels from two numbers (done / total).

### B. Small expression language (M2)
Comparisons, arithmetic, boolean operators on extracted fields. Handles "done / total" and combined conditions. Cons: a new language to specify, test and fuzz; evaluation limits needed; more code; not required in release 1.

### C. One hard-coded parser per source (M3)
Smallest per source. Cons: every new source means new firmware; breaks NEED-007.

### D. Embedded scripting (Lua or WebAssembly) (M4)
Most flexible. Cons: large flash and RAM, a runtime to keep secure (CRA vulnerability handling), attack surface through uploaded scripts. Rejected on resource and security grounds, not on features.

### E. Fixed neutral message only; adaptation happens outside the device (M5)
The device accepts only a small fixed JSON such as `{"state":"failed"}` or `{"level":42}`, for push and for poll. A script or proxy converts other data.
Strongest case: the least code on the device and the smallest attack surface; the project does not own source quirks.
Cons: cannot poll Jenkins directly (SYS-006, SYS-007 need the device to fetch and extract); users must run a proxy. This fails the first-release scope.

### F. Do nothing / defer
Hard-code Jenkins now, decide later. This is C in practice.

## Comparison
Scores 0 to 5, my judgement.

| Criterion (weight) | A | B | C | D | E |
|--------------------|---|---|---|---|---|
| First-release needs (5) | 4 | 5 | 3 | 5 | 1 |
| Bounded input handling (5) | 5 | 3 | 4 | 1 | 5 |
| New source without firmware change (3) | 3 | 4 | 0 | 5 | 4 |
| Flash and RAM (4) | 4 | 3 | 5 | 0 | 5 |
| PC test and fuzz (4) | 5 | 3 | 4 | 1 | 5 |
| No programming for the user (4) | 4 | 2 | 4 | 0 | 2 |
| Room to grow (3) | 3 | 5 | 0 | 5 | 2 |
| **Weighted sum (max 140)** | 115 | 99 | 87 | 64 | 96 |

## Decision
Choose **A** for release 1, behind an interface that lets B replace it later.
1. Interface (in `core/`, no OS calls): a mapper takes the source id and the received text and returns `{kind: state | level | none, state, level_permille}`. The extractor and mapper are pure functions on buffers, run on the PC.
2. Path syntax: a restricted JSON Pointer (object keys and array indexes, maximum depth [8], maximum path length [64] characters). No wildcards or filters.
3. Limits: input text at most [8] KiB per message or poll answer (a larger answer is cut off and reported as an error); a number must fit a 32-bit integer or be a decimal with at most [6] fractional digits (exponent form is not accepted as a target; PC prototype F2, F3); the document nesting is limited to [32] levels, also in skipped parts (F1); at most [16] table rows per source; extraction time bounded by the input size (single pass).
4. Table rows compare a text, a number, a boolean or null exactly (no patterns). Jenkins gives `building` as a boolean and `result` as null while a build runs (RV-001, finding 29). An unmapped value gives the state unknown (SYS-008).
5. Level: `(value - min) / (max - min)`, clamped to 0..100 %, with min and max set by the user per source (SYS-032). Min equal to max is rejected at configuration; max below min (inverted range) is accepted and inverts the level. A non-numeric value or NaN gives the state unknown, not a level.
6. The Jenkins preset (SYS-007) uses the URL filter `?tree=building,result` and a built-in two-step rule (if `building` is true, state running; otherwise map `result`). This special rule is a named preset, not a general feature.
7. Push events carry a neutral body of the same shape as the mapper result, so push needs no mapping (the Jenkins side sends `state` or `level`); a push to a configured path-mapping source is a later increment.
8. A later expression language (B) can plug in as a second mapper kind with the same return type. Sources do not change.

Open point for the owner: should push accept an arbitrary Jenkins notification body (needs the mapping on push) or only the neutral body of item 7? I recommend the neutral body: the sender is under the user's control.

## Consequences
- Positive: small and deterministic; fuzz-friendly; one place for limits; no new language to secure.
- **Negative / trade-offs accepted:** no field combination or arithmetic; the Jenkins preset has a special rule; a "done of total" progress level cannot be shown without a sender-side calculation; users who want more must wait for B.
- New risks (to add to risk register): path syntax misunderstood by users; oversize or deep JSON causing silent truncation; number parsing error at edges (overflow, locale); preset filter not supported by an older Jenkins.
- Requirements created or changed: SYS-008 is extended in a later pass by the level scaling and the path syntax limits (SYS-006 mentions "configured path"); new SW requirements for the limits above and for the interface of item 1. SYS-040 and SW-001 exist.

## Verification and revisit
- Unit tests on the PC for the extractor and mapper: normal cases, missing key, wrong type, depth and size limits, 10 000 random and mutated inputs without crash or hang (SYS-005, SYS-025). Coverage figure recorded when code exists.
- TC-006, TC-007, TC-008, TC-032 as written.
- Spike 7.1: measure RAM and time of the extractor on the target for the maximum input.
- Revisit when: a second real source needs field combination; users ask for "done / total" levels; a source answer exceeds the size limit with no filter available.

## Critical review notes
Strongest objection: "Without arithmetic or combined conditions the device will be outgrown at the first non-Jenkins source, and the limits make M1 a dead end."
Answer: the interface in item 1 keeps the sources independent of the mapper kind, so B can be added without touching them. The first release does not carry B's cost for a need nobody has yet.
Second objection: "A restricted JSON Pointer is not what most users know (JSONPath, dot paths)." Answer: valid. The web interface should offer a test field that shows the extracted value for a pasted sample, so a wrong path is found at once; the dot-path form is a display option only if the owner wants it.
