# SPDX-License-Identifier: Apache-2.0
"""Post-route clean-up (src/pcb_fix.py): parsing, track runs, and one routed connection on a small board. Needs pcbnew;
skipped visibly without it.
Run: cd hw/kicad/spike-gate && PYTHONPATH=src:tests python3 -m unittest test_pcb_fix
"""
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

try:
    import pcbnew
    import pcb_fix
    import pcb_full
    import pcb_rules
except ImportError:
    pcbnew = None


@unittest.skipIf(pcbnew is None, "pcbnew (KiCad Python) not available")
class Parsing(unittest.TestCase):
    def test_pad_track_via_descriptions(self):
        self.assertEqual(pcb_fix.parse_item("Pad 2 [GND] of C15 on B.Cu"), ("pad", "C15", "2", "GND", "B.Cu"))
        self.assertEqual(pcb_fix.parse_item("PTH pad A6 [Net-(J1-D+-PadA6)] of J1"), ("pad", "J1", "A6", "Net-(J1-D+-PadA6)", None))
        self.assertEqual(pcb_fix.parse_item("Track [/BUTTON] on F.Cu, length 0,4778 mm"), ("track", "/BUTTON", "F.Cu"))
        self.assertEqual(pcb_fix.parse_item("Via [GND] on F.Cu - B.Cu"), ("via", "GND"))
        self.assertIsNone(pcb_fix.parse_item("Zone [GND] on In1.Cu, priority 2"))

    def test_seg_points_include_both_ends(self):
        pts = pcb_fix.seg_points(0, 0, 1, 0, 0.25)
        self.assertEqual(pts[0], (0, 0))
        self.assertEqual(pts[-1], (1, 0))
        self.assertEqual(len(pts), 5)

    def test_run_of_stops_at_junctions_and_stoppers(self):
        a, b, c, d, e = (0, 0), (1, 0), (2, 0), (3, 0), (2, 1)
        s1, s2, s3, s4 = object(), object(), object(), object()
        same = [(s1, a, b), (s2, b, c), (s3, c, d), (s4, c, e)]          # a T at c
        got = pcb_fix.run_of(s1, same, set())
        self.assertEqual({id(x) for x in got}, {id(s1), id(s2)})         # the run stops at the junction c
        got = pcb_fix.run_of(s1, [(s1, a, b), (s2, b, c)], {b})          # a via or pad at b stops the run
        self.assertEqual({id(x) for x in got}, {id(s1)})

    def test_count_reads_violations_and_unconnected(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "d.json"
            p.write_text(json.dumps({"violations": [{"type": "clearance"}, {"type": "silk_overlap"}, {"type": "clearance"}],
                                     "unconnected_items": [{}, {}, {}]}))
            self.assertEqual(pcb_fix.count(str(p), ("clearance",)), 2)
            self.assertEqual(pcb_fix.count(str(p), ("unconnected_items",)), 3)
            self.assertEqual(pcb_fix.count(str(p), ("clearance", "unconnected_items")), 5)


def small_board():
    """Three pads in a row, two of net A (left and right) and a pad of net B between them, 1.0 mm wide: the route
    from the left pad to the right pad has to go round the pad of B."""
    b = pcbnew.BOARD()
    nets = {}
    for name in ("A", "B"):
        n = pcbnew.NETINFO_ITEM(b, name)
        b.Add(n)
        nets[name] = n
    cx, cy = pcb_full.CX, pcb_full.CY
    for ref, net, x, y in (("L", "A", cx - 4.0, cy), ("R", "A", cx + 4.0, cy), ("M", "B", cx, cy)):
        f = pcbnew.FOOTPRINT(b)
        f.SetReference(ref)
        f.SetPosition(pcb_full.vec(x, y))
        p = pcbnew.PAD(f)
        p.SetNumber("1")
        p.SetShape(pcbnew.PAD_SHAPE_RECT)
        p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        ls = pcbnew.LSET()
        ls.AddLayer(pcbnew.F_Cu)
        p.SetLayerSet(ls)
        p.SetSize(pcbnew.VECTOR2I(pcb_full.mm(1.0), pcb_full.mm(1.0) * (6 if ref == "M" else 1)))
        p.SetPosition(pcb_full.vec(x, y))
        p.SetNet(nets[net])
        f.Add(p)
        b.Add(f)
    edge = pcbnew.PCB_SHAPE(b)
    edge.SetShape(pcbnew.SHAPE_T_CIRCLE)
    edge.SetStart(pcb_full.vec(cx, cy))
    edge.SetEnd(pcb_full.vec(cx + 20.0, cy))
    edge.SetLayer(pcbnew.Edge_Cuts)
    b.Add(edge)
    return b


@unittest.skipIf(pcbnew is None, "pcbnew (KiCad Python) not available")
class RouteOneConnection(unittest.TestCase):
    def test_path_goes_round_a_foreign_pad_and_keeps_the_clearance(self):
        b = small_board()
        fx = pcb_fix.Fixer(b, 30.0)
        cx, cy = pcb_full.CX, pcb_full.CY
        w = pcb_rules.TRACK
        path = fx.route("A", (cx - 4.0, cy), "F.Cu", (cx + 4.0, cy), "F.Cu", w)
        self.assertIsNotNone(path)
        fx.commit("A", path, (cx - 4.0, cy), (cx + 4.0, cy), w)
        tracks = [a for a in fx.added if a[0] == "track"]
        self.assertTrue(tracks)
        # the pad of B spans y from cy-3 to cy+3 on F.Cu and x cx+-0.5: no track point may be closer than clearance + w/2
        for t in tracks:
            _, net, layer, a, e = t
            for px, py in pcb_fix.seg_points(a[0], a[1], e[0], e[1], 0.05):
                if layer == "F.Cu":
                    dx = max(abs(px - cx) - 0.5, 0.0)
                    dy = max(abs(py - cy) - 3.0, 0.0)
                    self.assertGreaterEqual(math.hypot(dx, dy), pcb_rules.CLEARANCE + w / 2 - 1e-6)
        self.assertTrue(any(a[0] == "via" for a in fx.added) or any(t[2] != "F.Cu" for t in tracks) or
                        any(abs(t[3][1] - cy) > 3.0 or abs(t[4][1] - cy) > 3.0 for t in tracks))

    def test_no_path_when_the_target_is_walled_in(self):
        b = small_board()
        fx = pcb_fix.Fixer(b, 30.0)
        cx, cy = pcb_full.CX, pcb_full.CY
        fx.hard["F.Cu"][:, :] = True                       # block every layer completely
        for L in pcb_fix.LAYERS:
            fx.hard[L][:, :] = True
        self.assertIsNone(fx.route("A", (cx - 4.0, cy), "F.Cu", (cx + 4.0, cy), "F.Cu", pcb_rules.TRACK))


if __name__ == "__main__":
    unittest.main()


@unittest.skipIf(pcbnew is None, "pcbnew (KiCad Python) not available")
class SnapToVias(unittest.TestCase):
    """Regression (ring12 run 8): two +5V track ends 0.009 and 0.05 mm beside a via made the gate fail with
    track_not_centered_on_via; snap_to_vias existed but nothing called it."""

    def board(self):
        b = pcbnew.BOARD()
        net = pcbnew.NETINFO_ITEM(b, "N")
        b.Add(net)
        via = pcbnew.PCB_VIA(b)
        via.SetPosition(pcb_full.vec(59.25, 34.148913))
        via.SetNet(net)
        b.Add(via)
        for (x0, y0, x1, y1) in ((59.2431, 34.1547, 59.2, 34.148913), (59.2, 34.148913, 58.7, 34.148913)):
            t = pcbnew.PCB_TRACK(b)
            t.SetStart(pcb_full.vec(x0, y0))
            t.SetEnd(pcb_full.vec(x1, y1))
            t.SetLayer(pcbnew.B_Cu)
            t.SetWidth(pcb_full.mm(0.1))
            t.SetNet(net)
            b.Add(t)
        return b

    def tracks(self, b):
        tr = b.Tracks()
        return [tr[i] for i in range(tr.size()) if tr[i].GetClass() == "PCB_TRACK"]

    def test_ends_next_to_a_via_move_onto_its_centre_and_a_zero_length_stub_goes(self):
        b = self.board()
        pcb_fix.snap_to_vias(b)
        left = self.tracks(b)
        self.assertEqual(len(left), 1)                            # the 0.04 mm stub became zero length and was removed
        t = left[0]
        self.assertAlmostEqual(pcbnew.ToMM(t.GetStart().x), 59.25, places=3)
        self.assertAlmostEqual(pcbnew.ToMM(t.GetStart().y), 34.148913, places=3)
        self.assertAlmostEqual(pcbnew.ToMM(t.GetEnd().x), 58.7, places=3)

    def test_a_track_end_of_another_net_is_left_alone(self):
        b = self.board()
        other = pcbnew.NETINFO_ITEM(b, "M")
        b.Add(other)
        for t in self.tracks(b):
            t.SetNet(other)
        pcb_fix.snap_to_vias(b)
        self.assertEqual(len(self.tracks(b)), 2)

    def test_only_ends_near_the_given_points_move(self):
        b = self.board()
        pcb_fix.snap_to_vias(b, near=[(10.0, 10.0)])                  # a finding elsewhere: nothing here may move
        self.assertEqual(len(self.tracks(b)), 2)
        pcb_fix.snap_to_vias(b, near=[(59.22, 34.15)])
        self.assertEqual(len(self.tracks(b)), 1)


def stacked_board():
    """Two 1.0 mm pads of net A at the board centre, one on F.Cu and one on B.Cu: the route from one to the other needs a
    via, and before plan 08 the router put it at the pad centre (in both pads)."""
    b = pcbnew.BOARD()
    b.SetCopperLayerCount(4)
    net = pcbnew.NETINFO_ITEM(b, "A")
    b.Add(net)
    cx, cy = pcb_full.CX, pcb_full.CY
    for ref, layer in (("T", pcbnew.F_Cu), ("U", pcbnew.B_Cu)):
        f = pcbnew.FOOTPRINT(b)
        f.SetReference(ref)
        f.SetPosition(pcb_full.vec(cx, cy))
        p = pcbnew.PAD(f)
        p.SetNumber("1")
        p.SetShape(pcbnew.PAD_SHAPE_RECT)
        p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        ls = pcbnew.LSET()
        ls.AddLayer(layer)
        p.SetLayerSet(ls)
        p.SetSize(pcbnew.VECTOR2I(pcb_full.mm(1.0), pcb_full.mm(1.0)))
        p.SetPosition(pcb_full.vec(cx, cy))
        p.SetNet(net)
        f.Add(p)
        b.Add(f)
    edge = pcbnew.PCB_SHAPE(b)
    edge.SetShape(pcbnew.SHAPE_T_CIRCLE)
    edge.SetStart(pcb_full.vec(cx, cy))
    edge.SetEnd(pcb_full.vec(cx + 20.0, cy))
    edge.SetLayer(pcbnew.Edge_Cuts)
    b.Add(edge)
    return b


@unittest.skipIf(pcbnew is None, "pcbnew (KiCad Python) not available")
class NoViaInPad(unittest.TestCase):
    """Plan 08 section 4.3 (HW-008, RV-014): the grid router (and so pcb_ring.py) places no via on an SMD pad of any net."""

    def vias(self, fx):
        return [a[2] for a in fx.added if a[0] == "via"]

    def test_mask_is_the_helper_at_every_cell_near_the_pads(self):
        fx = pcb_fix.Fixer(small_board(), 30.0)
        cx, cy = pcb_full.CX, pcb_full.CY
        ix0, iy0 = fx.cell(cx - 6.0, cy - 5.0)
        ix1, iy1 = fx.cell(cx + 6.0, cy + 5.0)
        bad = [(ix, iy) for iy in range(iy0, iy1 + 1) for ix in range(ix0, ix1 + 1)
               if fx.via_in_pad[iy, ix] != pcb_rules.via_hits_smd_pad(*fx.xy(ix, iy), pcb_rules.VIA_DIA, fx.pad_boxes)]
        self.assertEqual(bad, [])
        for x in (cx - 4.0, cx, cx + 4.0):                     # the pads of net A and of net B alike
            ix, iy = fx.cell(x, cy)
            self.assertTrue(fx.via_in_pad[iy, ix], x)

    def test_layer_change_between_stacked_pads_puts_the_via_beside_them(self):
        import pcb_fabcheck
        b = stacked_board()
        fx = pcb_fix.Fixer(b, 30.0)
        cx, cy = pcb_full.CX, pcb_full.CY
        path = fx.route("A", (cx, cy), "F.Cu", (cx, cy), "B.Cu", pcb_rules.TRACK)
        self.assertIsNotNone(path)
        fx.commit("A", path, (cx, cy), (cx, cy), pcb_rules.TRACK)
        vias = self.vias(fx)
        self.assertTrue(vias)
        for x, y in vias:
            self.assertFalse(pcb_rules.via_hits_smd_pad(x, y, pcb_rules.VIA_DIA, fx.pad_boxes), (x, y))
        self.assertEqual(pcb_fabcheck.vias_in_smd_pads(b), [])

    def test_a_via_on_the_start_cell_is_judged_at_the_start_point(self):
        # commit puts a via of the start cell at the start point itself, not at the cell centre: a start point 0.02 mm
        # inside the reach of a pad whose cell centre is 0.01 mm outside it may not take a via there
        fx = pcb_fix.Fixer(stacked_board(), 30.0)
        c = fx.xy(*fx.cell(pcb_full.CX + 5.0, pcb_full.CY))
        x1 = c[0] - pcb_rules.VIA_DIA / 2 - pcb_rules.VIA_IN_PAD_GROW - 0.01
        fx.pad_boxes.append((x1 - 1.0, c[1] - 0.5, x1, c[1] + 0.5, True))
        fx.via_in_pad = fx.via_in_pad_mask()
        p0 = (c[0] - 0.02, c[1])
        self.assertEqual(fx.cell(*p0), fx.cell(*c))
        self.assertTrue(pcb_rules.via_hits_smd_pad(*p0, pcb_rules.VIA_DIA, fx.pad_boxes))
        self.assertFalse(pcb_rules.via_hits_smd_pad(*c, pcb_rules.VIA_DIA, fx.pad_boxes))
        path = fx.route("A", p0, "F.Cu", p0, "B.Cu", pcb_rules.TRACK)
        self.assertIsNotNone(path)
        fx.commit("A", path, p0, p0, pcb_rules.TRACK)
        vias = self.vias(fx)
        self.assertTrue(vias)
        for x, y in vias:
            self.assertFalse(pcb_rules.via_hits_smd_pad(x, y, pcb_rules.VIA_DIA, fx.pad_boxes), (x, y))

    def test_commit_refuses_a_via_in_a_pad(self):
        fx = pcb_fix.Fixer(stacked_board(), 30.0)
        ix, iy = fx.cell(pcb_full.CX, pcb_full.CY)
        with self.assertRaises(ValueError):
            fx.commit("A", [(ix, iy, 0), (ix, iy, 3)], (pcb_full.CX, pcb_full.CY), (pcb_full.CX, pcb_full.CY),
                      pcb_rules.TRACK)


@unittest.skipIf(pcbnew is None, "pcbnew (KiCad Python) not available")
class CleanupWidths(unittest.TestCase):
    """Batch p1b7 (2026-11-19): the clean-up re-routed ripped-up +5V pieces at the 0.15 mm default width, and the TPS2553
    output current (analyst assumption 1.0 A) to the regulator ran through 51 mm of 0.15 mm track (Freerouting lays +5V at
    0.6 mm). A supply net keeps its current-based width (NET_WIDTH) in the clean-up too."""

    def test_supply_nets_keep_their_current_width(self):
        self.assertEqual(pcb_fix.width_for("+5V", None), pcb_rules.NET_WIDTH["+5V"])
        self.assertEqual(pcb_fix.width_for("+3V3", None), pcb_rules.NET_WIDTH["+3V3"])

    def test_pieces_at_led_ring_pads_take_the_ring_stub_width(self):
        """The ring cells feed each LED and its capacitor from the In2 plane through 0.25 mm stubs (pcb_ring.STUB, about
        20 mA per LED); a clean-up pair at such a pad keeps that width, the other +5V pairs take NET_WIDTH."""
        import pcb_ring
        led, cap = pcb_ring.cells()[0]
        self.assertEqual(pcb_fix.width_for("+5V", {led}), pcb_ring.STUB)
        self.assertEqual(pcb_fix.width_for("+5V", {cap}), pcb_ring.STUB)
        self.assertEqual(pcb_fix.width_for("+5V", {"U7"}), pcb_rules.NET_WIDTH["+5V"])
        self.assertEqual(pcb_fix.width_for("+5V", {led, "U8"}), pcb_rules.NET_WIDTH["+5V"])

    def test_pair_refs_from_the_drc_items(self):
        v = {"items": [{"description": "Pad 4 [+5V] of D6 on F.Cu"}, {"description": "Track [+5V] on F.Cu, length 0.6364 mm"}]}
        self.assertEqual(pcb_fix.pair_refs(v), {"D6"})

    def test_branches_of_the_split_main_path_and_signals(self):
        for net in pcb_rules.MAIN_PATH_NETS:          # main path locked in stage 1; the clean-up joins branches
            self.assertEqual(pcb_fix.width_for(net, None), pcb_rules.BRANCH_WIDTH)
        self.assertEqual(pcb_fix.width_for("/CC1", None), pcb_rules.NET_TRACK["/CC1"])
        self.assertEqual(pcb_fix.width_for("/LED_DATA", None), pcb_rules.TRACK)
