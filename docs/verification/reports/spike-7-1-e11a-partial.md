# Spike 7.1, E11a (partial): ECDSA P-256 build and secure-boot source checks

- **Status:** Draft (author's record; no goldfish or owner review)
- **Date:** 2026-11-03
- **Plan:** `docs/plans/03-spike-7-1-zephyr-esp32c3.md`, experiment E11a (no eFuse)
- **What was done:** one extra build on the PC and reading of source. **Secure boot and flash encryption were not enabled in any build, nothing was flashed, no eFuse was touched.** E11a is only partly done; its main question (do MCUboot, the chip's secure boot and flash encryption build and work together) is **open**.
- **Environment:** as in `spike-7-1-e1-build.md` (Zephyr v4.5.0, SDK 1.0.1, MCUboot 2.5.0).

## Build: ECDSA P-256 signing
Command options: sysbuild `-DSB_CONFIG_BOOT_SIGNATURE_TYPE_ECDSA_P256=y` and `-DSB_CONFIG_BOOT_SIGNATURE_KEY_FILE=<spike key>`. The spike key was made with `imgtool keygen -t ecdsa-p256` outside the repository, named `SPIKE-ONLY-ec-p256.pem`, and is not kept.

| Item | RSA-2048 (default sample key) | ECDSA P-256 (spike key) |
|------|-------------------------------|--------------------------|
| Result | built | built |
| Bootloader image (`zephyr.bin`) | 47 680 B | **42 560 B** (5 120 B smaller) |
| Loader segment `iram_loader_seg` | 5 952 B of 7 KB (83.04 %) | 5 952 B of 7 KB (83.04 %) |
| Application image, Wi-Fi shell (`zephyr.signed.bin`) | 709 780 B | 709 595 B |
| Swap mode | swap using offset | swap using offset |

Reading: ECDSA P-256 signing builds with no change other than the two options, and gives a smaller bootloader. The ROM loader segment is the same in both builds. The loader-size limit of MCUboot issue 1262 refers to the whole bootloader with secure boot and encryption on; this build has neither, so it does **not** settle that issue.

## Source checks (v4.5.0 workspace, no build)
| Item | Finding | Class | Effect |
|------|---------|-------|--------|
| Virtual eFuses | Zephyr v4.5.0 has `ESP32_EFUSE_VIRTUAL` ("simulate eFuse operations in RAM") and `ESP32_EFUSE_VIRTUAL_KEEP_IN_FLASH` (keeps the virtual fuses in the `sys` partition across reboots, "useful for testing secure boot and flash encryption"). It cannot be combined with release-mode flash encryption | in source | **Differs from the 2024 maintainer remark** (issue 1866) that virtual eFuses were not supported on Zephyr. If they work, stage 2 rehearsals of secure boot and development-mode encryption need no burned fuses, which lowers RISK-022 and the number of sacrificial kits. Untested |
| Secure boot dependency on the chip revision | The Espressif bootloader Kconfig says: secure boot is not supported for ESP32-C3 revision below v0.3. The C3 SoC capability file lists secure boot v2 with **RSA only** (no ECC) | in source | Confirms RSA-3072 for the ROM stage. **The chip revision must be at least v0.3**: check it on the dev kit (`esptool chip-id`) and make it a purchase and BOM requirement for the module (HW-008) |
| Official flash-encryption sample | `samples/boards/espressif/flash_encryption` lists the classic **ESP32** only (overlays for `esp32_devkitc`, `yd_esp32`); no ESP32-C3 entry | in source | Flash encryption under Zephyr on the C3 has no official sample. Expect to work from the MCUboot Espressif documentation. The risk that this path is less exercised stays |
| Secure boot options | The HAL's bootloader Kconfig has the secure-boot, signed-on-boot and flash-encryption symbols. I did not find how to set them from a Zephyr sysbuild (`SB_CONFIG` or an MCUboot overlay) | unknown | Next step: find the supported way (MCUboot Espressif readme, the `west espressif` tooling) and try a build with the options on |

## What this changes
**Applied in the next commit (autonomous session, 2026-11-03):** items 1 to 3 below are written into ADR-0007 (Proposed), HW-008 (Draft) and RISK-022. Original proposals:
1. **ADR-0007:** add (a) the chip revision condition (at least v0.3) to stage 2 and to the module purchase; (b) the virtual-eFuse option as the first rehearsal path in stage 2, to be verified; (c) a note that the official flash-encryption sample does not cover the C3.
2. **HW-008 / spike 7.4:** the BOM must name a module revision that supports secure boot (at least v0.3).
3. **RISK-022:** note the virtual-eFuse option as a possible mitigation (unverified).

## Still open in E11a
Secure boot and flash encryption enabled in an MCUboot build for the C3 (size against the 7 KB loader segment and the ROM limit); the swap mode with encryption (the port says `ESP_MCUBOOT_ERASE_PROGRESSIVELY` must be off); whether an upgrade request works with the `write-block-size = <32>` overlay. These need the Kconfig route above, and later the dev kit.
