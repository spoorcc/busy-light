# ADR-0020: PCB fabrication rules and use of the inner layers

- **Status:** Proposed (the owner decides; written by the assistant, 2026-11-08)
- **Date:** 2026-11-08
- **Deciders / reviewers:** owner (Ben Spoor); no goldfish review yet
- **Related:** HW-010, HW-005, ADR-0003, plan 06 (`docs/plans/06-pcb-spike-clean-route.md`), `docs/process/hw-generated-design-guardrails.md` section 3, `docs/verification/reports/spike-pcb-placement-routing.md`

## Context and problem
The 46 mm round board carries about 100 parts, a 0.4 mm pitch CC chip, a module and a 16 LED ring. With the spike rules (0.15 mm track and clearance, vias 0.6 / 0.3 mm) and with signals allowed on the inner layers, no routing run was complete on the real footprints (best of 8 runs: 1 open item; with signals kept off the ground plane: 4). The spike also let signal tracks cut the ground plane (In1) into islands: a ground via on an island is not connected (seen 2026-11-08). Two choices decide whether a clean board is possible: the fabrication rules the board is designed to, and what the inner layers carry. Not known: the fabricator (JLCPCB is the only one read; PCBWay and others are not checked) and the stack-up the owner orders.

## Decision criteria
| Criterion | Weight (1-5) | Source |
|-----------|--------------|--------|
| The board routes complete and passes the strict DRC | 5 | plan 06 G3, HW-010 |
| Manufacturability margin to the fabricator minimums (DFM) | 5 | process section 5 |
| Return path and power integrity (solid ground plane, supply drop) | 4 | HW-010, ESP32-C3 hardware guidelines |
| Cost and lead time | 3 | owner |
| Reversibility | 2 | process |

## Alternatives considered
### A. Keep the spike rules (0.15 mm track and space, vias 0.6 / 0.3 mm), inner layers free for signals
Margin to JLCPCB: track 0.15 against 0.09 mm (67 % margin). Evidence: best run of the real-footprint batches has 1 open item, silk and gate not clean, 316 mm of signal track on the ground plane in 4 pieces (report update 2026-11-08, `best3`).
### B. Fine rules (0.1 mm track and space, vias 0.5 / 0.2 mm), In1 only ground, signals on the outer layers and In2
Fabricator numbers (JLCPCB capability page, multilayer column, read 2026-11-08): track and space 0.09 mm at 1 oz; via hole minimum 0.15 mm, via diameter minimum 0.25 mm; annular ring recommended 0.20 mm, absolute minimum 0.15 mm; via hole to hole 0.2 mm; pad hole to pad hole 0.45 mm; pad to track 0.1 mm; SMD pad to pad 0.15 mm; copper to routed edge 0.2 mm. The via 0.5 / 0.2 mm has a ring of exactly 0.15 mm, the absolute minimum, 0.05 mm under the recommendation. The 0.1 mm track is 11 % above the fabricator minimum. Evidence from the experiment (4 runs, same placement seeds, `exB`): open items after the clean-up 0, 4, 0, 2; the best run passes the strict gate (waived findings only) with the ground plane in 1 piece, 11.7 % removed, no signal track on In1. With the same rules and signals allowed on In1 (`exA`): 0, 2, 1, 1.
### C. Six layers (two more routing layers), spike rules
Not run. Higher cost and lead time (not priced); the stack-up and the 0.5 oz inner copper would be re-checked.
### D. Defer: keep working at A until a fabricator is chosen
Costs routing time per run; the board does not reach a clean gate on the evidence so far.

## Comparison
| Criterion | A | B | C | D |
|-----------|---|---|---|---|
| Complete and strict-clean | no (best 1 open) | yes in 2 of 4 runs | not run | no |
| DFM margin | large | thin (via ring at the absolute minimum, track 11 %) | large | large |
| Return path | cut (4 pieces) | solid (1 piece) | likely solid | cut |
| Cost | base | base (not priced; the fabricator's price list is not read) | higher | base |
| Reversibility | n/a | high (numbers in `pcb_rules.py`, profile `SPIKE_PROFILE=fine`) | medium | n/a |

## Decision
Proposed: **B**, with the via annular ring raised to the recommended 0.20 mm if the routing still completes (for example 0.6 / 0.2 mm; not run), and with the fabricator's own DFM check on the Gerbers before an order. The owner has not accepted this.

## Consequences
- Positive: a complete, strict-clean board on the real footprints; a solid ground plane; a measured supply path.
- **Negative / trade-offs accepted:** thin margin to the fabricator minimums; only JLCPCB checked; the board is tied to a fabricator that does 0.1 mm / 0.5 mm vias at the standard price (price not read).
- New risks: yield at 0.1 mm lines (risk register entry to add after the owner decides); via annular ring at the absolute minimum.
- Requirements created or changed: none yet; a HW requirement for the fabrication rules would be drafted after acceptance.

## Verification and revisit
Fabricator DFM report on the Gerbers of the accepted board; repeat the batch with the accepted profile and keep the run table in the report. Revisit when the fabricator changes or when the first boards show open or short failures. Not verified: copper thickness tolerance, thermal rise of the 0.2 mm branches, RF and antenna behaviour.

## Critical review notes
Strongest objection: the spike needed three days of tuning, and the fine rules may only hide a placement that is too dense. Answer: partly true; the same placement routes complete at the fine rules in half of the runs and not at all at the coarse rules, so the rules are the limit, and the margin to the fabricator is stated above. A second objection: 0.1 mm lines for a product that may be built by another fabricator; not answered, the other fabricators were not read.
