# Analysis: heat of the 3V3 linear regulator with realistic Wi-Fi use (HW-010 proposal, HW-013)

- **Date:** 2026-11-07. **Author:** assistant. **Status:** Draft analysis. Nothing Approved, nothing measured.
- **Script and tests:** `hw/sim/scripts/regulator_heat.py`, `hw/sim/scripts/test_regulator_heat.py` (6 tests pass; ruff clean).

## Question
The owner chose the TLV75733P linear regulator on 2026-11-07, on condition that a Wi-Fi duty-cycle heat estimate shows the heat is acceptable in the closed PETG housing.

## Model
Loss = (5.5 V - 3.3 V) x average 3V3 current + the ground-current term. Input 5.5 V is the worst case. Module currents are read from the datasheets (`spike-7-5-power-budget-paper.md`): 28 mA modem-sleep with CPU, 82 mA receive, 350 mA transmit. Other 3V3 loads 5 mA (assumed). **The duty cycles are assumptions**, because the datasheets give only 100 % duty. Junction temperature = 35 degC ambient + a housing air rise (0, 20 or 40 K; unknown, HW-013 measures it) + thermal resistance x loss. TLV757P thermal resistance (SBVS322C table 5.4, read): DBV package 100.8 degC/W on the EVM board and 231.1 on the JEDEC board; DYD package (exposed pad) 60.3 and 92.5. Limit: 125 degC, with a 15 K margin (110 degC).

## Result (script output; "over" = above 110 degC)
| Scenario | I avg (mA) | P (mW) | Package / board | Tj at +0 K | +20 K | +40 K |
|---|---|---|---|---|---|---|
| connected, push model | 39 | 86 | DBV EVM | 44 | 64 | 84 |
| connected, push model | 39 | 86 | DBV JEDEC | 55 | 75 | 95 |
| connected, push model | 39 | 86 | DYD EVM | 40 | 60 | 80 |
| connected, push model | 39 | 86 | DYD JEDEC | 43 | 63 | 83 |
| polling every few s | 60 | 132 | DBV EVM | 48 | 68 | 88 |
| polling every few s | 60 | 132 | DBV JEDEC | 65 | 85 | 105 |
| polling every few s | 60 | 132 | DYD EVM | 43 | 63 | 83 |
| polling every few s | 60 | 132 | DYD JEDEC | 47 | 67 | 87 |
| firmware download (minutes) | 157 | 345 | DBV EVM | 70 | 90 | 110 |
| firmware download (minutes) | 157 | 345 | DBV JEDEC | 115 **over** | 135 **over** | 155 **over** |
| firmware download (minutes) | 157 | 345 | DYD EVM | 56 | 76 | 96 |
| firmware download (minutes) | 157 | 345 | DYD JEDEC | 67 | 87 | 107 |
| bound: TX 100 % (not a real use) | 355 | 781 | DBV EVM | 114 **over** | 134 **over** | 154 **over** |
| bound: TX 100 % (not a real use) | 355 | 781 | DBV JEDEC | 216 **over** | 236 **over** | 256 **over** |
| bound: TX 100 % (not a real use) | 355 | 781 | DYD EVM | 82 | 102 | 122 **over** |
| bound: TX 100 % (not a real use) | 355 | 781 | DYD JEDEC | 107 | 127 **over** | 147 **over** |

## Reading
- For **normal use** (connected with push, or polling every few seconds) the loss is 0.09 to 0.13 W and every package stays at or below 105 degC even with a 40 K housing rise. The regulator is not a thermal problem in normal use.
- A **firmware download of several minutes** (30 % transmit, 50 % receive: 0.35 W) is fine in the DYD package and in the DBV package on a good board, but **fails in the standard DBV package on a poor board** (115 degC with no housing rise).
- **Continuous transmit** (0.78 W, a bound, not a real use) fails in most cases, including the DYD package with a hot housing. It can be excluded only by firmware: the transmit duty is a design property, not a measurement.
- My earlier statement in the shortlist, "up to about 1 W, junction rise 89 to 97 K", used the 567 mA worst case with the better board figures. With the standard DBV package on the JEDEC board the worst case is higher. The shortlist is corrected.

## Recommendation
Keep the linear **TLV75733P in the DYD package (exposed thermal pad)**, with a copper pour under it, and put two limits in the requirements: (1) the firmware limits transmit duty during updates so that the 3V3 average stays at or below [150] mA, and (2) HW-013 measures the junction (case) temperature of the regulator at the update load. The buck converter stays the fallback if the measurement fails. Whether the DYD variant has the stock and the price needed is not checked.

## Not done
No measurement; duty cycles assumed; the housing rise is a parameter, not a result; LED heat and the regulator heat are not coupled in this model; stock of the DYD variant not read.

## Owner choice of 2026-11-07 and what it implies
The owner chose the **standard package (DBV), firmware limit only**, not the DYD pad package. The highest average 3V3 current that keeps the junction at or below 110 degC (script output):

| Board / housing rise | +0 K | +20 K | +40 K |
|---|---|---|---|
| DBV, EVM-class board (100.8 degC/W) | 338 mA | 248 mA | 158 mA |
| DBV, JEDEC-class board (231.1 degC/W) | 147 mA | 108 mA | 69 mA |

So the firmware rule has to be written for the weakest case: **an average 3V3 current of at most [70] mA** if the board is poor and the case is 40 K warm, or about [150] mA if the board spreads heat well and the case rise is small. A firmware download at 30 % transmit and 50 % receive averages 157 mA, so it needs a lower transmit duty (about 8 % transmit with 20 % receive averages 70 mA) or a slower download. The numbers become real only when HW-013 measures the housing rise and the regulator temperature. A new requirement for the transmit-duty limit is not written yet (skill `write-requirements`); until it exists, no firmware work depends on it.
