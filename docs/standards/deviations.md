# Deviation Register

Entries follow `docs/templates/deviation.md`. A suppression in code/CAD without a `DEV-nnn` here is a defect.


### DEV-001 Stand-in footprints on the PCB spike (footprint_symbol_mismatch, net_conflict)

- **Rule / requirement deviated from:** `docs/process/hw-generated-design-guardrails.md` (strict DRC with schematic parity); plan 06 section 1 item 4
- **Location:** `hw/kicad/spike-gate/known-open-violations.json`, profiles `placed-4l` and `routed-4l`, classes `footprint_symbol_mismatch` (max 29) and `net_conflict` (max 84), both limited to the refs U1, U8, U9, C1, C1B, C3, C4, D1 to D16, `TP*` and `H*` (checked by `kicad_strict.py`; any other ref fails)
- **Justification:** the spike board uses stand-in land patterns (U1, U8, U9, C1, C1B, C3, C4), the 2020 LED stand-in for D1 to D16 (the schematic still names the 5 x 5 footprint), test points and mounting holes that exist only on the board. The schematic is not changed by plan 06.
- **Risk assessment:** the parts are not the real land patterns; no claim on the parts is made. Foreign refs fail the check, so a real mismatch on another part is not hidden. Evidence: `tests/test_kicad_strict.py` (T14 class), placed DRC run of the spike branch.
- **Scope & duration:** spike only, until the schematic footprints and the real parts are aligned (HW-012 follow-up)
- **Approved by / date:** proposed 2026-11-05; not approved (owner approval pending)

### DEV-002 No project library table and unexplained ignored checks (lib_footprint_issues, ignored_checks)

- **Rule / requirement deviated from:** `docs/process/hw-generated-design-guardrails.md` (strict DRC); plan 06 section 1 item 4
- **Location:** `hw/kicad/spike-gate/known-open-violations.json`, profile `stitched-4l`, `strict_allow` (number only, no ref check)
- **Justification:** the generated spike board uses system-library footprints by name without a project footprint library table (`lib_footprint_issues`), and the generated project file ignores some checks (`ignored_checks`, 5); the cause of the second is not explained yet (plan 06 G4).
- **Risk assessment:** a real library problem on a part is hidden among the counted items; compensating measure: the count is capped at the observed value, so a rise fails.
- **Scope & duration:** spike only, until a project library table exists and the ignored checks are explained
- **Approved by / date:** proposed 2026-11-05; not approved (owner approval pending)

### DEV-003 Antenna keep-out overlap of the module courtyard (courtyards_overlap, items_not_allowed on U9)

- **Rule / requirement deviated from:** HW-005 (antenna keep-out, Draft); Espressif antenna placement guidance; plan 06 amendment A-1
- **Location:** `hw/kicad/spike-gate/known-open-violations.json`, profile `stitched-4l`, `strict_allow`, classes `courtyards_overlap` (max 16) and `items_not_allowed` (max 1), only findings that include U9
- **Justification:** the library courtyard of ESP32-C6-MINI-1 is the antenna keep-out; the mech design puts ring LEDs and other parts inside it. The courtyard is not shrunk.
- **Risk assessment:** the antenna environment is not acceptable as it stands; no statement on antenna performance is made. Open items for the owner: board cutout, separate antenna board, U.FL variant or module at the edge (mech or HW-005 decision).
- **Scope & duration:** spike only, until the owner decides the antenna arrangement
- **Approved by / date:** proposed 2026-11-05; not approved (owner approval pending)
