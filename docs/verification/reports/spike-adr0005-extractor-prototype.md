# Spike report: ADR-0005 extractor and mapper prototype (PC only)

- **Status:** Draft (author's record; no goldfish or owner review)
- **Date:** 2026-11-04
- **Evidence for:** `docs/decisions/ADR-0005-mapping-model.md` (alternative A, items 2 to 6) and `SW-001` (limits), with a side look at SYS-005, SYS-006, SYS-008, SYS-032, SYS-040
- **What was done:** a throw-away C99 prototype was written, unit-tested, fuzzed and measured on the author's PC. It is **not product code**. Nothing was merged into the repository; the code stays in the session scratchpad (`.../scratchpad/extractor/`, files `bl_extract.[ch]`, `bl_map.[ch]`, `test_bl.c`, `fuzz_bl.c`, `diff_test.py`, `bench.c`) and is not kept in the repository.
- **Labels:** each result is marked **run** (executed, output observed) or **not run**.

## 1. Purpose
Check, with working code, whether the model of ADR-0005 alternative A (restricted JSON Pointer, single-pass extractor, exact-match table, linear level, Jenkins two-step rule) is implementable within the stated limits; whether it can be tested and fuzzed on the PC; and how large it is. This gives evidence for the open numbers in ADR-0005 item 3 and SW-001 (flash, stack, run time). It does not decide the ADR.

## 2. Design (short)
- **Extractor** (`bl_extract`): one forward pass over a `(pointer, length)` buffer. No recursion, no heap, no global state, no libc except `string.h` (`memset`, `memcmp`, `memcpy`, `strlen` in table helpers) and `stdint.h`/`stddef.h`. A small state machine (`value`, `child`, `after`) with a 32-bit mask (object or array per nesting level) and one 16-bit element counter per path level. Strings are decoded byte by byte through a sink that either skips, captures (up to 32 bytes) or compares with the path token, so no key or value is buffered beyond 32 bytes.
- **Path** is parsed first into at most 8 tokens inside a 64-byte buffer (`~0` and `~1` decoded). A token is an array index only if it is 1 to 9 digits without a leading zero.
- **Early exit:** the walk stops when the target scalar is read. The rest of the document is not checked. If the target is not found, the whole document is validated, so "not found" means "valid JSON without that path".
- **Mapper** (`bl_map`): table of at most 16 rows (text up to 32 bytes, number, boolean, null; type and value must match exactly; first row wins; no match gives `unknown`). Level: `(v-min)/(max-min)` in 64-bit integer arithmetic on values scaled by 10^6, rounded to nearest, clamped to 0..1000 permille, inverted range allowed, `min == max` returns `BL_ERR_CONFIG`, a non-number gives state `unknown`. Jenkins preset `bl_map_jenkins`: `/building` true gives `running`, otherwise (false or absent) map `/result` through the table.
- **Error model:** named status codes (`BL_ERR_INPUT_TOO_LARGE`, `BL_ERR_PATH_TOO_LONG`, `BL_ERR_PATH_DEPTH`, `BL_ERR_JSON_SYNTAX`, `BL_ERR_JSON_DEPTH`, `BL_ERR_NUMBER`, `BL_ERR_VALUE_TOO_LONG`, ...). The output value is cleared on any non-OK status.
- **Style:** C99, fixed-width types, explicit casts, no magic limits outside `#define`, loops bounded by the input length. Followed in spirit only; see section 9.

## 3. Limits implemented
| Limit | Value | Behaviour at limit / one over | Source |
|-------|-------|-------------------------------|--------|
| Input text | 8192 bytes | 8192 accepted; 8193 gives `BL_ERR_INPUT_TOO_LARGE`, checked before reading | ADR-0005 item 3, SW-001 |
| Path length | 64 characters | 64 accepted; 65 gives `BL_ERR_PATH_TOO_LONG` | ADR-0005 item 2, SW-001 |
| Path depth | 8 tokens | 8 accepted; 9 gives `BL_ERR_PATH_DEPTH` | ADR-0005 item 2, SW-001 |
| Table rows | 16 | 17th row refused (`BL_ERR_CONFIG`); a table with count above 16 maps to `unknown` | ADR-0005 item 3, SW-001 |
| String result | 32 bytes | 33 gives `BL_ERR_VALUE_TOO_LONG` (also when a long string is only reached through escapes) | **prototype choice** (task said "small fixed length") |
| Integer | int32 (-2147483648..2147483647) | outside gives `BL_ERR_NUMBER` | ADR-0005 item 3 |
| Decimal | at most 6 fractional digits, integer part within int32 | 7 digits (even zeros) gives `BL_ERR_NUMBER` | **my reading** of "at most 6 digits" |
| Exponent form (`1e3`) | not supported | `BL_ERR_NUMBER` when it is the target; accepted when only skipped | **prototype choice** |
| Document nesting | 32 containers | 33 gives `BL_ERR_JSON_DEPTH` | **prototype addition, not in SW-001** |
| Heap use | none | - | SW-001 |

## 4. Test list and results
Unit tests: `test_bl.c`, plain `assert`-style `CHECK` macro and own `RUN` harness (no framework).

**Build and run (1): run.** gcc 16.2.1 and clang 23.1.1, both `-std=c99 -pedantic -Wall -Wextra -Wconversion -Wshadow -Werror -g -O1 -fsanitize=address,undefined -fno-sanitize-recover=undefined`. Library and tests compile with no warning on both. Result on both compilers: **27 tests, 0 failed; 434 checks, 0 failed**, no sanitizer report.

**Coverage of the unit tests: run** (gcc `--coverage`, `-O0`, gcov): `bl_extract.c` 98.98 % lines of 393 and 99.44 % branches; `bl_map.c` 94.20 % lines of 138 and 100 % branches. Not a requirement; recorded for information. The uncovered lines were not listed.

| Test | Covers |
|------|--------|
| t_basic_scalars | string, integer, decimal, true, false, null; `bl_value_as_int32` |
| t_jenkins_sample | realistic Jenkins build JSON, nested array/object path, escaped quote |
| t_whole_document_and_root_scalar | empty path, scalar root, path through a scalar |
| t_missing_key | missing key, empty containers, index past end, case, prefix of key |
| t_wrong_type | target is object/array; string where number is wanted; key on array; digit key on object; `/01`, `/-` |
| t_array_index | indexes, nested arrays, whitespace, 10-digit index |
| t_duplicate_keys_first_wins | first match wins |
| t_pointer_escapes | `~0`, `~1`, empty key, bad `~`, missing leading `/`, control char in path |
| t_depth_8_and_9 | path depth 8 found, 9 rejected; document 9 deep with path 8 |
| t_json_nesting_limit | document nesting 32 accepted, 33 rejected |
| t_path_length_64_and_65 | path length 64 accepted, 65 rejected |
| t_input_8192_and_8193 | input 8192 accepted (also target at the last bytes after 8 KB of skipped text), 8193 rejected |
| t_empty_and_garbage_input | empty, truncated, trailing comma, missing colon, wrong closer, BOM, bad literals, NUL, NULL pointers |
| t_string_escapes | all simple escapes, empty string, key with control character |
| t_string_errors | bad escape, unterminated, raw control character (in target and in skipped string) |
| t_unicode_escapes | 1, 2, 3 and 4-byte UTF-8 from `\u`, surrogate pair, lone high/low surrogate, high + non-low, short/bad hex, `\u0000`, escaped key vs UTF-8 path |
| t_string_length_limit | 32 accepted, 33 rejected, 33 via escape, long skipped string |
| t_numbers_edges | 0, -0, int32 min/max, overflow (+1, huge), decimals (1 to 7 digits), max decimal, exponent forms, leading zeros, `+1`, `.5`, `1.`, `-`, `1e`, hex, double minus, trailing junk |
| t_nan_like_text | bare `NaN`/`Infinity`/`-Infinity`/`nan` rejected as syntax; strings "NaN", "inf", "42" give state unknown through the level mapper |
| t_table_text | Jenkins words, unmapped, case, trailing space, prefix, embedded NUL, missing path, truncated JSON, wrong type |
| t_table_bool_null_number | boolean, null and number rows; `2` equals `2.0`; number row vs text row of same spelling; `0` is not false |
| t_table_limits | 16 rows accepted, 17th refused, corrupted count, 32 and 33 byte row text, first match wins, empty table |
| t_level_scale | 0, 25, 50, 53.1, 100, clamp both ends, rounding, offset and negative ranges, int32 extremes (64-bit overflow check) |
| t_level_inverted_and_config | inverted ranges incl. clamp, `min == max` rejected |
| t_level_non_numeric | string, boolean, null, object, array give state unknown; exponent and overflow numbers give error plus unknown; missing path |
| t_jenkins_preset | building true (any key order), each result word, NOT_BUILT, null result, building absent, building wrong type, truncated, empty |
| t_misc_args | NULL argument handling |

## 5. Fuzz results
- **Tool: run.** clang 23.1.1 libFuzzer (`-fsanitize=fuzzer,address,undefined -fno-sanitize-recover=undefined`, `-max_len=8300`, `-timeout=2` s per input, `-fprofile-instr-generate -fcoverage-mapping`). Harness `fuzz_bl.c`: input = `[path length byte][path][JSON]`; per input it calls `bl_extract` (four paths: the fuzzed one, `/building`, `/a/0/b`, empty), `bl_map_state_json`, `bl_map_level_json` (normal and inverted range) and `bl_map_jenkins`, and aborts if an invariant breaks (status OK with type none, string longer than 32 or not terminated, number outside the int32/6-decimal range, integer flag with a fraction, value not cleared on error, permille above 1000).
- **Seeds: run.** 160 seed files from `mkseeds.py`: Jenkins samples (finished, running, failed, `?tree=` form, aborted), nested depth 8 and 40, arrays and objects, number edge sets, escape sets, truncated, trailing-comma, NaN-like, control characters, UTF-8, an 8100-byte string, a 1500-element array, a 700-key object, each with several paths.
- **Run 1, seed 1: run.** 3 000 000 executions in 59 s, from the seed corpus. Result: **0 crashes, 0 sanitizer reports, 0 timeouts (limit 2 s per input), 0 out-of-memory.** libFuzzer end state: 293 coverage points, 1496 features, 598-input corpus.
- **Run 2, seed 7, `-use_value_profile=1`: run.** 2 000 000 executions in 53 s from an empty corpus plus the seeds. Same result: **0 crashes, 0 timeouts.** Total libFuzzer executions: **5 000 000**.
- **Fuzz coverage (llvm-cov, run):** `bl_extract.c` 96.72 % lines, 94.89 % branches; `bl_map.c` 83.15 % lines, 78.75 % branches; total 93.32 % lines. The unreached lines are argument checks, configuration errors and `bl_value_as_int32`, which the harness does not call and the unit tests do cover.
- **Differential test against Python `json`: run.** `diff_test.py` (library built with ASan/UBSan, loaded with ctypes). Random documents (nested, up to 5 deep, escapes, numbers of all edge forms, 32/33-byte strings, random whitespace) with a random path (some missing, some deeper than 8). Expected result of every valid document is computed by an independent model; each valid document is also mutated 3 times (random byte change, deletion, insertion of structural characters).
  - Seed 1 (earlier path generator): 300 000 valid documents, 900 000 mutants.
  - Seed 2: 400 000 valid, 1 200 000 mutants. Seed 3: 400 000 valid, 1 200 000 mutants.
  - Total **1 100 000 valid documents, 3 300 000 mutants. 0 mismatches.** Checks on mutants: a document Python accepts is never rejected as a syntax error; a document Python rejects is never reported "not found" (it may be reported OK when the target comes before the damage; this happened in about 5 to 7 % of mutants and is by design). Mutants with invalid UTF-8, lone surrogates or `\u0000` are excluded from the accept/reject comparison. Duplicate keys, NaN and Infinity are excluded by construction (the extractor takes the first duplicate and rejects NaN).
- **Hangs:** none observed. The loop is bounded by the input length (each pass advances the pointer). No formal proof was made.
- **Not run:** a fuzz run with a gcc-built binary; a run longer than about 2 minutes; fuzzing with the real target build; a fuzz run with 32-bit pointers (`-m32`).

## 6. Size and stack
**Size: run** (`riscv64-zephyr-elf-gcc` 14.3.0 from Zephyr SDK 1.0.1, `-std=c99 -Os -march=rv32imc -mabi=ilp32`, also with `-Wall -Wextra -Wconversion -Wshadow -Werror`: compiles with no warning). Object files, sections from `size -A`:

| Object | .text | .rodata | .data / .bss | Total |
|--------|-------|---------|--------------|-------|
| `bl_extract.o` (extractor) | 2664 B | 21 B | 0 / 0 | 2685 B |
| `bl_map.o` (mapper, table helpers, Jenkins preset) | 1316 B | 56 B | 0 / 0 | 1372 B |
| **Both** | **3980 B** | **77 B** | **0 / 0** | **4057 B** |

The count is of unlinked objects: no linker alignment, the objects call `memset`, `memcmp`, `memcpy`, `strlen` and the libgcc routine `__divdi3` (64-bit division, used by `bl_extract` for the micro-unit value and by the level scaling; `nm -u`). These are **not counted**; their size depends on the C library and libgcc of the build. `__divdi3` on rv32 is a software routine, so the level calculation is also slower than the extractor; a 32-bit-only variant is possible if the range is reduced. No static RAM. A build with `-ffunction-sections` gave the same totals. Not measured: `-O2`, other compilers, a final Zephyr link.

**Stack: run** (`-fstack-usage`, compiler-reported frame sizes in bytes; there is no recursion, so the call graph bounds the use):

| Function | Frame |
|----------|-------|
| `bl_extract` (includes the path buffer 64 B, token arrays, the walker state; the parser helpers are inlined) | 272 |
| `parse_string` (not inlined) | 64 |
| `match_literal` | 16 |
| `bl_map_jenkins` | 96 |
| `bl_map_state_json` | 80 |
| `bl_map_level_json` | 96 |
| `bl_value_as_int32` | 16 |
| others (`skip_ws`, `sink_put`, `read_hex4`, `is_digit`) | 0 |

Worst chain: `bl_map_jenkins` (96) -> `bl_map_state_json` (80) -> `bl_extract` (272) -> `parse_string` (64) = **512 bytes**. Chain for a level: 96 + 272 + 64 = 432 bytes. The two Jenkins extractions run one after the other, not nested. A caller's own frame, interrupt frames and the 40-byte `bl_value_t` of the caller are not included. The value is a compiler figure, **not measured on a target**. The Zephyr measurement (`CONFIG_THREAD_ANALYZER`) is **not run**.

**Run time on the PC: run, rough guide only.** gcc 16.2.1 `-O2`, no sanitizer, Intel Core Ultra 9 185H, 20 000 calls each, 8 KiB inputs: long string then target 6.1 us (0.75 ns/byte); 8181-byte array of one-digit numbers then target 17.5 us (2.1 ns/byte, the slowest); 8174 bytes of near-miss keys 13.4 us; 8192 bytes of `é` escapes 9.4 us; 8192 bytes of whitespace 2.5 us. **This says nothing reliable about the target.** SW-001 asks at most 50 ms on the target. Even a target 1000 times slower per byte (an assumption, not a measurement) would meet 50 ms on these inputs, but the actual figure needs the on-target measurement of spike 7.1 (**not run**).

## 7. Bugs found
Honest account: the tests, 5 000 000 libFuzzer executions and the differential run found **no defect in the extractor or mapper code**. The following were found and fixed during the work; all were in test or measurement code or were observations about the behaviour:
1. `test_bl.c` (test code): the 8192-byte target-at-the-end document was built 4 bytes short (`n == 8192` check failed). Fixed. The test now proves the 8192-byte boundary with the target in the last bytes.
2. `test_bl.c`: the path buffer was too small for the 65-character case (GCC `-Wformat-truncation` stopped the build with `-Werror`); an uninitialised variable passed by const pointer (clang `-Wuninitialized-const-pointer`). Fixed.
3. `bench.c` (measurement code): the document buffer was exactly 8192 bytes and `snprintf` cut the closing brace, so two benchmark cases first returned a syntax error. Fixed (buffer enlarged); the figures in section 6 are from the fixed version.
4. `diff_test.py` (reference harness): reading a `char[33]` field through ctypes stopped at the first NUL byte; the reference rejected invalid UTF-8 while the extractor passes bytes at or above 0x80 through. Fixed in the harness (byte array; mutants with invalid UTF-8 skipped).

**Behaviours that are decisions to take, not defects (design findings for the ADR/requirements):**
- **F1.** `SW-001` and ADR-0005 name no limit on the nesting of the *document*. Without one, a skipped subtree has unbounded depth. The prototype uses 32 (a 4-byte mask). Recommend adding a nesting limit to SW-001.
- **F2.** "Decimal with at most 6 digits" is ambiguous (6 digits in total or 6 after the point). The prototype reads it as at most 6 fractional digits. Needs wording.
- **F3.** Exponent numbers (`1e3`) are valid JSON but are rejected as a target. Some REST APIs print large numbers or small fractions this way. Needs an owner decision (accept, or state it in the user manual).
- **F4.** After the target the parser checks only the next non-space byte (end, `,`, `}` or `]`). So `{"a":1]` returns 1. The rest of a document is not validated after an early exit. Needs a decision if "malformed input is rejected" (SYS-005) is read as covering the whole body.
- **F5.** UTF-8 is not validated; lone surrogates (`\uD800`) are rejected; `\u0000` is accepted inside a string and compares correctly because lengths are explicit.
- **F6.** The Jenkins preset table maps `result: null` to `running` (ADR-0005 item 4). With `building` false and `result` null, the prototype also shows `running`. Real Jenkins behaviour for that combination is not tested here. If `building` is absent the preset falls back to `/result`; if it has another type, it returns `BL_ERR_TYPE` and state `unknown`. Needs confirmation by the owner.
- **F7.** Number rows compare by value (`2` equals `2.0`) and a number row never matches text with the same spelling. Rows of all four kinds need an editor that shows the type.
- **F8.** The extractor needs two calls for the Jenkins preset (two passes over the text, each single-pass). A `?tree=building,result` answer is small, so the cost is small.

## 8. Requirement-level reading of the results
| Item | Result | Label |
|------|--------|-------|
| SW-001 input, path length, depth, table row limits: one-over rejected with a named error, at-limit accepted | shown by unit tests on the PC | run |
| SW-001 "no heap allocation" | no allocation function is used or linked; checked by reading the source and by `nm -u` on the two RISC-V objects: undefined symbols are only `memset`, `memcmp`, `memcpy`, `strlen`, `__divdi3` and the cross-reference to `bl_extract` | partly run |
| SW-001 "at most 50 ms on target" | not measured on the target | **not run** |
| ADR-0005 item 5 (level: clamp, inverted, `min == max` rejected, non-numeric gives unknown) | shown by unit tests | run |
| ADR-0005 verification line "10 000 random and mutated inputs without crash or hang" | exceeded: 5 000 000 libFuzzer executions plus 3 300 000 differential mutants | run |
| ADR-0005 item 6 (Jenkins two-step rule) | shown for the cases in `t_jenkins_preset` | run |

## 9. What this does not prove
- **No target run.** Nothing was run on the ESP32-C3 or any RISC-V core, in an emulator or in Zephyr. Size and stack are compiler figures from an object file; the run times are PC figures and are a rough guide only. The 50 ms limit of SW-001 and the RAM use on the target are not shown.
- **No MISRA report.** The code was written in the spirit of CERT C and the MISRA subset (fixed-width types, casts, bounded loops, no recursion, no heap) but **no MISRA compliance is claimed**. No cppcheck/MISRA addon and no clang-tidy `cert-*` was run (**not run**). Known departures: `goto` is not used, but several functions have more than one return; `switch` without MISRA-style structure; `memcpy`/`strlen` used on configuration strings.
- **Not the product code.** The API, names, error codes and limits are a prototype. The real `core/` interface (ADR-0005 item 1: `{kind, state, level_permille}`) is not implemented as specified; no Zephyr integration, no `LOG_*`, no Kconfig, no requirement traceability in the code, no TC-101 as written.
- **Test and fuzz limits.** The tests are by the same author as the code. Fuzzing ran about 2 minutes per run on one machine with one harness; the differential model was written by the same author. Absence of findings is not proof of absence of defects. No unit-test run with gcc `-O2/-O3` plus sanitizers, with `-m32`, or with Valgrind was done (**not run**). Real Jenkins output of any version was not captured; the Jenkins samples were written from memory of the API and may differ from real answers. Spike 7.1 should record real answers with and without `?tree=`.
- **The limits and the design findings F1 to F8 are proposals** for the ADR and requirement owners. Nothing here sets a requirement or an ADR to Approved or Accepted.

## 10. Reproduction (scratchpad, not in the repository)
`./run_tests.sh` (both compilers, tests), `clang ... -fsanitize=fuzzer,address,undefined fuzz_bl.c bl_extract.c bl_map.c` and `/tmp/fuzz_bl -runs=3000000 -timeout=2 -max_len=8300 corpus`, `python3 -I diff_test.py <n> <seed>` (library built as a shared object with ASan/UBSan, needs `LD_PRELOAD` of libasan), and the RISC-V compile line in section 6.
