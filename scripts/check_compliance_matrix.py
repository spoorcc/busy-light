#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""DOC-001: keep the compliance matrix and the automated-check catalogue consistent.

1. Every SYS/SW/HW/MECH/TC ID in docs/regulatory/compliance-matrix.md is defined in docs/
   (IDs ending in -000 are the example rows of the template and are skipped).
2. Every requirement whose 'Regulatory:' field names a legal act or standard (not none or TBD)
   appears in at least one matrix row (Regulatory README section 1, step 2).
3. Every check rule ID (HWC-, SWC-, DOC-) in the matrix is in the catalogue.
4. The catalogue table in docs/regulatory/automated-checks.md and the RULES tables of the
   checker scripts list the same rules with the same severity.
Exit 1 on any finding.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_ci_supply_chain  # noqa: E402
import check_hw_compliance  # noqa: E402
import check_kconfig_policy  # noqa: E402
import check_sbom  # noqa: E402
import check_secrets  # noqa: E402
import check_sw_static  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
MATRIX = DOCS / "regulatory" / "compliance-matrix.md"
CATALOGUE = DOCS / "regulatory" / "automated-checks.md"
REQ_ID = re.compile(r"\b(?:SYS|SW|HW|MECH|TC)-\d{3}\b")
RULE_ID = re.compile(r"\b(?:HWC|SWC|DOC)-\d{3}\b")
DEF_RE = re.compile(r"^#{1,4}\s+((?:NEED|SYS|SW|HW|MECH|ARCH|RISK|TC)-\d{3})\b")
REG_FIELD = re.compile(r"^-\s+\*\*Regulatory:\*\*\s*(.*)$")
NOT_REGULATORY = re.compile(r"^(?:none|tbd|n/a|-)\b", re.I)
OWN_RULES = {"DOC-001": "gate"}


def code_rules() -> dict[str, str]:
    rules = {r.id: r.severity for r in check_hw_compliance.RULES.values()}
    for mod in (check_kconfig_policy, check_secrets, check_ci_supply_chain, check_sw_static):
        rules.update(mod.RULES)
    rules.update(check_sbom.RULES)
    rules.update(OWN_RULES)
    return rules


def definitions_and_regulatory() -> tuple[set[str], dict[str, str]]:
    defs: set[str] = set()
    regulatory: dict[str, str] = {}
    for path in sorted(DOCS.rglob("*.md")):
        if path.relative_to(DOCS).parts[0] == "templates":
            continue
        cur = None
        for line in path.read_text(encoding="utf-8").splitlines():
            m = DEF_RE.match(line)
            if m:
                cur = m.group(1)
                defs.add(cur)
                continue
            r = REG_FIELD.match(line)
            if r and cur and cur.split("-")[0] in {"SYS", "SW", "HW", "MECH"}:
                value = r.group(1).strip()
                if value and not NOT_REGULATORY.match(value):
                    regulatory[cur] = value
    return defs, regulatory


def table_rows(text: str) -> list[str]:
    return [
        ln
        for ln in text.splitlines()
        if ln.startswith("|") and not re.match(r"^\|[\s|:-]+\|?$", ln)
    ]


def catalogue_rules(text: str) -> dict[str, str]:
    out = {}
    for row in table_rows(text):
        cells = [c.strip() for c in row.strip("|").split("|")]
        if cells and RULE_ID.fullmatch(cells[0]) and len(cells) > 2:  # noqa: PLR2004
            out[cells[0]] = cells[2]
    return out


def check(matrix: str, catalogue: str, defs: set[str], regulatory: dict[str, str]) -> list[str]:
    findings = []
    rows = table_rows(matrix)
    matrix_req_ids: set[str] = set()
    matrix_rule_ids: set[str] = set()
    for row in rows:
        for i in REQ_ID.findall(row):
            if i.endswith("-000"):
                continue
            matrix_req_ids.add(i)
            if i not in defs:
                findings.append(f"DOC-001 compliance-matrix.md: {i} is not defined in docs/")
        matrix_rule_ids |= set(RULE_ID.findall(row))
    for req, value in sorted(regulatory.items()):
        if req not in matrix_req_ids:
            findings.append(
                f"DOC-001 {req} has 'Regulatory: {value[:60]}' but no compliance-matrix row"
            )
    cat = catalogue_rules(catalogue)
    for rid in sorted(matrix_rule_ids - set(cat)):
        findings.append(f"DOC-001 compliance-matrix.md: check {rid} is not in automated-checks.md")
    code = code_rules()
    for rid in sorted(set(cat) | set(code)):
        if rid not in code:
            findings.append(f"DOC-001 automated-checks.md: {rid} has no checker code")
        elif rid not in cat:
            findings.append(f"DOC-001 {rid} is in the checker code but not in automated-checks.md")
        elif cat[rid] != code[rid]:
            findings.append(
                f"DOC-001 {rid}: severity '{cat[rid]}' in the catalogue, '{code[rid]}' in code"
            )
    return findings


def main() -> int:
    defs, regulatory = definitions_and_regulatory()
    findings = check(
        MATRIX.read_text(encoding="utf-8"),
        CATALOGUE.read_text(encoding="utf-8"),
        defs,
        regulatory,
    )
    print("\n".join(findings))
    print(f"compliance matrix: {len(regulatory)} regulatory requirements, {len(findings)} findings")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
