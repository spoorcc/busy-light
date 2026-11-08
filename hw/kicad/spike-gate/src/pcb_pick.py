# SPDX-License-Identifier: Apache-2.0
"""Pick the best of several routing runs (Freerouting is not deterministic, so runs differ).

Usage: python3 pcb_pick.py <out dir> <run dir> [<run dir> ...]
Each run dir holds a/final.kicad_pcb and a/drc_final.json (written by run_pcb.sh). The score of a run is
(unconnected items, FAIL lines of the strict gate, hard findings); the lowest wins, the first listed run on a tie. The files of the
winner are copied to <out dir>/best/ and a table of all runs is printed. Exit 0 when the winner has no unconnected item
and no hard finding, else 1.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

HARD = ("clearance", "track_width", "via_dangling", "hole_clearance", "hole_to_hole", "copper_edge_clearance",
        "shorting_items", "isolated_copper", "min_through_hole", "annular_width", "starved_thermal")
TRACK = ("track_dangling", "track_not_centered_on_via")


def score(drc: dict) -> tuple[int, int, int]:
    """(unconnected items, hard findings, track findings) of one DRC report (kicad-cli JSON)."""
    kinds = [v["type"] for v in drc.get("violations", [])]
    return (len(drc.get("unconnected_items", [])), sum(k in HARD for k in kinds), sum(k in TRACK for k in kinds))


def strict_fails(board: Path, profile: str = "stitched-4l") -> int:
    """Number of FAIL lines of the strict gate (kicad_strict.py drc) for one board; the environment decides the mode."""
    import subprocess
    out = subprocess.run([sys.executable, str(Path(__file__).resolve().parent / "kicad_strict.py"), "drc", str(board), profile],
                         capture_output=True, text=True, check=False)
    return sum(1 for ln in (out.stdout + out.stderr).splitlines() if ln.lstrip().startswith("FAIL"))


def pick(runs: list[Path], gate=None) -> tuple[Path | None, list[tuple[Path, tuple[int, int, int] | None]]]:
    rows = []
    for r in runs:
        f = r / "a" / "drc_final.json"
        sc = score(json.loads(f.read_text(encoding="utf-8"))) if f.exists() and (r / "a" / "final.kicad_pcb").exists() else None
        if sc is not None and gate is not None:                  # the strict gate decides between runs with the same open items
            sc = (sc[0], gate(r / "a" / "final.kicad_pcb"), sc[1])
        rows.append((r, sc))
    ok = [(s, i) for i, (_, s) in enumerate(rows) if s is not None]
    return (rows[min(ok)[1]][0] if ok else None), rows


def main(argv: list[str]) -> int:
    out, runs = Path(argv[1]), [Path(a) for a in argv[2:]]
    best, rows = pick(runs, gate=strict_fails)
    for r, s in rows:
        print("%-40s %s" % (r.name, "no result" if s is None else "unconnected %d, strict FAIL %d, hard %d" % s))
    if best is None:
        print("no run finished")
        return 1
    dst = out / "best"
    shutil.rmtree(dst, ignore_errors=True)
    dst.mkdir(parents=True)
    for f in (best / "a").glob("final.*"):
        shutil.copy2(f, dst / f.name)
    for f in (best / "a").glob("drc_final.json"):
        shutil.copy2(f, dst / f.name)
    for f in (best / "a").glob("*-lib-table"):                      # fp-lib-table, sym-lib-table: the board needs them to find its libraries
        shutil.copy2(f, dst / f.name)
    for d in (best / "a").glob("*.pretty"):
        shutil.copytree(d, dst / d.name)
    (dst / "chosen_run.txt").write_text(best.name + "\n", encoding="utf-8")
    s = dict(rows)[best]
    print("best:", best.name, "->", dst)
    return 0 if s[0] == 0 and s[1] == 0 and s[2] == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
