# SPDX-License-Identifier: Apache-2.0
"""Spike: check a generated board against the schematic netlist and summarise a DRC JSON report.

Usage: python3 pcb_check.py <netlist.net> <board.kicad_pcb> [drc.json]
Prints a JSON summary: refs and nets compared, pad/net differences, unconnected count, DRC counts by type and
severity, and the layout-rule measurements (ILIM net length, Q3 gate star, VBUS track width).
Exit code 1 when the board and the netlist differ.
"""
import collections
import json
import math
import re
import sys

import pcbnew

import pcb_full as P


def expected_pad_nets(comps, nets):
    exp = {}
    for n, nodes in nets.items():
        for ref, pin in nodes:
            m = P.PADMAP.get(ref, {}).get(pin, pin)
            for pn in (m if isinstance(m, tuple) else (m,)):
                exp[(ref, pn)] = P.short_net(n)
    return exp


def compare(netlist, pcb):
    comps, nets = P.read_netlist(netlist)
    b = pcbnew.LoadBoard(pcb)
    refs = {f.GetReference(): f for f in b.GetFootprints()}
    exp = expected_pad_nets(comps, nets)
    out = {"refs_netlist": len(comps), "refs_board_excluding_holes": len([r for r in refs if not r.startswith("H")]),
           "missing_refs": sorted(set(comps) - set(refs)),
           "extra_refs": sorted(r for r in set(refs) - set(comps) if not r.startswith("H")),
           "nets_netlist": len(nets), "nets_named": len([n for n in nets if not n.startswith("unconnected-")])}
    wrong = []
    seen = set()
    for ref, f in refs.items():
        if ref not in comps:
            continue
        for p in f.Pads():
            key = (ref, p.GetNumber())
            seen.add(key)
            want = exp.get(key)
            have = p.GetNetname() or None
            if want != have:
                wrong.append((ref, p.GetNumber(), want, have))
    out["pad_net_differences"] = wrong
    out["netlist_pins_without_pad"] = sorted(k for k in exp if k not in seen)
    out["board_nets"] = len([n for n in b.GetNetsByName().keys() if str(n)])
    return out, b


SEG = re.compile(r'\(segment\s+\(start ([-\d.]+) ([-\d.]+)\)\s+\(end ([-\d.]+) ([-\d.]+)\)\s+\(width ([\d.]+)\)\s+'
                 r'\(layer "([^"]+)"\)\s+\(net "([^"]*)"\)')


def layout_rules(pcb_path):
    """Measurements of the layout rules from the earlier reports (report them; do not claim compliance).
    Tracks are read from the board text because the SWIG track iterator is broken in this Python."""
    text = open(pcb_path, encoding="utf-8").read()
    res = {}
    lens = collections.defaultdict(float)
    widths = collections.defaultdict(list)
    for m in SEG.finditer(text):
        x0, y0, x1, y1, w = (float(m.group(i)) for i in range(1, 6))
        l = math.hypot(x1 - x0, y1 - y0)
        lens[m.group(7)] += l
        widths[m.group(7)].append((w, l))
    res["track_length_mm"] = {k: round(v, 1) for k, v in sorted(lens.items())}
    res["via_count"] = len(re.findall(r"\(via\b", text))
    for name in ("VBUS_IC", "+5V", "+3V3"):
        w = widths.get(name, [])
        tot = sum(l for _, l in w) or 1.0
        res["width_" + name] = {"min_mm": round(min((x for x, _ in w), default=0), 2),
                                "share_ge_0.5mm": round(sum(l for x, l in w if x >= 0.5) / tot, 2)}
    return res


def drc_summary(path):
    d = json.load(open(path))
    out = {}
    for k in ("violations", "unconnected_items", "schematic_parity"):
        items = d.get(k, [])
        out[k] = {"total": len(items),
                  "by_type_severity": dict(collections.Counter("%s/%s" % (v["type"], v.get("severity", "?")) for v in items))}
    return out


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    res, board = compare(sys.argv[1], sys.argv[2])
    res["layout"] = layout_rules(sys.argv[2])
    if len(sys.argv) > 3:
        res["drc"] = drc_summary(sys.argv[3])
    print(json.dumps(res, indent=1, sort_keys=True))
    bad = res["missing_refs"] or res["extra_refs"] or res["pad_net_differences"] or res["netlist_pins_without_pad"]
    sys.exit(1 if bad else 0)
