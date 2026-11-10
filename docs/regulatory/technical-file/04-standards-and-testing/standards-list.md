# Standards list (candidate set)

- **Status:** Draft (assistant, 2026-11-10; not reviewed by the owner or a test lab)
- **Product:** busy-light, Wi-Fi status light, USB-C 5 V powered, no battery, EU market only (`../../applicability.md`)
- **Legal route assumed:** RED 2014/53/EU (covers safety and EMC of radio equipment, so LVD and EMCD do not apply in parallel), CRA (EU) 2024/2847 from 11 December 2027, RoHS, REACH, WEEE, GPSR.

**Read this first.** This is engineering guidance, not legal advice. Editions and harmonised status change. The list was made from secondary sources: the Official Journal (eur-lex.europa.eu) and the Commission's lists (webgate.ec.europa.eu) could not be opened from the session that wrote it, because the network policy does not allow those hosts. Every edition and every "harmonised" mark is *(verify)* until someone checks it against the current Implementing Decision under the RED, Decision (EU) 2022/2191 as amended (one source names Decision (EU) 2026/2003 of 4 September 2026 as the last amendment *(verify)*). Record the check (date, source, person) in the "Checked" column.

"Presumption" means: the standard is cited in the Official Journal under that act, so applying it in full gives a presumption of conformity with the matching essential requirements. Without it, the standard is still usable as state of the art, but the technical file must argue conformity itself, or a notified body is needed for RED Art. 3(2)/3(3).

## 1. RED Article 3(1)(a): health and safety

| Standard | Edition seen in sources | Presumption under RED | Applies to | Planned evidence | Checked |
|----------|------------------------|-----------------------|------------|------------------|---------|
| EN IEC 62368-1 (audio/video, IT equipment, safety) | 2020+A11:2020; EN IEC 62368-1:2024+A11:2024 published, sources say it is unlikely to be cited soon | cited under LVD; RED citation *(verify)* | whole product (USB-C SELV input, PS1/PS2 classification, fire enclosure, temperatures) | HW-010, HW-013, MECH-005 analyses; lab test or self-assessment report | -- |
| EN 62479 (low-power equipment, EMF) or EN 62311 / EN IEC 62311 (EMF assessment) | EN 62479:2010; EN IEC 62311:2020 | EN 62479 and EN 62311 cited under RED in older lists *(verify)* | Wi-Fi transmitter at up to about 20 dBm (module datasheet, not read in this work) | EMF assessment from the module conducted power and the antenna gain; EN 62479 applies only below its power threshold *(verify)* | -- |
| EN 62471 / IEC 62471 (photobiological safety of lamps) and IEC TR 62778 (blue light) | EN 62471:2008 | not cited under RED; used as state of the art for the LED ring | LED ring | risk-group assessment after spike 7.5 (applicability item 7) | -- |

## 2. RED Article 3(1)(b): EMC

| Standard | Edition seen in sources | Presumption under RED | Applies to | Planned evidence | Checked |
|----------|------------------------|-----------------------|------------|------------------|---------|
| ETSI EN 301 489-1 (common EMC for radio equipment) | V2.2.3 | yes *(verify)* | whole product | accredited EMC report (SYS-049, TC-049) | -- |
| ETSI EN 301 489-17 (broadband data, 2.4 GHz Wi-Fi) | V3.2.4; sources also show V3.3.1 | yes, edition *(verify)* | Wi-Fi function | same | -- |
| EN 55032 (emission, multimedia equipment) class B | 2015+A11:2020 | cited under EMCD; used with EN 301 489-1 for the non-radio part *(verify)* | LED driver, USB, MCU | same; pre-scan with [6] dB margin | -- |
| EN 55035 (immunity, multimedia equipment) | 2017+A11:2020 | cited under EMCD *(verify)* | same | same | -- |
| EN 61000-4-2 (ESD test method), -4-3 (radiated immunity), -4-4 (EFT), -4-5 (surge), -4-6 (conducted) | current editions | basic standards, referenced by the above | test methods only; -4-4/-4-5/-4-6 on a DC port with a cable shorter than 3 m are normally not required *(verify against EN 301 489-1 tables)* | test plan | -- |

Alternative set considered and rejected for now: EN IEC 55015 + EN 61547 (lighting equipment). The product is a status indicator with a network function, not a luminaire whose main purpose is illumination. Record the reasoning in the test plan and ask the lab *(verify)*.

## 3. RED Article 3(2): efficient use of the radio spectrum

| Standard | Edition seen in sources | Presumption under RED | Applies to | Planned evidence | Checked |
|----------|------------------------|-----------------------|------------|------------------|---------|
| ETSI EN 300 328 (2.4 GHz wideband transmission) | V2.2.2 | yes *(verify)* | Wi-Fi radio | module test report (Espressif, for the module) plus a product assessment: antenna placement inside the ring (ADR-0003) and a changed ground plane can change the radiated results, so the lab decides which tests to repeat | -- |

## 4. RED Article 3(3)(d), (e), (f): cybersecurity (units placed on the market before 11 December 2027)

| Standard | Edition | Presumption | Applies to | Planned evidence | Checked |
|----------|---------|-------------|------------|------------------|---------|
| EN 18031-1 (internet-connected radio equipment) | 2024 | yes, with a restriction: no presumption where the user may choose not to set a password (clauses 6.2.5.1, 6.2.5.2), Implementing Decision (EU) 2025/138 *(verify)* | network protection, access control, update, secure storage | gap analysis against the clauses (applicability consequence 3); the per-unit passphrase design (ADR-0006) avoids the restricted case | -- |
| EN 18031-2 (radio equipment processing personal data) | 2024 | as above | only if personal data is processed: by design no (applicability item 10) | statement in the technical file | -- |
| EN 18031-3 (radio equipment handling virtual money) | 2024 | as above | not applicable | statement | -- |

Delegated Regulation (EU) 2022/30 is repealed with effect from 11 December 2027 by Delegated Regulation (EU) 2026/339; after that date the CRA covers cybersecurity *(verify)*.

## 5. CRA (EU) 2024/2847 (from 11 December 2027; reporting duty from 11 September 2026)

| Standard / guidance | Status | Use | Checked |
|---------------------|--------|-----|---------|
| CRA horizontal and vertical harmonised standards (CEN/CENELEC JTC 13, ETSI) | none cited in the Official Journal in the sources read; drafts in progress *(verify)* | follow the drafts; until cited, conformity is argued against Annex I directly (`../05-cybersecurity/cra-annex-i-mapping.md`) | -- |
| ETSI EN 303 645 (consumer IoT baseline) | V3.1.3 *(verify)* | state of the art for consumer IoT; maps well to Annex I | -- |
| IEC 62443-4-1 (secure product development lifecycle) | 2018 | process reference for Annex I Part II | -- |
| SPDX 2.3 / ISO/IEC 5962:2021 | -- | SBOM format (`west spdx`, SYS-044) | -- |

Product class: default (not listed in Annex III or IV). Reasoning: the core function is a status display; it is not a smart-home product with security functions, a virtual assistant, a router, or another listed category (Implementing Regulation (EU) 2025/2392 describes the categories *(verify)*). Conformity route: internal control (Module A) *(verify)*.

## 6. Substances, waste, marking, product safety

| Standard / act | Use | Checked |
|----------------|-----|---------|
| EN IEC 63000:2018 (technical documentation for RoHS) | supplier declarations per part (HW-019, `../07-supplier-declarations/rohs-reach-weee.md`) | -- |
| EN 50419 (WEEE marking) | crossed-out bin symbol and the date mark (SYS-048) | -- |
| GPSR (EU) 2023/988 | product safety duties for consumer products not covered by specific rules (traceability, warnings, accident reporting) *(verify how it combines with RED)* | -- |
| Ecodesign (EU) 2023/826 (standby and networked standby, applies from 9 May 2025) | scope test needed: household and office equipment listed in its Annex I; networked standby limits if in scope *(verify)* | -- |
| Common charger, RED Art. 3(4) as amended by Directive (EU) 2022/2380 | applies to listed categories of rechargeable portable devices; this product has no battery, so it is not in scope *(verify)*; it uses USB-C anyway | -- |

## 7. Not applicable (with reason)

| Act or standard | Reason |
|-----------------|--------|
| LVD 2014/35/EU, EMCD 2014/30/EU | the RED covers safety and EMC of radio equipment (RED Art. 3(1)) |
| Batteries Regulation (EU) 2023/1542 | no battery (NEED-015 is a later release; re-assess then) |
| EN 60598-1 (luminaires) | not a luminaire; re-assess if the use changes to lighting |
| UKCA, FCC, ISED | EU market only (owner, 2026-11-03) |
