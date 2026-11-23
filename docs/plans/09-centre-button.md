# 09 -- Centre-of-ring button (design doc)

- **Status:** Draft (revision 2 of 2026-11-23 after the goldfish review RV-018: comprehension, three antagonistic passes; the
  implementation-readiness pass follows this revision)
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
  x = -13.4 to -8.8 mm.
  **Correction of revision 1:** nearest LED centre to the antenna strip is **5.06 mm** on the stored board (revision 1 said 7.6 mm, which
  took the footprint origin as the body centre). With `mech_outline.py` MOD_OFF = -4.0 (owner decision 2026-11-18, ADR-0023) the figure is
  6.07 mm; the two repository models differ by 1.0 mm and step 1 reconciles them. Plan 05 quotes about 9.5 mm for the unshifted module.
- Z chain (`mech/analysis/housing_params.py`): PCB top Z 6.6, LED top 7.25, module top 9.0 (2.4 above the PCB), lid underside 15.25,
  lid plate 1.2, lid top 16.45. The lid joint is a spigot with 3 snap hooks at 60, 180 and 300 degrees.
- Switch: footprint family TL3342 (4.5 x 3.5 mm body); the F160 variant means 160 gf, about 1.6 N, and the travel is taken as 0.25 mm.
  Both are **assumptions**: no datasheet is read (`hw/evidence/parts/sw-tl3342.yaml` is a placeholder, "mpn: not chosen").
- Press functions: short, [3] s (configuration AP), [10] s (factory reset after a ring confirmation) (SYS-017, A8). A hand lies over the
  antenna during these presses.
- HW-008: all SMD parts on one side, so a switch under the board is not allowed. MECH-003: plastic only in the box around the antenna;
  disc, arms, guide and plunger are plastic; every switch body is metal.

Definitions used below: the disc has radius R_disc = 15 mm (diameter 30 mm); R_use = 13 mm is the radius within which a press must
actuate (a 2 mm edge zone); the free circle has radius 19 mm. R_use covers 47 % and the disc 62 % of the free-circle area.

Assumptions (goldfish: challenge):
- **A1** The disc is a plate of the lid thickness (1.2 mm) lowered by 0.3 mm against the band. Its connection to the lid depends on the
  support concept (section 3.2): bridges in the same print, or a separate part with a retaining hook.
- **A2** PETG modulus E = 1.5 GPa and yield 40 MPa are working values; a coupon replaces them (TC-310 coupon level, section 6).
- **A3** The disc is stiff compared with its supports. **Doubtful:** a 1.2 mm PETG plate deflects about 0.05 mm/N centrally and more with
  an overhang (reviewer estimate); step 1 adds a plate-bending model and a coupon gate.
- **A4** R_use = [13] mm; the finger-pad width of 15 mm is a working figure without source.
- **A5** FDM +-0.3 mm on features and on the lid position on the spigot (plan 05 A7).
- **A6** A finger over the antenna during a press is accepted if the link recovers. **Owner decision needed** (section 7); the interim
  limit is the MECH-003 loss of [6] dB with a hand on the disc.

## 3. Alternatives considered
Significant and costly to reverse: the choices go to ADR-0026 with weighted criteria (4.8). Numbers in 3.2 to 3.4 come from the
assistant's scratch scripts and from three independent goldfish recomputations that agreed on the physics; the scripts are **not in the
repository, so not yet evidence**. Step 1 replaces them by tested scripts.

### 3.1 What is pressed (owner answered; recorded for ADR-0026)
| Option | Idea | Verdict |
|---|---|---|
| **A** Separate centre disc | A plate inside the ring, ring band and lid fixed | **Owner choice** |
| B Whole lid moves | The lid floats on the spigot | Not chosen; the diffuser plate and snap hooks carry the load |
| C Touch | Capacitive centre | Not chosen; ESP32-C3 has no touch input, needs a part, no click |
| D Do nothing | Side button as today | Rejected by decision 9 |

### 3.2 Switch place by support concept (feasibility matrix)
Model: rigid disc, linear supports, displacement w = a + bx + cy; switch 6.4 N/mm (1.6 N over 0.25 mm, bilateral); load F at any of
648 points inside R_use (600 random with seed 7 plus 48 on the boundary). F is the load at which the plunger travel reaches 0.25 mm;
"travel" is the largest press-point travel at that load. Criteria from section 4.1: F within 2 to 4 N at every point, travel at most
1.0 mm. S1 = switch 7 mm off the centre (rear of the module); S2 = switch at the centre.

| Concept | Support stiffness | F min / max (N) | Travel (mm) | Verdict |
|---|---|---|---|---|
| S2 + three bridges at r = 14 | 1 N/mm each | 2.35 / 2.35 | 1.60 | travel fails |
| | 2 | 3.10 / 3.10 | 1.14 | travel fails |
| | **3** | **3.85 / 3.85** | **0.99** | **passes, marginal** |
| | 4 | 4.60 / 4.60 | 0.91 | force fails |
| S1 + bridges centred on the switch (centroid rule) | 1 / 3 / 10 / 30 | 2.35 / 3.85 / 9.1 / 24.1 | 10.0 / 5.6 / 4.0 / 3.6 | fails |
| S1 + bridges symmetric on the disc | 1 / 3 / 10 | 1.6 to 44 / 2.4 to 65 / 5.1 to 139 | 40 / 20 / 13 | fails |
| M3: three switches at r = 11, rigid disc, no bridges | switches only | 1.43 / 4.37 | 0.43 | works; force window 1.4 to 4.4 N |

Findings:
1. The centroid rule makes the plunger travel position-independent, but with the plunger 7 mm off the centre the three supports must sit
   on one side and the far side of the disc is unrestrained (press-point travel 3.6 mm or more at every stiffness). A single off-centre
   switch on soft supports **does not work**.
2. The centred switch with three bridges passes only in a narrow band of bridge stiffness (about 2.5 to 3.2 N/mm). Arm stiffness follows
   w t^3, so an FDM error of +-0.3 mm on a 1.2 mm arm spreads it by 0.3x to 2.4x (reviewer estimate): the band is not reachable without
   per-unit tuning.
3. Three switches give the stiffness and the tilt restraint from the switches and are insensitive to FDM tolerance; the module stays
   where it is. They cost two more switches and metal bodies about 3 to 4 mm from the antenna strip (for r = 11), and a closed contact
   on any of three switches is a stuck-closed fault path (4.5).
4. Unequal supports and a parallel-motion linkage (scissor or double lever, print-in-place hinges) are not analysed.

Concepts: **M1** compliant bridges (viable only with S2, narrow band; arm stress about 40 MPa at 1.0 mm travel against the assumed yield, so
a fatigue limit is needed). **M2** guided disc in a bore: **rejected**. A guide jams when the load offset e exceeds L/(2 mu); with
mu = 0.3 and e = 13 mm the guide must be at least 7.8 mm long and the free height is 5.95 mm; a tilt of c/h = 0.35/2 = 0.17 rad lifts a
plunger 10 mm away by 1.7 mm. **M3** rigid disc on three switches in parallel on BTN_SW with three spring tabs as hold-down. **M4** central
pivot post: only S2 has room, and the switch is then not at the centre; dropped unless M1 and M3 fail.

### 3.3 Where the switch sits, and the cost to the antenna
| Option | Idea | Finding |
|---|---|---|
| S1 Switch off the centre, one switch | Module stays | Not workable with simple supports (3.2) |
| **S2** Module moves, switch at the centre | Symmetric disc | Search definition: module body 13.2 x 16.6 mm, translation +-14 mm in 0.5 mm steps, rotation 0 to 177 degrees in 3 degree steps, LEDs 2.0 mm squares oriented radially at R 20 mm, phase 3.75 degrees, clearance 0.5 mm to LEDs and 1.0 mm to a 4.5 x 3.5 mm switch body at the centre, module corners within R 19.5 mm. Result: 320 poses; best distance from the antenna strip to the nearest LED centre **3.6 mm** (an independent search gave 3.2 to 3.7 mm; the value depends on the definitions). Today: 5.06 mm, so S2 keeps 71 % of the margin. It also reverses the owner decision of 2026-11-18 (module toward the antenna-side edge, slot) and reopens ADR-0003 and DEV-004 |
| **S3** Three switches around the module (with M3) | Module as stored | Antenna strip to LED unchanged at 5.06 mm; two more switches and pads; metal 3 to 4 mm from the antenna strip |
| S4 Switch under the board | Plunger through the board | Breaks HW-008; rejected |

No lean until the matrix is reproduced by tested scripts (step 1). The owner decides in ADR-0026 between S2 with M1 and S3 with M3
(and any scissor linkage that step 1 proves).

### 3.4 Stack tolerance (the click cannot be designed without closing it)
Vertical chain: PCB on its posts, posts, lid ledge, lid plate and disc, plunger, switch height, switch actuation point. The existing
`check_tolerance.led_distance` (lid underside to LED top) already gives +-0.86 mm worst case and +-0.39 mm RSS; adding the disc and
plunger print (+-0.3) and the unread switch height gives about +-1.2 to +-1.4 mm worst case (reviewer estimate, not yet computed) against
a switch travel of 0.25 mm. A soft series plunger absorbs over-travel but not a gap error, and a gap above zero at worst case means a
nominal gap of at least the worst-case sum. Closing mechanisms: (a) a spacer or shim selected per unit after a first-article gap
measurement, (b) a preloaded soft plunger (preload below the click force, plunger stiffness at most [0.3] N/mm so +-1.2 mm costs +-0.36 N),
(c) a switch with longer travel (a different part, 4.9). The lateral chain (spigot play 0.65 mm maximum, PCB-to-wall gap 1.38 mm at worst
case, disc tilt) places the plunger on the actuator; the plunger tip is sized from it. Step 1 extends `check_tolerance.py` with both
chains, names the datums, and uses the worst case for the safety-type criteria ("never rests on the switch", "recess stays above zero").

## 4. Technical plan
### 4.1 What every variant must meet (working values in brackets; sources in section 7)
- Disc: diameter 30 mm, plate 1.2 mm lowered 0.3 mm against the band (top at Z 16.15, underside at Z 14.95). The recess must stay above
  zero at the worst case of the stack (the nominal value follows from step 1) so that a flat surface touches the band, not the disc.
- Gap around the disc: [0.8] mm wide (print-in-place separation of a 0.8 mm gap needs a coupon). A score line with a skin is **deleted**:
  a 0.4 mm skin around 97 mm has about 18 kN/mm stiffness against the 3 to 10 N/mm needed.
- Actuation: [2] to [4] N at every point inside R_use with a [12] mm probe; press-point travel at most [1.0] mm; a click (force drop of at
  least [30] % in the datasheet curve, value from step 0).
- Overload: a [20] N press (assumption) is carried by a stop inside the lid (the disc rim against a lip of the band), not by the PCB and not
  by the switch; the click occurs before the stop at every point inside R_use.
- Height under the disc: the disc underside is 8.35 mm above the PCB top (14.95 - 6.6); minus the [1.2] mm stroke and 1.0 mm margin, **parts on
  the board top stay at most 6.15 mm high** under the disc (the module is 2.4 mm). Each plunger column needs a keep-out of r = [2.5] mm around the
  switch centre (sized from the lateral chain).

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
19 % of the ring brightness at the centre, 54 % at r = 13 mm and 71 to 81 % at r = 15 to 16 mm. **The disc is lit by spill** (the owner's
"not lit on its own" can only mean no extra LED), and a gap or step at r = 15 to 16 mm sits in the bright zone, so a line is likely.
Options for the owner: (i) accept a softly lit disc and a stepped light seal at the gap, (ii) an opaque underside mask on the disc (a
coupon decides), (iii) a smaller disc. TC-302 gets a procedure first (it is a stub today), then a photo at 1 m and 0.5 m of disc and gap;
the criterion is a luminance ratio disc-to-band of [10] to [60] % and no gap line brighter than the band (values after the first coupon).

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
- ADR-0026 fixes exact switch coordinates (SW1, and SW1B and SW1C for S3), kept in `housing_params.py` and `pcb_full.py` (`SW1_POS`); the placer
  keeps treating the switches as fixed parts. The ADR lists the keep-outs of the chosen concept (plunger columns, tab landing zones, stop lip,
  any skirt ring).
- Area check: run the plan 08 placer with the chosen concept and report the area fill before and after (plan 08 A3: 66 to 80 %).
- Plan 05: rows "btn" and "az_btn" are replaced; O8 answered; section 4.5 gets a pointer. Plan 08 revision 6 inherits the switch rule.
- Part structure per concept: M1 is one print; M3 is a separate disc retained by a hook (print orientation: plate on the bed). `housing.py`
  asserts one solid today and changes for a cut disc.

### 4.7 Requirement proposals (text; entered as proposals in the requirement files at step 2)
Parent of all: SYS-017, NEED-008, owner decision 9.
- **MECH-010 Button actuation.** The housing shall actuate the button when a force of [2] N to [4] N is applied with a [12] mm probe at any point
  within [13] mm of the ring centre, with at most [1.0] mm of travel. Verified by TC-310.
- **MECH-011 Overload.** The button shall withstand a force of [20] N for [10] s without permanent deformation and with an actuation-force change of
  at most [20] %. TC-315.
- **MECH-012 No unintended actuation.** The button shall not actuate when the unit lies face down on a flat surface, or when a [5] N force is
  spread over the lid band. TC-313.
- **MECH-013 Click and life.** The button shall give a click (force drop at least [30] %) and keep its actuation force within [+-20] % after
  [20 000] presses. TC-311 (the life figure is an owner decision).
- **MECH-004 change:** "to the button with a finger" becomes "to the centre disc of the ring with a finger". **HW-007 change:** the button input
  may be driven by up to three parallel switches (S3); the pull-up and the ESD path are unchanged. **SYS-017 amendment:** section 4.5.

### 4.8 ADR-0026 criteria (weights 1 to 5)
Actuation force and travel inside the window at every point (5); robustness to FDM tolerance and to the stack (5); antenna margin and metal near
the antenna (5); no unintended or stuck actuation (4); part count, area and cost (3); light and look (3); printability (3); change to approved
texts (2). Alternatives: S2 + M1, S3 + M3, a scissor linkage with one switch (if step 1 proves it), and the switch part (4.9).

### 4.9 Switch part
Decision 9 also asks to change the button choice. The 0.25 mm travel of the TL3342 family is the root of the stack problem. Step 0 reads the
TL3342 datasheet and two alternatives (a long-travel tact switch; a snap dome with its pad), checks LCSC and JLCPCB stock and class
(extended or basic), and updates `hw/evidence/parts/sw-tl3342.yaml` (no second file); ADR-0026 covers the part.

## 5. Detailed implementation plan
**Rule 1 and the order of work.** Steps 0 and 1 are analysis and evidence under the Approved requirements MECH-004, MECH-002, MECH-003 and
HW-008 (they check the owner's decision 9 against them) and change no CAD, board or requirement text; they add new documents only. The owner
confirms this reading (section 7). Requirement texts, `housing_params.py`, the FreeCAD model and the board follow ADR-0026 and the approval.

**Files to create**
- Step 0: datasheet evidence in `hw/evidence/parts/sw-tl3342.yaml` (updated) and one file per alternative; the stock check is noted in the report.
- Step 1: `mech/analysis/button_disc.py` (pure statics, linted): `plate_on_supports(supports: list[tuple[float, float, float]],
  load_xy: tuple[float, float], force: float) -> tuple[float, float, float]`, `press_metrics(supports, switches, points, travel_mm: float) ->
  dict`, `guided_beam_stiffness(E_mpa: float, w_mm: float, t_mm: float, L_mm: float) -> float`, `arm_stress(E_mpa: float, t_mm: float,
  L_mm: float, stroke_mm: float) -> float`, `guide_jam_length(e_mm: float, mu: float) -> float`, `plate_deflection(...)` (plate bending model,
  A3). Test `mech/analysis/test_button_disc.py` (root pytest, `pyproject.toml` testpaths). `mech/analysis/check_tolerance.py` and
  `test_check_tolerance.py` gain the vertical and lateral button chains.
- Step 1: `hw/kicad/spike-gate/src/button_zone.py` (outside ruff while in spike-gate; exception recorded) with `tests/test_button_zone.py`: module
  body outline from the stored footprint and from `mech_outline`, antenna-to-LED distance, the S2 pose search, the keep-out check for a switch
  position. Physical-property tests: baseline 5.06 mm within 0.1 mm for the stored outline and 6.07 mm for `mech_outline`, S2 best distance below
  the baseline, no pose overlaps an LED; the pose count is reported, not asserted.
- Step 1: `docs/verification/reports/analysis-button-disc.md`; `docs/decisions/ADR-0026-centre-button-concept.md` (Proposed).

**Files to change (after the approval of step 2 unless stated)**
`docs/requirements/mech.md` (MECH-010 to MECH-013, MECH-004), `hw.md` (HW-007), `system.md` (SYS-017), `sw.md` (new SW item),
`docs/verification/test-cases-hw-mech.md` (TC-207 method, TC-302 and TC-304 procedures, TC-310 to TC-315), `test-cases-sw.md`,
`docs/risk/risk-register.md`, `docs/regulatory/` (matrix and technical file after `regulatory-check`), `docs/user/` (quick start, user guide,
troubleshooting, glossary terms "button" and "disc"), a section-view diagram source after the concept is chosen, ADR-0006 (note),
`docs/plans/05-mechanical-design.md`, `docs/plans/08-p1-one-sided-board.md` (revision 6), DEV-004 (SW1 is one of its 14 fixed parts),
`mech/analysis/housing_params.py` (BTN_* replaced), `mech/freecad/housing.py`, `mech/analysis/coupons.py` (disc stiffness, gap, seal, 0.8/1.2/1.6 mm
plates), `hw/kicad/spike-gate/src/mech_outline.py` (BTN_AZ, BTN_BODY_R/T; LED_PHASE loses its reason), `src/pcb_full.py` (`SW1_POS`,
`note_fixed`), `src/pcb_quality.py` (SW1 exemption), `src/pcb_rules.py`, `scripts/panel_tabs.py` ("button 240" keep-out) and
`scripts/tests/test_panel_tabs.py` (asserts on `BTN_D` and `BTN_DEG`), `tests/test_mech_outline.py`, `tests/test_board_p1.py` (the U9-courtyard
overlap set contains SW1), `tests/test_pcb_full.py`, `known-open-violations.json`, and for S3 `src/layout_full.py` and `src/sourcing.py`.
Acceptance for that change: the full root pytest and the spike-gate suite pass.

**Order of work**
0. Read datasheets, stock and class of the switch candidates; update the evidence.
1. Analysis and ADR-0026 (Proposed): reproduce the matrix with tested scripts, close the stack, plate model, light estimate, area check;
   reconcile the module models (the 1.0 mm difference, and `POST_AZ` 30/150/270 in `mech_outline.py` against `POST_DEG` 60/180/300 in
   `housing_params.py`).
2. The owner decides ADR-0026 and the open questions; `regulatory-check`; the requirement texts enter as proposals; the owner approves.
3. **Pre-order gate:** printed lids and a plain stand-in board with the switch or switches at the planned points (no module); TC-310 at coupon
   level on three lids, with the disc, gap, stop and light seal. P1 is not re-placed before this passes (the alternative is a respin).
4. Plan 08 revision 6 with exact switch coordinates and keep-outs; readiness review; re-placement and routing.
5. Housing model; prototype tests TC-310 to TC-315 on the first printed housings with P1.

**Fallback (rollback):** a side-actuated switch at the board rim with the side hole of plan 05 (azimuth 240). SW1 is re-placed at the rim by plan 08
revision 6 (the stored SW1 at 13 mm does not match the housing hole today). Plan 09 is then set to Abandoned.

## 6. Test and verification plan
| ID | Verifies | What | Level | Procedure and pass criterion (working values) |
|---|---|---|---|---|
| (unit) `test_button_disc.py` | analysis | statics, beam, plate | Unit | equilibrium residual below 1e-9; symmetric case gives F/(3k); centroid case gives equal plunger travel at 600 seeded points; analytic beam and plate values |
| (unit) `test_check_tolerance.py` | MECH-010 | vertical and lateral chain | Unit | worst case and RSS reproduce hand values; gap above zero and recess above zero at worst case |
| (unit) `test_button_zone.py` | analysis | outlines, distances, pose search | Unit | see section 5 |
| TC-310 | MECH-010 | force and position map | Coupon, then prototype | [12] mm probe with a 3 mm soft pad, 1 mm/s, gauge accuracy 0.1 N, actuation read from the BTN_SW level on a scope; 25 points (centre, 8 at r = 7, 8 at r = 13, 8 in the edge zone) on 3 housings, 10 presses each, unit flat and on a vertical mount, at 25 and 50 degC; every point inside R_use actuates at [2] to [4] N and at most [1.0] mm; no sticking |
| TC-311 | MECH-013 | life and click | Prototype | [20 000] presses with a servo jig (jig to define; the owner decides the number); force within [+-20] %; no crack; click criterion from the datasheet curve |
| TC-312 | MECH-003, SYS-038 | range with a hand on the disc | Prototype | loss against the TC-038 baseline with a hand phantom on the disc, at rest and during an AP start; at most [6] dB |
| TC-313 | MECH-012 | no unintended press | Prototype | unit face down on a flat table, on a soft pad, on a convex object, and under [5] N spread over the band, each for [60] s, vertical mount included; no actuation |
| TC-314 | HW-007 | ESD at the disc and gap | Prototype | IEC 61000-4-2 air discharge at the disc and the gap, levels from the technical file; no reset, no false press (test case to write) |
| TC-315 | MECH-011 | overload | Prototype | [20] N for [10] s at the disc edge and centre, then TC-310; the click occurs before the stop at every point |
| TC-302 (extended) | MECH-002 | disc and gap light | Prototype | photo at 1 m and 0.5 m; luminance ratios of 4.4 |
| TC-207, TC-304 (extended) | HW-007, MECH-004 | button input, access | Analysis, demonstration | procedures written at step 2 (both are stubs today) |

Not run now: everything above. The numbers of section 3 come from scratch scripts.

## 7. Risks and open questions
Risks (entered in the register after the owner reads this revision):
1. "Press anywhere" fails (3.2): only S2 + M1 in a narrow band, or S3 + M3, pass the model; a rocking or binding disc; a mushy click from the stack.
2. A hand over the antenna during a 3 s or 10 s press; S2 cuts the antenna margin to 71 % of today's 5.06 mm; S3 puts metal 3 to 4 mm from the strip.
3. Light: the disc is lit by spill; a gap line is likely (4.4).
4. Unintended or stuck press (4.5); three parallel switches triple the stuck-closed chance.
5. PETG creep and fatigue of arms or tabs at 50 degC (A2); FDM tolerance against a 0.25 mm switch travel (3.4).
6. Pre-order gate delay; respin cost if the gate is skipped.

Sources of the working values: the 2 to 4 N window, 1.0 mm travel, 20 N overload, 5 N spread load, 20 000 presses, 30 % click drop and R_use = 13 mm
are the assistant's working proposals without a standard or datasheet behind them; step 0 replaces what the datasheet gives, the owner decides the rest.

Open questions for the owner (they change what is built):
1. **Light:** accept a softly lit disc (19 % to 80 % of the ring brightness), or an opaque mask or a smaller disc?
2. **Direction:** S2 with bridges (module moves, antenna margin 3.6 against 5.06 mm, narrow stiffness band) or S3 with three switches (module stays,
   two more switches near the antenna), or a scissor-linkage study?
3. **Hand over the antenna:** is a loss of up to [6] dB with a hand on the disc acceptable (A6)?
4. **Stuck press:** accept the rules of 4.5 (no start after a stuck press; reset needs a second deliberate action)?
5. **Life** in presses ([20 000]) and the force window [2] to [4] N.
6. **Process:** may steps 0 and 1 run as analysis under the Approved requirements before MECH-010 is approved?
7. Disc and R_use against the free circle: 30 mm and 26 mm of 38 mm (62 % and 47 % of the area). Is that "the entire centre"?
8. Ingress: the gap is a 75 mm2 opening above the board and no requirement covers liquid or dust; add one or accept?

## 8. Rollout / rollback and traceability
Created: plan 09, RV-018, ADR-0026 (Proposed, step 1), MECH-010 to MECH-013 (proposals), TC-310 to TC-315, risk entries, analysis scripts and tests,
`button_zone.py`, switch evidence. Changed (proposals): HW-007, MECH-004, SYS-017, one SW item, ADR-0006 note, plan 05, plan 08 revision 6, DEV-004.
IDs reserved by this plan: ADR-0026, RV-018, MECH-010 to MECH-013, TC-310 to TC-315 (the traceability check does not read `docs/plans/`; the IDs enter
the checked files at step 2). Rollback: the fallback of section 5.
