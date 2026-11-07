# Spike: PCB placement and routing of the full board

Status: spike result, exploratory. It is not a product design and nothing here is approved. ADR-0012 is Proposed, so the PCB flow it describes is not decided, and nothing from this spike merges before the owner decides it. No compliance claim is made.
Traces: HW-010 (Draft proposal), HW-003, ADR-0016, ADR-0012 (Proposed), ADR-0010, SW-009 (proposed readback rule), RISK-042.
Implementation (spike branch `spike/hw-gate`, `hw/kicad/spike-gate/`): `src/pcb_full.py` (placed board), `src/route_grid.py` (router), `src/pcb_check.py`, `src/pcb_dsn.py`, `src/pcb_rules.py`, `run_pcb.sh`, `tests/test_pcb_full.py`, `tests/data/full.net` (netlist of the final full-board sheet).
Rebuild: run `run_full.sh <python> <dir>` for the schematic, then `sh run_pcb.sh <dir> <out>` with the system `python3` (KiCad 10.0.6 `pcbnew`, numpy 2.5.3, scipy 1.18.1, Python 3.14). The `.kicad_pcb` and `.kicad_pro` files are written by script into `<out>/a/` and are not committed, the same rule as the schematic spike. Nothing in them was edited by hand.

**Update (second run, same day):** section 10 adds the mechanical outline from the FreeCAD spike, Freerouting v2.5.0 and the 2-layer against 4-layer comparison. Where sections 1 to 9 differ from section 10 (outline, placement, router, widths), section 10 is the newer result. Sections 1 to 9 describe the first run on a provisional 136 x 64 mm rectangle with the own grid router; they are kept as the record of that run.

## 1. Result in numbers (run of 2026-11-05, final code)

| Item | Result |
|---|---|
| Parts placed | 86 of 86 refs of the netlist (plus 3 provisional mounting holes H1 to H3); no missing and no extra refs |
| Nets | 63 in the netlist (53 named, 10 `unconnected-*`); 63 on the board; 0 pad-to-net differences against the netlist (`pcb_check.py`) |
| Connections to route (excluding GND) | 141; routed 138, **not routed 3** (see section 5) |
| GND | back-layer pour plus a via for every SMD GND pad; **5 GND items stay unconnected** in the KiCad DRC |
| Tracks / vias | 884 track segments, 225 vias, 1646 mm of copper track, router time about 95 s |
| KiCad DRC (`kicad-cli pcb drc`, zones refilled) | **errors: 4 clearance, 8 unconnected items**; warnings: 86 `lib_footprint_issues`, 15 `silk_over_copper`, 1 `hole_to_hole`, 1 `connection_width`, 1 `via_dangling` |
| KiCad schematic parity | 100 warnings, all explained in section 4 (U1, U8, U9 pin names, four substituted capacitor footprints, three holes) |
| Placement build twice | byte-identical (`run_pcb.sh`, uuids normalised) |
| Routing run twice | byte-identical (`cmp` exit 0) |
| Unit tests | `tests/test_pcb_full.py`: 11 tests, all pass under system `python3` (skipped without `pcbnew`) |

The 4 clearance errors: two between a VBUS_IC track and pad 4 (`USB_DP`) of U6 (actual 0.125 mm, rule 0.150 mm) and two between a `+3V3` track and a `CC_OK_NOT_S3` track (actual 0.147 mm, rule 0.150 mm). The board does **not** pass DRC.

## 2. Tools and why

| Tool | Use | Status |
|---|---|---|
| KiCad 10.0.6 `pcbnew` Python | writes the board from the netlist; zone fill; DSN export | used |
| `kicad-cli pcb drc` / `export svg` | DRC with `--schematic-parity --refill-zones`; renders (scratchpad only) | used |
| Own grid router `src/route_grid.py` | A* on a 0.05 mm grid, 2 layers, through vias, Euclidean clearance raster (scipy), neck-down of wide nets, a retry pass | used (fallback) |
| Freerouting v2.5.0 (`freerouting-2.5.0.jar`, GitHub release) | the router I preferred | **not run**: see below |

**Freerouting was not run.** I tried to download the pinned jar into `~/Programming/busy-light-tools/` (outside the repository) and the permission layer of this session refused the download-and-execute action ("Code from External"). I did not work around the refusal. No version hash is recorded because no file was fetched. What exists: `src/pcb_dsn.py export` writes a Specctra DSN from the placed board (tested: it writes 63 nets with the net-class rules, 50 KB), and `pcb_dsn.py import` reads an SES back, refills zones and saves. The import path is **untested**. To use Freerouting the owner can allow the download or run `java -jar freerouting-2.5.0.jar -de x.dsn -do x.ses` on the DSN and then `pcb_dsn.py import`. Its result is likely better than mine (my router has no rip-up and re-route, only one retry pass), but that is an expectation, not evidence.

## 3. Board and placement decisions (all provisional)

- **Layers: 2.** Reasons from the earlier reports: the USB path carries 1.5 A (limit 1.38 to 1.58 A, step 3 up to 2 A worst case), which needs about 0.53 mm (1.5 A) and 0.78 mm (2.0 A) width at 1 oz and a 10 K rise (IPC-2221 curve fit, test `Rules`); the high-impedance ILIM node must stay short; USB 2.0 full speed needs no controlled impedance. The ESP32-C3 antenna wants no copper under or beside it, which a 2-layer board with one GND pour can honour. The cost is that routing is congested (many vias). A 4-layer stack would give an inner GND plane and is the likely answer if Freerouting results are also poor. No stack-up or fabricator rule was checked.
- **Outline 136 x 64 mm**: electronics zone x < 64 mm, 16 WS2812B LEDs in 2 rows of 8 at 8.5 mm pitch with a 100 nF capacitor each, 3 mounting holes M3. Mechanics, LED count and peg azimuth are open, so this outline has no basis in the mechanical design.
- **Rules:** clearance 0.15 mm (the J1 pad gap is 0.15 mm), signal track 0.2 mm (0.15 mm on nets at the 0.4 mm-pitch pads of U1), via 0.6/0.3 mm, copper-to-edge 0.3 mm, hole-to-hole 0.4 mm (relaxed from 0.5 mm because J1's through-hole pads are 0.85 mm apart with 0.4 mm drills). Whether a fabricator accepts these was **not checked**.
- **Placement by rule** (coordinates in `PLACE` in `pcb_full.py`): USB-C J1 with its mating face at the left edge; TVS and ESD parts beside J1; CC IC U1 at J1's CC pads; gate logic cluster in the middle; Q2, Q3, R2, R3 and the three ILIM resistors in a group next to U7 (ILIM parts within 15 mm of U7, tested); U5 with C1 and C1B beside it; the module U9 with its antenna end flush with the top edge and no other pad in its keep-out band (tested); LED field on the right. The placement was adjusted by hand-chosen coordinates and one iteration, not optimised: the render shows long runs.

## 4. Footprints: substitutions and gaps (all PROVISIONAL)

| Ref | Schematic footprint | Used | Why / what to check |
|---|---|---|---|
| U1 TUSB321 | `Package_X2QFN:X2QFN-12` | custom 12-pad footprint made in `pcb_full.py` | The system KiCad libraries have no `Package_X2QFN`. The geometry was read from a **text extract** of TI drawing RWB0012A (1.6 x 1.6 mm, 0.2 mm pads, 0.5 and 0.4 mm pitch). It may be wrong; take the land pattern from the TI drawing before any use. Pad numbers: CC1 1, CC2 2, PORT 4, VBUS_DET 5, GND 10, VDD 12 (datasheet pin table). |
| U9 ESP32-C3-MINI-1 | `RF_Module:ESP32-C3-MINI-1` | `RF_Module:ESP32-C6-MINI-1` | The C3 footprint is not in the libraries. Pad positions of the C6 footprint match the C3 pin diagram (pins 1 to 53, antenna to the top, corner pads 50 to 53), but I did not compare dimensions to datasheet figure 11-1. Its antenna keep-out zone (43 x 20 mm) comes with the footprint. Pad numbers from the C3 datasheet v2.2 table 3-1. |
| U8 REG_3V3 | empty (placeholder) | `SOT-223-3_TabPin2` | No regulator is chosen. Pin map GND 1, OUT 2, IN 3 is an AMS1117-style assumption. A 5 V to 3.3 V linear regulator at the module's peak current dissipates real heat; no thermal analysis was done. |
| C1, C1B | `C_0603` in the sheet | `C_1206` | The 470 nF and 150 nF C0G parts of the N4 addendum are 1206 (the sheet still draws 0603 for them: a schematic follow-up). |
| C3, C4 | `C_0603` | `C_0805`, `C_1206` | 10 uF and bulk values are "tbd"; sizes are guesses. |

Schematic pin names for U1, U8, U9 are names, not pad numbers (the box symbols of the full-board sheet are placeholders), so the generator maps them (`PADMAP`). KiCad's parity check therefore reports 84 `net_conflict` warnings on those three parts. The 13 `footprint_symbol_mismatch` warnings are the substitutions above plus six test points (BOM-exclusion attribute); 3 `extra_footprint` are the mounting holes. All 80 other refs are parity-clean.

## 5. What is not done or not good

- **3 connections are not routed:** `/CC1` and `/CC2` (J1 A5/B5 to U1 pads 1 and 2) and `Net-(U9-GPIO9_(boot))` (U9 pin 23 to TP6). The CC lines are exactly the nets the CC IC depends on (HW-010, HW-003), so the gate is **not** a complete design until they are routed. Likely cause: pads 1 and 2 of my guessed U1 land pattern are 0.4 mm apart with tight neighbours, and the router has no rip-up. I did not diagnose it further.
- **5 GND items unconnected** (U1 pad 10, U2 pad 3, U9 pad 49 and two via stubs): GND stub-and-via pieces that the back pour cannot reach, probably islands cut off by back-layer signal tracks.
- **4 clearance errors** (section 1). The router's raster is conservative but not exact; the DRC is the judge.
- **Layout quality is poor.** The render shows long and winding wide power tracks and 225 vias (about 80 for LED and capacitor GND alone). Track lengths: VBUS_IC 94 mm, +5V 243 mm, +3V3 148 mm. A person would place and route this more tightly.
- **Wide power tracks:** VBUS_IC is routed at 0.8 mm for 75 % of its length and +5V for 67 %; elsewhere it necks down to 0.25 mm near pads (the rest of the 1.5 A path is below the 0.53 mm that IPC-2221 gives, which is a finding, not a pass). +3V3 is meant to be 0.4 mm and is 0.25 mm in places.
- **Thermal relief:** only the zone's thermal spokes on the GND pour. No thermal vias or copper area for the TPS2553 or the regulator.
- **86 `lib_footprint_issues` warnings** mean the footprint libraries are not in a project library table; they say nothing about the layout. **15 silkscreen warnings** and one `hole_to_hole` (J1) were left open.

## 6. Layout rules from the earlier reports: what was measured

| Rule | Result |
|---|---|
| R3 and the U13 tap at the Q3 gate pin | `/ILIM_STEP3_EN` is routed as a star centred on Q3 pad 1 (every pad of the net, U4, U13, R3, R15, goes straight to that pad; 34 mm of track in total). R3 sits 5.7 mm from Q3. Tested only as placement and star setting, not by inspecting every spoke. |
| ILIM resistors near U7, short ILIM trace | R_ILIM1 to 3 within 15 mm of U7; the `/ILIM` net is 16.4 mm of track. "Away from switching nodes" was not analysed. |
| CC lines per the CC IC | **not met**: `/CC1` and `/CC2` are unrouted. |
| Wide VBUS | partly (section 5). |
| Antenna keep-out | no other pad in the band (test); no DRC error inside the rule area. Whether the pour and tracks respect the **real** C3 keep-out was not checked (the zone comes from the C6 footprint). |

## 7. Determinism

- Placement build: two builds are byte-identical (item uuids are set from a fixed seed, then normalised; checked in `run_pcb.sh` and in `test_two_builds_are_identical`).
- Routing: the router uses no random numbers, a fixed net order and fixed tie-breaks. A second routing run on the same placed board gave a byte-identical `.kicad_pcb` (`cmp` exit 0). This holds for this code, machine and KiCad version only. Freerouting, if used, would need its own seed recorded.

## 8. Not run

No signal-integrity, EMC, antenna or thermal analysis. No fabricator DFM check (JLCPCB capabilities, via and annular ring, solder-mask bridges, paste). No 3D or mechanical fit (connector overhang, LED peg positions, mounting holes). No stack-up study, no 4-layer comparison. No Freerouting run. No SPICE. No bench. The footprint substitutions in section 4 need datasheet verification (TUSB321 land pattern, ESP32-C3-MINI-1 land pattern, regulator). Nothing here shows the board is correct, only how far a script-generated layout got.

## 9. Owner items

- Allow the Freerouting download (or run it) and compare with this router; decide 2 or 4 layers from that result.
- Provide a mechanical outline (LED count, peg azimuth, connector position) before a real placement.
- Pick the regulator and confirm the TUSB321 and module land patterns from the datasheets.
- ADR-0012 decides whether this flow is used at all.

## 10. Second run (2026-11-05): mechanical outline, Freerouting, 2 layers against 4 layers

Spike result, exploratory, nothing approved. Code: `src/mech_outline.py` (the mech table with sources), `src/pcb_place.py` (annealing placer), `src/pcb_full.py` (board), `src/pcb_dsn.py` (DSN export, SES import), `src/pcb_stitch.py` (plane vias), `run_pcb.sh`, tests `tests/test_mech_outline.py` (8) and `tests/test_pcb_full.py` (18, need pcbnew). Rebuild: `FREEROUTING_JAR=<jar> sh run_pcb.sh <run_full dir> <out dir> [2|4]`.

### 10.1 Where the outline comes from (all numbers are from a concept spike, not from an Approved design)
Source: branch `spike/mech-concept`, commit `deb9a5c`, file `mech/freecad/busy_light_housing.py` (parameter block) and `docs/verification/reports/mech-spike-model.md` (sections 4 to 6) on that branch. The FCStd files in `.claude/worktrees/agent-ac020049007f58faf/mech/` (V1, V2-posts, V2-pocket) were generated by that script and were not opened with FreeCAD; the script is the source. `spike/mech-back-layout` holds only a 2D back-layout check and gave no PCB numbers. MECH requirements and plan 05 are Draft, ADR-0011 is the concept basis, and the report says "No variant is chosen (HW-005, ADR-0003)".

| Item | Value | Source (script parameter / report) |
|---|---|---|
| PCB disc | D 46.0 mm, 1.6 mm thick | `D_PCB`, `T_PCB` |
| LED ring | 16 LEDs on D 40.0 mm, first LED at 3.75 deg, pitch 22.5 deg | `N_LED`, `D_RING`; `LED_PHASE` is an ASSUMPTION of the mech spike (HW-001 gives no phase) |
| Poka-yoke notch | R 1.5 mm in the edge at 90 deg | `NOTCH_R`, `NOTCH_AZ` |
| Holding | three base posts with edge pegs and hook lugs at 30, 150, 270 deg (post R 20 to 22, 4 mm wide; hook overlaps the PCB top by 0.6 mm); no mounting holes | `POST_AZ`, `R_POST`, `POST_RAD`, `POST_TANG`, `HOOK_OVERLAP` |
| Space under the PCB | 3.0 mm (PCB underside at Z 5.0, floor 2.0) | `Z_PCB_BOT`, `T_FLOOR` |
| Module | 16.6 x 13.2 x 2.4 mm at the board centre, offset 1.0 mm towards azimuth 0, antenna strip 5.4 mm towards -X | `MOD_*` |
| Vendor antenna zone | 15 mm | `ANT_KEEPOUT` (plan 05 section 4.6) |
| USB-C (variant V1) | PCB tab at azimuth 0, 12 mm wide, to R 29.0 (placeholder); receptacle body R 22.5 to 29.85 on the top side (placeholder 7.35 x 8.94 mm) | `V1_TAB_W`, `V1_TAB_R`, `V1_USB_R0`, `USB_L`, `USB_W` |
| Button | side-actuated tact switch at the edge at 240 deg (placeholder body) | `BTN_AZ`, `BTN_BODY_*` |
| Housing limit | largest dimension 58 mm; the V1 model gives 57.43 mm | `MAX_DIM_MECH001`; report 4.1 |

**Variant choice: V1.** It is the only one of the three that passes all 41 checks of the mech report and keeps one-side assembly (SYS-022). Alternatives, not used: V0 (receptacle on the LED side at the board edge) fails its interference check in the mech report; V2-pocket and V2-posts put the receptacle on the PCB underside at azimuth 0 without a tab (plain D 46 disc), conflict with SYS-022 and need a window open through the floor edge, and V2-posts raises the housing by 0.56 mm. V2 would give a plain circular outline and free the top side, so it is worth a second spike if V1 stays infeasible.

### 10.2 Conflicts between the mech placeholders and the real parts of the schematic
The board uses the real footprints of the schematic. Each item is a finding for the owner, not a fix I may decide.
- **Receptacle depth.** The mech spike puts the mouth at R 29.85. With the real WS2812B 5 x 5 pads (reach R 22.3) and the J1 footprint (rear pad edge 9.5 mm behind the mouth) the rear pads of J1 overlap D1 and D16. The generator moves J1 out until the rear pad edge clears the LED pads by 0.45 mm: mouth at R 32.19 mm, tab to R 31.34 mm. Largest housing dimension then about **59.8 mm, above the 58 mm limit (MECH-001)** by 1.8 mm. Open: smaller LEDs or receptacle, a shifted LED phase, a larger limit, or variant V2.
- **LED size.** The mech model uses a 2 mm placeholder LED (corner at R 21.02). The 5 x 5 mm WS2812B reaches R 22.7, which leaves 0.3 mm or less to the edge, overlaps the hook lug areas (DRC `items_not_allowed`: D2 in the hook 30 area, D7 and D8 in hook 150, D13 in hook 270) and puts D5 against the notch (pad 4 of D5 touches the edge, 0.000 mm clearance). Neighbouring LED courtyards overlap (D8/D9, 7.85 mm pitch).
- **Button.** The schematic has a top-actuated TL3342; the mech model has a side-actuated switch at the edge. SW1 is placed inside the ring at R 13, 240 deg. A side-actuated part is needed for the housing hole at the wall.
- **Antenna keep-out.** The vendor zone of 15 mm beyond the module end is not met: the LED ring is 10.16 mm from the antenna edge (mech report 5, "a PCB matter, ADR-0003"). The board keeps only the module's antenna strip (5.4 x 13.2 mm) free of copper and parts on all layers, as a rule area. The module footprint's own 43 x 20 mm keep-out was removed from the board because it would cover half of the PCB. No RF analysis was done.
- **Receptacle on the LED side.** J1 is on the top side at the tab, outside the ring.
- Mech V2 and the posts: the bottom side has 3.0 mm of height, so bottom-side parts must be lower than about 2.5 mm; the footprint heights were not checked.

### 10.3 Placement
- LEDs D1 to D16 on the top side at R 20, azimuth 3.75 deg + k x 22.5 deg, with the footprint rotated so that DOUT of one LED faces DIN of the next. Bypass caps C8 to C23 on the bottom side under the LEDs; the caps of D2 and D13 are moved 2.5 mm tangentially to clear the base posts.
- Module U9 at the centre (offset 1.0 mm), antenna to -X. J1 on the tab. SW1 inside the ring.
- The other 51 parts: a simulated-annealing placer (`pcb_place.py`, seeded, half-perimeter wire length plus overlap penalty, parts may sit on either side) in the region R <= 16.6 mm, outside the module and the antenna strip; on the bottom side also on the tab. Result: no overlapping parts (pad extent plus margin), wire length 474.8 mm (HPWL), seed 1, 160 000 moves, about 7 s. Test points go to the bottom side.
- Determinism: two builds in one process and builds under three different `PYTHONHASHSEED` values give the same file (checked by `sha256`, the first run showed that sets in the cost sum made the result depend on the hash seed; fixed by sorting). The earlier routing runs `m2` to `m5` and `n2`, `n4` in the scratchpad were made before this fix; the numbers in 10.5 are from runs `f2` and `f4` on the final code.
- Both layers carry GND (2 layers: pours on F and B) or GND on In1 and +5V on In2 (4 layers).

### 10.4 Freerouting settings
Freerouting v2.5.0 (release 2026-10-05), jar `freerouting-2.5.0.jar`, sha256 `f6f51bb02245e8e717f9359bd260cc9c5c0b1bc0acc8b7cb2cd5b8ffeb5de3c7`, downloaded with `gh release download` from the official GitHub releases (not committed). Java 27 (OpenJDK). Command: `java -jar freerouting-2.5.0.jar -de b.dsn -do b.ses -mp 60 -mt 4`, defaults otherwise (greedy optimiser, which only runs on a fully routed board). DSN from `pcbnew.ExportSpecctraDSN`; SES imported with `pcbnew.ImportSpecctraSES`, then the zones are filled. Net classes: VBUS_IC and +5V 0.6 mm, +3V3 0.4 mm, default 0.2 mm, clearance 0.15 mm, via 0.6/0.3 mm. Freerouting is not seeded in a way I controlled; the runs `n2` and `f2` (2 layers, planes F and B, 0.6 mm) gave 19 and 31 unrouted connections from different placements, so a second run can differ.
Freerouting treats a net with a pour as a plane net and writes no vias for it. `pcb_stitch.py` adds a via and a short track at each pad of GND or +5V that the DRC reports as unconnected (clearance-checked against pads, tracks, vias, edge and the antenna strip); module ground pads may take a via in the pad. Vias in pads need filled or capped vias at the fabricator (not checked).

### 10.5 Results (runs f2 and f4, final code)
| | 2 layers (planes F and B) | 4 layers (In1 GND, In2 +5V) |
|---|---|---|
| Freerouting, unrouted connections at the end of 60 passes | 31 (173.6 s) | 39 (185.8 s) |
| After import and plane vias: DRC unconnected items | 106: GND 38, +5V 35, VBUS_IC 12, +3V3 11, LED_DATA 2, SEL_STEP2_GPIO 2 | 57: GND 49, +5V 3, ILIM_STEP3_EN 1, CC_OK_NOT_S3 1, CC_OK_1A5 1, U9 GPIO2 strap 1 |
| DRC violations that are not courtyard, silk or library warnings | starved_thermal 7, track_width 4 (0.12 mm tracks, minimum 0.15), copper_edge_clearance 2, pth_inside_courtyard 1, items_not_allowed 5, via_dangling 37 | copper_edge_clearance 2, pth_inside_courtyard 1, items_not_allowed 5, hole_to_hole 1, via_dangling 5 |
| Clearance and short errors | none reported | none reported |
| Courtyard overlaps | 51 (origin not analysed; includes the module's library courtyard) | 51 |
| Vias / track length | 72 / 523 mm | 143 / 693 mm |
| VBUS_IC (1.5 A path) | 8.6 mm routed, 12 connections unrouted | 83.1 mm, all connections routed; 77.2 mm at 0.6 mm and 5.9 mm (7 %) at 0.2 to 0.45 mm near pads |
| CC1 / CC2 | routed, 8.6 / 11.4 mm | routed, 8.0 / 11.5 mm |
| ILIM net | 14.8 mm | 11.7 mm |
| Gate star at the Q3 gate | `/ILIM_STEP3_EN` routed, 15.3 mm | one connection unrouted, 14.7 mm routed |
| Net comparison against the schematic netlist | 0 pad-net differences, 86 of 86 refs | same |
Reading: neither board is DRC clean and neither is fully routed. The 4-layer board routes the signals, the CC lines and the whole VBUS_IC path; its remaining unconnected items are mostly ground: 49 GND items, of which 22 are module ground pads that could not get a via (dense pads, antenna strip) plus pads in tight areas. The `via_dangling` count of the 2-layer board (37) comes from stitching vias that reach no second copper. Earlier runs on an older placement: 2 layers with planes on F and B at 0.8 mm VBUS width 31 unrouted; plane on B only 53; no planes, 4 layers, 48; 4 layers with planes, 0.8 mm, 40; 2 layers at 0.6 mm 19 (the last on the placement before the determinism fix).

### 10.6 Layer decision (owner rule: try 2 layers first, 4 layers only if 2 layers is really hard or infeasible)
Evidence for the switch, with the 2-layer result kept alongside:
- Freerouting could not complete 2 layers in any of four runs (31, 53, 19 and 31 unrouted connections; each run started with 143 unrouted nets and had at most 40 to 60 passes); 0 violations by its own checker, but unconnected.
- The VBUS_IC path at 0.6 mm stays unrouted on 2 layers (12 to 13 connections), the 1.5 A width rule cannot be met there. It is routed on 4 layers.
- The ground return cannot be made a plane on 2 layers because parts sit on both sides and the pour is cut up (7 starved thermal connections, 38 GND items unconnected).
- Contributing causes, not proven separately: movable parts limited to R 16.6 mm inside the ring, 51 parts on two sides, a 16-LED +5V ring, the antenna strip, and a 5 x 5 mm LED ring on a 46 mm board.
On this evidence I took the 4-layer result as the spike's main result. This is a spike decision for the owner to confirm; a 4-layer board changes cost (HW costs, SYS-021) and needs ADR-0012 to cover it.

### 10.7 Comparison with the own grid router
Not run on the new board: `src/route_grid.py` knows only the old rectangular outline (it stays in the repository, untouched, as the record of the first run). Its first-run numbers (138 of 141 connections on the 136 x 64 mm rectangle, 225 vias) are not comparable with the numbers above. Freerouting finished 2 layers with more unrouted connections than the grid router left on the rectangle, but on a board with about a fifth of the area (about 1700 mm2 against 8700 mm2).

### 10.8 Weak points of the first run: status
- **CC lines:** routed on both variants (8 to 11.5 mm each). The lengths are not matched or shielded; Rd/CC rules from the CC IC datasheet were not applied.
- **VBUS width:** 0.6 mm at 1.0 oz external, 10 K rise. The highest current limit in the top step is 1577 mA (E192 0.1 % set); IPC-2221 gives 0.56 mm for 1.577 A (0.53 mm for 1.5 A, 0.78 mm for 2.0 A). The router necks the track to 0.2 to 0.45 mm for 5.9 mm in total at pad exits on the 4-layer board; the rule is not met for those parts. Not checked: the TPS2553 and connector pad neck-down against the thermal limit.
- **Thermal relief:** the TPS2553 and the regulator have no extra copper area or thermal vias; only the pour spokes. With 3.0 mm free under the PCB and the closed housing the thermal question is open.
- **R3 and the U13 tap at the Q3 gate:** the placer keeps R3 within 6 mm of Q3 (tested); the router does not enforce a star. The ILIM net is 11.7 mm (4 layers).
- **Remaining:** 57 unconnected items and 5 DRC findings on the 4-layer board (LED against hook areas, D5 against the notch, one J1 pad in the D1 courtyard, a via pair at 0.11 mm hole distance), and every conflict of 10.2.

### 10.9 Not run
- No signal-integrity, EMC, antenna, thermal or current-density analysis; no fabricator DFM check (via in pad, 0.12 mm tracks, minimum drill, 4-layer stack-up, impedance); no 3D or housing fit (the FreeCAD model was not opened; footprint heights not checked against the 3.0 mm under-PCB space); no comparison with V0 or V2; no second Freerouting setting study (passes, greedy against global optimiser); no SPICE; no bench.
- The stub vias of `pcb_stitch.py` are a heuristic; 49 GND items stay open.
- The TUSB321 land pattern, the module footprint (C6 library part for the C3 module), the regulator and the placeholder capacitor sizes of the first run are still unverified (section 4).
- No compliance claim. Nothing in this section is approved or accepted.

### 10.10 Owner items
Choose the layer count (the evidence is in 10.5 and 10.6) and whether ADR-0012 covers a 4-layer board. Decide the receptacle conflict (10.2: 59.8 mm against the 58 mm limit; options: smaller LED, shifted LED phase, larger limit, variant V2). Choose a side-actuated button. Decide how to treat the antenna keep-out against the LED ring (ADR-0003). Confirm that Freerouting v2.5.0 may be used in this flow, and the via-in-pad rule for the module ground pads.


## Update 2026-11-07: rerun with the AND gate and the supply-pin protection (HW-010, ADR-0018)
- Command: `run_full.sh`, then `run_pcb.sh <dir> <out> 4 inner` with Freerouting v2.5.0 (pinned jar, KiCad 10.0.6). The placer put the new parts (R_SU1, R_SU14, R_SU15, C26, DZ1, DZ14, DZ15, the AND gate U10) without a change to the placement rules.
- Observed: unplaced-board DRC (4 layers, no router): only `unconnected_items` above the waiver (266 > 241). Routed: Freerouting started with 266 unrouted connections and finished with 48 unrouted and 0 violations in 221 s; M1 (routed board, plane nets excluded) 3 unrouted. Stitched: 247 DRC findings = 46 violations + 86 unconnected items on 4 nets (/CC1, /GATE_OK_RB, GND, one 887 k net) + 110 schematic-parity warnings (84 net_conflict, 26 footprint_symbol_mismatch, the known placeholder and stand-in cases).
- The strict waiver check **fails**: 86 unconnected items, 6 track_width errors, 9 via_dangling warnings and 1 hole_to_hole warning are not on the waiver list. This is worse than the earlier run on unconnected items and has not been analysed. Routing is not deterministic.
- Not done: the net fixture `tests/data/full.net` and the committed DRC fixtures are not refreshed; no manufacturing check; the new parts are not placed with intent (the annealer did it).

## Update 2026-11-07: strict-gate fixes after the AND-gate rerun (HW-010, DEV-006)
- Causes found: Freerouting 2.5.0 writes 0.10 and 0.12 mm wires at tight pads (the SES file has them), so `track_width` failed; it also leaves vias with copper on one layer (`via_dangling`); the stitcher checked every pad against all layers and in sorted order, so a pad never joined a via that its neighbour got later; the stitcher did not check hole-to-hole distance between vias of the same net.
- Changes: default track 0.15 mm (the 0.2 mm default made the router squeeze); dangling vias removed before stitching; stitcher retries in passes and joins existing ground vias with a track on the pad's layer only; via search keeps 0.7 mm centre distance to every via; silk of U9, U2, U4, TVS2 and J1 ignored by a named `.kicad_dru` rule (DEV-006, proposed).
- Observed (run on the full flow, 4 layers, planes `none`, Freerouting 522 s, 34 unrouted in its log; one run, not deterministic): stitched board strict check: `clearance`, `track_width`, `via_dangling`, `hole_to_hole`, `isolated_copper`, silk classes and `lib_footprint_mismatch` all 0; still failing: `unconnected_items` 50 (21 ground pads of the module U9 inside the antenna keep-out, 7 small ground pads, the rest on signal nets the router left open) and `track_dangling` 2 (ends of the open signal nets).
- A via in a U9 ground pad inside the keep-out was tried; it gave 18 `items_not_allowed` and dangling vias (the inner plane has the cut-out), so it was reverted.
- Not run: a second router run; the committed DRC fixtures are not refreshed.

## Update 2026-11-07 (later): antenna strip corrected, slot added (HW-005, ADR-0003, DEV-004)
- Cause of the 21 module ground pads in the strip: the strip was 5.4 mm and the pad area was centred in the module body. The ESP32-C3-MINI-1 datasheet v2.2 (fig 11-1, section 3.1) puts the antenna area beyond the pad rows: 16.6 - 11.2 - 0.8 = 4.6 mm, and the pad area is not centred. The board also uses the ESP32-C6-MINI-1 footprint as a stand-in for the C3 (pad rows 9.8 mm apart, as in the C3 figure; other dimensions not compared).
- Changes: `MOD_ANT_L` 4.6 mm; U9 placed so that its pad area starts at the end of the strip (moved 1.6 mm toward +X); a 1.0 mm slot in Edge.Cuts 1.5 mm beyond the antenna end (owner idea, vendor guide 1.4.7 advises cutting the board around the antenna), with a copper keep-out of 0.5 mm round it because the router does not see Edge.Cuts slots (first run without it: 22 `copper_edge_clearance`); tests for the strip length, the pad position and the slot (pure and pcbnew).
- Observed (one run, Freerouting 177 s, 20 unrouted in its log): stitched board strict check: 0 unconnected ground items, 0 copper-edge, 0 silk, 0 `via_dangling`, 0 `track_width`, 0 `hole_to_hole`; still failing: `unconnected_items` 30 (14 on VBUS_IC, 14 on +3V3, 1 /ILIM_STEP2_EN, 1 /CC_OK_NOT_S3), `clearance` 2 (an In2 track at 0.114 and 0.121 mm from a SUP_CT via), `track_dangling` 1.
- Not done: the slot is not in the housing or the mechanical model (the housing has no part under it; posts and hooks are at 30, 150 and 270 degrees); no RF check that the slot helps; the real C3 footprint (pad sizes) is not drawn; fabricator slot rules not checked (1.0 mm router bit assumed). The STEP model is saved in the datasheet folder; the Autodesk footprint source link of the datasheet returns 404.

## Update 2026-11-07 (last): placement and routing experiments (HW-010, ADR-0012)
All runs: same netlist, 4 layers, Freerouting 2.5.0, KiCad 10.0.6, strict check of the stitched board (`stitched-4l`). Numbers are from single runs.

| Run | Change | Unconnected items | Other strict findings |
|---|---|---|---|
| A | antenna strip 4.6 mm, slot, slot keep-out | 30 | 2 clearance, 1 dangling track |
| B | threads 1, 2, 4 and passes 25 to 150 | 30 each (identical) | same; the router is deterministic here, its settings are exhausted |
| C | +3V3 width 0.4 to 0.3 mm (1.0 A by IPC-2221, TLV757P rating) | 23 | 0 clearance, 5 dangling tracks |
| D | C plus VBUS_IC placement weight 3.0 and `R_MOVE` 16.6 to 17.3 mm (owner choice: loosen the ring) | **14, all VBUS_IC** | 1 clearance, 1 dangling track |
| E | D with VBUS_IC routed first and locked (`KEYFIRST=1`) | 8 (2 GND, 5 USB data, 1 UART RX) | 4 clearance, 3 dangling tracks |
| F | E with the four USB data nets also first | 12 | 11 clearance |
| (earlier) | all 17 key nets first and locked, before the placement change | 56 | 2 `items_not_allowed` |

- Reading: placement was the lever (D); routing order is not: locking the first stage's tracks pushes the failure to other nets (E, F). Neither D nor E is clean.
- The 14 items of D are the pads of VBUS_IC (R_SU1, R_SU14, R_SU15, R_VD, R1, R6, C2, TVS1, U5, U6, U7 and the J1 pins), a net of 10 or more pins that is routed at 0.6 mm everywhere, although only the path J1 to U6 carries the 1.5 A; the branches (supply-pin resistors, divider, TMUX supply) carry microamps. A router class cannot give one net two widths.
- Options that need a decision (not made): (a) a VBUS_IC copper pour on one layer near the connector; (b) a schematic change that names the low-current branches as a separate net behind the main path; (c) narrower tracks on the branches by a post-route step that is not yet written.
- Not done: no commit; the committed DRC fixtures and the README images are not refreshed; no electrical or RF check of the result.

## Update 2026-11-07 (main path split): VBUS_IC routed in two classes (HW-010, ADR-0012)
- Idea: only the path connector J1, TPS2553 input (U7 pin 1), C2 and TVS1 carries the switch current (up to 1.577 A, 0.6 mm by IPC-2221). The other pins of VBUS_IC (supervisor, ESD part, dividers, supply-pin resistors, enable) draw microamps. `run_pcb.sh` with `KEYFIRST=1` routes the main path alone at 0.6 mm (stage 1), locks it, then routes everything else with the VBUS_IC class at `BRANCH_WIDTH` 0.2 mm (stage 2); the branches join the locked main path. No schematic change. Code: `pcb_rules.MAIN_PATH_PADS`, `is_main_path_pad`, `pcb_dsn.py keyonly` and `branchwidth`.
- Observed, one run each (4 layers, planes `inner`, Freerouting 2.5.0; the router is not deterministic with 4 threads):

| Run | Setting | Unconnected | Clearance | Dangling |
|---|---|---|---|---|
| pl4 | planes `none` | 2 | 1 | 0 |
| pl5 | planes `inner` | **3** | **0** | **0** |
| pl6 | `inner`, In1 and In2 as power layers in the DSN | 22 | 3 | 0 |
| pl7 | as pl5 (same settings), after changing the via removal | 7 | 5 | 1 |

  pl5 and pl7 have the same settings; the difference is router variance, not a design change. The best run is not a result that can be repeated on demand.
- Reading: the split removes the VBUS_IC problem (stage 1 routes all main-path nets without an open item; the 14 open VBUS_IC items of the single-pass run are gone). What is left is 2 to 12 mixed findings that change from run to run: ground stubs, /ILIM_STEP2_EN, a few clearance findings at U9 and a via. Marking In1 and In2 as power layers (so that signals stay off the planes) leaves the board unroutable (pl6): this stack needs signals on the inner layers, and the router puts some VBUS_IC and signal tracks on In1 and In2, which cuts the GND plane in places. That is a layout weakness, not checked electrically.
- Via removal: a via that the DRC calls dangling is removed only when no pad is there and its track ends lie on one layer (`pcb_rules.joins_nothing`); the earlier version could remove a layer change.
- Not done: no run is clean; no repeatable result; a post-route cleanup of the leftovers (a small maze router, or hand-placed copper by script) is the next step; the README images and the DRC fixtures are not refreshed; no commit.

## Update 2026-11-07 (clean-up): post-route grid router `pcb_fix.py` (HW-010, ADR-0012)
- Method: after Freerouting and the stitcher, `run_pcb.sh` (`CLEANUP=1`, default) calls `src/pcb_fix.py auto`: up to 3 rounds of (1) remove the track run (up to junctions, vias and pads) at each `clearance` finding, (2) connect every `unconnected_items` pair with a deterministic A* grid router (0.05 mm grid, four layers, through vias; obstacles are the copper of other nets, the board edge, the slot, rule areas and the hole-to-hole distance, grown by the clearance plus half the track width plus 0.06 mm), (3) rip up and reroute a net from its pads when a pair still fails (also with the nearest blocking nets; all or nothing), (4) remove free-ended track pieces and dangling vias, (5) check with the strict DRC. The result is `final.kicad_pcb`. The router is checked only by the KiCad DRC.
- Observed (run pl8: `KEYFIRST=1`, planes `inner`, Freerouting 2.5.0, KiCad 10.0.6; the clean-up itself has no random part): stitched board 5 unconnected items and 135 findings; after the clean-up **1 unconnected item** (/ILIM, U7 pin 5 on the back to R_ILIM3 on the front) and in the strict check only the tolerated known classes: `courtyards_overlap` 14 and `items_not_allowed` 1 (both U9, DEV-004), `footprint_symbol_mismatch`, `net_conflict`, `ignored_checks`. Clearance, track width, hole-to-hole, copper-to-edge, silk (DEV-006), dangling vias and dangling tracks: 0.
- Rerun of the clean-up alone on the same stitched board of pl8: rounds gave 2, 8, 1, 1 open items (the second figure is after the ripup step, before routing).
- Open: the /ILIM connection (pin 5 of the TPS2553 sits in a crowded spot on the back); Freerouting's own output varies from run to run, so the stitched input differs between runs (pl5 to pl8: 3 to 7 open items); the clean-up has been run on pl7 and pl8 only. The inner layers still carry some signal and VBUS_IC tracks (cuts in the GND plane, not checked electrically). Stand-in footprints, antenna arrangement (DEV-004), electrical and RF checks: not done.
- Tests: `tests/test_pcb_fix.py` (6: description parsing, track runs, counts, a real route round a foreign pad on a small board with the clearance checked, a blocked board gives no path); 87 tests pass in the pcb, mech-outline, placement and run-script files.
