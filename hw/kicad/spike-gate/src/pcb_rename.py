# SPDX-License-Identifier: Apache-2.0
"""Rename the seven references that KiCad reads as unannotated (no trailing number) on a stored board (HW-010).

Usage: python3 pcb_rename.py <board.kicad_pcb>       (needs pcbnew; rewrites the file; no routing change)
The generators use the new names since 2026-11-08 (RV: spike-fab-review.md finding 1). Parts and nets are renamed; nothing else moves.
"""
from __future__ import annotations

import re
import sys

MAP = {"C1B": "C27", "C1C": "C28", "C1D": "C29", "C1E": "C30", "C1F": "C31", "R_ILIM3B": "R20", "R_VD": "R21"}
# The net of R_ILIM3 pad 1 and R20 pad 2 is auto-named by its first pad in sorted order; with R20 in place KiCad names it Net-(R20-Pad2).
NETS = {"Net-(R_ILIM3-Pad1)": "Net-(R20-Pad2)"}
_PAT = re.compile(r"(?<![A-Za-z0-9_])(%s)(?![A-Za-z0-9_])" % "|".join(sorted(MAP, key=len, reverse=True)))


def rename(name: str, mapping: dict[str, str]) -> str:
    return _PAT.sub(lambda m: mapping[m.group(1)], name)


def main(argv: list[str]) -> int:
    import pcbnew  # noqa: PLC0415
    b = pcbnew.LoadBoard(argv[1])
    n = 0
    for f in b.GetFootprints():
        new = rename(f.GetReference(), MAP)
        if new != f.GetReference():
            f.SetReference(new)
            n += 1
    nets = b.GetNetInfo().NetsByName()
    for name in [str(k) for k in nets.keys()]:
        new = NETS.get(name, rename(name, MAP))
        if new != name:
            nets[name].SetNetname(new)
            n += 1
    b.Save(argv[1])
    print("renamed %d parts and nets" % n)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
