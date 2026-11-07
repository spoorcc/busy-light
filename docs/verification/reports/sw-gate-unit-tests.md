# Evidence: unit tests of the gate logic (plan 07 increments 2 to 6; SW-005, SW-006, SW-007, SW-009, SW-010)

- **Date:** 2026-11-07. **Author:** assistant. **Status:** Evidence of a host run. Not a verification of the requirements: the bench parts of the test cases are not run.
- **Code:** `sw/app/src/gate.c`, `sw/app/src/gate.h`. **Tests:** `sw/app/tests/gate/src/main.c` (ztest, 20 cases).

## What was run
- Zephyr v4.5.0 workspace at `~/busy-light-zephyr-ws` (host gcc, `ZEPHYR_TOOLCHAIN_VARIANT=host`), board `native_sim/native/64`, command `west twister -T sw/app/tests -p native_sim/native/64`.
- Result as observed: **20 of 20 test cases passed**, 1 of 1 test configurations passed.
- Mutation check (to see that the tests can fail): with two faults put into `gate.c` (the stable-read comparison changed from `<` to `<=`, and the both-selects guard disabled) **8 of 20 cases failed** (12 of 20 passed). The file was restored and the 20 of 20 run repeated.
- Static checks: `gcc -std=c11 -Wall -Wextra -Wconversion -Wpedantic` gives no warning on `gate.c`; `clang-tidy` with `sw/.clang-tidy` gives no finding in the user code (one warning suppressed in non-user code). No MISRA report exists, so no MISRA claim is made.

## Coverage by test case (test names in `main.c`)
| Test case | Cases implemented | Not covered |
|---|---|---|
| TC-105 | (a), (b), (c), (d), (e), (g), (h) | (f) the 700 ms timing (bench), (i) a changed read period, (j) a sub-poll low glitch |
| TC-106 | (a), (b) budget before select, and the late-budget limit | (c) is TC-109; (d) the read-period recompute check; bench part |
| TC-107 | (a), (b), (c), (d), (g), (h), (i) | (e) survival through a real reset hook, (f) fallback without retention; bench retention check |
| TC-109 | edge sheds and does not feed the watchdog; readbacks invalid until configured | (a) the [X] ms timing, (b) a latch of an edge shorter than the poll (needs the interrupt path), (e) the GPIO_INPUT-only check, (f) the build-configuration inspection, (g) forced reset cases on the target; bench part |
| TC-110 | only `gate_service` feeds the watchdog | unit hang hook with a timer and an interrupt context, bench restart time, repeated hang on the target |

## Limits of this evidence
- The module has no Zephyr binding: the GPIO interrupt, the retained RAM, the watchdog driver and the LED layer are not written, so none of that is tested.
- The timing values are test parameters ([100] ms period, 6 reads, 60 s, 3 resets, 600 s window, 50 ms); they are not the product values. [X] ms of SW-009 is not used by the code.
- The code does not yet read the reset cause or the flag from hardware; `gate_boot` takes them as arguments.
- No CI run seen; the CI script changed to run twister (commit f3e26d9).
