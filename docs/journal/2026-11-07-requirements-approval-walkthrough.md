# 2026-11-07: requirements approval walkthrough

Owner decisions taken one by one in the session (the assistant recorded them; only the owner approves).

| Item | Decision |
|---|---|
| SYS-020 | Amendments A ([2] s), B (reset after gate closure allowed), C (three steps, step 2 thermal cap) approved. The owner first asked about dropping step 2; after the consequences were listed (saves one switch, one resistor, one gate cell, one GPIO; costs rework, ADR-0016 Amendment 3 and no thermal fallback without a respin) the owner kept three steps. |
| HW-010 | Consolidated revision approved. Open: debounce margin, M4 sag band, TVS1, 3V3 regulator, 1 V ILIM assumption. |
| SW-005, SW-006, SW-007, SW-009 | Amendments approved and folded into the text; SW-006 "does not reset" aligned with SYS-020. |
| SW-010, HW-013 | Approved as drafted; bracketed values stay open. |
| DEV-001 | Stays Proposed until TC-210 (d) and the TVS1 choice. |
| DEV-005 | Approved with updated compensating measures. |

SW-008 had no Proposed amendments and stays Draft.

Not run: no bench, SPICE or firmware work. The RV-010 readiness check stays NO-GO (unmeasured values, unchosen parts, TC procedures, outdated spike generator, HW-012 evidence).
