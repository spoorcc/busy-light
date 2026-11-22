# 08 -- Prototype board P1: one-sided assembly for JLCPCB Economic PCBA (design doc)

- **Status:** In Review (revision 5 of 2026-11-22: section 0 records the state after the build; goldfish review RV-016.
  Revision 4: after the RV-014 readiness review: NO-GO overall, steps 1 to 4 ready; blocking gaps B1 to B3 fixed in that revision). The owner pre-approved implementation after a GO from the
  readiness review (answer 16 of 2026-11-17, `docs/journal/2026-11-17-p1-order-owner-decisions.md`). The owner confirms or
  rejects this plan and its result together.
- **Date:** 2026-11-17  **Owner:** Ben Spoor (author: assistant)
- **Area:** hw (with a CI part under `.github/` and `scripts/`)
- **Requirements addressed:** HW-008 (Approved 2026-11-17 with the through-hole amendment), HW-010 (Approved; trim T1 under the
  owner rule of 2026-11-17; bench access for TC-210), HW-016 (Approved 2026-11-17, [10] mm), HW-017 (Approved 2026-11-17),
  HW-003 (Approved: rating of the input path, recalculated for R22 and the new path), HW-009 (Draft: ERC/DRC reports stored with the revision), HW-001, HW-005, HW-006 (Draft, unchanged ring geometry, antenna
  keep-out with DEV-004, test points). ADR-0021 (Accepted 2026-11-17). ADR-0020 stays Proposed: its fab numbers are used as
  **unaccepted inputs** (dated 2026-11-08), and P1 uses the owner's 0.15 mm answer, not ADR-0020 option B.
- **EGM review record:** RV-014 (comprehension / antagonistic / readiness); RV-016 (revision 5 and the stored board: not
  ready to order)
- **Superseding question (2026-11-18):** the measured one-sided placement does not fit on 46 mm; ADR-0022 (Proposed) asks the owner
  to choose between two-sided P1 (recommended), part reduction, board growth or giving up the keep-out. Steps 1 to 5 and the order-package
  scripts are implemented; routing of P1 waits for that decision. *(Revision 5: answered on 2026-11-18 by the "fewer parts"
  decisions of ADR-0023; ADR-0022 itself is still Proposed. See section 0.)*

## 0. Revision 5: state after the build (2026-11-22)
Where this section and sections 1 to 8 differ, this section applies. Sections 1 to 8 are the revision 4 text of 2026-11-18,
kept as RV-014 reviewed it. Sources: `docs/journal/2026-11-18-overnight.md`,
`docs/journal/2026-11-18-simplification-owner-decisions.md`, `docs/journal/2026-11-20-second-pass-board-p1.md`,
`hw/kicad/spike-gate/board-p1/README.md`. The work ran before a readiness GO (RV-014 finding 5, recorded there); the owner
confirms or rejects this plan and its result together.

### 0.1 What changed the plan after revision 4
- One side did not fit on 46 mm (ADR-0022, Proposed: best overlap 25.1 mm2). On 2026-11-18 the owner took the "fewer parts"
  direction (ADR-0023, Accepted for the decisions): step 3 = both ILIM switches with R_ILIM3 = 56.2 k (this replaces trim T1 and
  removes U13); the limiter FAULT and the TPS3840 RESET share the node GATE_OK_RB (U10 and R6 removed); smaller packages
  (implemented in `94ce2cf`, `8573614`). ADR-0022 stays Proposed until the owner closes it.
- Owner answers of 2026-11-18: the U9 library courtyard stays a placer obstacle; the module moves 5 mm towards the antenna edge;
  eight more parts in 0402 (`28f924d`).
- R1 did not happen: after ADR-0023, one side routed at 0.15 mm on 46 mm. The 0.1 mm comparison (b3, option A') was not run.
- HW-016 spares: on the bottom side in 1206, do-not-populate, so the assembly stays one-sided; the proposed 0805 change of
  HW-016 is withdrawn (HW-016 entry, `bbfa73d`).

### 0.2 Step status (section 5)
| Step | State | Evidence | Deviation from revision 4 |
|---|---|---|---|
| 1 Tooling | Done (`a58ef4a`) | `run_pcb.sh` hash test | none |
| 2 T1 | Done, then replaced by ADR-0023 | `test_ilim_steps.py::TrimT1`, `::BothOnStep3` | HW-010 amendment "ADR-0023" replaces amendment T1; the owner confirms both texts |
| 3 HW-017 split | Done (`706ba3e` for the power check) | `test_layout_full.py::DampingLink`, `test_pcb_rules.py::MainPathSplit`; power check cases VBUS and VBUS_IC | none |
| 4 No via-in-pad | Done (2026-11-18); a gate of the order script (`5146d53`) | `test_pcb_fabcheck.py`; board-p1: 0 of 174 vias in an SMD pad | none |
| 5 Placement | Done | `test_pcb_full.py` (P1 subprocess); placement overlap 0.0 mm2 | (a) **The four input-path rules of 4.2 were not implemented** (`LAYOUT_RULES` in `src/pcb_full.py` has none of them). Measured on board-p1 on 2026-11-22 (pcbnew, part centre to the nearest J1 `VBUS` pad centre): TVS1 7.55 mm (rule 6.0), U6 13.75 mm (8.0), R22 10.68 mm (8.0); R22 centre to U7 centre 12.53 mm (6.0). All four are missed. (b) HW-016 rule 7.5 mm, spares on the bottom (its code comment still says 0805). (c) LED capacitors keep 3 mm from the panel tab sectors. |
| 6 Batches | Done in another form | journals of 2026-11-18 and 2026-11-20 | Batches p1b1 to p1b12 (one change each) and a second router pass `run_repass.sh` (a new tool) replaced b1 to b3. Stored: p1b8 run 3 after the second pass (`7a26366`, `23aa36c`). Router, stitcher and clean-up defects found on the way were fixed with tests that fail before the fix (journals). |
| 7 Finishing | Done | `test_pcb_finish.py` | Fiducials: FID1 on the top and FID4 to FID6 on the bottom (revision 4: three on the top only); the panel rails add three. 50 designators on the silkscreen, 47 parts without room. |
| 8 Store | Done (`23aa36c`); `ci_hw.sh` checks board-p1 (`d4f01a3`, CI hardware job) | CI run 44904594328 | DRC and ERC JSON and `chosen_run.txt` are not stored: they are build output that the scripts write again; the README records the numbers and the run. The owner confirms. |
| 9 Board tests | Done, 6 tests | `tests/test_board_p1.py` | No test lists the pairs that overlap U9; only the DRC count (14, the waiver maximum) checks them. |
| 10 Order package | Done | `scripts/tests/test_fab_check.py`, `test_fab_p1_script.py`; `fab_p1.sh` exit 0 in the KiCad 10 image (2026-11-21) | scipy was missing from `requirements-fab.txt` until 2026-11-21 (fixed with a regression test) |
| 11 CI workflow | Written (`c7ef1ee`) | `scripts/tests/test_fab_release_workflow.py` | Not run on GitHub: it runs on `main` only. |
| 12 Records | Partly | DEV-007 (Proposed); TC-208, TC-216, TC-217 procedures (drafted); CHANGELOG; regulatory check of 2026-11-18 | **Not written:** the report `docs/verification/reports/p1-board.md` (its numbers are in `board-p1/README.md`); RISK entries for R2 (HASL on U1), R7 (jumper rating) and R9 (missing LCSC numbers): none in the register. The P1 section of `docs/regulatory/compliance-matrix.md` still says that P1 is not placed or routed. |

### 0.3 Result against the goals (section 1)
- G1 met: every assembled part on the top. On the bottom: TP1 to TP6, the DNP spares C4 and C32, FID4 to FID6.
- G2 met with tolerated classes only: strict ERC 0 findings; strict DRC `courtyards_overlap` 14 (maximum 14) and
  `items_not_allowed` 1, both U9 (DEV-004, Proposed).
- G3 met: 0 of 174 vias in an SMD pad.
- G4 partly met: R22 between `VBUS` and `VBUS_IC`; C4 and C32 within 10 mm of U7 pin 6 (`test_board_p1.py`). R22 has no part
  that meets HW-017's [10] mohm and no MPN in the BOM (A8); the main path is not >= 0.6 mm wide (RV-016 row 13).
- G5 not met: `fab_p1.sh` builds the package locally (2026-11-21); the CI build has not run.
- Supply drops (analyst currents, 50 mV analyst target): `VBUS` 23.9 mV and `VBUS_IC` 44.1 mV at 1.5 A, 68.0 mV from J1 to U7
  in copper. The jumper is not in the power check: the R22 candidate (up to 20 mohm) adds up to 30 mV at 1.5 A.

### 0.4 Open before an order
- Owner: approval of this plan with its result; closing ADR-0022; ADR-0023 text and the HW-010, SW-009 and HW-016 amendments;
  DEV-004 and DEV-007 (Proposed); the deviations in the table of 0.2 (step 5 (a), step 8).
- Owner: U5 TPS3840DL40DBVR has no LCSC or JLCPCB listing (without it the HW-010 hold-off does not work); the R22 candidate
  has up to 20 mohm against [10] mohm.
- Owner: the assistant's picks (spares on the bottom in 1206, tab azimuths, the 0.75 full-width rule, the 50 mV target).
- Assistant, after review: the records of step 12.
- Order steps O0 to O8 of section 6 are unchanged.
- Not run: housing fit, antenna range with the module 5 mm closer to the edge (TC-205), thermal, `fab-release.yml` on GitHub,
  JLCPCB DFM and price, bench.

### 0.5 Review RV-016 (2026-11-22): not ready to order
`docs/reviews/RV-016-p1-plan-rev5-as-built-goldfish.md` (45 rows; readiness pass not run). This list applies over 0.2 to 0.4.
- **Gate safety after ADR-0023** (rows 1 to 6): a missing U5 makes the gate fail open (R8 holds GATE_OK_RB high), and the order
  check lets U5 be missing; GPIO6 sits directly on GATE_OK_RB, so firmware can hold the gate open; the pull-up went from VBUS_IC
  (150 kohm) to 3V3 (10 kohm) against the read TPS3840 evidence; the owner's CC-pin protection (P3, 2026-11-07) is not on the
  board; the BZT52C5V1S zeners have no datasheet evidence; ADR-0023 has had no goldfish review.
- **Placement and copper** (rows 11 to 15): 5 of the 15 implemented `LAYOUT_RULES` are missed too (the placer keeps its best
  placement without a message); the input-path rules (0.2 step 5 (a)); the main path has 0.45 mm segments and two 0.3 mm vias,
  not >= 0.6 mm; no tool sums the J1-to-U7 drop; the bottom silkscreen map of 4.4 (answer 13) and U1's F.Fab text are missing.
- **Order files** (rows 16 to 18, 28, 29): the full BOM leaves out C4 and C32; their pads have bottom paste; no board text or
  revision; `fab_check` checks "0.1%", not the ILIM values.
- **Housing and parts** (rows 22 to 24): MECH-001 (Approved, 58 mm; amended to 60 mm by the owner on 2026-11-22, now met) was exceeded (`largest_dim_mm` 59.24, as for the spike
  board); the LED and U9 footprints are not compared with manufacturer drawings; SW1 does not match the housing button.
- **Evidence** (rows 26, 30, 33, 34): PR CI does not run `hw/kicad/spike-gate/tests`, so the test evidence of 0.2 is from local
  runs; no ERC or DRC report is stored (HW-009) and DEV-004 is scoped "spike only"; steps 5 to 12 ran after a readiness NO-GO
  and partly before Approved text (a DEV entry is to be written); the regulatory check predates ADR-0023.
- **Consequence** (row 45): rows 2 to 5 change the schematic and rows 11 to 13 need a new placement, so P1 is placed and routed
  again after the owner's decisions, with the tool fixes first.

Done after RV-016 without an owner decision (2026-11-22; journal `2026-11-22-reviews-and-gates-board-p1.md`): the order
script fails on board-p1 (placement rules; must-place parts U5 and R22; bottom paste); `pcb_layout_check.py`; exact ILIM
values; the full BOM with the DNP parts; release notes with the missing list and owner waivers; the release workflow on
pull requests and red on a failed gate (run 44989926250: as intended); the spike-gate tests in the `ci.yml` hardware job;
the placer records rule misses, enforces the input-path rules with P1 and gives the DNP spares no paste; HW-016 rule
7.0 mm; the J1-to-U7 drop reported; the bottom silkscreen map and an identification text in `pcb_finish.py`; RV-017 on
ADR-0023 (rejected as written); RISK-047 to RISK-053; DEV-008. Board-p1 is unchanged.

Superseded statements of sections 1 to 8 (RV-016 row 37):
- Header: "HW-010 (... trim T1 ...)": ADR-0023 amendment. "HW-003 (... recalculated for R22 and the new path)": not done
  (row 13). "HW-009 (Draft: ERC/DRC reports stored with the revision)": not stored (row 30).
- A5: the pin map is unchanged, but plan 07 firmware cannot reach step 3 on P1 (`gate.c` forces both selects off; with ADR-0023
  select 3 alone gives the step-2 current), row 25.
- A8 and R9: the missing LCSC numbers are R22 and U5 only (`scripts/fab_missing_lcsc.txt`).
- 4.1 items 1 to 3: R_ILIM3 is 56.2 k 0.1 % (ADR-0023), not 27.7 k.
- 4.3: the U9 front courtyard measures 43.3 x 31.9 mm on board-p1, not 43 x 20 mm (43 x 20 mm was the vendor keep-out zone).
- 4.4: fiducials FID1 (top) and FID4 to FID6 (bottom): `pcb_finish.py` found room for one on the top and numbers the bottom ones
  from 4; JLCPCB uses the three on the panel rails.
- 4.5: the ILIM values belong to `ilim_steps.candidate_both_on()`; `fab_check` checks "0.1%" only (row 28).
- 4.6: the build job installs the Python tools with pip from `scripts/requirements-fab.txt`, not with apt.
- Section 6 bench table: HOLD_OK and FAULT_N no longer exist; both are the node GATE_OK_RB (R8 pin 2, U5 pin 1, U7 pin 4); R6
  is removed. O2: "the 27.7 k 0805" is replaced by the 56.2 k 0.1 % parts; O7 and O8 are to be rewritten (row 9).

## 1. Problem definition
The owner wants to order a first prototype board (P1): 5 bare PCBs, 2 of them assembled by JLCPCB with the **Economic**
PCBA service, at most EUR 100 (answers 1, 3, 11). The stored board `hw/kicad/spike-gate/board/busy_light_spike.kicad_pcb`
(ring14 run 9, made with `SPIKE_PROFILE=fine`, i.e. **0.1 mm tracks and clearance**, vias 0.5 / 0.2 mm) has 41 footprints on
the top side and 60 on the bottom (6 of them bare test pads), has 35 vias inside SMD pads (32 in the LED ring cells, 2 at DZ15,
1 at C32; none under U9, although the stitcher code had a U9 via-in-pad path; measured 2026-11-18 by `pcb_fabcheck.py`), and its
`largest_dim_mm` is 59.24 (MECH-001 allows 58 mm). Economic PCBA, as the assistant understands it (not read, A1), assembles
one side only and no through-hole parts. P1 therefore needs a new placement with every assembled part on the top side.

**Correction to the owner question of 2026-11-17.** The owner answered "use 0.15 traces if I'm not mistaken". The stored board
uses 0.1 mm, and ADR-0020 records that no two-sided run on the real footprints completed at 0.15 mm. One side at 0.15 mm is
harder still. This plan routes at 0.15 mm as answered and runs one comparison batch at 0.1 mm, so the owner can decide with data.

Goal: a P1 candidate that (G1) has every assembled part on F.Cu, (G2) passes the strict DRC and ERC gate with only the
tolerated classes of section 4.3, (G3) has no via inside an SMD pad, (G4) carries the HW-017 damping link and the HW-016
spares within [10] mm, (G5) comes with an order package (panel Gerbers, drill, JLCPCB BOM and CPL in panel coordinates,
assembly drawing, ERC/DRC/fab-check reports) built by a script and by CI.

Out of scope: a product board; changing the three limit steps or the gate behaviour (HW-010); antenna or RF measurement
(spike 7.2, DEV-004 stays Proposed); firmware (the pin map does not change); placing the order (the owner does it);
growing the board or the housing (section 2, A4); trim T2 (section 4.1); ruff/lint of the spike code (listed in section 7).

## 2. Constraints and assumptions
Owner answers of 2026-11-17 (journal): one-sided SMD on the top (LED) side, test points as bare pads on the bottom (6);
0.15 mm tracks (3); 4 layers, 1.6 mm, HASL lead-free (10); no via-in-pad (9); designators on the top silkscreen where they
fit, on the bottom silkscreen, and in an assembly drawing PDF (13); own KiKit panel (14); fallback "grow the board up to the
housing limit" (7); Freerouting 2.5.0 from Maven Central with both hashes pinned (8); order files built by CI, not committed (17);
undecided reversible points: pick, log, continue; hard-to-reverse points: leave for the owner (19).

Assumptions (challenged in RV-014):
- **A1. Economic PCBA rules are not read.** Assumed: one side, SMD only, JLCPCB library parts, 4 layers accepted. jlcpcb.com is
  blocked here (proxy 403); the owner declined the network change. Order step O1 makes the owner read them. If Economic refuses
  4 layers or the panel, the fallback is Standard PCBA one-sided (more cost, same files).
- **A2. Fab numbers.** ADR-0020's JLCPCB multilayer numbers (read 2026-11-08, Proposed ADR, unaccepted input) are used.
  P1 uses the default profile of `src/pcb_rules.py` (0.15 mm track and clearance; via 0.6 / 0.3 mm, ring 0.15 mm = the absolute
  minimum). No other via size is tried tonight (there is no profile switch for it; see section 7).
- **A3. Area and routing risk.** Inside the LED ring the top has about 940 mm2 (r 17.3 mm) less the module (13.2 x 16.6 mm), its
  antenna strip and SW1: about 650 mm2. The movable parts' courtyards take about 430 mm2 (66 %; about 80 % with the vendor
  antenna keep-out), so placement itself may not be overlap-free. P1 frees the ring annulus: the LED capacitors move beside their
  LED (4.2), so `R_MOVE` becomes 18.4 mm for P1 (the LED courtyards start at r 18.75), about +120 mm2. The two-sided board needed
  both sides and 0.1 mm rules. **Failure to place or route at 0.15 mm is likely (R1).** A placement gate runs before any routing
  (4.3).
- **A4. No growth tonight.** The answer-7 fallback (grow the outline) is not automatic: `largest_dim_mm` of the stored board is
  already 59.24 mm against the 58 mm of MECH-001 (Approved), and with the J1 mouth tied to the LED ring every 2 mm of diameter adds
  about 1 mm. Growth changes an Approved MECH requirement's conformance, which answer 19 leaves to the owner. The P1 report states
  `largest_dim_mm` against 58 mm for every candidate. The housing model (`mech/analysis/housing_params.py` D_OUT, D_PCB) and
  `mech_outline.R_OUT` are not changed.
- **A5. The pin map does not change.** No GPIO is moved; firmware plan 07 stays valid.
- **A6. Trims.** Only T1 is applied (section 4.1). T2 (shared supply protection of U14 and U15) is **not** applied: it changes
  Approved HW-010 text ("each with its 100 nF at the pin and a 5.1 V zener") and touches no step or hold-off window, so it is
  outside the owner rule. Its surge analysis stays as an option for the owner. Other reductions (16 LED bypass capacitors,
  the six hold-off capacitors) are listed for the owner, not done.
- **A7. CPL rotations.** JLCPCB's rotation differs from KiCad's for some footprints. The owner checks them in JLCPCB's
  preview at order time (O4). No offset table is invented.
- **A8. Parts without an LCSC number.** R22 (0 ohm 1206, HW-017) has no recorded part; its MPN and LCSC stay empty and the BOM
  check reports it (section 4.5) for O2. **No part number is derived or taken from memory.** The HW-017 criteria "[10] mohm at
  1.5 A" and "[3] A" are checked against the chosen jumper's datasheet at O2; common 1206 jumpers may be specified at about
  50 mohm and 2 A (general knowledge, not verified), which would miss both bracketed values: an owner point.
  Missing LCSC numbers are wider than R22: TPS3840DL40 (U5), USBLC6-2P6 (U6), 74LVC1G02/08/11 (U13, U10, U3, U4),
  74AHCT1G125 (U11) have none in `sourcing.py`. Economic PCBA does not place a line without one, and U5 missing would defeat
  the HW-010 hold-off. The order check lists them all (4.5) and O2 resolves them; a swap with another footprint needs a re-route
  and, for gate parts, an ADR.
- **A9. Process status.** P1 files are prototype order files made from the spike generator on the owner's instruction, not
  "product files" in the sense of ADR-0012 G1. This reading is the assistant's; the owner confirms it (section 7).

## 3. Alternatives considered
| Option | Idea | For | Against |
|---|---|---|---|
| A (owner choice, answer 1) | Re-place the existing netlist with every assembled part on top, 0.15 mm rules | cheapest assembly (Economic); HW-008 one side | likely not routable at 0.15 mm (A3); new routing evidence needed |
| A' (comparison batch) | As A with the 0.1 mm profile (what the stored board used) | more likely to route | thin fab margin (ADR-0020); not the owner's answer |
| B | Order the stored two-sided board with Standard PCBA | ready now | two-sided assembly cost; violates HW-008 (one side); via-in-pad needs filled vias |
| C | A small gate-only test board first | quick bench of HW-010 | new schematic and layout; no LED, Wi-Fi or housing test |
| Do nothing | Wait | no cost | no bench evidence for HW-010, ADR-0021 or the antenna |

A is the owner's choice; A' gives data for the owner. B stays available: `board/` is kept (rollback, section 8).

## 4. Technical plan

### 4.1 Schematic (`src/layout_full.py`, regenerated with `run_full.sh`)
1. **HW-017 damping link.** New net `VBUS` for the connector side: J1 pins A4, A9, B4, B9, TVS1 pin 1, U6 pin 5. New part
   **R22**, value `0`, `Resistor_SMD:R_1206_3216Metric`, pin 1 on `VBUS`, pin 2 on `VBUS_IC`. Everything else on `VBUS_IC`
   stays: U7 pins 1 and 3, C2, R1, R6, R21, R_SU1, R_SU14, R_SU15, U5 pin 2. A `VBUS` rail with a power flag is added (ERC).
2. **Trim T1.** R_ILIM3 27.4 k + R20 301 ohm in series becomes one **R_ILIM3 = 27.7 k 0.1 % in 0805** (Yageo RT0805BRD0727K7L,
   LCSC C865349, from the JLCPCB library mirror query recorded in `stock-check-ilim-holdoff.md`; 0.1 % 27.7 k exists in 0805
   and 0402 only; stock not confirmed). R20 is deleted. Gate: `tests/test_ilim_steps.py::TrimT1` asserts all four HW-010
   margins (s1_min, s1_max, s3_min, s3_max) stay positive and each within 0.1 mA of the series pair, step 2 inside
   850..1150 mA; the hold-off set is unchanged. Result: step 3 window 1381.2 to 1566.7 mA (margins 15.22 and 10.33 mA).
3. T1 is written into HW-010 as an amendment marked "owner pre-approved by rule, 2026-11-17".
4. `src/sourcing.py`: 27.7 k entry as in item 2; the 27.4 k and 301 ohm entries are removed (no part uses them).
5. Effect on the old board: T1 and R22 change the shared netlist, so `board/` can no longer be regenerated from HEAD; it is
   frozen as made from commit `1d2a1a6` (recorded in `board/README.md`). `src/gen_gate.py` (the older gate fragment of
   `test_gate_logic.py`) keeps the old pair and is out of scope; noted in the report.

### 4.2 Placement (`src/pcb_full.py`, `src/pcb_ring.py`)
- New switch **`P1=1`** (environment, read at build time; default 0 keeps the two-sided behaviour):
  - every movable part gets `sides = "F"` except refs starting with `TP` (`"B"`); J1 keeps its bottom obstacle for the
    through-hole pins (hand-soldered, HW-008 amendment);
  - the 16 LED bypass capacitors go on **F** in the gap beside their LED (the gap between LED courtyards is about 4.6 mm
    tangentially), long axis radial, on the side that the WS2812B-2020 supply pads face (pad 4 +5V and pad 2 GND sit on opposite
    corners); the tangential offset is the smallest one that clears both courtyards (about 3.1 mm centre to centre); both sides
    and the four rotations are tried, ranked by the equal-net pad distance; the hook keep-outs are respected, and **a side whose
    courtyard meets any fixed courtyard (J1 included, which sits between D16 and D1) is rejected** (RV-014 readiness B3); J1's
    position is not moved for this (no growth, A4). This keeps the ring
    annulus inside the LEDs free for movable parts (`R_MOVE` 18.4 mm with P1) and leaves about 1.5 mm of the gap for the data link;
  - `pcb_ring.py`: the link layer follows the capacitor's actual layer (F.Cu to F.Cu for P1, no via; the stitcher connects the
    planes); the existing test that asserts the capacitors on B.Cu applies only without P1;
  - the top region of `region_rect_ok` also allows the tab (today bottom only);
  - the P1 flag and `R_MOVE` are written to `placement.json`; downstream tools read them from there, not from the environment;
  - **sourcing fields and DNP (RV-014 readiness B1):** `pcb_full.py` copies the schematic fields MPN, Manufacturer and LCSC
    (from `sourcing.sourcing_fields(value)`) to every footprint and sets do-not-populate and exclude-from-BOM on C4 and C32
    when P1 is set (today `pcb_spare_caps.py` does this only for a C32 it creates itself); test in `tests/test_pcb_full.py`.
- **Input path placement (HW-003, HW-017):** `LAYOUT_RULES` (with support for a fixed partner such as J1, measured to its VBUS pad
  centre) get `("TVS1", "J1", 6.0)`, `("U6", "J1", 8.0)`, `("R22", "J1", 8.0)`, `("R22", "U7", 6.0)`; the pin ties J1-U7 become
  J1-R22 pin 1 and R22 pin 2-U7 pin 1. C4 leaves the U8 block (it belongs to U7, HW-016).
- **HW-016:** `LAYOUT_RULES` gets `("C4", "U7", 7.0)` and `("C32", "U7", 7.0)`: 7.0 + 1.48 (U7 pad 6 from the SOT-23-6 origin)
  + 1.475 (1206 pad centre) = 9.96 mm <= 10 mm. A board test measures the real pad-centre distance.
- **Thermal note:** U1 (TUSB321, HW-013 ambient [70] degC), U7 and U8 now share the top side with the LEDs. No rule is added
  tonight (the placer has maximum-distance rules only); the report lists their distances for TC-213.
- **HW-017 routing:** `VBUS` joins `NET_WIDTH` (0.6 mm), `NET_WEIGHT` (3.0), `OUTER_ONLY` and `ROUTE_FIRST`; the main-path table
  becomes per net: `VBUS`: J1 (all VBUS pads), TVS1 pin 1, R22 pin 1; `VBUS_IC`: R22 pin 2, U7 pin 1, C2 pin 1
  (`pcb_rules.MAIN_PATH_PADS`, `MAIN_PATH_NETS`; users `pcb_dsn.py` branchwidth and `pcb_fix.py` updated). The power check gets
  two cases, `VBUS` (J1 to R22 pin 1) and `VBUS_IC` (R22 pin 2 to U7 pin 1), and reports their sum; the jumper's own resistance is
  not known (A8).
- **Antenna:** `PLACE_ANT_KEEPOUT=1` is part of the baseline (no movable part in the vendor keep-out on either side).

### 4.3 Routing, stitching and checks
- **Order:** the via-in-pad change (below) is made and tested **before** the first routing batch.
- **Placement gate before routing:** one placed P1 board (`pcb_full.py`, no routing) must have `overlap_mm2 == 0`, all LAYOUT_RULES
  met, and its strict `placed-4l` DRC run; its `courtyards_overlap` count with U9 is recorded. The U9 courtyard of the library
  footprint is 43 x 20 mm and covers part of the board; with every part on top the count may exceed the waiver maximum of 14.
  If it does, the work stops at this gate for that class: changing the U9 courtyard or the waiver (DEV-004) is the owner's
  decision; routing is still run for data, and the result is reported as **not gate-clean**.
- **No via-in-pad:** one helper `pcb_rules.via_hits_smd_pad(x, y, via_dia, pads)` (any net, the pad copper grown by 0.05 mm,
  which covers the default zero mask expansion) is used by every via producer: `pcb_stitch.py` (it places the via beside the pad
  with a short track), the grid router of `pcb_fix.py` and therefore `pcb_ring.py`. Vias are tented on both sides for P1. `pcb_fabcheck.py` gets `via_in_smd_pad` (count of such vias). Pass/fail: the CLI flag
  `--no-via-in-pad` makes a non-zero count fail; `ci_hw.sh` passes it for `board-p1/`. Existing boards without the flag report it.
- **Baseline environment of batch 1** (the ring14 settings, so the only change against ring14 is P1 and the netlist):
  `P1=1 PLACE_GRID=1.0 PLACE_ANT_KEEPOUT=1 PLACE_BLOCKS=3 PLACE_ORIENT=1.5 SEED_OFFSET=0 KEYFIRST=1 SPIKE_ALLOW_KNOWN_OPEN=0`,
  12 runs, `FREEROUTING_JAR` = the Maven jar (MD5 compared with Maven Central's published `.md5`: equal; SHA-1 file rate-limited).
- Batches: **b1** baseline; **b2** = b1 with `SEED_OFFSET=200` (new placement seeds); **b3** = the better of b1/b2 with
  `SPIKE_PROFILE=fine` (comparison A'). One change per batch. Each batch's table goes in the report.
- `run_pcb.sh`: the `fr_threads` value in `run_meta.json` is taken from `FR_THREADS` (it is a literal 4 today).
- Gate: strict DRC profile `stitched-4l`, strict ERC `full`, unchanged waiver file. Tolerated by that profile today:
  `courtyards_overlap` (refs U9, max 14), `items_not_allowed` (U9 antenna, DEV-004), `lib_footprint_issues` (DEV-003),
  `footprint_filters_mismatch` (DEV-002), `footprint_symbol_mismatch` (limited refs). Any other class, or a count above its max,
  is a FAIL. Because `courtyards_overlap` names only U9, the P1 report lists every pair that overlaps U9.
- Power check: drops against the 50 mV analyst target (an assumption, not a requirement); plane pieces.

### 4.4 Finishing (`src/pcb_finish.py`)
- Top silkscreen designators where the DRC allows (existing logic); **three fiducials on the top side only** for P1.
- **Bottom silkscreen map** (answer 13): each top part's reference as mirrored text on B.SilkS at the part's position, 1.0 mm high,
  0.15 mm stroke; obstacles are bottom pads, test points, vias, the board edge **and texts already placed**; text is moved in
  0.5 mm steps up to 2 mm, else left out; the refs left out are listed in the report; the strict gate runs after finishing.
- Fiducials: the panel rails carry three (4.5); board fiducials on the top are added where `pcb_finish` finds room and counted.
- Assembly drawing: `kicad-cli pcb export pdf` of F.Fab, F.SilkS and Edge.Cuts. U1's footprint (`custom_fp.py`) gets the
  F.Fab reference text it lacks today.

### 4.5 Order package and panel (`scripts/fab_p1.sh`, `scripts/fab_check.py`, `scripts/panel_p1.json`)
- Panel: KiKit 1.8.1, `kikit panelize -p scripts/panel_p1.json`: **1 x 1 board in a frame with two 5 mm rails**, 3 fiducials and
  4 tooling holes on the rails, mouse-bites on the round edge. 1 x 1 because the owner orders 5 PCBs and 2 assembled.
  Tabs are placed explicitly (KiKit annotation tabs or fixed positions) away from the J1 tab (0 deg), the notch (90 deg) and
  the hook and post azimuths; no capacitor within 3 mm of a tab (checked); the nub size is added to the mech tolerance check
  or listed as not checked.
- Order files from the **panel** with `kikit fab jlcpcb --assembly` (Gerbers, drill, BOM and CPL in panel coordinates, LCSC
  from the `LCSC` field), so Gerbers and CPL agree. Not assembled and excluded: J1 (through-hole by footprint attribute,
  hand-soldered, bought separately: GCT USB4085-GF-A), TP*, FID*, DNP parts (C4, C32), mounting holes. A full BOM (every
  part, DNP marked, extended/basic column "not known") ships next to the JLCPCB BOM (HW-008, HW-016).
- CI image facts (checked by RV-014 in `kicad/kicad:10.0`): no pip, no venv, no `gh`, user `kicad`, Python marked externally
  managed. The build job runs as root, installs `python3-pip python3-numpy python3-shapely ngspice` with apt and KiKit with
  `pip --break-system-packages --require-hashes`; the publish job runs on `ubuntu-24.04` (has `gh`).
- `scripts/fab_check.py <out dir> <board>` (tested): BOM refs equal CPL refs; every assembled ref of the board exactly once;
  every CPL row on the top layer; every CPL point inside the panel outline; no excluded ref present; **every BOM line with an
  empty LCSC number is listed and makes the check exit 1 unless `--allow-missing-lcsc` names it** (the list of A8, O2);
  R_ILIM1..3 values carry "0.1%" and equal `ilim_steps.candidate_p1()`. **Policy (RV-014 readiness B2):** the known missing
  numbers are listed with a reason in the committed file `scripts/fab_missing_lcsc.txt`; CI passes that list, and the release
  notes print it; a number found at order time (O2) goes into `src/sourcing.py` and leads to a new release, so the ordered BOM
  always equals a hashed manifest.
- Also in the package: assembly PDF, the board's strict DRC and ERC JSON, `pcb_fabcheck` output, `manifest.json` (sha256 of
  every file, input board sha256, panel JSON sha256, git describe, KiCad and KiKit versions). "Reproducible" means: same file
  content after the date lines that KiCad writes are removed; `fab_check.py --compare` tests it on two builds.
- `scripts/fab_p1.sh <board> <out>` runs all of it.

### 4.6 CI (`.github/workflows/fab-release.yml`)
- Jobs: **test** (KiCad image, installs ngspice and the pinned Python tools, runs `hw/kicad/spike-gate/tests` and
  `hw/sim/scripts`; skipped tests are listed in the job summary as not run), **build** (needs test; `contents: read`; image by
  digest; KiKit installed from `scripts/requirements-fab.txt` with `--require-hashes`; runs `fab_p1.sh` on `board-p1/` and
  `fab_check.py`; uploads one artifact), **publish** (needs build; job-level `contents: write`; only downloads the artifact and
  runs `gh release`; on push to `main` updates the draft release `fab-latest` with `gh release upload --clobber`; on
  `release: published` for any tag other than `fab-latest` attaches the files to that release). `concurrency` group per ref;
  `workflow_dispatch` runs test and build only. Actions pinned by SHA as in `ci.yml`.
- **The owner orders only from a published, tagged release** (O0); its manifest hashes go into the P1 report. This replaces the
  committed `hw/fabrication/<rev>/` of process section 9 for P1 (answer 17); a DEV entry (Proposed) records that.
- Not run tonight: GitHub Actions cannot run here. The script steps run locally in the same image; actionlint is not installed.

### 4.7 Non-functional
Testability: bottom test pads (pogo); the bench-access table of section 6 maps every TC-210 and TC-217 measurement to a pad.
Auditability: manifest, run metadata stored with the board, reports with ERC/DRC JSON. Safety: HW-010 behaviour unchanged;
T1 only through its test; T2 not applied. Security: write token only in the publish job; hash-pinned build tools.
Manufacturability: one side, no via-in-pad, fiducials, rails. Regulatory: R22 changes the VBUS input path (a series element
before the switch); `regulatory-check` is run and the compliance matrix gets the P1 evidence rows. Licensing: KiKit is MIT, a
build tool only.

## 5. Detailed implementation plan (one commit per step, pushed)
1. Tooling: `run_pcb.sh` two hashes (done in `a58ef4a`, before this review; RV-014 records it); test checks the `JAR_SHAS` line;
   `fr_threads` from the environment.
2. T1: test first, then generator, sourcing, HW-010 amendment.
3. HW-017: generator `VBUS` and R22, tests in `tests/test_layout_full.py::DampingLink`; `pcb_rules`, `pcb_dsn`, `pcb_fix`,
   `pcb_power_check` for the split; regenerate with `SPIKE_ALLOW_KNOWN_OPEN=0 sh run_full.sh python3 <scratch>/fullP1`
   (strict ERC 0 findings, intent equal, deterministic); refresh `tests/data/full.net`.
4. No via-in-pad: `pcb_stitch.py`, `pcb_fabcheck.py` with tests (synthetic board: via in pad fails, beside passes).
5. P1 placement, LED caps on top, `pcb_ring.py` F-only links, tab region, HW-016 rules: tests in `tests/test_pcb_full.py`
   run in a subprocess with `P1=1` (every footprint except TP* on F.Cu, J1 included as a footprint; LED caps within 3.5 mm
   of their LED centre (geometry: about 3.1 mm); `P1` unset gives the old sides); then the **placement gate** of 4.3.
6. Batches b1, b2, b3 (section 4.3). The candidate is the best gate-clean run of b1/b2 (0.15 mm); if none is clean, the best b3
   run is stored as `board-p1-fine/` for comparison and the owner decides (no growth, A4).
7. Finishing (4.4) with tests in `tests/test_pcb_finish.py`.
8. Store the candidate in `hw/kicad/spike-gate/board-p1/` with `run_meta.json`, the environment of the batch, `chosen_run.txt`,
   DRC and ERC JSON, placement json; `scripts/ci_hw.sh` checks it with the strict wrapper and `pcb_fabcheck --no-via-in-pad`.
9. Board inspection tests on `board-p1/` (`tests/test_board_p1.py`): one side, HW-016 distance, HW-017 path (R22 pads on VBUS
   and VBUS_IC, track width >= 0.6 mm on the J1-R22-U7 main path), no via in pad, U9 overlap pairs.
10. Order package and panel (4.5), tests `scripts/tests/test_fab_check.py`.
11. CI workflow (4.6) and `scripts/requirements-fab.txt` with hashes.
12. Records: report `docs/verification/reports/p1-board.md` (batch tables, gate counts, power drops, fab review, bench-access
    table, not run), TC-208, TC-216, TC-217 procedures, DEV entry for answer 17, RISK entries, CHANGELOG, traceability check.

## 6. Test and verification plan
| Item | Test / analysis | Level | Pass |
|---|---|---|---|
| T1 trim | `test_ilim_steps.py::TrimT1` | analysis | four margins > 0 and within 0.1 mA of the pair; step 2 band |
| R22 / VBUS split | `test_layout_full.py::DampingLink` | unit | net members exactly as 4.1 item 1 |
| Main path rules | `test_pcb_rules.py::MainPathSplit` | unit | per-net pads; both nets 0.6 mm, outer only, routed first |
| One side | `test_pcb_full.py` with P1=1 (subprocess) | unit | rule of step 5 |
| HW-016 (TC-216) | `test_board_p1.py` | inspection by script | C4 and C32 pad centres <= 10 mm from U7 pad 6 |
| HW-017 (TC-217 board part) | `test_board_p1.py` + power check | inspection by script | R22 pads on VBUS / VBUS_IC; main path >= 0.6 mm; drop reported |
| No via-in-pad | `test_pcb_fabcheck.py` + `ci_hw.sh` | unit + board | `via_in_smd_pad` = 0 on board-p1 |
| Gate (TC-209) | strict DRC `stitched-4l`, strict ERC `full` | tool | only the tolerated classes of 4.3 |
| Fab minimum | `pcb_fabcheck.py` | tool | PASS against ADR-0020 numbers (unaccepted input, dated 2026-11-08) |
| Order files (TC-208 part) | `test_fab_check.py` | unit | rules of 4.5 |
| Panel | KiKit run + `fab_check.py` | tool | 1 board; 3 rail fiducials; CPL inside the panel |

Bench-access table (TC-210, TC-217; probe points on P1): VBUS (J1 VBUS pad or TVS1 pin 1), VBUS_IC (R22 pin 2 or C2 pin 1),
+5V (TP1), 3V3 (TP2), GND (TP3), ILIM node (R_ILIM1 pin 1), ILIM_STEP2_EN and ILIM_STEP3_EN (R18 and R19 pin 1),
HOLD_OK (R6 pin 2), GATE_OK_RB and GPIO21 (module pads; R15 pin 2), supply pins of U1, U14, U15 (C26, C24, C25 pin 1),
FAULT_N (R8 pin 2). All are on part pads of the top side; no extra test point is added (one-sided density).

Not run tonight, by design: JLCPCB DFM and Economic rules, LCSC stock and price, the CPL rotation preview, GitHub Actions,
bench, antenna, thermal.

Order-time checklist for the owner (in the report): **O0** order only from a published tagged release; **O1** Economic PCBA
rules (one side, 4 layers, board size, panel acceptance); **O2** LCSC numbers and stock for every BOM line, including R22
(0 ohm 1206, [3] A, [10] mohm) and the 27.7 k 0805; **O3** JLCPCB DFM viewer on the Gerbers; **O4** CPL rotations in the
preview; **O5** HASL lead-free, 1.6 mm, 4 layers; **O6** price within EUR 100; **O7** bring-up: visual polarity and presence check (U5,
U7, U14, U15, DZ*, LEDs), first power from a current-limited lab supply at the J1 VBUS pin, step 1 measured before any USB source
(ADR-0021); **O8** buy J1 (GCT USB4085-GF-A) separately and hand-solder it.

## 7. Risks and open questions
- R1 (likely) one side does not route at 0.15 mm on 46 mm: the owner decides between 0.1 mm (b3 data), growth (MECH-001) or the
  two-sided board with Standard PCBA.
- R2 HASL on the X2QFN-12 (U1): bridges or opens; owner choice; RISK entry; ENIG is the order-time fallback.
- R3 Economic PCBA may refuse 4 layers or the panel: O1; Standard one-sided is the fallback.
- R4 T1 changes a safety-relevant value: only through its test, recorded for the owner to confirm.
- R5 LED bypass capacitors on the top side near the light path; diffuser 8 mm away; shadows not shown.
- R6 Budget: about 12 extended part types; price not read.
- R7 The 0 ohm jumper may not meet HW-017's bracketed [10] mohm / [3] A (A8).
- R8 The U9 courtyard waiver (max 14, refs U9) may block the gate with all parts on top (4.3).
- R9 Seven part types have no LCSC number (A8); a missing U5 defeats the hold-off.
- R10 HW-010 and HW-015 texts name VBUS_IC where the connector side is now VBUS (TVS1 clamp, supply pins); text updates are
  drafted as Proposed for the owner, not changed.
- R11 The housing models disagree (post azimuths 30/150/270 in `mech_outline.py`, 60/180/300 in `housing_params.py`); FreeCAD is
  not installed here, so no housing check runs tonight (no growth, A4).
- Not done, with reasons: a CPL rotation table (it would be invented without JLCPCB's data; O4 instead); a minimum-distance
  placement rule (the placer has none).
- Open for the owner: LED bypass capacitor count; hold-off capacitor count; T2 (and the correction of
  `analysis-supply-pin-surge.md` open point 4, which RV-014 shows is not fail-safe); SYS-022 against the hand-soldered J1;
  ADR-0020 revision for 0.15 mm; via 0.7 / 0.3 mm (ring 0.2 mm) profile; A9 (ADR-0012 G1); ruff and CI for the spike code
  before it makes production files.

## 8. Rollout / rollback and traceability
IDs: HW-008, HW-009, HW-010 (T1 amendment), HW-016, HW-017, ADR-0021, ADR-0020 (Proposed), new RISK and DEV entries, TC-208,
TC-216, TC-217, RV-014. Rollback: `board/` stays (frozen at `1d2a1a6` sources); `P1` unset gives the old placement rules; T1 and
the HW-017 split are separate commits.
