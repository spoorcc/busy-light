# SPDX-License-Identifier: Apache-2.0
"""Project library tables of the generated spike projects (plan 06 A-11).

kicad-cli (ERC and DRC) resolves the library nickname of every symbol (lib_id) and footprint through the symbol
and footprint library tables. The stock tables of a user configuration are not present on a build machine or in CI,
and kicad-cli reads a project table only when a project file (<stem>.kicad_pro) sits next to the schematic or board.
So the generators write, next to every generated schematic or board:
  <stem>.kicad_pro   minimal project file (the board generator writes its own, with the design rules)
  sym-lib-table      one entry per symbol nickname used in the schematic
  fp-lib-table       one entry per footprint nickname used
  <nick>.kicad_sym   custom symbol library (the generated box symbols of the schematic: nickname CUSTOM_SYM)
  <nick>.pretty      custom footprint library (the provisional X2QFN-12 land pattern: nickname CUSTOM)
Stock libraries are reached through ${KICAD10_SYMBOL_DIR} and ${KICAD10_FOOTPRINT_DIR} (set by KiCad 10 itself);
custom libraries through ${KIPRJMOD}. Output is deterministic (sorted nicknames, no timestamps). Pure Python.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import custom_fp

CUSTOM_SYM = {"busylight_gate"}     # generated box symbols (layout_sch.NS_LIB); file <nick>.kicad_sym in the project
CUSTOM_FP = {"CUSTOM"}              # generated footprints (pcb_full); directory <nick>.pretty in the project

_SYM_URI = "${KICAD10_SYMBOL_DIR}/%s.kicad_sym"
_FP_URI = "${KICAD10_FOOTPRINT_DIR}/%s.pretty"


def nicknames(sch_text: str) -> tuple[set[str], set[str]]:
    """(symbol nicknames, footprint nicknames) used by a schematic: lib_id values and Footprint properties."""
    sym = set(re.findall(r'\(lib_id "([^":"]+):', sch_text))
    fp = set(re.findall(r'\(property "Footprint" "([^":"]+):', sch_text))
    return sym, fp


def _table(tag: str, nicks, custom, stock_uri: str, custom_uri: str) -> str:
    lines = [f"({tag}", "  (version 7)"]
    for n in sorted(nicks):
        uri = custom_uri % n if n in custom else stock_uri % n
        lines.append(f'  (lib (name "{n}")(type "KiCad")(uri "{uri}")(options "")(descr ""))')
    lines.append(")")
    return "\n".join(lines) + "\n"


def sym_lib_table(nicks, custom=CUSTOM_SYM) -> str:
    return _table("sym_lib_table", nicks, custom, _SYM_URI, "${KIPRJMOD}/%s.kicad_sym")


def fp_lib_table(nicks, custom=CUSTOM_FP) -> str:
    return _table("fp_lib_table", nicks, custom, _FP_URI, "${KIPRJMOD}/%s.pretty")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def write_minimal_project(outdir: Path, stem: str) -> None:
    pro = outdir / f"{stem}.kicad_pro"
    if not pro.exists():
        write_text(pro, json.dumps({"meta": {"filename": f"{stem}.kicad_pro", "version": 3}}, indent=2) + "\n")


def write_custom_symbol_libs(sch_path: Path, outdir: Path, custom=CUSTOM_SYM) -> None:
    """Write <nick>.kicad_sym for each custom nickname: the symbols embedded in the schematic, without the nickname."""
    from kiutils.schematic import Schematic       # not needed by the board side
    from kiutils.symbol import SymbolLib

    sch = Schematic.from_file(str(sch_path))
    for nick in sorted(custom):
        lib = SymbolLib()
        lib.version = sch.version
        lib.generator = "busy-light-lib_tables"
        for s in sorted((s for s in sch.libSymbols if s.libraryNickname == nick), key=lambda s: s.entryName):
            s.libraryNickname = None
            s.libId = s.entryName
            lib.symbols.append(s)
        if lib.symbols:
            lib.to_file(str(outdir / f"{nick}.kicad_sym"))


def write_schematic_project(sch_path) -> None:
    """Next to a generated schematic: project file, both library tables and the custom symbol libraries."""
    sch_path = Path(sch_path)
    outdir = sch_path.parent
    sym, fp = nicknames(sch_path.read_text(encoding="utf-8"))
    write_minimal_project(outdir, sch_path.stem)
    write_text(outdir / "sym-lib-table", sym_lib_table(sym))
    write_text(outdir / "fp-lib-table", fp_lib_table(fp))
    write_custom_symbol_libs(sch_path, outdir)
    if CUSTOM_FP & fp:
        custom_fp.write_library(outdir)
