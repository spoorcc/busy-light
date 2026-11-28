# Owner decisions of 2026-11-28: ADR-0027 accepted, MECH-015 approved (in the working session; recorded by the assistant)

Context: the owner chose the LED configuration from the mock-up (`docs/journal/2026-11-28-owner-decision-led-config-centre-leds.md`) and asked the assistant to ask for the open decisions one question at a time, each with the situation, the consequences and a recommendation. Six questions were asked; the owner took the recommendation each time.

| # | Question | Owner answer | Recorded in |
|---|----------|--------------|-------------|
| 1 | Ring LEDs (the count was read from the screenshot) | 32 (16 per arc, pitch about 4 mm) | ADR-0027, SYS-001, SYS-028, SYS-032, NEED-003 clarification |
| 2 | Module's inner end (11.9 mm) inside the button wall ring (14.6 mm) | Smaller round disc, radius about 11 mm, wall ring about 11.2 mm | ADR-0027 (Centre light), plan 09 D10 |
| 3 | Glow of the centre button | Bright centre with 4 LEDs; no extra LEDs, no reflector | ADR-0027, plan 09 D10 |
| 4 | 36 LEDs are 540 mA at full white on a 500 mA source | Keep today's LED current budget: total light unchanged, each LED about 44 % as bright | ADR-0027, SYS-001 (Draft) |
| 5 | Accept ADR-0027 | Accept | ADR-0027 status; ADR-0003, ADR-0011 and ADR-0023 superseded in part |
| 6 | Approve MECH-015 | Approve as written | MECH-015 status |
| 7 (later the same day, after the plan 08 section S review) | The module library courtyard contains the vendor antenna keep-out and would cover about 10 ring LEDs and 10 caps; the ADR-0023 rule made it a no-go area for all parts (land 910 mm2, about 20 courtyard overlaps against the waiver maximum of 14) | Body courtyard for U9 on this board (module body plus 0.25 mm; the antenna strip rule area stays) | DEV-009, DEV-004 note, plan 08 section S |
| 8 (same day, after readiness pass 3d) | **Correction of row 7.** The numbers in the question were wrong: the bounding box of the courtyard was used, not its T shape. Real: the antenna keep-out part lies beyond R 23.1, outside the movable land, so the land is the same with either courtyard; the library courtyard overlaps only LEDs D15 to D18 (4 pairs, waiver maximum 14, not extended); the inside cap positions of the end LEDs are unchanged (18 each) | Library courtyard, withdraw DEV-009 (recommended) | DEV-009 withdrawn, DEV-004 note, plan 08 section S |

Go given: after the six answers the owner said "Yes go" to the sequence 66 mm limit in the generator and placer (tests first), plan 08 revision 7, a goldfish readiness pass, then re-place and route P1. Implementation after a readiness GO was pre-approved on 2026-11-17 (answer 16 of `2026-11-17-p1-order-owner-decisions.md`).

## What changed in the records
- ADR-0027: Accepted. Ring diameter [52] mm and LED clearance [3] mm stay working values (read from the screenshot, not asked).
- MECH-015: Approved. Values in square brackets stay open until the coupon test (TC-317).
- MECH-001: approved amendment, upper limit 66 mm (65.5 mm housing), recorded as part of the acceptance of ADR-0027, which states it. The margin to the smallest ITF tennis ball (65.4 mm) is gone; 65.5 mm is below the "about 67 mm" of the SYS-028 rationale. The generator and placer limit follow, tests first.
- SYS-001, SYS-028, SYS-032 (all Draft): 32 + 4 LEDs, ring of 32 in two arcs, level steps of 3.1 %, brightness restated as a ring total (1600 mcd, about 50 mcd per ring LED, working value). The owner approves these texts.
- NEED-003: clarification line for 32 + 4 LEDs.
- Plan 09: D10 gets the owner answers (11 mm disc, bright centre); revision 10 redoes the S2 and S3 pose search.

## Not done
- No generator, outline, housing, board or firmware change except `MAX_DIM_MECH001` 66.0 in `mech_outline.py` (tests first, commit 3a9db65).
- SW requirements and firmware that assume 16 LEDs are not reviewed yet (the SYS-032 level steps and the SYS-001 count change them).
- Plan 08 revision 7 (section S) is drafted and reviewed (RV-020: comprehension, three antagonistic passes); the readiness pass decides whether S1 may start. No placement before it.
- Open for the owner from before: approval of SYS-001, SYS-028, SYS-032 texts, plan 09 questions, DEV records, plan 08 approval.
