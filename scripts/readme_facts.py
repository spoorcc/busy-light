#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Print the facts that the READMEs quote, counted from the sources (skill readme-refresh).

Usage: python3 -I scripts/readme_facts.py [--root <repo>] [--json]

Counts requirements and approvals per file, ADRs per status, review records, plan statuses, host
test cases per ztest suite, and lists each README with its last commit date and the commits to
its own folder since then (root README: docs/, hw/, mech/, sw/, scripts/). Also lists images in
docs/verification/reports/images that no Markdown file shows. It reads only; it changes nothing.
The README text stays a human (or agent) decision: compare these numbers with it."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import TypedDict

REQ_HEAD = re.compile(r"^#{2,4} +((?:NEED|SYS|SW|HW|MECH)-\d+)\b.*$", re.M)
STATUS = re.compile(r"^- \*\*Status:\*\* *(.+)$", re.M)
ZTEST = re.compile(r"^ZTEST(?:_F)?\(\s*\w+\s*,\s*(\w+)\s*\)", re.M)
IMAGE_EXT = (".png", ".svg", ".jpg")
PRODUCT = ("docs", "hw", "mech", "sw", "scripts")
SKIP = {".git", "modules", "zephyr", "node_modules", ".claude", "build", ".venv"}


class Req(TypedDict):
    entries: int
    approved: list[str]


class Age(TypedDict):
    last_commit: str
    commits_since: int


def requirements(root: Path) -> dict[str, Req]:
    """Per requirements file: number of entries and the IDs whose own Status says Approved."""
    out: dict[str, Req] = {}
    for f in sorted((root / "docs/requirements").glob("*.md")):
        text = f.read_text(encoding="utf-8")
        heads = list(REQ_HEAD.finditer(text))
        approved = []
        for i, h in enumerate(heads):
            end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
            m = STATUS.search(text, h.end(), end)
            if m and m.group(1).startswith("Approved"):
                approved.append(h.group(1))
        out[f.name] = {"entries": len(heads), "approved": approved}
    return out


def adr_class(status: str) -> str:
    for word in ("Accepted", "Proposed", "Superseded", "Rejected", "Deprecated"):
        if status.startswith(word):
            return word
    return "other"


def adrs(root: Path) -> dict[str, list[str]]:
    """ADR ids per status class. A qualified status ("Accepted for the prototype only") counts as
    its first word; the README names the qualifier."""
    out: dict[str, list[str]] = {}
    for f in sorted((root / "docs/decisions").glob("ADR-*.md")):
        m = STATUS.search(f.read_text(encoding="utf-8"))
        status = m.group(1) if m else ""
        key = adr_class(status)
        plain = status == key or status.startswith(key + " (")
        out.setdefault(key, []).append(f.name[:8] + ("" if plain else "*"))
    return out


def reviews(root: Path) -> list[str]:
    return sorted("-".join(f.stem.split("-")[:2]) for f in (root / "docs/reviews").glob("RV-*.md"))


def plans(root: Path) -> dict[str, str]:
    out = {}
    for f in sorted((root / "docs/plans").glob("*.md")):
        m = STATUS.search(f.read_text(encoding="utf-8"))
        out[f.name] = (m.group(1) if m else "?")[:90]
    return out


def host_tests(root: Path) -> dict[str, int]:
    out = {}
    for suite in sorted(p for p in (root / "sw/app/tests").glob("*") if p.is_dir()):
        n = sum(len(ZTEST.findall(c.read_text(encoding="utf-8"))) for c in suite.rglob("*.c"))
        out[suite.name] = n
    return out


def shown_images(root: Path) -> set[Path]:
    """Every image path that a tracked-looking Markdown file under root links to (resolved)."""
    link = re.compile(r"""(?:src|href)="([^"]+)"|\]\(([^)\s]+)\)""")
    shown = set()
    for md in root.rglob("*.md"):
        if SKIP.intersection(md.parts):
            continue
        for m in link.finditer(md.read_text(encoding="utf-8", errors="replace")):
            ref = m.group(1) or m.group(2)
            if ref.endswith(IMAGE_EXT) and not re.match(r"[a-z]+:", ref):
                shown.add((md.parent / ref).resolve())
    return shown


def unused_images(root: Path) -> list[str]:
    folder = root / "docs/verification/reports/images"
    shown = shown_images(root)
    return sorted(
        p.name for p in folder.glob("*") if p.suffix in IMAGE_EXT and p.resolve() not in shown
    )


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=True
    ).stdout.strip()


def readme_ages(root: Path) -> dict[str, Age]:
    """Each tracked README: date of its last commit and the commits since then to its own folder
    (other files than the README); for the root README, to the product folders."""
    out: dict[str, Age] = {}
    for name in git(root, "ls-files", "README.md", "*/README.md").splitlines():
        last = git(root, "log", "-1", "--format=%h %cs", "--", name)
        if not last:
            continue
        sha, date = last.split()
        folder = str(Path(name).parent)
        dirs = PRODUCT if folder == "." else (folder,)
        since = git(root, "rev-list", "--count", f"{sha}..HEAD", "--", *dirs, f":!{name}")
        out[name] = {"last_commit": date, "commits_since": int(since)}
    return out


@dataclass
class Facts:
    requirements: dict[str, Req]
    adrs: dict[str, list[str]]
    reviews: list[str]
    plans: dict[str, str]
    host_tests: dict[str, int]
    unused_images: list[str]
    readmes: dict[str, Age] = field(default_factory=dict)


def collect(root: Path, with_git: bool = True) -> Facts:
    return Facts(
        requirements(root),
        adrs(root),
        reviews(root),
        plans(root),
        host_tests(root),
        unused_images(root),
        readme_ages(root) if with_git else {},
    )


def show(f: Facts) -> str:
    total = sum(r["entries"] for r in f.requirements.values())
    approved = [i for r in f.requirements.values() for i in r["approved"]]
    lines = [f"Requirements: {total} entries, {len(approved)} approved"]
    for name, r in f.requirements.items():
        ids = " ".join(r["approved"])
        lines.append(f"  {name}: {r['entries']} entries, approved {len(r['approved'])}: {ids}")
    lines.append(
        f"ADRs: {sum(len(v) for v in f.adrs.values())} records (* = qualified status, name it)"
    )
    lines += [f"  {k}: {len(ids)}: {' '.join(ids)}" for k, ids in sorted(f.adrs.items())]
    lines.append(f"Review records: {len(f.reviews)} (last {f.reviews[-1] if f.reviews else '-'})")
    lines.append("Plans:")
    lines += [f"  {k}: {v}" for k, v in f.plans.items()]
    lines.append(
        "Host test cases per suite (ZTEST lines; the last recorded run is in the reports):"
    )
    lines += [f"  {k}: {v}" for k, v in f.host_tests.items()]
    lines.append("Images in docs/verification/reports/images that no Markdown file shows:")
    lines += [f"  {n}" for n in f.unused_images] or ["  none"]
    if f.readmes:
        lines.append(
            "READMEs: last commit, then commits to its folder since (root README: product folders):"
        )
        lines += [f"  {k}: {v['last_commit']}, {v['commits_since']}" for k, v in f.readmes.items()]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--json", action="store_true", help="print JSON instead of text")
    a = ap.parse_args()
    facts = collect(a.root)
    print(json.dumps(asdict(facts), indent=1) if a.json else show(facts))


if __name__ == "__main__":
    main()
