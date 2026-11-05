# Zephyr facts: USB-Serial-JTAG console and GPIO pull handling on ESP32-C3

- **Status:** Draft (evidence report; nothing here is Approved)
- **Date:** 2026-11-05
- **Traces to:** SW-009 (proposed amendment), HW-010 (open point M3), HW-006, ADR-0016, owner-decisions-2026-11-05.md items 10 and section 2
- **Method:** static reading of the source of the pinned revision. No build, no hardware run.

## 1. Pinned revisions and how the source was obtained

| Item | Value | Source |
|---|---|---|
| Zephyr | `v4.5.0`, commit `41d10b59730406bbab4ca9f1fbbe9e96aafb4966` | `sw/west.yml` (`revision: v4.5.0`); `git clone --depth 1 --branch v4.5.0` from GitHub, `git rev-parse HEAD` |
| hal_espressif | `cc81db00233af6020f2fea9fbb0d0098fb3d0d86` | `west.yml` of the Zephyr tree, line 174-175; fetched with `git fetch --depth 1` of that commit, HEAD confirmed equal |
| ESP32-C3 TRM | v1.4 | `/home/ben/Programming/busy-light-datasheets/esp32-c3-technical-reference-manual-v1.4.pdf` (text extracted with pdftotext) |

All paths below are relative to the Zephyr tree at that commit unless they start with `hal_espressif:`. The trees were treated as untrusted data and were only read, never built or run.

## 2. Fact 1: console and logs on USB-Serial-JTAG

### 2.1 Findings

1. The device-tree node exists. `usb_serial: uart@60043000` with `compatible = "espressif,esp32-usb-serial"`, `status = "disabled"` by default (`dts/riscv/espressif/esp32c3/esp32c3_common.dtsi:234-243`). The binding includes `uart-controller.yaml` (`dts/bindings/serial/espressif,esp32-usb-serial.yaml`).
2. The driver is `drivers/serial/serial_esp32_usb.c` (`DT_DRV_COMPAT espressif_esp32_usb_serial`, line 8). Its Kconfig symbol is **`CONFIG_SERIAL_ESP32_USB`** (`drivers/serial/Kconfig.esp32:17-31`). It is `default y`, depends on `DT_HAS_ESPRESSIF_ESP32_USB_SERIAL_ENABLED` and selects `SERIAL_HAS_DRIVER` and `SERIAL_SUPPORT_INTERRUPT`. So the symbol is not set by hand; it follows the node status. There is no symbol called `CONFIG_USB_SERIAL_JTAG` or `CONFIG_UART_ESP32_USB` in this tree.
3. The driver offers polling and interrupt-driven API only (`poll_in`, `poll_out` lines 55-91; FIFO functions from line 139 under `CONFIG_UART_INTERRUPT_DRIVEN`). No async API.
4. The driver init enables the USB module clock and the PHY pad (`usb_serial_jtag_ll_phy_enable_pad(true)`, `serial_esp32_usb.c:100-114`). It touches the fixed USB pads GPIO18 and GPIO19 only. It does not touch GPIO20 or GPIO21 and has no pinctrl.
5. The upstream board `boards/espressif/esp32c3_devkitm/esp32c3_devkitm.dts` already has `&usb_serial { status = "okay"; }` (lines 56-59, with the comment "requires resoldering of resistors on the board") but selects `uart0` as console and shell (lines 19-20) and enables `uart0` with pinctrl `uart0_default` (lines 47-52). Its defconfig has `CONFIG_CONSOLE=y`, `CONFIG_SERIAL=y`, `CONFIG_UART_CONSOLE=y`, `CONFIG_GPIO=y` (`esp32c3_devkitm_defconfig:3-6`).
6. `CONFIG_UART_CONSOLE` depends on `SERIAL && SERIAL_HAS_DRIVER` (`drivers/console/Kconfig:42-44`). The console driver takes the device from `DT_CHOSEN(zephyr_console)` (`drivers/console/uart_console.c:42`). The UART log backend uses `zephyr,log-uart` if present, else `zephyr,console` (`subsys/logging/backends/log_backend_uart.c:31-39, 259`). The shell UART backend uses `zephyr,shell-uart` (`subsys/shell/backends/shell_uart.c:583, 601`; its Kconfig symbol `SHELL_BACKEND_SERIAL` defaults from the chosen node, `subsys/shell/backends/Kconfig.backends:17-19`). So pointing `zephyr,console` (and `zephyr,shell-uart` if a shell is used) at `&usb_serial` is enough for Zephyr console, logs and shell.
7. The SoC console glue derives the ROM console setting from `zephyr,console` (`soc/espressif/common/Kconfig.console:55-57, 65, 73`): with `usb_serial` enabled and chosen, `ESP_CONSOLE_USB_SERIAL_JTAG=y`, `ESP_CONSOLE_UART_NUM = ESP_ROM_USB_SERIAL_DEVICE_NUM` (3 on C3, lines 40-46) and `ESP_CONSOLE_UART` stays unset. Then `esp_console_init()` is the USB variant: it switches the ROM print buffer and `esp_rom_output_set_as_console` to the USB-Serial-JTAG device (`hal_espressif:zephyr/common/console_init.c:54-68`). It is called from the C3 early hardware init (`soc/espressif/esp32c3/hw_init.c`, under `#ifdef CONFIG_ESP_CONSOLE`, about line 44-47). So early Zephyr/ROM-library prints also leave the UART0 path.
8. `CONFIG_ESP_USB_SERIAL_JTAG_ENABLED` is `default y` on C3 and keeps the USB-Serial-JTAG clock and pads on at boot (`soc/espressif/common/Kconfig.console:82-95`). Leave it on.

### 2.2 GPIO20 and GPIO21 are left alone only if `uart0` is disabled

`GPIO20` is `UART0_RX` and `GPIO21` is `UART0_TX`. Zephyr configures them only through the `uart0` node: the UART driver applies pinctrl state `default` in its PM `TURN_ON` action, which runs from `uart_esp32_init` (`drivers/serial/uart_esp32.c:1599, 1626-1632`). The board pinctrl state is `UART0_TX_GPIO21` with `output-high` and `UART0_RX_GPIO20` with `bias-pull-up` (`boards/espressif/esp32c3_devkitm/esp32c3_devkitm-pinctrl.dtsi:10-20`). So with `uart0` at `status = "okay"` Zephyr drives GPIO21 high and enables the GPIO20 pull-up at boot, even when the console is on USB. A node with `status = "disabled"` creates no device and no `DT_HAS_..._ENABLED` entry for it, so no pin is touched.

Conclusion: the board devicetree for the busy-light must set `&uart0 { status = "disabled"; }` (the upstream devkit board enables it). Then Zephyr itself does not touch GPIO20 or GPIO21.

### 2.3 What Zephyr cannot change

The ROM boot message goes to UART0 before any Zephyr code runs. This is controlled by eFuse `EFUSE_UART_PRINT_CONTROL` and GPIO8 (TRM v1.4 section 7.3, Table 7.3-1, text lines 12158-12182 of the extracted TRM): with the eFuse at 0, the ROM prints on UART0 always; with the eFuse at 1, it prints only when GPIO8 is low. So GPIO21 is an output (TX) during ROM boot, as already noted in the HW-010 proposal. The owner decision (no eFuse burnt, 100 kohm series resistor on the readback) stays valid; this report does not change it. `EFUSE_USB_PRINT_CHANNEL` selects whether the ROM also prints to USB-Serial-JTAG.

### 2.4 Proposed configuration (not built)

Board overlay (or board devicetree for the custom board; the busy-light has no board directory yet, `sw/app/boards/` is empty):

```dts
/ {
	chosen {
		zephyr,console = &usb_serial;
		zephyr,shell-uart = &usb_serial;   /* only if a shell is used */
	};
};

&uart0 {
	status = "disabled";
};

&usb_serial {
	status = "okay";
};
```

`prj.conf` (a custom board that does not inherit the devkit defconfig needs these; they are harmless duplicates on the devkit):

```
CONFIG_CONSOLE=y
CONFIG_SERIAL=y
CONFIG_UART_CONSOLE=y
CONFIG_LOG=y
CONFIG_GPIO=y
```

Do not set `CONFIG_SERIAL_ESP32_USB` or `CONFIG_UART_ESP32` by hand; they follow the node status. After a build, check `build/zephyr/.config` for `CONFIG_SERIAL_ESP32_USB=y`, `CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG=y`, `# CONFIG_UART_ESP32 is not set`, and `build/zephyr/zephyr.dts` for `usb_serial` okay and `uart0` disabled.

## 3. Fact 2: does `gpio_pin_configure(..., GPIO_INPUT)` clear the pulls on ESP32-C3

### 3.1 Findings

1. `drivers/gpio/gpio_esp32.c`, function `gpio_esp32_config` (line 104):
   - Line 137: `gpio_ll_func_sel(&GPIO, io_pin, PIN_FUNC_GPIO)`. The pin leaves the U0RXD/U0TXD IO MUX function (`PIN_FUNC_GPIO` is 1, `hal_espressif:components/soc/esp32c3/register/soc/io_mux_reg.h:120`).
   - Line 144: `gpio_pull = !rtc_gpio_is_valid_gpio(io_pin) || GPIO_RTCIO_ARE_INDEPENDENT`. `GPIO_RTCIO_ARE_INDEPENDENT` is 1 for every SoC except the original ESP32 (lines 70-78). So on the C3 the GPIO/IO MUX registers carry the pull configuration.
   - Lines 148-166: when `GPIO_PULL_UP` is **not** in the flags, the else branch calls `gpio_ll_pullup_dis`. Lines 180-198: when `GPIO_PULL_DOWN` is not in the flags, `gpio_ll_pulldown_dis` is called.
   - Lines 256-257: with `GPIO_INPUT`, `gpio_ll_input_enable`.
   - Lines 250-253: without `GPIO_OUTPUT` and without the Espressif-specific `ESP32_GPIO_PIN_OUT_EN` flag, `gpio_ll_output_disable`.
2. `hal_espressif:components/esp_hal_gpio/esp32c3/include/hal/gpio_ll.h`: `gpio_ll_pullup_dis` (lines 60-68) clears `FUN_PU` (bit 8) in `IO_MUX_GPIO0_REG + 4*n`; the special USB D+ handling applies to GPIO19 only (lines 62-67). `gpio_ll_pulldown_dis` (lines 89-92) clears `FUN_PD` (bit 7). `FUN_PU`/`FUN_PD` definitions: `components/soc/esp32c3/register/soc/io_mux_reg.h:43, 48`. The TRM names the same bits `IO_MUX_GPIOn_FUN_WPU` and `IO_MUX_GPIOn_FUN_WPD` (TRM Register 5.21, text lines 11522-11526).

Answer: **yes**. In this revision, `gpio_pin_configure(dev, pin, GPIO_INPUT)` on GPIO20 or GPIO21 of the ESP32-C3 clears the internal pull-up and the internal pull-down, because the driver writes both pull bits from the flags on every call (clear when the flag is absent). It also switches the pad to GPIO function and disables the output driver. The same holds for `GPIO_INPUT | GPIO_ACTIVE_HIGH`. A devicetree `gpios` specifier carries the pull flags: if a node written for these pins contains `GPIO_PULL_UP`, the pull is set. Do not write pull flags in the readback nodes.

Caveat: this is a reading of the code, not a measured register. The readback of the bit in a test (section 5) turns it into evidence.

### 3.2 Reset default of GPIO20 and GPIO21 (TRM v1.4)

TRM v1.4 section 5.12, Table 5.12-1 "IO MUX Pin Functions", column "Reset" and key "Reset Configurations" (extracted text lines 10610-10611 and 10640-10648):

| Pin | Module pin (ESP32-C3-MINI-1, from the HW-010 proposal) | TRM Reset code | Meaning |
|---|---|---|---|
| GPIO20 (U0RXD) | 30 | 3 | IE = 1, WPU = 1: input enabled, **pull-up enabled** |
| GPIO21 (U0TXD) | 31 | 4 | OE = 1, WPU = 1: **output enabled, pull-up enabled** |

So both pins have the internal pull-up on after reset (the TRM does not give the pull-up resistance for these pins in the extracted text; the D+ values 2.2/1.1 kohm in the HW-010 proposal are for GPIO19 only). With the pull-up and the output enabled, GPIO21 is in the UART0 TX function after reset, which matches the ROM print behaviour in section 2.3. Between reset and the first `gpio_pin_configure` call, both pull-ups are on; the 2.1 V problem for a low gate in the HW-010 analysis therefore exists from reset until the firmware has configured the pins. SW-009 must say that the readbacks are not valid before the configuration call and the CC_OK validity rule (`HOLD_OK_RB` high) must not depend on GPIO20/21 before then. The hardware effect of the pull-up during that window (a 45 kohm pull-up against the 100 kohm readback resistor) is a hardware question for the HW-010 analysis and is not settled here.

## 4. Evidence summary

| Claim | Evidence | Strength |
|---|---|---|
| `usb_serial` node exists on C3 | `esp32c3_common.dtsi:234-243` | read in source |
| Driver symbol is `SERIAL_ESP32_USB`, follows node status | `Kconfig.esp32:17-31` | read in source |
| Chosen `zephyr,console` selects USB console, logs, ROM output | `Kconfig.console`, `console_init.c:54-68`, `log_backend_uart.c:31-39,259` | read in source |
| `uart0` must be disabled to keep GPIO20/21 untouched | `uart_esp32.c:1599,1626-1632`, pinctrl dtsi `:10-20`, upstream board dts `:47-52` | read in source; inference that a disabled node creates no device |
| `GPIO_INPUT` clears pulls | `gpio_esp32.c:148-166, 180-198`; `gpio_ll.h:60-68, 89-92` | read in source |
| GPIO20/21 reset pulls | TRM v1.4 Table 5.12-1 and key | read in datasheet |

## 5. Not verified (not run)

- **No build was run.** `west` is not installed (`import west` fails; no `west` in PATH). The Zephyr SDK 0.17.4 is at `~/zephyr-sdk-0.17.4` (with `riscv64-zephyr-elf`), but without west and the Python build dependencies the proposed overlay was not built, so the devicetree, the Kconfig symbols in section 2.4 and the absence of `CONFIG_UART_ESP32` are read, not generated. No tool was installed to get around this.
- No run on hardware: that the USB-Serial-JTAG enumerates, that logs appear, that the shell works over it, that nothing at GPIO20/21 changes after boot (scope or multimeter).
- The register state of `IO_MUX_GPIO20_REG` and `IO_MUX_GPIO21_REG` (`0x60009054`, `0x60009058`, i.e. `DR_REG_IO_MUX_BASE` 0x60009000 in `hal_espressif:components/soc/esp32c3/register/soc/reg_base.h:27` plus TRM offsets 0x0054 and 0x0058) after `gpio_pin_configure` was not read.
- The ROM boot print on GPIO21 was not measured, and the eFuse and strapping behaviour is taken from the TRM text only.
- Whether anything else in the Zephyr or hal_espressif start-up (for example `soc_hw_init`, the ROM bootloader, a future MCUboot) configures GPIO20/21 was not searched exhaustively; only the console, UART driver, pinctrl and GPIO driver paths were read.
- The custom board (ESP32-C3-MINI-1) has no Zephyr board definition yet; the checks above use `esp32c3_devkitm` as the closest in-tree board. The module datasheet and TRM pin numbering was not re-checked here.
- The pull-up resistance of GPIO20/21 was not found in the TRM text read; the datasheet value (`esp32-c3-datasheet.pdf`) was not looked up.

## 6. Recommended text for SW-009 (proposal only; not Approved, not applied to `docs/requirements/sw.md`)

Replace the "Not checked" sentence of the proposed amendment with:

> **Statement addition (proposed):** The firmware shall configure GPIO20 and GPIO21 as inputs without any pull (no `GPIO_PULL_UP`, no `GPIO_PULL_DOWN`) before it reads the gate-enable readbacks, and shall treat the readbacks as invalid until that configuration has completed. The firmware shall send its console and logs over the USB-Serial-JTAG interface and shall not enable the `uart0` device, so that the firmware does not configure GPIO20 or GPIO21 for the UART.
>
> **Rationale addition:** After reset, GPIO20 has its pull-up enabled and GPIO21 has its output and pull-up enabled (ESP32-C3 TRM v1.4, Table 5.12-1). In Zephyr v4.5.0 `gpio_pin_configure` with `GPIO_INPUT` clears both pull bits and disables the output (`drivers/gpio/gpio_esp32.c`, `gpio_esp32_config`), and the UART driver would apply its pinctrl (GPIO21 output high, GPIO20 pull-up) if `uart0` were enabled. Evidence: `docs/verification/reports/zephyr-usb-console-and-gpio-pull-facts.md` (source reading, no build, no hardware run).
>
> **Acceptance criteria to add:**
> 1. The build configuration shows `usb_serial` as `zephyr,console`, `uart0` disabled in the final devicetree, `CONFIG_SERIAL_ESP32_USB=y`, `CONFIG_UART_ESP32` not set and `CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG=y` (inspection of `zephyr.dts` and `.config`, recorded in `docs/verification/`).
> 2. On the prototype, a test reads `IO_MUX_GPIO20_REG` and `IO_MUX_GPIO21_REG` after the start-up configuration and shows `FUN_WPU` (bit 8) and `FUN_WPD` (bit 7) both 0, and function select `MCU_SEL` equal to 1 (GPIO).
> 3. On the prototype, the log output is visible on the USB-C connector alone with no UART adapter connected, and a scope or logic analyser shows no UART activity on GPIO21 after the application has started (the ROM boot print before that is expected and is tolerated by the readback series resistor, owner decision 2026-11-05 item 10).
> 4. A unit test on the native/simulated build (with the GPIO emulator) shows that the readback code calls `gpio_pin_configure` with `GPIO_INPUT` only, and that a readback taken before configuration is reported as invalid.

Open questions for the owner: whether the readbacks need an active-low `GPIO_ACTIVE_LOW` flag in the devicetree (not a pull flag, so it does not affect this finding); whether the window between reset and the configuration call needs a hardware answer (section 3.2).
