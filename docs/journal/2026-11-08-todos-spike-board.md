# 2026-11-08: open to-dos for the spike board (HW-010)

State: branch `fix/spike-fab-review-findings`, three commits on top of main (BOM sourcing fields, 13 MPN groups, capacitor values and spare C32). Not pushed, no PR. Source of the list: `docs/verification/reports/spike-fab-review.md` and its updates of this day.

## Fab review findings still open
- [ ] **MPNs, 60 references.** Missing: resistors and capacitors (JLCPCB basic-library parts with LCSC numbers; owner choice of manufacturer needed), TVS1 and TVS2 (no part chosen), J1 (the GCT USB4085-GF-A in the listings is through-hole; the footprint is edge mount: find the edge-mount variant), U9 (flash variant -N4 or -H4 undecided).
- [ ] **Check the 13 looked-up MPNs against datasheets or the shop at order time.** Distributor listings only. TUSB321RWBR is marked not recommended for new designs at LCSC; WS2812B-2020 is 2.2 x 2 mm at LCSC against 2.0 x 2.0 mm in the footprint; TL3342 force variant is an assumption.
- [ ] **27 parts without a silkscreen designator** (smaller text, other places, or a documented waiver; C32 is one of them).
- [ ] Fiducials: 4 on the board, usual count is 3 per side; JLCPCB's own rules not checked.
- [ ] Two-sided assembly (about 61 parts on the bottom, USB-C is through-hole): cost and process decision.
- [ ] Not run: independent Gerber view, fabricator DFM check, part availability and lifecycle, 3D fit against the housing, panelisation, test-fixture access, thermal, bench.

## Capacitors (HW-014, HW-015, HW-016)
- [ ] Owner: HW-016 asks for spares within [5] mm of U7 pin 6; C4 is 8.2 mm and C32 is 24.1 mm away. Relax the number or make room.
- [ ] Choose real capacitor parts for C2, C3, C5, C6 and the spares; read the DC-bias curves; calculate the effective capacitance (HW-014 and HW-015 criterion 1).
- [ ] RV-013 open points for the HW-014 upper bound: USB-IF inrush test text, surge decision S1 to S3, reverse current at unplug, hot-plug ringing on VBUS_IC (rating of C2).
- [ ] Owner approval of HW-014 to HW-016 (Draft) and ADR-0020 (Proposed).

## Tooling and quality
- [ ] Defect: a second `layout_full.build()` in one process draws extra symbols (253, then 295). Write a failing regression test first, then fix. `tests/test_sourcing.py` works around it.
- [ ] Put the power check into the run picker (ring15 run 1 passed the picker but had no +5V path).
- [ ] After every schematic regeneration run both gates: strict ERC and strict DRC (parity). The sourcing-field change was committed with ERC only and broke the DRC; fixed in `0b01509`.
- [ ] Test points not in a row and mixed IC rotations (placement rules did not help).
- [ ] Schematic simplification (one ILIM resistor, fewer supervisor capacitors): a separate revision with requirement and ADR.

## Process
- [ ] Push the branch and open a PR (owner decision). Reference HW-008, HW-010, HW-014 to HW-016.
- [ ] Antenna: spike 7.2 not run; DEV-004 stays Proposed (ADR-0003). The owner dropped the "add a PCB antenna" request on 2026-11-08; no change made.
