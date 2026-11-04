# Review Record RV-002

- **Subject:** `docs/plans/03-spike-7-1-zephyr-esp32c3.md` (Draft), state of 2026-11-03
- **Type:** Design (Elephant-Goldfish: comprehension pass and two antagonistic passes; no readiness pass)
- **Date:** 2026-11-03  **Reviewer(s):** three stateless subagents (comprehension; experiment validity; process and safety)
- **Independent?** Partly. The reviewers had no conversation context but are the same model family as the author. Their statements about Zephyr, ESP32-C3 and MCUboot came from memory and are not verified. The owner has not reviewed this record.

## Comprehension pass
The goldfish explained the intent and scope correctly. It found gaps that are now fixed: E12 had no numeric rule; E8 did not test the TLS key case; E13 did not check for heap allocation; the settings-area margin was not measured; the 45 s forced restart and the LED state during the swap were not sub-tests; no experiment covered the browser and Jenkins request-step test (RV-001 item 15); the paper flash budget needed the EAP figure from the last experiment; the test server was undefined.

## Findings and resolutions
The antagonistic reports held 16 and 24 findings. They are merged here. Status: **Fixed** (plan text changed), **Carried**, **Owner**.

| # | Severity | Finding | Resolution | Status |
|---|----------|---------|------------|--------|
| 1 | High | No feasibility check that the pinned Zephyr supports AP, AP+STA, WPA2-Enterprise, MCUboot with the chip's secure boot; no exit path | New step E0 (desk survey) before any purchase, with a fallback order and a stop rule | Fixed |
| 2 | High | E11 (eFuse) had no written procedure, mode choice, abort rule or eFuse log; development mode cannot show the locked state; negative tests missing; the final board uses native USB, the kit a bridge | E11 split into E11a (no eFuse), E11b (development mode), E11c (release mode); procedure document first; negative tests listed; kit result does not close SYS-043 or TC-043 | Fixed |
| 3 | High | E11 last although its result decides E9 (MCUboot or Espressif bootloader) | E11a runs before E9 is finalised | Fixed |
| 4 | High | Kit accounting: sacrificial kits and working kits mixed | [3] working and [3] sacrificial kits, labelled, state recorded | Fixed |
| 5 | High | No secrets handling for spike keys, logs, passphrases | New "Secrets and data handling" rules | Fixed |
| 6 | High | Plan unreviewed and unapproved while the purchase question was posed | Entry condition A7: no purchase and no experiment before the owner approves | Fixed |
| 7 | High | Rollback deleted the only source of the evidence | Branch is tagged `spike-7.1-final` or archived; not deleted | Fixed |
| 8 | High | E2 slot size treated as input; full image does not exist before E2 | E2a/E2b split, break-even formula, swap mode and build type recorded | Fixed |
| 9 | High | E5, E6 definitions: cold, heap metric, leak rule; E6 did not test SW-002 | Definitions added; 10 concurrent attempts, stalled clients and resets added | Fixed |
| 10 | High | E7: cheap analyser cannot resolve LED timing; flash write stalls not provoked; frame content not checked | Sample rate rule, update during animation, content check, supply droop recorded | Fixed |
| 11 | High | E9: swap mode and time breakdown missing; only one of the SW-004 cases | Swap mode first; separate timings; five cases | Fixed |
| 12 | High | E10: relay cuts are not random points; hold-up capacitance; no phase log; weak statistics | Phase logging, controlled and slow ramp, deterministic variant, confidence statement | Fixed |
| 13 | Medium | E3 and E4: clock start, OS versions, HTTP vs TLS page, channel change in AP+STA, wrong password, run length | Added | Fixed |
| 14 | Medium | E8: collision test inside one run is meaningless; RNG may need the radio | Collect across cold resets, statistical test, entropy source named | Fixed |
| 15 | Medium | Thresholds are brackets that circularly set requirement values; pass/fail source unclear | A8: a pass uses the current requirement value, otherwise it is a measurement; the owner sets values | Fixed |
| 16 | Medium | Power experiment missing though a power meter was listed; confounders (RF, AP model, supply) | E14 added; per-run record of channel, RSSI, AP model, chip revision | Fixed |
| 17 | Medium | Repetition, boards and "intermittent" undefined | Repeats, two boards, intermittent counts as failed | Fixed |
| 18 | Medium | Evidence binding: logs vs build; measured vs estimated | Script-made log header, SHA-256, "measured/estimated/not run", result row template | Fixed |
| 19 | Medium | Time and cost estimates weak; no overall time box | Group split, decision points, [6]-week box, parts budget; per-experiment estimates wait for E0 | Fixed (estimates carried) |
| 20 | Medium | Isolated network, regulatory, SBOM, CHANGELOG, ADR item numbers drift | A6, SBOM list in the report, decisions named not numbered | Fixed |
| 21 | Low | Kit is not the target part (flash mode, chip revision) | Chip revision, flash ID and eFuse dump recorded | Fixed |
| 22 | Low | Vendor eFuse procedure cited without a version | Named in the eFuse procedure document | Fixed |
| 23 | Low | Bracketed values and *(verify)* marks stay | Expected: they are resolved by the spike and by the owner | Carried |

## Readiness pass
Not run. Reason: the plan depends on E0, which cannot be done before the owner approves, and on many bracketed values. Run it after the owner approves and E0 is done.

## Outcome
**Approved with actions.** Actions: owner approval of the plan (entry condition A7); then E0; then the purchase decision. Only the owner sets `Approved`.
