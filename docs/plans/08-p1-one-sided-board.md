# 08 -- Prototype board P1: one-sided assembly for JLCPCB Economic PCBA (design doc)

- **Status:** In Review. The owner pre-approved implementation after a GO from the readiness review (answer 16 of 2026-11-17,
  `docs/journal/2026-11-17-p1-order-owner-decisions.md`). The owner confirms or rejects this plan and its result together.
- **Date:** 2026-11-17  **Owner:** Ben Spoor (author: assistant)
- **Area:** hw (with a CI part under `.github/` and `scripts/`)
- **Requirements addressed:** HW-008 (Approved 2026-11-17 with the through-hole amendment), HW-010 (Approved; trims under the
  owner rule of 2026-11-17), HW-016 (Approved 2026-11-17, [10] mm), HW-017 (Approved 2026-11-17), HW-001 (Draft, unchanged
  ring geometry), HW-005 (Draft, antenna keep-out; DEV-004 stays), HW-006 (Draft, test points). ADR-0021 (Accepted 2026-11-17).
  ADR-0020 stays Proposed; this plan uses the owner's 0.15 mm answer, not ADR-0020 option B.
- **EGM review record:** RV-014 (comprehension / antagonistic / readiness)

## 1. Problem definition
The owner wants to order a first prototype board (P1): 5 bare PCBs, 2 of them assembled by JLCPCB with the **Economic**
PCBA service, at most EUR 100 (answers 1, 3, 11). The stored board
`hw/kicad/spike-gate/board/busy_light_spike.kicad_pcb` (ring14 run 9) has 41 footprints on the top side and 60 on the
bottom side (6 of them bare test pads), uses the via-in-pad ground stitching under U9, and was routed with 0.15 mm
tracks. Economic PCBA, as the assistant understands it (not read, see A1), assembles one side only and no through-hole
parts. P1 therefore needs a new placement with every assembled part on the top side.

Goal: a P1 board that (G1) has every assembled part on F.Cu, (G2) passes the strict DRC and ERC gate with only the
tolerated classes, (G3) has no via inside an SMD pad, (G4) carries the HW-017 damping link and the HW-016 spares within
[10] mm, (G5) comes with a reproducible order package (Gerbers, drill, JLCPCB BOM and CPL, assembly drawing, KiKit
panel) built by a script and by CI on `main`.

Out of scope: a product board; changing the three limit steps or the gate behaviour (HW-010); antenna or RF
measurement (spike 7.2, DEV-004 stays Proposed); firmware for the new pin map (pin map is unchanged, so none is needed);
placing the order (the owner does it).

## 2. Constraints and assumptions
Owner answers of 2026-11-17 (journal): one-sided SMD on the top (LED) side, test points as bare pads on the bottom (6);
0.15 mm tracks (3); 4 layers, 1.6 mm, HASL lead-free (10); no via-in-pad (9); designators on the top silkscreen where
they fit, on the bottom silkscreen, and in an assembly drawing PDF (13); own KiKit panel (14); fallback "grow the board
up to the housing limit" if one-sided does not route (7); Freerouting 2.5.0 from Maven Central with both hashes pinned (8);
order files built by CI, not committed (17); undecided reversible points: pick, log, continue (19).

Assumptions (each is challenged in RV-014):
- **A1. Economic PCBA rules are not read.** Assumed: one side, SMD only, the parts from JLCPCB's library, 4-layer boards
  accepted. jlcpcb.com is blocked from this container (proxy 403); the owner declined the network change. The order
  checklist (section 6, step O1) makes the owner read them before ordering. If Economic does not accept 4 layers, the
  owner falls back to Standard PCBA one-sided (more cost, same files).
- **A2. Fab numbers.** The JLCPCB multilayer numbers of ADR-0020 (read 2026-11-08) are used unchanged: track and space
  0.09 mm minimum, via hole 0.15 mm minimum, annular ring 0.15 mm absolute minimum, 0.20 mm recommended. P1 uses the
  existing default profile of `src/pcb_rules.py` (0.15 mm track and clearance; via 0.6 / 0.3 mm, ring 0.15 mm) unchanged.
  The ring is at the absolute minimum; a 0.7 / 0.3 mm via (ring 0.2 mm) is tried once as batch V (section 5, step 7) and
  kept if it routes as well.
- **A3. Area.** Inside the LED ring the top side has about 940 mm2 (r 17.3 mm) less the module (13.2 x 16.6 mm) and its
  antenna strip, less SW1: about 650 mm2 for about 75 parts, plus the tab. The two-sided board needed both sides. Whether
  one side routes at 0.15 mm is not known; section 5 step 6 defines when to grow.
- **A4. Housing limit for growth.** The housing outer diameter is 53.0 mm (`mech_outline.R_OUT`) and MECH-001 limits the
  largest dimension to 58 mm. Growth of D_PCB in steps of 2 mm up to 50 mm keeps the housing at D_OUT <= 57 mm
  (D_OUT = D_PCB + 2 x (wall 1.6 + gap 0.4 + 1.5 ledge), checked by `mech/freecad/housing.py` before use). Above 50 mm the
  work stops and the owner decides (hard to reverse, answer 19).
- **A5. The pin map does not change.** No GPIO is moved; firmware plan 07 stays valid.
- **A6. Trims.** Only two trims are proposed under the owner rule (answer 5); both must pass their recalculation test
  before they reach the schematic (section 4.2). Other part reductions (16 LED bypass capacitors, the six hold-off
  capacitors) are listed for the owner, not done: the first is an LED decision outside HW-010, the second needs a C0G part
  whose stock cannot be checked tonight.
- **A7. CPL rotations.** JLCPCB's placement rotation differs from KiCad's for some footprints. The CPL is written with
  KiCad rotations; the owner checks the rotations in JLCPCB's preview at order time (step O4). No offset table is invented.
- **A8. New part numbers without LCSC numbers.** The 0 ohm link of HW-017 and the 27.7 kohm resistor of trim T1 get a
  manufacturer part number derived from a series code that is already in `src/sourcing.py`; their LCSC numbers stay empty
  and are listed in the order checklist (O2). The fab review reports them as findings, not as passes.

## 3. Alternatives considered
| Option | Idea | For | Against |
|---|---|---|---|
| A (owner choice, answer 1) | Re-place the existing netlist with every assembled part on top, 0.15 mm rules, grow the outline if needed | cheapest assembly (Economic); HW-008 one side; same schematic and tests | may not route on 46 mm; new routing evidence needed; grows the housing if it fails |
| B | Order the stored two-sided board with Standard PCBA | ready now (fab review done) | two-sided assembly cost; violates HW-008 (one side); via-in-pad needs filled vias |
| C | A small gate-only test board first | quick bench of HW-010 | new schematic and layout; no LED, Wi-Fi or housing test |
| Do nothing | Wait | no cost | no bench evidence for HW-010, ADR-0021 or the antenna |

A is the owner's choice. B stays available: the two-sided board stays in `board/` until the owner decides (rollback).

## 4. Technical plan

### 4.1 Schematic changes (`src/layout_full.py`, regenerated with `run_full.sh`)
1. **HW-017 damping link.** New net `VBUS` for the connector side: J1 pins A4, A9, B4, B9, TVS1 pin 1, U6 pin 5.
   New part **R22**, value `0`, footprint `Resistor_SMD:R_1206_3216Metric`, between `VBUS` (pin 1) and `VBUS_IC` (pin 2).
   Everything else on `VBUS_IC` stays (U7 pins 1 and 3, C2, R1, R6, R21, R_SU1, R_SU14, U5 pin 2). Rating: a 1206 jumper
   is usually rated 2 A or more; the HW-017 [3] A is checked from the datasheet at order time (O2) because no datasheet
   can be read tonight.
2. **Trim T1 (HW-010 step 3 resistor).** R_ILIM3 27.4 kohm + R20 301 ohm in series becomes one **R_ILIM3 = 27.7 kohm 0.1 %**
   (E192 value; 27.4 k + 0.301 k = 27.701 k). R20 is deleted. Gate: `sim/ilim_steps.py` with 27.7 k gives a step 3 window
   inside 1366 to 1577 mA with margin >= the current margin minus 0.1 mA, written as a pytest case in
   `tests/test_ilim_steps.py`. Effect: one part and one extended part type less.
3. **Trim T2 (shared supply protection of U14 and U15).** U14 pin 5 and U15 pin 5 join one net `VDD_SW` fed by R_SU14
   (1 kohm) with DZ14 (BZX84C5V1) to GND; R_SU15 and DZ15 are deleted; C24 and C25 (100 nF) stay, one at each supply pin.
   Gate: the surge script of `analysis-supply-pin-surge.md` is rerun with the shared node (two 100 nF, one zener, both
   TMUX1101 supply currents); the pin peak stays below 6 V and the steady pin voltage at VBUS_IC 4.5 V stays above the
   TMUX1101 minimum supply, as a pytest case. If the script cannot run (ngspice missing), T2 is not applied.
4. Every trim is written into HW-010 as an amendment marked "owner pre-approved by rule, 2026-11-17", with the numbers.
5. `src/sourcing.py`: add R22 and the 27.7 k part (A8); remove R20's entry if unused.

### 4.2 Placement (`src/pcb_full.py`, `src/pcb_place.py`, `src/mech_outline.py`)
- New switch **`P1=1`** (environment, default 0 so that the stored two-sided board and its tests do not change):
  - every movable part gets `sides = "F"` except refs starting with `TP` (`"B"`);
  - the 16 LED bypass capacitors are placed on **F**, beside their LED on the ring: the four rotations and both tangential
    sides are tried, ranked by the distance of the equal-net pads (+5V to LED pad 4, GND to LED pad 2) as today; the
    chosen spot must not touch the hook keep-outs or the neighbouring LED courtyard;
  - the top region of `region_rect_ok` also allows the tab (today bottom only);
  - J1 through-hole pins keep their bottom obstacle (they are not assembled; hand-soldered, HW-008 amendment).
- `P1_DIAM` (environment, default 46.0): board diameter for the fallback; `mech_outline` reads it for `D_PCB` only when
  `P1=1`. R_MOVE grows by the same amount as R_PCB minus the LED ring clearance (parts may also sit outside the ring:
  the annulus between the LED ring and the edge becomes a top-side region at r >= R_RING + 2.0 mm when P1_DIAM > 46).
- **HW-016:** `LAYOUT_RULES` gets `("C4", "U7", 8.0)` and `("C32", "U7", 8.0)` (centre distance 8 mm keeps the pad
  centres within 10 mm of U7 pin 6, because a 1206 pad centre is 1.5 mm from its part centre and U7 pin 6 is within
  1.0 mm of the U7 centre); a test measures the real pad-centre distance on the routed board.
- **HW-017:** R22 goes into `pcb_rules.MAIN_PATH_PADS` (both pads) and `ROUTE_FIRST` gets `VBUS` with width 0.6 mm,
  so the link is in the routed main path and as wide as the path before it.

### 4.3 Routing, stitching and checks (`run_pcb.sh`, `src/pcb_stitch.py`, `src/pcb_fabcheck.py`)
- `run_pcb.sh`: accept either pinned jar hash (GitHub release `f6f51bb0...`, Maven Central executable jar `7f8c6247...`);
  `run_meta.json` already records the jar hash.
- **No via-in-pad:** `pcb_stitch.py` must not put a via inside any SMD pad copper; it places a via beside the pad with a
  short track instead. `pcb_fabcheck.py` gets a check `via_in_smd_pad` (count of vias whose drill or annulus overlaps an
  SMD pad of another net or the same net) that must be 0 on P1. Existing boards are reported, not failed, unless `P1=1`.
- Gate: strict DRC profile `stitched-4l` and strict ERC `full`, unchanged waiver list (`known-open-violations.json`).
  Expected tolerated classes: `items_not_allowed` (U9 antenna, DEV-004) and `courtyards_overlap` (U9). Any new class is a FAIL.
- Power check `pcb_power_check.py`: report drops against the 50 mV analyst target (an assumption, not a requirement).

### 4.4 Finishing (`src/pcb_finish.py`)
- Top silkscreen designators where the DRC allows (existing logic), three fiducials on the top side (Economic is top only;
  the bottom fiducials are removed for P1).
- **Bottom silkscreen map** (answer 13): for every top part, its reference as mirrored text on B.SilkS at the part's
  position, 0.8 mm high; text that would touch a bottom pad, a test point or the board edge is moved in 0.5 mm steps
  tangentially up to 2 mm, else left out and counted. Count reported.
- Assembly drawing: `kicad-cli pcb export pdf` of F.Fab, F.SilkS, Edge.Cuts (every reference is on F.Fab).

### 4.5 Order package and panel (`scripts/fab_p1.sh`, `scripts/fab_jlcpcb.py`, `scripts/panel_p1.json`)
- `scripts/fab_jlcpcb.py <board> <out>`: runs kicad-cli for Gerbers (all copper, mask, paste, silk, Edge.Cuts) and Excellon
  drill, the position file and the BOM; converts BOM to JLCPCB columns `Comment, Designator, Footprint, LCSC Part #` (DNP
  and test points excluded, LCSC from the `LCSC` field) and CPL to `Designator, Mid X, Mid Y, Layer, Rotation`; writes
  `manifest.json` with sha256 per file, git describe, KiCad version; zips Gerbers + drill.
- Panel: KiKit 1.8.1 (`kikit panelize -p scripts/panel_p1.json`): **1 x 1 board in a frame with two rails of 5 mm**,
  3 fiducials and 4 tooling holes on the rails, mouse-bites on the round edge. 1 x 1 because the owner orders 5 PCBs and
  2 assembled: a 2 x 1 panel would force 4 assembled boards. Reversible: the panel file sets the layout.
- `scripts/fab_p1.sh <board> <out>` runs both, plus the assembly PDF.

### 4.6 CI (`.github/workflows/fab-release.yml`)
- On push to `main`: job in `kicad/kicad:10.0`, installs KiKit with pip, runs `scripts/fab_p1.sh` on the stored P1 board,
  then with `gh` (token `GITHUB_TOKEN`, permission `contents: write`) updates one **draft** release `fab-latest`:
  deletes its old assets, uploads the new zip, BOM, CPL, PDF and manifest, and writes the commit SHA in its notes.
- On `release: published`: the same build for the tagged commit, assets attached to that release.
- Not run tonight: GitHub Actions cannot run here. The script steps are run locally in the same image.

### 4.7 Non-functional
Testability: test pads stay on the bottom (pogo access), the HW-016 spares and HW-017 link are rework points.
Auditability: manifest with hashes and git describe; run tables in the report. Safety: HW-010 behaviour unchanged; trims
only through their recalculation tests. Security: CI token scoped to `contents: write` on this workflow only.
Manufacturability: one side, no via-in-pad, fiducials, panel rails. Resources: power check numbers reported.
Regulatory: no change to the radio, the power input or the LED drive; the compliance matrix gets the P1 evidence rows
(`regulatory-check`). Sustainability/licensing: KiKit is MIT; it is a build tool, not shipped.

## 5. Detailed implementation plan (order of work; one commit per step, pushed)
1. Tooling: `run_pcb.sh` two hashes, test `tests/test_run_pcb_jar.py` extended.
2. Trim T1: test first (`test_ilim_steps.py` case for 27.7 k), then `layout_full.py`, `sourcing.py`, HW-010 amendment.
3. Trim T2: surge rerun as a test first; apply only if it passes.
4. HW-017: `layout_full.py` net `VBUS` and R22; tests in `tests/test_layout_full.py` (net membership as in 4.1 item 1).
   Regenerate: `SPIKE_ALLOW_KNOWN_OPEN=0 sh run_full.sh python3 <scratch>/fullP1` (ERC 0 findings, deterministic).
5. P1 placement switch, top-side LED caps, region, HW-016 rules: tests in `tests/test_pcb_full.py`
   (all non-TP footprints on F.Cu with `P1=1`; LED caps within 3.0 mm of their LED; old behaviour with `P1=0` unchanged).
6. Routing batches: `P1=1 SPIKE_ALLOW_KNOWN_OPEN=0 sh run_best.sh <scratch>/fullP1 <scratch>/p1-ring1 12`. Up to **three**
   batches at D_PCB 46 mm (one change per batch, per the skill). If none passes the gate (unconnected 0, strict FAIL 0,
   hard 0), set `P1_DIAM=48`, check the housing (step 9 first part), and run up to three more; then 50 mm; then stop and report.
7. Batch V: the best placement seed range again with vias 0.7 / 0.3 mm; keep it if it also passes.
8. No via-in-pad: `pcb_stitch.py` change and `pcb_fabcheck.py` check with tests (a synthetic board with a via in a pad
   fails, one beside the pad passes); rerun on the chosen board.
9. Housing fit (only if the diameter changed): `mech/freecad/housing.py` with the new D_PCB, tolerance check, report.
10. Finishing: fiducials top only, bottom silkscreen map, designators; tests in `tests/test_pcb_finish.py`.
11. Store the chosen board as `hw/kicad/spike-gate/board-p1/` (board, project, schematic copy, libraries, placement json);
    `scripts/ci_hw.sh` checks it with the strict wrapper like `board/`.
12. Order package and panel (4.5) with tests in `scripts/tests/test_fab_jlcpcb.py` (column names; every assembled ref in
    BOM and CPL exactly once; DNP and TP excluded; manifest hashes match the files).
13. CI workflow (4.6).
14. Records: report `docs/verification/reports/p1-board.md` (run tables, gate counts, power drops, fab review, not run),
    TC-208 evidence row, CHANGELOG, traceability check, RISK entries (section 7).

## 6. Test and verification plan
| Item | Test / analysis | Level | Pass |
|---|---|---|---|
| T1 trim | `test_ilim_steps.py` 27.7 k case | analysis | step 3 window inside 1366..1577 mA |
| T2 trim | surge rerun with shared node | SPICE | pin peak < 6 V; steady pin voltage >= TMUX1101 VDD min at VBUS 4.5 V |
| R22 / VBUS split | `test_layout_full.py` | unit | net members exactly as 4.1 item 1 |
| One side | `test_pcb_full.py` with P1=1 | unit | every footprint except TP* and fiducials on F.Cu |
| HW-016 | test on the chosen board | inspection by script | C4 and C32 pad centres <= 10 mm from U7 pad 6 |
| HW-017 | test on the chosen board | inspection by script | R22 pads on VBUS / VBUS_IC; track width at R22 >= 0.6 mm |
| No via-in-pad | `test_pcb_fabcheck.py` + run on board | unit + board | `via_in_smd_pad` = 0 |
| Gate | strict DRC `stitched-4l`, strict ERC `full` | tool | only tolerated classes |
| Fab minimum | `pcb_fabcheck.py` | tool | PASS against ADR-0020 numbers (dated 2026-11-08) |
| Order files | `test_fab_jlcpcb.py` | unit | columns, refs once, DNP/TP out, hashes |
| Panel | KiKit run + DRC of the panel | tool | panel file written; 1 board; 3 fiducials |
| Housing (if grown) | FreeCAD tolerance check | analysis | existing checks pass |

Not run tonight, by design: JLCPCB DFM and Economic rules (O1), LCSC stock and price, CPL rotation preview, CI on GitHub,
any bench test, antenna, thermal.

Order-time checklist for the owner (written into the report): **O1** read Economic PCBA rules (one side, 4 layers, board
size, panel acceptance); **O2** LCSC numbers and stock for every BOM line, including R22 (0 ohm 1206, >= [3] A) and the
27.7 k part; **O3** upload the Gerbers to JLCPCB's DFM viewer; **O4** check CPL rotations in the preview; **O5** HASL
lead-free, 1.6 mm, 4 layers; **O6** price within EUR 100.

## 7. Risks and open questions
- R1 one side does not route at 46 mm: fallback growth (answer 7). Housing grows with it (MECH-001 margin shrinks).
- R2 HASL on the X2QFN-12 (U1): bridges or opens; owner choice; new RISK entry; ENIG is the fallback at order time.
- R3 Economic PCBA may refuse 4 layers or the panel: owner checks (O1); Standard one-sided is the fallback.
- R4 Trims change safety-relevant values: only through the tests above, recorded for the owner to confirm.
- R5 The LED bypass capacitors on the top side sit within the LED light path; the diffuser distance (8 mm) makes
  shadows unlikely but not shown.
- R6 Budget: about 12 extended part types; price not read.
- Open for the owner: LED bypass capacitor count; hold-off capacitor count; SYS-022 against the hand-soldered J1;
  ADR-0020 revision for the 0.15 mm rule set.

## 8. Rollout / rollback and traceability
IDs: HW-008, HW-010 (trim amendments), HW-016, HW-017, ADR-0021, ADR-0020 (Proposed, revision later), new RISK entries,
RV-014. Rollback: the two-sided board stays in `board/`; `P1=0` gives the old placement; each trim is its own commit.
