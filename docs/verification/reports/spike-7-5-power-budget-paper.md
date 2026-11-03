# Spike 7.5: paper power budget (datasheet values, not measured)

- **Status:** Draft
- **Date:** 2026-11-04
- **Author:** Claude (desk analysis for the owner). Analysis only. Nothing was measured. Not reviewed.
- **Related:** SYS-001, SYS-020, HW-003, HW-004, RISK-003, RISK-004, ADR-0004 (items 2, 3, 4), plan 02 spike 7.5
- **Script:** reproduced in section 3. Source file kept in the session scratchpad only.

## 1. Purpose

Find out, from manufacturer documents, how much of the [500] mA USB budget is left for the 16 LEDs after the Wi-Fi module and the supply loss.
Give a number where the inputs exist. Give a range where an input is missing. Say where nothing was found.
This report does not replace the bench measurement in spike 7.5. It tells us what to expect and which inputs to measure first.

## 2. Inputs

Status codes: **read** = I opened the document and read the value in its text or table (PDF downloaded, text extracted; two tables read from a page image). **snippet** = seen only in a search result, document not read. **not found** = no value found. **assumption** = my choice, not from a document.
Search-engine and fetch summaries were not used as values unless the status says snippet.

### 2.1 ESP32-C3 and ESP32-C3-MINI-1 (3.3 V rail)

| ID | Value | Unit | Condition | Source | Status |
|----|-------|------|-----------|--------|--------|
| E1 | 350 | mA peak | Wi-Fi TX, 802.11b 1 Mbps, +20.5 dBm, 100 % duty, 3.3 V, 25 C. MINI-1 Table 6-4 | https://documentation.espressif.com/esp32-c3-mini-1_datasheet_en.pdf (v2.2) | read |
| E2 | 295 | mA peak | TX 802.11g 54 Mbps, +18 dBm. Same table | same | read |
| E3 | 290 | mA peak | TX 802.11n HT20 MCS7, +17.5 dBm; also HT40 MCS7 at +17 dBm. Same table | same | read |
| E4 | 82 | mA peak | RX 802.11b/g/n HT20 (HT40: 84 mA). RX is rated with peripherals off and CPU idle | same | read |
| E5 | 335 / 285 / 276 / 278 / 84 / 87 | mA peak | Chip-only figures, ESP32-C3 Table 5-7: TX 11b 1 Mbps +21 dBm / 11g 54 Mbps +19 dBm / HT20 MCS7 +18.5 dBm / HT40 MCS7 +18.5 dBm / RX HT20 / RX HT40. TX at 100 % duty | https://documentation.espressif.com/esp32-c3_datasheet_en.pdf (v2.4) | read |
| E6 | 23 (28) | mA typ | Modem-sleep, 160 MHz, CPU running, peripheral clocks disabled (enabled). Wi-Fi clock gated. ESP32-C3 Table 5-8 and MINI-1 Table 6-6 | both datasheets | read |
| E7 | 17 (22) | mA typ | Modem-sleep, 80 MHz, CPU running, peripherals off (on) | both | read |
| E8 | 16 (21) / 13 (18) | mA typ | Modem-sleep, CPU idle, 160 MHz / 80 MHz, peripherals off (on) | both | read |
| E9 | 130 / 5 / 1 | uA typ | Light-sleep / deep-sleep / power off. Table 5-9 | ESP32-C3 datasheet | read |
| E10 | 3.0 / 3.3 / 3.6 | V min/typ/max | Supply voltage VDD33 (MINI-1 Table 6-2); VDD3P3 (C3 Table 5-2) | both | read |
| E11 | at least 0.5 | A | "Current delivered by external power supply" (MINI-1 Table 6-2); "Cumulative input current" (C3 Table 5-2) | both | read |
| E12 | 0.8 x VDD = 2.64 | V min | GPIO high-level output VOH at VDD 3.3 V (C3 Table 5-4). Source current rating IOH 40 mA at VOH >= 2.64 V | ESP32-C3 datasheet | read |
| E13 | TX current at lower power levels (for example +10 dBm) | mA | Datasheets give one power level per rate only | both | not found |
| E14 | TX average current at a realistic duty cycle (for example TLS client, 1 packet per second) | mA | Datasheets give 100 % duty only | both | not found |
| E15 | Brown-out detector threshold | V | Block diagram names a brown-out detector; no threshold value located | ESP32-C3 datasheet | not found |
| E16 | Whether the TX peak figure includes the CPU current | n/a | Not stated. The script adds E6 (28 mA) on top, which may double count | both | not found |
| E17 | Power-up and Wi-Fi calibration inrush current | mA | No value located | both | not found |

Note: the module datasheet asks for a supply that can deliver at least 0.5 A (E11). That is the whole USB budget.

### 2.2 LEDs

Parts found. Each row is a different part and a different document. The ring needs 2020 or 3535. Not every row is that package.

| ID | Part (package) | Value | Unit | Condition | Source | Status |
|----|----------------|-------|------|-----------|--------|--------|
| L1 | WS2812C-2020 (2020), World Semi, rev V1.0 2019-03-01 | 5 | mA per channel | "5mA operating current per channel" (features); LED characteristics tested at 5 mA | https://akizukidenshi.com/goodsaffix/ws2812c-2020.pdf | read |
| L2 | WS2812C-2020 | < 0.5 | mA | "Quiescent Current: <0.5mA" (LED characteristics table header). I treat it as a maximum | same | read |
| L3 | WS2812C-2020 | 3.7 to 5.3 | V | Absolute maximum VDD. Recommended operating range | same | read (abs max); not found (recommended) |
| L4 | WS2812C-2020 | VIH 2.7 min, VIL 0.7 max | V | TA 25 C, VDD 5 V, pin DIN | same | read |
| L5 | WS2812C-2020 | R 150/200/250, G 400/420/500, B 50/60/100 | mcd min/typ/max | At 5 mA per channel | same | read |
| L6 | SK6812MINI-E (3.2 x 2.8 x 1.78 mm, not 2020 or 3535), OPSCO rev 02 2019-01-18 | 12 (code "12 mA version"; rise-time test at 13 mA) | mA per channel | Name table: "5/12MA current version". A separate 5 mA version (SK6805MINI-E) is in the same document. The sheet does not say "12 mA per channel" in those words. I took the code as the channel current | https://cdn-shop.adafruit.com/product-files/4960/4960_SK6812MINI-E_REV02_EN.pdf | read (interpretation) |
| L7 | SK6812MINI-E | 1 | mA typ | "Static power consumption" IDD | same | read |
| L8 | SK6812MINI-E | 3.7 to 5.5 (abs max); chip supply 5.2 | V | Section 8 and 10 | same | read |
| L9 | SK6812MINI-E | VIH 0.7 x VDD min, VIL 0.3 x VDD max | V | VDD 5.0 V, so VIH 3.5 V | same | read |
| L10 | SK6812MINI (3535 name; 3.5 x 3.7 x 0.95 mm), Shenzhen BTF-Lighting spec rev 01 | per-channel current | mA | Not stated in the electrical tables. Only "IOUT = 13 mA" appears as the rise/fall test condition | https://cdn.shopify.com/s/files/1/0023/2960/8292/files/SK6812-3535LEDMINI.pdf | not found |
| L11 | SK6812MINI (3535) | 1 | mA typ | Static power consumption IDD. Tables are images; read from the page image | same | read |
| L12 | SK6812MINI (3535) | VIH 3.4 min, VIL 1.6 max | V | VDD 5.0 V | same | read |
| L13 | SK6812MINI (3535) | 3.5 to 5.5 | V | Absolute maximum VDD | same | read |
| L14 | XL-2020RGBC-SK6812B (2.0 x 2.0 x 0.65 mm); SK6812-compatible 2020 part from a third party (maker not identified in the text I read) | 5 | mA per channel | "R/G/B drive current ILED01", typ | https://atta.szlcsc.com/upload/public/pdf/source/20250225/502D47C6FF2933F7B2561BD85C0A5986.pdf | read |
| L15 | XL-2020RGBC-SK6812B | 0.5 | mA typ | "Operating current" IDD | same | read |
| L16 | XL-2020RGBC-SK6812B | VIH 0.5 x VDD min, VIL 0.25 x VDD max; supply 3.5 to 5.5 V (abs max) | V | VDD not given for the threshold; at 5 V, VIH 2.5 V | same | read |
| L17 | XL-2020RGBC-SK6812B | R 50-150, G 200-400, B 50-150 | mcd | IF = 5 mA | same | read |
| L18 | WS2812B (5050, not 2020), copy of the original sheet | VIH 0.7 x VDD min, VIL 0.3 x VDD max, VDD 4.5-5.5 V; abs max VDD 3.5 to 5.3 V | V | Per-channel current and quiescent current | https://cdn-shop.adafruit.com/datasheets/WS2812B.pdf | read (thresholds, abs max); not found (per-channel current, quiescent) |
| L19 | SK6812 5050 (LED COLOR rev 01) and SK6812-012 5050 (OPSCO), reference only | IDD 1 mA / 0.65 mA typ; VIH 3.4 V (first one); SK6812-012 is a "12 mA version" | mA | 5050 package, not usable on the ring | https://cdn-shop.adafruit.com/product-files/1138/SK6812+LED+datasheet+.pdf ; https://www.ledyilighting.com/wp-content/uploads/2025/02/SK6812-datasheet.pdf | read |
| L20 | SK6812-2020 (OPSCO, also called SK6812-EC20) | all values | | Only a Scribd search snippet seen; no usable document opened | https://www.scribd.com/document/454559809/SK6812-EC20-LED-Datasheet | snippet (not read), so not found |
| L21 | Opsco or any 2020 or 3535 part: recommended operating VDD range, thermal derating of current | | | Not stated beyond the absolute maximum values above | various | not found |

### 2.3 USB and Type-C source limits

I did not read the USB-IF specifications (USB 2.0, USB 3.x, BC 1.2, Type-C). The values below come from two TI documents that quote them. Treat them as secondary sources.

| ID | Value | Unit | Condition | Source | Status |
|----|-------|------|-----------|--------|--------|
| U1 | 100 / 500 / 900 | mA | Standard downstream port (SDP): 100 mA (USB 2.0), 500 mA (USB 2.0), 900 mA (USB 3.0). TI SLUAA94 Table 1-1 | https://www.ti.com/lit/pdf/sluaa94 | read (secondary) |
| U2 | 500 to 1500 / 900 to 1500 | mA | Dedicated charging port (DCP, wall adapter) / charging downstream port (CDP). Same table | same | read (secondary) |
| U3 | 100 | mA | Charger input limit when the host is not enabled or D+/D- detection times out. SLUAA94 section 4 (BQ24190 table) | same | read (secondary) |
| U4 | 5.1 (4.6 to 5.6) | kohm | Sink pull-down Rd. TUSB321 datasheet SLLSEO6C, section 6 | https://www.ti.com/lit/gpn/tusb321 | read (secondary) |
| U5 | 80 / 180 / 330 | uA typ | Source pull-up current for default / 1.5 A / 3 A advertisement | same | read (secondary) |
| U6 | 0.20 / 0.66 / 1.23 | V typ | Sink CC voltage thresholds for default / 1.5 A / 3 A advertisement | same | read (secondary) |
| U7 | Default USB power is 500 mA (USB 2.0) or 900 mA (USB 3.x); 1.5 A and 3 A via Rp | mA | Search snippet of TI TUSB320 datasheet | https://ti.com/document-viewer/TUSB320/datasheet/GUID-3BF156CA-3E11-436F-8D41-07D491DBA492 | snippet |
| U8 | Rp to 5 V of 56 kohm (default), 22 kohm (1.5 A), 10 kohm (3 A) | kohm | Search snippet of Microchip page; fetch timed out | https://developerhelp.microchip.com/xwiki/bin/view/applications/usb/typec-features/cc-vconn-signals/ | snippet |
| U9 | Some hosts give 100 mA only, some give 500 mA without enumeration | mA | Search snippet of an Analog Devices article | https://www.analog.com/cn/technical-articles/overview-of-usb-battery-charging-revision-12-and-the-important-role-of-charger-detectors.html | snippet |
| U10 | VBUS voltage tolerance at the sink connector | V | Not located | | not found |
| U11 | LDO and buck efficiency | % | Not looked up. Buck 85 % is the task input (assumption). LDO input current equals output current, so LDO efficiency is 3.3/5 = 66 % by arithmetic | n/a | assumption |
| U12 | Margin on the 3.3 V sum | 20 % | Chosen by me for the script. Covers part spread, temperature, supply tolerance | n/a | assumption |

## 3. Method

1. 3.3 V worst case: `I33 = (I_TX_peak + I_CPU) x (1 + margin)`. Inputs E1 (350 mA), E6 (28 mA, CPU running, peripherals on) and the 20 % margin (U12). This assumes TX at 100 % duty plus a running CPU. That is the HW-004 and RISK-004 case. It may double count the CPU (E16). Other 3.3 V loads (data buffer, regulator quiescent current) are not included because no part is chosen. They would only reduce the LED share.
2. 5 V side. LDO: `I5 = I33`. Buck at 85 %: `I5 = I33 x 3.3 / (5 x 0.85)`. Efficiency is assumed constant.
3. LED share: `I_LED = 500 mA - I5`. Per-LED average: `I_LED / 16`.
4. Brightness fraction of full white: `(I_per_LED - I_dark) / (3 x I_channel)`. The LEDs use constant-current PWM, so average current is proportional to duty. A fraction of 1.0 means R, G and B each at 255.
5. Dark current: `16 x I_dark`. It is part of every result above because it is subtracted from the per-LED allowance.
6. LED variants: A = WS2812C-2020 (5 mA per channel, 0.5 mA dark). B = SK6812MINI-E (12 mA, 1 mA). C = SK6812MINI 3535 (per-channel current not found, shown as a range 5 to 13 mA; 1 mA dark). The XL-2020 part (L14, L15) has the same numbers as A, so it is not run separately.
7. Sensitivity: each input changed by -20 % and +20 %, one at a time, for variant A with TX at 100 % duty. Efficiency is capped at 100 %.

Script (Python 3, standard library only, run with `python3 -I power_budget.py`):

```python
#!/usr/bin/env python3
"""Spike 7.5 paper power budget (busy-light). Analysis only, nothing measured.

All inputs are in the INPUTS dict with their source tag. Values marked
ASSUMPTION are not from a datasheet. Run: python3 power_budget.py
"""

N_LED = 16
USB_LIMIT_MA = 500.0           # SYS-020 working value [500]
V_IN, V_RAIL = 5.0, 3.3

INPUTS = {
    # 3.3 V rail, ESP32-C3-MINI-1 datasheet v2.2, Table 6-4 / 6-6 (read)
    "i_tx_peak": 350.0,        # mA, 802.11b 1 Mbps @20.5 dBm, 100 % duty
    "i_tx_ht20_mcs7": 290.0,   # mA, 802.11n HT20 MCS7 @17.5 dBm
    "i_rx": 82.0,              # mA, 802.11b/g/n HT20 RX
    "i_cpu": 28.0,             # mA, modem-sleep 160 MHz CPU running, periph clocks on
    "margin": 0.20,            # ASSUMPTION: 20 % on the 3.3 V sum (spread, voltage, temp)
    "eta_buck": 0.85,          # task input (not a datasheet value)
}

# LED variants: per-channel full-drive current and dark current, mA
# (lo, hi) shown where the datasheet gives no value.
LED_VARIANTS = {
    "A WS2812C-2020 (read)":           {"i_ch": (5.0, 5.0),   "i_q": (0.5, 0.5)},
    "B SK6812MINI-E 12 mA code (read)": {"i_ch": (12.0, 12.0), "i_q": (1.0, 1.0)},
    # 3535 SK6812MINI: per-channel current NOT FOUND; bound by 5..13 mA
    # (13 mA is only the IOUT test condition of the rise/fall time). IDD 1 mA read.
    "C SK6812MINI 3535 (i_ch not found)": {"i_ch": (5.0, 13.0), "i_q": (1.0, 1.0)},
}


def rail_33(i_tx, i_cpu, margin):
    """Worst-case 3.3 V rail current. TX peak plus CPU, then margin."""
    return (i_tx + i_cpu) * (1.0 + margin)


def in_5v(i33, supply, eta):
    """5 V side current drawn by the 3.3 V rail."""
    if supply == "LDO":
        return i33                       # linear: same current in and out
    return i33 * V_RAIL / (V_IN * eta)   # buck


def led_results(budget_5v, i_ch, i_q):
    """Return (per-LED avg mA, brightness fraction of full white)."""
    per_led = max(budget_5v, 0.0) / N_LED
    frac = max(per_led - i_q, 0.0) / (3.0 * i_ch)
    return per_led, min(frac, 1.0)


def budget_for(i_tx, i_cpu, margin, supply, eta, limit):
    i33 = rail_33(i_tx, i_cpu, margin)
    i5 = in_5v(i33, supply, eta)
    return i33, i5, limit - i5


def main():
    p = INPUTS
    print("=== 1. 3.3 V rail and 5 V logic share ===")
    scen = {
        "TX 11b peak + CPU": p["i_tx_peak"],
        "TX HT20 MCS7 + CPU": p["i_tx_ht20_mcs7"],
        "RX + CPU": p["i_rx"],
    }
    for name, itx in scen.items():
        i33 = rail_33(itx, p["i_cpu"], p["margin"])
        for supply in ("LDO", "buck"):
            i5 = in_5v(i33, supply, p["eta_buck"])
            print(f"{name:20s} {supply:4s}  I3v3={i33:6.1f} mA  I5v(logic)={i5:6.1f} mA"
                  f"  left for LEDs={USB_LIMIT_MA - i5:6.1f} mA")
    print(f"LDO dissipation at TX peak: {(V_IN - V_RAIL) * rail_33(p['i_tx_peak'], p['i_cpu'], p['margin']):.0f} mW")
    print(f"HW-004 check: 1.5 x unmargined sum = {1.5 * (p['i_tx_peak'] + p['i_cpu']):.0f} mA "
          f"(rail must deliver at least this)")

    print("\n=== 2. LED budget, per-LED current, brightness fraction (TX 11b peak, 500 mA) ===")
    for supply in ("LDO", "buck"):
        _, i5, left = budget_for(p["i_tx_peak"], p["i_cpu"], p["margin"], supply, p["eta_buck"], USB_LIMIT_MA)
        print(f"-- {supply}: left for LEDs {left:.1f} mA")
        for vname, v in LED_VARIANTS.items():
            lo_ch, hi_ch = v["i_ch"]
            res = [led_results(left, ic, v["i_q"][0]) for ic in (lo_ch, hi_ch)]
            per_led = res[0][0]
            f_lo, f_hi = sorted(r[1] for r in res)
            rng = f"{f_lo*100:5.1f} %" if f_lo == f_hi else f"{f_lo*100:5.1f} .. {f_hi*100:5.1f} %"
            print(f"   {vname:38s} per-LED avg {per_led:5.2f} mA  full-white fraction {rng}"
                  f"{'   <- rests on NOT FOUND i_ch' if lo_ch != hi_ch else ''}")

    print("\n=== 2b. Same, but RX + CPU only (no TX peak in the budget) ===")
    for supply in ("LDO", "buck"):
        _, i5, left = budget_for(p["i_rx"], p["i_cpu"], p["margin"], supply, p["eta_buck"], USB_LIMIT_MA)
        print(f"-- {supply}: left for LEDs {left:.1f} mA")
        for vname, v in LED_VARIANTS.items():
            lo_ch, hi_ch = v["i_ch"]
            res = [led_results(left, ic, v["i_q"][0]) for ic in (lo_ch, hi_ch)]
            f_lo, f_hi = sorted(r[1] for r in res)
            rng = f"{f_lo*100:5.1f} %" if f_lo == f_hi else f"{f_lo*100:5.1f} .. {f_hi*100:5.1f} %"
            print(f"   {vname:38s} per-LED avg {res[0][0]:5.2f} mA  full-white fraction {rng}")

    print("\n=== 3. Dark current of 16 LEDs ===")
    for vname, v in LED_VARIANTS.items():
        print(f"   {vname:38s} {N_LED * v['i_q'][0]:5.1f} mA")
    print("   LED full-white current (16 LEDs, no limit):")
    for vname, v in LED_VARIANTS.items():
        lo = N_LED * (v["i_q"][0] + 3 * v["i_ch"][0])
        hi = N_LED * (v["i_q"][1] + 3 * v["i_ch"][1])
        print(f"   {vname:38s} {lo:6.0f} .. {hi:6.0f} mA")

    print("\n=== 4. Sensitivity: +-20 % on each input (buck, TX 11b peak, variant A) ===")
    base = dict(i_tx=p["i_tx_peak"], i_cpu=p["i_cpu"], margin=p["margin"], eta=p["eta_buck"],
                limit=USB_LIMIT_MA, i_ch=5.0, i_q=0.5)

    def metric(d, supply="buck"):
        _, _, left = budget_for(d["i_tx"], d["i_cpu"], d["margin"], supply, d["eta"], d["limit"])
        per_led, frac = led_results(left, d["i_ch"], d["i_q"])
        return left, per_led, frac

    for supply in ("buck", "LDO"):
        b = metric(base, supply)
        print(f"-- {supply} base: left={b[0]:.1f} mA  per-LED={b[1]:.2f} mA  fraction={b[2]*100:.1f} %")
        for key in base:
            row = []
            for k in (0.8, 1.2):
                d = dict(base)
                d[key] = base[key] * k
                if key == "eta":
                    d[key] = min(d[key], 1.0)
                m = metric(d, supply)
                row.append(f"{m[0]:6.1f} mA / {m[2]*100:5.1f} %")
            if supply == "LDO" and key == "eta":
                row = ["(no effect)", "(no effect)"]
            print(f"   {key:7s} -20 %: {row[0]}   +20 %: {row[1]}   (left for LEDs / fraction)")
        # all-bad corner
        bad = dict(base, i_tx=base["i_tx"] * 1.2, i_cpu=base["i_cpu"] * 1.2, margin=base["margin"] * 1.2,
                   limit=base["limit"], i_ch=base["i_ch"], i_q=base["i_q"] * 1.2)
        if supply == "buck":
            bad["eta"] = base["eta"] * 0.8
        m = metric(bad, supply)
        print(f"   all supply-side inputs 20 % worse: left={m[0]:.1f} mA  fraction={m[2]*100:.1f} %")


if __name__ == "__main__":
    main()
```

## 4. Results

Output of the script above, copied unchanged:

```text
=== 1. 3.3 V rail and 5 V logic share ===
TX 11b peak + CPU    LDO   I3v3= 453.6 mA  I5v(logic)= 453.6 mA  left for LEDs=  46.4 mA
TX 11b peak + CPU    buck  I3v3= 453.6 mA  I5v(logic)= 352.2 mA  left for LEDs= 147.8 mA
TX HT20 MCS7 + CPU   LDO   I3v3= 381.6 mA  I5v(logic)= 381.6 mA  left for LEDs= 118.4 mA
TX HT20 MCS7 + CPU   buck  I3v3= 381.6 mA  I5v(logic)= 296.3 mA  left for LEDs= 203.7 mA
RX + CPU             LDO   I3v3= 132.0 mA  I5v(logic)= 132.0 mA  left for LEDs= 368.0 mA
RX + CPU             buck  I3v3= 132.0 mA  I5v(logic)= 102.5 mA  left for LEDs= 397.5 mA
LDO dissipation at TX peak: 771 mW
HW-004 check: 1.5 x unmargined sum = 567 mA (rail must deliver at least this)

=== 2. LED budget, per-LED current, brightness fraction (TX 11b peak, 500 mA) ===
-- LDO: left for LEDs 46.4 mA
   A WS2812C-2020 (read)                  per-LED avg  2.90 mA  full-white fraction  16.0 %
   B SK6812MINI-E 12 mA code (read)       per-LED avg  2.90 mA  full-white fraction   5.3 %
   C SK6812MINI 3535 (i_ch not found)     per-LED avg  2.90 mA  full-white fraction   4.9 ..  12.7 %   <- rests on NOT FOUND i_ch
-- buck: left for LEDs 147.8 mA
   A WS2812C-2020 (read)                  per-LED avg  9.24 mA  full-white fraction  58.2 %
   B SK6812MINI-E 12 mA code (read)       per-LED avg  9.24 mA  full-white fraction  22.9 %
   C SK6812MINI 3535 (i_ch not found)     per-LED avg  9.24 mA  full-white fraction  21.1 ..  54.9 %   <- rests on NOT FOUND i_ch

=== 2b. Same, but RX + CPU only (no TX peak in the budget) ===
-- LDO: left for LEDs 368.0 mA
   A WS2812C-2020 (read)                  per-LED avg 23.00 mA  full-white fraction 100.0 %
   B SK6812MINI-E 12 mA code (read)       per-LED avg 23.00 mA  full-white fraction  61.1 %
   C SK6812MINI 3535 (i_ch not found)     per-LED avg 23.00 mA  full-white fraction  56.4 .. 100.0 %
-- buck: left for LEDs 397.5 mA
   A WS2812C-2020 (read)                  per-LED avg 24.84 mA  full-white fraction 100.0 %
   B SK6812MINI-E 12 mA code (read)       per-LED avg 24.84 mA  full-white fraction  66.2 %
   C SK6812MINI 3535 (i_ch not found)     per-LED avg 24.84 mA  full-white fraction  61.1 .. 100.0 %

=== 3. Dark current of 16 LEDs ===
   A WS2812C-2020 (read)                    8.0 mA
   B SK6812MINI-E 12 mA code (read)        16.0 mA
   C SK6812MINI 3535 (i_ch not found)      16.0 mA
   LED full-white current (16 LEDs, no limit):
   A WS2812C-2020 (read)                     248 ..    248 mA
   B SK6812MINI-E 12 mA code (read)          592 ..    592 mA
   C SK6812MINI 3535 (i_ch not found)        256 ..    640 mA

=== 4. Sensitivity: +-20 % on each input (buck, TX 11b peak, variant A) ===
-- buck base: left=147.8 mA  per-LED=9.24 mA  fraction=58.2 %
   i_tx    -20 %:  213.0 mA /  85.4 %   +20 %:   82.6 mA /  31.1 %   (left for LEDs / fraction)
   i_cpu   -20 %:  153.0 mA /  60.4 %   +20 %:  142.6 mA /  56.1 %   (left for LEDs / fraction)
   margin  -20 %:  159.5 mA /  63.1 %   +20 %:  136.1 mA /  53.4 %   (left for LEDs / fraction)
   eta     -20 %:   59.7 mA /  21.6 %   +20 %:  200.6 mA /  80.3 %   (left for LEDs / fraction)
   limit   -20 %:   47.8 mA /  16.6 %   +20 %:  247.8 mA /  99.9 %   (left for LEDs / fraction)
   i_ch    -20 %:  147.8 mA /  72.8 %   +20 %:  147.8 mA /  48.5 %   (left for LEDs / fraction)
   i_q     -20 %:  147.8 mA /  58.9 %   +20 %:  147.8 mA /  57.6 %   (left for LEDs / fraction)
   all supply-side inputs 20 % worse: left=-45.9 mA  fraction=0.0 %
-- LDO base: left=46.4 mA  per-LED=2.90 mA  fraction=16.0 %
   i_tx    -20 %:  130.4 mA /  51.0 %   +20 %:  -37.6 mA /   0.0 %   (left for LEDs / fraction)
   i_cpu   -20 %:   53.1 mA /  18.8 %   +20 %:   39.7 mA /  13.2 %   (left for LEDs / fraction)
   margin  -20 %:   61.5 mA /  22.3 %   +20 %:   31.3 mA /   9.7 %   (left for LEDs / fraction)
   eta     -20 %: (no effect)   +20 %: (no effect)   (left for LEDs / fraction)
   limit   -20 %:  -53.6 mA /   0.0 %   +20 %:  146.4 mA /  57.7 %   (left for LEDs / fraction)
   i_ch    -20 %:   46.4 mA /  20.0 %   +20 %:   46.4 mA /  13.3 %   (left for LEDs / fraction)
   i_q     -20 %:   46.4 mA /  16.7 %   +20 %:   46.4 mA /  15.3 %   (left for LEDs / fraction)
   all supply-side inputs 20 % worse: left=-62.5 mA  fraction=0.0 %
```

### 4.1 Summary table (TX at 100 % duty, 802.11b peak, USB limit 500 mA)

| Item | LDO from 5 V | Buck, 85 % | Rests on |
|------|--------------|------------|----------|
| Worst-case 3.3 V rail current | 454 mA | 454 mA | E1, E6 read; 20 % margin assumed |
| 5 V current of the logic part | 454 mA | 352 mA | plus 85 % assumed for the buck |
| Left for the 16 LEDs | 46 mA | 148 mA | same |
| Per-LED average current | 2.9 mA | 9.2 mA | same |
| Full-white fraction, variant A (WS2812C-2020) | 16 % | 58 % | L1, L2 read |
| Full-white fraction, variant B (SK6812MINI-E) | 5.3 % | 23 % | L6 read by interpretation |
| Full-white fraction, variant C (3535) | **4.9 to 12.7 %** | **21 to 55 %** | **L10 not found; range only** |
| Dark current of 16 LEDs | 8 mA (A), 16 mA (B, C) | same | L2, L7, L11 read |
| LED current at full white, no limit | A 248 mA, B 592 mA, C **256 to 640 mA** | same | C rests on L10 not found |

Other scenarios from the same script (TX not at its peak):

| Scenario | Left for LEDs, LDO / buck | Variant A | Variant B |
|----------|---------------------------|-----------|-----------|
| TX HT20 MCS7 (290 mA) + CPU, margin 20 % | 118 / 204 mA | 46 % / 82 % | 18 % / 33 % |
| RX + CPU only (82 mA + 28 mA, margin 20 %) | 368 / 398 mA | 100 % / 100 % | 61 % / 66 % |

The HT20 MCS7 row is not in the script output. I computed it with the same functions, called with a TX current of 290 mA instead of 350 mA.

### 4.2 Reading the results

- With TX at its datasheet peak, an LDO leaves almost nothing for the LEDs. A buck leaves about 150 mA.
- With RX only, a 500 mA budget is enough for 16 WS2812C-2020 LEDs at full white (248 mA unlimited). It is not enough for 16 SK6812MINI-E (592 mA).
- The result depends mostly on one number: how much TX current counts against the budget. The datasheets give only the 100 % duty peak (E13 and E14 not found).
- Luminous intensity check against the SYS-001 working value (100 mcd per LED). This is arithmetic only. It scales the datasheet mcd values linearly with the fraction and ignores colour mixing, viewing angle and temperature. Variant A, sum of R+G+B at 5 mA per channel: 600 mcd min, 680 mcd typ (L5). LDO case at 16.0 %: about 96 mcd (min) to 109 mcd (typ). Buck case at 58.2 %: about 350 to 396 mcd. Variant B sum at 12 mA: 1600 to 2600 mcd (OPSCO table, read). LDO case at 5.3 %: about 85 to 138 mcd. Buck case at 22.9 %: about 366 to 595 mcd. So the 100 mcd working value is marginal with an LDO and met with a buck, on paper.

## 5. Sensitivity (+/- 20 % on each input)

Variant A, TX at 100 % duty. Each cell shows the LED share in mA and the full-white fraction. One input changes at a time.

| Input (base) | Buck: -20 % | Buck: +20 % | LDO: -20 % | LDO: +20 % |
|--------------|-------------|-------------|------------|------------|
| Base | 148 mA / 58.2 % | | 46 mA / 16.0 % | |
| TX peak (350 mA) | 213 mA / 85.4 % | 83 mA / 31.1 % | 130 mA / 51.0 % | -38 mA / 0 % |
| CPU current (28 mA) | 153 mA / 60.4 % | 143 mA / 56.1 % | 53 mA / 18.8 % | 40 mA / 13.2 % |
| Margin (20 %) | 160 mA / 63.1 % | 136 mA / 53.4 % | 62 mA / 22.3 % | 31 mA / 9.7 % |
| Buck efficiency (85 %) | 60 mA / 21.6 % | 201 mA / 80.3 % (efficiency capped at 100 %) | no effect | no effect |
| USB limit (500 mA) | 48 mA / 16.6 % | 248 mA / 99.9 % | -54 mA / 0 % | 146 mA / 57.7 % |
| Channel current (5 mA) | 148 mA / 72.8 % | 148 mA / 48.5 % | 46 mA / 20.0 % | 46 mA / 13.3 % |
| Dark current (0.5 mA) | 148 mA / 58.9 % | 148 mA / 57.6 % | 46 mA / 16.7 % | 46 mA / 15.3 % |
| All supply-side inputs 20 % worse (TX, CPU, margin, dark current, buck efficiency) | -46 mA / 0 % | | -63 mA / 0 % | |

What the table says:

- The TX peak, the buck efficiency and the USB limit move the answer most. A 20 % change in them changes the fraction by 25 to 40 points (buck).
- The LDO case has no room. 20 % more TX current, or 20 % less USB limit, leaves no LED current.
- Dark current and CPU current matter little.
- The unlimited-brightness current scales with the channel current, so the fraction moves inversely with it.
- The 20 % worse corner leaves a negative LED share. At that corner the logic part alone exceeds 500 mA.

## 6. What this means for SYS-001, SYS-020 and HW-004 (proposals only)

These are proposals for the owner. I changed no requirement.

**SYS-020 (total current at most [500] mA)**
1. Define what is bounded. Proposal: the average current at the USB connector, with TX at the worst case the product can produce, and all LEDs requested at full white. Say so in the acceptance criteria.
2. The LED limit is a budget for the sum of everything. With a datasheet TX peak and a buck, the LED share is about 150 mA (on paper). With an LDO it is about 46 mA. Decide the supply type first.
3. Two ways to size the limiter. (a) Static: size the LED budget for TX peak. Simple and safe, about 150 mA with a buck. (b) Dynamic: raise the LED budget when the radio is not transmitting. Brighter, but the limiter then depends on radio state. That is more software that can fail (RISK-003). I would start with (a) and use the numbers from the bench to see if (b) is needed.
4. Check if firmware can cap TX rate or TX power in a way that lowers the peak (for example only 11n rates). I did not check this. It is not in the datasheets I read (E13 not found).
5. The [500] mA value equals the USB 2.0 configured limit (U1). A USB 2.0 port gives 100 mA until the device enumerates (U1, U3). If the device has no USB data function, a strict host may give only 100 mA. That is below the module alone. Real hosts often give more (U9, snippet only). Decide whether SYS-020 and HW-003 must state "from a source that supplies at least 500 mA".
6. A Type-C source that advertises 1.5 A or 3 A gives much more room (U2, U5, U6). To use it, the board must read the CC voltage (extra parts, an ADR). I propose to keep [500] mA as the design maximum and decide separately if CC detection is worth it.

**HW-004 (3.3 V rail margin of [1.5] x)**
1. The unmargined sum of E1 and E6 is 378 mA. 1.5 x 378 = 567 mA. The module datasheet asks for a supply that delivers at least 500 mA (E11). The 3.3 V regulator should be rated for at least about 600 mA. This holds if TX at 100 % duty is the design case.
2. An LDO from 5 V at 454 mA dissipates about 770 mW. That heat is inside a printed shell (G10). I propose a buck.
3. HW-004 requires "LEDs at the limited maximum" in the bench test. Use TX at 11b peak, because that gives the highest peak (E1).
4. Bulk capacitance may smooth short TX bursts. I found no data for burst length or for the USB source's ripple tolerance. Keep this for the bench.

**SYS-001 (brightness)**
1. The 100 mcd per LED working value is met on paper with a buck and is marginal with an LDO (section 4.2). It should be set after the bench measurement, as the requirement already says.
2. Level mode (SYS-001, SYS-032) has fewer usable steps if the global scale is small. With the LDO and variant B the scale is about 5 %. That leaves roughly 13 of 255 steps per channel at full request.

**ADR-0004 items 2 to 4 (side findings)**
- Data level (item 2). The ESP32-C3 guarantees VOH of at least 2.64 V (E12) at 3.3 V. WS2812C-2020 needs VIH of at least 2.7 V at VDD 5 V (L4). The two do not overlap by 0.06 V at worst case. XL-2020 needs 0.5 x VDD = 2.5 V (L16). SK6812MINI-E and SK6812MINI (3535) need 3.5 V and 3.4 V (L9, L12). Those two fail with a direct 3.3 V drive. The buffer in item 2 stays unless 7.3 shows otherwise. The threshold also moves with the LED supply: 0.7 x 4.75 V is 3.3 V.
- Part choice (item 6). At the same brightness the 5 mA parts need less current. 16 LEDs at full white take about 250 mA (A) against about 590 mA (B). A 5 mA part makes the limiter less severe. The SK6812MINI-E is neither a 2020 nor a 3535 package, and the 3535 SK6812MINI has no stated channel current (L6, L10).
- Hardware backstop (item 4). The firmware limit protects a budget of about 150 mA (buck, TX peak). A fault that drives all LEDs at full white adds 248 mA (A) to 592 mA (B) on top of the logic. This exceeds 500 mA in every case except A with RX only. This supports keeping item 4 open for the owner. It looks required for variant B.

## 7. What is not known

- Wi-Fi TX current at lower power levels and at a realistic duty cycle (E13, E14). This is the largest uncertainty.
- Whether the TX peak includes the CPU (E16). The script adds both. The result may be about 28 mA too pessimistic.
- Brown-out threshold, power-up inrush, flash current during TX (E15, E17).
- Per-channel current of the 3535 SK6812MINI (L10), and the maker's recommended operating VDD range for all LED parts (L3, L21). Variant C is shown as a range for this reason.
- Per-channel current and quiescent current for the original WS2812B copy I read (L18). It is a 5050 package anyway.
- Any OPSCO SK6812-2020 document (L20).
- Whether the part spread or temperature changes LED channel current. Datasheets give typical values only.
- USB-IF specification text itself (U1 to U9 are from TI documents and snippets). VBUS tolerance (U10).
- Real regulator efficiency, regulator quiescent current, and the current of the data buffer and other 3.3 V loads. They are not in the numbers.
- Real behaviour of the product. Nothing here is measured. The bench test with a USB power meter (TC-020, TC-204) is still required.

## 8. Addendum 2026-11-04: higher USB limits (owner decision: allow more if the source advertises it)
Same script (`power_budget.py` as in section 3, unchanged), limit changed to 900 mA and 1350 mA (1500 mA minus the [10] % margin of SYS-020). Inputs and their "not found" gaps are the same as above. Worst case: TX 11b peak, 20 % margin, `i_cpu` 28 mA.

| USB limit | Supply | Left for LEDs (mA) | Per LED (mA) | Full-white fraction A (WS2812C-2020) | B (SK6812MINI-E) | C (3535, range from the not-found `i_ch`) |
|-----------|--------|--------------------|--------------|------------------|----|----|
| 500 | LDO | 46.4 | 2.90 | 16 % | 5 % | 5..13 % |
| 500 | buck 85 % | 147.8 | 9.24 | 58 % | 23 % | 21..55 % |
| 900 | LDO | 446.4 | 27.90 | 100 % | 75 % | 69..100 % |
| 900 | buck 85 % | 547.8 | 34.24 | 100 % | 92 % | 85..100 % |
| 1350 | LDO | 896.4 | 56.03 | 100 % | 100 % | 100 % |
| 1350 | buck 85 % | 997.8 | 62.36 | 100 % | 100 % | 100 % |

(Fractions are capped at 100 %: 16 LEDs at full white need about 250 mA for variant A and about 590 mA for variant B at the datasheet currents, so a source that advertises 1.5 A never forces the limiter to dim.)

Reading:
- With a source that advertises at least 1.5 A the LED budget is not the constraint for any of the three LED types. The limiter is a safety net there.
- The **default case (500 mA)** still decides the minimum design: only 5 to 23 % of full white for variant B with a buck at 500 mA, so any brightness target in SYS-001 must say at which source the target applies.
- A source that advertises 900 mA (USB 3 default) gives full white for variant A and 75 to 92 % for variant B. The decision on SYS-020 uses the advertised value, so 900 mA is covered by the same rule.
- Proposal for SYS-001 (not applied to the requirement text beyond the rationale note): state the brightness criterion at two operating points, the default source (500 mA) and a source advertising 1.5 A.
- Not covered: the 5 V path losses (cable drop), the input capacitor inrush at a higher limit, thermal rise at the higher dissipation (RISK-005), and connector and track ratings (HW-003).
