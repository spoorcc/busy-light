# Stakeholder Needs

- **Status:** Draft
- **Version:** 0.3
- **Owner:** Ben Spoor
- **Source:** Product owner statements, 2026-11-03. Wording below is close to the owner's words; interpretation is listed under *Open points* and is **not** yet agreed.

Product concept: a Wi-Fi connected ring of individually controllable RGB LEDs that shows levels or status from external data
(for example a busy light, a Jenkins agent or build indicator, or other status sources). Custom PCB, orderable from a prototype shop.

### NEED-001 Provision over the device's own access point
- **Statement:** The user can configure the device by connecting to the device in access point (AP) mode.
- **Open points:** Is AP mode the first-boot setup only, or also a permanent fallback? Does the AP need a password? How does the user enter AP mode later (button)?
- **Status:** Draft

### NEED-002 Simple web interface for configuration
- **Statement:** The configuration is done in a simple web interface served by the device.
- **Open points:** Which settings exactly (Wi-Fi, data sources, mapping of data to LEDs, brightness, name)? Is access protected? Mobile first?
- **Status:** Draft

### NEED-003 Ring of individually controllable RGB LEDs
- **Statement:** The device has an LED ring. Each LED is RGB and can be controlled individually.
- **Clarified (owner, 2026-11-03):** 16 LEDs.
- **Open points:** Brightness target (visible across a room or only on a desk?), colour accuracy needs, animation needs.
- **Status:** Draft

### NEED-004 Show levels and status from external data
- **Clarified (owner, 2026-11-03):** Level mode is in the first release (SYS-032).
- **Statement:** The device indicates levels or status that follow external data. Examples: busy light, Jenkins agent or build indicator, "all kinds of other things".
- **Open points:** What are the first two or three concrete use cases that must work at launch? What does "level" look like (fill the ring like a gauge)? What does "status" look like (colour, blink, animation)?
- **Status:** Draft

### NEED-005 Receive pushed events (first source: Jenkins)
- **Clarified (owner, 2026-11-03):** The network can be shared with other users. The 5 min stale timeout for push (SYS-033) is not in the first release (owner, 2026-11-03).
- **Statement:** The device can receive events and act on them. First release: Jenkins pushes the build status to the device.
- **Open points:** Who is allowed to send events (token)? Is the device always on the same network as Jenkins? Transport protection (plain HTTP or HTTPS)?
- **Status:** Draft

### NEED-006 Poll a REST endpoint (first source: Jenkins status API)
- **Statement:** The device can fetch status from a REST API and act on the result. First release: the Jenkins status REST API. GraphQL and other styles come later.
- **Open points:** HTTPS and certificates, authentication (user and API token), poll interval range, how the user selects the value from the response.
- **Status:** Draft

### NEED-007 Extensible source support (not concurrent, not all in the first release)
- **Statement:** More protocols are wanted over time. They do not have to run at the same time. The first release only needs the Jenkins push and the REST poll.
- **Consequence:** The software structure must allow adding a source later without redesign. Which sources come later is a future decision.
- **Status:** Draft

### NEED-008 One button controls the device
- **Statement:** A single button controls the device.
- **Open points:** Which functions (power/mode/brightness, enter AP mode, factory reset, acknowledge)? Short, long and double press assignments?
- **Status:** Draft

### NEED-009 Low unit cost
- **Statement:** The cost of one PCB including components is at most EUR 10 to 20.
- **Clarified (owner, 2026-11-03):** The EUR 10-20 is per assembled PCB including components. The housing is 3D printed and is not part of this figure.
- **Clarified (owner, 2026-11-03):** The first order is 10 units.
- **Clarified (owner, 2026-11-03):** Later production is planned at about 1000 units per year. Cost must then be judged at that volume (see plan 02, section 4.12); the first order of 10 is a prototype run.
- **Update (owner, 2026-11-03):** Platform ESP32-C3 chosen (plan 02, round 6). The EUR 20 limit stays; the nRF platform is a later option for the battery version.
- **Open points:** Do shipping, import tax and set-up fees count in the per-board figure (this document assumes yes: total cost of the order divided by 10)? Is EUR 10 the target and EUR 20 the limit? Does the USB power supply count (assumed no)?
- **Status:** Draft

### NEED-010 Orderable from a prototype PCB shop
- **Statement:** The PCB (with assembly) can be ordered later from a prototype shop.
- **Clarified (owner, 2026-11-03):** Assembly on one side of the PCB by the shop; no hand soldering.
- **Open points:** Which shop and which assembly service (parts library limits, minimum quantity)?
- **Status:** Draft

### NEED-013 3D printed housing
- **Statement:** The housing is 3D printed.
- **Source:** Product owner, 2026-11-03.
- **Open points:** Printer technology (FDM or resin) and material? Who prints it (the user at home, a print service)? How does the ring light pass through the housing (diffuser, translucent material)? Mounting (desk stand, wall, magnet)?
- **Status:** Draft

### NEED-014 Size halfway between a table-tennis ball and a tennis ball
- **Statement:** The device is between the size of a table-tennis ball and a tennis ball. The sweet spot is exactly in between, the average of the two.
- **Source:** Product owner, 2026-11-03 (replaces the earlier wording "smaller than an Amazon Echo and larger than a table-tennis ball").
- **Calculation:** A table-tennis ball is 40 mm in diameter. A tennis ball is about 67 mm (ITF: 65.4 to 68.6 mm). The average is about 53 mm.
- **Open points:** Is 53 mm the diameter of the housing, or the largest dimension? Shape (a sphere, a puck, a ring on a stand)? Is a flat base or stand allowed to be larger?
- **Status:** Draft

### NEED-015 Battery power later (future, not in the first release)
- **Statement:** The first release is powered from USB-C 5 V only. A later redesign may add battery power.
- **Consequence:** The first design must not make battery operation hard later (choice of MCU, power path, housing volume). No battery requirement exists for the first release.
- **Status:** Draft

### NEED-016 Usable by non-technical people later
- **Statement:** The first users are makers. Later users are less technical.
- **Consequence:** The first release is aimed at makers, but setup, the web interface, the ring feedback and the manual must be designed so that they can be simplified for non-technical users without a redesign.
- **Status:** Draft

### NEED-017 Update the firmware over the air
- **Statement:** The device can be updated over the network (OTA update). Required.
- **Source:** Product owner, 2026-11-03.
- **Open points:** Update by upload in the web interface, by download from a server, or both? Where do release images come from (open-source project releases)? How long does the project promise to supply updates?
- **Status:** Draft

### NEED-018 Add certificates
- **Statement:** The user can add certificates to the device.
- **Source:** Product owner, 2026-11-03.
- **Clarified (owner, 2026-11-03):** The user uploads the required certificates through the configuration web site while the device is in access point mode during provisioning (and, as assumed here, later as well).
- **Clarified (owner, 2026-11-03):** The user can also load the device's own certificate and key (SYS-035). Browser warnings at first use are accepted.
- **Open points:** Which certificates: trust anchors (CA certificates) so that the device accepts the user's HTTPS servers, such as a Jenkins server with a company certificate? Or also a certificate and key for the device's own HTTPS server? This document assumes the first; the second is open.
- **Status:** Draft

### NEED-019 Unique password per unit
- **Statement:** Each unit has its own password (for the setup access point).
- **Source:** Product owner, 2026-11-03.
- **Open points:** How does the user learn the password (label, card)? Who creates it (production step, first start)? What about people who build their own board from the open-source files?
- **Status:** Draft

### NEED-011 Professionally engineered, testable and auditable
- **Statement:** The product is engineered like a product from a regulated company: specification before implementation, recorded design decisions, strong testability and auditability.
- **Source:** Product owner, 2026-11-03 (process instruction).
- **Status:** Draft

### NEED-012 Open source
- **Statement:** The code is published as open source (Apache-2.0). The hardware, mechanical design and documentation are published source-available for non-commercial use (CC BY-NC-SA 4.0).
- **Clarified (owner, 2026-11-04):** Code Apache-2.0; documentation, hardware and mechanics CC BY-NC-SA 4.0. Hardware and mechanics are therefore not open source hardware (ADR-0013).
- **Open points:** Contributor licence agreement for hardware, mechanical and documentation contributions; CRA role (`docs/regulatory/applicability.md`).
- **Status:** Draft

## Project constraints (not product needs)
- Open-source project: Zephyr software, KiCad hardware, FreeCAD enclosure.
- Developed to the process in `docs/process/README.md`. Regulatory work comes later, but the design must not block it (`docs/regulatory/applicability.md`).
