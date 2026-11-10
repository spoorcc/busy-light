# SPDX-License-Identifier: Apache-2.0
"""Read-only parser for KiCad s-expression files (.kicad_pcb, .kicad_sch).

It needs no KiCad installation, so the compliance checks can run in any CI job. It never writes a
KiCad file (CLAUDE.md rule 12). It extracts only what the checks in check_hw_compliance.py need:
footprints with their pads and nets, board texts, and schematic symbols with their fields.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

Node = list["Node | str"] | str

_TOKEN = re.compile(r'\s*(?:(\()|(\))|"((?:[^"\\]|\\.)*)"|([^\s()"]+))', re.S)


def parse(text: str) -> Node:
    """Parse one s-expression. Quoted and bare atoms are both returned as str."""
    stack: list[list[Node | str]] = [[]]
    pos = 0
    end = len(text.rstrip())
    while pos < end:
        m = _TOKEN.match(text, pos)
        if m is None:
            raise ValueError(f"unexpected input at offset {pos}")
        pos = m.end()
        if m.group(1):
            stack.append([])
        elif m.group(2):
            if len(stack) < 2:  # noqa: PLR2004 - root list plus one open list
                raise ValueError(f"unbalanced ')' at offset {m.start()}")
            done = stack.pop()
            stack[-1].append(done)
        elif m.group(3) is not None:
            stack[-1].append(re.sub(r"\\(.)", r"\1", m.group(3)))
        else:
            stack[-1].append(m.group(4))
    if len(stack) != 1 or len(stack[0]) != 1:
        raise ValueError("unbalanced s-expression")
    return stack[0][0]


def head(node: Node) -> str:
    first = node[0] if isinstance(node, list) and node else None
    return first if isinstance(first, str) else ""


def children(node: Node, name: str) -> list[list[Node | str]]:
    if not isinstance(node, list):
        return []
    return [c for c in node if isinstance(c, list) and head(c) == name]


def child(node: Node, name: str) -> list[Node | str] | None:
    found = children(node, name)
    return found[0] if found else None


def atom(node: Node | None, index: int = 1, default: str = "") -> str:
    value = node[index] if isinstance(node, list) and len(node) > index else None
    return value if isinstance(value, str) else default


@dataclass
class Pad:
    number: str
    net: str


@dataclass
class Footprint:
    ref: str
    lib: str
    layer: str
    x: float
    y: float
    value: str
    pads: list[Pad] = field(default_factory=list)

    @property
    def nets(self) -> set[str]:
        return {p.net for p in self.pads if p.net}


@dataclass
class Text:
    text: str
    layer: str


@dataclass
class Segment:
    net: str
    width: float
    layer: str


@dataclass
class Board:
    footprints: list[Footprint]
    texts: list[Text]
    segments: list[Segment] = field(default_factory=list)

    def by_ref(self) -> dict[str, Footprint]:
        return {f.ref: f for f in self.footprints}


def _props(node: Node) -> dict[str, str]:
    return {atom(p, 1): atom(p, 2) for p in children(node, "property")}


def _pad_net(pad: Node) -> str:
    net = child(pad, "net")
    if net is None:
        return ""
    # KiCad <= 9: (net 3 "name"); KiCad 10: (net "name").
    return atom(net, len(net) - 1)


def read_board(path: Path) -> Board:
    root = parse(path.read_text(encoding="utf-8"))
    if head(root) != "kicad_pcb":
        raise ValueError(f"{path}: not a kicad_pcb file")
    fps: list[Footprint] = []
    for fp in children(root, "footprint"):
        props = _props(fp)
        at = child(fp, "at")
        fps.append(
            Footprint(
                ref=props.get("Reference", ""),
                lib=atom(fp, 1),
                layer=atom(child(fp, "layer")),
                x=float(atom(at, 1, "0")),
                y=float(atom(at, 2, "0")),
                value=props.get("Value", ""),
                pads=[Pad(atom(p, 1), _pad_net(p)) for p in children(fp, "pad")],
            )
        )
    texts = [Text(atom(t, 1), atom(child(t, "layer"))) for t in children(root, "gr_text")]
    segments = [
        Segment(_pad_net(s), float(atom(child(s, "width"), 1, "0")), atom(child(s, "layer")))
        for s in children(root, "segment")
    ]
    return Board(fps, texts, segments)


@dataclass
class Symbol:
    ref: str
    lib_id: str
    fields: dict[str, str]
    in_bom: bool
    dnp: bool


def read_schematic(path: Path) -> list[Symbol]:
    root = parse(path.read_text(encoding="utf-8"))
    if head(root) != "kicad_sch":
        raise ValueError(f"{path}: not a kicad_sch file")
    out: list[Symbol] = []
    for sym in children(root, "symbol"):  # top-level symbols are placed instances
        lib_id = atom(child(sym, "lib_id"))
        if not lib_id:
            continue
        fields = _props(sym)
        ref = fields.get("Reference", "")
        out.append(
            Symbol(
                ref=ref,
                lib_id=lib_id,
                fields=fields,
                in_bom=atom(child(sym, "in_bom"), 1, "yes") == "yes",
                dnp=atom(child(sym, "dnp"), 1, "no") == "yes",
            )
        )
    return out
