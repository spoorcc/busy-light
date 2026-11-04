# Goldfish review of the hardware gate fragment v2 (spike/hw-gate, commit 2689518)

- **Status:** Draft (stateless reviewer record; nothing Approved)
- **Date:** 2026-11-04
- **Reviewed:** `hw/kicad/spike-gate/src/gen_gate.py`, `tests/test_gate_logic.py`, `sim/*`, `docs/verification/reports/spike-hw-gate-fragment.md`; context HW-003, HW-010, ADR-0016, RISK-026/027/029/042/043, `cc-ic-datasheet-evidence.md`
- **Related:** HW-003, HW-010, ADR-0016, RISK-029, RISK-042

## 1. What the circuit does (from the files only)
1. A CC detection IC (U1, placeholder header, VDD from VBUS) has an open-drain OUT1_N, pulled to 3.3 V by R1 (100k); low means at least 1.5 A.
2. U2 (74LVC1G04, 3.3 V) inverts OUT1_N into CC_OK_1A5.
3. R6 (1M) and C1 (510n) charge from VBUS into Schmitt buffer U5 (5 V) giving HOLD_OK; D1 (RC to VBUS) should empty C1 on unplug.
4. U3 and U4 (74LVC1G11, 3.3 V) AND CC_OK, HOLD_OK and one firmware select each; the output drives a 2N7002 that switches a limit resistor into a shared ILIM net. 100k pull-downs sit on selects and enables.
5. Result: a step above the first is enabled only if the IC says at least 1.5 A, the start-up timer has run out and the firmware asks for it.

## 2. Findings (ranked)

### Critical
**C1. `run_powerup.sh` cannot fail on a simulator error.** Scenarios A to F expect `low`; the check is `awk 'BEGIN{print (e<1.65)?1:0}'` with `e=""` when ngspice prints no `en_max` (parse error, missing ngspice, bad netlist). I ran `awk -v e="" ...`: it prints 1 (ok). Scenario: a typo in `powerup.cir` makes every run fail to measure; six of seven scenarios print "ok" and exit 0. The only scenarios that can fail are `pulse` and `late`. The hold-off evidence in row 9a is therefore not trustworthy until the script rejects an empty value.

### High
**H1. D1 does not restart the hold-off after a VBUS dip (HW-010: "restarts after every loss of the IC supply").** D1 conducts only while RC > VBUS + Vf. After a dip of VBUS to, say, 3.5 V (below the IC's 4.5 V minimum, not to 0 V), C1 stays at about 3.8 V; when VBUS returns to 5 V, RC is above 0.6 of the rail (Schmitt high) at once. The IC may have restarted its 133 ms debounce while the gate has no hold-off. Scenario: a flaky cable or a source that sags under inrush. Not simulated, not tested; `test_hold_off_rc_...` checks only the topology.

**H2. Leakage is not in the tolerance budget.** A 1 Mohm node has 1 uA = 1 V. Reverse leakage of a Schottky D1 (cathode on VBUS, so leakage flows into C1 and shortens the hold-off) and the input leakage of U5 are quoted in uA at 85 C on typical datasheets (to check; I read none). Scenario: at hot closed-housing temperature the node rises early and the 200 ms minimum is lost, silently. `holdoff_tolerance.py` models only R, C and threshold. Also: 510 nF X7R "10 %" is not a tolerance over temperature and DC bias (5 V on 0603 loses tens of percent); the 200 ms minimum is then undefended.

**H3. Footprint/pin mismatch on U3 and U4.** The 74LVC1G11 is a 3-input gate with 6 pins (A, GND, B, Y, VCC, C), but the footprint is `SOT-23-5` and the script uses pin 6. The netlist tests pass because they read the netlist the script wrote (circular). Scenario: layout import fails or pin 6 has no pad; the hold-off input cannot be wired. The report admits pins were not checked against a datasheet, but the footprint error is visible without one.

**H4. The hold-off input has no safe default and its faults are silent.** There is no pull-down on HOLD_OK (pin 6) or CC_OK (pin 1); HW-010 lists "gate input open" in the fault injection. An open at pin 6 floats an LVC input, which may read high: the hold-off is lost and nothing shows it. Likewise C1 open, R6 or D1 shorted, or U5 output stuck high remove the hold-off with no detection. Fail-safe cases (C1 shorted) close the gate, but the fail-unsafe ones are not in the test list or the report.

### Medium
**M1. Power-order of the IC output (datasheet evidence item 6) is not handled, only mentioned.** OUT1 rating is VDD + 0.3 V. The pull-up goes to the 3.3 V rail, which normally decays slower than VBUS at unplug (bulk capacitance). Each unplug puts 3.3 V through 100k on a pin whose VDD is falling to 0. The current is limited (about 33 uA) but the rating is exceeded on every cycle. No test, no sim, no mitigation (for example a pull-up to VBUS_IC behind a divider, or a series element). The report says "not run".

**M2. Back-feed from U5 (5 V) into U3/U4 (3.3 V) when 3.3 V is down.** HOLD_OK reaches 5 V into AND inputs whose VCC may be 0 V (VBUS present, 3.3 V regulator off or in brown-out). Whether the 74LVC1G11 input is allowed with VCC = 0 V (Ioff) and what current flows was not read from a datasheet. If not allowed, HOLD_OK back-powers U3/U4 through the input clamp and their outputs are undefined. The above-rating case with 3.3 V present (5 V on a 3.3 V part, 6.5 V rating) was also not checked. The prompt asked for this specific case; the report is silent on it.

**M3. Hold-off start is VBUS, not "IC supply valid", and the margin to the debounce is thin.** R6 charges from the first volt of VBUS; HW-010 says "after the IC supply becomes valid". The IC debounce is 133 ms typical (no maximum read; the USB Type-C range for tCCDebounce is 100 to 200 ms in my memory, unchecked). The recomputed minimum of 232 ms (see M4) leaves only about 30 ms against a 200 ms debounce. In addition the real attach path (VBUS_DET through 887k, PORT to GND) is absent from the fragment; the pin 5 is named CC_RESERVED and left unconnected, while PORT open means DRP (source pull-up on CC) per datasheet item 7.

**M4. Report arithmetic is wrong in both directions (F10).** Recomputed with the stated assumptions (R 1 %, C 10 %, Schmitt 0.40 to 0.60 of rail, t = RC ln(1/(1-k))), nominal 510 ms: min 232 ms, max 519 ms; max/min = 1.794 x 1.247 = 2.24, not 2.97 ("met only just"). The stated 2.97 matches a 0.30 to 0.70 band (2.94). With R 1 % and C 20 %: ratio 2.74, below 3.0, so "A 20 % X7R capacitor does not fit" is also false on the report's own numbers. `holdoff_tolerance.py` (R 5 %, C 20 %) disagrees with F10 (R 1 %, C 10 %) and gives 515 ms nominal, which is what the generator uses; the generator says R6 "1M 1%" and C1 "10 %". Direction is conservative but the document cannot be reproduced; the F7 text (maximum about 600 ms, 133 + 500 ms overlap) rests on this.

**M5. ILIM sharing is unverified.** `Net("ILIM")` is created inside the loop, twice. SKiDL may merge them or rename the second (ILIM_1) with a warning; there is no test on ILIM, and the report only says "share one ILIM node" (F6). If they are separate nets the ILIM resistors are never parallel to the limit part. I could not run SKiDL here (module not installed), so this is unverified, not confirmed.

### Low
- **L1. Tests are partly tautological.** `test_gate_needs_both` asserts `step_enable == (out=="low" and sel)`, the formula in the model. `gate_logic_powered=False` returns False as a constant. The model has no hold-off input, no D1/C1 and no timing, so "12 tests pass" says nothing about HW-010's hold-off or about U5. No test checks VCC/GND of U2 to U5 (the V3 vs VBUS split, which is the power-level concern), nor ILIM, nor that CC_OUT2_N and PORT are handled.
- **L2. Stale report text.** Section 2 still lists two 74LVC1G08 gates and no hold-off; row 5 says 9 tests (now 12); row 9a describes the hold-off on the 3.3 V rail, 390 nF (the sim still uses 390n/312n, not 510n from VBUS, and holds the rail ramp at 1 ms, so the v2 hold-off was never simulated). The F10 "no v2 schematic" means ERC, parity and DRC were not run on v2; the title says "checked with KiCad ERC" and the generator header says v2, so a reader may assume it was.
- **L3. Single faults not covered, stated honestly in HW-010 but not tested here:** U2 output stuck high or R1 shorted to ground removes the IC gate for both steps (the ok net is single and shared; H1 of RV-008); stuck AND output; shorted select MOSFET. The 2N7002 is driven at 3.3 V (Vgs(th) max 2.5 V): drive margin not checked.
- **L4. Sim thresholds ideal, glitch assumed**, per the report; scenario G passes only because the sim uses an ideal half-rail threshold, which F7 already rejects.

## 3. What I did not check
No datasheets (74LVC1G11, 74LVC1G17, diode, TUSB321 beyond the evidence file). I did not run ngspice scenarios, the unit tests (no generated `gate.net`; SKiDL not installed), ERC, or the generated schematic (none exists for v2). Pin numbers of the 74LVC1G11 were checked only by my memory of the part (6 pins), and the KiCad symbol was not opened. Leakage and Vt+ values are not quantified. Regulatory and CRA aspects not reviewed.
