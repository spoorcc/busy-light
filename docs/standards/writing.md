# Writing Standard (user and technical documentation)

- **Status:** Draft

Documentation is part of the product. Users and service staff must be able to act correctly on first read,
including non-native English readers and people under time pressure. This also supports the legal duty to give clear
instructions and safety information (CRA Annex II, LVD/GPSR, RED) *(verify)*.

## 1. Basis: ASD-STE100 Simplified Technical English
Apply the principles of **ASD-STE100** (free specification and dictionary from asd-ste100.org; not stored in this repo
and not formally certified). Where we cannot follow it fully, follow the rules below. Project terms go in `docs/user/glossary.md`.

Core rules (summary of the ASD-STE100 writing rules; consult the specification for the authoritative text):
- **One word, one meaning, one part of speech.** Use the approved word; do not use synonyms for variety. Pick one name per
  part/button/state and use it everywhere ("indicator", not "light/lamp/LED" interchangeably).
- **Procedures:** write steps in the **imperative**, **one instruction per sentence**, **max 20 words** per step.
- **Descriptions:** max **25 words** per sentence; **max 6 sentences** per paragraph. One topic per paragraph.
- Use **active voice** and **simple present tense** ("The indicator shows red."). Use "shall" only in requirements, not manuals.
- Use **articles** ("the", "a"); do not drop them. Avoid contractions, idioms, phrasal verbs, humour, and abbreviations without definition.
- Use **numerals** for numbers, SI units with a space ("5 V", "20 mA"). Put units and tolerances in every value.
- Write **vertical lists** for 3+ items; use **tables** for specifications; use **figures** for spatial information and label them.
- Make nouns specific: do not stack more than three nouns in a noun cluster; use "the cable that connects the sensor".

## 2. Safety messages (placed BEFORE the step they apply to)
| Signal word | Meaning |
|-------------|---------|
| **WARNING** | Possible injury or death if ignored |
| **CAUTION** | Possible damage to the product or other equipment if ignored |
| **NOTE** | Helpful information; no hazard |

Format: signal word, the hazard, how to avoid it. Use ISO 7010 / ANSI Z535 style symbols where a symbol helps. Never bury a safety message in a paragraph.

## 3. Document design (readable, modern, consistent)
- Task-based structure: **Quick Start (one page, mostly pictures) -> User Guide -> Troubleshooting -> Maintenance -> Safety/Compliance -> Specifications.**
- Heading says the goal ("Connect the power supply"), not the component ("Power supply").
- Each procedure: purpose in one line, **prerequisites** (tools, parts, time), **numbered steps**, **expected result** after key steps, **what to do if it fails**.
- Show the **expected indicator behaviour** in a state table (state, colour, pattern, meaning, user action). Do not rely on colour alone (accessibility; add pattern/position cue).
- **Diagrams and graphics come from code** (`diagrams.md`); no hand-drawn images.
- Consistent templates (`docs/templates/procedure.md`), consistent figure style, alt text on every image, no text in images only.
- Plain, friendly but exact tone. Same terms as on the product, the packaging and in the firmware strings/logs.
- Accessibility: logical heading order, descriptive link text, sufficient contrast, readable on mobile, printable, translatable (short sentences, no text in images).
- Localisation: source language English (STE); translations track the source document version; the legally required languages for the target markets are provided with the product *(verify)*.

## 4. Quality control (verification of documentation)
- Automated style check: `python3 -I scripts/check_docs_style.py` (step/sentence/paragraph length, contractions, safety-message order cues). It does not replace an STE review.
- **Usability validation:** every procedure is executed **verbatim by someone who did not write it**, on the real product. Findings are recorded as `TC-nnn` (type: Demonstration) with pass/fail. Fix the document or the product.
- Docs are versioned with the product (firmware/hardware/mechanical revision stated on the first page). The release lists the document versions in the technical file.
- Technical review for correctness; editorial review for STE compliance and readability.
