# ADR-0011: Housing concept and manufacturing process

- **Status:** Proposed (only the owner sets Accepted)
- **Date:** 2026-11-04 (revised the same day: dimensions, label position and height resolved by author decisions that the owner must confirm; see Decision and the analysis report section 8)
- **Deciders / reviewers:** Ben Spoor (owner); goldfish review RV-004 (2026-11-04): not ready for approval, actions open
- **Related:** NEED-014, SYS-001, SYS-013, SYS-017, SYS-020, SYS-028, SYS-038, MECH-001, MECH-002, MECH-003, MECH-004, MECH-005, MECH-006, HW-001, HW-005, ADR-0003, ADR-0009, RISK-005, RISK-011; plan `docs/plans/05-mechanical-design.md`; analysis `docs/verification/reports/mech-concept-analysis.md`

## Context and problem
The device is a 16-LED status ring on one PCB with an ESP32-C3 module, a USB-C connector and one button. The housing is 3D printed (NEED-014, SYS-028: about 53 mm, 48 to 58 mm). It must diffuse the 16 LEDs into a closed band (MECH-002), keep metal away from the antenna (MECH-003), give access to the USB-C connector with common cables and to the button (MECH-004), stay below its heat deflection temperature minus [15] K (MECH-005) and give a fixed label area of 20 x 20 mm on a part that does not move when the housing opens (MECH-006).
The choice of concept and of printing process is costly to reverse: the PCB outline, the connector positions and the LED height depend on it (DFx standard section 1: "select the manufacturing process per ADR before detailed design").
All MECH requirements are Draft. This ADR does not authorise CAD work; the owner approves the requirements first.

Not known: the owner's printer and filaments (FDM or resin, which materials); the orientation of the device (assumed to lie flat, ring up: the owner confirms); the beam angle of the chosen LEDs (not found for the shortlisted parts); the light transmission of the diffuser material; the receptacle and button parts; the PCB outline. Each of these can change the result and is an open question in the plan.

## Evidence
Status: **read** = I read the text of the document; **snippet** = seen only in a search result; **not found**; **assumption**. Full list with sources in the analysis report, sections 2.1 to 2.3.

| ID | Fact | Value | Source | Status |
|----|------|-------|--------|--------|
| E1 | Type-C plug overmold envelope (USB-IF) | 12.35 x 6.5 mm max | USB-IF Type-C Compliance Document Rev 2.1b, Table B-1 | read |
| E2 | HDT 0.45 MPa: PLA 55 to 60, PETG 69 to 78, ASA 103 (Polymaker); other brands: ASA 92 to 102, PETG 65 to 73 | deg C | https://wiki.polymaker.com/polymaker-products/polymaker-filaments/technical-data-at-a-glance (read); others snippet | read / snippet |
| E3 | ESP32-C3 hardware design guidelines: "A clearance of at least 15 mm is recommended in all directions" for the PCB antenna inside the housing; the module "should not be placed in the center of the board with clearance created by hollowing out on all four sides"; the antenna is best outside the base board; the final product shall be tested for range | | https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/esp-hardware-design-guidelines-en-master-esp32c3.pdf (release master, Nov 03, 2026), section 1.4.7 and figure 21 | read (the figure dimensions are an image: not found) |
| E4 | ESP32-C3-MINI-1: 13.2 x 16.6 x 2.4 mm; antenna area of the land pattern 13.2 x about 5.4 mm at one end | | ESP32-C3-MINI-1 datasheet v2.2, figures 10-1 and 11-1 | read (5.4 mm read from the drawing: 16.6 - 11.2) |
| E5 | LED half-intensity angle 120 deg full (XL-2020 part); WS2812C-2020, SK6812MINI-E and SK6812MINI (3535): no number | | datasheets (see report) | read / not found |
| E6 | FDM design guide: minimum wall 4 x layer height; clearance follows layer height; holes undersized; heat-set insert wall 2 mm beyond the insert | | Stratasys Direct FDM Design Guide | read |
| E7 | Thermal estimate: PLA fails MECH-005 at 2.5 W; PETG fails 2.5 W in a 35 deg C room (D 53 x H 16.5; first draft D 55 x H 28: marginal); ASA passes 2.5 W but not 4.7 W (first draft: passed up to about 4 W) | | analysis report sections 4.2 and 8.2 | analysis (rough) |
| E8 | Tolerance stack: USB-C window needs [14.0] x [8.0] mm at worst case; lid spigot clearance at least 0.35 mm per side; radial gap PCB D 46 to wall 1.90 mm nominal, 1.38 mm worst case | | analysis report sections 4.3 and 8.2 | analysis (rough) |
| E9 | Resin printing: accuracy, HDT of translucent resins, post-cure safety | | not searched | not found |
| E10 | The owner's printer and materials | | | not found |

## Decision criteria
Criteria 1 and 4 of the concept table are gates: an option that scores 0 cannot meet MECH-002 or MECH-001/MECH-006 and is excluded whatever its sum. In the process table, a score of 0 on diffuser quality or at most 1 on thermal margin is a gate.

Concept table:

| # | Criterion | Weight (1-5) | Source requirement |
|---|-----------|--------------|--------------------|
| 1 | Diffusion: closed band, no point source | 5 | MECH-002, SYS-001 |
| 2 | Antenna friendliness: no metal, few parts near the antenna | 5 | MECH-003, SYS-038, RISK-011 |
| 3 | Thermal and material margin | 4 | MECH-005, RISK-005 |
| 4 | Size and fixed label area | 4 | MECH-001, MECH-006, SYS-028 |
| 5 | USB-C and button access | 4 | MECH-004, SYS-017 |
| 6 | Assembly without tools or with common screws; reopening 100 times | 4 | DFx standard 2 and 4, MECH-006 |
| 7 | Printability and tolerance sensitivity | 4 | DFx standard 1 |
| 8 | Test and programming access | 3 | DFx standard 3, HW-006 |
| 9 | Part count and print cost | 2 | SYS-021 (indirect; housing cost is not in SYS-021) |

Process table:

| # | Criterion | Weight (1-5) | Source requirement |
|---|-----------|--------------|--------------------|
| 1 | Dimensional accuracy for fits | 4 | MECH-004, DFx standard 1 |
| 2 | Thermal margin of the material | 5 | MECH-005 |
| 3 | Diffuser quality possible | 4 | MECH-002 |
| 4 | Availability at the owner and lead time | 4 | NEED-014; unknown |
| 5 | Strength of snaps and screw bosses, reopening | 3 | DFx standard 4 |
| 6 | Non-conductive material, no metal fill | 5 | MECH-003 |
| 7 | Handling safety and post-processing | 3 | DFx standard 5a |
| 8 | Cost per housing, prototype of 10 | 3 | project |

## Alternatives considered

### A. Clamshell with a separate diffuser ring
Three printed parts: opaque base, opaque top cap with a ring-shaped window, translucent diffuser ring that sits in the window. Screws or snaps join them.
Pros: the diffuser is a thin, flat, separately tuned part (thickness, material, even a different process) and can be swapped without a new base; a sharp ring look is possible because the cap masks the centre; the best diffusion of the three.
Cons: three parts and two joints, so more tolerance stack (light leaks at the joints, a gap between ring and cap); more assembly steps; more risk of a visible seam; more screws or snaps near the PCB.
Cost: three prints and fasteners.

### B. Opaque base with one translucent lid
Two printed parts. The base (opaque ASA or PETG) holds the PCB on posts and carries the label facet, USB-C window and button. The lid (natural or white translucent PETG) is a flat cap that closes the base and is the diffuser. The lid is retained by [3] snap hooks, with [3] M2.5 thread-forming screws as the fallback. The light passes through the whole lid, so the lit area is a wide band or a disc. An opaque centre insert is an option for a sharper ring.
Pros: fewest parts and joints; the lid prints flat on the bed (best surface); no metal near the antenna in the snap version; label on the base, which does not move when the lid opens (MECH-006); the lid is the only translucent part, so its material is the only optical variable.
Cons: the diffuser quality depends on one filament and on the infill and top-layer pattern, which are visible in the glow; the lid and the base in different materials and colours means two print jobs; the lid material is the hottest-running translucent part (natural PETG HDT 65 to 78 deg C, E2); the ring look needs distance (8 mm LED to diffuser), which makes the housing 16.5 mm tall.
Cost: two prints.

### C. Sphere with two snap-fit halves
A ball of 53 mm: opaque lower half, translucent upper half, snap ring between them.
Pros: matches the "ball" idea of NEED-014 and looks good; a dome spreads light well.
Cons: spherical surfaces need supports and show layer steps; a flat 20 x 20 mm label needs a flat cut into the sphere (the sag over 20 mm on a 53 mm sphere is 1.9 mm; on the underside this is easier than on a side facet); the USB-C window and the button sit on curved walls; thin shells creep at snap hooks; PCB fixing in a sphere is harder; thermal estimate unfavourable with the thin shell. Highest print risk.
Cost: two prints with supports.

### D. Do nothing: no housing, bare PCB with a printed diffuser disc only
The board is used as it is, with the ring uncovered or a loose disc on top.
Pros: no design effort; no antenna loading.
Cons: fails MECH-001 (no housing), MECH-006 (the label on a bare board does not meet the labelling rules), MECH-004 (no strain relief, no button guard), MECH-005 is moot but the board has exposed 5 V parts. Needed as the baseline only.

### Process alternatives (the second decision)
- **P1 FDM, PETG base and natural PETG lid.** Easy to print, tough, translucent grades exist; HDT 65 to 78 deg C is marginal in a hot room at 2.5 W (E7).
- **P2 FDM, ASA base and natural PETG lid.** The base has the HDT margin (103 deg C); the lid is still PETG; ASA needs an enclosed printer and ventilation (fumes; not researched).
- **P3 Resin (MSLA), opaque base and clear or white lid.** Best accuracy and surface; HDT of resins and post-cure handling not researched (E9); snaps are brittle; no owner printer known.
- **P4 FDM, PLA.** Cheapest and most common; fails the thermal margin (E7).
- **P5 Do nothing:** no printed housing; the same as D.

## Comparison
Scores 0 to 5, my judgement from the evidence above, not measured. The weighted sums were computed with Python (`adr_scores.py`, report section 7; re-run as `adr_scores_v2.py`, report section 8.5). **Re-scored 2026-11-04:** criterion 4 for A (3 to 4) and C (2 to 3) because the label moved to the underside; thermal score of P1 (3 to 2) because the smaller shell is hotter. The tables below show the new scores; the first draft values were A 129, C 113, B-A 18, P1 119, P2-P1 minus 8.

Concept table (weights 5, 5, 4, 4, 4, 4, 4, 3, 2; sum 35; maximum 175):

| Criterion (weight) | A clamshell + ring | B base + lid | C sphere | D do nothing |
|--------------------|--------------------|--------------|----------|--------------|
| 1 Diffusion (5) | 5 | 4 | 3 | 0 |
| 2 Antenna (5) | 4 | 5 | 5 | 5 |
| 3 Thermal (4) | 4 | 3 | 3 | 5 |
| 4 Size and label (4) | 4 | 5 | 3 | 0 |
| 5 Access (4) | 4 | 4 | 3 | 3 |
| 6 Assembly (4) | 3 | 4 | 4 | 5 |
| 7 Printability (4) | 3 | 4 | 2 | 5 |
| 8 Test access (3) | 4 | 4 | 3 | 5 |
| 9 Parts and cost (2) | 2 | 5 | 4 | 5 |
| **Weighted sum (max 175)** | 133 | 147 | 117 | 122 (excluded by gates 1 and 4) |

Sensitivity (Python): B leads A by 14 points. No single weight change of +-1 and no single score lowered by 1 on B makes A reach B. The difference is larger than the scoring error that I would claim for single scores, but B scores 4 on diffusion on my judgement only: the filament transmission and the LED beam angle are not found (E5). If B cannot reach the diffusion criterion on the prototype, A is the fallback; the PCB and the base are the same, only the lid changes.

Process table (weights 4, 5, 4, 4, 3, 5, 3, 3; sum 31; maximum 155):

| Criterion (weight) | P1 FDM PETG | P2 FDM ASA + PETG lid | P3 resin | P4 FDM PLA | P5 nothing |
|--------------------|-------------|-----------------------|----------|-----------|------------|
| 1 Accuracy (4) | 3 | 3 | 5 | 3 | 0 |
| 2 Thermal (5) | 2 | 4 | 2 | 1 | 5 |
| 3 Diffuser (4) | 3 | 3 | 4 | 3 | 0 |
| 4 Availability (4) | 4 | 3 | 3 | 5 | 5 |
| 5 Strength (3) | 3 | 3 | 2 | 3 | 0 |
| 6 Non-conductive (5) | 5 | 5 | 5 | 5 | 5 |
| 7 Handling (3) | 5 | 3 | 2 | 5 | 5 |
| 8 Cost (3) | 5 | 4 | 3 | 5 | 5 |
| **Weighted sum (max 155)** | 114 | 111 | 104 | 113 (excluded by thermal gate) | 100 (excluded by diffuser gate) |

Reading: P1 leads P2 by 3 points. That is inside my scoring error. The table does not decide between P1 and P2. The thermal estimate does: PETG fails 2.5 W in a hot room and ASA passes it (E7), so ASA for the base is the stronger recommendation than in the first draft. Criterion 4 (availability) is a guess because the owner's printer is not known (E10).

## Decision
Recommendation, not a decision. The owner decides; three points are **OPEN** and one is an assumption for the owner to confirm.

1. **Recommend concept B** (opaque base, one translucent lid, label in a recess of the underside of the base, snap-fit lid with a screw fallback), at [53.0] mm diameter and [16.5] mm height (17.45 mm with feet). PCB [46.0] mm, wall 1.6, floor 2.0, LED to diffuser 8.0, lid plate 1.2, window 14.0 x 8.0 mm. The dimensions are working values in plan 05 section 4.3. The first draft was 55 x 28 mm with a side label facet.
2. **Recommend FDM.** Base in **ASA** if the printer can print it, otherwise PETG with a measured thermal test before any claim (TC-305). Lid in natural or white translucent PETG; PLA is excluded by the thermal estimate. Resin stays a fallback for the lid if the FDM lid fails the diffusion test (TC-302).
3. **Recommend a coupon and mock-up step before the first housing**: a stack of lid coupons at 0.8, 1.2 and 1.6 mm over a ring of LEDs at 4, 6 and 8 mm; a tolerance coupon for window, spigot and posts. These need a mock-up of 16 LEDs; they are hardware work and wait for approved requirements.
4. **Assumption, owner confirms: orientation.** The unit lies flat on a desk with the ring up (plan 05 A1). The label is on the underside of the base, readable when the unit is lifted; MECH-006 is reworded (Draft). This removed the side facet and 11.5 mm of height. A stand, a wall mount or a hanging unit is excluded; if the owner needs one of them, the label position and the height are reopened.
5. **OPEN, owner: printer and materials** (FDM or resin, filaments, enclosed or not).
6. **OPEN, owner: ring look.** A wide glow or disc (simple, uniform) or a sharp ring (needs the centre masked and a smaller LED-to-diffuser distance, so more visible LED hotspots, or concept A).
7. **OPEN, owner: PCB mounting.** Snap hooks on the board edge (no holes) or screws through the board (metal near the antenna zone).

## Consequences
- Positive: two printed parts, one translucent; the label stays on a fixed part; no metal near the antenna in the snap version; a clear fallback to A for diffusion and to a different material for heat; the choice of material is made from data.
- **Negative / trade-offs accepted:** the housing is 16.5 mm tall, mainly because of the diffusion distance; the label cannot be read while the unit is in use and the unit must lie flat (assumption A1); the shell is smaller, so it runs hotter (PETG fails 2.5 W in a hot room, ASA is needed); the USB-C window is large ([14.0] x [8.0] mm) because of FDM position tolerance; the glow is a band or a disc, not a thin ring; one translucent PETG lid has a lower HDT than the base; the diffusion criterion for B rests on an unmeasured filament.
- New risks (proposed text for the risk register, not added there): **a)** The lid does not diffuse enough and LED points show (MECH-002). **b)** The housing softens at full limited power in a hot room (RISK-005 changes: PETG at 2.5 W marginal; at 1350 mA the limiter alone allows 6.75 W, more than the housing can shed). **c)** Snap hooks fail or loosen within 100 openings. **d)** The vendor figure of 15 mm antenna clearance cannot be met in a 53 mm housing: 14.3 mm from the antenna corners to the inner wall, lid, floor and label inside the 15 mm box (RISK-011). **e)** The radial gap between the PCB (D 46) and the wall is 1.38 mm in the worst case, so the board centring matters. **f)** The joint zone is 1.25 mm high, which is tight for snap hooks.
- Requirements created or changed (proposals, not done): MECH-005 needs a value for the highest room temperature; MECH-001 should say whether the cable and plug are excluded; MECH-006 reworded for the underside label (done in the Draft requirement); MECH-003 limited to what the housing controls (done); the antenna finding for the PCB layout is in ADR-0003; MECH-004 acceptance should name the overmold envelope (12.35 x 6.5 mm, USB-IF) as the "common cable" limit; a hardware requirement for the PCB outline and notches (HW-009 or new). SYS-020 and RISK-005: housing thermal limit as an input to the limit at 1350 mA.

## Verification and revisit
- Analysis: `mech/analysis/` tolerance stack and thermal script, once the owner has a CAD model and the PCB outline from KiCad (not created: the requirements are Draft).
- Prototype tests: TC-301 (size), TC-302 (diffuser, photo at 1 m, intensity at 0.5 m), TC-303 (antenna clearance, range test with the finished housing), TC-304 (three common cables including an overmolded plug), TC-305 (temperature at full limited power in a closed housing), TC-306 (label, 100 cycles).
- Revisit when: the lid fails TC-302; the measured temperature margin is below [15] K; the range test fails with the housing (RISK-011); the owner changes orientation or printer; the LED type changes (beam angle, height); a snap hook breaks before 100 cycles; the USB-IF overmold envelope changes (F3 in the report: 12.85 x 7.0 mm unconfirmed).

## Critical review notes
Strongest objection: "B wins because the criteria reward simplicity (parts, cost, assembly, label). Diffusion, the most visible quality and a weight-5 criterion, is exactly what B scores lower on than A, and the score of 4 is a guess because neither the LED beam angle nor the filament transmission is known."
Answer: correct. The lead of 14 points (after the re-score) holds under single weight and score changes, but the diffusion score of B could be 2 and the table would then be close (B 137, A 133 with that one change, computed by hand). The decision therefore rests on the cheap coupon test of step 3, not on the table. A reuses the same base and PCB, so falling back costs one new part.
Second objection: "The 15 mm clearance of the antenna guideline cannot be met in a 53 mm housing with the module in the middle of an LED ring, and the guideline also warns against a module in the middle of the board." Answer: yes. The LED, track and ground part is an ADR-0003 problem (finding of 2026-11-04), not a housing problem. The housing contributes: plastic only within the 15 mm box (no metal, magnet, conductive filament or metallised label) and the nearest wall 16.6 mm from the antenna end edge (14.3 mm from the corners, 0.7 mm short); a plastic wall is unavoidable. The range test (TC-303, TC-038) decides. If ADR-0003 moves to the u.FL variant (B in ADR-0003), the antenna sits on the wall, and the base gets an antenna mount; this changes the plan, not the concept.
Third objection: "The thermal estimate is one lumped surface with assumed h and no inner air." Answer: yes, it is a rough upper bound on the allowed power. It fixes the order of materials (PLA out, PETG marginal, ASA safe), not a value. TC-305 gives the evidence.
Fourth objection: "The owner's printer is unknown; ASA may not be printable." Answer: yes. The recommendation names PETG as the fallback with the same geometry, and the thermal test decides.

Fifth objection (2026-11-04): "Moving the label to the underside makes the passphrase invisible in use and sits inside the antenna box; the decision was driven by an assumption, not by the owner." Answer: yes on both. A1 is an assumption that the owner confirms; if it is wrong the height returns toward 28 mm. The label is plastic or paper and must not be metallised; the floor is 6.6 mm below the antenna plane, so a label outside the box is not possible in this shape.
