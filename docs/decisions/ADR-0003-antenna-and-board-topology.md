# ADR-0003: Antenna placement and board topology

- **Status:** Proposed (only the owner sets Accepted)
- **Date:** 2026-11-03
- **Deciders / reviewers:** Ben Spoor (owner); Reviewed in RV-001 (as referenced by plan 02); no separate ADR review
- **Related:** NEED-014, NEED-010, SYS-021, SYS-022, SYS-023, SYS-028, ADR-0002; design doc `docs/plans/02-system-design.md` (section 4.3, spike 7.2)

## Context and problem
The device is about 53 mm across (SYS-028, 48-58 mm). Inside the housing wall the PCB is about 46-48 mm. Sixteen LEDs sit evenly on a ring of at least 38 mm (SYS-028),
which leaves a free centre of about 30 mm. The ESP32-C3 module of ADR-0002 is about 13 x 17 mm (from memory, verify in the datasheet) and its on-board antenna needs a
copper-free keep-out area. The USB-C connector and the button also need edge space. The board is assembled on one side with no hand soldering (SYS-022).
Cost limit EUR 10-20 per assembled board (SYS-021).

Not known: how much the LED ring, its tracks and the 5 V plane detune and shadow the antenna. Only a measurement answers this (spike 7.2). The vendor's keep-out figure
is not yet checked.

## Decision criteria
| Criterion | Weight (1-5) | Source requirement |
|-----------|--------------|--------------------|
| Radio range works in the housing | 5 | NEED-001, SYS-001 |
| Unit cost at 10 and at 1000 units | 4 | SYS-021 |
| Fits 53 mm and even LED spacing | 4 | SYS-028 |
| Orderable with no hand soldering | 4 | SYS-022 |
| Radio approval effort (module is pre-certified) | 4 | `docs/regulatory/applicability.md` |
| Risk of redesign after first prototype | 3 | project |
| Assembly effort in the housing | 2 | NEED-010 |

## Alternatives considered

### A. One board; module with on-board antenna in the centre of the LED ring (T1)
Antenna end faces away from the USB-C connector; copper-free area under and around it; LED tracks routed away. Cheapest, one part, pre-certified module reused as is.
Cons: the antenna sits inside a ring of LEDs, so range may drop; nothing in the datasheet tells how much.

### B. One board; module variant with a u.FL connector plus a small antenna on the housing wall (T2)
Module such as the ESP32-C3-MINI-1U (exists; confirm the part and library status in spike 7.4). The antenna is outside the keep-out problem and can be placed at the rim.
Cost: connector is part of the module; the antenna with cable about EUR 1-2 (estimate). The connector is SMD, so SYS-022 (no soldering) holds; plugging the cable is a housing assembly step, not soldering.
Cons: a manual step per unit; a loose cable is a field failure; the antenna must be fixed in the housing; the module approval depends on the antennas listed in its filing, so the antenna must be one of those or the approval needs review.
This corrects the design doc, which said T2 conflicts with SYS-022. It does not, if the rule is read as "no soldering"; the owner may still read it as "no manual steps" (decision needed, see below).

### C. Bare ESP32-C3 chip with a chip antenna on the board (T3)
Smallest board area, lowest parts cost at volume (about 1000 units per year).
Strongest case: at 1000 units the saving per unit is real.
Cons: the RF matching network and antenna tuning need a vector network analyser or equivalent; the module's radio approval does not carry over, so a new radio test is needed; highest risk for a first board. Rejected for the first board.

### D. Two stacked boards: ring board and compute board (T4)
The antenna is on the compute board with a clear side. Decouples LED layout from RF. Cons: second PCB, board-to-board connector, thicker housing, more cost; at 10 units each extra fixed fee counts.

### E. Do nothing / defer
Draw the board without deciding. Not possible: placement of the module defines the board.

## Comparison
Scores 0 (poor) to 5 (good), my judgement; weights as above (max 130).

| Criterion (weight) | A | B | C | D | E |
|--------------------|---|---|---|---|---|
| Radio range (5) | 2 | 4 | 3 | 4 | 0 |
| Cost (4) | 5 | 4 | 5 | 2 | 0 |
| Fits 53 mm (4) | 3 | 4 | 5 | 3 | 0 |
| No hand soldering (4) | 5 | 4 | 5 | 3 | 0 |
| Approval effort (4) | 5 | 4 | 0 | 5 | 0 |
| Redesign risk (3) | 2 | 4 | 1 | 4 | 0 |
| Assembly effort (2) | 5 | 3 | 5 | 2 | 0 |
| **Weighted sum** | 98 | 102 | 88 | 88 | 0 |

The score for A on radio range is a guess. B scores only 4 points above A on paper, and it costs about EUR 1-2 and a manual step, and A could still pass the measurement.

## Decision
Proposed (see the update of 2026-11-07 below, which changes the fallback): **try A first, with B as the pre-agreed fallback, and decide with measured data, not with the table.**
1. Spike 7.2: measure RSSI (and packet loss at a fixed rate) at three distances for (i) the bare module on its dev board, (ii) the module inside a mock ring with LEDs, tracks, plane and a 3D-printed housing.
2. Pass criterion (proposed, to be confirmed by the owner): the loss against (i) is at most 6 dB at every distance, and the link stays up at the longest distance tested (10 m through one interior wall).
3. If A fails, use B. If B fails too, use D. C stays a later volume option, after a separate ADR and a radio test plan.
4. Layout rule for both: the keep-out comes from the vendor's hardware design guide, copied into the KiCad rules before routing (checked at design review). **Before any further design work:** place the real module outline and its keep-out in KiCad on a 46-48 mm circle with 16 LED pads. If the keep-out cannot be met, A is dropped without a spike (RV-001, finding 8). The module's radio approval depends on its filed antenna and installation conditions; these are read from the vendor documents before A is accepted.
5. Owner decision recorded for review: the goldfish review recommends B as the baseline, because a module antenna inside a ring of LEDs is high risk. This ADR keeps A first only because the cost difference is small and the data is missing; the owner may choose B now.

I do not recommend the final choice yet because the data is missing. If the owner wants to commit now, the choice is B: slightly higher cost, much lower range risk.

## Update 2026-11-07 (owner answers in the working session; status stays Proposed until the owner accepts)
- **SYS-022 is read as "no manual steps".** The owner answered that plugging the u.FL antenna cable is not acceptable. Option B (cable plus wall antenna) is therefore excluded unless the owner relaxes SYS-022. Option D (two stacked boards) is excluded on the same reading (stacking is a manual step; the assistant's reading, the owner did not rule on D).
- **Rim placement was asked and does not clear a full ring (assistant's first-order geometry, not measured).** Board radius 23 mm, antenna area 13.2 x 5.4 mm with its end at the rim, ring radius 19 to 21 mm, 16 LEDs evenly spaced, Espressif clearance 15 mm as a straight distance from the antenna area: 5 to 6 of the 16 LEDs fall inside the keep-out (4 to 5 at 10 mm clearance). The vendor drawing of the keep-out shape was not checked. The rim is better than the centre, where the nearest LED is about 9.5 mm from the antenna area, but it does not remove the conflict.
- **Decision (owner, 2026-11-07, recommended option): A first, decided by spike 7.2.** The module with its on-board antenna sits off-centre toward the rim as in the current layout. Range is decided by the relative loss of at most [6] dB against a bare module at three distances (item 1 and 2 above), not by the 15 mm guideline.
- **Fallback chain changed.** B is no longer a pre-agreed fallback. If A fails the spike, the owner chooses between: relaxing SYS-022 (then B), fewer or unevenly spaced LEDs (changes the ring, ADR-0012 and the mechanics), or a bare chip with a chip antenna (C, with a separate ADR and radio test plan).
- **Deviation DEV-004** (the keep-out overlap on the PCB spike) stays Proposed until the spike result exists.

## Consequences
- Positive: no redesign if A passes; known fallback if it fails; one board in both cases.
- **Negative / trade-offs accepted:** the layout of the first board waits for the spike; the spike needs a mock ring (a few days, a few euros); B adds a manual step and cost.
- New risks (to add to risk register): antenna detuning by LEDs or housing material; loose or wrong antenna in B; approval invalid if the antenna differs from the filed list; keep-out violated by a later layout change.
- Requirements created or changed: a possible HW requirement for the keep-out and a range requirement (see SYS-038, HW-005 (working defaults)).

## Verification and revisit
Spike 7.2 report in `docs/verification/`; the criterion above. Revisit when: first prototype range test fails, the housing material or ring diameter changes, the platform changes (ADR-0002), or the volume passes about 1000 units per year (then reconsider C).

## Critical review notes
Strongest objection: "Fallback B changes the BOM and the manual assembly, so deciding 'A first' makes the schematic work wasted."
Answer: A and B use the same chip and footprint family; the module variants have the same pin function, so schematic and most of the layout carry over. The module footprint differs (to confirm).
Second objection: "RSSI on a bench is not a real-world range test." Accepted; the criterion is a relative loss against a reference module, which removes most of the room dependence.

## Finding from the housing analysis (2026-11-04)
Source: plan 05 section 4.6 and `docs/verification/reports/mech-concept-analysis.md` section 8. Numbers are analysis, not measured. This ADR stays Proposed; the owner decides.
- The housing uses D_pcb [46.0] mm (inside the 46 to 48 mm of the context) in a 53.0 mm housing. The module sits at the board centre, antenna end toward azimuth 180, antenna end edge 8.3 mm from the axis (assumed antenna area 13.2 x 5.4 mm).
- The Espressif guideline (design guidelines, release master of 3 Nov 2026) asks for 15 mm clearance around the antenna, no LEDs, tracks or ground within it, and says not to centre the module with clearance on all four sides. Option A (module in the ring centre) breaks this by design. The housing cannot fix it. MECH-003 now covers only the housing part (plastic only in the 15 mm box, nearest wall at least 15 mm from the antenna edge).
- Distances in this layout: nearest LED centre to the antenna area about 9.5 mm (11.7 mm on the module axis; the package edge is about 1 mm closer); antenna corners to the inner housing wall 14.3 mm (0.7 mm below 15 mm); middle of the end edge to the wall 16.6 mm. The LED distance is below 15 mm.
- Consequence for the decision: option A needs board cut-outs around the antenna (both sides and below, per the guideline) and the KiCad keep-out check (decision item 4) **before** any layout work. If the cut-outs do not fit a 46 mm board with the ring of 16 LEDs, use the pre-agreed fallback B (u.FL variant), or move the module to the board edge. The distance to the nearest LED must be accepted by the range test of SYS-038 (TC-038) or be fixed by the layout.
- Not decided here: which of the two (B or board edge) to prefer. Open for the owner with the spike 7.2 data.
