# SPDX-License-Identifier: Apache-2.0
"""Plan 06 G3: M1 count (T10) and stitcher exit code (T9). Plan 08 section 4.3 (HW-008, RV-014): the stitcher places no
via in an SMD pad of any net, the U9 module ground pads included. Needs pcbnew; skipped visibly without it.
Run: cd hw/kicad/spike-gate && PYTHONPATH=src:tests python3 -m unittest test_pcb_check_stitch
"""
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "src"
sys.path.insert(0, str(SRC))

try:
    import pcbnew
    import pcb_check
    import pcb_fabcheck
    import pcb_full
    import pcb_rules
    import pcb_stitch
except ImportError:
    pcbnew = None

DATA = HERE / "data"


def entry(*descs):
    return {"description": "Missing connection between items", "severity": "error", "type": "unconnected_items",
            "items": [{"description": d} for d in descs]}


@unittest.skipIf(pcbnew is None, "pcbnew (KiCad Python) not available")
class CountUnrouted(unittest.TestCase):
    def test_fixtures_match_expected(self):
        exp = json.loads((DATA / "drc_expected.json").read_text())
        for key, name in (("placed", "drc_placed"), ("routed", "drc_routed"), ("stitched", "drc_stitched")):
            path = str(DATA / (name + ".json"))
            raw = len(json.loads(Path(path).read_text())["unconnected_items"])
            self.assertEqual(raw, exp[key]["raw_unconnected_items"], key)
            self.assertEqual(pcb_check.count_unrouted(path, pcb_rules.PLANE_NETS), exp[key]["m1"], key)

    def run_count(self, entries, planes=pcb_rules.PLANE_NETS):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "d.json"
            p.write_text(json.dumps({"unconnected_items": entries}))
            return pcb_check.count_unrouted(str(p), planes)

    def test_plane_net_is_not_counted_other_nets_are(self):
        self.assertEqual(self.run_count([entry("Track [GND] on F.Cu, length 1 mm", "Pad 1 [GND] of U1 on F.Cu")]), 0)
        self.assertEqual(self.run_count([entry("Pad 1 [/CC1] of U1 on F.Cu", "Pad 2 [/CC1] of J1 on F.Cu")]), 1)

    def test_entry_without_net_name_counts(self):
        self.assertEqual(self.run_count([entry("Zone on F.Cu")]), 1)

    def test_first_net_name_decides(self):
        self.assertEqual(self.run_count([entry("Via [+5V] on F.Cu - B.Cu", "Pad 1 [/CC1] of U1 on F.Cu")]), 0)


def fixture_board(path, pads, ref="T1", size=1.0):
    b = pcbnew.BOARD()
    b.SetCopperLayerCount(4)
    net = pcbnew.NETINFO_ITEM(b, "GND")
    b.Add(net)
    fp = pcbnew.FOOTPRINT(b)
    fp.SetReference(ref)
    for i, (x, y) in enumerate(pads):
        pad = pcbnew.PAD(fp)
        pad.SetNumber(str(i + 1))
        pad.SetShape(pcbnew.PAD_SHAPE_RECT)
        pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        pad.SetLayerSet(pcbnew.PAD.SMDMask())
        pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(size), pcbnew.FromMM(size)))
        pad.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
        pad.SetNet(net)
        fp.Add(pad)
    b.Add(fp)
    pcbnew.SaveBoard(str(path), b)


def run_stitch_cli(pads, ref="T1", size=1.0, keep=None):
    """Run pcb_stitch.py on a fixture board whose pads are all unconnected GND pads. Returns (exit code, report); with
    `keep` (a function of the stitched board) also its result."""
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        src = t / "busy_light_spike.kicad_pcb"
        fixture_board(src, pads, ref, size)
        (t / "busy_light_spike.placement.json").write_text(json.dumps({"tab_r": 30.0}))
        drc = t / "drc.json"
        drc.write_text(json.dumps({"unconnected_items": [
            entry("Pad %d [GND] of %s on F.Cu" % (i + 1, ref), "Track [GND] on F.Cu, length 1 mm") for i in range(len(pads))]}))
        res = subprocess.run([sys.executable, str(SRC / "pcb_stitch.py"), str(src), str(drc), str(t / "out.kicad_pcb")],
                             capture_output=True, text=True, check=False)
        out = json.loads([ln for ln in res.stdout.splitlines() if ln.startswith("{")][-1])
        extra = keep(pcbnew.LoadBoard(str(t / "out.kicad_pcb"))) if keep else None
        return res.returncode, out, extra


def board_vias(board):
    """(x, y, diameter) in mm of every via of the board."""
    tr = board.Tracks()
    out = []
    for i in range(tr.size()):
        if tr[i].GetClass() == "PCB_VIA":
            v = pcbnew.Cast_to_PCB_VIA(tr[i])
            out.append((pcbnew.ToMM(v.GetPosition().x), pcbnew.ToMM(v.GetPosition().y), pcbnew.ToMM(v.GetWidth(pcbnew.F_Cu))))
    return out


@unittest.skipIf(pcbnew is None, "pcbnew (KiCad Python) not available")
class StitcherExit(unittest.TestCase):
    def run_cli(self, pads):
        rc, out, _ = run_stitch_cli(pads)
        return rc, out

    def test_pad_that_can_be_stitched_exits_zero(self):
        rc, rep = self.run_cli([(pcb_full.CX, pcb_full.CY)])
        self.assertEqual((rc, rep["failed"]), (0, []), rep)
        self.assertEqual(rep["vias_added"], 1)

    def test_failed_pad_exits_non_zero(self):
        rc, rep = self.run_cli([(pcb_full.CX, pcb_full.CY), (pcb_full.CX + 200.0, pcb_full.CY)])
        self.assertEqual(rc, 1)
        self.assertEqual(len(rep["failed"]), 1)


@unittest.skipIf(pcbnew is None, "pcbnew (KiCad Python) not available")
class StitcherNoViaInPad(unittest.TestCase):
    """Before plan 08 the U9 ground pads got a via at the pad centre, and a 1 mm pad got its via 0.8 mm from the centre
    (the via edge 0.2 mm inside the pad copper): the same-net pad was never an obstacle."""

    def stitcher(self, t, pads, ref="T1", size=1.0):
        src = Path(t) / "b.kicad_pcb"
        fixture_board(src, pads, ref, size)
        st = pcb_stitch.Stitcher(pcbnew.LoadBoard(str(src)), str(src))
        st.tab_r = 30.0
        return st

    def test_via_ok_rejects_the_pad_of_the_same_net_and_accepts_a_point_beside_it(self):
        cx, cy = pcb_full.CX, pcb_full.CY
        with tempfile.TemporaryDirectory() as t:
            st = self.stitcher(t, [(cx, cy)], "U9", 1.45)
            self.assertFalse(st.via_ok(cx, cy, "GND"))               # the old U9 shortcut: the pad centre
            self.assertFalse(st.via_ok(cx + 1.0, cy, "GND"))         # via edge 0.025 mm inside the grown pad
            self.assertTrue(st.via_ok(cx + 1.2, cy, "GND"))          # 1.2 - 0.725 - 0.05 = 0.425 > 0.3
            self.assertTrue(st.free(cx, cy, pcb_stitch.VIA_D / 2, "GND"))   # only the new check rejects the centre
            with self.assertRaises(ValueError):
                st.put_via("U9", "1", "GND", cx, cy)

    def check_clear(self, board):
        boxes = pcb_stitch.pad_boxes(board)
        vias = board_vias(board)
        hits = [v for v in vias if pcb_rules.via_hits_smd_pad(v[0], v[1], v[2], boxes)]
        return vias, hits, pcb_fabcheck.vias_in_smd_pads(board)

    def test_u9_ground_pad_gets_its_via_beside_the_pad(self):
        cx, cy = pcb_full.CX, pcb_full.CY
        rc, rep, (vias, hits, exact) = run_stitch_cli([(cx, cy)], "U9", 1.45, keep=self.check_clear)
        self.assertEqual((rc, rep["failed"], rep["vias_added"]), (0, [], 1), rep)
        self.assertEqual((hits, exact), ([], []))
        self.assertGreaterEqual(math.hypot(vias[0][0] - cx, vias[0][1] - cy), 0.725 + 0.05 + 0.3)

    def test_small_pad_via_clears_its_own_pad(self):
        cx, cy = pcb_full.CX, pcb_full.CY
        rc, rep, (vias, hits, exact) = run_stitch_cli([(cx, cy)], keep=self.check_clear)
        self.assertEqual((rc, rep["failed"], rep["vias_added"]), (0, [], 1), rep)
        self.assertEqual((hits, exact), ([], []))

    def test_same_net_neighbour_pad_is_an_obstacle_for_the_via(self):
        # the second pad sits where the first free via spot to the right of pad 1 was (x + 1.0): the via goes elsewhere
        cx, cy = pcb_full.CX, pcb_full.CY
        rc, rep, (vias, hits, exact) = run_stitch_cli([(cx, cy), (cx + 1.6, cy)], keep=self.check_clear)
        self.assertEqual((rc, rep["failed"]), (0, []), rep)
        self.assertTrue(vias)
        self.assertEqual((hits, exact), ([], []))


if __name__ == "__main__":
    unittest.main()


@unittest.skipIf(pcbnew is None, "pcbnew (KiCad Python) not available")
class StitcherDogleg(unittest.TestCase):
    """P1 batch of 2026-11-18: on the one-sided board the router boxed plane pads in, so every straight track from the pad
    to a via spot was blocked (U11 pad 5 among them). The stitcher now tries one corner before it gives up."""

    def stitcher(self, t):
        src = Path(t) / "b.kicad_pcb"
        fixture_board(src, [(pcb_full.CX, pcb_full.CY)])
        st = pcb_stitch.Stitcher(pcbnew.LoadBoard(str(src)), str(src))
        st.tab_r = 30.0
        return st

    def boxed_in(self, st, first_leg_free=True):
        """Every straight track from the pad centre longer than 0.6 mm is blocked; tracks that start elsewhere are free."""
        cx, cy = pcb_full.CX, pcb_full.CY

        def track_free(p0, p1, w, net, layer=None):
            if abs(p0[0] - cx) < 1e-9 and abs(p0[1] - cy) < 1e-9:
                return first_leg_free and math.hypot(p1[0] - cx, p1[1] - cy) <= 0.6
            return True
        st.track_free = track_free
        st.via_ok = lambda x, y, net: math.hypot(x - cx, y - cy) >= 0.8
        return cx, cy

    def test_boxed_in_pad_gets_a_track_with_one_corner(self):
        with tempfile.TemporaryDirectory() as t:
            st = self.stitcher(t)
            cx, cy = self.boxed_in(st)
            self.assertTrue(st.stitch_pad("T1", "1", "GND", pcbnew.F_Cu, cx, cy))
            self.assertEqual(st.failed, [])
            via = st.vias[-1]
            corner = (st.segs[-2][2], st.segs[-2][3])
            self.assertAlmostEqual(math.hypot(corner[0] - cx, corner[1] - cy), pcb_stitch.DOG_FIRST[0])
            self.assertGreaterEqual(math.hypot(via[0] - cx, via[1] - cy), pcb_stitch.DIST[0])
            self.assertEqual((st.segs[-1][0], st.segs[-1][1]), corner)              # the second leg starts at the corner
            self.assertEqual((st.segs[-1][2], st.segs[-1][3]), (via[0], via[1]))   # and ends on the via

    def test_dogleg_is_deterministic(self):
        got = []
        for _ in range(2):
            with tempfile.TemporaryDirectory() as t:
                st = self.stitcher(t)
                cx, cy = self.boxed_in(st)
                got.append(st.dogleg(cx, cy, 0.25, "GND", "F.Cu"))
        self.assertIsNotNone(got[0])
        self.assertEqual(got[0], got[1])

    def test_pad_without_a_free_first_leg_still_fails(self):
        with tempfile.TemporaryDirectory() as t:
            st = self.stitcher(t)
            cx, cy = self.boxed_in(st, first_leg_free=False)
            self.assertFalse(st.stitch_pad("T1", "1", "GND", pcbnew.F_Cu, cx, cy))
            self.assertEqual(st.failed, [("T1", "1", "GND")])


@unittest.skipIf(pcbnew is None, "pcbnew (KiCad Python) not available")
class StitcherReuseLimit(unittest.TestCase):
    """run_pcb.sh PRESTITCH=1 stitches before the router: a pad must not run a long track to a far via across copper that
    is not routed yet, so the reuse distance is limited there (--reuse-max)."""

    def stitch_with(self, reuse_max):
        cx, cy = pcb_full.CX, pcb_full.CY
        with tempfile.TemporaryDirectory() as t:
            src = Path(t) / "b.kicad_pcb"
            fixture_board(src, [(cx, cy)])
            st = pcb_stitch.Stitcher(pcbnew.LoadBoard(str(src)), str(src))
            st.tab_r = 30.0
            st.vias.append((cx + 3.0, cy, pcb_stitch.VIA_D, "GND"))      # a via of the net 3 mm away
            if reuse_max is not None:
                st.reuse_max = reuse_max
            n0 = len(st.vias)
            self.assertTrue(st.stitch_pad("T1", "1", "GND", pcbnew.F_Cu, cx, cy))
            return len(st.vias) - n0, st.added[-1][3]

    def test_default_joins_the_via_3_mm_away(self):
        self.assertEqual(self.stitch_with(None), (0, 3.0))

    def test_short_limit_places_a_new_via_beside_the_pad(self):
        new, dist = self.stitch_with(1.6)
        self.assertEqual(new, 1)
        self.assertLess(dist, 1.6)

    def test_run_pcb_prestitch_uses_the_limit(self):
        txt = (Path(__file__).resolve().parent.parent / "run_pcb.sh").read_text(encoding="utf-8")
        block = txt[txt.index('if [ "${PRESTITCH:-0}" = 1 ]'):]
        block = block[:block.index("\n  fi\n")]
        self.assertIn("pcb_stitch.py", block)
        self.assertIn('--reuse-max="${PRESTITCH_REUSE:-1.6}"', block)
        self.assertIn("pcb_dsn.py\" lock", block)                          # the fan-out vias are locked for the router


@unittest.skipIf(pcbnew is None, "pcbnew (KiCad Python) not available")
class StitcherSeesLockedTracks(unittest.TestCase):
    """Batch p1b5 (2026-11-18): the pre-route stitch put a GND via on a locked LED ring track (/LED_ROW2), a short. KiCad
    writes `(locked yes)` between `width` and `layer` of a segment and the copper reader skipped such segments. After
    routing every track is unlocked, so only the fan-out-first switch (PRESTITCH=1) met the defect."""

    def board_with_track(self, path, locked):
        cx, cy = pcb_full.CX, pcb_full.CY
        fixture_board(path, [(cx, cy)])
        b = pcbnew.LoadBoard(str(path))
        net = pcbnew.NETINFO_ITEM(b, "SIG")
        b.Add(net)
        tr = pcbnew.PCB_TRACK(b)
        tr.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(cx - 3.0), pcbnew.FromMM(cy + 1.2)))
        tr.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(cx + 3.0), pcbnew.FromMM(cy + 1.2)))
        tr.SetWidth(pcbnew.FromMM(0.25))
        tr.SetLayer(pcbnew.F_Cu)
        tr.SetNet(net)
        tr.SetLocked(locked)
        b.Add(tr)
        pcbnew.SaveBoard(str(path), b)
        return cx, cy

    def test_locked_segment_is_read(self):
        with tempfile.TemporaryDirectory() as t:
            src = Path(t) / "b.kicad_pcb"
            self.board_with_track(src, locked=True)
            self.assertIn("(locked yes)", src.read_text(encoding="utf-8"))
            segs, _ = pcb_stitch.read_copper(str(src))
            self.assertEqual([(s[5], s[6]) for s in segs], [("SIG", "F.Cu")])

    def test_no_via_on_a_locked_track(self):
        for locked in (False, True):
            with self.subTest(locked=locked), tempfile.TemporaryDirectory() as t:
                src = Path(t) / "b.kicad_pcb"
                cx, cy = self.board_with_track(src, locked)
                st = pcb_stitch.Stitcher(pcbnew.LoadBoard(str(src)), str(src))
                st.tab_r = 30.0
                self.assertFalse(st.via_ok(cx, cy + 1.2, "GND"))           # on the track
                self.assertTrue(st.stitch_pad("T1", "1", "GND", pcbnew.F_Cu, cx, cy))
                vx, vy, _, _ = st.vias[-1]
                self.assertGreaterEqual(pcb_stitch.seg_dist(vx, vy, cx - 3.0, cy + 1.2, cx + 3.0, cy + 1.2),
                                        pcb_stitch.VIA_D / 2 + 0.125 + pcb_stitch.CLR - 1e-9)


@unittest.skipIf(pcbnew is None, "pcbnew (KiCad Python) not available")
class StitcherViaOnTheSessionGrid(unittest.TestCase):
    """Batch p1b6 (2026-11-19): pre-route stitch vias at positions such as 51.565807 mm went through the router (Specctra
    resolution 0.1 um); the router's tracks ended at the rounded point, KiCad reported `track_not_centered_on_via`, and the
    clean-up ripped up the via with its stitch track (U7 pin 6 lost its +5V via on run2). Stitch vias sit on the 0.1 um grid."""

    def test_new_via_is_on_the_grid(self):
        cx, cy = pcb_full.CX + 0.1234567, pcb_full.CY - 0.0987654
        with tempfile.TemporaryDirectory() as t:
            src = Path(t) / "b.kicad_pcb"
            fixture_board(src, [(cx, cy)])
            st = pcb_stitch.Stitcher(pcbnew.LoadBoard(str(src)), str(src))
            st.tab_r = 30.0
            self.assertTrue(st.stitch_pad("T1", "1", "GND", pcbnew.F_Cu, cx, cy))
            vx, vy, _, _ = st.vias[-1]
            for v in (vx, vy):
                self.assertEqual(pcbnew.FromMM(v) % 100, 0, v)          # nm; 100 nm = 0.1 um


@unittest.skipIf(pcbnew is None, "pcbnew (KiCad Python) not available")
class StitcherFinePitchGround(unittest.TestCase):
    """Batches p1b4 to p1b6: the GND pads 4 and 10 of U1 (TUSB321, X2QFN-12, 0.4 mm pitch, 0.2 mm pads) never got a stitch:
    a 0.25 mm GND track needs 0.335 mm from its centre line to the next pad, the pitch leaves 0.30 mm. GND has no current
    rating (NET_WIDTH), so the stitcher retries at the default track width (0.15 mm needs 0.285 mm)."""

    def board(self, path):
        cx, cy = pcb_full.CX, pcb_full.CY
        b = pcbnew.BOARD()
        b.SetCopperLayerCount(4)
        nets = {n: pcbnew.NETINFO_ITEM(b, n) for n in ("GND", "SIG")}
        for n in nets.values():
            b.Add(n)
        fp = pcbnew.FOOTPRINT(b)
        fp.SetReference("U1")
        for i, dy in enumerate((-0.4, 0.0, 0.4)):            # one side of the QFN: pads 0.5 mm long (x), 0.2 mm wide (y)
            pad = pcbnew.PAD(fp)
            pad.SetNumber(str(i + 3))
            pad.SetShape(pcbnew.PAD_SHAPE_RECT)
            pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
            pad.SetLayerSet(pcbnew.PAD.SMDMask())
            pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.5), pcbnew.FromMM(0.2)))
            pad.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(cx), pcbnew.FromMM(cy + dy)))
            pad.SetNet(nets["GND" if dy == 0.0 else "SIG"])
            fp.Add(pad)
        for dy in (-1.2, 1.2):                                # the other rows of the package: no escape up or down
            pad = pcbnew.PAD(fp)
            pad.SetNumber("9")
            pad.SetShape(pcbnew.PAD_SHAPE_RECT)
            pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
            pad.SetLayerSet(pcbnew.PAD.SMDMask())
            pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.2), pcbnew.FromMM(0.5)))
            pad.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(cx + 0.5), pcbnew.FromMM(cy + dy)))
            pad.SetNet(nets["SIG"])
            fp.Add(pad)
        b.Add(fp)
        pcbnew.SaveBoard(str(path), b)
        return cx, cy

    def test_ground_pad_at_0_4_mm_pitch_is_stitched_with_a_narrow_track(self):
        with tempfile.TemporaryDirectory() as t:
            src = Path(t) / "b.kicad_pcb"
            cx, cy = self.board(src)
            st = pcb_stitch.Stitcher(pcbnew.LoadBoard(str(src)), str(src))
            st.tab_r = 30.0
            self.assertTrue(st.stitch_pad("U1", "4", "GND", pcbnew.F_Cu, cx, cy))
            self.assertEqual(st.segs[-1][4], pcb_rules.TRACK)

    def test_rated_net_keeps_its_width(self):
        """+5V has a current-based width (NET_WIDTH): no narrow retry."""
        self.assertEqual(pcb_stitch.Stitcher.widths("+5V"), (pcb_rules.NET_WIDTH["+5V"],))
        self.assertEqual(pcb_stitch.Stitcher.widths("GND"), (pcb_rules.STITCH_W["GND"], pcb_rules.TRACK))
