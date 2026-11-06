# JLCPCB stock check for the HW-010 gate parts (2026-11-06)

> **Correction (2026-11-06, later the same day).** This entry was written from a branch that lacked the second owner
> record of 2026-11-05 (`owner-decisions-2026-11-05-b.md`) and the earlier `stock-check-ilim-holdoff.md`. It checked
> superseded values (56.9 kohm, 27.7 kohm, a MOSFET switch). The capacitor "not found" results are wrong for 1206:
> my filter covered only the label "C0G、NP0", and the 1206 parts are listed under other C0G and NP0 labels. See
> `2026-11-06-decisions-and-live-stock.md` for the live results and the decisions. The text below is kept unchanged.

Scope: open items of the owner-confirmed proposals of 2026-11-05 (resistors, hold-off capacitors, MOSFET).
Method: read-only searches on the JLCPCB parts library in a browser session. Nothing was added to a cart or an
account. Stock numbers change daily; treat them as a snapshot of 2026-11-06. Prices were not recorded.

## Resistors, 0.1 % (HW-010 proposal 1)

| Value | In stock | Notes |
|---|---|---|
| 47.0 kohm | Yes, many | 0603 examples: Yageo `RT0603BRD0747KL` C326725 (17,621), Viking `ARG03BTC4702` C335087 (18,831), Uniroyal `TC0350B4702T5F` C18186127 (20,216). All Extended. |
| 27.7 kohm | Two parts | Yageo `RT0805BRD0727K7L` C865349 (0805, 3,851); Yageo `RP0402BRD0727K7L` C7294198 (0402, 19,074). No 0603. |
| 56.9 kohm | **None** | Every 0.1 % chip part (Vishay, KOA) is pre-order or consignment only. |

Consequence: the E192 set cannot be bought from stock for the 56.9 kohm step, and the 27.7 kohm step fixes the
footprint at 0805 or 0402. Options (not decided): pre-order (lead time and minimum quantity not checked), E96
neighbours (needs a new `analysis-ilim-steps` run, the current limit window changes), series or parallel
combinations of stocked values. This reopens a value the owner confirmed, so it is an owner decision.

## Hold-off capacitors, C0G, 5 % (proposal 6: 220 nF + 220 nF + 150 nF + 33 nF)

Found with the category filters (MLCC SMD, In Stock, Tolerance 5 %). The text search does not handle
capacitance values (it returned unrelated parts and stale tables) and gave no usable result.

- 1210, C0G, 5 %, in stock, all TDK Extended: 100 nF 50 V `C3225C0G1H104JT000N` C338021 (4,576);
  47 nF 100 V `C3225C0G2A473JT000N` C342675 (4,770); 33 nF 630 V `C3225C0G2J333JT000N` C360348 (2,756) and
  `CGA6P4C0G2J333JT0Y0N` C432954 (1,002).
- 33 nF 100 V `C3225C0G2A333JT000N` C342701 shows 1 piece and is counted as unavailable.
- No C0G 5 % part at 150 nF or 220 nF was found in 1210.
- 1206: only three in stock (20 pF, 22 pF, 10 nF; Yageo). Only the label "C0G、NP0" was filtered. JLCPCB also
  uses "C0G", "COG" and "NP0" as separate labels, so a 1206 part under those labels is **not excluded**.

Consequence: the proposed set cannot be bought as written. A set made of 100 nF, 47 nF and 33 nF C0G parts in 1210
would reach the same total with more parts; the hold-off window of 200 to 600 ms must then be checked again.
Not decided.

## MOSFET for the ILIM select switches (replace the 2N7002)

Datasheets read: onsemi BSS138-D, AOS AO3400A Rev 3.1. Not read: 2N7002, the Diodes and Nexperia BSS138 variants.
JLCPCB stock (search listing): onsemi `BSS138` C52895 (73,894, Extended), Diodes `BSS138-7-F` C40912 (406,284,
Extended), Nexperia `BSS138P,215` C75547 (330,539, Extended), AOS `AO3400A` C20917 (893,453, **Basic**).
Leakage bound, the missing ILIM pin voltage and the open actions are in
`hw/sim/analysis-ilim-switch-leakage.md`.

## Tool notes

- KiCad: `kicad-cli` is installed and `import pcbnew` works (KiCad 10.0.6). Scripting of the schematic is not
  checked yet. FreeCAD (`FreeCADCmd`) is not installed.
- JLCPCB search pitfalls: values in nF or uF are not matched; the result table can show the previous query after a
  navigation (wait and compare the heading); the browser `find` tool reported "In Stock" for parts that had no
  stock (read the page text instead). Filter lists re-render after each click, so element references go stale.
- The 2026-11-06 correction of rule 12 (CAD changes by scripting, never GUI) is in `CLAUDE.md`.
