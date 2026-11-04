# SPDX-License-Identifier: Apache-2.0
"""Check a generated gate schematic: ERC errors = 0 and net parity with the SKiDL netlist.

Usage: check_gate.py <dir with gate.net and gate.kicad_sch>   (exit 0 = pass)
"""
import re
import subprocess
import sys
from pathlib import Path


def nets(text: str) -> dict:
    """Map net name to a frozenset of (reference, pin). Power flags and unnamed nets are skipped."""
    text = text[text.index("(nets"):]
    out = {}
    for blk in re.split(r"\(net\s*\(code", text)[1:]:
        pins = frozenset(p for p in re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', blk)
                         if not p[0].startswith("#"))
        if pins:
            out[pins] = re.search(r'\(name "([^"]*)"', blk).group(1)
    return out


def parity(skidl_net: str, sch_net: str) -> list:
    """Compare the sets of connected pin groups (net names may differ: N$1 or Net-(Q2-D))."""
    a, b = nets(skidl_net), nets(sch_net)
    # Ignore groups of one pin: they are unconnected pins, which ERC reports.
    ga = {k for k in a if len(k) > 1}
    gb = {k for k in b if len(k) > 1}
    return sorted(map(sorted, ga ^ gb))


def main(d: Path) -> int:
    rpt = d / "erc.rpt"
    subprocess.run(["kicad-cli", "sch", "erc", "--format", "report", "--severity-error",
                    "-o", str(rpt), str(d / "gate.kicad_sch")], check=True, capture_output=True)
    ercs = re.findall(r"^\[(\w+)\]", rpt.read_text(), re.M)
    subprocess.run(["kicad-cli", "sch", "export", "netlist", "--format", "kicadsexpr",
                    "-o", str(d / "kicad.net"), str(d / "gate.kicad_sch")],
                   check=True, capture_output=True)
    diff = parity((d / "gate.net").read_text(), (d / "kicad.net").read_text())
    print(f"ERC errors: {len(ercs)} {ercs}; parity differences: {len(diff)}")
    for g in diff:
        print("  differs:", g)
    return 0 if not ercs and not diff else 1


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
