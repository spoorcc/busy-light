# Spike 7.1 runbook: first hardware session (E1 run part)

- **Status:** Draft. Nothing in this runbook has been run on hardware. Commands marked *(verify)* were not checked against the pinned Zephyr release.
- **Plan:** `docs/plans/03-spike-7-1-zephyr-esp32c3.md` (Draft, not approved). **Do not start before the owner approves plan 03.**
- **Scope:** read-only checks of the dev kit, flashing the two E1 test images, recording the results. No fuse is burned and no secure-boot or encryption step is done in this runbook.

## Before you start
- **Parts:** one ESP32-C3-DevKitM-1 (working kit, never fused), a USB cable, a WPA2 test access point with no link to the production network (plan 03, A6).
- **Workspace on the PC:** the steps below rebuild the workspace used for the E1 build records. A different folder is fine.
- **Write the kit label** (for example `K1`) on the board with a marker. Every log must carry it.

> **WARNING:** Do not run any `espefuse` command that has `burn` in its name. Do not run `espsecure` or `esptool` commands that write eFuses. This runbook uses only read commands for eFuses.

## 1. Set up the workspace
1. Create the folder and a Python virtual environment, then install `west`.

   ```
   python3 -m venv venv && ./venv/bin/pip install west
   mkdir ws && cd ws
   ../venv/bin/west init -m <path to this repository> --mf sw/west.yml --mr <branch>
   ../venv/bin/west config manifest.project-filter -- '-.*,+zephyr,+hal_espressif,+mcuboot,+mbedtls,+hostap,+psa-arch-tests,+tf-psa-crypto'
   ../venv/bin/west update --narrow -o=--depth=1
   ```

   Expected result: `zephyr`, `modules` and `bootloader` folders appear (about 900 MB).
2. Install the Python packages and fetch the Wi-Fi blobs.

   ```
   ../venv/bin/pip install -r zephyr/scripts/requirements-base.txt
   ../venv/bin/west packages pip --install
   ../venv/bin/west blobs fetch hal_espressif
   ```
3. Install the Zephyr SDK 1.0.1 with only the RISC-V toolchain.

   ```
   ./setup.sh -t riscv64-zephyr-elf -h
   export ZEPHYR_SDK_INSTALL_DIR=<sdk folder>
   ```

   Expected result: `riscv64-zephyr-elf-gcc` exists under the SDK folder.

## 2. Read-only checks of the kit (record all output)
1. Connect the kit by USB.
2. Read the chip data.

   ```
   esptool chip-id
   esptool flash-id
   ```

   Record: chip revision, flash size, flash chip ID, MAC address. **Secure boot needs revision v0.3 or newer.**
3. Read the eFuse state. This only reads.

   ```
   espefuse summary
   ```

   Record the full output in the log. Expected result: no secure-boot or flash-encryption bits set on a new kit *(verify)*.

## 3. Build and flash the E1 images
1. Build `hello_world` with MCUboot.

   ```
   west build -p always -b esp32c3_devkitm --sysbuild -d build/hello zephyr/samples/hello_world
   ```
2. Flash it and open the console.

   ```
   west flash -d build/hello
   west espressif monitor
   ```

   Expected result: the console shows `Hello World! esp32c3_devkitm` *(verify the text)*.
3. Build and flash the Wi-Fi shell sample the same way (`zephyr/samples/net/wifi/shell`, build folder `build/wifishell`).
4. Join the test access point from the shell.

   ```
   wifi connect -s <SSID> -k 1 -p <passphrase>
   ```

   *(verify the option names with `wifi connect -h`)*. Expected result: the shell reports a connection and an IPv4 address. Record the channel and RSSI.
5. Repeat the join [10] times (reset between) and record the time from the command to the IPv4 address.

## 4. Record the results
For each step write the following in a log file (plain text) with this header:

```
date:      <date and time>
kit:       <label>, chip revision <rev>, flash <id>
repo:      <git hash of this repository>
zephyr:    v4.5.0 (<git hash>), SDK 1.0.1
board:     esp32c3_devkitm
command:   <the exact command>
result:    measured | not run | failed (<text>)
```

Store each raw capture with its SHA-256 (`sha256sum`). Do not put Wi-Fi passphrases in the log. Put the log in `docs/verification/reports/` only after removing credentials.

**If it does not work:**
- `west flash` cannot open the port: check the cable and the group `dialout`; use `--esp-device /dev/ttyUSB0` *(verify)*.
- The kit does not start after flashing: press the reset button. If that fails, record the console text and stop. Do not try any eFuse command.
- Anything unexpected: stop and record the output. A failed step is a result.
