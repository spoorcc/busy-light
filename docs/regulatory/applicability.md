# Regulatory Applicability Assessment (RAA-001)

- **Status:** Draft -- answers marked TBD must be provided by the product owner
- **Version:** 0.1   **Owner:**   **Last reviewed:**
- Re-run when: radio, battery, mains, cloud/app, data collection, new market, or new function is added.

## 1. Product definition inputs (drive everything below)
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

## 2. Legislation matrix
| Legislation | Applies if | Status | Conformity route | Candidate standards *(verify harmonised status)* |
|-------------|-----------|--------|------------------|-----------------------------------------------|
| **CRA** (EU) 2024/2847 | Product with digital elements (software+hardware, direct/indirect data connection) | Likely applies once units are placed on the market (network interface, OTA update). Not for the 10 prototypes *(verify)* | Self-assessment (default class) unless "important"/"critical" class; Annex VII tech doc | prEN/CEN-CENELEC CRA standards in development; EN 18031 series, ETSI EN 303 645, IEC 62443-4-x as guidance |
| **RED** 2014/53/EU (+ DA 2022/30) | Intentional radio emitter/receiver | Applies when placed on the market (Wi-Fi). A pre-certified module helps but does not cover the product (antenna, housing, software) *(verify)* | Module A possible if harmonised standards applied; else notified body | EN 62368-1 (safety), EN 301 489-1/-17 (EMC), EN 300 328 (2.4 GHz), EN 62311/EN 50663 (EMF), EN 18031-1/-2/-3 (cyber) |
| **LVD** 2014/35/EU | Mains-powered 50-1000 V AC / 75-1500 V DC, no radio | Not applicable on current inputs (SELV only, radio present, so RED covers safety) *(verify)* | Module A | EN 62368-1 and/or EN 60598-1 (luminaires), EN 62471 |
| **EMCD** 2014/30/EU | All electrical equipment (unless RED route) | Covered by RED on current inputs *(verify)* | Module A | EN IEC 55032 / EN 55035 (multimedia) or EN IEC 55015 + EN 61547 (lighting) or EN IEC 61000-6-1/-3 (generic) -- category to be justified |
| **RoHS** 2011/65/EU (+2015/863) | Electrical and electronic equipment | Applies | Module A | EN IEC 63000 technical documentation |
| **REACH** | Articles with SVHC > 0.1 % w/w | Applies (info duty Art. 33) | Supplier declarations | -- |
| **WEEE** 2012/19/EU | EEE | Applies (marking, registration per country) | Registration | EN 50419 marking |
| **Batteries Reg.** 2023/1542 | Battery included/removable | Not applicable (no battery) | Per regulation | -- |
| **GPSR** 2023/988 | Consumer products not fully covered by sector law | TBD | Risk assessment, traceability, labelling | -- |
| **ESPR/Ecodesign** | If delegated acts cover the product or its PSU | TBD | Per act | EU 2019/1782 etc. for external PSUs *(verify)* |
| **PPWR** | Packaging | TBD | -- | -- |
| **GDPR** | Personal data | TBD | -- | -- |

## 3. Derived consequences
Author's first assessment of 2026-11-03 from the design plan 02 and ADR-0002 to ADR-0008. It is guidance, not legal advice, and the owner has not reviewed it. Items marked *(verify)* need a check against the current legal text or an expert.

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

### Owner answers of 2026-11-03
- Market: EU only for now. Use: internal tool, designed so that it can be sold later.
- Distribution: start as open source; keep the professional-product route open. Which CRA role applies (open-source steward or manufacturer) depends on the first supply to others *(verify)*; the design plans for the manufacturer role.
- Support period: 5 years.
- Security: **secure boot and flash encryption are wanted.** This replaces "later with the door open" (round 2) for units that are sold. Consequence: ADR-0007 option C moves from "later" to a planned step. The author's working default is in ADR-0007 (new section "Owner input of 2026-11-03"): no irreversible chip step on the first prototypes until the procedure is proven on a sacrificial board; secure boot and flash encryption enabled before any unit leaves the owner's control. The owner must confirm that split.
- The 10 prototypes stay internal (owner, 2026-11-03). They are not placed on the market and are not supplied to others.
- Manufacturer (legal person and postal address) on the label: deferred by the owner. It must be decided before the first unit is supplied to anyone outside the owner's control.

### Open compliance questions for the owner (answered ones are in the list above)
1. ~~Prototypes stay internal.~~ Answered: yes.
2. Which markets: EU only, or also UK, US, Switzerland?
3. What support period will you commit to (CRA default is at least 5 years *(verify)*)?
4. Is the project published as open source with no commercial supply, or sold? This changes the CRA role (steward or manufacturer) *(verify)*. Since ADR-0013 (2026-11-04) the hardware and documents are source-available under CC BY-NC-SA 4.0 and the owner may sell commercial licences. The open-source steward path therefore cannot be assumed; plan for the manufacturer role (RV-005, needs a lawyer).
5. Do you accept that units placed on the market need secure boot and flash encryption, or a written justification?
6. Who will be the manufacturer (legal person and postal address) on the label for the first sold units? Deferred by the owner; needed before the first supply to others.

## 4. Review
Independent regulatory review recommended before the architecture gate and again before test-lab booking.
