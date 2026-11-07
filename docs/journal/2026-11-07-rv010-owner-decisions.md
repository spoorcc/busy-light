# Owner decisions after the RV-010 review (2026-11-07)

Records the owner's answers of 2026-11-07 in the working session, in the order asked. They follow the goldfish
review `docs/reviews/RV-010-hw-010-gate-bundle-goldfish.md`. Nothing here is Approved. Only the owner approves documents.

| # | Question | Answer | Follow-up work (status) |
|---|---|---|---|
| 1 | CC_OK_3A readback (OUT2, U12, R7, GPIO1) | Delete it (recommended) | HW-010 Proposed revision and SW-005, SW-009 Proposed text updated; spike untouched (rule 1) |
| 2 | Middle step (about 1 A) | Keep, define in SYS-020 (recommended) | SYS-020 Proposed amendment to draft (open) |
| 3 | TMUX1101 over-voltage at power-up | **Remove it by design** (not the recommendation; the recommendation was accept with a bench check) | Needs a design option analysis and an ADR-0016 amendment; DEV-001 stays until then (open) |
| 4 | Hold-off margin and maximum CC debounce | Look up the maximum, keep the set (recommended) | Datasheet search for the TUSB321 maximum debounce (open) |
| 5 | DEV entry for accepting ADR-0016 before its review | Yes (recommended) | DEV entry to draft as Proposed (open) |
| 6 | Thermal and watchdog requirements | Draft both now (recommended) | Two Draft requirements to write (open) |
| 7 | SW-007 retained flag | (a) retained flag (recommended) | SW-007 Proposed text updated; retention on the prototype is still to be shown |
| 8 | SYS-020 reset wording | Accept: reset allowed after a dip (recommended) | Wording already drafted as Proposed in SYS-020, SW-009 |

## Decision 4 result: maximum CC debounce

- TUSB321 datasheet SLLSEO6C section 6.6: debounce 133 ms typical, **no maximum stated**. Recorded in `cc-ic-datasheet-evidence.md` (note 2026-11-07). The "120 ms" there was the PTN5150A.
- Consequence for the capacitor set (script calls with 5 % C0G, TPS3840 constants, same model as `amendment2_numbers.py`):

  | C1 | Hold-off window |
  |---|---|
  | 600 nF (six 100 nF, current) | 203.2 to 553.2 ms |
  | 640 nF | 216.7 to 590.1 ms |
  | 649 nF | 219.8 to 598.4 ms |
  | 700 nF | 237.1 to 645.4 ms |

  The window ratio (maximum over minimum) is 2.72. A minimum of 220 ms (a [20] ms margin over a 200 ms debounce) puts the maximum at about 599 ms, which leaves 1 ms to the 600 ms limit. So with a 200 ms debounce the present limits [200] to [600] ms cannot give a robust margin on both sides.
- Options (owner decision, open): (1) keep six 100 nF and measure the real debounce and hold-off on the bench (TC-210); (2) widen the upper limit, for example to [700] ms: the SYS-020 worst case then becomes about 1322 ms (1222 + 100) against [2] s, and a 700 nF-class set gives about 237 to 645 ms; (3) a part with a stated maximum debounce.
- Recommendation: (1) now, with (2) prepared as the next step if the bench shows a debounce above about 180 ms. The upper limit has margin in the [2] s of SYS-020, the lower limit is the safety side.

## Drafted on 2026-11-07 (all Draft or Proposed, nothing Approved)

- Decision 2: SYS-020 Proposed amendment defining the three steps. The purpose of the middle step was not recorded anywhere. The owner confirmed on 2026-11-07, on the assistant's recommendation: a cap for the case that the thermal limit (HW-013) does not allow step 3; the staged-raise purpose was rejected. A Type-C source never advertises "about 1 A", so step 2 can only be a firmware choice. Revisit after TC-213.
- Decision 5: DEV-005 (Proposed), ADR-0016 accepted before its own review.
- Decision 6: HW-013 (thermal limit at the top step, TC-213) and SW-010 (watchdog restart returns the limit to the lowest step, TC-110), both Draft with bracketed working figures. SYS-027 already requires a restart within [10] s of a hang; SW-010 ties it to the select outputs.
- Compliance matrix row for HW-013 (EN 62368-1) is not added yet.

## Follow-up answers of 2026-11-07
- Middle step purpose: (B) thermal cap, as recommended.
- Debounce: measure first (bench, several units, 70 degC) and look for a newer TUSB321 datasheet revision; widen the upper limit to about [700] ms only if the measured debounce is above about 180 ms.
- Commit and push the drafts: yes.

## Decision 3 result: ILIM switch supply from VBUS_IC
Analysis in `docs/verification/reports/analysis-tmux1101-supply-from-vbus.md`. Recommended and drafted: option A (VDD of U14 and U15 from VBUS_IC with 100 nF). Rejected: series resistor or clamp, TS5A3166 fallback, keep with DEV-001. Open: TVS clamp voltage against the 6 V rating, dropout scope record, the 1 V ILIM assumption. The owner approves; the spike schematic is not changed.

TVS check (2026-11-07): TVS1 is a placeholder with no part chosen, so the 6 V question for the switch supply is a selection requirement for TVS1 (clamp voltage at the surge current against the VDD ratings of the parts on VBUS_IC), not a datasheet check. Open.
