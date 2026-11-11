#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check Zephyr Kconfig files against the security policy in sw/kconfig-policy.yaml.

SWC-001 (gate): no forbidden option is 'y' in a product config fragment or in a built .config.
SWC-002 (report): required hardening options that are not 'y' are listed.

Usage:
    python3 -I scripts/check_kconfig_policy.py                 # config fragments in the repo
    python3 -I scripts/check_kconfig_policy.py --dotconfig build/zephyr/.config
"""

from __future__ import annotations

import argparse
import fnmatch
import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
POLICY = ROOT / "sw" / "kconfig-policy.yaml"
RULES = {"SWC-001": "gate", "SWC-002": "report"}
SET_RE = re.compile(r"^\s*(CONFIG_[A-Za-z0-9_]+)\s*=\s*(.*?)\s*$")
UNSET_RE = re.compile(r"^\s*#\s*(CONFIG_[A-Za-z0-9_]+) is not set")


def parse_config(text: str) -> dict[str, str]:
    """Return option -> value. '# CONFIG_X is not set' gives 'n'. Later lines win, as in Kconfig."""
    values: dict[str, str] = {}
    for line in text.splitlines():
        m = SET_RE.match(line)
        if m:
            values[m.group(1)] = m.group(2).strip('"')
            continue
        u = UNSET_RE.match(line)
        if u:
            values[u.group(1)] = "n"
    return values


def in_scope(rel: str, policy: dict[str, Any]) -> bool:
    if any(fnmatch.fnmatch(rel, pat) for pat in policy.get("exclude", [])):
        return False
    return any(fnmatch.fnmatch(rel, pat) for pat in policy.get("product_configs", []))


def check(values: dict[str, str], where: str, policy: dict[str, Any], full: bool) -> list[str]:
    """Findings as 'SWC-00x <where>: text'. 'full' marks a built .config (all options present)."""
    out = []
    for opt, why in (policy.get("forbidden") or {}).items():
        if values.get(opt) == "y":
            out.append(f"SWC-001 {where}: {opt}=y is forbidden ({why})")
    if full:
        for opt, why in (policy.get("required") or {}).items():
            if values.get(opt) != "y":
                out.append(f"SWC-002 {where}: {opt} is not set ({why})")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--policy", type=Path, default=POLICY)
    ap.add_argument("--dotconfig", type=Path, action="append", default=[])
    args = ap.parse_args(argv)
    policy = yaml.safe_load(args.policy.read_text(encoding="utf-8"))
    findings: list[str] = []
    fragments = sorted(
        p for p in (ROOT / "sw").rglob("*.conf") if in_scope(str(p.relative_to(ROOT)), policy)
    )
    merged: dict[str, str] = {}
    for p in fragments:
        values = parse_config(p.read_text(encoding="utf-8"))
        merged.update(values)
        findings += check(values, str(p.relative_to(ROOT)), policy, full=False)
    if not args.dotconfig:
        # Without a build, SWC-002 is judged on the merged fragments (an option may still come
        # from a board default; the built .config is the authoritative input).
        findings += [
            f.replace("SWC-002 merged", "SWC-002 fragments")
            for f in check(merged, "merged", policy, full=True)
            if f.startswith("SWC-002")
        ]
    for dc in args.dotconfig:
        findings += check(parse_config(dc.read_text(encoding="utf-8")), str(dc), policy, True)
    for f in findings:
        print(("FAIL " if f.startswith("SWC-001") else "REPORT ") + f)
    gate = [f for f in findings if f.startswith("SWC-001")]
    print(
        f"kconfig policy: {len(fragments)} fragments, {len(args.dotconfig)} built configs, "
        f"{len(gate)} forbidden, {len(findings) - len(gate)} hardening options reported"
    )
    return 1 if gate else 0


if __name__ == "__main__":
    sys.exit(main())
