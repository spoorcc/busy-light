# Analysis N4: purchasable CT capacitor for the TPS3840 hold-off delay (C1)

- **Status:** Draft
- **Date:** 2026-11-05
- **Author:** Claude. Not reviewed. Nothing here is Approved or Accepted. No part is chosen.
- **Related:** finding N4 in `docs/verification/reports/review-full-board-goldfish-2.md`; delay window in `docs/verification/reports/datasheet-evidence-supervisor.md` (S1, A5, A6); HW-003, HW-010; C1 in `hw/kicad/spike-gate/src/layout_full.py` (unchanged by this analysis).
- **Labels:** **read** (seen in a web page or document on 2026-11-05), **derived** (computed here), **not checked**.

## 1. Question

C1 is `620n C0G 5%` in a 0603 footprint. Is a part of that kind purchasable, and if not, what meets the 200 to 600 ms window?

## 2. Method (derived)

tD min = k_min x C x (1 - tol); tD max = k_max x C x (1 + tol). k_min = 357.6 kohm, k_max = 875.6 kohm (datasheet-evidence-supervisor.md, A6; tD(no cap) neglected). Allowed C for a total tolerance tol: 200 ms / (k_min (1 - tol)) <= C <= 600 ms / (k_max (1 + tol)). C0G total tolerance is taken as the grade tolerance plus 0.6 % for temperature (assumed: 30 ppm/degC over 180 K is 0.54 %; the datasheet of a chosen part must confirm). Ageing and DC bias of C0G are taken as 0 (not checked per part). Script: scratchpad `n4.py`, output reproduced below.

- J (5 %) C0G: C must be 592 to 649 nF.
- G (2 %) C0G or film: C must be 574 to 668 nF.

## 3. Evidence found (read, 2026-11-05)

| ID | Finding | Source |
|---|---|---|
| E1 | Web searches for "680 nF C0G 1206/1210/1812" returned only 680 **pF** parts (Kemet, Yageo, TDK, Murata, Vishay, Kyocera AVX). No 560 to 680 nF C0G listing was found. | WebSearch 2026-11-05; e.g. https://www.digikey.co.uk/en/products/detail/kemet/C1206C681J2GACTU/2216154 (680 pF) |
| E2 | Holy Stone "HCN" high-capacitance NP0 catalogue (2016): 0603 and 0805 have rows to about 100 nF at most; 1206, 1210, 1812, 2220 are offered at 16, 25, 50 V; the capacitance list ends at 220 nF (code 224, 1812 and similar sizes, J = 5 %). No 330 nF or larger value. The 0603 NP0 column set in that table is much shorter. | https://datasheet.sic-components.com/HCN_Series_Cat.pdf (read via pdftotext, 2026-11-05; table is dense, size/value mapping read approximately) |
| E3 | KEMET SMC PPS film: SMC10.2 684J 50 V, 0.68 uF, 5 %, 4036 case (10.2 x 9.1 x 5.5 mm), 125 degC, listed at element14 and Arrow. 2220 size SMC parts found only to 0.068 uF. Stock and price **not read** (page fetches timed out). | https://sg.element14.com/kemet/smc10-2684j50a31tr16/cap-0-68-f-50v-5-pps-4036/dp/2496064 (search result only); https://www.arrow.com/ko-kr/products/smc10-2684j50a31tr16/kemet-corporation (search result only) |
| E4 | Mouser listing of KEMET SMC 0.68 uF 50 V PPS 2220 5 %, 700 in stock: reported by a search summary, **not confirmed** (no 2220 0.68 uF part found in a second search). Treat as unverified. | https://www.mouser.in/en/c/passive-components/capacitors/?series=SMC (search result only) |
| E5 | Murata GRM32 X7R 680 nF exists in 1210 at 50 V (e.g. GRM32NR71H684KA01L, K = 10 %). Murata states X7R-class parts change capacitance under DC bias and C0G does not. No bias curve at 5 V was obtained. | https://www.xonelec.com/mpn/murata/grm32nr71h684ma01l ; https://www.murata.com/support/faqs/products/capacitor/mlcc/char/0005 |
| E6 | LCSC/JLCPCB stock: no 560 to 680 nF C0G or SMD film listing found. LCSC pages returned by search were 68 nF or 68 pF parts. | WebSearch 2026-11-05 |

## 4. Candidates (derived; C0G total tolerance = grade + 0.6 %)

| Candidate | C | tD min | tD max | In 200 to 600 ms? |
|---|---|---|---|---|
| Current: 620 nF C0G 5 %, one part, 0603 | 620 nF | 209.3 ms | 573.3 ms | yes on paper, but **no such part found** (E1, E2) |
| 3 x 220 nF C0G 5 % in parallel (1812) | 660 nF | 222.8 ms | 610.3 ms | **no** (10 ms over) |
| 3 x 220 nF C0G 2 % (G grade not verified to exist) | 660 nF | 229.9 ms | 592.9 ms | yes, 7 ms margin |
| 220 + 220 + 150 nF C0G 5 % | 590 nF | 199.2 ms | 545.5 ms | **no** (0.8 ms short) |
| 220 + 220 + 150 + 33 nF C0G 5 % (4 parts) | 623 nF | 210.3 ms | 576.0 ms | yes |
| 220 + 220 + 100 + 68 nF C0G 5 % (4 parts) | 608 nF | 205.2 ms | 562.2 ms | yes |
| 6 x 100 nF C0G 5 % (0603) | 600 nF | 202.5 ms | 554.8 ms | yes |
| 680 nF PPS film 5 %, 4036 (KEMET SMC10.2) | 680 nF | 231.0 ms | 625.2 ms | **no** (25 ms over) |
| 560 nF film 5 % or 2 % | 560 nF | 190.2 / 196.3 ms | 514.9 / 500.1 ms | **no** (too low) |
| 620 nF film 5 % (hypothetical, not found) | 620 nF | 210.6 ms | 570.0 ms | yes, if it exists |
| 680 nF X7R 10 %, +/-15 % temperature, -10 % bias at 5 V (bias assumed, not read) | 680 nF | 158.1 ms | 744.3 ms | **no**; fails even with zero bias loss (25 % spread against the 10.1 % limit) |

Other timing options (from the existing evidence file, not re-checked): TPS3808G01 with 68 nF fails or relies on an extrapolated +/-40 % tolerance; TPS3839K50 fixed delay has 120 ms minimum. Neither removes the problem.

## 5. Assessment

- **X7R is excluded** by tolerance and temperature alone (> 25 % spread against 10.1 % allowed). DC bias is a minor extra: CT is a low-voltage node (abs max 5.5 V, datasheet-evidence-supervisor.md A8), so the actual bias is at most about 5.5 V; the number was not obtained.
- **A single 620 nF C0G part was not found.** The largest C0G value seen is 220 nF (E2), in 1812 (largest sizes). Single 0603 C0G stops far below.
- **The only fitting purchasable structures found are parallel C0G sets of 3 to 6 parts**, or a hypothetical 620 nF film part. Parallel sets add parts, area, and E-series rounding; a set of three equal parts (660 nF) misses the window at 5 %.
- The 10.1 % total limit leaves little: the window is feasible only with C0G or film, trimmed to about 600 to 650 nF at 5 %.

## 6. Recommendation (not a decision; no part chosen)

No clear single winner exists, so the generator is **not** changed. C1 stays a placeholder. Proposed next step for the user:

1. Verify at LCSC/Digi-Key/Mouser (stock, price, datasheet temperature coefficient) 220 nF, 150 nF and 33 nF C0G in 1206/1210/1812; if confirmed, use a parallel set of about 620 nF (for example 220 + 220 + 150 + 33 nF, or 220 + 220 + 100 + 68 nF, 1210/1812 and 0603) with 5 % parts. This is derived to fit with about 10 ms margin at the low end and 24 to 38 ms at the high end.
2. Or ask a distributor for 620 nF film (or G-grade 220 nF C0G), then three parts suffice.
3. Alternatively treat the window with margin by a requirement or architecture change (a wider window, a TPS3840 variant with a different RCT, or a controlled-value discrete RC) in a separate ADR. This needs the user.

Whatever is chosen, the footprint must be a pad set for the large case (1210 or 1812), not 0603. A CT-pin leakage and board leakage check is still open (A8).

## 7. Not checked

- Stock, price and lead time at LCSC, JLCPCB, Digi-Key and Mouser (searches only; two page fetches timed out).
- Manufacturer datasheets of any candidate (temperature coefficient, ageing, G-grade availability at 220 nF).
- Murata SimSurfing or other DC-bias data at 5 V.
- CT pin leakage and PCB surface leakage versus a 200 ms delay; capacitor insulation resistance of film parts.
- The HCN catalogue is from 2016; the size/value mapping was read from extracted text and is approximate.
- No simulation, no bench measurement, no generator, ERC or test run (no generator change made).
- No statement here says a part "is compliant".
