# Spike 7.1, E2a: paper flash budget for the 4 MB ESP32-C3

- **Status:** Draft (author's analysis; no goldfish or owner review)
- **Date:** 2026-11-03
- **Plan:** `docs/plans/03-spike-7-1-zephyr-esp32c3.md`, experiment E2a (paper part)
- **Evidence class:** arithmetic on numbers from the generated devicetree of the E1 build (`spike-7-1-e1-build.md`) and on estimates from the ADRs. No product-like image exists yet, so the image sizes in the scenarios are **not measurements**. The result is a **break-even size**, not a verdict.
- **Requirement basis:** SYS-026 (working limit: image at most [75] % of one slot, settings and certificate area at least [25] % free), SYS-029 (two slots, return to the previous image), ADR-0007.

## Default layout of `esp32c3_devkitm` (4 MiB = 4096 KiB), from the E1 build
| Partition | Offset | Size (KiB) |
|-----------|--------|-----------|
| `mcuboot` | 0x000000 | 64 |
| `sys` | 0x010000 | 64 |
| `image-0` | 0x020000 | 1792 |
| `image-1` | 0x1e0000 | 1792 |
| `image-0-lpcore`, `image-1-lpcore` (unused on the C3) | 0x3a0000 | 64 (2 x 32) |
| `storage` | 0x3b0000 | 192 |
| **Not assigned** | 0x3e0000 to 0x3fffff | **128** |
Sum of the assigned areas: 3968 KiB. The default layout leaves 128 KiB unassigned at the end of the flash.

## Slot size that is possible
Slot size S = (4096 - bootloader - sys - storage - other) / 2, and the SYS-026 working limit for the image is 0.75 x S. The swap mode "swap using offset" (E1 default) needs the secondary slot to be one flash sector (4 KiB) larger than the image *(to verify in E9; not included below)*.

| Layout | Bootloader | sys | storage | other | Slot S (KiB) | Image limit at 75 % (KiB) |
|--------|-----------|-----|---------|-------|--------------|---------------------------|
| Default as shipped | 64 | 64 | 192 | 64 (lpcore) + 128 (unassigned) | 1792 | 1344 |
| lpcore and unassigned space reclaimed | 64 | 64 | 192 | 0 | 1888 | 1416 |
| Storage 128 KiB | 64 | 64 | 128 | 0 | 1920 | 1440 |
| `sys` dropped (if virtual eFuses and NVS are not needed) | 64 | 0 | 192 | 0 | 1920 | 1440 |

**Break-even:** the application image must be at most about **1344 KiB (1.31 MiB)** in the default layout and about **1416 KiB (1.38 MiB)** with the free space reclaimed, if the 75 % rule of SYS-026 is kept. The measured Wi-Fi shell image is 693 KiB (709 780 B), so the shell sample uses 39.6 % of the default slot.

## Scenarios (image sizes are estimates from ADR-0007, not measurements)
| Image size | % of default slot (1792 KiB) | % of reclaimed slot (1888 KiB) | Meets 75 %? |
|------------|-----------------------------|--------------------------------|-------------|
| 710 KB (Wi-Fi shell, measured) | 39.6 | 37.6 | yes |
| 1024 KiB | 57.1 | 54.2 | yes |
| 1200 KiB | 67.0 | 63.6 | yes |
| 1344 KiB | 75.0 | 71.2 | limit in the default layout |
| 1536 KiB (ADR-0007 upper estimate, 1.5 MB) | 85.7 | 81.4 | **no** |

Reading: if the product image stays at or below about 1.3 MiB, the default 4 MB layout works without any change to the module. The ADR-0007 upper estimate (1.5 MB) would exceed the 75 % rule even after reclaiming the unused areas. The real size is unknown until E2b.

## Other items in the budget (still unknown)
| Item | Size | Source |
|------|------|--------|
| Web page files | in the image or in a partition; unknown | Decide in E2 (open design question) |
| Settings, certificates, device key record, unit passphrase | well below 192 KiB expected; to count | ADR-0006, ADR-0008, SYS-026 (25 % free of this area) |
| EAP (WPA2-Enterprise) headroom | unknown | E12 |
| Secure boot and flash encryption | no slot growth expected; the bootloader may grow (E11a) and must still fit the ROM loader limit | E11a |
| MCUboot trailer / swap metadata | a few KiB per slot | E9 |

## Conclusions and what comes next
1. The flash question is **open but not alarming**: the default layout gives a 75 % image limit of about 1.31 MiB. Whether the product fits depends on E2b, not on the module.
2. Reclaiming the unused `lpcore` and unassigned areas costs nothing and raises the limit to about 1.38 MiB; that needs a custom partition devicetree for the product (not a Zephyr change).
3. The ADR-0007 escape routes (8 MB module, differential update, smaller image) are only needed if E2b gives more than about 1.4 MiB. A smaller image is the first lever (log level, shell off, unused net features off).
4. Next measured step: E2b once the HTTP server, TLS, JSON and update upload exist in a throw-away image on the spike branch.
