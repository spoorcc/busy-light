"""Spike: route a board with Freerouting (DSN export, headless run, SES import). Fails if the jar hash differs.
usage: route_freerouting.py <in.kicad_pcb> <out.kicad_pcb> <freerouting.jar> <expected_sha256> [stored.ses]
With a stored session the router is not run: the session is imported (deterministic regeneration, ADR-0012 item 11).
The router itself is not deterministic (spike report section 9)."""
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

import pcbnew

src, out, jar, want = sys.argv[1:5]
stored = sys.argv[5] if len(sys.argv) > 5 else None
board = pcbnew.LoadBoard(src)
if stored:
    if not pcbnew.ImportSpecctraSES(board, stored):
        sys.exit("SES import failed")
    board.Save(out)
    sys.exit(0)
got = hashlib.sha256(Path(jar).read_bytes()).hexdigest()
if got != want:
    sys.exit(f"jar hash mismatch: {got} != {want}")
with tempfile.TemporaryDirectory() as tmp:
    dsn, ses = f"{tmp}/in.dsn", f"{tmp}/out.ses"
    if not pcbnew.ExportSpecctraDSN(board, dsn):
        sys.exit("DSN export failed")
    log = subprocess.run(
        ["java", "-Djava.awt.headless=true", "-jar", jar, "-de", dsn, "-do", ses, "-mp", "30"],
        capture_output=True, text=True, timeout=600, check=False,
    )
    tail = [ln for ln in log.stdout.splitlines() if "Auto-routing stage completed" in ln]
    print(tail[-1] if tail else "no completion line in the router log")
    if not Path(ses).exists() or not pcbnew.ImportSpecctraSES(board, ses):
        sys.exit("SES import failed")
    Path(out + ".ses").write_bytes(Path(ses).read_bytes())  # stored routing input (ADR-0012 item 11)
board.Save(out)
