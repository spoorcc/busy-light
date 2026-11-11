# Regulatory Applicability Assessment (RAA-001)

- **Document:** RAA-001, regulatory applicability assessment and conformity strategy for the busy-light
- **Status:** Draft -- not reviewed by the owner or by a compliance expert
- **Version:** 0.3   **Date:** 2026-11-10
- **Author:** the assistant   **Owner / approver:** Ben Spoor
- **Reviewers:** none yet (an independent regulatory review is recommended before the architecture gate and before a test laboratory is booked)
- **Re-run when:** radio, battery, mains, cloud or app, data collection, a new market, a new function, a new user group or a change of who sells the product is added.

**Limits of this document.** This is engineering guidance, not legal advice. The legal texts and the lists of harmonised standards change. The session that wrote version 0.3 could not open the Official Journal (eur-lex.europa.eu) or the Commission's standards lists; article numbers and dates come from the author's knowledge and from secondary sources, and each one marked *(verify)* must be checked against the official text. Nothing here states that the product conforms: the document states which rules apply, why, and which evidence is planned.

## 1. Purpose and scope

This assessment answers four questions for the busy-light (product description: `technical-file/01-general/product-description.md`):

1. Which European Union acts apply to the product, and which do not, with the reason for each.
2. Which role the project has under those acts, and from which moment the duties start.
3. Which conformity assessment procedure and which standards are planned.
4. Which decisions and checks are still open.

Scope: placing on the market in the European Union only (owner, 2026-11-03). The United Kingdom, the United States, Switzerland and other markets are out of scope until the owner adds them. The details per standard are in `technical-file/04-standards-and-testing/standards-list.md`, the clause-level mapping in `compliance-matrix.md`, the hazards in `technical-file/03-risk-and-safety/risk-assessment.md`.

## 2. Basis of the assessment

### 2.1 Product facts that drive the result

| Question | Answer | Why it matters |
|----------|--------|----------------|
| Intended use, user (consumer / professional / industrial), environment | Status light for build servers, used on a desk in an office or home; users are consumers or professionals (owner to confirm) | GPSR, EMC environment class, ecodesign |
| Power source: USB-C 5 V (SELV) / external PSU / mains inside / battery | USB-C 5 V, at most [500] mA (SYS-020). No mains inside, no battery. The user supplies the USB source | LVD scope (50-1000 V AC, 75-1500 V DC), PSU ecodesign, battery regulation |
| Wireless (Wi-Fi, BLE, 802.15.4, other radio)? | **Yes: Wi-Fi** (owner, 2026-11-03) | RED replaces LVD+EMCD; spectrum, cyber delegated act |
| Network connectivity / remote update / cloud or app | **Yes, including OTA firmware update (owner, 2026-11-03): LAN/Internet data sources, web UI on device** (owner, 2026-11-03). Update path and cloud use TBD | CRA, RED 3(3)(d-f), GDPR |
| Processes personal data? | Probably not by design (Jenkins job names are not personal data; the device name and Wi-Fi password are stored locally). Owner to confirm *(verify)* | GDPR, RED 3(3)(e) |
| Light output (LED power, visible to eyes) | **RGB LED ring** (owner, 2026-11-03). Power and optics TBD | EN 62471 photobiological safety |
| Target markets (EU only? UK, US, other) | **EU only for now** (owner, 2026-11-03) | UKCA, FCC/ISED etc. out of scope until stated |
| Sold commercially or purely community/open-source hardware? | **Owner 2026-11-03: internal tool now; start as open source; keep the option to develop it into a professional product that can be sold.** Earlier:  about 1000 units per year (owner, 2026-11-03).** The first 10 units are prototypes for the owner, not placed on the market | "Placing on the market" triggers manufacturer duties; CRA open-source steward rules |
| Expected product lifetime | **Support period 5 years, kept as short as the rules allow** (owner, 2026-11-03; CRA default is at least 5 years *(verify)*) | CRA support period (default >= 5 years unless shorter lifetime) |

### 2.2 Characteristics used in the scope tests

| Characteristic | Fact | Effect |
|----------------|------|--------|
| Intentional radio transmitter | yes, Wi-Fi 2.4 GHz (pre-certified module) | RED applies; LVD and EMCD do not apply in parallel |
| Supply voltage | 5 V DC, no mains part, no supply unit in the box | below the LVD range, but the RED applies the same safety objectives with no voltage limit |
| Digital elements with a data connection | yes: firmware, network, remote update | CRA applies |
| Battery | none | Batteries Regulation does not apply |
| Light source | [16] RGB indicator LEDs, not for illumination | EN 62471 assessment; scope test for the lighting ecodesign rules |
| Users | professional now, consumers possible later | GPSR and the consumer rules are assumed to apply |
| Personal data | none by design | GDPR not triggered by the device itself |

## 3. Role of the project and start of the duties

| Question | Assessment |
|----------|------------|
| Who is the manufacturer? | The natural or legal person who has the product designed or made and markets it under their name. That is the owner or a company of the owner. The legal person and the postal address are not decided (decision D1). |
| When do the duties start? | With the first *placing on the market*: the first time a unit is supplied to another person for distribution or use in the EU, for payment or free of charge. Building and using the 10 prototypes inside the owner's control is not placing on the market *(verify: Blue Guide section 2.3)*. |
| Prototypes | They stay internal (owner, 2026-11-03) and carry a "prototype, not for sale or field use" mark (MECH-006). Lending or giving a prototype to another person or company can count as making available: avoid it or treat that unit as a product. |
| Open-source publication | Publishing the design files is not placing a product on the market. The CRA has a lighter regime for open-source software stewards, but the project licenses the hardware under CC BY-NC-SA and keeps the option to sell commercial licences and units (ADR-0013, ADR-0015), so the steward regime cannot be assumed. This assessment plans for the full manufacturer role (RISK-038) *(needs a lawyer)*. |
| Other operators | No importer, distributor or authorised representative is planned. If units are made outside the EU and sold by another company, that company takes importer duties. |

Manufacturer duties that follow from the acts below, in short: design to the essential requirements; carry out the conformity assessment; draw up the technical documentation and keep it with the declaration of conformity for 10 years; affix the CE marking and the identification; give instructions and safety information; keep series production in conformity; handle complaints, non-conforming products and, under the CRA, vulnerabilities; cooperate with the market surveillance authorities.

## 4. Result in one table

| Act | Applies | Why | Conformity route | Main standards | Evidence status |
|-----|---------|-----|------------------|----------------|-----------------|
| Radio Equipment Directive 2014/53/EU (RED) | **Yes** | intentional radio transmitter | internal production control (Annex II) if harmonised standards are applied in full for Art. 3(2) and 3(3); otherwise a notified body | EN IEC 62368-1, EN 62311 or EN 50663, EN 301 489-1/-17, EN 55032, EN 55035, EN 300 328, EN 18031-1 | none |
| Cyber Resilience Act (EU) 2024/2847 (CRA) | **Yes**, for units placed on the market from 11 December 2027; reporting duties earlier | product with digital elements and a data connection | internal control (module A), default class | none harmonised yet; ETSI EN 303 645 as state of the art | drafts only |
| RoHS 2011/65/EU | **Yes** | electrical and electronic equipment | internal control; EN IEC 63000 | EN IEC 63000 | register seeded, 0 declarations |
| REACH (EC) 1907/2006 | **Yes** (articles) | every article supplied | information duty, no assessment procedure | -- | none |
| WEEE 2012/19/EU | **Yes** | electrical and electronic equipment | registration per member state | EN 50419 | none |
| General Product Safety Regulation (EU) 2023/988 (GPSR) | **Yes**, for aspects that the RED and the CRA do not cover, if consumers can get the product | consumer product | internal risk analysis and technical documentation | -- | risk assessment drafted |
| Packaging Regulation (EU) 2025/40 (PPWR) | **Yes**, for the packaging of sold units | packaging | per regulation | -- | none |
| Ecodesign: standby and networked standby (EU) 2023/826 | **Open** | depends on the product list of the regulation | internal design control | EN 50564, EN 50643 | scope test open (V4) |
| Ecodesign and energy label for light sources (EU) 2019/2020, 2019/2015 | **Probably not** | indicator, not illumination | -- | -- | scope test open (V5) |
| Data Act (EU) 2023/2854 | **Open, minor** | connected product | -- | -- | scope test open (V6) |
| Low Voltage Directive 2014/35/EU (LVD) | No | radio equipment is excluded; also below the voltage range | -- | -- | -- |
| EMC Directive 2014/30/EU (EMCD) | No | radio equipment is excluded; the RED applies its requirements | -- | -- | -- |
| Batteries Regulation (EU) 2023/1542 | No | no battery | -- | -- | -- |
| GDPR (EU) 2016/679 | Not for the device | no personal data processed by design | -- | -- | owner to confirm |
| Others (toys, machinery, medical devices, ATEX, accessibility, AI) | No | see section 6 | -- | -- | -- |

## 5. Assessment per act

Each part gives the scope test, the requirements that follow, the route, and the effect on the design.

### 5.1 Radio Equipment Directive 2014/53/EU

**Scope test.** Radio equipment is an electrical or electronic product that intentionally emits or receives radio waves for radio communication (Art. 2(1)(1)). The product contains a Wi-Fi transmitter and receiver, so it is radio equipment as a whole, not only the module. No exclusion of Annex I applies (the product is not an evaluation kit for professionals, not amateur radio, not aviation or marine equipment). A pre-certified module does not transfer conformity to the finished product: the manufacturer of the finished product declares conformity for all essential requirements and may use the module's test results as part of the evidence.

**Essential requirements (Art. 3).**

| Article | Requirement | How the product is affected | Planned evidence |
|---------|-------------|-----------------------------|------------------|
| 3(1)(a) | Health and safety of persons and domestic animals and protection of property, with the objectives of the LVD **but with no voltage limit applying** | The 5 V supply does not remove the safety assessment. Fire (a USB source can deliver 15 W and more), touch temperature, LED optical radiation, RF exposure and the mounting means are assessed (SYS-050, SYS-051, SYS-052, MECH-010, MECH-011) | safety assessment to EN IEC 62368-1; EMF assessment; EN 62471 assessment |
| 3(1)(b) | Adequate electromagnetic compatibility as in the EMC Directive | Emission and immunity of the whole product in its housing with a cable and a supply (SYS-049, HW-018) | EMC test report |
| 3(2) | Effective and efficient use of the radio spectrum | Radio parameters of the module in this product: antenna surroundings, output power setting, adaptivity (HW-005, SYS-038) | module test report plus product spot checks decided with the laboratory |
| 3(3)(d), (e), (f) | Network protection, privacy, protection from fraud | Applied to internet-connected radio equipment by Delegated Regulation (EU) 2022/30 since 1 August 2025; repealed with effect from 11 December 2027 by Delegated Regulation (EU) 2026/339, when the CRA takes over *(verify)*. (d) applies; (e) applies only if personal data is processed (by design no); (f) does not apply (no payments) | EN 18031-1 gap analysis, only if a unit is placed on the market before 11 December 2027 |
| 3(4) | Common charger | Only for the listed categories of rechargeable devices; the product has no battery | statement |

**Conformity route (Art. 17).** For Art. 3(1) the manufacturer may always use internal production control (Annex II, module A). For Art. 3(2) and 3(3) module A is allowed only where harmonised standards cited in the Official Journal are applied in full; otherwise an EU-type examination by a notified body (Annex III) or full quality assurance (Annex IV) is needed. Plan: module A with EN 300 328 and, if needed, EN 18031-1 applied in full. The EN 18031-1 citation carries a restriction for products that let the user skip setting a password; the per-unit passphrase (ADR-0006) avoids that case *(verify)*.

**Other duties.** Technical documentation with the content of Annex V; EU declaration of conformity (Annex VI) or the simplified one (Annex VII) with each unit; CE marking, type and serial identification, manufacturer name and address; instructions with the frequency band and the maximum radio power (Art. 10(8)); information on restrictions of use, none expected for 2.4 GHz Wi-Fi (Art. 10(10)). Item list: `technical-file/06-user-information-and-labelling/labelling-and-user-information.md` (SYS-048).

**Effect on the design.** Keep the module and its antenna within the conditions of the module's own approval (keep-out, ground, output power table); DEV-004 on the spike board is open against this. Set the regulatory domain and the transmit power in the firmware from the module's test report (no requirement exists yet, gap G5 of the risk assessment). Every firmware release that changes the radio stack or its settings is checked against Art. 3(2) again.

### 5.2 Cyber Resilience Act (EU) 2024/2847

**Scope test.** A product with digital elements whose intended or foreseeable use includes a direct or indirect data connection to a device or network (Art. 2(1), Art. 3). The product is hardware with firmware, joins a network and takes remote updates, so it is in scope. No exclusion applies (it is not a medical device, vehicle, aviation or marine equipment). **Class:** default. Annex III (important products) lists, among others, smart-home products with security functions (locks, cameras, baby monitors, alarms) and general-purpose virtual assistants; Annex IV lists critical products. A status light matches none; the class follows the core function of the product, not its parts *(verify against the technical descriptions in Implementing Regulation (EU) 2025/2392)*.

**Dates.** In force since 10 December 2024. Reporting duties (Art. 14) apply from 11 September 2026, also for products already on the market. All other duties apply to products placed on the market from 11 December 2027 *(verify)*.

**Requirements.** Annex I Part I (properties of the product) and Part II (vulnerability handling) on the basis of a cybersecurity risk assessment (Art. 13(2) and (3)); a support period of at least 5 years unless the product is expected to be in use for a shorter time (Art. 13(8); owner: 5 years); a software bill of materials; user information of Annex II; technical documentation of Annex VII; EU declaration of conformity; reporting of actively exploited vulnerabilities and severe incidents within 24 hours (early warning), 72 hours (notification) and a final report, through the single reporting platform. Mapping and gaps: `technical-file/05-cybersecurity/cra-annex-i-mapping.md`.

**Conformity route.** Default class: internal control (module A, Annex VIII) *(verify)*. No harmonised standard is cited yet in the sources read; conformity is argued directly against Annex I with ETSI EN 303 645 and the draft CEN/CENELEC standards as state of the art.

**Effect on the design.** Secure boot and flash encryption before any unit leaves the owner (SYS-043); signed updates with rollback protection (SYS-029, ADR-0007); no default or shared password (ADR-0006); debug access closed or protected in production (rule HWC-009 lists the access points); SBOM per release (SYS-044); a security event record and the automatic-update default are not specified yet (gaps in the mapping).

### 5.3 RoHS Directive 2011/65/EU

**Scope test.** Electrical and electronic equipment that depends on electric current to work (Art. 3(1)); category 11 covers all equipment not in another category. In scope; no exclusion applies. **Requirements:** the ten restricted substances stay below the limits in each homogeneous material (Art. 4, Annex II as amended by (EU) 2015/863), with the exemptions of Annex III where a part uses one (for example lead in some glass or ceramic of components, each with an expiry date to track). **Route:** internal production control (module A) with technical documentation to EN IEC 63000, covered by the same declaration of conformity and CE marking. **Effect:** a manufacturer declaration per part number and for the housing material (HW-019, `technical-file/07-supplier-declarations/rohs-reach-weee.md`).

### 5.4 REACH Regulation (EC) 1907/2006

**Scope test.** The product is an article. **Requirements:** tell the recipient, and a consumer on request within 45 days, if any article in the product contains a substance of the Candidate List above 0.1 % by weight (Art. 33); notify such articles to the SCIP database under the Waste Framework Directive; observe the restrictions of Annex XVII (for example on some phthalates and on lead in consumer articles). No CE marking and no conformity procedure. **Effect:** the same declarations as for RoHS, checked against the current Candidate List before each release; also check the Persistent Organic Pollutants Regulation (EU) 2019/1021 for flame retardants in plastics.

### 5.5 WEEE Directive 2012/19/EU

**Scope test.** Electrical and electronic equipment; small equipment (no external dimension above 50 cm) *(verify the category)*. **Requirements:** registration as a producer in each member state where units are sold, before the first sale there, with an authorised representative where the seller has no seat in that state; the crossed-out wheeled bin marking (EN 50419); financing of collection; information for users and for treatment facilities. **Effect:** label space (SYS-048, MECH-006); the registration is an organisational task with a lead time, to plan per country.

### 5.6 General Product Safety Regulation (EU) 2023/988

**Scope test.** Products that consumers are likely to use under reasonably foreseeable conditions, even if not intended for them (Art. 3). The product is aimed at professional teams now and at non-technical people later (NEED-016), so it counts as a consumer product. Where a specific act such as the RED covers a risk, the GPSR applies only to the aspects that act does not cover (Art. 2(1)). **Requirements that remain:** an internal risk analysis and technical documentation (Art. 9(2)); identification of the product and the manufacturer with a postal and an electronic address (Art. 9(5), (6)); instructions and safety information in the language of the member state (Art. 9(7)); a channel for complaints and a register of them; reports of accidents through the Safety Business Gateway; an EU-based responsible person (Art. 16); extra information duties for online sales (Art. 19). **Effect:** the risk assessment in the technical file also covers foreseeable use by children and vulnerable persons (small parts, flashing light).

### 5.7 Ecodesign rules

- **External power supplies (EU) 2019/1782:** not applicable; no power supply is placed on the market with the product.
- **Standby and networked standby (EU) 2023/826** (applies since 9 May 2025): applies to the household and office equipment listed in its Annex I that depends on mains input, directly or through an external supply, and sets limits for off, standby and networked standby power. The product is always on by function and is powered from a source the user supplies. Whether it falls under a listed category is not decided (V4). If it does, the networked-standby limit and the power-management rules would need a defined low-power state.
- **Light sources (EU) 2019/2020 and energy labelling (EU) 2019/2015:** these cover light sources by luminous flux and colour range, and products that contain them. An indicator ring is likely outside the scope or within the exemptions for signalling and display use (V5).
- **Ecodesign for Sustainable Products Regulation (EU) 2024/1781:** framework only; no delegated act for this product group is known.

### 5.8 Packaging and Packaging Waste Regulation (EU) 2025/40

Applies to the packaging of sold units (general application from August 2026 *(verify)*): minimised packaging, substance limits, material marking as the labelling rules take effect, and producer registration for packaging in each member state. **Effect:** an organisational task with the WEEE registration; choose a single-material carton.

### 5.9 Data protection and data acts

The device stores Wi-Fi credentials, tokens and certificates and shows build states. Job names and build states are not personal data in themselves; the device sends no logs or telemetry to the manufacturer (consequence 10 in Appendix A; rule SWC-001 forbids the network log backend). The GDPR is therefore not triggered by the device; the owner confirms. The Data Act (EU) 2023/2854 gives users rights to data that connected products generate; the duties of its Chapter II do not apply to micro and small enterprises, and the product makes its data available to the user directly (V6).

## 6. Acts assessed and found not applicable

| Act | Reason |
|-----|--------|
| Low Voltage Directive 2014/35/EU | Radio equipment under the RED is not subject to it (RED Art. 1(4) *(verify)*); its safety objectives apply through RED Art. 3(1)(a). The product is also below 75 V DC |
| EMC Directive 2014/30/EU | Radio equipment under the RED is excluded (the requirement applies through RED Art. 3(1)(b)) |
| Batteries Regulation (EU) 2023/1542 | No battery or cell. Re-assess for NEED-015 (battery power in a later release) |
| Common charger rules (RED Art. 3(4), Directive (EU) 2022/2380) | Apply to listed categories of rechargeable portable equipment; the product is not rechargeable |
| Toy Safety Directive 2009/48/EC | Not designed or intended for play by children under 14. The marketing must not present it as a toy |
| Machinery Regulation (EU) 2023/1230 | No moving parts driven by a drive system |
| Medical Devices Regulation (EU) 2017/745 | No medical purpose |
| ATEX Directive 2014/34/EU | Not for explosive atmospheres |
| European Accessibility Act (EU) 2019/882 | The product is not in its list (computers, terminals, e-readers and similar) *(verify)* |
| Artificial Intelligence Act (EU) 2024/1689 | No AI system |
| Lighting standards for luminaires (EN 60598-1) and lighting EMC (EN IEC 55015, EN 61547) | The main purpose is indication, not illumination; record the reasoning in the test plan and confirm with the laboratory |

## 7. Conformity strategy

1. **One declaration of conformity** covers the RED and RoHS, and the CRA from 11 December 2027 (`technical-file/09-declaration-of-conformity/DoC-template.md`).
2. **Module A throughout,** on the condition that EN 300 328 (and EN 18031-1 if a unit is sold before 11 December 2027) is applied in full. If a harmonised standard is not applied in full, a notified body is involved for that article.
3. **Pre-certified module:** obtain Espressif's RED test reports and declaration for the exact module variant; keep the module inside its approved conditions; agree with the laboratory which radio tests are repeated on the product (guidance: ETSI EG 203 367 *(verify)*).
4. **Design for the tests:** the design rules that the tests depend on are requirements (SYS-049 to SYS-052, HW-018 to HW-021, MECH-010, MECH-011) and, where a file can show them, automated checks (`automated-checks.md`).
5. **Pre-compliance before the accredited tests:** emission pre-scan and ESD on the first product board; the test plan is `technical-file/04-standards-and-testing/conformity-test-plan.md`.
6. **Risk assessment first:** the hazards and the measures are in `technical-file/03-risk-and-safety/risk-assessment.md`; the cybersecurity risk assessment per release follows the CRA mapping.
7. **Technical file as a by-product:** each evidence item is filed under `technical-file/` when it is made; `technical-file/INDEX.md` is the completeness list.

## 8. Dates that matter

| Date | Event | Effect on the project |
|------|-------|-----------------------|
| 13 December 2024 | GPSR applies | applies from the first consumer sale |
| 1 August 2025 | RED Art. 3(3)(d), (e), (f) apply (Delegated Regulation (EU) 2022/30) | EN 18031-1 needed for a sale before 11 December 2027 |
| 9 May 2025 | Standby regulation (EU) 2023/826 applies | only if in scope (V4) |
| 11 September 2026 | CRA reporting duties apply | a reporting procedure must exist before the first sale |
| 11 December 2027 | CRA applies in full; Delegated Regulation (EU) 2022/30 is repealed | the CRA is the cybersecurity basis for sales from this date |
| first supply to another person | all manufacturer duties start | decisions D1 to D4 must be closed before it |

All dates *(verify)*.

## 9. Open decisions and checks

### Decisions for the owner

| # | Decision | Needed before |
|---|----------|---------------|
| D1 | Manufacturer: legal person and postal address | first supply; the label drawing |
| D2 | First date of sale: before or after 11 December 2027 (decides whether the EN 18031-1 work is needed) | planning of the cybersecurity evidence |
| D3 | Sold to consumers or to businesses only (does not remove the GPSR if consumers can get it, but sets the language and warning effort) | user information |
| D4 | Markets inside the EU for the first sales (WEEE and packaging registers, languages) | first supply |
| D5 | Housing material and process for sold units (MECH-010 can rule out unrated printed PETG) | product housing design; a new ADR |
| D6 | Input protection against a faulty USB source (RISK-050): over-voltage cut-off, fuse, or accepted with evidence | product board schematic |
| D7 | Confirm that no logs or usage data leave the device | privacy statement |
| D8 | Accept the risk criteria proposed in the risk assessment | approval of the risk assessment |

### Checks against official texts or with an expert

| # | Check |
|---|-------|
| V1 | Every article number, date and standard edition marked *(verify)*, against the Official Journal and the current RED standards list |
| V2 | Fire classification of a USB-C powered product: can the circuits before the current limit be PS1, and what does the laboratory ask of the housing |
| V3 | RF exposure route: EN 50663 low-power exclusion with a duty limit, or EN IEC 62311 |
| V4 | Scope of the standby regulation (EU) 2023/826 for this product |
| V5 | Scope of the light-source rules (EU) 2019/2020 and 2019/2015 for an RGB indicator ring |
| V6 | Data Act duties, if any |
| V7 | CRA role (manufacturer or open-source steward) with a lawyer; CRA class against Implementing Regulation (EU) 2025/2392 |
| V8 | WEEE category and the producer registers of the first markets |

## 10. Record of owner input and history

### Owner answers of 2026-11-03

- Market: EU only for now. Use: internal tool, designed so that it can be sold later.
- Distribution: start as open source; keep the professional-product route open. Which CRA role applies (open-source steward or manufacturer) depends on the first supply to others *(verify)*; the design plans for the manufacturer role.
- Support period: 5 years.
- Security: **secure boot and flash encryption are wanted.** This replaces "later with the door open" (round 2) for units that are sold. Consequence: ADR-0007 option C moves from "later" to a planned step. The author's working default is in ADR-0007 (new section "Owner input of 2026-11-03"): no irreversible chip step on the first prototypes until the procedure is proven on a sacrificial board; secure boot and flash encryption enabled before any unit leaves the owner's control. The owner must confirm that split.
- The 10 prototypes stay internal (owner, 2026-11-03). They are not placed on the market and are not supplied to others.
- Manufacturer (legal person and postal address) on the label: deferred by the owner. It must be decided before the first unit is supplied to anyone outside the owner's control.

### History

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-11-03 | First assessment from the design plan 02 and ADR-0002 to ADR-0008; owner answers recorded |
| 0.2 | 2026-11-10 | Status update on RED cybersecurity, CRA dates and class, new Draft requirements |
| 0.3 | 2026-11-10 | Restructured: scope tests per act, role and start of duties, acts found not applicable with reasons, conformity strategy, dates, open decisions. RED Art. 3(1)(a) safety scope widened (fire, touch temperature, RF exposure, mounting). The 2026-11-03 consequence list is kept unchanged as Appendix A because other documents cite its item numbers |

## Appendix A: consequence list of 2026-11-03 (unchanged)

Author's first assessment from the design plan 02 and ADR-0002 to ADR-0008. Where this list and sections 4 to 8 differ, sections 4 to 8 are newer.

| # | Consequence | Source | Action |
|---|-------------|--------|--------|
| 1 | The 10 prototypes are for the owner and are not placed on the market. Manufacturer duties start when units are supplied to others (about 1000 per year later). Prototypes must carry a "prototype, not for sale or field use" label. | owner round 2 | Label text in the key-management and manual work; owner confirms the 10-unit scope |
| 2 | RED applies from the first unit placed on the market. The Wi-Fi module's own radio test reports help, but the finished product (antenna placement, housing, LED noise, software) needs its own assessment. ADR-0003 option A (module inside the ring) and option C (bare chip) change this a lot: a bare chip needs the full radio test. | ADR-0002, ADR-0003 | Keep the module (A or B) in the baseline; record the radio route in an ADR when the topology is chosen |
| 3 | RED delegated act 2022/30 (cyber, Art. 3(3)(d), (e), (f)) and EN 18031-1 apply to internet-connected radio equipment. Net effect: access control, secure update, secure storage, no default password, logging. The design has per-unit passphrase, web login, signed updates; it lacks secure storage on prototypes. | RV-001 item 12; ADR-0006, 0007 | Gap analysis against EN 18031-1 clauses before the first unit is sold *(verify whether the standard is harmonised at that date)* |
| 4 | CRA: self-assessment is the expected route for a default-class product *(verify)*. Needs SBOM, vulnerability handling, security update for the support period, secure by default, reporting duty to CSIRT/ENISA for exploited vulnerabilities. Open-source steward rules apply if the project is published without commercial supply *(verify)*. | ADR-0007, SYS-024, SYS-029 | SBOM requirement; vulnerability-handling document; support period decision by the owner |
| 5 | Physical attack on prototypes: flash is readable (no secure boot, no flash encryption). The claims in SYS-034 and SYS-035 are limited to network, web interface and access point. Units placed on the market need the secure-boot decision (ADR-0007 item 7) or a documented justification under EN 18031 / CRA *(verify)*. | RV-001 item 12 | Follow-up ADR on secure boot before volume production |
| 6 | Unit passphrase on a label is a shared secret. It is not a "default password" in the sense of a common password (each unit differs), which is the point of the per-unit design. *(verify with EN 18031-1 / ETSI EN 303 645 5.1)* | ADR-0006 | Include in the cyber gap analysis |
| 7 | LED ring: EN 62471 photobiological assessment for a ring that is visible to the eye. Likely low risk group for 16 small LEDs at limited current, but not measured. | SYS-001, SYS-020, RISK-021 | Assessment after spike 7.5 |
| 8 | Safety (EN 62368-1 via RED): USB-C SELV, no battery, plastic housing; thermal and flammability of the printed shell for prototypes; material for sold units to be rated *(verify)*. | RISK-005 | Thermal check in spike 7.5; housing material decision later |
| 9 | EMC: EN 301 489-1/-17 plus EN 55032/55035 *(verify exact set)*. LED data line (800 kHz class) and USB-C are emission paths. Layout and ESD are DFx items. | ARCH-001, ARCH-003 | Pre-compliance plan with the first board revision |
| 10 | Privacy: no personal data by design. The Wi-Fi password and the Jenkins token are secrets but not personal data in themselves. GDPR is likely not triggered *(verify)*. | owner confirm | Owner confirms that no logs leave the device |
| 11 | RoHS, REACH, WEEE: apply to units placed on the market. Supplier declarations for the shop's parts are needed; WEEE registration is per country. | RoHS, REACH | Collect declarations with the real BOM (spike 7.4) |
| 12 | Labelling: manufacturer name and address, type/serial, CE mark, WEEE symbol, the Wi-Fi band and power. The housing is about 53 mm, so label space is tight (AS4). | MECH | Label drawing when the housing is designed |
| 13 | Time and certificates: the product does not ship a trusted time source and uses a device-generated certificate with a pinned fingerprint; this is a design choice and not a compliance item, but the user information must explain the pin. | ADR-0008 | Manual |
