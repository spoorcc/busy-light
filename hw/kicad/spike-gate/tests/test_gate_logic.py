# SPDX-License-Identifier: Apache-2.0
"""Connectivity and truth-table checks of the generated gate netlist (ADR-0016, HW-010 Draft).

Not a circuit simulation: the gates and the IC output are modelled as ideal logic, and the
fault cases are evaluated on that model. Run: GATE_NET=<dir>/gate.net python3 -m unittest -v
"""
import itertools
import os
import re
import unittest
from pathlib import Path


def load(path):
    text = Path(path).read_text()
    text = text[text.index("(nets"):]
    nets = {}
    for blk in re.split(r"\(net\s*\(code", text)[1:]:
        name = re.search(r'\(name "([^"]*)"', blk).group(1)
        nets[name] = set(re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', blk))
    return nets


def net_of(nets, ref, pin):
    for n, pins in nets.items():
        if (ref, pin) in pins:
            return n
    return None


# Ideal model of the gate path. out1_n: level of the open-drain IC output
# ("low" = IC reports >= 1.5 A, "high_z" = released or IC unpowered, "short_high", "short_low").
def step_enable(out1_n, sel, pullup_present=True, gate_logic_powered=True):
    if not gate_logic_powered:
        return False                      # unpowered AND output is low
    level = {"low": 0, "short_low": 0, "short_high": 1,
             "high_z": 1 if pullup_present else None}[out1_n]
    if level is None:
        return False                      # floating input: not treated as "high" (HW-010 rule)
    ok = (level == 0)                     # inverter U2
    return ok and sel


class GateNetlist(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nets = load(os.environ["GATE_NET"])

    def test_ok_net_feeds_both_ands(self):
        ok = net_of(self.nets, "U2", "4")
        self.assertEqual(ok, "CC_OK_1A5")
        self.assertEqual(net_of(self.nets, "U3", "1"), ok)
        self.assertEqual(net_of(self.nets, "U4", "1"), ok)

    def test_ic_output_has_pullup_to_3v3(self):
        out = net_of(self.nets, "U1", "3")
        self.assertEqual(net_of(self.nets, "U2", "2"), out)
        self.assertEqual(net_of(self.nets, "R1", "2"), out)
        self.assertEqual(net_of(self.nets, "R1", "1"), "+3V3")

    def test_pulldowns_on_inputs_and_enables(self):
        for ref, gate_pin in (("R2", ("U3", "4")), ("R3", ("U4", "4")),
                              ("R4", ("U3", "2")), ("R5", ("U4", "2"))):
            self.assertEqual(net_of(self.nets, ref, "2"), "GND")
            self.assertEqual(net_of(self.nets, ref, "1"), net_of(self.nets, *gate_pin))

    def test_enable_drives_mosfet_gate(self):
        self.assertEqual(net_of(self.nets, "Q2", "1"), net_of(self.nets, "U3", "4"))
        self.assertEqual(net_of(self.nets, "Q3", "1"), net_of(self.nets, "U4", "4"))

    def test_both_ands_share_the_same_ic_path(self):
        # Finding H1 of RV-008: one IC fault reaches both steps and the firmware read.
        self.assertEqual(net_of(self.nets, "U3", "1"), net_of(self.nets, "U4", "1"))


class TruthTable(unittest.TestCase):
    def test_gate_needs_both(self):
        for out, sel in itertools.product(("low", "high_z"), (False, True)):
            self.assertEqual(step_enable(out, sel), out == "low" and sel)

    def test_source_with_default_current_never_enables(self):
        for sel in (False, True):
            self.assertFalse(step_enable("high_z", sel))

    def test_faults_resolve_to_lowest_step(self):
        self.assertFalse(step_enable("high_z", True, gate_logic_powered=False))   # logic unpowered
        self.assertFalse(step_enable("high_z", True))                             # IC unpowered
        self.assertFalse(step_enable("short_high", True))                         # output shorted high
        self.assertFalse(step_enable("high_z", True, pullup_present=False))       # pull-up open

    def test_not_covered_fault_is_visible(self):
        # IC output shorted low: both the gate and the firmware see "1.5 A" (RISK-042).
        self.assertTrue(step_enable("short_low", True))


if __name__ == "__main__":
    unittest.main()
