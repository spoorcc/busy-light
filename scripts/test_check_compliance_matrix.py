# SPDX-License-Identifier: Apache-2.0
"""Tests for check_compliance_matrix.py (DOC-001)."""

from __future__ import annotations

import check_compliance_matrix as cm

MATRIX = """| Legal | Req | ID | TC | Evidence | Status |
|---|---|---|---|---|---|
| CRA x | y | SW-000 | TC-000 | -- | Open |
| RED x | y | HW-018 | TC-218; HWC-001 | -- | Open |
| RED y | y | HW-999 | SWC-077 | -- | Open |
"""


def catalogue(rows: dict[str, str]) -> str:
    head = "| Rule | Check | Severity | Basis | Script | Job |\n|---|---|---|---|---|---|\n"
    return head + "".join(f"| {r} | c | {s} | b | s | j |\n" for r, s in rows.items())


def test_matrix_ids_regulatory_coverage_and_rule_ids() -> None:
    code = cm.code_rules()
    findings = cm.check(
        MATRIX,
        catalogue(code),
        defs={"HW-018", "TC-218", "SYS-001"},
        regulatory={"HW-018": "RED", "SYS-001": "CRA"},
    )
    assert any("HW-999 is not defined" in f for f in findings)
    assert any("SYS-001 has 'Regulatory" in f for f in findings)
    assert any("SWC-077 is not in automated-checks.md" in f for f in findings)
    assert not any("-000" in f for f in findings)  # template rows are skipped
    assert len(findings) == 3  # noqa: PLR2004


def test_catalogue_and_code_must_agree() -> None:
    code = cm.code_rules()
    cat = dict(code)
    cat["HWC-001"] = "report"  # wrong severity
    del cat["SWC-003"]  # missing in the catalogue
    cat["SWC-099"] = "gate"  # no code
    findings = cm.check("", catalogue(cat), set(), {})
    assert any("HWC-001: severity" in f for f in findings)
    assert any("SWC-003 is in the checker code" in f for f in findings)
    assert any("SWC-099 has no checker code" in f for f in findings)


def test_regulatory_field_filter() -> None:
    assert cm.NOT_REGULATORY.match("none")
    assert cm.NOT_REGULATORY.match("TBD")
    assert cm.NOT_REGULATORY.match("none (USB 2.0 conformance)")
    assert not cm.NOT_REGULATORY.match("RED Art. 3(2)")


def test_repository_is_consistent() -> None:
    assert cm.main() == 0
