# SPDX-License-Identifier: Apache-2.0
"""Merge the violations of two DRC reports (kicad-cli JSON) for the third finishing pass (RV-019 G3).

Usage: python3 merge_drc.py <first drc.json> <second drc.json> <out.json>
The first report supplies every key; its `violations` list is extended with the violations of the second one. pcb_finish.py reads only
the silkscreen findings of the merged list, so a text that failed in pass 1 or in pass 2 stays off the board in pass 3.
"""
from __future__ import annotations

import json
import sys


def merge(first: dict, second: dict) -> dict:
    out = dict(first)
    out["violations"] = list(first.get("violations", [])) + list(second.get("violations", []))
    return out


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print(__doc__, file=sys.stderr)
        return 2
    with open(argv[1], encoding="utf-8") as f1, open(argv[2], encoding="utf-8") as f2:
        merged = merge(json.load(f1), json.load(f2))
    with open(argv[3], "w", encoding="utf-8") as fo:
        json.dump(merged, fo)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
