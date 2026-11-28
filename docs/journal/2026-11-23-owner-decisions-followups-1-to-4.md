# Follow-ups 1 to 4 of the owner decisions of 2026-11-22 (2026-11-23)

Asked by the owner: "Start with 1-4" (the gate rework, the U5 supervisor, R_ILIM3, R22). jlcpcb.com, lcsc.com, ti.com and rohm.com
became readable from the work container after the environment `busy-light` was created (the earlier `Default` environment
refused them); stock and datasheets below were read on 2026-11-22.

## What was done
| Item | Result | Where |
|---|---|---|
| 1 Gate rework | ADR-0024 (Proposed): U10 + R6 + R8 (FAULT_N) restored, R23 on GPIO0, ESD diode + 100 ohm on CC1 and CC2, TP7 on FAULT_N; schematic generator draws it (57 nets, strict ERC 0 findings, deterministic); HW-010, HW-003, HW-006 and SW-009 proposals written; gate truth table and single faults on the generated netlist | `docs/decisions/ADR-0024-gate-rework-after-rv017.md`, `tests/test_gate_logic_full.py`, `sim/gate_rework_levels.py` |
| 2 U5 | ADR-0025 (Proposed): TPS3808G01 with a 931 k / 100 k divider and one 68 nF C0G, hold-off 221.8 to 572.7 ms (extrapolated from the 180 nF row); TLV803E, NCP303 and BD52xx fail a hard limit; U5 is not changed in the schematic | `docs/decisions/ADR-0025-u5-supervisor-replacement.md`, `sim/supervisor_options.py`, `hw/evidence/parts/tps3808g01.yaml` |
| 3 R_ILIM3 | Table anchor and resistor drift in the model: 56.2 k has a budget of 0.17 % (below tolerance + TCR 0.25 %), 54.9 k has 0.91 %; the owner decides | `docs/verification/reports/analysis-ilim-drift.md`, `sim/ilim_steps.py`, `hw/evidence/parts/ilim-resistors.yaml` |
| 4 R22 | TA-I Tech RLM12FTCMR005 (C316225), 5 mohm 1 % 1 W 1206; worst case 5.14 mohm | HW-017 note, `hw/evidence/parts/rlm12.yaml` |

## Findings that the owner should see
1. **The BOM's ILIM resistors were out of stock.** The FH TD03G4702BT and TD03G5622BT (C667109, C667119) show 0 at LCSC and JLCPCB.
   The BOM now names the Yageo parts of the approved HW-010 table (C326725, C705784; 17,723 and 5,618 in stock).
2. **The guaranteed drift of the in-stock Yageo RT parts (1.25 % per resistor) exceeds every ILIM budget**, step 1 included.
   Only the Yageo AT class (0.40 %) fits, and only for R_ILIM3 = 54.9 k (AT0603BRD0754K9L, C855900, 798 in stock); no AT part for
   47.0 k or 56.2 k is stocked. Options A to D in the analysis report.
3. **CC detection with the 100 ohm resistors:** the Type-C Rd limits were not read; the shift at the TUSB321 is below 0.7 %.
4. **GPIO0 with the internal pull-up on** reads exactly VIL at the 30 kohm corner; the firmware keeps the pull-up off (SW-009 proposal).
5. **HOLD_OK high level** with the VBUS_IC pull-up is 2.04 V against VIH 2.0 V at VBUS_IC 4.3 V with worst-case leakage.
6. **ADR-0025 option B depends on an extrapolation** of the TPS3808 delay spread from 180 nF to 68 nF; TC-210 measures it.
7. The stored `board-p1` is **stale** against the schematic (no U10, R6, R23, R24, R25, TVS3, TVS4, TP7; R22 value); the re-placement
   (plan 08 revision 6) makes the new board. `fab_p1.sh` fails until then, as intended.

## Not done
No bench. U5 not changed (the owner chooses ADR-0025 first). R_ILIM3 not changed (the owner decides). The goldfish review of ADR-0024
and ADR-0025. The regulatory re-check. The ESD test case. Datasheets of the Prosemi LMS12 and the Yageo AT 54.9 k part are not entered
as evidence.
