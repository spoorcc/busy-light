# SPDX-License-Identifier: Apache-2.0
"""Fabricator-minimum check (pcb_fabcheck.py): the pure gap arithmetic and the direct checks on a small in-memory board.
Via in pad (plan 08 section 4.3, HW-008, RV-014): the count, and the --no-via-in-pad flag of the command line."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC))
import pcb_fabcheck as F  # noqa: E402

try:
    import pcbnew
    import pcb_full
except ImportError:
    pcbnew = None


class Gaps(unittest.TestCase):
    def test_edge_to_edge_gap_of_two_holes(self):
        # centres 1.0 mm apart, diameters 0.2 and 0.4: gap 1.0 - 0.1 - 0.2 = 0.7
        self.assertAlmostEqual(F.hole_gap((0, 0, 0.2), (1.0, 0, 0.4)), 0.7)

    def test_slot_is_a_capsule_not_a_circle_of_its_long_side(self):
        # a 2.0 mm long, 0.4 mm wide slot along x from x=-1 to x=1 and a 0.4 mm hole 0.8 mm above its middle:
        # centre distance to the slot axis 0.8, minus half widths 0.2 + 0.2 = 0.4
        slot = (-1.0, 0.0, 1.0, 0.0, 0.4)
        hole = (0.0, 0.8, 0.0, 0.8, 0.4)
        self.assertAlmostEqual(F.hole_gap(slot, hole), 0.4)
        # a hole in line with the slot end: 0.5 mm beyond it, so 0.5 - 0.2 - 0.2 = 0.1
        self.assertAlmostEqual(F.hole_gap(slot, (1.5, 0.0, 1.5, 0.0, 0.4)), 0.1)
        self.assertAlmostEqual(F.hole_gap(slot, (0.0, 0.0, 0.0, 0.0, 0.4)), -0.4)     # inside: overlapping

    def test_pairs_below_the_limit_are_found_once(self):
        holes = [(0, 0, 0.2), (0.5, 0, 0.2), (5, 5, 0.2)]
        bad = F.holes_too_close(holes, 0.4)
        self.assertEqual(len(bad), 1)
        self.assertAlmostEqual(bad[0][2], 0.3)

    def test_nothing_close_gives_an_empty_list(self):
        self.assertEqual(F.holes_too_close([(0, 0, 0.2), (3, 0, 0.2)], 0.2), [])

    def test_dru_text_names_the_pad_rule_and_the_value(self):
        t = F.pad_rule_dru(0.15)
        self.assertIn('(rule "fab_pad_to_pad"', t)
        self.assertIn("(min 0.15mm)", t)
        self.assertIn("A.Type == 'Pad' && B.Type == 'Pad'", t)

    def test_verdict_is_fail_when_any_check_fails(self):
        self.assertEqual(F.verdict({"a": {"ok": True}, "b": {"ok": True}}), "PASS")
        self.assertEqual(F.verdict({"a": {"ok": True}, "b": {"ok": False}}), "FAIL")


@unittest.skipIf(pcbnew is None, "pcbnew (KiCad Python) not available")
class Direct(unittest.TestCase):
    def board(self, width=0.1, dia=0.5, drill=0.2):
        b = pcbnew.BOARD()
        net = pcbnew.NETINFO_ITEM(b, "N")
        b.Add(net)
        v = pcbnew.PCB_VIA(b)
        v.SetPosition(pcb_full.vec(10, 10))
        v.SetDrill(pcb_full.mm(drill))
        v.SetWidth(pcb_full.mm(dia))
        v.SetNet(net)
        b.Add(v)
        t = pcbnew.PCB_TRACK(b)
        t.SetStart(pcb_full.vec(0, 0))
        t.SetEnd(pcb_full.vec(5, 0))
        t.SetLayer(pcbnew.F_Cu)
        t.SetWidth(pcb_full.mm(width))
        t.SetNet(net)
        b.Add(t)
        return b

    def test_fine_rules_pass_and_report_the_ring_below_the_recommendation(self):
        r = F.direct_checks(self.board())
        self.assertTrue(all(c["ok"] for c in r["checks"].values()), r)
        self.assertAlmostEqual(r["min_annular_mm"], 0.15, places=3)
        self.assertEqual(r["vias_below_recommended_ring"], 1)

    def test_a_thin_track_and_a_small_via_fail(self):
        r = F.direct_checks(self.board(width=0.08, dia=0.3, drill=0.2))
        self.assertFalse(r["checks"]["track_width"]["ok"])
        self.assertFalse(r["checks"]["annular_ring"]["ok"])


def pad_board(via_xy, pad_net="GND", via_net="GND", size=(1.0, 1.0), angle=0.0, via_dia=0.6):
    """One SMD pad (F.Cu) centred at (20, 20) mm and one through via (drill 0.3 mm) at via_xy, both in mm."""
    b = pcbnew.BOARD()
    b.SetCopperLayerCount(4)
    nets = {}
    for name in {pad_net, via_net}:
        nets[name] = pcbnew.NETINFO_ITEM(b, name)
        b.Add(nets[name])
    fp = pcbnew.FOOTPRINT(b)
    fp.SetReference("U9")
    fp.SetPosition(pcb_full.vec(20.0, 20.0))
    pad = pcbnew.PAD(fp)
    pad.SetNumber("49")
    pad.SetShape(pcbnew.PAD_SHAPE_RECT)
    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    pad.SetLayerSet(pcbnew.PAD.SMDMask())
    pad.SetSize(pcbnew.VECTOR2I(pcb_full.mm(size[0]), pcb_full.mm(size[1])))
    pad.SetPosition(pcb_full.vec(20.0, 20.0))
    pad.SetOrientation(pcbnew.EDA_ANGLE(angle, pcbnew.DEGREES_T))
    pad.SetNet(nets[pad_net])
    fp.Add(pad)
    b.Add(fp)
    v = pcbnew.PCB_VIA(b)
    v.SetPosition(pcb_full.vec(*via_xy))
    v.SetDrill(pcb_full.mm(0.3))
    v.SetWidth(pcb_full.mm(via_dia))
    v.SetNet(nets[via_net])
    b.Add(v)
    return b


@unittest.skipIf(pcbnew is None, "pcbnew (KiCad Python) not available")
class ViaInSmdPad(unittest.TestCase):
    """The 1.0 x 1.0 mm pad spans 19.5 to 20.5 mm; grown by 0.05 mm it reaches 20.55. A 0.6 mm via reaches 0.3 mm."""

    def count(self, *a, **k):
        return len(F.vias_in_smd_pads(pad_board(*a, **k)))

    def test_via_in_the_pad_is_counted_whatever_the_net(self):
        self.assertEqual(self.count((20.0, 20.0)), 1)                              # same net: the old U9 shortcut
        self.assertEqual(self.count((20.0, 20.0), via_net="+5V"), 1)               # another net
        hit = F.vias_in_smd_pads(pad_board((20.6, 20.0)))[0]                       # partly over the pad edge
        self.assertEqual((hit["pad"], hit["pad_net"], hit["net"], hit["layer"]), ("U9.49", "GND", "GND", "F.Cu"))

    def test_the_grow_margin_counts(self):
        self.assertEqual(self.count((20.83, 20.0)), 1)      # edge gap 0.03 mm: inside the 0.05 mm grow
        self.assertEqual(self.count((20.87, 20.0)), 0)      # edge gap 0.07 mm: clear

    def test_via_beside_the_pad_is_not_counted(self):
        self.assertEqual(self.count((21.2, 20.0)), 0)
        self.assertEqual(self.count((20.0, 18.0)), 0)

    def test_exact_copper_not_the_bounding_box(self):
        # a 0.6 mm square pad turned 45 degrees is a diamond; its bounding box reaches 0.424 mm from the centre. A via at
        # (+0.55, +0.55) mm from the centre is inside the grown box (so a via producer would not place it) but 0.478 mm
        # from the diamond's edge, more than 0.3 + 0.05: the copper does not touch, so the count is 0.
        import pcb_rules
        import pcb_stitch
        b = pad_board((20.55, 20.55), size=(0.6, 0.6), angle=45.0)
        self.assertEqual(F.vias_in_smd_pads(b), [])
        self.assertTrue(pcb_rules.via_hits_smd_pad(20.55, 20.55, 0.6, pcb_stitch.pad_boxes(b)))
        self.assertEqual(self.count((20.3, 20.3), size=(0.6, 0.6), angle=45.0), 1)

    def test_count_is_reported_and_is_a_check_only_with_the_flag(self):
        b = pad_board((20.0, 20.0))
        r = F.direct_checks(b)
        self.assertEqual(r["via_in_smd_pad"], 1)
        self.assertNotIn("via_in_smd_pad", r["checks"])
        self.assertEqual(F.verdict(r["checks"]), "PASS")                           # report only
        r = F.direct_checks(b, no_via_in_pad=True)
        self.assertEqual(r["checks"]["via_in_smd_pad"]["count"], 1)
        self.assertEqual(F.verdict(r["checks"]), "FAIL")
        r = F.direct_checks(pad_board((21.2, 20.0)), no_via_in_pad=True)
        self.assertEqual((r["via_in_smd_pad"], F.verdict(r["checks"])), (0, "PASS"))


@unittest.skipIf(pcbnew is None or shutil.which("kicad-cli") is None, "pcbnew or kicad-cli not available")
class NoViaInPadFlag(unittest.TestCase):
    """The command line: --no-via-in-pad makes a via in a pad exit 1; without it the count is reported only."""

    def run_cli(self, via_xy, *flags):
        with tempfile.TemporaryDirectory() as t:
            path = Path(t) / "b.kicad_pcb"
            pcbnew.SaveBoard(str(path), pad_board(via_xy))
            res = subprocess.run([sys.executable, str(SRC / "pcb_fabcheck.py"), *flags, str(path)],
                                 capture_output=True, text=True, check=False)
        return res.returncode, json.loads(res.stdout)

    def test_via_in_the_pad_fails_with_the_flag(self):
        rc, out = self.run_cli((20.0, 20.0), "--no-via-in-pad")
        self.assertEqual((rc, out["verdict"], out["via_in_smd_pad"]), (1, "FAIL", 1), out)
        self.assertFalse(out["checks"]["via_in_smd_pad"]["ok"])

    def test_via_beside_the_pad_passes_with_the_flag(self):
        rc, out = self.run_cli((21.2, 20.0), "--no-via-in-pad")
        self.assertEqual((rc, out["verdict"], out["via_in_smd_pad"]), (0, "PASS", 0), out)

    def test_without_the_flag_the_count_is_reported_only(self):
        rc, out = self.run_cli((20.0, 20.0))
        self.assertEqual((rc, out["verdict"], out["via_in_smd_pad"]), (0, "PASS", 1), out)
        self.assertNotIn("via_in_smd_pad", out["checks"])


if __name__ == "__main__":
    unittest.main()
