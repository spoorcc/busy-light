# Datasheet evidence for the CC detection IC of ADR-0016

- **Status:** Draft
- **Date:** 2026-11-04
- **Author:** Claude. Not reviewed. Nothing here is Approved or Accepted. No part is chosen (ADR-0016 item 3).
- **Related:** ADR-0016 (item 3 checks), HW-003, HW-010, RISK-026, RISK-042, RISK-043, spike `docs/verification/reports/spike-hw-gate-fragment.md`
- **Labels:** each fact is marked **read** (read in a datasheet text on 2026-11-04) or **not found**. The PDFs were downloaded to a scratch folder and are not committed (ADR-0015: vendor datasheets are linked, not committed).

## Sources
- **S1** TI TUSB321, SLLSEO6C, June 2015, revised August 2018 (Rev C): https://www.ti.com/lit/ds/symlink/tusb321.pdf (10 pages as served; the page count and the revision are what the file says).
- **S2** NXP PTN5150, Rev. 1, 9 December 2016, from a distributor mirror: https://static.chipdip.ru/lib/909/DOC011909835.pdf. **This is the older PTN5150, not the current PTN5150A**, and it is not from the NXP site (NXP refused the download). Use only as a hint for a second source.
- Not obtained: the PTN5150A data sheet itself; the Type-C specification; the TI CC controller selection guide (March 2026, named by a search result, not opened).

## TUSB321 (S1), UFP mode
| # | Item | Fact | Status |
|---|------|------|--------|
| 1 | Supply | VDD 4.5 to 5.5 V; about 100 uA unattached and active (VDD = 5 V, PORT low). **Powered from VBUS, not from 3.3 V.** The spike assumed 3.3 V; corrected in the spike report | read |
| 2 | Temperature | Operating free-air 0 to 70 C. The LCSC listing (-40 to 85 C, ADR-0016 E15) conflicts; the datasheet governs | read |
| 3 | CC pins | Absolute maximum -0.3 to 6 V (Rev C changed this from VDD + 0.3). ESD: HBM 7000 V (the CDM value was not read). Rd 4.6 to 5.6 kohm. Closes the CC pin rating question of RISK-026 for this part; a VBUS short to CC above 6 V is not covered by the rating | read |
| 4 | Detection thresholds in UFP mode | default 0.15 / 0.20 / 0.25 V; 1.5 A: 0.61 / 0.66 / 0.70 V; 3 A: 1.169 / 1.23 / 1.29 V (min / typ / max). Matches ADR-0009 E5 | read |
| 5 | Outputs | OUT1 and OUT2 are open drain. OUT1 high = default, low = 1.5 A or 3 A; OUT2 low = 3 A only. Table 2 also says OUT2 is high (unattached) or low (attached) for default current at 900 mA (USB 3.1): so OUT2 is not a clean 3 A signal, and the gate uses OUT1 only. VOL at most 0.4 V at 1.6 mA; external pull-up at most 200 kohm | read |
| 6 | Output pin rating | OUT1 and OUT2 absolute maximum -0.3 V to VDD + 0.3 V. A pull-up to a 3.3 V rail is inside the rating only while the IC is powered; with the IC unpowered and 3.3 V present the pin exceeds the rating. Both rails derive from VBUS, so the order is a design point to check (HW-003) | read |
| 7 | Mode pin | PORT low = UFP (sink only). PORT open = DRP: the part then toggles and presents a source pull-up on CC. For a sink-only device the pin must be tied to GND; the state is sampled when VDD is active. Internal pull-up 588 kohm, pull-down 1.1 Mohm | read |
| 8 | Attach timing | Power-on default CC debounce 133 ms (typ); VBUS detect debounce 2 ms; attach needs VBUS_DET above a threshold of 2.95 to 3.80 V through an external 887 kohm resistor (855 to 920 kohm); VBUS_DET pin abs max 4 V | read |
| 9 | Output state at power-up | After power-up the part is in Unattached.SNK and "all IOs are operational". **The level of OUT1 and OUT2 before the first debounce completes is not stated.** The glitch of scenario C in the spike remains an assumption | not found |
| 10 | VCONN | The part has a VCONN switch (1.25 ohm, 200 mA). Treatment of the VCONN pin on a sink-only board not read | not found |
| 11 | Package, price, stock | X2QFN-12 1.6 x 1.6 mm (S1, ADR-0009 E14). Stock and the "AI variant unavailable" remark from a forum thread are not verified | not found |

## PTN5150 (S2, older revision), as a second-source hint
| # | Item | Fact | Status |
|---|------|------|--------|
| 12 | Supply and temperature | VDD 2.7 to 5.5 V; ambient -40 to +85 C | read |
| 13 | Thresholds | UFP: default 0.15 / 0.2 / 0.25 V; 1.5 A 0.61 / 0.66 / 0.70 V; 3 A 1.16 / 1.23 / 1.31 V | read |
| 14 | Outputs | OUT1 and OUT2 exist only when the ADR pin selects non-I2C mode (ADR mid or floating); they report the detected Rp current value. Polarity not read | read, partly |
| 15 | Pin ratings | CC1, CC2 and control pins: up to VDD + 0.3 V (the minus sign of the lower limit was lost in the text extraction); ESD HBM 7000 V on CC1, CC2, VBUS_DET, 2000 V on other pins; CDM 500 V. VBUS_DET 28 V | read |
| 16 | CC debounce | 120 ms typ | read |

## What this changes
- **RISK-026:** for TUSB321 the CC pin rating is 6 V absolute maximum and 7 kV HBM; the remaining question is a fault above 6 V on CC (a damaged cable or source).
- **RISK-043:** the 0 to 70 C limit of the TUSB321 is confirmed in the datasheet; the PTN5150 family states -40 to +85 C (older revision, not PTN5150A), which would remove the temperature conflict if its current revision and output polarity match. This gives a named second source to evaluate; none is chosen.
- **Gate design (spike):** the IC runs from 5 V and the output pull-up goes to 3.3 V; the logic parts must accept the pull-up level (they do at 3.3 V) and the power order must hold (item 6).
- **Hold-off:** the debounce of 133 ms gives the earliest time that OUT1 is meaningful. SW-005 asks for [5] equal reads over at least [500] ms, which exceeds it. The hardware gate alone has no hold-off (spike scenario C).
- **HW-003 and HW-010 test list:** tie PORT to GND and test the PORT-open fault (item 7); test OUT1 at the band edges 0.61 V and 0.70 V; test the 5 V to 3.3 V power order with the pull-up (item 6).

## Not done
No datasheet of PTN5150A, no TUSB321 evaluation board test, no check of the Type-C specification, no stock or price check.

## Note 2026-11-07: TUSB321 CC debounce (RV-010 finding 3)

Read in the TI datasheet SLLSEO6C (revision of August 2018, section 6.6 Switching Characteristics): tCCCB_DEFAULT, "Power on default of CC1 and CC2 voltage debounce time", **133 ms typical, no minimum and no maximum stated**. tVBUS_DB is 2 ms typical. The datasheet states no maximum, so the maximum CC debounce of the TUSB321 is not known from the datasheet. A newer revision was not looked for. The "120 ms typ" in row 16 above belongs to the PTN5150A rows (items 12 to 16), not to the TUSB321, so the two typical values do not disagree. Whether the USB Type-C specification limits the debounce (a range of 100 to 200 ms was quoted by the goldfish reviewers from memory) was not checked against the specification text.
