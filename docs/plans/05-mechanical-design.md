# 05 -- Mechanical design: housing for the LED status ring (design doc)

- **Status:** Draft (elephant draft; goldfish review RV-004 done, not ready for approval; the owner has not approved it; the MECH requirements are Draft). Revised 2026-11-04: the three open conflicts are resolved by author decisions that the owner must confirm (section 4.11).
- **Date:** 2026-11-04  **Owner:** Ben Spoor
- **Area:** mech (planning only; nothing in `mech/`, `hw/` or `sw/` is created or changed by this plan)
- **Requirements addressed:** MECH-001, MECH-002, MECH-003, MECH-004, MECH-005, MECH-006 (all Draft). Parents: SYS-001, SYS-013, SYS-017, SYS-020, SYS-028, SYS-038. Interfaces to HW-001, HW-005, HW-010 and HW-006.
- **Decision record:** ADR-0011 (Proposed). Analysis: `docs/verification/reports/mech-concept-analysis.md` (Draft, not measured).
- **EGM review record:** RV-004 (comprehension and antagonistic passes run 2026-11-04; outcome: not ready for approval, actions open; readiness pass not run)

## 1. Problem definition
The product needs a housing. It must hold one round PCB with 16 RGB LEDs on a ring, an ESP32-C3-MINI-1 module with its on-board antenna, a USB-C connector and one button. The housing is 3D printed. It turns the 16 LEDs into a closed band of colour that is readable at desk distance (SYS-001, MECH-002), is about 53 mm across (SYS-028: 48 to 58 mm, MECH-001), and carries the unit label on its underside (MECH-006, SYS-013).
Why now: ADR-0003 and the hardware requirements need the housing limits (ring size, board outline, connector positions) before the PCB outline is drawn, and the thermal and material choice (RISK-005) affects the firmware current limit (SYS-020, ADR-0009).
Out of scope: the PCB design (ask the owner for the outline, section 5.4), firmware, user documentation, injection moulding, ingress protection (no IP requirement exists), a wall or ceiling mount (not supported by the flat-lying assumption A1), CAD files (the owner makes them).

Status of the inputs: the MECH requirements are Draft and not approved, so this plan is a **proposal for the owner to approve first**. No file in `mech/` may be created from it until the owner approves the MECH requirements.

## 2. Constraints and assumptions
Constraints (from requirements and ADRs, quoted):
- Largest outer dimension 48 to 58 mm with the board fitted (MECH-001, SYS-028 [53] mm).
- 16 LEDs at 22.5 degrees on one circle of at least [38] mm, all on one board side (HW-001, SYS-028).
- No single LED visible as a point at 1 m; closed band (MECH-002).
- Inside a 15 mm box around the antenna area the housing has plastic only; the nearest wall is at least 15 mm from the antenna edge (MECH-003). The vendor figure and the split between housing and layout are in section 4.6.
- USB-C access with a standard cable and a finger on the button, without tools (MECH-004).
- Material at least [15] K below its HDT at the highest internal temperature (MECH-005).
- Flat label area at least [20] x [20] mm on the underside of the base, readable when the unit is lifted, on a part that does not move when the housing opens (MECH-006).
- Board assembled on one side, no hand soldering (SYS-022): the underside of the PCB is bare, so the board can sit on posts.
- Power: 5 V, [500] mA default, up to [1500] mA when advertised (SYS-020). Dissipation up to 2.5 W at 500 mA, 3.0 to 4.7 W in the realistic worst case, 6.75 W at the 1350 mA limiter cap (power budget report; ADR-0009).

Assumptions (goldfish: challenge these):
- **A1 (WITHDRAWN) Owner answer 2026-11-04: the unit is mounted both horizontal and vertical. A1 is therefore withdrawn; the dimensions, the label place and the thermal case that rest on it must be redone (RV-004 A1).** Was: the unit lies flat on a desk and the ring faces up. The label is on the underside of the base. **Assumption, answers O1; the owner confirms.** It excludes a stand, a wall mount and a hanging unit.
- **A2** The owner has an FDM printer that can print PETG; ASA is possible. Resin is not available. (O2.)
- **A3** The LED type is a 2020 package (0.65 mm high for the XL-2020 part; other parts not read). The PCB is 1.6 mm FR-4.
- **A4** The module is in the ring centre or at the board edge (ADR-0003 A or B). The housing is the same for both; only the mount of an external antenna (u.FL variant) would differ.
- **A5** The USB-C receptacle is on the LED side of the PCB at the board edge, mouth at the board edge. The button is a tactile switch with a side actuator (not chosen).
- **A6** Highest room temperature 35 deg C (O5).
- **A7** FDM external tolerance +-0.3 mm, small features +-0.2 mm until a calibration coupon is printed.
- **A8** PCB outline tolerance +-0.15 mm, thickness +-0.16 mm (shop value not found).

## 3. Alternatives considered
Full comparison, scoring and sensitivity in ADR-0011 (Proposed). Summary:

| Option | Idea | Weighted sum (max 175) | Verdict |
|--------|------|------------------------|---------|
| A | Clamshell: opaque base, opaque top cap with a ring window, separate translucent diffuser ring (3 parts) | 133 | Fallback if the single lid fails the diffusion test |
| **B** | Opaque base plus one translucent lid that is the diffuser (2 parts) | **147** | **Recommended** |
| C | Sphere of two snap-fit halves | 117 | Rejected: flat label and USB-C window on a sphere, supports, snap creep |
| D | Do nothing (bare board) | 122, excluded by gates | Baseline only |

Process (ADR-0011, second table): FDM with PETG (114) or ASA (111) for the base, natural translucent PETG for the lid; resin (104) as the fallback for the lid; PLA (113, excluded by the thermal gate). The tables do not separate PETG from ASA; the thermal estimate does (ASA safe, PETG marginal in a hot room).

## 4. Technical plan

### 4.1 Concept B in one paragraph
A flat cylinder of [53.0] mm diameter and [16.5] mm height. The **base** (opaque, ASA or PETG) is a cup 14 mm tall: floor, a wall, three short posts (3 mm) that hold the PCB near the floor, a window for the USB-C plug, a hole for the button. The underside of the floor has a label recess and four feet. The **lid** (natural or white translucent PETG) is a 2.45 mm cap: a 1.2 mm plate that diffuses the light and a skirt that fits over a spigot of the base and snaps on. The PCB lies on the posts with the LED side up, [8] mm under the lid plate. The label sits on the floor of the base, so it does not move when the lid is taken off.

Figure (text only, no diagram is added because no CAD exists; draw it from the table in 4.3 once the owner has a model): section from top: lid plate, 8 mm air gap, LED ring on the PCB, 3 mm of posts, floor with the label recess below.

### 4.2 Diffusion (MECH-002)
- The lit band is the lid plate over the ring. LED-to-diffuser distance [8.0] mm, plate [1.2] mm, natural or white translucent PETG.
- Analysis (report 4.1): ring D 40 mm, 16 LEDs, pitch 7.85 mm. The cones of neighbours touch at 2.3 mm (60 deg half angle) or 3.9 mm (45 deg). A ripple of at most 10 % before any scatter needs 5.0 mm (60 deg) or 6.0 mm (45 deg). At 8 mm the ripple is 1.1 % (60 deg) or 2.4 % (45 deg). The beam angle of the shortlisted LEDs is **not found**; one 2020 part has 120 deg (read).
- Price of the distance: at 8 mm the lit band is up to 14 mm wide on each side of the ring at half intensity (60 deg). The ring looks like a wide glow or a disc. This is O3 (ring look). The ring pitch and the 8 mm distance are unchanged by the resolution of section 4.11; the band reaches R 28 to 34 mm at half intensity and is cut by the wall at R 24.9 mm.
- Options if the look is wrong: (i) smaller distance with a thicker or more scattering lid (test with coupons), (ii) an opaque central insert, (iii) concept A (separate ring with a mask).
- Photobiological safety of the LED ring (viewing a bright LED) is not assessed here; a diffuser lowers the risk. Verify against the LED standard in the regulatory check.

### 4.3 Working dimensions of the recommended concept
All values are working values in [brackets] for the owner's parameter sheet (section 5.3). Tolerances are the FDM assumption A7 until a coupon is printed. Part names: `Base`, `Lid`.

| Param | Feature | Value | Tolerance | Basis |
|-------|---------|-------|-----------|-------|
| D_out | Outer diameter of base and lid | [53.0] mm | +-0.3 | MECH-001 (48 to 58); equals the SYS-028 working value |
| H_total | Total height, floor outer face to lid top (feet add 1.0) | [16.5] mm | +-0.3 | computed 16.45 (Z_lid_in 15.25 + t_diff 1.2), rounded; 17.45 mm with the feet |
| H_base | Base height to the joint | [14.0] mm | +-0.2 | window top at Z 12.25 plus margin |
| t_wall | Wall thickness | [1.6] mm | +-0.2 | 4 perimeters of 0.4 mm; 4 x layer height rule (report F8) |
| t_floor | Floor thickness | [2.0] mm | +-0.2 | |
| D_pcb | PCB outline diameter | [46.0] mm | +-0.15 (shop, assumed) | inside the 46 to 48 mm of ADR-0003; ring D 40 + LED half size 1.0 leaves 2.0 mm to the edge |
| t_pcb | PCB thickness | [1.6] mm | +-0.16 | A8 |
| D_ring | LED ring diameter (centres) | [40.0] mm | +-0.2 position (HW-001) | HW-001 (at least 38); pitch 7.85 mm |
| N_led | LEDs | 16 at 22.5 degrees | +-1 degree | HW-001 |
| h_led | LED package height above PCB | [0.65] mm | +-0.1 | XL-2020 part read; WS2812C-2020 not found |
| d_led | LED top to diffuser underside | [8.0] mm | +-0.86 (stack) | 4.2; stack in report 4.3 item 4 |
| t_diff | Lid plate thickness | [1.2] mm | +-0.2 | coupons at 0.8, 1.2, 1.6 (a PLA study prefers 0.8 mm, report M7) |
| Z_lid_in | Lid underside, from the floor outside | [15.25] mm | +-0.2 | Z_led + d_led |
| Z_led | LED top | [7.25] mm | | Z_pcb_top + h_led |
| Z_pcb_top | PCB top face | [6.6] mm | | Z_pcb_bot + t_pcb |
| Z_pcb_bot | PCB underside (sits on the posts) | [5.0] mm | | t_floor + H_post |
| H_post | Post height above the floor top | [3.0] mm | +-0.2 | bare PCB underside (SYS-022); 3 mm is a working value |
| N_post | PCB posts | [3] at 120 degrees, radius [21.0] mm, top pad [4.0] mm wide x [1.0] mm radial | | under the LED ring, none at the USB-C azimuth; the underside is bare (SYS-022); also three locating pegs, see below |
| g_peg | Locating pegs | [3] pegs against the PCB edge, clearance [0.2] mm per side | +-0.2 | stack 1; one PCB edge notch [R1.5] makes the board fit one way only (poka-yoke) |
| hook | PCB retention | [3] snap hooks on the posts, overlap [0.6] mm over the PCB top | | alternative: nylon screws through the PCB (O7) |
| spigot | Lid joint | base spigot [1.15] mm thick, joint zone Z [14.0] to [15.25] (1.25 mm high); lid skirt [0.9] mm thick; clearance [0.35] mm per side | clearance min 0.05 at worst case | stack 5: 0.25 mm can interfere; 0.35 mm is the minimum |
| lid hooks | Lid retention | [3] cantilever snap hooks, 120 degrees, at azimuth 60, 180, 300; engagement [0.6] mm; arm length [8] mm | | joint zone is only 1.25 mm high, so hook engagement 0.6 mm is tight (open point, section 4.11); strain limit of PETG/ASA: not found; tune by coupon; screw fallback M2.5 thread-forming in [3] bosses (heat-set inserts need 2 mm wall beyond the insert, report F9) |
| window | USB-C window in the base wall | [14.0] x [8.0] mm, corner radius [1.0] | +-0.3 | overmold 12.35 x 6.5 mm (USB-IF, read) + position stack 0.60 per side + size tolerance (report 4.3 item 3, unchanged in the re-run); centre at the receptacle axis; Z 4.25 to 12.25, 2.25 mm above the floor top, 1.75 mm below the joint zone |
| Z_usb | Window centre height | [8.25] mm | +-0.2 | Z_pcb_top + [1.65] (half the receptacle height; **receptacle not chosen**) |
| az_usb | Window azimuth | [0] degrees (rear) | | |
| funnel | Entry lead-in on the outside of the window | [0.8] mm chamfer | | helps misaligned plugs; may allow a smaller window later |
| btn | Button hole | [7.0] mm diameter, centre height Z_pcb_top + [1.0] mm | +-0.3 | switch actuator position **not chosen**; finger access; a printed plunger of [5.0] mm in a [5.4] mm bore is the alternative |
| az_btn | Button azimuth | [240] degrees | | |
| label | Label recess | [21.0] x [21.0] mm, depth [0.3] mm, in the outer face of the floor, centred on the axis | +-0.2 | MECH-006 at least 20 x 20 mm; label thickness not known (assumption: thin adhesive label, at most 0.3 mm); floor keeps 1.7 mm |
| az_mod | Module position | at the board centre, antenna end at azimuth [180] degrees | | ADR-0003 option A; antenna end edge 8.3 mm from the axis (4.6) |
| keep-out | Antenna keep-out | see 4.6 | | |
| feet | Feet | [4] pads, [1.0] mm tall, outside the label recess (diagonals, radius [21] mm, pad R [3] mm) | | the label stays 1.0 mm above the desk and is not scraped; clear of the recess by 3.2 mm |

Dimension chain check (script `mech_analysis_v2.py`, report section 8): the radial gap between the PCB and the wall is 1.90 mm (1.38 mm worst case, RSS 1.56 mm); there is no label facet stack any more; the LED-to-diffuser distance is 8.0 mm with a worst-case range of 7.14 to 8.86 mm. Distances from the floor outer face are used for all Z values; the feet add 1.0 mm below it.

### 4.4 Why 53 mm now (was 55 mm)
The first draft used 55 mm because a side label facet cut 3 mm off the wall and left 0.8 mm (worst case) to a PCB of 44 mm. With the label on the underside there is no facet. A circle of 53 mm with a 1.6 mm wall has a 49.8 mm inner diameter. The PCB of 46 mm (inside the 46 to 48 mm of ADR-0003) leaves 1.90 mm per side, 1.38 mm in the worst case. This is thinner than the 3.90 mm of the first draft, so the PCB centring (3 pegs) matters more. D_out equals the SYS-028 working value. A PCB of 48 mm (top of the ADR-0003 range) would leave 0.9 mm and 0.38 mm worst case: not recommended.

### 4.5 USB-C and button (MECH-004)
- Cable limit used: the USB-IF overmold envelope 12.35 x 6.5 mm (read, Compliance Document Rev 2.1b). A project note says 12.85 x 7.0 mm after an update (snippet, not confirmed). The 14.0 x 8.0 mm window also passes 12.85 x 7.0 mm at nominal position (slack 1.15 mm and 1.0 mm), but not at worst-case misalignment.
- The window is larger than the cable because FDM position error adds up (receptacle on the board +-0.1, board in housing +-0.3, window +-0.2). A funnel and tighter PCB location may let the window shrink to about 13.2 x 7.3 after the first prototype shows the real scatter.
- The overmold must be able to reach the receptacle mouth. A known failure is a receptacle that sits behind a small opening so that the plug cannot mate fully (report F7). The window passes the whole overmold through the wall. The distance from the outer wall surface to the board edge is 3.5 mm nominal (wall 1.6 mm plus a radial gap of 1.9 mm; 5.5 mm in the first draft); if the receptacle overhangs the board edge, this shrinks. The plug shell is 6.65 mm long (read); the overmold length behind it is **not found** (report F5). Whether the plug reaches full mating depth therefore cannot be derived now. The hardware designer must give the position of the receptacle mouth; the owner checks it on a mock-up with the real cables (three common cables including one with an overmolded plug and one with a thick strain relief).
- The button is reached from the side through a hole. The press force, travel and the switch height are hardware choices (HW) not yet made.
- Programming: the USB-C port carries USB-Serial-JTAG (ADR-0009 context). Test points on the underside need the lid off and the board lifted (the board sits on posts, no screws), which is acceptable for the production test fixture; HW-006 decides the points.

### 4.6 Antenna keep-out (MECH-003)
Facts (analysis report and ADR-0011 evidence):
- ESP32-C3-MINI-1 is 13.2 x 16.6 x 2.4 mm. The antenna area on the land pattern is the end strip of about 13.2 x 5.4 mm (read from datasheet v2.2 figures 10-1 and 11-1; the exact keep-out rectangle is in the Espressif figure 21 of the hardware design guidelines, an image: **not found as text**).
- The Espressif hardware design guidelines (release master, 3 Nov 2026) say: place the on-board antenna outside the base board where possible; if not possible, cut the board away on both sides and below the antenna; **do not place the module in the centre of the board with clearance on all four sides**; and, for the housing, **"a clearance of at least 15 mm is recommended in all directions"** around the antenna, with a throughput and range test of the final product.
- The vendor text mixes two things. What the housing controls: material and distance of the walls. What the PCB layout controls: LEDs, tracks and ground near the antenna and the centre placement. The 15 mm figure cannot be met literally in a 53 mm unit: the lid, the floor and the label are less than 15 mm from the antenna in Z.

Split of responsibility (resolution, section 4.11):
- **Housing (MECH-003):** inside the 15 mm box around the antenna area only non-conductive plastic. The nearest wall is at least 15 mm from the antenna edge.
- **PCB layout (ADR-0003, HW-005):** LEDs, tracks and ground within 15 mm of the antenna, and the module in the board centre. Recorded as a finding in ADR-0003 (Proposed, dated 2026-11-04).

Numbers (report section 8, `mech_analysis_v2.py`): module at the board centre, antenna end at azimuth 180, antenna end edge 8.3 mm from the axis; inner wall radius 24.9 mm.
- Middle of the end edge to the inner wall: 16.6 mm (outer surface 18.2 mm). This meets 15 mm.
- The two end corners (10.6 mm from the axis) to the inner wall: **14.3 mm** (outer surface 15.9 mm). This is 0.7 mm below 15 mm. It does not fit literally. The wall is plastic, so the rule that matters is "no conductive material", which holds. The range test decides whether the 0.7 mm matters. A D_out of 55 mm would give 15.3 mm at the corners (the old draft value).
- Lid underside to the antenna plane: 8.65 mm; floor outer face to the antenna plane: 6.6 mm. Both are inside the 15 mm box and are plastic. The label is in this box (underside, 6.6 mm below the antenna plane): the label must not be metallised.
- Nearest LED centre to the antenna rectangle: about 9.5 mm (11.7 mm on the module axis; the LED package edge is about 1 mm closer). This is below 15 mm and is a layout matter: the range test of SYS-038 (TC-038) accepts it, or the layout changes it.

Mechanical rules (the plastic wall and lid are unavoidable and are not conductive):
1. Inside a box of antenna area plus [15] mm in all directions, the housing has no metal, no magnet, no screw, no metal insert, no conductive or carbon filament, no metallic or "silk metallic" filament, no metallic or conductive paint, no metallised label, no cable. Plastic only.
2. The snap-fit version has no fasteners at all. The three snap hooks are plastic. If the screw fallback is used, screws are nylon or sit more than [15] mm from the antenna area; steel screws at R 25 would be 14.4 mm from the antenna corner (16.7 mm from the end edge), so they are not allowed.
3. The USB-C receptacle shell is metal. Its distance to the antenna is a layout question (HW-005).
4. The antenna end of the module points away from the USB-C connector (ADR-0003, USB-C at azimuth 0, antenna at 180) and toward the window-free side of the housing.
5. Whether the 15 mm figure applies to plastic as well as to metal is unclear in the text. The range test of SYS-038 (TC-038, TC-303) with the finished housing decides. This is the most uncertain item of the plan (RISK-011).

### 4.7 Thermal and material (MECH-005)
Analysis (report 4.2, rough estimate, one isothermal surface, bottom excluded, h_conv 10 / 5 / 3 W/m2K, emissivity 0.9):
- Shell for D 53 x H 16.5 mm (bottom excluded): 49.5 cm2, 31 % smaller than the first draft (72.1 cm2). The temperature rise is 1.4 times higher. Surface rise at 2.5 W: 30.9 / 43.1 / 50.7 K (first draft 21.6 / 30.7 / 36.5). At 0.5 / 1 / 2 / 3 W: 6.5 / 12.8 / 25.0 / 36.7 K at h_conv 10; 11.6 / 22.3 / 41.8 / 59.1 K at h_conv 3. At 4.7 W: 55 / 74 / 85 K. At 6.75 W: 76 / 99 / 111 K.
- Allowed power for a 15 K margin to HDT, room 35 deg C: PLA 0.2 to 0.8 W, PETG 0.9 to 2.3 W, ASA 2.8 to 4.7 W (first draft: PLA 0.3 to 1.2, PETG 1.3 to 3.4, ASA 4.1 to 6.8 W).
- Consequence: PLA is out; PETG now fails the full 500 mA dissipation (2.5 W) in a 35 deg C room for every convection value, and also at 25 deg C for the low values; ASA passes 2.5 W in all cases but fails 4.7 W at 35 deg C. The smaller housing makes ASA more necessary and the 3.0 to 4.7 W worst case less acceptable. If the unit lies on a desk the bottom is not free; if the desk side sheds heat, the result is close to the first draft (all faces, 3 W: 25.9 / 36.5 / 43.2 K). The lid is PETG in the recommended process and runs near the LEDs: its HDT (65 to 78 deg C by brand) is the weak point. Check with TC-305 and consider an ASA-like translucent grade or a resin lid if it fails (not researched).
- The cap of 1350 mA allows 6.75 W. The housing cannot shed that in a closed shape at a 15 K margin, even in ASA, if all of it were dissipated. Realistic worst case is 3.0 to 4.7 W. Whether the firmware should limit LED power by temperature (a sensor on the module is a hardware matter) is a question for SYS-020 and ADR-0009, not decided here.
- Vents: a closed housing is assumed. Vent slots would help heat but spoil the diffuser and the antenna keep-out; not proposed.
- Material data to be named on the drawing: filament maker, grade, colour, datasheet, HDT value and method, flammability class (not found for the owner's filament; O2).

### 4.8 Design for 3D printing (rules for the owner's model)
Sources are in the report, section 2.3 (F8, F9), and are for industrial FDM or search summaries of desktop guides; the owner's printer has the last word and a coupon decides.

| Topic | Rule | Source / status |
|-------|------|-----------------|
| Minimum wall | At least 4 x layer height (0.25 mm layer: 1.0 mm); use whole numbers of perimeters of the nozzle width (0.4 mm nozzle: 1.2 mm, 1.6 mm, 2.0 mm) | Stratasys (read); nozzle multiples: engineering practice |
| Tolerance | Plan with +-0.2 to 0.3 mm on desktop FDM; holes come out undersized; print a coupon before the first housing | Stratasys (read, industrial); search summaries (snippet) |
| Clearance between mating parts | At least 0.25 to 0.35 mm per side for a slip fit; this plan uses 0.35 mm at the lid spigot (stack: 0.25 mm can bind) | Stratasys (clearance follows layer height); stack in the report |
| Orientation | Base: floor on the bed, posts and hooks vertical. Lid: plate on the bed, skirt up; no supports. The label recess (0.3 mm) is on the bed side: check that elephant foot does not close it; the 1.0 mm feet are part of the print | engineering practice |
| Overhangs and supports | No overhang above 45 degrees without a plan; the USB window top is a bridge of 14 mm: round or chamfer the top of the window or accept a bridge | engineering practice, not sourced |
| Snap hooks | Orient the arm so that the layer lines run along its length (an arm that bends across layer lines breaks easily). Fillet the root. Strain limit for PETG and ASA: **not found**. Prove [100] cycles on a coupon (MECH-006) | search summary says fillet the arm root (snippet) |
| Screw bosses (fallback) | Thread-forming M2.5 into the plastic or heat-set inserts; wall around an insert at least 2.0 mm beyond its diameter (Stratasys); gussets on tall bosses | Stratasys (read) |
| Large flat lid | A 53 mm flat plate warps in PETG and ASA; use brim, a draft-free enclosed printer for ASA, and check flatness (0.3 mm?) | engineering practice, not sourced |
| Translucent lid | Use natural or white filament; 3 or more top layers; infill pattern shows through; test 0.8 / 1.2 / 1.6 mm plates over an LED ring; layer height 0.2 mm gave the best transmittance of 0.1 to 0.3 mm in one PETG study | studies in search results (snippet) |
| Marking | Part number, revision and material code (ISO 11469 style) moulded or printed on the underside of the base, next to the label recess and outside it (DFx 4) | DFx standard |
| General tolerance | ISO 2768-m as the default on the drawing for features not listed; all critical features in 4.3 carry a stated tolerance | DFx standard 1 |

### 4.9 Assembly, serviceability, test access
- Assembly from one direction: PCB onto posts and under the hooks, lid pushed on until the hooks click. No tools, no fasteners. Poka-yoke: one PCB notch and one peg make the PCB fit one way.
- Service: the lid comes off with a fingernail or coin in a [2.0] mm pry slot at azimuth 120, between two hooks. Open and close [100] times (MECH-006 acceptance) is proven on a coupon first.
- No permanent bonding. The lid cannot be removed from the label side: the label is on the base.
- Test access: USB-C port for programming; underside test points need the board lifted; no extra access features.

### 4.10 NFR and regulatory check (guidance, not legal advice)
- Safety: low-voltage (5 V) device; the heat estimate shows the surface temperature rise of 31 to 51 K at 2.5 W, meaning a surface up to 76 deg C in a 25 deg C room at the pessimistic convection value (first draft: 60 deg C). This is more than a plastic touch limit allows without a check. Touch temperature limits for accessible plastic surfaces (EN 62368-1) are **not found** (verify). Flammability class of the enclosure material and the power-source class: not looked up (verify). Filament RoHS/REACH declarations: ask the maker (O2).
- Labelling: the label area (MECH-006, underside) carries identifier, passphrase, QR code and the "prototype, not for sale" mark; CE and WEEE marks are not needed for a prototype that is not placed on the market (see `docs/regulatory/`); check again with skill `regulatory-check` before any sale. Label durability and legibility test: MECH-006 acceptance.
- Reliability: snap hooks creep in warm PETG; a screw fallback exists.
- Sustainability: reopenable, no glue; plastics marked.
- Security: the passphrase label is on the underside of the base, so it is not visible when the unit lies on a desk and is less exposed to photographing from a distance; opening the lid does not expose it more; physical access to the USB-C port exists by design (ADR-0007 covers firmware).
- Manufacturability: two parts, one translucent; prints on a desktop FDM printer; no supports expected.

### 4.11 Resolution of the three conflicts (2026-11-04)
These are the author's decisions. The owner confirms or rejects them. Everything stays Draft or Proposed. Numbers come from `mech_analysis_v2.py` (report section 8).

| # | Conflict | Before (first draft) | After (this revision) |
|---|----------|----------------------|-----------------------|
| 1 | MECH-006 "not hidden on a desk" forced a side label facet and 28 mm height | Label on a side facet, Z 2 to 23; H 28.0 mm; D 55.0 mm | Assumption A1: unit lies flat, ring up. Label recess 21 x 21 x 0.3 mm in the underside of the floor, 4 feet 1.0 mm tall outside it. H 16.5 mm (16.45 computed; 17.45 with feet). No facet. The label is not visible on the desk; it is read when the unit is lifted |
| 2 | 15 mm antenna clearance "in all directions" cannot be met literally | MECH-003 asked for the distance of ADR-0003; rule text mixed housing and layout | MECH-003 limited to the housing: plastic only in the 15 mm box; nearest wall at least 15 mm from the antenna edge. 16.6 mm at the middle of the end edge, **14.3 mm at the corners (not met by 0.7 mm)**. LEDs, tracks and ground within 15 mm and the centred module are a layout matter in ADR-0003 |
| 3 | ADR-0003 PCB 46 to 48 mm did not fit the label facet | D_pcb 44.0 mm; gap to the facet 1.38 mm (0.80 worst case) | D_pcb 46.0 mm, inside ADR-0003; D_out 53.0 mm; radial gap 1.90 mm (1.38 worst case, RSS 1.56) |

Other values that changed: post height 14.55 to 3.0 mm; Z_pcb_bot 16.55 to 5.0 mm; Z_pcb_top 18.15 to 6.6 mm; lid underside 26.8 to 15.25 mm; window centre Z 19.8 to 8.25 mm; joint zone Z 25.0 to 26.8 to Z 14.0 to 15.25; wall to PCB edge 5.5 to 3.5 mm; shell area 72.1 to 49.5 cm2; printed mass about 19 g to about 14 g (PETG, estimate: walls and plates solid, no infill model, PCB excluded). Unchanged: ring pitch 7.85 mm, d_led 8.0 mm, light ripple (1.1 % at 60 deg, 2.4 % at 45 deg), window 14.0 x 8.0 mm (stack unchanged), spigot clearance 0.35 mm.

What still does not fit or is open:
- Antenna: 14.3 mm at the corners to the inner wall (0.7 mm below 15 mm); LED centres about 9.5 mm from the antenna area; lid, floor and label are inside the 15 mm box and are plastic. The range test (TC-303, TC-038) decides.
- The label cannot be "outside the antenna box": the floor face is 6.6 mm below the antenna plane. MECH-006 asks for a non-metallised label instead.
- The thermal margin is worse: PETG fails 2.5 W in a hot room; ASA passes 2.5 W but not 4.7 W.
- The joint zone is 1.25 mm high; snap hooks with 0.6 mm engagement are tight. A coupon decides; the screw fallback needs bosses that the thin joint does not allow (open point for the first CAD).
- The label on the underside cannot be read while the unit is in use, and the unit must not stand on its edge or hang (A1).
- Re-scored ADR-0011: B leads A by 14 points (was 18); thermal score of P1 (PETG) lowered, P1 leads P2 by 3 (was 8): inside scoring error.

## 5. Detailed implementation plan
Nothing here is done by the elephant. After the owner approves the MECH requirements and this plan, the owner makes the CAD model. Files that **would** be created or changed later:

- **Files to create (owner, FreeCAD):** `mech/freecad/busy-light-housing.FCStd` (parametric model: spreadsheet `Params` with the names of 4.3, bodies `Base` and `Lid`, assembly with the STEP of the PCB), later `mech/exports/<rev>/base.step`, `lid.step`, `base.stl`, `lid.stl`, `mech/drawings/` (2D drawings with tolerances, material, revision).
- **Files to create (analysis, after approval):** `mech/analysis/light_uniformity.py`, `thermal_estimate.py`, `tolerance_stack.py` (the scripts of the report, `mech_analysis_v2.py` for the current numbers, parameterised by the FreeCAD spreadsheet values), `mech/analysis/README` of results, `docs/verification/reports/` for evidence.
- **Documents to change (after owner approval):** `docs/requirements/mech.md` (see section 7 proposals), `docs/decisions/ADR-0003-antenna-and-board-topology.md` (PCB size 46 mm, antenna finding of 2026-11-04), `docs/verification/test-cases-hw-mech.md` (procedures, only when requirements are Approved), `docs/risk/risk-register.md` (new risks of section 7), `CHANGELOG.md`.
- **Never by Claude:** any `.FCStd` or `.kicad_*` file.

### 5.1 Order of work
1. Owner answers the questions of section 7; approves MECH-001..006 (with changes).
2. Owner gives the PCB outline and the positions from KiCad (5.4), or confirms the working values of 4.3 so that hardware can start (hardware design has not started).
3. Increment 1, coupons: tolerance coupon (window, spigot, posts, hooks, holes), diffusion coupons (plate 0.8 / 1.2 / 1.6 over an LED ring at 4 / 6 / 8 mm). Needs a mock-up ring of LEDs (strip or breakout; hardware task).
4. Increment 2, first housing in the chosen process; PCB mock-up as a printed disc with the real connector.
5. Increment 3, with the first PCB: fit, USB cable, thermal, antenna range (TC-301..306).
6. Revise, release the package in `mech/exports/<rev>/`.

### 5.2 Interference check
Each revision: KiCad exports STEP of the PCB; the owner imports it in FreeCAD and runs the interference check; the result is recorded in `mech/analysis/` (DFx standard 6).

### 5.3 What the owner models in FreeCAD (handoff table)
Create one spreadsheet `Params` with the parameter names of 4.3 and derive the features from it. Features in modelling order:

| # | Body | Feature | Parameters (4.3) | Notes |
|---|------|---------|------------------|-------|
| 1 | Base | Outer cylinder | D_out = 53.0, H_base = 14.0 | floor outer face on Z = 0 |
| 2 | Base | Cavity | t_wall, t_floor | inner D = D_out - 2 t_wall = 49.8 |
| 3 | Base | Feet | feet: 4 pads R3, 1.0 tall, radius 21 on the diagonals | on the underside; below Z = 0 |
| 4 | Base | Label recess | label 21 x 21, depth 0.3 | in the outer face of the floor, centred, outside the feet |
| 5 | Base | Posts | N_post, radius 21.0, H_post = 3.0, pad 4.0 x 1.0 | tops at Z_pcb_bot = 5.0; none at azimuth 0 (USB-C) |
| 6 | Base | PCB pegs and notch peg | g_peg, notch R1.5 | needs the KiCad outline (5.4) |
| 7 | Base | PCB hooks | hook | on the posts, overlap 0.6 |
| 8 | Base | USB window | window, Z_usb = 8.25, az_usb, funnel | rectangular 14.0 x 8.0, corner R1.0, through the wall, Z 4.25 to 12.25; check the cable path to the receptacle mouth |
| 9 | Base | Button hole | btn, az_btn | Z from the switch actuator in KiCad |
| 10 | Base | Spigot | spigot, Z 14.0 to 15.25 | inner part of the wall |
| 11 | Base | Hook grooves | lid hooks, az 60 / 180 / 300 | on the spigot outer face |
| 12 | Base | Marking | part number, revision | underside, outside the label recess |
| 13 | Lid | Plate | D_out, t_diff, Z_lid_in | flat, no features on the light path |
| 14 | Lid | Skirt | skirt 0.9, spigot clearance 0.35, height 2.45 (Z 14.0 to 16.45) | |
| 15 | Lid | Snap hooks | lid hooks | arms along the skirt |
| 16 | Lid | Notch for the USB window | window | the window top is at Z 12.25, below the joint zone at 14.0, so the lid needs no notch; check this when the receptacle is chosen |
| 17 | Lid | Pry slot | 2 mm slot at azimuth 120 | between the hooks at 60 and 180 |
| 18 | Assembly | PCB | STEP from KiCad | interference check 5.2; module at the board centre, antenna end at azimuth 180 |
| 19 | Both | Coupon variants | d_led 4 / 6 / 8, t_diff 0.8 / 1.2 / 1.6 | variants of the same model |

Check before saving: all numbers come from `Params`; no magic numbers in sketches; name bodies as in the table.

### 5.4 What needs the PCB outline from KiCad (ask the owner; hardware design has not started)
The following are open until the hardware design gives them. The plan uses the working values of 4.3 and 2 (A3, A5):
1. Board outline: diameter, any flats or notches, thickness (D 46, 1.6 mm assumed).
2. LED ring: centre, ring diameter, angle of LED 1, LED package height.
3. Module: position, rotation, antenna area and keep-out rectangle, module height (2.4 mm).
4. USB-C receptacle: part number, position on the board, height above the board, how far the mouth is from the board edge, shell dimensions, panel cut-out drawing.
5. Button: part, position, actuator height above the board, side or top actuation, travel.
6. Tallest part under the lid, and any part under the board (the underside is meant to be bare).
7. Test points and programming points (HW-006).
8. Mounting holes or edge notches (O7).
9. 3D STEP of the board for the interference check.

## 6. Test and verification plan
Procedures wait for Approved requirements; this table only maps evidence to the existing `TC-nnn` entries (`docs/verification/test-cases-hw-mech.md`, procedures still TBD).

| TC | Requirement | Level | Analysis first | Prototype evidence | Notes |
|----|-------------|-------|----------------|--------------------|-------|
| TC-301 | MECH-001 size | Prototype | CAD dimension check (D 53, H 16.5) | caliper on [3] housings | MECH-001 should say if the cable is excluded |
| TC-302 | MECH-002 diffuser | Prototype | `light_uniformity.py` (report 4.1), coupon plan | photo at 1 m under office light; intensity at 0.5 m through the lid (SYS-001, TC-001 gear) | the number for "no point source" needs a definition (working: ripple at most 10 %) |
| TC-303 | MECH-003 antenna | Inspection | drawing shows the plastic-only box and the wall distance of 4.6 (16.6 mm at the end edge, 14.3 mm at the corners); range test of SYS-038 / TC-038 with the finished housing | range test, 6 dB rule of SYS-038 | depends on ADR-0003 and spike 7.2 |
| TC-304 | MECH-004 access | Prototype | tolerance stack (report 4.3) | [3] common cables incl. one overmolded plug and one with a thick boot; finger on button | name the cables |
| TC-305 | MECH-005 thermal | Prototype | `thermal_estimate.py` (report 4.2) | thermocouples at the LED ring, module, lid, wall; full limited power, closed housing, [25] deg C, stable to 1 K per 10 min | later FEA only if the measurement shows hot spots that the lumped model cannot explain |
| TC-306 | MECH-006 label | Inspection | drawing; stack 2 | label 21 x 21 applied, [100] open-close cycles on the lid, readability check | label sits on the floor of the base, underside; lift the unit to read it |

Other checks: first-article dimension check of the critical features of 4.3 (calipers or pin gauges) and a tolerance coupon per printer/material change; DFx review with `design-review` before approval; interference check with the KiCad STEP per revision.
Later FEA only if justified: the snap hooks (if a coupon fails before 100 cycles) or a thermal-structural case if TC-305 shows the lid deforming. A thermal FEA is not justified now: the inputs (h, the heat path of the module) are less certain than the model error.

What was not run: any measurement, any CAD or interference check, any RF analysis, any printing, any resin or material search beyond the report. The analysis in the report is a lumped estimate and a script.

## 7. Risks and open questions
Risks (proposed; not added to the risk register; RISK-005 and RISK-011 already exist):

| Id | Risk | Effect | Mitigation |
|----|------|--------|------------|
| R1 | The single lid does not diffuse enough; points show | MECH-002 fails | coupon test first; fallback concept A; resin lid |
| R2 | PETG lid or base softens at full limited power in a hot room (RISK-005) | deformation, LED shift | ASA base; measure TC-305; thermal input to SYS-020 |
| R3 | Antenna detuned; the 15 mm vendor clearance cannot be met (14.3 mm at the corners to the wall; LEDs about 9.5 mm; label and lid inside the box) (RISK-011) | range below SYS-038 | no metal in the box; range test; ADR-0003 fallback (u.FL) |
| R4 | Snap hooks fail or loosen before [100] cycles | MECH-006 acceptance | coupon test; screw fallback |
| R5 | The USB-C window is too small for a real cable, or the overmold cannot reach the receptacle | MECH-004 fails | window 14.0 x 8.0; mock-up with real cables; receptacle position from hardware |
| R6 | (was: label facet leaves 0.8 mm) Now: radial gap PCB to wall is 1.38 mm worst case, RSS 1.56 mm; label on the underside may be scraped or hidden if the unit stands on its edge | board touches the wall; label unreadable in use | peg location; PCB D 46 not 48; feet keep the label 1.0 mm off the desk; assumption A1 |
| R7 | Owner's printer or material differs from A2 | tolerances and HDT change | questions O2; recalculate with the script |
| R8 | The PCB outline from hardware differs from 4.3 | redo of the stack | work in the parameter sheet |
| R9 | Warping of the large lid | gap at the joint, light leaks | brim, enclosed printer, flatness check |
| R10 | Overmold envelope larger than 12.35 x 6.5 mm (one note says 12.85 x 7.0) | some cables do not fit | test with cables; window margin |
| R11 | Enclosure fire and touch-temperature rules apply (EN 62368-1, verify) | redesign of material | regulatory check before approval |

Open questions for the owner:
- **O1 Orientation. Answered by the owner 2026-11-04: both horizontal and vertical (A1 withdrawn).**
  - Owner decisions 2026-11-04 (answers to the orientation follow-up): (1) the back of the housing gets a small threaded interface that accepts a horizontal stand, various clips or a blank plate; (2) the label goes on the back; (3) an orientation sensor is added to the product, so the ring can align itself (level-mode zero position) and for other uses such as a clock mode (the ring shows the time, with 12 o'clock at the top in any orientation; a new feature, no requirement yet). Follow-ups 2026-11-04: the back interface is decided in ADR-0014 (Proposed). Clock mode is planned for a later release (owner, 2026-11-04). The orientation sensor should align the ring automatically; with an accelerometer this works when the unit hangs or stands, and for a flat unit the zero is fixed on the board (ADR-0014). Not yet done: requirements for the sensor and the mount interface (NEED/SYS/HW/MECH drafts), revision of the housing concept, dimensions and thermal model, and the cost and power effect of the sensor (SYS-021, SYS-020). Was: does the unit lie on a desk with the ring up, stand on its edge facing you, or hang on a wall? The label rule (not hidden when standing) and the ring surface depend on it. A wall hang or a stand changes the foot, the label position and the height. The flat-lying case was taken: the height dropped from 28 to 16.5 mm.
- **O2 Printer and material.** FDM or resin? Which filaments (PETG, ASA, PLA)? Enclosed printer? Datasheet and flammability class of each filament? Natural or white translucent filament for the lid?
- **O3 Ring look.** A wide band or disc glow, or a thin sharp ring?
- **O4 Size. Answered by assumption: D 53.0 mm (SYS-028 working value) and H 16.5 mm (17.45 mm with feet); the owner confirms.** Was: is 55 mm acceptable? Is height 28 mm acceptable?
- **O5 Highest room temperature** for MECH-005 (working value 35 deg C) and the accessible surface temperature you accept.
- **O6 Cable list.** Which three cables are the "common" cables (MECH-004)? Does the unit need to work with a right-angle plug or a thick boot?
- **O7 PCB fixing.** Snap hooks on the board edge (no holes), or screws through the board (metal in the keep-out)?
- **O8 Button.** Which button type and which side? Does it need a printed cap?
- **O9 Antenna.** Do you accept that the housing proposes plastic only in the 15 mm box, that LEDs and tracks near the antenna are a layout matter (ADR-0003 finding), and that spike 7.2 decides the range? Is ADR-0003 B (u.FL) still the fallback?
- **O10 Label.** Which label material and thickness (not metallised, at most 0.3 mm)? Is the label printed or hand-written?
- **O11 Feet or magnets.** Rubber feet (not in the antenna box)? Magnets are not allowed near the antenna.
- **O12 Process split.** May the base and the lid be different materials (base ASA, lid PETG)?
- **O13 Proposals to MECH requirements** (not changed by me): MECH-001 says whether the cable counts; MECH-002 gets a number (working: ripple at most 10 % along the ring); MECH-003 limited to what the housing controls (plastic-only 15 mm box, wall at least 15 mm from the antenna edge); MECH-004 names the overmold envelope (12.35 x 6.5 mm); MECH-005 names the room temperature; MECH-006 reworded for the underside label (done in `docs/requirements/mech.md`, still Draft).

## 8. Rollout / rollback and traceability
IDs created: none new. This plan, ADR-0011 (Proposed) and the report `mech-concept-analysis.md` (Draft) are new documents. Proposed text for new risks is in section 7 and ADR-0011; not added to the register.
Reverted if it fails: delete the three documents; nothing else depends on them. No `mech/`, `hw/` or `sw/` file is changed.
Traceability: MECH-001..006, SYS-001, SYS-013, SYS-017, SYS-020, SYS-028, SYS-038, HW-001, HW-005, HW-006, HW-010, ADR-0003, ADR-0009, ADR-0011, RISK-005, RISK-011, TC-301..TC-306, TC-038. Run `python3 -I scripts/check_traceability.py` after changes to `docs/`.
Next step: owner reviews, then the EGM goldfish passes (comprehension, antagonistic, readiness) run on this document, outcome recorded as `RV-nnn` in `docs/reviews/`.
