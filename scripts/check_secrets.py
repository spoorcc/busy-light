#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""SWC-003: find hard-coded credentials and private keys in tracked files.

Basis: CRA Annex I Part I (2)(b) secure by default and (2)(d) protection from unauthorised access
(verify clause letters); EN 18031-1 and ETSI EN 303 645 provision 5.1 (no universal default
passwords); SYS-013, SYS-016; docs/standards/coding-sw.md 4a.

It scans the files that git tracks. A line that must stay (for example a documented test vector)
carries the marker 'secret-scan: allow DEV-nnn' with a deviation record. This is a pattern scan:
it finds common mistakes and does not prove that no secret is present.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALLOW = re.compile(r"secret-scan:\s*allow\s+DEV-\d{3}")
MAX_BYTES = 2_000_000
RULES = {"SWC-003": "gate"}

PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("private key block", re.compile(r"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    ("AWS access key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b")),
    (
        "Kconfig secret value",
        re.compile(
            r"\bCONFIG_\w*(?:PASSWORD|PASSPHRASE|PSK|SECRET|TOKEN|API_KEY)\w*\s*=\s*\"[^\"]+\""
        ),
    ),
    (
        "C string credential",
        re.compile(
            r"\b\w*(?:password|passwd|passphrase|psk|secret|api_?key|token)\w*\s*(?:\[\s*\d*\s*\])?"
            r"\s*=\s*\"[^\"]{4,}\"",
            re.I,
        ),
    ),
]
C_LIKE = {".c", ".h", ".conf", ".overlay", ".dts", ".dtsi", ".cpp"}


def scan_text(text: str, suffix: str) -> list[tuple[int, str]]:
    hits = []
    for n, line in enumerate(text.splitlines(), 1):
        if ALLOW.search(line):
            continue
        for name, pat in PATTERNS:
            if name == "C string credential" and suffix not in C_LIKE:
                continue
            if pat.search(line):
                hits.append((n, name))
                break  # one finding per line
    return hits


def tracked_files() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
    ).stdout.decode()
    return [ROOT / p for p in out.split("\0") if p]


def main(argv: list[str] | None = None) -> int:
    files = [Path(a) for a in argv] if argv else tracked_files()
    findings = []
    for path in files:
        try:
            if path.stat().st_size > MAX_BYTES:
                continue
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
            continue
        for n, name in scan_text(text, path.suffix):
            findings.append(
                f"SWC-003 {path.relative_to(ROOT) if path.is_absolute() else path}:{n}: {name}"
            )
    print("\n".join(findings))
    print(f"secret scan: {len(files)} files, {len(findings)} findings")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
