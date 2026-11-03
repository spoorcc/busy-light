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
