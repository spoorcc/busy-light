# ADR-0027: Split LED ring on a round 58.5 mm board, module at the board edge, sharp light edges at the gaps

- **Status:** Proposed (owner decisions of 2026-11-28: round 58.5 mm board, "Do a split ring ensure by the mechanical design that the edges are sharp"; the owner has not accepted this ADR, the LED count and the ring diameter)
- **Date:** 2026-11-28
- **Deciders / reviewers:** owner (Ben Spoor); written by the assistant; no goldfish review yet
- **Related:** SYS-001, SYS-028, SYS-032, MECH-001, MECH-002, MECH-003, MECH-014 (new, Draft), HW-017, HW-005, ADR-0003, ADR-0011, ADR-0023, ADR-0026, DEV-004, RISK-011, RISK-054 (new), plan 05, plan 08, plan 09, `docs/journal/2026-11-28-owner-decision-round-58-5-disc.md`, `docs/journal/2026-11-28-owner-decision-split-ring.md`

## Context and problem
The droplet nose of 2026-11-27 does not give a clean placement: with every setting that adds length, the placer misses the 8.0 mm rule R22 to J1 VBUS, and the best result is the 20 mm nose without extra length (2 of 4 clean at penalty 3000, `docs/verification/reports/p1-placement-feasibility.md` section 6.1).
The cause is the ring: the 40 mm ring leaves 3 mm to the rim of the 46 mm board, so J1 (pads from R 22.76 mm outwards, mouth 8.89 mm ahead of the rear pad edge) cannot sit on the board and needs the tab or nose.
On 2026-11-28 the owner chose a round 58.5 mm board without a nose (housing 65.5 mm: board radius 29.25 mm, radial gap 1.90 mm, wall 1.60 mm, plan 05 dimension chain; J1 mouth at the wall, R 31.65 mm).
The owner then asked for a split ring (two arcs, the connector in one gap and the antenna at the board edge in the other) and for sharp edges, "ensured by the mechanical design".
A mock-up of the layout is in the journal entry of 2026-11-28 (artifact; numbers from `mech_outline.py`, the generator and the paper power budget; the keep-out half width and the light model are estimates).

What the layout gives (mock-up, working values [24] LEDs on a [52] mm ring, [4] mm LED clearance to the antenna strip): two arcs of 126 degrees with 12 LEDs each, pitch 5.2 mm, gaps of 23.6 mm between the end LEDs at J1 and at the module, 360 mA at full white (15 mA per LED), a per-LED ceiling of 2/3 of today's at the same current budget.
The ring is no longer in the way of J1 (J1 sits in a gap), and the module sits at the board edge with the antenna outside the base board, which is the first choice of the Espressif hardware design guidelines (plan 05 section 4.6). The antenna keep-out of 15 mm lies off the board, the slot and the module offset of ADR-0023 are not needed, and the centre is free for the switch of plan 09 (S2, module moved).

What "sharp" needs. A hard cut alone is not enough. A model of point sources (Lambertian, 8 mm to the diffuser, pitch 5.2 mm, 12 LEDs, end LED half a pitch from the wall; `mech/analysis/light_edge.py`, tests in `test_light_edge.py`) gives:

| End construction | Luminance at the wall | at the end LED (2.6 mm) | reaches 90 % of the arc mean at |
|---|---|---|---|
| Opaque wall, absorbing (black) | 50 % | 71 % | 7.0 mm |
| Opaque wall, white face (ideal mirror in the model) | 100 % | 100 % | at the wall |

The edge of an absorbing wall is crisp, but the arc looks faded over its last 7 mm, because the end LEDs have a neighbour on one side only. A white wall face removes the fade. A real white face reflects less than the ideal mirror in the model, so a per-LED gain for the two end LEDs of each arc is the second measure (firmware table, headroom exists: the 500 mA budget leaves 5 to 58 % of full white, `spike-7-5-power-budget-paper.md`).
The housing must also stop the plate from guiding light sideways: the translucent lid of concept B (ADR-0011) is one plate over both arcs and both gaps, and a translucent plate spreads light sideways, so its glow has no sharp end whatever is under it.

Constraints: the owner decisions of 2026-11-07 (wide glow along the band, concept B) and plan 09 D7 and D8 (centre disc dark, light from the ring only, Apple-grade look); MECH-003 (only non-conductive plastic in the 15 mm box around the antenna: no metallic paint, no carbon-fibre or other conductive filament; the walls at the antenna gap are inside that box); FDM tolerance 0.30 mm (plan 05); the printer and filaments of the owner are not known (ADR-0011).

Not known: the optical density of any printed black or white wall at [0.8], [1.2], [1.6] mm; the real reflectance of a printed or painted white face; whether the owner's printer can print two materials; the transmission of the diffuser insert; the range loss with the antenna 2.65 mm (plastic) from the wall (RISK-011, TC-303); the LED count and ring diameter (owner).

## Decision criteria
| Criterion | Weight (1-5) | Source requirement |
|-----------|--------------|--------------------|
| Sharp ends: luminance 1 mm inside at least [90] %, 3 mm outside at most [2] %, edge at most [1.5] mm | 5 | MECH-014 (new), owner request 2026-11-28 |
| Only non-conductive plastic near the antenna | 5 | MECH-003 |
| Apple-grade look: flush, even narrow seams | 5 | plan 09 D8 |
| Print feasibility and tolerance (FDM 0.30 mm, printer unknown) | 4 | MECH-001, plan 05 |
| Even glow along the arc, no point source | 4 | MECH-002 |
| Centre disc dark, light from the ring only | 3 | plan 09 D7 |
| Part count, cost and assembly | 3 | plan 05 |
| Change to approved texts and decisions | 2 | process |

## Alternatives considered
Two decisions are in this ADR. The layout (split ring) is the owner's decision of 2026-11-28 and is recorded here with the alternatives it replaced. The construction that makes the edges sharp is open and is compared in the table.

### Layout
- **L1 Droplet nose and continuous ring (2026-11-27).** Replaced. Strongest case: the housing stays at 59.24 mm and the ring is closed. Against: no clean placement with any setting tried; the nose needs new outline, hook, panel-tab and housing work.
- **L2 Round board, continuous Ø40 ring, J1 behind the ring.** Strongest case: no gap, the ring stays as today, 16 or 24 LEDs fit. Against: a dark 9 mm rim around the ring, which the owner does not want ("light from the ring and the rim"); the module stays in the keep-out conflict (2 LEDs in the vendor box).
- **L3 Round board, rim ring Ø52 open at J1 only.** Strongest case: a single gap, 23 LEDs. Against: the module stays inside the ring with 2 LEDs in its keep-out and the slot.
- **L4 Split ring, module at the board edge (chosen by the owner).** Two gaps, J1 and the antenna 180 degrees apart.

### Construction of the sharp edges
- **A. Opaque cap with two windows, two diffuser inserts, four radial light walls with white faces.** The walls rise from the base or the cap to the cap underside at each gap end, [1.2] mm thick, about [9.4] mm either side of the gap axis (end LED half a pitch inside), white faces. The window edge of the cap defines the visible edge; a lip of the cap overlaps the insert so that no seam shows. Parts: base, cap, two inserts (4). This is concept A of ADR-0011, adapted, and it also masks the centre (plan 09 D7).
- **B. One translucent lid (concept B), light walls under the lid only.** Strongest case: two parts, the approved concept, the cleanest look. Against: the plate guides light sideways, so the ends stay soft whatever is under it. Excluded by the gate: it cannot meet MECH-014.
- **C. One translucent lid with an opaque mask (film, ink or paint) between the arcs, walls under the lid.** Strongest case: two parts plus a mask. Against: the mask edge and registration (+-0.3 mm) set the edge, the mask material near the antenna must be non-conductive (no metallic ink, no metallised film), and an Apple-grade crisp mask edge needs a process the owner has not named (plan 09 question 10).
- **D. One lid printed in two materials (opaque and translucent) in one part.** Strongest case: one part, no seam. Against: the printer is not known; material bleed at the boundary is 0.2 to 0.4 mm; adhesion of the two materials is unproven.
- **E. Do nothing.** Keep concept B and accept soft ends. Fails the owner's request.

## Comparison
Scores 0 to 5 are the assistant's judgement from the text above; nothing was measured. B scores 1 on a gate criterion (sharp ends) and is excluded whatever its sum.

| Criterion (weight) | A | B | C | D | E |
|---|---|---|---|---|---|
| Sharp ends (5) | 5 | 1 | 4 | 4 | 0 |
| Antenna, non-conductive (5) | 4 | 4 | 3 | 3 | 4 |
| Apple-grade look (5) | 3 | 4 | 3 | 4 | 4 |
| Print feasibility (4) | 3 | 4 | 3 | 1 | 4 |
| Even glow (4) | 4 | 3 | 3 | 3 | 3 |
| Centre disc dark (3) | 5 | 3 | 4 | 5 | 3 |
| Part count and cost (3) | 2 | 5 | 4 | 5 | 5 |
| Change to approved texts (2) | 2 | 5 | 4 | 4 | 5 |
| **Weighted sum (max 155)** | **113** | 107 (excluded) | 106 | 109 | 102 (excluded) |

The margin between A, C and D is small (7 points) and rests on unmeasured numbers. The coupon test, not the sum, decides.

## Decision
We propose the split ring (L4, the owner's decision) with construction A as the working concept, with C and D as fallbacks that use the same board:
1. **Board.** Round 58.5 mm board, J1 in one gap, module at the board edge with the antenna end flush with the edge at the module corners (x = -28.50 mm), ring in two arcs, [24] LEDs on a [52] mm ring, [4] mm LED clearance to the antenna strip. The gaps are equal. The end LED of each arc sits half a pitch from its light wall. The four wall feet are keep-out strips for parts on the board (foot [1.2] mm plus [0.5] mm clearance either side).
2. **Housing.** Construction A: opaque cap with two windows, two diffuser inserts of [1.2] mm, light walls with white faces. Wall and cap material non-conductive and non-metallic (MECH-003); the black filament is checked for conductivity before use.
3. **Light.** A per-LED gain table in firmware for the two end LEDs of each arc, tuned from the coupon and lid photos. It is the second measure; it does not replace the white faces.
4. **Gate.** MECH-014 and TC-317: sector coupons first (wall thickness [0.8], [1.2], [1.6] mm, black core, white face against black face, optical density of each wall), then the finished lid. A fails the gate when the edge needs more than [1.5] mm or the gap luminance is above [2] %; then C or D is tried on the same board.
5. The ring is not a decision yet: the owner chooses the LED count and the ring diameter (the mock-up shows [24] on [52] mm and [24] on [44] mm).

## Consequences
- Positive: J1 and the antenna both leave the crowded area; the antenna follows the vendor's first choice and DEV-004 (keep-out overlap) can close for the module (the LED and track clearances to the antenna remain a layout deviation); the nose, its outline, hook, panel-tab and housing work is not needed; the centre is free for plan 09 S2; the placement region is larger (free board area about 1400 mm2 against about 650 mm2, an estimate).
- **Negative / trade-offs accepted:** four housing parts instead of two (concept A instead of B); MECH-002 "closed band" becomes two arcs; two dark gaps in the lit ring and an arc fill (SYS-032) that runs through them; a larger housing, 65.5 mm (MECH-001 limit 66 mm); eight more LEDs with their capacitors and a lower per-LED ceiling at 500 mA; the antenna is 2.65 mm of plastic wall from the housing and the LEDs are about 5 mm from the antenna strip, against the vendor's 15 mm, so the 6 dB range test decides (MECH-003); a white wall face and a per-LED gain table are extra tuning work.
- New risks (add to risk register): RISK-054 (sharp edges not reached: light through the walls, dim ends, seam light); RISK-011 (antenna detuning) gets a new cause (wall at 2.65 mm).
- Requirements created or changed: MECH-014 (new, Draft); MECH-002 amended by the owner (closed band to two arcs, recorded); MECH-001 limit 65 to 66 mm with this ADR's acceptance and the generator change; SYS-001, SYS-028 and SYS-032 (LED count, ring, quarter steps) when the owner chooses the count; TC-317 (stub); HW-017 and plan 08 revision 7 (placement region, keep-outs, module position); plan 05 and plan 09 (pose search of S2 with the module at the edge: inner end 11.9 mm from the axis, 2.1 mm inside the 14 mm support circle). On acceptance ADR-0003 (module position) and ADR-0023 item 5 (module offset) are superseded in part, and the status lines are updated then.

## Verification and revisit
Evidence so far is a model and a layout mock-up; nothing is printed or measured. Confirm with: TC-317 (edge profile on sector coupons, then the lid), TC-302 (diffuser), TC-303 and the range test of SYS-038 (antenna at the edge, wall at 2.65 mm), the generator check of the keep-outs and the housing size (65.5 mm), the placer run on the new region (plan 08 revision 7, readiness pass 4), the plan 09 coupon gate.
Revisit when: a coupon cannot reach [1.5] mm or [2] % with A (try C or D); the range loss is above 6 dB (move the module inwards, accept the slot again); the owner's printer is found to print two materials (D); the owner changes the LED count or the ring diameter.

## Critical review notes
Strongest objection: the owner decision of 2026-11-07 asked for a wide glow, not a sharp ring (MECH-002, ADR-0011 item 6), and concept A was a fallback. The answer is that this ADR reads "sharp" as the ends of the two arcs and the borders of the band, not as a thin ring: the glow along each arc stays soft and even, the windows define the ends. The owner confirmed on 2026-11-28 that the edges meant are the edges of the light ("Of the light I mean"), so the ends and the borders of the lit arcs. Whether the glow along each arc stays soft was not asked and is assumed from MECH-002. The window of the cap also sets the inner and outer border of each arc, so MECH-014 covers them.
Second objection: a hard cut with 50 % luminance at the end looks worse than a soft fade. The answer is the model above: black walls would do exactly that, so the white faces and the gain table are part of the decision, not options.
Third objection: the antenna 2.65 mm from the wall breaks the 15 mm goal. The answer is MECH-003: 15 mm to the wall is a goal, the 6 dB range test is the criterion, and the vendor prefers an antenna outside the board.
