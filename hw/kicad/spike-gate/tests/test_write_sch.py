# SPDX-License-Identifier: Apache-2.0
"""Unit tests of the schematic writer: determinism and pin coverage (needs kiutils, KiCad symbols)."""
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
import write_sch  # noqa: E402
from kiutils.schematic import Schematic  # noqa: E402

NETLIST = HERE / "data" / "gate.net"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class WriterTest(unittest.TestCase):
    def test_deterministic(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = os.path.join(d, "a.kicad_sch"), os.path.join(d, "b.kicad_sch")
            write_sch.write(str(NETLIST), a)
            write_sch.write(str(NETLIST), b)
            self.assertEqual(digest(a), digest(b))

    def test_deterministic_in_new_process(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = os.path.join(d, "a.kicad_sch"), os.path.join(d, "b.kicad_sch")
            write_sch.write(str(NETLIST), a)
            subprocess.run([sys.executable, str(HERE.parent / "src" / "write_sch.py"),
                            str(NETLIST), b], check=True,
                           env={**os.environ, "PYTHONHASHSEED": "7"})
            self.assertEqual(digest(a), digest(b))

    def test_every_connected_pin_has_label_or_power_symbol(self):
        _comps, nets = write_sch.parse_netlist(NETLIST.read_text())
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "g.kicad_sch")
            write_sch.write(str(NETLIST), out)
            sch = Schematic.from_file(out)
        ends = {(lbl.position.X, lbl.position.Y): lbl.text for lbl in sch.labels}
        for s in sch.schematicSymbols:
            if s.libraryNickname == "power":
                ends[(s.position.X, s.position.Y)] = s.properties[1].value
        wires = {w.uuid: w for w in sch.graphicalItems if w.type == "wire"}
        rails = {n for n, pins in nets.items() if any(p[0].startswith("#FLG") for p in pins)}
        missing, checked = [], 0
        for name, pins in nets.items():
            if len(pins) < 2 and name not in rails:
                continue  # one-pin net: a no-connect marker, not a label
            for ref, pin in pins:
                checked += 1
                w = wires.get(write_sch.uid(f"w{ref}.{pin}"))
                end = (w.points[1].X, w.points[1].Y) if w else None
                if ends.get(end) != name:
                    missing.append((ref, pin, name))
        self.assertGreater(checked, 40)
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
