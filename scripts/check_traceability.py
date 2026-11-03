#!/usr/bin/env python3
"""Validate requirement/ADR/risk/test-case traceability under docs/.

Definitions are headings starting with an ID, e.g. '### SW-012 Title'.
Links are bullet fields: '- **Parent:** SYS-003', '- **Verified by:** TC-010', ...
Exit status is non-zero on errors. Use --strict to treat warnings as errors.
"""
import re
import sys
from pathlib import Path

ID = r"(?:NEED|SYS|SW|HW|MECH|ARCH|ADR|RISK|TC)-\d{3,4}"
DEF_RE = re.compile(rf"^#{{1,4}}\s+(?:ADR\s+)?({ID})\b")
FIELD_RE = re.compile(r"^-\s+\*\*([A-Za-z ]+):\*\*\s*(.*)$")
REQ = ("SYS", "SW", "HW", "MECH")
LINK_FIELDS = {"parent", "verified by", "verifies", "mitigated by", "related", "implements"}


def main(strict: bool) -> int:
    root = Path(__file__).resolve().parent.parent / "docs"
    defs: dict[str, str] = {}
    items: dict[str, dict[str, set[str]]] = {}
    errors: list[str] = []
    warnings: list[str] = []
    refs: list[tuple[str, str, str]] = []  # (where, field, id)

    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root)
        if rel.parts[0] == "templates":
            continue
        cur = None
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            m = DEF_RE.match(line)
            if m:
                cur = m.group(1)
                where = f"{rel}:{n}"
                if cur in defs:
                    errors.append(f"{where}: duplicate ID {cur} (also {defs[cur]})")
                defs[cur] = where
                items.setdefault(cur, {})
                continue
            f = FIELD_RE.match(line)
            if f and cur:
                name = f.group(1).strip().lower()
                if name in LINK_FIELDS:
                    ids = set(re.findall(ID, f.group(2)))
                    items[cur].setdefault(name, set()).update(ids)
                    for i in ids:
                        refs.append((f"{rel}:{n}", name, i))

    for where, field, i in refs:
        if i not in defs:
            errors.append(f"{where}: '{field}' references undefined {i}")

    verified_by_tc: set[str] = set()
    for i, d in items.items():
        if i.startswith("TC-"):
            verified_by_tc |= d.get("verifies", set())
            if not d.get("verifies"):
                errors.append(f"{defs[i]}: {i} has no 'Verifies' link")
    for i, d in items.items():
        prefix = i.split("-")[0]
        if prefix in REQ:
            if not d.get("parent"):
                errors.append(f"{defs[i]}: {i} has no 'Parent' (untraceable requirement)")
            if not (d.get("verified by") or i in verified_by_tc):
                warnings.append(f"{defs[i]}: {i} has no verification (TC) yet")
        if prefix == "RISK" and not d.get("mitigated by"):
            warnings.append(f"{defs[i]}: {i} has no mitigation linked")

    for w in warnings:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"{len(defs)} items, {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors or (strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main("--strict" in sys.argv))
