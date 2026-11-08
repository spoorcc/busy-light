# SPDX-License-Identifier: Apache-2.0
"""Fabricator-minimum check of a routed spike board (read only; HW-010 spike, ADR-0020 Proposed).

Usage: python3 pcb_fabcheck.py <board.kicad_pcb>   (needs KiCad's pcbnew module and kicad-cli)
Compares the board with the JLCPCB multilayer minimums that ADR-0020 and pcb_rules.py record (capability page read 2026-11-08):
track and space 0.09 mm (1 oz), via hole 0.15 mm, via diameter 0.25 mm, annular ring 0.15 mm absolute minimum (0.20 recommended),
via hole to hole 0.2 mm, pad hole to pad hole 0.45 mm, SMD pad to pad 0.15 mm, copper to routed edge 0.2 mm.
Not a fabricator check: no fabricator reviewed the files, only JLCPCB numbers were used, and the page was not re-read.
Track and space and the edge distance are implied by the strict gate (0.1 mm clearance, 0.3 mm edge), see the report.
Exit code: 0 all checks pass, 1 a check fails, 2 not run.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import tempfile

NM = 1_000_000.0
FAB = {"track": 0.09, "via_dia": 0.25, "via_drill": 0.15, "annular_min": 0.15, "annular_recommended": 0.20,
       "via_hole_gap": 0.2, "pad_hole_gap": 0.45, "smd_pad_gap": 0.15}


def _capsule(h):
    """(ax, ay, bx, by, width) of a hole given as (x, y, diameter) or as a capsule already."""
    return h if len(h) == 5 else (h[0], h[1], h[0], h[1], h[2])


def _seg_dist(a, b):
    """Distance between two segments (ax, ay, bx, by, ...) that do not cross, or 0 when they do."""
    def pt_seg(px, py, s):
        dx, dy = s[2] - s[0], s[3] - s[1]
        L2 = dx * dx + dy * dy
        t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - s[0]) * dx + (py - s[1]) * dy) / L2))
        return math.hypot(px - (s[0] + t * dx), py - (s[1] + t * dy))

    def cross(o, p, q):
        return (p[0] - o[0]) * (q[1] - o[1]) - (p[1] - o[1]) * (q[0] - o[0])
    p1, p2, q1, q2 = (a[0], a[1]), (a[2], a[3]), (b[0], b[1]), (b[2], b[3])
    if (cross(p1, p2, q1) * cross(p1, p2, q2) < 0) and (cross(q1, q2, p1) * cross(q1, q2, p2) < 0):
        return 0.0
    return min(pt_seg(*p1, b), pt_seg(*p2, b), pt_seg(*q1, a), pt_seg(*q2, a))


def hole_gap(a, b):
    """Edge-to-edge gap (mm) of two holes, each (x, y, diameter) or a slot (ax, ay, bx, by, width); negative when they overlap."""
    ca, cb = _capsule(a), _capsule(b)
    return _seg_dist(ca, cb) - ca[4] / 2 - cb[4] / 2


def holes_too_close(holes, limit):
    """Pairs (i, j, gap) of holes whose edge gap is below limit; each pair once."""
    out = []
    for i in range(len(holes)):
        for j in range(i + 1, len(holes)):
            g = hole_gap(holes[i], holes[j])
            if g < limit - 1e-9:
                out.append((i, j, round(g, 4)))
    return out


def pad_rule_dru(limit):
    """Custom rule text: SMD and through pads of different items keep at least `limit` mm to each other."""
    return ('(version 1)\n(rule "fab_pad_to_pad"\n\t(condition "A.Type == \'Pad\' && B.Type == \'Pad\'")\n'
            "\t(constraint clearance (min %gmm)))\n" % limit)


def verdict(checks):
    return "PASS" if all(c["ok"] for c in checks.values()) else "FAIL"


def direct_checks(board):
    """Geometry checks that need no DRC: track width, via size and ring, hole gaps. Returns a dict with `checks` and numbers."""
    import pcbnew  # noqa: PLC0415
    tr = board.Tracks()        # index loop: the SWIG iterator is broken on Python 3.14
    widths, vias = [], []
    for i in range(tr.size()):
        t = tr[i]
        if t.GetClass() == "PCB_VIA":
            v = pcbnew.Cast_to_PCB_VIA(t)          # the list holds the base type; only the via has a drill
            p = v.GetPosition()
            vias.append((p.x / NM, p.y / NM, v.GetDrillValue() / NM, v.GetWidth(pcbnew.F_Cu) / NM))
        elif t.GetClass() == "PCB_TRACK":
            widths.append(t.GetWidth() / NM)
    pad_holes = []
    for f in board.GetFootprints():
        pl = f.Pads()
        for k in range(pl.size() if hasattr(pl, "size") else len(pl)):
            p = pl[k]
            ds = p.GetDrillSize()
            if ds.x > 0 and ds.y > 0:
                sh = p.GetEffectiveHoleShape()          # a segment with a width: a round hole has both ends equal
                if hasattr(sh, "GetSeg"):
                    sg = sh.GetSeg()
                    pad_holes.append((sg.A.x / NM, sg.A.y / NM, sg.B.x / NM, sg.B.y / NM, sh.GetWidth() / NM))
                else:
                    pos = p.GetPosition()
                    pad_holes.append((pos.x / NM, pos.y / NM, max(ds.x, ds.y) / NM))
    rings = [(v[3] - v[2]) / 2 for v in vias]
    via_holes = [(v[0], v[1], v[2]) for v in vias]
    pad_holes = [h for h in pad_holes]
    close_vias = holes_too_close(via_holes, FAB["via_hole_gap"])
    # a via against a pad hole counts with the pad rule, the stricter of the two
    close_pads = [(i, j, g) for (i, j, g) in holes_too_close(pad_holes + via_holes, FAB["pad_hole_gap"])
                  if i < len(pad_holes)]
    c = {
        "track_width": {"ok": (min(widths) if widths else 1.0) >= FAB["track"] - 1e-9, "min_mm": round(min(widths), 4) if widths else None,
                        "limit_mm": FAB["track"]},
        "via_diameter": {"ok": all(v[3] >= FAB["via_dia"] - 1e-9 for v in vias), "min_mm": round(min(v[3] for v in vias), 4) if vias else None,
                         "limit_mm": FAB["via_dia"]},
        "via_drill": {"ok": all(v[2] >= FAB["via_drill"] - 1e-9 for v in vias), "min_mm": round(min(v[2] for v in vias), 4) if vias else None,
                      "limit_mm": FAB["via_drill"]},
        "annular_ring": {"ok": all(r >= FAB["annular_min"] - 1e-9 for r in rings), "min_mm": round(min(rings), 4) if rings else None,
                         "limit_mm": FAB["annular_min"]},
        "via_hole_to_hole": {"ok": not close_vias, "pairs_below_limit": len(close_vias), "limit_mm": FAB["via_hole_gap"]},
        "pad_hole_to_hole": {"ok": not close_pads, "pairs_below_limit": len(close_pads), "limit_mm": FAB["pad_hole_gap"]},
    }
    return {"checks": c, "vias": len(vias), "tracks": len(widths), "pad_holes": len(pad_holes),
            "min_annular_mm": round(min(rings), 4) if rings else None,
            "vias_below_recommended_ring": sum(1 for r in rings if r < FAB["annular_recommended"] - 1e-9)}


def pad_gap_check(path, limit=None):
    """Run kicad-cli DRC on a copy of the board with only a pad-to-pad rule; returns {ok, violations} or None when not run."""
    limit = FAB["smd_pad_gap"] if limit is None else limit
    stem = os.path.splitext(os.path.basename(path))[0]
    src = os.path.dirname(os.path.abspath(path))
    with tempfile.TemporaryDirectory() as tmp:
        for ext in ("kicad_pcb", "kicad_pro"):
            s = os.path.join(src, "%s.%s" % (stem, ext))
            if os.path.exists(s):
                with open(s, "rb") as fi, open(os.path.join(tmp, "%s.%s" % (stem, ext)), "wb") as fo:
                    fo.write(fi.read())
        with open(os.path.join(tmp, stem + ".kicad_dru"), "w", encoding="utf-8") as f:
            f.write(pad_rule_dru(limit))
        out = os.path.join(tmp, "drc.json")
        res = subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "--severity-all", "-o", out,
                              os.path.join(tmp, stem + ".kicad_pcb")], capture_output=True, text=True, check=False)  # noqa: S603
        if not os.path.exists(out):
            return None
        rep = json.load(open(out, encoding="utf-8"))
    hits = [v for v in rep.get("violations", []) if v["type"] == "clearance" and "fab_pad_to_pad" in v["description"]]
    return {"ok": not hits, "violations": len(hits), "limit_mm": limit,
            "examples": [v["description"][:110] for v in hits[:3]]}


def main(path):
    import pcbnew  # noqa: PLC0415
    board = pcbnew.LoadBoard(path)
    r = direct_checks(board)
    pg = pad_gap_check(path)
    if pg is None:
        print(json.dumps({"fabcheck": "NOT RUN", "reason": "kicad-cli drc produced no report"}))
        return 2
    r["checks"]["smd_pad_to_pad"] = pg
    r["verdict"] = verdict(r["checks"])
    print(json.dumps(r, indent=1))
    return 0 if r["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
