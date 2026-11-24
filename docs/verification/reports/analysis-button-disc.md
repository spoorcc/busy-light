# Analysis: centre button, disc statics, light, zone geometry (plan 09 step 1)

Status: Draft. Date: 2026-11-24. Author: Claude (agent). Not reviewed by the owner. Nothing here is Approved or Accepted.
Traces: MECH-004, MECH-002, MECH-003, HW-008 (read for constraints); input to ADR-0026 (Proposed) and `docs/plans/09-centre-button.md`.
Repository revision when the output below was made: `bd59b6c` plus the uncommitted step 1 files. Tools: Python 3.13.18, ruff 0.16.9, standard library only for the scripts.

## 1. What was run

| Script | Test | What it computes |
|---|---|---|
| `mech/analysis/button_disc.py` | `mech/analysis/test_button_disc.py` | rigid disc on linear supports (plane model), S2 and M3 rows of plan 09 section 3.2, bridge stiffness bands, beam, plate, guide formulas |
| `mech/analysis/button_light.py` | `mech/analysis/test_button_light.py` | Lambertian ring sum onto a planar receiver at 8 mm |
| `mech/analysis/check_tolerance.py` (added functions) | `mech/analysis/test_check_tolerance.py` | vertical and lateral button chains (informational, not called by `run()`) |
| `hw/kicad/spike-gate/src/button_zone.py` | `hw/kicad/spike-gate/tests/test_button_zone.py` | outlines from the stored board-p1 text, antenna baseline, S2 pose search, S3 scan, fill |

`button_zone.py` is outside ruff because `pyproject.toml` excludes `hw/kicad/spike-gate` (449 findings at consolidation); this is the exception that plan 09 step 1 asked to record. Its tests run in the spike-gate suite in CI (`pytest` in `hw/kicad/spike-gate`), not in the root pytest. They do not need `pcbnew`.

## 2. Raw output

Disc statics and bands (`python3 -I mech/analysis/button_disc.py`; sampler `random.Random(7)`, 600 points plus the centre plus 48 boundary points, R_use 13 mm):

```
S2: switch at the centre, three bridges at r = 14 mm; press points inside R_use = 13 mm
TL3342F160QG (travel assumed): 1.57 N +- 0.49 N, click travel 0.25 mm, switch 6.3 N/mm
   k = 1 N/mm: F 2.32 to 2.32 N, press-point travel 1.58 mm, lift points 0
   k = 2 N/mm: F 3.07 to 3.07 N, press-point travel 1.13 mm, lift points 0
   k = 3 N/mm: F 3.82 to 3.82 N, press-point travel 0.98 mm, lift points 0
   k = 4 N/mm: F 4.57 to 4.57 N, press-point travel 0.91 mm, lift points 0
   k = 6 N/mm: F 6.07 to 6.07 N, press-point travel 0.83 mm, lift points 0
   band: k from 2.83 to 3.92 N/mm (ratio 1.4)
B3U-1000P: 1.5 N +- 0.49 N, click travel 0.15 mm, switch 10.0 N/mm
   k = 1 N/mm: F 1.95 to 1.95 N, press-point travel 1.27 mm, lift points 0
   k = 2 N/mm: F 2.40 to 2.40 N, press-point travel 0.84 mm, lift points 0
   k = 3 N/mm: F 2.85 to 2.85 N, press-point travel 0.70 mm, lift points 0
   k = 4 N/mm: F 3.30 to 3.30 N, press-point travel 0.62 mm, lift points 0
   k = 6 N/mm: F 4.20 to 4.20 N, press-point travel 0.55 mm, lift points 0
   band: k from 2.20 to 6.69 N/mm (ratio 3.0)
KSC221JLFS: 2.0 N +- 0.5 N, click travel 0.35 mm, switch 5.7 N/mm
   k = 1 N/mm: F 3.05 to 3.05 N, press-point travel 2.10 mm, lift points 0
   k = 2 N/mm: F 4.10 to 4.10 N, press-point travel 1.53 mm, lift points 0
   k = 3 N/mm: F 5.15 to 5.15 N, press-point travel 1.34 mm, lift points 0
   k = 4 N/mm: F 6.20 to 6.20 N, press-point travel 1.24 mm, lift points 0
   k = 6 N/mm: F 8.30 to 8.30 N, press-point travel 1.15 mm, lift points 0
   band: no band (travel limit not met up to 20 N/mm)
B3U-1000P, k = 3 N/mm, pre-travel 0.05 to 0.35 mm (typeset reading): click force 1.46 to 5.14 N against the window (2.0, 5.0)
B3U-1000P, k = 3 N/mm, pre-travel 0.05 to 0.25 mm (text layer reading): click force 1.46 to 4.24 N against the window (2.0, 5.0)
M3: three TL3342 switches at r = 11 mm, rigid disc: F 1.43 to 4.80 N, press-point travel 0.43 mm
```

Light (`python3 -I mech/analysis/button_light.py`):

```
Irradiance relative to the value above an LED (LED at azimuth 0):
  r mm   at an LED azimuth   between two LEDs
     0             0.182             0.182
     5             0.216             0.216
    10             0.352             0.352
    13             0.529             0.528
    15             0.698             0.694
    16             0.792             0.783
    18             0.956             0.928
    20             1.000             0.952
```

Zone geometry (`python3 -I hw/kicad/spike-gate/src/button_zone.py`):

```
U9 body 16.60 x 13.20 mm, SW1 body 6.40 x 5.20 mm, SW1 courtyard 8.50 x 6.00 mm
Stored board: antenna strip to nearest LED centre 5.06 mm
S2: module moved, switch at the centre (0.5 mm and 3 degree grid, rotation 0 to 177):
   TL3342 body 6.4 x 5.2, gap 1.0: 10 poses, best strip to LED 2.51 mm (50 % of 5.06)
   TL3342 courtyard 8.5 x 6.0, gap 0: 58 poses, best strip to LED 3.04 mm (60 % of 5.06)
   B3U body 3.0 x 2.5, gap 1.0: 1330 poses, best strip to LED 3.90 mm (77 % of 5.06)
   B3U body + 0.5 mm each side 4.0 x 3.5, gap 1.0: 428 poses, best strip to LED 3.64 mm (72 % of 5.06)
S3: three switches at r = 11 mm around the stored module:
   TL3342 body 6.4 x 5.2: 7 of 480 feasible, best gap to body 0.33 mm, to strip 0.34 mm
   TL3342 courtyard 8.5 x 6.0: 0 of 480 feasible, best gap to body 0.00 mm, to strip 0.00 mm
   B3U body 3.0 x 2.5: 92 of 480 feasible, best gap to body 1.68 mm, to strip 2.97 mm
Fill of the ring interior (plan 08 A3 figures: 430 mm2 movable, 650 mm2 available, not recomputed):
   today 66 %, S2 with the B3U courtyard (4.0 x 3.5) 63 %,
   S3 with two more TL3342 courtyards 82 %
```

## 3. Reading of the results

- **Switch click values.** TL3342F160QG 1.57 +- 0.49 N (the matrix of plan 09 section 3.2 uses 1.6 N, so its force rows are 0.03 N higher than the 1.57 N rows here); travel assumed 0.25 mm. B3U-1000P 1.50 +- 0.49 N, pre-travel 0.15 +0.2/-0.1 mm. KSC221JLFS 2 +- 0.5 N, travel 0.35 +0.3/-0.1 mm. Sources: `hw/evidence/parts/sw-*.yaml`.
- **S2 with three bridges.** The click force is F = OF + 3 k x at every press point. With the pass rule (window 2 to 5 N with the force tolerance, press-point travel at most 1.0 mm) the band of the bridge stiffness is 2.83 to 3.92 N/mm for the TL3342 (ratio 1.4) and 2.20 to 6.69 N/mm for the B3U (ratio 3.0). The KSC221 has no band: the travel limit is not met up to 20 N/mm.
- **B3U pre-travel tolerance.** At k = 3 N/mm the click force runs from 1.46 to 5.14 N for a pre-travel of 0.05 to 0.35 mm (the typeset table of the Omron catalogue, read from the rendered page on 2026-11-24) and from 1.46 to 4.24 N for 0.05 to 0.25 mm (the PDF text layer, "0.15 +- 0.1"). The window of 2 to 5 N is therefore not met at the extremes in either reading (the lower end is 1.46 N). The click travel must be measured on the real switch (plan 09 step 3).
- **M3** (three TL3342 at r = 11 mm): 1.43 to 4.80 N, press-point travel 0.43 mm; the centre needs 4.80 N, which is the analytic value 3 x 6.4 N/mm x 0.25 mm.
- **Light.** The centre gets 18 % of the value above an LED, r = 13 mm 53 %, r = 15 to 16 mm 70 to 79 % (plan 09 quoted 54 % and 71 to 81 %; this model gives 53 % and 70 to 79 %). The disc is lit by the ring whatever the lid does.
- **Antenna baseline.** Stored board: 5.06 mm from the strip to the nearest LED centre (the `mech_outline` model gives 6.07 mm). S2 with the TL3342 body keeps 2.51 mm (50 %); with the B3U body 3.90 mm (77 %); with the B3U plus 0.5 mm on each side 3.64 mm (72 %). Pose counts depend on the distance test: this script uses Euclidean polygon distance, a pose conflicts when the distance is below the gap or the shapes touch (gap 0 means no overlap). The earlier scratch search used axis-aligned separation and counted 1,322 and 424 poses for the two B3U cases; this script counts 1,330 and 428 (the best distances agree).
- **Corner radius matters.** For the courtyard case (8.5 x 6.0 mm, gap 0) the module corner limit of 19.5 mm gives 58 poses and 3.04 mm; without the limit 134 poses and 3.57 mm; at 19.0 mm 12 poses and 2.86 mm.
- **S3.** With the TL3342 body 7 of 480 configurations clear the stored module (best gaps 0.33 mm to the body, 0.34 mm to the strip), none with the courtyard. With the B3U body 92 of 480 clear it (gaps 1.68 mm and 2.97 mm), so the S3 fallback is placeable with the B3U; its other costs (three parallel switches, stuck-closed paths, area) remain.
- **Fill of the ring interior** uses the plan 08 A3 figures (430 mm2 of movable courtyards on 650 mm2; not recomputed): 66 % today, 63 % for S2 with the B3U courtyard, 82 % for S3 with two more TL3342 courtyards. The B3U land pattern is not read, so its courtyard (4.0 x 3.5 mm) is body plus 0.5 mm on each side.
- **Arm stress.** A k = 3 N/mm arm of 1.2 x 1.2 mm in E = 1500 MPa needs L = 10.1 mm and sees 53 MPa at a stroke of 1.0 mm (the figure "about 40 MPa" in earlier revisions of the plan had no stated length; 40 MPa needs L = 11.6 mm). PETG yield, creep and fatigue are not analysed.
- **Tolerance chains** (assumed values in `check_tolerance.py`, informational): vertical +-1.31 mm worst case, +-0.58 mm RSS; lateral +-3.05 mm worst case, +-2.04 mm RSS (the board-to-wall gap dominates). The worst-case recess of a nominal 0.3 mm recess is -0.20 mm: the disc can stand proud by design of these numbers, which is why the chains are not a CI gate.

## 4. Issues found, no file changed

1. `POST_AZ` 30/150/270 degrees in `hw/kicad/spike-gate/src/mech_outline.py` and `POST_DEG` 60/180/300 degrees in `mech/analysis/housing_params.py` describe the three post azimuths differently. Which one is current is not decided here; plan 08 revision 6 must settle it before the keep-outs are placed.
2. Two module models exist: the stored board-p1 footprint (strip 5.06 mm from the nearest LED) and `mech_outline` with `MOD_OFF` -4.0 mm (6.07 mm). The step 1 tests pin both numbers.
3. `test_button_zone.py` pins the stored board-p1 (SW1, U9 at (37.6, 40)). Plan 08 revision 6 re-places the board, so that test is on the step 4 file list.
4. The TC-310 probe of 4 mm diameter at r = 13 mm reaches r = 15 mm, the disc edge, with no margin against the print tolerance of +-0.3 mm. Plan 09 uses r = 12 mm for the outer ring of the force map.

## 5. Not done

No measurement. No FEM. No coupon. PETG modulus (1500 MPa) is an assumption. The B3U land pattern, plunger size and over-travel are not read. The lateral values `tilt_walk` and the switch height tolerance are assumptions. The traceability, docs-style, reuse and licence checks are run for the commit, not by these scripts.
