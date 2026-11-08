# Analysis: bounds for the bulk capacitance of the +5V rail (HW-014 draft, HW-004, HW-010)

- **Date:** 2026-11-08. **Author:** assistant. **Status:** Draft analysis. Nothing Approved, nothing measured. Goldfish review RV-013 (2026-11-08) rejected the first draft; this is the redraft after the owner decision of the same day (lower bound = part makers' minimum, spare footprints HW-016); not yet reviewed again.
- **Script and tests:** `hw/sim/scripts/bulk_cap_bounds.py`, `hw/sim/scripts/test_bulk_cap_bounds.py` (9 tests pass after the redraft).

## Question
C3 ("10u tbd") and C4 ("bulk tbd") on +5V have no designed value. The PCB spike places them as 0805 and 1206 while the
schematic says 0603 (two `footprint_symbol_mismatch` findings in the DRC report of the ring6 batch, 2026-11-08; `pcb_full.FOOTPRINT_OVERRIDE`). No requirement gives a value: ADR-0010 assumed 100 uF,
and `analysis-sw005-holdoff-timing.md` lists the gap as G10. This analysis gives a lower and an upper bound, so the
owner can set them in a requirement before a part and a size are chosen.

## Capacitors on the rails today (generator `layout_full.py`, 2026-11-08)
| Rail | Parts | Values |
|---|---|---|
| +5V | C3, C4, C5 (regulator input), C8 to C23 (one per LED) | 10u tbd, bulk tbd, tbd, 16 x 100n |
| +3V3 | C6 (regulator output), plus the capacitors inside the module (not known) | tbd |
| VBUS_IC | C2 | 1u tbd |

## Facts (read 2026-11-08; local datasheets are not committed, ADR-0015 item 8)
| ID | Fact | Source |
|---|---|---|
| F1 | IOS,min = 25230 / R^1.016 mA (R in kohm); at 47.0 kohm + 0.1 %: 504 mA | TPS2553 SLVS841G eq. 3; HW-010 R_ILIM1 |
| F2 | Overcurrent FAULT deglitch 3 / 7.5 / 11 ms (min / typ / max). The deglitch exists so that FAULT is "not accidentally asserted due to normal operation such as starting into a heavy capacitive load" | SLVS841G electrical characteristics (FAULT flag) and 8.3.3 |
| F3 | Output rise time 1.1 ms typ, 1.5 ms max at VIN 6.5 V (1 uF, 100 ohm); no minimum given | SLVS841G electrical characteristics (tr) |
| F4 | TPS2553 (no suffix) holds the current at IOS in overload, with no foldback; it turns off only at 135 C junction (min) | SLVS841G 8.3.1 |
| F5 | TLV757P: input capacitor 1 uF or larger; nominal capacitance after derating above 0.47 uF | TLV757P SBVS322C pin table and note 1 |
| F6 | TPS3840: VIT- accuracy -1.5 % to +1.5 % (-40 to 125 C); DL40 = 4.0 V, so 4.06 V at most | TPS3840 electrical characteristics (VIT- accuracy) |
| F7 | USB 2.0 7.2.4.1: at most 10 uF (in parallel with 44 ohm) at the device end of the cable, "plus any capacitive effects visible through the regulator"; with more capacitance the device "must incorporate some form of VBUS surge current limiting, such that it matches the characteristics of the above load" | USB 2.0, USB-IF package `usb_20_20240604.zip` (sha256 ffb1f8f24b855862e2405e425b7175a015b53a5f53f62e6e9144767d5c7827e2) |
| F8 | Device Capacitance ECN: CRPB 1.0 to 10.0 uF on the VBUS pin over 0 to 5.25 V; the minimum holds "regardless of whether the USB device is powered or unpowered"; the 10 uF maximum is the attach load of 7.2.4.1 | same package, `Device Capacitance ECN.pdf` |
| F9 | VBUS at the device 4.40 V (low-power port) or 4.75 V (high-power port) to 5.25 V | USB 2.0 table 7-7 |

Not read: the USB-IF compliance test specification (the inrush test and its charge limit), the USB Type-C
specification (vSafe5V maximum, sink rules for VBUS capacitance), any capacitor DC-bias curve.

## Lower bound: the part makers' minimum (owner decision 2026-11-08)
The first draft derived a lower bound from a load step against the cable inductance. RV-013 found that model unsound:
it had no cable resistance (a static drop that no capacitance recovers), the LED PWM (1.0 to 1.2 kHz, full-current
edges that the firmware cannot ramp) makes the step larger than assumed, and the CC IC (specified from 4.5 V) and the
USB 2.0 hub transient (down to 4.07 V) mean a capacitance cannot keep the supervisor from tripping. A capacitance that
smooths the LED PWM itself would need about 1 A x 0.5 ms / 0.1 V = 5 mF, far above the upper bound. A capacitance
can only damp the ringing on each PWM edge; that estimate (4 to 50 uF, depending on the cable) rests on assumed cable
values. The owner chose (2026-11-08): the lower bound is the part makers' minimum (F5: 1 uF nominal, more than
0.47 uF effective at the TLV757P input), the prototype gets spare footprints (HW-016), and the prototype measurement
(HW-014 criterion 3) decides whether more is fitted.

## Upper bound: start-up without a false FAULT
At plug-in the TPS2553 charges the rail. No minimum rise time is given (F3), so the bound assumes the worst case:
the whole charge flows at the lowest current limit of step 1 (F1; the gate holds step 1 during the hold-off).
The time in current limit must stay below the shortest overcurrent deglitch (F2, 3 ms) with a 50 % margin, or
FAULT_N reports a fault at every plug-in (GATE_OK_RB reads low, ADR-0018). The 3V3 rail charges through the
regulator in the same window.

C_max = (1.5 ms x (I_OS,min - I_start) - C_3V3 x 3.3 V) / 5.5 V

ASSUMED: I_start = 0.10 A (processor in reset, LEDs dark, regulator quiescent current); C_3V3 = 10 uF, whose charge is
counted in the same window (the timing of the regulator's own start-up is not modelled); 5.5 V as the highest charge voltage
(Type-C vSafe5V maximum, not read here).

Result: C_max = 104 uF. Proposed upper bound: **[100] uF effective at 0 V bias** (time in limit 1.44 ms).

Sensitivity (script output): the bracket holds only for a small start load and a small 3V3 capacitance. HW-014
criterion (1) therefore reruns the script with the chosen values.

| I_start (A) | C_3V3 10 uF | C_3V3 22 uF | C_3V3 47 uF |
|---|---|---|---|
| 0.05 | 118 uF | 111 uF | 96 uF |
| 0.10 | 104 uF | 97 uF | 82 uF |
| 0.20 | 77 uF | 70 uF | 55 uF |
| 0.30 | 50 uF | 42 uF | 27 uF |
The bound is taken at 0 V bias because a ceramic capacitor has its highest capacitance there, at the start of the ramp.

Other limits checked, none binding:
- Energy: the switch dissipates about the stored energy, 0.5 x C x V^2 = 1.5 mJ at 100 uF and 5.5 V. This is far
  from the thermal shutdown (F4). Not calculated against the package thermal mass.
- Decay after unplug (HW-010 test item 8): 100 uF at 0.1 A falls 1 V in about 1 ms. A larger capacitance does
  not make the unplug decay a timing problem for the gate. The hold-up for SW-009 stays far below 1 ms, as
  `analysis-sw005-holdoff-timing.md` says.

## USB rule (F7, F8): what it does and does not say
The +5V capacitance sits behind the switch. The switch limits the current (F4) and ramps the output (F3), which is
"some form of VBUS surge current limiting". Whether the result "matches the characteristics" of 10 uF in parallel with
44 ohm is decided by the USB-IF inrush test, which was not read. **Risk:** if that test counts all charge drawn in the
attach event against a 50 uC limit (a secondary source, an Analog Devices/Maxim USB charging overview, names 50 uC; the USB-IF text was not read), 100 uF at 5 V (500 uC) fails it. The
bench inrush test (HW-014 acceptance) and a read of the compliance test specification close this before layout.

## Finding outside the question: C2 on VBUS_IC
The ECN (F8) needs at least 1.0 uF on the VBUS pin over 0 to 5.25 V. C2 is "1u tbd" in 0603. A nominal 1 uF
ceramic loses capacitance at 5 V bias and has a tolerance of typically 10 %, so it is below 1.0 uF at 5 V. C2 needs
a larger nominal value (about 2.2 to 4.7 uF), and the sum on VBUS_IC must stay at or below 10 uF. This is not in
HW-014. The owner chose a separate requirement on 2026-11-08: HW-015 (Draft). For C24 to C26 behind the series
resistors the bias is the voltage of their own node, at most the 5.1 V zener voltage. The protection parts (TVS1,
U6, zeners) add their junction capacitance from their datasheets.

## Limits of this analysis
- No simulation, no bench measurement. The start-up load and the 3V3 capacitance are assumptions; the sensitivity
  table shows how much the upper bound depends on them.
- The bounds give an effective capacitance. The part choice needs the manufacturer DC-bias curve of the chosen part
  (not read). That choice sets the footprint of C3 and C4.
- Open from RV-013 for the upper bound: the USB-IF inrush test text (finding 5), the surge decision S1/S2/S3
  (finding 9), reverse current at unplug (finding 11), hot-plug ringing on VBUS_IC (finding 10).
