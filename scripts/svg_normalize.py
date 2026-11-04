#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Normalise a rendered SVG for comparison across machines.

Text widths come from the machine's font metrics, so coordinates and sizes differ by fractions of a
pixel between machines. This script replaces every number inside a quoted attribute value with '#'.
Text content (labels), element names, attribute names, colours and the order of elements stay exact.
Usage: svg_normalize.py FILE   (prints the normalised text)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_ATTR = re.compile(r'="([^"]*)"')
_ARGS = 2
_NUM = re.compile(r"-?\d+(?:\.\d+)?")


def normalize(svg: str) -> str:
    """Return the SVG text with numbers inside attribute values replaced by '#'."""
    return _ATTR.sub(lambda m: '="' + _NUM.sub("#", m.group(1)) + '"', svg)


def main(argv: list[str]) -> int:
    if len(argv) != _ARGS:
        print("usage: svg_normalize.py FILE", file=sys.stderr)
        return 2
    sys.stdout.write(normalize(Path(argv[1]).read_text(encoding="utf-8")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
