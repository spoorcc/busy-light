# ADR-0023: Simpler current-limit gate and smaller packages for one-sided placement

- **Status:** Accepted for the decisions (by the owner, Ben Spoor, 2026-11-18, in the working session: decision 1 "Yes, R3 =
  56.2 k", decision 2 "Yes, fault closes gate", decision 3 left to the assistant's recommendation; recorded by the assistant,
  `docs/journal/2026-11-18-simplification-owner-decisions.md`). The text below was written after the answers and has not been
  read by the owner; no goldfish review. Amends ADR-0016 (gate logic) and ADR-0018 (FAULT_N handling). Answers the
  "fewer parts" option of ADR-0022.
- **Date:** 2026-11-18
- **Deciders / reviewers:** owner (Ben Spoor)
- **Related:** HW-010, HW-008, HW-016, HW-007, SW-005, SW-009, SYS-020, SYS-022, ADR-0010, ADR-0016, ADR-0018, ADR-0022, plan 08

## Context and problem
With every assembled part on the top side, the 46 mm board does not fit (ADR-0022: best overlap 25.1 mm2). The movable parts
take 469 mm2 (60 parts) of about 525 mm2 usable area; one-sided routing at 0.15 mm needs far less. The owner asked to simplify the
schematic creatively to reach one-sided placement. Two facts open a structural simplification:
1. The three ILIM steps are exclusive today: step 3 uses switch U15 alone, and "both switches on" gives 1817 to 2020 mA, above
   the step 3 maximum of 1577 mA; only the NOR gate U13 prevents that state.
2. The TPS3840 RESET (hold-off) and the TPS2553 FAULT are both open-drain outputs; ADR-0018 ANDs them with a gate U10.

## Decision criteria
| Criterion | Weight (1-5) | Source requirement |
|-----------|--------------|--------------------|
| Current-limit safety: no state above the step 3 maximum, fail to the lowest step | 5 | HW-010, SYS-020, ADR-0016 |
| One-sided placement at 46 mm (measured overlap 0) | 5 | HW-008, MECH-001 |
| Fewer parts and part types (cost, Economic PCBA feeder fees) | 3 | SYS-021 |
| Change to firmware and approved texts | 2 | SW-005, SW-009 |
| Bench access and rework | 2 | HW-006, TC-210 |

## Alternatives considered
### A. Step 3 = both switches on, FAULT wired onto the hold-off node, smaller packages (chosen)
R_ILIM3 = 56.2 k (the same part as R_ILIM2): step 2 = switch 2 on, step 3 = both on, switch 3 alone = a step-2-like state. Step
windows (`sim/ilim_steps.py::both_on_windows`, 0.1 % resistors, TMUX1101 limits): step 1 504.2 to 616.6 mA, step 2 934.9 to
1091.7 mA, switch 3 alone 934.9 to 1091.7 mA, step 3 1368.8 to 1553.5 mA (margins 2.8 mA to the 1366 mA minimum, 23.5 mA to the
1577 mA maximum). **No switch state exceeds the step 3 maximum**, so the exclusivity gate U13 is removed. The TPS3840 RESET and
TPS2553 FAULT outputs are wired on one node GATE_OK_RB with one 10 kohm pull-up to 3V3 (R8); the node feeds both 3-input ANDs and
GPIO6. U10 and the 150 kohm HOLD_OK pull-up R6 are removed. A limiter fault now also closes the hardware gate (lowest step), in
addition to the firmware shed of SW-009. Packages: zeners SOT-23 to SOD-323 (BZT52C5V1S), logic U2, U3, U4, U11 to SC-70 (DCK),
eleven pull-up and series resistors to 0402 (JLCPCB basic parts), button pull-up R13 removed (GPIO5 internal pull-up), the
two spare footprints C4, C32 to 0805. The six hold-off capacitors stay 1206 C0G: no 0805 C0G 100 nF part was found (web search
2026-11-18). Measured (scratch placement, 46 mm, keep-out on): the full set reaches overlap 0 (with 0805 hold-off capacitors);
the real generator run without that is in the P1 report.
### B. Keep the exclusive steps, change packages only
Strongest case: no change to the gate logic or the approved texts. Against: measured overlap with packages alone is not 0
(the gate parts are needed too), the over-limit "both on" state stays, two more ICs.
### C. Replace the TPS2553 and both TMUX1101 by a switch with logic-selectable limits
Strongest case: the largest saving (8 to 10 parts) and no analog switch on the ILIM node. Against: no part identified, no
datasheet readable from this container, three steps may become two; more risk and time.
### D. Do nothing / two-sided P1 (ADR-0022 option C)
Against: the owner wants one side; A reaches it with recorded parts and a safety gain.

## Comparison
| Criterion (weight) | A | B | C | D |
|-----------|---|---|---|---|
| Safety (5) | 5 | 3 | 4 | 3 |
| One side at 46 mm (5) | 5 | 2 | 4 | 1 |
| Parts and types (3) | 4 | 2 | 5 | 1 |
| Firmware and texts (2) | 3 | 5 | 2 | 5 |
| Bench access (2) | 3 | 4 | 3 | 5 |
| **Weighted sum** | **74** | **49** | **65** | **43** |

## Decision
A (owner decisions of 2026-11-18). R_ILIM3 = 56.2 k; FAULT closes the gate; all four package changes.

## Consequences
- Positive: no over-limit switch state by construction; U13, U10, R6, R13 removed (97 parts instead of 101); one ILIM part type
  fewer (R_ILIM3 = R_ILIM2) and trim T1 (27.7 k 0805) is not needed; a limiter fault reaches the lowest step in hardware.
- **Negative / trade-offs accepted:** the step 3 lower margin is thin (2.8 mA; the functional side, the safety side has 23.5 mA);
  during an overload the gate can cycle between the selected step and step 1 until the firmware sheds load (SW-009 already
  requires the shed); 0402 and SC-70 parts are harder to probe and rework (TC-210 fault injection); the button relies on the
  firmware enabling the internal pull-up (a floating input until then, harmless: GPIO5 is not a strapping pin).
- New risks (add to risk register): GATE_OK_RB floating if R8 is open (the gate inputs undefined; same class as the old open R6);
  TPS3840 RESET pulled up to 3V3 while its VDD (VBUS_IC) is absent: back-feed through the output not read from the datasheet.
- Requirements created or changed (texts drafted as Proposed in the requirement files, owner to confirm): HW-010 (steps not
  exclusive, step 3 = both, R_ILIM3, GATE_OK_RB wiring, fault-injection rows), HW-016 (spare size [0805]), HW-007 (internal
  pull-up), SW-009 and SW-005 (the "never both" rule and "EN2 and EN3 both high is unknown" change when step 3 is unlocked; while
  the SW-005 table keeps step 3 locked, the firmware never drives both selects and `gate.c` needs no change).

## Verification and revisit
`tests/test_ilim_steps.py::BothOnStep3`, `tests/test_layout_full.py` (gate wiring, no U13/U10/R6/R13, SOD-323 zener pins),
strict ERC 0 findings; P1 placement and routing with the real generator (P1 report); bench: TC-210 step windows including the
"switch 3 alone" state and the fault-closes-gate behaviour. Revisit if the bench shows the step 3 minimum below 1366 mA (then
R_ILIM3 = 54.9 k, margins 13.1 / 12.7 mA, a part with no recorded LCSC number yet) or gate cycling that the firmware cannot settle.

## Critical review notes
Strongest objection: making step 3 depend on two switches means a failed-open switch 2 drops step 3 to the "switch 3 alone"
state (about 1 A) and a failed-open switch 3 drops it to step 2. Answer: both failures go to a lower current, the safe side; the
firmware sees the step through the EN2/EN3 readbacks and the input current. A second objection: wiring FAULT into the gate changes
an accepted ADR-0018 behaviour a day after acceptance. Answer: the owner chose it explicitly; the readback meaning on GPIO6 is
unchanged, and the hardware reaction is toward the lowest step.
