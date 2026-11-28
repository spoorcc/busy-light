# Stock check and datasheet read: tact switches for the centre button (plan 09 step 0)

Status: Draft. Date of research: 2026-11-23. Author: Claude (agent). Not reviewed. Nothing here is Approved or Accepted, and no part is chosen.
Traces: MECH-004, MECH-002, MECH-003, HW-008. Input to ADR-0026 (not yet written) and `docs/plans/09-centre-button.md` section 4.9 and step 0.
The owner said "Continue" after the plan 09 status report; the assistant read this as a go-ahead for step 0 only (analysis, no CAD, board or requirement
change). The other owner questions of plan 09 section 7 stay open.

## 1. Method and access

- Product pages of LCSC (`www.lcsc.com/product-detail/C...`) and JLCPCB (`jlcpcb.com/partdetail/C...`) were fetched with `curl` from the container
  (both hosts are allowed in the `busy-light` environment) and the embedded page data was read with a script. The datasheets were fetched from
  `datasheet.lcsc.com` (links on the LCSC pages). The assistant's WebFetch helper agents could not resolve the two hosts (DNS error); the `curl` path worked.
- **Stock.** The LCSC page data holds the part's own stock (`stockNumber`). The JLCPCB page data holds the class (`componentLibraryType`: `base` = Basic,
  `expand` = Extended) but **not** the part's own JLCPCB stock: its `stockCount` values belong to related parts, so the JLCPCB stock of these parts was **not read**.
  The JLCPCB `overseasStockCount` is listed below as a second, unlabelled number. The class has one source (the JLCPCB page).
- The PDFs are in a scratch folder outside the repository (`BUSY_LIGHT_DATASHEETS`), as for the other parts. `check_part_evidence.py` ran on the three switch
  files against that folder: 3 document hashes and 15 quotes checked, 0 errors. Dimensions come from drawings and are **not** machine-checked (carried in `notes`).
- Not done: no JLCPCB search API (a POST was denied earlier in the session and was not retried), no distributor other than LCSC, no vendor contact, no sample.

## 2. Parts

| Item | TL3342F160QG (today's P1 part) | B3U-1000P (alternative 1, small body) | KSC221JLFS (alternative 2, longer travel) |
|---|---|---|---|
| Maker | E-Switch | Omron | C&K |
| LCSC number | C2886898 | C231329 | C221726 |
| JLCPCB class | Extended | Extended | Extended |
| LCSC stock (read 2026-11-23) | **1** | 49,545 | 15,080 |
| JLCPCB `overseasStockCount` | 1 | 56,941 | 16,565 |
| Price (LCSC "from", at the highest quantity step) | $0.5474 | $0.1032 | $0.3901 |
| Price at 1 piece, JLCPCB ladder | $1.044 (1 to 9) | $0.1877 (1 to 49) | not read |
| Body (LCSC and JLCPCB lists) | 5.2 x 5.2 mm; the stored footprint has 6.4 x 5.2 mm over the terminals | 3.0 x 2.5 mm | 6.2 x 6.2 mm |
| Height (page list) | 1.54 mm | 1.6 mm (catalogue headline says 1.2 mm; type table 1.6 mm) | "0.6 mm" (meaning not known) |
| Force (datasheet text) | 160 +- 50 gf = 1.57 N +- 0.49 N | 1.50 +- 0.49 N (page lists 1.53 N) | 2 +- 0.5 N |
| Travel (datasheet text) | **not published**; assumed 0.25 mm | pre-travel 0.15 mm (tolerance +0.2/-0.1 mm as read from the table, not text-checked); no total travel | 0.35 +0.3/-0.1 mm (0.25 to 0.65 mm) |
| Force-travel curve | none | none | none |
| Life | 100,000 cycles typical | 200,000 or more | 500,000 |
| Other | gull wing, 12 V 50 mA | 2 terminals, no ground terminal, plunger black | IP67 sealed, J-bend |
| Evidence file | `hw/evidence/parts/sw-tl3342.yaml` | `hw/evidence/parts/sw-b3u-1000p.yaml` | `hw/evidence/parts/sw-ksc221.yaml` |

Criteria of plan 09 section 4.9 against the three: (a) body below 6.4 x 5.2 mm, ideally 4.5 x 3.5 mm or less: B3U yes (3.0 x 2.5 mm), TL3342 no,
KSC221 no; (b) published travel and force-travel curve: **no part publishes a curve**; TL3342 publishes no travel at all, B3U a pre-travel only, KSC221 a travel with
tolerance; (c) actuator height 1.6 mm or less: B3U and TL3342 (1.6 and 1.54 mm), KSC221 not known; (d) travel of 0.5 mm or more: **none** (KSC221 reaches it only at the
upper tolerance); (e) basic class: **none** (all three Extended); stock: B3U and KSC221 yes, TL3342 one piece.

Finding: **no listed part meets all criteria.** The B3U-1000P is the best on body size, stock, life and price; its price and its 3.0 x 2.5 mm body also remove
most of the antenna cost of option S2 (section 3). The KSC221JLFS is the best on travel but is larger than today's part. The step 0 rule applies: the alternatives enter the S2 and S3
analysis by body size and by the published click values only.

## 3. What the real values change in the plan (assistant's scratch scripts, **not repository evidence** until step 1 holds them with tests)

- **Antenna margin with the module moved (S2).** Same search as plan 09 section 3.3 (0.5 mm and 3 degree grid, 1.0 mm to the switch body): TL3342 body 6.4 x 5.2 mm gives
  10 poses and 2.51 mm (50 % of today's 5.06 mm); **B3U body 3.0 x 2.5 mm gives 1,322 poses and 3.90 mm (77 %)**; with 0.5 mm added on each side for a courtyard (4.0 x 3.5 mm) 424 poses and 3.64 mm.
- **Centre switch with three bridges (S2), press-point sweep as in 3.2.** The click force with a centred switch is F = OF + 3 k x_click (the switch click force plus the bridge
  load at the click travel). Pass rule as in 4.1: F inside [2] to [5] N and press-point travel at most [1.0] mm, with the switch force tolerance added. Nominal pre-travel:
  - TL3342 (1.57 +- 0.49 N, assumed 0.25 mm): bridge stiffness k from **2.83 to 3.92 N/mm** (ratio 1.4).
  - **B3U-1000P (1.50 +- 0.49 N, 0.15 mm): k from 2.20 to 6.69 N/mm (ratio 3.0).** At k = 3: F 2.85 N nominal, press-point travel 0.70 mm; at k = 4: 3.30 N and 0.62 mm.
  - KSC221 (2 +- 0.5 N, 0.35 mm nominal): at k = 2, F = 4.10 N and travel 1.53 mm (fails the travel limit); at the travel limits 0.25 and 0.65 mm the force is 3.5 and 5.9 N.
  The FDM spread of arm stiffness (0.32x to 2.4x, plan 09 finding 2) is still wider than the B3U band of 3.0, but much less so than the TL3342 band of 1.4.
- **Open point for the B3U:** the pre-travel tolerance (0.05 to 0.35 mm if +0.2/-0.1 is right) is not in these numbers. At k = 3 the force F = OF + 9 x_click then runs from
  1.01 + 0.45 = 1.5 N to 1.99 + 3.15 = 5.1 N, so the window **fails at the tolerance extremes** and needs a measured click travel (step 3 coupon) or a tighter selection. The plunger of
  the B3U is not read (drawing only).

## 4. Rejected or not read

- XKB TS-1187A-B-A-B (C318884, JLCPCB Basic, LCSC stock 357,160, 5.1 x 5.1 mm, 1.5 mm, 1.6 N, 100,000 cycles): its datasheet is a one-page image with no text layer and no travel found.
  It is the Basic-class fallback if class matters more than size; it needs a coupon-measured curve.
- Hanxia HX 3x4x2-2P-1.6N (C49234124), G-Switch GT-TC029A-H025-L1A (C843666) and other 4 x 3 mm listings: the listings give force and height but no travel; datasheets were not read.
- Omron B3AL long-stroke (SMT): no LCSC or JLCPCB listing was found by search; not read. Panasonic EVQ-P and Alps parts: no listing checked; not read.

## 5. Consequences for plan 09

1. Question 5 of plan 09 section 7 (scissor study) changes: with the B3U-1000P the S2 option keeps 77 % of today's antenna margin on paper and the bridge stiffness band widens from a ratio of 1.4 to 3.0, but
   the pre-travel tolerance and the FDM spread of the arms still exceed it. The scissor study is not needed to find a first workable option, but the click travel must be measured. The datasheet gives no total travel,
   no over-travel and no curve; a coupon (step 3) must measure them.
2. The part is Extended class and the TL3342F160QG has one piece in stock: either way the P1 order needs the part named, a stock check on the order day and the extended-part fee.
3. The 0.15 mm pre-travel makes the vertical stack tighter than the 0.25 mm assumed (plan 09 section 3.4); step 1 must rerun the tolerance chain with 0.15 mm.
4. These are first-order checks by the assistant. They change no requirement, ADR or design file. Only the owner chooses the part (ADR-0026).
