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


class Dru(unittest.TestCase):
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
