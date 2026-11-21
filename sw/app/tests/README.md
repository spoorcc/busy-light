# Tests

Every code change in `sw/` is accompanied by tests here (Zephyr ztest, run via `west twister -T sw/app/tests`).
Each test cites the `TC-nnn` it implements. See `docs/process/verification-strategy.md`.

| Suite | Platform | Cases | Covers |
|-------|----------|-------|--------|
| `gate/` (`busy_light.gate`) | `native_sim/native/64` | 20 | `sw/app/src/gate.c`: TC-105, TC-106, TC-107, TC-109, TC-110 at unit level (SW-005, SW-006, SW-007, SW-009, SW-010) |

Run them as `scripts/ci_sw.sh` does:

```sh
ZEPHYR_TOOLCHAIN_VARIANT=host west twister -T sw/app/tests -p native_sim/native/64 --inline-logs
```

Last recorded run: 20 of 20 passed (`docs/verification/reports/sw-target-build-2026-11-18.md`). No test runs on a board yet.
