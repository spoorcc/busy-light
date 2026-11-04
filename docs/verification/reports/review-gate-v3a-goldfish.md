# Goldfish review of the hardware gate fragment v3a (spike/hw-gate, commit a1e7d45)

- **Status:** Draft (stateless reviewer record; nothing Approved)
- **Date:** 2026-11-04
- **Reviewed:** `hw/kicad/spike-gate/src/gen_gate.py`, `src/write_sch.py` (skim, header only), `tests/*`, `sim/powerup.cir`, `sim/run_powerup.sh`, `sim/holdoff_tolerance.py`, report sections "Version 3" and "3a", the three datasheet-evidence files. Context: HW-003, HW-010, ADR-0016, RISK-042..044, SW-005..008.
- **Ran:** `sim/run_powerup.sh` (11 scenarios, all "ok", rc 0), four mutations of the netlist (section 4), `python3 -m unittest` on the committed fixture. **Not run:** SKiDL (not installed), ERC, parity, writer.

## 1. Circuit, explained back (files only)
1. VBUS_IC (5 V) supplies the CC IC U1 (placeholder), the supervisor U5 (TPS3840DL40 candidate, C1 620n on its delay pin) and the pull-ups R1 (IC output) and R6 (supervisor output); +3V3 supplies U2 (inverter) and U3/U4 (3-input AND).
2. U1 OUT1_N is open-drain, low = at least 1.5 A; R1 pulls it to VBUS_IC; U2 inverts it to CC_OK_1A5 (high = advertised).
3. U5 holds RESET low while VBUS < about 4 V and for tD (about 0.62 s/uF x C) after; R6 pulls HOLD_OK to VBUS_IC, so high = hold-off done.
4. U3/U4 each AND CC_OK, HOLD_OK and one firmware select; the output drives a 2N7002 that switches a placeholder ILIM resistor into a shared ILIM net; 100k pull-downs on selects and enables.
5. Intended result: a step above the first is on only if IC says >= 1.5 A and hold-off is done and firmware asks; unpowered or open nodes read low.

## 2. HW-010 check
| Item | Verdict |
|---|---|
| Hold-off 200..600 ms | Only by datasheet arithmetic (211..570 ms at 620n, total capacitor tolerance 5 % C0G/film). J and K in the sim are the same arithmetic (see M2), not independent evidence. Leakage of CT, DC bias, tD(no cap) min are not in it. Window margin 10.6 ms low / 30 ms high. |
| Restart after VBUS dip | Topologically yes (supervisor). Timing rests on an assumed 1 kohm CT discharge; the datasheet gives no discharge time. Dips between about 4.06 V and the IC minimum 4.5 V do not restart it (M1). **Not proven.** |
| Every step above the first gated | Yes, U3 and U4 get the same CC_OK and HOLD_OK nets (test + netlist). Step 1 has no gate by design. |
| Unpowered or open resolves to lowest | Mostly. Enable and select pull-downs present. But see H1: "IC unpowered" is no longer caught by CC_OK. HOLD_OK open at a gate pin has no pull-down (H3). |

## 3. Findings

### High
**H1. The unit-test model no longer describes the circuit; "IC unpowered -> lowest step" now rests only on the supervisor.** In v3a R1 goes to VBUS_IC. With VBUS gone and 3V3 still up (bulk capacitance on unplug), OUT1_N sits at 0 V, so U2 outputs CC_OK = 1 ("1.5 A advertised"). Only HOLD_OK (low, supervisor/R6 to 0 V) keeps the enable low. `step_enable("high_z", ...)` in `test_gate_logic.py` still assumes "IC unpowered = output high = not advertised" (the v2 pull-up to 3V3). The test passes for the wrong reason. Scenario: supervisor output stuck high (RISK-044) plus unplug/dip -> a step above the first is enabled by a dead IC. Before v3a this single fault was covered by the IC pull-up; v3a turned it into a common-mode dependency on U5. No test, no risk text for this change.

**H2. A VBUS dip drops the limit to 500 mA while the firmware does not know (SW-005/006/007 interplay).** 3V3 is held by bulk capacitance, the MCU keeps running with its select high and the LEDs at the raised level. The dip restarts the hold-off, the gate closes for 211..570 ms, and the limit part falls back to the lowest step with full LED load. The firmware has no readback of HOLD_OK, the enable, or the actual ILIM step. Result: limit part current-limits or the 5 V rail sags, brown-out, SW-007 back-off (60 s) after a mere cable wobble. Same at start-up: SW-005 settles after 5 reads over >= 500 ms; the gate may still be closed up to 570 ms from VBUS. If the MCU boots in under about 70 ms the firmware believes the step is raised while it is not. The spike never states the firmware must wait for the hold-off or read the state back. SYS-020 1 s is not exceeded (worst case about 0.63 to 0.7 s), but the hold-off adds a silent lower step.

**H3. Dip restart evidence (scenario H) is a function of an assumed constant.** I changed the off-state resistance of the delay node (`? 893k : 1k`): at 100 kohm H still passes; at 1 Mohm (tau 0.62 s) H fails (enable pulses at 560 ms), as do 10 Mohm and 100 Mohm. So H can fail and is not vacuous (the enable cannot be low in 560..640 ms for any reason other than the restart: the control "no dip" with 620n pulses at 560 ms; I ran it). But it proves only "if the real CT discharges in under about 50 ms, the restart works", and the discharge time is exactly what `datasheet-evidence-supervisor.md` A16 says is not found. The report says this ("a model, not evidence"), but RISK-044 mitigation and the spike recommendation read as if solved. The glitch is also placed 60 ms after the dip ends, giving the capacitor extra time; a dip immediately followed by the glitch is not run.

**H4. Tests committed with the fixture do not pass; the "18 tests pass" claim is not reproducible from the repo.** `tests/data/gate.net` is the v2 netlist (contains D1, no VBUS_IC on R1). On this commit `python3 -m unittest` with `GATE_NET=tests/data/gate.net` gives 5 failures and 1 error (kiutils missing). The 18 passes must come from an uncommitted regeneration (SKiDL not installed here). `test_write_sch.py` (determinism, label coverage) uses the same stale fixture, so the claim "writer produced the v3a schematic, ERC 0, parity 0, byte-identical" is not backed by anything in the commit. Evidence ID missing: no log of the run.

### Medium
**M1. Supervisor threshold is below the IC's operating minimum.** TPS3840DL40 resets at 3.94..4.06 V; TUSB321 VDD minimum is 4.5 V. A dip to 4.1..4.4 V (inrush through a long cable, weak charger; the USB sink floor is below 4.5 V) browns the IC out without restarting the hold-off, yet the IC may restart its own debounce and glitch OUT1 (the very fault the hold-off exists for; RISK-042). HW-010 says "restarts after every loss of the IC supply"; the IC's supply is lost below about 4.5 V, not 4.0 V. No scenario below 3.5 V or between 4.0 and 4.5 V. DL42 does not help (release up to 4.488 V against 4.5 V). Needs an IC POR threshold from TI, or a detection other than a threshold.

**M2. Scenarios J and K restate the formula.** The sim emulates the min and max datasheet constants by choosing CT = 340n and 921n with the typical constant, then checks the result against 200/600 ms. They pass by construction (340n x 618.9k = 210 ms) and would pass for any model with the right tD formula; they test neither the circuit nor the threshold (sim: 4.2 V, no hysteresis; real 3.94..4.285 V). Label "capacitor 5 % low" is wrong: 340n is not 620n - 5 % (589n). Value as evidence: arithmetic check only.

**M3. Single faults of the new part are uncovered and undetectable.** (a) U5 output stuck high / shorted to VBUS: hold-off gone for both steps, nothing alarms (RISK-044 says "not covered", fine, but see H1: it now also removes the unpowered-IC protection). (b) C1 shorted: tD about 50 us -> hold-off gone (silent). C1 open: tD about 50 us, same. Leaky C1 or X7R: shorter. (c) R6 open: HOLD_OK never rises, both steps dead, fail-safe but looks like "charger only gives 500 mA"; not detectable. (d) U2 output stuck high: CC_OK high, removes the IC gate for both steps (H1 of RV-008). (e) U3/U4 output stuck high: HW-010 lists as not covered (RISK-029); AND stuck low: fail-safe. (f) Shared nets: one fault in U2, U5 or R6 hits both steps. None of (a)-(d) is in `test_gate_logic.py`; the truth-table model has no hold-off input at all.

**M4. Placeholder U5 does not match the candidate it is named after.** `Conn_01x04` with SOT-23-6 footprint; TPS3840 is SOT-23-5 (RESET 1, VDD 2, GND 3, MR 4, CT 5, evidence A15), and the placeholder pin order (VDD1, GND2, CT3, OUT4) is different. The MR/NC pin is not modelled. If the schematic is treated as the design, the part is mis-wired. The tests assert the placeholder numbering, which would lock in the error. Also the 74LVC1G04 is placed in a SOT-23-5 footprint with the DBV pinout; correct.

**M5. Power-order coverage is thin and the report contradicts itself.** The sim has one order only (both rails ramp together in 1 ms; no 3V3-late, no 3V3-retained VBUS loss, no VBUS to 0, no 3V3 only). Voltage levels I checked on paper: HOLD_OK/CC-side 5.5 V into 74LVC1G11/G04 inputs is within 5.5 V recommended / 6.5 V absolute and Ioff <= 10 uA at VCC = 0 (read in the evidence files, not re-read by me); R1 pull-up now stays within VDD + 0.3 V of the TUSB321; U2 output at VCC = 0 is unspecified, covered only by pull-downs R2/R3 and unpowered ANDs. VBUS overshoot above 6.5 V on hot plug is not discussed (ESD part not in the fragment). The report's "Not run on version 3" list still says the 3.3 V pull-up question is open and the AND-input back-feed "not checked", but 3a and the gate-logic evidence address both; stale.

### Low
**L1. Tautological tests persist (v2 finding L1 unchanged).** `step_enable` implements the formula the test asserts; `gate_logic_powered=False` returns a constant; `test_faults_resolve_to_lowest_step` does not exercise any netlist. Netlist tests check the wiring the generator wrote (circular, but they do catch a regression of pins, and they now use exact-pin asserts for U5/R6/C1).
**L2. Stale or misleading documents.** Report sections 1-4 still describe v1 (two 74LVC1G08, 9 tests, 3.3 V IC); `gen_gate.py` docstring says "Version 3", the sim header says "Scenarios A to I" (J, K exist); `holdoff_tolerance.py` is the superseded RC model, kept in `sim/` and runnable, but the 600 ms claim of F7 ("overlap") is based on it; `run_powerup.sh` carries two contradictory "Columns:" comments; Rev. C vs SLLSF53 mismatch noted by the evidence file only.
**L3. R6 150k and R1 100k on the same VBUS: leakage and loading.** R6 into VOL: 5.5 V/150k = 37 uA, fine. Pull-up to VBUS_IC means HOLD_OK/OK see VBUS-level high into 3.3 V logic: VIH is fine, input current into clamp at VCC dips (3V3 sagging while VBUS up) not analysed.
**L4. 2N7002 drive at 3.3 V** (Vgs(th) max 2.5 V) and the AND output high level at VCC sag (brown-out) not checked; carried from v2.

## 4. Status of the v2 findings (checked in code, not taken from the report)
| v2 finding | Now |
|---|---|
| C1 script passes on simulator error | **Fixed.** `isnum` check; `window`/`late` also fail on non-number. I did not feed a broken netlist but read the logic. |
| H1 D1 does not restart hold-off | **Fixed in topology**, timing unproven (H3, M1 here). |
| H2 leakage/tolerance not in budget | **Open.** Supervisor CT leakage still "not found"; C0G 5 % assumed; new risk text exists (RISK-044). |
| H3 footprint SOT-23-5 on 6-pin gate | **Fixed** (SOT-23-6; test is a string check). New footprint error on U5 (M4). |
| H4 no safe default, silent faults | **Partly.** HOLD_OK default is now "low when unpowered"; faults (stuck, C1) still silent (M3). No pull-down on HOLD_OK at the gate pin (open U5 + R6 open leave R6/U5 side floating? R6 gives a defined high; an open trace at pin 6 floats it). |
| M1 pull-up to 3V3 above VDD + 0.3 V | **Fixed** (R1 to VBUS_IC). Side effect: H1 here. |
| M2 5 V into 3.3 V AND | **Addressed on paper** by the evidence files; not simulated. |
| M3 hold-off starts at VBUS, thin margin to 133 ms | **Open**, margin now 211 ms minimum vs 133 ms (better). PORT/VBUS_DET path still absent from the fragment; CC_RESERVED left open. |
| M4 arithmetic of F10 | **Replaced** by datasheet constants; `holdoff_tolerance.py` is orphaned. |
| M5 ILIM twice | **Fixed** (one net, test). |
| L1 tautological tests | **Open.** |
| L2 stale report | **Open** (L2 here). |
| L3 uncovered single faults | **Open**; new ones added (M3). |
| L4 ideal thresholds, assumed glitch | **Open**; glitch still assumed, IC datasheet does not state OUT1 before first debounce. |

## 5. What I did not check
Datasheets themselves (I used the evidence files, which are unreviewed Draft); KiCad symbol pin numbers; ERC, parity, the writer, ngspice beyond the four mutations; the real SOT-23-5/6 footprints; TUSB321 behaviour below 4.5 V; MCU boot time and SW-005 implementation (no firmware read, only the requirement text); source-side behaviour on a dip; EMC, ESD, and regulatory aspects; thermal.
