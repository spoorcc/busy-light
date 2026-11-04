# SPDX-License-Identifier: Apache-2.0
"""Tests for check_license_map: a code file under the CC licence is reported."""

from check_license_map import is_code, violations


def _f(path: str, lic: str) -> dict[str, object]:
    return {"path": path, "spdx_expressions": [{"value": lic}]}


def test_code_under_cc_is_reported() -> None:
    files = [_f("hw/sim/run.py", "CC-BY-NC-SA-4.0"), _f("docs/a.md", "CC-BY-NC-SA-4.0")]
    assert violations(files) == ["hw/sim/run.py"]


def test_code_under_apache_passes() -> None:
    assert violations([_f("scripts/x.py", "Apache-2.0")]) == []


def test_code_detection() -> None:
    assert is_code("sw/app/CMakeLists.txt")
    assert is_code("a/b/test.sh")
    assert not is_code("docs/README.md")
