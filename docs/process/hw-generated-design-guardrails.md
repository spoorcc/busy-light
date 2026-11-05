# Guardrails for generated hardware designs

Status: Draft (Proposed process rules). The owner (Ben Spoor) decides which rules block a merge.
Nothing here is Approved. Traces: HW-009, HW-010, HW-012, ADR-0012 (Proposed), ADR-0016, ADR-0017, CLAUDE.md rules 1, 5, 6, 11 and 12.
Source: web research of 2026-11-05 (`research-strict-drc-guardrails.md`, kept outside the repository; the sources are listed in section 7).

**Why.** Schematics and boards of this project are written by scripts that AI agents write and run. A generated
board can pass every check that the generator also controls. The rules below make each check independent of the
generator, make a weakened check visible, and keep a human in the release decision.

Evidence labels: **[doc]** read from the primary page, **[local]** tested with `kicad-cli` 10.0.6, **[secondary]** read from a non-primary page,
**[unverified]** no primary source read; do not write an unverified item into a requirement before it is checked.

## 1. Rules to adopt first

Block = the merge fails if the check fails. Advisory = reported, a human reads it.

| # | Rule | Value or threshold | How to automate | Block | Label |
|---|------|--------------------|-----------------|-------|-------|
| 1 | Any DRC finding fails, warnings and exclusions included | `kicad-cli pcb drc --severity-all --exit-code-violations` (exit code 5) | `scripts/ci_hw.sh` (exists); spike scripts now use `src/kicad_strict.py` | yes | [doc] |
| 2 | Any ERC finding fails | `kicad-cli sch erc --severity-all --exit-code-violations` | same | yes | [doc] |
| 3 | No ignored rule types in the project file | A fresh project ignores missing courtyard, footprint filter mismatch, footprint type mismatch, track end off via, tuning profile | script reads the severities in `.kicad_pro`; fails on `ignore` or `warning`; the JSON key names must be copied from a project saved by the GUI | yes | [local]; key names [unverified] |
| 4 | A rule file is proven loaded | A rejected `.kicad_dru` can look like a clean run | canary board with known violations and a golden expected count; a linter for the rule file | yes | [secondary]; local test inconclusive |
| 5 | Footprint-to-schematic parity | `--schematic-parity` | `ci_hw.sh`; check that the schematic file was found (a silent skip is [unverified]) | yes | [doc] |
| 6 | Zone fill is current | Refill on a copy and compare | `--refill-zones --save-board` on a copy; fail on a difference | yes | [local] |
| 7 | Fab limits as rules with margin | project limit = fab value plus at least 20 % (`docs/standards/design-hw.md`); table in section 3 | committed `.kicad_dru`, linted, canary-tested | yes | [doc] for the fab values; rule syntax mostly [unverified] |
| 8 | Independent pad-net comparison | every (ref, pad) net equals the exported netlist; the checker imports nothing from the generator | separate parser over `kicad-cli sch export netlist` and the board file | yes | project rule |
| 9 | Golden pin table per IC, signed by a human | symbol pins, footprint pads and netlist equal a table with datasheet page references | the evidence files (`hw/evidence/parts`, HW-012) plus a pad-number check; the table is not agent-editable without human approval | yes | idea from PCBSchemaGen [doc abstract] |
| 10 | Track width against current | IPC-2221: 1.577 A needs at least 0.56 mm on an outer layer, 1 oz, 10 K rise (spike result) | script over every segment and via count of the nets with a current budget | yes | formula from the spike; IPC text [unverified] |
| 11 | USB rules | 90 ohm differential pair, matched length, continuous ground reference, TUSB321 stub at most 3.5 mm, 100 nF at VDD | custom rules plus a stub-length script | yes | [doc] (Espressif, TI) |
| 12 | Decoupling and ESD distances measured | Espressif gives no number ("close"); the project must set one, for example a pad-to-pin distance | script; the threshold becomes a requirement | yes | [doc] for the rule; the number is a project choice |
| 13 | Antenna keep-out | no copper under or beside the module antenna; at least 15 mm to the housing | rule area plus a mechanical check | yes | [doc] |
| 14 | Regeneration and determinism | committed files equal generator output; two runs give identical bytes | `generate.py --check`; `cmp` of two builds (spike has it) | yes | project rule |
| 15 | Human sign-off gates | G1 schematic, G2 layout, G3 fabrication files with a DFM report, G4 first article | process; only the owner sets Approved | yes | CLAUDE.md rule 1 |

### Process rules (all block unless marked advisory)
1. **Reviewer agent.** A separate agent with different instructions, no access to the generator source, receives only the artefacts and the checklist and returns a table with file and line evidence. It does not replace scripts or the owner.
2. **Protected paths.** Rule files, project severities, `scripts/ci_hw.sh`, golden pin tables, canary boards and the waiver list need human review. CI fails when one change edits the generator and a checker or threshold file together. A bot cannot approve its own change.
3. **Checker integrity.** Each rule has a negative test: a known-bad input must fail. Flip one pad net in a copy of a good board: parity must fail.
4. **Pinned tools.** The KiCad container, Python packages and the Freerouting jar are pinned by digest or hash. `kicad/kicad:10.0` in CI is a moving tag today.
5. **No claim without an artefact.** A statement in a pull request links to a CI report. A missing input is `NOT RUN`, and once hardware files exist a missing rule file, project file or golden table is a failure.
6. **Reviewable diffs.** Commit a normalised summary of generated files (netlist, BOM, footprint positions, net widths). A raw S-expression diff is not a review.
7. **Waivers are visible.** A waived finding is listed in a file with a reason and a `DEV-nnn`. KiBot `filters` and any `exclusion` severity are waivers (advisory for KiBot as a second runner).
8. **Evidence bundle** per revision in `docs/verification/reports/`: tool versions, command lines, hashes of the inputs and the JSON reports.
9. **Pre-release checklist.** ERC 0; DRC 0 with all severities; only listed waivers; parity pass; zones refilled and unchanged; pin table and land pattern table pass; BOM with MPN and supplier number; placement file rotations reviewed; 3D fit in the housing; test points and fiducials; silk revision; fabrication files regenerated byte-equal; DFM report archived; second-person review recorded.

## 2. Extra checks that a generating agent cannot fake

A check counts when it (a) reads files that KiCad wrote, (b) shares no code or table with the generator, (c) takes its expected values from a human-signed source and (d) has a negative test.

| Check | Rule | Block |
|-------|------|-------|
| Footprint against datasheet land pattern | pad count, pitch, pad size, pin 1, body size from a human-entered dimension table; second-person check | yes |
| Part number against footprint | each BOM line has an MPN and a supplier number whose package matches the footprint | yes (assembly) |
| Polarity and orientation | pin 1 and polarity marks in silk and fab layers; rotations in the placement file against the fabricator convention | yes; the convention is [unverified] |
| Courtyard and 3D fit | no courtyard overlap; STEP export against the housing | yes |
| 5 V clearance | USB is SELV; the fab minimum and the project margin dominate | yes; IPC table values [unverified] |
| ESD and TVS placement | the data lines pass through the TVS pads; distance connector to TVS is a project number | yes |
| Return path | USB pair and LED data line have an unbroken ground reference | yes for USB |
| Thermal | power loss computed from the netlist currents; copper area at thermal pads | yes |
| Test points | at least 1.0 mm pads on every rail and key signal, silk labelled | yes |
| Fiducials | required for the Standard assembly service, not for Economic | yes if Standard |
| Assembly limits | smallest package and pin pitch of the chosen assembly service | yes |
| Output reproducibility | fabrication files regenerated twice are byte-equal after removing dates; the flag names for date handling are [unverified] | yes |
| Gerber diff between revisions | a human views the diff | yes (review) |
| Impedance | JLCPCB offers controlled impedance only on four or more layers; a 2-layer board cannot guarantee 90 ohm | decision (ADR) |

## 3. Fab limits to put in the rule file (JLCPCB rigid board, read 2026-11-05)

Source: <https://jlcpcb.com/capabilities/pcb-capabilities> [doc]. The page contradicts itself on board thickness and copper weight; ask the fabricator when it matters. PCBWay was not checked.

| Parameter | Fab value | Suggested project rule |
|-----------|-----------|------------------------|
| Track and space, 1 or 2 layers, 1 oz | 0.10 / 0.10 mm | at least 0.15 / 0.15 mm |
| Pad to track | 0.10 mm | at least 0.15 mm |
| SMD pad to pad, different nets | 0.15 mm | at least 0.18 mm |
| Via hole / diameter | 0.15 / 0.25 mm | 0.3 / 0.6 mm |
| Annular ring, plated hole, 2 layers | recommended 0.25, absolute minimum 0.18 mm | at least 0.25 mm |
| Hole to hole, pad to pad | 0.45 mm | at least 0.5 mm |
| Plated hole to track | 0.28 mm (recommended 0.35) | at least 0.35 mm |
| Copper to routed edge | 0.2 mm | at least 0.3 mm |
| Silk line, text height, pad to silk | 0.15 / 1.0 / 0.15 mm | 0.15 / 1.0 / 0.2 mm |
| Mask bridge, 1 oz | 0.10 mm (0.13 mm black or white mask) | check the bridge rule for the chosen colour |

Chip rules from the Espressif ESP32-C3 hardware guidelines [doc]: main 3.3 V traces at least 0.64 mm, the main power on inner layers with at least two vias per layer change, 10 uF before the chip, no vias on clock traces, 90 ohm plus or minus 10 % USB pair, antenna at least 15 mm from the housing. TI TUSB321 [doc]: stub at most 3.5 mm, 100 nF at VDD; the other layout bullets were not read.

## 4. Gaps in the spike checks (state at consolidation, 2026-11-05)

| # | Gap | Status |
|---|-----|--------|
| 1 | No `.kicad_dru` and no committed project severity policy; the project file is written by Python with numeric minima only | open |
| 2 | Spike minima are lax: annular ring 0.1 mm (fab minimum 0.15, recommended 0.25 for 2 layers), hole to hole 0.4 mm (fab 0.45), silk clearance 0.0 mm (fab 0.15) | open |
| 3 | Spike ERC used `--severity-error` only; spike DRC had no `--exit-code-violations` and ended in `\| tail -2`, so a failure did not stop the script | **changed** in the spike scripts (section 5) |
| 4 | `pcb_check.py` imports the generator module and its pad map, so it is not an independent check; there is no golden datasheet pin table | open |
| 5 | No canary or negative tests for rules; no waiver list | waiver list for the spike added (section 5); canary tests open |
| 6 | The zone refill result is discarded | open |
| 7 | `ci_hw.sh` skips the regeneration check when `hw/kicad/src/generate.py` is absent, and no `.kicad_*` file is committed today, so it prints `NOT RUN` | open |
| 8 | CI container tag is not pinned by digest; the Freerouting jar is pinned by checksum in the report only | open |
| 9 | No BOM-to-footprint check, no footprint dimension table, no rotation check, no fabrication-file reproducibility check, no decoupling or ESD distance measurement, no return-path check, no test-point or fiducial count, no DFM report step | open |
| 10 | No code-owner or protected-path policy for checker and rule files; no reviewer-agent protocol for generated boards | open |
| 11 | 2 layers against 4 layers: controlled impedance only on four or more layers at JLCPCB; the PCB spike moved to 4 layers on routing evidence | decision (ADR) |

## 5. What changed in the spike scripts

`hw/kicad/spike-gate/src/kicad_strict.py` runs `kicad-cli` with `--format json --severity-all --exit-code-violations` (DRC also `--schematic-parity --refill-zones`).
Every warning, error, unconnected item and ignored check counts. Mode is chosen by `SPIKE_ALLOW_KNOWN_OPEN`:
`0` (program default) fails on any finding; `1` (set by the spike `run_*.sh` scripts while the spike is open) tolerates only types that
`known-open-violations.json` lists with a reason and a maximum count. A new type, or a count above the maximum, fails. The list is a waiver list and records the state of 2026-11-05; it is not a claim that these findings are acceptable.
No new rule was added.

## 6. Open decisions for the owner

1. Which rules in section 1 block a merge, and which stay advisory.
2. Whether the spike waiver list is accepted for the spike only, and a date or event after which the list must be empty.
3. 2 or 4 layers (rule 11 and gap 11), and whether ADR-0012 covers it.
4. Numbers the project must choose itself: decoupling and ESD distances, margin on fab limits.
5. Who may change protected files (rule 2 of the process rules).

## 7. Sources and unverified items

Primary pages read: KiCad 10 command-line reference and PCB editor manual (custom rules), JLCPCB PCB and assembly capability pages, Espressif ESP32-C3 hardware design guidelines (schematic checklist, layout, USB Type-C guide), TI TUSB321 datasheet layout section, KiBot preflight documentation, PCBSchemaGen (abstract only).
Secondary or snippet only: the kicad-druid project, the Hackaday language-model test, EDA Bench, PCBInnoBench, HWE-Bench, a vendor summary of aerospace PCB standards.

Unverified, not to be written into a requirement before a check: the JSON key names of the severities in the project file; the exact syntax of most starter `.kicad_dru` rules (only six examples are verbatim from the manual); whether `kicad-cli` exits non-zero on a malformed rule file; whether `--schematic-parity` silently skips when no schematic is found; IPC-2221B and IPC-7351 table values; JLCPCB assembly rules for edge distance, spacing and via-in-pad; rotation conventions; KiBot diff and bill-of-materials viewer output; SKiDL ERC behaviour; NASA and ESA review checklists (none obtained); any published taxonomy of language-model errors in electronics design; whether USB full speed on the ESP32-C3 requires controlled 90 ohm impedance.
