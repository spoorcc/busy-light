"""Spike: canonical semantic dump of a design for reproducibility and regeneration checks (ADR-0012 item 11).
Covers parts (value, footprint, HW_REQ), nets, footprint positions, tracks, vias, zones and rule areas,
stackup, design rules and net classes. UUID-free, sorted, coordinates rounded to 1 um.
usage: dump_design.py <netlist> <pcb> <project.kicad_pro> -> JSON on stdout"""
import json
import sys
from pathlib import Path

import pcbnew
from sexpr import find, parse


def r(x) -> float:
    return round(float(x), 3)


def dump(net_file: str, pcb_file: str, pro_file: str) -> dict:
    tree = parse(Path(net_file).read_text())
    parts = {}
    for c in find(find(tree, "components")[0], "comp"):
        f = {x[1][1]: (x[2] if len(x) > 2 else "") for fl in find(c, "fields") for x in find(fl, "field")}
        parts[find(c, "ref")[0][1]] = {
            "value": find(c, "value")[0][1],
            "footprint": find(c, "footprint")[0][1],
            "HW_REQ": f.get("HW_REQ", ""),
        }
    nets = {
        find(n, "name")[0][1]: sorted(f"{find(x, 'ref')[0][1]}.{find(x, 'pin')[0][1]}" for x in find(n, "node"))
        for n in find(find(tree, "nets")[0], "net")
    }
    board = pcbnew.LoadBoard(pcb_file)
    positions = {
        fp.GetReference(): [
            r(pcbnew.ToMM(fp.GetPosition().x)),
            r(pcbnew.ToMM(fp.GetPosition().y)),
            r(fp.GetOrientationDegrees() % 360),
        ]
        for fp in board.GetFootprints()
    }
    pcb = parse(Path(pcb_file).read_text())

    def val(node, key):
        v = find(node, key)
        return v[0][1:] if v else []

    tracks = sorted(
        json.dumps(
            [val(t, "net")[0], val(t, "layer")[0], r(val(t, "width")[0])]
            + sorted([[r(v) for v in val(t, "start")], [r(v) for v in val(t, "end")]])
        )
        for t in find(pcb, "segment")
    )
    vias = sorted(
        json.dumps([val(v, "net")[0], [r(x) for x in val(v, "at")], r(val(v, "size")[0]), r(val(v, "drill")[0]), val(v, "layers")])
        for v in find(pcb, "via")
    )
    zones = []
    for z in find(pcb, "zone"):
        pts = [[r(v) for v in p[1:3]] for poly in find(z, "polygon") for pp in find(poly, "pts") for p in find(pp, "xy")]
        zones.append(
            {
                "name": (val(z, "name") or [""])[0],
                "layers": val(z, "layers"),
                "net": (val(z, "net_name") or [""])[0],
                "keepout": json.dumps(find(z, "keepout")),
                "points": pts,
            }
        )
    zones.sort(key=lambda z: z["name"])
    setup = find(pcb, "setup")[0]
    stackup = [
        [x[1], next((q[1] for q in find(x, "thickness")), None)] for st in find(setup, "stackup") for x in find(st, "layer")
    ]
    pro = json.loads(Path(pro_file).read_text())
    ds = pro["board"]["design_settings"]
    return {
        "parts": parts,
        "nets": nets,
        "positions": positions,
        "tracks": tracks,
        "vias": vias,
        "zones": zones,
        "board_thickness": val(find(pcb, "general")[0], "thickness"),
        "stackup": stackup,
        "design_rules": ds["rules"],
        "net_classes": pro["net_settings"]["classes"],
        "netclass_patterns": pro["net_settings"]["netclass_patterns"],
    }


if __name__ == "__main__":
    print(json.dumps(dump(*sys.argv[1:4]), indent=1, sort_keys=True))
