# SPDX-License-Identifier: Apache-2.0
"""Tests for check_sw_static.py (MISRA judging, suppressions, compile db) and check_sbom.py."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import check_sbom as sb
import check_sw_static as ss


def xml(*errors: tuple[str, str]) -> str:
    body = "".join(
        f'<error id="{i}" severity="{s}" msg="m"><location file="a.c" line="3"/></error>'
        for i, s in errors
    )
    return f'<?xml version="1.0"?><results version="2"><errors>{body}</errors></results>'


def test_misra_categories() -> None:
    assert ss.category("9.1") == "mandatory"
    assert ss.category("15.5") == "advisory"
    assert ss.category("8.4") == "required"
    assert ss.category("99.9") == "required"  # unknown rules are treated as Required


def test_judge_advisory_reported_required_fails() -> None:
    failing, reported = ss.judge_cppcheck(
        xml(
            ("misra-c2012-15.5", "style"),
            ("misra-c2012-17.7", "style"),
            ("nullPointer", "error"),
            ("variableScope", "style"),
            ("missingIncludeSystem", "information"),
        )
    )
    assert len(failing) == 2  # noqa: PLR2004
    assert any("17.7 (required)" in f for f in failing)
    assert any("nullPointer" in f for f in failing)
    assert len(reported) == 2  # noqa: PLR2004


def test_empty_cppcheck_output_is_not_a_pass() -> None:
    failing, _ = ss.judge_cppcheck("")
    assert failing
    assert "NOT RUN" in failing[0]


def test_suppressions_need_a_deviation(tmp_path: Path) -> None:
    f = tmp_path / "a.c"
    f.write_text(
        "int a; // NOLINT(cert-x) DEV-002\nint b; /* cppcheck-suppress misra-c2012-8.4 */\n",
        encoding="utf-8",
    )
    found = ss.check_suppressions([f])
    assert len(found) == 1
    assert ":2:" in found[0]


def test_repository_suppressions_pass() -> None:
    assert ss.main(["suppressions"]) == 0


def test_compile_db_keeps_project_files_and_drops_gcc_flags() -> None:
    root = str(ss.ROOT)
    entries: list[dict[str, Any]] = [
        {
            "directory": "/b",
            "file": f"{root}/sw/app/src/main.c",
            "command": "/usr/bin/gcc -DX=1 -fno-freestanding --param=min-pagesize=0 -c main.c",
        },
        {"directory": "/b", "file": f"{root}/zephyr/kernel/init.c", "command": "gcc -c init.c"},
    ]
    out = ss.clang_compile_db(entries)
    assert [e["file"] for e in out] == [f"{root}/sw/app/src/main.c"]
    assert out[0]["arguments"] == ["/usr/bin/gcc", "-DX=1", "-c", "main.c"]


SPDX = """SPDXVersion: SPDX-2.3
PackageName: app-sources
PackageLicenseConcluded: Apache-2.0
FileName: ./main.c
FileChecksum: SHA256: 00
LicenseConcluded: Apache-2.0
PackageName: blob
PackageLicenseConcluded: NOASSERTION
PackageLicenseDeclared: NOASSERTION
FileName: ./blob.bin
LicenseConcluded: NOASSERTION
LicenseInfoInFile: NONE
"""


def test_sbom_summary() -> None:
    s = sb.summarise("x.spdx", SPDX)
    assert s.packages == 2  # noqa: PLR2004
    assert s.packages_without_licence == ["blob"]
    assert s.files == 2  # noqa: PLR2004
    assert s.files_without_licence == 1
    assert s.files_without_sha256 == 1


def test_sbom_missing_or_empty_fails(tmp_path: Path) -> None:
    assert sb.main([str(tmp_path)]) == 1
    (tmp_path / "e.spdx").write_text("SPDXVersion: SPDX-2.3\n", encoding="utf-8")
    assert sb.main([str(tmp_path)]) == 1
    (tmp_path / "e.spdx").write_text(SPDX, encoding="utf-8")
    assert sb.main([str(tmp_path), "--json", str(tmp_path / "s.json")]) == 0
    assert (tmp_path / "s.json").is_file()
