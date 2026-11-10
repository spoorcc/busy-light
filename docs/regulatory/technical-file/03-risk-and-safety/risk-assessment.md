# Product risk assessment

- **Document:** Technical file section 03, risk analysis and assessment of the busy-light
- **Status:** Draft -- not reviewed; the risk criteria in section 3.3 are a proposal that the owner must accept (decision D8 of the applicability assessment)
- **Version:** 0.1   **Date:** 2026-11-10
- **Author:** the assistant   **Owner / approver:** Ben Spoor
- **Reviewers:** none yet
- **Design state assessed:** the requirements, the accepted decisions and the spike board (`hw/kicad/spike-gate`). No product board, no product housing and no product firmware exist. Every score is an engineering judgement; no measurement or test supports it yet.

## 1. Purpose

The technical documentation of the Radio Equipment Directive must contain an adequate analysis and assessment of the risks (Annex II and Annex V of 2014/53/EU *(verify)*). The General Product Safety Regulation asks the manufacturer for an internal risk analysis (Art. 9(2)), and the Cyber Resilience Act for a cybersecurity risk assessment (Art. 13(2) and (3)). This document is that analysis for safety, electromagnetic compatibility, radio spectrum use and substances, and it gives the summary and the links for cybersecurity.

It does three things: it identifies the hazards of the product in its intended use and its foreseeable misuse; it estimates and evaluates each risk; and it names the measure that reduces each risk, the requirement that carries the measure and the test that will show it. The detailed entries stay in the risk register (`docs/risk/risk-register.md`); this document is the structured view of them for the technical file. It does not state that any risk is acceptable today.

## 2. Product, users and use

The product is described in `../01-general/product-description.md`. The points that matter for the risks:

| Aspect | Assumption used in this assessment |
|--------|------------------------------------|
| Intended use | Status indication on a desk, a stand, a clip or a rack adapter, indoors, dry, up to [35] degC ambient, always powered |
| Users | Adults at work or at home. Children and vulnerable persons can be near the product in a home, although it is not intended for them |
| Supply | Any USB-C source the user owns: computer port, charger, power bank, hub; with any cable |
| Life | 5 years support period; continuous operation |
| Maintenance | None by the user. The housing can be opened (MECH-009), which the user is not asked to do |

### Reasonably foreseeable misuse

| # | Misuse | Considered in |
|---|--------|---------------|
| M1 | A cheap, damaged or non-compliant charger or cable; a Power Delivery source that applies more than 5 V by fault | H-02, H-03 |
| M2 | The device is covered (papers, cloth), put in the sun or on a warm device | H-02, H-04, H-05 |
| M3 | Use where children can reach it; a child takes it as a toy | H-07, H-10 |
| M4 | Use as a warning or safety signal that people rely on | H-13 |
| M5 | Mounting above a person with a self-made or damaged accessory | H-09 |
| M6 | Opening the housing while powered | H-01, H-11 |
| M7 | Use in a dark room at full brightness, at close range | H-06, H-07 |
| M8 | The user changes radio or security settings to unsafe values through the web interface | R-01, C-02 |
| M9 | Use in a damp place or outdoors | excluded by the user information; not designed for |

## 3. Method

### 3.1 Steps

The assessment follows the usual sequence of ISO 12100 and ISO/IEC Guide 51: define the limits of the product (section 2); identify hazards; estimate the risk; evaluate it against criteria; reduce it, in the order (1) safe design, (2) protective measures, (3) information for the user; then estimate the remaining risk. Hazards are identified by:

- the energy-source model of EN IEC 62368-1 for safety (electrical, power and fire, hazardous substances, mechanical, thermal, radiation);
- the phenomena of the EMC standards for each port of the product (housing port, DC power port, data port);
- the radio parameters of EN 300 328;
- the assets and interfaces of the product for cybersecurity (summary only);
- the lists of restricted substances.

### 3.2 Scales

The scales are those of the risk register, defined here so that scores can be compared.

| Score | Severity: harm to persons | Severity: other harm |
|-------|---------------------------|----------------------|
| 1 | none, or discomfort | cosmetic; no loss of function |
| 2 | minor injury, first aid at most | short loss of function; the user recovers it |
| 3 | injury that needs medical treatment, full recovery | unit damaged or wrong indication; a compliance test fails |
| 4 | serious injury, lasting effect | property damage; product cannot be sold or must be withdrawn; secrets of users exposed |
| 5 | life-threatening or fatal | fire beyond the product; signing key lost for all units |

| Score | Likelihood over the life of the product, with the measures that exist today |
|-------|----------------------------------------------------------------------------|
| 1 | not expected; needs several independent faults or deliberate misuse |
| 2 | unlikely; a single fault or a rare condition |
| 3 | possible; will happen to some units or users |
| 4 | likely; expected in normal use over the life |
| 5 | almost certain |

Risk = severity x likelihood.

### 3.3 Risk criteria (proposed, decision D8)

| Class | Score | Meaning |
|-------|-------|---------|
| Low | 1 to 4 | Acceptable. No further measure needed; keep the information for the user |
| Medium | 5 to 9 | Acceptable only if the risk is reduced as far as reasonably practicable and the owner accepts the remaining risk in writing |
| High | 10 to 25 | Not acceptable for a unit placed on the market. A design or protective measure is needed |

Two extra rules: a hazard with severity 5 needs a design measure whatever its score, because information for the user alone is not enough; and a risk counts as reduced only when its test case has recorded evidence. Until then the initial score stands.

## 4. Hazards and risk control

Columns: **S x L = R** is the initial estimate with the design as it is today. **Target** is the score that the named measures are expected to reach once verified; it is a goal, not a result. **Register** links the full entry.

### 4.1 Safety (RED Art. 3(1)(a), GPSR)

| ID | Hazard and harm | Cause or situation | S x L = R | Risk control (requirement) | Verification | Target | Register |
|----|-----------------|--------------------|-----------|----------------------------|--------------|--------|----------|
| H-01 | Electric shock | Contact with live parts when the housing is open | 1 x 1 = 1 Low | All circuits at 5 V nominal, class ES1 (limit 60 V DC *(verify)*); also ES1 if a faulty source applies 20 V. No safeguard needed | Classification table of SYS-050 | 1 | -- |
| H-02 | Fire: a part ignites the board or the housing | Short circuit of a part on VBUS_IC or +5V; current-limit switch fails short; source of 15 W or more; unrated printed housing; covered device (M1, M2) | 5 x 2 = 10 **High** | Design: hardware current limit (HW-010); circuit classification and single-fault safety (SYS-050); board material V-1 or better (HW-021); rated housing material (MECH-010); thermal limit (HW-013); track width report (rule HWC-010). Information: supply rating, do not cover | TC-050, TC-221, TC-310, TC-213 | 5 x 1 = 5 | RISK-047, RISK-003, RISK-029 |
| H-03 | Over-voltage on the input, then overheating or fire | Faulty or non-compliant source or cable applies 9 V to 20 V (M1); parts on VBUS_IC are rated 6 V to 7 V | 4 x 2 = 8 Medium | **No design measure exists** (no over-voltage cut-off, no fuse). TVS1 clamps a surge but overheats under a steady over-voltage. Decision D6. The fault tests of SYS-050 show the outcome | TC-050 | to set after D6 | RISK-050, RISK-046 |
| H-04 | Burn from a hot surface | Top current step in a warm room; hung firmware holds the top step; covered device | 2 x 2 = 4 Low | Surface limit (SYS-051); thermal limit (HW-013, MECH-005); watchdog returns to the lowest step (SW-010) | TC-051, TC-213, TC-110 | 2 x 1 = 2 | RISK-048 |
| H-05 | Housing softens, deforms or opens | Heat above the material limit (PETG prototype) | 2 x 3 = 6 Medium | Material margin (MECH-005); material choice for sold units (MECH-010, D5) | TC-305 | 2 x 2 = 4 | RISK-005 |
| H-06 | Eye hazard or glare from the LEDs | Full white at close range in a dark room (M7) | 2 x 2 = 4 Low | Current limit sets the maximum light output (SYS-020); diffuser (MECH-002); photobiological assessment to EN 62471 with the result in the user information if above the exempt group | assessment after spike 7.5 (not planned in a TC yet, gap G8) | 2 x 1 = 2 | RISK-021 |
| H-07 | Seizure in a person with photosensitive epilepsy | A pattern flashes a large part of the ring at 3 Hz or more (M3, M7) | 4 x 2 = 8 Medium | Flash-rate limit enforced by the pattern engine, also for user mappings (SYS-053) | TC-053 | 4 x 1 = 4 | RISK-052 |
| H-08 | Radio-frequency exposure above the public limits | Hand or body on the housing while the radio transmits | 2 x 2 = 4 Low | Exposure assessment; transmit-duty limit or stated distance (SYS-052) | TC-052 | 1 x 1 = 1 | -- |
| H-09 | Unit falls from a wall, ceiling or rack mount | Printed lug creeps or breaks; wrong accessory (M5) | 3 x 3 = 9 Medium | Retention and cycle life (MECH-007, MECH-008); load test for mounting accessories (MECH-011) | TC-307, TC-308, TC-311 | 2 x 2 = 4 | RISK-039 |
| H-10 | Choking on a small part | Lid, accessory or broken lug within reach of a small child (M3) | 5 x 1 = 5 Medium | Lid and board retention (MECH-009); accessory retention (MECH-008). Information: not a toy, keep away from small children (SYS-048). Severity 5: a design check of each detachable part against the small-parts cylinder is recommended (gap G7) | TC-309, TC-308, TC-048 | 5 x 1 = 5, owner acceptance | RISK-053 |
| H-11 | Cut or pinch; tripping over the cable | Sharp printed edges; opening the housing; loose cable | 1 x 2 = 2 Low | Edge inspection at the first article | first-article inspection | 2 | -- |
| H-12 | Contact with or release of hazardous substances | Restricted substance in a part or in the filament; emissions from warm printed plastic | 3 x 2 = 6 Medium | Material declarations for every part (HW-019); the housing material must be added to the register (gap G6) | TC-219 | 3 x 1 = 3 | RISK-051 |
| H-13 | People rely on a wrong or frozen indication | Stale data, hung firmware, use as a safety signal (M4) | 4 x 4 = 16 **High** (harm is to the user's work, not to persons) | Stale-data and liveness rules (SYS-010, SYS-033); safe start state (SYS-011). Information: not for safety signalling | TC-010, TC-033, TC-011 | set in the register | RISK-001, RISK-002 |

### 4.2 Electromagnetic compatibility (RED Art. 3(1)(b))

Ports of the product: the housing (radiated phenomena, electrostatic discharge), one DC power port (USB-C VBUS, cable under 3 m), and the USB data lines on the same connector (signal port, used for programming and the production test). The test levels and criteria are in the conformity test plan.

| ID | Phenomenon and effect | Cause or situation | S x L = R | Risk control (requirement) | Verification | Target | Register |
|----|-----------------------|--------------------|-----------|----------------------------|--------------|--------|----------|
| E-01 | Radiated emission above the class B limits; interference with radio services | LED data line edges, LED current steps, layout made by a generator, the cable as an antenna | 4 x 3 = 12 **High** | EMC requirement (SYS-049); series resistor at the LED data source (HW-002); layout review and keep-outs (ADR-0012); pre-scan with [6] dB margin | TC-049 | 4 x 1 = 4 | RISK-032 |
| E-02 | Conducted emission on the supply cable | LED current pulses at the refresh rate drawn from the source | 3 x 3 = 9 Medium | Capacitance of the rails (HW-014, HW-015); SYS-049; test with a named supply and cable | TC-049, TC-214, TC-215 | 3 x 1 = 3 | -- |
| E-03 | Electrostatic discharge damages or upsets the unit | Discharge to the USB-C shell or pins, the button, the housing seams; CC lines without a clamp on the spike | 3 x 4 = 12 **High** | Clamp on every interface net, near the connector (HW-018, HW-003; rules HWC-001, HWC-002) | TC-218, TC-049 | 3 x 1 = 3 | RISK-049, RISK-026 |
| E-04 | Radio-frequency field upsets the unit: wrong current step, corrupted LED data, reset | A phone or the unit's own transmitter near the CC detection and gate logic | 3 x 2 = 6 Medium | Immunity criteria of SYS-049; hardware gate independent of the firmware (HW-010); fault recovery (SYS-027) | TC-049, TC-210 | 3 x 1 = 3 | RISK-042 |
| E-05 | Surge at plug-in above the part ratings | Cable inductance against ceramic capacitors (hot plug) | 3 x 4 = 12 **High** | Measure first on the prototype, damping footprint (ADR-0021, HW-017); TVS1 | TC-217, TC-210 | set after the measurement | RISK-046 |
| E-06 | Supply dip resets the unit repeatedly | Wi-Fi and LED peaks together; weak source | 3 x 3 = 9 Medium | Supply margin (HW-004); back-off after brown-out (SW-007) | TC-204, TC-107 | 3 x 1 = 3 | RISK-004, RISK-024 |
| E-07 | The product disturbs its own receiver; short Wi-Fi range | LED and USB noise near the antenna; detuning by the ring and the housing | 4 x 3 = 12 **High** | Antenna keep-out (HW-005, open deviation DEV-004 on the spike); range requirement (SYS-038) | TC-205, TC-038 | 4 x 1 = 4 | RISK-011 |

Not relevant, with the reason: mains harmonics and flicker (no mains port); fast transients and surge on signal lines (no cable of 3 m or more *(verify the length rule in EN 301 489-1)*); magnetic field immunity (no sensitive magnetic parts; the orientation sensor is an accelerometer *(verify the part)*).

### 4.3 Radio spectrum (RED Art. 3(2))

| ID | Hazard and effect | Cause or situation | S x L = R | Risk control (requirement) | Verification | Target | Register |
|----|-------------------|--------------------|-----------|----------------------------|--------------|--------|----------|
| R-01 | Transmit power or channels outside the approved values | Wrong country code or power default; user-set country; a default changed by an update of Zephyr or the blobs (M8) | 4 x 3 = 12 **High** | Fixed regulatory domain and power limit, re-tested at each radio stack update (SW-013) | TC-113 | 4 x 1 = 4 | RISK-054, RISK-020 |
| R-02 | Radiated performance differs from the module's test report | Antenna inside the LED ring, changed ground, housing and label near the antenna | 4 x 3 = 12 **High** | Keep-out and clearance (HW-005, MECH-003); spike 7.2 as a gate (ADR-0003); radiated spot checks on the product agreed with the laboratory | TC-205, TC-303, product radio test | 4 x 1 = 4 | RISK-011, RISK-040 |
| R-03 | Adaptivity or receiver behaviour changes after a firmware update | The behaviour lives in closed Wi-Fi binaries that a Zephyr update replaces | 3 x 2 = 6 Medium | Release check of SW-013; change impact assessment for every radio stack update (technical file INDEX, completeness gate) | TC-113 | 3 x 1 = 3 | RISK-020 |

### 4.4 Cybersecurity (RED Art. 3(3) until 11 December 2027, then the CRA): summary

This table is a summary by threat group. The entries, their scores and their status are in the risk register; the requirement mapping and the gaps are in `../05-cybersecurity/cra-annex-i-mapping.md`. The cybersecurity risk assessment that the CRA asks for each release (assets, threat model, attack paths) is not written yet; it is due with the first product firmware.

Assets: the release signing key; the unit passphrase and the web password; the Wi-Fi credentials and the source tokens of the user; the integrity of the firmware; the availability of the indication; the user's network (the device must not become a way in). Entry points: the provisioning access point, the web interface, the push input, the polling client, the update client, the USB-C port (USB-Serial-JTAG), the test points, the flash chip.

| ID | Threat | Highest register score | Main controls (requirements) | Register |
|----|--------|------------------------|------------------------------|----------|
| C-01 | Signing key lost, leaked, or a development key in a release | 5 x 2 = 10 **High** | Key management, release procedure (SYS-029, ADR-0007); secret scan in CI (rule SWC-003) | RISK-006, RISK-007 |
| C-02 | Access with a guessed, shared or leaked credential | 4 x 2 = 8 Medium | Per-unit passphrase, password rules, access control (SYS-013, SYS-016, SYS-039) | RISK-012 |
| C-03 | Read-out or change of the flash; open debug access | 3 x 2 = 6 Medium (accepted for prototypes only) | Secure boot and flash encryption before a unit leaves the owner (SYS-043); debug-access inventory (rule HWC-009) | RISK-013, RISK-022, RISK-023 |
| C-04 | Malicious or old firmware installed | 3 x 2 = 6 Medium (accepted by the owner for now) | Signed updates, confirmation and rollback (SYS-029, SW-004) | RISK-014 |
| C-05 | Hostile network input crashes or exhausts the device | 3 x 3 = 9 Medium | Input limits, session limits, fuzz tests (SW-001, SW-002, SW-003); fault recovery (SYS-027) | RISK-018, RISK-010 |
| C-06 | Secrets or data exposed in transit; wrong time defeats certificate checks | 3 x 3 = 9 Medium | Transport protection, certificates, time rules (SYS-034, SYS-035, SYS-031) | RISK-015, RISK-019, RISK-016 |
| C-07 | Compromised build tool or dependency; unknown component | 4 x 2 = 8 Medium | Pinned tools and actions (rules SWC-004, SWC-005); SBOM (SYS-044, rule SWC-009) | RISK-033, RISK-035 |
| C-08 | Weak firmware configuration (shell, debug, missing hardening) or coding defect | not in the register | Configuration policy and static analysis (SW-011, SW-012; rules SWC-001, SWC-002, SWC-006, SWC-007) | -- |
| C-09 | A published vulnerability in Zephyr or the Wi-Fi binaries is missed | not in the register | Vulnerability handling and support period (SYS-045); no monitoring procedure exists (gap G9) | -- |

### 4.5 Substances and end of life (RoHS, REACH, WEEE)

| ID | Hazard and effect | S x L = R | Risk control | Verification | Register |
|----|-------------------|-----------|--------------|--------------|----------|
| S-01 | A part or the housing material contains a restricted substance, or an SVHC that is not communicated | 3 x 2 = 6 Medium | Declarations per part number (HW-019); materials register with CI report (rules HWC-006, HWC-007) | TC-219 | RISK-051 |
| S-02 | The product is disposed of in household waste | 2 x 3 = 6 Medium | Crossed-out bin marking and user information (SYS-048); producer registration (applicability 5.5) | TC-048 | -- |

## 5. Evaluation

| Class (initial) | Count | Items |
|-----------------|-------|-------|
| High | 9 | H-02, H-13, E-01, E-03, E-05, E-07, R-01, R-02, C-01 |
| Medium | 18 | H-03, H-05, H-07, H-09, H-10, H-12, E-02, E-04, E-06, R-03, C-02 to C-07, S-01, S-02 (C-08 and C-09 are not scored) |
| Low | 5 | H-01, H-04, H-06, H-08, H-11 |

Reading of the result:

1. **No risk is shown as reduced.** Every measure is a requirement or a plan; no test case has evidence. By the rule of section 3.3 the initial scores stand.
2. **The High items have measures defined, except where a decision is open.** H-02 (fire) depends on the classification question V2 and on the housing material decision D5. H-13 is a functional risk with requirements in place. The EMC and radio items are normal for a first board and are closed by layout rules, spike 7.2 and the pre-compliance tests.
3. **One hazard has no design measure at all: H-03**, over-voltage from a faulty source (decision D6). It is Medium by score but feeds H-02, which has severity 5.
4. **Two severity-5 hazards exist: H-02 and H-10.** H-02 has design measures. H-10 (small parts) relies on retention requirements and on information; a small-parts check of the detachable parts is recommended before the owner accepts it.

## 6. Gaps and recommended actions

| # | Gap | Recommended action | Related |
|---|-----|--------------------|---------|
| G1 | Fire classification of the circuits before the current limit is not settled; no input protection against a faulty source | Ask a test laboratory (V2). Decide D6: an over-voltage protected load switch, a fuse or a resettable fuse at the connector, or an accepted outcome with fault-test evidence. Record the decision in an ADR | H-02, H-03, SYS-050 |
| G2 | The housing material of sold units has no flammability rating | New ADR for the product housing material and process (D5); MECH-010 | H-02, H-05 |
| G3 | CC1 and CC2 have no ESD clamp on the spike board | Choose a clamp part with the CC-line capacitance limit; approve or change HW-018 | E-03 |
| G4 | No product firmware requirement existed for the radio settings and for the flash rate | Review and approve SW-013 and SYS-053 (Draft) | R-01, H-07 |
| G5 | Radio performance in the product is unknown; DEV-004 is open | Run spike 7.2 before any product layout (ADR-0003) | R-02, E-07 |
| G6 | The housing material, the label and the packaging are not in the materials register | Add them to `hw/compliance/materials.yaml` when chosen | H-12, S-01 |
| G7 | No small-parts check of the lid and the accessories | Add a check to the mechanical verification when the accessory set is fixed | H-10 |
| G8 | The photobiological assessment has no test case and no planned date | Add a TC when spike 7.5 gives the LED data; state the risk group | H-06 |
| G9 | No procedure to watch for vulnerabilities in Zephyr and the Wi-Fi binaries; no CRA risk assessment per release | Extend `../05-cybersecurity/vulnerability-handling.md`; write the release threat model with the first product firmware | C-08, C-09 |
| G10 | The risk criteria of section 3.3 and all scores are the author's proposal | Owner review; a second person checks the hazard list | all |

## 7. Information for the user that the risk control relies on

These points must appear in the user information (SYS-048, item list in `../06-user-information-and-labelling/labelling-and-user-information.md`). The wording follows `docs/standards/writing.md` when the manual is written; this is the content list only.

| # | Content | For hazard |
|---|---------|------------|
| I1 | Supply: a USB-C source of 5 V that meets the safety standard for such supplies; the input rating of the product | H-02, H-03 |
| I2 | Do not cover the product; use indoors, in a dry place, up to the stated ambient temperature | H-02, H-04, H-05 |
| I3 | Not a toy; keep away from small children; small parts | H-10 |
| I4 | Not for safety signalling; the indication can be late or wrong | H-13 |
| I5 | Flashing light notice, if any pattern is near the limit; how to lower the brightness | H-06, H-07 |
| I6 | Mounting: only the supplied accessories; the limits of each | H-09 |
| I7 | Minimum distance to the body, only if the exposure assessment needs one | H-08 |
| I8 | Disposal: separate collection | S-02 |

## 8. Review and revision

Review this assessment at every gate of the process and when any of these happens: a product board or housing design exists; a requirement cited here changes; a test result contradicts a score; a hazard is reported from use; the radio stack, the supply concept or the housing material changes; a new accessory is added. Each revision records what changed and why.

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-11-10 | First issue from the requirements, the risk register (RISK-001 to RISK-054) and the spike board checks. No evidence exists for any measure |
