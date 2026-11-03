# 04 -- Owner review guide (state of 2026-11-03)

- **Status:** Draft (a reading aid, not a controlled design document; it decides nothing)
- **Purpose:** one place that lists what waits for the owner, what the author recommends, and what was done without hardware.
- **Nothing is Approved or Accepted.** Only the owner sets those states.

## 1. What waits for approval
| Item | Where | Author's advice |
|------|-------|-----------------|
| Plan 02 (system design) | `docs/plans/02-system-design.md` | Read sections 3, 8, 10 first. Approve after the owner decisions below |
| Plan 03 (spike 7.1) | `docs/plans/03-spike-7-1-zephyr-esp32c3.md`, `docs/verification/spike-7-1-runbook.md` | Approve first: it unlocks the hardware purchase and all kit experiments |
| ADR-0002 to ADR-0008 | `docs/decisions/` | Accept only after the spikes. ADR-0007 has a new section on the secure-boot build chain |
| Requirements | `docs/requirements/` (SYS-001..046, SW-001..004, HW-001..009, MECH-001..006) | Review the bracketed values; approve in groups |
| Key management | `docs/regulatory/technical-file/05-cybersecurity/key-management.md` | Approve before any unit leaves your hands |

## 2. Decisions that need the owner (with the author's recommendation)
| # | Decision | Recommendation | Why |
|---|----------|----------------|-----|
| 1 | **Secure-boot build chain (RISK-023).** The Zephyr sysbuild bootloader has no secure boot or flash encryption for the C3; only the standalone Espressif port (ESP-IDF 6.0.x HAL) has them. Accept a pinned ESP-IDF build for the bootloader only, or reconsider secure boot for release 1 | Accept it for stage 3, keep the application in Zephyr, and test both the Espressif port and Espressif's own bootloader in the spike | You asked for secure boot; stage 1 prototypes are unaffected. See `spike-7-1-e11a-build-variants.md` |
| 2 | Approve plan 03 and buy parts: 6 ESP32-C3-DevKitM-1 (3 working, 3 sacrificial), LED ring or strip, USB power meter, logic analyser at 8 MS/s or more, USB switch for power cuts, a spare WPA2 access point | Approve; check the module revision is v0.3 or newer | Without hardware no experiment can run |
| 3 | Antenna topology (ADR-0003): module in the ring centre (A) first, or a module with an external antenna connector (B) as the baseline now | Baseline B if range matters more than size; A only after the KiCad keep-out check | The reviewer advised B; the working default is A first |
| 4 | Ring state while the firmware is not running (ADR-0004) | Accept and document | A fix needs an LED supply switch or a bootloader hook |
| 5 | HTTP polls (SYS-007): warn or forbid | Warn only for release 1 | The token is exposed on plain HTTP; the user is told |
| 6 | Push-only liveness (SYS-033) is a Must | Keep it | Without it the ring can show a stale green |
| 7 | VAT inside the EUR 10-20 limit (A4) | Keep it included | Conservative |
| 8 | Prototype eFuse steps | None on the 10 internal prototypes | Debugging; stage 2 proves the procedure first |
| 9 | Manufacturer name and address on the label | Deferred by you; needed before the first unit goes to someone else | CRA and RED labelling |
| 10 | Bracketed requirement values (brightness, range, intervals, limits) | Review as a group after spike 7.5 | They are the author's working values |
| 11 | WPA2-Enterprise (SYS-036) priority | Keep Must for now | The ESP32 driver in v4.5.0 maps EAP types to the Espressif blob; the build-only cost is about +70 KB flash and +6 KB static RAM (`spike-7-1-e12-e2b-followup.md`); function is untested |
| 12 | **USB current limit — decided by the owner on 2026-11-04: allow a higher current if the source advertises it (SYS-020 and HW-003 updated, still Draft). Open follow-ups: the cap ([1500] mA proposed), a CC read circuit or a CC controller, and whether a hardware current limit is now needed.** ADR-0009 (Proposed) compares the options: it recommends reading the CC lines with the processor's ADC (score 136) with a CC detection IC as fallback (127); the 9-point gap is within scoring error, so a spike should decide. Original question: USB current limit (SYS-020 uses [500] mA). The paper power budget (`spike-7-5-power-budget-paper.md`) shows that Wi-Fi TX peaks leave only 5 to 58 % of full white for the LEDs at 500 mA, depending on LED type and LDO or buck | Decide whether the product may draw more than 500 mA when the USB-C source advertises 1.5 A or 3 A through the CC lines, with a safe fallback to 500 mA; and decide the brightness target of SYS-001 against that | The 100 mcd working value of SYS-001 may not be reachable at 500 mA; this is a requirement question, not a design detail |
| 13 | Extractor details found by the PC prototype (`spike-adr0005-extractor-prototype.md`): accept numbers in exponent form (F3); validate the whole body or stop at the target (F4); how a Jenkins answer with `building` false and `result` null is shown (F6) | Reject exponent numbers (document it); stop at the target; show `result: null` as running and test it against a real Jenkins in E5 | Keeps the code small; matches ADR-0005 item 4 |

## 3. What was found without hardware (all Draft reports, `docs/verification/reports/`)
- E0: Zephyr v4.5.0 (pinned in `sw/west.yml`, with your approval) has the ESP32 Wi-Fi driver with AP+STA, WPA2-PSK soft AP, a DHCP server and an HTTP server with TLS. The captive-portal DNS is custom code. LEDs: SPI `ws2812` only.
- E1: `hello_world` and the Wi-Fi shell build for `esp32c3_devkitm`; nothing was flashed.
- E2a/E2b: the 75 % image limit is about 1.31 MiB; a throw-away image with Wi-Fi, TLS, JSON, DHCP, LED and settings is 792 KB signed (43 % of a slot) with 285 KB of 360 KB static RAM used. RAM looks tighter than flash. The signed sizes carry up to about 128 KiB of flash-mapping padding noise (follow-up report); the TLS heap can be cut by 20 to 45 KB in builds that link, run-time adequacy unknown.
- E11a: ECDSA P-256 signing builds. Secure boot and flash encryption do not exist in the sysbuild bootloader (decision 1).
- Facts from reviewers' memory (not verified): none are carried into requirements without a source.

## 4. What needs hardware (runbook, not run)
E1 run part, E3 to E10, E11b/c, E14. Start with `docs/verification/spike-7-1-runbook.md`. Read-only kit checks come first.

## 5. Side effects on this machine
- `sw/west.yml` pin changed from v4.2.0 to v4.5.0 (your approval).
- `west zephyr-export` added a file under `~/.cmake/packages/Zephyr/` that points into a temporary folder. Delete it when the temporary folder is gone.
- The west workspace, the Zephyr SDK (about 2 GB), the spike key and all build trees are in the session scratchpad under `/tmp`. They are not in the repository and disappear with the temporary folder. The commands to rebuild them are in the runbook.
- A background agent tried to build the Espressif bootloader against a cloned ESP-IDF; the permission check refused that build step and it was not retried by other means.
- Commits (`git log`) are local on `feature/project-foundation`; nothing was pushed.
