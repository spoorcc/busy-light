# ADR-0025: Stocked replacement for the hold-off supervisor U5

- **Status:** Proposed (the owner chose "another supervisor part" on 2026-11-22, decision 5; the part is not chosen)
- **Date:** 2026-11-22
- **Deciders / reviewers:** owner (Ben Spoor); written by the assistant; no goldfish review yet
- **Related:** HW-010, HW-008, HW-003, ADR-0016, ADR-0018, ADR-0021, ADR-0024, RV-016 rows 1 and 11, RISK-044, RISK-047, RISK-053

## Context and problem
U5 (TPS3840DL40DBVR, open-drain, falling threshold 4.0 V, release 4.115 to 4.285 V, delay set by six 100 nF C0G 1206 on CT)
makes the HW-010 hold-off: no step above step 1 for 200 to 600 ms after VBUS_IC returns. It has no LCSC or JLCPCB listing
(RV-016 row 1); the owner asked for a stocked part with the same function instead of global sourcing (decision 5,
`docs/journal/2026-11-22-owner-decisions-p1-rework.md`). Stock and datasheets were read on 2026-11-22 (LCSC and JLCPCB part
pages, TI and LCSC-hosted PDFs). The ADR-0024 gate rework keeps U5's output on HOLD_OK with the R6 pull-up (150 kohm).

Constraints from the design: the hold-off window [200] to [600] ms by worst case (HW-010); every pin rating against the
hot-plug clamp of TVS1 on VBUS_IC (8 to 14 V, ADR-0021: measure first); release below the 4.5 V VBUS minimum assumed in HW-010
criterion 5 (M4); HOLD_OK feeds 3.3 V LVC inputs (U3, U4, U10; 6.5 V absolute maximum).

Not known: the TUSB321 maximum CC debounce (133 ms typical only); whether the TPS3808 delay spread at 68 nF equals the spread
the datasheet gives at 180 nF (assumption below); live stock on the order day.

## Decision criteria
"Stocked at JLCPCB with an LCSC number" is a must (owner decision 5); options without it are listed but not scored.

| Criterion | Weight (1-5) | Source requirement |
|-----------|--------------|--------------------|
| Hold-off window inside 200 to 600 ms by worst case | 5 | HW-010 |
| Pin ratings against the VBUS_IC surge (no pin above its absolute maximum) | 4 | HW-010 criterion 4, ADR-0021 |
| Release threshold below the 4.5 V VBUS minimum, falling threshold near today's | 4 | HW-010 criterion 5 (M4) |
| Open-drain output (keeps the ADR-0018 option E and ADR-0024 structure, R6 pull-up) | 3 | ADR-0018, owner decision 1 |
| Board area and part count (the six 1206 C0G break the placement rules today) | 3 | HW-008, RV-016 row 11 |
| Change effort and risk (footprint, evidence, analysis) | 2 | plan 08 |

## Alternatives considered
Numbers: `sim/supervisor_options.py` (thresholds), `sim/holdoff_cap.py` (hold-off), evidence `tps3840dl40.yaml` (family
SNVSB03E) and `tps3808g01.yaml` (SBVS050N, hash and quotes checked).

### A. TPS3840PL42DBVR, push-pull, same family (C2868083; JLCPCB 31 on 2026-11-22)
Same CT network and delay equations as today: 203.2 to 553.2 ms with the six 100 nF (HW-010 table). Falling 4.137 to 4.263 V,
release 4.312 to 4.488 V. Against: the push-pull output drives HOLD_OK to VBUS_IC, so during the hot-plug clamp the LVC inputs
see up to 14 V from a low impedance; a series resistor is needed, and with the worst-case input leakage of three LVC inputs
(15 uA) it must stay below about 22 kohm for a valid low (0.33 V), which still lets about 0.34 mA into the inputs at the clamp
peak (not rated). R6 changes role. The six 1206 capacitors stay. Stock is thin.
### B. TPS3808G01DBVR, open-drain, adjustable threshold, one CT capacitor (C19653; JLCPCB 30; Q1 variant C130062, 66) (recommended)
SENSE 0.405 V +-2 % with a divider from VBUS_IC (931 k / 100 k, 1 %): falling 3.996 to 4.360 V, release up to 4.491 V
(hysteresis 3 % maximum, SENSE current +-25 nA included). Delay: one 68 nF C0G 5 % 1206 (Murata GRM3195C1H683JA05D, C3847777,
JLCPCB 2,343) gives 221.8 to 572.7 ms, using the min/typ and max/typ ratios of the datasheet row at 180 nF (0.62 / 1.03 /
1.44 s) scaled to 68 nF (assumption: the delay is proportional to CT and the spread comes from the internal current and
threshold). VDD and RESET are rated 7 V, so VDD and the R6 pull-up move to VDD_U1 (the TUSB321 supply node behind 470 ohm and
the 5.1 V zener, already protected); SENSE sees about 1.4 V at a 14 V clamp. For: open drain (no change to the gate logic of
ADR-0024), five parts fewer (one capacitor instead of six 1206), all pins inside their ratings by design. Against: new
footprint (SOT-23-6, pin 1 RESET, 2 GND, 3 MR, 4 CT, 5 SENSE, 6 VDD), two divider resistors, a wider threshold window than
today, the delay spread at 68 nF is an extrapolation, stock is thin (fallback: the Q1 variant, pin-compatible, its datasheet
not read).
### C. TPS3840PL43DBVR, push-pull, same family (C2066559; JLCPCB 116)
As A with the best stock of the TPS3840 options, but release 4.410 to 4.589 V: above the 4.5 V VBUS minimum, so a sagging
source may never release the gate (the safe direction, a functional loss).
### D. Keep the TPS3840DL40 and buy it outside JLCPCB (global sourcing or consigned parts) (do nothing)
Technically the best fit (12 V ratings, today's thresholds and analysis). Fails the must: the owner chose another part.
### Not scored (fail a hard limit)
- TLV803EA42/EA43 (fixed 200 ms, stocked): delay 130 to 270 ms, minimum below 200 ms and below the 133 ms typical CC debounce;
  the 400 ms option (260 to 540 ms) exists only at 2.6 and 2.9 V. The LCSC text of TLV803EB42 says "200ms", but code B is
  40 us (SLVSES2J figure 5-1).
- NCP303LSN42 / NCV303LSN42 (10 V rated, open drain, stocked as NCV): internal delay resistor 0.5 to 2.0 Mohm, a 4:1 spread
  that cannot fit a 3:1 window.
- ROHM BD5242G / BD5243G: listed as discontinued or obsolete. TPS3840DL42: 0 stock.

## Comparison
Scores 1 to 5; D fails the must and is not scored.

| Criterion (weight) | A | B | C |
|-----------|---|---|---|
| Hold-off window (5) | 5 | 4 | 5 |
| Pin ratings against the surge (4) | 2 | 4 | 2 |
| Thresholds (4) | 4 | 3 | 2 |
| Open drain (3) | 2 | 5 | 2 |
| Area and parts (3) | 2 | 5 | 2 |
| Change effort (2) | 4 | 2 | 4 |
| **Weighted sum** | **69** | **82** | **61** |

Sensitivity: if B's window score drops to 2 (the 68 nF extrapolation proves wrong), B scores 72 and still leads A.

## Decision
Proposed: **B**, TPS3808G01DBVR with the divider 931 k / 100 k from VBUS_IC, one 68 nF C0G on CT, VDD and the R6 pull-up on
VDD_U1; fallback TPS3808G01QDBVRQ1 if the stock is gone at order time. The owner decides.

## Consequences
- Positive: U5 orderable at JLCPCB; five fewer parts and five fewer 1206 footprints near U5 (RV-016 row 11 misses go away);
  every U5 pin inside its absolute maximum during the clamp; the gate structure of ADR-0024 is unchanged.
- **Negative / trade-offs accepted:** wider threshold window (3.996 to 4.360 V falling against 3.94 to 4.06 V today); the
  hold-off window rests on an extrapolation until TC-210 measures it; a new part and its evidence; two more resistors.
- New risks: R6 or the divider open (an open R2 pulls SENSE high: the hold-off ends early; an open R1 holds SENSE low: the gate
  never opens, the safe side) to add to the fault-injection table and RISK-044; thin stock (RISK-053 extends).
- Requirements created or changed (proposals for the owner): HW-010 table rows "Supervisor" and "Hold-off capacitor C1" and
  the hold-off window (221.8 to 572.7 ms); HW-010 criterion 7 rows for the divider; HW-003 note that VDD_U1 also supplies U5.

## Verification and revisit
`tests/test_supervisor_options.py`, `tests/test_holdoff_cap.py::Tps3808Option`; strict ERC after the schematic change; bench
TC-210: the hold-off at 25 and 70 degC on every P1 board, the release threshold with a slow VBUS ramp. Revisit if a measured
hold-off lies outside 200 to 600 ms, or if the TPS3840DL40 becomes stocked again.

## Critical review notes
Strongest objection: "B changes more than A: a new footprint, a divider, a new capacitor and a new supply node, to replace one
part." Answer: A's push-pull output breaks the open-drain HOLD_OK structure that the owner restored the same day and exposes
the LVC inputs to the clamp; B also removes the six 1206 capacitors that the placement could not hold near U5. Second
objection: the delay spread at 68 nF is extrapolated. Answer: recorded as an assumption; the sensitivity line shows B still
leads, and TC-210 measures it on every board.
