# Spike: PCB placement and routing of the full board

Status: spike result, exploratory. It is not a product design and nothing here is approved. ADR-0012 is Proposed, so the PCB flow it describes is not decided, and nothing from this spike merges before the owner decides it. No compliance claim is made.
Traces: HW-010 (Draft proposal), HW-003, ADR-0016, ADR-0012 (Proposed), ADR-0010, SW-009 (proposed readback rule), RISK-042.
Implementation (spike branch `spike/hw-gate`, `hw/kicad/spike-gate/`): `src/pcb_full.py` (placed board), `src/route_grid.py` (router), `src/pcb_check.py`, `src/pcb_dsn.py`, `src/pcb_rules.py`, `run_pcb.sh`, `tests/test_pcb_full.py`, `tests/data/full.net` (netlist of the final full-board sheet).
Rebuild: run `run_full.sh <python> <dir>` for the schematic, then `sh run_pcb.sh <dir> <out>` with the system `python3` (KiCad 10.0.6 `pcbnew`, numpy 2.5.3, scipy 1.18.1, Python 3.14). The `.kicad_pcb` and `.kicad_pro` files are written by script into `<out>/a/` and are not committed, the same rule as the schematic spike. Nothing in them was edited by hand.

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
