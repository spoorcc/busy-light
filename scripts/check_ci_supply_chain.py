#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Supply-chain rules for the CI that builds and checks the product.

SWC-004 (gate): every GitHub Action is pinned to a full commit SHA (or a docker digest).
SWC-005 (gate): every file downloaded by curl or wget in a workflow step or a scripts/*.sh file is
checked with 'sha256sum -c' in the same step or script; piping a download into a shell is forbidden.

Basis: CRA Annex I Part I (1) and Part II (1) (know and control the components that go into the
product, verify); docs/standards/coding-sw.md 4a; ADR-0012 item 4. A pinned SHA proves the action
did not change after review; it does not prove the action is safe.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
RULES = {"SWC-004": "gate", "SWC-005": "gate"}
USES_OK = re.compile(r"^(?:\./.+|docker://.+@sha256:[0-9a-f]{64}|[^@\s]+@[0-9a-f]{40})$")
FETCH = re.compile(r"\b(?:curl|wget)\b")
PIPE_TO_SHELL = re.compile(r"\b(?:curl|wget)\b[^\n|]*\|\s*(?:sudo\s+)?(?:ba|z|da)?sh\b")
VERIFY = re.compile(r"sha256sum\s+(?:-c|--check)\b")


def check_run_block(text: str, where: str) -> list[str]:
    out = []
    if PIPE_TO_SHELL.search(text):
        out.append(f"SWC-005 {where}: a download is piped into a shell")
    fetches = [
        ln for ln in text.splitlines() if FETCH.search(ln) and not ln.lstrip().startswith("#")
    ]
    if fetches and not VERIFY.search(text):
        out.append(f"SWC-005 {where}: download without 'sha256sum -c': {fetches[0].strip()[:80]}")
    return out


def check_workflow(path: Path) -> list[str]:
    data: Any = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
    out = []
    for job_name, job in (data.get("jobs") or {}).items():
        for i, step in enumerate(job.get("steps") or []):
            where = f"{rel} job {job_name} step {i + 1}"
            uses = step.get("uses")
            if uses and not USES_OK.match(str(uses).strip()):
                out.append(f"SWC-004 {where}: action not pinned to a commit SHA: {uses}")
            if step.get("run"):
                out += check_run_block(str(step["run"]), where)
        image = (job.get("container") or {}).get("image") if isinstance(job, dict) else None
        if image and "@sha256:" not in str(image):
            out.append(f"REPORT SWC-004 {rel} job {job_name}: container image by tag: {image}")
    return out


def main() -> int:
    findings = []
    for wf in sorted((ROOT / ".github" / "workflows").glob("*.y*ml")):
        findings += check_workflow(wf)
    for sh in sorted((ROOT / "scripts").glob("*.sh")):
        findings += check_run_block(sh.read_text(encoding="utf-8"), str(sh.relative_to(ROOT)))
    for f in findings:
        print(f)
    gate = [f for f in findings if not f.startswith("REPORT")]
    print(f"ci supply chain: {len(gate)} failing, {len(findings) - len(gate)} reported")
    return 1 if gate else 0


if __name__ == "__main__":
    sys.exit(main())
