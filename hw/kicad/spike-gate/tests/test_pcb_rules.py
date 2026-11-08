# SPDX-License-Identifier: Apache-2.0
"""Plan 06 G2: rule numbers live in pcb_rules.py (T4) and the generated .kicad_dru is loaded by KiCad (T11).

Pure-Python tests run anywhere. Tests that need pcbnew or kicad-cli are skipped visibly when it is missing.
Run: cd hw/kicad/spike-gate && PYTHONPATH=src:tests python3 -m unittest test_pcb_rules
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
import pcb_rules as R  # noqa: E402

try:
    import pcbnew  # noqa: E402
    import pcb_full  # noqa: E402
    import pcb_stitch  # noqa: E402
except ImportError:  # venv python without KiCad
    pcbnew = None

# The values of write_project and the stitcher at the start of G2 (the current .kicad_pro). Nothing may be looser.
EXPECTED_FLOOR = {"clearance": 0.15, "track": 0.15, "via_diameter": 0.5, "through_hole": 0.3, "annular": 0.1,
                  "hole_clearance": 0.25, "hole_to_hole": 0.4, "edge": 0.3}
DRU_RULES = ("spike_clearance", "spike_track", "spike_via", "spike_annular", "spike_hole_to_hole", "spike_edge")


class Constants(unittest.TestCase):
    def test_floor_is_the_values_found_at_g2(self):
        self.assertEqual(R.FLOOR, EXPECTED_FLOOR)

    def test_no_minimum_is_looser_than_the_floor(self):
        for key, val in R.minimums().items():
            self.assertGreaterEqual(val, R.FLOOR[key], key)

    def test_base_values_fit_their_minimums(self):
        self.assertGreaterEqual(R.TRACK, R.MIN_TRACK)
        self.assertGreaterEqual(R.VIA_DIA, R.MIN_VIA_DIA)
        self.assertGreaterEqual((R.VIA_DIA - R.VIA_DRILL) / 2, R.ANNULAR)
        for n, w in R.NET_WIDTH.items():
            self.assertGreaterEqual(w, R.MIN_TRACK, n)

    def test_stitch_margin_and_plane_nets(self):
        self.assertEqual(R.STITCH_MARGIN, 0.06)
        self.assertEqual(R.PLANE_NETS, frozenset({"GND", "+5V"}))

    def test_stitch_width_rule(self):
        self.assertEqual(R.stitch_width("+5V"), R.NET_WIDTH["+5V"])
        self.assertEqual(R.stitch_width("GND"), R.STITCH_W["GND"])
        self.assertEqual(R.STITCH_W["GND"], 0.25)

    def test_net_class_widths(self):
        w = R.net_class_widths()
        self.assertEqual(w["Default"], R.TRACK)
        for n, width in R.NET_WIDTH.items():
            self.assertEqual(w["PWR_" + n.strip("+")], width)
        self.assertEqual(len(w), 1 + len(R.NET_WIDTH))


class RunMeta(unittest.TestCase):
    """T16 (meta part): run_meta.json has exactly the specified keys; a missing key is an error."""

    FIELDS = dict(placed_board_sha256="a", dsn_sha256="b", kicad_version="10", jar_sha256="c", fr_passes=60,
                  fr_threads=4, java_version="21", wall_time_s=1.5, planes="none")

    def test_keys(self):
        import pcb_replay

        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "run_meta.json"
            pcb_replay.write_meta(str(p), **self.FIELDS)
            data = json.loads(p.read_text())
        self.assertEqual(sorted(data), sorted(pcb_replay.META_KEYS))
        self.assertIsInstance(data["fr_passes"], int)
        self.assertIsInstance(data["wall_time_s"], float)

    def test_missing_key_raises(self):
        import pcb_replay

        fields = dict(self.FIELDS)
        del fields["jar_sha256"]
        with self.assertRaises(ValueError):
            pcb_replay.write_meta("/nonexistent/x.json", **fields)


class CleanUpHelpers(unittest.TestCase):
    def test_clamp_track_width(self):
        self.assertEqual(R.clamp_track_width(0.10), R.MIN_TRACK)
        self.assertEqual(R.clamp_track_width(0.12), R.MIN_TRACK)
        self.assertEqual(R.clamp_track_width(0.30), 0.30)

    def test_default_track_is_not_below_minimum(self):
        self.assertGreaterEqual(R.TRACK, R.MIN_TRACK)

    def test_hole_gap_ok_needs_hole_edge_distance(self):
        vias = [(0.0, 0.0, R.VIA_DIA, "GND")]
        need = R.VIA_DRILL + R.HOLE_TO_HOLE          # drill 0.3 each: centre distance 0.7 mm
        self.assertFalse(R.hole_gap_ok(need - 0.01, 0.0, vias))
        self.assertTrue(R.hole_gap_ok(need, 0.0, vias))
        self.assertTrue(R.hole_gap_ok(5.0, 5.0, vias))
        self.assertTrue(R.hole_gap_ok(0.0, 0.0, []))

    def test_hole_gap_ignores_nets(self):
        vias = [(0.0, 0.0, R.VIA_DIA, "+3V3")]
        self.assertFalse(R.hole_gap_ok(0.3, 0.0, vias))

    def test_dangling_via_positions_reads_only_vias(self):
        drc = {"violations": [
            {"type": "via_dangling", "items": [{"description": "Via [GND] on F.Cu - B.Cu", "pos": {"x": 1.0, "y": 2.0}}]},
            {"type": "via_dangling", "items": [{"description": "Track [GND]", "pos": {"x": 9.0, "y": 9.0}}]},
            {"type": "clearance", "items": [{"description": "Via [GND]", "pos": {"x": 7.0, "y": 7.0}}]}]}
        self.assertEqual(R.dangling_via_positions(drc), [(1.0, 2.0)])
        self.assertEqual(R.dangling_via_positions({}), [])

    def test_reuse_targets_nearest_first_same_net_only(self):
        vias = [(3.0, 0.0, 0.6, "GND"), (1.0, 0.0, 0.6, "GND"), (0.5, 0.0, 0.6, "+5V"), (9.0, 0.0, 0.6, "GND")]
        got = R.reuse_targets(0.0, 0.0, vias, "GND", 3.2)
        self.assertEqual([v[0] for v in got], [1.0, 3.0])
        self.assertEqual(R.reuse_targets(0.0, 0.0, vias, "GND", 0.5), [])


class ViaRemoval(unittest.TestCase):
    def test_joins_nothing_only_when_no_second_layer_is_needed(self):
        ends = [(1.0, 1.0, "F.Cu"), (5.0, 5.0, "F.Cu"), (5.0, 5.0, "B.Cu"), (7.0, 7.0, "F.Cu"), (7.0, 7.0, "F.Cu")]
        self.assertTrue(R.joins_nothing(9.0, 9.0, ends, []))            # no track end
        self.assertTrue(R.joins_nothing(1.0, 1.0, ends, []))            # one track end
        self.assertTrue(R.joins_nothing(7.0, 7.0, ends, []))            # two ends on one layer touch each other
        self.assertFalse(R.joins_nothing(5.0, 5.0, ends, []))           # a layer change
        self.assertFalse(R.joins_nothing(9.0, 9.0, [], [(8.0, 8.0, 10.0, 10.0)]))   # a pad is there


class MainPathSplit(unittest.TestCase):
    def test_main_path_pads(self):
        self.assertTrue(R.is_main_path_pad("VBUS_IC", "J1", "A4"))
        self.assertTrue(R.is_main_path_pad("VBUS_IC", "U7", "1"))
        self.assertFalse(R.is_main_path_pad("VBUS_IC", "U7", "3"))        # enable pin: microamps
        self.assertFalse(R.is_main_path_pad("VBUS_IC", "R1", "1"))
        self.assertTrue(R.is_main_path_pad("GND", "R1", "2"))             # other nets are not split

    def test_branch_width_is_a_legal_narrow_track(self):
        self.assertGreaterEqual(R.BRANCH_WIDTH, R.MIN_TRACK)
        self.assertLess(R.BRANCH_WIDTH, R.NET_WIDTH["VBUS_IC"])

    def test_main_path_pins_exist_in_the_main_net_table(self):
        self.assertEqual(R.MAIN_PATH_NET, "VBUS_IC")
        self.assertIn("J1", R.MAIN_PATH_PADS)


class RouteFirst(unittest.TestCase):
    def test_key_nets_are_exact_names_and_not_plane_nets(self):
        self.assertTrue(R.is_key_net("VBUS_IC"))
        self.assertFalse(R.is_key_net("GND"))
        self.assertFalse(R.is_key_net("+5V"))
        self.assertFalse(R.is_key_net("vbus_ic"))
        self.assertTrue(set(R.ROUTE_FIRST).isdisjoint(R.PLANE_NETS))

    def test_vbus_path_width_covers_the_top_current_step(self):
        self.assertGreaterEqual(R.NET_WIDTH["VBUS_IC"], R.ipc2221_width_mm(R.I_TOP_STEP_MAX_A) - 0.01)

    def test_3v3_width_covers_the_regulator_rating(self):
        self.assertGreaterEqual(R.NET_WIDTH["+3V3"], R.ipc2221_width_mm(1.0) - 0.01)     # TLV757P: 1 A

    def test_vbus_path_has_a_placement_weight(self):
        self.assertGreater(R.NET_WEIGHT["VBUS_IC"], 1.0)


class Dru(unittest.TestCase):
    def test_silk_waiver_names_only_the_listed_footprints(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "x.kicad_dru"
            R.write_dru(str(p), 4, silk_waiver=True)
            text = p.read_text()
            q = Path(t) / "y.kicad_dru"
            R.write_dru(str(q), 4, silk_waiver=False)
            self.assertNotIn("severity ignore", q.read_text())          # default: no waiver (DEV-006 not approved)
        self.assertIn('(rule "spike_silk_waiver"', text)
        self.assertIn("(severity ignore)", text)
        for ref in R.SILK_WAIVER_REFS:
            self.assertIn("memberOfFootprint('%s')" % ref, text)
        self.assertEqual(text.count("(severity ignore)"), 2)      # silk clearance and the J1 silk edge rule only
        self.assertNotIn("(severity ignore)\n\t(condition \"A.Layer == 'F.Cu'", text)

    def test_write_dru_is_deterministic_and_complete(self):
        with tempfile.TemporaryDirectory() as t:
            a, b = Path(t) / "a.kicad_dru", Path(t) / "b.kicad_dru"
            R.write_dru(str(a), 4)
            R.write_dru(str(b), 4)
            self.assertEqual(a.read_bytes(), b.read_bytes())
            text = a.read_text()
        self.assertTrue(text.startswith("(version 1)"))
        for name in DRU_RULES:
            self.assertIn('(rule "%s"' % name, text)
        got = dict(re.findall(r"\(constraint (\w+) \(min ([0-9.]+)mm\)\)", text))
        self.assertEqual(float(got["clearance"]), R.CLEARANCE)
        self.assertEqual(float(got["track_width"]), R.MIN_TRACK)
        self.assertEqual(float(got["via_diameter"]), R.MIN_VIA_DIA)
        self.assertEqual(float(got["annular_width"]), R.ANNULAR)
        self.assertEqual(float(got["hole_to_hole"]), R.HOLE_TO_HOLE)
        self.assertEqual(float(got["edge_clearance"]), R.EDGE_CLEARANCE)

    def test_dru_values_not_looser_than_floor(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "x.kicad_dru"
            R.write_dru(str(p), 4)
            vals = [float(v) for v in re.findall(r"\(min ([0-9.]+)mm\)", p.read_text())]
        self.assertEqual(len(vals), 6)
        self.assertGreaterEqual(min(vals), min(EXPECTED_FLOOR.values()))


@unittest.skipIf(pcbnew is None, "pcbnew (KiCad Python) not available")
class SharedSource(unittest.TestCase):
    def test_pcb_full_reads_pcb_rules(self):
        for name in ("CLEARANCE", "TRACK", "VIA_DIA", "VIA_DRILL", "EDGE_CLEARANCE", "NET_WIDTH", "NET_TRACK"):
            self.assertEqual(getattr(pcb_full, name), getattr(R, name), name)

    def test_stitcher_reads_pcb_rules(self):
        self.assertEqual((pcb_stitch.VIA_D, pcb_stitch.VIA_DRILL), (R.VIA_DIA, R.VIA_DRILL))
        self.assertAlmostEqual(pcb_stitch.CLR, R.CLEARANCE + R.STITCH_MARGIN)
        self.assertEqual(pcb_stitch.stitch_width("+5V"), R.NET_WIDTH["+5V"])
        self.assertEqual(pcb_stitch.stitch_width("GND"), R.STITCH_W["GND"])

    def test_project_file_carries_the_rules(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "x.kicad_pro"
            pcb_full.write_project(str(p), "x")
            pro = json.loads(p.read_text())
        rules = pro["board"]["design_settings"]["rules"]
        self.assertEqual(rules["min_clearance"], R.CLEARANCE)
        self.assertEqual(rules["min_track_width"], R.MIN_TRACK)
        self.assertEqual(rules["min_via_diameter"], R.MIN_VIA_DIA)
        self.assertEqual(rules["min_through_hole_diameter"], R.MIN_THROUGH_HOLE)
        self.assertEqual(rules["min_via_annular_width"], R.ANNULAR)
        self.assertEqual(rules["min_hole_clearance"], R.HOLE_CLEARANCE)
        self.assertEqual(rules["min_hole_to_hole"], R.HOLE_TO_HOLE)
        self.assertEqual(rules["min_copper_edge_clearance"], R.EDGE_CLEARANCE)
        widths = {c["name"]: c["track_width"] for c in pro["net_settings"]["classes"]}
        self.assertEqual(widths, R.net_class_widths())


def add_outline(b):
    mm = pcbnew.FromMM
    for (x0, y0, x1, y1) in ((0, 0, 20, 0), (20, 0, 20, 20), (20, 20, 0, 20), (0, 20, 0, 0)):
        s = pcbnew.PCB_SHAPE(b)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(mm(x0), mm(y0)))
        s.SetEnd(pcbnew.VECTOR2I(mm(x1), mm(y1)))
        s.SetLayer(pcbnew.Edge_Cuts)
        b.Add(s)


def canary_board(path, track_w=0.25):
    """Small board built by pcbnew calls: 4 layers, an outline, one track of width track_w on net N1."""
    b = pcbnew.BOARD()
    b.SetCopperLayerCount(4)
    net = pcbnew.NETINFO_ITEM(b, "N1")
    b.Add(net)
    mm = pcbnew.FromMM
    add_outline(b)
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(pcbnew.VECTOR2I(mm(5), mm(10)))
    t.SetEnd(pcbnew.VECTOR2I(mm(15), mm(10)))
    t.SetWidth(mm(track_w))
    t.SetLayer(pcbnew.F_Cu)
    t.SetNet(net)
    b.Add(t)
    pcbnew.SaveBoard(str(path), b)


class RouterZoneSelection(unittest.TestCase):
    """Plan 06 A-8: which zones the router sees for each `planes` setting (pure function, no pcbnew)."""

    def test_none_keeps_no_zone(self):
        for lay, net in (("F", "GND"), ("B", "GND"), ("In1", "GND"), ("In2", "+5V")):
            self.assertFalse(R.router_keeps_zone("none", lay, net), (lay, net))

    def test_inner_keeps_only_inner_gnd(self):
        self.assertTrue(R.router_keeps_zone("inner", "In1", "GND"))
        self.assertFalse(R.router_keeps_zone("inner", "In2", "+5V"), "the +5V plane stays out of the router view")
        self.assertFalse(R.router_keeps_zone("inner", "F", "GND"))
        self.assertFalse(R.router_keeps_zone("inner", "B", "GND"))

    def test_setting_is_case_insensitive(self):
        self.assertTrue(R.router_keeps_zone("INNER", "In1", "GND"))
        self.assertFalse(R.router_keeps_zone("NONE", "In1", "GND"))

    def test_outer_settings_keep_listed_outer_layers_and_inner_zones(self):
        self.assertTrue(R.router_keeps_zone("B", "B", "GND"))
        self.assertFalse(R.router_keeps_zone("B", "F", "GND"))
        self.assertTrue(R.router_keeps_zone("FB", "F", "GND"))
        self.assertTrue(R.router_keeps_zone("B", "In1", "GND"), "behaviour before A-8 is unchanged")

    def test_unknown_setting_is_an_error(self):
        with self.assertRaises(ValueError):
            R.router_keeps_zone("inner2", "In1", "GND")


@unittest.skipIf(pcbnew is None, "pcbnew (KiCad Python) not available")
class NetClassesInDsn(unittest.TestCase):
    """T4 (DSN part): the router classes come from the PWR_* net classes of the project file."""

    def test_dsn_carries_the_net_widths(self):
        with tempfile.TemporaryDirectory() as t:
            pcb = Path(t) / "x.kicad_pcb"
            nets = sorted(R.NET_WIDTH)
            b = pcbnew.BOARD()
            b.SetCopperLayerCount(4)
            add_outline(b)
            fp = pcbnew.FOOTPRINT(b)
            fp.SetReference("T1")
            for i, n in enumerate(nets):
                net = pcbnew.NETINFO_ITEM(b, n)
                b.Add(net)
                pad = pcbnew.PAD(fp)
                pad.SetNumber(str(i + 1))
                pad.SetShape(pcbnew.PAD_SHAPE_RECT)
                pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
                pad.SetLayerSet(pcbnew.PAD.SMDMask())
                pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(1), pcbnew.FromMM(1)))
                pad.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(5 + 3 * i), pcbnew.FromMM(-10)))
                pad.SetNet(net)
                fp.Add(pad)
            b.Add(fp)
            pcbnew.SaveBoard(str(pcb), b)
            pcb_full.write_project(str(pcb.with_suffix(".kicad_pro")), "x")
            dsn = Path(t) / "x.dsn"
            # a fresh process: pcbnew caches the project of a path it has already saved, so it would not see the new file
            code = "import sys, pcbnew; b = pcbnew.LoadBoard(sys.argv[1]); sys.exit(0 if pcbnew.ExportSpecctraDSN(b, sys.argv[2]) else 1)"
            res = subprocess.run([sys.executable, "-c", code, str(pcb), str(dsn)], capture_output=True, text=True, check=False)
            self.assertEqual(res.returncode, 0, res.stderr)
            text = dsn.read_text()
        for n, w in R.NET_WIDTH.items():
            cls = "PWR_" + n.strip("+")
            m = re.search(r"\(class %s\b.*?\(width ([0-9.]+)\)" % re.escape(cls), text, re.S)
            self.assertIsNotNone(m, cls)
            self.assertAlmostEqual(float(m.group(1)) / 1000.0, w, places=3, msg=cls)  # DSN unit is um here


@unittest.skipIf(pcbnew is None or shutil.which("kicad-cli") is None, "pcbnew or kicad-cli not available")
class DruCanary(unittest.TestCase):
    """T11: a track under the DRU minimum gives a track_width finding that cites the rule `spike_track`."""

    def drc(self, pcb):
        out = pcb.with_suffix(".json")
        subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "--severity-all", "-o", str(out), str(pcb)],
                       check=False, capture_output=True)
        return json.loads(out.read_text())

    def test_dru_is_loaded(self):
        with tempfile.TemporaryDirectory() as t:
            pcb = Path(t) / "c.kicad_pcb"
            canary_board(pcb, track_w=0.25)
            clean = [v for v in self.drc(pcb)["violations"] if v["type"] == "track_width"]
            self.assertEqual(clean, [])
            dru = pcb.with_suffix(".kicad_dru")
            R.write_dru(str(dru), 4)
            text = dru.read_text().replace("(constraint track_width (min %smm))" % R.MIN_TRACK,
                                           "(constraint track_width (min 0.5mm))")
            self.assertIn("0.5mm", text)
            dru.write_text(text)
            hits = [v for v in self.drc(pcb)["violations"] if v["type"] == "track_width"]
        self.assertTrue(hits, "no track_width finding: KiCad did not load the .kicad_dru")
        self.assertIn("spike_track", json.dumps(hits))


if __name__ == "__main__":
    unittest.main()


class OuterOnly(unittest.TestCase):
    def test_layers_allowed(self):
        L = ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"]
        self.assertEqual(R.layers_allowed("VBUS_IC", L), ["F.Cu", "B.Cu"])
        self.assertEqual(R.layers_allowed("+3V3", L), ["F.Cu", "B.Cu"])
        self.assertEqual(R.layers_allowed("/ILIM", L), ["F.Cu", "In2.Cu", "B.Cu"])
        self.assertEqual(R.layers_allowed("+5V", L), ["F.Cu", "In2.Cu", "B.Cu"])
        self.assertEqual(R.layers_allowed("GND", L), L)

    def test_dsn_outer_rule(self):
        import subprocess
        import sys
        import tempfile
        from pathlib import Path

        dsn = ("(pcb x (network (class kicad_default /A (circuit (use_via V))) (class PWR_VBUS_IC VBUS_IC\\n      (circuit\\n        (use_via V)\\n      )"
               "\\n      (rule (width 600))) (class PWR_3V3 +3V3 (circuit (use_via V)) (rule (width 300)))))")
        with tempfile.TemporaryDirectory() as t:
            a, b = Path(t, "a.dsn"), Path(t, "b.dsn")
            a.write_text(dsn)
            subprocess.run([sys.executable, str(Path(__file__).resolve().parent.parent / "src" / "pcb_dsn.py"), "outer", str(a), str(b)],
                           check=True, capture_output=True)
            out = b.read_text()
        self.assertEqual(out.count("(use_layer F.Cu B.Cu)"), 2)
        self.assertEqual(out.count("(use_layer F.Cu In2.Cu B.Cu)"), 1)
        self.assertLess(out.index("kicad_default"), out.index("use_layer F.Cu In2.Cu B.Cu"))
        self.assertLess(out.index("use_layer F.Cu In2.Cu B.Cu"), out.index("PWR_VBUS_IC"))   # the default class got the In2 rule


class FineProfile(unittest.TestCase):
    """SPIKE_PROFILE=fine stays inside the JLCPCB multilayer minimums (capability page read 2026-11-08) and is off by default."""

    def values(self, env):
        import os
        e = dict(os.environ, **env)
        e.pop("SPIKE_PROFILE", None) if not env else None
        out = subprocess.run([sys.executable, "-c", "import json, pcb_rules as R; print(json.dumps([R.CLEARANCE, R.MIN_TRACK, R.VIA_DIA, R.VIA_DRILL, R.ANNULAR]))"],
                             cwd=str(Path(__file__).resolve().parent.parent / "src"), env=e, capture_output=True, text=True, check=True)
        return json.loads(out.stdout)

    def test_default_is_the_spike_profile(self):
        self.assertEqual(self.values({}), [0.15, 0.15, 0.6, 0.3, 0.1])

    def test_fine_is_inside_the_fab_minimums(self):
        clr, trk, via, drill, ring = self.values({"SPIKE_PROFILE": "fine"})
        self.assertGreaterEqual(clr, 0.09)                      # track and space 0.09 mm
        self.assertGreaterEqual(trk, 0.09)
        self.assertGreaterEqual(drill, 0.15)                    # via hole
        self.assertGreaterEqual(via, 0.25)                      # via diameter
        self.assertGreaterEqual((via - drill) / 2 + 1e-9, 0.15)  # annular ring absolute minimum
        self.assertGreaterEqual(ring, 0.15)
