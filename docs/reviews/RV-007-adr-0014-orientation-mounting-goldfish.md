# Review Record RV-007

- **Subject:** ADR-0014 (back mounting interface, Proposed) and the requirements drafted with it: NEED-020, NEED-021, NEED-022, SYS-047, HW-011, MECH-006, MECH-007, MECH-008 (all Draft), with test-case stubs TC-047, TC-211, TC-306, TC-307, TC-308; commit d4f0d57 (text before this review)
- **Type:** Architecture and requirements
- **Date:** 2026-11-04  **Reviewer(s):** three stateless goldfish subagents (comprehension; failure modes and mechanical safety lens; requirements quality lens)  **Independent?** partly: same model family as the author
- **Not run:** the implementation-readiness pass; any geometry drawing, load calculation or sensor datasheet read.

## Comprehension check
The comprehension goldfish restated the decision correctly (printed bayonet on the back, label on the back, orientation sensor, clock mode later). Its open questions are findings G1 to G4.

## Findings
The weighted sums recompute correctly (A 92, B 128, C 120, D 95, E 83, F 103, G 40).

| # | Severity | Finding | Resolution | Status |
|---|----------|---------|------------|--------|
| G1 | Critical | The label and the bayonet recess do not both fit on the 53 mm back: a centred 30 mm recess leaves a ring (53 - 30) / 2 = 11.5 mm wide; a 20 mm square needs more. Found independently by two reviewers; verified by my arithmetic. | Accepted. Noted in ADR-0014. Needs a scale drawing (circle 53, recess 30, label 21 x 21, feet) and a choice: smaller recess, smaller label, or label inside the recess. | Open |
| G2 | Critical | "No supports" is wrong for the plan 05 orientation (floor on the bed makes the recess a bridge); a 1.5 mm recess in a 2.0 mm floor leaves 0.5 mm, not a whole number of perimeters; the lug and recess values break the ADR's own 0.4 mm rule. | Accepted. Noted in ADR-0014; "fits the 2 mm floor" removed from the rationale. Decide print orientation or a separate printed ring part; fix floor skin and lug geometry. | Open |
| G3 | High | MECH-007 says "quarter turn of about 30 degrees"; a quarter turn is 90 degrees. | Fixed now ("a turn of about 30 degrees"). Entry and lock angles and keying still to state. | Fixed |
| G4 | High | The sensitivity sentence is wrong: if C scores 4 on printing and 3 on rotation it totals 127, so B still leads by 1, not zero. | Fixed now. | Resolved |
| G5 | High | The 10 N pull-off figure has no derivation; the load is moment and shear, not axial; no safety factor; MECH-008 is a Safety item with priority Should. | Accepted. Weigh the unit; load cases (axial, moment, cable side pull, unplugging); owner decides Should or Must. | Open (owner) |
| G6 | High | A 30 degree turn unlocks the unit: a knock or turning it by hand releases it; no unlock torque limits; creep test only 24 h; soak temperature defined two ways. | Accepted. Unlock torque limits; positive lock or longer travel; long-term creep test; define the soak once. RISK-039. | Open |
| G7 | High | Antenna: any accessory on the back lies inside the 15 mm box; the range test has no accessory or metal-wall case; "metal accessories outside the box" cannot be met for anything touching the back. | Accepted. Range test with each standard accessory and on a metal surface; reword rule 1; manual warning. RISK-040. | Open |
| G8 | High | Thermal case for horizontal, vertical and a wall-mounted back is not redone; the creep soak temperature depends on it. | Accepted. Re-run the thermal model (also open in RV-004). | Open |
| G9 | High | The stand tilt may sit on the 30 degree switch point (flicker); face-down and ceiling mounts mirror the flat zero; NEED-020 and NEED-021 promised "every orientation", which a flat unit cannot meet. | Partly fixed: NEED-020 reworded (hangs or stands); SYS-032 now says the level starts at the LED of SYS-047. Open: fixed stand tilt away from 30 degrees, face-down behaviour, a user-set zero as an alternative. RISK-041. | Partly resolved |
| G10 | Medium | SYS-047 testing: only 90 degree steps; hysteresis (5 degrees) equals the sensor error (5 degrees); no filter for knocks; "failed sensor" undefined (no response, 0 g, frozen); "plus or minus 1 LED" is 22.5 degrees; "top" is an LED or a gap. | Accepted. Test at 20 to 60 degrees; larger hysteresis; define failure detection and non-blocking reads; define the zero LED. | Open |
| G11 | Medium | HW-011 values are not derived: cost EUR 0.5 and 0.2 mA come from no datasheet; the extended-part fee is not counted; the 5 degree budget does not say what it includes; the 12 test positions and jig accuracy are unspecified. | Accepted. Pick two candidate parts, read datasheets, do a budget line. | Open |
| G12 | Medium | The label on the back faces the wall when the unit hangs; the passphrase is needed for provisioning; MECH-006 "flat area" vs ADR "recess"; MECH-006 acceptance contains tests but its method was "Inspection"; the wipe-test count (20) differs from a note in ADR-0011 (100). | Partly fixed: MECH-006 method is now "Inspection and Test". Open: is the label readable while mounted; align the cycle counts in ADR-0011 and plan 05. | Partly resolved |
| G13 | Medium | The scoring double-counts or does not discriminate: B scores 4 for "any rotation" with 3 lock positions while A scores 2; the label criterion is 3 for all options; the sensor already removes the need for angle freedom. | Accepted. Re-score or drop those criteria before acceptance. | Open |
| G14 | Medium | All five test-case stubs are "TBD"; the coupon test of the ADR is not in TC-307 or TC-308; accessory feet, flush plate and datum plane are undefined; no regulatory check was run for accessories. | Accepted. | Open |
| G15 | Low | NEED-021 pulls the sensor into release 1 with no cost trade-off (the sensor is justified by NEED-020 alone); NEED-022 mixes solution into the need; clock mode has no 12 o'clock when flat and 16 LEDs do not match 12 hours. | Accepted. Keep open points explicit. | Open |

## Outcome
**Not ready for approval. Actions required.** Verdict (inferred, readiness pass not run): **NO-GO**. Option B may not survive G1 and G2 as drawn; the dovetail (option C) stays the fallback. The seven requirements are consistent with each other after the fixes above, but their numbers are working figures.

## Actions
Do the scale drawing and print-orientation decision first (G1, G2), then the load case and unlock torque (G5, G6), the range test with accessories (G7), and re-run the thermal model for both orientations (G8). Owner decisions: G5 (priority), G9 (stand tilt and face-down), G12 (label readable while mounted).
