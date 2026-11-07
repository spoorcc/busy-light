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
ALLOW: set[str] = {
    # Datasheet evidence data (HW-012, ADR-0017): repository-authored data with short vendor quotes,
    # treated as documentation (CC-BY-NC-SA-4.0). Owner/lawyer to confirm; see consolidation report.
    "hw/evidence/parts/2n7002.yaml",
    "hw/evidence/parts/74lvc1g02.yaml",
    "hw/evidence/parts/capacitors.yaml",
    "hw/evidence/parts/esp32-c3-mini-1.yaml",
    "hw/evidence/parts/reg-3v3.yaml",
    "hw/evidence/parts/resistors.yaml",
    "hw/evidence/parts/sn74ahct1g125.yaml",
    "hw/evidence/parts/sn74lvc1g04.yaml",
    "hw/evidence/parts/sn74lvc1g11.yaml",
    "hw/evidence/parts/sn74lvc1g125.yaml",
    "hw/evidence/parts/sw-tl3342.yaml",
    "hw/evidence/parts/test-point.yaml",
    "hw/evidence/parts/tlv75733p.yaml",
    "hw/evidence/parts/tmux1101.yaml",
    "hw/evidence/parts/tps2553.yaml",
    "hw/evidence/parts/tps3840dl40.yaml",
    "hw/evidence/parts/tusb321.yaml",
    "hw/evidence/parts/tvs-sod323.yaml",
    "hw/evidence/parts/usb-c-receptacle.yaml",
    "hw/evidence/parts/usblc6-2p6.yaml",
    "hw/evidence/parts/ws2812b.yaml",
    "hw/evidence/schema/part-evidence.schema.json",
}


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
