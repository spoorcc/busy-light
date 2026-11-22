# SPDX-License-Identifier: Apache-2.0
"""Tests for the finishing geometry (pcb_finish.py): silkscreen designators and fiducial spots; the class `OnABoard` needs pcbnew."""
import subprocess
import sys
import tempfile
import math
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import pcb_finish as F  # noqa: E402

try:
    import pcbnew
except ImportError:      # pragma: no cover
    pcbnew = None


class Rects(unittest.TestCase):
    def test_overlap_with_margin(self):
        a = (0.0, 0.0, 2.0, 1.0)                              # x0, y0, x1, y1
        self.assertTrue(F.overlap(a, (1.5, 0.5, 3.0, 2.0), 0.0))
        self.assertFalse(F.overlap(a, (2.1, 0.0, 3.0, 1.0), 0.0))
        self.assertTrue(F.overlap(a, (2.1, 0.0, 3.0, 1.0), 0.2))      # a 0.1 mm gap is inside a 0.2 mm margin

    def test_text_box_grows_with_the_number_of_characters(self):
        w1, h1 = F.text_size("C1", 1.0)
        w2, _ = F.text_size("R_ILIM1", 1.0)
        self.assertGreater(w2, w1)
        self.assertEqual(h1, 1.0)


class Texts(unittest.TestCase):
    def test_text_goes_beside_the_part_and_avoids_obstacles(self):
        part = (0.0, 0.0, 2.0, 1.0)
        pos = F.place_text("C1", part, obstacles=[], inside=lambda r: True, height=1.0)
        self.assertIsNotNone(pos)
        box = F.text_box("C1", pos, 1.0)
        self.assertFalse(F.overlap(box, part, 0.0))
        blocked = [F.text_box("C1", pos, 1.0)]
        pos2 = F.place_text("C1", part, obstacles=blocked, inside=lambda r: True, height=1.0)
        self.assertNotEqual(pos, pos2)

    def test_no_room_gives_none(self):
        self.assertIsNone(F.place_text("C1", (0, 0, 2, 1), obstacles=[], inside=lambda r: False, height=1.0))

    def test_the_nearest_free_candidate_wins(self):
        part = (0.0, 0.0, 2.0, 1.0)
        pos = F.place_text("C1", part, obstacles=[], inside=lambda r: True, height=1.0)
        d = abs(pos[0] - 1.0) + abs(pos[1] - 0.5)
        self.assertLess(d, 3.0)


class Findings(unittest.TestCase):
    def test_map_text_stays_at_the_part_when_free(self):
        """Owner answer 13 (RV-016 row 15): the bottom map text sits at the top part's position when nothing is there."""
        self.assertEqual(F.map_spot("C1", (10.0, 10.0), [], lambda r: True, 1.0), (10.0, 10.0))

    def test_map_text_moves_in_steps_up_to_the_reach(self):
        pad = (9.0, 9.5, 11.0, 10.5)                     # a bottom pad under the part
        pos = F.map_spot("C1", (10.0, 10.0), [pad], lambda r: True, 1.0)
        self.assertIsNotNone(pos)
        self.assertLessEqual(math.hypot(pos[0] - 10.0, pos[1] - 10.0), 2.0 + 1e-9)
        self.assertFalse(F.overlap(F.text_box("C1", pos, 1.0), pad, F.MARGIN))
        self.assertAlmostEqual((pos[0] * 2) % 1.0, 0.0)  # on the 0.5 mm grid around the part
        wall = (0.0, 0.0, 20.0, 20.0)
        self.assertIsNone(F.map_spot("C1", (10.0, 10.0), [wall], lambda r: True, 1.0))

    def test_identification_text_takes_the_first_free_place(self):
        pos = F.first_free_box("busy-light P1 abc1234", 1.0, [(0.0, 0.0, 30.0, 5.0)], lambda r: r[0] >= 0 and r[1] >= 0,
                               (0.0, 0.0, 40.0, 40.0))
        self.assertIsNotNone(pos)
        self.assertFalse(F.overlap(F.text_box("busy-light P1 abc1234", pos, 1.0), (0.0, 0.0, 30.0, 5.0), F.MARGIN))

    def test_box_points_cover_the_inside_of_a_box(self):
        pts = F.box_points((0.0, 0.0, 2.0, 1.0))
        self.assertIn((1.0, 0.5), pts)                     # a slot through the middle would be found
        self.assertIn((0.0, 0.0), pts)
        self.assertIn((2.0, 1.0), pts)

    def test_refs_named_in_silkscreen_findings(self):
        drc = {"violations": [
            {"type": "silk_overlap", "items": [{"description": "Segment of U9 on F.Silkscreen"}, {"description": "Reference field of C4"}]},
            {"type": "silk_edge_clearance", "items": [{"description": "Arc on Edge.Cuts"}, {"description": "Reference field of D3"}]},
            {"type": "clearance", "items": [{"description": "Reference field of R1"}]}]}
        self.assertEqual(F.refs_in_silk_findings(drc), {"C4", "D3"})

    def test_keep_out_rect_blocks_points_near_it(self):
        self.assertTrue(F.in_rects(1.0, 1.0, [(0.0, 0.0, 2.0, 2.0)], 0.0))
        self.assertTrue(F.in_rects(2.5, 1.0, [(0.0, 0.0, 2.0, 2.0)], 1.0))
        self.assertFalse(F.in_rects(5.0, 1.0, [(0.0, 0.0, 2.0, 2.0)], 1.0))


class Fiducials(unittest.TestCase):
    def test_free_spot_keeps_the_clearance_to_every_item_and_the_edge(self):
        items = [(5.0, 5.0, 1.0)]                              # x, y, radius of copper
        spot = F.free_spot(items, inside=lambda x, y: 0 <= x <= 10 and 0 <= y <= 10, clearance=2.0, step=0.5, far_from=[])
        self.assertIsNotNone(spot)
        self.assertGreaterEqual(((spot[0] - 5) ** 2 + (spot[1] - 5) ** 2) ** 0.5, 3.0)

    def test_second_spot_is_far_from_the_first(self):
        s = F.free_spot([], inside=lambda x, y: 0 <= x <= 20 and 0 <= y <= 20, clearance=1.0, step=1.0, far_from=[(1.0, 1.0)], min_far=10.0)
        self.assertGreaterEqual(((s[0] - 1) ** 2 + (s[1] - 1) ** 2) ** 0.5, 10.0)

    def test_none_when_no_space(self):
        self.assertIsNone(F.free_spot([(5, 5, 20.0)], inside=lambda x, y: 0 <= x <= 10 and 0 <= y <= 10, clearance=1.0, step=1.0, far_from=[]))


@unittest.skipIf(pcbnew is None, "pcbnew (KiCad Python) not available")
class OnABoard(unittest.TestCase):
    """2026-11-20, board p1b13: the designators were placed first and the fiducials after them, avoiding copper only; each
    of three passes left one designator (D4, R14, C26) on FID1 (`silk_over_copper`). The fixture puts a part at the top edge
    near the corner: its designator fits only below it, where the first fiducial goes."""

    def finish(self):
        with tempfile.TemporaryDirectory() as t:
            path = Path(t) / "b.kicad_pcb"
            b = pcbnew.BOARD()
            b.SetCopperLayerCount(4)
            edge = pcbnew.PCB_SHAPE(b)
            edge.SetShape(pcbnew.SHAPE_T_RECT)
            edge.SetLayer(pcbnew.Edge_Cuts)
            edge.SetStart(pcbnew.VECTOR2I(0, 0))
            edge.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(20), pcbnew.FromMM(20)))
            edge.SetWidth(pcbnew.FromMM(0.1))
            b.Add(edge)
            fp = pcbnew.FOOTPRINT(b)
            fp.SetReference("T1")
            pad = pcbnew.PAD(fp)
            pad.SetNumber("1")
            pad.SetShape(pcbnew.PAD_SHAPE_RECT)
            pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
            pad.SetLayerSet(pcbnew.PAD.SMDMask())
            pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.0), pcbnew.FromMM(1.0)))
            fp.Add(pad)
            b.Add(fp)
            fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(2.95), pcbnew.FromMM(0.6)))   # at the top edge: text only below, on FID1
            pcbnew.SaveBoard(str(path), b)
            res = subprocess.run([sys.executable, str(Path(F.__file__)), str(path)], capture_output=True, text=True, check=False)
            self.assertEqual(res.returncode, 0, res.stderr[-500:])
            return pcbnew.LoadBoard(str(path))

    def test_no_designator_on_a_fiducial(self):
        b = self.finish()
        fids = [f for f in b.GetFootprints() if f.GetReference().startswith("FID")]
        texts = [f.Reference() for f in b.GetFootprints() if not f.GetReference().startswith("FID") and f.Reference().IsVisible()]
        self.assertTrue(fids)
        self.assertTrue(texts)                                   # T1 got a silkscreen designator
        for t in texts:
            for f in fids:
                if f.IsFlipped() != (t.GetLayer() == pcbnew.B_SilkS):
                    continue
                self.assertFalse(t.GetBoundingBox().Intersects(f.GetBoundingBox()), (t.GetText(), f.GetReference()))


if __name__ == "__main__":
    unittest.main()
