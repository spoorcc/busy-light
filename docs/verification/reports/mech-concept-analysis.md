# Mechanical concept analysis: light uniformity, thermal estimate, tolerance stack (desk analysis, not measured)

- **Status:** Draft
- **Date:** 2026-11-04
- **Author:** Claude (analysis for the owner). Analysis only. Nothing was measured. Not reviewed by a goldfish or the owner.
- **Related:** MECH-001, MECH-002, MECH-003, MECH-004, MECH-005, MECH-006, SYS-001, SYS-020, SYS-028, SYS-038, HW-001, HW-005, ADR-0003, ADR-0009, ADR-0011, RISK-005, RISK-011, plan 05 (`docs/plans/05-mechanical-design.md`); power numbers from `spike-7-5-power-budget-paper.md`
- **Script:** reproduced in sections 6 and 7. The source files are kept in the session scratchpad only (`mech/mech_analysis.py`, `mech/adr_scores.py`). Section 8 (2026-11-04) re-runs everything with the resolved dimensions (`mech_analysis_v2.py`, `adr_scores_v2.py`); sections 1 to 7 are the first draft.

## 1. Purpose

Give first numbers for three questions about the 55 mm housing: (a) how far must the diffuser be from the LEDs so that 16 LEDs look like a closed band; (b) how hot does a closed printed housing get at the dissipation that the power budget allows; (c) do the proposed printed dimensions fit with FDM tolerances (PCB in housing, USB-C plug in its window, LED-to-diffuser distance, lid spigot, label facet).
All three are **rough estimates**. Each rests on assumptions that are marked below. None replaces the prototype tests (TC-302, TC-304, TC-305).

## 2. Inputs

Status codes as in the other reports: **read** = I opened the document and read the value in its text or table (PDF text extracted); **snippet** = seen only in a search result; **not found** = looked for, not found; **assumption** = my choice, not from a document.

### 2.1 Light

| ID | Value | Condition | Source | Status |
|----|-------|-----------|--------|--------|
| M1 | 2theta(1/2) = 120 deg | "Half light angle", typ, XL-2020RGBC-SK6812B (2.0 x 2.0 x 0.65 mm) | https://atta.szlcsc.com/upload/public/pdf/source/20250225/502D47C6FF2933F7B2561BD85C0A5986.pdf | read |
| M2 | Beam angle of WS2812C-2020 | The sheet says "large scattering angle" and gives no number | https://akizukidenshi.com/goodsaffix/ws2812c-2020.pdf | not found |
| M3 | Beam angle of SK6812MINI-E | The sheet has a radiation pattern graph and the words "scattering angle"; no number in the text | https://cdn-shop.adafruit.com/product-files/4960/4960_SK6812MINI-E_REV02_EN.pdf | not found (graph only) |
| M4 | Beam angle of SK6812MINI (3535) | no number | https://cdn.shopify.com/s/files/1/0023/2960/8292/files/SK6812-3535LEDMINI.pdf | not found |
| M5 | Height of the XL-2020 package: 0.65 mm | from the power budget report (L14) | spike 7.5 report | read (there) |
| M6 | Height of the WS2812C-2020 package | the mechanical drawing is an image; not read | | not found |
| M7 | Light transmission of natural or translucent PLA or PETG at 0.4 to 1.6 mm | A PLA study says transmittance falls and haze rises with wall thickness and prefers 0.8 mm for lampshades; no percentage found. A PETG study says 0.2 mm layer height gave the best transmittance of 0.1 to 0.3 mm. No data for the filament that will be used | https://bioresources.cnr.ncsu.edu/resources/optical-properties-and-lampshade-design-applications-of-pla-3d-printing-materials/ (search result) | snippet |
| M8 | Eye resolution 1 arcmin (used to say that the LED pitch at 1 m, 25 to 31 arcmin, is resolvable) | general figure | no source read | assumption |
| M9 | Michelson ripple at most 10 % (5 % better) for "no visible points" | my working criterion; MECH-002 has no number | | assumption |

The beam model is a generalised Lambertian source with intensity proportional to cos^m(angle), and m from the half-intensity half angle: 60 deg gives m = 1 (pure Lambertian), 45 deg gives m = 2. Real LED packages differ. The 120 deg figure (M1) belongs to one 2020 part. The parts on the shortlist (ADR-0004) have no number (M2 to M4), so both 60 and 45 deg are shown.

### 2.2 Thermal

| ID | Value | Condition | Source | Status |
|----|-------|-----------|--------|--------|
| T1 | HDT at 0.45 MPa in deg C: PLA 55 (PolyMax PLA), 58.1 to 60 (PolyLite PLA and Pro); PETG 69 (Polymaker PETG), 76 (PolyMax PETG), 78 (PolyLite PETG); ASA 103 (Polymaker ASA) | Polymaker manufacturer table "HDT 0.45 Mpa"; the page does not state the method per product | https://wiki.polymaker.com/polymaker-products/polymaker-filaments/technical-data-at-a-glance | read |
| T2 | Other values in deg C: ASA 102.2 (Xometry generic), 95 (3DXTech, ISO 75), 92 (Purefil, ASTM D648); PETG 65 (Polymaker PETG in a different table), 73 (MakeItFrom, 455 kPa) | differ by brand, test method and orientation | search results for purefil, 3DXTech, Xometry, MakeItFrom | snippet |
| T3 | Which filament the owner uses, its datasheet, its flammability class | | | not found (owner question) |
| T4 | Natural convection h: 5 to 10 W/(m2 K) as a boundary condition; 2 to 4 for vertical surfaces in still air; 4.5 typical still-air value | engineering blogs and forum posts, not a textbook | https://eng-tips.com/threads/rough-estimate-for-temperature-rise-in-an-electronics-box.158079 and other results of the search | snippet |
| T5 | Emissivity of printed plastic 0.9 | typical for plastic surfaces; no source read | | assumption |
| T6 | ESP32-C3-MINI-1 operating ambient: 85 deg C or 105 deg C version | datasheet v2.2, section 6 | https://www.espressif.com/sites/default/files/documentation/esp32-c3-mini-1_datasheet_en.pdf | read |
| T7 | WS2812C-2020 operation junction temperature -25 to +85 deg C | maximum ratings table | WS2812C-2020 datasheet (URL in M2) | read |
| T8 | Highest expected room temperature 35 deg C | MECH-005 mentions "the highest expected room temperature" and gives no value | | assumption (owner question) |
| T9 | Dissipation: 500 mA x 5 V = 2.5 W; 1350 mA x 5 V = 6.75 W (cap [1500] mA minus 10 %); realistic worst case: logic about 352 mA plus 16 LEDs at full white 248 mA (variant A) to 592 mA (variant B) = 600 to 944 mA = 3.0 to 4.7 W | spike 7.5 report sections 4.1 and 8; ADR-0009 | project documents | read (there) |
| T10 | Touch temperature limits for accessible plastic surfaces (EN 62368-1) | | | not found (verify) |

All electrical input is counted as heat in the housing. Light that leaves the housing carries away a small part of it. This is the safe side.

### 2.3 Fit

| ID | Value | Source | Status |
|----|-------|--------|--------|
| F1 | Type-C plug overmold/insulator: width 12.35 mm max, height 6.5 mm max. For cable assemblies only the overmold dimensions are checked | USB-IF Type-C Compliance Document Rev 2.1b (June 2021), Table B-1, https://www.usb.org/sites/default/files/USB%20Type-C_Compliance%20Document_Rev_2_1b_June_2021.pdf | read |
| F2 | Plug shell: width 8.25 +-0.03 mm, thickness 2.40 +-0.03 mm, length 6.65 +-0.10 mm | same table | read |
| F3 | A GitHub project note says an update raised the overmold envelope to 12.85 x 7.0 mm | https://github.com/crimpdeq/crimpdeq-case/pull/7 (the fetched excerpt did not show this number; a search summary did) | snippet, not confirmed |
| F4 | A designer's forum post gives 12.5 mm as the longest overmold that his recessed port tolerates (own requirement, not a standard) | https://forum.digikey.com/t/overmold-size-of-the-usb-c-male-end/70874 | read (one number) |
| F5 | Overmold length behind the plug front on common cables; real overmold shapes | | not found |
| F6 | Receptacle height, depth, position on the PCB; panel cutout of the chosen receptacle | no receptacle chosen yet | not found (hardware) |
| F7 | Failure mode: a receptacle 1.7 mm behind a wall opening of about 11 x 5.4 mm stopped the overmold, so the plug could not mate fully | https://github.com/crimpdeq/crimpdeq-case/pull/7 | read (excerpt) |
| F8 | FDM: realistic tolerances are "a few tenths of a millimetre" on desktop machines; 0.2 to 0.3 mm clearance gives a snug fit; holes come out "fractionally undersized"; recommended minimum wall = 4 x layer height (0.25 mm layer: 1.0 mm); clearance between mating parts follows the layer height (0.010 in layers: 0.010 in clearance) | Stratasys Direct FDM Design Guide (industrial machines; desktop printers are less accurate), https://www.stratasys.com/siteassets/sdm/content---website-storage/design-guides/dg_sdm_fdm_0725a.pdf (text extracted); desktop values from search summaries of printpal, Midlands3D and Wevolver | read (Stratasys), snippet (desktop values) |
| F9 | Heat-set inserts: wall around the insert at least 0.080 in (2.0 mm) beyond the insert outer diameter | Stratasys guide | read |
| F10 | PCB outline and thickness tolerance of the prototype shop | | not found (assumed +-0.15 mm and +-0.16 mm; ask the shop) |
| F11 | Tolerances used in the stack: external size +-0.3 mm, small features and positions +-0.2 mm, on a tuned desktop printer | my choice from the range of the task and F8 | assumption (a calibration coupon decides) |

## 3. Method

(a) **Light.** 16 identical emitters on a circle of diameter D, intensity cos^m. Irradiance on a plane at height h over the LEDs, sampled along the ring circle over one pitch: E = h^(m+1) / (h^2 + r^2)^((m+2)/2), summed over all LEDs, r the distance in the plane. The ripple is the Michelson ratio (Emax - Emin) / (Emax + Emin) of that profile. A diffuser scatters further, so the result is the **ripple before scatter**. The "cones touch" distance d = (chord/2) / tan(half angle) is the lower bound.

(b) **Thermal.** One isothermal outer surface, dT = P / ((h_conv + h_rad) A), with h_rad = eps sigma (Ts^4 - Ta^4) / (Ts - Ta) solved by iteration (eps 0.9) and h_conv 10, 5 and 3 W/(m2 K). Cylinder D 55 x H 28 mm. A = 95.9 cm2 for all faces and 72.1 cm2 with the bottom face excluded (the bottom sits on a desk; this is the pessimistic case and the one used for limits). The result is the **surface** temperature. The air inside, the LED bodies and the module are hotter by an amount that this model does not give. Treat the allowed power as an upper bound.

(c) **Tolerance.** Worst case (WC, sum of absolute tolerances) and RSS (root of the sum of squares). WC is the criterion for fits that must never bind (USB-C window). RSS is shown for information only, because the distribution of FDM errors is not known.

## 4. Results (script output in section 6)

### 4.1 Light uniformity (16 LEDs, ring D 38 to 46 mm)

| Ring D [mm] | Pitch, arc / chord [mm] | Angle at 1 m [arcmin] | "Cones touch" d, 60 deg [mm] | same, 45 deg [mm] |
|-------------|-------------------------|-----------------------|------------------------------|-------------------|
| 38 | 7.46 / 7.41 | 25.5 | 2.14 | 3.71 |
| 40 | 7.85 / 7.80 | 26.8 | 2.25 | 3.90 |
| 46 | 9.03 / 8.97 | 30.9 | 2.59 | 4.49 |

Ripple before scatter, ring D 40 mm (the proposal), by height h of the diffuser over the LED tops:

| h [mm] | 3 | 4 | 5 | 6 | 8 | 10 |
|--------|---|---|---|---|---|----|
| half angle 60 deg | 38.5 % | 19.9 % | 9.8 % | 4.8 % | 1.1 % | 0.2 % |
| half angle 45 deg | 57.2 % | 33.4 % | 18.1 % | 9.4 % | 2.4 % | 0.6 % |

Smallest h for a ripple of at most 10 %: ring D 38 mm: 4.75 mm (60 deg) and 5.75 mm (45 deg); D 40 mm: 5.0 and 6.0 mm; D 46 mm: 5.75 and 7.0 mm.
Radial half width of the lit band on the diffuser at half intensity, h tan(theta), for 60 deg: 6.9 mm (h = 4), 10.4 mm (h = 6), 13.9 mm (h = 8).

Reading:
- The LED pitch (7.5 to 9 mm) is resolvable by eye at 1 m (M8), so a diffuser is needed (MECH-002).
- With no scatter at all, the diffuser must sit about 5 to 6 mm over the LED tops to get a ripple under 10 % on a 40 mm ring. A scattering diffuser relaxes this.
- The same distance widens the lit band to 2 x 7 to 14 mm radially. The ring then looks like a **wide glowing band or a disc**, not a thin ring. The distance is a trade between uniformity and the sharpness of the ring.
- Plan 05 proposes h = [8] mm as the first value (ripple 1 to 2.4 % before scatter, margin for the +-0.86 mm stack) and a coupon test at [4], [6] and [8] mm.
- The beam angles of the shortlisted LEDs are **not found** (M2 to M4). The conclusion rests on M1 (a different part) and on the two assumed angles.

### 4.2 Thermal (rough estimate)

Surface temperature rise for D 55 x H 28 mm, bottom face excluded (A = 72.1 cm2), 25 deg C ambient:

| P [W] | dT at h_conv 10 [K] | at 5 | at 3 |
|-------|---------------------|------|------|
| 0.5 | 4.5 | 6.5 | 8.0 |
| 1.0 | 8.9 | 12.9 | 15.7 |
| 2.0 | 17.4 | 24.9 | 29.9 |
| 2.5 (500 mA at 5 V) | 21.6 | 30.7 | 36.5 |
| 3.0 | 25.7 | 36.2 | 42.9 |
| 4.7 (logic plus 16 LEDs, variant B, full white) | 39.3 | 54.0 | 62.8 |
| 6.75 (1350 mA cap) | 54.7 | 73.4 | 83.9 |

With all faces included (A = 95.9 cm2): 0.5 W gives 3.4 / 4.9 / 6.1 K; 1 W gives 6.7 / 9.8 / 11.9 K; 2 W gives 13.2 / 19.0 / 23.0 K; 3 W gives 19.6 / 27.9 / 33.3 K.

Maximum steady dissipation so that room temperature plus rise stays at least 15 K below the HDT (MECH-005), bottom face excluded, at h_conv 10 / 5 / 3:

| Material (HDT in deg C) | Room 25 deg C | Room 35 deg C (assumed) |
|-------------------------|---------------|-------------------------|
| PLA (55) | 1.71 / 1.17 / 0.96 W | 0.58 / 0.40 / 0.33 W |
| PLA (60) | 2.31 / 1.58 / 1.30 W | 1.17 / 0.81 / 0.67 W |
| PETG (69) | 3.40 / 2.35 / 1.94 W | 2.27 / 1.58 / 1.31 W |
| PETG (78) | 4.53 / 3.16 / 2.61 W | 3.40 / 2.39 / 1.99 W |
| ASA (103) | 7.90 / 5.63 / 4.72 W | 6.77 / 4.86 / 4.09 W |

Reading:
- PLA does not meet MECH-005 at 2.5 W (the 500 mA case) for any assumed convection value, even at 25 deg C. PLA is excluded for the housing.
- PETG meets the margin at 25 deg C for about 1.9 to 4.5 W, but only 1.3 to 3.4 W in a 35 deg C room. At the full 500 mA dissipation (2.5 W) PETG is marginal to failing in a hot room.
- ASA meets the margin over the whole realistic worst case (up to 4.7 W) in a 35 deg C room at h_conv 10 and about 4 W at h_conv 3. At the 6.75 W cap even ASA fails when h_conv is 5 or less.
- The realistic worst case (3.0 to 4.7 W) is below the 6.75 W that the limiter alone allows (SYS-020, 1350 mA). If the firmware limit rises to 1350 mA and the LEDs and Wi-Fi can use it, the housing limit becomes an input to the limit value. This is a new point for SYS-020 and RISK-005, for the owner to decide.
- Average dissipation in normal use (status colours at part brightness, Wi-Fi mostly receiving) is far below these values. Only the test at "full limited power" (MECH-005 acceptance, TC-305) reaches them.
- The analysis supports ASA as the safe material for the base and PETG as an experiment. It does not prove either.

### 4.3 Tolerance stack (working dimensions of plan 05, FDM +-0.3 mm external, +-0.2 mm small features)

| # | Stack | Nominal | Worst case | RSS | Result |
|---|-------|---------|------------|-----|--------|
| 1 | Radial gap from PCB (D 44 +-0.15) to the cylinder wall (inner D 51.8 +-0.3), PCB centred on pegs +-0.3 | 3.90 mm | 3.38 mm | 3.56 mm | no interference |
| 2 | Gap from PCB edge to the inner plane of the label facet (recess 21 x 21 mm, facet 23 mm wide, plane 24.98 mm from the axis, wall 1.6 mm) | 1.38 mm | 0.80 mm | not computed | fits, thin |
| 3 | USB-C window against overmold 12.35 x 6.5 mm; misalignment = receptacle on PCB (+-0.1) + PCB in housing (+-0.3) + window position (+-0.2) | | +-0.60 mm | +-0.37 mm | window 13.2 x 7.3 fails WC; 13.6 x 7.7 fails WC; **14.0 x 8.0 passes WC** |
| 4 | LED-to-diffuser distance (posts, PCB thickness, LED height, lid and base heights); the script ran with 6.0 mm, the tolerances do not depend on the nominal | 6.0 mm in the run | +-0.86 mm | +-0.39 mm | at the proposed [8.0] mm the range is 7.14 to 8.86 mm; ripple over 7.14 to 8.86 mm is 2.1 to 0.6 % at 60 deg and 4.4 to 1.4 % at 45 deg (extra run of the same functions) |
| 5 | Lid/base spigot per-side clearance, each diameter +-0.3 mm | 0.25 / 0.35 / 0.40 mm | -0.05 / +0.05 / +0.10 mm | +0.04 / +0.14 / +0.19 mm | 0.25 mm can interfere; **0.35 mm minimum** |

Reading:
- The USB-C window must be **[14.0] x [8.0] mm** to pass at worst case. The size is driven by the position error of the receptacle on the board, of the board in the housing and of the window, not by the cable. A 14 mm window is large on a 55 mm housing. Tighter PCB location (pegs against the board edge) and a printed funnel in front of the window reduce it. These are design options in plan 05.
- Stack 2 is the thinnest fit. The label facet costs wall room beside the PCB.
- Stack 5 uses +-0.3 mm on each diameter. A calibrated printer with a test coupon reaches a smaller error, and the stack then relaxes.

## 5. What this analysis does not show

- No LED beam angle for the shortlisted parts (M2 to M4), no filament transmission (M7), no scatter model of the diffuser. The light result is an upper bound for ripple and a lower bound for the distance.
- Other heat paths (the USB cable, the desk) are ignored. Inner air and component temperatures are not modelled. The 15 K margin applies to the plastic where it is hottest, near the LEDs and the module, so a measurement is required (TC-305).
- All tolerances are assumptions (F10, F11). The PCB shop value and the printer value are unknown.
- No RF analysis of the antenna. Plan 05 section 4.6 gives the mechanical keep-out and the vendor figure.
- No FEA. Plan 05 says when FEA would be justified.
- Not run: any measurement, any CAD interference check (no CAD exists), any ngspice or thermal solver.

## 6. Script `mech_analysis.py`

Run: `python3 -I mech_analysis.py` (Python 3, standard library only).

```python
#!/usr/bin/env python3
"""busy-light mechanical concept analysis. Analysis only, nothing measured.
Run: python3 -I mech_analysis.py
(a) light uniformity of a 16-LED ring behind a diffuser
(b) rough steady-state thermal estimate of a closed ~55 mm housing
(c) worst-case and RSS tolerance stack (PCB in housing, USB-C plug in window,
    LED-to-diffuser distance, label facet)
All inputs marked SRC=read/snippet/assumption in the report; see INPUTS.
"""
import math

N_LED = 16
# ---------------------------------------------------------------- (a) light
def lambert_order(half_angle_deg):
    """Generalised Lambertian order m for a half-intensity half angle."""
    return -math.log(2.0) / math.log(math.cos(math.radians(half_angle_deg)))

def ring_pitch(d_ring_mm):
    arc = math.pi * d_ring_mm / N_LED
    chord = d_ring_mm * math.sin(math.pi / N_LED)
    return arc, chord

def ring_irradiance_ripple(d_ring, h, m, n_pts=3600):
    """Irradiance on the ring circle at height h above 16 identical emitters
    (cos^m intensity, flat plane): E = h^(m+1)/(h^2+r^2)^((m+2)/2).
    Returns (Michelson ripple, Emax/Emin)."""
    R = d_ring / 2.0
    leds = [(R * math.cos(2 * math.pi * k / N_LED), R * math.sin(2 * math.pi * k / N_LED))
            for k in range(N_LED)]
    emin, emax = 1e99, 0.0
    # one LED pitch is enough by symmetry; sample angles 0..22.5 deg
    for i in range(n_pts + 1):
        a = (2 * math.pi / N_LED) * i / n_pts
        x, y = R * math.cos(a), R * math.sin(a)
        e = 0.0
        for lx, ly in leds:
            r2 = (x - lx) ** 2 + (y - ly) ** 2
            e += h ** (m + 1) / (h * h + r2) ** ((m + 2) / 2.0)
        emin, emax = min(emin, e), max(emax, e)
    return (emax - emin) / (emax + emin), emax / emin

def part_a():
    print("=== (a) LED pitch on the ring ===")
    print("D_ring[mm]  arc pitch[mm]  chord[mm]  angle at 1 m[arcmin]")
    for d in (38, 40, 42, 44, 46):
        arc, ch = ring_pitch(d)
        print(f"{d:9.0f}  {arc:13.2f}  {ch:9.2f}  {ch / 1000.0 * 3437.75:20.1f}")
    print("\nHalf-intensity half angles and the Lambertian order m (cos^m model)")
    for th in (45, 60, 65):
        print(f"  half angle {th} deg (full {2*th} deg): m = {lambert_order(th):.2f}")
    print("\n=== (a2) distance at which the half-intensity cones of neighbours touch ===")
    print("d_touch = (chord/2)/tan(half angle); needed minimum, not a uniformity result")
    for d in (38, 40, 46):
        _, ch = ring_pitch(d)
        for th in (45, 60):
            print(f"  D_ring {d} mm, half angle {th} deg: d_touch = {(ch/2)/math.tan(math.radians(th)):.2f} mm")
    print("\n=== (a3) ripple of irradiance along the ring circle vs height h (before diffuser scatter) ===")
    print("Michelson ripple = (Emax-Emin)/(Emax+Emin); ratio = Emax/Emin")
    hs = (1, 2, 3, 4, 5, 6, 8, 10, 12)
    for d in (38, 40, 46):
        for th in (60, 45):
            m = lambert_order(th)
            row = []
            for h in hs:
                rp, ra = ring_irradiance_ripple(d, h, m)
                row.append(f"{h}:{rp*100:5.1f}%")
            print(f"D_ring {d} mm, half angle {th} deg (m={m:.2f}):  " + "  ".join(row))
    # smallest h with ripple <= 10 %, <= 5 %
    print("\nSmallest h (0.25 mm steps) with ripple <= limit:")
    for d in (38, 40, 46):
        for th in (60, 45):
            m = lambert_order(th)
            res = []
            for lim in (0.20, 0.10, 0.05):
                h = 0.25
                while h < 30 and ring_irradiance_ripple(d, h, m, 400)[0] > lim:
                    h += 0.25
                res.append(f"<= {lim*100:.0f}%: h={h:.2f} mm")
            print(f"  D_ring {d} mm, half angle {th} deg: " + ";  ".join(res))
    # radial spread: band width seen on the diffuser for a cone at height h
    print("\n=== (a4) radial half width of the lit band on the diffuser (to half intensity) = h*tan(theta) ===")
    for h in (4, 6, 8):
        print(f"  h={h} mm: theta 60 deg -> {h*math.tan(math.radians(60)):.1f} mm; 45 deg -> {h*math.tan(math.radians(45)):.1f} mm")

# --------------------------------------------------------------- (b) thermal
SIGMA = 5.670374e-8
def housing_area(d_mm, h_mm, include_bottom=True):
    d, h = d_mm / 1000.0, h_mm / 1000.0
    side = math.pi * d * h
    top = math.pi * d * d / 4.0
    return side + top + (top if include_bottom else 0.0)

def h_rad(t_surf_c, t_amb_c, eps):
    """Linearised radiative coefficient between a surface and surroundings."""
    ts, ta = t_surf_c + 273.15, t_amb_c + 273.15
    return eps * SIGMA * (ts ** 4 - ta ** 4) / (ts - ta)

def solve_dt(P, A, h_conv, eps, t_amb):
    """Solve dT = P/((h_conv + h_rad(T)) A) by iteration; h_conv fixed (assumption)."""
    dt = 10.0
    for _ in range(200):
        hr = h_rad(t_amb + dt, t_amb, eps)
        dt_new = P / ((h_conv + hr) * A)
        if abs(dt_new - dt) < 1e-6:
            break
        dt = 0.5 * dt + 0.5 * dt_new
    return dt, hr

def part_b():
    print("\n=== (b) Steady-state surface temperature rise, closed housing (ROUGH ESTIMATE) ===")
    print("Model: dT = P / ((h_conv + h_rad) * A), one isothermal surface, P = ALL electrical input power")
    print("heat leaving through the shell (light output is absorbed in the plastic or leaves as light:")
    print("treating it all as heat is the safe side). h_rad = eps*sigma*(Ts^4-Ta^4)/(Ts-Ta), eps=0.9 (assumption).")
    print("h_conv natural convection 3 (low, still-air vertical wall), 5 and 10 W/m2K (snippet range).")
    d, hgt = 55.0, 28.0
    for incl in (True, False):
        A = housing_area(d, hgt, incl)
        print(f"\nHousing D={d:.0f} mm x H={hgt:.0f} mm, area {'all faces' if incl else 'bottom excluded (on a desk)'}: A = {A*1e4:.1f} cm2")
        print("   P[W]  | dT[K] at h_conv=10 | at 5 | at 3   (h_rad about 5.5-6.5 W/m2K inside)")
        for P in (0.5, 1.0, 2.0, 2.5, 3.0, 4.7, 6.75):
            vals = []
            for hc in (10.0, 5.0, 3.0):
                dt, hr = solve_dt(P, A, hc, 0.9, 25.0)
                vals.append(dt)
            print(f"  {P:5.2f}  | {vals[0]:17.1f} | {vals[1]:4.1f} | {vals[2]:4.1f}")
    # Allowed dissipation vs material limit
    print("\nMax P so that (T_room + dT) <= HDT - 15 K  (MECH-005 margin), skin temp used as proxy for the plastic:")
    A = housing_area(d, hgt, False)
    mats = {"PLA 55 C (PolyMax PLA)": 55, "PLA 60 C (PolyLite PLA)": 60, "PETG 69 C (Polymaker PETG)": 69,
            "PETG 78 C (PolyLite PETG)": 78, "ASA 103 C (Polymaker ASA)": 103}
    for t_room in (25.0, 35.0):
        print(f"  room temperature {t_room:.0f} C (35 C = assumed hottest room, ASSUMPTION), A bottom excluded")
        for name, hdt in mats.items():
            allowed = hdt - 15.0 - t_room
            out = []
            for hc in (10.0, 5.0, 3.0):
                if allowed <= 0:
                    out.append("  none")
                    continue
                # invert: find P by bisection
                lo, hi = 0.0, 20.0
                for _ in range(60):
                    mid = 0.5 * (lo + hi)
                    dt, _ = solve_dt(mid, A, hc, 0.9, t_room)
                    if dt > allowed:
                        hi = mid
                    else:
                        lo = mid
                out.append(f"{lo:5.2f} W")
            print(f"    {name:30s} allowed rise {max(allowed,0):5.1f} K -> P_max at h_conv 10/5/3: {out[0]} / {out[1]} / {out[2]}")

# ------------------------------------------------------- (c) tolerance stack
def rss(vals):
    return math.sqrt(sum(v * v for v in vals))

def part_c():
    print("\n=== (c) Tolerance stack (worst case WC and RSS; FDM +-0.3 mm assumed, see report) ===")
    tol_fdm = 0.30   # +-mm, printed external size (assumption from guides, 0.2-0.3)
    tol_fdm_f = 0.20 # +-mm, small printed features and positions (assumption)
    tol_pcb_d = 0.15 # +-mm PCB outline (assumption, shop value not found)
    tol_pcb_t = 0.16 # +-mm PCB thickness 1.6 (assumption, 10 %)
    # Geometry (working values of the plan)
    D_out, wall, D_pcb = 55.0, 1.6, 44.0
    D_in = D_out - 2 * wall
    # 1. radial gap round the PCB (cylindrical wall)
    nom = (D_in - D_pcb) / 2.0
    wc = (D_in - tol_fdm - (D_pcb + tol_pcb_d)) / 2.0
    # PCB is not held by the wall but by posts: add placement error of the PCB on the posts
    place = 0.30  # +-mm PCB centre vs housing axis via 3 locating pegs with clearance (assumption)
    wc_gap = wc - place
    rss_gap = nom - rss([tol_fdm / 2.0, tol_pcb_d / 2.0, place])
    print(f"1. Radial gap PCB to cylinder wall: nominal {nom:.2f} mm, worst case {wc_gap:.2f} mm, RSS {rss_gap:.2f} mm")
    # 2. label facet: flat plane cut in the base at plane distance p from the axis
    lab = 21.0
    facet_w = lab + 2.0
    p_plane = math.sqrt((D_out / 2.0) ** 2 - (facet_w / 2.0) ** 2)
    inner_plane = p_plane - wall
    gap_facet = inner_plane - D_pcb / 2.0
    gap_facet_wc = gap_facet - tol_fdm_f - tol_pcb_d / 2.0 - place
    sag = D_out / 2.0 - p_plane
    print(f"2. Label facet: recess {lab:.0f} x {lab:.0f} mm, facet width {facet_w:.0f} mm -> plane at {p_plane:.2f} mm from axis"
          f" (cut depth {sag:.2f} mm). Inner plane {inner_plane:.2f} mm; gap to PCB edge nominal {gap_facet:.2f} mm, worst case {gap_facet_wc:.2f} mm")
    # 3. USB-C window versus overmold (USB-IF 12.35 x 6.5 max)
    ov_w, ov_h = 12.35, 6.5
    pos = [0.10,  # receptacle position on PCB (assumption)
           place, # PCB position in the housing (as above)
           tol_fdm_f]  # window position in the wall
    mis_wc, mis_rss = sum(pos), rss(pos)
    print(f"3. USB-C window: overmold {ov_w} x {ov_h} mm (read). Lateral misalignment receptacle-to-window: worst case +-{mis_wc:.2f}, RSS +-{mis_rss:.2f} mm")
    for w, h in ((13.2, 7.3), (13.6, 7.7), (14.0, 8.0)):
        # window size is itself +-tol_fdm_f/2 per edge (hole undersized, we add + bias): use size tol +-0.3
        slack_wc_w = (w - tol_fdm) - ov_w
        slack_wc_h = (h - tol_fdm) - ov_h
        need_w = 2 * mis_wc
        need_r = 2 * mis_rss
        print(f"   window {w:.1f} x {h:.1f}: slack WC (min size) {slack_wc_w:.2f} x {slack_wc_h:.2f} mm; "
              f"needed WC {need_w:.2f}, RSS {need_r:.2f} -> "
              f"{'WC ok' if min(slack_wc_w, slack_wc_h) >= need_w else ('RSS ok, WC not' if min(slack_wc_w, slack_wc_h) >= need_r else 'FAIL')}")
    # window as 'bored' hole: required nominal size for WC
    print(f"   Window size needed for worst case: width >= {ov_w + 2*mis_wc + tol_fdm:.2f}, height >= {ov_h + 2*mis_wc + tol_fdm:.2f} mm (nominal, with +-{tol_fdm} size tolerance)")
    # plug shell vs receptacle: not ours (HW), plug 8.25 +-0.03 x 2.40 +-0.03 (read)
    # 4. LED-to-diffuser distance
    d_nom = 6.0
    tol_items = {"post height": 0.20, "PCB thickness": tol_pcb_t, "LED height (assumption)": 0.10,
                 "lid skirt/top position": 0.20, "base height": 0.20}
    d_wc = sum(tol_items.values())
    d_rss = rss(list(tol_items.values()))
    print(f"4. LED-to-diffuser distance nominal {d_nom:.1f} mm: WC +-{d_wc:.2f} mm, RSS +-{d_rss:.2f} mm -> range {d_nom-d_wc:.2f}..{d_nom+d_wc:.2f} (WC)")
    # 5. lid/base spigot: each diameter +-tol_fdm -> per-side clearance changes by +-tol_fdm (WC)
    for cl_nom in (0.25, 0.35, 0.40):
        cl_wc = cl_nom - tol_fdm
        cl_rss = cl_nom - rss([tol_fdm / 2.0, tol_fdm / 2.0])
        print(f"5. Lid/base spigot, nominal per-side clearance {cl_nom:.2f} mm: worst-case minimum {cl_wc:+.2f} mm, RSS minimum {cl_rss:+.2f} mm "
              f"({'interference possible' if cl_wc < 0 else 'no interference'}); WC maximum play {cl_nom + tol_fdm:.2f} mm per side")

if __name__ == "__main__":
    part_a()
    part_b()
    part_c()
```

Output, copied unchanged from the run:

```text
=== (a) LED pitch on the ring ===
D_ring[mm]  arc pitch[mm]  chord[mm]  angle at 1 m[arcmin]
       38           7.46       7.41                  25.5
       40           7.85       7.80                  26.8
       42           8.25       8.19                  28.2
       44           8.64       8.58                  29.5
       46           9.03       8.97                  30.9

Half-intensity half angles and the Lambertian order m (cos^m model)
  half angle 45 deg (full 90 deg): m = 2.00
  half angle 60 deg (full 120 deg): m = 1.00
  half angle 65 deg (full 130 deg): m = 0.80

=== (a2) distance at which the half-intensity cones of neighbours touch ===
d_touch = (chord/2)/tan(half angle); needed minimum, not a uniformity result
  D_ring 38 mm, half angle 45 deg: d_touch = 3.71 mm
  D_ring 38 mm, half angle 60 deg: d_touch = 2.14 mm
  D_ring 40 mm, half angle 45 deg: d_touch = 3.90 mm
  D_ring 40 mm, half angle 60 deg: d_touch = 2.25 mm
  D_ring 46 mm, half angle 45 deg: d_touch = 4.49 mm
  D_ring 46 mm, half angle 60 deg: d_touch = 2.59 mm

=== (a3) ripple of irradiance along the ring circle vs height h (before diffuser scatter) ===
Michelson ripple = (Emax-Emin)/(Emax+Emin); ratio = Emax/Emin
D_ring 38 mm, half angle 60 deg (m=1.00):  1: 92.9%  2: 64.1%  3: 34.9%  4: 17.2%  5:  8.1%  6:  3.8%  8:  0.8%  10:  0.2%  12:  0.0%
D_ring 38 mm, half angle 45 deg (m=2.00):  1: 98.2%  2: 81.5%  3: 52.9%  4: 29.5%  5: 15.3%  6:  7.7%  8:  1.8%  10:  0.4%  12:  0.1%
D_ring 40 mm, half angle 60 deg (m=1.00):  1: 93.8%  2: 67.4%  3: 38.5%  4: 19.9%  5:  9.8%  6:  4.8%  8:  1.1%  10:  0.2%  12:  0.1%
D_ring 40 mm, half angle 45 deg (m=2.00):  1: 98.5%  2: 84.1%  3: 57.2%  4: 33.4%  5: 18.1%  6:  9.4%  8:  2.4%  10:  0.6%  12:  0.1%
D_ring 46 mm, half angle 60 deg (m=1.00):  1: 95.8%  2: 75.5%  3: 48.8%  4: 28.3%  5: 15.6%  6:  8.4%  8:  2.4%  10:  0.7%  12:  0.2%
D_ring 46 mm, half angle 45 deg (m=2.00):  1: 99.1%  2: 89.6%  3: 68.1%  4: 44.8%  5: 27.1%  6: 15.7%  8:  5.0%  10:  1.5%  12:  0.4%

Smallest h (0.25 mm steps) with ripple <= limit:
  D_ring 38 mm, half angle 60 deg: <= 20%: h=4.00 mm;  <= 10%: h=4.75 mm;  <= 5%: h=5.75 mm
  D_ring 38 mm, half angle 45 deg: <= 20%: h=4.75 mm;  <= 10%: h=5.75 mm;  <= 5%: h=6.75 mm
  D_ring 40 mm, half angle 60 deg: <= 20%: h=4.00 mm;  <= 10%: h=5.00 mm;  <= 5%: h=6.00 mm
  D_ring 40 mm, half angle 45 deg: <= 20%: h=5.00 mm;  <= 10%: h=6.00 mm;  <= 5%: h=7.00 mm
  D_ring 46 mm, half angle 60 deg: <= 20%: h=4.75 mm;  <= 10%: h=5.75 mm;  <= 5%: h=7.00 mm
  D_ring 46 mm, half angle 45 deg: <= 20%: h=5.75 mm;  <= 10%: h=7.00 mm;  <= 5%: h=8.00 mm

=== (a4) radial half width of the lit band on the diffuser (to half intensity) = h*tan(theta) ===
  h=4 mm: theta 60 deg -> 6.9 mm; 45 deg -> 4.0 mm
  h=6 mm: theta 60 deg -> 10.4 mm; 45 deg -> 6.0 mm
  h=8 mm: theta 60 deg -> 13.9 mm; 45 deg -> 8.0 mm

=== (b) Steady-state surface temperature rise, closed housing (ROUGH ESTIMATE) ===
Model: dT = P / ((h_conv + h_rad) * A), one isothermal surface, P = ALL electrical input power
heat leaving through the shell (light output is absorbed in the plastic or leaves as light:
treating it all as heat is the safe side). h_rad = eps*sigma*(Ts^4-Ta^4)/(Ts-Ta), eps=0.9 (assumption).
h_conv natural convection 3 (low, still-air vertical wall), 5 and 10 W/m2K (snippet range).

Housing D=55 mm x H=28 mm, area all faces: A = 95.9 cm2
   P[W]  | dT[K] at h_conv=10 | at 5 | at 3   (h_rad about 5.5-6.5 W/m2K inside)
   0.50  |               3.4 |  4.9 |  6.1
   1.00  |               6.7 |  9.8 | 11.9
   2.00  |              13.2 | 19.0 | 23.0
   2.50  |              16.4 | 23.5 | 28.2
   3.00  |              19.6 | 27.9 | 33.3
   4.70  |              30.1 | 42.0 | 49.4
   6.75  |              42.2 | 57.7 | 66.9

Housing D=55 mm x H=28 mm, area bottom excluded (on a desk): A = 72.1 cm2
   P[W]  | dT[K] at h_conv=10 | at 5 | at 3   (h_rad about 5.5-6.5 W/m2K inside)
   0.50  |               4.5 |  6.5 |  8.0
   1.00  |               8.9 | 12.9 | 15.7
   2.00  |              17.4 | 24.9 | 29.9
   2.50  |              21.6 | 30.7 | 36.5
   3.00  |              25.7 | 36.2 | 42.9
   4.70  |              39.3 | 54.0 | 62.8
   6.75  |              54.7 | 73.4 | 83.9

Max P so that (T_room + dT) <= HDT - 15 K  (MECH-005 margin), skin temp used as proxy for the plastic:
  room temperature 25 C (35 C = assumed hottest room, ASSUMPTION), A bottom excluded
    PLA 55 C (PolyMax PLA)         allowed rise  15.0 K -> P_max at h_conv 10/5/3:  1.71 W /  1.17 W /  0.96 W
    PLA 60 C (PolyLite PLA)        allowed rise  20.0 K -> P_max at h_conv 10/5/3:  2.31 W /  1.58 W /  1.30 W
    PETG 69 C (Polymaker PETG)     allowed rise  29.0 K -> P_max at h_conv 10/5/3:  3.40 W /  2.35 W /  1.94 W
    PETG 78 C (PolyLite PETG)      allowed rise  38.0 K -> P_max at h_conv 10/5/3:  4.53 W /  3.16 W /  2.61 W
    ASA 103 C (Polymaker ASA)      allowed rise  63.0 K -> P_max at h_conv 10/5/3:  7.90 W /  5.63 W /  4.72 W
  room temperature 35 C (35 C = assumed hottest room, ASSUMPTION), A bottom excluded
    PLA 55 C (PolyMax PLA)         allowed rise   5.0 K -> P_max at h_conv 10/5/3:  0.58 W /  0.40 W /  0.33 W
    PLA 60 C (PolyLite PLA)        allowed rise  10.0 K -> P_max at h_conv 10/5/3:  1.17 W /  0.81 W /  0.67 W
    PETG 69 C (Polymaker PETG)     allowed rise  19.0 K -> P_max at h_conv 10/5/3:  2.27 W /  1.58 W /  1.31 W
    PETG 78 C (PolyLite PETG)      allowed rise  28.0 K -> P_max at h_conv 10/5/3:  3.40 W /  2.39 W /  1.99 W
    ASA 103 C (Polymaker ASA)      allowed rise  53.0 K -> P_max at h_conv 10/5/3:  6.77 W /  4.86 W /  4.09 W

=== (c) Tolerance stack (worst case WC and RSS; FDM +-0.3 mm assumed, see report) ===
1. Radial gap PCB to cylinder wall: nominal 3.90 mm, worst case 3.38 mm, RSS 3.56 mm
2. Label facet: recess 21 x 21 mm, facet width 23 mm -> plane at 24.98 mm from axis (cut depth 2.52 mm). Inner plane 23.38 mm; gap to PCB edge nominal 1.38 mm, worst case 0.80 mm
3. USB-C window: overmold 12.35 x 6.5 mm (read). Lateral misalignment receptacle-to-window: worst case +-0.60, RSS +-0.37 mm
   window 13.2 x 7.3: slack WC (min size) 0.55 x 0.50 mm; needed WC 1.20, RSS 0.75 -> FAIL
   window 13.6 x 7.7: slack WC (min size) 0.95 x 0.90 mm; needed WC 1.20, RSS 0.75 -> RSS ok, WC not
   window 14.0 x 8.0: slack WC (min size) 1.35 x 1.20 mm; needed WC 1.20, RSS 0.75 -> WC ok
   Window size needed for worst case: width >= 13.85, height >= 8.00 mm (nominal, with +-0.3 size tolerance)
4. LED-to-diffuser distance nominal 6.0 mm: WC +-0.86 mm, RSS +-0.39 mm -> range 5.14..6.86 (WC)
5. Lid/base spigot, nominal per-side clearance 0.25 mm: worst-case minimum -0.05 mm, RSS minimum +0.04 mm (interference possible); WC maximum play 0.55 mm per side
5. Lid/base spigot, nominal per-side clearance 0.35 mm: worst-case minimum +0.05 mm, RSS minimum +0.14 mm (no interference); WC maximum play 0.65 mm per side
5. Lid/base spigot, nominal per-side clearance 0.40 mm: worst-case minimum +0.10 mm, RSS minimum +0.19 mm (no interference); WC maximum play 0.70 mm per side
```

## 7. Script `adr_scores.py` (decision tables of ADR-0011)

```python
#!/usr/bin/env python3
"""ADR-0011 weighted decision tables. Scores are the author's judgement (0-5), not measured.
Run: python3 -I adr_scores.py"""
def table(title, crit, opts, gate_idx):
    w = [c[1] for c in crit]
    print(f"== {title}: weights {w}, sum {sum(w)}, max {5*sum(w)}")
    for name, sc in opts.items():
        assert len(sc) == len(crit), name
        assert all(0 <= s <= 5 for s in sc)
        tot = sum(a * b for a, b in zip(w, sc))
        gate = [crit[i][0] for i, lim in gate_idx if sc[i] <= lim]
        print(f"  {name:48s} sum {tot:4d} ({100*tot/(5*sum(w)):5.1f} %)" + (f"  EXCLUDED by gate: {gate}" if gate else ""))
    print()

C = [("1 Diffusion: closed band, no point source (MECH-002)", 5),
     ("2 Antenna friendliness: no metal near antenna (MECH-003)", 5),
     ("3 Thermal and material margin (MECH-005)", 4),
     ("4 Size and fixed label area (MECH-001, MECH-006)", 4),
     ("5 USB-C and button access (MECH-004)", 4),
     ("6 Assembly without tools or common screws, reopening (DFx)", 4),
     ("7 Printability, tolerance sensitivity (DFx 1)", 4),
     ("8 Test and programming access (DFx 3, HW-006)", 3),
     ("9 Part count and print cost", 2)]
concepts = {
 "A clamshell + separate diffuser ring (3 parts)":      [5, 4, 4, 3, 4, 3, 3, 4, 2],
 "B opaque base + one translucent lid (2 parts)":        [4, 5, 3, 5, 4, 4, 4, 4, 5],
 "C sphere, two snap-fit halves":                        [3, 5, 3, 2, 3, 4, 2, 3, 4],
 "D do nothing (bare board, no housing)":                [0, 5, 5, 0, 3, 5, 5, 5, 5],
}
table("Concept table", C, concepts, gate_idx=[(0, 0), (3, 0)])

# sensitivity: +-1 on every score of the top two, check ranking holds / weights +-1
import itertools
w0 = [c[1] for c in C]
def total(w, s): return sum(a*b for a, b in zip(w, s))
a, b = concepts["A clamshell + separate diffuser ring (3 parts)"], concepts["B opaque base + one translucent lid (2 parts)"]
print("B - A =", total(w0, b) - total(w0, a))
# worst-case: each criterion weight changed by -1/+1 one at a time
flip = []
for i in range(len(w0)):
    for d in (-1, 1):
        w = list(w0); w[i] = max(1, w[i] + d)
        if total(w, b) <= total(w, a): flip.append((C[i][0][:30], d))
print("single weight +-1 changes that make A >= B:", flip or "none")
# score shift: every B score -1 on one criterion
flip2 = []
for i in range(len(w0)):
    bb = list(b); bb[i] = max(0, bb[i]-1)
    if total(w0, bb) <= total(w0, a): flip2.append(C[i][0][:30])
print("lowering one B score by 1 makes A >= B for:", flip2 or "none")
# diffuser weight 5 -> A advantage criterion: how much must criterion-1 weight rise for A to tie B
for w1 in range(5, 15):
    w = list(w0); w[0] = w1
    if total(w, a) >= total(w, b):
        print("A ties/overtakes B when weight of criterion 1 reaches", w1); break
print()

P = [("1 Dimensional accuracy for fits (USB-C window, spigot)", 4),
     ("2 Thermal margin: HDT vs MECH-005 (needs data per product)", 5),
     ("3 Diffuser quality possible in this process", 4),
     ("4 Availability at the owner and lead time (UNKNOWN: owner question)", 4),
     ("5 Strength of snap/screw features, reopening x100", 3),
     ("6 Non-conductive, no metal fill (MECH-003)", 5),
     ("7 Handling safety, post-processing effort", 3),
     ("8 Cost per housing (prototype, 10 units)", 3)]
procs = {
 "P1 FDM, PETG base + natural PETG diffuser":            [3, 3, 3, 4, 3, 5, 5, 5],
 "P2 FDM, ASA base + natural PETG diffuser":             [3, 4, 3, 3, 3, 5, 3, 4],
 "P3 resin (MSLA), opaque base + clear/white lid":       [5, 2, 4, 3, 2, 5, 2, 3],
 "P4 FDM, PLA (cheapest, common)":                       [3, 1, 3, 5, 3, 5, 5, 5],
 "P5 do nothing (no printed housing)":                   [0, 5, 0, 5, 0, 5, 5, 5],
}
table("Process table", P, procs, gate_idx=[(2, 0), (1, 1)])
w = [c[1] for c in P]
print("P2 - P1 =", total(w, procs["P2 FDM, ASA base + natural PETG diffuser"]) - total(w, procs["P1 FDM, PETG base + natural PETG diffuser"]))
```

Output, copied unchanged:

```text
== Concept table: weights [5, 5, 4, 4, 4, 4, 4, 3, 2], sum 35, max 175
  A clamshell + separate diffuser ring (3 parts)   sum  129 ( 73.7 %)
  B opaque base + one translucent lid (2 parts)    sum  147 ( 84.0 %)
  C sphere, two snap-fit halves                    sum  113 ( 64.6 %)
  D do nothing (bare board, no housing)            sum  122 ( 69.7 %)  EXCLUDED by gate: ['1 Diffusion: closed band, no point source (MECH-002)', '4 Size and fixed label area (MECH-001, MECH-006)']

B - A = 18
single weight +-1 changes that make A >= B: none
lowering one B score by 1 makes A >= B for: none

== Process table: weights [4, 5, 4, 4, 3, 5, 3, 3], sum 31, max 155
  P1 FDM, PETG base + natural PETG diffuser        sum  119 ( 76.8 %)
  P2 FDM, ASA base + natural PETG diffuser         sum  111 ( 71.6 %)
  P3 resin (MSLA), opaque base + clear/white lid   sum  104 ( 67.1 %)
  P4 FDM, PLA (cheapest, common)                   sum  113 ( 72.9 %)  EXCLUDED by gate: ['2 Thermal margin: HDT vs MECH-005 (needs data per product)']
  P5 do nothing (no printed housing)               sum  100 ( 64.5 %)  EXCLUDED by gate: ['3 Diffuser quality possible in this process']

P2 - P1 = -8
```

## 8. Re-run with resolved dimensions (2026-11-04)

Sections 1 to 7 above are the first draft and are kept unchanged. This section re-runs the analysis with the dimensions chosen to resolve the three open conflicts of plan 05 (MECH-006 height and facet, the 15 mm antenna clearance, the PCB size of ADR-0003). The new dimensions are the author's decisions, not yet confirmed by the owner. Still analysis only, nothing measured. Scripts are in the session scratchpad (`mech/mech_analysis_v2.py`, `mech/adr_scores_v2.py`); the old scripts are unchanged. `mech_analysis_v2.py` imports the functions of `mech_analysis.py` (section 6); keep both in one folder.

### 8.1 New inputs
D_out 53.0 mm, wall 1.6 mm, floor 2.0 mm, D_pcb 46.0 mm, D_ring 40.0 mm, post height 3.0 mm, Z_pcb_bot 5.0, Z_pcb_top 6.6, LED top 7.25, d_led 8.0, lid plate 1.2, lid underside 15.25, H_total 16.5 (16.45 computed), joint zone Z 14.0 to 15.25, label recess 21 x 21 x 0.3 in the underside with 4 feet 1.0 mm tall, window 14.0 x 8.0 mm centred at Z 8.25, module at the board centre with the antenna end at azimuth 180. All are assumptions or working values (brackets in plan 05).

### 8.2 Results

| Topic | First draft (D 55 x H 28) | Re-run (D 53 x H 16.5) | What changes |
|-------|---------------------------|------------------------|--------------|
| Ring pitch (D_ring 40) | 7.85 mm arc, 7.80 mm chord | same | nothing |
| Ripple at d_led 8.0 (60 / 45 deg half angle) | 1.1 % / 2.4 % | same; over 7.14 to 8.86 mm: 2.1 to 0.6 % and 4.4 to 1.3 % | nothing (the old note says 1.4 % for 45 deg at 8.86 mm; this run gives 1.3 %: rounding) |
| Radial gap PCB to wall, nominal / worst case / RSS | 3.90 / 3.38 / 3.56 mm | 1.90 / 1.38 / 1.56 mm | thinner by 2.0 mm; no interference |
| Label facet stack | 1.38 mm nominal, 0.80 mm worst case | removed | the thinnest fit of the first draft is gone |
| USB-C window 14.0 x 8.0 against 12.35 x 6.5 | worst case ok | identical numbers (slack 1.35 x 1.20 mm, 1.20 needed); window Z 4.25 to 12.25: 2.25 mm above the floor top, 1.75 mm below the joint zone | passes; the receptacle position on the board is still unknown |
| Wall outer surface to PCB edge | 5.5 mm | 3.5 mm | the plug overmold must still reach the receptacle mouth (open, report F5) |
| Spigot clearance 0.35 mm, worst case minimum | +0.05 mm | +0.05 mm | nothing; the joint zone is now 1.25 mm high (was 1.8 mm) |
| Shell area, bottom excluded | 72.1 cm2 | 49.5 cm2 (ratio 0.687); all faces 71.6 cm2 | 31 % less |
| Mass, PETG, base plus lid (estimate) | 19.2 g | 13.6 g (base ASA, lid PETG: 12.0 g; old 16.8 g) | about 30 % less; walls and plates taken as solid, PCB and parts excluded |

Thermal, surface rise at 25 deg C ambient, bottom excluded, h_conv 10 / 5 / 3 W/m2K:

| P [W] | First draft [K] | Re-run [K] |
|-------|-----------------|-----------|
| 0.5 | 4.5 / 6.5 / 8.0 | 6.5 / 9.5 / 11.6 |
| 1.0 | 8.9 / 12.9 / 15.7 | 12.8 / 18.5 / 22.3 |
| 2.0 | 17.4 / 24.9 / 29.9 | 25.0 / 35.3 / 41.8 |
| 2.5 | 21.6 / 30.7 / 36.5 | 30.9 / 43.1 / 50.7 |
| 3.0 | 25.7 / 36.2 / 42.9 | 36.7 / 50.7 / 59.1 |
| 4.7 | 39.3 / 54.0 / 62.8 | 55.4 / 74.2 / 84.8 |
| 6.75 | 54.7 / 73.4 / 83.9 | 76.3 / 99.1 / 111.2 |

Maximum power for HDT minus 15 K, room 35 deg C, h_conv 10 / 5 / 3: PLA (55) 0.40 / 0.28 / 0.23 W; PETG (69) 1.56 / 1.09 / 0.90 W; PETG (78) 2.34 / 1.64 / 1.36 W; ASA (103) 4.65 / 3.33 / 2.81 W. Room 25 deg C: PETG (69) 2.33 / 1.62 / 1.33 W; PETG (78) 3.11 / 2.17 / 1.79 W; ASA 5.42 / 3.86 / 3.24 W (first draft ASA at 35 deg C: 6.77 / 4.86 / 4.09 W).
Reading: the same rough model with a smaller shell, so the rise is 1.4 times higher. PETG does not meet MECH-005 at 2.5 W in a 35 deg C room for any assumed convection; ASA meets 2.5 W in all cases but not 4.7 W. The model has no heat path through the desk. Counting all faces (not realistic for a unit on a desk) gives about the first-draft numbers (3 W: 25.9 / 36.5 / 43.2 K).

Antenna geometry (module 13.2 x 16.6 mm centred, antenna strip 5.4 mm at the end, inner wall radius 24.9 mm, outer 26.5 mm):

| Distance | Value | Against 15 mm |
|----------|-------|---------------|
| Antenna end edge (middle) to inner wall | 16.6 mm (outer surface 18.2) | met |
| Antenna end corners (10.6 mm from the axis) to inner wall | 14.3 mm (outer surface 15.9) | not met by 0.7 mm |
| Same corners with D_out 55 (R_in 25.9) | 15.3 mm | met |
| PCB top (antenna plane) to lid underside / to floor outer face | 8.65 / 6.6 mm | inside the box; plastic and the label |
| Nearest LED centre (R 20) to the antenna rectangle | 9.5 mm (11.7 mm on the module axis) | below 15 mm; layout matter |

The task text gave about 11 mm for the LED distance; the computed minimum over the 16 LEDs is 9.5 mm (assumed antenna rectangle 13.2 x 5.4 mm, full width; the real keep-out is in an Espressif figure that is not available as text).

Other results: the label recess 21 x 21 mm has a half diagonal of 14.85 mm; feet at radius 21 mm with pad radius 3 mm are 3.15 mm clear of it. The band of light at half intensity reaches R 28 to 34 mm and is cut by the wall at R 24.9 mm, as before. For what does not fit, see plan 05 section 4.11.

### 8.3 ADR-0011 scores re-run
Criterion 4 (size and label) improves for A (3 to 4) and C (2 to 3) because a label on the underside is easier than a facet in a sphere or in a three-part case; B stays at 5. Process criterion 2 (thermal) for P1 (PETG) falls from 3 to 2 because of the thermal result. Result: B 147, A 133 (was 129), C 117 (was 113), D 122 (excluded by gates); B leads A by 14 points (was 18); P1 114 (was 119), P2 111, P3 104, P4 113 (excluded), P5 100 (excluded); P2 minus P1 is minus 3 (was minus 8). The ranking is unchanged. These are the author's scores, not measured.

### 8.4 Script `mech_analysis_v2.py`

```python
#!/usr/bin/env python3
"""busy-light mechanical analysis, re-run with the resolved dimensions (plan 05 rev 2026-11-04).
Analysis only, nothing measured. Run: python3 -I mech_analysis_v2.py
Imports the functions of mech_analysis.py (same folder) for light and thermal.
Parts: (a) light pitch/ripple, (b) thermal for the smaller shell, (c) tolerance stack,
(d) antenna geometry, (e) printed mass (estimate)."""
import math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mech_analysis as m

rss = m.rss if hasattr(m, "rss") else (lambda v: math.sqrt(sum(x * x for x in v)))
OLD = dict(D_out=55.0, H=28.0, D_pcb=44.0)
NEW = dict(D_out=53.0, H=16.5, D_pcb=46.0)

def part_a():
    print("=== (a) light: D_ring 40.0, d_led 8.0 (unchanged) ===")
    arc, ch = m.ring_pitch(40.0)
    print(f"pitch arc {arc:.2f} mm, chord {ch:.2f} mm")
    for th in (60, 45):
        mm = m.lambert_order(th)
        for h in (7.14, 8.0, 8.86):
            rp, _ = m.ring_irradiance_ripple(40.0, h, mm)
            print(f"  half angle {th} deg, h {h:.2f} mm: ripple {rp*100:.1f} %")
    # new lit-band width unchanged; check band fits inside the lid: outer lit edge radius
    for th in (60, 45):
        w = 8.0 * math.tan(math.radians(th))
        print(f"  half-intensity band half width at 8 mm, {th} deg: {w:.1f} mm; ring R 20 + {w:.1f} = {20+w:.1f} mm vs inner wall R 24.9 mm")

def part_b():
    print("\n=== (b) thermal, 25 deg C ambient, eps 0.9 ===")
    for tag, g in (("OLD", OLD), ("NEW", NEW)):
        d, h = g["D_out"], g["H"]
        for incl in (False, True):
            A = m.housing_area(d, h, incl)
            print(f"{tag} D{d:.0f} x H{h:.1f}, {'all faces' if incl else 'bottom excluded'}: A = {A*1e4:.1f} cm2")
            if incl: continue
            for P in (0.5, 1.0, 2.0, 2.5, 3.0):
                v = [m.solve_dt(P, A, hc, 0.9, 25.0)[0] for hc in (10.0, 5.0, 3.0)]
                print(f"   P {P:4.2f} W: dT {v[0]:5.1f} / {v[1]:5.1f} / {v[2]:5.1f} K (h_conv 10/5/3)")
    A = m.housing_area(53, 16.5, False)
    for P in (4.7, 6.75):
        print(f"   NEW bottom excluded P {P:4.2f} W: dT " + " / ".join(f"{m.solve_dt(P, A, hc, 0.9, 25.0)[0]:.1f}" for hc in (10.0, 5.0, 3.0)) + " K")
    A = m.housing_area(53, 16.5, True)
    for P in (0.5, 1.0, 2.0, 3.0):
        print(f"   NEW all faces P {P:4.2f} W: dT " + " / ".join(f"{m.solve_dt(P, A, hc, 0.9, 25.0)[0]:.1f}" for hc in (10.0, 5.0, 3.0)) + " K")
    A_old, A_new = m.housing_area(55, 28, False), m.housing_area(53, 16.5, False)
    print(f"area ratio new/old = {A_new/A_old:.3f}")
    print("max P for HDT-15 K, bottom excluded, NEW shell (h_conv 10/5/3):")
    mats = {"PLA 55": 55, "PLA 60": 60, "PETG 69": 69, "PETG 78": 78, "ASA 103": 103}
    A = A_new
    for t_room in (25.0, 35.0):
        print(f" room {t_room:.0f} C")
        for name, hdt in mats.items():
            allowed = hdt - 15.0 - t_room
            out = []
            for hc in (10.0, 5.0, 3.0):
                if allowed <= 0:
                    out.append("none"); continue
                lo, hi = 0.0, 20.0
                for _ in range(60):
                    mid = 0.5 * (lo + hi)
                    dt, _ = m.solve_dt(mid, A, hc, 0.9, t_room)
                    if dt > allowed: hi = mid
                    else: lo = mid
                out.append(f"{lo:.2f}")
            print(f"   {name:10s} {out[0]} / {out[1]} / {out[2]} W")

def part_c():
    print("\n=== (c) tolerance stack, new dimensions ===")
    tf, tff, tpd, tpt, place = 0.30, 0.20, 0.15, 0.16, 0.30
    D_out, wall, D_pcb = 53.0, 1.6, 46.0
    D_in = D_out - 2 * wall
    nom = (D_in - D_pcb) / 2.0
    wc = (D_in - tf - (D_pcb + tpd)) / 2.0 - place
    rs = nom - rss([tf / 2, tpd / 2, place])
    print(f"1. radial gap PCB to wall: D_in {D_in:.1f}; nominal {nom:.2f}, WC {wc:.2f}, RSS {rs:.2f} mm")
    print(f"   (old: 3.90 / 3.38 / 3.56). Distance outer wall surface to PCB edge: {wall+nom:.2f} mm (old 5.5)")
    ov_w, ov_h = 12.35, 6.5
    pos = [0.10, place, tff]
    mw, mr = sum(pos), rss(pos)
    print(f"3. USB-C window: misalignment WC +-{mw:.2f}, RSS +-{mr:.2f}")
    for w, h in ((13.2, 7.3), (13.6, 7.7), (14.0, 8.0)):
        sw, sh = (w - tf) - ov_w, (h - tf) - ov_h
        ok = "WC ok" if min(sw, sh) >= 2 * mw else ("RSS ok, WC not" if min(sw, sh) >= 2 * mr else "FAIL")
        print(f"   {w:.1f} x {h:.1f}: slack WC {sw:.2f} x {sh:.2f}; need WC {2*mw:.2f}, RSS {2*mr:.2f} -> {ok}")
    # window vertical position
    zc, zt, zb = 8.25, 8.25 + 4.0, 8.25 - 4.0
    print(f"   window Z {zb:.2f}..{zt:.2f}; floor top 2.00; joint zone starts 14.00 -> margin to floor {zb-2.0:.2f}, to joint {14.0-zt:.2f} mm")
    # cable path: window bottom vs PCB bottom
    print(f"   window bottom {zb:.2f} vs PCB underside 5.00 and post top 5.00: posts at R 21, window at the wall, no clash if no post at azimuth 0")
    # 4 LED to diffuser
    items = {"post": 0.20, "pcb t": tpt, "LED h": 0.10, "lid": 0.20, "base h": 0.20}
    wcd, rsd = sum(items.values()), rss(list(items.values()))
    print(f"4. d_led 8.0: WC +-{wcd:.2f} ({8-wcd:.2f}..{8+wcd:.2f}), RSS +-{rsd:.2f}")
    for cl in (0.25, 0.35, 0.40):
        print(f"5. spigot clearance {cl:.2f}: WC min {cl-tf:+.2f}, RSS min {cl-rss([tf/2, tf/2]):+.2f}, max play {cl+tf:.2f}")
    # Z chain
    z_pcb_bot, t_pcb, h_led, d_led, t_lid, t_floor = 5.0, 1.6, 0.65, 8.0, 1.2, 2.0
    z_pcb_top = z_pcb_bot + t_pcb; z_led = z_pcb_top + h_led; z_lid = z_led + d_led; H = z_lid + t_lid
    print(f"Z chain: PCB top {z_pcb_top:.2f}, LED top {z_led:.2f}, lid underside {z_lid:.2f}, H_total {H:.2f}; post height {z_pcb_bot - t_floor:.2f}")
    print(f"   joint zone 14.00..{z_lid:.2f} = {z_lid-14.0:.2f} mm high; lid skirt 14.00..{H:.2f} = {H-14.0:.2f} mm; module top {z_pcb_top+2.4:.2f}")
    print(f"   feet 1.0: overall height {H+1.0:.2f} mm; label recess 0.3 in floor 2.0 leaves {2.0-0.3:.1f} mm")
    # label recess vs feet
    half_diag = 21 * math.sqrt(2) / 2
    print(f"   label 21 x 21 half diagonal {half_diag:.2f} mm; feet pad R3 at radius 21 on the diagonals: nearest edge {21-3:.1f} mm -> {'clear' if 21-3 > half_diag else 'CLASH'}")
    # old stack 2 (label facet) no longer exists
    print("2. label facet stack: removed (no side facet).")

def part_d():
    print("\n=== (d) antenna geometry ===")
    L, Wd, ant = 16.6, 13.2, 5.4
    R_in, R_out = 24.9, 26.5
    tip = L / 2
    corner = math.hypot(Wd / 2, tip)
    print(f"module centred; antenna end edge at {tip:.2f} mm from axis; far corners at {corner:.2f} mm")
    print(f"distance end edge (mid) to inner wall {R_in-tip:.2f}, outer surface {R_out-tip:.2f}")
    print(f"distance corner to inner wall {R_in-corner:.2f}, outer surface {R_out-corner:.2f} mm (15 mm rule: {'ok' if R_in-corner>=15 else 'NOT met at corners'})")
    # old: D_out 55, R_in 25.9
    print(f"old (R_in 25.9): end {25.9-tip:.2f}, corner {25.9-corner:.2f}")
    # vertical: module top and antenna to lid, floor
    z_mod_top, z_pcb_top, z_lid = 9.0, 6.6, 15.25
    print(f"antenna plane (PCB top 6.6) to lid underside {z_lid-z_pcb_top:.2f} mm, to lid top {z_lid+1.2-z_pcb_top:.2f}; PCB top to floor outer face {z_pcb_top:.1f} mm")
    print("label on the floor outer face is inside the 15 mm box vertically (6.6 mm below the antenna)")
    # LED distances
    ring_R = 20.0
    # antenna end strip: x from 2.9 to 8.3 along azimuth 180 axis, width +-6.6
    best = 1e9
    import itertools
    for k in range(16):
        a = math.radians(22.5 * k)
        lx, ly = ring_R * math.cos(a), ring_R * math.sin(a)
        # rectangle in module frame: antenna end toward azimuth 180 -> x in [-8.3, -2.9], y in [-6.6, 6.6]
        dx = max(-8.3 - lx, 0, lx + 2.9); dy = max(abs(ly) - 6.6, 0)
        best = min(best, math.hypot(dx, dy))
    print(f"LED centres at R 20 (ring phase 0 deg): nearest distance to antenna rectangle {best:.2f} mm (user figure about 11 mm)")
    # phase 11.25 deg
    best2 = 1e9
    for k in range(16):
        a = math.radians(22.5 * k + 11.25)
        lx, ly = ring_R * math.cos(a), ring_R * math.sin(a)
        dx = max(-8.3 - lx, 0, lx + 2.9); dy = max(abs(ly) - 6.6, 0)
        best2 = min(best2, math.hypot(dx, dy))
    print(f"ring phase 11.25 deg: {best2:.2f} mm; the LED edge (2.0 mm package) is about 1 mm closer")

def part_e():
    print("\n=== (e) printed mass, ESTIMATE (walls and plates solid, density PETG 1.27, ASA 1.07 g/cm3; PCB and parts excluded) ===")
    def vol(D_out, wall, floor, H_base, H_tot, t_lid, post_h, post_a=16.0, spig_t=1.15, spig_h=1.8, skirt_t=0.9, facet=0.0):
        r = D_out / 2; ri = r - wall
        v_floor = math.pi * r * r * floor
        v_wall = math.pi * (r * r - ri * ri) * (H_base - floor)
        v_post = 3 * post_a * post_h
        v_spig = math.pi * ((ri - 0.0) ** 2 - (ri - spig_t) ** 2) * spig_h
        v_plate = math.pi * r * r * t_lid
        v_skirt = math.pi * (r * r - (r - skirt_t) ** 2) * spig_h
        return (v_floor + v_wall + v_post + v_spig - facet) / 1000.0, (v_plate + v_skirt) / 1000.0  # cm3
    ob, ol = vol(55, 1.6, 2.0, 25.0, 28.0, 1.2, 14.55, spig_h=1.8, facet=0.0)
    nb, nl = vol(53, 1.6, 2.0, 14.0, 16.5, 1.2, 3.0, spig_h=1.25)
    for tag, b, l in (("OLD 55x28", ob, ol), ("NEW 53x16.5", nb, nl)):
        print(f"{tag}: base {b:.1f} cm3, lid {l:.1f} cm3; PETG {1.27*(b+l):.1f} g; base ASA + lid PETG {1.07*b+1.27*l:.1f} g")
    print("(infill reductions in floor/plate are not modelled; real mass is likely lower; weigh the first print)")

if __name__ == "__main__":
    part_a(); part_b(); part_c(); part_d(); part_e()
```

Output, copied unchanged:

```text
=== (a) light: D_ring 40.0, d_led 8.0 (unchanged) ===
pitch arc 7.85 mm, chord 7.80 mm
  half angle 60 deg, h 7.14 mm: ripple 2.1 %
  half angle 60 deg, h 8.00 mm: ripple 1.1 %
  half angle 60 deg, h 8.86 mm: ripple 0.6 %
  half angle 45 deg, h 7.14 mm: ripple 4.4 %
  half angle 45 deg, h 8.00 mm: ripple 2.4 %
  half angle 45 deg, h 8.86 mm: ripple 1.3 %
  half-intensity band half width at 8 mm, 60 deg: 13.9 mm; ring R 20 + 13.9 = 33.9 mm vs inner wall R 24.9 mm
  half-intensity band half width at 8 mm, 45 deg: 8.0 mm; ring R 20 + 8.0 = 28.0 mm vs inner wall R 24.9 mm

=== (b) thermal, 25 deg C ambient, eps 0.9 ===
OLD D55 x H28.0, bottom excluded: A = 72.1 cm2
   P 0.50 W: dT   4.5 /   6.5 /   8.0 K (h_conv 10/5/3)
   P 1.00 W: dT   8.9 /  12.9 /  15.7 K (h_conv 10/5/3)
   P 2.00 W: dT  17.4 /  24.9 /  29.9 K (h_conv 10/5/3)
   P 2.50 W: dT  21.6 /  30.7 /  36.5 K (h_conv 10/5/3)
   P 3.00 W: dT  25.7 /  36.2 /  42.9 K (h_conv 10/5/3)
OLD D55 x H28.0, all faces: A = 95.9 cm2
NEW D53 x H16.5, bottom excluded: A = 49.5 cm2
   P 0.50 W: dT   6.5 /   9.5 /  11.6 K (h_conv 10/5/3)
   P 1.00 W: dT  12.8 /  18.5 /  22.3 K (h_conv 10/5/3)
   P 2.00 W: dT  25.0 /  35.3 /  41.8 K (h_conv 10/5/3)
   P 2.50 W: dT  30.9 /  43.1 /  50.7 K (h_conv 10/5/3)
   P 3.00 W: dT  36.7 /  50.7 /  59.1 K (h_conv 10/5/3)
NEW D53 x H16.5, all faces: A = 71.6 cm2
   NEW bottom excluded P 4.70 W: dT 55.4 / 74.2 / 84.8 K
   NEW bottom excluded P 6.75 W: dT 76.3 / 99.1 / 111.2 K
   NEW all faces P 0.50 W: dT 4.5 / 6.6 / 8.1 K
   NEW all faces P 1.00 W: dT 8.9 / 13.0 / 15.8 K
   NEW all faces P 2.00 W: dT 17.6 / 25.1 / 30.1 K
   NEW all faces P 3.00 W: dT 25.9 / 36.5 / 43.2 K
area ratio new/old = 0.687
max P for HDT-15 K, bottom excluded, NEW shell (h_conv 10/5/3):
 room 25 C
   PLA 55     1.18 / 0.80 / 0.66 W
   PLA 60     1.58 / 1.09 / 0.89 W
   PETG 69    2.33 / 1.62 / 1.33 W
   PETG 78    3.11 / 2.17 / 1.79 W
   ASA 103    5.42 / 3.86 / 3.24 W
 room 35 C
   PLA 55     0.40 / 0.28 / 0.23 W
   PLA 60     0.81 / 0.56 / 0.46 W
   PETG 69    1.56 / 1.09 / 0.90 W
   PETG 78    2.34 / 1.64 / 1.36 W
   ASA 103    4.65 / 3.33 / 2.81 W

=== (c) tolerance stack, new dimensions ===
1. radial gap PCB to wall: D_in 49.8; nominal 1.90, WC 1.38, RSS 1.56 mm
   (old: 3.90 / 3.38 / 3.56). Distance outer wall surface to PCB edge: 3.50 mm (old 5.5)
3. USB-C window: misalignment WC +-0.60, RSS +-0.37
   13.2 x 7.3: slack WC 0.55 x 0.50; need WC 1.20, RSS 0.75 -> FAIL
   13.6 x 7.7: slack WC 0.95 x 0.90; need WC 1.20, RSS 0.75 -> RSS ok, WC not
   14.0 x 8.0: slack WC 1.35 x 1.20; need WC 1.20, RSS 0.75 -> WC ok
   window Z 4.25..12.25; floor top 2.00; joint zone starts 14.00 -> margin to floor 2.25, to joint 1.75 mm
   window bottom 4.25 vs PCB underside 5.00 and post top 5.00: posts at R 21, window at the wall, no clash if no post at azimuth 0
4. d_led 8.0: WC +-0.86 (7.14..8.86), RSS +-0.39
5. spigot clearance 0.25: WC min -0.05, RSS min +0.04, max play 0.55
5. spigot clearance 0.35: WC min +0.05, RSS min +0.14, max play 0.65
5. spigot clearance 0.40: WC min +0.10, RSS min +0.19, max play 0.70
Z chain: PCB top 6.60, LED top 7.25, lid underside 15.25, H_total 16.45; post height 3.00
   joint zone 14.00..15.25 = 1.25 mm high; lid skirt 14.00..16.45 = 2.45 mm; module top 9.00
   feet 1.0: overall height 17.45 mm; label recess 0.3 in floor 2.0 leaves 1.7 mm
   label 21 x 21 half diagonal 14.85 mm; feet pad R3 at radius 21 on the diagonals: nearest edge 18.0 mm -> clear
2. label facet stack: removed (no side facet).

=== (d) antenna geometry ===
module centred; antenna end edge at 8.30 mm from axis; far corners at 10.60 mm
distance end edge (mid) to inner wall 16.60, outer surface 18.20
distance corner to inner wall 14.30, outer surface 15.90 mm (15 mm rule: NOT met at corners)
old (R_in 25.9): end 17.60, corner 15.30
antenna plane (PCB top 6.6) to lid underside 8.65 mm, to lid top 9.85; PCB top to floor outer face 6.6 mm
label on the floor outer face is inside the 15 mm box vertically (6.6 mm below the antenna)
LED centres at R 20 (ring phase 0 deg): nearest distance to antenna rectangle 9.54 mm (user figure about 11 mm)
ring phase 11.25 deg: 9.47 mm; the LED edge (2.0 mm package) is about 1 mm closer

=== (e) printed mass, ESTIMATE (walls and plates solid, density PETG 1.27, ASA 1.07 g/cm3; PCB and parts excluded) ===
OLD 55x28: base 12.0 cm3, lid 3.1 cm3; PETG 19.2 g; base ASA + lid PETG 16.8 g
NEW 53x16.5: base 7.9 cm3, lid 2.8 cm3; PETG 13.6 g; base ASA + lid PETG 12.0 g
(infill reductions in floor/plate are not modelled; real mass is likely lower; weigh the first print)
```

### 8.5 Script `adr_scores_v2.py`

```python
#!/usr/bin/env python3
"""ADR-0011 weighted decision tables, re-run 2026-11-04 with resolved dimensions (changed scores: A crit 4 3->4, C crit 4 2->3, P1 thermal 3->2). Scores are the author's judgement (0-5), not measured.
Run: python3 -I adr_scores_v2.py"""
def table(title, crit, opts, gate_idx):
    w = [c[1] for c in crit]
    print(f"== {title}: weights {w}, sum {sum(w)}, max {5*sum(w)}")
    for name, sc in opts.items():
        assert len(sc) == len(crit), name
        assert all(0 <= s <= 5 for s in sc)
        tot = sum(a * b for a, b in zip(w, sc))
        gate = [crit[i][0] for i, lim in gate_idx if sc[i] <= lim]
        print(f"  {name:48s} sum {tot:4d} ({100*tot/(5*sum(w)):5.1f} %)" + (f"  EXCLUDED by gate: {gate}" if gate else ""))
    print()

C = [("1 Diffusion: closed band, no point source (MECH-002)", 5),
     ("2 Antenna friendliness: no metal near antenna (MECH-003)", 5),
     ("3 Thermal and material margin (MECH-005)", 4),
     ("4 Size and fixed label area (MECH-001, MECH-006)", 4),
     ("5 USB-C and button access (MECH-004)", 4),
     ("6 Assembly without tools or common screws, reopening (DFx)", 4),
     ("7 Printability, tolerance sensitivity (DFx 1)", 4),
     ("8 Test and programming access (DFx 3, HW-006)", 3),
     ("9 Part count and print cost", 2)]
concepts = {
 "A clamshell + separate diffuser ring (3 parts)":      [5, 4, 4, 4, 4, 3, 3, 4, 2],
 "B opaque base + one translucent lid (2 parts)":        [4, 5, 3, 5, 4, 4, 4, 4, 5],
 "C sphere, two snap-fit halves":                        [3, 5, 3, 3, 3, 4, 2, 3, 4],
 "D do nothing (bare board, no housing)":                [0, 5, 5, 0, 3, 5, 5, 5, 5],
}
table("Concept table", C, concepts, gate_idx=[(0, 0), (3, 0)])

# sensitivity: +-1 on every score of the top two, check ranking holds / weights +-1
import itertools
w0 = [c[1] for c in C]
def total(w, s): return sum(a*b for a, b in zip(w, s))
a, b = concepts["A clamshell + separate diffuser ring (3 parts)"], concepts["B opaque base + one translucent lid (2 parts)"]
print("B - A =", total(w0, b) - total(w0, a))
# worst-case: each criterion weight changed by -1/+1 one at a time
flip = []
for i in range(len(w0)):
    for d in (-1, 1):
        w = list(w0); w[i] = max(1, w[i] + d)
        if total(w, b) <= total(w, a): flip.append((C[i][0][:30], d))
print("single weight +-1 changes that make A >= B:", flip or "none")
# score shift: every B score -1 on one criterion
flip2 = []
for i in range(len(w0)):
    bb = list(b); bb[i] = max(0, bb[i]-1)
    if total(w0, bb) <= total(w0, a): flip2.append(C[i][0][:30])
print("lowering one B score by 1 makes A >= B for:", flip2 or "none")
# diffuser weight 5 -> A advantage criterion: how much must criterion-1 weight rise for A to tie B
for w1 in range(5, 15):
    w = list(w0); w[0] = w1
    if total(w, a) >= total(w, b):
        print("A ties/overtakes B when weight of criterion 1 reaches", w1); break
print()

P = [("1 Dimensional accuracy for fits (USB-C window, spigot)", 4),
     ("2 Thermal margin: HDT vs MECH-005 (needs data per product)", 5),
     ("3 Diffuser quality possible in this process", 4),
     ("4 Availability at the owner and lead time (UNKNOWN: owner question)", 4),
     ("5 Strength of snap/screw features, reopening x100", 3),
     ("6 Non-conductive, no metal fill (MECH-003)", 5),
     ("7 Handling safety, post-processing effort", 3),
     ("8 Cost per housing (prototype, 10 units)", 3)]
procs = {
 "P1 FDM, PETG base + natural PETG diffuser":            [3, 2, 3, 4, 3, 5, 5, 5],
 "P2 FDM, ASA base + natural PETG diffuser":             [3, 4, 3, 3, 3, 5, 3, 4],
 "P3 resin (MSLA), opaque base + clear/white lid":       [5, 2, 4, 3, 2, 5, 2, 3],
 "P4 FDM, PLA (cheapest, common)":                       [3, 1, 3, 5, 3, 5, 5, 5],
 "P5 do nothing (no printed housing)":                   [0, 5, 0, 5, 0, 5, 5, 5],
}
table("Process table", P, procs, gate_idx=[(2, 0), (1, 1)])
w = [c[1] for c in P]
print("P2 - P1 =", total(w, procs["P2 FDM, ASA base + natural PETG diffuser"]) - total(w, procs["P1 FDM, PETG base + natural PETG diffuser"]))
```

Output, copied unchanged:

```text
== Concept table: weights [5, 5, 4, 4, 4, 4, 4, 3, 2], sum 35, max 175
  A clamshell + separate diffuser ring (3 parts)   sum  133 ( 76.0 %)
  B opaque base + one translucent lid (2 parts)    sum  147 ( 84.0 %)
  C sphere, two snap-fit halves                    sum  117 ( 66.9 %)
  D do nothing (bare board, no housing)            sum  122 ( 69.7 %)  EXCLUDED by gate: ['1 Diffusion: closed band, no point source (MECH-002)', '4 Size and fixed label area (MECH-001, MECH-006)']

B - A = 14
single weight +-1 changes that make A >= B: none
lowering one B score by 1 makes A >= B for: none

== Process table: weights [4, 5, 4, 4, 3, 5, 3, 3], sum 31, max 155
  P1 FDM, PETG base + natural PETG diffuser        sum  114 ( 73.5 %)
  P2 FDM, ASA base + natural PETG diffuser         sum  111 ( 71.6 %)
  P3 resin (MSLA), opaque base + clear/white lid   sum  104 ( 67.1 %)
  P4 FDM, PLA (cheapest, common)                   sum  113 ( 72.9 %)  EXCLUDED by gate: ['2 Thermal margin: HDT vs MECH-005 (needs data per product)']
  P5 do nothing (no printed housing)               sum  100 ( 64.5 %)  EXCLUDED by gate: ['3 Diffuser quality possible in this process']

P2 - P1 = -3
```
