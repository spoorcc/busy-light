# ADR-0022: How the prototype board P1 gets its parts onto the board

- **Status:** Proposed (written by the assistant, 2026-11-18; the owner decides)
- **Date:** 2026-11-18
- **Deciders / reviewers:** owner (Ben Spoor); no goldfish review of this ADR yet
- **Related:** HW-008, HW-010, HW-005, HW-016, HW-017, MECH-001, SYS-020, SYS-021, SYS-022, ADR-0003, ADR-0010, ADR-0016,
  ADR-0020, plan 08, RV-014, `docs/journal/2026-11-18-overnight.md`, `docs/journal/2026-11-17-p1-order-owner-decisions.md`

## Context and problem
The owner wants to order P1 with JLCPCB Economic PCBA, every assembled part on one side, 0.15 mm tracks, 4 layers, HASL lead-free,
5 PCBs with 2 assembled, at most EUR 100 (answers of 2026-11-17; HW-008 Approved with the through-hole amendment). Measurements of
2026-11-18 (scratch experiments, journal of that day) show that this does not fit:

| Variant (placement only, 16 seeds of 160000 iterations) | Best part overlap (mm2, 0 = fits) |
|---|---|
| 46 mm board, all parts on top, vendor antenna keep-out on | 25.1 (61 courtyard overlaps, waiver max 14) |
| same, 4 x iterations | 25.2 (a space problem, not a placer limit) |
| 46 mm, keep-out off | 6.6 |
| 46 mm, one hold-off capacitor instead of six | 9.0 |
| 46 mm, both | 0.57 |
| 50 mm, parts also outside the LED ring | 9.7 |
| 54 mm, parts also outside the LED ring | 0.0 |

One routing run of the 54 mm placement at 0.15 mm left 5 unconnected items after the clean-up; the strict gate also fails on 33
U9 courtyard overlaps (waiver max 14). The stored two-sided board routed completely with the 0.1 mm rules (ADR-0020 option B,
Proposed), never with 0.15 mm.

Not known: JLCPCB Economic PCBA rules and prices (not read; no network to jlcpcb.com), the price of a two-sided Standard PCBA order,
whether parts with the functions of option A exist with fitting limits (no datasheet read), the real housing size for a larger board
(FreeCAD not run).

## Decision criteria
| Criterion | Weight (1-5) | Source requirement |
|-----------|--------------|--------------------|
| Meets the Approved requirements (one side HW-008, size MECH-001, antenna HW-005, limit behaviour HW-010) | 5 | HW-008, MECH-001, HW-005, HW-010 |
| Measured evidence that it places and routes | 4 | `docs/process/verification-strategy.md` |
| The current-limit safety argument stays all-hardware and simple | 4 | ADR-0016, HW-010 |
| Cost per board | 3 | SYS-021 |
| Time to the first ordered board | 3 | owner goal (bench evidence for HW-010, TC-217, antenna) |
| Reversibility | 2 | process section 6 |

## Alternatives considered
### A. Fewer parts, keep 46 mm and one side
Replace the TPS2553 with two TMUX1101 switches, their supply protection and pull-downs by one USB power switch whose current limit is
selected by logic pins (TI's USB charging-port-controller family has ILIM_HI/ILIM_LO pins; not checked against the HW-010 windows),
and replace the TPS3840DL with its six 100 nF C0G capacitors by a supervisor with a fixed internal delay inside the 200 to 600 ms
window (part to find). Estimated saving about 15 parts (not measured). Strongest case: it serves the owner's request to simplify, the
product cost (SYS-021) and the one-sided rule of SYS-022 and HW-008 at the same time, and keeps the gate in hardware. Against: no part
is identified yet; ADR-0010 and ADR-0016 need amendments; three limit steps may become two (SYS-020 middle step); new schematic and
analysis before any routing; the placement evidence is an estimate (one hold-off capacitor gave 25.1 to 9.0 mm2; the combination
with the keep-out gave 0.57, still not 0).
### B. Grow the board to about 54 mm, one side
Evidence: placement fits; one routing run with 5 unconnected items. Strongest case: the best measured one-sided result, no circuit
change. Against: the housing grows to about 61 mm (board + 7 mm by `housing_params.py`, an estimate) against the 58 mm of MECH-001
(Approved; the current board is already 59.24 mm); the U9 courtyard waiver still fails; a larger product.
### C. Two-sided assembly for P1 (JLCPCB Standard PCBA), the stored board's family with R22 and T1
Re-place and route the current netlist two-sided with the 0.1 mm rules that routed before (ADR-0020 option B), with the new
no-via-in-pad rule. Strongest case: the only configuration with complete routing in the record; fastest to bench evidence; no new
parts. Against: violates HW-008 as approved on 2026-11-17 (one side) and SYS-022; two-sided assembly costs more (price not read;
the EUR 100 budget may not hold); thin fab margin at 0.1 mm; a new routing batch is still needed for R22 and T1.
### D. Give up the vendor antenna keep-out and use one hold-off capacitor, 46 mm one side
Evidence: 0.57 mm2, still not overlap-free. Strongest case: smallest change. Against: does not fit as measured; antenna risk
(HW-005, ADR-0003, DEV-004); needs a C0G part whose stock is not checked.
### E. Do nothing / defer the order
No P1 until the product design is settled. Strongest case: no money spent on a board that may change. Against: no bench evidence for
HW-010, ADR-0021 (surge) or the antenna; the open risks stay open.

## Comparison
Scores 1 (poor) to 5 (good); weighted sum in the last row.

| Criterion (weight) | A | B | C | D | E |
|-----------|---|---|---|---|---|
| Approved requirements (5) | 4 | 1 | 2 | 2 | 3 |
| Measured evidence (4) | 2 | 4 | 5 | 3 | 1 |
| Safety argument (4) | 4 | 5 | 5 | 5 | 5 |
| Cost per board (3) | 4 | 3 | 2 | 4 | 5 |
| Time to first board (3) | 2 | 4 | 5 | 3 | 1 |
| Reversibility (2) | 3 | 2 | 4 | 3 | 5 |
| **Weighted sum** | **68** | **66** | **79** | **69** | **67** |

## Decision
Proposed: **C for P1, and A as the direction for the next board revision.** P1 exists to produce bench evidence (HW-010 gate,
TC-217 surge, antenna), and C is the only option with measured complete routing; the scores favour it clearly (79 against 66 to 69).
A is the right answer for the product (SYS-021, SYS-022) but has no identified parts and no evidence yet, so it should not hold up P1.
Conditions: (1) the owner amends HW-008 for P1 to allow two-sided assembly (a P1-only exception; SYS-022 stays for the product);
(2) the two-sided Standard PCBA price for 2 boards is within the owner's limit (order step O6); if it is not, A becomes the P1 route.
This contradicts the owner's answer 1 of 2026-11-17 (one side); the measurements of 2026-11-18 are the reason.

## Consequences
- Positive: a board that is known to route; bench evidence sooner; no new parts for P1.
- **Negative / trade-offs accepted:** higher assembly cost; HW-008 needs a P1 exception; the 0.1 mm rules (ADR-0020 B) must be
  accepted for P1; plan 08 (one side) is replaced by a two-sided variant for P1; the one-sided work (P1 placement switch, top-side
  LED capacitors) is kept for revision 2.
- New risks (add to risk register): price over budget; yield at 0.1 mm lines; A may find no suitable parts.
- Requirements created or changed: HW-008 P1 exception (owner); ADR-0020 acceptance (owner); a study task for A (switch with
  selectable limit, fixed-delay supervisor) with datasheet evidence (HW-012).

## Verification and revisit
C: a new two-sided routing batch with the current netlist passes the strict gate and `pcb_fabcheck --no-via-in-pad`; the JLCPCB price
for 2 assembled boards. A: datasheet evidence for both parts, recalculated HW-010 windows, and a one-sided placement with overlap 0 at
46 mm. Revisit when the price is known, or when A's parts are found.

## Critical review notes
Strongest objection: the owner chose one side and Economic PCBA on purpose, and HW-008 was approved that way a day ago; recommending
two-sided overrides the owner. Answer: the recommendation does not override; it needs the owner's amendment and is conditional on the
price. The one-sided request was made before the measurements, which show it does not fit on 46 mm with the present circuit; the
choice is now between changing the circuit (A, slow, unproven), the housing (B, breaks MECH-001) or the assembly (C). A second
objection: the scores are the assistant's judgement; a different weight on cost would favour A or D. With cost weighted 5 instead of
3, A gives 76, C 83: C still leads, because only C has routing evidence.
