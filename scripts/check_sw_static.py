#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Judge static-analysis results of the project C code (rules SWC-006, SWC-007, SWC-008).

    check_sw_static.py misra <cppcheck.xml>   SWC-007: cppcheck + MISRA addon results
    check_sw_static.py suppressions           SWC-008: every suppression names a DEV- record
    check_sw_static.py tidy-db <in> <out>     copy of compile_commands.json with the project
                                              files only and no GCC-only flags (for
                                              clang-tidy; the build is not changed)

SWC-007 policy (docs/standards/coding-sw.md 4, ADR-0022 Proposed): a MISRA finding of a Mandatory
or Required rule fails; an Advisory finding is reported. A rule that is not in the table below is
treated as Required. cppcheck findings of severity error or warning fail; style, performance and
portability findings are reported. The category table holds only rule numbers and categories (no
rule texts, which are copyrighted); it was written from the published rule list and must be
checked against the MISRA C:2012 document the project holds (verify). This output is NOT a MISRA
compliance report: cppcheck covers part of the rules only.
"""

from __future__ import annotations

import json
import re
import shlex
import sys
import xml.etree.ElementTree as ET  # noqa: N817 - the input is cppcheck's own report file
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
PROJECT_CODE = ("sw/app", "sw/drivers", "sw/lib")
RULES = {"SWC-006": "gate", "SWC-007": "gate", "SWC-008": "gate"}

MANDATORY = {
    "9.1", "12.5", "13.6", "17.3", "17.4", "17.6", "19.1", "21.13", "21.17", "21.18", "21.19",
    "21.20", "22.2", "22.4", "22.5", "22.6",
}  # fmt: skip
ADVISORY = {
    "1.2", "2.3", "2.4", "2.5", "2.6", "2.7", "4.2", "5.9", "8.7", "8.9", "8.11", "8.13", "10.5",
    "11.4", "11.5", "12.1", "12.3", "12.4", "13.3", "13.4", "15.1", "15.4", "15.5", "17.5", "17.8",
    "18.4", "18.5", "19.2", "20.1", "20.5", "20.10", "21.12",
}  # fmt: skip
MISRA_ID = re.compile(r"misra-c2012-(\d+\.\d+)")
FAIL_SEVERITIES = {"error", "warning"}


def category(rule: str) -> str:
    if rule in MANDATORY:
        return "mandatory"
    if rule in ADVISORY:
        return "advisory"
    return "required"


def judge_cppcheck(xml_text: str) -> tuple[list[str], list[str]]:
    """Return (failing, reported) findings as text lines."""
    failing: list[str] = []
    reported: list[str] = []
    if not xml_text.strip():
        return ["SWC-007 cppcheck produced no report (tool error): NOT RUN"], []
    root = ET.fromstring(xml_text)
    for err in root.iter("error"):
        ident = err.get("id", "")
        loc = err.find("location")
        where = f"{loc.get('file')}:{loc.get('line')}" if loc is not None else "?"
        if ident in {"missingIncludeSystem", "checkersReport", "unmatchedSuppression"}:
            continue
        m = MISRA_ID.fullmatch(ident)
        if m:
            cat = category(m.group(1))
            line = f"SWC-007 {where}: MISRA C:2012 rule {m.group(1)} ({cat})"
            (reported if cat == "advisory" else failing).append(line)
            continue
        sev = err.get("severity", "")
        line = f"SWC-007 {where}: cppcheck {sev} {ident}: {err.get('msg', '')}"
        (failing if sev in FAIL_SEVERITIES else reported).append(line)
    return failing, reported


SUPPRESS = re.compile(r"(NOLINT\w*|cppcheck-suppress\w*|#pragma\s+GCC\s+diagnostic\s+ignored)")
DEV_REF = re.compile(r"DEV-\d{3}")


def check_suppressions(files: list[Path]) -> list[str]:
    out = []
    for path in files:
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if SUPPRESS.search(line) and not DEV_REF.search(line):
                rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
                out.append(f"SWC-008 {rel}:{n}: suppression without a DEV-nnn reference")
    return out


GCC_ONLY = re.compile(
    r"^(?:-fno-freestanding|-fno-reorder-functions|-fno-defer-pop|-fno-printf-return-value"
    r"|-fno-tree-switch-conversion|-fno-ipa-sra|--param=.*|-mfp16-format=.*|-fdiagnostics-color=.*"
    r"|-Wno-unused-but-set-variable|-fmacro-prefix-map=.*)$"
)


def clang_compile_db(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep the project files only and drop GCC-only arguments that clang rejects."""
    out: list[dict[str, Any]] = []
    roots = [str(ROOT / d) + "/" for d in PROJECT_CODE]
    for e in entries:
        if not any(e["file"].startswith(r) for r in roots):
            continue
        args = shlex.split(e["command"]) if "command" in e else list(e.get("arguments", []))
        kept = [a for a in args if not GCC_ONLY.match(a)]
        out.append({"directory": e["directory"], "file": e["file"], "arguments": kept})
    return out


def project_sources() -> list[Path]:
    files: list[Path] = []
    for d in PROJECT_CODE:
        base = ROOT / d
        if base.is_dir():
            files += [p for p in base.rglob("*") if p.suffix in {".c", ".h"}]
    return sorted(files)


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[0] == "misra":  # noqa: PLR2004
        failing, reported = judge_cppcheck(Path(argv[1]).read_text(encoding="utf-8"))
        for f in failing:
            print("FAIL " + f)
        for r in reported:
            print("REPORT " + r)
        print(f"cppcheck/MISRA: {len(failing)} failing, {len(reported)} reported (advisory/style)")
        return 1 if failing else 0
    if len(argv) == 3 and argv[0] == "tidy-db":  # noqa: PLR2004
        entries = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
        Path(argv[2]).parent.mkdir(parents=True, exist_ok=True)
        Path(argv[2]).write_text(json.dumps(clang_compile_db(entries), indent=1), encoding="utf-8")
        return 0
    if argv == ["suppressions"]:
        found = check_suppressions(project_sources())
        print("\n".join(found))
        print(f"suppressions: {len(found)} without a deviation reference")
        return 1 if found else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
