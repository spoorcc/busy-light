# ADR-0012 gate G1: re-run of the stand-in spike on 2026-11-04

- **Status:** Draft
- **Date:** 2026-11-04 (a re-run late in the session)
- **Author:** Claude. Not reviewed. Nothing here is Approved or Accepted.
- **Related:** ADR-0012 item 9 (G1), `docs/verification/reports/spike-hw-kicad-pipeline.md` (on branch `spike/hw-kicad`)
- **Method:** a worktree of `spike/hw-kicad`, `hw/kicad/spike/run_spike.sh` with a Python venv (system site packages for `pcbnew`, `kiutils` 1.4.8), KiCad 10.0.6, no Freerouting jar. Run time about 9 s. Labels: **run** or **not run**.

## Results
| G1 criterion (ADR-0012 item 9) | Result of this re-run | Run |
|--------------------------------|-----------------------|-----|
| (a) ERC 0, parity 0, DRC 0 unwaived | ERC: 0 violations. Schematic parity: 0 issues. DRC of the board built from the stored routing session: 0 violations, 0 unconnected items. Every part has an `HW_REQ` field | **run** |
| (b) 100 percent routed | 0 unconnected items in the DRC of the stored-session board. The routing itself was imported from the stored session, not produced by a router run today | **run**, import only |
| (c) identical dumps in two runs | Two schematic generations: semantic dumps identical and the schematic bytes identical. The routed dump equals the committed dump | **run** |
| (d) Freerouting scripted in CI | The script exists. It was **not run today** (no jar) and nothing runs in CI | **not run** |

## What this does not show
- Freerouting is not deterministic; the stored session is the reproducibility input (ADR-0012 item 9).
- The stand-in uses peg azimuths of 15, 150 and 285 degrees. With the housing azimuths of 30, 150 and 270 degrees the criteria (a) and (b) fail (mounting holes fall on the pads of LED D2 and D13): a housing or LED-count decision for the owner is still open.
- The FreeCAD fit check was not run (no housing directory set).
- The schematic writer is the spike's `kiutils` writer on a stand-in circuit, not the product schematic with the gate of ADR-0016.
- No CI, no pinned container, no hash-pinned packages (ADR-0012 item 4), no goldfish review of the generator.

## Conclusion
The local part of G1 (a to c, the stored-session route) is reproduced. G1 is **not** complete: (d) in CI, the peg-azimuth decision and the CI pinning remain. ADR-0012 stays Proposed. This run does not change the recommendation: accept after (d), the pinning and the azimuth decision.
