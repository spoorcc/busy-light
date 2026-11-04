#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fail when a code file falls under the documentation licence (ADR-0013, RV-005 finding L8).

REUSE.toml gives code paths Apache-2.0 and everything else CC BY-NC-SA 4.0. A code file in an
unlisted folder silently becomes CC BY-NC-SA. This check reads `reuse lint --json` and lists them.
Usage: check_license_map.py   (needs the `reuse` tool; exit 1 when a code file has the CC licence)
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import PurePosixPath
from typing import Any

CODE_SUFFIXES = {".py", ".sh", ".c", ".h", ".cmake", ".overlay", ".conf", ".yml", ".yaml"}
CODE_NAMES = {"CMakeLists.txt", "Kconfig", "west.yml"}
DOC_LICENCE = "CC-BY-NC-SA-4.0"
# Files with a code-like suffix that are data or documentation (add with a reason).
ALLOW: set[str] = set()


def is_code(path: str) -> bool:
    p = PurePosixPath(path)
    return p.suffix in CODE_SUFFIXES or p.name in CODE_NAMES


def violations(files: list[dict[str, Any]]) -> list[str]:
    """Return paths of code files whose licence expression is the documentation licence."""
    bad = []
    for f in files:
        path = f["path"]
        if path in ALLOW or not is_code(path):
            continue
        licences = {e["value"] for e in f.get("spdx_expressions", [])}
        if DOC_LICENCE in licences:
            bad.append(path)
    return sorted(bad)


def main() -> int:
    out = subprocess.run(  # noqa: S603 (fixed argument list, no shell)
        ["reuse", "lint", "--json"],  # noqa: S607
        capture_output=True,
        text=True,
        check=False,
    )
    files = json.loads(out.stdout)["files"]
    bad = violations(files)
    for path in bad:
        print(f"code file under {DOC_LICENCE}: {path}")
    if bad:
        print(
            "ERROR: add the path to REUSE.toml (Apache-2.0) or to ALLOW with a reason",
            file=sys.stderr,
        )
        return 1
    print("license map: every code file is outside the documentation licence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
