# Analysis: protection of the TUSB321 CC1 and CC2 pins (options for the owner; HW-010, ADR-0016)

- **Date:** 2026-11-07. **Author:** assistant. **Status:** Draft options. Nothing chosen, nothing Approved, nothing measured.

## Question
The TUSB321 CC1 and CC2 pins have a 6 V absolute maximum (SLLSEO6C table 6.1, read) and face the cable directly. How are they protected?

## Facts
- The chip itself has an ESD rating of 7000 V HBM (table 6.2, read) and the datasheet says it has "limited built-in ESD protection" (handling note, read). CC1 and CC2 abs max 6 V; VBUS_DET tolerates 28 V.
- The product is a sink with no Power Delivery talk. A Power Delivery source stays at 5 V until a sink negotiates, so a cable fault that shorts VBUS to a CC pin sees 5 V (up to about 5.5 V) from this product's point of view. That is inside the 6 V rating. A 9 to 20 V exposure needs a sink that negotiates, which this one does not. This is my reasoning from the USB Type-C and Power Delivery behaviour as I know it; the USB-IF documents were not read here.
- The real exposure is **ESD on the CC pins at plug-in** (system level, IEC 61000-4-2) and cable-end hot-plug transients. The design already has a USBLC6-2 ESD part on D+ and D- (`spike-full-board-schematic.md`); none is drawn on CC1 and CC2 (the schematic generator ties them to the connector and the chip only, `layout_full.py` line 351 onwards, not fully checked).

## Options
| # | Option | For | Against |
|---|---|---|---|
| P1 | A low-capacitance 5 V ESD array on CC1 and CC2 (one extra SOT-23-6 part such as the USBLC6-2 class) | cheap, standard, helps the EMC and ESD tests of the RED/EMCD file | an ESD part clamps at 10 V or more at a strong pulse (same effect as TVS1), so it does not make the 6 V pin safe alone; adds capacitance on CC |
| P2 | Nothing extra; rely on the chip's 7 kV HBM and run the IEC 61000-4-2 test at the end | no part | a failed ESD test late means a board change; the chip's own rating is for handling, not for the system test |
| P3 | P1 plus a 100 ohm series resistor in each CC line | limits current into the pin during a pulse; pin stays below 6 V for short pulses (same method as the supply pins) | the Type-C rules limit series resistance on CC; the TUSB321 CC pin voltage thresholds could shift; needs the datasheet's application guidance, which I have not read |

## Recommendation
P1 now (one part, standard practice), with the ESD test as an explicit TC. Decide P3 only after the TUSB321 application guidance and the Type-C resistance rules are read.

## Not done
USB Type-C specification not read; TUSB321 application section not read; no simulation; no ESD test; schematic CC wiring not fully checked.

## Owner choice of 2026-11-07 and a caution
The owner chose **P3, an ESD part plus series resistors**, before the open reading was done. Notes on what I could and could not check:
- TUSB321 datasheet (read): it gives no guidance for series resistors on CC1 and CC2 or for external ESD parts. The pin has an internal pull-down Rd of 4.6 to 5.6 kohm. A 100 ohm series resistor adds 2 % to the Rd seen by the source, which is small against the Type-C Rd tolerance as I know it (the Type-C document was not read, so the exact limit is not checked).
- **A series resistor does not by itself keep the pin under 6 V.** With the Rd of about 5.1 kohm to ground, 100 ohm in series passes almost all of a pulse to the pin (98 %). The resistor helps only by limiting the current into the chip's own ESD structures (7 kV HBM), and the external ESD part takes the energy. Whether this holds for an IEC 61000-4-2 pulse is shown only by the ESD test. This is a correction of the optimistic wording in option P3 above.
- Recommendation kept: place the ESD part at the connector, the 100 ohm resistors between it and the chip, and add an ESD test case (IEC 61000-4-2, to be written) before the layout is frozen.
