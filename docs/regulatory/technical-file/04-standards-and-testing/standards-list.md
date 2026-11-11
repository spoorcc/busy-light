# List of standards and specifications

- **Document:** Technical file section 04, standards and specifications considered for the busy-light
- **Status:** Draft -- a candidate list, not a list of standards applied. No standard has been applied or tested against yet
- **Version:** 0.2   **Date:** 2026-11-10
- **Author:** the assistant   **Owner / approver:** Ben Spoor   **Reviewers:** none yet (a test laboratory should confirm the list before tests are booked)

## 1. How to read this list

The legal basis of each group is assessed in `../../applicability.md`. The planned tests are in `conformity-test-plan.md`. The clause-to-requirement mapping is in `../../compliance-matrix.md`.

- **Edition** is the edition the project works with. It was taken from secondary sources: the Official Journal and the Commission's lists could not be opened from the session that wrote this list. Every edition and every citation status is *(verify)* against the current list under Implementing Decision (EU) 2022/2191 as amended for the RED, before a test is booked and again before the declaration of conformity is signed. Record the check in the last column (date, source, name).
- **Cited** says whether the standard is believed to be cited in the Official Journal under the act named, which gives a presumption of conformity when the standard is applied in full. "No" means the standard is used as the recognised state of the art and the technical file must carry the argument itself.
- **Use** is `full` (all applicable clauses), `part` (the clauses named) or `ref` (method or guidance only).

## 2. Safety: RED Art. 3(1)(a)

| Standard | Edition | Cited | Use | Scope in this product | Evidence planned | Checked |
|----------|---------|-------|-----|-----------------------|------------------|---------|
| EN IEC 62368-1, Audio/video, information and communication technology equipment, safety requirements | 2020 + A11:2020 (the 2024 edition is published; sources say its citation is not expected soon) | under the LVD; under the RED *(verify)* | full | whole product; see the clause table below | safety assessment report (in-house or laboratory), single-fault tests | -- |
| EN 62471, Photobiological safety of lamps and lamp systems | 2008 | No (called by EN IEC 62368-1 clause 10.4) | part | LED ring: risk group at the viewing distance | assessment from LED data and a measurement if the calculation is not clearly in the exempt group | -- |
| IEC TR 62778, Blue light hazard assessment | 2014 | No | ref | method for the blue-light part of the assessment | as above | -- |
| EN 50663, Low-power equipment and human exposure to electromagnetic fields (generic) | 2017 | *(verify)* | full, if the route is chosen | Wi-Fi transmitter, if the time-averaged power is at most 20 mW | exposure assessment (SYS-052) | -- |
| EN 62479, Compliance of low-power equipment with the basic restrictions | 2010 | *(verify)* | ref | method behind the EN 50663 exclusion | as above | -- |
| EN IEC 62311, Assessment of electronic and electrical equipment related to human exposure restrictions | 2020 | *(verify)* | full, if the EN 50663 route is not possible | Wi-Fi transmitter above the exclusion level | exposure assessment (SYS-052) | -- |
| IEC 60695-11-10, Flame test methods (50 W horizontal and vertical); UL 94 | current | No | ref | flammability class of the board and the housing material | material data sheets, coupon test for printed parts (HW-021, MECH-010) | -- |
| IEC 60695-2-11, Glow-wire flammability test for end products | current | No | ref | only if the laboratory asks for it for the housing | -- | -- |

### Clauses of EN IEC 62368-1 that shape the design

Clause numbers and limits are from the author's memory of the 2020 edition and partly confirmed by secondary sources *(verify all against the standard)*.

| Clause | Subject | Meaning for the busy-light | Requirement |
|--------|---------|----------------------------|-------------|
| 4, Annex B | General; normal, abnormal and single-fault conditions | Defines the fault tests: one fault at a time, also faults in the firmware-controlled current steps | SYS-050 |
| 5 | Electrically caused injury; energy source classes ES1 to ES3 | All circuits at 5 V are ES1 (limit 60 V DC). No insulation, creepage or clearance requirement follows | SYS-050 (table) |
| 6.2 | Power source classes: PS1 at most 15 W after 3 s; PS2 at most 100 W after 5 s; PS3 above | After the current-limit switch about 8.7 W: PS1 candidate. Before the switch the source sets the power: treated as PS2 until a laboratory accepts PS1 | SYS-050, HW-010 |
| 6.3, 6.4 | Safeguards against fire under normal, abnormal and single-fault conditions; control of fire spread | PS1: no safeguard. PS2: parts on board material V-1 or better, and either separation from combustible material or a housing that meets the fire enclosure rules | HW-021, MECH-010 |
| 6.4.8, Annex S | Fire enclosure materials and flammability tests | If the housing is a fire enclosure: V-1 or better at the wall thickness used. A printed part needs its own evidence | MECH-010 |
| 8.7 | Equipment mounted on a wall, ceiling or other structure | Load test of the mounting means for the wall, clip and rack accessories | MECH-011 |
| 8 (other) | Mechanical hazards: sharp edges, stability, small parts for children's products | Edge inspection; the product is not for children | risk assessment H-10, H-11 |
| 9, Table 38 | Thermal burn; touch temperature classes TS1 to TS3 | Outer surfaces and the button within the TS1 limits | SYS-051 |
| 10.4 | Optical radiation from LEDs | Calls EN 62471 for the LED ring | risk assessment H-06 |
| Annex F | Markings and instructions | Supply rating on the product or in the instructions; safety instructions | SYS-048 |
| Annex G | Components | Ratings of the current-limit switch, the TVS diodes and the USB-C connector on file | HW-012 |
| Annex Q | Limited power source | Route to treat a supply as power-limited; relevant to the PS classification question | SYS-050 |

## 3. Electromagnetic compatibility: RED Art. 3(1)(b)

| Standard | Edition | Cited | Use | Scope in this product | Evidence planned | Checked |
|----------|---------|-------|-----|-----------------------|------------------|---------|
| ETSI EN 301 489-1, EMC for radio equipment, common technical requirements | V2.2.3 | Yes *(verify)* | full | whole product; defines the ports, the test set and the performance criteria | accredited EMC report (SYS-049) | -- |
| ETSI EN 301 489-17, specific conditions for broadband data transmission systems | V3.2.4 (V3.3.1 is also seen in declarations) | Yes, edition *(verify)* | full | Wi-Fi function: operating modes during the tests, criteria | same report | -- |
| EN 55032, Emission of multimedia equipment | 2015 + A11:2020 + A1:2020 | under the EMCD; used through EN 301 489-1 | full | emission of the non-radio functions, class B (residential) | same report; pre-scan | -- |
| EN 55035, Immunity of multimedia equipment | 2017 + A11:2020 | under the EMCD | full | immunity of the non-radio functions | same report | -- |
| EN 55016 series (CISPR 16), measuring apparatus and methods | current | No | ref | method for the pre-compliance set-up | pre-compliance record | -- |
| EN 61000-4-2, Electrostatic discharge immunity test | 2009 | basic standard | ref | housing port, USB-C shell, button | part of the EMC report; HW-018 | -- |
| EN 61000-4-3, Radiated radio-frequency field immunity test | 2020 | basic standard | ref | housing port | part of the EMC report | -- |
| EN 61000-4-4, -4-5, -4-6 (fast transients, surge, conducted disturbances) | current | basic standards | ref | DC power port and signal port: apply only if the port rules of EN 301 489-1 ask for them (cable length, connection to a DC network); expected not to apply to a USB port with a cable under 3 m *(verify)* | argument in the test plan | -- |

## 4. Radio spectrum: RED Art. 3(2)

| Standard | Edition | Cited | Use | Scope in this product | Evidence planned | Checked |
|----------|---------|-------|-----|-----------------------|------------------|---------|
| ETSI EN 300 328, Wideband transmission systems in the 2.4 GHz band | V2.2.2 | Yes *(verify)* | full | Wi-Fi radio: output power (20 dBm e.i.r.p. limit), power spectral density, occupied bandwidth, out-of-band and spurious emissions, adaptivity, receiver blocking | the module maker's test report for the exact module variant; product spot checks agreed with the laboratory (radiated power and spurious emissions with the product antenna surroundings); SW-013 | -- |

## 5. Cybersecurity under the RED: Art. 3(3)(d), (e), (f)

Needed only for a unit placed on the market before 11 December 2027 (decision D2 of the applicability assessment).

| Standard | Edition | Cited | Use | Scope in this product | Evidence planned | Checked |
|----------|---------|-------|-----|-----------------------|------------------|---------|
| EN 18031-1, Common security requirements for radio equipment, internet-connected radio equipment | 2024 | Yes, with a restriction where the user may choose not to set a password (Implementing Decision (EU) 2025/138) *(verify)* | full | access control, authentication, secure update, secure storage, secure communication, resilience | assessment against each requirement and decision tree of the standard | -- |
| EN 18031-2, radio equipment that processes personal, traffic or location data | 2024 | as above | not applied | no such data by design; statement in the technical file | statement | -- |
| EN 18031-3, radio equipment that handles virtual money or monetary value | 2024 | as above | not applied | no such function | statement | -- |

## 6. Cyber Resilience Act (EU) 2024/2847

| Standard or specification | Edition | Cited | Use | Scope in this product | Checked |
|---------------------------|---------|-------|-----|-----------------------|---------|
| Harmonised standards for the CRA (CEN/CENELEC JTC 13 and ETSI, horizontal and product-specific) | drafts | None cited in the sources read *(verify)* | follow | will give the presumption of conformity for Annex I when cited | -- |
| ETSI EN 303 645, Cyber security for consumer Internet of Things, baseline requirements | V3.1.3 *(verify)* | No | ref | state of the art for the Annex I argument (no default passwords, vulnerability disclosure, updates, secure storage and communication, attack surface, data deletion) | -- |
| EN IEC 62443-4-1, Secure product development lifecycle requirements | 2018 | No | ref | process reference for Annex I Part II | -- |
| SPDX 2.3 (ISO/IEC 5962:2021) | 2.3 | No | full | SBOM format produced by `west spdx` (SYS-044) | -- |
| ISO/IEC 29147 and ISO/IEC 30111, vulnerability disclosure and handling | 2018, 2019 | No | ref | process reference for `../05-cybersecurity/vulnerability-handling.md` | -- |

## 7. Substances, waste, marking

| Standard or act | Edition | Use | Scope in this product | Checked |
|-----------------|---------|-----|-----------------------|---------|
| EN IEC 63000, Technical documentation for the assessment of products with respect to the restriction of hazardous substances | 2018 | full | RoHS technical documentation: supplier declarations per part and supplier assessment (HW-019) | -- |
| EN IEC 62474, Material declaration for products of and for the electrotechnical industry | 2019 | ref | data format for declarations collected from suppliers | -- |
| EN 50419, Marking of electrical and electronic equipment (WEEE) | 2022 *(verify)* | full | crossed-out wheeled bin and the bar or date mark (SYS-048) | -- |
| EN 50564, Measurement of low power consumption; EN 50643, networked standby | current | ref | only if the standby regulation (EU) 2023/826 applies (check V4) | -- |

## 8. Other specifications that the design follows (not legal requirements)

| Specification | Use |
|---------------|-----|
| USB Type-C Cable and Connector Specification; USB 2.0 with the Device Capacitance and inrush rules | sink behaviour, CC resistors, capacitance on VBUS (HW-003, HW-015) |
| IPC-2221, IPC-2152 (current capacity), IPC-7351 (land patterns), IPC-A-600 and IPC-A-610 (acceptability) | board design and acceptance (design-hw.md; rule HWC-010) |
| WCAG 2.x success criterion 2.3.1 and ISO 9241-391, flashing content | flash-rate limit of the light patterns (SYS-053) |
| SEI CERT C; MISRA C:2012 subset | firmware coding (coding-sw.md, SW-012) |

## 9. Standards considered and not applied

| Standard | Reason |
|----------|--------|
| EN 60598-1 (luminaires), EN IEC 55015 and EN 61547 (lighting EMC), EN 62493 (lighting EMF) | The product is an indicator, not lighting equipment; the multimedia and radio standards cover it. Confirm with the laboratory and record its answer |
| EN 61000-3-2, EN 61000-3-3 (mains harmonics and flicker) | No mains port; the user's supply is separate equipment |
| EN 55014-1, EN 55014-2 (household appliances) | Not a household appliance in the sense of these standards |
| EN IEC 61000-6-1, -6-3 (generic EMC) | A product standard exists (EN 301 489 series with EN 55032 and EN 55035) |
| EN IEC 62368-3 (DC power transfer through communication cables and ports) | Covers equipment that supplies power over such ports; the product only takes power *(verify)* |
| EN 62133, EN IEC 62619 and other battery standards | No battery |
| EN 71 series (toys) | Not a toy |
| EN 62479 as the only EMF evidence | The peak power is above 20 mW; usable only with a time-averaged power limit (SYS-052) |

## 10. Guidance documents

| Document | Use |
|----------|-----|
| The Blue Guide on the implementation of EU product rules (Commission notice 2022/C 247/01) | placing on the market, manufacturer role, modules |
| Guide to the Radio Equipment Directive 2014/53/EU (Commission) | scope, combined equipment, documentation |
| ETSI EG 203 367, Guide to the application of harmonised standards to multi-radio and combined radio and non-radio equipment | which module results can be reused for the product *(verify)* |
| REDCA technical guidance notes | practice for modules and risk assessment |
| CEPT ERC Recommendation 70-03 | frequency use conditions for short-range devices, background for the 2.4 GHz band |
| Commission guidance on the standby regulation; Commission FAQ on the CRA | scope tests V4 and V7 |

## 11. History

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-11-10 | First candidate list |
| 0.2 | 2026-11-10 | Clause table for EN IEC 62368-1 (power source classes, fire enclosure, touch temperature, mounting, optical radiation); EMF route with EN 50663; basic EMC standards and the port question; EN 300 328 parameters; guidance documents; standards considered and not applied with reasons |
