#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the part-evidence files in hw/evidence/parts/ (see hw/evidence/README.md).

Always run: JSON Schema (draft 2020-12), unique ids, id prefix, document references, units
(pint), min <= typ <= max, the 'verified' rule, quote shape (one sentence or one table row),
formula syntax.
Run when the datasheets folder exists (BUSY_LIGHT_DATASHEETS or the default path): SHA-256 of each
document, page count, and that each quote occurs on the cited page. Otherwise these checks are
reported as NOT RUN, never as passed.
Run when --netlist is given: every 'used_in' reference exists in the KiCad netlist; the pin table
is compared with the pins of each reference (report; use --fail-on-pin-mismatch to fail on it).

Exit status: 0 no errors, 1 errors found, 2 a required tool is missing (reported as NOT RUN).
Command: python3 scripts/check_part_evidence.py [--netlist PATH] [--evidence-dir DIR]
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

import part_evidence as pe

QUOTE_MAX = 300
FUNCTIONS = {"ln", "log", "exp", "sqrt"}
SENTENCE_END = re.compile(r"[.!?]\s+[A-Z]")
DASHES = dict.fromkeys(map(ord, "‐‑‒–—−"), "-")


def normalise(text: str) -> str:
    """Normalise text for the quote search: NFKC, ASCII dashes and quotes, one space."""
    text = unicodedata.normalize("NFKC", text).translate(DASHES).replace("­", "")
    text = text.replace("’", "'").replace("“", '"').replace("”", '"')
    return " ".join(text.split())


class Report:
    """Collects findings; errors make the exit status 1."""

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.notes: list[str] = []

    def error(self, where: str, msg: str) -> None:
        self.errors.append(f"ERROR {where}: {msg}")

    def note(self, msg: str) -> None:
        self.notes.append(f"NOTE  {msg}")


def load_schema() -> dict[str, Any]:
    return json.loads(pe.SCHEMA_PATH.read_text(encoding="utf-8"))  # type: ignore[no-any-return]


def schema_errors(validator_cls: Any, schema: dict[str, Any], ref: str, data: Any) -> list[str]:
    """Errors of ``data`` against a definition of the schema (ref is a '#/$defs/..' pointer)."""
    validator = validator_cls(schema if ref == "#" else {"$ref": ref, "$defs": schema["$defs"]})
    out = []
    for err in sorted(validator.iter_errors(data), key=lambda e: list(map(str, e.path))):
        path = "/".join(str(p) for p in err.absolute_path)
        out.append(f"{path or '<root>'}: {err.message[:200]}")
    return out


def check_unit(ureg: Any, unit: str) -> str | None:
    """Return an error text when pint cannot parse the unit."""
    try:
        ureg.Unit(unit)
    except Exception as exc:  # noqa: BLE001 - pint raises several error types
        return f"unit '{unit}' is not parseable by pint ({type(exc).__name__})"
    return None


def check_formula(entry: dict[str, Any]) -> list[str]:
    """The expression must parse and use only its declared variables and plain arithmetic."""
    formula = entry.get("formula")
    if not formula:
        return []
    try:
        tree = ast.parse(formula["expression"], mode="eval")
    except SyntaxError:
        return [f"formula expression '{formula['expression']}' is not valid"]
    allowed = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Name, ast.Load, ast.Call)
    allowed_ops = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.USub, ast.UAdd)
    out = []
    funcs = {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and not (isinstance(node.func, ast.Name) and node.func.id in FUNCTIONS):
            out.append("formula calls a function; only ln, log, exp and sqrt are allowed")
        elif isinstance(node, ast.Name):
            if node.id in funcs and node.id in FUNCTIONS:
                continue
            if node.id not in formula["variables"]:
                out.append(f"formula uses undeclared variable '{node.id}'")
        elif not isinstance(node, allowed + allowed_ops):
            out.append(f"formula uses {type(node).__name__}; only arithmetic is allowed")
    return out


def semantic_errors(item: dict[str, Any], ureg: Any) -> list[str]:
    """Checks that JSON Schema cannot express."""
    out: list[str] = []
    values = [item.get(k) for k in ("min", "typ", "max")]
    present = [v for v in values if v is not None]
    if present != sorted(present):
        out.append(f"min <= typ <= max violated ({values})")
    if "unit" in item and (err := check_unit(ureg, item["unit"])):
        out.append(err)
    for key, val in (item.get("condition") or {}).items():
        if isinstance(val, dict) and (err := check_unit(ureg, val["unit"])):
            out.append(f"condition '{key}': {err}")
    formula = item.get("formula")
    if formula:
        for var, unit in formula["variables"].items():
            if err := check_unit(ureg, unit):
                out.append(f"formula variable '{var}': {err}")
        if err := check_unit(ureg, formula["unit"]):
            out.append(f"formula: {err}")
    out.extend(check_formula(item))
    if item.get("status") == "verified":
        v_by, e_by = item.get("verified_by"), item.get("extracted_by")
        if v_by and e_by and v_by.get("kind") != "human" and v_by == e_by:
            out.append("status verified: verified_by equals extracted_by and is not a human")
        if v_by and e_by and v_by.get("kind") != "human" and v_by.get("name") == e_by.get("name"):
            out.append("status verified: an AI verifier must have a different name from the extractor")
        if item.get("method") == "extracted" and not v_by:
            out.append("status verified without verified_by")
    elif item.get("verified_by") and item.get("status") in ("unverified", "source-missing"):
        out.append(f"verified_by is set but status is '{item['status']}'")
    quote = (item.get("source") or {}).get("quote")
    if quote:
        if "\n" in quote:
            out.append("quote has a line break (one sentence or one table row on one line)")
        if SENTENCE_END.search(quote):
            out.append("quote looks like more than one sentence (limit: one sentence or one row)")
        if len(quote) > QUOTE_MAX:
            out.append(f"quote has {len(quote)} characters (limit {QUOTE_MAX})")
    return out


class Datasheets:
    """Access to the vendor documents outside the repository."""

    def __init__(self, folder: Path) -> None:
        self.folder = folder
        self.have_tool = shutil.which("pdftotext") is not None
        self._pages: dict[tuple[str, int], str] = {}
        self._hashes: dict[str, str] = {}

    @property
    def available(self) -> bool:
        return self.folder.is_dir()

    def sha256(self, name: str) -> str | None:
        path = self.folder / name
        if not path.is_file():
            return None
        if name not in self._hashes:
            self._hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        return self._hashes[name]

    def page_text(self, name: str, page: int) -> str | None:
        key = (name, page)
        if key not in self._pages:
            texts = []
            for mode in ("-layout", "-raw"):
                res = subprocess.run(
                    ["pdftotext", mode, "-f", str(page), "-l", str(page), str(self.folder / name), "-"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if res.returncode != 0:
                    return None
                texts.append(normalise(res.stdout))
            self._pages[key] = "\n".join(texts)
        return self._pages[key]

    def page_count(self, name: str) -> int | None:
        res = subprocess.run(
            ["pdfinfo", str(self.folder / name)], capture_output=True, text=True, check=False
        )
        m = re.search(r"^Pages:\s+(\d+)", res.stdout, re.M)
        return int(m.group(1)) if m else None


def check_documents(
    where: str, docs: list[dict[str, Any]], ds: Datasheets, rep: Report, stats: Counter[str]
) -> None:
    for doc in docs:
        name = doc["file"]
        digest = ds.sha256(name)
        if digest is None:
            rep.error(where, f"document '{doc['id']}': file {name} not found in {ds.folder}")
            continue
        stats["documents_hash_checked"] += 1
        if digest != doc["sha256"]:
            rep.error(where, f"document '{doc['id']}': sha256 differs (file {digest})")
        pages = doc.get("pages")
        if pages and ds.have_tool and ds.page_count(name) != pages:
            rep.error(where, f"document '{doc['id']}': page count differs from 'pages: {pages}'")


def check_quote(
    where: str, item: dict[str, Any], ds: Datasheets, docs: dict[str, dict[str, Any]],
    rep: Report, stats: Counter[str]
) -> None:
    src = item.get("source")
    if not src or src.get("document") not in docs:
        return
    text = ds.page_text(docs[src["document"]]["file"], src["page"])
    if text is None:
        rep.error(where, f"{item['id']}: page {src['page']} cannot be read (page out of range?)")
        return
    stats["quotes_checked"] += 1
    if normalise(src["quote"]) not in text:
        rep.error(where, f"{item['id']}: quote not found on PDF page {src['page']}")


def parse_netlist(path: Path) -> dict[str, set[tuple[str, str]]]:
    """Map reference -> {(pin, pin function)} from a KiCad netlist (S-expression text)."""
    text = path.read_text(encoding="utf-8")
    refs = set(re.findall(r'\(comp\s+\(ref "([^"]+)"\)', text))
    pins: dict[str, set[tuple[str, str]]] = {r: set() for r in refs}
    for m in re.finditer(
        r'\(node\s+\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)(?:\s+\(pinfunction "([^"]*)"\))?', text
    ):
        pins.setdefault(m.group(1), set()).add((m.group(2), m.group(3) or ""))
    return pins


def pin_report(
    data: dict[str, Any], pins_by_ref: dict[str, set[tuple[str, str]]], lines: list[str]
) -> int:
    """Compare the part's pin table with each used reference. Returns the mismatch count."""
    part = data["part"]
    code = (part.get("package") or {}).get("code")
    table = [p for k, p in pe.resolved_items(data) if k == "pin" and p.get("pin")]
    table = [p for p in table if p.get("package") == code and p.get("name")]
    if not table:
        return 0
    mismatches = 0
    for ref in part["used_in"]:
        net_pins = pins_by_ref.get(ref)
        if net_pins is None:
            continue
        known = {p["pin"] for p in table} | {p["name"] for p in table}
        in_net = {pin for pin, _fn in net_pins}
        for pin, fn in sorted(net_pins):
            if pin not in known:
                mismatches += 1
                lines.append(f"  {ref}: netlist pin '{pin}' ({fn}) is not in the {part['mpn']} table")
        missing = [p["pin"] for p in table if p["pin"] not in in_net and p["name"] not in in_net]
        if missing:
            lines.append(f"  {ref}: table pins not in the netlist: {', '.join(sorted(missing))}")
    return mismatches


def run(args: argparse.Namespace) -> int:  # noqa: PLR0912, PLR0915
    try:
        import jsonschema  # noqa: PLC0415
        import pint  # noqa: PLC0415
    except ImportError as exc:
        print(f"check_part_evidence: NOT RUN - missing package ({exc.name}). "
              "Install with: pip install --group dev", file=sys.stderr)
        return 2
    rep = Report()
    stats: Counter[str] = Counter()
    schema = load_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    ureg = pint.UnitRegistry()
    files = pe.evidence_files(args.evidence_dir)
    if not files:
        rep.error(str(args.evidence_dir or pe.PARTS_DIR), "no *.yaml part files")
    ds = Datasheets(pe.datasheets_dir())
    ids: dict[str, str] = {}
    all_data: list[tuple[Path, dict[str, Any]]] = []

    for path in files:
        where = path.name
        try:
            data = pe.load_yaml(path)
        except (ValueError, Exception) as exc:  # noqa: BLE001 - yaml errors
            rep.error(where, f"cannot load: {exc}")
            continue
        errs = schema_errors(jsonschema.Draft202012Validator, schema, "#", data)
        for e in errs:
            rep.error(where, f"schema: {e}")
        if errs:
            continue
        all_data.append((path, data))
        part = data["part"]
        if path.stem != part["key"].lower():
            rep.error(where, f"file name must be '{part['key'].lower()}.yaml' (part.key)")
        docs = {d["id"]: d for d in data["documents"]}
        if len(docs) != len(data["documents"]):
            rep.error(where, "duplicate document id")
        for item_kind, item in pe.resolved_items(data):
            ref = "#/$defs/resolvedPin" if item_kind == "pin" else "#/$defs/resolvedClaim"
            iid = item.get("id", "?")
            for e in schema_errors(jsonschema.Draft202012Validator, schema, ref, item):
                rep.error(where, f"{iid}: {e}")
            if iid in ids:
                rep.error(where, f"duplicate id {iid} (also in {ids[iid]})")
            ids[iid] = where
            if not iid.startswith(part["key"] + "."):
                rep.error(where, f"{iid}: id must start with '{part['key']}.'")
            src = item.get("source")
            if src and src.get("document") not in docs:
                rep.error(where, f"{iid}: source.document '{src.get('document')}' is not in documents")
            for msg in semantic_errors(item, ureg):
                rep.error(where, f"{iid}: {msg}")
            stats[f"{item_kind}:{item.get('status')}"] += 1
        if ds.available and ds.have_tool:
            check_documents(where, data["documents"], ds, rep, stats)
            for _k, item in pe.resolved_items(data):
                check_quote(where, item, ds, docs, rep, stats)
        part_ids = {i["scheme"] for i in part.get("ids", [])}
        stats["id_schemes"] += len(part_ids)

    # derived_from must point at existing ids
    for path, data in all_data:
        for _k, item in pe.resolved_items(data):
            for dep in item.get("derived_from", []):
                if dep not in ids:
                    rep.error(path.name, f"{item['id']}: derived_from '{dep}' does not exist")

    if not ds.available:
        rep.note(f"NOT RUN: sha256 and quote-on-page checks (no datasheets folder at {ds.folder})")
    elif not ds.have_tool:
        rep.note("NOT RUN: quote-on-page checks (pdftotext not installed); sha256 also skipped")
    else:
        rep.note(f"datasheets folder {ds.folder}: {stats['documents_hash_checked']} document hashes "
                 f"and {stats['quotes_checked']} quotes checked")

    pin_lines: list[str] = []
    if args.netlist:
        if not args.netlist.is_file():
            rep.error(str(args.netlist), "netlist not found")
        else:
            pins_by_ref = parse_netlist(args.netlist)
            mism = 0
            for path, data in all_data:
                for r in data["part"]["used_in"]:
                    if r not in pins_by_ref:
                        rep.error(path.name, f"used_in '{r}' is not in the netlist {args.netlist.name}")
                pin_lines.append(f"{path.name} ({data['part']['mpn']}):")
                before = len(pin_lines)
                mism += pin_report(data, pins_by_ref, pin_lines)
                if len(pin_lines) == before:
                    pin_lines.pop()
            if mism and args.fail_on_pin_mismatch:
                rep.error(args.netlist.name, f"{mism} netlist pin(s) not in the datasheet pin table")
            rep.note(f"netlist {args.netlist.name}: used_in checked; pin mismatches: {mism}")
    else:
        rep.note("NOT RUN: used_in and pin-table checks (no --netlist given)")

    for line in rep.errors + rep.notes:
        print(line)
    if pin_lines:
        print("Pin table vs netlist:")
        print("\n".join(pin_lines))
    summary = ", ".join(f"{k}={v}" for k, v in sorted(stats.items()) if ":" in k)
    print(f"check_part_evidence: {len(files)} files, {len(ids)} ids; {summary or 'no entries'}; "
          f"{len(rep.errors)} error(s)")
    return 1 if rep.errors else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--evidence-dir", type=Path, default=None, help="folder with the part YAML files")
    ap.add_argument("--netlist", type=Path, default=None, help="KiCad .net file for used_in and pins")
    ap.add_argument("--fail-on-pin-mismatch", action="store_true")
    return run(ap.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
