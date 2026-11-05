# SPDX-License-Identifier: Apache-2.0
"""Check the full-board sheet: ERC errors = 0 and net groups equal to the intent table.

The intent (every connection the layout script meant to draw, recorded while drawing) is compared
with the netlist that kicad-cli exports from the drawn sheet. Net names may differ (KiCad names
unlabelled nets itself); the groups of (reference, pin) are compared. Groups of one pin and the
power flags are ignored.
Usage: check_full.py <dir with full.kicad_sch and intent.json>
"""
import json
import re
import subprocess
import sys
from pathlib import Path


def groups(text):
    text = text[text.index("(nets"):]
    out = {}
    for blk in re.split(r"\(net\s*\(code", text)[1:]:
        pins = frozenset(p for p in re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', blk)
                         if not p[0].startswith("#"))
        if len(pins) > 1:
            out[pins] = re.search(r'\(name "([^"]*)"', blk).group(1)
    return out


def main(d):
    d = Path(d)
    rpt = d / "erc.rpt"
    subprocess.run(["kicad-cli", "sch", "erc", "--format", "report", "--severity-error",
                    "-o", str(rpt), str(d / "full.kicad_sch")], check=True, capture_output=True)
    ercs = re.findall(r"^\[(\w+)\]: (.*)$", rpt.read_text(), re.M)
    subprocess.run(["kicad-cli", "sch", "export", "netlist", "--format", "kicadsexpr",
                    "-o", str(d / "kicad.net"), str(d / "full.kicad_sch")], check=True, capture_output=True)
    drawn = groups((d / "kicad.net").read_text())
    intent = {frozenset(map(tuple, v)): k for k, v in json.loads((d / "intent.json").read_text()).items()
              if len(v) > 1}
    only_intent = [(intent[g], sorted(g)) for g in intent if g not in drawn]
    only_drawn = [(drawn[g], sorted(g)) for g in drawn if g not in intent]
    print(f"ERC errors: {len(ercs)}; intent nets: {len(intent)}; drawn nets: {len(drawn)}; "
          f"only in intent: {len(only_intent)}; only in drawing: {len(only_drawn)}")
    for e in ercs[:20]:
        print("  ERC", e)
    for n, g in only_intent[:15]:
        print("  intent only:", n, g)
    for n, g in only_drawn[:15]:
        print("  drawn only:", n, g)
    return 0 if not ercs and not only_intent and not only_drawn else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
