# ADR-0002: Wi-Fi platform for the first prototype and production candidate

- **Status:** Accepted (by the owner, Ben Spoor, 2026-11-07, in the working session, option A as the prototype platform; recorded by the assistant). Spike 7.1 is only partly run (desk and PC parts); the measured checks of the Verification section are still open and the revisit conditions stay in force.
- **Date:** 2026-11-03
- **Deciders / reviewers:** Ben Spoor (owner); Reviewed in RV-001 (as referenced by plan 02); no separate ADR review
- **Related:** NEED-009, NEED-012, NEED-014, NEED-015, NEED-017, SYS-021, SYS-022, SYS-023, SYS-026, SYS-029, SYS-030, SYS-036, SYS-037; design doc `docs/plans/02-system-design.md` (sections 4.2, 4.2a, 4.2b, 4.12-4.14)

## Context and problem
The device needs Wi-Fi (station and soft access point), HTTPS server and client at the same time, signed over-the-air updates with two image slots, user certificates, and a 16-LED ring, on a board of about 46-48 mm
across, for EUR 10-20 per board, firmware in Zephyr, tools free and open source, and as much as possible testable on a PC. Production is planned later at about 1000 units per year. The choice is costly to reverse
(board, firmware port, certification). Not known yet: whether the Zephyr driver of the chosen part supports SoftAP with WPA2, HTTPS server plus client within the RAM margin, and WPA2-Enterprise (spike 7.1);
the real price at 10 and at 1000 units (spike 7.4). Owner decision, round 6: ESP32-C3.

## Decision criteria
| Criterion | Weight (1-8) | Source requirement |
|-----------|--------------|--------------------|
| Zephyr readiness: soft-AP, TLS, MCUboot, HTTP server | 8 | project rule (Zephyr), SYS-012, 029, 030 |
| Unit cost | 5 | NEED-009, SYS-021 |
| Board area and antenna fit | 4 | NEED-014, SYS-028 |
| Flash and RAM margin | 4 | SYS-026, 029, 030, 036 |
| Shop availability, one side | 4 | NEED-010, SYS-022 |
| PC simulation with open tools | 4 | SYS-025, 037 |
| USB-C programming and test without extra chip | 3 | SYS-023 |
| Radio module pre-certified | 3 | RED, `docs/regulatory/applicability.md` |
| Battery path later | 2 | NEED-015 |

## Alternatives considered
### A. ESP32-C3 module (for example ESP32-C3-MINI-1, 4 MB flash)
One chip, Wi-Fi 4 2.4 GHz, 400 KB RAM (from memory, verify), USB serial and debug in the chip. Upstream Zephyr: production-ready since 4.0, station plus AP listed in the 4.0 notes. Module price about EUR 2-3 (estimate). QEMU (Espressif fork, no Wi-Fi) and `native_sim` for the PC.
Cons: Wi-Fi is Espressif's binary library; Zephyr documentation and samples thinner than Nordic's; ESP32 driver maps EAP types to the Espressif blob (E0 pass 2; untested); no 5 GHz.
### B. ESP32-C6 module
Wi-Fi 6, 802.15.4, more RAM (from memory). Slightly dearer; Zephyr Wi-Fi support newer. Same family and tools, so it is the natural step up if C3 RAM proves too small.
### C. nRF5340 + nRF7002 (Fanstel WT02x40x single module, or two modules)
Best vendor documentation and a SoftAP sample (nRF Connect SDK), upstream board and `nrf5340bsim`. Dual band, enterprise Wi-Fi listed. Cons: estimated EUR 25-35 per board against the EUR 20 limit, needs external flash for two slots, SoftAP and enterprise in upstream Zephyr unconfirmed, price and stock of the single module unknown, small module vendor.
### D. NXP RW612 module (u-blox IRIS-W106)
Single chip, Wi-Fi 6, upstream Zephyr board with a Wi-Fi blob. About EUR 12.3 per module. SoftAP in upstream not confirmed; no simulator found.
### E. Host MCU plus Wi-Fi co-processor (ST67W611M1, ESP-AT)
Two parts. The Zephyr driver for the ST module is station-only, which fails SYS-012. Not viable now.
### F. Do nothing / defer
Stay on dev kits and decide at the 1000-unit quote gate. Costs time; no hardware learning; rejected because spike 7.1 needs a platform and a dev kit is cheap.

## Comparison
Scores 1-5 (judgement, not measured); totals use the weights above and the scores of plan 02, section 4.2.
| Criterion | A ESP32-C3 | B ESP32-C6 | C nRF5340 + nRF7002 |
|-----------|-----------|-----------|---------------------|
| Zephyr readiness (8) | 4 | 3 | 5 |
| Unit cost (5) | 5 | 4 | 1 |
| Area and antenna (4) | 4 | 4 | 2 |
| Flash and RAM (4) | 3 | 4 | 5 |
| Shop, one side (4) | 5 | 4 | 3 |
| PC simulation, open tools (4) | 3 | 3 | 3 |
| USB-C program and test (3) | 5 | 5 | 4 |
| Pre-certified module (3) | 4 | 4 | 3 |
| Battery later (2) | 4 | 4 | 5 |
| **Weighted total (max 185)** | **152** | **139** | **128** |
D and E are not scored: D has too little evidence (SoftAP, simulation, price at 1000 units), E fails SYS-012. The margin of A over C comes from cost, area and shop availability; C leads on Zephyr readiness by one point.

## Decision
Accepted by the owner on 2026-11-07: choose **A, ESP32-C3**, because it is the only candidate that meets cost, area and shop limits together and is in mainline Zephyr with Wi-Fi AP support listed. Keep a thin hardware layer (Wi-Fi, LED output, button, storage, clock) so that B or C can replace it.
Decision applies to the prototype board and is confirmed for production at the 1000-unit quote gate.

## Consequences
- Positive: lowest cost; one small module; USB-C programming and test through the chip; large community; QEMU and `native_sim` available; fits the EUR 20 limit with an estimated EUR 11-19.
- **Negative / trade-offs accepted:** Zephyr is less well documented for ESP32 Wi-Fi than for nRF70; Espressif binary Wi-Fi library (licence check, G16); 400 KB RAM must hold TLS server and client, HTTP server and later WPA2-Enterprise (25 % margin may not hold); no 5 GHz, no Wi-Fi 6; weaker battery path (NEED-015) and weaker hardware key store than nRF54; secure boot uses one-time fuses (decision deferred, plan 4.7).
- New risks (add to risk register): RAM exhaustion with two TLS roles; Zephyr driver gaps (SoftAP, enterprise); Espressif blob licence; module antenna in an LED ring (G15).
- Requirements created or changed: SYS-021 (limit stays EUR 20); SYS-036 (risk note); SYS-037; spike plan 7.1 first.

## Verification and revisit
Spike 7.1 on a ESP32-C3 dev kit with Zephyr must show, measured: SoftAP with WPA2 and a phone joining; station mode; HTTPS server and HTTPS client at the same time with a user CA; signed MCUboot swap and rollback; free RAM and flash against SYS-026. Revisit this ADR if any of these fail,
if the free RAM after the spike is below 25 %, if the 1000-unit quote shows the saving versus nRF below about EUR 5 per unit, or if the battery version becomes a near-term plan.

## Critical review notes
Strongest objection: Zephyr is important to the owner and nRF is the best-documented Zephyr Wi-Fi platform, so choosing ESP32 trades support quality for price. Answer: both are in mainline; the evidence for a gap is documentation and samples, not missing features (not yet measured);
spike 7.1 tests exactly the features we need, and the hardware layer keeps the nRF option open. If the spike shows missing features, fallback per owner round 7: write the missing feature and upstream it (plan 02 section 10).
