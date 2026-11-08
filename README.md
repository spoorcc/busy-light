<div align="center">

# busy-light

**A Wi-Fi status ring for desks, doors and build rooms.**
Sixteen RGB LEDs that show your Jenkins build status or any other level, with no app and no cloud account.

[![CI](https://github.com/spoorcc/busy-light/actions/workflows/ci.yml/badge.svg)](https://github.com/spoorcc/busy-light/actions/workflows/ci.yml)
![Status: design phase](https://img.shields.io/badge/status-design%20phase-orange)
![Zephyr 4.5.0](https://img.shields.io/badge/Zephyr-4.5.0-7e57c2?logo=zephyrproject&logoColor=white)
![ESP32-C3](https://img.shields.io/badge/MCU-ESP32--C3-e7352c?logo=espressif&logoColor=white)
![KiCad 10](https://img.shields.io/badge/KiCad-10-314cb0?logo=kicad&logoColor=white)
![FreeCAD 1.1](https://img.shields.io/badge/FreeCAD-1.1-ae1c28?logo=freecad&logoColor=white)
![Market: EU](https://img.shields.io/badge/market-EU%20(not%20certified)-003399)
[![Code: Apache-2.0](https://img.shields.io/badge/code-Apache--2.0-blue)](LICENSES/Apache-2.0.txt)
[![Docs, hardware, mechanics: CC BY-NC-SA 4.0](https://img.shields.io/badge/docs%20%C2%B7%20hardware%20%C2%B7%20mechanics-CC%20BY--NC--SA%204.0-lightgrey)](LICENSES/CC-BY-NC-SA-4.0.txt)
[![Issues and reviews welcome](https://img.shields.io/badge/issues%20%26%20reviews-welcome-brightgreen)](CONTRIBUTING.md)

[Documentation](docs/README.md) ·
[Requirements](docs/requirements/needs.md) ·
[Architecture decisions](docs/decisions/) ·
[Roadmap](#roadmap) ·
[Contributing](CONTRIBUTING.md) ·
[Security](SECURITY.md)

</div>

---

> **Honest status:** busy-light is in the **design phase**. There is no released firmware, no manufactured
> hardware and no approved requirement set yet. Everything below describes the **intended** product and
> what the project has already proved with desk studies, PC prototypes and CAD experiments.
> Nothing here is certified, and no conformity with any regulation is claimed.

## What is it?

busy-light is a small round device with a ring of 16 individually controllable RGB LEDs. It joins your Wi-Fi,
listens to your build server or fetches its status over REST, and turns that into a colour or a level you can see
from across the room.

The first use case is a **Jenkins build light**: green, red, unstable, running, aborted. The second is a
**level gauge**: the ring fills like a dial from 0 to 100 percent for queue length, test pass rate, or any number
a REST endpoint can give.

## Why another status light?

Most status lights need a vendor app, a cloud account or a USB cable to a PC. busy-light is designed around a
different set of goals.

| Goal | What it means |
|------|---------------|
| **Works on a shared, untrusted network** | Per-unit access point password, encrypted provisioning, authenticated and signed updates. |
| **No app, no cloud** | Set-up and configuration through a web page served by the device itself. |
| **Small enough to put anywhere** | About 53 mm across, powered over USB-C. |
| **Cheap to build** | Target assembled board cost of EUR 10 to 20 with a prototype shop. |
| **Source-available and reproducible** | Software, hardware and mechanics are all in this repository, with generated files and checks that anyone can rerun. Code is Apache-2.0. Documentation, hardware and mechanics are free to copy and build for non-commercial use. |
| **Built like a product** | Requirements, decisions, risks and tests are traced from the first line, with EU market access (CE) in mind from day one. |

## Planned features

These are **planned**, taken from the draft requirements in [`docs/requirements/`](docs/requirements/). None is released.

- **16-LED RGB ring** with status colours, animations and a level (gauge) mode
- **Jenkins first:** receive pushed build events, or poll the Jenkins REST API
- **Mapping without code:** pick a value in the JSON answer, map it to a state or scale it to a level
- **Own access point for set-up:** the device creates a Wi-Fi network with a unique password printed on a label, you open a web page and enter your Wi-Fi details
- **Web interface** served by the device, no app to install
- **WPA2 and WPA2-Enterprise** networks, with user-loadable certificates
- **Over-the-air updates** that are signed and can be checked before they run
- **USB-C power** with safe handling of the available current: a hardware current limit and a firmware limiter on LED brightness
- **Secure boot and flash encryption** (planned for production units)

```mermaid
flowchart LR
    J[Jenkins or other REST source] -- push or poll --> D((busy-light))
    P[Phone or laptop] -- set-up page over the device's own Wi-Fi --> D
    D --> R[16-LED ring]
    U[USB-C] -- power --> D
```

## What exists today

The project has done a lot of thinking and some experiments, but **no product code or hardware yet**.

| Area | State |
|------|-------|
| Requirements | Written for needs, system, software, hardware and mechanics (101 entries). **18 are approved by the owner** (all 9 mechanical, 5 software, 3 hardware including the current-limit gate HW-010, 1 system); the rest are drafts. |
| Architecture decisions | 19 decision records. **17 are accepted** by the owner (ADR-0011, the housing, only for the prototype); 2 are superseded. Recent decisions: first antenna layout (ADR-0003), annular back bayonet (ADR-0014), AND gate for the fault readback (ADR-0018) and a standard-package regulator with a firmware current limit (ADR-0019). |
| Risk register | Open. Each risk has a mitigation and a verification link. |
| Reviews | Independent "goldfish" reviews recorded for the system design, the first spike plan and the hardware flow decision ([`docs/reviews/`](docs/reviews/)). |
| Software | Zephyr 4.5.0 workspace pinned. The input-current gate logic (`sw/app/src/gate.c`) has **20 host unit tests that pass** on `native_sim`; nothing runs on a board. A mapping extractor and an LED current limiter were tried as PC-only prototypes (results in the reports, code not in `sw/`). |
| Hardware | A scripted KiCad flow produces a **spike** full-board schematic (USB-C input, current-limit gate, hold-off, AND-gate fault readback, supply-pin surge protection, ESP32-C3 module, 16 LEDs) and a 4-layer board on the mechanical-spike outline, routed with Freerouting. The board is routed with **0 unconnected items** and passes the strict check apart from tolerated antenna and stand-in findings, but nothing is reviewed. Part datasheet evidence is recorded in a schema, **none verified**. The surge on the 5 V side is still to be **measured** on a built board. **No product schematic or layout yet.** |
| Mechanics | FreeCAD scripts generate the housing (base with USB-C window, button hole, PCB posts and snap hooks, annular back bayonet with lock lips and a mating accessory ring, lid with snap bumps), print coupons for the diffuser and the bayonet, and a tolerance check with tests. **Nothing printed or fit-tested**; the tolerances are assumptions. |
| Regulatory | Applicability analysis and compliance matrix started. No evidence collected, no declaration made. |

The reports behind these lines are in [`docs/verification/reports/`](docs/verification/reports/).

### Gallery

All images are generated from text sources or tool exports; none is hand-drawn. None shows a product design: they show the proposal and the experiments.

**Proposed software blocks** (PlantUML source in [`docs/diagrams/plantuml/`](docs/diagrams/plantuml/), draft architecture):

![Proposed software blocks: Jenkins and a phone browser talk to the device; inside the device source adapters, mapping, display engine, network manager, web server and settings store](docs/diagrams/generated/plantuml/arch-system-blocks.svg)

**Hardware spike (KiCad 10, generated by script, not reviewed, not the product design):**

| Schematic (spike), part 1: USB-C input, CC detection, current-step gate, hold-off, regulator |
|---|
| <a href="docs/verification/reports/images/spike-schematic-gate-power.png"><img src="docs/verification/reports/images/spike-schematic-gate-power.png" alt="Left part of the spike schematic: USB-C receptacle, TUSB321, 74LVC1G gates, two TMUX1101 switches for the current-limit steps, TPS2553 current limit, TPS3840 hold-off timer, 3.3 V regulator box, and the supply-pin protection (resistor, 100 nF, 5.1 V zener)" width="900"></a> |

| Schematic (spike), part 2: ESP32-C3 module, button, AND-gate fault readback, LED buffer, 16 LEDs |
|---|
| <a href="docs/verification/reports/images/spike-schematic-mcu-leds.png"><img src="docs/verification/reports/images/spike-schematic-mcu-leds.png" alt="Lower part of the spike schematic: ESP32-C3-MINI-1 module, button, the AND gate that combines HOLD_OK and FAULT_N, the LED data buffer and a chain of 16 LEDs in two rows of eight" width="900"></a> |
| Two crops of one single-sheet schematic, exported with `kicad-cli`; click an image for full size. Some labels overlap (for example C1 and C1B) and part values are open (`tbd`). The schematic is a spike under ADR-0012 (Proposed), not reviewed and not approved. |

| Board, 4 layers, top view (3D render) | Board, all copper layers and silkscreen |
|---|---|
| <img src="docs/verification/reports/images/spike-pcb-4layer-top3d.png" alt="Round green board with a ring of 16 square LED footprints, an ESP32 module, a button and a USB-C receptacle tab on the right" width="420"> | <img src="docs/verification/reports/images/spike-pcb-4layer-layers.png" alt="Copper layers of the round board in colour: ground pours, tracks and vias" width="420"> |
| Generated by script from the schematic netlist on the outline of the mechanical spike. The 16 LED cells (one 2020 LED with its capacitor) are placed and routed as a symmetric ring by script; the rest is routed with Freerouting v2.5.0 (fine rules, 0.1 mm tracks, see ADR-0020, Proposed). | One run (ring14 run 9), picked as the best of 12 (routing is not deterministic); the board is stored in [`hw/kicad/spike-gate/board/`](hw/kicad/spike-gate/board/). **0 unconnected items, 0 hard findings.** The strict check lists 11 findings, all in the classes that the waiver list tolerates: 8 courtyard overlaps and 1 item inside the rule area (ESP32 antenna keep-out), 2 symbol mismatches (C3, C4). Power paths (analyst assumptions of 1.5, 1.0 and 0.5 A): 13.5, 18.0 and 22.7 mV drop. The fabricator-minimum check passes for the JLCPCB numbers of ADR-0020 (Proposed), with the via ring at the 0.15 mm minimum. Not run: antenna/RF, thermal, full fab review, bench. A spike result, **not** a reviewed board. |

Regenerate with [`hw/kicad/spike-gate/render_readme_images.sh`](hw/kicad/spike-gate/render_readme_images.sh). The 3D render has no component models for most parts and is not a fit check. See [`spike-pcb-placement-routing.md`](docs/verification/reports/spike-pcb-placement-routing.md).

| Housing model (FreeCAD script), exploded | Back of the base |
|---|---|
| <img src="docs/verification/reports/images/housing-model-exploded.png" alt="Exploded view of the generated housing model: a flat round lid, the base cup with a USB-C window, a button hole, PCB posts and hooks, and below it the accessory ring" width="480"> | <img src="docs/verification/reports/images/housing-model-back.png" alt="Back of the base with the annular bayonet groove: three entry sectors, lock lips and stops, and the open centre for the label" width="420"> |
| Generated by [`mech/freecad/housing.py`](mech/freecad/housing.py) and [`accessory.py`](mech/freecad/accessory.py), drawn by [`mech/render_readme_images.sh`](mech/render_readme_images.sh). Parts: lid with snap bumps, base with USB-C window, button hole (working values, the switch is not chosen), posts, snap hooks and the bayonet groove with lock lips, stop and detent; the orange ring is the accessory with three T-lugs. The model passes its own checks (valid solids, no overlap, board fits, the lock holds and stops). **Nothing is printed or fit-tested**; the release tab is not modelled. Results: [`mech-housing-first-model.md`](docs/verification/reports/mech-housing-first-model.md). |

## Roadmap

| Phase | Goal | State |
|-------|------|-------|
| **0. Foundation** | Process, requirements, decisions, risks, regulatory outline, CI | in progress |
| **1. Spikes** | Prove the risky parts on a dev kit: Wi-Fi access point, web page, LED drive, power budget, secure boot | planned, waiting for approval of the spike plan |
| **2. Prototype** | 10 internal prototypes: schematic, board, housing, first firmware | planned |
| **3. Verify** | Test cases against approved requirements, pre-compliance tests | planned |
| **4. Release candidate** | Signed firmware, documentation, technical file | planned |

Dates are deliberately not given. Phases start when the previous one has evidence.

## How the project works

busy-light is run like a small regulated company, because the goal is a product that could be sold.

- **Specification before implementation.** No firmware, board or housing change without an approved requirement it traces to.
- **Decisions are recorded.** Costly choices get an architecture decision record with real alternatives, weighted criteria and a critical review.
- **Evidence over claims.** A result is only reported with its test or analysis. What was not run is stated.
- **Everything is code.** Diagrams, hardware (KiCad files generated from scripts) and mechanics (FreeCAD from scripts) are text sources with checks in CI.
- **Documentation is part of the product.** User documentation follows a controlled-language standard (ASD-STE100 principles).
- **EU market access from the start.** Cyber Resilience Act, Radio Equipment Directive, RoHS and friends are tracked in [`docs/regulatory/`](docs/regulatory/README.md). The project states which evidence exists and never states that the product "is compliant".

The full process is in [`docs/process/README.md`](docs/process/README.md).

## Repository layout

| Path | Contents |
|------|----------|
| [`sw/`](sw/) | Zephyr application, west manifest, tests |
| [`hw/`](hw/) | KiCad project, simulation, fabrication outputs, datasheets |
| [`mech/`](mech/) | FreeCAD models, exports, drawings, analysis |
| [`docs/`](docs/README.md) | Process, requirements, architecture, decisions, risk, verification, regulatory, user docs, standards |
| [`scripts/`](scripts/) | Traceability, documentation and CI check scripts |

## Getting started (developers)

**Software** (needs the Zephyr SDK and `west`):

```sh
west init -l sw
west update
west build -b <board> sw/app
```

**Repository checks:**

```sh
python3 -m venv --system-site-packages .venv
.venv/bin/pip install --group dev --group hw
python3 -I scripts/check_traceability.py     # requirements, decisions, risks and tests are linked
python3 -I scripts/check_docs_style.py       # user documentation style
scripts/build_diagrams.sh --check            # diagrams are up to date
.venv/bin/ruff check . && .venv/bin/pytest   # Python tooling
```

**Hardware and mechanical checks** run in CI through `scripts/ci_hw.sh` (KiCad 10) and `scripts/ci_mech.sh` (FreeCAD).
They report **NOT RUN** until product sources exist, so a skipped check is never mistaken for a pass.

## Contributing

Ideas, reviews and critical questions are welcome. Pull requests with code or documents are not accepted until the contributor terms have had a legal check. Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) first.
A good first contribution is to challenge a draft requirement or a proposed decision in
[`docs/decisions/`](docs/decisions/): write down the alternative you would pick and why.

## Security

busy-light is designed for shared networks. To report a vulnerability, follow [`SECURITY.md`](SECURITY.md).
The planned vulnerability handling and key management are drafts under
[`docs/regulatory/technical-file/05-cybersecurity/`](docs/regulatory/technical-file/05-cybersecurity).

## License

| Part | Licence |
|------|---------|
| Code (firmware, scripts, generators, CI, assistant instructions in `.claude/`) | [Apache-2.0](LICENSES/Apache-2.0.txt) |
| Documentation, hardware, mechanics, images | [CC BY-NC-SA 4.0](LICENSES/CC-BY-NC-SA-4.0.txt) |
| Commercial use of the hardware, mechanics or documentation | Separate licence from the owner |

You may copy, study and build from the hardware and mechanical files for non-commercial purposes. Using a unit that you
bought is not restricted. The non-commercial parts are **source-available, not open source hardware**.
Details and the path-by-path map are in [`LICENSE.md`](LICENSE.md) and [`REUSE.toml`](REUSE.toml);
the decision is [ADR-0015](docs/decisions/ADR-0015-licensing-corrections.md). Third-party parts such as Zephyr keep their own licences.
This is not legal advice.
