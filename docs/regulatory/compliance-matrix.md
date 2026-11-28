# Compliance Matrix

- **Status:** Draft

Maps every applicable legal requirement or standard clause to a project requirement and evidence. No row may stay
uncovered at the release gate. Example row format:

| Legal / standard reference | Requirement (what must be met) | Project requirement ID | Verification (TC) | Evidence file | Status |
|----------------------------|--------------------------------|------------------------|-------------------|---------------|--------|
| CRA Annex I Part I (2)(a) | No known exploitable vulnerabilities at placing on market | SW-000 | TC-000 | `technical-file/05-cybersecurity/...` | Open |
| CRA Annex I Part II (1) | SBOM in machine-readable format | SW-000 | TC-000 | `technical-file/05-cybersecurity/sbom/` | Open |
| EMCD Annex I 1(a) | Emissions limited so radio/telecom equipment can operate as intended | HW-000 | TC-000 | test report | Open |
| RoHS Art. 4 | No restricted substances above limits | HW-000 | -- (supplier declarations) | `07-supplier-declarations/` | Open |

## Rows from the system design (author's first draft, 2026-11-03; none verified, no evidence exists yet)
Legal clause numbers marked *(verify)* are from memory and must be checked against the legal text. Requirements are Draft.

| Legal / standard reference | Requirement (what must be met) | Project requirement ID | Verification (TC) | Evidence file | Status |
|----------------------------|--------------------------------|------------------------|-------------------|---------------|--------|
| CRA Annex I Part I (2)(b) *(verify)* | Secure by default configuration, no default password | SYS-013, SYS-016, SYS-039 | TC-013 | -- | Open |
| CRA Annex I Part I (2)(c) *(verify)* | Security updates, automatic where applicable | SYS-029 | TC-029 | -- | Open |
| CRA Annex I Part I (2)(d) *(verify)* | Protection from unauthorised access (authentication, access control) | SYS-004, SYS-016, SYS-039 | TC-004, TC-016, TC-039 | -- | Open |
| CRA Annex I Part I (2)(e), (f) *(verify)* | Confidentiality and integrity of stored and transmitted data | SYS-034, SYS-035, SYS-013, SYS-043 | TC-034, TC-035, TC-043 | -- | Open (prototype flash not protected, RISK-013) |
| CRA Annex I Part I (2)(h)-(j) *(verify)* | Minimise attack surface, resilience, limit impact of an incident | SYS-005, SYS-012, SYS-027, SW-001, SW-002, SW-003 | TC-005, TC-012, TC-027, TC-101, TC-102, TC-103 | -- | Open |
| CRA Annex I Part II (1) *(verify)* | SBOM in machine-readable format | SYS-044 | TC-044 | `technical-file/05-cybersecurity/sbom/` | Open |
| CRA Annex I Part II (2)-(8) *(verify)* | Vulnerability handling, disclosure policy, contact, update distribution | SYS-045 | TC-045 | `technical-file/05-cybersecurity/` | Open |
| RED Art. 3(3)(d), (e), (f) / DA 2022/30 *(verify)* | Network protection, personal data and privacy, fraud protection | SYS-013, SYS-016, SYS-034, SYS-035 | TC-013, TC-034 | -- | Open |
| EN 18031-1 *(verify harmonisation)* | Internet-connected radio equipment: cyber essential requirements | SYS-004, SYS-013, SYS-016, SYS-029, SYS-034, SYS-035 | -- | gap analysis to write | Open |
| RED Art. 3(2) / EN 300 328 *(verify)* | Efficient use of the 2.4 GHz spectrum | SYS-038 | TC-038 (range only; radio test is separate) | module test report plus product test | Open |
| RED Art. 3(1)(a) / EN 62368-1, EN 62311 *(verify)* | Safety and RF exposure | SYS-020, SYS-028 | TC-020 | -- | Open |
| RED Art. 3(1)(b) / EN 301 489-1, -17 *(verify)* | EMC | none yet (HW requirement to write) | -- | test report | Open |
| EN 62471 | Photobiological safety of the LED ring | SYS-001, SYS-020 | TC-001, TC-020 | `technical-file/03-risk-and-safety/` | Open, assessment after spike 7.5 |
| RoHS Art. 4, REACH Art. 33, WEEE | Substances, SVHC information, marking | none yet | -- | `technical-file/07-supplier-declarations/` | Open |
| CRA Art. 13 / Annex II *(verify)* | User information incl. support period | SYS-024 (manual requirement missing) | -- | `technical-file/06-user-information-and-labelling/` | Open |

## Regulatory check of the P1 board changes (2026-11-18)
Check by the assistant (`regulatory-check`) of: the HW-017 damping link R22 (0 ohm 1206, new net `VBUS` for J1, TVS1 and U6,
in series before `VBUS_IC` and the current-limit switch U7); HW-010 trim T1 (one 27.7 k 0.1 % 0805 replaces 27.4 k + 301 ohm);
the planned one-sided assembly at JLCPCB Economic PCBA, 4 layers, HASL lead-free (plan 08; journals of 2026-11-17 and
2026-11-18). Engineering guidance, not legal advice. **Nothing is built or measured:** P1 is not placed or routed, no part is
bought, no bench test has run. P1 units are prototypes for the owner and are not placed on the market (`applicability.md`
consequence 1), so this is design-for-CE for the product that follows. The applicability inputs do not change, so
`applicability.md` is unchanged; the route stays RED, safety under Art. 3(1)(a) and EMC under Art. 3(1)(b) *(verify)*.

| Legal / standard reference | Requirement (what must be met) | Project requirement ID | Verification (TC) | Evidence file | Status |
|----------------------------|--------------------------------|------------------------|-------------------|---------------|--------|
| RED Art. 3(1)(a) / EN 62368-1 *(verify)* | Input path J1 - `VBUS` - R22 - `VBUS_IC` - U7 rated for the input current; a single fault before the limit (R22, C2, U5, supply-pin parts) is limited only by the external source (no fuse) | HW-003, HW-017 (both `Regulatory: none`, finding F1) | TC-203, TC-217 (board part) | Exists: per-net main-path rules in `pcb_rules.py` (0.6 mm, outer layers) with unit tests; netlist test `DampingLink`. Missing: R22 part and datasheet ([3] A, [10] mohm not shown); rating calculation of the new path in `hw/sim/`; split of `pcb_power_check.py` (F3); single-fault analysis of the segment before U7 | Open |
| RED Art. 3(1)(a) / EN 62368-1 *(verify)* | Hardware current limit keeps the HW-010 step windows after T1 (step 3 within 1366 to 1577 mA) | HW-010 | TC-210 | Exists: desk calculation `hw/kicad/spike-gate/sim/ilim_steps.py` and test `TrimT1` (step 3 1381.2 to 1566.7 mA; 1 V on ILIM assumed; temperature coefficient and ageing not modelled). Missing: bench; fault rows for an open or shorted ILIM resistor (F5); owner confirmation of T1 | Open (analysis only) |
| RED Art. 3(1)(a) / EN 62368-1 *(verify)* | Parts inside their ratings at hot-plug; part and surface temperatures in the closed housing | HW-010 crit. 4, HW-013, HW-017, ADR-0021, RISK-046 | TC-210 step 4, TC-213, TC-217 (bench) | Exists: ngspice analysis of the supply pins, `docs/verification/reports/analysis-supply-pin-surge.md`. Missing: every measurement; TC-213 procedure. One side puts U1, U7 and U8 on the LED side (thermal coupling changes, not assessed). T1 moves the step 3 maximum by 0.1 mA (no thermal effect) | Open |
| RED Art. 3(1)(b) / EN 301 489-1, -17; ESD to EN 61000-4-2 *(verify)* | ESD and EMC of the USB-C input: TVS1 and U6 at the connector, before the series element | none (EMC requirement missing, F2); HW-003 statement, HW-017 criterion | none for EMC; TC-217 checks the nets only | Exists: `DampingLink` test (TVS1 and U6 on `VBUS`). Missing: placement rules TVS1, U6, R22 to J1 (plan 08 step 5, not done; today a 9 mm group around U7); the P1 layout; any pre-compliance scan or ESD test. A ferrite at R22 (ADR-0021 option S3) changes the input filter and needs an EMC re-check | Open |
| RoHS Art. 4, REACH Art. 33 / EN IEC 63000 *(verify)* | No restricted substance above the limits in parts, bare PCB (HASL lead-free) and solder (paste; hand-soldered J1); SVHC information | HW-008 | TC-208 (no declaration step, F6) | Exists: owner choice of HASL lead-free (answer 10). Missing: every declaration (`technical-file/07-supplier-declarations/` is empty); shop declaration for finish and paste (shop site not read); R22 and seven part types have no MPN or LCSC number; 27.7 k part (Yageo RT0805BRD0727K7L) not collected | Open |
| RED Art. 3(2) *(verify)* | Module antenna keep-out kept | HW-005 | TC-205 | P1 baseline keeps the vendor keep-out (`PLACE_ANT_KEEPOUT=1`). Dropping it is one lever for the one-sided fit (journal 2026-11-18, DEV-004): if chosen, re-run this check | No change |
| CRA Annex I; RED Art. 3(3)(d)-(f) *(verify)* | -- | -- | -- | Not touched: pin map, firmware, interfaces and data unchanged (plan 08 A5); the CI order-file release is build tooling, not product software | No change |

Findings (severity for the product; the P1 prototype has no conformity duty):
- **F1 Medium.** HW-017 has `Regulatory: none`, but it sets the rating of a series part in the input path before the
  current limit, and keeps TVS1 and U6 on the connector side. Proposed field: "RED Art. 3(1)(a) / EN 62368-1 *(verify)*;
  RED Art. 3(1)(b) / EN 301 489-1 *(verify)*". HW-003 (input rating, ESD parts) also has `none`; SYS-020 has `TBD`.
  Not edited: the owner decides.
- **F2 Medium.** No requirement covers RED Art. 3(1)(b) EMC and ESD (open since 2026-11-03).
- **F3 Medium.** `pcb_power_check.py` still has one `VBUS_IC` case from J1 to U7 pin 1. J1 is now on `VBUS`, so the
  input-path drop for HW-003 and TC-217 cannot be produced until the case is split (plan 08 step 3; not in `aa4438a`).
- **F4 Medium.** R22 has no part: the HW-017 [3] A and [10] mohm are not shown, and common 1206 jumpers may be about 2 A
  (general knowledge, not verified). R22 sits before the limit with no fuse. P1 mitigation: lab supply first (TC-217, O7).
- **F5 Low.** The TC-210 fault table has no row for an open or shorted ILIM resistor (before T1 too); T1 makes it one part.
- **F6 Medium.** HW-008 cites RoHS, but neither its criteria nor TC-208 collect declarations. J1 hand soldering needs
  lead-free solder; the Economic PCBA paste type is not read.
- **F7 Low.** The order checklist (plan 08 O0 to O8) does not name the prototype label of `applicability.md` consequence 1.
- **F8 Info.** P1 order files go to CI releases, not `hw/fabrication/<rev>/` (answer 17): for a product, the release tag and
  manifest hashes are the design record of the technical file.
- **F9 Info.** HASL on U1 (0.4 mm pitch, plan 08 R2) has no RISK entry yet. A bridge on U1 is a fault at the gate input of
  the limit; the TC-210 rows "IC output shorted high and low" cover it in part.

Checks behind this section: the T1 and `DampingLink` tests were re-run on 2026-11-18 in the `kicad/kicad:10.0` image (7 passed).
Not run: bench, SPICE of the new path, power check, any EMC, ESD, thermal or RoHS evidence.

## Regulatory check of plan 08 revision 7: round 58.5 mm board, 36 LEDs, module at the edge (2026-11-28)
Inputs that change (`applicability.md`): light output (16 to 36 LEDs, 32 in two arcs and 4 under the centre button; the LED current budget stays, the per-channel current basis is unverified), antenna environment (module at the board edge, end LEDs 2.40 to 2.95 mm from the antenna strip, housing wall 1.90 mm from the module corners, DEV-004), housing size (53 to 65.5 mm). Not changed: radio, power source (USB-C 5 V, at most [500] mA), connectivity, data, battery, markets. The conformity route does not change. P1 stays a prototype for the owner (no conformity duty).
| Rule | Touched by | Requirement / TC | Evidence | Status |
|---|---|---|---|---|
| EN 62471 | 36 LEDs instead of 16, bright centre button under a translucent cap | SYS-001, SYS-020, HW-001 (amendment draft) | None for 36 LEDs; the consequence 7 text "16 small LEDs" is superseded; per-LED current is lower than before at the same budget but the basis is unverified | Open |
| RED Art. 3(2) / Art. 3(1)(b) *(verify)* | Antenna at the edge with LEDs, a 21.6 mm data link crossing the J1 gap and copper near the strip | HW-005 (amendment draft), SYS-038, TC-205 | Computed distances (plan 08 section S, pure Python, not KiCad); vendor keep-out lies off the board except a sliver; DEV-004 (courtyard kept, 4 LED overlaps); no range test, no EMC measurement | Open |
| RED Art. 3(1)(a) / EN 62368-1 *(verify)* | Full-white current of 36 LEDs against a 500 mA source | SYS-020, HW-010 | Paper budget only; no figure is verified (5 mA per channel for a WS2812C-2020 against 12 mA in the stored WS2812B-2020 footprint description, which would be about 1.3 A for 36 LEDs); the limit is firmware | Open |
| RED Art. 3(1)(a) / EN 62368-1 *(verify)* | Thermal and flammability of a larger printed housing with 36 LEDs | RISK-005 | None | Open |
| CRA, RED Art. 3(3)(d)-(f), GDPR, RoHS, REACH, WEEE | Board layout only | -- | Not touched: firmware, interfaces and data unchanged | No change |

Findings (the P1 prototype has no conformity duty):
- **F10 Medium.** The limit of the LED current is by firmware only. With 36 LEDs a firmware fault at full white could draw more than the source allows if the per-channel current is 12 mA; ADR-0004's review says a firmware-only limit is not a safety measure. The hardware limit of the TPS2553 (HW-010) bounds the source, not the LED frame. Owner decision pending (plan 08 gate (d)).
- **F11 Medium.** HW-005 says "no LED inside the keep-out"; the round board cannot meet that (end LEDs 2.40 to 2.95 mm from the strip). The amendment text is drafted (Draft); the range test and a pre-compliance scan decide. RISK-011 stays open.
- **F12 Low.** `applicability.md` consequence 7 ("16 small LEDs") and consequence 12 ("about 53 mm housing, label space is tight") are out of date: noted there.
- **F13 Low.** EMC: two long data links (21.6 mm across the J1 gap and about 20 mm to the centre) and the 800 kHz data line near the antenna strip: no pre-compliance plan yet (F2 stays open).
- **F14 Info.** No technical-file evidence is produced by this change; the computed geometry lives in plan 08 section S and RV-020 and is not filed under `technical-file/`.

Checks behind this section: reading of `applicability.md`, this matrix, ADR-0004, ADR-0027 and plan 08 section S. Not run: any measurement, simulation of the new geometry, EMC, thermal or photobiological assessment.
