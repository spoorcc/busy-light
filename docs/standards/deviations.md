# Deviation Register

Entries follow `docs/templates/deviation.md`. A suppression in code/CAD without a `DEV-nnn` here is a defect.


### DEV-001 Stand-in footprints on the PCB spike (footprint_symbol_mismatch, net_conflict)

- **Rule / requirement deviated from:** `docs/process/hw-generated-design-guardrails.md` (strict DRC with schematic parity); plan 06 section 1 item 4
- **Location:** `hw/kicad/spike-gate/known-open-violations.json`, profiles `placed-4l` and `routed-4l`, classes `footprint_symbol_mismatch` (max 29) and `net_conflict` (max 84), both limited to the refs U1, U8, U9, C1, C1B, C3, C4, D1 to D16, `TP*` and `H*` (checked by `kicad_strict.py`; any other ref fails)
- **Justification:** the spike board uses stand-in land patterns (U1, U8, U9, C1, C1B, C3, C4), the 2020 LED stand-in for D1 to D16 (the schematic still names the 5 x 5 footprint), test points and mounting holes that exist only on the board. The schematic is not changed by plan 06.
- **Risk assessment:** the parts are not the real land patterns; no claim on the parts is made. Foreign refs fail the check, so a real mismatch on another part is not hidden. Evidence: `tests/test_kicad_strict.py` (T14 class), placed DRC run of the spike branch.
- **Scope & duration:** spike only, until the schematic footprints and the real parts are aligned (HW-012 follow-up)
- **Approved by / date:** proposed 2026-11-05; not approved (owner approval pending)
