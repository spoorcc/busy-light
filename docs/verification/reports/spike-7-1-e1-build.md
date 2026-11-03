# Spike 7.1, E1: first builds for the ESP32-C3 dev kit

- **Status:** Draft (author's record; no goldfish or owner review)
- **Date:** 2026-11-03
- **Plan:** `docs/plans/03-spike-7-1-zephyr-esp32c3.md`, experiment E1 (build part only)
- **What was done:** two builds on the PC. **Nothing was flashed, no hardware was used, no Wi-Fi association or LED output was tested.** The E1 pass rule ("joins a WPA2 network; LEDs show a test pattern") is therefore **not run**.
- **Evidence class:** build output, measured by the build tools on the author's machine. Raw logs are in the session scratchpad (`build_hello.log`, `build_wifishell.log`) and are not kept in the repository.

## Environment (exact)
| Item | Value |
|------|-------|
| Manifest | `sw/west.yml` at commit `de34f23` (Zephyr `v4.5.0`) |
| Workspace | west 1.5.0, created in the scratchpad; project filter: zephyr, hal_espressif, mcuboot, mbedtls, hostap, psa-arch-tests, tf-psa-crypto; shallow clones |
| Toolchain | Zephyr SDK 1.0.1 (minimal) with `riscv64-zephyr-elf` only; GCC 14.3.0, binutils 2.43.1 |
| Host | Linux x86_64, Python 3.14.7, CMake 4.4.4 |
| Python packages | Zephyr `requirements` via `west packages pip --install` (includes esptool 5.6.0, imgtool 2.5.0) |
| Blobs | `west blobs fetch hal_espressif` (all chips' Espressif binary blobs were fetched; the C3 ones are the ones used) |
| Board | `esp32c3_devkitm` with `--sysbuild` (MCUboot is the default bootloader) |
| Mbed TLS / MCUboot | 4.1.1 (PSA-based, TF-PSA-Crypto module needed) / 2.5.0 |

Finding while setting up: the project filter I first used left out `tf-psa-crypto`, and the build failed ("TF-PSA-Crypto target tfpsacrypto does not exist"). The module is required by Mbed TLS 4 in this release. Also `esptool` must be installed (the build refuses to configure without `esptool>=5.0.2`).

## Results
| Build | Result | Application image (`zephyr.signed.bin`) | Bootloader (`zephyr.bin`) | Notes |
|-------|--------|------------------------------------------|----------------------------|-------|
| `samples/hello_world` | **Built** | 134 564 B | 47 680 B | Image 3.20 % of the 4 MB flash region used by the linker |
| `samples/net/wifi/shell` | **Built** | 709 780 B | 47 680 B | FLASH 709 316 B (16.91 %); `dram0_0_seg` 183 840 B of 360 208 B (51.04 %); `iram0_0_seg` 50 544 B (14.03 %) |

## Default flash layout of the board (from the generated devicetree, `partitions_0x0_default_4M.dtsi`)
| Partition | Offset | Size |
|-----------|--------|------|
| `mcuboot` | 0x0 | 0x10000 (64 KiB) |
| `sys` | 0x10000 | 0x10000 (64 KiB) |
| `image-0` (primary slot) | 0x20000 | 0x1c0000 (1 835 008 B = 1.75 MiB) |
| `image-1` (secondary slot) | 0x1e0000 | 0x1c0000 (1.75 MiB) |
| `image-0-lpcore`, `image-1-lpcore` | 0x3a0000, 0x3a8000 | 0x8000 each (not used by the C3) |
| `storage` | 0x3b0000 | 0x30000 (192 KiB) |

Derived (arithmetic on the numbers above, not measured): the two slots take 3.5 MiB of the 4 MiB. The Wi-Fi shell image (709 780 B) is 38.7 % of one slot. SYS-026's working limit of 75 % of the slot would be 1 376 256 B. These are the defaults; the real layout is an E2 / ADR-0007 decision (the `lpcore` areas are unused and could be reclaimed).

## Build defaults that matter (read from the generated `.config` of the MCUboot image)
- Signature: **RSA-2048** with MCUboot's public sample key `root-rsa-2048.pem` from the MCUboot repository. This is a **well-known development key**: images signed with it are not protected. The product uses ECDSA P-256 with its own keys (ADR-0007); the default must be replaced and never shipped.
- Swap mode: **swap using offset** (`CONFIG_BOOT_SWAP_USING_OFFSET`).
- The Wi-Fi shell sample is a shell/logging test image. Its size is **not representative** of the product (no HTTP server, no TLS, no JSON, no display code), and it does not use AP+STA.

## What this shows and does not show
- Shows: v4.5.0, the SDK and the blobs build for `esp32c3_devkitm` on this machine; the MCUboot sysbuild path works; a Wi-Fi-enabled image fits a default slot with a wide margin.
- Does not show: that the image runs, that Wi-Fi works, anything about AP mode, AP+STA, TLS, the HTTP server, `led_strip` or timing. Those need the dev kit (E1 run part, E3 onward).
- The product-like image will be much larger than 710 KB. The first realistic size comes from E2b.

## Side effects on the author's machine
`west zephyr-export` registered the scratchpad workspace in the user CMake package registry (`~/.cmake/packages/Zephyr/14589fc7...`). That path points into a temporary directory; remove the file when the scratchpad is deleted. No other files outside the scratchpad and the repository were changed.

## Next steps (not done)
1. Run part of E1 on the dev kit: flash, join a WPA2 network, drive a 16-LED ring with the SPI `ws2812` driver (needs the owner's hardware and approval of plan 03).
2. E2a on paper with the defaults above; E2b after the product-like image exists.
3. Rebuild with `CONFIG_BOOT_SIGNATURE_TYPE_ECDSA_P256` and a spike key to check size and the E11a questions. Done in the E11a record.
