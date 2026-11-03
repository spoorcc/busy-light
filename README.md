# busy-light

An open-source busy light for desks and doors, designed as a product: Zephyr software, KiCad hardware, FreeCAD enclosure,
documented to professional standards and prepared for EU market access (CE).

> **Status:** early design. No requirements are approved yet. Nothing here is certified or declared conformant.

## Documentation
| I want to... | Go to |
|--------------|-------|
| Use the product | [`docs/user/`](docs/user/README.md) |
| Understand how the project works | [`docs/process/`](docs/process/README.md) |
| See requirements, architecture and decisions | [`docs/`](docs/README.md) |
| Review regulatory (CE) status | [`docs/regulatory/`](docs/regulatory/README.md) |
| Contribute | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| Report a security issue | [`SECURITY.md`](SECURITY.md) |

## Repository layout
| Path | Contents |
|------|----------|
| `sw/` | Zephyr application, west manifest, tests |
| `hw/` | KiCad project, simulation, fabrication outputs, datasheets |
| `mech/` | FreeCAD models, exports, drawings, analysis |
| `docs/` | Process, requirements, architecture, decisions, risk, verification, regulatory, user docs, standards |
| `scripts/` | Traceability and documentation checks |
| `.claude/` | Claude Code skills and project instructions |

## Build the software
```sh
west init -l sw
west update
west build -b <board> sw/app
```

## Checks
```sh
python3 -I scripts/check_traceability.py
python3 -I scripts/check_docs_style.py
```

## License
TBD -- to be chosen (suggestion: Apache-2.0 software, CERN-OHL hardware, CC-BY-SA docs and mechanical).
