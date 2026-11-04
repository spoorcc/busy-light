# System Requirements

- **Status:** Draft
- **Version:** 0.1
- **Owner:** Ben Spoor
- **Scope:** first release: Jenkins status pushed to the device and fetched from a REST API (decision of the owner, 2026-11-03).

Values in [square brackets] depend on the assumptions below and are not yet agreed. Nothing here is Approved.

Entries follow `docs/templates/requirement.md`. The non-functional checklist (`docs/process/README.md` section 5) is not complete yet: open items are security update path, regulatory scope, environmental limits and EMC.

## Working assumptions (owner has not confirmed; change them here first)
| ID | Assumption | Affects |
|----|------------|---------|
| A1 | Ring has 16 individually addressable RGB LEDs (confirmed) | SYS-001, SYS-020 |
| A2 | Powered from USB-C 5 V only (confirmed); battery may come in a later redesign (NEED-015) and must not be made hard; no mains inside | SYS-018 |
| A3 | Device is used on a local network (LAN) only; no cloud service. The LAN may be shared with other, untrusted users (owner, 2026-11-03) | SYS-003, SYS-004, SYS-034 |
| A4 | Cost target: EUR 10-20 per assembled PCB with components; housing is 3D printed and excluded; first order is 10 units (all confirmed). Later volume: about 1000 units per year (owner, 2026-11-03), which may need a second cost requirement at that volume. Assumed, not confirmed: the figure is the total landed cost of the order (parts, PCB, assembly, set-up fees, shipping, import tax) divided by 10; VAT is included (conservative; owner's working default 2026-11-03) | SYS-021 |
| A5 | First users are makers; less technical users later (confirmed, NEED-016) | SYS-012, SYS-013 |
| A6 | Ring is read from desk distance (about 1 to 3 m). Housing size: about 53 mm, halfway between a table-tennis ball (40 mm) and a tennis ball (about 67 mm) (NEED-014) | SYS-001 |
| A7 | The device shows one status at a time (one logical channel) | SYS-002, SYS-008 |
| A8 | Button functions in SYS-017 are proposals; short press on/off confirmed by owner 2026-11-03 | SYS-017 |

## Not yet specified (waiting for owner decisions)
Open items are listed in `docs/plans/02-system-design.md` section 10 and in `docs/reviews/RV-001-system-design-goldfish.md`. Answered since the first draft: support period (SYS-045), transport protection (SYS-034, ADR-0008), device certificate (SYS-035), unit password (SYS-013), regulatory scope (`docs/regulatory/applicability.md`).

### SYS-001 Status indicator ring

- **Statement:** The device shall show its status on a ring of [16] RGB LEDs, each LED controlled individually for colour and brightness.
- **Rationale:** The ring is the only display; individual control allows levels and animations. The brightness figure depends on the current that the source allows (SYS-020): at the default 500 mA the paper power budget leaves 5 to 58 % of full white depending on LED type, on a source that advertises 1.5 A the limiter does not dim (`spike-7-5-power-budget-paper.md`, section 8). The figure is therefore to be agreed at two operating points: the default source and a source advertising 1.5 A.
- **Parent:** NEED-003
- **Acceptance criteria:** Each LED can be set to any of 256 levels per colour channel, independently of the others (before the current limit of SYS-020 scales the frame), and with all LEDs at the status brightness the ring gives a luminous intensity of at least [to be set from the bench measurement in spike 7.5; working value 100 mcd per LED] measured at 0.5 m, and a person with normal colour vision can name the state colour at 2 m in 300 lux room light.
- **Verification method:** Test
- **Verified by:** TC-001
- **Category:** Functional
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-002 Status model

- **Statement:** The device shall support the states unknown, building, success, unstable, failure and aborted, and show each with a configurable colour and animation (steady, blink, pulse or rotate).
- **Rationale:** Jenkins results map to these states; a common model keeps later sources simple.
- **Parent:** NEED-004
- **Acceptance criteria:** Each state has a default appearance and the user can change colour and animation for each state; the state is clearly distinguishable from every other state.
- **Verification method:** Test
- **Verified by:** TC-002
- **Category:** Functional
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-003 Push input

- **Statement:** The device shall accept a status event as an HTTP POST request at a documented endpoint on the local network and update the ring within [1] s of receiving a valid event.
- **Rationale:** Jenkins pushes build status when a build starts and ends.
- **Parent:** NEED-005
- **Acceptance criteria:** 95 % of valid events update the ring within 1 s of receipt (measured at the ring).
- **Verification method:** Test
- **Verified by:** TC-003
- **Category:** Performance
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-004 Push authentication

- **Statement:** The device shall reject push events that do not carry the valid access token, shall answer them with an error status, and shall not change the ring because of them.
- **Rationale:** Anyone on the network could otherwise set a false status.
- **Parent:** NEED-005
- **Acceptance criteria:** 100 % of requests without a valid token are rejected with HTTP 401 and cause no state change. The token has at least 128 bits of randomness and can be replaced by the user.
- **Verification method:** Test
- **Verified by:** TC-004
- **Category:** Security
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-005 Push robustness

- **Statement:** The device shall reject malformed, oversized (more than [1] KiB) or rate-exceeding push requests without crashing or changing state.
- **Rationale:** An open listener must not be a way to crash the device.
- **Parent:** NEED-005
- **Acceptance criteria:** A fuzz test of at least [10 000] requests causes no reset, no hang and no state change.
- **Verification method:** Test
- **Verified by:** TC-005
- **Category:** Robustness
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-006 REST polling

- **Statement:** The device shall poll a configured REST endpoint at an interval that the user sets between [5] s and [300] s (default [30] s), and extract a status value from the JSON response with a configured path.
- **Rationale:** The device fetches Jenkins status itself when push is not possible.
- **Parent:** NEED-006
- **Acceptance criteria:** The device polls at the set interval (tolerance 10 %) and extracts the configured field from a JSON response.
- **Verification method:** Test
- **Verified by:** TC-006
- **Category:** Functional
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-007 Jenkins preset

- **Statement:** The device shall provide a preset for the Jenkins job JSON API (fields building and result) with HTTP basic authentication (user name and API token), so that the user only enters the base address, job and credentials. If the address uses plain HTTP, the interface shows a warning that the credentials cross the network in clear text.
- **Rationale:** Jenkins is the first use case.
- **Parent:** NEED-006
- **Acceptance criteria:** With the preset, a Jenkins build that is running, successful, unstable, failed or aborted is shown as the matching state within one poll interval.
- **Verification method:** Test
- **Verified by:** TC-007
- **Category:** Functional
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-008 Value mapping

- **Statement:** The device shall map extracted values to states through a table that the user can edit.
- **Rationale:** Other REST APIs use other words for status.
- **Parent:** NEED-007
- **Acceptance criteria:** The user can add, change and remove table rows; an unmapped value gives the state unknown.
- **Verification method:** Test
- **Verified by:** TC-008
- **Category:** Functional
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-009 Source precedence

- **Statement:** When both push and poll are configured, the device shall use the most recent valid update from either source.
- **Rationale:** The owner wants both sources.
- **Parent:** NEED-005
- **Acceptance criteria:** With a poll result and a push event in either order, the ring shows the state of the one whose data was produced later (event time, or request start time for a poll), not the one that arrived later.
- **Verification method:** Test
- **Verified by:** TC-009
- **Category:** Functional
- **Regulatory:** TBD
- **Priority:** Should
- **Status:** Draft

### SYS-010 Stale and failed data

- **Statement:** If [3] successive polls fail, the device shall show a connection-error indication that differs from every status state.
- **Rationale:** A stale green ring would mislead the user.
- **Parent:** NEED-004
- **Acceptance criteria:** After 3 failed polls the ring shows the error indication within one poll interval, and in any case within [15] min, and returns to the status after the next successful poll. A failed poll is a timeout, a connection error, an HTTP status other than 2xx, an answer that cannot be parsed, or a value the mapping cannot use.
- **Verification method:** Test
- **Verified by:** TC-010
- **Category:** Safety
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-011 Safe start state

- **Statement:** After every start or reset, the device shall show the state unknown until it has a valid update.
- **Rationale:** A stored old status would be wrong data.
- **Parent:** NEED-004
- **Acceptance criteria:** After a power cycle or watchdog reset, the ring shows unknown until the first valid update.
- **Verification method:** Test
- **Verified by:** TC-011
- **Category:** Safety
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-012 Provisioning access point

- **Statement:** If the device has no Wi-Fi credentials, or the user requests it, the device shall start its own Wi-Fi access point with a name that contains a unique device identifier and serve the configuration web interface.
- **Rationale:** The user needs a way to configure the device without other software.
- **Parent:** NEED-001
- **Acceptance criteria:** A phone can join the AP, open the interface and store Wi-Fi credentials; the device then joins the network. The AP accepts one client at a time and stops after [10] min without completed setup; a new long press starts it again. The interface never shows stored credentials or keys.
- **Verification method:** Test
- **Verified by:** TC-012
- **Category:** Functional
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-013 Provisioning security
- **Statement:** The access point shall be protected by encryption with a password that is unique to each unit, and the password shall not be derivable from information that the device broadcasts (such as its name or MAC address).
- **Rationale:** The user types the home Wi-Fi password over this link (NEED-019). A shared or guessable password lets anyone nearby read it.
- **Parent:** NEED-001
- **Acceptance criteria:** In a sample of 10 units, no two units have the same password. A passive radio capture of a provisioning session does not reveal the Wi-Fi credentials. The password cannot be calculated from the SSID or MAC address. (The mechanism is a design decision, see ADR to be written.)
- **Verification method:** Test
- **Verified by:** TC-013
- **Category:** Security
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-014 Web interface

- **Statement:** The device shall serve the configuration web interface from its own storage, without needing Internet access, and the interface shall be usable on a phone screen of 360 px width.
- **Rationale:** The device may be on a network without Internet.
- **Parent:** NEED-002
- **Acceptance criteria:** The interface loads with the Internet blocked and all functions of SYS-015 work on a 360 px viewport.
- **Verification method:** Test
- **Verified by:** TC-014
- **Category:** Usability
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-015 Configurable settings

- **Statement:** The web interface shall let the user set: Wi-Fi network, device name, brightness, access token, poll source and interval, value mapping and the appearance of each state; and shall show the current state and the time of the last valid update.
- **Rationale:** These are the functions the owner described.
- **Parent:** NEED-002
- **Acceptance criteria:** Each listed setting can be changed through the interface and takes effect without a manual restart.
- **Verification method:** Test
- **Verified by:** TC-015
- **Category:** Functional
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-016 Interface access control

- **Statement:** Outside the provisioning access point, the device shall require a password for the web interface, set by the user during setup.
- **Rationale:** Anyone on the LAN could otherwise change the device.
- **Parent:** NEED-002
- **Acceptance criteria:** Requests without valid credentials receive HTTP 401; there is no default password.
- **Verification method:** Test
- **Verified by:** TC-016
- **Category:** Security
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-017 Button

- **Statement:** The device shall have one button. A short press shall [switch the ring on or off]; a press of [3] s shall start the configuration access point; a press of [10] s shall reset to factory settings after a clear ring confirmation.
- **Rationale:** One button controls the device (functions proposed in A8).
- **Parent:** NEED-008
- **Acceptance criteria:** Each press length gives its function; a press shorter than the long threshold never starts AP or reset; reset needs the confirmation pattern.
- **Verification method:** Test
- **Verified by:** TC-017
- **Category:** Functional
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-018 Device status patterns

- **Statement:** The ring shall show distinct, documented patterns for: starting, access-point mode, connecting, connection lost, update in progress and reset confirmation, and these shall differ from all job states.
- **Rationale:** The ring is the only display and must be understood without colour alone.
- **Parent:** NEED-004
- **Acceptance criteria:** Each pattern is documented, visually distinct in a blind comparison by 3 observers, and distinguishable by pattern when colour is ignored.
- **Verification method:** Test
- **Verified by:** TC-018
- **Category:** Usability
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-019 Configuration persistence

- **Statement:** The device shall keep its settings across power loss, and a power loss during a settings write shall not corrupt them.
- **Rationale:** Users do not want to configure again after a power cut.
- **Parent:** NEED-002
- **Acceptance criteria:** After 1000 random power cuts during writes the device starts with a valid configuration (the old or the new one) every time.
- **Verification method:** Test
- **Verified by:** TC-019
- **Category:** Reliability
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-020 Power

- **Statement:** The device shall operate from a USB-C 5 V supply. It shall limit its total current to [500] mA by limiting LED brightness, and shall allow up to the current that the source advertises on the USB-C CC lines (at most [1500] mA) when the source advertises more than the default.
- **Rationale:** A standard USB port must be able to power it. Owner decision of 2026-11-04: allow a higher current if the source advertises it. At 500 mA the Wi-Fi transmit peak leaves only 46 to 148 mA for the LEDs (`docs/verification/reports/spike-7-5-power-budget-paper.md`). The default (500 mA) applies whenever no higher current is advertised or the advertised value cannot be read.
- **Parent:** NEED-003
- **Acceptance criteria:** With all LEDs set to full white the supply current stays at or below the limit that applies. On a source that advertises the default current (including a USB-C to USB-A cable), the limit is [500] mA. On a source that advertises 1.5 A, the limit is the advertised value minus a margin of [10] %. If the advertised value cannot be read, the limit is [500] mA. The limit is set within [1] s of connection. The device does not reset in any of these cases.
- **Verification method:** Test
- **Verified by:** TC-020
- **Category:** Safety
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-021 Unit cost
- **Statement:** The landed cost of one assembled PCB including all components (parts, PCB, assembly, set-up fees, shipping and import tax; not the housing) shall not exceed EUR [20] for an order of 10 units, with EUR [10] to [15] as the target.
- **Rationale:** This is the owner's cost target (A4) for the first order. Platform ESP32-C3 chosen by the owner on 2026-11-03 (plan 02, round 6); estimated EUR 11-19 per board, not yet quoted. At 10 units, fixed shop fees are a large part of the cost, so they are counted.
- **Parent:** NEED-009
- **Acceptance criteria:** A real quote from the chosen prototype shop, with BOM and shipping to the delivery address, gives a total order cost divided by 10 that is at or below the limit.
- **Verification method:** Analysis
- **Verified by:** TC-021
- **Category:** Cost
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-022 Orderable from a prototype shop

- **Statement:** The PCB design shall be orderable with assembly from a prototype shop using only parts that the shop offers, with all parts surface-mounted on one side, so that no hand soldering is needed (this includes the USB-C connector, the button and the Wi-Fi module).
- **Rationale:** The owner will order from a prototype shop.
- **Parent:** NEED-010
- **Acceptance criteria:** The shop's design check accepts the files, every BOM line is available in the shop's parts list, and the assembled board needs no manual soldering before the first power-up.
- **Verification method:** Inspection
- **Verified by:** TC-022
- **Category:** Manufacturability
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-023 Programming and test access

- **Statement:** The device shall be programmable and testable through the USB-C connector, and shall have a production self-test mode that checks the LEDs, the button and the Wi-Fi radio.
- **Rationale:** Low-cost production needs fast, fixture-light testing.
- **Parent:** NEED-010
- **Acceptance criteria:** A new board can be programmed and self-tested using only the USB-C cable; the self-test result is reported to the host; the per-unit password (SYS-013) can be created and recorded in the same production step.
- **Verification method:** Demonstration
- **Verified by:** TC-023
- **Category:** Testability
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-024 Version and build identity

- **Statement:** The device shall report its firmware version, build identifier and hardware revision in the web interface and in its logs, and builds shall be reproducible from the tagged source.
- **Rationale:** Auditors and users must know exactly what runs on the device.
- **Parent:** NEED-011
- **Acceptance criteria:** Two builds of the same tag give identical binaries; the reported identity matches the tag.
- **Verification method:** Test
- **Verified by:** TC-024
- **Category:** Auditability
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-025 Host-testable logic

- **Statement:** The device logic (status model, mapping, parsing, state machines) shall run in automated tests on a host computer without the target hardware.
- **Rationale:** Fast, repeatable evidence without hardware.
- **Parent:** NEED-011
- **Acceptance criteria:** The test suite runs in CI on a host build and covers every requirement that has a logic part.
- **Verification method:** Test
- **Verified by:** TC-025
- **Category:** Testability
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-026 Resource margin

- **Statement:** The firmware shall leave at least [25] % free in each of: the size of one image slot (image size at most [75] % of the slot), the settings and certificate area, and the RAM measured as the lowest free heap during the stress test.
- **Rationale:** Margin for updates and security fixes over the support period. The earlier text did not say what the 25 % refers to (RV-001 item 2); a build total hides the real limit, which is the slot.
- **Parent:** NEED-011
- **Acceptance criteria:** The release build report shows the image size against the slot size. The stress test (two TLS sessions, an update upload, a poll and LED output at the same time) records the lowest free heap. All three values are at or above the limit. If two slots plus the margin do not fit in the flash, ADR-0007 and spike 7.1 decide the remedy before this value is fixed.
- **Verification method:** Analysis
- **Verified by:** TC-026
- **Category:** Maintainability
- **Regulatory:** TBD
- **Priority:** Should
- **Status:** Draft

### SYS-027 Fault recovery

- **Statement:** If the firmware hangs, the device shall restart by itself within [10] s.
- **Rationale:** An unattended indicator must recover.
- **Parent:** NEED-011
- **Acceptance criteria:** A forced hang in a test build causes a restart within 10 s, and the device then shows the state unknown (SYS-011).
- **Verification method:** Test
- **Verified by:** TC-027
- **Category:** Reliability
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-028 Size
- **Statement:** The largest outer dimension of the finished device shall be [53] mm, with a tolerance of [plus or minus 5] mm.
- **Rationale:** The owner wants the size halfway between a table-tennis ball (40 mm) and a tennis ball (about 67 mm) (NEED-014).
- **Parent:** NEED-014
- **Acceptance criteria:** A measurement of the printed housing with the PCB fitted gives a largest dimension from 48 mm to 58 mm. The 16 LEDs are evenly spaced on a ring of at least [38] mm diameter inside the housing.
- **Verification method:** Inspection
- **Verified by:** TC-028
- **Category:** Mechanical
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-029 Firmware update over the network
- **Statement:** The device shall install a new firmware image received over the network through the web interface, shall accept the image only if its signature is valid, and shall keep the previous image so that it returns to it if the new image fails to start.
- **Rationale:** Required by the owner (NEED-017). Unsigned updates would let anyone replace the firmware.
- **Parent:** NEED-017
- **Acceptance criteria:** A correctly signed image installs and runs. An image with a wrong signature or a changed byte is rejected and the device keeps running. A power loss at any point of the update leaves a working device (tested at least [100] times). A new image that does not confirm itself is restarted and replaced by the previous one within [60] s of its first start, including the time of the image swap (to be measured on hardware). Settings are kept.
- **Verification method:** Test
- **Verified by:** TC-029
- **Category:** Security
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-030 User-supplied trust certificates
- **Statement:** The user shall be able to upload, list and remove CA certificates in the configuration web interface, including during provisioning in access point mode, and the device shall store them permanently and check the certificate of every HTTPS server that it connects to against the user-supplied certificates [and the built-in public CA certificates].
- **Rationale:** The Jenkins server may use a certificate from a private authority (NEED-018). The owner wants to upload the required certificates during provisioning. Adding a trust certificate changes whom the device trusts, so the upload is allowed only through the password-protected access point (SYS-013) or the password-protected interface (SYS-016).
- **Parent:** NEED-018
- **Acceptance criteria:** In access point mode, before the device has any network connection, a certificate file in PEM format can be uploaded; a file that is not a valid certificate, or that exceeds [8] KiB or [4] certificates in total, is rejected with a clear message. Uploaded certificates are still present after a restart and after a firmware update. With the company CA added, polling an HTTPS server with a certificate from that CA works. With a certificate from an unknown CA, the poll fails and the connection-error indication of SYS-010 shows. Removing the CA stops the poll from working. Certificate checks cannot be switched off silently (a switch, if allowed, needs a clear warning in the interface).
- **Verification method:** Test
- **Verified by:** TC-030
- **Category:** Security
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-031 Time for certificate checks
- **Statement:** The device shall get the current time from a network time server (configurable) and shall not accept an HTTPS server certificate while it has no valid time.
- **Rationale:** Certificate validity needs the time, and the device has no battery-backed clock.
- **Parent:** NEED-018
- **Acceptance criteria:** After a start without time, HTTPS polls wait for the time and then work. The device shows the connection-error indication if time is not available. The time server address can be set. A time earlier than the build date of the firmware is never accepted. The rule applies to connections that the device makes; the device's own certificate is not checked against the time (ADR-0008).
- **Verification method:** Test
- **Verified by:** TC-031
- **Category:** Security
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-032 Level display

- **Statement:** The device shall show a level between 0 % and 100 % as a filled arc of the ring, starting at the LED given by SYS-047 (the fixed LED when the unit is flat), with the last lit LED set in proportion to the remainder.
- **Rationale:** The owner wants levels as well as states in the first release (NEED-004, owner answer 2026-11-03).
- **Parent:** NEED-004
- **Acceptance criteria:** For input levels 0, 25, 50, 75 and 100 % the ring lights 0, 4, 8, 12 and 16 LEDs fully; for 50 % plus half of one LED step (53.1 %) the ninth LED is lit at about half brightness; a step of 1/16 of the range (6.25 %) is visible as a change. The user can set the colour and the value range (minimum and maximum) per source.
- **Verification method:** Test
- **Verified by:** TC-032
- **Category:** Functional
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-033 Push liveness

- **Statement:** When push is the only configured source, the device shall show the stale indication of SYS-010 if it has received no valid push event or heartbeat for [5] min.
- **Rationale:** Without it, a stopped Jenkins leaves the last state on the ring (gap G2, owner answer 2026-11-03: 5 min). Jenkins sends events only when a build starts or ends, so the sender must also send a heartbeat. The owner first deferred this; after the goldfish review (RV-001, finding 1) the owner's working default of 2026-11-03 is to follow the recommendation and make it a Must for push-only use. A factory reset changes the device key, which breaks the sender's pin and is made visible by this rule.
- **Parent:** NEED-005
- **Acceptance criteria:** After 5 min (tolerance 10 s) without a valid request the ring shows the stale indication; the next valid request restores the state. A documented heartbeat request keeps the state without changing it.
- **Verification method:** Test
- **Verified by:** TC-033
- **Category:** Safety
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-034 LAN transport protection

- **Statement:** Outside the provisioning access point, the device shall serve the web interface and accept push events only over TLS with a key pair that the device creates itself, and shall show the certificate fingerprint in the web interface.
- **Rationale:** The LAN may be shared with untrusted users (owner answer 2026-11-03), so the web password and the push token must not travel in clear text (gap G3). The mechanism is a design decision (ADR-0008).
- **Parent:** NEED-002
- **Acceptance criteria:** A plain HTTP request to the web interface or push endpoint on the LAN gets no data and no credentials are accepted; the fingerprint shown equals that of the certificate served; the private key cannot be read through the network, the web interface or the access point (a flash dump over USB is possible on prototypes without fuses and is a recorded limitation, ADR-0007); a new key pair is created after a factory reset.
- **Verification method:** Test
- **Verified by:** TC-034
- **Category:** Security
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-035 User-supplied device certificate

- **Statement:** The device shall let the user upload a certificate chain and private key for the device's own HTTPS server, shall use them instead of the self-created pair, and shall return to a self-created pair on request.
- **Rationale:** Owner answer 2026-11-03 (NEED-018, second reading): the user may load the device's own certificate. A company can then use its own CA for the web interface and the push endpoint. Browser warnings at first use are accepted (SYS-034).
- **Parent:** NEED-018
- **Acceptance criteria:** A PEM chain of at most [8] KiB and its matching key can be uploaded only through the password-protected interface or the provisioning access point; a key that does not match, or an invalid file, is rejected with a clear message; the key cannot be read back through the network, the web interface or the access point; the new certificate is served after the next connection and its fingerprint is shown; the data survives restart and firmware update; a factory reset removes it.
- **Verification method:** Test
- **Verified by:** TC-035
- **Category:** Security
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-036 Headroom for WPA2-Enterprise

- **Statement:** The hardware platform and the firmware design shall keep enough flash, RAM and certificate storage, and a Wi-Fi chip with supplicant support, so that WPA2-Enterprise (EAP-TLS and PEAP) can be added later without a hardware change.
- **Rationale:** Owner answer 2026-11-03: the design must not add hardware limits that rule out WPA2-Enterprise. Risk with ESP32-C3: the chip supports it in Espressif's own SDK (from memory), but in the Zephyr v4.5.0 source the ESP32 driver maps the EAP types to the Espressif blob (desk survey E0); build-only measurement (E12 follow-up): about +70 KB flash and +6 KB static RAM with `CONFIG_ESP32_WIFI_ENTERPRISE=y`; run-time heap use and function are not tested. Shared company networks often need it. The feature itself is not in the first release.
- **Parent:** NEED-001
- **Acceptance criteria:** The Wi-Fi chip documentation states support for WPA2-Enterprise in station mode. The release build report shows free flash and RAM of at least the size that a spike build with EAP-TLS enabled adds ([to be measured]), on top of the margin of SYS-026. The settings store has room for a client certificate and key.
- **Verification method:** Analysis
- **Verified by:** TC-036
- **Category:** Maintainability
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-037 Firmware runs in PC simulation

- **Statement:** The application firmware (everything above the hardware abstraction layer) shall build and run on a host computer in a simulator with simulated LED ring, button, network interface and persistent storage, and shall allow a test to cut power at a chosen moment.
- **Rationale:** Owner wish 2026-11-03: simulate as much as possible on the PC. It gives repeatable tests without hardware, including power-loss tests that are hard to do on a bench (SYS-019, SYS-029). Wi-Fi radio behaviour is not simulated; it is verified on hardware.
- **Parent:** NEED-011
- **Acceptance criteria:** One command builds and starts the simulation in CI; a test can press the button, send push events through the network interface, read the 16 LED values, and cut and restore power at [1000] random points; the ring output of a scripted test is compared with expected frames. The list of what the simulation does not cover (radio, RF, timing of real LED drive) is documented.
- **Verification method:** Test
- **Verified by:** TC-037
- **Category:** Testability
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-038 Wi-Fi range

- **Statement:** The device shall keep a Wi-Fi link to an access point at a distance of [10] m through one interior wall, with a packet loss of at most [5] % over 1 minute.
- **Rationale:** SYS-001 and ADR-0003 have no range figure. The antenna sits inside a ring of LEDs (ADR-0003); a figure is needed to decide between the antenna options. Working default of the owner, 2026-11-03.
- **Parent:** NEED-001
- **Acceptance criteria:** In a test room with a reference access point, the loss measured with the finished housing is at most 6 dB worse than a bare module of the same type (ADR-0003 criterion), and the packet loss stays at or below the limit at 10 m through one wall.
- **Verification method:** Test
- **Verified by:** TC-038
- **Category:** Performance
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-039 Web password rules

- **Statement:** The device shall store the web interface password only as a salted hash, shall require a password of at least [10] characters, and shall delay each further login attempt by [60] s after [5] failed attempts in a row.
- **Rationale:** SYS-016 requires a password but gives no rules. Brute force from a shared LAN is a stated threat (A3). The password is chosen during setup and is not the access point passphrase (ADR-0006).
- **Parent:** NEED-002
- **Acceptance criteria:** A password shorter than 10 characters is rejected at setup; the stored value does not contain the password; after 5 failures the next attempt within 60 s is refused even with the right password; the token and password comparison does not depend on how many characters match (timing check).
- **Verification method:** Test
- **Verified by:** TC-039
- **Category:** Security
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-040 Push request format

- **Statement:** The device shall accept a push event as an HTTPS POST with a JSON body of the form {"state": "<name>"} or {"level": <number>} or {"heartbeat": true}, shall reject any other body with HTTP 400, and shall reject a body larger than [1] KiB.
- **Rationale:** ADR-0005 item 7 chooses a neutral body so that the push path needs no mapping. The sender is under the user's control. The heartbeat supports SYS-033.
- **Parent:** NEED-005
- **Acceptance criteria:** Each valid form changes the ring or, for the heartbeat, only the liveness timer; an unknown state name, a non-numeric level, a body above the limit and a body with extra fields each get HTTP 400 and no change; the format is documented with an example script.
- **Verification method:** Test
- **Verified by:** TC-040
- **Category:** Functional
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-041 Factory reset scope

- **Statement:** A factory reset shall keep only the unit passphrase, shall remove all other user data (Wi-Fi credentials, settings, web password, user certificates and keys, user CA certificates), and shall create a new device key pair and a new push token.
- **Rationale:** SYS-017, 030, 034, 035 and ADR-0006 disagreed about what survives (RV-001, finding 18). The passphrase identifies the unit (ADR-0006). A new key and token mean that an old sender cannot keep access. Working default of the owner, 2026-11-03.
- **Parent:** NEED-008
- **Acceptance criteria:** After a reset, each of the items above is checked one by one: the passphrase is unchanged; every other item is absent or new. A power cut at any point during a reset leaves the device in either the old or the new state, never a mix, and a started reset is completed at the next start.
- **Verification method:** Test
- **Verified by:** TC-041
- **Category:** Security
- **Regulatory:** TBD
- **Priority:** Must
- **Status:** Draft

### SYS-042 Stable device name

- **Statement:** The device shall announce a host name that contains its unit identifier through mDNS on the LAN, so that the user can reach it without knowing its IP address.
- **Rationale:** A changed IP address after a DHCP renewal breaks the sender silently (gap G13).
- **Parent:** NEED-016
- **Acceptance criteria:** A PC on the same LAN resolves the name to the current address of the device within [5] s after the device joins; after a DHCP renewal with a new address, the name resolves to the new address.
- **Verification method:** Test
- **Verified by:** TC-042
- **Category:** Usability
- **Regulatory:** TBD
- **Priority:** Should
- **Status:** Draft

### SYS-043 Secure boot and flash encryption

- **Statement:** Every unit that leaves the owner's control shall start only a bootloader signed with the secure-boot key and run only application images signed with the release key, and its flash content shall be encrypted, with the chip's one-time settings locked.
- **Rationale:** Owner request of 2026-11-03: security is important and the product may be sold. Without it, someone with the board and a programmer can read the device key, the token and the unit passphrase, and run other firmware. The 10 internal prototypes are exempt (staged plan in ADR-0007).
- **Parent:** NEED-017
- **Acceptance criteria:** On a unit prepared with the production procedure: an image signed with another key does not start; reading the flash with a programmer shows no readable secret; the download mode and the debug port cannot be used to read or write flash (checked on a sacrificial board). The record of each unit states its stage (prototype without locks, or locked).
- **Verification method:** Test
- **Verified by:** TC-043
- **Category:** Security
- **Regulatory:** CRA Annex I Part I (2)(e), (f) *(verify)*; EN 18031-1 *(verify)*
- **Priority:** Must
- **Status:** Draft

### SYS-044 Software bill of materials

- **Statement:** Every release shall include a machine-readable software bill of materials that lists all software components with name, version, licence and origin, including binary blobs.
- **Rationale:** Required for the technical file under the CRA *(verify)* and for licence checks of the Wi-Fi binary blobs (RISK-020).
- **Parent:** NEED-011
- **Acceptance criteria:** A release build produces an SPDX or CycloneDX file; the file lists every component in the build and the hash of each binary blob; a check fails the release build if a component has no licence entry.
- **Verification method:** Inspection
- **Verified by:** TC-044
- **Category:** Auditability
- **Regulatory:** CRA Annex I Part II (1) *(verify)*
- **Priority:** Must
- **Status:** Draft

### SYS-045 Vulnerability handling and support period

- **Statement:** The project shall publish a contact for vulnerability reports and shall provide security updates for [5] years after the last unit is supplied.
- **Rationale:** Owner decision of 2026-11-03: support period 5 years, as short as the rules allow. The CRA requires vulnerability handling for products placed on the market *(verify)*.
- **Parent:** NEED-017
- **Acceptance criteria:** A `security.txt` or equivalent contact is published; a written process states who receives reports, the time to a first answer ([14] days) and how a fix is released; the support end date is stated in the user information.
- **Verification method:** Inspection
- **Verified by:** TC-045
- **Category:** Security
- **Regulatory:** CRA Art. 13 and Annex I Part II *(verify)*
- **Priority:** Must
- **Status:** Draft

### SYS-046 Recovery of a locked unit

- **Statement:** A unit with secure boot and flash encryption enabled shall be recoverable over USB, with a correctly signed image only, without weakening the lock.
- **Rationale:** The locks of SYS-043 restrict the chip's download mode. A unit with a broken image must not need replacement (SYS-023, SYS-029), and recovery must not open an unsigned path.
- **Parent:** NEED-010
- **Acceptance criteria:** On a sacrificial locked board with a broken application image: a signed recovery image loads over USB and the unit works again; an unsigned or wrongly signed image is refused; the passphrase and device key are not erased by the recovery.
- **Verification method:** Test
- **Verified by:** TC-046
- **Category:** Security
- **Regulatory:** none
- **Priority:** Should
- **Status:** Draft

### SYS-047 Automatic ring orientation

- **Statement:** The device shall measure its orientation and shall start the level display (SYS-032) at the top of the ring within [2] s of a change when the ring plane is more than [30] degrees from horizontal, and at a fixed position on the ring given in the hardware design (proposed: opposite the USB-C connector) when the ring plane is within [30] degrees of horizontal, without user action.
- **Rationale:** NEED-020. An accelerometer gives the direction of gravity, so "up" is known only when the ring plane is not horizontal. A level gauge that starts at a different place in each orientation is hard to read. A fixed zero for the flat case is the only automatic rule that gravity allows.
- **Parent:** NEED-020
- **Acceptance criteria:** With the unit rotated in steps of 90 degrees (plus or minus [10] degrees) in a vertical plane, the zero of a 0 to 100 percent level lies at the top (plus or minus 1 LED). With the unit flat, the zero lies at the fixed position. A change takes effect within [2] s and does not flicker at the [30] degree limit (hysteresis of at least [5] degrees). With the sensor missing or failed, the zero is the fixed position, a fault event is logged and the status display still works (SYS-003).
- **Verification method:** Test
- **Verified by:** TC-047
- **Category:** Functional
- **Regulatory:** none
- **Priority:** Should
- **Status:** Draft
