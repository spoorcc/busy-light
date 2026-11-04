"""Spike: canonical semantic dump of a design (parts, fields, nets, positions) for reproducibility checks.
usage: dump_design.py <netlist> <pcb> -> JSON on stdout (sorted, UUID-free)."""
import json
import sys
from pathlib import Path

import pcbnew
from sexpr import find, parse

tree = parse(Path(sys.argv[1]).read_text())
parts = {}
for c in find(find(tree, "components")[0], "comp"):
    f = {x[1][1]: (x[2] if len(x) > 2 else "") for fl in find(c, "fields") for x in find(fl, "field")}
    parts[find(c, "ref")[0][1]] = {
        "value": find(c, "value")[0][1],
        "footprint": find(c, "footprint")[0][1],
        "HW_REQ": f.get("HW_REQ", ""),
    }
nets = {
    find(n, "name")[0][1]: sorted(
        f"{find(x, 'ref')[0][1]}.{find(x, 'pin')[0][1]}" for x in find(n, "node")
    )
    for n in find(find(tree, "nets")[0], "net")
}
board = pcbnew.LoadBoard(sys.argv[2])
pos = {
    fp.GetReference(): [
        round(pcbnew.ToMM(fp.GetPosition().x), 3),
        round(pcbnew.ToMM(fp.GetPosition().y), 3),
        round(fp.GetOrientationDegrees() % 360, 3),
    ]
    for fp in board.GetFootprints()
}
print(json.dumps({"parts": parts, "nets": nets, "positions": pos}, indent=1, sort_keys=True))
