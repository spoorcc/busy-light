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

    def test_input_path_sum_with_the_jumper(self):
        """RV-016 row 14: board-p1 numbers of 2026-11-20 (VBUS 23.9 mV, VBUS_IC 44.1 mV at 1.5 A)."""
        doc = PC.input_path({"VBUS": {"drop_mv": 23.9, "current_a": 1.5}, "VBUS_IC": {"drop_mv": 44.1, "current_a": 1.5}})
        self.assertEqual(doc["copper_drop_mv"], 68.0)
        self.assertEqual(doc["drop_with_r22_10_mohm_mv"], 83.0)
        self.assertEqual(doc["drop_with_r22_20_mohm_mv"], 98.0)
        self.assertIsNone(PC.input_path({"VBUS": {"drop_mv": None, "current_a": 1.5}}))

    def test_case_pads_are_on_the_case_net(self):
        for net, (src, dst, _amps, _basis) in PC.CASES.items():
            for ref, pad in (src, dst):
                if pad is None:      # all pads of the ref that are on this net
                    self.assertTrue(any(r == ref and n.lstrip("/") == net for (r, _p), n in self.pin_net.items()), (net, ref))
                else:
                    self.assertEqual(self.pin_net[(ref, pad)].lstrip("/"), net, (net, ref, pad))


if __name__ == "__main__":
    unittest.main()


@unittest.skipIf(PC is None, "pcb_power_check needs pcbnew, numpy and scipy")
class FullWidthPath(unittest.TestCase):
    """Batch p1b7 (2026-11-19): the clean-up joined U7 pin 6 to the regulator through 0.15 mm track; the drop alone did not
    show it (29 mV at a 0.05 mm grid). The check solves each case again without the tracks narrower than
    WIDTH_SHARE x NET_WIDTH: no path then means the current needs a thin track."""

    def board(self, width):
        import pcbnew
        b = pcbnew.BOARD()
        b.SetCopperLayerCount(4)
        net = pcbnew.NETINFO_ITEM(b, "+5V")
        b.Add(net)
        for ref, x in (("A", 10.0), ("B", 20.0)):
            fp = pcbnew.FOOTPRINT(b)
            fp.SetReference(ref)
            pad = pcbnew.PAD(fp)
            pad.SetNumber("1")
            pad.SetShape(pcbnew.PAD_SHAPE_RECT)
            pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
            pad.SetLayerSet(pcbnew.PAD.SMDMask())
            pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.0), pcbnew.FromMM(1.0)))
            pad.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(10.0)))
            pad.SetNet(net)
            fp.Add(pad)
            b.Add(fp)
        tr = pcbnew.PCB_TRACK(b)
        tr.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(10.0), pcbnew.FromMM(10.0)))
        tr.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(20.0), pcbnew.FromMM(10.0)))
        tr.SetWidth(pcbnew.FromMM(width))
        tr.SetLayer(pcbnew.F_Cu)
        tr.SetNet(net)
        b.Add(tr)
        edge = pcbnew.PCB_SHAPE(b)
        edge.SetShape(pcbnew.SHAPE_T_RECT)
        edge.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(5.0), pcbnew.FromMM(5.0)))
        edge.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(25.0), pcbnew.FromMM(15.0)))
        edge.SetLayer(pcbnew.Edge_Cuts)
        b.Add(edge)
        return b

    def path(self, width):
        b = self.board(width)
        ras = PC.Raster(b)
        layers = [b.GetLayerName(l) for l in b.GetEnabledLayers().CuStack()]
        r = PC.effective_resistance(b, ras, "+5V", ("A", "1"), ("B", "1"), layers, min_width=PC.min_path_width("+5V"))
        return r is not None and r != float("inf")

    def test_net_width_track_is_a_full_width_path(self):
        self.assertTrue(self.path(0.6))

    def test_neck_down_to_the_share_is_kept(self):
        self.assertTrue(self.path(0.45))

    def test_default_width_track_is_not(self):
        self.assertFalse(self.path(0.15))

    def test_min_width_per_case_net(self):
        import pcb_rules
        for net in PC.CASES:
            self.assertAlmostEqual(PC.min_path_width(net), PC.WIDTH_SHARE * pcb_rules.NET_WIDTH[net])
