# ILIM select MOSFET: off-state leakage bound (HW-010, ADR-0010, ADR-0016)

Status update 2026-11-06: the owner kept the TMUX1101DCKR analog switch (decision 5 of the journal entry
`docs/journal/2026-11-06-decisions-and-live-stock.md`). This analysis stays as the conditional BSS138 fallback
(fits the 118 nA budget of the second owner record only if V_ILIM is about 0.85 V or more and the part stays near 25 degC).

Status: analysis, draft. Not reviewed. Supports the open item "replace the 2N7002 by a part with stated low-voltage
leakage" of the owner-confirmed proposals of 2026-11-05. Code: `scripts/ilim_switch_leakage.py`, test:
`scripts/test_ilim_switch_leakage.py` (5 tests, pass).

## Question

A select MOSFET that is off leaks a current from the ILIM node to GND. This adds to the current that the TPS2553
sources out of ILIM and raises the current limit by about the same fraction (IOS is proportional to about 1/R, ADR-0010
E3). How large may the leakage be so that it does not spoil the 0.1 % resistors?

## Method

Relative rise of the limit = n_off x I_leak x R_total / V_ILIM (formula and assumptions in the script header).
Resistors: R1 47.0 kohm, R2 56.9 kohm, R3 27.7 kohm (proposal, not Approved). Steps are exclusive.

## Facts used (read from datasheets in this session)

| Part | Vgs(th) max | IDSS max | Rds(on) | Source |
|---|---|---|---|---|
| BSS138 (onsemi) | 1.5 V (1 mA) | 100 nA at 30 V; 0.5 uA at 50 V; 5 uA at 125 C, 50 V | 6.0 ohm at 4.5 V; no value at 3.3 V | onsemi BSS138-D |
| AO3400A (AOS) | 1.45 V (250 uA) | 1 uA at 30 V (the extracted text shows "mA" for the micro sign) | 48 mohm at 2.5 V | AOS AO3400A Rev 3.1 |

Not read: the 2N7002 datasheet, the Diodes and Nexperia BSS138 variants.

TPS2553 (SLVS841G): the pin carries "a regulated voltage" (section 8); **no numeric value is stated**. ILIM source
current maximum 1 mA; pin voltage range -0.3 to 7 V.

## Result

Largest leakage per switch for a 0.1 % error (nA), by step and assumed V_ILIM:

| Step | R_total | n off | 0.5 V | 1 V | 2 V |
|---|---|---|---|---|---|
| 1 (Q2, Q3 off) | 47.00 kohm | 2 | 5.3 | 10.6 | 21.3 |
| 2 (Q2 on) | 25.74 kohm | 1 | 19.4 | 38.9 | 77.7 |
| 3 (Q3 on) | 17.43 kohm | 1 | 28.7 | 57.4 | 114.8 |

Error if the leakage equals the datasheet IDSS maximum (upper bound, step 1, the worst step):

| Part | 0.5 V | 1 V | 2 V |
|---|---|---|---|
| BSS138, 100 nA (30 V) | 1.88 % | 0.94 % | 0.47 % |
| AO3400A, 1 uA (30 V) | 18.8 % | 9.4 % | 4.7 % |

## Conclusion (what this does and does not show)

- The datasheet IDSS limits are measured at 30 V or more. They are **bounds**, not leakage at the ILIM voltage.
  Leakage at about 1 V is expected to be far lower, but no datasheet states it, so this analysis cannot prove the
  0.1 % accuracy for either part.
- The BSS138 bound is 10 times tighter than the AO3400A bound. Neither bound meets 0.1 % at step 1 for any
  assumed V_ILIM.
- Step 1 (the 500 mA step, no firmware needed) is the worst case, because two switches are off.
- The assumed V_ILIM range (0.5 to 2 V) is not from a datasheet. It must be measured on the prototype.

## Open actions (owner decision where marked)

1. Measure V_ILIM and the ILIM node leakage with the real parts on the prototype (add to the HW-010 acceptance
   criteria; owner decision).
2. Or choose a part whose datasheet states a lower IDSS or a leakage at low VDS. Not searched yet.
3. Read the 2N7002 datasheet for the same comparison. Not done.
4. A series switch is not needed if the leakage stays below the 0.1 % limits above; if it does not, consider a
   different switching scheme (owner decision, ADR-0010 and ADR-0016 would change).
