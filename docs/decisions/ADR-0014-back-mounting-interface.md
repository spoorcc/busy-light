# ADR-0014: Mounting interface on the back of the housing

- **Status:** Proposed (only the owner sets Accepted)
- **Date:** 2026-11-04
- **Deciders / reviewers:** Ben Spoor (owner); goldfish review RV-007 (2026-11-04): not ready for approval, actions open
- **Related:** NEED-014, NEED-020, NEED-022, SYS-047, HW-011, MECH-007, MECH-008, SYS-013, SYS-028, MECH-001, MECH-003, MECH-006, ADR-0003, ADR-0011, RISK-011, RISK-005, RV-004 (finding A1)

## Context and problem
The owner decided on 2026-11-04 that the unit is mounted both horizontal and vertical (withdraws assumption A1 of plan 05), that the back of the housing gets a small interface that accepts a horizontal stand, clips or a blank plate, and that the label goes on the back. The owner first proposed a thread; this ADR weighs it against other interfaces.

Constraints that exist today:
- The floor of the base is 2.0 mm thick and lies inside the 15 mm plastic-only box around the antenna (MECH-003: no metal, magnet, screw or insert). A metal insert or magnet in the back is therefore excluded unless the antenna moves (ADR-0003 option B).
- The label with the per-unit passphrase must stay on a part that does not move and must not be covered by an accessory (SYS-013, MECH-006).
- The unit is 3D printed (FDM, ADR-0011); layer lines make printed threads weak and prone to wear.
- The unit is small (53 mm) and 16.5 mm tall; every millimetre added to the back adds to the height.
- An orientation sensor is added (owner decision 2026-11-04), so the rotation angle of the unit on its accessory need not be fixed mechanically.

Not known: the weight and leverage of the intended accessories (stand, clips); the printer and filament (O2 of plan 05); creep of PETG or ASA under a continuous load at 50 to 60 deg C (no value found); whether the antenna stays in the centre (ADR-0003).

## Decision criteria
| Criterion | Weight (1-5) | Source requirement |
|-----------|--------------|--------------------|
| Only plastic in the antenna box (gate: score 0 excludes the option) | 5 | MECH-003, RISK-011 |
| Holds the unit under load, many times, and warm (hang weight, 100 cycles, creep) | 5 | MECH-005, MECH-006 |
| Prints on FDM without supports and fits the floor and the height budget (not shown yet, RV-007) | 4 | ADR-0011, MECH-001, SYS-028 |
| Takes different accessories (stand, clips, blank plate) | 4 | owner decision 2026-11-04 |
| Attaches without tools, with one hand | 3 | DFx standard 2 |
| Works at any rotation angle (the sensor handles orientation) | 3 | owner decision 2026-11-04 |
| Keeps the label visible and protected | 3 | SYS-013, MECH-006 |
| Few parts, low cost | 3 | SYS-021 (indirect) |

## Alternatives considered

### A. Printed thread in the back (the owner's first idea)
A boss with an internal thread, for example M5 or M6, printed in the base. Accessories have a matching bolt.
Strongest case: familiar, one accessory type for many uses, no metal.
Cons: FDM threads are weak across the layers and wear; many turns to fit; the thread depth (about 5 to 6 mm) does not fit a 2 mm floor, so a boss raises the height or intrudes into the board volume; the stop angle is random.

### B. Bayonet (quarter-turn) with printed lugs
A shallow round recess in the back with three lugs; the accessory has matching ramps and turns by about 30 to 45 degrees to lock. Lug height about 1.2 mm; a bump and a notch hold the lock.
Strongest case: no metal, tool-free, one hand, shallow (fits the floor), prints without supports with chamfered lugs, and loads act across the lugs in shear instead of along weak layer lines.
Cons: a custom standard (no off-the-shelf accessories); the lock detent is printed plastic and can creep when warm; locked positions are fixed (for example 3 or 4), not any angle.

### C. Dovetail slide plate
A short rail or dovetail slot on the back; accessories slide in.
Strongest case: strongest hold under load, and it fixes the direction (which would define "up" when the unit lies flat).
Cons: needs a raised rail or a deep slot (height); overhang needs supports or careful angles; a rectangular feature on a 53 mm round back takes space; the rotation angle is fixed by the accessory.

### D. Magnet plate
Magnet in the back, steel plate on the accessory.
Strongest case: easiest to use.
Excluded by the gate: a magnet in the floor lies inside the 15 mm plastic-only box (MECH-003), and the magnet can disturb a later magnetometer.

### E. Tripod socket (1/4-inch-20) with metal insert
Strongest case: the standard camera thread gives a large ecosystem of stands and clamps.
Excluded by the gate: a metal insert in the antenna box. It is also too deep for a 2 mm floor (the standard thread needs about 6 mm).

### F. Keyhole slots only (no accessory interface)
Strongest case: nearly free and strong enough for hanging on a screw.
Cons: no stand, no clip, no blank plate, no tilt.

### G. Do nothing / defer
The back stays flat. It blocks the plan 05 revision, the label place and the thermal case for both orientations. Not possible.

## Comparison
Scores 0 to 5, my judgement; nothing is printed or tested. The totals come from the weights above (max 150).

| Criterion (weight) | A | B | C | D | E | F | G |
|--------------------|---|---|---|---|---|---|---|
| Plastic only (5) | 5 | 5 | 5 | 0 | 0 | 5 | 5 |
| Load, cycles, warm (5) | 2 | 4 | 5 | 3 | 5 | 3 | 0 |
| FDM and height (4) | 3 | 4 | 3 | 4 | 2 | 5 | 0 |
| Accessories (4) | 3 | 4 | 4 | 4 | 5 | 1 | 0 |
| Tool-free, one hand (3) | 2 | 5 | 4 | 5 | 2 | 4 | 0 |
| Any rotation angle (3) | 2 | 4 | 2 | 4 | 3 | 1 | 0 |
| Label kept visible (3) | 3 | 3 | 3 | 3 | 3 | 3 | 0 |
| Parts and cost (3) | 4 | 5 | 5 | 4 | 2 | 5 | 5 |
| **Weighted sum (max 150)** | 92 | **128** | 120 | 95 (excluded) | 83 (excluded) | 103 | 40 |

Sensitivity: B stays first when any single weight changes by 2 up or down. B leads C by 8, which is inside my scoring error; the lead shrinks to 1 point if C scores 4 on FDM and height and 3 on rotation (C then totals 127). The coupon test, not the table, decides between B and C.

## Decision
Choose **B, a printed bayonet**, with these design rules. Items in brackets are working values.
1. **Plastic only.** No metal, magnet or insert in or on the back (MECH-003). Accessories may contain metal only outside the 15 mm box (for example a clip spring); an accessory that clips on does not count as part of the housing.
2. **Geometry.** Round recess of [30] mm diameter and [1.5] mm depth centred on the back, three lugs at 120 degrees, lug height [1.2] mm, lock turn [30] degrees, detent bump [0.4] mm. All wall thicknesses are whole numbers of 0.4 mm perimeters. No supports; the lug undersides are chamfered at 45 degrees.
3. **Accessories.** Standard set: blank plate (closes the recess, flush), horizontal stand (tilt angle chosen with the orientation sensor, see ADR-0011 revision), wall clip or screw plate. The accessory standard is part of this repository (mech, Apache or CC BY-NC-SA per ADR-0013).
4. **Label.** The label lies in a separate recess outside the bayonet recess, on the back. Accessories do not cover it. The passphrase label is never on a swappable part.
5. **Orientation.** The bayonet allows [3] lock positions. The orientation sensor reports the real angle, so no mechanical zero is needed (see Orientation in the consequences).
6. **Wear and creep.** The lug and detent are checked by a coupon: [100] attach and detach cycles at room temperature and after a soak at the hottest internal temperature plus [15] K of margin to HDT (MECH-005). If the lug creeps or breaks, fall back to C.

## Consequences
- Positive: no metal near the antenna; tool-free; shallow; one interface for stand, clips and plate; leaves the label on the back free.
- **Negative / trade-offs accepted:** a custom interface (no standard tripod accessories); accessories must be printed or made; lock positions are discrete; a stand holding a heavy load is not claimed; the lug on a 2.0 mm floor may need local thickening, which adds height.
- New risks (add to the risk register after the owner confirms): lug creep or fracture when warm; accessory loosens and the unit falls; accessory cover blocks the label; accessory with a metal part near the antenna after the user mounts it (a marking or manual warning).
- Requirements created or changed: MECH-007 (back interface) and MECH-008 (retention), MECH-006 rewritten (label on the back, not covered), NEED-020 to NEED-022, SYS-047 and HW-011 (orientation sensor), all Draft. Still to do: changes to ADR-0011 and plan 05 (height, thermal in both orientations, label recess).
- Orientation: an accelerometer gives the direction of gravity. It tells vertical from horizontal and the rotation when the unit hangs. When the unit lies flat with the ring up, gravity gives no direction in the plane, so "automatic" is not possible with this sensor. A magnetometer gives a compass direction, not a useful zero. The proposed automatic rule: when the unit lies flat, the zero position is fixed on the board (12 o'clock opposite the USB-C connector, so the cable comes toward the viewer); when it hangs or stands, gravity sets the zero. The owner can confirm or change this in the requirement.

## Verification and revisit
- Coupon test (plan 05 increment 1): attach and detach [100] cycles, a pull-off test at room temperature and after a heat soak, a hanging load test with the heaviest planned accessory.
- Revisit when: the coupon fails the heat soak or the cycles (then C); the antenna moves to the board edge (ADR-0003 B), which would allow a metal insert and option E; the owner needs standard tripod accessories; the floor thickness or height changes.

## Review findings still open (RV-007)
The goldfish review of 2026-11-04 found problems that can invalidate this option as drawn; the status stays Proposed.
- **Layout:** a centred 30 mm recess leaves a ring (53 - 30) / 2 = 11.5 mm wide, so a 20 mm label does not fit beside it. The recess, the label and the feet need a scale drawing first.
- **Floor:** a 1.5 mm recess in a 2.0 mm floor leaves 0.5 mm, which is not a whole number of 0.4 mm perimeters, and the lug and recess values are not multiples of 0.4 mm either.
- **Print orientation:** with the floor on the bed, the recess is a bridge. "No supports" is not shown.
- **Release:** a 30 degree turn unlocks the unit, so a knock or turning it by hand can release it.
- **Load case:** the 10 N pull-off figure has no derivation; a stand loads the lugs in moment and shear.
- **Antenna:** any accessory on the back lies inside the 15 mm box; the range test has no accessory case.

## Critical review notes
Strongest objection: "A custom bayonet means no existing accessories; the owner's thread or a 1/4-inch tripod socket would give many for free."
Answer: a metal insert is excluded by the antenna rule, and a printed thread is weaker and does not fit a 2 mm floor. The accessory set is small (plate, stand, clip), so the custom interface costs little. If the antenna moves to the edge, revisit E.
Second objection: "An FDM bayonet lug in PETG can creep and fail in a warm unit." Answer: accepted as a risk. The coupon tests it after a heat soak, and C is the fallback.
