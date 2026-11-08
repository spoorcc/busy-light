# Deviation Register

Entries follow `docs/templates/deviation.md`. A suppression in code/CAD without a `DEV-nnn` here is a defect.


### DEV-001 TMUX1101 signal pin above its absolute maximum at power-up (ILIM select switches Q2, Q3)

- **Status:** Proposed (owner decision of 2026-11-05 to use the part with a bench check and this deviation; not Approved; the owner approves)
- **Note 2026-11-07:** the owner decided to remove the exceedance by design (switch supply from VBUS_IC, `docs/verification/reports/analysis-tmux1101-supply-from-vbus.md`, ADR-0016 update of 2026-11-07). This entry is withdrawn when the owner approves that change and TC-210 (d) shows no exceedance; until then it stays Proposed.
- **Rule / requirement deviated from:** hardware standard `docs/standards/design-hw.md`, the component derating rule (voltage at most 80 % of ratings, exceptions documented; here the absolute maximum rating itself is exceeded); TMUX1101 SCDS410D section 6.1: signal voltage at most VDD + 0.5 V. Affects HW-010 (proposed amendment, item (a)), ADR-0010, ADR-0016.
- **Location:** U-select switches that replace Q2 and Q3 on the ILIM node of the TPS2553 (U7); net ILIM_SW2 and ILIM_SW3 (names as in the spike schematic; the board is not final).
- **Justification:** the TPS2553 is enabled directly from VBUS_IC and 3V3 comes from its output through the regulator, so 3V3 is below about 0.5 V while the ILIM node (about 1 V, assumed, not found in the SLVS841G text) already rises. The sequence cannot be changed by the gate (the EN pin is not held low, `analysis-ilim-switch-replacement.md` addendum A.2), and a circular enable on 3V3 is not possible. The TMUX1101 is the only candidate that states 0.2 nA leakage at about 1 V up to 85 C (590 times below the budget of 118 nA); the fallback TS5A3166 states its powered-off leakage (1 uA at 25 C, 5 uA full range) which breaks the step margins in the window.
- **Risk assessment:** the datasheet states no leakage, clamp current or switch state for a signal above VDD + 0.5 V. First-order estimate: with an ESD clamp to VDD (not stated in the datasheet text read) the current is at most about 7 uA (assumed 0.6 V clamp, 56.2 kohm branch, the owner choice of 2026-11-06), taken from the ILIM node, which would raise the current limit in the window by a visible part of the 21 uA of step 1; the effect is unknown, not zero. Possible damage of the switch over many power-ups is not assessed. Compensating measures: the switch is off in the window (100 kohm pull-down on the control pin, fail-safe control input); the firmware starts at the lowest step; the window lasts only while 3V3 is below about 0.5 V. Evidence required: TC-210 point (d) (scope of VBUS_IC, +5V, 3V3 and the ILIM node, window time, peak voltage and limit error, repeated plug-ins). If the effect is not acceptable, use the fallback TS5A3166DBVR and review its powered-off leakage, or add a series resistor or clamp after the bench numbers exist. Related risk: RISK-045.
- **Scope & duration:** prototype only, until the TC-210 bench record exists and the owner decides; then close, change to a permanent deviation with the evidence, or withdraw with a part change.
- **Approved by / date:** not approved (Proposed 2026-11-05)

### DEV-002 Stand-in footprints on the PCB spike (footprint_symbol_mismatch, net_conflict)

- **Rule / requirement deviated from:** `docs/process/hw-generated-design-guardrails.md` (strict DRC with schematic parity); plan 06 section 1 item 4
- **Location:** `hw/kicad/spike-gate/known-open-violations.json`, profiles `placed-4l` and `routed-4l`, classes `footprint_symbol_mismatch` (max 29) and `net_conflict` (max 84), both limited to the refs U1, U8, U9, C1, C1B, C3, C4, D1 to D16, `TP*` and `H*` (checked by `kicad_strict.py`; any other ref fails)
- **Justification:** the spike board uses stand-in land patterns (U1, U8, U9, C1, C1B, C3, C4), the 2020 LED stand-in for D1 to D16 (the schematic still names the 5 x 5 footprint), test points and mounting holes that exist only on the board. The schematic is not changed by plan 06.
- **Risk assessment:** the parts are not the real land patterns; no claim on the parts is made. Foreign refs fail the check, so a real mismatch on another part is not hidden. Evidence: `tests/test_kicad_strict.py` (T14 class), placed DRC run of the spike branch.
- **Scope & duration:** spike only, until the schematic footprints and the real parts are aligned (HW-012 follow-up)
- **Update 2026-11-08:** the schematic now names the real footprints for U8 (TLV75733P SOT-23-5), U9 (CUSTOM:ESP32-C3-MINI-1, datasheet figure 11-1), U1 (TI drawing RWB0012A) and the LEDs (2020 package). Left as stand-ins: C3 (0805) and C4 (1206), whose values are open, and the test points and mounting holes. `footprint_symbol_mismatch` fell from 26 to 8 on the best run; the waiver list in `known-open-violations.json` has not been shortened yet. The owner agreed to shrink this deviation (2026-11-08, in the session).
- **Update 2026-11-08 (evening):** U1 and U9 carry the datasheet pad numbers and the test points are out of the BOM in the schematic too; `net_conflict` fell to 0 and `footprint_symbol_mismatch` to 2 (C3, C4) on the best ring7 run. Owner decision of the same day: profile `stitched-4l` now allows `net_conflict` 0 and `footprint_symbol_mismatch` 2 (refs C3 and C4 only). The older profiles `placed-4l` and `routed-4l` are not changed.
- **Approved by / date:** proposed 2026-11-05; not approved (owner approval pending)

### DEV-003 No project library table and unexplained ignored checks (lib_footprint_issues, ignored_checks)

- **Rule / requirement deviated from:** `docs/process/hw-generated-design-guardrails.md` (strict DRC); plan 06 section 1 item 4
- **Location:** `hw/kicad/spike-gate/known-open-violations.json`, profile `stitched-4l`, `strict_allow` (number only, no ref check)
- **Justification:** the generated spike board uses system-library footprints by name without a project footprint library table (`lib_footprint_issues`), and the generated project file ignores some checks (`ignored_checks`, 5); the cause of the second is not explained yet (plan 06 G4).
- **Risk assessment:** a real library problem on a part is hidden among the counted items; compensating measure: the count is capped at the observed value, so a rise fails.
- **Update 2026-11-08:** the ignored checks are resolved: the generated project files switch the default-ignored ERC and DRC checks on and the ignored-check limits are 0 (the owner agreed to close this part, 2026-11-08). The `lib_footprint_issues` part stays open until a project library table exists (best run: 100 findings, limit 93, not yet analysed).
- **Scope & duration:** spike only, until a project library table exists and the ignored checks are explained
- **Approved by / date:** proposed 2026-11-05; not approved (owner approval pending)

### DEV-004 Antenna keep-out overlap of the module courtyard (courtyards_overlap, items_not_allowed on U9)

- **Rule / requirement deviated from:** HW-005 (antenna keep-out, Draft); Espressif antenna placement guidance; plan 06 amendment A-1
- **Location:** `hw/kicad/spike-gate/known-open-violations.json`, profile `stitched-4l`, `strict_allow`, classes `courtyards_overlap` (max 14 since the owner decision of 2026-11-08; was 16) and `items_not_allowed` (max 1), only findings that include U9
- **Justification:** the library courtyard of ESP32-C6-MINI-1 is the antenna keep-out; the mech design puts ring LEDs and other parts inside it. The courtyard is not shrunk.
- **Risk assessment:** the antenna environment is not acceptable as it stands; no statement on antenna performance is made. Open items for the owner: board cutout, separate antenna board, U.FL variant or module at the edge (mech or HW-005 decision).
- **Scope & duration:** spike only, until the owner decides the antenna arrangement.
- **Approved by / date:** proposed 2026-11-05; not approved (owner approval pending)

### DEV-005 ADR-0016 accepted before its own goldfish review

- **Status:** Approved (owner, 2026-11-07)
- **Rule / requirement deviated from:** the review step of `docs/process/README.md` (an ADR is reviewed before it is accepted; CLAUDE.md rule 2 and the skills `egm-plan`, `egm-review`).
- **Location:** `docs/decisions/ADR-0016-independent-hardware-gate-for-high-current-step.md`, status line ("Accepted before its own goldfish review").
- **Justification:** the owner accepted option B on explicit instruction in the session of 2026-11-04 to let the gate work proceed.
- **Risk assessment:** an unreviewed decision could carry errors into HW-010. The goldfish reviews RV-008 (after acceptance) and RV-010 (2026-11-06) found material points (truth table, hold-off margin, abs-max exceedance) that were then added as amendments and open actions, so the risk was real and is being closed by those records. Compensating measures: Amendment 2 was reviewed by RV-010 before the owner accepted it on 2026-11-07, and the HW-010 revision was approved by the owner on 2026-11-07 after that review; the readiness check of RV-010 stays NO-GO until its open actions are closed.
- **Scope & duration:** one-off, closed when the open actions of RV-010 are closed, the readiness check answers GO, and the owner confirms the closure.
- **Approved by / date:** the owner (Ben Spoor), 2026-11-07, in the session; recorded by the assistant

### DEV-006 Silkscreen findings ignored for five spike footprints

- **Status:** Proposed (the owner decides)
- **Rule / requirement deviated from:** the silk checks of the strict PCB gate (plan 06 section 1 item 3: `silk_edge_clearance`, `silk_over_copper`, `silk_overlap` must be 0)
- **Location:** `hw/kicad/spike-gate/src/pcb_rules.py` (`SILK_WAIVER_REFS`, rules `spike_silk_waiver` and `spike_silk_edge_waiver` in the written `.kicad_dru`); footprints U9, U2, U4, TVS2, J1
- **Justification:** the outline of U9 (module) crosses parts placed inside its courtyard (see DEV-004); J1 silk lies at the board edge; U2, U4 and TVS2 silk touches neighbours. The silk of a prototype board does not change function; fabricators clip silk over pads. The footprints are not edited, so they still match the library.
- **Risk assessment:** a real silk problem on these five parts is hidden. Compensating measure: the rule names the footprints and only silkscreen layers; copper clearance, edge clearance of copper and all other checks stay on. A production board needs the silk fixed instead.
- **Scope & duration:** spike only, until the placement is decided by the owner
- **Approved by / date:** proposed 2026-11-07; **not approved**: the owner declined it (2026-11-08, in the session). The waiver is off by default (`SPIKE_SILK_WAIVER=1` switches it on for comparison); the silk findings must be fixed by placement or footprint changes, still open.
