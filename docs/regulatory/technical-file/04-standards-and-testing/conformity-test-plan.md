# Conformity test plan

- **Document:** Technical file section 04, plan of the assessments and tests for CE marking
- **Status:** Draft -- no test has been run; no laboratory has been asked
- **Version:** 0.1   **Date:** 2026-11-10
- **Author:** the assistant   **Owner / approver:** Ben Spoor   **Reviewers:** none yet

## 1. Purpose and scope

This plan lists the assessments and tests that produce the conformity evidence for the busy-light, in which order, on which samples and against which criteria. The standards are in `standards-list.md`; the hazards behind the tests are in `../03-risk-and-safety/risk-assessment.md`. The general verification plan of the project is `docs/verification/test-plan.md`; this plan covers the regulatory part only. Laboratory quotations, the sample count and the dates are open until a product hardware revision exists.

## 2. Equipment under test

| Item | Definition |
|------|------------|
| Product | A released hardware revision in the product housing, with the release firmware. The spike board is not a valid test sample for accredited tests |
| Supply for the tests | A USB-C charger and a cable of stated make and model, both with their own CE evidence, named in every report. The emission result belongs to the product with that set-up; a second run with a computer port is recommended |
| Test firmware modes | (a) normal operation with Wi-Fi traffic and a moving pattern; (b) all LEDs at the limited maximum, continuous Wi-Fi transmission; (c) receive only; (d) radio test mode with fixed channel and modulation, if the laboratory needs it. Modes (b) to (d) need a manufacturing-test function in the firmware (no requirement yet, to draft with SYS-023) |
| Accessories | The stand; the wall or rack accessory for the mounting test |
| Sample count | To agree; typically [3] for safety fault tests, [1] to [2] for EMC and radio |

## 3. Ports of the product (EN 301 489-1, EN 55032, EN 55035)

| Port | Description | Phenomena that apply | Not applied, with reason |
|------|-------------|----------------------|--------------------------|
| Enclosure | Printed plastic housing with button and LED window | Radiated emission; radiated field immunity; electrostatic discharge (contact on conductive points that can be reached, air on the housing) | -- |
| DC power | USB-C VBUS and ground, user's supply, cable under 3 m | Conducted emission, measured on the mains side of the stated charger *(verify the method)* | Fast transients, surge and conducted radio-frequency immunity are expected not to apply to a DC port that is not connected to a DC distribution network and has a cable under 3 m *(verify against the port tables)* |
| Signal | USB D+ and D- on the same connector; used for programming and the production test, not in normal use | Electrostatic discharge at the connector | Conducted tests: cable under 3 m. If the data lines are disconnected or disabled in the product, state it in the report |
| Antenna | Integral PCB antenna of the module, no connector | Covered by the radio tests | Conducted measurements at an antenna port are not possible; radiated methods apply |

## 4. Assessments and tests

| # | Subject | Standard | Kind | By | Requirement / test case | Pass criterion |
|---|---------|----------|------|----|-------------------------|----------------|
| T1 | Energy source classification, single-fault tests, heating | EN IEC 62368-1 clauses 5, 6, 9, Annex B | assessment and test | in-house first, then a laboratory report | SYS-050, SYS-051 / TC-050, TC-051, TC-213 | classes as declared; no fire, no molten metal; temperatures within TS1 and the part ratings |
| T2 | Materials | EN IEC 62368-1 clause 6.4, Annex S | inspection of declarations; coupon flame test for a printed part | in-house, material makers | HW-021, MECH-010 / TC-221, TC-310 | classes as required by T1 |
| T3 | Mounting means | EN IEC 62368-1 clause 8.7 | test | in-house | MECH-011 / TC-311 | no release, no damage |
| T4 | Photobiological safety of the LED ring | EN 62471 | calculation; measurement if needed | in-house or laboratory | risk assessment H-06 (test case to add) | exempt group or risk group 1 at the use distance, else a warning and a design change |
| T5 | Flash rate of the patterns | WCAG 2.3.1, ISO 9241-391 | host test and bench record | in-house | SYS-053 / TC-053 | at most [3] flashes in any second |
| T6 | Radio-frequency exposure | EN 50663 or EN IEC 62311 | assessment | in-house, from module data | SYS-052 / TC-052 | within the public limits at the use distance |
| T7 | Radiated and conducted emission | EN 301 489-1, -17; EN 55032 class B | pre-scan, then accredited test | in-house pre-scan; accredited laboratory | SYS-049 / TC-049 | below the limits; pre-scan margin [6] dB |
| T8 | Immunity: electrostatic discharge, radiated field | EN 301 489-1, -17; EN 55035; EN 61000-4-2, -4-3 | accredited test | accredited laboratory | SYS-049, HW-018 / TC-049, TC-218 | performance criteria of EN 301 489-17: no loss of function beyond the allowed, self-recovery; no change of the current step |
| T9 | Radio parameters | EN 300 328 | review of the module report; spot checks on the product | module maker's report; accredited laboratory for the spot checks | HW-005, SW-013 / TC-205, TC-113 | module results valid for the product; radiated power and spurious emissions within the limits |
| T10 | Cybersecurity (only for sales before 11 December 2027) | EN 18031-1 | assessment with functional tests | in-house; laboratory optional | SYS-004, SYS-013, SYS-016, SYS-029, SYS-034 | each applicable requirement of the standard met and documented |
| T11 | Cybersecurity under the CRA | Annex I of (EU) 2024/2847 | risk assessment, tests, review | in-house | mapping in `../05-cybersecurity/cra-annex-i-mapping.md` | every clause has evidence |
| T12 | Substances | EN IEC 63000 | document review | in-house | HW-019 / TC-219 | a declaration for every part number and material |
| T13 | Marking and user information | RED Art. 10, WEEE, GPSR, CRA Annex II | inspection of the first article | in-house | SYS-048 / TC-048 | every item of the list present |

## 5. Sequence

1. **Now, on paper:** fire classification question to a laboratory (V2); exposure route (V3); material decision (D5); input protection decision (D6).
2. **Spike and prototype boards:** hot-plug surge record (TC-217); thermal run (TC-213, TC-051); spike 7.2 antenna check; in-house electrostatic discharge trial on the interface clamps; first emission pre-scan as a learning step, not as evidence.
3. **First product revision:** T1 to T6 in-house; T7 pre-scan with margin; fix and repeat.
4. **Frozen design:** T7 to T9 at an accredited laboratory; T10 or T11; T12; T13 on the first article.
5. **After any change:** a change impact record decides which tests are repeated (hardware revision, housing material, radio stack update, accessory).

## 6. Evidence and records

Each report names the hardware revision, the firmware version (git describe), the sample serial numbers, the supply and cable used, the laboratory and its accreditation, the standard editions and the date. Reports are filed in this folder or, for in-house tests, in `docs/verification/reports/`, and linked from `../INDEX.md` and from the evidence column of the compliance matrix. In-house results are labelled pre-compliance and are not used as the only evidence for Art. 3(2).

## 7. Open points

| # | Open point |
|---|------------|
| 1 | Choice of the laboratory; whether it accepts the module report for EN 300 328 and which spot checks it asks for |
| 2 | The named charger and cable for the emission tests |
| 3 | A manufacturing and radio test mode in the firmware (needed for T7 to T9) |
| 4 | Whether the USB data lines stay connected in the product (port list, attack surface) |
| 5 | Test case for the photobiological assessment (T4) |
