# Owner decision of 2026-11-28: split ring with sharp ends (in the working session; recorded by the assistant)

Context: the mock-up of the LED ring on the 58.5 mm board (`docs/journal/2026-11-28-owner-decision-round-58-5-disc.md`) showed that a ring above 40 mm overlaps the J1 pads and that the module sits in the antenna keep-out.
The owner asked: "Could we kill 2 birds in with one stone by making the led ring to half circles, with on one side the antenna at the pcb edge and on the other the connector?"
The assistant showed the option in the mock-up (J1 and antenna 180 degrees apart, module at the board edge, antenna outside the base board, centre free for plan 09 S2) and its costs (gaps of 23.6 mm for [4] mm LED clearance, antenna 2.65 mm of plastic from the wall, LEDs about 5 mm from the antenna strip).
Owner answer, in full: **"Do a split ring ensure by the mechanical design that the edges are sharp"**.

## What was recorded
- Direction: split ring, two arcs, J1 in one gap and the module at the board edge in the other. The LED count ([24] working value) and the ring diameter ([52] mm working value, 4 mm LED clearance to the antenna strip) are not chosen by the owner yet.
- MECH-002 (Approved): approved amendment in the owner's words (two arcs instead of a closed band; sharp ends).
- MECH-014 (new, Draft): sharp ends of the light arcs, with measurable luminance criteria; TC-317 (stub). The plan 09 proposals MECH-010 to MECH-013 are untouched.
- ADR-0027 (Proposed): layout alternatives L1 to L4 and five constructions for the sharp ends (A to E); working concept A (opaque cap with two windows, two diffuser inserts, four light walls with white faces); fallbacks C and D on the same board. RISK-054 (new).
- Analysis: `mech/analysis/light_edge.py` with tests (`test_light_edge.py`): an absorbing (black) wall gives a crisp cut but only 50 % luminance at the wall, 71 % at the end LED, 90 % only 7 mm inside; a white wall face (ideal mirror in the model) gives 100 % up to the wall. Model only; no measurement.
- Mock-up updated (same artifact link): light walls, white or black faces, lit ring with hard ends.
- Not changed: MECH-001 (65 mm, to 66 mm with the ADR), SYS-001, SYS-028, SYS-032, `mech_outline.py`, the generator, the housing model, plan 05, plan 08 (revision 7) and plan 09. No code in `hw/` or `mech/freecad` was touched.

## Reading of "sharp" (to be confirmed)
The assistant read "edges are sharp" as the four ends of the two arcs and the borders of the band, not as a thin ring. The glow along each arc stays soft and even (MECH-002, owner decision of 2026-11-07). If the owner means only sharp borders, the walls and the gain table of ADR-0027 are not needed.

## Points for the owner
- Confirm the reading of "sharp", the LED count and the ring diameter, and accept or change ADR-0027 and MECH-014.
- Construction A has four housing parts instead of two (base, cap, two inserts) and replaces concept B of ADR-0011.
- The owner's printer and filaments decide fallback D (two materials in one lid). The black filament must be non-conductive near the antenna (MECH-003).
- The antenna at the board edge is a range risk (RISK-011): the 6 dB range test of SYS-038 decides, with the wall at 2.65 mm.
- After acceptance: MECH-001 to 66 mm, SYS-001, SYS-028 and SYS-032 for the new count, plan 05 and plan 09 (S2 pose with the module at the edge), plan 08 revision 7 with readiness pass 4 before any placement, then the generator, outline, keep-outs for the wall feet, housing model and the re-placement and routing of P1.
