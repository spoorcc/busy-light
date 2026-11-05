# SPDX-License-Identifier: Apache-2.0
"""Strict ERC/DRC runner for the spike: a violation fails the run (HW generated-design guardrails).

Usage: kicad_strict.py erc <file.kicad_sch> <profile> [--out report.json]
       kicad_strict.py drc <file.kicad_pcb> <profile> [--out report.json]

kicad-cli runs with `--format json --severity-all --exit-code-violations` (ERC) and additionally
`--schematic-parity --refill-zones` (DRC). Every violation, warning and unconnected item counts.

Two modes, chosen by the environment variable SPIKE_ALLOW_KNOWN_OPEN:
  0 (default of this program)  strict: any violation fails.
  1 (default of the run_*.sh scripts while the spike is open)  a violation type is tolerated only
     when `known-open-violations.json` lists it for the profile with a reason and a maximum count;
     a type that is not listed, or a count above the maximum, fails. Tolerated items are printed.
Exit codes: 0 pass, 1 violations not tolerated, 2 kicad-cli did not run or the report is unusable.
The allow-list is a waiver list: changing it needs the owner (see docs/process/hw-generated-design-guardrails.md).
"""

from __future__ import annotations

import collections
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ALLOW_FILE = Path(__file__).resolve().parent.parent / "known-open-violations.json"
VIOLATION_EXIT = 5  # kicad-cli exit code with --exit-code-violations


def run_cli(kind: str, target: Path, out: Path) -> int:
    if kind == "erc":
        cmd = ["kicad-cli", "sch", "erc", "--format", "json", "--severity-all", "--exit-code-violations"]
    else:
        cmd = [
            "kicad-cli", "pcb", "drc", "--format", "json", "--severity-all", "--exit-code-violations",
            "--schematic-parity", "--refill-zones",
        ]  # fmt: skip
    cmd += ["-o", str(out), str(target)]
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)  # noqa: S603
    return res.returncode


def tally(report: dict, kind: str) -> collections.Counter:
    """Count (severity, type) over every list of findings in a KiCad JSON report."""
    c: collections.Counter = collections.Counter()
    lists = [s.get("violations", []) for s in report.get("sheets", [])] if kind == "erc" else []
    if kind == "drc":
        lists = [report.get(k, []) for k in ("violations", "unconnected_items", "schematic_parity")]
        # schematic_parity is an integer count in some versions; ignore non-lists
        lists = [x for x in lists if isinstance(x, list)]
    for items in lists:
        for v in items:
            c[(v["severity"], v["type"])] += 1
    ignored = report.get("ignored_checks", 0)
    ignored = len(ignored) if isinstance(ignored, list) else int(ignored)  # list in ERC, count in DRC
    if ignored:
        c[("ignored", "ignored_checks")] = ignored
    return c


def judge(counts: collections.Counter, allowed: dict[str, dict], strict: bool) -> tuple[int, list[str]]:
    lines: list[str] = []
    bad = 0
    for (sev, typ), n in sorted(counts.items()):
        entry = allowed.get(typ)
        if strict or entry is None:
            lines.append(f"FAIL {sev} {typ}: {n}" + ("" if strict else " (not in allow-list)"))
            bad += 1
        elif n > entry["max"]:
            lines.append(f"FAIL {sev} {typ}: {n} > allowed {entry['max']}")
            bad += 1
        else:
            lines.append(f"tolerated {sev} {typ}: {n} (max {entry['max']}; {entry['reason']})")
    return bad, lines


def main(argv: list[str]) -> int:
    if len(argv) < 3 or argv[0] not in ("erc", "drc"):
        print(__doc__)
        return 2
    kind, target, profile = argv[0], Path(argv[1]), argv[2]
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else None
    strict = os.environ.get("SPIKE_ALLOW_KNOWN_OPEN", "0") != "1"
    with tempfile.TemporaryDirectory() as tmp:
        rpt = out or Path(tmp) / f"{kind}.json"
        rc = run_cli(kind, target, rpt)
        if rc not in (0, VIOLATION_EXIT) or not rpt.exists():
            print(f"{kind.upper()} NOT RUN: kicad-cli exit {rc}")
            return 2
        try:
            report = json.loads(rpt.read_text())
            counts = tally(report, kind)
        except (ValueError, KeyError) as exc:
            print(f"{kind.upper()} NOT RUN: report unusable ({exc})")
            return 2
    allowed = {}
    if not strict:
        allowed = json.loads(ALLOW_FILE.read_text())[kind].get(profile, {})
    bad, lines = judge(counts, allowed, strict)
    total = sum(counts.values())
    # kicad-cli's own exit code must agree with the tally: exit 5 with an empty tally means a parse gap.
    if rc == VIOLATION_EXIT and total == 0:
        print(f"{kind.upper()} FAIL: kicad-cli reported violations but the tally is empty")
        return 1
    print(f"{kind.upper()} {profile}: {total} finding(s), mode={'strict' if strict else 'known-open allow-list'}")
    for line in lines:
        print("  " + line)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
