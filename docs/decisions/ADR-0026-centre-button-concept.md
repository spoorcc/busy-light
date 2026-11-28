# ADR-0026: Centre-of-ring button: switch place, disc support and switch part

- **Status:** Proposed (owner directions D1 and D4 of 2026-11-24 in plan 09: S2 with the Omron B3U-1000P as the working direction and S3 as the second candidate, both to the coupon gate; the owner has not accepted this ADR)
- **Note 2026-11-28:** the owner reversed D7 (disc dark): the disc is translucent and lit by 4 LEDs (ADR-0027, plan 09 D10). The criterion "light from the ring only, disc dark" and the opaque-disc transmission limit no longer apply; the switch and support comparison stays. Proposed ADR, text otherwise unchanged.
- **Date:** 2026-11-24
- **Deciders / reviewers:** owner (Ben Spoor); written by the assistant; reviewed by a fresh goldfish against the code on 2026-11-24 (RV-018 rows R29 to R45); this version is not yet reviewed
- **Related:** MECH-004, MECH-002, MECH-003, MECH-001, HW-008, HW-007, SYS-017, ADR-0003, ADR-0006, ADR-0023, DEV-004, RV-018

## Context and problem
Owner decision 9 of 2026-11-22: the entire centre of the LED ring becomes the button (`docs/journal/2026-11-22-owner-decisions-p1-rework.md`).
The interview of 2026-11-23 (plan 09 section 0) fixed: a separate disc inside the ring, a clear click, a disc that is not lit by an extra LED. The second set of
answers (2026-11-24) adds: the disc is **dark**, the light comes from the ring and rim and not from the centre (D7); the product looks like a really designed
Apple-grade product (D8); the button is used very rarely (D6); both concepts go to the coupon gate (D4); the force window is good enough to start (D5).
The module sits at the ring centre today, the stored SW1 (E-Switch TL3342F160QG, 6.4 x 5.2 mm) sits at r = 13 mm, azimuth 240 degrees, with a side hole in the
housing, and the antenna strip is 5.06 mm from the nearest LED centre. The ADR chooses the switch place, the support concept for the disc and the switch part.
The analysis is in `docs/verification/reports/analysis-button-disc.md` and `stock-check-button-switches.md`; the scripts have tests.

Constraints: one assembled side (HW-008); the antenna margin (MECH-003); a click inside a force window of [2] to [5] N and a press-point travel of at most [1.0] mm
at every press point inside r = 13 mm (working values of plan 09 section 4.1, not yet requirements); FDM tolerance (0.30 mm) against a [0.4] mm gap that must be even to
[+-0.1] mm (a separate opaque disc, D7 and D8); light spill of the ring onto the disc (about 17 % of the ring value at the centre, 50 % at r = 13 mm, 67 to 77 % at
r = 15 to 16 mm) that the opaque disc must stop (transmission at most 4.5 % at r = 15 mm for a limit of 3 % of the ring luminance).

Not known: the real click travel of any candidate (no datasheet publishes a force-travel curve; the B3U publishes a pre-travel of 0.15 +0.2/-0.1 mm only); the printed arm
stiffness (assumed E = 1500 MPa); the stiffness of the disc plate itself (a 30 mm, 1.2 mm PETG plate deflects 0.042 mm/N at a central load, about 40 % of the 0.10 mm/N of the
B3U, so a central press travels 0.10 to 0.21 mm more than the rigid-disc rows say); the B3U land pattern and plunger size (drawing only, not read); which process reaches an
Apple-grade surface (plan 09 question 10); live stock on the order day.

## Decision criteria
| Criterion | Weight (1-5) | Source |
|-----------|--------------|--------|
| Force and travel inside the window at every press point | 5 | plan 09 section 4.1, MECH-004 |
| Robustness to FDM tolerance and to the stack | 5 | plan 09 section 3.4 |
| Antenna margin and metal near the antenna | 5 | MECH-003 |
| Look and feel, Apple grade: flush, narrow even gap, short visible travel | 5 | owner decision D8, plan 09 section 4.1 |
| No unintended or stuck actuation | 4 | plan 09 section 4.5, SYS-017 |
| Part count, area and cost | 3 | HW-008 |
| Light from the ring only, disc dark | 3 | MECH-002, owner decision D7 |
| Printability | 3 | MECH-001, plan 05 |
| Change to approved texts and decisions | 2 | process |

## Alternatives considered
Numbers from `button_disc.py`, `button_zone.py` and `button_light.py` (report sections 2 and 3). The matrix rows use a rigid disc, linear supports and press points inside
R_use = 13 mm.

### A. S2 with the Omron B3U-1000P: module moved, switch at the centre, three compliant bridges (owner direction D1)
B3U-1000P body 3.0 x 2.5 mm, 1.50 +- 0.49 N, pre-travel 0.15 +0.2/-0.1 mm, life 200,000 or more, LCSC C231329 (Extended, LCSC stock 49,545). With the module moved so that the
switch is at the centre the best pose has the antenna strip 3.90 mm from the nearest LED (77 % of 5.06 mm) but 1.35 mm from the metal switch; with the antenna end away from the
switch (plan 09 section 4.3) it is 3.64 mm (72 %; 60 % of the `mech_outline` baseline of 6.07 mm), and 3.55 mm (70 %) with the strip at least 3 mm from the switch (1,330 poses
before the rule). The click force is F = OF + 3 k x at every press point; at the nominal pre-travel the bridge stiffness k passes the rule (force window with the switch tolerance,
travel at most 1.0 mm) from 2.20 to 6.69 N/mm (ratio 3.0). Against: **over the whole datasheet pre-travel tolerance (0.05 to 0.35 mm) no stiffness holds the window** (it needs
k >= 6.60 and k <= 2.87 N/mm; for 0.05 to 0.25 mm k <= 4.01, still none), and at a pre-travel of 0.35 mm the press-point travel is 1.08 to 1.47 mm; an arm of 1.2 x 1.2 mm in PETG
has a stiffness that FDM tolerance spreads by 0.32x to 2.4x (ratio 7.7, more than the band of 3.0); a k = 3 N/mm arm (L = 10.1 mm) sees 53 MPa at 1.0 mm of stroke against the
assumed yield of 40 MPa; the tolerance chains are wide (vertical +-1.41 mm worst case and +-0.60 mm RSS against a click travel of 0.15 mm; lateral +-3.05 mm and +-2.04 mm against
an actuator of about 2.0 mm, so the plunger tip needs a wide pad or the board must be located); the press-point travel of 0.6 to 1.3 mm is visible and needs a wider gap and a
visible dish (look and feel); the module and its keep-outs move (plan 08 revision 6, reversing the owner decision of 2026-11-18 and reopening ADR-0003, ADR-0023 and DEV-004);
the B3U land pattern is not read.
### B. S2 with the E-Switch TL3342F160QG (the assumption of plan 09 revisions 1 to 5; dropped)
6.4 x 5.2 mm body, 1.57 +- 0.49 N, no published travel (0.25 mm assumed), LCSC stock 1. The module only fits with the antenna strip 2.51 mm from the nearest LED (50 % of today; 10 poses).
The stiffness band is 2.83 to 3.92 N/mm (ratio 1.4), far below the FDM spread. Not recommended.
### C. S3 with three switches in parallel under a rigid disc
The module stays as stored (strip 5.06 mm). With the TL3342 body 7 of 480 switch triplets at r = 11 mm clear the module and none clear its courtyard; with the B3U body 92 of 480
clear it at clearance 0 (best gaps 1.68 mm to the body, 2.97 mm to the strip) and 22 at a clearance of 1.0 mm (2.50 mm to the strip). Statics: a rigid disc on three switches does
not depend on the arm stiffness and travels only 0.26 mm at the press point (a flush disc and a 0.4 mm gap are possible); with the B3U the click force of a press at an edge point
is 1.34 N; a press at the centre needs 3 x (OF +- tol) = 3.03 to 5.97 N. Both ends miss the window of [2] to [5] N (the window is a working proposal; a different window or a
hold-down preload would change this). Against: three parallel closed-contact fault paths (stuck-closed chance three times higher), two more switches and courtyards (fill 65 % with
B3U courtyards, 78 % with TL3342 courtyards on the same method), metal on the antenna side, and the plate flexibility between the three switches is not modelled.
### D. A scissor or double-lever linkage with one switch
Not studied (owner direction D1: no scissor study). Listed for completeness; not scored.
### Not scored (fail a hard limit)
- C&K KSC221JLFS (6.2 x 6.2 mm, 2 +- 0.5 N, travel 0.35 +0.3/-0.1 mm): the travel limit is not met up to 20 N/mm of bridge stiffness, and the body is larger than today's.
- A single off-centre switch on soft supports (plan 09 section 3.2, S1): press-point travel of 3.6 mm or more at every stiffness; a guided disc in a bore (M2): jams (needs a guide of
  at least 7.8 mm against a free height of 5.95 mm); a score line with a skin: about 18 kN/mm stiffness against the 3 to 10 N/mm needed.

## Comparison
Scores 1 to 5; the scores are the assistant's, from the report and from the review of plan and code (RV-018 rows R29 to R45); the owner may change them. The first version of this ADR
scored A 96, B 73 and C 89 without the look criterion; the review corrected it to 84, 66 and 87; the second set of owner answers (D7, D8) adds the look criterion (weight 5).

| Criterion (weight) | A | B | C |
|-----------|---|---|---|
| Force and travel inside the window (5) | 3 | 2 | 2 |
| Robustness to FDM tolerance and stack (5) | 2 | 1 | 4 |
| Antenna margin and metal near the antenna (5) | 3 | 2 | 3 |
| Look and feel, Apple grade (5) | 2 | 1 | 4 |
| No unintended or stuck actuation (4) | 3 | 3 | 2 |
| Part count, area and cost (3) | 4 | 3 | 3 |
| Light from the ring only, disc dark (3) | 3 | 3 | 3 |
| Printability (3) | 3 | 3 | 4 |
| Change to approved texts and decisions (2) | 1 | 1 | 2 |
| **Weighted sum** | **94** | **71** | **107** |

Look and feel: a press of A travels 0.6 to 1.3 mm at the press point (plus the plate flexibility), which needs a wider gap, a visible dish and soft arms; a rigid disc on three B3U (C)
travels 0.26 mm, so a 0.4 mm gap and a flush disc are possible and the feel is a short, firm click. The dark disc (D7) is the same work in all three: an opaque disc and a light-tight
gap lip (plan 09 section 4.4).

Sensitivity: C leads A by 13 points. The look score decides it (without that criterion C leads by 3). C loses its lead if its force score drops to 1 and its look score to 3 (-15), or if
A gains two points in the weight-5 criteria while C loses one. The owner chose to build both (D4), so the ranking is a recommendation, not a decision.

## Decision
Proposed: **build both A and C in the pre-order coupon gate (owner decision D4: "Both"; plan 09 step 3: one B3U at the centre and three B3U at r = 11 mm on the stand-in board, an opaque
disc with a light-tight gap lip, a 0.4 mm gap, flush and recessed variants) and choose on the measured click travel, click force, arm stiffness, disc luminance and appearance.** The
assistant's scores lean to C (107 against 94), mainly on look and feel and on robustness to print tolerance; A keeps one switch and no stuck-closed multiplication. S2 with the TL3342
(B) is dropped. P1 is not re-placed before the owner chooses. The owner decides and accepts.

## Consequences
- Positive (A): one small switch; the stored SW1 footprint (6.4 x 5.2 mm) leaves the ring interior; the estimated ring-interior fill falls from 66 % to 63 % (plan 08 A3 figures, not
  recomputed). (C): the module and its antenna margin stay as stored; no arms to design; a short visible travel.
- **Negative / trade-offs accepted:** A rests on an assumed PETG modulus and on a click travel that the datasheet gives only as a pre-travel with a +0.2/-0.1 mm tolerance, over which no
  bridge stiffness holds the force window; A moves the module (antenna margin 72 % of today at best) and reopens ADR-0003, ADR-0023 and DEV-004; C triples the closed-contact fault paths
  and misses the force window at both ends; the B3U is an Extended part; the disc must be opaque with a light-tight gap lip, which adds a part and a finish to decide (plan 09 questions 10 and 11).
- New risks: a press at boot or a stuck press (plan 09 section 4.5 rules); a hand over the antenna during a long press (A6, 6 dB working limit); PETG creep and fatigue of the arms at 50 degC
  (less severe at the derived life of [2 000] presses); an Apple-grade surface that FDM cannot reach.
- Requirements created or changed (proposals for the owner, plan 09 section 4.7): MECH-010 to MECH-014, changes to MECH-002, MECH-004, HW-007 and SYS-017, one SW item, a note in ADR-0006.

## Verification and revisit
Unit tests of the scripts (`test_button_disc.py`, `test_button_light.py`, `test_check_tolerance.py`, `test_button_zone.py`); coupons and the pre-order gate (plan 09 step 3): disc stiffness,
the gap and its light seal, the opaque disc luminance, the click travel and force of the B3U on a stand-in board for both concepts; TC-310 to TC-316 on printed housings. Revisit if the
coupons give a click travel spread that no stiffness can hold (A), an edge force below the working window that the owner will not accept (C), a disc luminance above 3 % of the ring, or a
hand-over-antenna loss above 6 dB.

## Critical review notes
Strongest objection: "the first version recommended A at 96 against 89 and the owner followed it." Answer: the review of plan and code found four errors in the reasoning (a false
sensitivity sentence, the metal switch next to the antenna, the pre-travel tolerance, the three-switch centre force); the corrected scores put A and C within noise, and the Apple-grade criterion
(D8) then moves the lean to C; the ADR says so and the owner chose to build both. Second objection: "moving the module costs a re-placement." Answer: plan 08 revision 6 re-places P1 anyway
for the owner's decisions of 2026-11-22, but A also reverses the decision of 2026-11-18. Third objection: "the force window of [2] to [5] N is the assistant's working value." Answer: yes; the
owner called it good enough to start (D5); changing it changes the C scores most.
