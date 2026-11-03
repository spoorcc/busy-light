# 03 -- Spike 7.1: Zephyr on ESP32-C3 (design doc)

- **Status:** Draft (no goldfish review run yet; the owner has not approved it)
- **Date:** 2026-11-03  **Owner:** Ben Spoor
- **Area:** sw (exploratory; no product code)
- **Requirements addressed:** none are implemented. The spike measures the feasibility of SYS-012, SYS-026, SYS-027, SYS-029, SYS-034, SYS-036, SYS-043, SW-002 and SW-004, and answers open questions in ADR-0002, ADR-0006, ADR-0007 and ADR-0008.
- **EGM review record:** none yet (run `egm-review` before the owner approves)

## 1. Problem definition
Plan 02 and ADR-0002..0008 depend on facts about Zephyr on the ESP32-C3 that nobody has checked: flash fit, heap, access point with station, MCUboot together with the chip's secure boot, TLS server and client together, LED output during Wi-Fi traffic. Until these are measured, the ADRs cannot be accepted and the requirement values stay guesses (RV-001 readiness pass: NO-GO).
Out of scope: product code, the web page design, the mapping model, hardware design, any step that cannot be undone on a board that is not a sacrificial one.

## 2. Constraints and assumptions
- Process rule (`docs/process/README.md`): spike code lives only on a branch `spike/7.1-zephyr-esp32c3`, is never merged, and its results go into `docs/verification/reports/spike-7-1.md` on the normal branch. Code written here is thrown away or rewritten under Approved requirements with tests.
- A1: the ESP32-C3-DevKitM-1 (module ESP32-C3-MINI-1, 4 MB flash) is representative of the planned module *(verify the flash size of the kit at purchase)*.
- A2: Zephyr v4.2.0 as pinned in `sw/west.yml`. If a needed feature exists only in a newer release, the spike records that and tests the newer release as a second run.
- A3: free tools only, and a PC build (Wokwi excluded, owner round 7).
- A4: the owner runs the hardware steps. I (Claude) write the procedure and the scripts, and analyse the logs the owner pastes or saves. I do not claim a measurement that nobody made.
- A5: eFuse steps are done only on boards marked "sacrificial" (ADR-0007 stage 2). At least [3] such kits are bought; the first one is expected to be lost.

## 3. Alternatives considered
- **Spike on a dev kit (chosen).** Fast, cheap, same module as the target.
- **Paper study only.** Rejected: the same reviewers that found the flash gap worked from memory (RV-001).
- **Build the real board first.** Rejected: it would freeze the antenna and the LED drive before the facts are known (ADR-0003, ADR-0004).
- **Do nothing.** The design stays NO-GO.

## 4. Technical plan
The spike is a list of experiments. Each has a method, a pass rule and a result field. A failure is a useful result: it names the fallback.

| # | Experiment | Method | Pass rule | If it fails |
|---|------------|--------|-----------|-------------|
| E1 | Hello, Wi-Fi station and `led_strip` | Build `samples/hello_world` and a Wi-Fi station sample for the board with the pinned release; drive a 16-LED ring (or a short strip of 16) through the SPI or RMT `led_strip` driver | Builds; joins a WPA2 network; LEDs show a test pattern | Record the missing symbol or driver; start the [2]-week cap for that feature (RV-001 item 23) |
| E2 | Flash and RAM budget on paper, then measured | Fill a table: bootloader, two slots, settings, certificate/secret area, web files, margin, EAP headroom. Then build the app with Wi-Fi, TLS (client and server), HTTP server, JSON, MCUboot and measure `size` and the largest free heap block | Image size at most [75] % of the slot (SYS-026); two slots fit in the 4 MB flash with the settings and secret areas | Options in ADR-0007 item 1: smaller image, larger-flash module, differential update |
| E3 | Access point with WPA2-PSK | Run a soft AP with a 16-character passphrase and a DNS responder; join with one iPhone and one Android phone; scan the Wi-Fi QR code; open the page | Both phones join and reach the page within [20] s; the captive-portal sheet opens or a typed address works | Record the phone behaviour; consider a fixed address and the typed-address instruction |
| E4 | AP and station at the same time | Run the AP and a station that joins another network | Both stay up for [10] min with a client on the AP and traffic on the station | ADR-0006 item 9 fallback: the test join closes the AP and reopens it on failure |
| E5 | HTTP server with TLS, and a TLS client with a user CA | Serve a page over TLS with an EC P-256 device certificate created on the device; poll a test HTTPS server with a certificate signed by a user-loaded CA; pinned-key `curl --pinnedpubkey` | Handshake completes; time to the first byte is at most [3] s for the server (cold) and [5] s for the client; no heap leak over [1000] requests | Smaller cipher set, session reuse, or a lighter TLS stack setting; record the numbers |
| E6 | Heap with two TLS sessions and an update upload | Run two TLS sessions, one poll and one image upload to the secondary slot at the same time (SW-002) | The lowest free heap is at least [25] % of the heap (SYS-026); no reset in [30] min | Lower the session limit to 1; cut buffers; record the effect on SW-002 |
| E7 | LED frame integrity under load | Output a fixed animation by the hardware driver while E6 runs; capture the data line with a logic analyser *(a cheap one is enough)* | No corrupted frame in [10] min (compare with the expected frame count) | ADR-0004: move to the clocked LED (option B) |
| E8 | Key creation and random source | Create an EC P-256 key on the device with the hardware random generator seeded; time it; create [1000] passphrases and check for repeats | Key creation at most [10] s; no repeated passphrase; random source reported as seeded before use | ADR-0006 item 2 fallback: generate on the host (W1a) |
| E9 | MCUboot with signed images, test-then-confirm | Build MCUboot for the board; sign with a development key; upload by the device's own server; run SW-004's confirmation rule; measure swap time | A good image installs and confirms; a bad signature and a changed byte are rejected; an unconfirmed image reverts within [60] s of its first start including the swap | ADR-0007 fallback E (Espressif bootloader) |
| E10 | Power cut during update and settings write | Use a relay or a controllable USB switch; cut power at random points during upload, swap and a settings write; [100] cuts | The unit always boots to a working image; settings and the unit passphrase stay readable or are detected as invalid and recovered | Record the corner cases; this feeds TC-019 and TC-029 and the power-cut rig design |
| E11 | MCUboot with the chip's secure boot and flash encryption (sacrificial kit) | Follow the vendor's procedure for secure boot v2 and flash encryption in development mode first; then the signed MCUboot, an encrypted update and a power cut during the first encrypted boot; test the recovery path (SYS-046) | The unit boots only signed images, flash is unreadable by a programmer, an encrypted update works, recovery works | ADR-0007: use the Espressif bootloader (E); record the eFuse list and what cannot be undone |
| E12 | EAP headroom | Build with the WPA2-Enterprise supplicant options enabled and measure the flash and heap difference | Difference is recorded; compare with SYS-036's limit once measured | Mark SYS-036 not feasible on 4 MB; ask the owner |
| E13 | Time and size of the extractor | Run the SW-001 limits on the target with the maximum input | At most [50] ms | Reduce the limits |

## 5. Detailed implementation plan
- **Files to create (all on the branch `spike/7.1-zephyr-esp32c3`, never merged):** `sw/spike/` with one folder per experiment (`e01_hello`, `e02_budget`, ...), each with a `README.md` giving the exact `west build` line, the Kconfig used, and what to look for; `sw/spike/results/` for raw logs.
- **Files to create on the normal branch after the run:** `docs/verification/reports/spike-7-1.md` with the filled-in table, the commit hash of the spike branch, the Zephyr revision and the board; updates to ADR-0002, 0006, 0007, 0008 (Proposed, so editable) and to the bracketed values in the requirements.
- **Kconfig and devicetree:** unknown until E1. The spike records the final `prj.conf`, overlay files and board name in the report. Names I expect to need are `CONFIG_WIFI`, the ESP32 Wi-Fi driver options, `CONFIG_NET_*` sockets, `CONFIG_HTTP_SERVER`, `CONFIG_MBEDTLS_*` or the PSA crypto options, `CONFIG_BOOTLOADER_MCUBOOT`, `CONFIG_LED_STRIP` *(all to verify against the pinned release; no names are fixed here)*.
- **Order of work:** E1, E2 (paper), E3, E4, E8, E5, E6, E7, E9, E10, E13, E12, E11. E11 is last because it uses a sacrificial kit and may destroy it.
- **Shopping list for the owner:** [3] or more ESP32-C3-DevKitM-1 kits; a 16-LED ring or strip of the chosen type; a 5 V supply and a USB power meter; a logic analyser; a USB relay or controllable USB hub for the power cuts; one iPhone and one Android phone; a Jenkins instance or a test HTTPS server; a Wi-Fi access point with WPA2 for testing.
- **Rules during the spike:** every measured number is copied with its unit and the exact build; a failed experiment is reported as failed. Any local patch to Zephyr or a module gets a `DEV-` record with a plan to upstream it (round 7 decision). A feature that takes more than [2] weeks stops and goes to the owner.

## 6. Test and verification plan
The spike is itself the verification. Mapping to test cases (procedures are written later, using these measurements):
| Experiment | Feeds |
|------------|-------|
| E3, E4 | TC-012, TC-013 |
| E5 | TC-034, TC-035, TC-030 |
| E6 | TC-026, TC-102 |
| E7 | TC-001, TC-018 |
| E8 | TC-013 |
| E9, E10 | TC-029, TC-104, TC-019 |
| E11 | TC-043, TC-046 |
| E12 | TC-036 |
| E13 | TC-101 |
Evidence: raw logs and captures are stored with the report (large files stay outside Git and are listed by hash).

## 7. Risks and open questions
- The dev kit may differ from the planned module (flash size, antenna type, USB bridge). Record the exact kit.
- The development kit's USB-serial bridge is not the same as the chip's native USB used on the final board *(verify)*. Programming and recovery tests on the kit may not transfer.
- E11 may brick the kit: that is accepted. RISK-022 is about this.
- The owner's time: E3 and E10 need phones and a rig. A rough effort estimate is [3] to [5] working days of owner time plus waiting for parts. This is a guess.
- Open question for the owner: buy the kits and parts now? The list is in section 5.

## 8. Rollout / rollback and traceability
IDs involved: ADR-0002, 0003 (not touched), 0004 (E7), 0005 (E13), 0006 (E3, E4, E8), 0007 (E2, E9, E10, E11), 0008 (E5); SYS-012, 026, 027, 029, 034, 036, 043, 046; SW-001, 002, 004; RISK-009, 010, 022.
Rollback: delete the spike branch. Nothing from it enters `main` except the report and the document updates.
