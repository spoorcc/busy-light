# RoHS, REACH and WEEE: approach and status

- **Status:** Draft (assistant, 2026-11-10; legal references *(verify)*)
- **Requirement:** HW-019 (Draft), verified by TC-219; automated rules HWC-006, HWC-007, HWC-008.

## 1. Obligations in short *(verify against the texts)*
- **RoHS** 2011/65/EU with (EU) 2015/863: ten restricted substances in homogeneous materials (lead, mercury, cadmium, hexavalent chromium, PBB, PBDE at 0.1 %; cadmium at 0.01 %; DEHP, BBP, DBP, DIBP at 0.1 %), exemptions in Annexes III and IV. The manufacturer draws up technical documentation (Art. 7) and the EU declaration of conformity; CE marking covers RoHS too. EN IEC 63000 describes the documentation: a risk-based assessment of the parts and suppliers, and supplier declarations, material declarations or test results as evidence.
- **REACH** (EC) 1907/2006 Art. 33: a supplier of an article with a Candidate List substance (SVHC) above 0.1 % w/w gives the recipient enough information for safe use, at least the substance name; the consumer can ask for it (45 days). Art. 7(2) notification and the SCIP database notification under the Waste Framework Directive apply above 0.1 % too *(verify)*.
- **WEEE** 2012/19/EU: the product is electrical and electronic equipment in the small-equipment category *(verify: category 5 small equipment or 6 small IT)*. Registration with the national register in each member state where it is sold, the crossed-out bin marking (EN 50419) and take-back financing.

## 2. Method
1. The schematic carries `MPN` and `Manufacturer` for each BOM part (HWC-006).
2. `hw/compliance/materials.yaml` holds one entry per MPN: `rohs`, `reach`, `lifecycle`, `source`, `checked`, and for a declaration the file name, its SHA-256 and the Candidate List date it refers to.
3. Only a manufacturer document counts as `declared`. A distributor page is `distributor-claim`: it shows a likely status, not evidence.
4. Declarations are kept in this folder, or outside the repository if their licence forbids it (ADR-0015 item 8), with the hash in the register.
5. Before each release: re-check SVHC statements against the current Candidate List (it is updated twice a year *(verify)*), and lifecycle status.
6. The CI report (`hw-compliance.json`) lists every open part. The release gate needs zero open items for the board revision that is placed on the market.

## 3. Status on 2026-11-10 (spike board)
- 33 part numbers in the register (30 from the stored schematic, 3 from `sourcing.py` that are not yet in the stored schematic; DEV-007).
- Declarations on file: 0. RoHS status: unknown for all. REACH status: unknown for all.
- Lifecycle: TUSB321RWBR marked NRND by a shop listing (not checked at TI); all others unknown.
- The 10 prototypes are not placed on the market (applicability, owner answer 2026-11-03), so no declaration is needed for them. The work is needed before the first unit is supplied.

## 4. Open items
1. Collect manufacturer RoHS and REACH declarations (start with the ICs and the module: Espressif, TI, STMicroelectronics, Nexperia, Worldsemi; then the passives).
2. Check the TUSB321 lifecycle at TI; if NRND is confirmed, record a RISK entry or choose a replacement (ADR-0016 names the part).
3. WEEE category and the national registers: decide when the first market is known.
