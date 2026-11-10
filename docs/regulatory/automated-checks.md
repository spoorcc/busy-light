# Automated compliance checks (rule catalogue)

- **Status:** Draft (written by the assistant, 2026-11-10; the policy choices are in ADR-0022, Proposed)
- **Scope:** checks that run in CI on every push and pull request and that produce evidence for the compliance matrix and the technical file.

The checks below are automated design rules. They do **not** show that the product conforms to any law or standard. They show that a listed design rule holds for the files checked, at the commit checked. Each finding of a `gate` rule fails CI unless a waiver names a `DEV-`, `RISK-` or `ADR-` record. A `report` rule lists open items as evidence and does not fail CI.

`scripts/check_compliance_matrix.py` checks that every rule ID in this table exists in the checker code with the same severity, and the reverse.

## 1. Rule catalogue

| Rule | Check | Severity | Basis (legal or standard reference, project rule) | Script | CI job |
|------|-------|----------|----------------------------------------------------|--------|--------|
| HWC-001 | Every signal and supply net of an external interface has an ESD or surge clamp, directly or through one series part | gate | RED Art. 3(1)(b) via EN 301 489-1 / EN 55035 (ESD to EN 61000-4-2) *(verify)*; design-hw.md 3, 4a; HW-003, HW-018 | `scripts/check_hw_compliance.py` | python-tools |
| HWC-002 | The clamp is within [10] mm of the connector | report | design-hw.md 4 (DFEMC) | same | python-tools |
| HWC-003 | Every power rail has a test point | gate | design-hw.md 1 (DFT); HW-006 | same | python-tools |
| HWC-004 | Reset and boot nets have test access | gate | design-hw.md 1; HW-006; SYS-023 | same | python-tools |
| HWC-005 | Board name and revision on the silkscreen | gate | design-hw.md 2, 4a; HW-020; traceability for RED Art. 10(6) and GPSR Art. 9 *(verify)* | same | python-tools |
| HWC-006 | Every BOM part has an MPN and a manufacturer | gate | EN IEC 63000 (technical documentation per part) *(verify)*; design-hw.md 5; HW-008, HW-019 | same | python-tools |
| HWC-007 | Every BOM MPN has a RoHS and REACH declaration in `hw/compliance/materials.yaml` | report | RoHS 2011/65/EU Art. 4, 7; REACH Art. 33; HW-019 | same | python-tools |
| HWC-008 | No BOM part is NRND, EOL or obsolete | gate | design-hw.md 5; CRA support period (SYS-045) | same | python-tools |
| HWC-009 | Inventory of debug and programming access paths | report | CRA Annex I Part I (2)(j) attack surface *(verify)*; SYS-043 | same | python-tools |
| SWC-001 | No forbidden Kconfig option (shell, debugger stub, test RNG, network log backend...) in a product config or built `.config` | gate | CRA Annex I Part I (2)(j) *(verify)*; SW-011 | `scripts/check_kconfig_policy.py` | python-tools, software |
| SWC-002 | Hardening options set (stack protection, canaries, fortify, watchdog, MCUboot) | report | CRA Annex I Part I (2)(k) *(verify)*; SW-011 | same | python-tools, software |
| SWC-003 | No hard-coded credentials or private keys in tracked files | gate | CRA Annex I Part I (2)(b), (d) *(verify)*; EN 18031-1, ETSI EN 303 645 5.1 *(verify)*; SYS-013 | `scripts/check_secrets.py` | python-tools |
| SWC-004 | GitHub Actions pinned to a commit SHA | gate | CRA Annex I Part I (1), Part II (1) *(verify)*; ADR-0012 item 4 | `scripts/check_ci_supply_chain.py` | python-tools |
| SWC-005 | Downloaded tools are checked with `sha256sum -c`; no download piped into a shell | gate | same as SWC-004 | same | python-tools |
| SWC-006 | clang-tidy (CERT C, bugprone, clang-analyzer) clean on project C code | gate | coding-sw.md 1, 4; CRA Annex I Part I (2)(a) *(verify)*; SW-012 | `scripts/ci_sw_static.sh` (`sw/.clang-tidy`) | software |
| SWC-007 | cppcheck with the MISRA addon: no Mandatory or Required finding, no cppcheck error or warning. Covers the project C files that build without Zephyr headers (the pure logic of plan 07); for files that need Zephyr it prints NOT RUN, because cppcheck 2.x cannot preprocess Zephyr's `IS_ENABLED()` | gate | coding-sw.md 1, 4; ADR-0001; SW-012 | `scripts/ci_sw_static.sh`, `scripts/check_sw_static.py` | software |
| SWC-008 | Every suppression (`NOLINT`, `cppcheck-suppress`, pragma) names a `DEV-nnn` | gate | coding-sw.md 5; deviations.md | `scripts/check_sw_static.py` | python-tools |
| SWC-009 | An SPDX SBOM is made from the build; packages without a licence are listed | report | CRA Annex I Part II (1) *(verify)*; SYS-044 | `scripts/ci_sw_static.sh`, `scripts/check_sbom.py` | software |
| DOC-001 | Compliance matrix IDs exist; every requirement with a `Regulatory:` reference has a matrix row; this catalogue matches the code | gate | Regulatory README 1 (matrix 100 % covered at release) | `scripts/check_compliance_matrix.py` | python-tools |

Existing checks that also give regulatory evidence (not repeated above): strict ERC and DRC with the fabricator rules (`scripts/ci_hw.sh`, HW-009), part evidence schema (`scripts/check_part_evidence.py`, HW-012), licence map and REUSE (`reuse lint`, `scripts/check_license_map.py`, CRA SBOM licence data), traceability (`scripts/check_traceability.py`), user-documentation style (`scripts/check_docs_style.py`, CRA Annex II and RED Art. 10(8) user information).

## 2. Evidence produced

| Output | Where | Retention |
|--------|-------|-----------|
| `hw-compliance.json` (all HWC findings, waivers, rule list) | CI artefact `compliance-reports` | attach to the release record (`docs/verification/releases/`) for each baseline |
| `cppcheck-misra.xml`, `clang-tidy.txt` | CI artefact `sw-static` | same |
| `*.spdx` from `west spdx` | CI artefact `sw-static`; release: `technical-file/05-cybersecurity/sbom/` | same; 10 years after the last unit is placed on the market *(verify)* |

## 3. What the automation does not show

- That the board meets EN 55032/55035 or EN 301 489 limits: only a test in a lab shows that. HWC-001 shows that a clamp exists, not that it is good enough.
- RoHS or REACH conformity: HWC-007 only shows which declarations are on file.
- MISRA compliance: cppcheck covers part of the rules. A compliance report needs the rule list, the tool coverage, the deviations and a review (coding-sw.md 4).
- CRA conformity: the checks cover part of Annex I. The cyber risk assessment, the vulnerability handling and the support period are process evidence (`technical-file/05-cybersecurity/cra-annex-i-mapping.md`).
- Physical labelling, user information content and photobiological safety: inspection and analysis items (TC-048, EN 62471 assessment).
