# Spike ADR-0004 item 3: firmware current limiter prototype (PC only)

- **Status:** Draft
- **Date:** 2026-11-04
- **Author:** Claude (exploratory prototype for the owner). Not reviewed. Nothing here is Approved or Accepted.
- **Related:** ADR-0004 (item 3), SYS-001, SYS-020, SYS-032, `spike-7-5-power-budget-paper.md`, `docs/standards/coding-sw.md`
- **Code:** kept in the session scratchpad only, folder `limiter` (`limiter.c`, `limiter.h`, `test_limiter.c`, `level_mode.c`, `bench.c`, `build.sh`, logs in `limiter/logs`). Nothing was added to `sw/`. It cannot be merged without an Approved SW requirement and the unit tests in the Zephyr test tree.
- **Labels:** every result is marked **run** or **not run**.

## 1. Purpose

Collect evidence for ADR-0004 item 3: a limiter that is the last step before the LED driver, estimates the current from the final 8-bit values, and scales the whole frame by one global factor.
Questions:
1. Can it be written in plain integer C99, with a proof that it never exceeds the budget and never darkens more than needed?
2. What does it cost on the target (flash, stack, helper calls)?
3. What does global scaling do to level mode (SYS-032)?
4. What should it do when the budget is below the dark current?

## 2. Design (short)

- Input: 16 pixels x 3 channels of 8 bit (48 bytes, order R, G, B per LED). Output: 48 bytes, plus the scale (Q16: 65536 = x1.0, 0 = dark) and a status.
- Parameters (all `uint32_t`): current per channel at value 255 in uA (R, G, B separate), dark current per LED in uA, spread margin in permille (0 to 1000), budget in uA.
- Estimate of a frame, exact rational number:
  `E = (16 x I_dark + sum_c(P_c x I_c) / 255) x (1000 + m) / 1000`
  where `P_c` is the sum of the output values of channel c over all 16 LEDs. The spread margin covers the dark current too (conservative).
- Test "fits": `(16 x 255 x I_dark + sum_c(P_c x I_c)) x (1000 + m) <= budget x 255000`. This is the same as `E <= budget` (budget is an integer, so rounding `E` up changes nothing). It needs no division and no rounding.
- Search: if the unscaled frame fits, return it (status `LIM_OK`). Else if the all-dark frame does not fit, return all zero (`LIM_BELOW_DARK`). Else binary search for the largest `s` in 0..65535 where the frame scaled by `s` fits (`LIM_SCALED`). The loop runs at most 16 times. This is valid because the scaled value is non-decreasing in `s` and all currents are non-negative, so the estimate is non-decreasing in `s`. Test 2b checks this by brute force.
- Other statuses: `LIM_BAD_PARAM` (NULL pointer or spread above 1000): output all zero. `in` and `out` may be the same buffer.
- No heap, no floating point, no library call in the source. Only 32-bit and 64-bit unsigned integers.

## 3. Integer widths and rounding rule

### 3.1 Rounding rule

1. The only rounding is in the output pixel: `out = (v x s + 32768) >> 16` (round to nearest, `s` in 0..65536).
2. The estimate is **never rounded**. It is computed from the rounded `out` values and compared with the budget in cross-multiplied integer form. So the check sees exactly the values the driver gets, and rounding up of a pixel cannot push the estimate over: the search tests the rounded frame, and a scale whose rounded frame does not fit is not chosen.
3. Because the test is on the output, the rule "round to nearest" is safe. Round-down would also be safe but darkens more.
4. `out <= in` for every pixel, for every `s <= 65536` (`s = 65536` gives `out = in`). Test run (section 5).
5. Plateau note: for `s` from 65408 to 65536 all 8-bit inputs map to themselves. The limiter returns the largest `s` that fits, so a returned `s` is the top of a plateau of identical outputs. "Largest" means the largest `s`, and equally the brightest output frame. Q16 is finer than needed; Q12 would give the same output frames, not tested.

### 3.2 Integer widths and overflow argument

Bounds: `P_c <= 16 x 255 = 4080 < 2^12`. All parameters `<= 2^32 - 1`. Spread `<= 1000` (checked first; larger is `LIM_BAD_PARAM`). `s <= 65536 = 2^16`.

| Quantity | Width | Bound | Reasoning |
|----------|-------|-------|-----------|
| `v x s + 32768` | u32 | `255 x 65536 + 32768 = 16744448 < 2^25` | fits |
| `P_c` (per-channel sums) | u32 | `4080` | 48 additions of values `<= 255` |
| `16 x 255 x I_dark` | u64 | `4080 x (2^32 - 1) < 2^44` | operands cast to u64 before the multiplication |
| `P_c x I_c` | u64 | `< 2^12 x 2^32 = 2^44` | each of the three terms |
| sum `num` | u64 | `< 4 x 2^44 = 2^46` | four terms |
| `num x (1000 + m)` | u64 | `< 2^46 x 2000 < 2^57` | factor `<= 2000 < 2^11` |
| `budget x 255000` | u64 | `< 2^32 x 2^18 = 2^50` | 255000 `< 2^18` |
| binary search `lo`, `hi`, `mid` | u32 | `<= 65536` | |

All limits are far below 2^64, so no wrap is possible. Nothing needs 128 bit. Signed arithmetic is not used, so there is no signed overflow.

Test evidence (run): the 128-bit oracle evaluated the extreme case (all parameters 4294967295, spread 1000, all-white input). The largest intermediate was 140187732508800000, about 0.0076 x 2^64, i.e. just below 2^57, which matches the bound of 2^57 in the table. A clang build with `-fsanitize=unsigned-integer-overflow,implicit-conversion` ran all tests with no report (run, section 5).

## 4. Level mode (SYS-032): resolution loss from global scaling

Setup (run, `level_mode.c`): levels 0 to 1000 permille on 16 white LEDs. The first `floor(L x 16 / 1000)` LEDs are 255, the next LED is `round(255 x remainder)`, the rest are 0. The frame is scaled with the limiter's rule. "Distinct frames" counts different output frames among the 1001 levels. No gamma is applied (the limiter is after gamma in ADR-0004, so a real frame already has fewer low codes).

### 4.1 Fixed scale factor

| Scale | Max code | Steps on the partial LED | Distinct frames of 1001 levels | Permille per code step | Largest jump between neighbouring levels (sum of 3 channels) |
|-------|----------|--------------------------|--------------------------------|------------------------|-------|
| 100 % (reference) | 255 | 256 | 1001 | 0.25 | 15 |
| 50 % | 128 | 129 | 1001 | 0.49 | 9 |
| 25 % | 64 | 65 | 1001 | 0.98 | 6 |
| 10 % | 26 | 27 | **417** | 2.40 | 3 |

Reading: a level is distinguishable only if the frame changes. Up to 25 % all 1001 levels still give different frames (16 x 64 = 1024 steps, just above 1000). At 10 % there are only 16 x 26 + 1 = 417 steps, so about 2.4 levels share one frame. The SYS-032 acceptance criteria (0/25/50/75/100 % light 0/4/8/12/16 LEDs, half step gives about half brightness, a 6.25 % step is visible) need far fewer steps than 1001 and stay met at 10 % on paper. Whether a 26-code step is visible to a person is **not run**.

### 4.2 Closed loop: scale depends on how many LEDs are lit

The limiter scales the whole frame, so the scale rises when fewer LEDs are lit (run, parameters 5000 uA per channel, 500 uA dark, spread 100 permille, budget set so level 1000 gives about the target):

| Target scale at level 1000 | Scale at L=750 | L=500 | L=250 | L=62 (one LED) | Code of a full LED at L=1000 vs L=62 | Distinct frames |
|------|------|------|------|------|------|------|
| 50 % | 66.9 % | 100 % | 100 % | 100 % | 128 vs 255 | 1001 |
| 25 % | 33.5 % | 50.4 % | 100 % | 100 % | 64 vs 255 | 993 |
| 10 % | 13.5 % | 20.6 % | 41.0 % | 100 % | 26 vs 255 | 751 |

Finding: with a global scale, the LEDs that are already lit become darker when the next LED lights up. At the 10 % target a full LED changes from code 255 (one LED) to code 26 (all 16). That is a visible artefact for a filled arc, and it is the opposite of what SYS-032 describes ("filled arc"). The count of distinct frames (751 at the 10 % target) is higher than for a fixed 10 % scale (417) only because low levels use finer codes; the arc is not uniform.

### 4.3 Scale factors with the spike 7.5 paper budgets (run, all-white frame, spread 100 permille assumed)

| Case | Scale | Max code |
|------|-------|----------|
| A WS2812C-2020 (5 mA/ch, 0.5 mA dark), budget 147.8 mA (buck) | 52.75 % | 134 |
| A, budget 46.4 mA (LDO) | 14.31 % | 36 |
| B SK6812MINI-E (12 mA/ch, 1 mA dark), budget 147.8 mA | 20.59 % | 52 |
| B, budget 46.4 mA | 4.51 % | 11 |
| B, budget 46.4 mA, spread 0 | 5.29 % | 13 |
| B, budget 17 mA (dark current 16 mA x 1.1 = 17.6 mA) | status `LIM_BELOW_DARK`, scale 0 | 0 |

On paper, in the LDO case with variant B, the ring has about 12 levels per channel at full white. That is a problem for SYS-001 (256 levels before the limit) and for colour mixing, not only for SYS-032.

## 5. Test list and results

Compilers: gcc 16.2.1, clang 23.1.1 (host x86-64), riscv64-zephyr-elf-gcc 14.3.0 (Zephyr SDK 1.0.1). The same random seed was used for gcc and clang, so both saw the same frames. The independent oracle in the test uses `unsigned __int128` and a separate statement of the rounding rule.

Checks applied to every frame: output equals the oracle scale; no output pixel above its input; the oracle estimate of the output is at most the budget; if the input already fits then status is `LIM_OK` and scale is 65536; otherwise `s + 1` does **not** fit (largest scale); if the all-dark frame is over budget, status is `LIM_BELOW_DARK` and the output is all zero.

| ID | Test | Result (run) |
|----|------|--------|
| 1a | Grid: 2 LEDs (pairs 0+1 and 0+15), each 3 channels in {0,1,2,4,8,16,32,64,128,192,255}, others dark; 2 parameter sets x 4 budgets (dark total plus 0, 200, 3000, 20000 uA). 11^6 x 2 pairs x 2 sets x 4 budgets | 28,344,976 frames, 0 failures. 22,372,204 scaled, 5,972,772 not scaled |
| 1b | All LEDs equal, every (r,g,b) with step 5 from 0 to 255 (140,608 triples), 4 parameter sets x 6 budgets (0, 1, 8, 30, 100, 250 mA) | 3,374,592 frames, 0 failures. 1,227,356 scaled, 459,940 not scaled (the rest below the dark current) |
| 2 | Random: 10,000,000 frames (gcc, clang) in 11 kinds, 909,091 each: uniform, all white, all red, all green, all blue, alternating LEDs, alternating channels, sparse, same colour on all LEDs, very low values, binary 0/255. Parameters change every 64 frames (4 fixed sets, random paper-like, random up to 32 bit). Budget modes: random between 0 and 1.33 x full white, exactly on an edge (output estimate equals budget), one uA below an edge, around the dark total, random | 0 failures. 5,514,034 scaled, 2,228,438 not scaled, 2,257,528 below dark, 2,225,714 with output estimate exactly equal to the budget |
| 2b | Brute force: for 3000 sampled frames evaluate all 65537 scales; fits must be true exactly for `s <=` result (checks monotonicity and "largest") | 160,762,261 scale evaluations, 0 failures |
| 3 | Parameter mutation: budget 0 (with and without dark current), budget one below / exactly at the dark total with margin, budget below dark, budget above full white, budget exactly at full-white estimate and one below, all currents zero, all parameters 4294967295 with spread 1000, only dark at maximum, one channel at maximum; each with all-white, all-dark and 2000 random frames; spread 1001 and 4294967295, NULL pointers, `in == out` | 30,030 frames, 0 failures, all expected statuses matched |
| 4a | gcc and clang `-std=c99 -Wall -Wextra -Wconversion -Wshadow -Werror -fsanitize=address,undefined -fno-sanitize-recover=all` on `limiter.c`; full test run on each | built without warnings; gcc: 41,752,598 frames, 0 failures, no sanitizer report; clang: 41,752,598 frames, 0 failures, no sanitizer report |
| 4b | clang additionally with `-fsanitize=unsigned-integer-overflow,implicit-conversion` (random count 3,000,000) | 34,752,598 frames, 0 failures, no report |
| 4c | riscv64-zephyr-elf-gcc `-Os -march=rv32imc -mabi=ilp32` with the same warning flags | built without warnings (section 6) |
| 5 | Test of the test (mutants of `limiter.c`, 300,000 random frames plus all grids): floor instead of round-to-nearest; margin ignored; strict `<` instead of `<=`; result one step too dark; 32-bit budget product; 32-bit dark term; 32-bit product for the red channel; spread limit removed | 7 of 8 detected (failures from 1 to 26.9 million; the removed spread limit is detected by the single bad-parameter case). One mutant (search upper bound 65535 instead of 65536) was **not** detected. It is an equivalent mutant: `s = 65535` and `s = 65536` give identical output frames (plateau note, section 3.1) |
| - | Static analysis (clang-tidy `cert-*`, cppcheck MISRA addon), coverage, target execution (QEMU or hardware) | **not run** |

The tests use random numbers with a fixed seed. They are not a proof; the proof is the argument in section 3.2 and the monotonicity argument in section 2, backed by tests 2b and 3.

## 6. Size, stack and cost

All numbers from riscv64-zephyr-elf-gcc 14.3.0, `-Os -march=rv32imc -mabi=ilp32 -fstack-usage` (run):

| Item | Value |
|------|-------|
| `.text` | 532 bytes (540 bytes with `-fno-tree-loop-distribute-patterns`); no `.data`, no `.bss`, no read-only data |
| Stack | `lim_apply` 48 bytes; `fits` and `lim_scale_px` 0 bytes (leaf functions). Worst case about 48 bytes plus the return address |
| `nm`: undefined symbols | only `memset` (gcc turns the clear loops into a call). With `-fno-tree-loop-distribute-patterns` there are none |
| libgcc helpers | **none** (`__udivdi3`, `__umoddi3`, `__muldi3` do not appear). The 64-bit multiplications compile to `mul` and `mulhu`; the shifts replace the divisions by 2 and 65536. `objdump` shows no `div` or `rem` instruction |

Cost (rough guide, not measured on the target):
- PC, x86-64 `-O2`, 2,000,000 calls each, machine under load from the test runs: worst case (all white, 17 evaluations of the frame) 370 ns (gcc) and 348 ns (clang) per call; best case (frame already fits, one evaluation) 31 ns (gcc) and 7 ns (clang). Run.
- rv32imc, from the listing (static count, not run): about 19 instructions per LED in the inner loop, so about 355 instructions for one evaluation of a frame. Worst case 18 evaluations (2 start checks plus 16 search steps) plus the final 48-byte write: about 7000 instructions. At one frame update per 16 ms that is below 0.5 % of a 160 MHz core if one instruction took about one cycle. The cycle cost of `mul` and `mulhu` on the ESP32-C3 was not looked up. Estimate only.

## 7. Findings and proposals

### 7.1 Budget below the dark current

What the prototype does (run, test 3): `lim_apply` returns `LIM_BELOW_DARK`, sets the scale to 0 and writes an all-zero frame. The LEDs still draw the dark current (for example 16 x 1 mA = 16 mA for variant B), which is above the budget by definition. Firmware cannot lower it. The paper spike 7.5 reaches this region: "all supply-side inputs 20 % worse" gives a negative LED budget.

What it should do (proposal):
1. Treat it as a **power-budget fault**, not as a display state. Return the status to the caller, log it once, and set a fault flag that the status page and the self-test (SYS-020, TC-020) can read.
2. Still send the all-dark frame (never skip the driver call, because LEDs hold the last frame, ADR-0004 item 5).
3. Check at build time or at boot that `budget >= ceil(16 x I_dark x (1 + m / 1000))` plus a minimum useful brightness. A constant budget makes this a compile-time check. A budget that varies at run time (for example by Wi-Fi state) needs the run-time status.
4. If the fault can occur in a real product, the only remedy is hardware: a switch on the LED supply (ADR-0004 items 4 and 5b). Decide that when the 7.5 bench measurement gives the real numbers.
5. Add a requirement that fixes the behaviour (all dark, fault flag), so it is testable.

### 7.2 Proposals for ADR-0004 item 3

- Keep "last step before the driver, global scale". The prototype shows it is small (532 bytes, 48 bytes stack, no division helpers) and exhaustively testable on the PC (section 5).
- State the estimate rule in the ADR: current per channel is proportional to the 8-bit value; the estimate is computed on the output values; the margin applies to the sum including the dark current; the test is exact (no rounding of the estimate). Add the rounding rule of section 3.1.
- Fix the parameter types: currents and budget in uA as 32 bit, spread limited to 1000 permille. Say that 64-bit unsigned arithmetic is used (inline `mul`/`mulhu` on RV32IM, no libgcc call).
- Define `LIM_BELOW_DARK` (section 7.1) as a named fault state.
- Level mode: see 7.3.
- The spread margin value is still **not found** (spike 7.5 needs a bench value). The prototype used 100 permille only as a test value, not a recommendation.

### 7.3 Proposals for SYS-032 and SYS-001

- Global scaling dims lit LEDs as the arc grows (section 4.2). Propose for level mode: compute one fixed scale for the worst-case frame of the chosen level colour (full ring) and use it for all levels, so lit LEDs keep a constant brightness. The limiter stays the last step as the safety net and never sees an over-budget frame in normal use. This needs a SW requirement and a test (not written).
- SYS-032 acceptance criteria do not state a minimum number of brightness steps for the partial LED. Propose a criterion such as "at least 16 distinct partial-LED steps at the lowest allowed scale" (needs max code 15, a scale of about 6 %). A 1001-level criterion would need a scale of about 25 % or higher (max code 63).
- SYS-001 says 256 levels per channel "before the current limit". Given the paper numbers (max code 11 to 36 at full white in the LDO case, section 4.3), add a figure for the usable number of levels after the limit, or accept the loss and document it. The brightness figure (working value 100 mcd per LED) must be checked against the scale the limiter allows.
- SYS-020: the limiter works on an estimate. TC-020 (measured, all LEDs white) is the evidence that the estimate parameters are right. The test should compare the measured current with the estimate at several frame values, not only at full white, to check the proportional model.
- The Wi-Fi TX peak and the LED peak are not synchronised. A static budget must assume the worst case and so dims the ring all the time (14 % or 4.5 % in the LDO case, section 4.3). A budget that follows the Wi-Fi state is a design question for the owner (not now).

### 7.4 Supply voltage drop and temperature (mention only, not now)

The prototype does not use the LED supply voltage or temperature. Open design question: may the limiter use them?
- Constant-current LED drivers keep the channel current about constant while the supply is in range, so the voltage drop along the ring is expected to change colour more than current. Not verified; the datasheets in 7.5 gave no recommended range (L21 not found).
- Temperature could scale the per-channel current or the budget (for example derating in a hot housing, G10). That needs a sensor and a derating curve, neither of which exists in the inputs.
- If either input is added, keep `lim_apply` pure and let the caller compute the budget from them. The core then stays deterministic and keeps its exhaustive tests. The safety case then also depends on the sensor.

## 8. What this does not prove

- **No hardware.** The estimate model (current proportional to the 8-bit value, per-channel constant, dark current always present) is an assumption. No LED was driven and no current was measured. Not run.
- **Parameters are paper values** from `spike-7-5-power-budget-paper.md`: per-channel current of the 3535 SK6812MINI is not found (L10), the spread margin is not found, the LED budget depends on assumed inputs (20 % margin, 85 % buck efficiency) and on E13 to E17 (not found). The 100 permille spread is a test value.
- **No MISRA report and no MISRA claim.** The code was written in C99 with CERT-style habits (fixed-width types, bounded loop, no heap, checked pointers). clang-tidy `cert-*`, cppcheck with the MISRA addon and gcov coverage were **not run**. No DEV-nnn records were needed or created; none were checked.
- **Not run on the target.** The RISC-V object was only built and inspected (size, stack, symbols, listing). No QEMU, no ESP32-C3. Instruction and cycle figures are static estimates, PC timings are a rough guide on a loaded machine.
- **Not integrated:** no Zephyr build, no `core/` unit test in `sw/app/tests`, no gamma stage, no driver, no Kconfig. Interaction with `ws2812-spi` and with animation timing is not examined.
- Visibility of the resolution loss (can a person tell 26 codes from 27) is **not run**.
- Random testing and mutants show the test finds the defects tried; they do not show absence of other defects.
- No traceability check, style check or diagram check was run on this report. IDs used here are references only; no requirement or ADR text was changed.
