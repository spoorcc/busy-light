# Regulatory Applicability Assessment (RAA-001)

- **Status:** Draft -- answers marked TBD must be provided by the product owner
- **Version:** 0.1   **Owner:**   **Last reviewed:**
- Re-run when: radio, battery, mains, cloud/app, data collection, new market, or new function is added.

## 1. Product definition inputs (drive everything below)
| Question | Answer | Why it matters |
|----------|--------|----------------|
| Intended use, user (consumer / professional / industrial), environment | TBD | GPSR, EMC environment class, ecodesign |
| Power source: USB-C 5 V (SELV) / external PSU / mains inside / battery | TBD | LVD scope (50-1000 V AC, 75-1500 V DC), PSU ecodesign, battery regulation |
| Wireless (Wi-Fi, BLE, 802.15.4, other radio)? | **Yes: Wi-Fi** (owner, 2026-11-03) | RED replaces LVD+EMCD; spectrum, cyber delegated act |
| Network connectivity / remote update / cloud or app | **Yes, including OTA firmware update (owner, 2026-11-03): LAN/Internet data sources, web UI on device** (owner, 2026-11-03). Update path and cloud use TBD | CRA, RED 3(3)(d-f), GDPR |
| Processes personal data? | TBD | GDPR, RED 3(3)(e) |
| Light output (LED power, visible to eyes) | **RGB LED ring** (owner, 2026-11-03). Power and optics TBD | EN 62471 photobiological safety |
| Target markets (EU only? UK, US, other) | TBD | UKCA, FCC/ISED etc. out of scope until stated |
| Sold commercially or purely community/open-source hardware? | TBD | "Placing on the market" triggers manufacturer duties; CRA open-source steward rules |
| Expected product lifetime | TBD | CRA support period (default >= 5 years unless shorter lifetime) |

## 2. Legislation matrix
| Legislation | Applies if | Status | Conformity route | Candidate standards *(verify harmonised status)* |
|-------------|-----------|--------|------------------|-----------------------------------------------|
| **CRA** (EU) 2024/2847 | Product with digital elements (software+hardware, direct/indirect data connection) | TBD (likely yes if any connectivity/update interface) | Self-assessment (default class) unless "important"/"critical" class; Annex VII tech doc | prEN/CEN-CENELEC CRA standards in development; EN 18031 series, ETSI EN 303 645, IEC 62443-4-x as guidance |
| **RED** 2014/53/EU (+ DA 2022/30) | Intentional radio emitter/receiver | TBD | Module A possible if harmonised standards applied; else notified body | EN 62368-1 (safety), EN 301 489-1/-17 (EMC), EN 300 328 (2.4 GHz), EN 62311/EN 50663 (EMF), EN 18031-1/-2/-3 (cyber) |
| **LVD** 2014/35/EU | Mains-powered 50-1000 V AC / 75-1500 V DC, no radio | TBD (likely **not** applicable if SELV-only) | Module A | EN 62368-1 and/or EN 60598-1 (luminaires), EN 62471 |
| **EMCD** 2014/30/EU | All electrical equipment (unless RED route) | TBD (applies unless RED) | Module A | EN IEC 55032 / EN 55035 (multimedia) or EN IEC 55015 + EN 61547 (lighting) or EN IEC 61000-6-1/-3 (generic) -- category to be justified |
| **RoHS** 2011/65/EU (+2015/863) | Electrical and electronic equipment | Applies | Module A | EN IEC 63000 technical documentation |
| **REACH** | Articles with SVHC > 0.1 % w/w | Applies (info duty Art. 33) | Supplier declarations | -- |
| **WEEE** 2012/19/EU | EEE | Applies (marking, registration per country) | Registration | EN 50419 marking |
| **Batteries Reg.** 2023/1542 | Battery included/removable | TBD | Per regulation | -- |
| **GPSR** 2023/988 | Consumer products not fully covered by sector law | TBD | Risk assessment, traceability, labelling | -- |
| **ESPR/Ecodesign** | If delegated acts cover the product or its PSU | TBD | Per act | EU 2019/1782 etc. for external PSUs *(verify)* |
| **PPWR** | Packaging | TBD | -- | -- |
| **GDPR** | Personal data | TBD | -- | -- |

## 3. Derived consequences
Fill after Section 1: conformity route per act, Notified Body needed (Y/N), required essential requirements,
standards list with versions, test lab plan, estimated test scope. Each consequence creates requirements/ADRs/risks.

## 4. Review
Independent regulatory review recommended before the architecture gate and again before test-lab booking.
