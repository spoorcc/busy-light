# ADR-0004: LED type, data drive and current limiting

- **Status:** Proposed (only the owner sets Accepted)
- **Date:** 2026-11-03
- **Deciders / reviewers:** Ben Spoor (owner); Reviewed in RV-001 (as referenced by plan 02); no separate ADR review
- **Related:** NEED-003, NEED-009, NEED-010, NEED-014, SYS-001, SYS-011, SYS-020, SYS-021, SYS-022, SYS-027, SYS-028, SYS-032, ADR-0002, ADR-0003; design doc `docs/plans/02-system-design.md` (sections 4.4, G4, G10, G11, G14, spikes 7.3 and 7.5)

## Context and problem
The ring has 16 RGB LEDs, each controlled for colour and brightness (SYS-001), evenly spaced on a ring of at least 38 mm (SYS-028), on one side of the board, assembled by a prototype shop (SYS-022), for a total board cost of EUR 10-20 (SYS-021).
The total current from the USB-C supply is limited to [500] mA (SYS-020), and the Wi-Fi radio uses a large share of that during transmit peaks (G4, to verify in the datasheet). The LED share may be only about 150-250 mA (estimate), a fraction of full white (about 0.9-1 A for 16 LEDs, estimate).
The processor runs Wi-Fi and TLS at the same time, so interrupts can delay software timing.

Not known (spikes 7.3 and 7.5): whether a 3.3 V data signal drives the chosen 5 V LED reliably at room and at high temperature; the real current draw of Wi-Fi peaks; how bright the ring must be (brightness is set in SYS-001, working value, from spike 7.5); the thermal margin inside a printed shell (G10); photobiological safety (G11, EN 62471).

## Decision criteria
| Criterion | Weight (1-5) | Source requirement |
|-----------|--------------|--------------------|
| Fits the ring (package about 2020 or 3535) | 4 | SYS-028 |
| Part cost and parts count on the shop's list | 4 | SYS-021, SYS-022 |
| Drive works while Wi-Fi interrupts run | 4 | SYS-027 |
| Total current can be limited reliably (safety) | 5 | SYS-020 |
| Enough light at the limited current | 3 | SYS-001 |
| Predictable state at power-up and reset | 3 | SYS-011 |
| Can be simulated or tested without the board | 2 | SYS-025, SYS-037 |

## Alternatives considered

### A. Single-wire addressable RGB LED, 2020 or 3535 package (WS2812 or SK6812 type)
One data line through all 16 LEDs; one part type; common in shop libraries; the Zephyr `led_strip` API has an SPI-based driver (`worldsemi,ws2812-spi`, in source at v4.5.0); no RMT driver for the C3 was found (desk survey E0).
Cons: the data timing is tight (about 1.25 us per bit; to confirm in the datasheet); the data input threshold is typically 0.7 x the LED supply, i.e. about 3.5 V at 5 V, above a 3.3 V output (G14); no hardware current limit; each LED draws about 1 mA when dark (estimate, 16 mA total).

### B. Clocked addressable LED (APA102 type, also 2020 variants)
Clock and data lines, no timing problem, tolerant of interrupts. Higher part price, two signal lines, more tracks on a tight board, and the same lack of a hardware current limit.
Strongest case: in the presence of Wi-Fi jitter it is the most robust. In practice option A with a hardware peripheral (SPI or RMT) removes the jitter problem too, so B pays extra for a risk that A can avoid.

### C. Discrete RGB LEDs with a constant-current driver IC
Hardware current control and no timing problem. Cons: a driver chip with an I2C or SPI interface, resistors, and 16 more pads and tracks; more parts and more board area; likely more than the cost budget at 10 units.

### D. Do nothing / defer
The LED choice determines the footprint and the first schematic. Not possible.

## Comparison
Scores 0 to 5, my judgement; no datasheet values checked yet. The scores are close (A 91, B and C 87), so the decision rests on cost and board area, and on the hardware-peripheral rule that removes B's advantage.

| Criterion (weight) | A | B | C | D |
|--------------------|---|---|---|---|
| Fits ring (4) | 5 | 4 | 2 | 0 |
| Cost and parts count (4) | 5 | 3 | 1 | 0 |
| Works with Wi-Fi interrupts (4) | 3 | 5 | 5 | 0 |
| Current limiting (5) | 2 | 2 | 5 | 0 |
| Light at limited current (3) | 4 | 4 | 4 | 0 |
| Predictable power-up (3) | 3 | 3 | 4 | 0 |
| Simulation and test (2) | 4 | 4 | 3 | 0 |
| **Weighted sum (max 125)** | 91 | 87 | 87 | 0 |

## Decision
Choose **A** with these design rules; items marked (7.3) or (7.5) are confirmed by the spike before the schematic is frozen.
1. **Drive by hardware peripheral**, not by software timing: SPI (the Zephyr `worldsemi,ws2812-spi` driver, the only route found in v4.5.0; no Zephyr RMT driver for the C3 was found, desk survey E0), with the buffer sent by the driver. Software bit-banging is not used. Interrupt latency from Wi-Fi then cannot corrupt a frame (7.1 verifies the driver exists for the pinned revision).
2. **Data level (7.3):** fit one small buffer with a 5 V supply and a TTL-compatible input (for example a 74AHCT1G125 type, one gate) between the processor and the first LED, with a series resistor of about 330 ohm near the first LED and a pull-down resistor on the data input. If 7.3 shows the LED reliably accepts 3.3 V over the temperature range, the buffer is removed. The cost of the buffer is about EUR 0.1 or less (estimate).
3. **Current limit in firmware, in `core/`** with unit tests: the display engine estimates the current from the final 8-bit colour values that go to the driver (per-channel current model from the datasheet, plus a margin for LED spread, value from 7.5), and scales the frame so the estimate stays at or below the LED budget from the power analysis (7.5). The limit is the **last step before the driver**, after animation and gamma, so no later stage can raise the current (goldfish review RV-001, finding 3). Scaling is global; the effect on level-mode resolution is tested (SYS-001, SYS-032). This is a safety function (SYS-020). The budget is a configuration constant in one place. PC prototype (`docs/verification/reports/spike-adr0004-limiter-prototype.md`, scratchpad only, run on the PC): integer-only, rounding applied to the output pixel only so that the estimate of the rounded output never exceeds the budget; 31.7 M grid frames and 10 M random frames with no failure; 532 B and 48 B stack on rv32imc, no libgcc helpers. Two proposals from it: in level mode use a fixed scale so lit LEDs do not dim as the arc grows (global scaling leaves 417 of 1001 levels at a 10 % scale); when the budget is below the total dark current the limiter outputs all zero and raises a fault flag.
4. **Hardware backstop (open):** a USB-side current-limited load switch is an extra part that would limit the total to a fixed value even if firmware fails. Decide after 7.5: required if the analysis shows that a firmware fault could exceed the USB-C source limit or a connector rating.
5. **Power-up and reset state:** the pull-down holds the data line low at reset; the firmware sends an all-dark frame as its first action (SYS-011) and a frame that matches the real state only after the state is known. **Known gap (RV-001, finding 4):** LEDs hold their last frame while powered. A pull-down does not darken them. During a hang, a watchdog reset, the bootloader, or an image swap (many seconds, no LED driver) the ring keeps showing the old state, for example green. SYS-011 cannot be met in that window. Options: (a) accept and document, (b) a switch on the LED supply that the bootloader or a hardware timer opens, (c) a bootloader LED hook. Decision belongs to the owner; (a) is the default until 7.5 and the swap-time measurement are done.
6. **Part choice:** pick the specific 2020 or 3535 part from the shop's current list during design, with a second source of the same footprint noted in the BOM. The part number is not fixed in this ADR.
7. **Brightness requirement:** set in SYS-001 (working value, from spike 7.5).

## Consequences
- Positive: one LED part type; low cost; hardware timing; firmware limiter testable on the PC.
- **Negative / trade-offs accepted:** current limiting is a software safety function until item 4 is decided; one extra part (buffer) may be needed; LED maximum brightness is limited by the shared USB budget; the dark current of 16 LEDs (about 16 mA, estimate) is always drawn.
- New risks (to add to risk register): stale colour held by the LEDs during hang, reset or image swap; firmware fault drives LEDs above the budget; 3.3 V data marginal at temperature; first LED fails and the chain goes dark; thermal softening of printed housing; photobiological limit exceeded at full white; brown-out reset when Wi-Fi peak and LED peak coincide.
- Requirements created or changed: SYS-001 now has a measurable brightness figure (working value); SYS-020 acceptance criteria stay; HW-002 (buffer, pull-down, series resistor) and HW-001 exist; new SW requirement for the current limiter; analysis files in `hw/sim/`.

## Verification and revisit
- Spike 7.3: ngspice and a breadboard test of the data level at 5 V and at a lowered supply, over the temperature range available.
- Spike 7.5: power budget script in `hw/sim/` (Wi-Fi peak from the module datasheet, LED model, USB source), then a bench measurement with a USB power meter at full-white request.
- Unit tests: for all colour inputs the estimated current never exceeds the budget (exhaustive over a grid, then random).
- TC-020 measured on a prototype: all LEDs at full white, current at or below the limit, no reset.
- Revisit when: 7.3 or 7.5 fail, the shop's LED part is out of stock, the ring diameter changes (ADR-0003), or tests show Wi-Fi corrupting frames despite the hardware driver (then B).

## Critical review notes
Strongest objection: "A current limit that exists only in firmware is not a safety measure; a software fault removes it."
Answer: accepted as a limitation. The product risk is a hot LED ring or an overloaded USB source, not a life-safety hazard, and the limiter is a small isolated function with exhaustive tests. Item 4 keeps the hardware backstop as an explicit decision with a trigger, rather than ignoring it.
Second objection: "The buffer adds a part to a cost-critical board for a problem that may not exist." Answer: it costs a few cents and removes a field failure that is hard to diagnose; item 2 deletes it if the spike proves it unnecessary.
