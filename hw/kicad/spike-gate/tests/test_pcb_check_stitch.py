# SPDX-License-Identifier: Apache-2.0
"""Plan 06 G3: M1 count (T10) and stitcher exit code (T9). Needs pcbnew; skipped visibly without it.
Run: cd hw/kicad/spike-gate && PYTHONPATH=src:tests python3 -m unittest test_pcb_check_stitch
"""
import json
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


def fixture_board(path, pads):
    b = pcbnew.BOARD()
    b.SetCopperLayerCount(4)
    net = pcbnew.NETINFO_ITEM(b, "GND")
    b.Add(net)
    fp = pcbnew.FOOTPRINT(b)
    fp.SetReference("T1")
    for i, (x, y) in enumerate(pads):
        pad = pcbnew.PAD(fp)
        pad.SetNumber(str(i + 1))
        pad.SetShape(pcbnew.PAD_SHAPE_RECT)
        pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        pad.SetLayerSet(pcbnew.PAD.SMDMask())
        pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(1), pcbnew.FromMM(1)))
        pad.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
        pad.SetNet(net)
        fp.Add(pad)
    b.Add(fp)
    pcbnew.SaveBoard(str(path), b)


@unittest.skipIf(pcbnew is None, "pcbnew (KiCad Python) not available")
class StitcherExit(unittest.TestCase):
    def run_cli(self, pads):
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            src = t / "busy_light_spike.kicad_pcb"
            fixture_board(src, pads)
            (t / "busy_light_spike.placement.json").write_text(json.dumps({"tab_r": 30.0}))
            drc = t / "drc.json"
            drc.write_text(json.dumps({"unconnected_items": [
                entry("Pad %d [GND] of T1 on F.Cu" % (i + 1), "Track [GND] on F.Cu, length 1 mm") for i in range(len(pads))]}))
            res = subprocess.run([sys.executable, str(SRC / "pcb_stitch.py"), str(src), str(drc), str(t / "out.kicad_pcb")],
                                 capture_output=True, text=True, check=False)
            out = json.loads([ln for ln in res.stdout.splitlines() if ln.startswith("{")][-1])
            return res.returncode, out

    def test_pad_that_can_be_stitched_exits_zero(self):
        rc, rep = self.run_cli([(pcb_full.CX, pcb_full.CY)])
        self.assertEqual((rc, rep["failed"]), (0, []), rep)
        self.assertEqual(rep["vias_added"], 1)

    def test_failed_pad_exits_non_zero(self):
        rc, rep = self.run_cli([(pcb_full.CX, pcb_full.CY), (pcb_full.CX + 200.0, pcb_full.CY)])
        self.assertEqual(rc, 1)
        self.assertEqual(len(rep["failed"]), 1)


if __name__ == "__main__":
    unittest.main()
