# Spike 7.1, E12 and E2b follow-up: WPA2-Enterprise headroom, step 7 cause, TLS RAM, Wi-Fi buffers

- **Status:** Draft (author's record; no goldfish or owner review)
- **Date:** 2026-11-04
- **Plan:** `docs/plans/03-spike-7-1-zephyr-esp32c3.md`, experiments E12 (WPA2-Enterprise) and follow-up to E2b (`spike-7-1-e2b-size-ladder.md`)
- **What was done:** 11 further PC builds of the throw-away E2b application, plus map and ELF analysis. **Nothing was flashed, no hardware was used, nothing was run.** The code only has to compile and link.
- **Labels:** every statement is marked **built** (measured from a build on this PC), **in source** (read in the Zephyr or HAL source, not proven by a build) or **unknown**.
- **Evidence class:** build output on the author's machine. Build directories `f12_ent1`, `f12_ent2`, `f12_ent3`, `f13_*` and logs are in the session scratchpad and are not kept in the repository.

## Environment
| Item | Value | Label |
|------|-------|-------|
| Zephyr / SDK / toolchain | v4.5.0, Zephyr SDK 1.0.1, `riscv64-zephyr-elf` GCC 14.3.0 | built |
| Board / mode | `esp32c3_devkitm`, `--sysbuild`, `-p always`, MCUboot ECDSA P-256 with the spike-only key | built |
| Baseline | E2b step 8 (cumulative steps 2 to 8): signed 792 107 B, FLASH 791 828 B, iram0 54 656 B, dram0 285 056 B of 360 208 B | built (rebuilt identically by the `f13_r1`..`f13_w2` builds when only a non-memory option changed) |
| Method | Same app and fragments as step 8, plus one extra fragment per build (`f12/*.conf`, scratchpad) | built |
| "Content" | Sum of the file sizes of the ELF LOAD segments (`readelf -l`). This is the real code and data in flash, without alignment padding | built |

## Part 1: E12, WPA2-Enterprise (EAP) on the ESP32 Wi-Fi driver

### Kconfig found
- `CONFIG_ESP32_WIFI_ENTERPRISE` in `zephyr/drivers/wifi/esp32/Kconfig.esp32` (line 751). It is the only option you must set. **In source**.
- It selects: `ESP32_WIFI_MBEDTLS_CRYPTO`, `WIFI_CERTIFICATE_LIB`, `MBEDTLS`, `MBEDTLS_PEM_PARSE_C`, `MBEDTLS_SSL_EXTENDED_MASTER_SECRET`, `MBEDTLS_SSL_KEYING_MATERIAL_EXPORT`, `MBEDTLS_SSL_SERVER_NAME_INDICATION`, `MBEDTLS_X509_CRL_PARSE_C`, `MBEDTLS_X509_CRT_PARSE_C`, and three ECDHE GCM/CBC cipher suites. **In source**, and the resulting `.config` confirms `ESP32_WIFI_MBEDTLS_CRYPTO=y`, `WIFI_CERTIFICATE_LIB=y` (**built**).
- Sub-options that default to `y` once enterprise is on: `ESP32_WIFI_ENTERPRISE_MBEDTLS_TLS_CLIENT`, `ESP32_WIFI_GCMP_SUPPORT`, `ESP32_WIFI_GMAC_SUPPORT`, `ESP32_WIFI_SUITE_B`, `ESP32_WIFI_BSS_MAX_IDLE_SUPPORT`. `ESP32_WIFI_SUITE_B_192` is off by default and would add SECP384R1 and AES-256 suites. **Built** (`.config`).
- Driver use: `esp_wifi_drv.c` compiles `esp32_wifi_enterprise_method()`, `esp32_wifi_configure_enterprise()` and the `enterprise_creds` management op under `#if defined(CONFIG_ESP32_WIFI_ENTERPRISE)`. It maps the Zephyr security types `WIFI_SECURITY_TYPE_EAP_*` (PEAP-MSCHAPv2, PEAP-GTC, TTLS-MSCHAPv2, PEAP-TLS and others) to `esp_eap_method_t`, then calls `esp_eap_client_set_identity/username/password/ca_cert/certificate_and_key`. Without the option the connect call returns `-EINVAL` with the log text "Enable CONFIG_ESP32_WIFI_ENTERPRISE". **In source**.
- With the option on, these symbols are in the linked ELF: `esp_eap_client_set_identity`, `_set_password`, `_set_ca_cert`, `_set_certificate_and_key`, `_set_eap_methods`, `eap_peer_peap_register`, `eap_peer_mschapv2_register`, `eap_peer_tls_*`, `esp32_wifi_enterprise_creds` (154 text symbols with "eap" in the name). **Built** (`nm`).
- Hostap route `CONFIG_WIFI_NM_WPA_SUPPLICANT_CRYPTO_ENTERPRISE` (`zephyr/modules/hostap/Kconfig`, line 317): **does not apply** to this driver. It belongs to the Zephyr hostap `wpa_supplicant` port, which is a separate Wi-Fi manager (`WIFI_NM_WPA_SUPPLICANT`, EXPERIMENTAL, selects `WIFI_NM`, `NOT_SECURE` for the crypto option). The ESP32 driver uses Espressif's own supplicant inside the HAL and, in this build, `WIFI_NM` and `WIFI_NM_WPA_SUPPLICANT` are off. Several ESP32 options even say `depends on !WIFI_NM_WPA_SUPPLICANT`. **In source**; I did not build the hostap route (**unknown** whether the two can be combined on the C3).

### Results table
All rows are cumulative on E2b step 8. `Signed` = `zephyr.signed.bin`.

| Build | Extra Kconfig on step 8 | Builds | Signed (B) | Delta signed (B) | Content (B) | Delta content (B) | FLASH (B) | iram0 (B) | dram0 (B) | Label |
|-------|--------------------------|--------|-----------|------------------|-------------|-------------------|-----------|-----------|-----------|-------|
| step 8 (baseline) | none | yes | 792 107 | 0 | 671 896 | 0 | 791 828 | 54 656 | 285 056 | built |
| `f12_ent1` | `ESP32_WIFI_ENTERPRISE=y` (defaults) | yes, rc=0 | 862 091 | +69 984 | 741 240 | +69 344 | 861 812 | 54 656 | 291 120 | built |
| `f12_ent3` | enterprise, with `SUITE_B`, `GCMP`, `GMAC`, `BSS_MAX_IDLE` set to `n` | yes, rc=0 | 862 076 | +69 969 | 739 368 | +67 472 | 861 796 | 54 656 | 291 120 | built |
| `f12_ent2` | as `ent3` and also `ESP32_WIFI_ENTERPRISE_MBEDTLS_TLS_CLIENT=n` | **no, link error** | none | none | none | none | none | none | none | built |

Reading (arithmetic on **built** values):
- Enterprise support costs about **+69 KB real content** (+69 344 B) and **+6 064 B dram0** (about 2 percentage points of dram0). iram0 does not change.
- The signed-image delta (+69 984 B) is close to the content delta in this case. The signed image is quantised in 64 KiB steps (see Part 2a), so it can jump differently in other builds.
- New total: 862 091 B = 47.0 % of the default slot of 1 835 008 B and 62.6 % of the 75 % limit (1 376 256 B). Margin to the limit: 514 165 B. Arithmetic.
- Turning off Suite-B, GCMP, GMAC and BSS max idle saves only 1 872 B content. Not worth the loss of WPA3-Enterprise.
- The `WIFI_MGMT_BSS_MAX_IDLE_TIME=300` option stays in `.config` after `BSS_MAX_IDLE_SUPPORT=n`. Meaning not analysed (**unknown**).

### Error found
`f12_ent2` (TLS client backend off) fails at link time: `undefined reference to base64_decode` from `components/wpa_supplicant/src/tls/tlsv1_cred.c` (`tlsv1_add_cert`, `tlsv1_set_private_key`). So `ESP32_WIFI_ENTERPRISE_MBEDTLS_TLS_CLIENT` must stay `y` (the default) in this Zephyr and HAL version. The missing symbol is a HAL function, not a binary blob symbol. **Built**. Cause not analysed (**unknown**).

No missing blob symbols were seen in the two successful enterprise builds. **Built**. Other warnings in the enterprise build are the same as in step 8 (`TEST_RANDOM_GENERATOR`, `MCUBOOT_UPDATE_FOOTER_SIZE`).

Not covered by E12 (**unknown**): whether the code works at run time (EAP-PEAP/TTLS/TLS handshake against a RADIUS server), the run-time heap and stack the EAP-TLS handshake needs (it uses mbedTLS and the shared mbedTLS heap of 60 000 B, so a concurrent web-server TLS session may compete), RSA support (the enterprise selects RSA ECDHE suites but the throw-away has no RSA verification test), CA and client certificate storage size and how the product stores them.

## Part 2a: cause of the +132 KB at step 7

### Finding
**The +132 752 B is mostly alignment padding in the ESP image, not code.** Real content grew by 14 424 B only. **Built**.


| Quantity | Step 6 | Step 7 | Delta | Label |
|----------|--------|--------|-------|-------|
| Content, sum of LOAD segment file sizes (B) | 655 456 | 669 880 | +14 424 | built |
| `zephyr.bin` (B) | 659 204 | 791 956 | +132 752 | built |
| Signed (B) | 659 355 | 792 107 | +132 752 | built |
| Padding (bin minus content), B | 3 748 | 122 076 | +118 328 | built (arithmetic) |
| Load address of the code (`.text`, irom) segment | 0x010000 | 0x020000 | +64 KiB | built |
| Load address of the read-only data (drom) segment | 0x090000 | 0x0B0000 | +128 KiB | built |

(Offsets are the physical/load addresses of the LOAD segments in `readelf -l`: .text at 0x10000 in step 6 and 0x20000 in step 7; read-only data at 0x90000 and 0xb0000. The filler segment before `.text` is 0x34 B in step 6 and 0xef5c B in step 7.)

Mechanism (**in source**, from the linker layout, consistent with the **built** map and segment table): the ESP32-C3 maps flash through the MMU in 64 KiB pages. The code segment and the read-only data segment must start at a flash offset that matches their virtual address modulo 64 KiB. The RAM-resident segments (iram/dram initialised data) are stored first. At step 7 they grew past the 0x10000 boundary (end at 0x110a4), so the code segment moved to the next page, 0x20000, which wastes 0x0ef5c (61 276 B) of filler. Then `.text` ended at 0xa1290, just after a page boundary, so the read-only data had to start at 0xb0000 and the filler `.flash.dummy` grew to 0xed70 (60 784 B). Together this is about 118 KB of zero filler. The staircase therefore moves in steps of up to 64 KiB, twice, for a small real change.

Why the earlier ladder looks uneven (arithmetic on **built** values): content grows smoothly (for example +6 832 B from step 3 to step 4) while the signed size jumps only when a 64 KiB boundary is crossed. The sizes in `spike-7-1-e2b-size-ladder.md` therefore carry up to about 2 x 64 KiB of layout noise, and the content column is the better measure of real growth. I did not check the other steps for padding jumps one by one (**unknown**).

Consequence for budgets: a flash budget should add up to about 128 KB for this padding, or read the content figure. The padding is inside the signed image, so it uses slot space. Whether the application can avoid it with a linker or partition change is **unknown**; I did not try it.

### What step 7 really adds
Per-symbol difference between the ELFs of step 6 and 7 (`nm -S`, 155 changed symbols, net +12 765 B of symbols; the rest of the +14 424 B is alignment and section overhead). **Built**.

| Group | Delta (B) | Largest members | Label |
|-------|-----------|-----------------|-------|
| ESP flash driver, MMU and cache (`esp_mmu_map_virt` 1 604, `esp_flash_erase_region`, `esp_flash_write*`, `esp_flash_read*`, `spi_flash_mmap`, `esp_mmu_unmap`, cache freeze/intr functions) | +5 704 | these come from the HAL via `flash_esp32` | built |
| NVS (`nvs_mount` 828, `nvs_gc` 704, `nvs_write` 496, ATE helpers) | +3 792 | | built |
| Settings core and NVS backend (`settings_nvs_save/load`, `settings_commit_subtree`, name parsing) | +1 925 | | built |
| flash_map / flash API (`default_flash_map`, `flash_area_open`, page info) | +576 | | built |
| Other | +768 | `crc8_ccitt` 66 | built |

So what pulls the code in: the flash driver (`CONFIG_FLASH` with `flash_esp32`, from the HAL `esp_flash` and `esp_mmu`) is the largest part (45 %), then NVS (30 %), then settings (15 %). No crypto, filesystem, FCB or ZMS code is involved. **Built**.

### Lighter settings backend
Same app, step 7 fragment replaced. The only valid comparison is content, because the signed size is quantised.

| Backend | Kconfig | Content (B) | Delta vs NVS (B) | Signed (B) | dram0 (B) | Label |
|---------|---------|-------------|------------------|-----------|-----------|-------|
| NVS (`f13` not rebuilt; step 8) | `NVS`, `SETTINGS_NVS` | 671 896 | 0 | 792 107 | 285 056 | built |
| ZMS (`f13_zms`) | `ZMS`, `SETTINGS_ZMS` | 674 328 | +2 432 | 792 491 | 285 088 | built |
| FCB (`f13_fcb`) | `FCB`, `SETTINGS_FCB` | 671 712 | -184 | 791 995 | 285 136 | built |

Reading: the three backends are within about 2.5 KB of each other. Changing the backend does not remove the cost. Step 6 content is 655 456 B and the three step-8 variants are 671 7xx to 674 3xx B, so settings plus the 2 KB of PSA key code is the whole difference. The floor for any flash-backed store is the ESP flash driver (about 5.7 KB in the table above) plus `flash_map`. A custom record store on the same flash driver would save at most the NVS and settings parts (about 5.7 KB combined), minus its own code. I did not build a custom store (**unknown**). Not tested: wear, power-loss safety, retention of keys and credentials. The backend choice also changes the on-flash format and the update path, so it is an ADR question, not a size question.

## Part 2b: TLS static RAM
Static RAM for TLS is the mbedTLS heap (`MBEDTLS_HEAP_SIZE`, linked into dram0). The record buffers (`MBEDTLS_SSL_IN/OUT_CONTENT_LEN`) are taken from that heap at run time per session, so they change the needed heap, not the static size, except through the heap size you choose. **In source** (heap size is the only static item; the dram0 deltas below match the heap changes exactly in `f13_r1`).

Options found: `CONFIG_MBEDTLS_HEAP_SIZE`, `CONFIG_MBEDTLS_SSL_IN_CONTENT_LEN`, `CONFIG_MBEDTLS_SSL_OUT_CONTENT_LEN` (the older `MBEDTLS_SSL_MAX_CONTENT_LEN` still exists; 0 = use the IN/OUT values), `MBEDTLS_SSL_MAX_FRAGMENT_LENGTH`, `MBEDTLS_SSL_VARIABLE_BUFFER_LENGTH`, `CONFIG_NET_SOCKETS_TLS_MAX_CONTEXTS`, `NET_SOCKETS_TLS_MAX_SESSION_CONTEXTS`, `TLS_MAX_CREDENTIALS_NUMBER`, `MBEDTLS_PSA_KEY_SLOT_COUNT`. **In source** (`zephyr/modules/mbedtls/Kconfig.mbedtls`, `zephyr/subsys/net/lib/sockets/Kconfig`).

| Build | Change from step 8 | Builds | dram0 (B) | dram0 % | Delta dram0 (B) | FLASH (B) | Signed (B) | Content (B) | Label |
|-------|--------------------|--------|-----------|---------|-----------------|-----------|-----------|-------------|-------|
| step 8 | heap 60 000; IN/OUT 2048/2048; TLS contexts 4; PSA slots 16; credentials 5 | yes | 285 056 | 79.14 | 0 | 791 828 | 792 107 | 671 896 | built |
| `f13_r1` | heap 40 000 | yes | 265 056 | 73.58 | -20 000 | 791 828 | 792 107 | 671 896 | built |
| `f13_r2` | heap 30 000; IN/OUT 1024/1024; TLS contexts 2; session contexts 2 | yes | 251 824 | 69.91 | -33 232 | 791 828 | 792 107 | 671 784 | built |
| `f13_r3` | heap 20 000; IN/OUT 1024/1024; TLS contexts 1; session contexts 1; PSA slots 8; credentials 3 | yes | 239 856 | 66.59 | -45 200 | 791 828 | 792 107 | 671 720 | built |

Reading:
- Flash does not change (content moves by under 200 B). The whole gain is RAM: up to 45 200 B in `f13_r3`, which leaves 120 352 B free in dram0 (arithmetic from 360 208 - 239 856), against 75 152 B at step 8.
- The part not explained by the heap size alone in r2 (3 232 B) and r3 (5 200 B) comes from the per-context and key-slot tables. **Built** (sizes), cause by arithmetic and **in source** only.
- Part of dram0 shown is the kernel heap (56 384 B, see Part 2c). The same dram0 gain does not apply to run-time heap use of that.

**Do not read these as safe settings.** These builds link; they say nothing about whether a TLS 1.2 ECDSA handshake plus the HTTP server fits in 20 000 or 30 000 B, whether a peer that sends 16 KiB records works with 1024-byte buffers (the MFL extension, `MBEDTLS_SSL_MAX_FRAGMENT_LENGTH`, is on by default but works only if the peer honours it), or what happens with E12 enterprise TLS using the same heap. Run-time adequacy is **unknown**. Handshake peak heap needs a measurement on hardware (for example `mbedtls_memory_buffer_alloc_max_get` or the Zephyr heap stats).

## Part 2c: Wi-Fi driver static buffer options
Options in `zephyr/drivers/wifi/esp32/Kconfig.esp32` and the values in the step 8 `.config` (**built**):

| Option | Default / step 8 | Range | Source note | Label |
|--------|------------------|-------|-------------|-------|
| `ESP32_WIFI_STATIC_RX_BUFFER_NUM` | 10 | 2 to 25 | about 1.6 KB each, allocated at `esp_wifi_init`, always from the system (kernel) heap | in source |
| `ESP32_WIFI_DYNAMIC_RX_BUFFER_NUM` | 32 | 0 to 128 | allocated as frames arrive; frames are dropped if the heap is empty | in source |
| `ESP32_WIFI_DYNAMIC_TX_BUFFER` (type) / `_NUM` | dynamic / 32 | 1 to 128 | `STATIC_TX_BUFFER_NUM` (16, 1.6 KB each) only if static TX is chosen | in source |
| `ESP32_WIFI_RX_MGMT_BUF_NUM_DEF` | 5 | 1 to 10 | static RX management buffers | in source |
| `ESP32_WIFI_MGMT_SBUF_NUM` | 32 | 6 to 32 | management short buffers | in source |
| `ESP32_WIFI_AMPDU_TX/RX_ENABLED`, `TX_BA_WIN`, `RX_BA_WIN` | y, y, 6, 6 | 2 to 32 | docs say keep `STATIC_RX >= RX_BA_WIN` | in source |
| `HEAP_MEM_POOL_ADD_SIZE_ESP_WIFI` | 51 200 (hidden, not settable) | none | the minimum the driver adds to the kernel heap; covers the default buffer counts | built (`.config`), in source (default) |

How these reach dram0. The Wi-Fi buffers are not separate static arrays. They are allocated at run time from the Zephyr system heap. The system heap is a static array in dram0 of size max(`HEAP_MEM_POOL_SIZE`, sum of all `HEAP_MEM_POOL_ADD_SIZE_*`). In step 8 the sum is 51 200 (Wi-Fi) + 4 096 (board) + 280 + 296 + 256 + 256 = 56 384 B, which is above the 16 384 B set in `prj.conf`, so the final value is 56 384 B (compile flag `K_HEAP_MEM_POOL_SIZE=56384`). The Wi-Fi driver is therefore about 51 KB of the static dram0. **Built** (compile flag, `.config`) with the arithmetic checked.

| Build | Change from step 8 | Builds | dram0 (B) | Delta dram0 (B) | Warning in log | Label |
|-------|--------------------|--------|-----------|-----------------|----------------|-------|
| `f13_w1` | `STATIC_RX` 4, `DYNAMIC_RX` 16, `DYNAMIC_TX` 16, `MGMT_SBUF` 16 | yes | 285 056 | 0 | none | built |
| `f13_w2` | `STATIC_RX` 16, `DYNAMIC_RX` 64 | yes | 285 056 | 0 | "Heap too small for Wi-Fi RX buffers" (`drivers/wifi/esp32/CMakeLists.txt`) | built |
| `f13_w3` | `HEAP_MEM_POOL_IGNORE_MIN=y`, `HEAP_MEM_POOL_SIZE=32768` | yes | 261 440 | -23 616 | none (the minimum check is skipped) | built |

Reading:
- Changing the buffer counts does not change static dram0. The heap size does (w3: system heap 56 384 to 32 768 B, delta 23 616 B). **Built**.
- w2 shows that raising static RX buffers above 10 does not enlarge the heap by itself: the build only warns. With 16 static RX buffers the CMake check calls for about 9 600 B more heap (6 x 1 600). **Built** (warning), figure **in source**.
- w3 is not an advice. It removes the heap guard. With less heap than the driver's own minimum, buffer allocation can fail at run time: **unknown**. Real heap use of Wi-Fi, `wpa_supplicant` (internal), the net stack and sockets at run time was not measured.

## What is not known
All items **unknown**:
- Everything at run time: association, EAP handshakes, TLS handshake peak heap, web server load, concurrent TLS server and EAP client, NVS writes, Wi-Fi throughput with fewer buffers.
- Whether the 64 KiB padding (Part 2a) can be avoided by a partition or linker change, and whether the esp-idf image tool or MCUboot treats the padded gaps differently on the product build (secure boot, flash encryption, see E11a). This padding applies to the signed image used for slot sizing.
- Cause of the `base64_decode` link error in `f12_ent2` and whether any other enterprise sub-option combination fails.
- Whether the hostap route could work on the C3 at all.
- Size of a custom record store; size effect of `CONFIG_SETTINGS_NVS`/ZMS options such as sector count (left at defaults in these builds).
- Whether the ZMS or FCB layout meets the product's power-loss and wear requirements.
- Reproducibility bit for bit and build times were not recorded.
- Product extras still absent from the proxy: real web assets, DFU handling, certificate storage, secure boot and flash encryption (E11a), a real entropy source (the throw-away uses `TEST_RANDOM_GENERATOR`).

## Side effects
Only files in the session scratchpad (`f12/`, `build/f12_*`, `build/f13_*`, logs) and this report were written. No git command was run and no other repository file was edited. Nothing was flashed.
