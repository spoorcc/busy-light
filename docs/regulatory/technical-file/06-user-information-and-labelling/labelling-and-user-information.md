# Labelling and user information: item list

- **Status:** Draft (assistant, 2026-11-10; legal references *(verify)* against the official texts)
- **Requirement:** SYS-048 (Draft), verified by TC-048. Label area: MECH-006, TC-306.

Each row is one item to show on the unit, the packaging or in the user information. "Unit" means on the product itself; where the size or the nature of the product does not allow it, the acts allow the packaging or an accompanying document for some items *(verify per item)*. The housing is about 53 mm across, so the label must be planned with MECH-006.

## 1. On the unit (label on the base, MECH-006)

| # | Item | Legal basis *(verify)* | Fallback if no room |
|---|------|------------------------|---------------------|
| U1 | CE marking, at least 5 mm high, visible, legible, indelible | RED Art. 19, 20; Regulation (EC) 765/2008 Art. 30 | packaging and documents (RED Art. 19(1)) |
| U2 | Type, batch or serial number | RED Art. 10(6); GPSR Art. 9(5) | packaging or document |
| U3 | Manufacturer name, registered trade name or mark, and postal address (a single contact point) | RED Art. 10(7); GPSR Art. 9(6); CRA Art. 13(16) | packaging or document |
| U4 | Crossed-out wheeled bin, with the bar or a date of placing on the market | WEEE Art. 14(4); EN 50419 | packaging, manual and guarantee if the product is too small |
| U5 | Unit passphrase (ADR-0006) | not legal; product design | none: it must stay on the base (MECH-006) |
| U6 | "Prototype, not for sale or field use" for the internal prototypes only | applicability consequence 1 | -- |

## 2. Packaging

| # | Item | Legal basis *(verify)* |
|---|------|------------------------|
| P1 | Items U1 to U4 if they are not on the unit | as above |
| P2 | Restrictions on use in a member state, if any apply to the 2.4 GHz band | RED Art. 10(10) (none expected for 2.4 GHz Wi-Fi) |
| P3 | Packaging material marking | PPWR (EU) 2025/40 *(verify dates and scope)* |

## 3. User information (manual, quick start; language of the member state)

| # | Item | Legal basis *(verify)* |
|---|------|------------------------|
| M1 | Instructions and safety information in a language the user can understand | RED Art. 10(8); GPSR Art. 9(7) |
| M2 | Frequency band(s) and maximum radio-frequency power transmitted in each band | RED Art. 10(8)(a) |
| M3 | EU declaration of conformity, or the simplified declaration with the internet address of the full text | RED Art. 10(9) |
| M4 | Manufacturer contact and the single point of contact for vulnerability reports | CRA Annex II (1), (2) |
| M5 | Product identification (name, type, version) | CRA Annex II (3) |
| M6 | Intended purpose, security environment, essential functions and security properties | CRA Annex II (4) |
| M7 | Known foreseeable circumstances that can lead to cybersecurity risks | CRA Annex II (5) |
| M8 | Where the SBOM can be found, if the manufacturer makes it available to the user | CRA Annex II (9) |
| M9 | End date of the support period (at least month and year), stated at purchase | CRA Art. 13(19), Annex II (7) |
| M10 | How to install security updates; secure decommissioning and data removal (SYS-041); how to turn off automatic updates | CRA Annex II (8) |
| M11 | WEEE information: separate collection, take-back, the meaning of the symbol | WEEE Art. 14(2) |
| M12 | Supply: use a USB-C source that complies with EN IEC 62368-1 (or its successor); input rating 5 V, maximum current | EN IEC 62368-1 instructions *(verify)*; SYS-020 |
| M13 | Photobiological safety statement for the LED ring (if the assessment gives a risk group above exempt) | EN 62471 |
| M14 | Explanation of the certificate pin (ADR-0008) | applicability consequence 13 (not legal) |
| M15 | Not a toy; keep away from small children; small parts | GPSR Art. 9(7); risk assessment I3 |
| M16 | Not for safety signalling; the indication can be late or wrong | risk assessment I4 |
| M17 | Do not cover; indoor, dry use; highest ambient temperature | EN IEC 62368-1 instructions *(verify)*; risk assessment I2 |
| M18 | Flashing light notice and how to lower the brightness, if the assessment asks for it | risk assessment I5 |
| M19 | Mounting: only the supplied accessories and their limits | EN IEC 62368-1 clause 8.7 *(verify)*; risk assessment I6 |
| M20 | Minimum distance to the body, only if the exposure assessment needs one | SYS-052 |

## 4. Open items for the owner
1. Manufacturer legal person and postal address (deferred by the owner; needed before the first supply to anyone).
2. Which items fit on the 53 mm base, and which go to the packaging: a label drawing with MECH-006.
3. Language set for the EU market.
4. Simplified or full DoC in the box.

User-facing text for these items follows `docs/standards/writing.md` and is written with the `write-user-docs` skill when the manual is drafted. No user text is written here.
