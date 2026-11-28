# SPDX-License-Identifier: Apache-2.0
"""Helpers of scripts/fab_p1.sh for the P1 order package (plan 08 section 4.5; HW-008, HW-009).

Usage:
  fab_package.py ignore-refs <board.kicad_pcb>
      Print the comma-separated refs for `kikit fab jlcpcb --ignore`, with the reason of each on
      stderr: the refs that JLCPCB does not assemble (`fab_check.exclusion_reason`: through-hole
      by footprint attribute, DNP, TP*, FID*, mounting holes, footprints excluded from the BOM or
      the position files) less the footprints marked `exclude_from_pos_files`, which KiKit leaves
      out of the CPL, and therefore out of the BOM, by itself.
      Reason: KiKit 1.8.1 on KiCad 10.0.8 stops with "'SwigPyObject' object has no attribute
      'SetOutputDirectory'" when --ignore removes 9 or more footprints (seen 2026-11-18 on the
      stand-in board; 2 to 5 refs worked). scripts/fab_check.py checks the result either way.
  fab_package.py full-bom <kicad-cli bom.csv> <out.csv> [--schematic <board.kicad_sch>]
      Copy the full BOM that kicad-cli wrote and add the column "JLCPCB library" with the value
      "not known" (basic or extended is not read from JLCPCB; plan 08 section 4.5). With the
      schematic, add a row for each symbol that is excluded from the BOM (kicad-cli 10 leaves them
      out): the do-not-populate spares C4 and C32 (HW-016, TC-216: "do-not-populate in the BOM")
      and the test points, with DNP "DNP" or "excluded from BOM" (RV-016 row 16).
  fab_package.py manifest <out dir> --input NAME=PATH ... --tool NAME=VERSION ...
                 --git-describe TEXT
      Write <out dir>/manifest.json: sha256 of every file in <out dir> (raw, and without the KiCad
      date lines of fab_check.DATE_LINE), sha256 of every input, the tool versions and the source
      description.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from fab_check import (
    InputError,
    classify,
    digest_without_dates,
    parse_sexpr,
    read_footprints,
    ref_key,
    sexpr_atoms,
    sexpr_children,
)

LIBRARY_COLUMN = "JLCPCB library"
LIBRARY_VALUE = "not known"
MANIFEST = "manifest.json"


def ignore_refs(board: Path) -> tuple[list[str], dict[str, str]]:
    """Refs to pass to `kikit fab jlcpcb --ignore` (sorted) and the reason of every excluded ref."""
    footprints = read_footprints(board)
    _, excluded = classify(footprints)
    pos_excluded = {fp.ref for fp in footprints if "exclude_from_pos_files" in fp.attrs}
    return sorted(set(excluded) - pos_excluded), excluded


def excluded_symbols(sch: Path) -> list[dict[str, str]]:
    """Fields of the schematic symbols that are excluded from the BOM (power symbols left out), with
    "DNP" set to "DNP" for a do-not-populate symbol and "excluded from BOM" otherwise."""
    try:
        tree = parse_sexpr(sch.read_text(encoding="utf-8"))
    except OSError as exc:
        raise InputError(f"cannot read schematic {sch}: {exc}") from exc
    if not tree or not isinstance(tree[0], list) or tree[0][:1] != ["kicad_sch"]:
        raise InputError(f"{sch} is not a kicad_sch file")
    out = []
    for sym in sexpr_children(tree[0], "symbol"):
        flags = {n[0]: (sexpr_atoms(n) or [""])[0] for n in sym[1:] if isinstance(n, list) and n}
        if flags.get("in_bom") != "no":
            continue
        fields = {}
        for prop in sexpr_children(sym, "property"):
            atoms = sexpr_atoms(prop)
            if len(atoms) >= 2:  # noqa: PLR2004
                fields[atoms[0]] = atoms[1]
        if fields.get("Reference", "#").startswith("#"):
            continue
        fields["DNP"] = "DNP" if flags.get("dnp") == "yes" else "excluded from BOM"
        out.append(fields)
    return out


def full_bom(src: Path, dst: Path, schematic: Path | None = None) -> int:
    """Add the library column to a kicad-cli BOM, and with the schematic a row per symbol excluded
    from the BOM. Returns the number of data rows."""
    rows = list(csv.reader(io.StringIO(src.read_text(encoding="utf-8-sig"))))
    if not rows:
        raise InputError(f"{src} is empty")
    header = rows[0]
    if schematic is not None:
        have = {r.strip() for row in rows[1:] for r in row[header.index("Refs")].split(",")}
        groups: dict[tuple[str, ...], list[str]] = {}
        names = {"Refs": "Reference", "Qty": None}
        for f in excluded_symbols(schematic):
            if f["Reference"] in have:
                continue
            key = tuple(f.get(names.get(h) or h, "") for h in header if h not in names)
            groups.setdefault(key, []).append(f["Reference"])
        for key, refs in sorted(groups.items(), key=lambda kv: ref_key(min(kv[1], key=ref_key))):
            vals = iter(key)
            row = []
            for h in header:
                if h == "Refs":
                    row.append(",".join(sorted(refs, key=ref_key)))
                elif h == "Qty":
                    row.append(str(len(refs)))
                else:
                    row.append(next(vals))
            rows.append(row)
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow([*header, LIBRARY_COLUMN])
    for row in rows[1:]:
        writer.writerow([*row, LIBRARY_VALUE])
    dst.write_text(buf.getvalue(), encoding="utf-8")
    return len(rows) - 1


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def manifest(
    out_dir: Path, inputs: dict[str, Path], tools: dict[str, str], git_describe: str
) -> dict[str, object]:
    """Manifest of a package directory (the manifest file itself is not listed)."""
    files: dict[str, dict[str, object]] = {}
    for p in sorted(out_dir.rglob("*")):
        name = p.relative_to(out_dir).as_posix()
        if not p.is_file() or name == MANIFEST:
            continue
        data = p.read_bytes()
        files[name] = {
            "bytes": len(data),
            "sha256": sha256(data),
            "sha256_without_dates": digest_without_dates(name, data),
        }
    return {
        "schema": 1,
        "description": "P1 order package (plan 08 section 4.5); made by scripts/fab_p1.sh",
        "git_describe": git_describe,
        "tools": dict(sorted(tools.items())),
        "inputs": {
            k: {"path": str(v), "sha256": sha256(v.read_bytes())} for k, v in sorted(inputs.items())
        },
        "files": files,
    }


def _pairs(items: Sequence[str], what: str) -> dict[str, str]:
    out = {}
    for item in items:
        key, sep, val = item.partition("=")
        if not sep or not key or not val:
            raise InputError(f"{what} '{item}' is not NAME=VALUE")
        out[key] = val
    return out


def main(argv: Sequence[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("ignore-refs")
    s.add_argument("board")
    s = sub.add_parser("full-bom")
    s.add_argument("src")
    s.add_argument("dst")
    s.add_argument("--schematic", default=None)
    s = sub.add_parser("manifest")
    s.add_argument("out_dir")
    s.add_argument("--input", action="append", default=[], metavar="NAME=PATH")
    s.add_argument("--tool", action="append", default=[], metavar="NAME=VERSION")
    s.add_argument("--git-describe", required=True)
    args = p.parse_args(argv)
    try:
        if args.cmd == "ignore-refs":
            refs, reasons = ignore_refs(Path(args.board))
            for r in sorted(reasons):
                how = "--ignore" if r in refs else "left out by KiKit (exclude_from_pos_files)"
                print(f"not assembled: {r} ({reasons[r]}; {how})", file=sys.stderr)
            print(",".join(refs))
        elif args.cmd == "full-bom":
            sch = Path(args.schematic) if args.schematic else None
            n = full_bom(Path(args.src), Path(args.dst), sch)
            print(f"full BOM: {n} lines -> {args.dst}")
        else:
            inputs = {k: Path(v) for k, v in _pairs(args.input, "--input").items()}
            doc = manifest(
                Path(args.out_dir), inputs, _pairs(args.tool, "--tool"), args.git_describe
            )
            target = Path(args.out_dir) / MANIFEST
            target.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
            print(f"manifest: {target}")
    except (InputError, OSError) as exc:
        print(f"fab_package: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
