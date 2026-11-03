# Software Requirements

- **Status:** Draft
- **Version:** 0.1
- **Owner:**

Entries use IDs `SW-nnn` and follow `docs/templates/requirement.md`.
Process rules: `docs/process/README.md`.

### SW-001 Input limits of the extractor and mapper

- **Statement:** The extractor and mapper shall accept at most [8] KiB of input text per message, a path depth of at most [8], a path length of at most [64] characters and at most [16] table rows per source, and shall reject anything larger with an error, without crashing or waiting.
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

