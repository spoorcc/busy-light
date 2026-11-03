# Verification Strategy

Principle: **nothing is "done" without executable or recorded evidence.** Prefer automation; where a check cannot be
automated, record the procedure and result.

## Software -- every code change ships with tests
- Every function/module/behaviour added or changed has an accompanying test **in the same PR** (no exceptions without `DEV-nnn`).
  Bug fixes start with a failing regression test.
- Each test names the requirement it verifies (`TC-nnn` -> `SW-nnn`; test source cites the `TC-` ID).
- Levels: unit (Zephyr ztest, `native_sim`), integration (`native_sim`/QEMU/Renode with emulated peripherals),
  system/HIL on real board. Hardware abstraction (devicetree + emulated drivers / fakes) is a design requirement so logic is testable without hardware.
- Run with `west twister -T sw/app/tests` (and board-targeted runs for HIL). Tests must be deterministic and run in CI.
- Coverage: collect gcov on `native_sim`; targets are set per requirement criticality (default: statement >= 90 %, branch >= 80 %
  for project code); gaps explained, not ignored. Add sanitizers (ASan/UBSan) and static analysis (`docs/standards/coding-sw.md`).
- Negative testing: invalid input, boundary values, fault injection (timeouts, driver errors), power-fail/reset.
- Test code is held to review standards too; test results are retained as artefacts.

## Hardware -- verify by simulation and analysis *before* fabrication, by measurement after
Use every technique that is feasible and proportionate; each result is stored in `hw/sim/` and referenced by a `TC-nnn`.

| Concern | Technique | Tooling (open-source first) |
|---------|-----------|-----------------------------|
| Electrical correctness | ERC, netlist/BOM checks, pin-mux & voltage-level compatibility script | KiCad ERC (`kicad-cli sch erc`), Python in `hw/sim/scripts` |
| Layout rules / manufacturability | DRC, DFM checks against fab rules | `kicad-cli pcb drc` |
| Analog/power behaviour (LED drive, regulators, protection, filters, level shifters) | SPICE transient/AC/DC sweeps | ngspice (KiCad simulator), models in `hw/sim/spice` |
| Component tolerance & temperature | Worst-case and Monte-Carlo analysis, derating calculation | ngspice `.step`/Monte Carlo, Python |
| Power budget & battery/supply | Budget script with margins per mode | Python (`hw/sim/scripts`) |
| Thermal | Analytical calcs; FEM/CFD where justified | Python, FreeCAD FEM (CalculiX), KiCad thermal estimates |
| Signal / power integrity, EMC | Rule-based review, simple transmission-line/PDN calcs, pre-compliance plan | Python; near-field probing after build |
| Digital interfaces / firmware-hardware interaction | Co-simulation of firmware against emulated peripherals; timing analysis | Renode / native_sim fakes |
| Reliability | Derating, FMEA, MTBF estimate | `docs/risk/` |
| Built boards | Bring-up procedure, first-article inspection, measurements vs simulation (correlation recorded), production test | `docs/verification/reports/` |

If simulation is not possible for a requirement, the `Verified by` TC states the alternative (analysis, inspection, bench test)
and why. Simulation models have provenance (source, version) and assumptions listed; unvalidated models are flagged.

## Mechanical
- Interference/clearance check against the KiCad STEP each revision (scripted FreeCAD headless where possible).
- Tolerance stack-up (worst-case and RSS) in `mech/analysis/` as reproducible scripts or spreadsheets.
- FEM for structural/thermal where risk justifies (FreeCAD FEM); test coupons/prototype fit checks for printed parts;
  optical measurement of the light path; recorded dimensional inspection of first article.

## Evidence
Each report: requirement/TC IDs, revision under test (git describe / board rev), tool versions, setup, raw data or logs, pass/fail, author, date.
Stored in `docs/verification/reports/` (large raw files may live in CI artefacts with hashes recorded).
