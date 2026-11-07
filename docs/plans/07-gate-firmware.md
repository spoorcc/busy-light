# 07 -- Gate firmware logic (design doc)

- **Status:** Draft (not reviewed by a goldfish; not approved by the owner)
- **Date:** 2026-11-07  **Owner:** Ben Spoor (author: assistant)
- **Area:** sw
- **Requirements addressed:** SW-005, SW-006, SW-007, SW-009, SW-010 (all Approved 2026-11-07); SYS-020; HW-010 (readback inputs)
- **EGM review record:** RV-011 (goldfish review of 2026-11-07, in progress). The readiness rerun of 2026-11-07 is in RV-010 and asked for this plan.

## 1. Problem definition
The USB input current limit has a hardware gate (ADR-0016) and needs the firmware that raises the step only after a stable reading, sheds load when the gate closes, backs off after brown-outs and restarts when hung. Out of scope: the LED, Wi-Fi and mapping firmware, HW-011 sensor, bench measurements, any hardware change.

## 2. Constraints and assumptions
- A1: this plan builds only the **firmware logic slice** on the host (native_sim, ztest) with GPIO, clock, retained-memory and watchdog fakes. No target build, no board, no bench (RV-010 readiness: GO only for this slice).
- A2: bracketed values of the requirements are Kconfig constants, not hard-coded numbers. SW-009 [X] ms has no default; a test fails if it is unset.
- A3: the ESP32-C3-MINI-1 is the module (ADR-0002). The PCB spike uses the ESP32-C6-MINI-1 footprint only as a stand-in because the C3 footprint is not in the KiCad library (`spike-pcb-placement-routing.md`).
- A4: the retained flag of SW-007 uses RTC memory; its survival over this reset cause is **not verified**. Fallback in SW-007: HOLD_OK_RB at the first read only.
- A5: the pin map below is taken from the spike generator `hw/kicad/spike-gate/src/layout_full.py` (lines 551 to 586); it is a spike map, not an approved board map.

## 3. Alternatives considered
| Option | Idea | For | Against |
|---|---|---|---|
| A (recommended) | One pure-C state machine module with a small hardware abstraction (read inputs, write selects, clock, retained store, watchdog), tested on native_sim | testable without a board; MISRA subset is easy to apply; each SW requirement maps to one function | an extra layer of indirection |
| B | Write directly against Zephyr GPIO and kernel APIs in `main.c` | fewer files | only testable on hardware; fails rule 6 (tests with all code) |
| C | Do nothing until a board exists | no rework | no evidence for five Approved requirements for months |

## 4. Technical plan
Module `gate` (no Zephyr includes in the logic file):
- `gate_step()` is called every [100] ms with a snapshot struct (`hold_ok_rb`, `cc_ok_1a5`, `en2_rb`, `en3_rb`, `now_ms`) and returns the select outputs.
- Edge events (falling `hold_ok_rb`, `en2_rb`, `en3_rb`) call `gate_on_edge()`, which latches the event and asks the LED layer to reduce to the lowest-step budget within [X] ms (SW-009).
- Interlock: one function `gate_set_selects()` is the only writer of the select pins and refuses both-high (SW-009 "never both").
- Brown-out back-off (SW-007): counter and back-off deadline in a store behind `gate_store_*` (retained RAM); a reset counts unless `hold_ok_rb` was low at the first read or the retained flag is set.
- Watchdog (SW-010): serviced only from the loop that calls `gate_step()`; no service from a timer or interrupt.
- Inputs valid only while `hold_ok_rb` is high. there is no separate `fault_n`; a limiter fault arrives as a fall of `hold_ok_rb` (GATE_OK_RB, ADR-0018 option E); SW-009 text amendment is Proposed.
Failure behaviour: any unknown input pattern gives the lowest step. Safety: this is the first of two checks; the hardware gate stays the independent one.

## 5. Detailed implementation plan
**Decisions of 2026-11-07 (owner):** FAULT_N combined into GATE_OK_RB (ADR-0018, Accepted); regulator in the standard package with a firmware limit (ADR-0019, Proposed); retained flag cleared when the gate reopens, elapsed-time clock, watchdog resets count toward the back-off, watchdog timeout 8 s (Proposed amendments of SW-007 and SW-010).

**Gate on approval (rule 1):** the SW-005 step table, the removal of FAULT_N from SW-009 and the pin map are Proposed amendments or spike data. No `sw/` file is created until the owner has approved them and this plan.

**Hardware abstraction `gate_hal.h` (interface list, to be fixed in the review):** `gate_hal_read_inputs(snapshot *)`, `gate_hal_write_selects(step2, step3)`, `gate_hal_now_ms()`, `gate_hal_request_budget(level)` (the LED-layer call; level lowest or normal; the layer must reach the budget within [X] ms), `gate_hal_store_read(*)` and `gate_hal_store_write(*)` (retained store), `gate_hal_reset_cause()`, `gate_hal_wdt_service()`. Edge events: `gate_hal` calls `gate_on_edge(which)` from the GPIO interrupt; on native_sim a test injects the edge.

**Mapping of requirements to functions:** SW-005 `gate_step()`; SW-006 `gate_on_advert_fall()` (budget before select, [50] ms from the read that shows the fall); SW-007 `gate_boot()` (reads cause, retained flag and counter at start, before the readback pins are configured, clears the flag after use); SW-009 `gate_on_edge()` and `gate_readbacks_valid()` (false until GPIO20 and GPIO21 are configured as inputs without pull); SW-010 `gate_loop()` (the only caller of `gate_hal_wdt_service()`).

**Pin map validity:** the pin map below comes from the spike generator, which uses the ESP32-C6-MINI-1 footprint as a stand-in (DEV-004). It is not valid for layout or any product file until the ESP32-C3-MINI-1 footprint exists and the map is rechecked.
**Pin map (spike, from `layout_full.py`; to be confirmed in HW-010 and the product schematic):**

| ESP32-C3 GPIO | Net | Direction | Requirement |
|---|---|---|---|
| GPIO0 | CC_OK_1A5 | input | SW-005 |
| GPIO1 | reserved: I2C line for the orientation sensor (owner decision 2026-11-07; was CC_OK_3A, deleted) | not used by the gate | HW-011 |
| GPIO2 | pulled up (R16), strapping pin | not used | HW-010 |
| GPIO3 | SEL_STEP2_GPIO | output | SW-005, SW-009 |
| GPIO4 | reserved: I2C line for the orientation sensor (FAULT_N is combined into GATE_OK_RB, ADR-0018 option E, not yet in the schematic) | not used by the gate | HW-011, SW-009 |
| GPIO5 | BUTTON | input | HW-007 |
| GPIO6 | GATE_OK_RB = hold-off ok AND no limiter fault (AND gate, replaces the buffer; ADR-0018 option E) | input | SW-009 |
| GPIO7 | LED_DATA | output | LED driver |
| GPIO8 | pulled up (R17), strapping pin | not used | HW-010 |
| GPIO9 | BOOT test point | not used | HW-006 |
| GPIO10 | SEL_STEP3_GPIO | output | SW-005, SW-009 |
| GPIO18, GPIO19 | USB_DN, USB_DP | USB | console, programming |
| GPIO20 | STEP2_EN_RB (R14, 100 k) | input, no pull | SW-009 |
| GPIO21 | STEP3_EN_RB (R15, 100 k) | input, no pull | SW-009 |

Note: the first goldfish read guessed GPIO2 and GPIO3 for the selects; the map shows GPIO3 and GPIO10. The owner decided on 2026-11-07 (ADR-0018 option E) to combine FAULT_N into the GATE_OK_RB signal so that GPIO1 and GPIO4 can carry the orientation sensor; the spike schematic still shows FAULT_N on GPIO4 and a buffer on GPIO6 until HW-010 is amended.

- **Files to create (this change set, after approval):** `sw/app/src/gate.c`, `sw/app/src/gate.h`, `sw/app/src/gate_hal.h` (interface only), `sw/app/tests/gate/` (ztest sources, `CMakeLists.txt`, `prj.conf`, `testcase.yaml`), `sw/app/Kconfig` (constants), `sw/app/boards/esp32c3_devkitm.overlay` is **not** created in this slice.
- **Kconfig symbols (the advertised-current step is `BL_ADVERT_STEP`, default 2):** `BL_READ_PERIOD_MS` (100), `BL_STABLE_READS` (6), `BL_SELECT_WINDOW_MS` (700), `BL_BACKOFF_S` (60), `BL_BROWNOUT_MAX` (3), `BL_BROWNOUT_WINDOW_MIN` (10), `BL_SHED_MS` (no default), `BL_ADVERT_FALL_MS` (50, SW-006), `BL_WDT_S` (8, Proposed amendment of SW-010).
- **Order of work:** (1) value table and interlock; (2) SW-005 counter; (3) SW-009 edge latch and shed; (4) SW-007 counter and store; (5) SW-006 time base; (6) SW-010 watchdog.

## 6. Test and verification plan
TC-105, TC-106, TC-107, TC-109, TC-110 at unit level in ztest on native_sim, run by CI; every case has a table of inputs and expected outputs. Cases beyond TC-105 to TC-110: the SW-009 build-configuration checks (a) to (c) and the GPIO_INPUT-only check are part of TC-109. Resource budget (proposed, to be measured): `gate_step()` under [1] ms of CPU and under [2] KiB of RAM including the store; not measured. The native_sim build is not proven: a smoke test that builds and runs an empty ztest is the first increment. Static analysis per `docs/standards/coding-sw.md` (clang-tidy, no MISRA claim without a report). Bench parts of the test cases stay not run.

## 7. Risks and open questions
- SW-005 value table: owner decision 2026-11-07, 1.5 A and 3 A both give the middle step until TC-213; the Proposed amendment must be approved and ADR-0010 open point 3 updated.
- RTC retention of the flag is not shown (A4).
- Native_sim timing is not the target timing; [700] ms and [X] are only checked at the bench.
- Zephyr and west toolchain: not installed or run in this session (not checked).

## 8. Rollout / rollback and traceability
IDs: SW-005, SW-006, SW-007, SW-009, SW-010, SYS-020, TC-105 to TC-110. Rollback: delete `sw/app/src/gate*` and `sw/app/tests/gate/`. Nothing in `hw/` changes.
