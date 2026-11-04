# SPDX-License-Identifier: Apache-2.0
"""Layout writer: deterministic output, every netlist pin is drawn, no random UUIDs (ADR-0012 spike)."""
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
import layout_sch  # noqa: E402
import write_sch  # noqa: E402

NETLIST = HERE / "data" / "gate.net"


class LayoutWriter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = NETLIST.read_text()

    def test_two_builds_are_identical(self):
        a = layout_sch.build(self.text)
        b = layout_sch.build(self.text)
        out = []
        for i, s in enumerate((a, b)):
            f = HERE / f"_tmp_layout_{i}.kicad_sch"
            s.to_file(str(f))
            out.append(f.read_bytes())
            f.unlink()
        self.assertEqual(out[0], out[1])

    def test_every_component_is_placed(self):
        comps, _ = write_sch.parse_netlist(self.text)
        refs = {c["ref"] for c in comps if not c["ref"].startswith("#")}
        self.assertEqual(refs, set(layout_sch.PLACE))

    def test_every_connected_pin_has_a_wire_end_or_a_neighbour(self):
        # Each pin of a placed part must be the end of a wire, a no-connect, a power symbol pin or
        # share its point with another part's pin (the power symbols and R1/R6 joins).
        _, nets = write_sch.parse_netlist(self.text)
        sch = layout_sch.build(self.text)
        ends = set()
        for g in sch.graphicalItems:
            for p in g.points:
                ends.add((round(p.X, 2), round(p.Y, 2)))
        for j in sch.junctions:   # a pin that ends on the middle of a wire sits on a junction
            ends.add((round(j.position.X, 2), round(j.position.Y, 2)))
        for n in sch.noConnects:
            ends.add((round(n.position.X, 2), round(n.position.Y, 2)))
        for s in sch.schematicSymbols:
            if s.libraryNickname == "power":
                ends.add((round(s.position.X, 2), round(s.position.Y, 2)))
        comps, _ = write_sch.parse_netlist(self.text)
        # rebuild pin positions through a fresh sheet
        sheet = layout_sch.Sheet([c for c in comps if not c["ref"].startswith("#")])
        for ref, (x, y, rot) in layout_sch.PLACE.items():
            sheet.place(ref, x, y, rot)
        pin_net = {p: n for n, pins in nets.items() for p in pins}
        for (ref, number), (px, py) in sheet.pins.items():
            if (ref, number) in pin_net:
                self.assertIn((round(px, 2), round(py, 2)), ends, f"{ref} pin {number} is not drawn")


if __name__ == "__main__":
    unittest.main()
