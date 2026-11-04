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
def step_enable(out1_n, sel, pullup_present=True, gate_logic_powered=True,
                vbus_present=True, hold_done=True, supervisor_stuck_high=False):
    """Ideal model of one gated step.

    The IC output pull-up goes to VBUS_IC (not 3V3): with VBUS gone and 3V3 still up, the output
    reads 0 V, "CC OK" goes high (RV-008 v3a finding H1) and only the hold-off input keeps the
    gate closed, through the pull-up of HOLD_OK to VBUS_IC. A supervisor stuck high is a single
    fault that removes the hold-off (RISK-044) and is not covered by the gate itself.
    """
    if not gate_logic_powered:
        return False                      # unpowered AND output is low
    if not vbus_present:
        level = 0                         # pull-up and IC supply both gone: output reads 0 V
        hold = supervisor_stuck_high      # HOLD_OK pulled up to the absent VBUS_IC
    else:
        level = {"low": 0, "short_low": 0, "short_high": 1,
                 "high_z": 1 if pullup_present else None}[out1_n]
        hold = hold_done or supervisor_stuck_high
    if level is None:
        return False                      # floating input: not treated as "high" (HW-010 rule)
    ok = (level == 0)                     # inverter U2
    return ok and sel and hold


class GateNetlist(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nets = load(os.environ["GATE_NET"])

    def test_ok_net_feeds_both_ands(self):
        ok = net_of(self.nets, "U2", "4")
        self.assertEqual(ok, "CC_OK_1A5")
        self.assertEqual(net_of(self.nets, "U3", "1"), ok)
        self.assertEqual(net_of(self.nets, "U4", "1"), ok)

    def test_ic_output_has_pullup_to_ic_supply(self):
        out = net_of(self.nets, "U1", "3")
        self.assertEqual(net_of(self.nets, "U2", "2"), out)
        self.assertEqual(net_of(self.nets, "R1", "2"), out)
        self.assertEqual(net_of(self.nets, "R1", "1"), "VBUS_IC")  # not 3V3: VDD + 0.3 V pin rating

    def test_pulldowns_on_inputs_and_enables(self):
        for ref, gate_pin in (("R2", ("U3", "4")), ("R3", ("U4", "4")),
                              ("R4", ("U3", "3")), ("R5", ("U4", "3"))):
            self.assertEqual(net_of(self.nets, ref, "2"), "GND")
            self.assertEqual(net_of(self.nets, ref, "1"), net_of(self.nets, *gate_pin))

    def test_enable_drives_mosfet_gate(self):
        self.assertEqual(net_of(self.nets, "Q2", "1"), net_of(self.nets, "U3", "4"))
        self.assertEqual(net_of(self.nets, "Q3", "1"), net_of(self.nets, "U4", "4"))

    def test_ic_is_supplied_from_vbus_not_3v3(self):
        self.assertEqual(net_of(self.nets, "U1", "1"), "VBUS_IC")

    def test_hold_off_input_on_both_ands(self):
        hold = net_of(self.nets, "U5", "1")
        self.assertEqual(hold, "HOLD_OK")
        self.assertEqual(net_of(self.nets, "U3", "6"), hold)
        self.assertEqual(net_of(self.nets, "U4", "6"), hold)

    def test_hold_off_supervisor_on_ic_supply_with_pullup_to_ic_supply(self):
        # Pull-up to VBUS_IC (not 3V3): an unpowered supervisor must read "hold-off not done".
        self.assertEqual(net_of(self.nets, "U5", "2"), "VBUS_IC")  # VDD (TPS3840 DBV pin order)
        self.assertEqual(net_of(self.nets, "R6", "1"), "VBUS_IC")
        self.assertEqual(net_of(self.nets, "R6", "2"), "HOLD_OK")
        self.assertEqual(net_of(self.nets, "C1", "1"), net_of(self.nets, "U5", "5"))   # CT
        self.assertEqual(net_of(self.nets, "U5", "1"), "HOLD_OK")                   # RESET
        self.assertEqual(net_of(self.nets, "U5", "3"), "GND")
        self.assertEqual(net_of(self.nets, "C1", "2"), "GND")

    def test_no_single_pin_named_nets_except_placeholders(self):
        # Review finding: Net("ILIM") created twice gave two one-pin nets that parity ignored.
        allowed = {"CC_OUT2_N", "CC_RESERVED", "SUP_MR_NC"}
        for name, pins in self.nets.items():
            real = {p for p in pins if not p[0].startswith("#")}
            if len(real) < 2 and name not in allowed and not name.startswith("unconnected"):
                self.fail(f"net {name} has only {sorted(real)}")

    def test_ilim_is_one_net_with_both_switches(self):
        self.assertEqual(net_of(self.nets, "R_ILIM2", "2"), "ILIM")
        self.assertEqual(net_of(self.nets, "R_ILIM3", "2"), "ILIM")

    def test_six_pin_gates_use_a_six_pin_footprint(self):
        text = os.environ["GATE_NET"]
        text = Path(text).read_text()
        for ref in ("U3", "U4"):
            blk = text[text.index(f'(ref "{ref}")'):][:600]
            self.assertIn("SOT-23-6", blk)
        self.assertIn("SOT-23-5", text[text.index('(ref "U5")'):][:600])   # supervisor: 5-pin package

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

    def test_hold_off_blocks_even_a_good_reading(self):
        self.assertFalse(step_enable("low", True, hold_done=False))
        self.assertTrue(step_enable("low", True, hold_done=True))

    def test_vbus_gone_with_3v3_up_stays_closed_only_through_the_hold_off(self):
        # v3a finding H1: "CC OK" is high here, so the hold-off input is the only barrier.
        self.assertFalse(step_enable("high_z", True, vbus_present=False))
        self.assertTrue(step_enable("high_z", True, vbus_present=False, supervisor_stuck_high=True))

    def test_not_covered_fault_is_visible(self):
        # IC output shorted low: both the gate and the firmware see "1.5 A" (RISK-042).
        self.assertTrue(step_enable("short_low", True))


if __name__ == "__main__":
    unittest.main()
