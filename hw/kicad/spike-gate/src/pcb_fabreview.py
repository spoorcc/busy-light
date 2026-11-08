# SPDX-License-Identifier: Apache-2.0
"""Assembly and documentation checks of a spike board (HW-010): what the DRC and pcb_fabcheck.py do not cover.

Usage: python3 pcb_fabreview.py <board.kicad_pcb> <bom.csv>      (bom.csv from `kicad-cli sch export bom`; needs pcbnew)
Checks: unannotated references in the BOM, BOM against the board, parts with a tbd value, reference designators on the
silkscreen, fiducials. Prints JSON; exit 0 when there are no findings, 1 otherwise. It does not check part numbers or
availability (the BOM has no MPN field) and it does not replace a fabricator's review.
"""
from __future__ import annotations

import csv
import json
import sys


def unannotated(refs: list[str]) -> list[str]:
    return [r for r in refs if r.endswith("?")]


def bom_vs_board(bom_refs: list[str], board_refs: list[str]) -> dict:
    board = [r for r in board_refs if not r.startswith("TP")]           # test points are out of the BOM on purpose
    return {"only_bom": sorted(set(bom_refs) - set(board)), "only_board": sorted(set(board) - set(bom_refs))}


def open_values(rows: list[tuple[str, str]]) -> list[str]:
    return [ref for ref, val in rows if not val.strip() or "tbd" in val.lower()]


def missing_mpn(rows: list[tuple[str, dict]]) -> list[str]:
    return [ref for ref, f in rows if not f.get("MPN", "").strip()]


def refs_on_silk(ref_layers: list[str]) -> int:
    return sum(1 for n in ref_layers if "silk" in n.lower())


def fiducials(fp_names: list[str]) -> int:
    return sum(1 for n in fp_names if "fiducial" in n.lower())


def verdict(m: dict) -> dict:
    f = []
    if m["unannotated"]:
        f.append("BOM has unannotated references: %s" % ", ".join(m["unannotated"]))
    if m["no_fiducials"]:
        f.append("no fiducials on the board")
    if m["refs_on_silk"] == 0:
        f.append("no reference designators on the silkscreen")
    if m["open_values"]:
        f.append("parts with a tbd value: %s" % ", ".join(m["open_values"]))
    return {"status": "FINDINGS" if f else "OK", "findings": f}


def main(argv: list[str]) -> int:
    import pcbnew  # noqa: PLC0415
    b = pcbnew.LoadBoard(argv[1])
    fps = b.GetFootprints()
    board_refs = [f.GetReference() for f in fps]
    rows = list(csv.DictReader(open(argv[2], encoding="utf-8")))
    bom_refs = [x.strip() for r in rows for x in r["Refs"].split(",")]
    val = [(x.strip(), r["Value"]) for r in rows for x in r["Refs"].split(",")]
    m = {"unannotated": unannotated(bom_refs), "bom_vs_board": bom_vs_board(bom_refs, board_refs),
         "open_values": open_values(val), "refs_on_silk": refs_on_silk([f.Reference().GetLayerName() for f in fps]),
         "fiducials": fiducials([str(f.GetFPID().GetLibItemName()) for f in fps]),
         "parts": len(fps), "bottom_side": sum(1 for f in fps if f.GetLayerName() == "B.Cu"),
         "has_mpn_field": "MPN" in rows[0]}
    m["no_fiducials"] = m["fiducials"] == 0
    m["verdict"] = verdict(m)
    print(json.dumps(m, indent=1))
    return 0 if m["verdict"]["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
