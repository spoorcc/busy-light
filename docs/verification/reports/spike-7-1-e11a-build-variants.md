# Spike 7.1, E11a (build variants): secure boot v2 and flash encryption in the ESP32-C3 MCUboot build

- **Status:** Draft (author's record; no goldfish or owner review)
- **Date:** 2026-11-03
- **Plan:** `docs/plans/03-spike-7-1-zephyr-esp32c3.md`, experiment E11a
- **Follows:** `spike-7-1-e11a-partial.md`
- **Scope:** Build only. Nothing was flashed, no hardware was touched, no eFuse was burned.
- **Result in one line:** In Zephyr v4.5.0 sysbuild, the MCUboot that sysbuild builds for `esp32c3_devkitm` **has no secure boot v2 and no flash encryption options**. The variants A (secure boot), B (flash encryption) and C (both) **could not be built** with sysbuild. The Espressif MCUboot port that does have these options **could not be built** from the Zephyr HAL. Virtual eFuse and the application side of flash encryption do build.

Marks: **in source** = read in the files named; **built** = a build ran and the result was observed; **unknown** = not determined.

## 1. Environment
| Item | Value | Mark |
|------|-------|------|
| Zephyr / MCUboot / SDK | v4.5.0 / 2.5.0 / Zephyr SDK 1.0.1 | built |
| Board, sample | `esp32c3_devkitm`, `zephyr/samples/net/wifi/shell` with `--sysbuild` | built |
| App signing in all builds | ECDSA P-256, key `SPIKE-ONLY-ec-p256.pem` (outside the repository) | built |
| HAL in the west workspace | `modules/hal/espressif`, reports itself as HAL version 6.2.0 | built |
| Flash layout of the board | `partitions_0x0_default_4M.dtsi`: boot 0x0 (64 KB), `sys` 0x10000 (64 KB), slot0 0x20000, slot1 0x1e0000 | in source |
| Chip revision | not checked; no hardware used | unknown |

Build logs and trees are in the session scratchpad (`logs/e11a_*.log`, `build/e11a_*`). They are not kept in the repository.

## 2. Options found, with file references
Paths are relative to the west workspace.

1. **Which MCUboot is built.** Zephyr sysbuild builds the Zephyr application `bootloader/mcuboot/boot/zephyr` (build info: `source-dir .../boot/zephyr`). This is not the Espressif port in `bootloader/mcuboot/boot/espressif`. (built; in source)
2. **How to pass options to that MCUboot from the sysbuild command line.** `-Dmcuboot_CONFIG_<SYMBOL>=<value>` works. It is written to `mcuboot/zephyr/misc/generated/extra_kconfig_options.conf`. Devicetree: `-Dmcuboot_DTC_OVERLAY_FILE=<file>` (and `-Dshell_DTC_OVERLAY_FILE=` for the application) worked. A `sysbuild/mcuboot.conf` file in the application directory is the other documented route; I did not use it. (built for `-D`; unknown for the file route)
3. **Secure boot and flash encryption symbols for the bootloader.** `CONFIG_SECURE_BOOT`, `CONFIG_SECURE_BOOT_V2_ENABLED`, `CONFIG_SECURE_FLASH_ENC_ENABLED` and the `..._MODE_DEVELOPMENT` symbols are defined **only** in `modules/hal/espressif/components/bootloader/Kconfig.projbuild` (lines 604, 643, 821). That file is not read by the Zephyr Kconfig. The Zephyr tree has no definition of them (search of `zephyr/` for `SECURE_BOOT` and `SECURE_FLASH_ENC`). Test: `-Dmcuboot_CONFIG_SECURE_BOOT=y -Dmcuboot_CONFIG_SECURE_BOOT_V2_ENABLED=y` stops configuration with `attempt to assign the value 'y' to the undefined symbol SECURE_BOOT` and `Aborting due to Kconfig warnings`. (built)
4. **Where the options are documented.** `bootloader/mcuboot/docs/readme-espressif.md`, sections "Secure Boot" (line 339) and "Flash Encryption" (line 493), and `boot/espressif/port/esp32c3/bootloader.conf` (commented lines). They apply to the **standalone Espressif port**, built with `cmake -DMCUBOOT_TARGET=esp32c3 -DESP_HAL_PATH=... -DMCUBOOT_CONFIG_FILE=...`, not to the Zephyr app. The Zephyr sample `samples/boards/espressif/flash_encryption/README.rst` also says the bootloader must be configured "per the MCUBoot Readme". (in source)
5. **Options listed for the C3 in that readme.** Secure boot v2: `CONFIG_SECURE_SIGNED_ON_BOOT`, `CONFIG_SECURE_BOOT`, `CONFIG_SECURE_BOOT_V2_ENABLED`, `CONFIG_SECURE_SIGNED_APPS_RSA_SCHEME`, `CONFIG_SECURE_BOOT_SUPPORTS_RSA`. Flash encryption development mode: `CONFIG_SECURE_FLASH_ENC_ENABLED`, `CONFIG_SECURE_FLASH_ENCRYPTION_MODE_DEVELOPMENT`, plus `..._UART_BOOTLOADER_ALLOW_ENC/DEC/CACHE`. Development aids: `CONFIG_SECURE_BOOT_ALLOW_JTAG`, and the port's own `CONFIG_EFUSE_VIRTUAL`, `CONFIG_EFUSE_VIRTUAL_KEEP_IN_FLASH`, `CONFIG_EFUSE_VIRTUAL_OFFSET=0x10000`, `CONFIG_EFUSE_VIRTUAL_SIZE=0x2000`. App signing in the port: `CONFIG_ESP_SIGN_EC256` with `CONFIG_ESP_USE_TINYCRYPT`. Note: the readme names the RSA scheme for the ROM stage and EC256 for the MCUboot image check, so both are used together. (in source)
6. **Virtual eFuse in the Zephyr app.** `ESP32_EFUSE_VIRTUAL` and `ESP32_EFUSE_VIRTUAL_KEEP_IN_FLASH` are defined in `zephyr/soc/espressif/common/Kconfig.efuse`. The offset and size default to the `sys_partition` node (0x10000, 0x2000). The HAL maps them to `CONFIG_EFUSE_VIRTUAL*` in `modules/hal/espressif/zephyr/port/include/zephyr_compat.h` (lines 200 to 205). `flash_esp32.c` and `bootloader_flash.c` use them. (in source)
7. **Flash encryption on the application side.** `CONFIG_ESP_FLASH_ENCRYPTION` (`zephyr/soc/espressif/common/Kconfig.flash`, line 136) depends on `!ESP_SIMPLE_BOOT && !MCUBOOT && write-block-size = 32`. So it exists only for the application, and the Zephyr MCUboot app cannot have it. (in source; built for the application)
8. **Official sample.** `flash_encryption` lists the classic ESP32 only. (in source, see partial report)
9. **Stale reference.** `modules/hal/espressif/zephyr/CMakeLists.txt` tests `CONFIG_MCUBOOT_ESPRESSIF`; no Kconfig symbol of that name exists in the workspace. It looks like a leftover of an earlier integration. (in source; meaning unknown)

## 3. Results
Common options for every sysbuild row: `west build -p always -b esp32c3_devkitm --sysbuild zephyr/samples/net/wifi/shell -- -DSB_CONFIG_BOOT_SIGNATURE_TYPE_ECDSA_P256=y -DSB_CONFIG_BOOT_SIGNATURE_KEY_FILE=\"<spike key>\"`, plus the options in the table. The loader limit is the 7 KB `iram_loader_seg`.

| ID | Variant | Extra options | Result | Bootloader `zephyr.bin` | `iram_loader_seg` | Error or note | Mark |
|----|---------|---------------|--------|-------------------------|-------------------|---------------|------|
| Base | ECDSA P-256, no security features (from partial report) | none | success | 42 560 B | 5 952 B (83.04 %) | | built |
| A | Secure boot v2 only, sysbuild | `-Dmcuboot_CONFIG_SECURE_BOOT=y -Dmcuboot_CONFIG_SECURE_BOOT_V2_ENABLED=y` | **failed at configure** | none | none | `undefined symbol SECURE_BOOT`; `Aborting due to Kconfig warnings` | built |
| B | Flash encryption (development mode) only, sysbuild | not tried with `SECURE_FLASH_ENC_ENABLED`: same undefined-symbol mechanism as A | **not built** | none | none | Symbols do not exist in the Zephyr Kconfig (section 2, item 3). I did not run this build; the A failure shows the mechanism | in source |
| C | Both, sysbuild | as A and B | **not built** | none | none | As B | in source |
| V1 | Virtual eFuse in RAM, bootloader | `-Dmcuboot_CONFIG_ESP32_EFUSE_VIRTUAL=y` | success | 42 560 B | 5 952 B (83.04 %) | Same size as base: the symbol adds no code to the bootloader by itself, because nothing in it uses secure features | built |
| V2 | Virtual eFuse kept in flash, bootloader | V1 plus `-Dmcuboot_CONFIG_ESP32_EFUSE_VIRTUAL_KEEP_IN_FLASH=y` | success | 43 616 B (+1 056 B) | 5 964 B (83.20 %) | `OFFSET=0x10000`, `SIZE=0x2000` taken from `sys_partition` | built |
| B1 | Application flash-encryption compatibility, plus V2 on both images | `-Dmcuboot_DTC_OVERLAY_FILE` and `-Dshell_DTC_OVERLAY_FILE` with `&flash0 { write-block-size = <32>; };`, `-Dshell_CONFIG_ESP_FLASH_ENCRYPTION=y`, V2 options on `mcuboot_` and `shell_` | success | 43 648 B | 5 964 B (83.20 %) | App `zephyr.signed.bin` 776 986 B (709 595 B without the option, +67 391 B). Both images show `write-block-size = <0x20>` in `zephyr.dts`. **This does not encrypt anything**: the bootloader has no encryption code. It only proves the application and overlay parts build | built |
| S0 | Espressif port, C3, EC256 signing only (no secure features) | `cmake -DMCUBOOT_TARGET=esp32c3 -DESP_HAL_PATH=<west hal_espressif>`, toolchain from Zephyr SDK `riscv64-zephyr-elf-gcc` | **failed at configure** | none | none | First: `Unsupported HAL version 6.2.0, expected 6.0.0`. After a temporary edit of the version check in the scratch workspace copy (since restored): `Cannot find source file .../components/log/src/noos/log_timestamp.c`; also missing `components/esp_security/src/esp_crypto_lock.c` and `esp_crypto_periph_clk.c`. The Zephyr HAL has no `log` and no `esp_security` component | built |

Image size warning of MCUboot issue 1262: **not seen** in any of the builds that ran (searched the logs for "exceed", "too large", "overflow", "size limit"). That says nothing about issue 1262, because no build had secure boot or encryption in the bootloader. (built; the question stays open)

Other warnings seen in sysbuild logs, not related to this work: use of the default signing key when the key option was quoted wrongly (my own command error, repeated and corrected), and `TEST_RANDOM_GENERATOR` "Not secure symbol". (built)

## 4. What this means
- **There is no supported way, in Zephyr v4.5.0 sysbuild, to turn on secure boot v2 or flash encryption in the bootloader.** The bootloader that sysbuild builds is the Zephyr-app MCUboot, which has neither feature. (built for secure boot; in source for flash encryption)
- The only documented route is the **standalone Espressif port** (`boot/espressif`), which expects an ESP-IDF-style HAL of version 6.0.0. The Zephyr `hal_espressif` module (6.2.0, trimmed) cannot build it. (built)
- That route means a **second bootloader build chain** in the product: ESP-IDF (or `esp-hal-3rdparty`) checkout, Espressif toolchain or a compatible one, a fixed HAL version, outside west/sysbuild. This affects the build reproducibility, SBOM and CRA evidence for ADR-0007 and ADR-0008, and the sacrificial-kit plan in RISK-022. (inference from the built results; the effect on those documents is not yet assessed)
- Virtual eFuse can be switched on for Zephyr applications and for the Zephyr-app MCUboot, but without secure-boot code in the bootloader it has no function there. The partial report's idea "rehearse secure boot with virtual eFuses" holds **only** for the Espressif port (whose readme lists the same options). (built; in source)
- The 32-byte write block overlay and `ESP_FLASH_ENCRYPTION` for the application build with MCUboot signing and sysbuild. (built)

## 5. What is still open
1. **Standalone port build.** I tried it and stopped: a full ESP-IDF v6.0 checkout (a Git clone of `espressif/esp-idf`, about 344 MB) was needed. I cloned it into the scratchpad, but the build step that uses it was **denied by the session's permission check** (code from an external source), so I did not use it. Not built: A, B, C in the Espressif port, loader segment size, ROM size limit (issue 1262), the image size warning. Needs a decision from the user: allow a build against a pinned ESP-IDF v6.0.x clone (or `esp-hal-3rdparty`), or accept that the Zephyr route does not offer these features. (unknown)
2. Whether a newer or later Zephyr/MCUboot revision brings Kconfig for these features into the Zephyr-app MCUboot. Not searched beyond the pinned v4.5.0 workspace and MCUboot 2.5.0. (unknown)
3. Whether the Zephyr-built MCUboot can verify the Zephyr app image when the standalone port is the bootloader, with the same flash map (slot offsets, `sys` partition at 0x10000 against the port's `bootloader.conf` virtual eFuse offset 0x10000). Both use 0x10000 for the virtual eFuse; the port's 0xF000 bootloader size fits below it. Not tested. (in source for the numbers; unknown for behavior)
4. Swap mode with encryption and `CONFIG_ESP_MCUBOOT_ERASE_PROGRESSIVELY`: belongs to the port; not tested. (unknown)
5. Chip revision of the dev kit (at least v0.3 needed for secure boot v2). Needs hardware. (unknown)
6. A `sysbuild/mcuboot.conf` file instead of `-D` options: not tried; expected to be equivalent. (unknown)
7. Everything that needs hardware: first-boot behavior, upgrade with a 32-byte write block, plaintext OTA path. Not run, by design.

## 6. Suggested next steps (for the owner to decide)
- Record in ADR-0007 that the Zephyr sysbuild bootloader has no secure boot or flash encryption, and that the options exist only in the Espressif port with an ESP-IDF 6.0.x HAL.
- Allow the standalone port build (open item 1) with a pinned ESP-IDF, to get the real size numbers for A, B, C.
- Re-assess the stage 2 plan in the spike if the second build chain is not acceptable.
