# Architecture blocks

- **Status:** Draft (proposed in `docs/plans/02-system-design.md` section 4; not approved by the owner)

The numbers 006 to 009 are skipped on purpose: they are reserved for hardware and mechanical blocks not yet identified (for example test fixture, label). Block diagram: [arch-system-blocks.puml](../diagrams/plantuml/arch-system-blocks.puml). Interfaces, budgets and failure behaviour are added when the requirements are approved.

### ARCH-001 Power and USB-C input

- **Domain:** HW
- **Related:** SYS-020, ADR-0004
- **Description:** USB-C 5 V input, CC resistors, ESD and inrush protection, reverse-current protection; power budget in `hw/sim/` (spike 7.5).

### ARCH-002 Wi-Fi SoC module

- **Domain:** HW
- **Related:** SYS-022, SYS-023, ADR-0002, ADR-0003
- **Description:** ESP32-C3 module (4 MB flash), antenna and keep-out per ADR-0003; USB and reset access.

### ARCH-003 LED ring and LED data drive

- **Domain:** HW
- **Related:** SYS-001, SYS-028, ADR-0004
- **Description:** 16 single-wire RGB LEDs on a ring of at least 38 mm; 5 V data buffer, series resistor and pull-down (removable after spike 7.3).

### ARCH-004 Button and test points

- **Domain:** HW
- **Related:** SYS-017, SYS-023, ADR-0006
- **Description:** One button; test points for power, UART/USB and LED data.

### ARCH-005 Housing and light diffuser

- **Domain:** MECH
- **Related:** SYS-028, ADR-0003
- **Description:** About 53 mm housing, diffuser for the ring, antenna clearance, thermal margin in a printed shell.

### ARCH-010 Bootloader and update (MCUboot)

- **Domain:** SW
- **Related:** SYS-029, ADR-0007
- **Description:** Two slots, signed images, test-then-confirm, secrets in separate partitions.

### ARCH-011 Core runtime and event bus

- **Domain:** SW
- **Related:** SYS-025, SYS-027, ADR-0002
- **Description:** Pure logic in `core/` (no OS calls), event bus, watchdog supervision; runs on the PC.

### ARCH-012 Source adapters (push, poll)

- **Domain:** SW
- **Related:** SYS-003, SYS-004, SYS-005, SYS-006, SYS-007, SYS-009, SYS-010, SYS-033, SYS-040, ADR-0005, ADR-0008
- **Description:** Push endpoint and REST poller; request limits; source precedence; stale handling.

### ARCH-013 Mapping and status model

- **Domain:** SW
- **Related:** SYS-002, SYS-008, SYS-032, ADR-0005
- **Description:** Restricted JSON Pointer extractor, state table, linear level scale; Jenkins preset.

### ARCH-014 Display engine and current limiter

- **Domain:** SW
- **Related:** SYS-001, SYS-018, SYS-020, SYS-032, ADR-0004
- **Description:** Patterns, gamma, animation and the current limiter as last step before the LED driver.

### ARCH-015 Network manager (station, AP, SNTP)

- **Domain:** SW
- **Related:** SYS-012, SYS-031, SYS-038, ADR-0006
- **Description:** Station, provisioning access point with timeout, time sanity rule.

### ARCH-016 Web server, config API, static page

- **Domain:** SW
- **Related:** SYS-014, SYS-015, SYS-016, SYS-039, ADR-0008
- **Description:** HTTPS on the LAN, HTTP only in the access point; login; configuration and certificate upload; update upload.

### ARCH-017 Security services (credentials, token, certificate store, TLS)

- **Domain:** SW
- **Related:** SYS-004, SYS-013, SYS-016, SYS-030, SYS-034, SYS-035, ADR-0006, ADR-0008
- **Description:** Unit passphrase store, device key and certificate record, trust store, TLS configuration.

### ARCH-018 Settings store

- **Domain:** SW
- **Related:** SYS-019, SYS-041, ADR-0007
- **Description:** Persistent settings with checksum and power-cut safety; factory reset scope.

### ARCH-019 Diagnostics (log, shell, self-test, identity)

- **Domain:** SW
- **Related:** SYS-023, SYS-024, SYS-042, ADR-0007
- **Description:** Log, shell, self-test, version and build identity, stable device name.
