# ADR-0026: Centre-of-ring button: switch place, disc support and switch part

- **Status:** Proposed (owner direction D1 of 2026-11-24 in plan 09: S2 with the Omron B3U-1000P as the working direction; the scores below put S2 and S3 within noise; the owner has not accepted this ADR)
- **Date:** 2026-11-24
- **Deciders / reviewers:** owner (Ben Spoor); written by the assistant; no goldfish review of this ADR yet
- **Related:** MECH-004, MECH-002, MECH-003, MECH-001, HW-008, HW-007, SYS-017, ADR-0003, ADR-0006, ADR-0023, DEV-004, RV-018

## Context and problem
Owner decision 9 of 2026-11-22: the entire centre of the LED ring becomes the button (`docs/journal/2026-11-22-owner-decisions-p1-rework.md`).
The interview of 2026-11-23 (plan 09 section 0) fixed three things: a separate disc inside the ring, a clear click, a translucent disc
in the lid material that is not lit by an extra LED. The module sits at the ring centre today, the stored SW1 (E-Switch TL3342F160QG, 6.4 x 5.2 mm)
sits at r = 13 mm, azimuth 240 degrees, with a side hole in the housing, and the antenna strip is 5.06 mm from the nearest LED centre.
The ADR chooses the switch place, the support concept for the disc and the switch part. The analysis is in
`docs/verification/reports/analysis-button-disc.md` and `stock-check-button-switches.md`; the scripts have tests.

Constraints: one assembled side (HW-008); the antenna margin (MECH-003); a click inside a force window of [2] to [5] N and a press-point travel of at
most [1.0] mm at every press point inside r = 13 mm (working values of plan 09 section 4.1, not yet requirements); FDM tolerance on a disc that is
printed in place with a [0.8] mm gap; light spill of the ring onto the disc (about 17 % of the ring value at the centre, 50 % at r = 13 mm).

Not known: the real click travel of any candidate (no datasheet publishes a force-travel curve; the B3U publishes a pre-travel of 0.15 +0.2/-0.1 mm
only); the printed arm stiffness (assumed E = 1500 MPa); the stiffness of the disc plate itself (a 30 mm, 1.2 mm PETG plate deflects 0.042 mm/N at a central load, about 40 % of the 0.10 mm/N of the B3U, so a central press travels 0.10 to 0.21 mm more than the rigid-disc rows say); the B3U land pattern and plunger size (drawing only, not read); live stock on the order day.

## Decision
Proposed (revision of 2026-11-24 after the review): **no winner by score. Keep A (the owner's direction D1) and C as the two candidates, build both in the pre-order coupon gate (plan 09 step 3: one B3U at the centre and
three B3U at r = 11 mm on the stand-in board, with the matching printed lids) and choose on the measured click travel, click force and arm stiffness.** S2 with the TL3342 (B) is dropped. P1 is not re-placed before
the owner chooses. The owner decides and accepts.

## Consequences
- Positive (A): one small switch; the stored SW1 footprint (6.4 x 5.2 mm) leaves the ring interior; the estimated ring-interior fill falls from 66 % to 63 % (plan 08 A3 figures, not recomputed). (C): the module and its antenna margin stay as stored; no arms to design.
- **Negative / trade-offs accepted:** A rests on an assumed PETG modulus and on a click travel that the datasheet gives only as a pre-travel with a +0.2/-0.1 mm tolerance, over which no bridge stiffness holds the force window;
  A moves the module (antenna margin 72 % of today at best) and reopens ADR-0003, ADR-0023 and DEV-004; C triples the closed-contact fault paths and misses the force window at both ends; the B3U is an Extended part; the disc is lit by spill.
- New risks: a press at boot or a stuck press (plan 09 section 4.5 rules); a hand over the antenna during a long press (A6, 6 dB working limit); PETG creep and fatigue of the arms at 50 degC.
- Requirements created or changed (proposals for the owner, plan 09 section 4.7): MECH-010 to MECH-013, changes to MECH-004, HW-007 and SYS-017, one SW item, a note in ADR-0006.

## Verification and revisit
Unit tests of the scripts (`test_button_disc.py`, `test_button_light.py`, `test_check_tolerance.py`, `test_button_zone.py`); coupons and the pre-order gate (plan 09 step 3): disc stiffness,
the gap, the click travel and force of the B3U on a stand-in board; TC-310 to TC-315 on printed housings. Revisit if the coupons give a click travel spread that no stiffness can hold (A), an edge
force below the working window that the owner will not accept (C), or a hand-over-antenna loss above 6 dB.

## Critical review notes
Strongest objection: "the first version recommended A at 96 against 89 and the owner followed it." Answer: the review of plan and code found four errors in the reasoning (a false sensitivity sentence, the metal
switch next to the antenna, the pre-travel tolerance, the three-switch centre force); the corrected scores put A and C within noise and the ADR now says so. Second objection: "moving the module costs a re-placement."
Answer: plan 08 revision 6 re-places P1 anyway for the owner's decisions of 2026-11-22, but A also reverses the decision of 2026-11-18. Third objection: "the force window of [2] to [5] N is the assistant's working value."
Answer: yes; changing it changes the C scores most, which is why the owner decides the window (plan 09 question 5).
