# SPDX-License-Identifier: Apache-2.0
"""Table of placement-only runs (plan 08 R2a; RV-019 pass 3, S4).

Usage: python3 place_table.py <placement dir> [<placement dir> ...]
Each dir holds busy_light_spike.placement.json (written by pcb_full.py). One line per dir: the seed that was kept, its overlap,
the number of missed placement rules and the worst few as "part distance/limit". Exit 0 when at least one dir has no overlap and
no missed rule, 1 when none has, 2 on a usage error."""

from __future__ import annotations

import json
import sys
from pathlib import Path

WORST = 4
OVERLAP_EPS = 1e-9


def table(dirs: list[str]) -> tuple[list[str], bool]:
    lines: list[str] = []
    clean = False
    for d in dirs:
        info = json.loads((Path(d) / "busy_light_spike.placement.json").read_text(encoding="utf-8"))
        misses = info.get("layout_rule_misses", [])
        ok = not misses and info.get("overlap_mm2", 0.0) < OVERLAP_EPS
        clean = clean or ok
        worst = sorted(misses, key=lambda m: m[3] - m[2], reverse=True)[:WORST]
        names = ", ".join(f"{m[0]} {m[3]}/{m[2]}" for m in worst)
        lines.append(
            f"{d}: seed {info.get('seed')}, overlap {info.get('overlap_mm2')} mm2, "
            f"{len(misses)} misses{(' (' + names + ')') if names else ''}"
        )
    return lines, clean


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    lines, clean = table(argv[1:])
    print("\n".join(lines))
    return 0 if clean else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
