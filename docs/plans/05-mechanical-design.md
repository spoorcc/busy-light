# 05 -- Mechanical design: housing for the LED status ring (design doc)

- **Status:** Draft (elephant draft; no goldfish review yet; the owner has not approved it; the MECH requirements are Draft)
- **Date:** 2026-11-04  **Owner:** Ben Spoor
- **Area:** mech (planning only; nothing in `mech/`, `hw/` or `sw/` is created or changed by this plan)
- **Requirements addressed:** MECH-001, MECH-002, MECH-003, MECH-004, MECH-005, MECH-006 (all Draft). Parents: SYS-001, SYS-013, SYS-017, SYS-020, SYS-028, SYS-038. Interfaces to HW-001, HW-005, HW-010 and HW-006.
- **Decision record:** ADR-0011 (Proposed). Analysis: `docs/verification/reports/mech-concept-analysis.md` (Draft, not measured).
- **EGM review record:** none yet (comprehension / antagonistic / readiness passes still to run)

## 1. Problem definition
The product needs a housing. It must hold one round PCB with 16 RGB LEDs on a ring, an ESP32-C3-MINI-1 module with its on-board antenna, a USB-C connector and one button. The housing is 3D printed. It turns the 16 LEDs into a closed band of colour that is readable at desk distance (SYS-001, MECH-002), is about 53 mm across (SYS-028: 48 to 58 mm, MECH-001), and carries the unit label (MECH-006, SYS-013).
Why now: ADR-0003 and the hardware requirements need the housing limits (ring size, board outline, connector positions) before the PCB outline is drawn, and the thermal and material choice (RISK-005) affects the firmware current limit (SYS-020, ADR-0009).
Out of scope: the PCB design (ask the owner for the outline, section 5.4), firmware, user documentation, injection moulding, ingress protection (no IP requirement exists), a wall or ceiling mount (orientation is an owner question), CAD files (the owner makes them).

Status of the inputs: the MECH requirements are Draft and not approved, so this plan is a **proposal for the owner to approve first**. No file in `mech/` may be created from it until the owner approves the MECH requirements.

## 2. Constraints and assumptions
Constraints (from requirements and ADRs, quoted):
- Largest outer dimension 48 to 58 mm with the board fitted (MECH-001, SYS-028 [53] mm).
- 16 LEDs at 22.5 degrees on one circle of at least [38] mm, all on one board side (HW-001, SYS-028).
- No single LED visible as a point at 1 m; closed band (MECH-002).
- No metal, conductive filament or metallised paint at the antenna, to the distance of ADR-0003 (MECH-003). ADR-0003 gives no distance. The vendor figure is in section 4.6.
- USB-C access with a standard cable and a finger on the button, without tools (MECH-004).
- Material at least [15] K below its HDT at the highest internal temperature (MECH-005).
- Flat label area at least [20] x [20] mm that does not move when the housing opens and is not hidden when the unit stands on a desk (MECH-006).
- Board assembled on one side, no hand soldering (SYS-022): the underside of the PCB is bare, so the board can sit on posts.
- Power: 5 V, [500] mA default, up to [1500] mA when advertised (SYS-020). Dissipation up to 2.5 W at 500 mA, 3.0 to 4.7 W in the realistic worst case, 6.75 W at the 1350 mA limiter cap (power budget report; ADR-0009).

Assumptions (goldfish: challenge these):
- **A1** The unit lies flat on a desk and the ring faces up. The label is on a flat facet of the base side. (Owner question O1.)
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
| A | Clamshell: opaque base, opaque top cap with a ring window, separate translucent diffuser ring (3 parts) | 129 | Fallback if the single lid fails the diffusion test |
| **B** | Opaque base plus one translucent lid that is the diffuser (2 parts) | **147** | **Recommended** |
| C | Sphere of two snap-fit halves | 113 | Rejected: flat label and USB-C window on a sphere, supports, snap creep |
| D | Do nothing (bare board) | 122, excluded by gates | Baseline only |

Process (ADR-0011, second table): FDM with PETG (119) or ASA (111) for the base, natural translucent PETG for the lid; resin (104) as the fallback for the lid; PLA (113, excluded by the thermal gate). The tables do not separate PETG from ASA; the thermal estimate does (ASA safe, PETG marginal in a hot room).

## 4. Technical plan

### 4.1 Concept B in one paragraph
A cylinder of about 55 mm diameter and 28 mm height. The **base** (opaque, ASA or PETG) is a cup 25 mm tall: floor, a wall, three posts that hold the PCB near the top, a flat facet on the wall for the label, a window for the USB-C plug, a hole for the button. The **lid** (natural or white translucent PETG) is a 3 mm cap: a 1.2 mm plate that diffuses the light and a skirt that fits over a spigot of the base and snaps on. The PCB lies on the posts with the LED side up, [8] mm under the lid plate. The label sits on the base, so it does not move when the lid is taken off.

Figure (text only, no diagram is added because no CAD exists; draw it from the table in 4.3 once the owner has a model): section from top: lid plate, 8 mm air gap, LED ring on the PCB, 14.5 mm of posts, floor.

### 4.2 Diffusion (MECH-002)
- The lit band is the lid plate over the ring. LED-to-diffuser distance [8.0] mm, plate [1.2] mm, natural or white translucent PETG.
- Analysis (report 4.1): ring D 40 mm, 16 LEDs, pitch 7.85 mm. The cones of neighbours touch at 2.3 mm (60 deg half angle) or 3.9 mm (45 deg). A ripple of at most 10 % before any scatter needs 5.0 mm (60 deg) or 6.0 mm (45 deg). At 8 mm the ripple is 1.1 % (60 deg) or 2.4 % (45 deg). The beam angle of the shortlisted LEDs is **not found**; one 2020 part has 120 deg (read).
- Price of the distance: at 8 mm the lit band is up to 14 mm wide on each side of the ring at half intensity (60 deg). The ring looks like a wide glow or a disc. This is O6 (ring look).
- Options if the look is wrong: (i) smaller distance with a thicker or more scattering lid (test with coupons), (ii) an opaque central insert, (iii) concept A (separate ring with a mask).
- Photobiological safety of the LED ring (viewing a bright LED) is not assessed here; a diffuser lowers the risk. Verify against the LED standard in the regulatory check.

### 4.3 Working dimensions of the recommended concept
All values are working values in [brackets] for the owner's parameter sheet (section 5.3). Tolerances are the FDM assumption A7 until a coupon is printed. Part names: `Base`, `Lid`.

| Param | Feature | Value | Tolerance | Basis |
|-------|---------|-------|-----------|-------|
| D_out | Outer diameter of base and lid | [55.0] mm | +-0.3 | MECH-001 (48 to 58); 53 mm is the SYS-028 working value, 55 mm is the larger size needed for the label facet and the window, within the range |
| H_total | Total height | [28.0] mm | +-0.3 | 25.0 base + 3.0 lid |
| H_base | Base height to the joint | [25.0] mm | +-0.2 | label facet 21 mm + 2 mm each end |
| t_wall | Wall thickness | [1.6] mm | +-0.2 | 4 perimeters of 0.4 mm; 4 x layer height rule (report F8) |
| t_floor | Floor thickness | [2.0] mm | +-0.2 | |
| D_pcb | PCB outline diameter | [44.0] mm | +-0.15 (shop, assumed) | LED ring D 40 + LED half size 1.0 + 1.0 edge = 44; ADR-0003 says 46 to 48, which the label facet does not allow (4.4) |
| t_pcb | PCB thickness | [1.6] mm | +-0.16 | A8 |
| D_ring | LED ring diameter (centres) | [40.0] mm | +-0.2 position (HW-001) | HW-001 (at least 38); pitch 7.85 mm |
| N_led | LEDs | 16 at 22.5 degrees | +-1 degree | HW-001 |
| h_led | LED package height above PCB | [0.65] mm | +-0.1 | XL-2020 part read; WS2812C-2020 not found |
| d_led | LED top to diffuser underside | [8.0] mm | +-0.86 (stack) | 4.2; stack in report 4.3 item 4 |
| t_diff | Lid plate thickness | [1.2] mm | +-0.2 | coupons at 0.8, 1.2, 1.6 (a PLA study prefers 0.8 mm, report M7) |
| Z_lid_in | Lid underside, from the floor outside | [26.8] mm | +-0.2 | H_total 28.0 - t_diff 1.2 |
| Z_led | LED top | [18.8] mm | | Z_lid_in - d_led |
| Z_pcb_top | PCB top face | [18.15] mm | | Z_led - h_led |
| Z_pcb_bot | PCB underside (sits on the posts) | [16.55] mm | | Z_pcb_top - t_pcb |
| H_post | Post height above the floor top | [14.55] mm | +-0.2 | Z_pcb_bot - t_floor |
| N_post | PCB posts | [3] at 120 degrees, radius [21.0] mm, top pad [4.0] mm wide x [1.0] mm radial | | under the LED ring; the underside is bare (SYS-022); also three locating pegs, see below |
| g_peg | Locating pegs | [3] pegs against the PCB edge, clearance [0.2] mm per side | +-0.2 | stack 1; one PCB edge notch [R1.5] makes the board fit one way only (poka-yoke) |
| hook | PCB retention | [3] snap hooks on the posts, overlap [0.6] mm over the PCB top | | alternative: nylon screws through the PCB (O7) |
| spigot | Lid joint | base spigot [1.15] mm thick, from Z 25.0 to 26.8; lid skirt [0.9] mm thick; clearance [0.35] mm per side | clearance min 0.05 at worst case | stack 5: 0.25 mm can interfere; 0.35 mm is the minimum |
| lid hooks | Lid retention | [3] cantilever snap hooks, 120 degrees, at azimuth 60, 180, 300; engagement [0.6] mm; arm length [8] mm | | strain limit of PETG/ASA: not found; tune by coupon; screw fallback M2.5 thread-forming in [3] bosses (heat-set inserts need 2 mm wall beyond the insert, report F9) |
| window | USB-C window in the base wall | [14.0] x [8.0] mm, corner radius [1.0] | +-0.3 | overmold 12.35 x 6.5 mm (USB-IF, read) + position stack 0.60 per side + size tolerance (report 4.3 item 3); centre at the receptacle axis |
| Z_usb | Window centre height | [19.8] mm | +-0.2 | Z_pcb_top + [1.65] (half the receptacle height; **receptacle not chosen**) |
| az_usb | Window azimuth | [0] degrees (rear) | | |
| funnel | Entry lead-in on the outside of the window | [0.8] mm chamfer | | helps misaligned plugs; may allow a smaller window later |
| btn | Button hole | [7.0] mm diameter, centre height Z_pcb_top + [1.0] mm | +-0.3 | switch actuator position **not chosen**; finger access; a printed plunger of [5.0] mm in a [5.4] mm bore is the alternative |
| az_btn | Button azimuth | [240] degrees | | |
| label | Label recess | [21.0] x [21.0] mm, depth [0.3] mm, on a flat facet [23.0] mm wide | +-0.2 | MECH-006 at least 20 x 20 mm; label thickness not known (assumption: thin adhesive label) |
| plane | Facet plane distance from axis | [24.98] mm | | sqrt(27.5^2 - 11.5^2) |
| az_label | Label azimuth and height | [120] degrees, Z [2.0] to [23.0] mm | | on the base, below the joint (Z 25) |
| keep-out | Antenna keep-out | see 4.6 | | |
| feet | Feet | [4] pads, [1.0] mm tall, optional | | for a desk; not required |

Dimension chain check (script `mech_analysis.py` used the same numbers): the label facet leaves 1.38 mm (0.80 mm worst case) between the plane wall and the PCB edge; the radial gap elsewhere is 3.90 mm (3.38 mm worst case); the LED-to-diffuser distance is 8.0 mm with a worst-case range of 7.14 to 8.86 mm.

### 4.4 Why 55 mm and not 53 mm
SYS-028 has [53] mm and MECH-001 allows 48 to 58 mm. A circle of 53 mm with a 1.6 mm wall has a 49.8 mm inner diameter. The label facet (23 mm wide) cuts 2.5 mm off a 55 mm circle and 3.0 mm off a 53 mm circle, and the PCB (D 44) then has less than 1 mm to the wall at the facet. 55 mm keeps 1.38 mm. If the owner wants 53 mm, the PCB shrinks to D 42 (the LED ring D 38 has no margin), or the label moves to the bottom (O1). ADR-0003 mentions a PCB of 46 to 48 mm; that does not fit with the label facet and should be corrected to 44 mm there if this plan is approved (ADR-0003 is Proposed, so the owner can still change it).

### 4.5 USB-C and button (MECH-004)
- Cable limit used: the USB-IF overmold envelope 12.35 x 6.5 mm (read, Compliance Document Rev 2.1b). A project note says 12.85 x 7.0 mm after an update (snippet, not confirmed). The 14.0 x 8.0 mm window also passes 12.85 x 7.0 mm at nominal position (slack 1.15 mm and 1.0 mm), but not at worst-case misalignment.
- The window is larger than the cable because FDM position error adds up (receptacle on the board +-0.1, board in housing +-0.3, window +-0.2). A funnel and tighter PCB location may let the window shrink to about 13.2 x 7.3 after the first prototype shows the real scatter.
- The overmold must be able to reach the receptacle mouth. A known failure is a receptacle that sits behind a small opening so that the plug cannot mate fully (report F7). The window passes the whole overmold through the wall. The distance from the outer wall surface to the board edge is 5.5 mm nominal (wall 1.6 mm plus a radial gap of 3.9 mm); if the receptacle overhangs the board edge, this shrinks. The plug shell is 6.65 mm long (read); the overmold length behind it is **not found** (report F5). Whether the plug reaches full mating depth therefore cannot be derived now. The hardware designer must give the position of the receptacle mouth; the owner checks it on a mock-up with the real cables (three common cables including one with an overmolded plug and one with a thick strain relief).
- The button is reached from the side through a hole. The press force, travel and the switch height are hardware choices (HW) not yet made.
- Programming: the USB-C port carries USB-Serial-JTAG (ADR-0009 context). Test points on the underside need the lid off and the board lifted (the board sits on posts, no screws), which is acceptable for the production test fixture; HW-006 decides the points.

### 4.6 Antenna keep-out (MECH-003)
Facts (analysis report and ADR-0011 evidence):
- ESP32-C3-MINI-1 is 13.2 x 16.6 x 2.4 mm. The antenna area on the land pattern is the end strip of about 13.2 x 5.4 mm (read from datasheet v2.2 figures 10-1 and 11-1; the exact keep-out rectangle is in the Espressif figure 21 of the hardware design guidelines, an image: **not found as text**).
- The Espressif hardware design guidelines (release master, 3 Nov 2026) say: place the on-board antenna outside the base board where possible; if not possible, cut the board away on both sides and below the antenna; **do not place the module in the centre of the board with clearance on all four sides**; and, for the housing, **"a clearance of at least 15 mm is recommended in all directions"** around the antenna, with a throughput and range test of the final product.
- ADR-0003 (Proposed) puts the module in the ring centre first (option A). The 15 mm figure cannot be met literally: the LED ring edge is at R 19 and the housing wall at R 27.5.

Mechanical rules proposed (the plastic wall and lid are unavoidable and are not conductive):
1. Inside a box of antenna area plus [15] mm in all directions, the housing has no metal, no magnet, no screw, no metal insert, no conductive or carbon filament, no metallic or "silk metallic" filament, no metallised or conductive paint, no cable. Plastic only, and the lid and base use ordinary non-conductive filament.
2. The snap-fit version has no fasteners at all. The three snap hooks are plastic. If the screw fallback is used, screws are nylon or sit more than [15] mm from the antenna area; steel screws at R 25 are 20 mm or more from a centre module.
3. The USB-C receptacle shell is metal. Its distance to the antenna is a layout question (HW-005).
4. The antenna end of the module points away from the USB-C connector (ADR-0003) and toward the window-free side of the housing.
5. Whether the 15 mm figure applies to plastic as well as to metal is unclear in the text. The range test of SYS-038 (TC-038, TC-303) with the finished housing decides. This is the most uncertain item of the plan (RISK-011).

### 4.7 Thermal and material (MECH-005)
Analysis (report 4.2, rough estimate, one isothermal surface, bottom excluded, h_conv 10 / 5 / 3 W/m2K, emissivity 0.9):
- Surface rise at 2.5 W: 21.6 / 30.7 / 36.5 K. At 4.7 W: 39 / 54 / 63 K. At 6.75 W: 55 / 73 / 84 K.
- Allowed power for a 15 K margin to HDT, room 35 deg C: PLA 0.3 to 1.2 W, PETG 1.3 to 3.4 W, ASA 4.1 to 6.8 W.
- Consequence: PLA is out; PETG may fail at the full 500 mA dissipation in a hot room; ASA passes the realistic worst case. The lid is PETG in the recommended process and runs near the LEDs: its HDT (65 to 78 deg C by brand) is the weak point. Check with TC-305 and consider an ASA-like translucent grade or a resin lid if it fails (not researched).
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
| Orientation | Base: floor on the bed, posts and hooks vertical. Lid: plate on the bed, skirt up; no supports. The label facet is vertical | engineering practice |
| Overhangs and supports | No overhang above 45 degrees without a plan; the USB window top is a bridge of 14 mm: round or chamfer the top of the window or accept a bridge | engineering practice, not sourced |
| Snap hooks | Orient the arm so that the layer lines run along its length (an arm that bends across layer lines breaks easily). Fillet the root. Strain limit for PETG and ASA: **not found**. Prove [100] cycles on a coupon (MECH-006) | search summary says fillet the arm root (snippet) |
| Screw bosses (fallback) | Thread-forming M2.5 into the plastic or heat-set inserts; wall around an insert at least 2.0 mm beyond its diameter (Stratasys); gussets on tall bosses | Stratasys (read) |
| Large flat lid | A 55 mm flat plate warps in PETG and ASA; use brim, a draft-free enclosed printer for ASA, and check flatness (0.3 mm?) | engineering practice, not sourced |
| Translucent lid | Use natural or white filament; 3 or more top layers; infill pattern shows through; test 0.8 / 1.2 / 1.6 mm plates over an LED ring; layer height 0.2 mm gave the best transmittance of 0.1 to 0.3 mm in one PETG study | studies in search results (snippet) |
| Marking | Part number, revision and material code (ISO 11469 style) moulded or printed on the underside of the base (DFx 4) | DFx standard |
| General tolerance | ISO 2768-m as the default on the drawing for features not listed; all critical features in 4.3 carry a stated tolerance | DFx standard 1 |

### 4.9 Assembly, serviceability, test access
- Assembly from one direction: PCB onto posts and under the hooks, lid pushed on until the hooks click. No tools, no fasteners. Poka-yoke: one PCB notch and one peg make the PCB fit one way.
- Service: the lid comes off with a fingernail or coin in a [2.0] mm pry slot at azimuth 120, between two hooks. Open and close [100] times (MECH-006 acceptance) is proven on a coupon first.
- No permanent bonding. The lid cannot be removed from the label side: the label is on the base.
- Test access: USB-C port for programming; underside test points need the board lifted; no extra access features.

### 4.10 NFR and regulatory check (guidance, not legal advice)
- Safety: low-voltage (5 V) device; the heat estimate shows the surface temperature rise of 22 to 37 K at 2.5 W, meaning a surface up to 60 deg C in a 25 deg C room at the pessimistic convection value. Touch temperature limits for accessible plastic surfaces (EN 62368-1) are **not found** (verify). Flammability class of the enclosure material and the power-source class: not looked up (verify). Filament RoHS/REACH declarations: ask the maker (O2).
- Labelling: the label area (MECH-006) carries identifier, passphrase, QR code and the "prototype, not for sale" mark; CE and WEEE marks are not needed for a prototype that is not placed on the market (see `docs/regulatory/`); check again with skill `regulatory-check` before any sale. Label durability and legibility test: MECH-006 acceptance.
- Reliability: snap hooks creep in warm PETG; a screw fallback exists.
- Sustainability: reopenable, no glue; plastics marked.
- Security: the passphrase label is on the base; opening the lid does not expose it more; physical access to the USB-C port exists by design (ADR-0007 covers firmware).
- Manufacturability: two parts, one translucent; prints on a desktop FDM printer; no supports expected.

## 5. Detailed implementation plan
Nothing here is done by the elephant. After the owner approves the MECH requirements and this plan, the owner makes the CAD model. Files that **would** be created or changed later:

- **Files to create (owner, FreeCAD):** `mech/freecad/busy-light-housing.FCStd` (parametric model: spreadsheet `Params` with the names of 4.3, bodies `Base` and `Lid`, assembly with the STEP of the PCB), later `mech/exports/<rev>/base.step`, `lid.step`, `base.stl`, `lid.stl`, `mech/drawings/` (2D drawings with tolerances, material, revision).
- **Files to create (analysis, after approval):** `mech/analysis/light_uniformity.py`, `thermal_estimate.py`, `tolerance_stack.py` (the scripts of the report, parameterised by the FreeCAD spreadsheet values), `mech/analysis/README` of results, `docs/verification/reports/` for evidence.
- **Documents to change (after owner approval):** `docs/requirements/mech.md` (see section 7 proposals), `docs/decisions/ADR-0003-antenna-and-board-topology.md` (PCB size 44 mm, antenna keep-out distance), `docs/verification/test-cases-hw-mech.md` (procedures, only when requirements are Approved), `docs/risk/risk-register.md` (new risks of section 7), `CHANGELOG.md`.
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
| 1 | Base | Outer cylinder | D_out, H_base | floor on Z = 0 |
| 2 | Base | Cavity | t_wall, t_floor | inner D = D_out - 2 t_wall = 51.8 |
| 3 | Base | Label facet | plane, label width 23, Z 2 to 23, az_label | flat cut on the outside; wall behind it stays t_wall (cavity follows the flat) |
| 4 | Base | Label recess | label 21 x 21, depth 0.3 | on the facet |
| 5 | Base | Posts | N_post, radius 21.0, H_post, pad 4.0 x 1.0 | tops at Z_pcb_bot |
| 6 | Base | PCB pegs and notch peg | g_peg, notch R1.5 | needs the KiCad outline (5.4) |
| 7 | Base | PCB hooks | hook | on the posts, overlap 0.6 |
| 8 | Base | USB window | window, Z_usb, az_usb, funnel | rectangular, corner R1.0, through the wall; check the cable path to the receptacle mouth |
| 9 | Base | Button hole | btn, az_btn | Z from the switch actuator in KiCad |
| 10 | Base | Spigot | spigot, from Z 25.0 to 26.8 | inner part of the wall |
| 11 | Base | Hook grooves | lid hooks, az 60 / 180 / 300 | on the spigot outer face |
| 12 | Base | Marking | part number, revision | underside |
| 13 | Lid | Plate | D_out, t_diff, Z_lid_in | flat, no features on the light path |
| 14 | Lid | Skirt | skirt 0.9, spigot clearance 0.35, height 1.8 | |
| 15 | Lid | Snap hooks | lid hooks | arms along the skirt |
| 16 | Lid | Notch for the USB window | window | the window top is at Z 23.8, below the joint at 25.0, so the lid needs no notch; check this when the receptacle is chosen |
| 17 | Lid | Pry slot | 2 mm slot at azimuth 120 | between the hooks at 60 and 180 |
| 18 | Assembly | PCB | STEP from KiCad | interference check 5.2 |
| 19 | Both | Coupon variants | d_led 4 / 6 / 8, t_diff 0.8 / 1.2 / 1.6 | variants of the same model |

Check before saving: all numbers come from `Params`; no magic numbers in sketches; name bodies as in the table.

### 5.4 What needs the PCB outline from KiCad (ask the owner; hardware design has not started)
The following are open until the hardware design gives them. The plan uses the working values of 4.3 and 2 (A3, A5):
1. Board outline: diameter, any flats or notches, thickness (D 44, 1.6 mm assumed).
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
| TC-301 | MECH-001 size | Prototype | CAD dimension check (D 55, H 28) | caliper on [3] housings | MECH-001 should say if the cable is excluded |
| TC-302 | MECH-002 diffuser | Prototype | `light_uniformity.py` (report 4.1), coupon plan | photo at 1 m under office light; intensity at 0.5 m through the lid (SYS-001, TC-001 gear) | the number for "no point source" needs a definition (working: ripple at most 10 %) |
| TC-303 | MECH-003 antenna | Inspection | drawing shows the keep-out of 4.6; range test of SYS-038 / TC-038 with the finished housing | range test, 6 dB rule of SYS-038 | depends on ADR-0003 and spike 7.2 |
| TC-304 | MECH-004 access | Prototype | tolerance stack (report 4.3) | [3] common cables incl. one overmolded plug and one with a thick boot; finger on button | name the cables |
| TC-305 | MECH-005 thermal | Prototype | `thermal_estimate.py` (report 4.2) | thermocouples at the LED ring, module, lid, wall; full limited power, closed housing, [25] deg C, stable to 1 K per 10 min | later FEA only if the measurement shows hot spots that the lumped model cannot explain |
| TC-306 | MECH-006 label | Inspection | drawing; stack 2 | label 21 x 21 applied, [100] open-close cycles on the lid, readability check | label sits on the base |

Other checks: first-article dimension check of the critical features of 4.3 (calipers or pin gauges) and a tolerance coupon per printer/material change; DFx review with `design-review` before approval; interference check with the KiCad STEP per revision.
Later FEA only if justified: the snap hooks (if a coupon fails before 100 cycles) or a thermal-structural case if TC-305 shows the lid deforming. A thermal FEA is not justified now: the inputs (h, the heat path of the module) are less certain than the model error.

What was not run: any measurement, any CAD or interference check, any RF analysis, any printing, any resin or material search beyond the report. The analysis in the report is a lumped estimate and a script.

## 7. Risks and open questions
Risks (proposed; not added to the risk register; RISK-005 and RISK-011 already exist):

| Id | Risk | Effect | Mitigation |
|----|------|--------|------------|
| R1 | The single lid does not diffuse enough; points show | MECH-002 fails | coupon test first; fallback concept A; resin lid |
| R2 | PETG lid or base softens at full limited power in a hot room (RISK-005) | deformation, LED shift | ASA base; measure TC-305; thermal input to SYS-020 |
| R3 | Antenna detuned; the 15 mm vendor clearance cannot be met (RISK-011) | range below SYS-038 | no metal in the box; range test; ADR-0003 fallback (u.FL) |
| R4 | Snap hooks fail or loosen before [100] cycles | MECH-006 acceptance | coupon test; screw fallback |
| R5 | The USB-C window is too small for a real cable, or the overmold cannot reach the receptacle | MECH-004 fails | window 14.0 x 8.0; mock-up with real cables; receptacle position from hardware |
| R6 | Label facet leaves 0.8 mm (worst case) to the PCB | board touches the wall | peg location; PCB D 44 |
| R7 | Owner's printer or material differs from A2 | tolerances and HDT change | questions O2; recalculate with the script |
| R8 | The PCB outline from hardware differs from 4.3 | redo of the stack | work in the parameter sheet |
| R9 | Warping of the large lid | gap at the joint, light leaks | brim, enclosed printer, flatness check |
| R10 | Overmold envelope larger than 12.35 x 6.5 mm (one note says 12.85 x 7.0) | some cables do not fit | test with cables; window margin |
| R11 | Enclosure fire and touch-temperature rules apply (EN 62368-1, verify) | redesign of material | regulatory check before approval |

Open questions for the owner:
- **O1 Orientation.** Does the unit lie on a desk with the ring up, stand on its edge facing you, or hang on a wall? The label rule (not hidden when standing) and the ring surface depend on it. A wall hang or a stand changes the foot, the label position and the height. If it lies flat and the label may be on the bottom, the height drops from 28 to about 18 mm.
- **O2 Printer and material.** FDM or resin? Which filaments (PETG, ASA, PLA)? Enclosed printer? Datasheet and flammability class of each filament? Natural or white translucent filament for the lid?
- **O3 Ring look.** A wide band or disc glow, or a thin sharp ring?
- **O4 Size.** Is 55 mm acceptable (SYS-028 says [53] +-5)? Is height 28 mm acceptable?
- **O5 Highest room temperature** for MECH-005 (working value 35 deg C) and the accessible surface temperature you accept.
- **O6 Cable list.** Which three cables are the "common" cables (MECH-004)? Does the unit need to work with a right-angle plug or a thick boot?
- **O7 PCB fixing.** Snap hooks on the board edge (no holes), or screws through the board (metal in the keep-out)?
- **O8 Button.** Which button type and which side? Does it need a printed cap?
- **O9 Antenna.** Do you accept that the housing proposes no metal in the 15 mm box and relies on spike 7.2 for the range? Is ADR-0003 B (u.FL) still the fallback?
- **O10 Label.** Which label material and thickness? Is the label printed or hand-written?
- **O11 Feet or magnets.** Rubber feet (not in the antenna box)? Magnets are not allowed near the antenna.
- **O12 Process split.** May the base and the lid be different materials (base ASA, lid PETG)?
- **O13 Proposals to MECH requirements** (not changed by me): MECH-001 says whether the cable counts; MECH-002 gets a number (working: ripple at most 10 % along the ring); MECH-003 names the distance (the vendor's 15 mm box); MECH-004 names the overmold envelope (12.35 x 6.5 mm); MECH-005 names the room temperature; MECH-006 names the orientation.

## 8. Rollout / rollback and traceability
IDs created: none new. This plan, ADR-0011 (Proposed) and the report `mech-concept-analysis.md` (Draft) are new documents. Proposed text for new risks is in section 7 and ADR-0011; not added to the register.
Reverted if it fails: delete the three documents; nothing else depends on them. No `mech/`, `hw/` or `sw/` file is changed.
Traceability: MECH-001..006, SYS-001, SYS-013, SYS-017, SYS-020, SYS-028, SYS-038, HW-001, HW-005, HW-006, HW-010, ADR-0003, ADR-0009, ADR-0011, RISK-005, RISK-011, TC-301..TC-306, TC-038. Run `python3 -I scripts/check_traceability.py` after changes to `docs/`.
Next step: owner reviews, then the EGM goldfish passes (comprehension, antagonistic, readiness) run on this document, outcome recorded as `RV-nnn` in `docs/reviews/`.
