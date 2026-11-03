---
name: regulatory-check
description: Check a change, plan, ADR or design against EU market-access obligations (CRA, RED/LVD/EMCD, RoHS, etc.) and keep the technical file and compliance matrix updated.
---

# Regulatory check

Read `docs/regulatory/README.md` and `applicability.md`. This is engineering guidance, not legal advice; mark uncertain
legal statements *(verify)*.

1. Does the change alter the applicability inputs (radio, power source, connectivity, data, battery, light output, markets)?
   If yes, update `applicability.md` and flag the user - conformity route may change.
2. Which legal/standard requirements does it touch? Ensure a requirement with a `Regulatory:` field exists and a row in
   `compliance-matrix.md`.
3. CRA/security: attack surface, secure defaults, authenticated + signed updates, no default credentials, SBOM updated
   (`west spdx` / CycloneDX), vulnerability handling, support period.
4. EMC/safety: layout/filter/ESD decisions, creepage/clearance, thermal, flammability, photobiological, labelling space.
5. Does it produce technical-file evidence (drawing, report, declaration)? Put/link it under `docs/regulatory/technical-file/`
   and update `INDEX.md` status.
6. List open compliance questions for the user; never state the product "is CE compliant" - state which evidence exists.
