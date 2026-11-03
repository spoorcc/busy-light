# Review Record RV-001

- **Subject:** `docs/plans/02-system-design.md` (Draft) with ADR-0002 to ADR-0008 as referenced, state of 2026-11-03
- **Type:** Design (Elephant-Goldfish: comprehension pass and three antagonistic passes)
- **Date:** 2026-11-03  **Reviewer(s):** four stateless subagents (comprehension; failure modes and safety; testability and auditability; integration and manufacturability)
- **Independent?** Partly. The reviewers had no conversation context, but they are the same model family as the author, and I (the Elephant) resolved the findings. The owner has not reviewed this record.

## Comprehension pass
The goldfish explained the architecture, scope and decisions correctly. It found stale ESP32-nRF text, inconsistent counts (G1-G14 vs G17), a diagram that said HTTP where ADR-0008 requires TLS, and unclear ARCH numbering. All were corrected in the plan and the diagram before the antagonistic passes.

## Findings and resolutions
The three antagonistic reports held 24, 30 and 30 findings (84 in all, many overlapping). They are merged into 24 items below. Status: **Fixed** (text changed in this commit set), **Carried** (action recorded, work not yet done), **Owner** (needs a decision from the owner), **Rejected** (with reason). Source numbers are in brackets: T = testability report, S = safety report, I = integration report.

| # | Severity | Finding | Resolution | Status |
|---|----------|---------|------------|--------|
| 1 | Critical | **False green with push-only.** SYS-033 is deferred; SYS-010 covers polls only; with a 3600 s poll interval, three failures take 3 h to show; a changed device key after factory reset silently breaks Jenkins' pin. [T10, S1, S19, I20] | Valid. This reverses a decision the owner made (deferral), so I do not change it. Recommendation: make a stale indication a Must for a push-only configuration, with a minimal form (the sender sends a heartbeat; the device shows stale after a user-set age), and add a maximum-age rule to polls that does not depend on the interval. Residual risk to be recorded in the risk register and the manual. | Owner |
| 2 | Critical | **Flash does not fit.** Two slots of 1.9-2.4 MB (image 1.0-1.5 MB, plus 25 % margin, plus EAP headroom) exceed 4 MB. SYS-026 does not say what the 25 % refers to. [T3, S2, I1] | Valid. Plan spike 7.1 now has numeric pass/fail items and a stated fallback; the paper flash budget is a required step before the spike. SYS-026 definition (per slot or total) goes into the requirements pass. | Carried |
| 3 | Critical | **8 MB module is not an escape hatch.** [I2] | Checked by web search: Espressif's datasheet lists only 4 MB variants of ESP32-C3-MINI-1. 8 MB parts exist as ESP32-C3-WROOM-02-N8 and -02U-N8 (a larger module, different footprint, about 18 x 20 mm, to verify). A MINI-1 N8 appears in one third-party listing only and is unconfirmed. The ADR-0007 option "8 MB module" therefore means a redesign of the board outline. Plan row 7.1 states this. | Fixed in plan; ADR-0007 is Accepted and not edited |
| 4 | High | **ADR-0007 is Accepted although it depends on unproven items** (MCUboot on this part, key count, slot layout) and on Proposed ADRs; the review had not run. [S2, I3, S27] | Valid. I cannot change an Accepted ADR. Decided by the owner on 2026-11-03: ADR-0007 is set back to Proposed. Its content (downgrade allowed, offline release key) is unchanged and stays confirmed by the owner. | Closed |
| 5 | High | **Current limiter placement.** ADR-0004 said "before gamma and animation, never after", which does not bound the final output. [I5, S9, T11] | Valid, my error. ADR-0004 item 3 now puts the limit as the last step before the driver, with a margin for LED spread. | Fixed |
| 6 | High | **Ring holds the old frame during hang, reset, bootloader and image swap**, so SYS-011 and SYS-018 cannot be met in that window. [I6] | Valid. ADR-0004 item 5 states the gap and three options (accept, LED supply switch, bootloader hook). Default: accept and document. The owner decides after 7.5 and a measurement of the swap time. | Owner |
| 7 | High | **Revert rule has no trigger when the new image runs but never confirms; 30 s confirm plus swap may exceed 60 s.** [I7, T14] | Valid. SYS-029 now says the device restarts and reverts within 60 s of first start including the swap, and the swap time is measured. The confirm rule itself is in the Accepted ADR-0007 and cannot change; a SW requirement must add the forced restart. | Fixed in SYS-029; SW requirement carried |
| 8 | High | **Confirm rule can ship an image that can never be fixed remotely** (does not wait for Wi-Fi; no health check of the web server or update endpoint). [S8] | Partly valid. A local health check (web server listening, update endpoint reachable on loopback) is a sound addition. It belongs in a SW requirement and, if the owner wants it as a decision, a new ADR that supersedes item 3 of ADR-0007. Settings schema versioning added to the carried list. | Carried |
| 9 | High | **Key lifecycle:** the bootloader holds the public key and cannot be updated; development-key units cannot accept release images; the first image on each unit needs a defined key. [I4, S7] | Valid. The key-management document (G8) must cover: which key signs the first image, which public keys the bootloader holds, how the 10 prototypes are re-flashed over USB, and the unit quarantine policy. Required before any unit leaves the owner. | Carried |
| 10 | High | **Access point threats.** Unprovisioned unit keeps the AP open; label is a shared secret; uploads of CA and certificate in the AP; button press by a passer-by. [T8, S3, S4] | Valid. ADR-0006 now adds a [10] min AP timeout, one client at a time, no display of stored credentials, and states that the label is a shared secret. WPA3-SAE stays a later option. Risk-register entries carried. | Fixed in ADR-0006; risks carried |
| 11 | High | **Passphrase: "never sent" vs "readable over USB".** No read-back check before printing the label. [S5] | Valid. ADR-0006 item 7 resolves it: USB read only with the button held, never over the network; read-back compare before the label; secrets partition included in power-cut tests. | Fixed |
| 12 | High | **"Private key cannot be read through any interface"** cannot be shown on prototypes (USB download mode, no fuses). [S6, I11, T6] | Valid. SYS-034 and SYS-035 criteria now say "network, web interface or access point" and name the USB limitation. Prototype-only labelling and the CRA/EN 18031 consequence go to `regulatory-check`. | Fixed in requirements; regulatory check carried |
| 13 | High | **Antenna inside the LED ring is likely to fail the keep-out; plan and ADR-0003 conflict on topology order.** [I8, I9] | Valid. Plan 4.3 now points to ADR-0003 and marks the old order as a record. ADR-0003 now requires a KiCad keep-out check before any further design and records the reviewer's advice to make B the baseline. The owner decides A-first or B now. | Owner |
| 14 | High | **Provisioning flow:** AP and station together or not; wrong-password handling; captive-portal browsers may have no file picker. [I12, I13] | Valid. ADR-0006 items 9 and 10 add a state machine, a test join, pasted-PEM entry and two-phone tests. Spike 7.1 pass/fail added. | Fixed |
| 15 | High | **Certificate validity 1970-9999 and SYS-031 scope; Jenkins plug-in pinning untested.** [T9, S19, I14] | Valid. ADR-0008 now uses 2000-01-01 to 2049-12-31 (UTCTime), states SYS-031 applies to outgoing connections only, and spike 7.1 tests Chrome, Safari, Firefox, curl and a Jenkins HTTP step. | Fixed |
| 16 | High | **Time:** no RTC; unauthenticated NTP on a shared LAN; browser-time fallback not a requirement. [S11] | Valid. Needs a requirement with an acceptance rule (sanity lower bound at the build date; who may set the time). Not drafted yet. | Carried |
| 17 | High | **Poll over plain HTTP exposes the Jenkins token.** [S12] | Valid. SYS-007 now requires a warning for plain HTTP. Whether HTTP polls should be forbidden is left to the owner. | Fixed (warning); Owner (forbid?) |
| 18 | High | **Missing requirements:** web login password and lockout, push body format, brightness figure, range figure, host name, key management evidence, reset behaviour table (what survives a factory reset), AP timeout, extractor limits, USB recovery. [T7, T16, S14, I24] | Valid. Several need owner values (brightness, range). To be drafted in the requirements pass; the reset table is needed because SYS-017, 030, 034, 035 and ADR-0006 disagree. | Carried |
| 19 | Medium | **Test cases are empty stubs; SYS-037 and SYS-019 power-cut tests cannot be shown on `native_sim` or QEMU for a real MCUboot swap or ESP32 flash behaviour.** [T1, T2, S18, I23] | Valid. Plan 4.13 L2 text corrected. A hardware power-cut rig (relay) is mandatory evidence for TC-019 and TC-029. Test procedures are written when the requirements are approved; I do not claim any verification exists. | Fixed (plan); Carried (TCs, rig) |
| 20 | Medium | **Safety arithmetic and measurability:** SYS-001 "visible at 2 m", the 256 levels vs global scaling, 500 mA peak vs average, USB-C CC/ESD/inrush, thermal, photobiological, flash rate, level-mode edge cases, colour-blind and "black" settings. [T11, T12, S9, S10, S21-S25, I18] | Valid. Level edge cases and boolean/null types are fixed in ADR-0005. The rest needs requirement rewrites and analyses (7.3, 7.5, G10, G11). | Fixed (ADR-0005); Carried |
| 21 | Medium | **Robustness of the web and poll paths:** concurrent TLS sessions, handshake floods, auth lockout, escaping, CSRF, response size, timeouts, fuzz scope. [T13, S14-S16] | Valid. SW requirements with limits and fuzz targets (parser, extractor, PEM/X.509, update stream) to be drafted. | Carried |
| 22 | Medium | **Cost, BOM and supply chain:** no BOM; "other parts EUR 1" is optimistic; extended-part fees; board outline rules; VAT definition. [I16, I17, T24] | Valid. Spike 7.4 becomes a real BOM with stock and prices, and the shop's outline rules. A4 must say whether VAT counts. | Carried; Owner (VAT) |
| 23 | Medium | **Zephyr gaps with no effort cap; locally patched stack, blob and licence, SBOM, reproducible signed builds.** [T4, T20, S26, I26, I28] | Valid. Plan spike 7.1 row has a [2] week cap per feature and requires a DEV record for any local patch. SBOM, blob hash pinning and "reproducible means the unsigned image" go into the requirements pass. | Fixed (cap); Carried |
| 24 | Medium | **Stale plan text and traceability:** Wokwi in D10, superseded 4.12 recommendation, different weight sets, ARCH IDs not registered, risk register nearly empty, regulatory fields TBD. [T17-T19, S27, I25] | Valid. D10, 4.12 and the L2 row are corrected; the weight difference between 4.2 (5) and 4.13 (8) stays explained in the plan as two sets. Risk register entries, ARCH registration and `regulatory-check` are the next steps. | Fixed (text); Carried (register, ARCH, regulatory) |

### Rejected or reduced
- **Make hard backstop for current mandatory now** [S9]: not rejected, deferred to spike 7.5 with a decision trigger; ADR-0004 item 4 stays open.
- **Treat reviewer figures as facts:** reviewers worked from memory and say so. No figure from them is carried into a requirement without a source.
- **Score for "SYS-013 ten units differ is meaningless"** [S5, S30]: valid as a weak test, but kept as a sanity check; the entropy analysis in ADR-0006 is the real evidence. Wording to be refined in the requirements pass.

## Readiness pass
Run on 2026-11-03 by one fresh stateless subagent (same model family as the author) after the requirements pass, SYS-043..046, SW-001..004, the risk register, ARCH registration, the regulatory first assessment and the key-management draft.

**Verdict: NO-GO.** As expected for a system-level design: the plan has no signatures, nets or dimensions to implement, and it says itself that nothing in it is a decision.

What checks out (verified by the goldfish): traceability check 164 items with 0 errors and 0 warnings; every ID cited by the plan exists (ADR-0001..0008, SYS-001..046, TC-001..046, TC-101..104, RISK-001..022, ARCH-001..019); every SYS and SW requirement links to a test case.

Blockers, with the resolution state:
| Sev | Blocker | State |
|-----|---------|-------|
| Critical | No requirement is Approved, so nothing may be built in `sw/`, `hw/` or `mech/` | Owner approval needed |
| Critical | All 50 test cases are stubs (procedure, automation, evidence TBD); the power-cut rig does not exist | Procedures are written after approval; rig carried |
| Critical | `hw.md` and `mech.md` are empty: no HW or MECH requirements | To draft next |
| Critical | Open owner decisions (items 1, 6, 13, 17, 22) | Working defaults applied; owner confirms |
| Critical | Flash fit unproven (SYS-026 definition now fixed; remedy depends on spike 7.1) | Spike 7.1 |
| Critical | Zephyr features on ESP32-C3 unproven; `sw/app` is a stub with no board and no Kconfig | Spike 7.1 on a development kit, on a `spike/*` branch |
| High | All ADRs are Proposed | Owner accepts after the spikes |
| High | Requirement values are placeholders in brackets | Owner sets; spikes 7.1 and 7.5 measure |
| High | Gap-list requirements may be missing (time/NTP rule, web password, USB recovery, SBOM) | Checked by the Elephant: SYS-031, SYS-039, SYS-046, SYS-044 now cover them; blob pinning is in SYS-044; no gap known beyond the carried HW/MECH requirements |
| High | Hardware cannot start: no keep-out check in KiCad, no `hw/sim` analyses | Owner places the outline; analyses after the spike |
| High | Production and security process: key-management is Draft with *(verify)* items; no provisioning tool | Owner review; tool is code, after approval |
| Medium | Cost basis is unverified | Spike 7.4 |
| Medium | Stale plan text (status line, SYS range, ARCH not registered) | Fixed in this commit set |
| Medium | `sw/app` has no `core/` layout or tests | Created with the code after approval |

Not checked by the goldfish: no build, no `west`, no diagram check, and SYS-038..046 were not read one by one.

## Outcome
**Approved with actions** (readiness verdict NO-GO). The design is coherent and the alternatives are real, but nothing in it is yet verified. Actions: the owner decisions above; the requirements pass; risk-register entries; ARCH registration; `regulatory-check`; the key-management document; spikes 7.1, 7.2, 7.3, 7.4 and 7.5. Only the owner sets `Approved` on the plan.
