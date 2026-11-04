# Spike ADR-0016: scripted schematic of the CC gate fragment, checked with KiCad ERC

- **Status:** Draft
- **Date:** 2026-11-04
- **Author:** Claude (exploratory spike on the owner's instruction "Use kicad"). Not reviewed. Nothing here is Approved or Accepted.
- **Related:** ADR-0016, ADR-0012 (Proposed), HW-003 and HW-010 (Draft), RISK-042, RV-008 (H5, H6)
- **Code:** branch `spike/hw-gate`, folder `hw/kicad/spike-gate/` (`src/gen_gate.py`, `src/check_gate.py`, `run_gate.sh`, `tests/test_gate_logic.py`). Exploratory. It must not merge into `main` as design content before HW-003, HW-010 and ADR-0012 are Approved or Accepted (rule 1). Generated files (`.kicad_sch`, netlist, PDF) are not committed (rule 12, no build output).
- **Labels:** every result is marked **run** or **not run**.

## 1. Purpose
RV-008 H5 asked for the circuit behind "an open pull-up reads default" to be drawn. This spike builds the fragment of ADR-0016 option B from code, checks it with KiCad and tests its truth table. It does not choose parts.

## 2. What the fragment contains
Generic parts only: a placeholder 5-pin header for the CC detection IC (VDD, GND, open-drain OUT1_N low = at least 1.5 A, OUT2_N, spare); R1 100 kohm pull-up on OUT1_N; U2 74LVC1G04 inverter giving CC_OK_1A5; two 74LVC1G08 AND gates U3 and U4 (CC_OK AND select GPIO for step 2 and step 3); 100 kohm pull-downs R2 to R5 on both select inputs and both enable outputs; two 2N7002 with placeholder ILIM resistors. Every part is a stock KiCad symbol; no part number of ADR-0016 item 3 is fixed.

## 3. Results
| # | Check | Result | Run |
|---|-------|--------|-----|
| 1 | SKiDL 3.0.0 writes a netlist and a KiCad schematic | Netlist every time. Schematic: the router failed 0 to 3 times in 5 tries (`RoutingFailure`, `KeyError`), so the script retries | **run** |
| 2 | `kicad-cli sch erc` (10.0.6), errors only | 0 errors on the accepted schematics. Earlier tries showed real drops: U3 pin 3 (dual gate, second unit) and R2 pin 1 were missing from the drawn schematic while the netlist had them | **run** |
| 3 | Parity: netlist exported from the schematic against the SKiDL netlist (`check_gate.py`) | 0 differences on accepted schematics. It caught a dropped connection (R5 to U4) that ERC did not report in one try | **run** |
| 4 | `run_gate.sh`: generate until ERC and parity pass | Passed after 1, 3 and 1 generations in three runs | **run** |
| 5 | `tests/test_gate_logic.py`: connectivity (pull-up on the IC output, shared CC_OK net, pull-downs, enable to MOSFET gate) and an ideal-logic truth table | 9 tests pass | **run** |
| 6 | Truth table, on the ideal-logic model | Step enable only if IC output low and select high. IC unpowered, output shorted high, pull-up open, gate logic unpowered: lowest step. IC output shorted low with select high: step enabled (not covered, RISK-042) | **run**, model only |
| 7 | ERC warnings (`lib_symbol_issues`, `footprint_link_issues`) | 37 warnings in the first run (before later changes), only because no library tables were configured for the run; not analysed further | **run**, not resolved |
| 8 | Readable drawing | The PDF is an autorouted tangle with crossing wires and overlapping labels; it is not suitable for review | **run**, looked at one page |
| 9 | Circuit simulation (ngspice) of voltages, delays or glitches | not done: logic levels, thresholds, the IC output voltage and gate delay were not modelled | **not run** |
| 10 | Any datasheet, the CC IC behaviour, the AND gate input thresholds at 3.3 V with the IC output pull-up | not read | **not run** |

## 4. Findings
- **F1.** The fragment is feasible with two stock logic parts and passives; the cost is one more inverter and one AND per gated step (parts count for HW-010 and SYS-021). An IC with a high-active output, or a P-channel stage, would remove U2; not evaluated.
- **F2.** The truth table of ADR-0016 holds on the model for the single faults it lists. The model shares the one IC path between both steps, which is the H1 weakness of RV-008, now visible in the netlist (`test_both_ands_share_the_same_ic_path`).
- **F3.** SKiDL's schematic writer dropped a pin of the second unit of a dual gate symbol. The spike uses single gates. ADR-0012 already prefers an own deterministic writer; this supports that preference but does not prove it is needed for a bigger design.
- **F4.** The SKiDL router is not deterministic and failed or dropped pins in several tries. ERC alone is not enough: the parity check found a missing connection that ERC did not report. Both checks are needed on any generated schematic.
- **F5.** Open: the 3.3 V logic level versus the IC output (open-drain pulled to 3.3 V is fine on paper, not checked against a datasheet), the AND gate input threshold, the inverter delay at plug-in (a short glitch could enable a step before the IC settles; the gate input pull-down does not help here), and the state of the select GPIO during reset (ADR-0010 E24, not found).
- **F6.** The two enable nets share one ILIM node; the spike does not model the TPS2553 ILIM network or the resistor values.

## 5. Not done
No PCB, no footprints checked, no 3D, no DRC, no ngspice, no BOM, no JLCPCB check, no review by a goldfish. The schematic is not a deliverable.

## 6. Recommendation
Keep the fragment as the reference for the truth table; draw the real schematic in the KiCad GUI or with the writer of ADR-0012 after HW-003 and HW-010 are Approved and a part is chosen. Add the parity check to any generated schematic. Add a glitch and power-up sequence check (ngspice) before HW-010 is Approved.
