# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Scope: the changelog covers the product as a whole (software, hardware, mechanical and user-visible documentation).
Hardware and mechanical revisions are named in the entries (for example "hardware rev A").

## [Unreleased]

### Added
- Project structure for Zephyr software (`sw/`), KiCad hardware (`hw/`) and FreeCAD mechanics (`mech/`).
- Engineering process: lifecycle with gates, Elephant-Goldfish planning, document control, verification strategy.
- Standards: C coding (CERT C and MISRA C subset), hardware and mechanical design-for-X, writing (ASD-STE100 based), diagrams as code.
- Regulatory scaffolding for EU market access: applicability assessment, compliance matrix, technical-file index.
- Traceability check (`scripts/check_traceability.py`), documentation style check (`scripts/check_docs_style.py`), diagram build (`scripts/build_diagrams.sh`).
- Stakeholder needs (NEED-001 to NEED-019) and draft system requirements (SYS-001 to SYS-031) for the first release:
  Jenkins status by push and by REST polling, 16-LED RGB ring, Wi-Fi provisioning with web interface, OTA update,
  user-uploaded CA certificates, per-unit password, 3D printed housing.
- Draft user documentation skeleton, `CONTRIBUTING.md` and `SECURITY.md`.
- Claude Code project instructions and skills (`CLAUDE.md`, `.claude/skills/`).
