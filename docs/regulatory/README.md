# Regulatory Compliance (EU market access / CE marking)

- **Status:** Draft
- **Disclaimer:** This is engineering process, **not legal advice**. Legal texts and harmonised-standard lists change;
  every statement here marked *(verify)* must be checked against the Official Journal / current official text, and a
  qualified compliance expert or test lab should confirm the final assessment before market placement.

Goal: the product is **designed for CE marking from day one** and the **technical documentation is built as a by-product of
the normal process**, not reconstructed at the end. The repository is the technical-file source of truth.

## 1. Workflow
1. **Regulatory Applicability Assessment** (`applicability.md`) -- done *before* system requirements, revisited at every
   architecture change (adding radio, battery, mains, cloud, new market...). Output: list of applicable legislation,
   conformity route (usually Module A internal production control; notified body if required), candidate standards.
2. **Regulatory requirements** become normal requirements (`SYS-/SW-/HW-/MECH-`) with a `Regulatory:` field citing the
   legal basis and standard clause. They are verified like any other requirement.
3. **Compliance matrix** (`compliance-matrix.md`): legal requirement / standard clause -> requirement ID -> TC / evidence.
   **Automated design-rule checks** (`automated-checks.md`, ADR-0022 Proposed) run in CI on every change: hardware rules on
   the KiCad files (ESD clamps on interfaces, test access, identification, part numbers, materials register, lifecycle),
   firmware rules (Kconfig attack surface, secrets, clang-tidy CERT, cppcheck MISRA, SBOM) and the matrix consistency check.
   They produce evidence of design rules; they never show conformity on their own.
4. **Pre-compliance** testing during design (EMC near-field/scan, ESD, safety checks, security testing); final accredited
   tests on a frozen design.
5. **Technical file** (`technical-file/`) kept current; reviewed at every gate. Checklist: `technical-file/INDEX.md`.
6. **Release gate:** technical file complete, compliance matrix 100 % covered, EU Declaration of Conformity drafted and
   signed by the responsible person, CE mark and labelling verified on the first article.
7. **Post-market:** vulnerability handling, incident reporting, corrective actions, support period, record retention
   (keep technical documentation and DoC for **10 years** after placing on the market *(verify per act; CRA: 10 years or support period if longer)*).

## 1a. Document map
| Question | Document |
|----------|----------|
| What is the product? | `technical-file/01-general/product-description.md` |
| Which rules apply, which do not, and why? Which route, which open decisions? | `applicability.md` (RAA-001) |
| What can go wrong and what controls it? | `technical-file/03-risk-and-safety/risk-assessment.md`, entries in `docs/risk/risk-register.md` |
| Which standards, which clauses matter? | `technical-file/04-standards-and-testing/standards-list.md` |
| Which tests, on what, in which order? | `technical-file/04-standards-and-testing/conformity-test-plan.md` |
| Which requirement and evidence covers each legal clause? | `compliance-matrix.md` |
| Which design rules does CI check? | `automated-checks.md` |
| Is the technical file complete? | `technical-file/INDEX.md` |

## 2. Legislation to assess (details in `applicability.md`)
CRA (Regulation (EU) 2024/2847), RED (2014/53/EU) incl. cybersecurity delegated act (EU) 2022/30, LVD (2014/35/EU),
EMCD (2014/30/EU), RoHS (2011/65/EU), REACH, WEEE (2012/19/EU), Batteries Regulation (EU) 2023/1542, GPSR (EU) 2023/988,
ESPR / Ecodesign (EU) 2024/1781 and product-specific ecodesign (e.g. external power supplies), Packaging (PPWR),
photobiological safety of LEDs (EN 62471), GDPR if personal data is processed.
Note: **RED and LVD/EMCD are mutually exclusive routes** -- radio equipment is assessed under RED *(verify)*.

## 3. Design-time rules (summary; full rules in the domain standards)
- Decide **radio / no radio, power source (SELV USB vs mains vs battery), connectivity/cloud, markets** early -- they drive the legal route.
- Prefer **pre-certified radio modules** and **certified external power supplies**: reduces scope but does not remove integrator obligations
  (system-level EMC, antenna integration, RED cybersecurity, CRA).
- EMC, safety and security are architecture-level concerns: they appear in ADRs, risk register and test plan, not as late fixes.
