# Spike report: own deterministic KiCad schematic writer

Status: Draft. Spike evidence only, not a verified tool. Traces to ADR-0012 (own writer preferred over the
SKiDL schematic router), ADR-0016, HW-010, HW-003.

## Question

Can a small own script write a legible, deterministic, ERC-clean `.kicad_sch` for the ADR-0016 gate fragment,
so that the SKiDL schematic router (which does not finish on this fragment) is not needed?

## What was built

- `hw/kicad/spike-gate/src/write_sch.py` (224 lines): reads the SKiDL netlist `gate.net` (the output of
  `generate_netlist`), writes `gate.kicad_sch` with kiutils 1.4.8.
- Symbols come from the system KiCad libraries (`/usr/share/kicad/symbols`, KiCad 10.0.6); `extends`
  symbols (2N7002) are flattened into `lib_symbols`.
- Placement: one part per grid cell (5 columns, 88.9 x 50.8 mm, A2 sheet), in natural reference order. Parts
  with only vertical pins (R, C, D) are rotated 90 degrees so the labels run sideways.
- Connections: every pin gets a 5.08 mm wire stub that ends in a local net label. Rail nets (nets that hold a
  PWR_FLAG: `+3V3`, `VBUS_IC`, `GND`) end in a power symbol instead; the PWR_FLAGs are placed as parts. Unconnected
  pins and one-pin nets get a no-connect marker. No routing, no junctions.
- Determinism: no random numbers or clock; UUIDs are `uuid5` of a stable key (reference and pin).
- `src/gen_gate.py --netlist-only` writes only the netlist; `run_writer.sh <python> <out>` runs
  netlist, writer, ERC and parity (reuses `check_gate.py` unchanged). No retry loop is needed.
- `tests/test_write_sch.py` (67 lines, stdlib `unittest`) plus fixture `tests/data/gate.net`.

## Results (observed 2026-11-04, machine of the spike)

| Check | Result |
|---|---|
| `kicad-cli sch erc --severity-error` | 0 errors |
| ERC all severities, first run (before a label font fix) | 0 errors, 63 warnings, all library or footprint table warnings (no `sym-lib-table` next to the standalone file); not re-run after the fix |
| Netlist parity with SKiDL netlist (`check_gate.py`) | 0 differences |
| Determinism | two runs in the same process and one run in a new process (PYTHONHASHSEED=7) give byte-identical files; sha256 `bfae12f7...3798`; `cmp` identical |
| Unit tests `tests.test_write_sch` | 3 run, 3 pass (determinism x2, every connected pin has a label or power symbol at its wire end) |
| Time, writer alone | 2.07 s wall (most of it Python and kiutils start-up and library parsing) |
| Time, `run_writer.sh` (SKiDL netlist, writer, ERC, netlist export, parity) | 4.9 s wall |
| Size | writer 224 lines, test 67 lines; output file 69,587 bytes |

For comparison, `run_gate.sh` with the SKiDL router needed retries and the router did not finish on version 2 of the
fragment.

## Visual check

The sheet was rendered with `kicad-cli sch export pdf` and viewed as an image. All 20 netlist
components (17 parts, 3 PWR_FLAGs) are visible. No part overlaps another part. Small overlaps remain: the +3V3 power symbol
of U4 touches its reference text, and on U1 and U2 the pin labels and no-connect markers sit close together
(U1 pins are 2.54 mm apart). Only the first sheet render was reviewed by eye, at 80 dpi.

## What does not work, honest limits

- A labels-only schematic is machine-correct but not a good design document. Nobody sees a signal flow; the
  reader must match label names. It is legible for a 20-part fragment, not for a full board. Grouping into
  functional blocks (hierarchical sheets) and hand placement are still needed for review documents.
- Placement is a plain grid in reference order; related parts (U2 and R1, for example) are not near each other.
- Pins are handled for unit 1 only. Multi-unit symbols (dual gates) are not supported, and neither are
  hidden power pins, buses, mirrored parts or symbols with alternate body styles.
- Label length is not checked against the cell width. The longest label here fits; a long name can overlap a
  neighbour cell. Vertical labels (the MOSFET drain) are short here only by luck.
- Power symbols are always drawn upright; on a stub that points sideways this looks odd but is correct.
- The `ILIM` net in `gen_gate.py` is created twice (once per loop pass), so the netlist has two one-pin
  nets named `ILIM` and `ILIM1`, and the writer draws no-connect markers on both R_ILIM pins (`N$1`, `N$2` appear).
  Parity ignores one-pin groups, so the check does not catch this. This is a defect of the circuit source,
  not of the writer; it means the parity check cannot see lost singletons (a limit of `check_gate.py`).
- Parity compares pin groups, not net names; the writer keeps the SKiDL names, but a rename would pass.
- The file uses format version 20231120 (set by the script) and was opened by KiCad 10.0.6 only. Opening it
  in the KiCad GUI, and the GUI "update symbols from library" behaviour, were not tried. KiCad may rewrite
  the file on first save.
- The standalone file has no `sym-lib-table`, so ERC with all severities warns about library tables
  (63 warnings); the sheet needs a project directory with library tables before it is a usable project.
- The writer depends on kiutils 1.4.8 (pinned, third party, upstream is slow) and on the symbol library layout
  of KiCad 10. Updating KiCad may change library pin positions and so the output bytes. That is an
  expected, explainable change, but the "byte identical" claim holds only for fixed inputs: netlist, library
  files, kiutils version.
- `tests/test_gate_logic.py` needs `GATE_NET`; the 1 error in a plain `unittest discover` run is that
  existing test with no environment variable set, not a defect of the writer.

## Not run

- GUI open and save, KiCad 9 or older, PCB update from this schematic (`kicad-cli pcb` netlist import).
- SKiDL `generate_schematic` (hangs, by instruction).
- Library-table configuration; footprint checks.
- Any worst-case, power or simulation work; this spike makes no claim there.
- Cross-machine determinism (other OS, Python version). The UUID scheme and ordering do not depend on the
  environment, but only one machine was used.
- MISRA and CERT C checks do not apply (Python spike code). No requirement is traced for this tool; it is
  an ADR-0012 spike and is not product code.

## Conclusion (evidence only)

For this fragment the own writer removes the retry loop and the router hang, in about 220 lines, with ERC 0
errors and 0 parity differences. Whether labels-only output is acceptable as the review document is the user's
call; a hierarchical, block-placed layout is the next step if it is not.
