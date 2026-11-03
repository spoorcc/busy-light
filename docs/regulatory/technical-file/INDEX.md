# Technical File (Technical Documentation) -- Index and Completeness Checklist

- **Status:** Draft   **Product / model / revision:**   **Baseline tag:**

The technical file is assembled from controlled documents in this repository (link, don't duplicate). Retain for **10 years**
after placing on the market *(verify per act; CRA: longer if support period is longer)*. Record the baseline (git tag) per release.

| # | Content (typical across CRA Annex VII, RED/LVD/EMCD, RoHS) | Source in repo | Status |
|---|------------------------------------------------------------|----------------|--------|
| 01 | General description: product, intended use, variants, versions, photos, markets | `01-general/` | Open |
| 01 | Applicability assessment, conformity route, responsible economic operator | `../applicability.md` | Open |
| 02 | Design & manufacturing drawings, schematics, PCB layout, BOM, assembly drawings | `hw/fabrication/<rev>/`, `mech/exports/<rev>/` | Open |
| 02 | Architecture, interface and software design descriptions; ADRs | `docs/architecture/`, `docs/decisions/` | Open |
| 02 | Requirements and traceability (incl. regulatory requirements) | `docs/requirements/`, `../compliance-matrix.md` | Open |
| 03 | Risk assessment: safety/hazards (LVD/GPSR), EMC, **cybersecurity risk assessment (CRA)** | `docs/risk/` | Open |
| 03 | Photobiological (EN 62471), thermal, fire/flammability, mechanical safety analyses | `03-risk-and-safety/` | Open |
| 04 | List of standards/specifications applied (with versions, full/partial application) | `04-standards-and-testing/standards-list.md` | Open |
| 04 | Test reports: EMC, safety, radio, EMF, environmental; pre-compliance and accredited | `04-standards-and-testing/`, `docs/verification/reports/` | Open |
| 05 | **SBOM** (machine-readable, e.g. SPDX/CycloneDX) per release | `05-cybersecurity/sbom/` | Open |
| 05 | Vulnerability handling process + coordinated disclosure policy + contact; `security.txt` | `05-cybersecurity/` | Open |
| 05 | Security update mechanism & support period; secure-by-default configuration; update test evidence | `05-cybersecurity/` (key management: `05-cybersecurity/key-management.md`, Draft) | Open |
| 05 | Evidence of conformity with CRA Annex I essential requirements; reporting procedure to CSIRT/ENISA | `05-cybersecurity/` | Open |
| 06 | User instructions & safety information (Annex II CRA etc.), languages, installation, end-of-support date | `06-user-information-and-labelling/` | Open |
| 06 | Labelling: type/batch/serial, manufacturer name+postal address, CE mark, WEEE symbol, ratings; label drawing | `06-user-information-and-labelling/` | Open |
| 07 | Supplier declarations: RoHS/REACH (SVHC), material declarations, component datasheets, pre-certified module certificates & grants | `07-supplier-declarations/` | Open |
| 08 | Production controls ensuring conformity (internal production control), traceability, production test, change control | `08-production-and-quality/` | Open |
| 08 | Records of corrective actions, field issues, vulnerability reports | `08-production-and-quality/` | Open |
| 09 | EU Declaration of Conformity (per Decision 768/2008/EC annex III format), signed | `09-declaration-of-conformity/` | Open |

## Completeness gate
Before CE marking: every row `Complete`, each evidence file has a version/date/revision-under-test, and the traceability
check and compliance matrix show no gaps. Changes after release: assess whether re-testing/re-declaration is required (change impact record).
