# SPDX-License-Identifier: Apache-2.0
"""Full-board layout (ADR-0012 spike): determinism, intent facts, HW-007 and the 5 V rule for the MCU."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
import layout_full  # noqa: E402


# pin numbers of the KiCad symbol LED:WS2812B-2020 (layout_full.LED_*)
L_DOUT, L_VSS, L_DIN, L_VDD = (layout_full.LED_DOUT, layout_full.LED_VSS, layout_full.LED_DIN, layout_full.LED_VDD)


class PinNet(dict):
    """Intent pin -> net, keyed by pad number; U1 and U9 pins may also be looked up by name (layout_full.PAD)."""

    @staticmethod
    def _k(k):
        return (k[0], layout_full.pads(*k)[0])

    def __getitem__(self, k):
        return super().__getitem__(self._k(k))

    def get(self, k, default=None):
        return super().get(self._k(k), default)

    def __contains__(self, k):
        return super().__contains__(self._k(k))


def pin_net_of(intent):
    return PinNet({p: n for n, pins in intent.items() for p in pins})


class FullBoard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sch, cls.intent = layout_full.build()
        cls.pin_net = pin_net_of(cls.intent)

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
            self.assertEqual(self.pin_net[(f"D{i}", L_DOUT)], self.pin_net[(f"D{i + 1}", L_DIN)], f"D{i}")
        self.assertEqual(self.pin_net[("D8", L_DOUT)], self.pin_net[("D9", L_DIN)])   # row end to row start
        self.assertEqual(self.pin_net[("R10", "2")], self.pin_net[("D1", L_DIN)])
        self.assertEqual(sum(1 for r in layout_full.PARTS if r.startswith("D") and r[1:].isdigit()), 16)

    def test_every_led_has_a_5v_capacitor(self):
        for i in range(1, 17):
            self.assertEqual(self.pin_net[(f"D{i}", L_VDD)], "+5V")
            self.assertEqual(self.pin_net[(f"D{i}", L_VSS)], "GND")
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
        self.assertEqual(self.pin_net[("U1", "VDD")], "VDD_U1")
        self.assertEqual(self.pin_net[("R1", "1")], "VBUS_IC")     # pull-up on the IC supply, not 3V3
        self.assertNotIn("R7", layout_full.PARTS)                  # OUT2 reading deleted (owner decision 2026-11-07)
        self.assertNotIn("U12", layout_full.PARTS)
        self.assertNotIn("CC_OK_3A", self.pin_net.values())
        self.assertEqual(self.pin_net[("R21", "2")], self.pin_net[("U1", "VBUS_DET")])

    def test_cc_ic_symbol_has_the_datasheet_pins(self):
        # TUSB321 datasheet SLLSEO6C section 4: 12 pins, no ADR pin; VCONN is a feature, not a pin.
        names = {pin.name for unit in layout_full.BOXES["U1"].units for pin in unit.pins}
        self.assertEqual(names, {"CC1", "CC2", "VDD", "GND", "PORT", "VBUS_DET", "OUT1_N", "OUT2_N",
                                 "CURRENT_MODE", "VCONN_FAULT", "ID", "DIR"})

    def test_tps2553_in_the_vbus_path(self):
        self.assertEqual(self.pin_net[("U7", "1")], "VBUS_IC")
        self.assertEqual(self.pin_net[("U7", "3")], "VBUS_IC")
        self.assertEqual(self.pin_net[("U7", "6")], "+5V")
        self.assertEqual(self.pin_net[("U8", "1")], "+5V")
        self.assertEqual(self.pin_net[("U8", "5")], "+3V3")
        self.assertEqual(self.pin_net[("U7", "5")], "ILIM")
        for r in ("R_ILIM1", "R_ILIM2", "R_ILIM3"):
            self.assertIn(self.pin_net[(r, "1")] if r == "R_ILIM1" else self.pin_net[(r, "2")], ("ILIM",))

    def test_switch_and_buffer_pins_follow_the_datasheets(self):
        """TPS2553 DBV (SLVS841G tab. 5-1): 1 IN, 2 GND, 3 EN, 4 FAULT, 5 ILIM, 6 OUT.
        SN74LVC1G08 DBV (SCES217AA): 1 A, 2 B, 3 GND, 4 Y, 5 VCC. SN74AHCT1G125 DBV (SCLS378P): 1 OE, 2 A, 3 GND, 4 Y, 5 VCC."""
        pn = self.pin_net
        self.assertEqual([pn[("U7", str(i))] for i in (1, 2, 3, 4, 5, 6)],
                         ["VBUS_IC", "GND", "VBUS_IC", "FAULT_N", "ILIM", "+5V"])
        self.assertEqual([pn[("U10", str(i))] for i in (1, 2, 3, 4, 5)],
                         ["FAULT_N", "HOLD_OK", "GND", "GATE_OK_RB", "+3V3"])
        self.assertEqual([pn[("U11", str(i))] for i in (1, 2, 3, 4, 5)],
                         ["GND", "LED_DATA", "GND", "LED_BUF", "+5V"])
        for ref in ("U10", "U11"):
            self.assertEqual(layout_full.PARTS[ref][2], "Package_TO_SOT_SMD:SOT-23-5")
        self.assertEqual(layout_full.PARTS["U7"][2], "Package_TO_SOT_SMD:SOT-23-6")

    def test_gate_inputs_and_readbacks(self):
        self.assertEqual(self.pin_net[("U4", "1")], "CC_OK_1A5")
        self.assertEqual(self.pin_net[("U3", "1")], "CC_OK_NOT_S3")
        for g in ("U3", "U4"):
            self.assertEqual(self.pin_net[(g, "6")], "HOLD_OK")
        self.assertEqual(self.pin_net[("U9", "GPIO0")], "CC_OK_1A5")
        self.assertEqual(self.pin_net[("U10", "4")], "GATE_OK_RB")
        self.assertEqual(self.pin_net[("U9", "GPIO6")], "GATE_OK_RB")

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

    def test_exclusive_steps_nor_gate(self):
        """U13 74LVC1G02 (A=1, B=2, GND=3, Y=4, VCC=5): NOR(CC_OUT1_N, ILIM_STEP3_EN) feeds U3 pin 1."""
        pn = self.pin_net
        self.assertEqual([pn[("U13", str(i))] for i in (1, 2, 3, 4, 5)],
                         ["CC_OUT1_N", "ILIM_STEP3_EN", "GND", "CC_OK_NOT_S3", "+3V3"])
        self.assertEqual(layout_full.PARTS["U13"][1], "74LVC1G02")
        self.assertEqual(layout_full.PARTS["U13"][2], "Package_TO_SOT_SMD:SOT-23-5")
        self.assertEqual(pn[("U15", "4")], "ILIM_STEP3_EN")
        for ref, val in (("R2", "10k"), ("R3", "10k"), ("R14", "100k"), ("R15", "100k")):
            self.assertEqual(layout_full.PARTS[ref][-1], val)

    def test_ilim_resistor_values(self):
        P = layout_full.PARTS
        self.assertEqual((P["R_ILIM1"][-1], P["R_ILIM2"][-1], P["R_ILIM3"][-1], P["R20"][-1]),
                         ("47.0k 0.1%", "56.2k 0.1%", "27.4k 0.1%", "301 0.1%"))   # E96, HW-010 revision

    def test_tmux1101_ilim_switches(self):
        """Owner decision 2026-11-05 (a). TMUX1101DCK (SCDS410D tab. 5-1): 1 D, 2 S, 3 GND, 4 SEL, 5 VDD."""
        pn, P = self.pin_net, layout_full.PARTS
        for sw, en, r_ilim, cap, rpd in (("U14", "ILIM_STEP2_EN", "R_ILIM2", "C24", "R18"),
                                         ("U15", "ILIM_STEP3_EN", "R20", "C25", "R19")):
            self.assertEqual([pn[(sw, str(i))] for i in (2, 3, 4, 5)], ["GND", "GND", en, f"VDD_{sw}"])   # VDD from VBUS_IC through R_SU14 / R_SU15
            self.assertEqual(pn[(sw, "1")], pn[(r_ilim, "1")])
            self.assertEqual((pn[(cap, "1")], pn[(cap, "2")]), (f"VDD_{sw}", "GND"))
            self.assertEqual({pn[(rpd, "1")], pn[(rpd, "2")]}, {en, "GND"})
            self.assertEqual(P[rpd][-1], "100k")
            self.assertEqual(P[cap][-1], "100n")
            self.assertEqual(P[sw][-1], "TMUX1101DCKR")
            self.assertEqual(P[sw][2], "Package_TO_SOT_SMD:SOT-353_SC-70-5")
        self.assertNotIn("Q2", P)
        self.assertNotIn("Q3", P)
        self.assertEqual(pn[("R20", "2")], pn[("R_ILIM3", "1")])
        self.assertEqual(pn[("R_ILIM3", "2")], "ILIM")

    def test_holdoff_capacitor_set(self):
        """Owner decision 2026-11-06: six 100 nF C0G 5 % 1206 on SUP_CT (HW-010 revision)."""
        P = layout_full.PARTS
        vals = {r: P[r][-1] for r in ("C1", "C27", "C28", "C29", "C30", "C31")}
        self.assertEqual(sorted(v.split()[0] for v in vals.values()), ["100n"] * 6)
        for r, v in vals.items():
            self.assertIn("C0G 5%", v)
            self.assertEqual(self.pin_net[(r, "1")], "SUP_CT")
            self.assertEqual(self.pin_net[(r, "2")], "GND")
            self.assertEqual("Capacitor_SMD:C_1206_3216Metric", P[r][2])

    def test_no_uart_test_points(self):
        self.assertFalse({"UART_TX", "UART_RX"} & set(self.pin_net.values()))

    def test_every_gpio_in_use_is_listed(self):
        used = {p for r, p in dict.keys(self.pin_net) if r == "U9"} - set(layout_full.pads("U9", "GND")) - {"3"}
        self.assertEqual(used, {layout_full.pads("U9", n)[0] for n in (
            "GPIO0", "GPIO3", "GPIO10", "GPIO5", "GPIO6", "GPIO7",
            "GPIO18", "GPIO19", "GPIO20", "GPIO21", "GPIO9", "GPIO2", "GPIO8", "EN")})

    @staticmethod
    def _symbol_pins(ref):
        return {(pin.number, pin.name) for unit in layout_full.BOXES[ref].units for pin in unit.pins}

    def test_cc_ic_pin_numbers_are_the_datasheet_pads(self):
        """TUSB321 RWB, TI SLLSEO6C (Aug 2018) section 5 Pin Functions; schematic number = board pad number."""
        self.assertEqual(self._symbol_pins("U1"), {
            ("1", "CC1"), ("2", "CC2"), ("3", "CURRENT_MODE"), ("4", "PORT"), ("5", "VBUS_DET"),
            ("6", "VCONN_FAULT"), ("7", "OUT1_N"), ("8", "OUT2_N"), ("9", "ID"), ("10", "GND"), ("11", "DIR"),
            ("12", "VDD")})

    def test_module_pin_numbers_are_the_datasheet_pads(self):
        """ESP32-C3-MINI-1 datasheet v2.2 table 3-1 (p. 11): GND = 1, 2, 11, 14, 36 to 53 (49 = the 9 centre pads)."""
        pins = self._symbol_pins("U9")
        gnd = {n for n, name in pins if name == "GND"}
        self.assertEqual(gnd, {"1", "2", "11", "14"} | {str(i) for i in range(36, 54)})
        self.assertEqual({(n, name.split()[0]) for n, name in pins if name != "GND"}, {
            ("3", "3V3"), ("5", "GPIO2"), ("6", "GPIO3"), ("8", "EN"), ("12", "GPIO0"), ("13", "GPIO1"),
            ("16", "GPIO10"), ("18", "GPIO4"), ("19", "GPIO5"), ("20", "GPIO6"), ("21", "GPIO7"), ("22", "GPIO8"),
            ("23", "GPIO9"), ("26", "GPIO18"), ("27", "GPIO19"), ("30", "GPIO20"), ("31", "GPIO21")})

    def test_every_module_ground_pad_is_on_gnd(self):
        for p in layout_full.pads("U9", "GND"):
            self.assertEqual(dict.get(self.pin_net, ("U9", p)), "GND", p)

    def test_test_points_are_not_in_the_bom(self):
        """The TestPoint_Pad footprint is excluded from the BOM; the symbol must say the same (DRC parity)."""
        tps = [y for y in self.sch.schematicSymbols
               if any(p.key == "Reference" and p.value.startswith("TP") for p in y.properties)]
        self.assertEqual(len(tps), 6)
        self.assertTrue(all(y.inBom is False for y in tps))

    def test_test_points(self):
        nets = {self.pin_net[(f"TP{i}", "1")] for i in range(1, 7)}
        self.assertEqual(nets, {"+5V", "+3V3", "GND", "LED_DATA", "CHIP_EN", "BOOT"})



class SupplyPinProtection(unittest.TestCase):
    """HW-010 amendment (owner 2026-11-07): 470 ohm and 1 kohm in series, 100 nF and a 5.1 V zener at each 6 V pin."""

    @classmethod
    def setUpClass(cls):
        cls.sch, cls.intent = layout_full.build()
        cls.pin_net = pin_net_of(cls.intent)

    def test_resistor_from_vbus_to_each_protected_pin(self):
        for r, node, ohm in (("R_SU1", "VDD_U1", "470"), ("R_SU14", "VDD_U14", "1k"), ("R_SU15", "VDD_U15", "1k")):
            self.assertEqual(self.pin_net[(r, "1")], "VBUS_IC")
            self.assertEqual(self.pin_net[(r, "2")], node)
            self.assertEqual(layout_full.PARTS[r][3], ohm)

    def test_pins_are_on_the_protected_nodes_with_a_zener_and_a_capacitor(self):
        for pin, node, dz, cap in ((("U1", "VDD"), "VDD_U1", "DZ1", "C26"), (("U14", "5"), "VDD_U14", "DZ14", "C24"),
                                   (("U15", "5"), "VDD_U15", "DZ15", "C25")):
            self.assertEqual(self.pin_net[pin], node)
            self.assertEqual(self.pin_net[(dz, "3")], node)      # cathode on the node
            self.assertEqual(self.pin_net[(dz, "1")], "GND")     # anode on ground
            self.assertEqual(self.pin_net[(cap, "1")], node)
            self.assertEqual(self.pin_net[(cap, "2")], "GND")
            self.assertEqual(layout_full.PARTS[dz][3], "BZX84C5V1")

    def test_no_6v_supply_pin_is_left_on_the_raw_rail(self):
        for pin in (("U1", "VDD"), ("U14", "5"), ("U15", "5")):
            self.assertNotEqual(self.pin_net[pin], "VBUS_IC")


class GateOkReadback(unittest.TestCase):
    """ADR-0018 option E: GATE_OK_RB = HOLD_OK AND FAULT_N; GPIO4 and GPIO1 are free for the sensor."""

    @classmethod
    def setUpClass(cls):
        cls.sch, cls.intent = layout_full.build()
        cls.pin_net = pin_net_of(cls.intent)

    def test_fault_n_reaches_the_and_gate_with_a_3v3_pull_up_and_not_the_mcu(self):
        self.assertEqual(self.pin_net[("U10", "1")], "FAULT_N")
        self.assertEqual(self.pin_net[("U7", "4")], "FAULT_N")
        self.assertEqual(self.pin_net[("R8", "1")], "+3V3")
        self.assertEqual(self.pin_net[("R8", "2")], "FAULT_N")
        self.assertNotIn(("U9", "GPIO4"), self.pin_net)

    def test_sensor_pins_are_unused(self):
        for pin in ("GPIO1", "GPIO4"):
            self.assertNotIn(("U9", pin), self.pin_net)

    def test_gate_is_the_and_part(self):
        self.assertEqual(layout_full.PARTS["U10"][1], "74LVC1G08")


if __name__ == "__main__":
    unittest.main()
