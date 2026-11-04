"""Regression tests for scripts/check_docs_style.py."""

from pathlib import Path

import check_docs_style as cds


def test_long_step_is_reported(tmp_path: Path) -> None:
    doc = tmp_path / "a.md"
    doc.write_text("1. " + " ".join(["word"] * 25) + "\n", encoding="utf-8")
    assert any("step has 25 words" in f for f in cds.check(doc))


def test_contraction_is_reported(tmp_path: Path) -> None:
    doc = tmp_path / "b.md"
    doc.write_text("Do not press it. It doesn't work.\n", encoding="utf-8")
    assert any("contraction" in f for f in cds.check(doc))


def test_clean_text_has_no_findings(tmp_path: Path) -> None:
    doc = tmp_path / "c.md"
    doc.write_text("1. Press the button.\n", encoding="utf-8")
    assert cds.check(doc) == []
