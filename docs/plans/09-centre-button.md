# 09 -- Centre-of-ring button (design doc)

- **Status:** Draft (revision 9 of 2026-11-24: revision 8 plus the owner's second set of answers (section 0, D4 to D8: both concepts to the gate, force window good enough, rare use, light from the ring only, Apple-grade look); not yet reviewed by a goldfish; revision 8 was revision 7 with the resolutions of the review of plan and code (RV-018 rows R29 to R45); revision 7 was revision 6 with the resolutions of the third readiness NO-GO (RV-018 rows R13 to R27) and the step 1 files as built; revision 6: revision 5 plus the owner's direction of 2026-11-24 (section 0, decisions D1 to D3): S2 with the Omron B3U-1000P, S3 kept as the fallback,
  step 1 rescoped to the B3U values. Step 0 ran on 2026-11-23 (section 4.9). The third readiness pass runs on this revision; the other questions of section 7 stay open)
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

### Owner decisions of 2026-11-24 (in the working session; recorded by the assistant)
After the step 0 report the owner said "Do your recommendations". The recommendations in that report were the following; they are recorded as decisions D1 to D3 and nothing else:
- **D1 Direction:** S2 (module moved, switch at the centre) with the Omron B3U-1000P as the working switch; S3 (three switches) stays as the fallback; **no scissor-linkage study**.
  ADR-0026 (Proposed) records this and the alternatives; the owner still accepts the ADR.
- **D2 Process (question 6):** steps 0 and 1 run as analysis under the Approved requirements with the change set of section 5. Step 0 ran on 2026-11-23.
- **D3 Part class:** the B3U-1000P is an Extended part and the TL3342F160QG is Extended too with LCSC stock 1; the owner did not object to the extended-part fee. This is noted only: the order-day part and stock check stays in the gate.
Not decided by "Do your recommendations", because the report made no recommendation for them: light (question 1), hand over the antenna (3), stuck press (4), life and force window (5), disc size (7) and ingress (8). Step 1 uses the working values in brackets for them.

### Owner answers of 2026-11-24, second set (in the working session; recorded by the assistant)
Answers to the open questions of the status report after revision 8. The owner's words are quoted; nothing else is a decision.
- **D4 (question 9, S2 or S3):** "Both." S2 and S3 both go to the pre-order coupon gate; ADR-0026 stays Proposed until the owner accepts it.
- **D5 (force window):** "Good enough to start." The working window [2] to [5] N stays for the coupons; the life figure is not answered (see D6).
- **D6:** "Button is only used very rarely."
- **D7 (light):** "Light should come from the ring/rim not the center." The disc must not glow: the owner's earlier "not lit on its own" is replaced by "dark".
- **D9 (2026-11-24, third answer; questions 10 and 11):** "I agree with your recommendations." The recommendations were: question 10, prove the function with FDM coupons and housings, make the appearance sample (lid, band and disc) in a finer process (resin or MJF with finishing, to be priced) and decide the production process (injection moulding) at the manufacturing review, without promising the Apple-grade finish in FDM; question 11, a matt opaque disc in the lid colour family, with the finish decided on the appearance sample. Question 7 (disc size) had no recommendation and stays open with 30 mm as the working value.
- **D10 (2026-11-28, owner, after the LED ring mock-up; reverses D7):** "This is what I want + 4 LEDs in the center under the translucent button". The disc is translucent and lit by 4 LEDs; D7 (dark disc) no longer holds. Rows of this plan about the opaque disc, its transmission limit and the proposed MECH-002 change (4.4, 4.7, 5) are void until revision 10; the module at the board edge collides with the disc wall ring (ADR-0027, section Centre light). Not yet reviewed.
- **D8:** "Product should look like a really designed apple grade product." A goal for the whole product; for the button it means a flush, tight, even and dark centre disc, no visible tolerance.
Derived by the assistant from D6 to D8, **working values that the owner may change**: life [2 000] presses (was [20 000]); hand over the antenna [6] dB stays (rare use); the stuck-press rules of 4.5 stay (cheap, and a rare
press does not remove a stuck one); ingress accepted with a tight gap; the disc is a **separate opaque part** (not translucent, not print-in-place) so that the gap can be [0.4] mm and the disc can be dark; the look
criteria of 4.1 and MECH-014 are proposals. The process for the look and the disc material were answered by D9.

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
  `board-p1`). The vendor datasheet (LCSC-hosted copy, stored as evidence in step 0: `hw/evidence/parts/sw-tl3342.yaml`) gives a
  5.20 x 5.20 mm body, 6.40 mm over the terminals, 1.54 mm height, an actuator of about 2.0 mm diameter, 160 +-50 gf (1.08 to 2.06 N) and
  100 000 cycles, and **no travel and no force-travel curve**. Revision 2 used 4.5 x 3.5 mm, which is the side-button placeholder in
  `mech_outline.py` (BTN_BODY_T and BTN_BODY_R), and a travel of 0.25 mm, which is an **assumption** until a source or the TC-310 bench
  measurement exists. The evidence file now carries `pin_count: 4`.
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
2. The centred switch with three bridges passes only in a narrow band of bridge stiffness (2.83 to 3.92 N/mm with the TL3342 and the force tolerance). Arm stiffness follows
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

Concepts: **M1** compliant bridges (viable only with S2; the stiffness band is narrow with the TL3342 and wider with the B3U; a k = 3 N/mm arm of 1.2 x 1.2 mm needs L = 10.1 mm and sees 53 MPa at 1.0 mm of stroke
against the assumed yield of 40 MPa, so the arm must be made thinner or longer and a fatigue limit is needed). **M2** guided disc in a bore: **rejected**. A guide jams when the load offset e exceeds L/(2 mu); with
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

Direction (owner decision D1 of 2026-11-24): **S2 with the Omron B3U-1000P** (body 3.0 x 2.5 mm; section 4.9) as the working direction of step 1. The review of plan and code (RV-018 rows R29 to R45) then
found that the headline 3.90 mm (77 %) puts the antenna end 1.35 mm from the metal switch; with the antenna end away from the switch (section 4.3) it is 3.64 mm (72 % of 5.06 mm, 60 % of the `mech_outline` 6.07 mm),
and 3.55 mm (70 %) with the strip at least 3 mm from the switch. Over the whole datasheet pre-travel tolerance no bridge stiffness keeps the click force in the window (section 4.1), and a k = 3 N/mm arm sees 53 MPa
against the assumed 40 MPa yield. S3 with three B3U is placeable (92 of 480 at clearance 0, 22 at 1.0 mm) and a rigid disc on three switches does not depend on the arm stiffness, but it fails the force window at both ends
(an edge press needs 1.34 N, a centre press 3.03 to 5.97 N with the tolerance). ADR-0026 scores S2 at 84 and S3 at 87 against 66 for S2 with the TL3342: **S2 and S3 are within the scoring noise**. Recommendation of
revision 8: take both to the pre-order coupon gate (step 3) and choose on the measured click travel and arm stiffness. No scissor study (D1). The owner decides in ADR-0026.

### 3.4 Stack tolerance (the click cannot be designed without closing it)
Vertical chain: PCB on its posts, posts, lid ledge, lid plate and disc, plunger, switch height, switch actuation point. The existing
`check_tolerance.led_distance` (lid underside to LED top) already gives +-0.86 mm worst case and +-0.39 mm RSS; adding the disc and
plunger print (+-0.3) and the switch height (1.54 mm nominal, tolerance not read) gives about +-1.2 to +-1.4 mm worst case (estimate, not yet
computed) against a switch travel that is itself unknown. A soft series plunger absorbs over-travel but not a gap error, and a gap above
zero at worst case means a nominal gap of at least the worst-case sum. Closing mechanisms: (a) a spacer or shim selected per unit after a
first-article gap measurement, (b) a preloaded soft plunger (preload below the click force, plunger stiffness at most [0.3] N/mm so +-1.2 mm
costs +-0.36 N), (c) a switch with longer travel (a different part, 4.9). The lateral chain (spigot play 0.65 mm maximum, PCB-to-wall gap
1.38 mm at worst case; the code takes the 1.90 mm nominal gap as the board shift, disc tilt) places the plunger on the 2.0 mm actuator; the plunger tip is sized from it. Step 1 adds both chains as
functions of `check_tolerance.py` with named datums; they are **informational** (not part of `run()` and not a CI gate) until step 2
approves the numbers, because the worst-case recess check fails against the nominal 0.3 mm recess by design. The worst case governs the
safety-type criteria ("never rests on the switch", "recess stays above zero").

## 4. Technical plan
### 4.1 What every variant must meet (working values in brackets; sources in section 7)
- Disc: diameter 30 mm, plate 1.2 mm lowered 0.3 mm against the band (top at Z 16.15, underside at Z 14.95). The recess must stay above
  zero at the worst case of the stack (the nominal value follows from step 1) so that a flat surface touches the band, not the disc.
- Gap around the disc: [0.4] mm wide and even to [+-0.1] mm (D8). The disc is a **separate opaque part** (D7), so the gap is set by two printed edges and the assembly, not by a print-in-place separation; FDM
  tolerance (TOL_FDM 0.30 mm) is wider than the gap tolerance, so the coupon decides which process reaches it (question 10). A score line with a skin is **deleted**: a 0.4 mm skin around 97 mm has about 18 kN/mm
  stiffness against the 3 to 10 N/mm needed.
- Look (D8, proposals for MECH-014): the disc top is flush with the band to [+-0.1] mm or recessed by a designed [0.3] mm dish (the coupons compare 0, 0.15 and 0.3 mm; flush needs the actuation force and the
  no-actuation test of MECH-012 to hold); no visible fastener, hook, seam or print line on the visible face other than the one gap; one matt finish and colour over lid, band and disc; the visible travel of a press at most
  [0.3] mm (S3 travels 0.26 mm, S2 0.6 to 1.3 mm: this favours S3).
- Actuation: [2] to [5] N at every point whose force resultant lies inside R_use (the switch alone is 1.1 to 2.1 N by its +-50 gf, so the
  window of revision 2, 2 to 4 N, did not allow for it; the owner called the window good enough to start, D5); press-point travel at most [1.0] mm; a click (force drop of at least [30] %,
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

### 4.4 Light (MECH-002; owner decision D7: the light comes from the ring and rim, not from the centre)
The ring glows as a closed band (MECH-002 stays); **the disc stays dark**. By the plan 05 geometry (LEDs under a translucent plate; Lambertian ring sum, `button_light.py`, receiver at the disc underside 7.7 mm above the LED
top) the spill reaches 16.5 % of the value above an LED at the centre, 50 % at r = 13 mm and 67 to 77 % at r = 15 to 16 mm (18 %, 53 % and 70 to 79 % with the lid underside at 8.0 mm). A translucent disc would glow, so:
- the disc is an **opaque** part (colour and finish chosen with the owner, question 11); with a working limit of [3] % of the ring luminance the disc transmission must be at most 18 % at the centre, 6.0 % at r = 13 mm and
  4.5 % at r = 15 mm (optical density at least 0.74, 1.22 and 1.35; `button_light.required_transmission`), so an unmasked thin opaque print is not enough and the coupon measures the disc;
- **no light leaks at the gap**: the disc rim overlaps a lip of the band (a labyrinth) so that no bright line shows at the 0.4 mm gap, and the gap is dark against the ring (a line brighter than the band is a fail);
- the lit band is even: no single LED visible at 1 m (MECH-002) and a luminance variation along the ring of at most [+-25] % (value after the first coupon).
TC-302 gets a procedure first (it is a stub today), then a photo at 1 m and 0.5 m of disc, gap and ring; the criteria are a disc-to-ring luminance ratio of at most [3] %, no gap line brighter than [3] % of the ring and the
MECH-002 band criteria. MECH-002 (Approved) gets a change proposal: "the centre disc shall not glow".

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
- Area check: step 1 gives a capacity estimate (`button_zone.fill_fraction`, plan 08 A3 figures of 430 mm2 on 650 mm2: 66 % today, 63 % for S2 with the B3U courtyard of 4.0 x 3.5 mm, 82 % for S3 with two more TL3342 courtyards); the placer run with the chosen concept is part of plan 08
  revision 6 (step 4), with the area fill before and after as its report.
- Plan 05: rows "btn" and "az_btn" are replaced; O8 answered; section 4.5 gets a pointer. Plan 08 revision 6 inherits the switch rule.
- Part structure (D7, D8): for both concepts the disc is a separate opaque part retained by hooks or tabs under the band (print orientation: plate on the bed); for S2 the bridge arms are part of the disc part or of a
  carrier ring. `housing.py` asserts one solid today and changes for a separate disc.

### 4.7 Requirement proposals (text; entered as proposals in the requirement files at step 2)
Parent of all: SYS-017, NEED-008, owner decision 9.
- **MECH-010 Button actuation.** The housing shall actuate the button when a force of [2] N to [5] N is applied, through a [4] mm probe, at any
  point within [13] mm of the ring centre, with at most [1.0] mm of travel. Verified by TC-310.
- **MECH-011 Overload.** The button shall withstand a force of [20] N for [10] s without permanent deformation and with an actuation-force change of
  at most [20] %. TC-315.
- **MECH-012 No unintended actuation.** The button shall not actuate when the unit lies face down on a flat surface, or when a [5] N force is
  spread over the lid band. TC-313.
- **MECH-013 Click and life.** The button shall give a click (force drop at least [30] %, measured on the real switch) and keep its actuation
  force within [+-20] % after [2 000] presses (rare use, D6; the switch alone is rated 100 000 cycles for the TL3342 and 200 000 for the B3U). TC-311 (the life figure is derived
  from D6 and stays the owner's to change).
- **MECH-014 Appearance of the button (proposal, D8).** The centre disc shall sit flush with the band to [+-0.1] mm (or in a designed recess), with a gap of [0.4] mm even to [+-0.1] mm, with no visible
  fastener or print line on the visible face and with the same finish and colour family as the lid. Verified by TC-316 (gauge, photo at 0.5 m, owner design review of the sample).
- **MECH-002 change (D7):** add "the centre disc shall not glow: its luminance shall be at most [3] % of the ring luminance and the gap shall show no line brighter than that". TC-302.
- **MECH-004 change:** "to the button with a finger" becomes "to the centre disc of the ring with a finger". **HW-007 change:** the button input
  may be driven by up to three parallel switches (S3); the pull-up and the ESD path are unchanged. **SYS-017 amendment:** section 4.5.

### 4.8 ADR-0026 criteria (weights 1 to 5)
Actuation force and travel inside the window at every point (5); robustness to FDM tolerance and to the stack (5); antenna margin and metal near the antenna (5); **look and feel, Apple grade: flush, narrow even gap,
short visible travel (5, new with D8)**; no unintended or stuck actuation (4); part count, area and cost (3); light from the ring only, disc dark (3, D7); printability (3); change to approved texts and decisions (2).
Alternatives: S2 + M1 with the B3U-1000P (the owner's direction D1), S2 + M1 with the TL3342F160QG (dropped), S3 + M3 (fallback; D4: both go to the gate), a scissor linkage with one switch (not studied, D1), and the
switch part (4.9). ADR-0026 names only existing IDs in its Related field (the proposed MECH, TC and SW items appear as "plan 09 section 4.7"), so that `check_traceability.py` passes before step 2.

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
at 1,330 module poses (TL3342 body: 2.51 mm, 10 poses); the bridge stiffness band for the pass rule of 4.1 widens from 2.83 to 3.92 N/mm (ratio 1.4, TL3342 with the assumed 0.25 mm) to 2.20 to 6.69 N/mm (ratio 3.0, B3U);
the B3U pre-travel tolerance is not yet in that band and breaks the force window at its extremes. Step 1 must rerun the matrix, the stack and the antenna search with these values; step 3 must measure click travel.

## 5. Detailed implementation plan
**Rule 1 and the order of work.** Steps 0 and 1 are analysis and evidence under the Approved requirements MECH-004, MECH-002, MECH-003 and
HW-008 (they check the owner's decision 9 against them) and change no CAD, board or requirement text; they add two new evidence files, one updated evidence file, four new Python files with tests (`button_disc.py`, `button_light.py`,
`button_zone.py` and their three test files), one changed script (`check_tolerance.py` with its test), two allow-list lines in `check_license_map.py` (made in step 0), three new documents (stock-check report, analysis report, ADR-0026) and a README
row. **Owner decision D2 of 2026-11-24 confirms this reading and this change set** (section 7, question 6); step 0 has run, step 1 starts after the third readiness pass of RV-018.
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

**Step 1 (analysis; Python standard library only, no numpy; SPDX Apache-2.0 headers; `reuse lint` clean) - as built on 2026-11-24.** Conventions that the third readiness pass
found open are pinned here (RV-018 rows R13 to R27). All values below are reproduced by the scripts; the report `docs/verification/reports/analysis-button-disc.md` holds the raw output.
- `mech/analysis/button_disc.py` (linted, `# noqa: PLR0913, PLR0917` on every function with more than five arguments):
  - `Support = tuple[float, float, float]` (x mm, y mm, N/mm); `Plane = (a mm, b, c)` with w(x, y) = a + b x + c y; `Point = tuple[float, float]`.
  - `solve_plane(supports, load_xy, force_n) -> Plane` solves sum_i k_i v_i v_i^T [a b c]^T = F [1 x y]^T (v_i = [1, x_i, y_i]) by Cramer's rule; `ValueError` if |det| < 1e-12.
    `displacement(plane, point) -> float`. `bridges(radius_mm, stiffness) -> list[Support]` gives three equal bridges at 90, 210 and 330 degrees.
  - `sample_points(radius_mm, n_random, n_boundary, seed, extra=())`: `n_random` points (u first, then v, from `random.Random(seed)`; radius R sqrt(u), angle 2 pi v), then `extra`, then
    `n_boundary` points from angle 0. The report uses 600, the centre as extra, 48, seed 7, R_use = 13 mm.
  - `PressMetrics(force_min_n, force_max_n, travel_max_mm, lift_points)` and `press_metrics(supports, switches, click_travel_mm, points)`: a switch is (x, y, N/mm) and is added to
    the supports; per point the plunger travel w is the largest switch displacement for a unit load; w <= 1e-9 counts as a lift point and is left out of the force and travel ranges;
    F = click_travel / w and the press-point travel is F times the displacement at the point; if every point lifts the forces are `inf` and the travel is 0.
  - `tolerance_band(F, tol, x_min, x_max, window_n, n_bridges=3)` = (k_low, k_high) from the force only over the whole pre-travel tolerance; for the B3U (1.5 +- 0.49 N, 0.05 to 0.35 mm) k >= 6.60 and
    k <= 2.87 N/mm, so **no stiffness holds the window** (0.05 to 0.25 mm: k <= 4.01, still none). `bridge_band` evaluates the travel at the nominal click force and raises `ValueError` if the plunger lifts at any press point.
  - `s2_click_force(switch_force_n, bridge_k, n_bridges, click_travel_mm)` = F + n k x; `click_force_extremes(F, tol, x_min, x_max, k, n)` = (F - tol + n k x_min, F + tol + n k x_max);
    `bridge_band(F, tol, x, window_n, travel_limit_mm, points, bridge_r_mm=14.0) -> (k_low, k_high)`: k_low is the larger of the stiffness at which the largest press-point travel equals the
    limit (bisection between 0.1 and 20 N/mm, 80 steps) and the stiffness at which F - tol reaches the lower window value; k_high is the stiffness at which F + tol reaches the upper value;
    `ValueError` if the travel limit is not met up to 20 N/mm or if k_low > k_high. Working values: window (2.0, 5.0) N, travel limit 1.0 mm.
  - `guided_beam_stiffness`, `arm_stress`, `guide_jam_length` and `plate_deflection(radius, thickness, E, nu, force, edge)` (central load only) as in the formulas of 3.2.
  - `main()` prints, for the TL3342 (1.57 +- 0.49 N, 0.25 mm assumed), the B3U (1.50 +- 0.49 N, 0.15 mm) and the KSC221 (2.0 +- 0.5 N, 0.35 mm): the S2 rows for k = 1, 2, 3, 4, 6 N/mm and the band
    (`ValueError` is caught and printed as "no band", which happens for the KSC221), then the click force of the B3U at k = 3 for the pre-travel extremes 0.05 to 0.35 mm (typeset table) and 0.05 to 0.25 mm
    (PDF text layer), and the M3 row.
- `mech/analysis/button_light.py` (linted): `ring_irradiance(r_mm, height_mm=8.0, ring_r_mm=20.0, n=16, azimuth_deg=0.0, phase_deg=0.0) -> float` is sum_k h^2 / (d_k^2 + h^2)^2 (Lambertian emitter, planar
  receiver; d_k the horizontal distance to LED k at phase_deg + 360 k / n degrees), divided by the same sum at the ring radius and azimuth phase_deg (directly above an LED). The value at r = 0 is 0.165
  (`HEIGHT_MM` 7.7, test 0.15 to 0.20; 0.165 at r = 0, 0.500 at 13, 0.672 at 15, 0.771 at 16, pinned to 0.002).
- `mech/analysis/check_tolerance.py` (changed, informational; neither chain is called by `run()`): `BUTTON_VERTICAL` (mm plus-minus: `pcb_post` 0.36 = 0.20 post seat + 0.16 board thickness, `lid_ledge` 0.30,
  `lid_plate` 0.20, `disc_plunger` 0.20, `switch_height` 0.15 assumption, `switch_actuation` 0.20; datum PCB top Z 6.6 to the plunger contact plane) and `BUTTON_LATERAL` (`pcb_wall_gap` 1.90 = nominal
  radial gap, `spigot_play` 0.65, `tilt_walk` 0.20 assumption, `plunger_tip` 0.30); `button_vertical_chain(tolerances)` and `button_lateral_chain(tolerances)` return `{"wc": sum, "rss": root of the sum of
  squares}` (hand values: vertical 1.41 and 0.6017, lateral 3.05 and 2.0402); `recess_worst_case(nominal, tolerances)` = nominal - `lid_plate` (0.3 gives +0.10; the ledge moves disc and band together in one print, so it is left out; placeholder until a coupon measures the step). The values are tied to `housing_params` (`switch_height` 0.15 and `tilt_walk` 0.20 are assumptions; `switch_actuation` 0.20 is the larger side of the B3U +0.2/-0.1 mm). A missing key raises `KeyError`.
- `hw/kicad/spike-gate/src/button_zone.py` (outside ruff while in spike-gate, as `pyproject.toml` excludes that folder; recorded in the report) with `hw/kicad/spike-gate/tests/test_button_zone.py` (unittest style,
  runs in the spike-gate suite, needs no `pcbnew`, no skips; all frames have the board centre at the origin, KiCad's y down for outlines and y up for the ring and the searches, harmless because the antenna strip is
  symmetric about the module long axis):
  - `read_footprint_outline(pcb_text, ref, layer="F.Fab", board_centre=(40.0, 40.0))`: bounding rectangle of the layer's `fp_line` items of one footprint (balanced-parenthesis parse; KiCad rotation
    X = x + lx cos t + ly sin t, Y = y - lx sin t + ly cos t); `ValueError` for an unknown reference or a layer without lines. SW1: 6.4 x 5.2 mm (F.Fab) and 8.5 x 6.0 mm (F.CrtYd); U9: 16.6 x 13.2 mm,
    x from -13.4 to +3.2 mm.
  - `led_squares(r_mm=20.0, n=16, phase_deg=3.75, size_mm=2.0)`; `antenna_strip(body, strip_mm=4.6, end="min_x")` (the strip of the bounding rectangle 4.6 mm from the stated end);
    `nearest_led_distance(strip, leds)` (to the LED centre); `poly_distance` and `point_poly_distance` for convex polygons.
  - `Pose = tuple[float, float, float]` (x, y, angle degrees); `s2_poses(module_size, switch_size, switch_gap_mm, led_gap_mm, corner_radius_mm, extent_mm, step_mm, step_deg)`: `module_size` is
    (width 13.2, length 16.6) with the width along local x and the antenna end at local -y; the module is rotated counter-clockwise by the angle about its centre (x, y); x and y run from -extent to +extent, the angle from 0 to 177
    degrees; a pose is one entry per (x, y, angle), valid when all corners are within `corner_radius_mm` of the origin and the Euclidean distance is at least `switch_gap_mm` to the switch (axis-aligned at the
    origin) and at least `led_gap_mm` to every LED square; a distance below the gap, touching or overlapping conflicts (so gap 0 means no overlap). Report arguments: module (13.2, 16.6), switch (6.4, 5.2) gap 1.0 or
    (8.5, 6.0) gap 0.0 or (3.0, 2.5) gap 1.0 or (4.0, 3.5) gap 1.0, LED gap 0.5, corner radius 19.5, extent 14.0, step 0.5, 3.0 degrees.
    `strip_polygon(pose, flipped, ...)` and `antenna_distance(pose, flipped, ...)` give one pose and end (the stored module pose (x -5.1, y 0, 90 degrees, flipped) gives 5.0628 mm);
    `best_antenna_distance(poses, module_size=(13.2, 16.6), strip_mm=4.6, leds=None, switch_size=None, min_switch_strip_mm=0.0, away_from_switch=False)` is the largest, over the poses and both antenna ends, of the strip to
    nearest LED centre distance (0 for no pose); with `switch_size` an end counts only if its strip is at least `min_switch_strip_mm` from the switch and, with `away_from_switch`, not nearer to it than the other end.
    Results (pinned in the tests): 10 poses and 2.51 mm, 58 and 3.04 mm, 1,330 and 3.90 mm, 428 and 3.64 mm in that order (B3U with the antenna end away from the switch 3.64 mm, strip at least 3 mm from the switch 3.55 mm); without the corner limit the courtyard case gives 134 poses and 3.57 mm and at 19.0 mm 12 poses and 2.86 mm.
  - `s3_conflicts(switch_centres, switch_size, switch_rotation_deg, module_body, antenna_strip_poly, leds, clearance_mm)` returns "SW<i> overlaps module", "SW<i> overlaps antenna strip" and
    "SW<i> overlaps LED<j>" strings; `s3_scan(r_mm, switch_size, clearance_mm, module_body, antenna_strip_poly, leds) -> (feasible, total, best gap to body, best gap to strip)` scans triplet azimuths 90 + rot + 120 k for
    rot 0 to 119 degrees in 1 degree steps and the four **absolute** switch orientations 0, 45, 90 and 135 degrees (all three switches share one), total 480, clearance 0 (touching conflicts); the best gap is the largest over the
    feasible configurations of the smallest gap of the three switches, the two maxima independent. Stored module: 7 of 480 (best gaps 0.33 mm and 0.34 mm) for the 6.4 x 5.2 mm body, 0 for the courtyard, 92 of 480
    (1.68 mm and 2.97 mm) for the B3U body 3.0 x 2.5 mm. The `mech_outline` model gives 7 and 0.33 mm for the TL3342 body.
  - `fill_fraction(movable_mm2, available_mm2, extra_movable_mm2=0.0, fixed_delta_mm2=0.0)` = (movable + extra) / (available - fixed delta); `main()` prints the S2, S3 and fill results.
- Tests: `mech/analysis/test_button_disc.py` (equilibrium residuals below 1e-9; three equal supports; the centroid-rule case with acos(0.2) gives equal plunger travel to 1e-9; S2 rows position-independent and equal to
  0.25 (3 k + k_switch); S2 and S1 rows within 5 % of 3.2; M3 maximum 4.80 N; singular set raises; empty list gives `inf`; sampler determinism and extras; beam 0.199 N/mm; plate 0.042 and the clamped analytic value;
  `arm_stress`, `guide_jam_length`; `s2_click_force` 3.85 and 2.40 N; `click_force_extremes` (1.46, 5.14); `bridge_band` for the TL3342 (2.83, 3.92) and the B3U (2.20, 6.69) within 3 %, the B3U band wider, `ValueError` for
  the KSC221 and for an empty window; `main()` smoke test), `test_button_light.py` (0.17 to 0.20 at r = 0; reference 1; monotone; `main()` smoke test), additions to `test_check_tolerance.py` (hand values, key
  check, not part of `run()`), and `hw/kicad/spike-gate/tests/test_button_zone.py` (outlines, baselines 5.06 mm within 0.1 mm for the stored footprint and 6.07 mm for `mech_outline`, LED squares, strip, distances,
  the pose counts and best distances pinned on the full 0.5 mm and 3 degree grid (10, 58, 1,330, 428 poses; 2.51, 3.04, 3.90, 3.64 mm; the metal-switch rule values 3.64 and 3.55 mm; corner limit variants 134 and 12 poses),
  every pose checked for the gaps, the corner limit and the angle range, the stored module pose giving 5.0628 mm, S3 counts pinned (7 and 0 at clearance 0; 92 and 22 for the B3U at clearance 0 and 1.0 mm), conflict strings,
  fill figures, `main()` smoke test; the S2 tests take about 30 s).
- Documents: `docs/verification/reports/analysis-button-disc.md` (raw output, tools, revision, issues found without file change: `POST_AZ` 30/150/270 in `mech_outline.py` against `POST_DEG` 60/180/300 in
  `housing_params.py`, the two module models, the stored-board pin of `test_button_zone.py`, the TC-310 probe margin), `mech/analysis/README.md` (rows for the new files),
  `docs/decisions/ADR-0026-centre-button-concept.md` (Proposed). Verification of step 1: the new tests, `check_traceability.py`, `ruff check .`, `ruff format --check .`, `reuse lint`, `check_license_map.py`,
  the root pytest and the spike-gate suite for `button_zone.py`; a `CHANGELOG.md` entry.

**Step 2** The owner decides ADR-0026 and the questions of section 7; `regulatory-check`; the requirement texts of 4.7 enter the requirement files as proposals and
the owner approves; ESD, overload, life and click procedures are written (TC-207, TC-302, TC-304, TC-311, TC-314 are stubs or new).

**Step 3 (pre-order gate)** printed lids and a plain stand-in board with the switch or switches at the planned points (no module), made by a script in `scripts/`
(rule 12); coupons in `mech/freecad/coupons.py` (disc stiffness for S2 and the rigid disc for S3, 0.8 mm gap, stop lip, light seal, the 0.8 / 1.2 / 1.6 mm plates), with one B3U at the centre and three B3U at r = 11 mm on the stand-in board (D4: both), an opaque disc coupon for the light limit of 4.4, a 0.4 mm gap with a labyrinth lip, and the flush, 0.15 mm and 0.3 mm recess variants of 4.1, PETG brand and print settings
recorded; TC-310 at coupon level on three lids with the 4 mm probe; sample sizes of 3 lids, 25 points, 10 presses. P1 is not re-placed before this passes; a failed
gate sends the plan back to ADR-0026 (the alternative to the gate is a respin).

**Step 4** Plan 08 revision 6 with exact switch coordinates and keep-outs; readiness review; re-placement and routing. Files changed then: `housing_params.py`
(BTN_* replaced), `mech_outline.py` (BTN_AZ, BTN_BODY_R/T; LED_PHASE loses its reason), `src/pcb_full.py` (`SW1_POS`, `note_fixed`), `src/pcb_quality.py` (SW1
exemption), `src/pcb_rules.py`, `scripts/panel_tabs.py` ("button 240" keep-out), `scripts/tests/test_panel_tabs.py` (asserts on `BTN_D` and `BTN_DEG`),
`tests/test_mech_outline.py`, `tests/test_board_p1.py` (the U9-courtyard overlap set contains SW1), `tests/test_pcb_full.py`, `tests/test_button_zone.py` (pins the stored board-p1: SW1, U9 at (37.6, 40), 5.06 mm), `known-open-violations.json`,
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
| TC-310 | MECH-010 | force and position map | Coupon, then prototype | [4] mm probe with a 1 mm pad, 1 mm/s, gauge accuracy 0.1 N, actuation read from the BTN_SW level on a scope; 25 points (centre, 8 at r = 7, 8 at r = 12 (probe edge at 14 mm, 0.7 mm inside the disc edge against the +-0.3 mm print tolerance), 8 in the edge zone) on 3 housings, 10 presses each, unit flat and on a vertical mount, at 25 and 50 degC; every point inside R_use actuates at [2] to [5] N and at most [1.0] mm; no sticking; the click force drop is read here |
| TC-311 | MECH-013 | life and click | Prototype | [2 000] presses with a servo jig (jig to define; the owner decides the number); force within [+-20] %; no crack |
| TC-312 | MECH-003, SYS-038 | range with a hand on the disc | Prototype | loss against the TC-038 baseline with a hand phantom on the disc, at rest and during an AP start; at most [6] dB |
| TC-313 | MECH-012 | no unintended press | Prototype | unit face down on a flat table, on a soft pad, on a convex object, and under [5] N spread over the band, each for [60] s, vertical mount included; no actuation |
| TC-314 | HW-007 | ESD at the disc and gap | Prototype | IEC 61000-4-2 air discharge at the disc and the gap, levels from the technical file; no reset, no false press (test case to write) |
| TC-315 | MECH-011 | overload | Prototype | [20] N for [10] s at the disc edge and centre, then TC-310; the click occurs before the stop at every point |
| TC-302 (extended) | MECH-002, MECH-014 | ring band, dark disc and gap | Coupon, prototype | photo at 1 m and 0.5 m with luminance read-out; disc-to-ring luminance at most [3] %; no gap line brighter than [3] % of the ring; ring variation at most [+-25] %; no single LED visible at 1 m |
| TC-316 | MECH-014 | appearance of the disc | Coupon, prototype | feeler gauge or optical measurement of the gap at 8 points (0.4 +- 0.1 mm) and of the flushness (+-0.1 mm); photo at 0.5 m; owner design review of the sample against the Apple-grade goal (D8); no visible fastener or print line |
| TC-207, TC-304 (extended) | HW-007, MECH-004 | button input, access | Analysis, demonstration | procedures written at step 2 (both are stubs today) |

Not run now: everything above. The numbers of section 3 come from scratch scripts.

## 7. Risks and open questions
Risks (entered in the register after the owner reads this revision):
1. "Press anywhere" fails (3.2): only S2 + M1 (band ratio 3.0 with the B3U, 1.4 with the TL3342; the B3U pre-travel tolerance of +0.2/-0.1 mm still breaks the force window at its extremes, so the click travel must be measured), or S3 + M3 (not placeable at r = 11 with the TL3342 body), pass the model; a rocking or binding disc; a mushy click from the stack.
2. A hand over the antenna during a 3 s or 10 s press; S2 with the B3U keeps 72 % of today's 5.06 mm with the antenna end away from the switch (50 % with the TL3342 body); S3 puts metal
   next to the strip if it can be placed at all.
3. Light: the disc must stay dark (D7); the spill needs a disc transmission of at most 4.5 % at r = 15 mm and a light-tight gap; a bright gap line or a glowing disc fails TC-302 (4.4).
3a. Look (D8): FDM tolerance (+-0.3 mm) is wider than a 0.4 mm gap tolerance of +-0.1 mm; an Apple-grade finish may need another process for the visible parts (question 10).
4. Unintended or stuck press (4.5); three parallel switches triple the stuck-closed chance.
5. PETG creep and fatigue of arms or tabs at 50 degC (A2); FDM tolerance against a switch travel that is not yet known (3.4).
6. Area: S3 raises the fill of the ring interior from 66 % to about 82 % (plan 08 figures, not recomputed).
7. Pre-order gate delay; respin cost if the gate is skipped.

Sources of the working values: the 2 to 5 N window, 1.0 mm travel, 20 N overload, 5 N spread load, 2 000 presses (derived from D6), 30 % click drop and R_use = 13 mm
are the assistant's working proposals without a standard behind them; step 0 replaces what the datasheets give, the owner decides the rest.

Open questions for the owner (they change what is built):
Answered: direction (D1), process (D2), S2 or S3 (D4: both to the gate), force window (D5: good enough to start), light (D7: from the ring, the disc dark), process for the look (D9, question 10) and disc material and finish (D9, question 11). Derived from D6 to D8 and open to correction: life [2 000], antenna [6] dB, stuck-press rules, ingress.
7. Disc and R_use against the free circle: 30 mm and 26 mm of 38 mm (62 % and 47 % of the area). Is that "the entire centre"? (unchanged; a dark opaque disc makes the size a pure design question)
10. **Process for the look (D8):** answered (D9): FDM coupons and housings prove the function; the appearance sample (lid, band, disc) is made in a finer process (resin or MJF with finishing, to be priced); the
    production process is decided at the manufacturing review; no Apple-grade promise in FDM. Not asked again.
11. **Disc material and finish:** answered (D9): matt opaque, lid colour family, finish decided on the appearance sample (optical density of at least 1.35 at r = 15 mm). Not asked again.

## 8. Rollout / rollback and traceability
Created: plan 09, RV-018, ADR-0026 (Proposed, step 1), MECH-010 to MECH-013 (proposals), TC-310 to TC-315, risk entries, analysis scripts and tests,
`button_zone.py`, switch evidence. Changed (proposals): HW-007, MECH-004, SYS-017, one SW item, ADR-0006 note, plan 05, plan 08 revision 6, DEV-004.
IDs reserved by this plan: ADR-0026, RV-018, MECH-010 to MECH-014, TC-310 to TC-316 (the traceability check reads `docs/**/*.md`, plans included, and finds the IDs only where a heading starts with one; the IDs enter
the checked files at step 2). Rollback: the fallback of section 5.
