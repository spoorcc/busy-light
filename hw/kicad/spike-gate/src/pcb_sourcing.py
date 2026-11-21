# SPDX-License-Identifier: Apache-2.0
"""Copy the sourcing fields (MPN, Manufacturer, LCSC) of the schematic symbols to the footprints of a stored board.

Usage: python3 pcb_sourcing.py <board.kicad_pcb> <schematic.kicad_sch>      (needs pcbnew; rewrites the board; no copper change)
The schematic is the source (its fields come from `sourcing.py` through the generator). A stored board keeps the fields it was
built with, so a number found later (plan 08 order step O2, `scripts/fab_missing_lcsc.txt`) reaches the order files only through
this script. A new field is hidden on the Fab layer of the part's side, as `pcb_full.set_p1_fields` does. Prints the changes as
JSON. HW-008, HW-009.
"""
from __future__ import annotations

import json
import sys

from pcb_spare_caps import SOURCING_FIELDS, schematic_fields


def changes(sch: dict[str, dict[str, str]], board: dict[str, dict[str, str]]) -> list[tuple[str, str, str, str]]:
    """(ref, field, old, new) for every sourcing field of a schematic symbol whose footprint differs; refs not on the board
    are skipped. Sorted, so the output is deterministic."""
    out = []
    for ref in sorted(set(sch) & set(board)):
        for k in SOURCING_FIELDS:
            new = sch[ref].get(k)
            if new is not None and board[ref].get(k, "") != new:
                out.append((ref, k, board[ref].get(k, ""), new))
    return out


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        sys.exit(__doc__)
    import pcbnew  # noqa: PLC0415
    b = pcbnew.LoadBoard(argv[1])
    sch = schematic_fields(open(argv[2], encoding="utf-8").read())
    fps = {f.GetReference(): f for f in b.GetFootprints()}
    have = {r: {k: (f.GetField(k).GetText() if f.GetField(k) else "") for k in SOURCING_FIELDS} for r, f in fps.items()}
    todo = changes(sch, have)
    for ref, k, _old, new in todo:
        fp = fps[ref]
        if fp.GetField(k) is None:
            fp.SetField(k, new)
            fld = fp.GetField(k)
            fld.SetVisible(False)
            fld.SetLayer(pcbnew.B_Fab if fp.IsFlipped() else pcbnew.F_Fab)
        else:
            fp.GetField(k).SetText(new)
    pcbnew.SaveBoard(argv[1], b)
    print(json.dumps({"changed": [list(c) for c in todo]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
