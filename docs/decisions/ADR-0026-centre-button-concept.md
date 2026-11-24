# ADR-0026: Centre-of-ring button: switch place, disc support and switch part

- **Status:** Proposed (owner direction D1 of 2026-11-24 in plan 09: S2 with the Omron B3U-1000P; the owner has not accepted this ADR)
- **Date:** 2026-11-24
- **Deciders / reviewers:** owner (Ben Spoor); written by the assistant; no goldfish review of this ADR yet
- **Related:** MECH-004, MECH-002, MECH-003, MECH-001, HW-008, HW-007, SYS-017, ADR-0006, ADR-0023, RV-018

## Context and problem
Owner decision 9 of 2026-11-22: the entire centre of the LED ring becomes the button (`docs/journal/2026-11-22-owner-decisions-p1-rework.md`).
The interview of 2026-11-23 (plan 09 section 0) fixed three things: a separate disc inside the ring, a clear click, a translucent disc
in the lid material that is not lit by an extra LED. The module sits at the ring centre today, the stored SW1 (E-Switch TL3342F160QG, 6.4 x 5.2 mm)
sits at r = 13 mm, azimuth 240 degrees, with a side hole in the housing, and the antenna strip is 5.06 mm from the nearest LED centre.
The ADR chooses the switch place, the support concept for the disc and the switch part. The analysis is in
`docs/verification/reports/analysis-button-disc.md` and `stock-check-button-switches.md`; the scripts have tests.

Constraints: one assembled side (HW-008); the antenna margin (MECH-003); a click inside a force window of [2] to [5] N and a press-point travel of at
most [1.0] mm at every press point inside r = 13 mm (working values of plan 09 section 4.1, not yet requirements); FDM tolerance on a disc that is
printed in place with a [0.8] mm gap; light spill of the ring onto the disc (about 18 % of the ring value at the centre, 53 % at r = 13 mm).

Not known: the real click travel of any candidate (no datasheet publishes a force-travel curve; the B3U publishes a pre-travel of 0.15 +0.2/-0.1 mm
only); the printed arm stiffness (assumed E = 1500 MPa); the B3U land pattern and plunger size (drawing only, not read); live stock on the order day.

## Decision criteria
| Criterion | Weight (1-5) | Source |
|-----------|--------------|--------|
| Force and travel inside the window at every press point | 5 | plan 09 section 4.1, MECH-004 |
| Robustness to FDM tolerance and to the stack | 5 | plan 09 section 3.4 |
| Antenna margin and metal near the antenna | 5 | MECH-003 |
| No unintended or stuck actuation | 4 | plan 09 section 4.5, SYS-017 |
| Part count, area and cost | 3 | HW-008 |
| Light and look | 3 | MECH-002 |
| Printability | 3 | MECH-001, plan 05 |
| Change to approved texts | 2 | process |

## Alternatives considered
Numbers from `button_disc.py`, `button_zone.py` and `button_light.py` (report sections 2 and 3). The matrix rows use a rigid disc, linear supports and
press points inside R_use = 13 mm.

### A. S2 with the Omron B3U-1000P: module moved, switch at the centre, three compliant bridges (recommended; owner direction D1)
B3U-1000P body 3.0 x 2.5 mm, 1.50 +- 0.49 N, pre-travel 0.15 mm, life 200,000 or more, LCSC C231329 (Extended, LCSC stock 49,545). With the module moved so that the
switch is at the centre the antenna strip keeps 3.90 mm to the nearest LED (77 % of 5.06 mm; 1,330 module poses on the 0.5 mm and 3 degree grid). The click force is
F = OF + 3 k x at every press point; the stiffness k of the three bridges passes the rule (force window with the switch tolerance, travel at most 1.0 mm) from 2.20 to
6.69 N/mm (ratio 3.0). Against: a bridge arm of 1.2 x 1.2 mm in PETG has a stiffness that FDM tolerance spreads by 0.32x to 2.4x; the pre-travel tolerance breaks the window at its
extremes (1.46 to 5.14 N at k = 3 N/mm); the module and its keep-outs move (plan 08 revision 6); the B3U land pattern is not read.
### B. S2 with the E-Switch TL3342F160QG (the assumption of plan 09 revisions 1 to 5)
6.4 x 5.2 mm body, 1.57 +- 0.49 N, no published travel (0.25 mm assumed), LCSC stock 1. The module only fits with the antenna strip 2.51 mm from the nearest LED
(50 % of today; 10 poses). The stiffness band is 2.83 to 3.92 N/mm (ratio 1.4), far below the FDM spread. Not recommended.
### C. S3 with three switches in parallel under a rigid disc (fallback)
The module stays as stored (strip 5.06 mm). With the TL3342 body 7 of 480 switch triplets at r = 11 mm clear the module and none clear its courtyard; with the B3U body 92 of 480
clear it (best gaps 1.68 mm to the body, 2.97 mm to the strip). Statics: a rigid disc on three switches is insensitive to FDM stiffness; with the B3U the click force runs from 1.34 to 4.50 N
(0.85 to 4.99 N with the switch tolerance), press-point travel 0.26 mm: the lower end is below the 2 N window, so a hold-down preload or a higher click force is needed. Against: three
parallel closed-contact fault paths (stuck-closed chance three times higher), two more switches and courtyards (fill 82 % with TL3342 courtyards), metal on the antenna side.
### D. A scissor or double-lever linkage with one switch
Not studied (owner direction D1: no scissor study). Listed for completeness; not scored.
### Not scored (fail a hard limit)
- C&K KSC221JLFS (6.2 x 6.2 mm, 2 +- 0.5 N, travel 0.35 +0.3/-0.1 mm): the travel limit is not met up to 20 N/mm of bridge stiffness, and the body is larger than today's.
- A single off-centre switch on soft supports (plan 09 section 3.2, S1): press-point travel of 3.6 mm or more at every stiffness; a guided disc in a bore (M2): jams (needs a guide of at least 7.8 mm
  against a free height of 5.95 mm); a score line with a skin: about 18 kN/mm stiffness against the 3 to 10 N/mm needed.

## Comparison
Scores 1 to 5; the scores of A, B and C are the assistant's, from the report; the owner may change them.

| Criterion (weight) | A | B | C |
|-----------|---|---|---|
| Force and travel inside the window (5) | 4 | 3 | 3 |
| Robustness to FDM tolerance and stack (5) | 2 | 1 | 4 |
| Antenna margin and metal near the antenna (5) | 4 | 2 | 3 |
| No unintended or stuck actuation (4) | 3 | 3 | 2 |
| Part count, area and cost (3) | 4 | 3 | 2 |
| Light and look (3) | 3 | 3 | 3 |
| Printability (3) | 3 | 3 | 4 |
| Change to approved texts (2) | 2 | 2 | 2 |
| **Weighted sum** | **96** | **73** | **89** |

Sensitivity: if A's robustness score drops to 1 (the arm stiffness cannot be held), A scores 91 and still leads C narrowly; if C's antenna score rises to 4 (the B3U triplet has room), C scores 94
and leads A. The ranking of A and C therefore depends on two numbers that only a coupon can give: the printed arm stiffness and the real click travel.

## Decision
Proposed: **A**, S2 with the Omron B3U-1000P and three compliant bridges, with **C** (S3 with the B3U) kept as the fallback if the coupons show that the bridge stiffness cannot be held
within the band. The owner decides and accepts.

## Consequences
- Positive: the module keeps 77 % of today's antenna margin; one small switch; the stored footprint of SW1 (6.4 x 5.2 mm) leaves the ring interior; the ring-interior fill falls from 66 % to 63 %.
- **Negative / trade-offs accepted:** the whole bridge concept rests on an assumed PETG modulus and a click travel that the datasheet gives only as a pre-travel with a +0.2/-0.1 mm tolerance;
  the module and the keep-outs move, so plan 08 revision 6 and a re-placement are needed; the B3U is an Extended part; the disc is lit by spill.
- New risks: a press at boot or a stuck press (plan 09 section 4.5 rules); a hand over the antenna during a long press (A6, 6 dB working limit); PETG creep and fatigue of the arms at 50 degC.
- Requirements created or changed (proposals for the owner, plan 09 section 4.7): MECH-010 to MECH-013, changes to MECH-004, HW-007 and SYS-017, one SW item, a note in ADR-0006.

## Verification and revisit
Unit tests of the scripts (`test_button_disc.py`, `test_button_light.py`, `test_check_tolerance.py`, `test_button_zone.py`); coupons and the pre-order gate (plan 09 step 3): disc stiffness,
the gap, the click travel and force of the B3U on a stand-in board; TC-310 to TC-315 on printed housings. Revisit if the coupons give a bridge stiffness spread wider than the band,
a click travel outside 0.05 to 0.35 mm, or a hand-over-antenna loss above 6 dB.

## Critical review notes
Strongest objection: "A rests on two numbers nobody has measured, and its score leads the fallback by only 7 points." Answer: agreed; the ADR is Proposed, the plan keeps the pre-order gate (P1 is not ordered before
the coupons pass) and names C as the fallback. Second objection: "moving the module costs a re-placement." Answer: plan 08 revision 6 re-places P1 anyway for the owner's decisions of 2026-11-22.
