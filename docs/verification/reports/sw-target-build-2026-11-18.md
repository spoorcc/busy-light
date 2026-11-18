# Evidence: target build of `sw/app` for the ESP32-C3 dev kit, and host tests (plan 07; SW-005, SW-009)

- **Status:** Draft (author's record; no goldfish or owner review)
- **Date:** 2026-11-18. **Author:** assistant.
- **Plan:** `docs/plans/07-gate-firmware.md` (section 6 and risk "Zephyr and west toolchain: not installed or run"). Earlier records: `spike-7-1-e1-build.md` (board name, SDK), `sw-gate-unit-tests.md` (host tests).
- **Scope:** build and host tests only. **Nothing was flashed. No hardware, no dev kit and no bench were used.** No file under `sw/` was changed.
- **Result in one line:** `sw/app` **built** for `esp32c3_devkitm` with Zephyr SDK 1.0.1 (0 warnings, FLASH 134 884 B = 3.22 %); the host tests passed **20 of 20** on `native_sim/native/64`. The gate logic of SW-005 and SW-009 is **not in the target image** (see 3.4).

Marks: **built** = a build ran and the result was observed; **ran** = the program ran and the result was observed; **not run** = not done.

## 1. Environment (exact)
| Item | Value |
|------|-------|
| Repository commit | `c337ba3` (branch `ccr-fff92b31-b7kqlu`) at the time of the builds, working tree without changes under `sw/`; `sw/` is the same at `3f9bd7e` (`git diff` empty) |
| Manifest | `sw/west.yml`, Zephyr `v4.5.0` = `41d10b59730406bbab4ca9f1fbbe9e96aafb4966` (`west list`) |
| `hal_espressif` | `cc81db00233af6020f2fea9fbb0d0098fb3d0d86` |
| Workspace | repository root (`.west/config`: manifest path `sw`); fetched before this run with `west update --narrow -o=--depth=1` |
| west | 1.5.0 |
| Zephyr SDK | 1.0.1, minimal bundle `zephyr-sdk-1.0.1_linux-x86_64_minimal.tar.xz` (version asked by `zephyr/SDK_VERSION`) |
| Target toolchain | `toolchain_gnu_linux-x86_64_riscv64-zephyr-elf.tar.xz` only: GCC 14.3.0, GNU ld 2.43.1 |
| SDK host tools | installer `zephyr-sdk-x86_64-hosttools-standalone-0.10.sh` from the minimal bundle; only `dtc` (1.7.0) is used, through a symlink on `PATH` (the host has no `dtc`) |
| Download check | the three archives above and `hosttools_linux-x86_64.tar.xz` (downloaded, not used) match `sha256.sum` of the GitHub release `v1.0.1` (`sha256sum -c`: OK for each). The sum file comes from the same release, so this checks the transfer, not the origin |
| Host | Linux x86_64 (kernel 6.18), Python 3.13.18 (venv), CMake 3.28.3, Ninja 1.11.1, host GCC 13.3.0 (Ubuntu 24.04) |
| Python packages | `zephyr/scripts/requirements-base.txt`, `-build-test.txt`, `-run-test.txt` and `modules/hal/espressif/zephyr/requirements.txt` with pip (esptool 5.6.0, pyelftools 0.33, junitparser 5.0.3). The extras and compliance files are not installed |
| Espressif blobs | `west blobs fetch hal_espressif` **not run**: `west blobs list` shows all 73 blobs not present, and the build did not need them (no Wi-Fi or Bluetooth in `sw/app`) |

Logs and build trees are in the session scratchpad (`twister.log`, `build-c3.log`, `build-native.log`, `build-c3/`, `twister-out/`). They are not kept in the repository.

## 2. Commands
All from the repository root, in the venv, with the SDK `dtc` on `PATH`.

```sh
# 1. Host unit tests (the twister command of scripts/ci_sw.sh; -O only moves the output to the scratchpad)
ZEPHYR_TOOLCHAIN_VARIANT=host west twister -T sw/app/tests -p native_sim/native/64 --inline-logs -O <scratchpad>/twister-out

# 2. Host build of the app (last step of scripts/ci_sw.sh; -d only moves the output)
ZEPHYR_TOOLCHAIN_VARIANT=host west build -b native_sim sw/app --pristine -d <scratchpad>/build-native

# 3. Target build
ZEPHYR_TOOLCHAIN_VARIANT=zephyr ZEPHYR_SDK_INSTALL_DIR=<scratchpad>/zsdk \
  west build -p -b esp32c3_devkitm sw/app -d <scratchpad>/build-c3

# 4. Gate logic alone, target compiler and the -march/-mabi/-mcmodel/-Os/-std flags of the app build
riscv64-zephyr-elf-gcc -march=rv32imc_zicsr_zifencei -mabi=ilp32 -mcmodel=medlow -Os -std=c17 \
  -ffreestanding -ffunction-sections -fdata-sections -Wall -Wextra -Wconversion -Wpedantic \
  -c sw/app/src/gate.c -o <scratchpad>/gate-xc/gate.o
```

## 3. Results

### 3.1 Host unit tests (ran)
- Twister: **1 of 1** test configurations passed, **20 of 20** test cases passed, 0 failed, 0 errored, "with no warnings", 14.80 s. Suite `busy_light.gate`, platform `native_sim/native/64`, toolchain `host/gnu`.
- The 20 case names (TC-105 to TC-110 at unit level) are the same as in `sw-gate-unit-tests.md`; each has status `passed` in `twister.json`.

### 3.2 Host build of the app (built, ran)
- First try: **failed**. `/usr/include/stdint.h:26:10: fatal error: bits/libc-header-start.h: No such file or directory` (the `native_sim` build uses `-m32`). The host had no `gcc-multilib`. This is a gap of the machine, not of the code: the CI workflow installs `gcc-multilib`.
- After `apt-get install -y gcc-multilib` (4:13.2.0-7ubuntu1) in the session container: **built**, 106 steps, 0 lines with "warning".
- `zephyr.exe -stop_at=1` printed `*** Booting Zephyr OS build 41d10b597304 ***` and `<inf> main: busy-light starting`, then stopped at 1.000 s simulated time.

### 3.3 Target build for `esp32c3_devkitm` (built)
- Result: **success**, 254 build steps, 0 lines with "warning" in the log, about 21 s wall time.
- CMake output: `Board: esp32c3_devkitm, qualifiers: esp32c3`; `Found toolchain: zephyr 1.0.1`; `Found host-tools: zephyr 1.0.1`; `Zephyr version: 4.5.0 ... build: 41d10b597304`.
- Memory usage, as printed by the linker:

```
Memory region         Used Size  Region Size  %age Used
           FLASH:      134884 B    4194048 B      3.22%
     iram0_0_seg:       38064 B     378640 B     10.05%
     dram0_0_seg:         55 KB     378640 B     14.87%
     irom0_0_seg:       17296 B         4 MB      0.41%
     drom0_0_seg:       69348 B         4 MB      1.65%
    rtc_iram_seg:          36 B       8168 B      0.44%
rtc_reserved_seg:           0 B         24 B      0.00%
        IDT_LIST:           0 B         8 KB      0.00%
```

- esptool 5.6.0: "Successfully created ESP32-C3 image."
- `zephyr.bin`: 134 884 B, sha256 `75b509062d692f77c0e9adf4ad6d783284686c42458ba08e17f7eadbb9b67b74`. `zephyr.elf` sha256 `744400ed31bc42d82fe6f23d22c6fefa36005cce32163b40e104d64b79e7b73c`.
- Boot mode: `CONFIG_ESP_SIMPLE_BOOT=y`. This build has **no MCUboot, no sysbuild and no signature**. The E1 spike used `--sysbuild` with MCUboot, so the image sizes of the two records are not the same kind of image.

### 3.4 Gate logic in the target image (inspected)
- `sw/app/CMakeLists.txt` adds only `src/main.c`. `riscv64-zephyr-elf-nm` finds **0** `gate_` symbols in `zephyr.elf`. The target image therefore holds only `main.c` (one log line) and Zephyr. **It does not contain the SW-005 or SW-009 logic.**
- `gate.c` compiled alone with command 4: **0 warnings**; object size `.text` 884 B, `.data` 0 B, `.bss` 0 B (`riscv64-zephyr-elf-size`). It is not linked and not run. This is a size of the code, not the resource budget of plan 07 section 6 (the state and the store are owned by the caller).

## 4. What this shows and does not show
- **Shows:** the v4.5.0 workspace in the repository, Zephyr SDK 1.0.1 (riscv64 only) and the listed Python packages build the current `sw/app` for `esp32c3_devkitm` without warnings; the host tests still pass 20 of 20; `gate.c` compiles for RV32IMC with the target compiler without warnings.
- **Does not show:** any SW-005 or SW-009 behaviour on the target (the logic is not in the image); the Zephyr binding (GPIO interrupt, retained RAM, watchdog, LED layer, reset cause), which is not written; the `BL_*` Kconfig symbols of plan 07, which do not exist in `sw/app` (no `sw/app/Kconfig`), so the SW-009 note "the Kconfig symbols are not verified by a build" stays open; MCUboot, signing and the flash layout; that the image boots or runs on a chip; any timing.
- No requirement is verified by this record.

## 5. Not run, and differences from CI
- **Not run:** flashing, any hardware or bench step, `--sysbuild` / MCUboot build, `west blobs fetch hal_espressif`, static analysis (clang-tidy) on this run, any MISRA check (no MISRA claim), a CI run on the server (not seen).
- `scripts/ci_sw.sh` itself is not run. It makes `.venv-sw` in the repository, runs `west update` and `west packages pip --install`. Its two `west` commands are run by hand instead (section 2), with output moved to the scratchpad.
- Python 3.13.18 here, 3.12 in CI. `dtc` from the SDK host tools here, the Ubuntu package in CI. Not all of `west packages pip` is installed here (extras and compliance files left out).

## 6. Side effects outside the scratchpad
- Debian package `gcc-multilib` installed in the session container (cloud machine, not the owner's computer).
- Zephyr cache files in `/root/.cache/zephyr`.
- No CMake package registration (`west zephyr-export` and `setup.sh -c` not run).

## 7. Traceability
Plan 07; SW-005, SW-009 (build evidence only); TC-105 to TC-110 at unit level on the host (3.1).
