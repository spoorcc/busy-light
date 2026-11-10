#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""SWC-009: summarise the SPDX tag-value SBOM that `west spdx` writes.

Usage: python3 -I scripts/check_sbom.py <dir with *.spdx> [--json out.json]

Fails (exit 1) when no SPDX document is found or a document has no package: then the SBOM step
did not work. Packages and files without a licence (NOASSERTION or NONE) are reported, not failed:
SYS-044 asks for a licence on every component, and the gap is open evidence until SYS-044 is
Approved and the tooling fills it (ADR-0022). Basis: CRA Annex I Part II (1) (verify); SYS-044.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

NO_LICENCE = {"NOASSERTION", "NONE", ""}
RULES = {"SWC-009": "report"}


@dataclass
class DocSummary:
    name: str
    packages: int = 0
    packages_without_licence: list[str] = field(default_factory=list)
    files: int = 0
    files_without_licence: int = 0
    files_without_sha256: int = 0


def summarise(name: str, text: str) -> DocSummary:
    s = DocSummary(name)
    pkg = ""
    pkg_lic: set[str] = set()
    in_file = False
    file_lic: set[str] = set()
    file_sha = False

    def close_pkg() -> None:
        nonlocal pkg, pkg_lic
        if pkg and pkg_lic <= NO_LICENCE:
            s.packages_without_licence.append(pkg)
        pkg, pkg_lic = "", set()

    def close_file() -> None:
        nonlocal in_file, file_lic, file_sha
        if in_file:
            if file_lic <= NO_LICENCE:
                s.files_without_licence += 1
            if not file_sha:
                s.files_without_sha256 += 1
        in_file, file_lic, file_sha = False, set(), False

    for raw in text.splitlines():
        key, _, value = raw.partition(":")
        value = value.strip()
        if key == "PackageName":
            close_file()
            close_pkg()
            pkg = value
            s.packages += 1
        elif key in {"PackageLicenseConcluded", "PackageLicenseDeclared"}:
            pkg_lic.add(value)
        elif key == "FileName":
            close_file()
            in_file = True
            s.files += 1
        elif key in {"LicenseConcluded", "LicenseInfoInFile"} and in_file:
            file_lic.add(value)
        elif key == "FileChecksum" and value.startswith("SHA256"):
            file_sha = True
    close_file()
    close_pkg()
    return s


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("spdx_dir", type=Path)
    ap.add_argument("--json", type=Path)
    args = ap.parse_args(argv)
    docs = sorted(args.spdx_dir.glob("*.spdx"))
    if not docs:
        print(f"SWC-009 FAIL: no *.spdx in {args.spdx_dir}")
        return 1
    sums = [summarise(d.name, d.read_text(encoding="utf-8")) for d in docs]
    for s in sums:
        print(
            f"SWC-009 {s.name}: {s.packages} packages ({len(s.packages_without_licence)} without "
            f"licence), {s.files} files ({s.files_without_licence} without licence, "
            f"{s.files_without_sha256} without SHA-256)"
        )
    if args.json:
        args.json.write_text(json.dumps([asdict(s) for s in sums], indent=2) + "\n", "utf-8")
    empty = [s.name for s in sums if s.packages == 0]
    if empty:
        print(f"SWC-009 FAIL: documents without a package: {', '.join(empty)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
