#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Regulatory and DFx rule checks on the KiCad design files (no KiCad installation needed).

These checks add to KiCad's ERC and DRC (scripts/ci_hw.sh). Each one covers a design rule that
EMC, safety or market-access evidence depends on and that ERC/DRC do not check. Each rule names
its basis (standard clause, legal article, project rule). The rule catalogue is in
docs/regulatory/automated-checks.md, and check_compliance_matrix.py keeps it in step with RULES.

Usage:
    python3 -I scripts/check_hw_compliance.py [--config CONFIG.yaml] [--out report.json]
    python3 -I scripts/check_hw_compliance.py --list-rules

Severity "gate": an unwaived finding fails the run. Severity "report": the finding is listed as
evidence of an open item and does not fail the run. Every waiver must match a current finding;
a stale waiver fails the run, so the waiver list cannot hide a fixed or changed item.
Passing these checks is not proof of conformity: it shows that the listed design rules hold for
the files checked.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kicad_sexp  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / "hw" / "compliance" / "boards.yaml"
DEFAULT_MATERIALS = ROOT / "hw" / "compliance" / "materials.yaml"
SERIES_PREFIXES = ("R", "L", "FB")  # a two-pad series part between a net and its clamp
BAD_LIFECYCLE = {"nrnd", "eol", "obsolete"}


@dataclass(frozen=True)
class Rule:
    id: str
    title: str
    severity: str  # gate | report
    basis: str


RULES: dict[str, Rule] = {
    r.id: r
    for r in (
        Rule(
            "HWC-001",
            "Every signal and supply net of an external interface has an ESD or surge clamp",
            "gate",
            "RED Art. 3(1)(b) via EN 301 489-1 (ESD, EN 61000-4-2) and EN 55035; "
            "docs/standards/design-hw.md 3 and 4a; HW-003",
        ),
        Rule(
            "HWC-002",
            "The clamp of an external interface net is near the connector",
            "report",
            "docs/standards/design-hw.md 4 (DFEMC: short clamp path); EN 61000-4-2 practice",
        ),
        Rule(
            "HWC-003",
            "Every power rail has a test point",
            "gate",
            "docs/standards/design-hw.md 1 (DFT); HW-006; production control evidence "
            "(Module A internal production control)",
        ),
        Rule(
            "HWC-004",
            "Reset and boot-mode nets have test access",
            "gate",
            "docs/standards/design-hw.md 1 (DFT); HW-006; SYS-023",
        ),
        Rule(
            "HWC-005",
            "The board carries its name and revision on the silkscreen",
            "gate",
            "docs/standards/design-hw.md 2 and 4a (identification); traceability for "
            "RED Art. 10(6) and GPSR Art. 9 type/batch identification (verify)",
        ),
        Rule(
            "HWC-006",
            "Every BOM part has a manufacturer part number and a manufacturer",
            "gate",
            "EN IEC 63000 (RoHS technical documentation per part); REACH Art. 33; "
            "docs/standards/design-hw.md 5; HW-008",
        ),
        Rule(
            "HWC-007",
            "Every BOM part number has a RoHS and REACH record in the materials register",
            "report",
            "RoHS 2011/65/EU Art. 4 and 7, EN IEC 63000; REACH Art. 33; technical file section 07",
        ),
        Rule(
            "HWC-008",
            "No BOM part is marked not-recommended-for-new-designs or end-of-life",
            "gate",
            "docs/standards/design-hw.md 5 (DFC lifecycle); CRA Art. 13(8) support period (verify)",
        ),
        Rule(
            "HWC-009",
            "Inventory of debug and programming access (to disable or protect in production)",
            "report",
            "CRA Annex I Part I (2)(j) attack surface (verify); EN 18031-1 (verify); "
            "docs/standards/design-hw.md 4a",
        ),
    )
}


@dataclass
class Finding:
    rule: str
    board: str
    item: str
    message: str
    waived_by: str = ""


def _is_unconnected(net: str) -> bool:
    return not net or net.startswith("unconnected-")


def _protected_nets(board: kicad_sexp.Board, protection_refs: list[str]) -> set[str]:
    """Nets that touch a clamp directly or through one two-pad series part."""
    fps = board.by_ref()
    direct: set[str] = set()
    for ref in protection_refs:
        if ref in fps:
            direct |= fps[ref].nets
    extended = set(direct)
    for fp in board.footprints:
        nets = fp.nets
        if fp.ref.startswith(SERIES_PREFIXES) and len(fp.pads) == 2 and len(nets) == 2:  # noqa: PLR2004
            a, b = sorted(nets)
            if a in direct:
                extended.add(b)
            if b in direct:
                extended.add(a)
    return extended


def check_interface_protection(
    name: str, board: kicad_sexp.Board, cfg: dict[str, Any]
) -> list[Finding]:
    fps = board.by_ref()
    exempt = set(cfg.get("exempt_nets", []))
    protection = list(cfg.get("protection_refs", []))
    protected = _protected_nets(board, protection)
    max_mm = float(cfg.get("protection_max_distance_mm", 10.0))
    out: list[Finding] = []
    for ref in cfg.get("external_interfaces", []):
        fp = fps.get(ref)
        if fp is None:
            out.append(Finding("HWC-001", name, ref, f"interface part {ref} is not on the board"))
            continue
        for net in sorted(fp.nets):
            if _is_unconnected(net) or net in exempt:
                continue
            if net not in protected:
                out.append(
                    Finding("HWC-001", name, f"{ref}:{net}", f"net {net} of {ref} has no clamp")
                )
                continue
            clamps = [fps[p] for p in protection if p in fps and net in fps[p].nets]
            if not clamps:
                continue  # protected through a series part; distance is not defined
            near = min(clamps, key=lambda c: math.dist((c.x, c.y), (fp.x, fp.y)))
            dist = math.dist((near.x, near.y), (fp.x, fp.y))
            if dist > max_mm:
                out.append(
                    Finding(
                        "HWC-002",
                        name,
                        f"{ref}:{net}",
                        f"{net}: nearest clamp {near.ref} is {dist:.1f} mm from {ref} "
                        f"(limit {max_mm} mm)",
                    )
                )
    return out


def check_test_access(name: str, board: kicad_sexp.Board, cfg: dict[str, Any]) -> list[Finding]:
    tp_prefix = str(cfg.get("test_point_prefix", "TP"))
    tp_nets: set[str] = set()
    for fp in board.footprints:
        if fp.ref.startswith(tp_prefix):
            tp_nets |= fp.nets
    all_nets = {n for fp in board.footprints for n in fp.nets}
    out: list[Finding] = []
    for net in cfg.get("power_nets", []):
        if net not in all_nets:
            out.append(Finding("HWC-003", name, net, f"power net {net} is not on the board"))
        elif net not in tp_nets:
            out.append(Finding("HWC-003", name, net, f"power net {net} has no test point"))
    for role, net in (cfg.get("access_nets") or {}).items():
        if net not in tp_nets:
            out.append(Finding("HWC-004", name, role, f"{role} net {net} has no test point"))
    return out


def check_board_identity(name: str, board: kicad_sexp.Board, cfg: dict[str, Any]) -> list[Finding]:
    pattern = re.compile(str(cfg.get("board_id_pattern", r"(?i)rev")))
    silk = [t.text for t in board.texts if t.layer.endswith("SilkS")]
    if any(pattern.search(t) for t in silk):
        return []
    return [
        Finding(
            "HWC-005",
            name,
            "silkscreen",
            f"no silkscreen text matches {pattern.pattern!r} ({len(silk)} silkscreen texts)",
        )
    ]


def bom_symbols(symbols: list[kicad_sexp.Symbol]) -> list[kicad_sexp.Symbol]:
    return [s for s in symbols if s.ref and not s.ref.startswith("#") and s.in_bom and not s.dnp]


def check_bom(
    name: str, symbols: list[kicad_sexp.Symbol], materials: dict[str, dict[str, Any]]
) -> list[Finding]:
    out: list[Finding] = []
    for s in sorted(bom_symbols(symbols), key=lambda s: s.ref):
        mpn = s.fields.get("MPN", "").strip()
        if not mpn or not s.fields.get("Manufacturer", "").strip():
            out.append(Finding("HWC-006", name, s.ref, f"{s.ref} has no MPN or manufacturer"))
            continue
        rec = materials.get(mpn)
        if rec is None:
            out.append(Finding("HWC-007", name, mpn, f"{mpn} ({s.ref}) is not in the register"))
            continue
        open_keys = [
            f"{key} {rec.get(key, 'unknown')}"
            for key in ("rohs", "reach")
            if str(rec.get(key, "unknown")) not in {"declared", "exempt-declared"}
        ]
        if open_keys:
            out.append(Finding("HWC-007", name, mpn, f"{mpn}: {', '.join(open_keys)}"))
        if str(rec.get("lifecycle", "unknown")).lower() in BAD_LIFECYCLE:
            out.append(
                Finding(
                    "HWC-008",
                    name,
                    mpn,
                    f"{mpn} ({s.ref}) lifecycle is {rec['lifecycle']} ({rec.get('source', '')})",
                )
            )
    # One HWC-007 or HWC-008 finding per part number, not per reference.
    seen: set[tuple[str, str]] = set()
    unique = []
    for f in out:
        if (f.rule, f.item) not in seen:
            seen.add((f.rule, f.item))
            unique.append(f)
    return unique


def debug_inventory(name: str, board: kicad_sexp.Board, cfg: dict[str, Any]) -> list[Finding]:
    nets = set(cfg.get("debug_nets", []))
    out = []
    for fp in board.footprints:
        hit = sorted(fp.nets & nets)
        if hit and fp.ref not in cfg.get("debug_inventory_skip", []):
            out.append(Finding("HWC-009", name, fp.ref, f"{fp.ref} reaches {', '.join(hit)}"))
    return out


def check_board(cfg: dict[str, Any], materials: dict[str, dict[str, Any]]) -> list[Finding]:
    name = str(cfg["name"])
    board = kicad_sexp.read_board(ROOT / cfg["pcb"])
    findings = check_interface_protection(name, board, cfg)
    findings += check_test_access(name, board, cfg)
    findings += check_board_identity(name, board, cfg)
    if cfg.get("sch"):
        findings += check_bom(name, kicad_sexp.read_schematic(ROOT / cfg["sch"]), materials)
    findings += debug_inventory(name, board, cfg)
    return findings


def apply_waivers(findings: list[Finding], waivers: list[dict[str, Any]]) -> list[str]:
    """Mark waived findings. Return errors for malformed or stale waivers."""
    errors = []
    for w in waivers:
        ref = str(w.get("ref", ""))
        if not re.fullmatch(r"(DEV-\d{3}|RISK-\d{3}|ADR-\d{4}|[A-Z]+-finding-\d+)", ref):
            errors.append(f"waiver {w}: 'ref' must name a DEV-, RISK- or ADR- record")
            continue
        if not str(w.get("reason", "")).strip():
            errors.append(f"waiver {w}: 'reason' is empty")
            continue
        hits = [
            f
            for f in findings
            if f.rule == w.get("rule") and f.board == w.get("board") and f.item == w.get("item")
        ]
        if not hits:
            errors.append(f"stale waiver (no matching finding): {w.get('rule')} {w.get('item')}")
        for f in hits:
            f.waived_by = ref
    return errors


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    ap.add_argument("--materials", type=Path, default=DEFAULT_MATERIALS)
    ap.add_argument("--out", type=Path, help="write the JSON report here (evidence)")
    ap.add_argument("--list-rules", action="store_true")
    args = ap.parse_args(argv)
    if args.list_rules:
        print(json.dumps([asdict(r) for r in RULES.values()], indent=2))
        return 0
    cfg = load_yaml(args.config)
    materials = load_yaml(args.materials).get("parts", {})
    findings: list[Finding] = []
    for board_cfg in cfg.get("boards", []):
        findings += check_board(board_cfg, materials)
    errors = apply_waivers(findings, cfg.get("waivers", []))
    failing = [f for f in findings if RULES[f.rule].severity == "gate" and not f.waived_by]
    report = {
        "tool": "scripts/check_hw_compliance.py",
        "rules": [asdict(r) for r in RULES.values()],
        "findings": [asdict(f) for f in findings],
        "errors": errors,
        "failing": len(failing),
    }
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    findings.sort(key=lambda f: (f.rule, f.board, f.item))
    for f in findings:
        sev = RULES[f.rule].severity
        state = f"waived {f.waived_by}" if f.waived_by else sev.upper()
        print(f"{f.rule} [{state}] {f.board}: {f.message}")
    for e in errors:
        print(f"ERROR: {e}")
    print(
        f"hw compliance: {len(findings)} findings, {len(failing)} failing gate findings, "
        f"{len(errors)} waiver errors"
    )
    return 1 if failing or errors else 0


if __name__ == "__main__":
    sys.exit(main())
