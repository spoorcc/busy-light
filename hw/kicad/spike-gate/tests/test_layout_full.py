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

    def test_cc_ic_symbol_has_the_datasheet_pins(self):
        # TUSB321 datasheet SLLSEO6C section 4: 12 pins, no ADR pin; VCONN is a feature, not a pin.
        names = {pin.name for unit in layout_full.BOXES["U1"].units for pin in unit.pins}
        self.assertEqual(names, {"CC1", "CC2", "VDD", "GND", "PORT", "VBUS_DET", "OUT1_N", "OUT2_N",
                                 "CURRENT_MODE", "VCONN_FAULT", "ID", "DIR"})

    def test_tps2553_in_the_vbus_path(self):
        self.assertEqual(self.pin_net[("U7", "1")], "VBUS_IC")
        self.assertEqual(self.pin_net[("U7", "3")], "VBUS_IC")
        self.assertEqual(self.pin_net[("U7", "6")], "+5V")
        self.assertEqual(self.pin_net[("U8", "IN")], "+5V")
        self.assertEqual(self.pin_net[("U8", "OUT")], "+3V3")
        self.assertEqual(self.pin_net[("U7", "5")], "ILIM")
        for r in ("R_ILIM1", "R_ILIM2", "R_ILIM3"):
            self.assertIn(self.pin_net[(r, "1")] if r == "R_ILIM1" else self.pin_net[(r, "2")], ("ILIM",))

    def test_switch_and_buffer_pins_follow_the_datasheets(self):
        """TPS2553 DBV (SLVS841G tab. 5-1): 1 IN, 2 GND, 3 EN, 4 FAULT, 5 ILIM, 6 OUT.
        SN74LVC1G125 / SN74AHCT1G125 DBV (SCES223U / SCLS378P): 1 OE, 2 A, 3 GND, 4 Y, 5 VCC."""
        pn = self.pin_net
        self.assertEqual([pn[("U7", str(i))] for i in (1, 2, 3, 4, 5, 6)],
                         ["VBUS_IC", "GND", "VBUS_IC", "FAULT_N", "ILIM", "+5V"])
        self.assertEqual([pn[("U10", str(i))] for i in (1, 2, 3, 4, 5)],
                         ["GND", "HOLD_OK", "GND", "HOLD_OK_RB", "+3V3"])
        self.assertEqual([pn[("U11", str(i))] for i in (1, 2, 3, 4, 5)],
                         ["GND", "LED_DATA", "GND", "LED_BUF", "+5V"])
        for ref in ("U10", "U11"):
            self.assertEqual(layout_full.PARTS[ref][2], "Package_TO_SOT_SMD:SOT-23-5")
        self.assertEqual(layout_full.PARTS["U7"][2], "Package_TO_SOT_SMD:SOT-23-6")

    def test_gate_inputs_and_readbacks(self):
        for g in ("U3", "U4"):
            self.assertEqual(self.pin_net[(g, "1")], "CC_OK_1A5")
            self.assertEqual(self.pin_net[(g, "6")], "HOLD_OK")
        self.assertEqual(self.pin_net[("U9", "GPIO0")], "CC_OK_1A5")
        self.assertEqual(self.pin_net[("U9", "GPIO1")], "CC_OK_3A")
        self.assertEqual(self.pin_net[("U10", "4")], "HOLD_OK_RB")
        self.assertEqual(self.pin_net[("U9", "GPIO6")], "HOLD_OK_RB")

    def test_no_mcu_net_is_pulled_to_5v_or_driven_by_a_5v_output(self):
        """Derived from the connections, not from net names: a pull-up resistor to a 5 V rail, or a
        output pin of a part that runs on 5 V (U1 7/8, U5 1, U7 6, U11 4) on the same net as an MCU pin."""
        rails = {"VBUS", "VBUS_IC", "+5V"}
        five_volt_outputs = {("U1", "7"), ("U1", "8"), ("U5", "1"), ("U7", "6"), ("U11", "4")}
        for (ref, pin), net in self.pin_net.items():
            if ref != "U9" or net in ("+3V3", "GND"):
                continue
            for (r2, p2) in self.intent[net]:
                if r2[0] == "R":
                    other = "2" if p2 == "1" else "1"
                    self.assertNotIn(self.pin_net[(r2, other)], rails, f"U9 {pin}: {r2} pulls {net} to 5 V")
                if (r2, p2) == ("U7", "4"):     # TPS2553 FAULT: open drain, must be pulled up to 3V3
                    self.assertEqual(self.pin_net[("R8", "1")], "+3V3")
                    self.assertEqual(self.pin_net[("R8", "2")], net)
                    continue
                self.assertNotIn((r2, p2), five_volt_outputs, f"U9 {pin} on {net} shares a net with {r2} pin {p2}")

    def test_strapping_pins_have_defined_levels(self):
        """Module datasheet Tables 4-1 and 4-3: GPIO2 and GPIO8 float by default; both pulled up."""
        for pin, ref in (("GPIO2", "R16"), ("GPIO8", "R17")):
            net = self.pin_net[("U9", pin)]
            self.assertEqual(self.pin_net[(ref, "2")], net)
            self.assertEqual(self.pin_net[(ref, "1")], "+3V3")
            self.assertEqual({r for r, _ in self.intent[net]}, {"U9", ref})
        self.assertEqual(layout_full.PARTS["R16"][-1], "10k")

    def test_gate_enable_readbacks(self):
        self.assertEqual(self.pin_net[("U3", "4")], "ILIM_STEP2_EN")
        self.assertEqual(self.pin_net[("U4", "4")], "ILIM_STEP3_EN")
        self.assertEqual(self.pin_net[("U9", "GPIO20")], "STEP2_EN_RB")
        self.assertEqual(self.pin_net[("U9", "GPIO21")], "STEP3_EN_RB")
        self.assertEqual({self.pin_net[("R14", "1")], self.pin_net[("R14", "2")]}, {"ILIM_STEP2_EN", "STEP2_EN_RB"})
        self.assertEqual({self.pin_net[("R15", "1")], self.pin_net[("R15", "2")]}, {"ILIM_STEP3_EN", "STEP3_EN_RB"})

    def test_no_uart_test_points(self):
        self.assertFalse({"UART_TX", "UART_RX"} & set(self.pin_net.values()))

    def test_every_gpio_in_use_is_listed(self):
        used = {p[1] for p in self.pin_net if p[0] == "U9"} - {"3V3", "GND"}
        self.assertEqual(used, {"GPIO0", "GPIO1", "GPIO3", "GPIO10", "GPIO4", "GPIO5", "GPIO6", "GPIO7",
                                "GPIO18", "GPIO19", "GPIO20", "GPIO21", "GPIO9", "GPIO2", "GPIO8", "EN"})

    def test_test_points(self):
        nets = {self.pin_net[(f"TP{i}", "1")] for i in range(1, 7)}
        self.assertEqual(nets, {"+5V", "+3V3", "GND", "LED_DATA", "CHIP_EN", "BOOT"})


if __name__ == "__main__":
    unittest.main()
