# Owner decision of 2026-11-28: LED configuration of the split ring and four LEDs under the centre button (in the working session; recorded by the assistant)

Context: after the answer "Of the light I mean" (sharp edges are the edges of the light, `docs/journal/2026-11-28-owner-decision-split-ring.md`) the assistant asked for the LED count and the ring diameter.
The owner sent a screenshot of the mock-up (https://claude.ai/artifact/DZPYe64pzByRHY9mYfr2Mp, phone view: half circles on, white faces on, LED clearance 3 mm, ring diameter 52 mm) and wrote, in full: **"This is what I want + 4 LEDs in the center under the translucent button"**.
The LED count slider is cut off in the screenshot. The assistant read 32 ring LEDs from the screenshot (16 LEDs on the visible upper arc, pitch about 4 mm) and asks the owner to confirm.

## What was recorded
- Configuration: [32] ring LEDs in two arcs of 16 on a [52] mm ring, [3] mm LED clearance to the antenna strip, white faces on the light walls, J1 and the module in the two gaps (gaps 21.6 mm between the end LEDs), plus [4] LEDs under a translucent centre button: 36 LEDs.
- ADR-0027 (Proposed) now carries these working values and a section "Centre light"; MECH-015 (Draft) covers the border of the centre button too.
- Reversal: this reverses plan 09 D7 (disc dark, owner 2026-11-24) and the first answer of the project ("Light should come from the ring/rim not the center"). Plan 09 gets D10; ADR-0026 gets a note. Nothing else of plan 09 or ADR-0026 was changed.
- Mock-up (same link, version 4): four centre LEDs with a radius slider, the opaque wall ring round the button, the lit centre, and the owner's configuration as the default and as a preset.

## Findings from the mock-up (model, not measured)
- The module at the board edge collides with the wall ring of the button: its inner end is 11.9 mm from the axis, the wall ring is at r about 14.6 mm.
- Four LEDs give a bright centre, not an even disc: +-62 % inside r 13 at 6 mm LED radius, +-49 % at the best radius (9 mm). Eight LEDs on r 9 give +-29 %.
- 36 LEDs are 540 mA at full white on a source of 500 mA; the per-LED ceiling is 44 % of the 16-LED figure. The 100 mcd per LED of SYS-001 needs a new check.
- The 32 ring LEDs divide into quarters (8 each).

## Points for the owner
- Confirm 32 ring LEDs and 3 mm clearance.
- The module collision with the button: flat on the disc, smaller disc (about 11 mm radius) or another module position.
- An even disc (more LEDs or a reflector) or a bright centre fading outwards.
- Accept or change ADR-0027; approve or change MECH-015.
- Not changed yet: MECH-001 (65 mm, to 66 mm), SYS-001, SYS-028, SYS-032 (the 16 LEDs of the texts), the generator, the housing model, plan 08 revision 7.
