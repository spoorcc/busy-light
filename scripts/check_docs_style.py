#!/usr/bin/env python3
"""Light style check for user documentation (docs/user/**/*.md) against docs/standards/writing.md.

Checks: numbered steps <= 20 words, other sentences <= 25 words, paragraphs <= 6 sentences,
no contractions.
This is NOT an ASD-STE100 conformance check; it catches common violations only. Exit 1 on findings.
"""

import re
import sys
from pathlib import Path

STEP_MAX, SENT_MAX, PARA_MAX = 20, 25, 6
CONTRACTION = re.compile(r"\b\w+(?:n't|'re|'ve|'ll|'d|'m)\b", re.I)
STEP = re.compile(r"^\s*\d+\.\s+(.*)")


def clean(text: str) -> str:
    text = re.sub(r"`[^`]*`", "X", text)  # inline code
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)  # links
    text = re.sub(r"[*_>#]", "", text)  # emphasis, quotes, headings
    return text.strip()


def sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def check(path: Path) -> list[str]:
    out, in_code = [], False
    para: list[str] = []
    para_start = 0

    def flush() -> None:
        nonlocal para
        if para:
            n = len(sentences(" ".join(para)))
            if n > PARA_MAX:
                out.append(f"{path}:{para_start}: paragraph has {n} sentences (max {PARA_MAX})")
        para = []

    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if raw.strip().startswith("```"):
            in_code = not in_code
            flush()
            continue
        if in_code:
            continue
        if not raw.strip() or raw.lstrip().startswith(("|", "#", "<!--", "- **")):
            flush()
            continue
        step = STEP.match(raw)
        text = clean(step.group(1) if step else raw)
        found = CONTRACTION.search(text)
        if found:
            out.append(f"{path}:{n}: contraction ('{found.group(0)}')")
        if step:
            flush()
            words = len(text.split())
            if words > STEP_MAX:
                out.append(f"{path}:{n}: step has {words} words (max {STEP_MAX})")
            continue
        for s in sentences(text):
            if len(s.split()) > SENT_MAX:
                out.append(f"{path}:{n}: sentence has {len(s.split())} words (max {SENT_MAX})")
        if not para:
            para_start = n
        para.append(text)
    flush()
    return out


def main() -> int:
    root = Path(__file__).resolve().parent.parent / "docs" / "user"
    findings = [f for p in sorted(root.rglob("*.md")) for f in check(p)]
    print("\n".join(findings) or "docs style: no findings")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
