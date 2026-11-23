# 09 -- Centre-of-ring button (design doc)

- **Status:** Draft (revision 1 of 2026-11-23; interview answers in section 0; no goldfish review yet)
- **Date:** 2026-11-23  **Owner:** Ben Spoor (author: assistant)
- **Area:** mech (with hw and sw consequences)
- **Requirements addressed:** SYS-017 (Draft, unchanged), HW-007 (Draft, change proposed), MECH-004 (Approved, change
  proposed), MECH-002, MECH-003, MECH-001 (Approved, read for constraints), HW-008 (Approved). New: MECH-010 (proposal).
- **EGM review record:** pending (comprehension / antagonistic / readiness; to be recorded as RV-018)
- **Decides:** where SW1 sits on P1 (input to plan 08 revision 6 and the re-placement), the housing change for the
  button, and the support concept of a 30 mm button disc.

## 0. Owner interview of 2026-11-23 (in the working session; recorded by the assistant)
Background: decision 9 of 2026-11-22: "Change mechanics so the entire center of the ring becomes the button. Change the
button choice and mechanics etc to accommodate this" (`docs/journal/2026-11-22-owner-decisions-p1-rework.md`).

| # | Question | Owner answer |
|---|---|---|
| 1 | Which part is pressed | A separate centre disc inside the LED ring; the ring band and the lid stay fixed |
| 2 | Where the switch sits (the module is at the ring centre) | "Study both in the plan": a switch off the centre, and the module moved so that the switch is at the centre |
| 3 | Look and feel | A clear click, disc in the same translucent PETG as the lid, centre not lit on its own |
| 4 | Timing | Settle the concept first, then re-place P1 (plan 08 revision 6). P1 is not ordered before that |

## 1. Problem definition
SYS-017 and NEED-008 give the device one button. Today SW1 is a TL3342-family tact switch (E-Switch TL3342F160QG,
C2886898) that sits inside the LED ring on the stored board-p1 at 13 mm from the board centre, and the housing has a
side hole at azimuth 240 degrees ([7.0] mm, plan 05 section 4.3 row "btn"). The owner wants the whole centre of the ring
to be the button: one large disc that is pressed anywhere. Why now: the place of SW1 and the part choice set the input
of the re-placement of P1; a new placement made before this decision would be redone.
Out of scope: the placement itself (plan 08 revision 6), the gate and current-limit work (ADR-0024, ADR-0025), the press
lengths of SYS-017, capacitive touch (not chosen), the diffuser thickness and ring light path (MECH-002, TC-302 stay as
they are), the rear bayonet and accessory (MECH-007).

## 2. Constraints, facts and assumptions
Facts (read from the repository, not measured):
- LED ring: 16 LEDs, ring D 40 mm (LED centres), 2020 package (2.0 mm), phase 3.75 degrees (`hw/kicad/spike-gate/src/mech_outline.py`).
  The inner LED edge is at about 19 mm from the axis, so the free circle inside the ring has a radius of about 19 mm.
- Module ESP32-C3-MINI-1 (13.2 x 16.6 x 2.4 mm) sits at the ring centre on the stored board-p1 (centre 2.4 mm off the board
  centre, antenna end toward -X). Nearest LED centre to the antenna area (4.6 x 13.2 mm strip): **7.6 mm** by the
  assistant's scratch calculation (plan 05 quotes about 9.5 mm for the unshifted module and a 5.4 mm antenna strip; the 2.4 mm shift and the 4.6 mm strip explain the difference).
- Z chain (`mech/analysis/housing_params.py`): PCB top 6.6 mm, LED top 7.25 mm, module top 9.0 mm, lid underside 15.25 mm,
  lid plate 1.2 mm. Free height over the module under the lid: 6.25 mm. Lid joint: spigot and 3 snap hooks at 60, 180, 300 degrees.
- Switch: footprint family TL3342 (4.5 x 3.5 mm body); the force variant F160 means 160 gf, about 1.6 N (**assumption**, the
  datasheet is not read; travel taken as 0.25 mm, also an assumption). `sourcing.py` marks the force as an assumption.
- Press functions: short, [3] s (configuration AP), [10] s (factory reset after a ring confirmation) (SYS-017, A8).
  During a 3 s or 10 s press a hand lies over the antenna.
- HW-008: all SMD on one side, so a switch under the board is not allowed. MECH-003: plastic only in the 15 mm box
  around the antenna; the disc, arms and plunger are plastic.

Assumptions (goldfish: challenge):
- **A1** The disc is cut from the lid plate (one printed part, natural or white translucent PETG, plate [1.2] mm).
- **A2** PETG modulus, yield and fatigue are unknown for the owner's filament; E = 1.5 GPa and yield 40 MPa are working
  values, replaced by a coupon test (TC-310 step 1).
- **A3** The disc is stiff compared with its supports (checked by FEM or a coupon).
- **A4** "Pressed anywhere" means anywhere inside a usable radius R_use = [13] mm of the disc centre (a finger pad is
  about 15 mm wide); the outer 3 mm of the disc is an edge zone that need not actuate.
- **A5** The owner accepts an FDM tolerance of +-0.3 mm on features and +-0.3 mm on the lid position on the spigot (plan 05 A7).
- **A6** A finger over the antenna during a press is accepted if the link recovers; TC-312 measures the loss.

## 3. Alternatives considered
Significant and costly to reverse: the choices go to ADR-0026 with scores. Findings below come from the assistant's scratch
calculations (Python in the session scratch folder, **not in the repository, so not yet evidence**; step 1 replaces them
by tested scripts).

### 3.1 What is pressed (owner answered in the interview; recorded for ADR-0026)
| Option | Idea | Verdict |
|---|---|---|
| **A** Separate centre disc | The disc is a cut-out of the lid plate; ring band and lid fixed | **Owner choice** |
| B Whole lid moves | The lid floats on the spigot; ring and centre move together | Not chosen; the diffuser plate and snap hooks carry the load |
| C Touch | Capacitive centre, no movement | Not chosen; ESP32-C3 has no touch input, needs a part |
| D Do nothing | Side button as today | Rejected by decision 9 |

### 3.2 Where the switch sits (owner: study both)
| Option | Idea | First-order finding |
|---|---|---|
| **S1** Switch off the centre | Module stays; the switch sits in the ring free circle beside it; the disc presses it through a plunger | Keeps the antenna at 7.6 mm from the nearest LED. The disc must act as if pressed at the switch (section 3.3) |
| **S2** Module moves, switch at the centre | Switch at the true centre, symmetric support | The module can only fit if it is pushed against the ring: **320 module positions on a 0.5 mm / 3 degree grid** (gap 0.5 mm to LEDs, 1.0 mm to the switch), and the best antenna-area to nearest-LED distance is **3.6 mm** (7.6 mm today). It reopens ADR-0003 and DEV-004 |
| S3 Switch under the board | Switch on the back, plunger through the board | Breaks HW-008 (all SMD on one side); rejected |
Lean: **S1**. S2 takes antenna margin away from ADR-0003 option A, which the owner accepted on the condition of the range test (spike 7.2), for the sake of a symmetric disc; 3.6 mm is less than half of today's 7.6 mm.
The owner decides in ADR-0026.

### 3.3 How a 30 mm disc is supported (new, found while studying 3.2)
Model: a rigid disc on linear supports, displacement w = a + b x + c y, force F at any point (statics only).
Findings (400 random press points inside a disc of radius 15 mm; three supports of 1.0 N/mm and a switch of 0.5 N/mm in check 1; supports on a circle of radius 14 mm in check 2):
1. **Centroid rule.** If three equal supports have their centroid under the plunger, the plunger travel is F/(3k + k_switch)
   for **every** press point (ratio max/min 1.000 in the check). With three supports centred on the disc and the switch
   off the centre, the plunger travel per newton ranged from -0.12 to 0.62 mm/N: pressing on the far side lifts the plunger.
2. **Compliant bridges tilt.** Three soft bridges in the lid plate (k = 0.2 N/mm each, the stiffness of a 25 mm long, 1.2 x 1.2 mm
   PETG arm by the guided-beam formula 12 E I / L^3 with A2) and a switch at the centre (1.6 N over 0.25 mm): actuation at 1.75 N,
   but an edge press moves the press point **7.9 mm**. With 2 N/mm bridges: 3.1 N and 1.6 mm; with 20 N/mm: 16.6 N and 0.97 mm.
   A disc on a lone switch and bridges does not give "press anywhere" with usable force and stroke.
3. Concepts that remain (ADR-0026 compares them; none is chosen here):
   | Concept | Idea | Open cost |
   |---|---|---|
   | **M2** Guided disc | Disc with a skirt sliding in a bore of the lid ring; plunger spring or soft tip in series | Binding at the edge (clearance 0.35 mm over a short skirt), friction, FDM bore tolerance |
   | **M3** Rigid disc on three switches in parallel | Three SW footprints at 120 degrees under the disc, all on BTN_SW; the disc is held down by 3 light spring tabs | 2 more switches and pads inside the ring (area, placement), actuation force 1.6 N at a switch edge up to about 4.8 N at the centre (F/3 per switch) |
   | M1 Compliant bridges only | As in finding 2 | Fails by the model unless a tilt guide is added; kept as the baseline |
   | M4 Central pivot | Disc rocks on a post at the centre | The module is at the centre; only S2 allows it |
4. **Stack tolerance.** PCB position +-0.3, lid position +-0.3, disc and plunger +-0.3, switch height: the sum is of the order of
   +-0.8 mm against a 0.25 mm switch travel. The plunger needs a series compliance (a printed spring tab, stiffness well
   below the switch's 6.4 N/mm) or an adjustment; the free gap at the worst case must stay above zero so that the unit never
   rests on the switch. This sets the disc stroke (about 1 mm) and the feel; step 1 computes it with `mech/analysis/check_tolerance.py`.

## 4. Technical plan
### 4.1 Working concept (not yet decided; the plan fixes what every variant must meet)
- Disc diameter [30] mm, top surface [0.3] mm below the lid band (a flat desk or hand-laid object touches the band, not the
  disc; the recess also marks the button by touch), separated from the band by a gap [0.8] mm wide (through-slot with a stepped
  light seal, or a score line with a [0.4] mm skin; coupon decides).
- Stroke to the click [0.3 to 1.0] mm (stack), hard stop at [1.2] mm that carries any press above the switch force, so that
  a [20] N press cannot overload the switch or the arms (**[20] N is an assumption** for MECH-010).
- Actuation force [2] to [4] N at any point inside R_use (target for MECH-010; the owner asks for "click"); click felt and heard.
- Plunger axis, switch and (for M3) the three switches lie inside the free circle; nothing taller than 4.0 mm stands on the board
  under the disc (6.25 mm free under the lid at the module, minus 1.2 mm stroke and 1 mm margin). The disc needs no board
  keep-out except the plunger column (r = [2.5] mm around the switch centre).
### 4.2 Electrical (HW-007)
GPIO5, R12 and TVS2 stay as they are (BTN_SW, no external pull-up, the firmware enables the internal pull-up, no strapping
pin). M3 puts three switches in parallel on BTN_SW (a press is any closed contact). The ESD path is plastic, so a finger or
an air discharge does not reach the contacts; TC-207 stays; the ESD test case that ADR-0024 planned includes the disc.
### 4.3 Antenna (MECH-003)
Disc, arms, guide, stops: plastic only. Switch body is metal; put it on the side of the module away from the antenna end
where the placement allows (a soft rule, not a pass criterion). The disc lies 8.65 mm above the antenna plane; a finger on
it detunes the antenna during the press: TC-312 measures the loss (A6).
### 4.4 Light (MECH-002)
The slot or score line lies at radius [15 to 16] mm, 3 to 4 mm inside the LED inner edge. LED light can leak through a
through-slot as a bright arc: use the stepped seal or the skin; TC-302 is extended by a photo at 1 m and 0.5 m (the disc
may show ring spill; it must not show a hard line).
### 4.5 Firmware and system
No change to SYS-017 press lengths. A large disc can be held by an object on the lid (stuck press): proposal for the owner,
not in this plan's scope to decide: a press longer than [30] s is ignored until release (SW requirement, with a test). The factory
reset keeps its confirmation pattern (SYS-017), so a stuck press cannot reset the unit silently.
### 4.6 Housing and board interface (inputs to plan 08 revision 6)
- Placer rule for SW1 (and SW1B, SW1C for M3): inside the disc circle at radius at most R_disc - 4 mm; the plunger column of
  r = [2.5] mm has no other part on the board. For S1 the switch is on the +X side of the module (rear end) where possible.
- Lid: disc, slot or score, support (bridges, guide or spring tabs) and the plunger underside; base: no change except the stop
  ribs if the stop sits on the base (decided by ADR-0026).
- Plan 05: row "btn" and "az_btn" are replaced; O8 is answered; section 4.5 gets a pointer.

## 5. Detailed implementation plan
Implementation starts only after the owner approves MECH-010 and the HW-007 and MECH-004 changes (rule 1).
**Files to create**
- `docs/decisions/ADR-0026-centre-button-concept.md` (actuation, switch place, support concept, with scores).
- `mech/analysis/button_disc.py`: `plate_on_supports(supports, load_xy, force) -> (a, b, c)`, `plunger_travel(...)`,
  `actuation_force(...)`, `edge_travel(...)`, `guided_beam_stiffness(E, w, t, L)`, `guide_binding_force(clearance, skirt, diameter, mu)`,
  `parallel_switch_force(...)`; test file `mech/analysis/test_button_disc.py` (CI step `scripts/ci_mech.sh`).
- `mech/analysis/button_geometry.py` (or a function in `hw/kicad/spike-gate/src/button_zone.py`, decided at step 1): the S2
  feasibility search and the antenna-to-LED distance, with tests that reproduce 7.6 mm (P1 place), 320 positions and 3.6 mm.
- `hw/kicad/spike-gate/src/button_zone.py` and `tests/test_button_zone.py`: the disc circle, the plunger column and the SW1 rule
  that `pcb_rules.py` and the placer use.
- `hw/evidence/parts/tl3342.yaml`: datasheet facts (force, travel, height, life), quotes checked by `check_part_evidence`.
- `docs/verification/reports/analysis-button-disc.md`: results of step 1.
**Files to change**: `docs/requirements/mech.md` (MECH-010 proposal, MECH-004 proposal), `docs/requirements/hw.md` (HW-007 proposal),
`docs/plans/05-mechanical-design.md` (btn rows, O8), `docs/plans/08-p1-one-sided-board.md` (revision 6 inherits the SW1 rule),
`mech/analysis/housing_params.py` (BTN_* replaced by DISC_*), `mech/freecad/housing.py` (lid disc, slot, support; stop ribs),
`docs/verification/test-cases-hw-mech.md` (TC-304, TC-310 to TC-313), `docs/risk/risk-register.md`, `CHANGELOG.md`.
**Order of work**
1. Study and ADR-0026 (scripts and tests, then the report); owner decides actuation concept, switch place, support concept.
2. Requirement proposals (MECH-010, MECH-004, HW-007); owner approves.
3. Switch part and evidence; `housing_params.py`, FreeCAD model, coupons (disc stiffness, binding, slot light).
4. Plan 08 revision 6 with the SW1 rule; goldfish readiness review; re-placement and routing.
5. Prototype tests TC-310 to TC-313 on the first printed housings.

## 6. Test and verification plan
| ID | What | Level | Pass criterion (working values) |
|---|---|---|---|
| (unit) `test_button_disc.py` | statics of the disc: equilibrium, symmetric case F/(3k), centroid rule, known beam values | Unit | residual below 1e-9; the centroid case gives equal travel at 400 points |
| (unit) `test_button_geometry.py` | S2 search and antenna distance | Unit | 7.6, 320 and 3.6 mm reproduced (tolerance 0.1 mm / exact count) |
| (unit) `test_button_zone.py` | SW1 rule on a placement | Unit | rule rejects a switch outside R_disc - 4 mm |
| TC-310 | force and position map of the printed disc | Prototype | 25 points on 3 housings, 10 presses each: actuates at every point inside R_use, force [2] to [4] N, no sticking, stroke to click at most [1.0] mm |
| TC-311 | life | Prototype | [20 000] presses without loss of click or crack of a support (jig not defined; owner decides the number) |
| TC-312 | range with a finger on the disc | Prototype | loss recorded against TC-303; pass limit set by the owner |
| TC-313 | accidental press | Prototype | the unit face down on a flat table and under a [5] N spread load does not press |
| TC-207, TC-304, TC-302 | button input, access, diffusion | existing | extended as in section 4 |
Not run now: everything above. The scratch numbers of section 3 come from throw-away scripts.

## 7. Risks and open questions
Risks (to enter in the register after the review):
1. "Press anywhere" fails: a floppy or binding disc (section 3.3 finding 2); the click is mushy because of the stack.
2. A hand over the antenna in a 3 s or 10 s press (A6) and the possible loss of Wi-Fi during a short press.
3. Light leak at the slot or score line (MECH-002).
4. Accidental or stuck press; the disc is large.
5. PETG creep or fatigue of the supports (A2); FDM tolerance of +-0.3 mm against a 0.25 mm switch travel.
6. S2 reopens the antenna decision of ADR-0003 (3.6 mm to the nearest LED).
7. The switch is metal near the antenna; the plunger column removes board area; M3 adds two switches.
Open questions for the owner: the life requirement in presses; the stuck-press rule; whether a finger over the antenna may
cost range during a press; whether a coloured or marked disc is allowed; the click force window.

## 8. Rollout / rollback and traceability
Created: plan 09, ADR-0026 (Proposed), MECH-010 (proposal), TC-310 to TC-313, risk entries, `button_disc.py`, `button_zone.py`,
`tl3342.yaml`. Changed (proposals): HW-007, MECH-004, plan 05 (btn rows, O8), plan 08 revision 6.
Rollback: keep the side-hole button; SW1 stays where board-p1 has it; plan 09 is set to Abandoned.
