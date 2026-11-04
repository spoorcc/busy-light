# SPDX-License-Identifier: Apache-2.0
"""Full-board layout (ADR-0012 spike): determinism, intent facts, HW-007 and the 5 V rule for the MCU."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
import layout_full  # noqa: E402


class FullBoard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sch, cls.intent = layout_full.build()
        cls.pin_net = {p: n for n, pins in cls.intent.items() for p in pins}

    def test_two_builds_are_identical(self):
        out = []
        for i in range(2):
            sch, _ = layout_full.build()
            f = HERE / f"_tmp_full_{i}.kicad_sch"
            sch.to_file(str(f))
            out.append(f.read_bytes())
            f.unlink()
        self.assertEqual(out[0], out[1])

    def test_sixteen_leds_in_one_chain(self):
        for i in range(1, 16):
            if i == 8:
                continue
            self.assertEqual(self.pin_net[(f"D{i}", "2")], self.pin_net[(f"D{i + 1}", "4")], f"D{i}")
        self.assertEqual(self.pin_net[("D8", "2")], self.pin_net[("D9", "4")])   # row end to row start
        self.assertEqual(self.pin_net[("R10", "2")], self.pin_net[("D1", "4")])
        self.assertEqual(sum(1 for r in layout_full.PARTS if r.startswith("D") and r[1:].isdigit()), 16)

    def test_every_led_has_a_5v_capacitor(self):
        for i in range(1, 17):
            self.assertEqual(self.pin_net[(f"D{i}", "1")], "+5V")
            self.assertEqual(self.pin_net[(f"D{i}", "3")], "GND")
            self.assertEqual(self.pin_net[(f"C{7 + i}", "1")], "+5V")
            self.assertEqual(self.pin_net[(f"C{7 + i}", "2")], "GND")

    def test_button_is_not_on_a_strapping_pin_hw007(self):
        net = self.pin_net[("R13", "2")]
        self.assertEqual(net, "BUTTON")
        self.assertEqual(self.pin_net[("U9", "GPIO5")], "BUTTON")
        for strap in ("GPIO2", "GPIO8", "GPIO9"):
            self.assertNotEqual(self.pin_net.get(("U9", strap)), "BUTTON")

    def test_no_5v_net_reaches_an_mcu_pin(self):
        five_volt = {"VBUS_IC", "+5V", "CC_OUT1_N", "CC_OUT2_N", "HOLD_OK", "LED_BUF"}
        for (ref, pin), net in self.pin_net.items():
            if ref == "U9":
                self.assertNotIn(net, five_volt, f"U9 {pin} on {net}")

    def test_cc_ic_is_sink_only_and_supplied_from_vbus(self):
        self.assertEqual(self.pin_net[("U1", "PORT")], "GND")
        self.assertEqual(self.pin_net[("U1", "VDD")], "VBUS_IC")
        self.assertEqual(self.pin_net[("R1", "1")], "VBUS_IC")     # pull-up on the IC supply, not 3V3
        self.assertEqual(self.pin_net[("R7", "1")], "VBUS_IC")
        self.assertEqual(self.pin_net[("R_VD", "2")], self.pin_net[("U1", "VBUS_DET")])

    def test_tps2553_in_the_vbus_path(self):
        self.assertEqual(self.pin_net[("U7", "1")], "VBUS_IC")
        self.assertEqual(self.pin_net[("U7", "3")], "VBUS_IC")
        self.assertEqual(self.pin_net[("U7", "6")], "+5V")
        self.assertEqual(self.pin_net[("U8", "IN")], "+5V")
        self.assertEqual(self.pin_net[("U8", "OUT")], "+3V3")
        self.assertEqual(self.pin_net[("U7", "5")], "ILIM")
        for r in ("R_ILIM1", "R_ILIM2", "R_ILIM3"):
            self.assertIn(self.pin_net[(r, "1")] if r == "R_ILIM1" else self.pin_net[(r, "2")], ("ILIM",))

    def test_gate_inputs_and_readbacks(self):
        for g in ("U3", "U4"):
            self.assertEqual(self.pin_net[(g, "1")], "CC_OK_1A5")
            self.assertEqual(self.pin_net[(g, "6")], "HOLD_OK")
        self.assertEqual(self.pin_net[("U9", "GPIO0")], "CC_OK_1A5")
        self.assertEqual(self.pin_net[("U9", "GPIO1")], "CC_OK_3A")
        self.assertEqual(self.pin_net[("U10", "4")], "HOLD_OK_RB")
        self.assertEqual(self.pin_net[("U9", "GPIO6")], "HOLD_OK_RB")

    def test_every_gpio_in_use_is_listed(self):
        used = {p[1] for p in self.pin_net if p[0] == "U9"} - {"3V3", "GND"}
        self.assertEqual(used, {"GPIO0", "GPIO1", "GPIO3", "GPIO10", "GPIO4", "GPIO5", "GPIO6", "GPIO7",
                                "GPIO18", "GPIO19", "GPIO20", "GPIO21", "GPIO9", "EN"})

    def test_test_points(self):
        nets = {self.pin_net[(f"TP{i}", "1")] for i in range(1, 9)}
        self.assertEqual(nets, {"+5V", "+3V3", "GND", "UART_TX", "UART_RX", "LED_DATA", "CHIP_EN", "BOOT"})


if __name__ == "__main__":
    unittest.main()
