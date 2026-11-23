# 09 -- Centre-of-ring button (design doc)

- **Status:** Draft (revision 5 of 2026-11-23: revision 4 plus the result of step 0 (section 4.9, `stock-check-button-switches.md`); the owner said "Continue" after
  the status report and the assistant read that as a go-ahead for step 0 only. A third readiness pass runs after the owner has answered section 7, because the answers change the scope of step 1)
- **Date:** 2026-11-23  **Owner:** Ben Spoor (author: assistant)
- **Area:** mech (with hw and sw consequences)
- **Requirements addressed:** SYS-017 (Draft; amendment proposed), HW-007 (Draft; change proposed), MECH-004 (Approved; change
  proposed), MECH-002, MECH-003, MECH-001 and HW-008 (Approved, read for constraints). New proposals: MECH-010 to MECH-013 (section 4.7).
- **EGM review record:** RV-018 (`docs/reviews/RV-018-plan-09-centre-button-goldfish.md`)
- **Decides:** nothing by itself. It fixes the facts, the criteria and the order of work; ADR-0026 decides the switch place, the
  support concept and the switch part, and the owner approves.

## 0. Owner interview of 2026-11-23 (in the working session; recorded by the assistant)
Background: decision 9 of 2026-11-22: "Change mechanics so the entire center of the ring becomes the button. Change the
button choice and mechanics etc to accommodate this" (`docs/journal/2026-11-22-owner-decisions-p1-rework.md`).

| # | Question | Owner answer |
|---|---|---|
| 1 | Which part is pressed | A separate centre disc inside the LED ring; the ring band and the lid stay fixed |
| 2 | Where the switch sits (the module is at the ring centre) | "Study both in the plan": a switch off the centre, and the module moved so that the switch is at the centre |
| 3 | Look and feel | A clear click, disc in the same translucent PETG as the lid, centre not lit on its own (see 4.4: spill lights the disc) |
| 4 | Timing | Settle the concept first, then re-place P1 (plan 08 revision 6). P1 is not ordered before that |

## 1. Problem definition
SYS-017 and NEED-008 give the device one button. Today SW1 is a TL3342-family tact switch (E-Switch TL3342F160QG, C2886898)
at 13 mm from the board centre on the stored board-p1, and the housing has a side hole at azimuth 240 degrees ([7.0] mm,
plan 05 section 4.3 row "btn"). The owner wants the whole centre of the ring to be the button. Why now: the place and the
type of SW1 are inputs to the re-placement of P1 (plan 08 revision 6); a placement made before this decision is redone.
Out of scope: the placement itself (plan 08 revision 6), the gate and current-limit work (ADR-0024, ADR-0025), the press
lengths of SYS-017, capacitive touch (not chosen), the diffuser thickness (MECH-002 coupons), the rear bayonet (MECH-007).

## 2. Constraints, facts and assumptions
Facts, read from the repository (not measured). Heights are measured from the housing floor outer face (Z) or from the PCB top.
- LED ring: 16 LEDs, ring D 40 mm (LED centres), 2020 package, phase 3.75 degrees (`hw/kicad/spike-gate/src/mech_outline.py`).
  The inner LED edge is at about 19 mm from the axis (free circle radius 19 mm, area 1134 mm2). Plan 08 uses a placement radius
  of 18.4 mm for movable parts (`R_MOVE_P1`) and an LED courtyard from 18.75 mm.
- Module ESP32-C3-MINI-1 (13.2 x 16.6 x 2.4 mm). On the stored board-p1 the footprint origin is at (37.6, 40), rotation 90, board
  centre (40, 40). The body (F.Fab outline, local y -11.0 to 5.6) is **not centred on the origin**: it spans x = -13.4 to +3.2 mm from
  the board centre (body centre 5.1 mm off the board centre, antenna toward -X), y = +-6.6 mm. The antenna strip (4.6 x 13.2 mm) spans
  x = -13.4 to -8.8 mm. Nearest LED centre to the antenna strip: **5.06 mm** on the stored board (revision 1 said 7.6 mm, which took
  the footprint origin as the body centre). With `mech_outline.py` MOD_OFF = -4.0 (owner decision 2026-11-18, ADR-0023) the figure is
  6.07 mm; the two repository models differ by 1.0 mm and step 1 reports the reconciliation. Plan 05 quotes about 9.5 mm for the unshifted module.
- Z chain (`mech/analysis/housing_params.py`): PCB top Z 6.6, LED top 7.25, module top 9.0 (2.4 above the PCB), lid underside 15.25,
  lid plate 1.2, lid top 16.45. The lid joint is a spigot with 3 snap hooks at 60, 180 and 300 degrees.
- Switch TL3342F160QG: the stored SW1 footprint has four pads, F.Fab outline **6.4 x 5.2 mm** and courtyard **8.5 x 6.0 mm** (checked in
  `board-p1`). The vendor datasheet, read by the readiness goldfish from the LCSC-hosted copy and to be stored as evidence in step 0, gives a
  5.20 x 5.20 mm body, 6.40 mm over the terminals, 1.54 mm height, an actuator of about 2.0 mm diameter, 160 +-50 gf (1.08 to 2.06 N) and
  100 000 cycles, and **no travel and no force-travel curve**. Revision 2 used 4.5 x 3.5 mm, which is the side-button placeholder in
  `mech_outline.py` (BTN_BODY_T and BTN_BODY_R), and a travel of 0.25 mm, which is an **assumption** until a source or the TC-310 bench
  measurement exists. `hw/evidence/parts/sw-tl3342.yaml` is a placeholder with `pin_count: 2` (wrong; four terminals).
- Press functions: short, [3] s (configuration AP), [10] s (factory reset after a ring confirmation) (SYS-017, A8). A hand lies over the
  antenna during these presses.
- HW-008: all SMD parts on one side, so a switch under the board is not allowed; a snap dome is a manual assembly step and is excluded
  unless the owner relaxes SYS-022. MECH-003: plastic only in the box around the antenna; disc, arms, guide and plunger are plastic;
  every switch body is metal.

Definitions used below: the disc has radius R_disc = 15 mm (diameter 30 mm); R_use = 13 mm is the radius within which the **force
resultant** of a press must actuate (a 2 mm edge zone); the free circle has radius 19 mm. R_use covers 47 % and the disc 62 % of the
free-circle area. A finger spreads its load, which is less demanding for tilt than a point load; the test uses a small probe (4.1).

Assumptions (goldfish: challenge):
- **A1** The disc is a plate of the lid thickness (1.2 mm) lowered by 0.3 mm against the band. Its connection to the lid depends on the
  support concept (section 3.2): bridges in the same print, or a separate part with a retaining hook.
- **A2** PETG modulus E = 1.5 GPa and yield 40 MPa are working values; a coupon replaces them (step 3).
- **A3** The disc is stiff compared with its supports. **Doubtful:** a 1.2 mm PETG disc deflects about 0.04 mm/N under a central load
  (simply supported, nu = 0.4) and more with an overhang; step 1 adds the plate formula and step 3 the coupon gate.
- **A4** R_use = [13] mm for the force resultant; the finger-pad width of 15 mm is a working figure without source.
- **A5** FDM +-0.3 mm on features and on the lid position on the spigot (plan 05 A7).
- **A6** A finger over the antenna during a press is accepted if the link recovers. **Owner decision needed** (section 7); the interim
  limit is the MECH-003 loss of [6] dB with a hand on the disc.

## 3. Alternatives considered
Significant and costly to reverse: the choices go to ADR-0026 with weighted criteria (4.8). Numbers in 3.2 to 3.4 come from the
assistant's scratch scripts, which three goldfish rebuilt independently (the S2 rows, the M3 minimum and the pose search agree within the
definitions); the scripts are **not in the repository, so not yet evidence**. Step 1 replaces them by tested scripts.

### 3.1 What is pressed (owner answered; recorded for ADR-0026)
| Option | Idea | Verdict |
|---|---|---|
| **A** Separate centre disc | A plate inside the ring, ring band and lid fixed | **Owner choice** |
| B Whole lid moves | The lid floats on the spigot | Not chosen; the diffuser plate and snap hooks carry the load |
| C Touch | Capacitive centre | Not chosen; ESP32-C3 has no touch input, needs a part, no click |
| D Do nothing | Side button as today | Rejected by decision 9 |

### 3.2 Switch place by support concept (feasibility matrix)
Model: rigid disc, linear supports, displacement w = a + bx + cy; switch spring = 1.6 N / 0.25 mm = 6.4 N/mm (nominal force, **assumed
travel**, bilateral); load F at any of
650 or more points inside R_use: 600 from `random.Random(7)` (per point `u = rng.random()`, then `v = rng.random()`; radius R sqrt(u), angle 2 pi v),
plus the centre, plus every switch position, plus 48 equally spaced on the boundary starting at angle 0. The table below was made with a numpy
sampler (`default_rng(7)`) that did not include the centre; the stdlib rebuild in step 1 replaces the numbers, which are indicative to about 5 %. F is the load at which the plunger travel reaches 0.25 mm; "travel" is the largest press-point travel at that load. The switch
tolerance of +-0.49 N adds +-0.49 N to every F below. S1 = switch 7 mm off the centre (rear of the module); supports "centred on the
switch" are at azimuth 0 and +-acos(0.2) = +-78.463 degrees on r = 15 (centroid at x = 7); "symmetric" supports are at 90, 210, 330 degrees on r = 14;
S2 = switch at the centre with supports at 90, 210, 330 degrees on r = 14; M3 = three switches at r = 11 at 90, 210, 330 degrees.

| Concept | Support stiffness | F min / max (N) | Travel (mm) | Verdict |
|---|---|---|---|---|
| S2 + three bridges | 1 N/mm each | 2.35 / 2.35 | 1.60 | travel fails |
| | 2 | 3.10 / 3.10 | 1.14 | travel fails |
| | **3** | **3.85 / 3.85** | **0.99** | **passes at nominal, marginal; 4.3 N at +50 gf** |
| | 4 | 4.60 / 4.60 | 0.91 | force fails |
| S1 + bridges centred on the switch (centroid rule) | 1 / 3 / 10 / 30 | 2.35 / 3.85 / 9.1 / 24.1 | 10.0 / 5.6 / 4.0 / 3.6 | fails |
| S1 + bridges symmetric on the disc | 1 / 3 / 10 | 1.6 to 44 / 2.4 to 65 / 5.1 to 139 | 40 / 20 / 13 | fails |
| M3: three switches at r = 11, rigid disc, no bridges | switches only | 1.43 / **4.80** (centre; the sample of revision 3 missed it and said 4.37) | 0.43 | works mechanically; 1.4 N is below the 2 N lower bound, and the centre needs 4.8 N nominal and about 5.3 N with +50 gf on a switch, above the [5] N window |

Findings:
1. The centroid rule makes the plunger travel position-independent, but with the plunger 7 mm off the centre the three supports must sit
   on one side and the far side of the disc is unrestrained (press-point travel 3.6 mm or more at every stiffness). A single off-centre
   switch on soft supports **does not work**.
2. The centred switch with three bridges passes only in a narrow band of bridge stiffness (about 2.5 to 3.2 N/mm). Arm stiffness follows
   w t^3: with w and t both off by +-0.3 mm on a 1.2 x 1.2 mm arm it spreads by 0.32x to 2.4x (0.42x to 1.95x for t alone), so the band is
   not reachable without per-unit tuning.
3. Three switches give the stiffness and the tilt restraint from the switches and are insensitive to FDM tolerance, but **they do not fit
   around the stored module at r = 11**. A goldfish scan (triplet rotation 0 to 119 degrees in 1 degree steps, four switch orientations, both module
   models; step 1 reproduces it) finds that with the real 6.4 x 5.2 mm body only 7 of 480 configurations clear the module (best gap 0.33 mm to the body and
   0.34 mm to the antenna strip), and with the 8.5 x 6.0 mm courtyard none; with the azimuths 90, 210, 330 degrees of the table the 210 degree switch lies inside the
   module. A larger r changes the force window, a smaller switch relieves it. Two more courtyards also add about 102 mm2 to plan 08 A3's 430 of 650 mm2
   (quoted figures: (430 + 102) / 650 = 82 %, about 96 % with the vendor antenna keep-out). A closed contact on any of three switches is a stuck-closed
   fault path (4.5).
4. Unequal supports and a parallel-motion linkage (scissor or double lever, print-in-place hinges) are not analysed.

Concepts: **M1** compliant bridges (viable only with S2, narrow band; arm stress about 40 MPa at 1.0 mm travel against the assumed
yield, so a fatigue limit is needed). **M2** guided disc in a bore: **rejected**. A guide jams when the load offset e exceeds L/(2 mu); with
mu = 0.3 and e = 13 mm the guide must be at least 7.8 mm long and the free height is 5.95 mm; a tilt of c/h = 0.35/2 = 0.17 rad lifts a
plunger 10 mm away by 1.7 mm. **M3** rigid disc on three switches in parallel on BTN_SW with three spring tabs as hold-down. **M4** central
pivot post: only S2 has room, and the switch is then not at the centre; dropped unless M1 and M3 fail.

### 3.3 Where the switch sits, and the cost to the antenna
| Option | Idea | Finding |
|---|---|---|
| S1 Switch off the centre, one switch | Module stays | Not workable with simple supports (3.2) |
| **S2** Module moves, switch at the centre | Symmetric disc | Search (pose counts cover rotation 0 to 177 degrees; the full circle doubles them): module body 13.2 x 16.6 mm, translation +-14 mm in 0.5 mm steps, rotation 0 to 177 degrees in 3 degree steps (enough: the ring has 16 LEDs and the switch is a rectangle, both 180-degree symmetric; the antenna end is tried on both sides), LEDs 2.0 mm squares oriented radially at R 20 mm, phase 3.75 degrees, clearance 0.5 mm to LEDs, module corners within R 19.5 mm. **With the real switch (6.4 x 5.2 mm body at the centre, 1.0 mm clearance): 10 poses, best distance from the antenna strip to the nearest LED centre 2.51 mm, 50 % of today's 5.06 mm. With the 8.5 x 6.0 mm courtyard and no extra clearance: 58 poses, 3.04 mm (60 %).** Revision 2's 320 poses and 3.6 mm used the wrong body (4.5 x 3.5 mm) and are withdrawn; a switch of that size would give 324 poses and 3.64 mm (72 %), which is why step 0 looks for a smaller switch. S2 also reverses the owner decision of 2026-11-18 (module toward the antenna-side edge, slot) and reopens ADR-0003 and DEV-004 |
| **S3** Three switches around the module (with M3) | Module as stored | Antenna strip to LED unchanged at 5.06 mm, but the switches are not placeable at r = 11 around the stored module with the real switch (finding 3 of 3.2); two more courtyards and metal next to the antenna strip if they are placed |
| S4 Switch under the board | Plunger through the board | Breaks HW-008; rejected |

No lean until the matrix is reproduced by tested scripts (step 1). With the real switch both S2 (antenna margin halves) and S3 (does not fit at r = 11; area and metal
beside the antenna) are strained; a smaller switch (step 0) relieves both, and a scissor linkage with one switch would remove the support
problem. The owner decides in ADR-0026.

### 3.4 Stack tolerance (the click cannot be designed without closing it)
Vertical chain: PCB on its posts, posts, lid ledge, lid plate and disc, plunger, switch height, switch actuation point. The existing
`check_tolerance.led_distance` (lid underside to LED top) already gives +-0.86 mm worst case and +-0.39 mm RSS; adding the disc and
plunger print (+-0.3) and the switch height (1.54 mm nominal, tolerance not read) gives about +-1.2 to +-1.4 mm worst case (estimate, not yet
computed) against a switch travel that is itself unknown. A soft series plunger absorbs over-travel but not a gap error, and a gap above
zero at worst case means a nominal gap of at least the worst-case sum. Closing mechanisms: (a) a spacer or shim selected per unit after a
first-article gap measurement, (b) a preloaded soft plunger (preload below the click force, plunger stiffness at most [0.3] N/mm so +-1.2 mm
costs +-0.36 N), (c) a switch with longer travel (a different part, 4.9). The lateral chain (spigot play 0.65 mm maximum, PCB-to-wall gap
1.38 mm at worst case, disc tilt) places the plunger on the 2.0 mm actuator; the plunger tip is sized from it. Step 1 adds both chains as
functions of `check_tolerance.py` with named datums; they are **informational** (not part of `run()` and not a CI gate) until step 2
approves the numbers, because the worst-case recess check fails against the nominal 0.3 mm recess by design. The worst case governs the
safety-type criteria ("never rests on the switch", "recess stays above zero").

## 4. Technical plan
### 4.1 What every variant must meet (working values in brackets; sources in section 7)
- Disc: diameter 30 mm, plate 1.2 mm lowered 0.3 mm against the band (top at Z 16.15, underside at Z 14.95). The recess must stay above
  zero at the worst case of the stack (the nominal value follows from step 1) so that a flat surface touches the band, not the disc.
- Gap around the disc: [0.8] mm wide (print-in-place separation of a 0.8 mm gap needs a coupon). A score line with a skin is **deleted**:
  a 0.4 mm skin around 97 mm has about 18 kN/mm stiffness against the 3 to 10 N/mm needed.
- Actuation: [2] to [5] N at every point whose force resultant lies inside R_use (the switch alone is 1.1 to 2.1 N by its +-50 gf, so the
  window of revision 2, 2 to 4 N, did not allow for it); press-point travel at most [1.0] mm; a click (force drop of at least [30] %,
  **measured in TC-310 on the real switch** because the TL3342 datasheet has no curve). Test probe: [4] mm flat end with a 1 mm elastomer pad,
  so that the resultant at r = 13 mm stays inside the 15 mm disc.
- Overload: a [20] N press (assumption) is carried by a stop inside the lid (the disc rim against a lip of the band), not by the PCB and not
  by the switch; the click occurs before the stop at every point inside R_use.
- Height under the disc: the disc underside is 8.35 mm above the PCB top (14.95 - 6.6); minus the [1.2] mm stroke and 1.0 mm margin, **parts on
  the board top stay at most 6.15 mm high** under the disc (the module is 2.4 mm, the switch 1.54 mm). Each plunger column needs a keep-out of
  r = [2.5] mm around the actuator centre (to be sized from the lateral chain; the actuator is about 2.0 mm in diameter).

### 4.2 Electrical (HW-007)
GPIO5, R12 and TVS2 stay (BTN_SW, no external pull-up, internal pull-up enabled by the firmware, GPIO5 is no strapping pin). S3 puts
three switches in parallel on BTN_SW. The finger path is plastic. The ESD test for the disc and the gap is a **new** test case (TC-314,
IEC 61000-4-2 air discharge); the claim of revision 1 that ADR-0024's test covers it is withdrawn (that test is for CC1 and CC2).

### 4.3 Antenna (MECH-003)
Disc, arms, guide, stops: plastic. The finger contact plane (disc top, Z 16.15) is 7.15 mm above the module top. A hand over the antenna during
the 3 s and 10 s presses detunes it. TC-312 measures the loss with a hand on the disc against the bare-module baseline of TC-038 (SYS-038), at
rest and during an AP start; interim limit [6] dB (MECH-003). Metal switch bodies inside the MECH-003 box need a MECH-003 wording or a DEV
(for S3); the soft rule "switch on the side away from the antenna" is kept for S2.

### 4.4 Light (MECH-002)
By the plan 05 geometry (LEDs 8 mm under a translucent plate; Lambertian, ring sum; the LED beam angle is not found) the plate shows about
19 % of the ring brightness at the centre (re-checked), 54 % at r = 13 mm and 71 to 81 % at r = 15 to 16 mm (reviewer values). **The disc is
lit by spill** (the owner's "not lit on its own" can only mean no extra LED), and a gap or step at r = 15 to 16 mm sits in the bright zone,
so a line is likely. Options for the owner: (i) accept a softly lit disc and a stepped light seal at the gap, (ii) an opaque underside mask on
the disc (a coupon decides), (iii) a smaller disc. TC-302 gets a procedure first (it is a stub today), then a photo at 1 m and 0.5 m of disc
and gap; the criterion is a luminance ratio disc-to-band of [10] to [60] % and no gap line brighter than the band (values after the first coupon).

### 4.5 Firmware and system (proposals for SYS-017 and a new SW requirement)
- A press present at boot, or one not preceded by a release of at least [1] s, starts nothing (a stuck press cannot start the AP at 3 s or
  the reset at 10 s). The 30 s rule of revision 1 is withdrawn: it fired after the harmful windows.
- The factory reset after 10 s needs a **second deliberate action** (a short press during the confirmation pattern within [10] s); a ring
  pattern alone is not a confirmation. This amends SYS-017 (Draft).
- ADR-0006 item 7 (USB passphrase read only while the button is held) stays valid as the physical-presence proof; a stuck press cannot start
  the AP, but it could satisfy a "button held" check, so ADR-0006 gets a note (hold length and release rule decided with the SW requirement).
- Debounce and release chatter (a compliant disc can chatter), boot with the button pressed, and the GPIO5 pull-up with EMC: new SW
  requirement and tests (`sw.md`, `test-cases-sw.md`); RV-017 row 27 is closed against the new exposure. S3: three parallel switches triple
  the stuck-closed chance; added to the fault table and the risks.

### 4.6 Housing and board interface (inputs to plan 08 revision 6)
- ADR-0026 fixes exact switch coordinates (SW1, and SW1B and SW1C for S3), kept in `housing_params.py` and `pcb_full.py` (`SW1_POS` is one
  (radius, azimuth) tuple today and becomes a list for S3); the placer keeps treating the switches as fixed parts. The ADR lists the keep-outs of
  the chosen concept (plunger columns, tab landing zones, stop lip, any skirt ring).
- Area check: step 1 gives a capacity estimate from courtyard areas (3.2 finding 3); the placer run with the chosen concept is part of plan 08
  revision 6 (step 4), with the area fill before and after as its report.
- Plan 05: rows "btn" and "az_btn" are replaced; O8 answered; section 4.5 gets a pointer. Plan 08 revision 6 inherits the switch rule.
- Part structure per concept: M1 is one print; M3 is a separate disc retained by a hook (print orientation: plate on the bed). `housing.py`
  asserts one solid today and changes for a cut disc.

### 4.7 Requirement proposals (text; entered as proposals in the requirement files at step 2)
Parent of all: SYS-017, NEED-008, owner decision 9.
- **MECH-010 Button actuation.** The housing shall actuate the button when a force of [2] N to [5] N is applied, through a [4] mm probe, at any
  point within [13] mm of the ring centre, with at most [1.0] mm of travel. Verified by TC-310.
- **MECH-011 Overload.** The button shall withstand a force of [20] N for [10] s without permanent deformation and with an actuation-force change of
  at most [20] %. TC-315.
- **MECH-012 No unintended actuation.** The button shall not actuate when the unit lies face down on a flat surface, or when a [5] N force is
  spread over the lid band. TC-313.
- **MECH-013 Click and life.** The button shall give a click (force drop at least [30] %, measured on the real switch) and keep its actuation
  force within [+-20] % after [20 000] presses (the TL3342 datasheet gives 100 000 cycles for the switch alone). TC-311 (the life figure is an
  owner decision).
- **MECH-004 change:** "to the button with a finger" becomes "to the centre disc of the ring with a finger". **HW-007 change:** the button input
  may be driven by up to three parallel switches (S3); the pull-up and the ESD path are unchanged. **SYS-017 amendment:** section 4.5.

### 4.8 ADR-0026 criteria (weights 1 to 5)
Actuation force and travel inside the window at every point (5); robustness to FDM tolerance and to the stack (5); antenna margin and metal near
the antenna (5); no unintended or stuck actuation (4); part count, area and cost (3); light and look (3); printability (3); change to approved
texts (2). Alternatives: S2 + M1, S3 + M3, a scissor linkage with one switch (only if the owner asks for it and step 1 proves it), and the switch
part (4.9). ADR-0026 names only existing IDs in its Related field (the proposed MECH, TC and SW items appear as "plan 09 section 4.7"), so that
`check_traceability.py` passes before step 2.

### 4.9 Switch part
Decision 9 also asks to change the button choice. Step 0 reads the datasheet of the TL3342F160QG and of **two alternatives chosen by these
criteria**: body footprint area (smaller than 6.4 x 5.2 mm, ideally 4.5 x 3.5 mm or less, for S2 and S3), a datasheet that publishes travel and
the force-travel curve, actuation force and tolerance, actuator height 1.6 mm or less, life, and JLCPCB class (basic preferred) with stock.
Alternative 1: a small-body tact switch. Alternative 2: a longer-travel tact switch (travel of 0.5 mm or more) for the stack. A snap dome is
excluded (HW-008, manual assembly). The method is the one of the earlier stock checks: the LCSC and JLCPCB product pages and the
LCSC-hosted datasheets (reachable from the `busy-light` environment); the earlier precedent `stock-check-ilim-holdoff.md` records that stock
and class on those pages need a second source, which step 0 states per part.

**Step 0 result (2026-11-23; `docs/verification/reports/stock-check-button-switches.md`, evidence files `sw-tl3342.yaml`, `sw-b3u-1000p.yaml`, `sw-ksc221.yaml`).**
No listed part meets all criteria above; no part publishes a force-travel curve. Alternative 1 is the **Omron B3U-1000P** (LCSC C231329, JLCPCB Extended, LCSC stock 49,545):
body 3.0 x 2.5 mm, 1.50 +- 0.49 N, pre-travel 0.15 mm, life 200,000 or more. Alternative 2 is the **C&K KSC221JLFS** (C221726, Extended, stock 15,080): 6.2 x 6.2 mm, 2 +- 0.5 N, travel 0.35 +0.3/-0.1 mm,
life 500,000, IP67. The TL3342F160QG has LCSC stock 1 and publishes no travel. First-order values (assistant's scratch scripts, not evidence until step 1): with the B3U body, S2 keeps 3.90 mm (77 % of 5.06 mm)
at 1,322 module poses (TL3342 body: 2.51 mm, 10 poses); the bridge stiffness band for the pass rule of 4.1 widens from 2.83 to 3.92 N/mm (ratio 1.4, TL3342 with the assumed 0.25 mm) to 2.20 to 6.69 N/mm (ratio 3.0, B3U);
the B3U pre-travel tolerance is not yet in that band and breaks the force window at its extremes. Step 1 must rerun the matrix, the stack and the antenna search with these values; step 3 must measure click travel.

## 5. Detailed implementation plan
**Rule 1 and the order of work.** Steps 0 and 1 are analysis and evidence under the Approved requirements MECH-004, MECH-002, MECH-003 and
HW-008 (they check the owner's decision 9 against them) and change no CAD, board or requirement text; they add two new evidence files, one updated evidence file, about five new Python files with tests, one changed script
(`check_tolerance.py` with its test), one allow-list line in `check_license_map.py`, three new documents (stock-check report, analysis report, ADR-0026) and a README
row. **They start only after the owner confirms this reading and this change set** (section 7, question 6); until then the plan is not ready to run.
Requirement texts, `housing_params.py`, the FreeCAD model and the board follow ADR-0026 and the approval.

**Step 0 (evidence)**
- Files: `hw/evidence/parts/sw-tl3342.yaml` (updated; `mpn: TL3342F160QG`, `manufacturer: E-Switch`, `selection: chosen` as the P1 placeholder, LCSC C2886898 read
  from the product page, `url` and `retrieved_on` of the PDF), `hw/evidence/parts/sw-<mpn>.yaml` for each of the two alternatives,
  `docs/verification/reports/stock-check-button-switches.md` (stock, class, price and the second source per part, with the date; a single read of
  2026-11-23 showed LCSC stock 1 and JLCPCB stock 0, extended, for the TL3342F160QG). `scripts/check_license_map.py` gets the new yaml files in its ALLOW list.
- **Recording rule** (the checker needs a quote for every claim and the number must occur in the quote): the E-Switch sheet is one page and its dimensions are
  only in the drawing graphic, so (a) force is a claim `typ: 160` gf with the quote "160+- 50 gf" and a separate claim for the tolerance of 50 gf, the newton values go into
  `notes`; (b) life is a statement-only claim ("100,000 cycles typical", no number field); (c) "no travel and no force-travel curve" is a `source-missing` claim with
  notes; (d) body, height and actuator dimensions are **not machine-checked**: they are carried in `notes` and in the stock-check report, marked "from the drawing,
  not text-checked", and cross-checked against the stored footprint (6.4 x 5.2 mm). The same rule applies to alternatives whose PDFs lack a text layer.
  "0 errors" from `check_part_evidence.py` then means: schema valid, hashes and text quotes of the claims above pass; geometry is unchecked.
- Verification: `python3 -I scripts/check_part_evidence.py` with `BUSY_LIGHT_DATASHEETS` pointing to a scratch folder holding the PDFs (the owner's
  datasheet folder is not in the container; the hash and quote checks are reported as run or not run); `check_license_map.py`; `reuse lint`.
- Output: the numbers that step 1 needs (body, height, force and tolerance, travel if published). If no alternative meets all criteria of 4.9, the report names
  the best two and the criteria they fail; alternatives enter the S2 and S3 analysis by body size only.

**Step 1 (analysis; Python standard library only, no numpy; SPDX Apache-2.0 headers; `reuse lint` clean)**
- `mech/analysis/button_disc.py` (linted):
  - `Support = tuple[float, float, float]` (x mm, y mm, stiffness N/mm); `Plane = tuple[float, float, float]` (a mm, b, c) with w(x, y) = a + b x + c y.
  - `solve_plane(supports: Sequence[Support], load_xy: tuple[float, float], force_n: float) -> Plane`: solves sum_i k_i v_i v_i^T [a b c]^T = F [1 x y]^T
    with v_i = [1, x_i, y_i] by Cramer's rule; raises `ValueError` if singular.
  - `displacement(plane: Plane, point: tuple[float, float]) -> float`.
  - `sample_points(radius_mm: float, n_random: int, n_boundary: int, seed: int, extra: Sequence[tuple[float, float]] = ()) -> list[tuple[float, float]]`: the
    `n_random` points as in 3.2 (u first, then v, from `random.Random(seed)`), then `extra` (the centre and the switch positions), then `n_boundary` points from angle 0.
  - `PressMetrics` (frozen dataclass: `force_min_n`, `force_max_n`, `travel_max_mm`, `lift_points: int`) and `press_metrics(supports:
    Sequence[Support], switches: Sequence[tuple[float, float, float]], click_travel_mm: float, points: Sequence[tuple[float, float]]) -> PressMetrics`
    where a switch is (x mm, y mm, stiffness N/mm) and is added to the supports; the click is the first switch whose travel reaches `click_travel_mm`;
    a point whose plunger travel is not positive counts in `lift_points`.
  - `main() -> None` prints the matrix of 3.2 for the report.
  - `guided_beam_stiffness(E_mpa, w_mm, t_mm, L_mm) -> float` = E w t^3 / L^3 (fixed-guided beam, N/mm); `arm_stress(E_mpa, t_mm, L_mm, stroke_mm) -> float`
    = 3 E t stroke / L^2 (MPa); `guide_jam_length(e_mm, mu) -> float` = 2 mu e (mm); `plate_deflection(radius_mm, thickness_mm, E_mpa, nu, force_n,
    edge: Literal["simply_supported", "clamped"]) -> float` (carries `# noqa: PLR0913, PLR0917` as `check_part_evidence.py` does) for a **central** load (P R^2 (3 + nu) / (16 pi D (1 + nu)) and P R^2 / (16 pi D) with
    D = E t^3 / (12 (1 - nu^2))); edge presses are left to the coupon (step 3).
- `mech/analysis/button_light.py` (linted): `ring_irradiance(r_mm: float, height_mm: float = 8.0, ring_r_mm: float = 20.0, n: int = 16) -> float`,
  Lambertian ring sum relative to the value above an LED.
- `mech/analysis/check_tolerance.py` (changed, informational): `button_vertical_chain(tolerances: Mapping[str, float]) -> dict[str, float]` returning
  `{"wc": ..., "rss": ...}` and `button_lateral_chain(tolerances: Mapping[str, float]) -> dict[str, float]` likewise (keys: `pcb_wall_gap`, `spigot_play`, `tilt_walk`, `plunger_tip`); the vertical keys are `pcb_post`, `lid_ledge`, `lid_plate`,
  `disc_plunger`, `switch_height`, `switch_actuation`. The inputs are a local dict of working values (the switch-height tolerance is not published, so it is an assumption), not
  `housing_params.py`; neither function is called by `run()`; a third function `recess_worst_case(nominal_recess_mm, tolerances) -> float` gives the worst-case recess that the report quotes.
- Tests (root pytest, `pyproject.toml` testpaths): `mech/analysis/test_button_disc.py` (residual of the three equilibrium equations below 1e-9;
  three equal supports at 120 degrees with the load at the centroid give F/(3k); the centroid-rule case with the exact angle acos(0.2) gives equal plunger travel at all sample points
  to 1e-9; the S2 rows are position-independent and equal the analytic F = 0.25 (3 k + k_switch) within 1e-9; the M3 maximum is the analytic 4.80 N at the centre; beam 0.199 N/mm for
  E = 1500, 1.2 x 1.2, L = 25; plate 0.042 mm/N for R = 15, t = 1.2, E = 1500, nu = 0.4; analytic values of `arm_stress`, `guide_jam_length` and the clamped plate; a singular
  support set raises `ValueError`; `sample_points` is deterministic for a seed and holds the extra points; the sampled matrix rows of 3.2 within 5 %), `test_button_light.py` (value 0.18 to 0.20 at r = 0 relative to the ring value at r = 20 by the same function), additions to
  `test_check_tolerance.py` (hand values for worst case and RSS and for `recess_worst_case`), tests for `led_squares` and `antenna_strip` in `test_button_zone.py`.
- `hw/kicad/spike-gate/src/button_zone.py` (outside ruff while in spike-gate, as `pyproject.toml` already excludes that folder; the exception is
  recorded in the report) with `tests/test_button_zone.py`:
  - `read_footprint_outline(pcb_text: str, ref: str, layer: str = "F.Fab", board_centre: tuple[float, float] = (40.0, 40.0)) -> list[tuple[float, float]]` (stdlib regex parse of
    the `.kicad_pcb` of board-p1; the y axis stays KiCad's, pointing down; the rotation is KiCad's, X = x + lx cos t + ly sin t and Y = y - lx sin t + ly cos t for the footprint
    angle t; the outline is the bounding rectangle of the layer's lines; `pcbnew` is not needed and the tests are not skipped);
  - `led_squares(r_mm: float = 20.0, n: int = 16, phase_deg: float = 3.75, size_mm: float = 2.0) -> list[list[tuple[float, float]]]`;
  - `antenna_strip(body: Sequence[tuple[float, float]], strip_mm: float = 4.6, end: str = "min_x") -> list[tuple[float, float]]` (4.6 mm from the stated end of the bounding rectangle; the interior
    F.Fab line at 5.4 mm is ignored);
  - `nearest_led_distance(strip, leds) -> float` (to the LED centre);
  - `Pose = tuple[float, float, float, bool]` (x mm, y mm, angle degrees, antenna end flipped); `s2_poses(module_size: tuple[float, float], switch_size: tuple[float, float], switch_gap_mm: float,
    led_gap_mm: float, corner_radius_mm: float, extent_mm: float, step_mm: float, step_deg: float) -> list[Pose]` (report values: 19.5, 14.0, 0.5, 3.0; the corner radius is material:
    without it the result is 58 poses and 2.86 mm for the courtyard case) and `best_antenna_distance(poses) -> float`;
  - `s3_conflicts(switch_centres: Sequence[tuple[float, float]], switch_size: tuple[float, float], switch_rotation_deg: float, module_body, antenna_strip, leds, clearance_mm: float) -> list[str]` returns one
    string per overlap ("SW<i> overlaps module", "SW<i> overlaps LED<j>") and the gaps to the body and the strip; `s3_scan(r_mm: float, switch_size, clearance_mm: float, module_body, antenna_strip, leds) ->
    tuple[int, int, float, float]` scans triplet rotations 0 to 119 degrees in 1 degree steps and the four switch orientations and returns (feasible, total, best gap to the body, best gap to the strip);
  - `main() -> None` prints the S2 and S3 results for the report.
  - Tests: the SW1 outline is 6.4 x 5.2 mm and its courtyard 8.5 x 6.0 mm in board-p1; baseline 5.06 mm within 0.1 mm for the stored footprint and 6.07 mm for `mech_outline`; no pose overlaps an LED
    or the switch; the best S2 distance is below the baseline; `s3_scan` finds at most 20 of 480 feasible for the 6.4 x 5.2 body and none for the courtyard (the goldfish scan found 7 and 0; the
    test asserts "small", not the exact count); the pose count and the best distances are printed in the report, not asserted.
- Documents: `docs/verification/reports/analysis-button-disc.md` (results, the capacity estimate of 4.6, the reconciliation of the two module models and
  of `POST_AZ` 30/150/270 in `mech_outline.py` against `POST_DEG` 60/180/300 in `housing_params.py` as a list of issues with no file change),
  `mech/analysis/README.md` (rows for the new files), `docs/decisions/ADR-0026-centre-button-concept.md` (Proposed). Verification of step 1: the new
  tests, `check_traceability.py`, `ruff check .`, `ruff format --check .`, `reuse lint`, `check_license_map.py`, the root pytest and the spike-gate suite for `button_zone.py`; a `CHANGELOG.md` entry.

**Step 2** The owner decides ADR-0026 and the questions of section 7; `regulatory-check`; the requirement texts of 4.7 enter the requirement files as proposals and
the owner approves; ESD, overload, life and click procedures are written (TC-207, TC-302, TC-304, TC-311, TC-314 are stubs or new).

**Step 3 (pre-order gate)** printed lids and a plain stand-in board with the switch or switches at the planned points (no module), made by a script in `scripts/`
(rule 12); coupons in `mech/freecad/coupons.py` (disc stiffness, 0.8 mm gap, stop lip, light seal, the 0.8 / 1.2 / 1.6 mm plates), PETG brand and print settings
recorded; TC-310 at coupon level on three lids with the 4 mm probe; sample sizes of 3 lids, 25 points, 10 presses. P1 is not re-placed before this passes; a failed
gate sends the plan back to ADR-0026 (the alternative to the gate is a respin).

**Step 4** Plan 08 revision 6 with exact switch coordinates and keep-outs; readiness review; re-placement and routing. Files changed then: `housing_params.py`
(BTN_* replaced), `mech_outline.py` (BTN_AZ, BTN_BODY_R/T; LED_PHASE loses its reason), `src/pcb_full.py` (`SW1_POS`, `note_fixed`), `src/pcb_quality.py` (SW1
exemption), `src/pcb_rules.py`, `scripts/panel_tabs.py` ("button 240" keep-out), `scripts/tests/test_panel_tabs.py` (asserts on `BTN_D` and `BTN_DEG`),
`tests/test_mech_outline.py`, `tests/test_board_p1.py` (the U9-courtyard overlap set contains SW1), `tests/test_pcb_full.py`, `known-open-violations.json`,
DEV-004 (SW1 is one of its 14 fixed parts), and for S3 `src/layout_full.py` and `src/sourcing.py`. Acceptance: the full root pytest and the spike-gate suite (the
board tests need `pcbnew`, which only the CI hardware container has).

**Step 5** Housing model (`mech/freecad/housing.py`: cut disc, gap, stop, retention hook, plunger; the one-solid assertion changes), prototype tests TC-310 to
TC-315 on the first printed housings with P1 (test equipment: force gauge 0.1 N, servo jig, scope, RF set-up of TC-038). Also changed after approval:
`docs/requirements/mech.md`, `hw.md`, `system.md`, `sw.md`, `docs/verification/test-cases-hw-mech.md` and `test-cases-sw.md`, `docs/risk/risk-register.md`,
`docs/regulatory/` (matrix and technical file), `docs/user/` (quick start, user guide, troubleshooting, glossary terms "button" and "disc"), a section-view diagram
source, ADR-0006 (note), plan 05, plan 08.

**Fallback (rollback):** a side-actuated switch at the board rim with the side hole of plan 05 (azimuth 240). SW1 is re-placed at the rim by plan 08
revision 6 (the stored SW1 at 13 mm does not match the housing hole today). Plan 09 is then set to Abandoned.

## 6. Test and verification plan
| ID | Verifies | What | Level | Procedure and pass criterion (working values) |
|---|---|---|---|---|
| (unit) `test_button_disc.py`, `test_button_light.py` | analysis | statics, beam, plate, light | Unit | as listed in step 1 |
| (unit) `test_check_tolerance.py` | MECH-010 | vertical and lateral chain | Unit | worst case and RSS reproduce hand values |
| (unit) `test_button_zone.py` | analysis | outlines, distances, pose search | Unit | as listed in step 1 |
| (check) `check_part_evidence.py` | analysis | switch evidence | Check | 0 errors; hash and quote checks reported as run or not run |
| TC-310 | MECH-010 | force and position map | Coupon, then prototype | [4] mm probe with a 1 mm pad, 1 mm/s, gauge accuracy 0.1 N, actuation read from the BTN_SW level on a scope; 25 points (centre, 8 at r = 7, 8 at r = 13, 8 in the edge zone) on 3 housings, 10 presses each, unit flat and on a vertical mount, at 25 and 50 degC; every point inside R_use actuates at [2] to [5] N and at most [1.0] mm; no sticking; the click force drop is read here |
| TC-311 | MECH-013 | life and click | Prototype | [20 000] presses with a servo jig (jig to define; the owner decides the number); force within [+-20] %; no crack |
| TC-312 | MECH-003, SYS-038 | range with a hand on the disc | Prototype | loss against the TC-038 baseline with a hand phantom on the disc, at rest and during an AP start; at most [6] dB |
| TC-313 | MECH-012 | no unintended press | Prototype | unit face down on a flat table, on a soft pad, on a convex object, and under [5] N spread over the band, each for [60] s, vertical mount included; no actuation |
| TC-314 | HW-007 | ESD at the disc and gap | Prototype | IEC 61000-4-2 air discharge at the disc and the gap, levels from the technical file; no reset, no false press (test case to write) |
| TC-315 | MECH-011 | overload | Prototype | [20] N for [10] s at the disc edge and centre, then TC-310; the click occurs before the stop at every point |
| TC-302 (extended) | MECH-002 | disc and gap light | Prototype | photo at 1 m and 0.5 m; luminance ratios of 4.4 |
| TC-207, TC-304 (extended) | HW-007, MECH-004 | button input, access | Analysis, demonstration | procedures written at step 2 (both are stubs today) |

Not run now: everything above. The numbers of section 3 come from scratch scripts.

## 7. Risks and open questions
Risks (entered in the register after the owner reads this revision):
1. "Press anywhere" fails (3.2): only S2 + M1 in a narrow band, or S3 + M3 (not placeable at r = 11 with the real switch), pass the model; a rocking or binding disc; a mushy click from the stack.
2. A hand over the antenna during a 3 s or 10 s press; S2 cuts the antenna margin to 50 to 60 % of today's 5.06 mm with the real switch; S3 puts metal
   next to the strip if it can be placed at all.
3. Light: the disc is lit by spill; a gap line is likely (4.4).
4. Unintended or stuck press (4.5); three parallel switches triple the stuck-closed chance.
5. PETG creep and fatigue of arms or tabs at 50 degC (A2); FDM tolerance against a switch travel that is not yet known (3.4).
6. Area: S3 raises the fill of the ring interior from 66 % to about 82 % (plan 08 figures, not recomputed).
7. Pre-order gate delay; respin cost if the gate is skipped.

Sources of the working values: the 2 to 5 N window, 1.0 mm travel, 20 N overload, 5 N spread load, 20 000 presses, 30 % click drop and R_use = 13 mm
are the assistant's working proposals without a standard behind them; step 0 replaces what the datasheets give, the owner decides the rest.

Open questions for the owner (they change what is built):
1. **Light:** accept a softly lit disc (19 % to 80 % of the ring brightness), or an opaque mask or a smaller disc?
2. **Direction:** with the TL3342 body, S2 (module moves; antenna margin 2.5 to 3.0 mm against 5.06 mm today) and S3 (three switches; they do not fit around the stored module at r = 11,
   area up to 82 to 96 %) are both strained. Step 0 found the Omron B3U-1000P (3.0 x 2.5 mm): S2 then keeps 3.9 mm (77 %) on paper. Choose S2 with the B3U as the direction for step 1,
   keep S3 as a fallback, or still add a scissor-linkage study?
3. **Hand over the antenna:** is a loss of up to [6] dB with a hand on the disc acceptable (A6)?
4. **Stuck press:** accept the rules of 4.5 (no start after a stuck press; reset needs a second deliberate action)?
5. **Life** in presses ([20 000]) and the force window [2] to [5] N.
6. **Process:** may steps 0 and 1 run as analysis under the Approved requirements before MECH-010 is approved?
7. Disc and R_use against the free circle: 30 mm and 26 mm of 38 mm (62 % and 47 % of the area). Is that "the entire centre"?
8. Ingress: the gap is a 75 mm2 opening above the board and no requirement covers liquid or dust; add one or accept?

## 8. Rollout / rollback and traceability
Created: plan 09, RV-018, ADR-0026 (Proposed, step 1), MECH-010 to MECH-013 (proposals), TC-310 to TC-315, risk entries, analysis scripts and tests,
`button_zone.py`, switch evidence. Changed (proposals): HW-007, MECH-004, SYS-017, one SW item, ADR-0006 note, plan 05, plan 08 revision 6, DEV-004.
IDs reserved by this plan: ADR-0026, RV-018, MECH-010 to MECH-013, TC-310 to TC-315 (the traceability check does not read `docs/plans/`; the IDs enter
the checked files at step 2). Rollback: the fallback of section 5.
