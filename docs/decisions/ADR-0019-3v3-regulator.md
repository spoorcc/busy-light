# ADR-0019: 3V3 regulator topology and package

- **Status:** Proposed (only the owner sets Accepted)
- **Date:** 2026-11-07
- **Deciders / reviewers:** Ben Spoor (owner); goldfish review RV-011 (finding 3)
- **Related:** SYS-021, HW-004, HW-010, HW-013, ADR-0003, ADR-0007, ADR-0011, RISK-004, RISK-005

## Context and problem
The ESP32-C3-MINI-1 and a few small parts need 3.3 V from the +5V rail. The module datasheet asks for a supply that delivers at least 500 mA; the worst case with a 20 % margin is 567 mA (`spike-7-5-power-budget-paper.md`). The housing is closed PETG (ADR-0011), so heat is a constraint. Not known: the real Wi-Fi duty cycle (assumed in `analysis-regulator-heat.md`), the housing temperature rise at the regulator, the stock of the chosen variant.

## Decision criteria
| Criterion | Weight (1-5) | Source requirement |
|-----------|--------------|--------------------|
| Thermal margin in the closed PETG housing | 5 | HW-013, ADR-0011, RISK-005 |
| Radio noise and layout risk near the antenna | 4 | ADR-0003, NEED-014 |
| Part count, cost and assembly | 3 | SYS-021, SYS-022 |
| Current margin over 567 mA | 4 | HW-004, RISK-004 |
| Availability and second source | 3 | HW-012 |

## Alternatives considered
### A. Linear TLV75733P, standard DBV package, with a firmware limit on the average 3V3 current
1 A, 25 uA ground current, 6 V absolute maximum on VIN (TLV757P datasheet SBVS322C, read). Strongest case: one small part, no coil, no switching noise, easiest to buy. Cons: on a weak board at +40 K housing rise only about [70] mA average is allowed (`analysis-regulator-heat.md`), so the firmware must cap Wi-Fi transmit duty, and the firmware has no current sensor.
### B. Same part, DYD package with exposed pad and copper under it
Strongest case: about 170 mA average on the weakest board at +40 K, and about 360 mA with no housing rise. Cons: the DYD variant's stock and price were not checked; a layout rule for the pad.
### C. Small buck converter (3.3 V, 1 A)
Strongest case: least heat in the shell. Cons: inductor and layout, switching noise near the antenna, a second DFx path, too heavy for the first board.
### D. Do nothing / defer
Keep the placeholder regulator in the spike. Not possible for a product board.

## Comparison
Scores 0 to 5 (my judgement; maximum 95).

| Criterion (weight) | A | B | C | D |
|---|---|---|---|---|
| Thermal margin (5) | 2 | 4 | 5 | 0 |
| Radio noise and layout (4) | 5 | 5 | 2 | 0 |
| Part count, cost, assembly (3) | 5 | 4 | 2 | 0 |
| Current margin (4) | 5 | 5 | 5 | 0 |
| Availability (3) | 4 | 3 | 3 | 0 |
| **Weighted sum** | 77 | 81 | 68 | 0 |

## Decision
**Recommendation of the assistant: B** (DYD pad package). **Owner decision (2026-11-07): A**, the standard package with a firmware limit only. The assistant recorded this and states that B scores higher and that A relies on a requirement that does not yet exist (the transmit-duty or average-current limit). Status stays Proposed until the owner accepts the text.

## Consequences
- Positive: simplest part; no switching noise.
- **Negative / trade-offs accepted:** thermal margin depends on firmware and on an unmeasured housing rise; a firmware download at about 157 mA average exceeds the weakest-case limit; DBV on a poor board can reach 115 degC with no housing rise.
- New risks: regulator overtemperature during a long update (RISK-005); the firmware cannot measure the current it must limit.
- Requirements created or changed: a transmit-duty or average-current requirement (owner said later), HW-013 and TC-213 with a Wi-Fi update-load run, ADR-0007 (update path rate).

## Verification and revisit
TC-213 with a regulator thermocouple at the update load. Revisit if the measured regulator temperature is above 110 degC, if the housing rise exceeds 20 K, or if the firmware limit costs an unacceptable update time (then B or C).

## Critical review notes
Strongest objection: "The table prefers B, and A needs a limit the firmware cannot sense." Answer: both true. The owner accepts A for the prototype because B is a package swap that costs little if TC-213 fails.
