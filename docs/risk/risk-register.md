# Risk Register

- **Status:** Draft (entries are proposed by the author; the owner reviews and accepts risks)

Entries follow `docs/templates/risk.md`. Review at each gate and before every release. Scores are the author's judgement (1 = low, 5 = high); initial risk = severity x likelihood. Nothing is verified yet: `Verified by` lists the planned test cases, which are still stubs.

Source: goldfish review RV-001 and the "new risks" lists of ADR-0003 to ADR-0008.

### RISK-001 False green from stale or push-only data

- **Hazard / failure mode:** Ring shows success while the build is failing or the sender is dead
- **Cause:** Push-only source with no liveness; long poll interval; Jenkins pin broken after factory reset
- **Effect:** Team trusts a wrong green
- **Severity (1-5):** 4  **Likelihood (1-5):** 4  **Initial risk:** 16
- **Mitigated by:** SYS-010, SYS-033, SYS-006, SYS-041, ARCH-012
- **Residual risk (after mitigation):** Working default: SYS-033 is a Must. Residual risk stays until the heartbeat and max-age rules are tested.
- **Verified by:** TC-010, TC-033
- **Status:** Open

### RISK-002 Frozen ring during hang, reset or image swap

- **Hazard / failure mode:** LEDs hold the last frame (for example green) while the firmware is not running
- **Cause:** Single-wire LEDs keep the last frame; bootloader and swap have no LED driver
- **Effect:** Wrong status shown for seconds up to the swap time
- **Severity (1-5):** 3  **Likelihood (1-5):** 4  **Initial risk:** 12
- **Mitigated by:** SYS-011, SYS-018, SYS-029, ARCH-003, ARCH-014
- **Residual risk (after mitigation):** ADR-0004 item 5: accept and document by default; owner decides after the swap time is measured.
- **Verified by:** TC-011, TC-029
- **Status:** Open

### RISK-003 Firmware fault exceeds the current budget

- **Hazard / failure mode:** LED current above the USB-C source limit or connector rating
- **Cause:** Limiter is firmware only; bug or corrupt frame
- **Effect:** Brown-out, hot ring, overloaded USB source
- **Severity (1-5):** 4  **Likelihood (1-5):** 2  **Initial risk:** 8
- **Mitigated by:** SYS-020, ARCH-014, ARCH-001
- **Residual risk (after mitigation):** Hardware backstop is open (ADR-0004 item 4) and is decided after spike 7.5.
- **Verified by:** TC-020
- **Status:** Open

### RISK-004 Brown-out reset when Wi-Fi peak and LED peak coincide

- **Hazard / failure mode:** Random resets under load
- **Cause:** Shared 500 mA budget; transmit peaks
- **Effect:** Unit restarts, ring dark or frozen
- **Severity (1-5):** 3  **Likelihood (1-5):** 3  **Initial risk:** 9
- **Mitigated by:** SYS-020, SYS-027, ARCH-001, ARCH-014
- **Residual risk (after mitigation):** Needs the power budget and bench measurement (spike 7.5).
- **Verified by:** TC-020, TC-027
- **Status:** Open

### RISK-005 Thermal softening of the printed housing

- **Hazard / failure mode:** Housing deforms near the LEDs and module
- **Cause:** Heat from LEDs and radio in a closed 53 mm shell
- **Effect:** Cosmetic damage; possible LED or antenna shift
- **Severity (1-5):** 2  **Likelihood (1-5):** 3  **Initial risk:** 6
- **Mitigated by:** SYS-020, SYS-028, ARCH-005
- **Residual risk (after mitigation):** Gap G10; thermal check on a prototype.
- **Verified by:** TC-020
- **Status:** Open

### RISK-006 Release key lost or leaked

- **Hazard / failure mode:** Units cannot be updated, or an attacker signs images
- **Cause:** Single offline key; weak handling
- **Effect:** Fleet cannot be fixed, or a hostile image is accepted
- **Severity (1-5):** 5  **Likelihood (1-5):** 2  **Initial risk:** 10
- **Mitigated by:** SYS-029, ARCH-010
- **Residual risk (after mitigation):** Key-management document (G8) must exist before any unit leaves the owner. Owner decision 2026-11-03: accepted. The Espressif MCUboot port holds one key, so a lost or leaked release key means a recall of locked units. Two encrypted copies in separate places and a yearly test reduce the likelihood.
- **Verified by:** TC-029
- **Status:** Open

### RISK-007 Development key or test passphrase shipped in a release

- **Hazard / failure mode:** Release image accepted by a key everyone has
- **Cause:** Build script error
- **Effect:** Anyone can install an image
- **Severity (1-5):** 5  **Likelihood (1-5):** 2  **Initial risk:** 10
- **Mitigated by:** SYS-029, SYS-024, ARCH-010
- **Residual risk (after mitigation):** Release build fails on the development key ID; check is part of TC-029.
- **Verified by:** TC-029
- **Status:** Open

### RISK-008 Image does not fit two slots with margin

- **Hazard / failure mode:** Cannot build or update
- **Cause:** 4 MB flash, 1.0 to 1.5 MB image estimate
- **Effect:** Redesign: smaller image, larger flash or different update scheme
- **Severity (1-5):** 4  **Likelihood (1-5):** 4  **Initial risk:** 16
- **Mitigated by:** SYS-026, SYS-029, ARCH-010
- **Residual risk (after mitigation):** Spike 7.1 flash budget decides. A larger module changes the board outline.
- **Verified by:** TC-026
- **Status:** Open

### RISK-009 Zephyr feature missing or unstable on ESP32-C3

- **Hazard / failure mode:** AP+STA, MCUboot, TLS server or LED driver does not work on the pinned revision
- **Cause:** Immature upstream support
- **Effect:** Schedule slip or platform change
- **Severity (1-5):** 4  **Likelihood (1-5):** 3  **Initial risk:** 12
- **Mitigated by:** SYS-025, SYS-026, ARCH-002, ARCH-010, ARCH-015
- **Residual risk (after mitigation):** Spike 7.1 gate; effort cap of [2] weeks per missing feature; local patches need a DEV record. Desk survey (E0, 2026-11-03): AP+STA, RMT LED driver, captive-portal DNS and WPA2-Enterprise on the C3 not found in the documentation; a documented MCUboot failure with flash encryption on the C3 (issue 1866). See `docs/verification/reports/spike-7-1-e0-desk-survey.md`.
- **Verified by:** TC-037
- **Status:** Open

### RISK-010 RAM exhaustion with two TLS sessions

- **Hazard / failure mode:** Handshake fails or device resets under concurrent requests
- **Cause:** Small RAM, TLS buffers, JSON and web buffers
- **Effect:** Web interface or push unavailable
- **Severity (1-5):** 3  **Likelihood (1-5):** 3  **Initial risk:** 9
- **Mitigated by:** SYS-026, SYS-027, ARCH-016, ARCH-017
- **Residual risk (after mitigation):** Needs measured heap with two sessions (spike 7.1) and a limit on concurrent sessions.
- **Verified by:** TC-026
- **Status:** Open

### RISK-011 Antenna detuned by LED ring, housing or ground

- **Hazard / failure mode:** Range below SYS-038
- **Cause:** Module in the ring centre; keep-out violated
- **Effect:** Unit loses Wi-Fi in normal use
- **Severity (1-5):** 4  **Likelihood (1-5):** 3  **Initial risk:** 12
- **Mitigated by:** SYS-038, SYS-028, ARCH-002, ARCH-005
- **Residual risk (after mitigation):** ADR-0003: KiCad keep-out check first, spike 7.2 range test, B as pre-agreed fallback.
- **Verified by:** TC-038
- **Status:** Open

### RISK-012 Unit passphrase exposed through label or weak random source

- **Hazard / failure mode:** Attacker joins the access point or predicts the passphrase
- **Cause:** Label photo; poorly seeded generator at production; prototypes keep secrets in plain flash
- **Effect:** Wi-Fi password captured during provisioning
- **Severity (1-5):** 4  **Likelihood (1-5):** 2  **Initial risk:** 8
- **Mitigated by:** SYS-012, SYS-013, SYS-034, ARCH-015, ARCH-017
- **Residual risk (after mitigation):** ADR-0006: AP off in normal use, [10] min timeout, USB read with button held. Label is a shared secret. WPA3-SAE later.
- **Verified by:** TC-012, TC-013
- **Status:** Open

### RISK-013 Private key or token readable on prototypes

- **Hazard / failure mode:** Someone with the board and a programmer reads flash
- **Cause:** No flash encryption or secure boot on prototypes
- **Effect:** Impersonation of the device; token theft
- **Severity (1-5):** 3  **Likelihood (1-5):** 2  **Initial risk:** 6
- **Mitigated by:** SYS-034, SYS-035, ARCH-017
- **Residual risk (after mitigation):** Prototypes are not for the field. Owner wants secure boot and flash encryption before any unit leaves the owner (2026-11-03); then this risk is closed for those units and replaced by the eFuse risk (RISK-022). Claim limited to network, web interface and access point. EN 18031 / CRA consequence is in the regulatory check.
- **Verified by:** TC-034
- **Status:** Accepted for prototypes

### RISK-014 Downgrade to an old signed image

- **Hazard / failure mode:** Known vulnerability reinstalled
- **Cause:** Release 1 does not block older signed images
- **Effect:** Attacker with the web login runs old firmware
- **Severity (1-5):** 3  **Likelihood (1-5):** 2  **Initial risk:** 6
- **Mitigated by:** SYS-029, SYS-016, ARCH-010
- **Residual risk (after mitigation):** Revisit when the CRA argument needs it (ADR-0007).
- **Verified by:** TC-029
- **Status:** Accepted (owner, 2026-11-03)

### RISK-015 Poll over plain HTTP exposes the Jenkins token

- **Hazard / failure mode:** Token captured on the shared network
- **Cause:** User enters an http URL
- **Effect:** Jenkins account misuse
- **Severity (1-5):** 3  **Likelihood (1-5):** 3  **Initial risk:** 9
- **Mitigated by:** SYS-007, SYS-004
- **Residual risk (after mitigation):** Warn only (working default); owner may forbid it.
- **Verified by:** TC-007
- **Status:** Open

### RISK-016 Pinned device key breaks after factory reset

- **Hazard / failure mode:** Jenkins push fails or ring shows stale
- **Cause:** Reset creates a new key (SYS-041)
- **Effect:** Silent loss of updates
- **Severity (1-5):** 3  **Likelihood (1-5):** 3  **Initial risk:** 9
- **Mitigated by:** SYS-041, SYS-033, ARCH-017, ARCH-018
- **Residual risk (after mitigation):** SYS-033 liveness shows stale; the manual must say that the pin changes.
- **Verified by:** TC-041
- **Status:** Open

### RISK-017 Settings or secrets corrupted by power cut

- **Hazard / failure mode:** Unit loses configuration or the unit passphrase
- **Cause:** Write interrupted
- **Effect:** Unit needs reprovisioning; lost passphrase needs USB recovery
- **Severity (1-5):** 3  **Likelihood (1-5):** 3  **Initial risk:** 9
- **Mitigated by:** SYS-019, SYS-027, SYS-029, ARCH-018
- **Residual risk (after mitigation):** Atomic record with checksum; real power-cut rig on hardware is mandatory evidence (RV-001 item 19).
- **Verified by:** TC-019
- **Status:** Open

### RISK-018 Hostile input crashes or hangs the device

- **Hazard / failure mode:** Malformed JSON, PEM or update stream
- **Cause:** Parsers on untrusted input
- **Effect:** Denial of service on a shared network
- **Severity (1-5):** 3  **Likelihood (1-5):** 3  **Initial risk:** 9
- **Mitigated by:** SYS-005, SYS-027, ARCH-012, ARCH-013, ARCH-016
- **Residual risk (after mitigation):** Limits per ADR-0005; fuzz targets to be written as SW requirements.
- **Verified by:** TC-005
- **Status:** Open

### RISK-019 Wrong time accepted

- **Hazard / failure mode:** Certificate checks pass or fail wrongly
- **Cause:** No RTC; unauthenticated NTP
- **Effect:** Expired certificate accepted, or valid one refused
- **Severity (1-5):** 3  **Likelihood (1-5):** 3  **Initial risk:** 9
- **Mitigated by:** SYS-031, ARCH-015
- **Residual risk (after mitigation):** Lower bound at the build date; scope is outgoing connections only.
- **Verified by:** TC-031
- **Status:** Open

### RISK-020 Closed-source Wi-Fi blob licence or supply change

- **Hazard / failure mode:** Cannot build or redistribute
- **Cause:** Espressif binary blobs in the stack
- **Effect:** Open-source release or build blocked
- **Severity (1-5):** 3  **Likelihood (1-5):** 2  **Initial risk:** 6
- **Mitigated by:** SYS-024, SYS-026, ARCH-002
- **Residual risk (after mitigation):** Check licence and pin hashes; SBOM requirement carried from RV-001 item 23.
- **Verified by:** TC-024
- **Status:** Open

### RISK-021 Photobiological or glare limit exceeded at full white

- **Hazard / failure mode:** Ring too bright at close range
- **Cause:** 16 LEDs at full white
- **Effect:** User discomfort; possible EN 62471 issue
- **Severity (1-5):** 2  **Likelihood (1-5):** 2  **Initial risk:** 4
- **Mitigated by:** SYS-001, SYS-020, ARCH-014
- **Residual risk (after mitigation):** Gap G11; the limiter lowers the maximum; assessment needed before field units.
- **Verified by:** TC-001
- **Status:** Open

### RISK-022 Irreversible eFuse step bricks a unit

- **Hazard / failure mode:** Secure boot or flash encryption is enabled wrongly and the unit cannot be programmed or updated again
- **Cause:** One-time eFuse programming; wrong key, wrong bootloader or an interrupted step; MCUboot with the chip's secure boot is unproven
- **Effect:** Lost unit; for a batch, a lost batch or units that cannot be fixed in the field
- **Severity (1-5):** 4  **Likelihood (1-5):** 3  **Initial risk:** 12
- **Mitigated by:** SYS-029, ARCH-010
- **Residual risk (after mitigation):** Procedure proven on sacrificial boards first; first 10 prototypes without eFuse steps; production step scripted and checked. The staged plan is in ADR-0007; the owner decides after spike 7.1.
- **Verified by:** TC-029
- **Status:** Open
