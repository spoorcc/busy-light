# SPDX-License-Identifier: Apache-2.0
"""Check a JLCPCB order package made from the P1 panel (plan 08 section 4.5; HW-008, HW-009).

Usage:
  fab_check.py <out dir> <board.kicad_pcb> [--allow-missing-lcsc REF,...]
               [--missing-lcsc-file FILE] [--owner-waiver-file FILE]
  fab_check.py --compare <dir1> <dir2>

Package files read from <out dir>: jlcpcb_bom.csv and jlcpcb_cpl.csv (`kikit fab jlcpcb
--assembly` on the panel) and gerbers.zip (its Edge.Cuts layer). The board is read as text
(footprint reference, value, library, layer, attributes); KiCad is not needed, so the tests run
with any Python.

Checks (each failure is listed):
  1. The BOM refs equal the CPL refs, and no ref is in a file twice.
  2. Every assembled ref of the board is in the BOM; every BOM ref is an assembled ref of the board.
  3. Every CPL row is on the top layer.
  4. Every CPL point is inside the panel outline (Edge.Cuts Gerber; same origin and y direction as
     the CPL).
  5. No excluded ref (see `exclusion_reason`) is in the BOM or the CPL.
  6. R_ILIM1, R_ILIM2 and R_ILIM3 are in the BOM with exactly the values of `ILIM_VALUES`
     (HW-010, ADR-0023; RV-016 row 28: a "0.1%" substring test let a wrong value pass).
  7. Every BOM line with an empty LCSC number is listed. It fails unless each of its refs is named
     by --allow-missing-lcsc or by the list file (one ref per line, then the reason; `#` starts a
     comment). Policy (plan 08 B2 fix): CI passes scripts/fab_missing_lcsc.txt and the release
     notes print it. A ref in `MUST_PLACE` (the HW-010 gate and the HW-017 power path) fails even
     when listed, unless the owner waiver file names it (RV-016 row 1: without U5 the gate fails
     open; without R22 the board has no power). Same file format.
  8. The bottom paste layer of the Gerbers is empty: the order is one-sided (HW-008; RV-016 row 17:
     the do-not-populate spares on the bottom had paste).
Exit codes: 0 all checks pass, 1 a check fails, 2 an input is missing or cannot be read.

--compare: both directories have the same files, and every file has the same content after the
lines with a date that KiCad writes are removed (`DATE_LINE`). Zip files are compared member by
member. In manifest.json the raw size and sha256 of each file are left out of the comparison (they
change with the dates); the hashes without the date lines are compared. Exit 0 when equal, 1 when
not, 2 when a directory is missing.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
import sys
import zipfile
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

BOM_FILE = "jlcpcb_bom.csv"
CPL_FILE = "jlcpcb_cpl.csv"
GERBER_ZIP = "gerbers.zip"
ILIM_REFS = ("R_ILIM1", "R_ILIM2", "R_ILIM3")
# HW-010 as amended by ADR-0023: step 3 = both switches, R_ILIM3 equals R_ILIM2. The test
# test_ilim_values_equal_the_generator_and_the_model keeps this equal to
# ilim_steps.candidate_both_on() and to the generator (layout_full.PARTS).
ILIM_VALUES = {"R_ILIM1": "47.0k 0.1%", "R_ILIM2": "56.2k 0.1%", "R_ILIM3": "54.9k 0.1%"}
# Parts whose absence leaves the HW-010 gate open or undefined, or the board without power: the CC
# IC and its inverter and pull-up, both ANDs, the supervisor and its delay capacitors, the
# gate-node pull-up, the limiter, both select switches, the ILIM resistors, the HW-017 link
# (ADR-0016, ADR-0023, HW-017). The fail-direction table of RV-016 row 7 may add parts.
MUST_PLACE = frozenset(
    {"U1", "U2", "R1", "U3", "U4", "U5", "C1", "R26", "R27", "R8", "U7"}
    | {"U14", "U15", "R_ILIM1", "R_ILIM2", "R_ILIM3", "R22"}
)
BOTTOM_PASTE = re.compile(r"(B_Paste|BPaste|\.gbp$)", re.IGNORECASE)
TOP_LAYERS = ("T", "TOP")

# Lines with a date that KiCad 10 writes: Gerber and Excellon headers, the Gerber job file, the
# drill report, the DRC/ERC JSON reports and the PDF information dictionary.
DATE_LINE = re.compile(
    rb"TF\.CreationDate|\"CreationDate\"|^G04 Created by KiCad .* date |^; DRILL file .* date "
    rb"|^Created on |\"date\"\s*:|/CreationDate|/ModDate"
)


class InputError(Exception):
    """A package or board file is missing or cannot be read."""


# -------------------------------------------------------------------------------------------- board
@dataclass(frozen=True)
class Footprint:
    ref: str
    value: str
    lib_id: str
    layer: str
    attrs: frozenset[str]


Sexpr = str | list["Sexpr"]
_TOKEN = re.compile(r'\s*(?:(\()|(\))|"((?:[^"\\]|\\.)*)"|([^\s()"]+))')


def parse_sexpr(text: str) -> list[Sexpr]:
    """Parse KiCad s-expression text into nested lists of str (quoted and bare atoms alike)."""
    stack: list[list[Sexpr]] = [[]]
    pos = 0
    while pos < len(text):
        m = _TOKEN.match(text, pos)
        if m is None:
            if text[pos:].strip():
                raise InputError(f"s-expression syntax error at offset {pos}")
            break
        pos = m.end()
        if m.group(1):
            stack.append([])
        elif m.group(2):
            if len(stack) < 2:  # noqa: PLR2004
                raise InputError(f"unbalanced ')' at offset {pos}")
            done = stack.pop()
            stack[-1].append(done)
        elif m.group(3) is not None:
            stack[-1].append(re.sub(r"\\(.)", r"\1", m.group(3)))
        elif m.group(4) is not None:
            stack[-1].append(m.group(4))
    if len(stack) != 1:
        raise InputError("unbalanced '(' at end of file")
    return stack[0]


def sexpr_children(node: list[Sexpr], head: str) -> list[list[Sexpr]]:
    return [c for c in node[1:] if isinstance(c, list) and c and c[0] == head]


def sexpr_atoms(node: list[Sexpr]) -> list[str]:
    return [c for c in node[1:] if isinstance(c, str)]


_children, _atoms = sexpr_children, sexpr_atoms


def read_footprints(board: Path) -> list[Footprint]:
    """Footprints of a .kicad_pcb file (KiCad 6 to 10 text format)."""
    try:
        tree = parse_sexpr(board.read_text(encoding="utf-8"))
    except OSError as exc:
        raise InputError(f"cannot read board {board}: {exc}") from exc
    if not tree or not isinstance(tree[0], list) or tree[0][:1] != ["kicad_pcb"]:
        raise InputError(f"{board} is not a kicad_pcb file")
    out = []
    for fp in _children(tree[0], "footprint"):
        lib = fp[1] if len(fp) > 1 and isinstance(fp[1], str) else ""
        fields: dict[str, str] = {}
        for prop in _children(fp, "property") + _children(fp, "fp_text"):
            atoms = _atoms(prop)
            if len(atoms) >= 2:  # noqa: PLR2004
                fields.setdefault(atoms[0].lower(), atoms[1])
        layer = next((a for n in _children(fp, "layer") for a in _atoms(n)), "")
        attrs = frozenset(a for n in _children(fp, "attr") for a in _atoms(n))
        out.append(
            Footprint(fields.get("reference", ""), fields.get("value", ""), lib, layer, attrs)
        )
    return out


def exclusion_reason(fp: Footprint) -> str | None:
    """Why a footprint is not assembled by JLCPCB, or None when it is an assembled part."""
    rules = (
        ("through_hole" in fp.attrs, "through-hole footprint (hand-soldered)"),
        ("dnp" in fp.attrs, "do not populate"),
        (fp.ref.startswith("TP"), "test point"),
        (fp.ref.startswith("FID"), "fiducial"),
        (
            fp.lib_id.split(":")[0] == "MountingHole" or bool(re.fullmatch(r"(MH|H)\d+", fp.ref)),
            "mounting hole",
        ),
        (
            bool(fp.attrs & {"exclude_from_bom", "exclude_from_pos_files", "board_only"}),
            "excluded from the BOM or the position files",
        ),
        ("smd" not in fp.attrs, "not an SMD footprint"),
    )
    return next((why for hit, why in rules if hit), None)


def classify(footprints: Iterable[Footprint]) -> tuple[set[str], dict[str, str]]:
    """(assembled refs, {excluded ref: reason}) of a board."""
    assembled: set[str] = set()
    excluded: dict[str, str] = {}
    for fp in footprints:
        reason = exclusion_reason(fp)
        if reason is None:
            assembled.add(fp.ref)
        else:
            excluded[fp.ref] = reason
    return assembled, excluded


# ------------------------------------------------------------------------------------ package files
@dataclass(frozen=True)
class BomLine:
    value: str
    refs: tuple[str, ...]
    footprint: str
    lcsc: str


@dataclass(frozen=True)
class CplRow:
    ref: str
    x: float
    y: float
    layer: str


def _rows(path: Path, required: Sequence[str]) -> list[dict[str, str]]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise InputError(f"cannot read {path}: {exc}") from exc
    reader = csv.DictReader(io.StringIO(text))
    header = {h.strip().lower(): h for h in (reader.fieldnames or [])}
    missing = [r for r in required if r.lower() not in header]
    if missing:
        raise InputError(f"{path}: missing column(s) {', '.join(missing)}")
    return [{r: (row.get(header[r.lower()]) or "").strip() for r in required} for row in reader]


def read_bom(path: Path) -> list[BomLine]:
    rows = _rows(path, ("Comment", "Designator", "Footprint", "LCSC"))
    return [
        BomLine(
            r["Comment"],
            tuple(x.strip() for x in r["Designator"].split(",") if x.strip()),
            r["Footprint"],
            r["LCSC"],
        )
        for r in rows
    ]


def read_cpl(path: Path) -> list[CplRow]:
    out = []
    for r in _rows(path, ("Designator", "Mid X", "Mid Y", "Layer")):
        try:
            out.append(CplRow(r["Designator"], float(r["Mid X"]), float(r["Mid Y"]), r["Layer"]))
        except ValueError as exc:
            raise InputError(f"{path}: bad coordinate in row {r}") from exc
    return out


# ------------------------------------------------------------------------------------------- gerber
Segment = tuple[float, float, float, float]
_FS = re.compile(r"FSLAX(\d)(\d)Y(\d)(\d)")
_STMT = re.compile(
    r"^(?:G0?(?P<g>[123]))?(?:X(?P<x>[+-]?\d+))?(?:Y(?P<y>[+-]?\d+))?"
    r"(?:I(?P<i>[+-]?\d+))?(?:J(?P<j>[+-]?\d+))?(?:D0?(?P<d>[123]))?$"
)
ARC_STEP_DEG = 2.0


def _arc_points(
    start: tuple[float, float], end: tuple[float, float], centre: tuple[float, float], cw: bool
) -> list[tuple[float, float]]:
    """Polyline of an arc from start to end around centre (a full circle when start == end)."""
    r = math.hypot(start[0] - centre[0], start[1] - centre[1])
    a0 = math.atan2(start[1] - centre[1], start[0] - centre[0])
    a1 = math.atan2(end[1] - centre[1], end[0] - centre[0])
    sweep = a1 - a0
    if cw:
        sweep = sweep if sweep < 0 else sweep - 2 * math.pi
    else:
        sweep = sweep if sweep > 0 else sweep + 2 * math.pi
    n = max(2, math.ceil(abs(math.degrees(sweep)) / ARC_STEP_DEG))
    pts = [
        (centre[0] + r * math.cos(a0 + sweep * k / n), centre[1] + r * math.sin(a0 + sweep * k / n))
        for k in range(n)
    ]
    return [*pts, end]


def gerber_segments(text: str) -> list[Segment]:
    """Drawn segments of a Gerber layer (lines; arcs as short lines; multi-quadrant mode only)."""
    ext = re.findall(r"%([^%]*)%", text)
    fs = next((m for e in ext if (m := _FS.search(e))), None)
    if fs is None or fs.group(2) != fs.group(4):
        raise InputError("Gerber without a usable %FS...% format statement")
    scale = 10.0 ** -int(fs.group(2))
    if any(e.strip().startswith("MOIN") for e in ext):
        scale *= 25.4
    body = re.sub(r"%[^%]*%", "", text)
    segs: list[Segment] = []
    cur = (0.0, 0.0)
    mode = "1"
    for raw in body.split("*"):
        st = raw.strip()
        if not st or st.startswith("G04") or st in ("G74", "G75", "M02", "G36", "G37"):
            continue
        m = _STMT.match(st)
        if m is None:
            continue  # aperture selection (D10 ...) and other statements without geometry
        if m.group("g"):
            mode = m.group("g")
        x = int(m.group("x")) * scale if m.group("x") else cur[0]
        y = int(m.group("y")) * scale if m.group("y") else cur[1]
        d = m.group("d")
        if d == "1":
            if mode == "1":
                segs.append((cur[0], cur[1], x, y))
            else:
                i = int(m.group("i") or 0) * scale
                j = int(m.group("j") or 0) * scale
                pts = _arc_points(cur, (x, y), (cur[0] + i, cur[1] + j), cw=mode == "2")
                segs.extend((a[0], a[1], b[0], b[1]) for a, b in zip(pts, pts[1:], strict=False))
        if d in ("1", "2") or (d is None and (m.group("x") or m.group("y"))):
            cur = (x, y)
    return segs


def inside(px: float, py: float, segs: Iterable[Segment]) -> bool:
    """Even-odd rule over closed outlines (inner cut-outs count as outside)."""
    hit = False
    for x0, y0, x1, y1 in segs:
        if (y0 > py) != (y1 > py) and px < x0 + (py - y0) * (x1 - x0) / (y1 - y0):
            hit = not hit
    return hit


def edge_cuts_from_zip(path: Path) -> list[Segment]:
    try:
        with zipfile.ZipFile(path) as zf:
            names = [
                n for n in zf.namelist() if re.search(r"(?i)(edge_?cuts|\.gm1$)", Path(n).name)
            ]
            if len(names) != 1:
                raise InputError(f"{path}: expected one Edge.Cuts member, found {names}")
            text = zf.read(names[0]).decode("ascii", "replace")
    except (OSError, zipfile.BadZipFile) as exc:
        raise InputError(f"cannot read {path}: {exc}") from exc
    segs = gerber_segments(text)
    if not segs:
        raise InputError(f"{path}: Edge.Cuts layer has no outline")
    return segs


# ------------------------------------------------------------------------------------- missing LCSC
def read_missing_list(path: Path) -> dict[str, str]:
    """{ref: reason} from the list file: one ref per line, then a reason; `#` starts a comment."""
    out: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise InputError(f"cannot read {path}: {exc}") from exc
    for n, line in enumerate(lines, 1):
        text = line.split("#", 1)[0].strip()
        if not text:
            continue
        parts = text.split(None, 1)
        if len(parts) < 2:  # noqa: PLR2004
            raise InputError(f"{path}:{n}: '{parts[0]}' has no reason")
        if parts[0] in out:
            raise InputError(f"{path}:{n}: '{parts[0]}' is listed twice")
        out[parts[0]] = parts[1]
    return out


# ------------------------------------------------------------------------------------------- checks
@dataclass
class Result:
    name: str
    ok: bool
    detail: str


def _refs(refs: Iterable[str]) -> str:
    return ", ".join(sorted(refs, key=_ref_key)) or "-"


def ref_key(ref: str) -> tuple[str, int]:
    """Sort key that puts C4 before C32."""
    m = re.match(r"(.*?)(\d*)$", ref)
    assert m is not None  # the pattern always matches
    return m.group(1), int(m.group(2) or 0)


_ref_key = ref_key


def run_checks(  # noqa: PLR0913, PLR0917 - one argument per package input, as read by _check_main
    bom: Sequence[BomLine],
    cpl: Sequence[CplRow],
    footprints: Sequence[Footprint],
    outline: Sequence[Segment],
    allowed_missing: dict[str, str],
    owner_waivers: dict[str, str] | None = None,
    bottom_paste: str | None = None,
) -> tuple[list[Result], list[str]]:
    """All checks of the module docstring. Returns the results and the missing-LCSC report lines."""
    res: list[Result] = []
    bom_refs = [r for line in bom for r in line.refs]
    cpl_refs = [row.ref for row in cpl]
    dup = {r for r, n in Counter(bom_refs).items() if n > 1} | {
        r for r, n in Counter(cpl_refs).items() if n > 1
    }
    diff = set(bom_refs) ^ set(cpl_refs)
    res.append(
        Result(
            "bom_equals_cpl",
            not dup and not diff,
            f"{len(set(bom_refs))} refs; only in one file: {_refs(diff)}; twice: {_refs(dup)}",
        )
    )

    assembled, excluded = classify(footprints)
    unknown = set(bom_refs) - assembled - set(excluded)
    not_in_bom = assembled - set(bom_refs)
    res.append(
        Result(
            "assembled_refs_once",
            not not_in_bom and not unknown and not dup,
            f"{len(assembled)} assembled refs on the board; not in the BOM: {_refs(not_in_bom)}; "
            f"in the BOM but not on the board: {_refs(unknown)}",
        )
    )

    bottom = [row.ref for row in cpl if row.layer.strip().upper() not in TOP_LAYERS]
    res.append(Result("cpl_top_layer", not bottom, f"rows not on the top layer: {_refs(bottom)}"))

    outside = [row.ref for row in cpl if not inside(row.x, row.y, outline)]
    res.append(
        Result("cpl_inside_panel", not outside, f"points outside the panel: {_refs(outside)}")
    )

    present = (set(bom_refs) | set(cpl_refs)) & set(excluded)
    res.append(
        Result(
            "no_excluded_refs",
            not present,
            "present: "
            + (", ".join(f"{r} ({excluded[r]})" for r in sorted(present, key=_ref_key)) or "-"),
        )
    )

    values = {r: line.value for line in bom for r in line.refs}
    bad_ilim = [r for r in ILIM_REFS if values.get(r) != ILIM_VALUES[r]]
    res.append(
        Result(
            "ilim_values",
            not bad_ilim,
            "; ".join(
                f"{r}={values.get(r, 'not in the BOM')!r} (expected {ILIM_VALUES[r]!r})"
                for r in ILIM_REFS
            ),
        )
    )

    waivers = owner_waivers or {}
    missing = sorted({r for line in bom if not line.lcsc for r in line.refs}, key=_ref_key)
    lines: list[str] = []
    not_allowed = []
    for r in missing:
        if r in MUST_PLACE and r in waivers:
            lines.append(f"  {r}: must-place part, OWNER WAIVER ({waivers[r]})")
        elif r in MUST_PLACE:
            why = f"listed ({allowed_missing[r]}), but " if r in allowed_missing else ""
            lines.append(f"  {r}: {why}a must-place part (HW-010 gate or HW-017 path): NOT ALLOWED")
            not_allowed.append(r)
        elif r in allowed_missing:
            lines.append(f"  {r}: allowed ({allowed_missing[r]})")
        else:
            lines.append(f"  {r}: NOT ALLOWED")
            not_allowed.append(r)
    stale = sorted(set(allowed_missing) - set(missing), key=_ref_key)
    lines += [f"  note: {r} is allowed but has no missing LCSC number here" for r in stale]
    res.append(
        Result(
            "lcsc_numbers",
            not not_allowed,
            f"{len(missing)} ref(s) without an LCSC number, not allowed: {_refs(not_allowed)}",
        )
    )

    paste_ops = gerber_operations(bottom_paste) if bottom_paste is not None else 0
    res.append(
        Result(
            "bottom_paste_empty",
            paste_ops == 0,
            "no bottom paste file"
            if bottom_paste is None
            else f"{paste_ops} flash or draw operation(s) on the bottom paste layer",
        )
    )
    return res, lines


def gerber_operations(text: str) -> int:
    """Number of flash (D03) and draw (D01) operations in a Gerber file."""
    return len(re.findall(r"D0?[13]\*", text))


def bottom_paste_from_zip(path: Path) -> str | None:
    """Text of the bottom paste Gerber in the zip, or None when the zip has none."""
    try:
        with zipfile.ZipFile(path) as zf:
            names = [n for n in zf.namelist() if BOTTOM_PASTE.search(n)]
            return zf.read(names[0]).decode("ascii", "replace") if names else None
    except (OSError, zipfile.BadZipFile) as exc:
        raise InputError(f"cannot read {path}: {exc}") from exc


# ------------------------------------------------------------------------------------------ compare
def normalized(data: bytes) -> bytes:
    """File content without the lines that carry a KiCad date."""
    return b"".join(
        line for line in data.splitlines(keepends=True) if not DATE_LINE.search(line.strip())
    )


def _zip_members(data: bytes) -> dict[str, bytes]:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        return {n: normalized(zf.read(n)) for n in zf.namelist()}


def digest_without_dates(name: str, data: bytes) -> str:
    """sha256 of a file without its KiCad date lines; a zip file by its member names and content."""
    h = hashlib.sha256()
    if name.endswith(".zip"):
        for member, content in sorted(_zip_members(data).items()):
            h.update(member.encode() + b"\0" + hashlib.sha256(content).digest())
    else:
        h.update(normalized(data))
    return h.hexdigest()


def _manifest_view(data: bytes) -> object:
    """The manifest without the raw size and sha256 of each file (they change with the dates)."""
    doc = json.loads(data)
    doc["files"] = {k: v.get("sha256_without_dates") for k, v in doc.get("files", {}).items()}
    return doc


def compare_dirs(a: Path, b: Path) -> list[str]:
    """Differences between two package directories, as text lines (empty when they are equal)."""
    for d in (a, b):
        if not d.is_dir():
            raise InputError(f"{d} is not a directory")
    fa = {p.relative_to(a).as_posix() for p in a.rglob("*") if p.is_file()}
    fb = {p.relative_to(b).as_posix() for p in b.rglob("*") if p.is_file()}
    out = [f"only in {a}: {n}" for n in sorted(fa - fb)] + [
        f"only in {b}: {n}" for n in sorted(fb - fa)
    ]
    for name in sorted(fa & fb):
        da, db = (a / name).read_bytes(), (b / name).read_bytes()
        if name.endswith(".zip"):
            ma, mb = _zip_members(da), _zip_members(db)
            if set(ma) != set(mb):
                out.append(f"{name}: different members {sorted(set(ma) ^ set(mb))}")
            out += [f"{name}:{m}: content differs" for m in sorted(ma) if ma[m] != mb.get(m)]
        elif Path(name).name == "manifest.json":
            if _manifest_view(da) != _manifest_view(db):
                out.append(f"{name}: content differs (raw sizes and sha256 left out)")
        elif normalized(da) != normalized(db):
            out.append(f"{name}: content differs")
    return out


# ---------------------------------------------------------------------------------------------- CLI
def _check_main(args: argparse.Namespace) -> int:
    out_dir, board = Path(args.out_dir), Path(args.board)
    allowed: dict[str, str] = {}
    if args.missing_lcsc_file:
        allowed.update(read_missing_list(Path(args.missing_lcsc_file)))
    for ref in filter(None, (r.strip() for r in args.allow_missing_lcsc.split(","))):
        allowed.setdefault(ref, "--allow-missing-lcsc")
    waivers = read_missing_list(Path(args.owner_waiver_file)) if args.owner_waiver_file else {}
    results, lcsc_lines = run_checks(
        read_bom(out_dir / BOM_FILE),
        read_cpl(out_dir / CPL_FILE),
        read_footprints(board),
        edge_cuts_from_zip(out_dir / GERBER_ZIP),
        allowed,
        waivers,
        bottom_paste_from_zip(out_dir / GERBER_ZIP),
    )
    print(
        f"fab_check: board {board}"
    )  # no package path: the report is part of a reproducible package
    for r in results:
        print(f"{'PASS' if r.ok else 'FAIL'} {r.name}: {r.detail}")
    print("missing LCSC numbers:")
    print("\n".join(lcsc_lines) or "  none")
    failed = [r.name for r in results if not r.ok]
    print("RESULT: " + (f"FAIL ({', '.join(failed)})" if failed else "PASS"))
    return 1 if failed else 0


def main(argv: Sequence[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("out_dir", nargs="?")
    p.add_argument("board", nargs="?")
    p.add_argument("--allow-missing-lcsc", default="", metavar="REF,...")
    p.add_argument("--missing-lcsc-file", default=None, metavar="FILE")
    p.add_argument("--owner-waiver-file", default=None, metavar="FILE")
    p.add_argument("--compare", nargs=2, metavar=("DIR1", "DIR2"))
    args = p.parse_args(argv)
    try:
        if args.compare:
            diffs = compare_dirs(Path(args.compare[0]), Path(args.compare[1]))
            for line in diffs:
                print(line)
            print("COMPARE: " + ("equal" if not diffs else f"{len(diffs)} difference(s)"))
            return 1 if diffs else 0
        if not args.out_dir or not args.board:
            p.error("give <out dir> <board> or --compare <dir1> <dir2>")
        return _check_main(args)
    except InputError as exc:
        print(f"fab_check: NOT RUN: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
