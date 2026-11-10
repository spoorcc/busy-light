# SPDX-License-Identifier: Apache-2.0
"""Tests for kicad_sexp.py and check_hw_compliance.py (synthetic boards, stored spike board)."""

from __future__ import annotations

from pathlib import Path

import check_hw_compliance as hwc
import kicad_sexp
import pytest

ROOT = Path(__file__).resolve().parent.parent


def fp(ref: str, lib: str, x: float, y: float, pads: list[tuple[str, str]]) -> str:
    pad_txt = " ".join(f'(pad "{n}" smd rect (net "{net}"))' for n, net in pads)
    return (
        f'(footprint "{lib}" (layer "F.Cu") (at {x} {y} 90) '
        f'(property "Reference" "{ref}") (property "Value" "v") {pad_txt})'
    )


def board_text(*fps: str, texts: tuple[str, ...] = ()) -> str:
    gr = " ".join(f'(gr_text "{t}" (at 0 0) (layer "F.SilkS"))' for t in texts)
    return f"(kicad_pcb (version 20260206) {' '.join(fps)} {gr})"


def make_board(tmp_path: Path, text: str) -> kicad_sexp.Board:
    p = tmp_path / "b.kicad_pcb"
    p.write_text(text, encoding="utf-8")
    return kicad_sexp.read_board(p)


CFG = {
    "external_interfaces": ["J1"],
    "protection_refs": ["D1"],
    "exempt_nets": ["GND"],
    "protection_max_distance_mm": 5,
    "power_nets": ["+5V", "GND"],
    "access_nets": {"reset": "EN"},
    "board_id_pattern": "(?i)demo.*rev",
}


def test_parse_handles_escapes_and_both_net_forms(tmp_path: Path) -> None:
    text = (
        '(kicad_pcb (footprint "L:X" (layer "B.Cu") (at 1 2) (property "Reference" "U1") '
        '(pad "1" smd (net 3 "A \\"q\\"")) (pad "2" smd (net "B")) (pad "3" smd)))'
    )
    b = make_board(tmp_path, text)
    assert b.footprints[0].layer == "B.Cu"
    assert [p.net for p in b.footprints[0].pads] == ['A "q"', "B", ""]


def test_parse_rejects_unbalanced() -> None:
    with pytest.raises(ValueError, match="unbalanced"):
        kicad_sexp.parse("(a (b)")
    with pytest.raises(ValueError, match="unbalanced"):
        kicad_sexp.parse("(a))")


def test_unprotected_interface_net_is_a_gate_finding(tmp_path: Path) -> None:
    b = make_board(
        tmp_path,
        board_text(
            fp("J1", "C", 0, 0, [("1", "VBUS"), ("2", "CC"), ("3", "GND"), ("4", "unconnected-x")]),
            fp("D1", "D", 1, 0, [("1", "VBUS"), ("2", "GND")]),
        ),
    )
    found = hwc.check_interface_protection("t", b, CFG)
    assert [(f.rule, f.item) for f in found] == [("HWC-001", "J1:CC")]


def test_clamp_through_one_series_resistor_counts(tmp_path: Path) -> None:
    b = make_board(
        tmp_path,
        board_text(
            fp("J1", "C", 0, 0, [("1", "BTN_RAW")]),
            fp("R1", "R", 1, 0, [("1", "BTN_RAW"), ("2", "BTN")]),
            fp("D1", "D", 2, 0, [("1", "BTN"), ("2", "GND")]),
        ),
    )
    assert hwc.check_interface_protection("t", b, CFG) == []


def test_far_clamp_is_a_report_finding(tmp_path: Path) -> None:
    b = make_board(
        tmp_path,
        board_text(
            fp("J1", "C", 0, 0, [("1", "VBUS")]),
            fp("D1", "D", 30, 40, [("1", "VBUS"), ("2", "GND")]),
        ),
    )
    found = hwc.check_interface_protection("t", b, CFG)
    assert [f.rule for f in found] == ["HWC-002"]
    assert "50.0 mm" in found[0].message
    assert hwc.RULES["HWC-002"].severity == "report"


def test_missing_interface_part_is_reported(tmp_path: Path) -> None:
    b = make_board(tmp_path, board_text(fp("D1", "D", 0, 0, [("1", "A")])))
    assert [f.rule for f in hwc.check_interface_protection("t", b, CFG)] == ["HWC-001"]


def test_test_access(tmp_path: Path) -> None:
    b = make_board(
        tmp_path,
        board_text(
            fp("TP1", "T", 0, 0, [("1", "GND")]),
            fp("U1", "U", 0, 0, [("1", "+5V"), ("2", "EN"), ("3", "GND")]),
        ),
    )
    found = hwc.check_test_access("t", b, CFG)
    assert sorted((f.rule, f.item) for f in found) == [("HWC-003", "+5V"), ("HWC-004", "reset")]


def test_board_identity(tmp_path: Path) -> None:
    good = make_board(tmp_path, board_text(texts=("Demo board rev A",)))
    bad = make_board(tmp_path, board_text(texts=("Demo board",)))
    assert hwc.check_board_identity("t", good, CFG) == []
    assert [f.rule for f in hwc.check_board_identity("t", bad, CFG)] == ["HWC-005"]


def sym(ref: str, mpn: str, man: str = "M", in_bom: bool = True, dnp: bool = False) -> str:
    return (
        f'(symbol (lib_id "x:y") (in_bom {"yes" if in_bom else "no"}) '
        f'(dnp {"yes" if dnp else "no"}) (property "Reference" "{ref}") '
        f'(property "MPN" "{mpn}") (property "Manufacturer" "{man}"))'
    )


def test_bom_rules(tmp_path: Path) -> None:
    p = tmp_path / "s.kicad_sch"
    p.write_text(
        '(kicad_sch (lib_symbols (symbol "x:y")) '
        + sym("R1", "")
        + sym("R2", "OK1")
        + sym("R3", "OK1")
        + sym("U1", "OLD")
        + sym("U2", "NEW")
        + sym("TP1", "", in_bom=False)
        + sym("C9", "", dnp=True)
        + sym("#PWR01", "")
        + ")",
        encoding="utf-8",
    )
    materials = {
        "OK1": {"rohs": "declared", "reach": "declared", "lifecycle": "active"},
        "OLD": {"rohs": "declared", "reach": "unknown", "lifecycle": "NRND"},
    }
    found = hwc.check_bom("t", kicad_sexp.read_schematic(p), materials)
    assert sorted((f.rule, f.item) for f in found) == [
        ("HWC-006", "R1"),
        ("HWC-007", "NEW"),
        ("HWC-007", "OLD"),
        ("HWC-008", "OLD"),
    ]


def test_waivers_mark_findings_and_reject_stale_or_bad_ones() -> None:
    findings = [hwc.Finding("HWC-005", "b", "silkscreen", "m")]
    errors = hwc.apply_waivers(
        findings,
        [
            {
                "rule": "HWC-005",
                "board": "b",
                "item": "silkscreen",
                "ref": "DEV-007",
                "reason": "r",
            },
            {"rule": "HWC-003", "board": "b", "item": "+5V", "ref": "DEV-007", "reason": "r"},
            {"rule": "HWC-003", "board": "b", "item": "+5V", "ref": "nobody", "reason": "r"},
            {"rule": "HWC-003", "board": "b", "item": "+5V", "ref": "DEV-001", "reason": " "},
        ],
    )
    assert findings[0].waived_by == "DEV-007"
    assert len(errors) == 3  # noqa: PLR2004
    assert any("stale" in e for e in errors)


def test_every_rule_has_basis_and_known_severity() -> None:
    for rule in hwc.RULES.values():
        assert rule.severity in {"gate", "report"}
        assert rule.basis.strip()


def test_stored_spike_board_passes_with_its_waivers() -> None:
    """The real config: every gate finding of the spike board is waived and no waiver is stale."""
    assert hwc.main([]) == 0


def test_spike_board_finds_the_known_gaps() -> None:
    cfg = hwc.load_yaml(hwc.DEFAULT_CONFIG)["boards"][0]
    materials = hwc.load_yaml(hwc.DEFAULT_MATERIALS)["parts"]
    found = {(f.rule, f.item) for f in hwc.check_board(cfg, materials)}
    assert ("HWC-001", "J1:/CC1") in found
    assert ("HWC-005", "silkscreen") in found
    # The button is protected through R12 and TVS2; VBUS and the data lines through TVS1 and U6.
    assert not any(r == "HWC-001" and i.startswith("SW1") for r, i in found)
    assert ("HWC-001", "J1:VBUS_IC") not in found


def test_ipc2221_width_matches_hand_calculation() -> None:
    # 1.5 A, 10 K, 35 um outer: A = (1.5 / (0.048 * 10**0.44))**(1/0.725) = 28.5 mil^2 -> 0.53 mm
    assert hwc.ipc2221_min_width_mm(1.5, 10, 35, outer=True) == pytest.approx(0.53, abs=0.01)
    inner = hwc.ipc2221_min_width_mm(1.5, 10, 17.5, outer=False)
    assert inner > 5 * hwc.ipc2221_min_width_mm(1.5, 10, 35, outer=True) / 2


def test_track_current_reports_narrow_segments_per_layer_group(tmp_path: Path) -> None:
    seg = '(segment (start 0 0) (end 1 0) (width {w}) (layer "{layer}") (net "{net}"))'
    text = (
        "(kicad_pcb "
        + seg.format(w=1.0, layer="F.Cu", net="+5V")
        + seg.format(w=0.2, layer="B.Cu", net="+5V")
        + seg.format(w=0.2, layer="F.Cu", net="SIG")
        + seg.format(w=5.0, layer="In1.Cu", net="+5V")
        + ")"
    )
    b = make_board(tmp_path, text)
    assert len(b.segments) == 4  # noqa: PLR2004
    cfg = {"track_current": {"nets": {"+5V": 1.5}, "inner_copper_um": 17.5}}
    found = hwc.check_track_current("t", b, cfg)
    assert [(f.rule, f.item) for f in found] == [("HWC-010", "+5V:outer")]
    assert "1 of 2" in found[0].message
    assert hwc.check_track_current("t", b, {}) == []
