# ADR-0007: Firmware update path and boot security

- **Status:** Proposed (owner set back from Accepted on 2026-11-03 after goldfish review RV-001; revised the same day for the owner's wish for secure boot and flash encryption; downgrade policy and offline release key remain confirmed by the owner; only the owner sets Accepted)
- **Date:** 2026-11-03
- **Deciders / reviewers:** Ben Spoor (owner); Reviewed in RV-001 (as referenced by plan 02); no separate ADR review
- **Related:** NEED-017, NEED-018, SYS-023, SYS-024, SYS-026, SYS-027, SYS-029, SYS-030, SYS-034, SYS-043, SYS-044, SYS-046, ADR-0002, ADR-0006, ADR-0008; design doc `docs/plans/02-system-design.md` (sections 4.7, G6, G8)

## Context and problem
The owner requires firmware updates over the network (NEED-017). A bad or hostile image must not run (signature check), a power cut or a bad image must not brick the unit
(SYS-029), and settings, certificates and the unit passphrase must survive (SYS-029, SYS-030, ADR-0006).
Owner decisions so far: the first 10 units are prototypes and stay internal. Round 2 said secure boot with fuses comes later with the door open. On 2026-11-03 the owner said security is important and wants secure boot and flash encryption (product may be sold later, EU only, support period 5 years). This revision follows that input.
Flash is 4 MB on the ESP32-C3 module (ADR-0002), and SYS-026 asks for 25 % free space. A Zephyr image with Wi-Fi, TLS and the web server may need 1.0-1.5 MB (estimate, spike 7.1), so two slots fill most of the flash. Paper budget E2a (`docs/verification/reports/spike-7-1-e2a-flash-budget.md`): the break-even image is about 1.31 MiB in the default 4 MB layout and about 1.38 MiB with the unused areas reclaimed; the 1.5 MB upper estimate does not fit at 75 %. The real size comes from E2b.

Not known: image size and slot layout (spike 7.1); whether MCUboot runs on the ESP32-C3 in the pinned Zephyr revision with the needed options (signature type, test/confirm, swap mode).

## Decision criteria
| Criterion | Weight (1-5) | Source requirement |
|-----------|--------------|--------------------|
| A bad or unsigned image never runs | 5 | SYS-029 |
| Power loss or failing image cannot brick | 5 | SYS-029, SYS-027 |
| Fits the flash with margin | 4 | SYS-026 |
| Protection against someone with the board in hand (secure boot, flash encryption) | 4 | owner 2026-11-03; SYS-034, SYS-035; CRA / EN 18031 |
| Irreversible chip steps are staged and safe | 3 | owner round 2; RISK-022 |
| Auditable, standard, reviewable component | 3 | process, CRA |
| No server or hosting needed | 3 | A3 (LAN only) |
| Testable on the PC (power-cut injection) | 3 | SYS-025, SYS-037 |
| Production and recovery stay simple | 3 | SYS-023 |

## Alternatives considered

### A. MCUboot, two slots, signed images, upload through the web interface (U1)
Standard bootloader supported by Zephyr. Image header with signature (ECDSA P-256 with SHA-256 proposed; the key is public in the bootloader), "test, then confirm" semantics: a new image runs once, and if it does not confirm itself, the bootloader swaps back.
Strongest case: it is the project's default and used on many products; the same component works on the PC simulation and in QEMU. Cons: two slots use about twice the image size; a swap needs a scratch or move area (wear); the bootloader itself is not updated over the air.

### B. Pull update from a release URL over HTTPS (U2)
The device checks a server and downloads. Easy for users. Cons: needs a server, a certificate and a clock (SYS-031); ties the project to hosting; larger attack surface. This is an addition on top of A (same slot layout), not a replacement; the owner has not asked for it.

### C. A plus the chip's secure boot and flash encryption, introduced in stages (U3)
The chip's ROM checks the signature of the first-stage bootloader (secure boot v2, key digest in eFuse documented for the C3 in the MCUboot Espressif readme, not tested), MCUboot checks the application image, and flash content is encrypted with a key that stays in eFuse. Stage 1: A without eFuse steps (the 10 internal prototypes). Stage 2: the procedure is proven on sacrificial boards, including encrypted update. Stage 3: eFuses are set on every unit before it leaves the owner.
Strongest case: it is the only option that protects against someone with the board and a programmer, which the owner now wants and which the CRA / EN 18031 argument for a sold product needs.
Cons: irreversible steps (RISK-022); two long-lived secrets besides the passphrases; MCUboot together with the chip's secure boot and encrypted flash is unproven in the pinned Zephyr revision; USB download mode must be restricted by eFuse for the protection to hold *(verify)*, which affects recovery (SYS-023); more production steps.

### D. No bootloader; single image overwritten (U4)
Largest free flash. Cons: a power cut during the write bricks the unit; fails SYS-029. Rejected.

### E. Espressif's own second-stage bootloader and OTA format instead of MCUboot
Works with the chip's own tools and secure boot v2 and is well tested there. Strongest case: possibly less flash used for the loader and native secure-boot support.
It also supports secure boot v2 and flash encryption natively, so it scores as C does on protection. Cons: leaves the Zephyr-standard component, ties the project to a vendor format, is harder to run on the PC simulation, and makes a platform change (ADR-0002 revisit) harder. Kept as the fallback if MCUboot cannot be made to work together with the chip's secure boot on this part.

### F. Do nothing / defer
Not possible for a first release: NEED-017 is a Must.

## Comparison
Scores 0 to 5, my judgement; no datasheet values checked. A here means the end state without eFuse steps, which is also stage 1 of C.

| Criterion (weight) | A | B | C | D | E |
|--------------------|---|---|---|---|---|
| Bad image never runs (5) | 3 | 3 | 5 | 0 | 5 |
| Cannot brick (5) | 4 | 4 | 3 | 0 | 3 |
| Flash margin (4) | 2 | 2 | 2 | 5 | 2 |
| Protection against physical access (4) | 0 | 0 | 4 | 0 | 4 |
| Irreversible steps staged and safe (3) | 5 | 5 | 3 | 5 | 3 |
| Standard, auditable (3) | 5 | 3 | 4 | 0 | 3 |
| No server (3) | 5 | 0 | 5 | 5 | 5 |
| PC test (3) | 5 | 3 | 3 | 4 | 2 |
| Simple production (3) | 4 | 4 | 2 | 5 | 3 |
| **Weighted sum (max 165)** | 115 | 88 | 115 | 77 | 112 |

D scores low and also fails the Must requirement SYS-029, so it is excluded regardless of score.
A and C tie because C is A plus extra steps: the tie is honest. The protection row exists because of the owner's input of 2026-11-03; without it A would win. The decision therefore follows the owner's priority, and the staging in C keeps the cost of the irreversible steps out of the prototype phase. E is close (112) and is the fallback.

## Decision
Choose **C, staged**: build A first (stage 1), prove the eFuse procedure on sacrificial boards (stage 2), and enable secure boot and flash encryption before any unit leaves the owner (stage 3). E is the fallback if MCUboot cannot be made to work with the chip's secure boot.
1. Bootloader MCUboot; images signed with ECDSA P-256 / SHA-256 (algorithm to confirm in spike 7.1). Slot layout and sizes come from the spike 7.1 flash budget table (gap G6). Decision needed if two slots plus 25 % margin do not fit in 4 MB: options are a smaller image (drop features), an 8 MB module (ESP32-C3-WROOM-02-N8, larger module, new board outline; RV-001 item 3), or a differential update. This ADR does not choose among them.
2. **Keys.** (Stage 3 adds the secure-boot key, item 7.) From day 1 every image is signed. The development key is generated in the repository tooling, marked in the image header by a distinct key ID, and never used for a release. The release key is generated and kept offline by the owner (hardware token or encrypted offline medium). The Espressif MCUboot port holds exactly one public key (desk survey E0, Pass 3), so there is no backup key in the bootloader. **Owner decision of 2026-11-03: a lost or leaked release key means a recall of the locked units; no local patch for a second key.** The risk is reduced by keeping two encrypted copies of the same release key in separate places and testing the copies every year (key-management document). The key-management document (G8) must exist before any unit leaves the owner.
3. **Confirmation rule.** A new image confirms itself after its main loop, watchdog and web server have run without fault for [30] s. It does **not** wait for Wi-Fi to connect, because a changed network would otherwise cause a revert loop.
4. **Upload.** Through the web interface over TLS and the web login (ADR-0008), streamed into the secondary slot without a full image in RAM; a size limit equal to the slot; rate-limited; the file is signature-checked again by the bootloader. A failed or interrupted upload leaves the running image untouched.
5. **Downgrade.** Release 1 does not block signed older versions (a hardware counter is not used). The risk that an old vulnerable signed image is re-installed by someone with the web login is accepted for release 1 and recorded.
6. **Storage.** The unit passphrase (ADR-0006), user certificates and the device TLS key are in partitions outside the image slots, not in the image. The layout keeps them in separate areas so they can later be moved under flash encryption.
7. **Stages 2 and 3 (secure boot and flash encryption).**
   - Keep the partition table compatible with flash encryption from stage 1, and write no raw secret in the image.
   - Key types (desk survey E0): the ROM secure boot verifies the bootloader with RSA-3072 (RSA-PSS); the application image is signed with ECDSA P-256 (EC256 in the MCUboot port; RSA signing is reported to make the bootloader too large with secure boot and encryption on the C3). So the release key (EC256) and the secure-boot key (RSA-3072) are different algorithms.
   - Stage 2 checklist additions: set the flash `write-block-size = <32>` in the devicetree overlay (needed for flash encryption with the port; without it an upgrade request failed silently in a reported case); check the bootloader size with secure boot, signing and encryption all on; compare swap using move and swap using offset (no scratch partition) for swap time and flash use.
   - Chip revision (desk survey E0 and E11a): the HAL states that secure boot is not supported on ESP32-C3 revisions below v0.3, so the module and the dev kits must be revision v0.3 or newer (`esptool chip-id`). The purchase and the BOM name the revision.
   - Rehearsal without burned fuses: Zephyr v4.5.0 has `ESP32_EFUSE_VIRTUAL` and `ESP32_EFUSE_VIRTUAL_KEEP_IN_FLASH` (virtual eFuses kept in the `sys` partition) for testing secure boot and development-mode flash encryption. Whether they work on the C3 with MCUboot is not yet tested (E11a). The official Zephyr flash-encryption sample covers the classic ESP32 only.
   - Stage 2: write the fuse procedure and run it on sacrificial boards, including an encrypted update and a power cut during the first encrypted boot. Spike 7.1 shows that MCUboot, the chip's secure boot and encrypted flash work together in the pinned revision *(not verified yet)*. If not, switch to E.
   - Stage 3: before any unit is given to anyone else, the production procedure sets secure boot, flash encryption and the lock of download mode and JTAG *(verify the exact eFuse list)*. Which units are exempt (internal prototypes) is recorded per serial number.
   - The secure-boot signing key is a second offline key. The key-management document (G8) covers it, the MCUboot release key and the flash-encryption key policy (device-generated key never leaves the chip is preferred (documented as possible in the MCUboot Espressif readme; not tested)).
   - After stage 3 the claims in SYS-034 and SYS-035 can extend to physical access for those units. USB recovery (SYS-023) then needs a defined path that does not weaken the lock; see SYS-046.
8. **Pull update (B)** is a later increment behind the same slots.

## Consequences
- Positive: standard bootloader; rollback after a bad image; no server; sold units are protected against a physical attacker; prototypes are not blocked by the irreversible steps.
- **Negative / trade-offs accepted:** flash is halved; the bootloader cannot be updated over the air; keys must be handled with care; old signed images are not blocked; stage 3 steps are irreversible and add a second offline key; internal prototypes stay unprotected against someone with the board and a programmer; recovery of locked units is restricted.
- New risks (to add to risk register): release key loss or leak (accepted by the owner: recall of locked units); development key accidentally shipped; image does not fit two slots with margin; MCUboot not usable on the platform; RISK-022 (bricking by a wrong eFuse step); bricking by a bad bootloader build (bootloader is not recoverable over the air; USB recovery is the path); power-loss corner cases in swap; downgrade attack.
- Requirements created or changed: SYS-029 stays. New SYS/SW needed for: key management evidence, confirmation rule, downgrade policy statement, image size limit, production USB recovery path.

## Verification and revisit
- Spike 7.1 (secure boot part): MCUboot plus ESP32-C3 secure boot v2 and flash encryption on a sacrificial board, encrypted OTA, recovery path after the lock.
- Spike 7.1: build MCUboot and a minimal signed app for ESP32-C3, update it over the air, measure image size, slot sizes and free flash.
- TC-029: update, reject a wrong signature, reject a changed byte, power cut at every step (target at least [100] cuts; first on the PC with injected flash write failures in `native_sim`, then on hardware), revert after a failing image.
- Check that the development key cannot sign a release build (release build script fails on the development key ID).
- Revisit when: image plus margin does not fit, MCUboot cannot be built on this platform (then E), the sacrificial-board test fails (then E), the eFuse list or recovery limits change SYS-023, or a downgrade attack is shown to matter for the CRA argument.

## Evidence update from spike 7.1 E11a (2026-11-03, build only)
Record: `docs/verification/reports/spike-7-1-e11a-build-variants.md`.
- In Zephyr v4.5.0 the bootloader that sysbuild builds for `esp32c3_devkitm` is the Zephyr-app MCUboot (`boot/zephyr`). It has **no** Kconfig symbols for the chip's secure boot v2 or flash encryption: setting them fails with "undefined symbol" (built).
- The symbols exist only in the **standalone Espressif port** of MCUboot (`boot/espressif`), which expects an ESP-IDF-style HAL version 6.0.x. The Zephyr `hal_espressif` module (6.2.0, trimmed) cannot build it (built, failed at configure). A build against a full ESP-IDF v6.0 checkout was started and not completed.
- Consequence for stage 3: secure boot and flash encryption need a **second bootloader build chain** (ESP-IDF checkout, pinned version, outside west and sysbuild), or Espressif's own bootloader (option E), which has the same need. The Zephyr application image would still be signed with `imgtool` (EC256) and verified by that bootloader; the flash map of the port and of the Zephyr application must match (not yet checked).
- This lowers the score of option C relative to option A for the Zephyr-only toolchain, and makes the fallback E nearer to C than the ADR assumed. The scores above are not changed in this edit; the owner decides whether the second build chain is acceptable. **Open owner decision:** accept a pinned ESP-IDF build for the bootloader only (and allow the build to be completed in the spike), or reconsider secure boot for release 1.
- Stage 1 (no eFuse steps) is unaffected: sysbuild MCUboot with EC256 signing, swap using offset, builds today.

## Critical review notes
First objection: "Without secure boot, a signature check is bypassed by anyone who can write flash, so the signed update gives a false sense of security."
Answer: true for stage 1, and stage 1 is for the internal prototypes only. Stage 3 closes the gap before any unit leaves the owner. The technical file states which units are in which stage.
Second objection: "Two 1.5 MB slots in a 4 MB flash leaves no room for the 25 % margin." Answer: probably true; this is flagged as an open decision pending the spike, with three named options, not hidden.
Third objection: "One eFuse mistake bricks a unit; a batch of units can be lost." Answer: that is why stage 2 exists and why the procedure is scripted and run on sacrificial boards first (RISK-022).
