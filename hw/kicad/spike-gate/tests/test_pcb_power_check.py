# SPDX-License-Identifier: Apache-2.0
"""Plan 08 step 3 (HW-017, RV-014 finding 9): the power check follows the VBUS split at R22.

The cases must name pads that sit on the case's own net in the full-board netlist, otherwise the effective-resistance
solver finds no path and every routing run gets the same "no path" failure in the picker.
"""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

try:
    import pcb_power_check as PC
    import pcb_full
except ImportError as e:     # pcbnew, numpy or scipy missing
    PC = None
    WHY = str(e)

NETLIST = HERE / "data" / "full.net"


@unittest.skipIf(PC is None, "pcb_power_check needs pcbnew, numpy and scipy")
class VbusSplit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.comps, cls.nets = pcb_full.read_netlist(str(NETLIST))
        cls.pin_net = {(r, p): n for n, nodes in cls.nets.items() for r, p in nodes}

    def test_two_input_cases_in_series(self):
        self.assertEqual(PC.CASES["VBUS"][0], ("J1", None))
        self.assertEqual(PC.CASES["VBUS"][1], ("R22", "1"))
        self.assertEqual(PC.CASES["VBUS_IC"][0], ("R22", "2"))
        self.assertEqual(PC.CASES["VBUS_IC"][1], ("U7", "1"))
        self.assertEqual(PC.CASES["VBUS"][2], PC.CASES["VBUS_IC"][2])          # the same current flows through both

    def test_case_pads_are_on_the_case_net(self):
        for net, (src, dst, _amps, _basis) in PC.CASES.items():
            for ref, pad in (src, dst):
                if pad is None:      # all pads of the ref that are on this net
                    self.assertTrue(any(r == ref and n.lstrip("/") == net for (r, _p), n in self.pin_net.items()), (net, ref))
                else:
                    self.assertEqual(self.pin_net[(ref, pad)].lstrip("/"), net, (net, ref, pad))


if __name__ == "__main__":
    unittest.main()
