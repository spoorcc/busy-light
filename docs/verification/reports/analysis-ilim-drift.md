# Analysis: drift of the ILIM resistors and the value of R_ILIM3 (HW-010, ADR-0023, RV-017 row 6)

- **Date:** 2026-11-22. **Author:** assistant. **Status:** Draft analysis for the owner. Nothing chosen, nothing measured.
- **Asked by:** owner decision 3 of 2026-11-22 ("Keep 56.2 k, model it better": resistor drift, ageing and the datasheet table
  anchor in the model first, then the owner decides 56.2 k or 54.9 k), `docs/journal/2026-11-22-owner-decisions-p1-rework.md`.
- **Script and tests:** `hw/kicad/spike-gate/sim/ilim_steps.py` (`table_interp`, `ios_min_anchored`, `ios_max_anchored`,
  `DRIFT_SETS`, `tol_eff`, `both_on_margins`, `drift_budget`, `best_r3_for_budget`, `print_drift_report`);
  `tests/test_ilim_steps.py` classes `TableAnchor` and `DriftBudget` (36 tests in the file pass).
- **Evidence:** `hw/evidence/parts/ilim-resistors.yaml` (Yageo RT V.16, Yageo AT V.6, Vishay MCT document 28700; hashes,
  pages and quotes checked with `check_part_evidence.py` against the downloaded copies; status unverified, one reader).

## 1. Question
ADR-0023 decision 1 makes step 3 the state "both select switches on" with R_ILIM3 = 56.2 kohm. RV-017 row 6 found the step 3
lower margin (2.8 mA) inside the model's own error: the TPS2553 limit equation lies above the datasheet table, and the
resistor temperature coefficient and drift were not modelled. Which R_ILIM3 value keeps every HW-010 limit when these are in?

## 2. Method
1. **Table anchor.** The SLVS841G table gives min, nominal and max at 15, 20, 49.9 and 210 kohm. The model now interpolates
   each column log-log between neighbouring points and takes the lower of the equation and the table for the minimum, the
   higher for the maximum (`anchored=True`). At the step 3 resistance (17.61 kohm) the table gives 1366.6 mA against the
   equation's 1368.4 mA.
2. **Drift stack per resistor.** Initial tolerance + TCR times the largest excursion from 25 degC + soldering-heat change +
   1000 h life change, added linearly in the worst direction for every resistor at once (the conservative stack; an RSS sum
   needs independence, which is not shown). Resistor temperature range: -20 to 85 degC, an assumption (no system
   operating-temperature requirement exists; HW-013 uses 35 degC ambient and HW-010 asks for a step test at 70 degC).
3. **Drift budget.** The largest common resistor deviation for which step 1 (500 to 623 mA) and step 3 (1366 to 1577 mA, also
   covering the "switch 3 alone" state) both hold, with the TMUX1101 limits (Rds(on) 9.5 ohm, leakage 0.2 nA). A part
   choice passes when its stack is at or below the budget. This is the analysis criterion that replaces the ADR-0023
   revisit trigger ("bench shows the step 3 minimum below 1366 mA"), which a few room-temperature units cannot trigger.

## 3. Results
Stack per resistor (tolerance 0.1 %, TCR 25 ppm/degC over 60 K = 0.15 %):

| Part class (guaranteed datasheet limits) | Soldering heat | Life 70 degC 1000 h | Stack |
|---|---|---|---|
| Tolerance only (the analysis of record before today) | - | - | 0.10 % |
| Tolerance + TCR | - | - | 0.25 % |
| Yageo AT (automotive), Vishay MCT class 0.25 | 0.05 % | 0.1 % | 0.40 % |
| Yageo RT (the in-stock parts of the HW-010 table) | 0.5 % | 0.5 % | 1.25 % |

Margins at 0.1 % (anchored) and the drift budget (R_ILIM1 47.0 k, R_ILIM2 56.2 k):

| R_ILIM3 | s1 min / max | s3 min / max | Budget step 3 | Budget step 1 | Budget, all |
|---|---|---|---|---|---|
| 56.2 k | 4.2 / 6.4 mA | **1.0** / 23.5 mA | **0.17 %** | 0.93 % | **0.17 %** |
| 54.9 k | 4.2 / 6.4 mA | 11.3 / 12.7 mA | 0.91 % | 0.93 % | 0.91 % |

- **56.2 k fails as soon as the TCR is counted:** its budget (0.17 %) is below tolerance + TCR (0.25 %). The anchored lower
  margin is 1.0 mA, as RV-017 row 6 estimated.
- **54.9 k is the E192 value with the largest step 3 budget** (searched 40 to 70 k). Its budget (0.91 %) is set by step 1
  almost as much as by step 3; it covers the AT and MCT class stack (0.40 %) with 0.5 % left.
- **The guaranteed limits of the Yageo RT parts (1.25 %) exceed every budget, step 1 included.** With RT parts no R_ILIM3
  value can show the HW-010 limits from datasheet guarantees; step 1 (one resistor, 623 mA) cannot either. Typical RT
  drift is likely far smaller, but this repository holds no source for typical values.

## 4. Sourcing found on 2026-11-22 (LCSC and JLCPCB part pages)
| Part | Value | JLCPCB stock | LCSC stock | Note |
|---|---|---|---|---|
| FH TD03G4702BT (C667109), FH TD03G5622BT (C667119) | 47.0 k, 56.2 k | 0 | 0 | the BOM parts until today: **out of stock** |
| Yageo RT0603BRD0747KL (C326725) | 47.0 k | 17,723 | 0 | HW-010 approved table; the BOM now uses it |
| Yageo RT0603BRD0756K2L (C705784) | 56.2 k | 5,618 | 5,600 | HW-010 approved table; the BOM now uses it |
| Yageo AT0603BRD0754K9L (C855900) | 54.9 k | 798 | 490 | AT class (0.40 % stack) |
| Yageo AT0603BRD0756K2L (C855903) | 56.2 k | 0 | 0 | AT class, out of stock |
| FH TD03G5492BT (C667117) | 54.9 k | 0 | 0 | out of stock |
| Yageo AT0603BRD0747KL | 47.0 k | - | - | no LCSC listing found (web search) |

The BOM (`src/sourcing.py`) now names the two Yageo RT parts of the approved HW-010 table instead of the out-of-stock FH parts.
R_ILIM3 stays 56.2 k in the schematic until the owner decides.

## 5. Options for the owner
| # | Option | For | Against |
|---|---|---|---|
| A | R_ILIM3 = 54.9 k (Yageo AT0603BRD0754K9L), R_ILIM1 and R_ILIM2 Yageo RT; a bench check that measures the three ILIM resistances after reflow on every P1 board and the step windows at 70 degC (TC-210) | the only value that survives tolerance + TCR; in stock; the bench check catches a real drift on the few P1 boards | R_ILIM1 and R_ILIM2 stay unproven by guarantees (a DEV entry for P1); one more part type |
| B | Keep 56.2 k (one part type) with the same bench check | fewest part types | fails the analysis with TCR alone (budget 0.17 % < 0.25 %); a P1 board can pass at room temperature and still be below 1366 mA when warm |
| C | All three in a 0.40 % class (AT or MCT) | the HW-010 limits follow from guaranteed limits | 47.0 k and 56.2 k in AT or MCT class have no stocked LCSC part today; needs other values (a new E192 search with stocked parts) or global sourcing |
| D | Change HW-010 (wider step 1 and step 3 limits, or limits that state the resistor class) | removes the conflict at the source | changes an approved safety requirement; ADR-0010 margins to the source rating get smaller |

**Recommendation: A for P1, and C before a product build.** 54.9 k costs nothing in area and turns the step 3 margin from
1.0 mA into 11.3 mA; the bench check is the honest cover for the RT parts on five boards. A product build needs C or D.

## 6. Not done
No measurement. Typical drift values not used (no source). Life drift beyond 1000 h (product life) not covered. The
resistor temperature range is an assumption. The same-direction drift of all three resistors is assumed (the worst case for
the parallel network). Per-resistor mixed stacks (option A with RT for R_ILIM1 and R_ILIM2) are not computed as a proof;
they fail by construction because the RT stack alone exceeds the step 1 budget. The 1.0 V ILIM voltage stays an assumption
(it only scales the leakage term). The FH TD03G datasheet was not read (the part is out of stock).
