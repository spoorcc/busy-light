# Stock check: 0.1 % ILIM resistors and hold-off C0G capacitors

Status: Draft. Date of research: 2026-11-05. Author: Claude (agent). Not reviewed. Nothing here is Approved or Accepted, and no part is chosen.
Traces: HW-010, ADR-0010, ADR-0016, RISK-027.
Closes two open items of `owner-decisions-2026-11-05.md` (decisions 1 and 6), partly. Inputs: `analysis-ilim-steps.md`, `analysis-n4-holdoff-capacitor.md`.

## 1. Method and access

- Method: WebSearch (summaries of search results) and WebFetch of single product pages. No browser session, no login, no live parametric search.
- LCSC and JLCPCB search pages are JavaScript pages. A fetch of `https://www.lcsc.com/search?q=...` returned only site navigation. Product detail pages returned part data (value, tolerance, package) but **not stock, price or the JLCPCB basic/extended class** (LCSC C464977, C328427). One JLCPCB page returned the class (extended) but no stock or price.
- Stock and price numbers below come from search result summaries (snapshots of unknown age). They are labelled "search summary". They were not confirmed on the live page. Treat them as hints only.

## 2. What the spike uses today (read from `hw/kicad/spike-gate/src/gen_gate.py`)

| Ref | Value | Footprint |
|---|---|---|
| R_ILIM1 to R_ILIM3 | `PLACEHOLDER` (generator values stay `tbd`) | R_0603 |
| C1 / C1B | 470n C0G 5 % 25 V / 150n C0G 5 % 50 V | C_1206 |

Note: `layout_full.py` and `analysis-n4-holdoff-capacitor.md` still mention a 620 nF placeholder. The generator draws 470n + 150n (= 620 nF). The planned set 220 + 220 + 150 + 33 nF (623 nF) is different from both.

## 3. ILIM resistors (0603, 0.1 %): 47.0 k, 56.9 k, 27.7 k

| Value | E-series | Result | Evidence |
|---|---|---|---|
| 47.0 k, 0.1 %, 0603 | E24 (47 k) | **Available.** JLCPCB C5889717, Yageo RP0603BRD0747KL, 0.1 %, 25 ppm, **Extended** (page read). Search summary: 4900 in stock, USD 0.064 at qty 1. LCSC C328427 (RESI PTFR0603B47K0P9, 0.1 %, 25 ppm, page read; search summary 9654 in stock, USD 0.0552 at 5+). LCSC C394548 (RESI PTFR0603B47K0N9, 10 ppm, search summary 6599 in stock, USD 0.1618 at 5+). | https://jlcpcb.com/partdetail/YAGEO-RP0603BRD0747KL/C5889717 ; https://lcsc.com/product-detail/Chip-Resistor-Surface-Mount_RESI-PTFR0603B47K0P9_C328427.html ; https://lcsc.com/datasheet/lcsc_datasheet_2409280131_RESI-PTFR0603B47K0N9_C394548.pdf |
| 56.9 k, 0.1 %, 0603 | E192 | **No LCSC/JLCPCB listing found** in two searches. Found elsewhere: Yageo RT0603WRD0756K9L (56.9 k, but 0.05 %), Vishay P0603E5692BBWA (0.1 %), both only in search summaries. Neighbours on LCSC: 56.2 k 0.1 % (Yageo AT0603BRD0756K2L, LCSC C855903). | https://www.digikey.jp/en/products/detail/yageo/RT0603BRD0756KL/1072582 ; https://findchips.com/detail/P0603E5692BBWA/Vishay-Intertechnologies ; https://lcsc.com/product-detail/Pre-ordered-RLCs_YAGEO_C855903.html |
| 27.7 k, 0.1 %, 0603 | E192 | **No LCSC/JLCPCB listing found.** Yageo RT0603DRE0727K7L exists as 27.7 k but **0.5 %** (Octopart, DigiKey India; not 0.1 %). Nearby 0.1 %: 27 k (LCSC C326751, C186426), 27.4 k (Yageo RT0603BRE0727K4L at DigiKey). | https://octopart.com/part/yageo-group/RT0603DRE0727K7L ; https://www.lcsc.com/product-detail/C326751.html ; https://www.digikey.dk/en/products/detail/yageo/RT0603BRE0727K4L/6616834 |
| E192 Panasonic ERA-3A family | E192 | A Panasonic datasheet states that E192 values exist as **custom part numbers** on request (so not catalogue stock). The existence of ERA-3AEB2772V and ERA-3AEB5692V as stock parts was **not confirmed**. | https://static.chipdip.ru/lib/839/DOC011839368.pdf |

Conclusion: of the three values only 47.0 k is confirmed purchasable at 0.1 %, and it is extended at JLCPCB. Two E192 values (56.9 k, 27.7 k) have no confirmed JLCPCB/LCSC source. "No listing found" is not proof of absence. The direct LCSC/JLCPCB parametric search must be done by the owner or with a browser.

## 4. Alternative using only E96 / E24 0.1 % parts (derived)

Script: `hw/kicad/spike-gate/sim/ilim_steps.py` (reused unchanged; same assumptions as `analysis-ilim-steps.md`: IOS equations, Rds 0 to 15 ohm, tolerance applied in the worst direction, no leakage).

1. **A single E96 resistor per position does not work, even at 0.1 %.** The script's `search()` over E96 at 0.1 %, 0.25 % and 0.5 % finds no (R1, R3) pair that meets all four HW-010 numbers (623 mA step 1 maximum, 500 mA step 1 minimum, 1366 to 1577 mA step 3). Best E96 0.1 % pairs miss by 1.1 to 1.2 mA (for example 46.4 k / 28.0 k: step 1 maximum 1.1 mA over; 47.5 k / 28.0 k: step 1 minimum 1.2 mA short). This reproduces the E96 1 % result of the existing analysis.
2. **R2 (middle step) is not constrained by HW-010.** Use E96 56.2 k, 0.1 % (LCSC C855903, extended-class not confirmed) or a standard 56 k 0.1 %. 56.2 k gives step 2 935 to 1092 mA (0.1 %, no leakage) against the assumed 850 to 1150 mA window.
3. **R1 = 47.0 k single part** (confirmed, section 3).
4. **R3 = 27.7 k as a series pair of two E96 0.1 % parts: 27.4 k + 301 ohm = 27.701 k.** Computed margins with R1 47.0 k, R2 56.2 k, R3 27.701 k: step 1 minimum +4.2 mA, step 1 maximum +6.4 mA, step 3 minimum +15.0 mA, step 3 maximum +10.4 mA. These are the same as candidate A (the sum of two 0.1 % parts keeps a 0.1 % band; the 301 ohm part adds tolerance in absolute terms only). Alternative pair 24.9 k + 2.67 k = 27.57 k also fits (smaller margin, step 3 maximum +6.0 mA in the best-margin search).
5. Cost: one extra 0603 part and one extra pad pair for R_ILIM3, no new net. Whether 27.4 k 0.1 % and 301 ohm 0.1 % are LCSC/JLCPCB parts was **not checked** (27.4 k 0.1 % was seen only at DigiKey). Extended-class fees apply per distinct extended part in any case.
6. Not changed: the leakage budget (118 nA per off MOSFET) and all the other findings of `analysis-ilim-steps.md`. The margins stay 4 to 15 mA.

Proposal for the owner (not a decision): if a JLCPCB/LCSC listing of 56.9 k and 27.7 k at 0.1 % cannot be confirmed, use R1 47.0 k, R2 56.2 k, R3 27.4 k + 301 ohm (all 0.1 %), after checking the stock of those four values. The alternative of widening HW-010 for 1 % E96 parts stays as listed in `analysis-ilim-steps.md` section 7.

## 5. Hold-off capacitor, C0G 5 %

| Value / size | Result | Evidence |
|---|---|---|
| 220 nF, 1206, 50 V | Listed: LCSC C464977, Murata GRM31C5C1H224JE02L (page read: C0G, 5 %, 50 V, 1206). Search summary: 4470 and 16,970 in stock (two different snapshots), USD 0.3228 at 5+, 0.1741 at 2000+. Class not shown. | https://www.lcsc.com/product-detail/C464977.html |
| 150 nF, 1206, 50 V | Murata GRM31C5C1H154JE02L exists (DigiKey listing, 17 week lead time on one listing). **No LCSC/JLCPCB listing found.** LCSC lists TDK C4532C0G1H154JT000N (1812, 150 nF C0G 5 % 50 V) with **stock zero** (search summary). | https://www.digikey.it/en/products/detail/murata-electronics/GRM31C5C1H154JE02L/18683861 ; https://datasheet.lcsc.com/lcsc/1912111437_TDK-C4532C0G1H154JT000N_C342306.pdf |
| 33 nF, 1206 | Listed: LCSC C3909605, Yageo CC1206JRNPO9BN333. Search summary: about 2225 in stock, about USD 0.15 at 2500+. Also 0805: TDK C2012C0G1H333JT000N (C76628, about 29,480 in stock) and Murata GRM2165C1H333JA01D (C1518212, about 5230). Class not shown. | https://www.lcsc.com/product-detail/C3909605.html ; https://www.lcsc.com/product-detail/C1518212.html |
| 470 nF C0G, 1206/1210 (current C1) | **No such part found.** 470 nF in 1206/1210 appears only as X7R (for example LCSC C309505). Not suitable (X7R is excluded by `analysis-n4-holdoff-capacitor.md`). | https://www.lcsc.com/product-detail/C309505.html |

Conclusions:
- The generator's 470n C0G part (C1) is probably not purchasable; the 150n C0G (C1B) is not confirmed at LCSC/JLCPCB. The existing generator set is therefore at risk of having no source. Not changed here.
- 220 nF and 33 nF C0G are confirmed listed at LCSC. 150 nF is the gap.
- Substitute for the 150 nF part (derived, uses the formula of `analysis-n4-holdoff-capacitor.md` section 2: tD min = 357.6 kohm x C x (1 - 5.6 %); tD max = 875.6 kohm x C x (1 + 5.6 %)): 220 + 220 + 100 + 68 nF (608 nF) is in the existing candidate table (205 to 562 ms). Whether 100 nF and 68 nF C0G 1206 are in stock at LCSC was **not checked** (the earlier report saw only 68 nF 0603 listings). Another option from the same table: 6 x 100 nF.
- Each extra part adds C0G tolerance and temperature terms that are already included at 5 % plus 0.6 %; parts from different makers have different temperature coefficients (not checked).

## 6. Not verified

- Live stock and price on the JLCPCB parts library and LCSC (pages did not show them). All stock/price figures are search snapshots of unknown date.
- JLCPCB basic/extended class for every part except C5889717 (extended). Likely extended for all 0.1 % thin-film parts and the 220 nF/33 nF C0G parts, but not read.
- Existence of 56.9 k and 27.7 k at 0.1 % on LCSC/JLCPCB beyond two searches each. Existence of 27.4 k and 301 ohm at 0.1 % on LCSC/JLCPCB. Existence of 100 nF and 68 nF C0G 1206 on LCSC.
- Temperature coefficient and ageing of the C0G parts; Digi-Key/Mouser stock; JLCPCB assembly feasibility of 1210/1206 and series pairs on the board; the layout effect of a series pair at R_ILIM3.
- Nothing was measured or simulated beyond running the existing script; the PCB, BOM and generator were not changed.

## Addendum 2 (follow-up checks)

Status: Draft. Date of research: 2026-11-05 (about 19:30 UTC). Author: Claude (agent). Not reviewed. Earlier text is unchanged. Nothing here is Approved, and no part is chosen.
Traces: HW-010, ADR-0010, ADR-0016, RISK-027.

### A2.1 Method and a usable JSON API

- `jlcsearch.tscircuit.com` has a JSON API that works **without JavaScript**. It needs a `curl` style client: a Python `urllib` default user agent got HTTP 403, and the WebFetch tool got HTTP 500 for the same URLs. `curl` answered.
- Pattern that worked: `https://jlcsearch.tscircuit.com/resistors/list.json?resistance=27400&package=0603` and `https://jlcsearch.tscircuit.com/capacitors/list.json?package=1206&capacitance=1e-7`. The answer holds `lcsc`, `mfr`, `description`, `stock`, `price1`, `in_stock`, `tolerance_fraction`, `is_basic`.
- The `tolerance_fraction` URL parameter was **ignored** (all tolerances came back). The filter was applied on the client side.
- The backend (Cloudflare D1) returned "D1 DB is overloaded" on many calls. Repeated calls gave the data for most queries. The 56.2 k, 0603 query never succeeded.
- This site is a **mirror** of the JLCPCB parts library with an unknown refresh date. It is **not a live LCSC or JLCPCB page**. Every stock figure below is therefore **unconfirmed**. Source for each figure is the query URL named in the table.
- Basic or extended class: the mirror shows `is_basic` false for all parts below. The same mirror agrees with the earlier page read (C5889717 extended). The class is **unconfirmed** for all other parts (a mirror flag, not a live page).
- Stock `null` in the mirror means no stock figure. It is **not proof of zero stock**: it also shows `null` for 47.0 k parts for which section 3 had search summaries of several thousand pieces. The same mirror shows large numbers for other parts (for example 10 k 0805, stock 50,871,854). The `null` values are treated as "no data".

### A2.2 C0G / NP0 5 % capacitors, 1206 / 1210

Source of every row: `https://jlcsearch.tscircuit.com/capacitors/list.json?package=<1206|1210>&capacitance=<farad>` (query 2026-11-05). All figures **unconfirmed** (mirror). Class: mirror says extended, unconfirmed. Price is `price1` in USD.

| Value | Package | LCSC | Part | Stock (mirror) | Price1 | Note |
|---|---|---|---|---|---|---|
| 100 nF 50 V NP0 | 1206 | C170182 | 1206N104J500CT | 153,428 | 0.1115 | |
| 100 nF 50 V C0G | 1206 | C97946 | Murata GRM31C5C1H104JA01L | 60,938 | 0.1801 | |
| 100 nF 100 V C0G | 1206 | C405303 | Murata GRM31C5C2A104JA01L | 13,986 | 0.3433 | |
| 100 nF 50 V C0G | 1206 | C46348 | 1206CG104J500NT | 9,123 | 0.3049 | |
| 100 nF 50 V C0G | 1206 | C319186 | TDK C3216C0G1H104JT000N | 4,589 | 0.4434 | |
| 100 nF 50 V NP0 | 1206 | C105970 | C1206N104J050T | 3,058 | 0.1605 | |
| 100 nF 50 V C0G | 1210 | C338021 | TDK C3225C0G1H104JT000N | no stock figure | 0.6654 | listed only |
| 68 nF 50 V C0G | 1206 | C361177 | C3216C0G1H683JT000N | 2,000 | 0.3266 | only 68 nF part with a stock figure |
| 68 nF 50 V C0G | 1206 | C77084, C3847777, C2170927 | Murata GRM31C5C1H683JA01L, GRM3195C1H683JA05D, TDK | no stock figure | 0.15 to 0.37 | listed only |
| 68 nF | 1210 | none | | | | 17 rows returned, none C0G 5 % |
| 150 nF | 1206, 1210 | **none** | | | | 19 and 7 rows returned, **no C0G/NP0 5 %** part (1812 not queried; section 5 lists TDK 1812 at stock zero) |
| 220 nF 50 V C0G | 1206 | C464977 | Murata GRM31C5C1H224JE02L | 56,831 | 0.5045 | (section 5 gave 4470 and 16,970 as older snapshots) |
| 220 nF 25 V C0G | 1206 | C1518214 | Murata GRM31C5C1E224JE02L | no stock figure | 0.4377 | |
| 220 nF C0G | 1210 | C2181671 | C1210X224J3GACAUTO (25 V) | no stock figure | 1.173 | |
| 33 nF 50 V C0G | 1206 | C97930 | Murata GRM3195C1H333JA01D | 18,405 | 0.1294 | |
| 47 nF 50 V C0G | 1206 | C21812 | Murata GRM31M5C1H473JA01L | 52,917 | 0.1619 | |

Result: **150 nF C0G 5 % is not offered in 1206 or 1210** in this mirror. 100 nF is plentiful, 220 nF 1206 has C464977, 68 nF 1206 has one part with stock (2,000, C361177). The 50 V ratings are the same as the planned set. The datasheets of these parts were not read (temperature coefficient assumed 0 +/- 30 ppm/degC, class I).

### A2.3 Resistors, 0.1 %, 0603

Source: `https://jlcsearch.tscircuit.com/resistors/list.json?resistance=<ohm>&package=0603` (2026-11-05). Unconfirmed (mirror). Stock field: no data (null, `in_stock` false) for every 0.1 % part below, so **no stock figure is available** from this source. Price is `price1` in USD.

| Value | LCSC | Part | Price1 | Note |
|---|---|---|---|---|
| 27.4 k, 0.1 % | C861274 | Yageo RT0603BRD0727K4L (25 ppm) | 0.0331 | |
| 27.4 k, 0.1 % | C861793 | Yageo RT0603BRE0727K4L (50 ppm) | 0.0305 | |
| 27.4 k, 0.1 % | C855755 | Yageo AT0603BRD0727K4L (25 ppm) | 0.065 | |
| 27.4 k, 0.1 % | C667082 | TD03G2742BT (25 ppm) | 0.0248 | |
| 27.4 k, 0.1 % | C413736, C3930217, C2079063 | ERJPB3B2742V, ERA-3AEB2742V, TNPW060327K4BEEA | 0.0542, 0.1395, 0.2189 | |
| 301 ohm, 0.1 % | C861310 | Yageo RT0603BRD07301RL (25 ppm) | 0.0287 | |
| 301 ohm, 0.1 % | C666860 | TD03G3010BT (25 ppm) | 0.0236 | |
| 301 ohm, 0.1 % | C2074494, C2089450, C4320651 | ERA-3AEB3010V, TNPW0603301RBEEA, RN73H1JTTD3010B25 | 0.0851, 0.2031, 0.1245 | |
| 47.0 k, 0.1 % | C326725 | Yageo RT0603BRD0747KL (25 ppm) | 0.0311 | 15 listings in total, also C5889717, C328427 of section 3 |
| 56.9 k | C863161 | Yageo RT0603DRE0756K9L | 0.0079 | **0.5 %** only. No 0.1 % in any package (query without `package`) |
| 27.7 k | C863005 | Yageo RT0603DRE0727K7L | 0.0199 | **0.5 %** only in 0603. 0.1 % exists only in 0805 (C865349 RT0805BRD0727K7L) and 0402 (C7294198 RP0402BRD0727K7L) |
| 56.2 k, 0.1 % | not retrieved | | | The query failed (D1 overload) on 3 tries. Section 3 gave C855903 (the URL names it "Pre-ordered"). Open. |

Result: this API **confirms the earlier finding**: 56.9 k and 27.7 k at 0.1 % do not exist in 0603 on the JLCPCB library mirror (the 27.7 k 0.1 % part exists in 0805 and 0402 only). The two E96 values for the series pair, 27.4 k and 301 ohm at 0.1 %, **are listed** (several makers, 25 ppm). Whether they are in stock is **unconfirmed** (no stock data).

### A2.4 Parametric stock without JavaScript (question 3)

- Yes, for **listing and parameters**: the API above answers with plain JSON for `curl`. Parameters seen: `resistance`, `package`, `capacitance` (others not tried). It does not filter by tolerance.
- For **stock**: the field is present and shows values for many parts (for example 56,831 for C464977) but is null for the 0.1 % resistors. A null may be a data gap of the mirror. The stock stays unconfirmed until the LCSC or JLCPCB page is read in a browser.
- Not tried: `yaqwsx.github.io/jlcparts` (static database download, large), LCSC and JLCPCB live pages (JavaScript).

### A2.5 Hold-off window with purchasable C0G sets

Script: `hw/kicad/spike-gate/sim/holdoff_cap.py` (imported unchanged: `td_window()`; k = 357.6 kohm to 875.6 kohm per farad; 5 % tolerance per part; C0G 30 ppm/degC over -55 to 125 degC = 0.3 %; ageing, DC bias and leakage taken as 0). Window of HW-010: 200 to 600 ms. A helper script in the agent scratchpad (not in the repository) fed the new part lists to the same functions. Output exactly as observed (rounded, ms):

| Set (all C0G 5 %) | Total | Parts | tD min | tD max | Result |
|---|---|---|---|---|---|
| 6 x 100 nF | 600 nF | 6 | 203.2 | 553.2 | In window |
| 220 + 220 + 100 + 68 nF | 608 nF | 4 | 205.9 | 560.6 | In window |
| 5 x 100 nF | 500 nF | 5 | 169.3 | 461.0 | OUT (below 200 ms) |
| 5 x 100 + 68 nF | 568 nF | 6 | 192.4 | 523.7 | OUT |
| 220 + 220 + 100 + 33 nF | 573 nF | 4 | 194.0 | 528.3 | OUT |
| 220 + 220 + 68 + 68 nF | 576 nF | 4 | 195.1 | 531.1 | OUT |
| 220 + 100 + 100 + 100 + 68 nF | 588 nF | 5 | 199.1 | 542.1 | OUT (0.9 ms short) |
| 220 + 220 + 150 nF | 590 nF | 3 | 199.8 | 544.0 | OUT (0.2 ms short); 150 nF not purchasable anyway |
| 3 x 220 nF | 660 nF | 3 | 223.5 | 608.5 | OUT (above 600 ms) |

Findings:
- With 5 % C0G parts the window is tight. The usable total is roughly 603 to 610 nF; sets near 600 nF pass, sets of 590 nF or less miss 200 ms.
- Best purchasable sets (derived, from the mirror data above):
  - **220 + 220 + 100 + 68 nF** (C464977 x2, C97946 or C170182, C361177): 205.9 to 560.6 ms, 4 parts, margin 5.9 ms to the 200 ms limit and 39.4 ms to 600 ms. Needs the 68 nF C3216C0G1H683JT000N (mirror stock 2,000, one source).
  - **6 x 100 nF** (one value, mirror stock 60,938 to 153,428): 203.2 to 553.2 ms, 6 parts, margin 3.2 ms and 46.8 ms. One part number, widest second source, but six pads and six placements.
- The lower margin is small in both cases (3 to 6 ms, about 1.5 to 3 % of 200 ms). The calculation excludes DC bias, ageing and the tD(no cap) term; those are not checked. Margin to 600 ms is larger.
- The 150 nF part of the current generator set (C1B) and the 470 nF part (C1) have no purchasable C0G source in 1206 or 1210 (section 5 and A2.2). The generator and PCB were not changed.

### A2.6 Proposal for the owner (not a decision)

1. ILIM: R1 47.0 k (several 0.1 % listings), R2 56.2 k or 56 k (stock check still open), R3 = 27.4 k + 301 ohm, both 0.1 % and listed (A2.3). Stock must be checked on the live LCSC or JLCPCB page.
2. Hold-off: 220 + 220 + 100 + 68 nF or 6 x 100 nF (A2.5). The set with 150 nF cannot be bought as C0G.

### A2.7 Not verified (Addendum 2)

- Live stock, price and basic or extended class on LCSC and JLCPCB (mirror data only, refresh date unknown).
- Stock of every 0.1 % resistor (no data in the mirror). The 56.2 k, 0603 query. 1812 and other packages for 150 nF.
- Datasheets of the C0G parts (temperature coefficient, ageing, DC bias at the working voltage), assembly feasibility of six parallel 1206 parts or a series resistor pair on the board.
- `ilim_steps.py` was not run again; the margins of section 4 were not recomputed for these specific part tolerances.
