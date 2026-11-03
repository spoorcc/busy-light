# ADR-0006: Provisioning channel and per-unit access point password

- **Status:** Proposed (only the owner sets Accepted)
- **Date:** 2026-11-03
- **Deciders / reviewers:** Ben Spoor (owner); goldfish review not yet run
- **Related:** NEED-001, NEED-016, NEED-019, SYS-012, SYS-013, SYS-023, SYS-034, SYS-035, ADR-0002, ADR-0008; design doc `docs/plans/02-system-design.md` (sections 4.5, 4.6)

## Context and problem
A new device has no Wi-Fi credentials and no screen. The user must give it the home or company Wi-Fi password, and possibly a certificate (SYS-035), using only a phone or PC (NEED-001).
The link that carries these secrets must be encrypted with a password that is different for each unit and cannot be derived from what the device broadcasts (SYS-013).
Two decisions in one ADR because they depend on each other: the channel (how the user reaches the device) and the unit password (how that channel is protected and how the user learns the password).

Forces: no app (NEED-016); the first 10 units are made by the owner, later units perhaps by others from the open files, so the production step must be documented and repeatable
(SYS-023); WPA2 must stay possible (owner round 1); secure-boot fuses are not used on prototypes (owner round 2), so secrets in flash are readable by someone with the board in hand.

Not known: whether the pinned Zephyr revision gives a soft AP with WPA2-PSK and a DNS responder for a captive portal on ESP32-C3 (spike 7.1); how phones behave when the AP has no Internet.

## Decision criteria
| Criterion | Weight (1-5) | Source requirement |
|-----------|--------------|--------------------|
| Secrets not readable by a nearby radio listener | 5 | SYS-013 |
| Works on phones without an app | 5 | NEED-001, NEED-016 |
| Password unique and not derivable from SSID or MAC | 5 | SYS-013, NEED-019 |
| User can learn the password without tools | 4 | NEED-016 |
| Repeatable by a builder from the open files | 3 | SYS-023 |
| Small code, small flash use | 3 | SYS-026 |
| Keeps WPA2 and later WPA2-Enterprise possible | 2 | SYS-036 |
| Does not need irreversible chip steps | 2 | owner round 2 |

## Alternatives considered

### Channel
**V1. Soft AP plus web page** (as NEED-001). Works on every phone and laptop, no app. Cons: phones warn "no Internet"; a captive-portal DNS answer is useful; the device cannot be a station and AP at the same time on some stacks, so the home network is joined after the page is closed.
**V2. BLE provisioning from a web page.** No temporary network. Cons: Web Bluetooth does not work on iOS Safari; adds a Bluetooth stack to flash; fails NEED-016 for iPhone users.
**V3. USB serial only.** Simple and reliable. Cons: needs a PC and a tool; not for non-technical users. Kept as the production and recovery path.
**V4. Vendor smart-config** (the Wi-Fi password broadcast to the device). Quick. Cons: weak confidentiality, vendor lock-in, not in the Zephyr upstream.

### Unit password (for V1)
**W1. Random passphrase per unit created in the production step, stored in a separate flash area, shown on a label as text and as a Wi-Fi QR code.** A 16-character passphrase from a 32-character set has 80 bits.
Strongest case: simple, standard WPA2-PSK, phones join by camera scan, no extra protocol to review.
Sub-options: W1a generated on the production PC and written to the device; W1b generated on the device from its hardware random generator and read once through USB for the label.
**W2. Derived from a chip secret (eFuse) and the MAC.** No password list. Cons: irreversible fuse use (against owner round 2); the user still needs the value, so a label or tool is needed anyway.
**W3. Open AP plus a pairing code (PAKE) at application level.** No printed Wi-Fi password. Cons: the Wi-Fi layer is unencrypted; code to specify, review and fuzz; fails SYS-013 wording ("access point protected by encryption").
**W4. Same password on every unit.** Trivial. Cons: fails NEED-019 and SYS-013. Rejected.
**W5. WPA3-SAE with the unit passphrase.** Better protection against offline guessing. Cons: Zephyr and phone support is not confirmed; WPA3 is not mandatory with an 80-bit passphrase. A later upgrade on the same label.

### Do nothing / defer
Ship with an open AP for the 10 prototypes. Rejected: the Wi-Fi password would cross an open link, and the owner already chose per-unit passwords (NEED-019).

## Comparison
Scores 0 to 5, my judgement. I compare packages of channel plus password.

| Criterion (weight) | V1+W1 | V1+W3 | V2+W1 | V3 only | V1+W4 |
|--------------------|-------|-------|-------|---------|-------|
| Secrets safe from radio listener (5) | 5 | 3 | 4 | 5 | 1 |
| Works on phones, no app (5) | 4 | 4 | 2 | 0 | 4 |
| Unique, not derivable (5) | 5 | 3 | 5 | 5 | 0 |
| User learns password without tools (4) | 4 | 4 | 4 | 0 | 5 |
| Builder can repeat (3) | 4 | 3 | 3 | 4 | 5 |
| Small code (3) | 4 | 1 | 2 | 5 | 5 |
| WPA2 and Enterprise stay possible (2) | 5 | 3 | 5 | 5 | 5 |
| No irreversible steps (2) | 5 | 5 | 5 | 5 | 5 |
| **Weighted sum (max 145)** | 130 | 94 | 106 | 97 | 95 |

W2 and V4 are not scored: W2 would score 0 on the "no irreversible steps" row and V4 fails confidentiality, so neither could beat V1+W1.

## Decision
Choose **V1 + W1b**, with V3 as the production and recovery path.
1. The AP starts only when there are no credentials or the user asks for it (long button press, SYS-012). It is not on in normal use. It stops after [10] min without a completed setup and then waits for a new long press (an unprovisioned unit does not stay open indefinitely; RV-001, finding 5). It accepts one client at a time. The Zephyr ESP32 driver fixes the limit at 5 clients, so our code enforces one (or a driver change with a `DEV-` record, spike 7.1). The page never shows stored credentials or keys.
2. WPA2-PSK with a 16-character passphrase from a 32-character set without look-alike characters (80 bits), created on the device from the hardware random generator, only after the radio has been started (the generator gets extra entropy only while Wi-Fi or Bluetooth is enabled, desk survey E0), and shown once through USB in the production step.
   Reason for W1b over W1a: no file with the secrets of all units has to exist on a production PC. The owner prints the label from the one-time output and then does not keep it, or keeps it in a password manager. If the random generator cannot be shown to be seeded at that moment (spike 7.1), fall back to W1a with `secrets` from the host.
3. The label carries: the SSID suffix (unit identifier), the passphrase, and a Wi-Fi QR code. The device also needs a short unit name on the housing.
4. The passphrase lives in its own flash area (not in the normal settings area), survives factory reset (it identifies the unit) and firmware update, and is never sent over any interface after production.
5. The SSID contains the unit identifier but nothing from which the passphrase can be calculated.
6. The page in the AP is served on plain HTTP (ADR-0008); this is acceptable because the link is WPA2 encrypted with the unit passphrase.
7. Lost label: the passphrase can be read again only over USB with the physical device, and only while the button is held (physical presence), in a documented recovery command. This resolves the conflict with item 4: the passphrase is never sent over the network or the AP page. There is no remote or button-only reset of the passphrase in release 1. The value is read back from flash and compared before the label is printed, and the secrets partition is part of the power-cut tests (RV-001, finding 5).
8. WPA3-SAE (W5) is a later option behind the same label.
9. **Provisioning state machine** (to specify in the SW requirements): AP up, user submits credentials, the device tests the join, on failure it stays in AP mode and shows the failure on the ring, on success it stops the AP. Spike 7.1 must show whether the AP and station can run together; if not, the test join closes the AP and reopens it on failure.
10. Certificate upload inside the AP may fail in the restricted browser that phones open for captive portals (no file picker). The page therefore also accepts pasted PEM text, and the spike tests one iPhone and one Android phone.

Open point for the owner: the **web interface login password** (SYS-016) on the LAN. This ADR assumes it is chosen by the user during first setup and stored hashed (not the same as the AP passphrase). A requirement for this is missing and must be drafted.

## Consequences
- Positive: no app; secrets protected by the Wi-Fi layer; no password list in the file system; works with the camera app on phones.
- **Negative / trade-offs accepted:** the label can be lost or photographed; any person who sees the label can join the AP when the user starts it; production needs a step per unit (about 1 minute, estimate) and a label printer; the passphrase is stored in plain flash on prototypes (no secure boot yet), so physical access with a programmer reads it.
- New risks (to add to risk register): passphrase leaked by label photo; weak random source at production; passphrase lost on a flash erase; phone auto-join behaviour; captive-portal failure on some phones; leftover test passphrase in a released image.
- Requirements created or changed: SYS-013 acceptance criteria stay; new SYS for the web login password; new SW requirements for the unit-secret store, the USB production command and the AP start rules; TC-013 gets a "radio capture" procedure.

## Verification and revisit
- TC-012 and TC-013 on at least two phone types (one iOS, one Android) in spike 7.1, including the QR join.
- Analysis: entropy of the generator (80 bits, no repeated values in 10 units, test on the PC with the same algorithm).
- Radio capture of a provisioning session shows only encrypted frames (inspection of a capture).
- Revisit when: secure boot or flash encryption is introduced (ADR-0007), a platform change (ADR-0002), Zephyr drops WPA2-PSK in the AP, or the volume passes about 1000 units per year (then a printed label per unit needs a line process).

## Critical review notes
Strongest objection: "A label is a weak secret store; anyone who sees the device can join the AP, and the AP offers certificate upload."
Answer: the AP is off in normal use and needs the long button press, so a person needs physical access to the device and the label together. That is the same level of access as pressing a reset button on many consumer devices.
The residual risk is accepted for the first release. The label is a shared secret, not a per-session secret: anyone who has seen it can decrypt a captured join handshake of another client and read the Wi-Fi password typed during that session. WPA3-SAE (W5) would remove this; it stays a later option.
Second objection: "80 bits is not needed; 63 characters is possible." Answer: the label must be typeable by a user; 16 characters is the longest value that keeps typing realistic, and offline guessing of 80 bits through WPA2's key derivation is not practical.
Third objection: "Generating the secret on the device assumes a good random source." Accepted as a risk, with the host-generated fall-back in item 2.
