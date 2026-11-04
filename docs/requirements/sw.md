# Software Requirements

- **Status:** Draft
- **Version:** 0.1
- **Owner:**

Entries use IDs `SW-nnn` and follow `docs/templates/requirement.md`.
Process rules: `docs/process/README.md`.

### SW-001 Input limits of the extractor and mapper

- **Statement:** The extractor and mapper shall accept at most [8] KiB of input text per message, a path depth of at most [8], a path length of at most [64] characters, a document nesting of at most [32] levels (also in parts that are skipped), numbers as 32-bit integers or decimals with at most [6] fractional digits (numbers with an exponent are not accepted as a target), and at most [16] table rows per source, and shall reject anything larger with an error, without crashing or waiting.
- **Rationale:** Bounded input keeps memory and time bounded (ADR-0005 item 3). Oversize input from a source that the user or a network peer controls must not stop the device.
- **Parent:** SYS-005, SYS-008
- **Acceptance criteria:** For every limit, an input one unit over the limit is rejected with a named error and an input at the limit is accepted. The run time on the maximum input is at most [50] ms on the target (measured in spike 7.1). No allocation from the heap happens during extraction.
- **Verification method:** Test
- **Verified by:** TC-101
- **Category:** Robustness
- **Regulatory:** none
- **Priority:** Must
- **Status:** Draft

### SW-002 Limit on concurrent network sessions

- **Statement:** The device shall serve at most [2] TLS sessions at the same time, shall refuse further connections within [1] s with a busy answer, and shall keep the LED output and the watchdog running while sessions are open or refused.
- **Rationale:** RAM is small and a TLS handshake is expensive. A flood of connection attempts on a shared LAN must not exhaust the heap or stop the display (RISK-010, RISK-018).
- **Parent:** SYS-027, SYS-005
- **Acceptance criteria:** With [10] simultaneous connection attempts: [2] sessions work, the others get the busy answer, the free heap stays above the SYS-026 limit, no reset happens in [10] min, and the LED frame rate does not drop by more than [10] %.
- **Verification method:** Test
- **Verified by:** TC-102
- **Category:** Robustness
- **Regulatory:** none
- **Priority:** Must
- **Status:** Draft

### SW-003 Fuzz tests of external inputs

- **Statement:** Each parser of external input (JSON extractor, push body, HTTP request, PEM and X.509 loader, update stream header) shall have a fuzz test that runs on the PC.
- **Rationale:** External input on a shared LAN is untrusted (A3). Fuzzing finds crashes that example tests do not (SYS-005, SYS-025).
- **Parent:** SYS-005, SYS-025
- **Acceptance criteria:** Each fuzz target runs at least [10000] mutated inputs per test run, and a longer run of at least [1] hour before each release, with no crash, hang or sanitizer finding. Found inputs become regression tests.
- **Verification method:** Test
- **Verified by:** TC-103
- **Category:** Robustness
- **Regulatory:** CRA Annex I Part I (2)(h)-(j) *(verify)*
- **Priority:** Must
- **Status:** Draft

### SW-004 Image confirmation and forced restart

- **Statement:** A new image shall confirm itself only after the main loop, the watchdog, the web server and a local health check have run without fault for [30] s, and shall restart itself if it has not confirmed within [45] s of its first start.
- **Rationale:** ADR-0007 item 3 and RV-001 items 7 and 8: the rule must have a trigger, and a confirmed image must be able to receive the next update. Wi-Fi is not part of the rule, so a changed network does not cause a revert loop.
- **Parent:** SYS-029, SYS-027
- **Acceptance criteria:** A test image that hangs before confirming is replaced by the previous image within [60] s of its first start (SYS-029). A test image whose web server does not start does not confirm. A test image on a network without Wi-Fi coverage confirms.
- **Verification method:** Test
- **Verified by:** TC-104
- **Category:** Reliability
- **Regulatory:** none
- **Priority:** Must
- **Status:** Draft


### SW-005 Raise the current limit only after a stable advertised-current reading

- **Statement:** The firmware shall start with the lowest current step and shall select a higher step only after the advertised-current input has given the same value in [5] consecutive reads over at least [500] ms, and shall select a step no higher than the one that the stable value allows.
- **Rationale:** A higher step on a source that advertises only the default overloads the source (RISK-003, RISK-025, RV-006 S1). The hardware gate (ADR-0016) is independent of firmware faults only. This rule is the first of two checks, not a replacement for it.
- **Parent:** SYS-020
- **Acceptance criteria:** After power-up, the step is the lowest until the stable reading exists. A reading that changes inside the window restarts the count. With a stable default reading, the high select outputs stay off. With an unreadable or unknown value, the step is the lowest. The step is set within [1] s of a stable reading (SYS-020).
- **Verification method:** Test
- **Verified by:** TC-105
- **Category:** Safety
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SW-006 Reduce load before lowering the current step

- **Statement:** The firmware shall read the advertised-current input at least every [100] ms during operation, and when the stable value falls, shall reduce the LED current to the new allowed level within [50] ms and only then lower the current step.
- **Rationale:** Lowering the limit under load can cause the brown-out that the limit is meant to prevent (RV-006 S4). Lowering the load first keeps the 5 V rail up.
- **Parent:** SYS-020
- **Acceptance criteria:** A change from the 1.5 A value to the default value at full white: the LED current is at or below the new allowed level within [50] ms, the step is lowered after that, and the device does not reset. The 5 V rail stays above [4.5] V during the change (to be confirmed against HW-004).
- **Verification method:** Test
- **Verified by:** TC-106
- **Category:** Safety
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SW-007 Back-off after a brown-out reset

- **Statement:** After a brown-out reset, the firmware shall start at the lowest current step and shall not raise the step for [60] s, and after [3] brown-out resets in [10] min shall stay at the lowest step until the next power-up and show this state on the LEDs.
- **Rationale:** Without a rule, the device reads the 1.5 A value after each reset and raises the limit again, which gives a reset loop (RV-006 S5).
- **Parent:** SYS-020, SYS-029
- **Acceptance criteria:** After a forced brown-out the step stays lowest for [60] s. After [3] forced brown-outs in [10] min the step stays lowest after a further reset. The reset cause and the counter are kept over a reset (persistence method is a design decision). The LED indication is defined with the user documentation.
- **Verification method:** Test
- **Verified by:** TC-107
- **Category:** Reliability
- **Regulatory:** TBD
- **Priority:** Should
- **Status:** Draft

### SW-008 Tolerance of Power Delivery traffic and source changes on the CC line

- **Statement:** The firmware shall not raise the current step while the advertised-current input changes more often than [once] per [500] ms, and shall give the lowest step when the input does not settle within [5] s.
- **Rationale:** Power Delivery sources and cables put traffic on the CC line, and some sources change the advertised current (RV-006 S3, S6). A filter that never settles must fail to the safe step.
- **Parent:** SYS-020
- **Acceptance criteria:** With a Power Delivery charger, a charger that toggles the advertised value, and a cable with a wrong pull-up (test setup to define): the step never exceeds the one that the true advertised value allows, and the device ends in a stable state in [5] s or at the lowest step.
- **Verification method:** Test
- **Verified by:** TC-108
- **Category:** Safety
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft
