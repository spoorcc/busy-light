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


def steps(cc_ok, sel2, sel3, hold, nor_powered=True, u3_powered=True, u4_powered=True,
          en3_open=False, en3_short_high=False, en3_short_low=False, nor_out_stuck_high=False):
    """Logic of both steps as drawn: U4 = AND3(cc_ok, sel3, hold) -> en3;
    U13 = NOR(NOT cc_ok, en3) -> ok2; U3 = AND3(ok2, sel2, hold) -> en2. Returns (en2, en3).
    cc_ok is the level of CC_OK_1A5 (= NOT CC_OUT1_N, so NOR input A is NOT cc_ok).
    Faults act on the net ILIM_STEP3_EN (open: R3 pulls the net low)."""
    en3_gate = bool(u4_powered and cc_ok and sel3 and hold)
    if en3_short_high:
        en3 = True
    elif en3_short_low or en3_open:
        en3 = False
    else:
        en3 = en3_gate
    ok2 = bool(nor_powered and not ((not cc_ok) or en3))
    if nor_out_stuck_high:
        ok2 = True
    en2 = bool(u3_powered and ok2 and sel2 and hold)
    return en2, en3


class GateNetlist(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nets = load(os.environ["GATE_NET"])

    def test_ok_net_feeds_step_3_and_nor_feeds_step_2(self):
        ok = net_of(self.nets, "U2", "4")
        self.assertEqual(ok, "CC_OK_1A5")
        self.assertEqual(net_of(self.nets, "U4", "1"), ok)
        self.assertEqual(net_of(self.nets, "U3", "1"), "CC_OK_NOT_S3")   # step 2: CC OK AND NOT step 3 enable

    def test_exclusive_steps_nor_wiring(self):
        # U13 74LVC1G02: A=1, B=2, GND=3, Y=4, VCC=5. Y = NOT(CC_OUT1_N OR ILIM_STEP3_EN).
        n = self.nets
        self.assertEqual(net_of(n, "U13", "1"), net_of(n, "U1", "3"))     # IC output CC_OUT1_N
        self.assertEqual(net_of(n, "U13", "2"), net_of(n, "U4", "4"))     # step 3 gate output, not the select line
        self.assertEqual(net_of(n, "U13", "4"), "CC_OK_NOT_S3")
        self.assertEqual(net_of(n, "U13", "3"), "GND")
        self.assertEqual(net_of(n, "U13", "5"), "+3V3")
        self.assertEqual(net_of(n, "U15", "4"), net_of(n, "U13", "2"))    # the NOR sees the real step 3 switch control

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

    def test_enable_drives_switch_control_pin(self):
        # TMUX1101DCK (SCDS410D tab. 5-1): 1 D, 2 S, 3 GND, 4 SEL, 5 VDD; SEL high = on (tab. 8-1)
        self.assertEqual(net_of(self.nets, "U14", "4"), net_of(self.nets, "U3", "4"))
        self.assertEqual(net_of(self.nets, "U15", "4"), net_of(self.nets, "U4", "4"))
        self.assertNotIn("Q2", {r for pins in self.nets.values() for r, _ in pins})
        self.assertNotIn("Q3", {r for pins in self.nets.values() for r, _ in pins})

    def test_switch_power_and_ground(self):
        for sw, cap in (("U14", "C24"), ("U15", "C25")):
            self.assertEqual(net_of(self.nets, sw, "5"), "+3V3")
            self.assertEqual(net_of(self.nets, sw, "3"), "GND")
            self.assertEqual(net_of(self.nets, sw, "2"), "GND")      # source side to ground, drain side to the resistor
            self.assertEqual(net_of(self.nets, cap, "1"), "+3V3")
            self.assertEqual(net_of(self.nets, cap, "2"), "GND")

    def test_control_pin_pulldowns_100k(self):
        for ref, sw, gate in (("R18", "U14", "U3"), ("R19", "U15", "U4")):
            self.assertEqual(net_of(self.nets, ref, "1"), net_of(self.nets, sw, "4"))
            self.assertEqual(net_of(self.nets, ref, "1"), net_of(self.nets, gate, "4"))
            self.assertEqual(net_of(self.nets, ref, "2"), "GND")

    def test_step_3_resistor_is_a_series_pair(self):
        n = self.nets
        self.assertEqual(net_of(n, "U15", "1"), net_of(n, "R_ILIM3B", "1"))
        self.assertEqual(net_of(n, "R_ILIM3B", "2"), net_of(n, "R_ILIM3", "1"))
        self.assertEqual(net_of(n, "R_ILIM3", "2"), "ILIM")
        self.assertNotEqual(net_of(n, "R_ILIM3B", "2"), "ILIM")
        self.assertEqual(net_of(n, "U14", "1"), net_of(n, "R_ILIM2", "1"))

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
        self.assertEqual(net_of(self.nets, "C1B", "1"), net_of(self.nets, "U5", "5"))   # parallel C0G part
        self.assertEqual(net_of(self.nets, "C1B", "2"), "GND")
        for ref in ("C1C", "C1D"):     # decision (c): 220 + 220 + 100 + 68 nF
            self.assertEqual(net_of(self.nets, ref, "1"), net_of(self.nets, "U5", "5"))
            self.assertEqual(net_of(self.nets, ref, "2"), "GND")

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

    def test_both_steps_share_the_same_ic_path(self):
        # Finding H1 of RV-008: one IC fault reaches both steps and the firmware read.
        n = self.nets
        self.assertEqual(net_of(n, "U13", "1"), net_of(n, "U2", "2"))
        self.assertEqual(net_of(n, "U4", "1"), net_of(n, "U2", "4"))


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


class ExclusiveSteps(unittest.TestCase):
    """Owner decision 2026-11-05: the step 2 and step 3 ILIM switches must never both be on (HW-010 proposal, ADR-0016)."""

    def test_truth_table_all_input_combinations(self):
        for cc_ok, hold, sel2, sel3 in itertools.product((False, True), repeat=4):
            en2, en3 = steps(cc_ok, sel2, sel3, hold)
            ok = cc_ok and hold
            self.assertEqual(en3, ok and sel3, (cc_ok, hold, sel2, sel3))
            self.assertEqual(en2, ok and sel2 and not sel3, (cc_ok, hold, sel2, sel3))

    def test_never_both_on_for_any_input_combination(self):
        for cc_ok, hold, sel2, sel3 in itertools.product((False, True), repeat=4):
            self.assertFalse(all(steps(cc_ok, sel2, sel3, hold)), (cc_ok, hold, sel2, sel3))

    def test_both_selects_resolve_to_the_top_step(self):
        self.assertEqual(steps(True, True, True, True), (False, True))

    def test_gate_logic_unpowered_is_lowest_step(self):
        for sel2, sel3 in itertools.product((False, True), repeat=2):
            self.assertEqual(steps(True, sel2, sel3, True, nor_powered=False, u3_powered=False, u4_powered=False),
                             (False, False))

    def test_unpowered_nor_alone_cannot_enable_step_2(self):
        self.assertFalse(steps(True, True, False, True, nor_powered=False)[0])

    def test_en3_open_or_shorted_low_cannot_make_both_on(self):
        # R3 pulls the net low and the step 3 switch is off: step 2 may be on (single step), never both.
        for kw in ({"en3_open": True}, {"en3_short_low": True}):
            for cc_ok, hold, sel2, sel3 in itertools.product((False, True), repeat=4):
                self.assertFalse(all(steps(cc_ok, sel2, sel3, hold, **kw)))

    def test_en3_short_high_forces_step_2_off(self):
        for cc_ok, hold, sel2, sel3 in itertools.product((False, True), repeat=4):
            en2, en3 = steps(cc_ok, sel2, sel3, hold, en3_short_high=True)
            self.assertFalse(en2)
            self.assertTrue(en3)    # step 3 switch on by the fault: not covered by the gate (the top step alone)

    def test_not_covered_nor_output_stuck_high_can_make_both_on(self):
        # Single fault in U13 (output stuck high) removes the exclusion; only the readbacks show it.
        en2, en3 = steps(True, True, True, True, nor_out_stuck_high=True)
        self.assertTrue(en2 and en3)


if __name__ == "__main__":
    unittest.main()
