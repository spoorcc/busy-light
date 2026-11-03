# Spike 7.1, E2b: size ladder of a product-like throw-away image

- **Status:** Draft (author's record; no goldfish or owner review)
- **Date:** 2026-11-03
- **Plan:** `docs/plans/03-spike-7-1-zephyr-esp32c3.md`, experiment E2b (size proxy only)
- **What was done:** eight cumulative builds on the PC of a throw-away application. **Nothing was flashed, no hardware was used, nothing was run.** The code only has to compile and link; it is not correct and was not executed. All values are labelled **built** (measured by the build tools) or **unknown**.
- **Evidence class:** build output on the author's machine. Raw logs are in the session scratchpad (`build/e2b_s1.log` to `e2b_s8.log`) and are not kept in the repository. The throw-away code stays in the scratchpad (`spike_e2b/`) and is described below, not copied.

## Environment
| Item | Value | Label |
|------|-------|-------|
| Zephyr / SDK / toolchain | v4.5.0, Zephyr SDK 1.0.1, `riscv64-zephyr-elf` GCC 14.3.0 | built |
| Workspace | same scratchpad west workspace as `spike-7-1-e1-build.md` | built |
| Board / build mode | `esp32c3_devkitm`, `--sysbuild`, `-p always`, one build directory per step (`e2b_s1` to `e2b_s8`) | built |
| MCUboot | 2.5.0, swap using offset (`CONFIG_BOOT_SWAP_USING_OFFSET=y`), `CONFIG_BOOT_SIGNATURE_TYPE_ECDSA_P256=y`, spike-only key (not a product key) | built |
| Bootloader image | 42 560 B in every step (`zephyr.bin`) | built |
| Optimisation | Zephyr default for the app (`CONFIG_SIZE_OPTIMIZATIONS`/default; not tuned) | built (default not changed) |

## Method
1. One application, `spike_e2b`, with one source file. Each feature is guarded by an application Kconfig integer `E2B_STEP` (1 to 8). Each step adds a Kconfig fragment and the matching code on top of the earlier steps (cumulative).
2. The code references each API so the linker keeps it. I checked with `nm` on the linked ELF that these symbols are present in the step that adds them: `http_client_req`, `zsock_getaddrinfo`, `json_obj_parse`, `net_dhcpv4_server_start`, `ws2812_spi_0_cfg` and `spi_esp32_transceive`, `nvs_write`, `settings_save_one`, `psa_export_public_key`, `tls_credential_add`, `esp32_wifi_ap_enable`, `net_mgmt_NET_REQUEST_WIFI_AP_ENABLE` (all **built**).
3. Common base (all steps): IPv4 only (IPv6 off), TCP/UDP, BSD sockets, connection manager, DHCPv4 client, `CONFIG_WIFI_ESP32`, `NET_L2_WIFI_MGMT`, Zephyr `http_server` with the HTTP parser, POSIX API and eventfd (needed by the http_server), `LOG` with default level 2 (warning), **shell off** (`CONFIG_SHELL=n`), random source `TEST_RANDOM_GENERATOR` (insecure, throw-away only).
4. Reported values: size of `zephyr.signed.bin` (includes the MCUboot header and the ECDSA signature/TLV), the linker's `FLASH` line, and the `iram0_0_seg` and `dram0_0_seg` lines of the app link.
5. Percentages of the slot use the default slot of 1 835 008 B (1792 KiB) and the SYS-026 working limit of 75 % = 1 376 256 B from `spike-7-1-e2a-flash-budget.md` (arithmetic).

### What the steps contain
| Step | Added | Code that references it (throw-away) |
|------|-------|---------------------------------------|
| 1 | Wi-Fi station + soft AP, net stack, HTTP server without TLS | `NET_REQUEST_WIFI_CONNECT` on the default interface, `NET_REQUEST_WIFI_AP_ENABLE`, `http_server_start()`, one static and one dynamic resource |
| 2 | TLS server (Mbed TLS with PSA, socket TLS, credentials) | `HTTPS_SERVICE_DEFINE`, `tls_credential_add` for certificate and key |
| 3 | TLS client | HTTPS GET with `http_client_req` over a TLS socket, `zsock_getaddrinfo`, `DNS_RESOLVER` |
| 4 | JSON | `json_obj_parse` and `json_obj_encode_buf` of a struct with a string, a number and a bool |
| 5 | DHCPv4 server | `net_dhcpv4_server_start` on the AP interface |
| 6 | LED strip | `led_strip_update_rgb`, 16 pixels, `worldsemi,ws2812-spi` node on `&spi2` (the C3's general-purpose SPI) via a devicetree overlay |
| 7 | Settings on NVS | `settings_subsys_init`, `settings_load`, `settings_save_one`; `CONFIG_FLASH`, `FLASH_MAP`, `NVS`, `SETTINGS_NVS` |
| 8 | PSA EC P-256 key creation | `psa_generate_key` and `psa_export_public_key` (SECP R1 256, sign/hash use) |

## Size ladder
All values **built**. `Signed image` is `zephyr.signed.bin` in bytes.

| Step | Signed image (B) | FLASH (B) | FLASH % of 4 MB region | % of default slot | % of 75 % limit | iram0_0_seg (B / 360 208) | dram0_0_seg (B / 360 208) | dram0 % |
|------|------------------|-----------|------------------------|-------------------|-----------------|----------------------------|----------------------------|---------|
| 1 Wi-Fi STA+AP, net, HTTP (no TLS) | 586 315 | 586 036 | 13.97 | 32.0 | 42.6 | 50 656 | 196 800 | 54.64 |
| 2 + TLS server | 657 434 | 657 156 | 15.67 | 35.8 | 47.8 | 50 656 | 272 272 | 75.59 |
| 3 + TLS client | 657 675 | 657 396 | 15.67 | 35.8 | 47.8 | 50 656 | 277 888 | 77.15 |
| 4 + JSON | 658 124 | 657 844 | 15.68 | 35.9 | 47.8 | 50 656 | 277 888 | 77.15 |
| 5 + DHCPv4 server | 658 172 | 657 892 | 15.69 | 35.9 | 47.8 | 50 832 | 279 776 | 77.67 |
| 6 + LED strip (SPI ws2812, 16 px) | 659 355 | 659 076 | 15.71 | 35.9 | 47.9 | 50 832 | 280 608 | 77.90 |
| 7 + settings/NVS | 792 107 | 791 828 | 18.88 | 43.2 | 57.6 | 54 656 | 285 056 | 79.14 |
| 8 + PSA EC P-256 key creation | 792 107 | 791 828 | 18.88 | 43.2 | 57.6 | 54 656 | 285 056 | 79.14 |

Reading (arithmetic on the numbers above, **built** inputs):
- The final throw-away image is 792 107 B (773.6 KiB), 43.2 % of the default slot, 57.6 % of the 75 % limit (1344 KiB). Margin to the 75 % limit: 584 149 B (570 KiB).
- The ADR-0007 upper estimate of 1.5 MB is not reached by this proxy; the proxy is about half of it. See "What is not known" before relying on this.
- Step 8 adds nothing: once the TLS server is on, the PSA crypto code with ECC key-pair generation is already linked (symbols `psa_generate_key` and `psa_export_public_key` present in the step 8 ELF).
- Steps 3 to 6 add less than 2 KB each, because the TLS client, JSON, DHCP server and the SPI LED driver are small or share code with the server side. Step 2 (TLS server) costs about 71 KB flash and about 75 KB static RAM (the Mbed TLS heap, see below).
- Step 7 costs 132 752 B of flash, much more than expected. A coarse look at the linker map (per-object sizes, which include debug-section noise) shows the NVS, flash driver (`flash_esp32`), `flash_map`, `flash_util` and `settings` objects as the largest additions. The exact cause was **not analysed** (unknown). It is worth a separate look because it is the biggest single step after TLS.

## Free static RAM (estimate)
- `dram0_0_seg` is 360 208 B. Used at step 8: 285 056 B. Free static: **75 152 B** (arithmetic from linker output, **built**).
- That static figure already contains two heaps reserved at link time: the Mbed TLS heap (`CONFIG_MBEDTLS_HEAP_SIZE=60000`) and the kernel heap (`K_HEAP_MEM_POOL_SIZE=56384` in the compile flags, derived from `HEAP_MEM_POOL_SIZE=16384` plus additions by the subsystems). **Whether the linker counts them in `dram0_0_seg` was not separately verified** (unknown); the 75 KB jump at step 2 matches the 60 000 B Mbed TLS heap, which indicates it is counted.
- The Wi-Fi blob buffers (`CONFIG_ESP32_WIFI_*` defaults: 10 static RX buffers, 32 dynamic RX, 32 dynamic TX, 32 management buffers) and the stacks are partly allocated at run time. How much heap the Wi-Fi driver, `wpa_supplicant`, the net stack and TLS handshakes really use at run time is **unknown**. No run-time heap measurement exists.

## Build problems
| # | Symptom (short) | Cause | Fix | Label |
|---|-----------------|-------|-----|-------|
| 1 | `attempt to assign the value '24' to the undefined symbol ZVFS_OPEN_ADD_SIZE_NET_SAMPLE`; Kconfig warnings are errors | Symbol exists only in a Zephyr sample's own Kconfig | Removed from `prj.conf` | built |
| 2 | `operator '>=' has no left operand` in `main.c` | Sysbuild does not forward an arbitrary `-D` variable to the app (`-Dspike_e2b_E2B_STEP=n` did not arrive) | Made `E2B_STEP` an application Kconfig symbol, set by a generated fragment per step | built |
| 3 | `static assertion failed: "TLS is required for HTTP secure"` | `main.c` used `HTTPS_SERVICE_DEFINE` in step 1 because the step macro was empty (cause 2) | Fixed by 2 | built |
| 4 | `'TLS_CREDENTIAL_SERVER_CERTIFICATE' undeclared` | Wrong constant name in v4.5.0 | Use `TLS_CREDENTIAL_PUBLIC_CERTIFICATE` | built |
| 5 | Linker: `undefined reference` to `_http_resource_desc_web_list_start` / `_list_end` | The http_server needs an iterable linker section per service; Zephyr does not create it from the service name | Added `zephyr_linker_section(NAME http_resource_desc_web KVMA RAM_REGION GROUP RODATA_REGION)` and a `sections-rom.ld` with `ITERABLE_SECTION_ROM(http_resource_desc_web, ...)` (as in `samples/net/sockets/http_server`) | built |
| 6 | `attempt to assign ... undefined symbol NET_SOCKETS_POSIX_NAMES` | Symbol does not exist in v4.5.0 | Removed | built |

Features that failed to build and stayed failed: **none**. Every step 1 to 8 linked and produced a signed image. The sysbuild passes the application-specific files through `-Dspike_e2b_EXTRA_CONF_FILE` and `-Dspike_e2b_DTC_OVERLAY_FILE`; plain `-DEXTRA_CONF_FILE` is not enough with `--sysbuild` (built).

Build warnings seen in the last build (step 8): the insecure `TEST_RANDOM_GENERATOR` is enabled (expected, throw-away only; the product needs a real entropy source, see the E-series for the C3 TRNG), and a `MCUBOOT_UPDATE_FOOTER_SIZE` assignment warning (not analysed, unknown meaning for the product).

## Kconfig that mattered
Values as set in the throw-away image. Whether each value is *right* for the product is unknown.

| Option | Value | Why / effect | Label |
|--------|-------|--------------|-------|
| `CONFIG_MBEDTLS_HEAP_SIZE` (with `MBEDTLS_ENABLE_HEAP`) | 60000 | Copied from the Zephyr `http_server` TLS overlay. It is reserved statically and caused the +75 KB RAM at step 2. Whether 60 000 B is enough (or too much) for two concurrent TLS sessions is unknown | built (size effect); unknown (adequacy) |
| `CONFIG_MBEDTLS_SSL_IN_CONTENT_LEN` / `OUT_CONTENT_LEN` | 2048 / 2048 | Smaller TLS record buffers than the 16 KiB default. A peer that sends larger records (a public HTTPS server) may fail; not tested | built (set); unknown (effect) |
| `CONFIG_NET_SOCKETS_SOCKOPT_TLS` | y | Needed by `HTTPS_SERVICE_DEFINE` (BUILD_ASSERT) | built |
| `CONFIG_NET_SOCKETS_TLS_MAX_CONTEXTS` | 4 | Concurrent TLS sockets (server clients plus client) | built (set); unknown (adequacy) |
| `CONFIG_TLS_CREDENTIALS`, `TLS_MAX_CREDENTIALS_NUMBER` | y, 5 | Credential store | built |
| `CONFIG_MBEDTLS_CIPHERSUITE_TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256` | y | Only an ECDSA suite is enabled (matches the product's EC key idea, ADR-0006/0008) | built |
| `CONFIG_PSA_WANT_KEY_TYPE_ECC_KEY_PAIR_DERIVE`, `MBEDTLS_PK_WRITE_C` | y | Taken from the sample overlay. In Mbed TLS 4.x the PSA crypto layer is always present | built |
| `CONFIG_MBEDTLS_PSA_KEY_SLOT_COUNT` | 16 | Sample uses 64; 16 was chosen without analysis | built (set); unknown (adequacy) |
| `CONFIG_PSA_WANT_*` (ECDSA, secp256r1, ECC key-pair generate/import/export, public key) in step 8 | y | Made explicit for key creation. No size change because the TLS server already enables them | built |
| `CONFIG_HEAP_MEM_POOL_SIZE` | 16384 | Kernel heap; the compile flags show the final `K_HEAP_MEM_POOL_SIZE=56384` | built |
| `CONFIG_MAIN_STACK_SIZE`, `SYSTEM_WORKQUEUE_STACK_SIZE` | 4096, 2048 | Set from the samples, not found by a link failure | built (set); unknown (adequacy) |
| `CONFIG_NET_TX_STACK_SIZE`, `NET_RX_STACK_SIZE` | 2048, 2048 | From the Wi-Fi shell sample; unverified | built (set); unknown (adequacy) |
| `CONFIG_NET_PKT_RX_COUNT` / `TX_COUNT`, `NET_BUF_RX_COUNT` / `TX_COUNT` | 16 / 16, 32 / 32 | Net buffers; guessed between the Wi-Fi shell (10/10, 20/20) and the http_server sample (16/16, 128/128). Part of dram | built (set); unknown (adequacy) |
| `CONFIG_NET_MAX_CONTEXTS` | 16 | Sockets and contexts | built (set) |
| `CONFIG_HTTP_SERVER_MAX_CLIENTS` | 2 | Concurrent HTTP clients | built (set) |
| `CONFIG_LOG`, `LOG_DEFAULT_LEVEL` | y, 2 | Modest logging; shell off | built |
| `CONFIG_NET_IPV6` | n | IPv6 off, smaller image | built (set); size effect not measured separately |
| `CONFIG_NET_DHCPV4_SERVER` (`ADDR_COUNT=4` default) | y | Adds a few hundred bytes of flash, about 1.9 KB dram | built |
| `CONFIG_LED_STRIP`, `SPI`; DT node `worldsemi,ws2812-spi` with `chain-length = <16>`, `spi-max-frequency = <6400000>`, one/zero frames 0xf0 / 0xc0 | y | ws2812 on `&spi2`, 16 pixels; adds about 1.2 KB flash. The SPI timing values are placeholders, not checked against the ws2812 timing | built (size); unknown (timing) |
| `CONFIG_FLASH`, `FLASH_MAP`, `NVS`, `SETTINGS`, `SETTINGS_NVS` | y | +132 KB flash at step 7 | built |
| `CONFIG_ZVFS_POLL_MAX=32`, `POSIX_API`, `EVENTFD` | y | Required by the http_server | built |

Heap and stack settings needed *to link*: **none**. Every heap and stack value above was set up front from the Zephyr samples, none was found by a link error. Whether they are large enough at run time is **unknown**.

## What is not known
All items are **unknown**:
- **Run-time heap use** of Wi-Fi (blob and `wpa_supplicant`), net stack, TLS (two server sessions plus one client session at the same time), JSON and the PSA key store. No run was done. The static free RAM of 75 152 B is not the run-time free RAM.
- Whether the image works at all: association, AP+STA operation, TLS handshake, HTTPS GET, LED output, NVS write. Nothing was run. In particular, the real AP+STA coexistence behaviour (one radio, one channel) is untested; only the calls link.
- Stack sizes for the threads (main, system workqueue, net, http_server, TLS handshake) have not been measured; handshakes with ECDSA are stack-hungry.
- The proxy omits product pieces that will add flash: the real web page and its assets, update upload and `mcumgr`/DFU handling, certificate and key handling code, the device key record, display or further drivers, WPA2-Enterprise (EAP, E12), the real logging strings, application logic, secure boot and flash encryption (E11a), and a real entropy source instead of `TEST_RANDOM_GENERATOR`. The 792 KB figure is therefore a **lower bound**, not an estimate of the product.
- Log level 2 with the `LOG` subsystem on is a modest setting; the effect of higher levels or of `LOG_MODE_MINIMAL` was not measured.
- The cause of the +132 KB at step 7 and whether it can be reduced (for example a different settings backend, or flash driver options) was not analysed.
- Whether the build is reproducible bit for bit, and the build time, were not recorded.
- Mbed TLS option set: only one cipher suite and TLS 1.2 style sockets were exercised in code; TLS 1.3, certificate chains with RSA and larger record sizes were not tried. A TLS client talking to a public server may need more options (and more flash/RAM).
- Security of the configuration: the throw-away uses a spike key and `TEST_RANDOM_GENERATOR`; none of it is a product design.

## Side effects
Only files in the session scratchpad (`spike_e2b/`, `build/e2b_s1` to `e2b_s8` and their logs) and this report were written. No git command was run in the repository.
