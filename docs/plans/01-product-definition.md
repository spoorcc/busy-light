# 01 -- Product definition (brainstorm record)

- **Status:** Draft (Brainstorm phase of EGM -- no design decisions yet)
- **Date:** 2026-11-03  **Owner:** Ben Spoor
- **Area:** project
- **Requirements addressed:** NEED-001 to NEED-010

## 1. What we heard
See `docs/requirements/needs.md`. In one sentence: a Wi-Fi RGB LED ring, configured through its own access point and a small web
interface, that shows status or levels from pushed events or polled endpoints, controlled by one button, on a custom PCB of EUR 10-20.

## 1a. Scope decision (owner, 2026-11-03)
Protocols do not need to run concurrently. **First release: Jenkins status pushed to the device (HTTP) and fetched by the device from
a REST API.** GraphQL and other sources come later. The software must be structured so that adding a source needs no redesign (NEED-007).
Draft system requirements: `docs/requirements/system.md` (with explicit assumptions A1-A8).

## 2. Critical observations (to resolve before system requirements)
1. **Breadth of protocols was the largest risk; the first release scope now removes most of it.** Each protocol costs flash, RAM, code review, tests and attack surface. HTTPS/TLS alone needs tens of kB of RAM per connection plus a certificate strategy and correct time (NTP). A fixed, small core set with a generic extraction/mapping layer is more realistic than breadth.
2. **The hard part is not the protocols but the mapping**: how does a JSON/GraphQL response or an event become LED states? The mapping model (rules, thresholds, templates, small expression language) decides the product's usability, its test effort and its security. It needs its own ADR.
3. **Receiving events needs an inbound listener on the device.** That requires authentication and rate limiting from day one. A device on a home LAN is not reachable from the Internet without a relay or broker; MQTT (device connects out) avoids that.
4. **Cost target at 10 units (confirmed order size).** At 10 boards, the shop's fixed fees (assembly set-up, stencil, a charge for each part type outside the shop's standard library, shipping, import tax) can be as large as the parts themselves. A rough estimate from memory, not a quote, puts a simple Wi-Fi board near the EUR 10-20 range, but with little margin. Consequences for the design: use as few different part types as possible, prefer the shop's standard (basic) library parts, avoid exotic parts, and keep the board small and simple (2 layers). Get a real quote for a draft BOM early (a cost gate in the architecture phase). Cost per board will fall at larger orders.
5. **Power and light:** a full-white ring draws roughly 50-60 mA per LED at 5 V, so 16-24 LEDs reach 1-1.5 A. USB-C source limits, brownout and heat need a brightness limit or current budget as a system requirement.
6. **Size of about 53 mm is tight (NEED-014).** After a printed wall of 2-3 mm, the PCB is about 45-48 mm across. Sixteen LEDs on a ring of about 38-42 mm leave a pitch of about 7.5-8.5 mm and a free centre of about 30 mm, which is only just larger than a typical Wi-Fi module (about 13 x 17 mm). The USB-C connector (about 9 mm wide), the button and the power parts must fit too. A module with an on-board antenna needs free space (no copper, no LEDs, no metal) around the antenna; inside a ring of LEDs this is hard. Options for the architecture phase: place the module with its antenna at the edge in a gap of the LED ring, use a module with an external antenna connector and a small antenna, use two stacked PCBs (costly at 10 units and needs a connector), or use a bare chip with a chip antenna (RF design risk). This is a first-order design driver and needs an ADR. A small LED package (2020 or 3535) is needed; a 5050 LED is too large.
7. **Single button, no display:** every state (AP mode, connecting, error, update, factory reset) must be shown with the ring itself. That is a user-experience requirement and a testability asset.
8. **Zephyr on a Wi-Fi SoC:** Zephyr supports several Wi-Fi capable parts, but maturity of soft-AP, captive portal, TLS and OTA differs per SoC. Choose the MCU by an ADR with evidence (not by habit); the choice is costly to reverse.
9. **Open-source distribution:** if people build the board from the published files, support and security-update promises must be written down early.

## 3. Open questions for the product owner
Answered: question 1 (Jenkins push and REST poll) and the protocol core set (reduced). Still open, with the default used in `system.md`:
1. **First use cases:** which two or three must work at launch (busy light, Jenkins job status, other)? Who sends the data (a script on a PC, Jenkins itself, Home Assistant)?
2. **Protocol must-haves:** is "HTTP webhook in + HTTP/HTTPS GET/POST polling (REST and GraphQL) + MQTT" the right core set? What is nice-to-have?
3. **Cost scope:** EUR 10-20 per assembled PCB (confirmed); first order 10 units (confirmed); housing excluded (confirmed). Does the figure include shipping and tax (assumed yes)?
4. **Power:** USB-C 5 V only? Battery? Mains?
5. **Ring:** 16 LEDs (confirmed). Size between a table-tennis ball and an Amazon Echo (which model?). Desk-top or visible across a room (brightness)?
6. **Security posture:** is the device LAN-only? Is a password-protected web UI acceptable and expected?
7. **Updates:** field firmware updates required (via web UI or from a server)?
8. **User:** developers/makers or non-technical users? This sets the web UI scope and the documentation level.
9. **PCB shop and assembly:** a preferred shop, one-sided assembly, hand-soldered parts allowed?
10. **Name, license and distribution model** (kit, assembled, files only).

## 3a. Decisions received (owner, 2026-11-03)
OTA update is required (NEED-017). The user can add certificates (NEED-018). Each unit has its own password (NEED-019).

Consequences to examine in the architecture phase:
- **Flash:** two firmware slots (for rollback), TLS, the web interface files and a settings area must fit with 25 % margin (SYS-026). This favours at least 4 MB flash and sets a floor for the module choice.
- **Per-unit secret:** with 10 units flashed by the owner, a production step can generate and label each password. A builder of the open-source design must be able to do the same; this needs a documented, tested procedure.
- **Trust and time:** certificates need a clock; there is none without the network (SYS-031).
- **Signing keys:** the project needs a key management plan (who holds the update signing key, how it is protected, what happens if it is lost). This is a risk to record.
- **Certificate upload during provisioning (owner):** the AP-mode web site must accept certificate files before the device has network, time or Internet access. The device can check the file format at upload but not the validity dates (no time yet, SYS-031). The upload path is a security-relevant function: only the unit-password-protected AP may use it.
- **Still open:** does "add certificates" include the device's own HTTPS certificate? Is the push endpoint HTTP with a token or HTTPS?

## 4. Next steps (after answers)
1. Draft system requirements (`SYS-`) with the non-functional checklist, and update `docs/regulatory/applicability.md`.
2. ADRs: MCU and radio module; LED type and drive; data-to-LED mapping model; web UI architecture and provisioning; update mechanism.
3. Design doc for EGM review before any implementation.
