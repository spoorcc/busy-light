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
- **Residual risk (after mitigation):** Hardware backstop is open (ADR-0004 item 4) and is decided after spike 7.5. Owner decision 2026-11-04: a higher current is allowed when the source advertises it (up to [1500] mA, SYS-020), so a limiter fault now overloads a source that advertises more: the backstop question is more important and the limiter budget must follow the CC reading with the safe default of [500] mA.
- **Verified by:** TC-020
- **Status:** Open

### RISK-004 Brown-out reset when Wi-Fi peak and LED peak coincide

- **Hazard / failure mode:** Random resets under load
- **Cause:** Shared 500 mA budget; transmit peaks (paper budget 7.5: with the ESP32-C3-MINI-1 TX peak of 350 mA at 3.3 V, about 454 mA are used on the 3.3 V rail in the worst case, leaving 46 mA (LDO) or 148 mA (buck at 85 %) of the 500 mA for the LEDs; see `spike-7-5-power-budget-paper.md`)
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
- **Cause:** 4 MB flash, 1.0 to 1.5 MB image estimate (paper budget E2a: break-even about 1.31 MiB at the 75 % rule; size ladder E2b: a throw-away image with Wi-Fi, TLS server and client, JSON, DHCP, LED and settings is 792 KB signed, 43 % of the default slot, a lower bound without the web page, update and EAP code)
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
- **Residual risk (after mitigation):** Spike 7.1 gate; effort cap of [2] weeks per missing feature; see RISK-023 for the secure-boot bootloader chain; local patches need a DEV record. Desk survey (E0, 2026-11-03, source read at v4.5.0): AP+STA exists in the driver (untested on the C3); an RMT LED driver is not needed (ADR-0004 uses SPI); captive-portal DNS is custom code; WPA2-Enterprise is mapped to the Espressif blob; a documented MCUboot failure with flash encryption on the C3 (issue 1866, fixed per the reporter by a `write-block-size` overlay); virtual eFuses exist in v4.5.0 (untested). See `docs/verification/reports/spike-7-1-e0-desk-survey.md`.
- **Verified by:** TC-037
- **Status:** Open

### RISK-010 RAM exhaustion with two TLS sessions

- **Hazard / failure mode:** Handshake fails or device resets under concurrent requests
- **Cause:** Small RAM, TLS buffers, JSON and web buffers (size ladder E2b: static RAM is 285 KB of 360 KB used in the throw-away image; the TLS server alone adds about 75 KB, mostly its 60 000 B mbedTLS heap; run-time heap use unknown)
- **Effect:** Web interface or push unavailable
- **Severity (1-5):** 3  **Likelihood (1-5):** 3  **Initial risk:** 9
- **Mitigated by:** SYS-026, SYS-027, SW-002, ARCH-016, ARCH-017
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
- **Mitigated by:** SYS-005, SYS-027, SW-003, ARCH-012, ARCH-013, ARCH-016
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
- **Residual risk (after mitigation):** Possible rehearsal with virtual eFuses (Zephyr `ESP32_EFUSE_VIRTUAL`, untested); module revision at least v0.3; procedure proven on sacrificial boards first; first 10 prototypes without eFuse steps; production step scripted and checked. The staged plan is in ADR-0007; the owner decides after spike 7.1.
- **Verified by:** TC-029
- **Status:** Open

### RISK-023 Secure boot needs a second bootloader build chain

- **Hazard / failure mode:** The chip's secure boot v2 and flash encryption cannot be enabled in the bootloader that Zephyr sysbuild builds
- **Cause:** Zephyr v4.5.0 MCUboot (`boot/zephyr`) has no such options; they exist only in the standalone Espressif port, which needs an ESP-IDF 6.0.x HAL (spike 7.1 E11a)
- **Effect:** A second, pinned build chain and a second toolchain in the product; the flash map of the bootloader and of the Zephyr application must match; more to audit (SBOM, SYS-044) and to keep secure (CRA)
- **Severity (1-5):** 3  **Likelihood (1-5):** 4  **Initial risk:** 12
- **Mitigated by:** SYS-043, SYS-044, ARCH-010
- **Residual risk (after mitigation):** Owner decision pending: accept a pinned ESP-IDF bootloader build, or reconsider secure boot for release 1. Stage 1 prototypes are not affected.
- **Verified by:** TC-043
- **Status:** Open

### RISK-024 Source advertises more current than it delivers

- **Hazard / failure mode:** The source advertises 1.5 A but supplies less (weak charger, long or thin cable, cable drop)
- **Cause:** Allowed current follows the CC advertisement (SYS-020, ADR-0009)
- **Effect:** Brown-out reset of the device, or the source shuts down
- **Severity (1-5):** 3  **Likelihood (1-5):** 3  **Initial risk:** 9
- **Mitigated by:** SYS-020, HW-003, HW-004, ARCH-001
- **Residual risk (after mitigation):** Margin of [10] % on the advertised value; a brown-out detector that drops the limit to [500] mA after a reset (to specify)
- **Verified by:** TC-203
- **Status:** Open

### RISK-025 CC voltage read wrongly

- **Hazard / failure mode:** The advertised current is read wrongly and the device draws up to 1350 mA from a source that advertises 500 mA
- **Cause:** ADC error, Wi-Fi noise, tolerance of Rd or Rp (ADR-0009)
- **Effect:** Overloaded source or cable
- **Severity (1-5):** 4  **Likelihood (1-5):** 2  **Initial risk:** 8
- **Mitigated by:** SYS-020, HW-003, ARCH-001, ARCH-014
- **Residual risk (after mitigation):** Single threshold inside the gap between the bands, repeated reads, fallback to [500] mA; a hardware current limit is wanted by the owner (HW-010, ADR-0004 item 4): it starts at [500] mA and is raised by the firmware after the CC read. It covers a stopped firmware and a short circuit, **not** a firmware that misreads CC and raises the limit itself (RV-006 S1); an independent path from firmware faults is decided in ADR-0016; it does not cover a fault of the detection IC itself (RISK-042)
- **Verified by:** TC-203, TC-020
- **Status:** Open

### RISK-026 CC pin over-voltage damages the processor input

- **Hazard / failure mode:** The CC pin sees a voltage above the processor pin rating (VCONN supply or a fault) and damages the ADC pin
- **Cause:** CC lines connect directly to processor inputs without a divider (ADR-0009, option A)
- **Effect:** Unit does not start or cannot read the advertised current
- **Severity (1-5):** 3  **Likelihood (1-5):** 2  **Initial risk:** 6
- **Mitigated by:** SYS-020, HW-003
- **Residual risk (after mitigation):** Pin voltage rating still *not found* in the sources read; with ADR-0016 the CC pins belong to a detection IC (the ADC pin no longer touches CC); TUSB321 datasheet: CC pins 6 V absolute maximum, 7 kV HBM (`docs/verification/reports/cc-ic-datasheet-evidence.md`); a fault above 6 V on CC and a clamp are still to decide
- **Verified by:** TC-203
- **Status:** Open

### RISK-027 Hardware current limit band is wider than the margin

- **Hazard / failure mode:** The limit band is up to +25 % at 500 mA and up to about +5 % over the advertised 1500 mA at the top step, so the limit does not protect a source at its exact rating, or trips below the firmware value
- **Cause:** Tolerance of the current-limit switch and of the set resistor (ADR-0010, finding 2)
- **Effect:** Overloaded source, or a false trip on a legitimate draw
- **Severity (1-5):** 3  **Likelihood (1-5):** 3  **Initial risk:** 9
- **Mitigated by:** HW-010, SYS-020, ADR-0010
- **Residual risk (after mitigation):** Band chosen by owner instruction 2026-11-04 (ADR-0010 open points 1 and 2): 506 to 623 mA at the first step with a 500 mA firmware budget; 1366 to 1577 mA at the top step with a 1350 mA firmware value. The limit can be up to about 5 % over a 1.5 A source rating in a fault; not assessed further. Owner confirmation, bench values (TC-210) and the thermal analysis are open
- **Verified by:** TC-203, TC-020
- **Status:** Open

### RISK-028 Peak above the limit collapses the 5 V rail

- **Hazard / failure mode:** A peak above the constant-current limit lets the 5 V rail fall, the buck draws more current as a constant-power load, and the unit resets
- **Cause:** Constant-current limiting without foldback; Wi-Fi and LED peaks coincide (ADR-0010, E5)
- **Effect:** Brown-out reset in the field; related to RISK-004
- **Severity (1-5):** 3  **Likelihood (1-5):** 3  **Initial risk:** 9
- **Mitigated by:** HW-004, HW-010, ADR-0010 (firmware budget below the minimum hardware limit, bulk capacitance)
- **Residual risk (after mitigation):** Not assessed; no simulation or bench evidence yet (behavioural model in `hw/sim/` proposed)
- **Verified by:** TC-020, TC-203
- **Status:** Open

### RISK-029 Higher current step stays on after a firmware fault

- **Hazard / failure mode:** The limit select output is driven high while the firmware hangs, or the select MOSFET shorts, so the higher step stays on
- **Cause:** Single fault in the select path (ADR-0010)
- **Effect:** The hardware backstop allows the higher limit; this single fault is not covered
- **Severity (1-5):** 3  **Likelihood (1-5):** 2  **Initial risk:** 6
- **Mitigated by:** HW-010, ADR-0010 (gate pull-downs, R1-only start state)
- **Residual risk (after mitigation):** Not assessed; owner to accept or add a watchdog-driven drop to the lower step
- **Verified by:** TC-020
- **Status:** Open

### RISK-030 Chosen current-limit switch unavailable or not recommended for new designs

- **Hazard / failure mode:** The switch is an extended part, goes out of stock or is marked not recommended for new designs (as found for TPS2553-1 and AP22802)
- **Cause:** Single-source part in a 5-year support period (SYS-021 cost)
- **Effect:** Re-layout and re-verification for another part
- **Severity (1-5):** 3  **Likelihood (1-5):** 3  **Initial risk:** 9
- **Mitigated by:** HW-010, SYS-021, ADR-0010
- **Residual risk (after mitigation):** Not assessed; second source with the same footprint to be named in the BOM
- **Verified by:** Design review of the BOM at G2 of ADR-0012
- **Status:** Open

### RISK-031 USB-C receptacle does not fit inside the LED ring

- **Hazard / failure mode:** The receptacle (8.94 mm wide, reaching in to about R 16) collides with the LED ring (R 20, pitch 7.85 mm, LED bodies about 2 mm)
- **Cause:** 16 LEDs on a ring of 40 mm and a board of 46 mm (HW-001), receptacle on the same side at the board edge (HW-003, SYS-022); found by the FreeCAD spike model (`mech-spike-model.md`, check UsbC-Leds, 2.6 mm3 overlap)
- **Effect:** Board cannot be laid out as specified; no azimuth works on this ring
- **Severity (1-5):** 3  **Likelihood (1-5):** 5  **Initial risk:** 15
- **Mitigated by:** HW-001, HW-003, SYS-022, ARCH-003
- **Residual risk (after mitigation):** Modelled on the spike branch `spike/mech-concept` (placeholders): V1 board tab plus wall bulge passes all checks, largest outer dimension 57.43 mm; V2 bottom-side receptacle passes with a floor pocket or taller posts but breaks the one-side assembly of SYS-022; a larger ring is not possible within 58 mm. Owner decision needed.
- **Verified by:** TC-201, TC-209
- **Status:** Open

### RISK-032 Generated layout fails RF or EMC review

- **Hazard / failure mode:** The scripted placement and routing of the antenna, USB-C and ESD area is worse than a hand layout and the failure is found late
- **Cause:** ADR-0012 option B (generated hardware); keep-out of ADR-0011 already below the vendor figure
- **Effect:** Board respin; RED radio and EMC evidence delayed
- **Severity (1-5):** 4  **Likelihood (1-5):** 3  **Initial risk:** 12
- **Mitigated by:** ADR-0012 items 3, 5, 6 (DRC-enforced keep-out, review set, pre-compliance scan, fallback to GUI routing)
- **Residual risk (after mitigation):** Not assessed; no RF evidence exists (spike used a stand-in)
- **Verified by:** Gate G2 of ADR-0012; TC-nnn to be written
- **Status:** Open

### RISK-033 Generator or build tool compromised, changed or abandoned

- **Hazard / failure mode:** A dependency (kiutils, KiCad, Freerouting jar, Java runtime) changes a net or part in the generated hardware, or is abandoned during the 5-year support period
- **Cause:** Hardware authored by code; community tools; unsigned jar; floating tags
- **Effect:** Wrong or non-reproducible board that still passes ERC
- **Severity (1-5):** 4  **Likelihood (1-5):** 2  **Initial risk:** 8
- **Mitigated by:** ADR-0012 items 4, 11, 12 (digest and hash pins, tool-qualification table, SBOM, regeneration gate, tool change procedure)
- **Residual risk (after mitigation):** Not assessed; pins are not yet in place
- **Verified by:** Gate G1 of ADR-0012
- **Status:** Open

### RISK-034 Generated files and generator drift apart

- **Hazard / failure mode:** A reviewer or the owner saves a generated file in the KiCad GUI (KiCad 10 rewrites the format), or a manual edit passes the check
- **Cause:** Committed generated files; the semantic dump covered parts, nets and positions only
- **Effect:** Released board differs from the reviewed source
- **Severity (1-5):** 3  **Likelihood (1-5):** 3  **Initial risk:** 9
- **Mitigated by:** ADR-0012 items 1 and 11 (marker, full-scope dump, CI regeneration gate, negative tests)
- **Residual risk (after mitigation):** Not assessed; the gate is not implemented
- **Verified by:** Gate G1 of ADR-0012
- **Status:** Open

### RISK-035 Licence-incompatible dependency in the build

- **Hazard / failure mode:** A dependency or blob (Wi-Fi binaries, Mbed TLS licence choice, KiCad or vendor libraries) has terms that conflict with Apache-2.0 for code or CC BY-NC-SA 4.0 for the rest
- **Cause:** Mixed licences (ADR-0013); vendor material may land in the repository under the catch-all CC licence
- **Effect:** Distribution not allowed, or a licence violation in a published image or file
- **Severity (1-5):** 3  **Likelihood (1-5):** 3  **Initial risk:** 9
- **Mitigated by:** ADR-0013 item 6, SYS-044
- **Residual risk (after mitigation):** Not assessed; compatibility table and NOTICE file do not exist yet (RV-005)
- **Verified by:** `reuse lint` in CI; compatibility table (to be written)
- **Status:** Open

### RISK-036 Meaning of "non-commercial" leads to a dispute

- **Hazard / failure mode:** Hobbyists, charities, schools and companies disagree with the owner on what CC BY-NC-SA 4.0 allows
- **Cause:** The licence text defines non-commercial vaguely; LICENSE.md gives no examples
- **Effect:** Dispute, bad reputation or a licence that cannot be enforced
- **Severity (1-5):** 3  **Likelihood (1-5):** 3  **Initial risk:** 9
- **Mitigated by:** ADR-0013, LICENSE.md
- **Residual risk (after mitigation):** Not assessed; FAQ with examples and a lawyer check are open (RV-005)
- **Verified by:** Legal review (no test case)
- **Status:** Open

### RISK-037 Contributor terms are not enforceable

- **Hazard / failure mode:** Contributions arrive without a valid grant, so the owner cannot license them commercially or defend the licence
- **Cause:** Draft terms in CONTRIBUTING.md; a sign-off certifies origin but is not a licence grant
- **Effect:** Split ownership of the design; the commercial route is blocked
- **Severity (1-5):** 3  **Likelihood (1-5):** 2  **Initial risk:** 6
- **Mitigated by:** CONTRIBUTING.md notice (no outside contributions until the legal check), ADR-0013
- **Residual risk (after mitigation):** Not assessed
- **Verified by:** Legal review (no test case)
- **Status:** Open

### RISK-038 CRA role differs from the open-source steward assumption

- **Hazard / failure mode:** The project is treated as a manufacturer of a product with digital elements, not as an open-source steward
- **Cause:** Hardware and documents are source-available (not open source) and the owner may sell commercial licences (ADR-0013)
- **Effect:** Full manufacturer duties (vulnerability handling, SBOM, reporting) apply to published firmware
- **Severity (1-5):** 3  **Likelihood (1-5):** 4  **Initial risk:** 12
- **Mitigated by:** ADR-0013, SYS-044, SYS-045
- **Residual risk (after mitigation):** Plan for the manufacturer role; legal check open (applicability.md question 4)
- **Verified by:** Regulatory check (no test case)
- **Status:** Open

### RISK-039 Bayonet lug creeps, breaks or releases

- **Hazard / failure mode:** The printed lugs or the detent creep in a warm unit, break, or release when the unit is turned by hand; the unit falls
- **Cause:** FDM lugs in PETG or ASA at 50 to 60 deg C; hanging and leverage loads; a 30 degree turn unlocks (ADR-0014)
- **Effect:** Unit falls off a wall or stand while on USB power
- **Severity (1-5):** 3  **Likelihood (1-5):** 3  **Initial risk:** 9
- **Mitigated by:** MECH-007, MECH-008, ADR-0014
- **Residual risk (after mitigation):** Not assessed; load case, unlock torque and geometry are open (RV-007)
- **Verified by:** TC-307, TC-308
- **Status:** Open

### RISK-040 Accessory covers the label or puts metal near the antenna

- **Hazard / failure mode:** A locked accessory hides the label with the passphrase, or has a metal part near the antenna
- **Cause:** Label and accessories share the back; accessories are made by users
- **Effect:** Passphrase unreadable while mounted; range loss or detuning (RISK-011)
- **Severity (1-5):** 3  **Likelihood (1-5):** 3  **Initial risk:** 9
- **Mitigated by:** MECH-006, MECH-007, MECH-003
- **Residual risk (after mitigation):** Not assessed; range test with accessories attached is not planned yet (RV-007)
- **Verified by:** TC-306, TC-303
- **Status:** Open

### RISK-041 Orientation is reported wrongly

- **Hazard / failure mode:** The level gauge starts at the wrong place: flat unit, stand tilt near the 30 degree limit, ring facing down, sensor failed or knocked
- **Cause:** An accelerometer gives no in-plane direction when flat (SYS-047)
- **Effect:** A level is read wrongly (display only; status colours are not affected)
- **Severity (1-5):** 2  **Likelihood (1-5):** 3  **Initial risk:** 6
- **Mitigated by:** SYS-047, HW-011
- **Residual risk (after mitigation):** Not assessed; filtering, hysteresis and face-down behaviour are open (RV-007)
- **Verified by:** TC-047, TC-211
- **Status:** Open

### RISK-042 CC detection IC misclassifies a charger with no firmware second opinion

- **Hazard / failure mode:** The IC reports 1.5 A for a source that advertises the default current (or latches or fails with its output low), so the gate and the firmware both read "high" and the high step switches on
- **Cause:** The IC thresholds fill the 90 mV gap between the bands (0.61 to 0.70 V); a fault in the IC or its output; the Type-C specification was not read (ADR-0016)
- **Effect:** Overloaded source or cable; the hardware gate no longer protects (it is independent of firmware faults only)
- **Severity (1-5):** 4  **Likelihood (1-5):** 2  **Initial risk:** 8
- **Mitigated by:** HW-003, HW-010, ADR-0016
- **Residual risk (after mitigation):** Not assessed; band-edge and fault-injection tests are open; a diverse second opinion (ADC or comparator) is not part of ADR-0016; a start-up hold-off of at least [200] ms on the gate is required (HW-010) because the IC output level before its first debounce is not stated
- **Verified by:** TC-203, TC-210
- **Status:** Open

### RISK-043 CC detection IC temperature range, package or availability

- **Hazard / failure mode:** The IC is specified for 0 to 70 C recommended (datasheet) in a closed housing with a hot LED ring; its X2QFN 1.6 mm package may not suit the shop; it goes out of stock or has one source
- **Cause:** Single candidate part (ADR-0016); conflicting range of the vendor and a distributor listing
- **Effect:** Misreads at temperature, assembly yield loss, or a re-layout for another part
- **Severity (1-5):** 3  **Likelihood (1-5):** 3  **Initial risk:** 9
- **Mitigated by:** HW-003, ADR-0016 item 3 (checks before a part is fixed), SYS-021
- **Residual risk (after mitigation):** TUSB321 chosen by the owner 2026-11-04; datasheet confirms 0 to 70 C, the prototype must record the IC ambient (HW-003) with PTN5150A as fallback; the older PTN5150 states -40 to +85 C and is a candidate second source (PTN5150A not read; `docs/verification/reports/cc-ic-datasheet-evidence.md`)
- **Verified by:** Design review of the BOM at G2 of ADR-0012; TC-203
- **Status:** Open

### RISK-044 Hold-off supervisor of the current-limit gate fails or is mis-set

- **Hazard / failure mode:** The start-up hold-off of the gate (HW-010) is lost or too short: the supervisor output is stuck high or shorted, its delay capacitor is shorted, open, mis-valued (X7R loses capacitance under DC bias) or leaks, or a dip of VBUS does not discharge the capacitor and so does not restart the full delay
- **Cause:** One extra part in the gate path (ADR-0016 spike, version 3); the delay is set by a capacitor (TPS3840: tD = 618937 x C + 50 us, datasheet constants); the datasheets do not state the discharge time of the delay capacitor or its leakage
- **Effect:** An IC output glitch before its first debounce (RISK-042) can switch on the high current step for a source that advertises the default current
- **Severity (1-5):** 4  **Likelihood (1-5):** 2  **Initial risk:** 8
- **Mitigated by:** HW-010 (hold-off at least [200] ms, at most [600] ms), SW-005 (firmware waits for equal reads), `docs/verification/reports/datasheet-evidence-supervisor.md` on branch `spike/hw-gate` (candidate part TPS3840DL40; C0G or film capacitor at 5 % or better is needed for a 200 to 600 ms window)
- **Residual risk (after mitigation):** Not assessed. Part not chosen (owner decision). Dip restart is not guaranteed by the datasheets and needs a bench or simulation check; a stuck-high output is a single fault that removes the hold-off, not covered by the gate itself
- **Verified by:** TC-210 (dip and repeated plug-in), TC-203
- **Status:** Open
