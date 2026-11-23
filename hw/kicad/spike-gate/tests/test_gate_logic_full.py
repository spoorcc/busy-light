# SPDX-License-Identifier: Apache-2.0
"""Truth table and single faults of the current-limit gate as built in the full board netlist (RV-017 row 8, ADR-0024).

`tests/test_gate_logic.py` models the older `gate.net` fragment (U13 exclusivity, a shared HOLD_OK/FAULT node did not exist
there). This file reads `tests/data/full.net`: which net feeds each gate input is taken from the netlist, the levels are an
ideal logic model of the supply states. It is not a circuit simulation (no thresholds, no timing); analog margins are in
`sim/gate_rework_levels.py`. None means "floating or undefined: not proven closed".
"""
import re
import unittest
from pathlib import Path

NET = Path(__file__).resolve().parent / "data" / "full.net"


def load(path):
    text = Path(path).read_text()
    text = text[text.index("(nets"):]
    nets = {}
    for blk in re.split(r"\(net\s*\(code", text)[1:]:
        name = re.search(r'\(name "([^"]*)"', blk).group(1).lstrip("/")   # kicad-cli names root-sheet nets "/NAME"
        nets[name] = set(re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', blk))
    return nets


def net_of(nets, ref, pin):
    for n, pins in nets.items():
        if (ref, pin) in pins:
            return n
    return None


def world(**kw):
    """Default state: plugged in, 3V3 up, a 1.5 A source, hold-off over, no fault, both selects high."""
    w = dict(vbus_ic_up=True, v3v3_up=True, adv_1a5=True, hold_done=True, fault=False, sel2=True, sel3=True,
             gpio0=None, gpio6=None, r6_open=False, r8_open=False, u5_missing=False, u7_missing=False)
    w.update(kw)
    return w


def evaluate(nets, w):
    """Levels (1, 0 or None) of the gate nets and of the two step enables for world `w`; the gate wiring is read from nets."""
    ok_in, hold_in = net_of(nets, "U3", "1"), net_of(nets, "U3", "6")
    fault_in, hold_b = net_of(nets, "U10", "1"), net_of(nets, "U10", "2")
    assert (net_of(nets, "U4", "1"), net_of(nets, "U4", "6")) == (ok_in, hold_in)       # both ANDs see the same two nets
    up, v3 = w["vbus_ic_up"], w["v3v3_up"]
    # CC IC output: pulled to VBUS_IC by R1; with VBUS gone both the pull-up and the IC supply are gone (0 V)
    cc_out_n = (0 if w["adv_1a5"] else 1) if up else 0
    lv = {net_of(nets, "U2", "4"): (0 if cc_out_n else 1) if v3 else 0}                 # inverter U2, unpowered output low
    # hold-off node: U5 RESET pulls low during the hold-off and below its VPOR; R6 pulls up to VBUS_IC
    if not up:
        hold = 0                                                                         # R6 and U5 both at about 0 V
    elif w["u5_missing"]:
        hold = None if w["r6_open"] else 1
    elif not w["hold_done"]:
        hold = 0
    else:
        hold = None if w["r6_open"] else 1
    lv[hold_in] = hold
    # FAULT_N: U7 pulls low on a fault; R8 pulls up to 3V3
    if w["u7_missing"] or not w["fault"] or not up:
        fault = 0 if not v3 else (None if w["r8_open"] else 1)
    else:
        fault = 0
    lv[fault_in] = fault
    assert hold_b == hold_in                                                             # U10 sees the same HOLD_OK node
    def and_all(*xs):
        if 0 in xs:
            return 0
        return None if None in xs else 1
    en2 = and_all(lv[ok_in], int(w["sel2"]), lv[hold_in]) if v3 else 0
    en3 = and_all(lv[ok_in], int(w["sel3"]), lv[hold_in]) if v3 else 0
    gate_ok = and_all(lv[fault_in], lv[hold_in]) if v3 else 0
    if w["gpio6"] is not None:                                                           # the MCU output overrides the readback only
        gate_ok = int(w["gpio6"])
    return {"cc_ok": lv[ok_in], "hold_ok": lv[hold_in], "fault_n": lv[fault_in], "en2": en2, "en3": en3, "gate_ok_rb": gate_ok}


class GateStructure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nets = load(NET)

    def test_ands_take_cc_ok_select_and_hold_ok(self):
        n = self.nets
        for g, sel in (("U3", "SEL_STEP2_GPIO"), ("U4", "SEL_STEP3_GPIO")):
            self.assertEqual(net_of(n, g, "1"), "CC_OK_1A5")
            self.assertEqual(net_of(n, g, "6"), "HOLD_OK")
            self.assertEqual(net_of(n, "R4" if g == "U3" else "R5", "1"), net_of(n, g, "3"))
            self.assertEqual(net_of(n, "U9", "16" if g == "U4" else "6"), sel)   # GPIO10 = module pin 16, GPIO3 = pin 6

    def test_no_mcu_pin_on_a_gate_input_net(self):
        n = self.nets
        gate_inputs = {net_of(n, g, p) for g in ("U3", "U4") for p in ("1", "6")}
        mcu_nets = {name for name, pins in n.items() if any(r == "U9" for r, _ in pins)}
        self.assertFalse(gate_inputs & mcu_nets, gate_inputs & mcu_nets)

    def test_fault_and_gate_ok_nets(self):
        n = self.nets
        self.assertEqual(net_of(n, "U7", "4"), "FAULT_N")
        self.assertEqual(net_of(n, "U10", "1"), "FAULT_N")
        self.assertEqual(net_of(n, "U10", "4"), "GATE_OK_RB")
        self.assertEqual(net_of(n, "U9", "20"), "GATE_OK_RB")
        self.assertNotIn("FAULT_N", {net_of(n, g, "6") for g in ("U3", "U4")})
        self.assertEqual(net_of(n, "R6", "1"), "VBUS_IC")
        self.assertEqual(net_of(n, "R8", "1"), "+3V3")

    def test_fault_input_net_has_a_test_pad(self):
        self.assertIn(("TP7", "1"), self.nets["FAULT_N"])


class TruthTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nets = load(NET)

    def ev(self, **kw):
        return evaluate(self.nets, world(**kw))

    def steps(self, r):
        return (r["en2"], r["en3"])

    def test_normal_operation(self):
        r = self.ev()
        self.assertEqual((self.steps(r), r["gate_ok_rb"]), ((1, 1), 1))

    def test_hold_off_closes_both_steps_and_the_readback(self):
        r = self.ev(hold_done=False)
        self.assertEqual((self.steps(r), r["gate_ok_rb"]), ((0, 0), 0))

    def test_limiter_fault_does_not_close_the_gate_but_clears_the_readback(self):
        r = self.ev(fault=True)
        self.assertEqual(self.steps(r), (1, 1))          # ADR-0024: no coupling of a trip at step 3 to step 1 (RV-017 row 5)
        self.assertEqual(r["gate_ok_rb"], 0)             # the firmware sheds (SW-009)

    def test_vbus_gone_with_3v3_up_keeps_the_gate_closed(self):
        r = self.ev(vbus_ic_up=False, hold_done=True)
        self.assertEqual(r["cc_ok"], 1)                  # the inverter reads high: the case SW-009 documents (RISK-049)
        self.assertEqual((self.steps(r), r["gate_ok_rb"]), ((0, 0), 0))   # HOLD_OK follows VBUS_IC through R6

    def test_3v3_absent_keeps_the_gate_closed(self):
        r = self.ev(v3v3_up=False)
        self.assertEqual((self.steps(r), r["gate_ok_rb"]), ((0, 0), 0))

    def test_default_current_source_keeps_the_gate_closed(self):
        r = self.ev(adv_1a5=False)
        self.assertEqual(self.steps(r), (0, 0))

    def test_select_low_closes_its_step_only(self):
        self.assertEqual(self.steps(self.ev(sel2=False)), (0, 1))
        self.assertEqual(self.steps(self.ev(sel3=False)), (1, 0))

    def test_exhaustive_enable_needs_all_conditions(self):
        for up in (True, False):
            for v3 in (True, False):
                for adv in (True, False):
                    for done in (True, False):
                        for s2 in (True, False):
                            r = self.ev(vbus_ic_up=up, v3v3_up=v3, adv_1a5=adv, hold_done=done, sel2=s2)
                            if r["en2"] == 1:
                                self.assertTrue(up and v3 and adv and done and s2, (up, v3, adv, done, s2))


class SingleFaults(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nets = load(NET)

    def ev(self, **kw):
        return evaluate(self.nets, world(**kw))

    def test_gpio6_driven_high_does_not_open_the_gate(self):
        r = self.ev(hold_done=False, gpio6=True)
        self.assertEqual((r["en2"], r["en3"]), (0, 0))   # RV-017 row 1 closed: GPIO6 is not on a gate input net
        self.assertEqual(r["gate_ok_rb"], 1)             # the readback lies; the firmware rule SW-009 (proposal) covers it

    def test_gpio0_driven_high_does_not_open_the_gate(self):
        # GPIO0 sits on CC_OK_RB behind R23; U2 alone drives CC_OK_1A5
        self.assertNotEqual(net_of(self.nets, "U9", "12"), net_of(self.nets, "U3", "1"))
        r = self.ev(adv_1a5=False, gpio0=True)
        self.assertEqual((r["en2"], r["en3"]), (0, 0))

    def test_r6_open_keeps_the_hold_off_but_floats_after_it(self):
        self.assertEqual(self.ev(r6_open=True, hold_done=False)["hold_ok"], 0)   # U5 still pulls low during the hold-off
        r = self.ev(r6_open=True, hold_done=True)
        self.assertIsNone(r["hold_ok"])                                           # after the release the node floats: not covered
        self.assertIsNone(r["en2"])

    def test_u5_missing_is_not_covered(self):
        r = self.ev(u5_missing=True, hold_done=False)
        self.assertEqual((r["en2"], r["en3"]), (1, 1))   # RISK-047: the gate is open during a hold-off that never happens

    def test_u5_missing_with_vbus_gone_still_closes(self):
        self.assertEqual(self.ev(u5_missing=True, vbus_ic_up=False)["en2"], 0)

    def test_r8_open_leaves_the_gate_alone(self):
        r = self.ev(r8_open=True)
        self.assertEqual((r["en2"], r["en3"]), (1, 1))
        self.assertIsNone(r["gate_ok_rb"])               # the readback floats: TC-210 row

    def test_u7_missing_leaves_the_gate_alone(self):
        r = self.ev(u7_missing=True, fault=True)
        self.assertEqual((r["en2"], r["en3"]), (1, 1))


if __name__ == "__main__":
    unittest.main()
