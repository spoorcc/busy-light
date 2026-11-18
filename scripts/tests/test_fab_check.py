# SPDX-License-Identifier: Apache-2.0
"""Tests of the P1 order-package checks (scripts/fab_check.py and fab_package.py; plan 08 4.5)."""

from __future__ import annotations

import csv
import importlib.util
import io
import json
import zipfile
from pathlib import Path
from types import ModuleType

import fab_check as fc
import fab_package as fp
import pytest

ROOT = Path(__file__).resolve().parents[2]
SPIKE = ROOT / "hw" / "kicad" / "spike-gate"


# ------------------------------------------------------------------------------------------ helpers
def footprint(
    ref: str,
    value: str = "1k",
    lib: str = "Resistor_SMD:R_0603_1608Metric",
    layer: str = "F.Cu",
    attrs: str = "smd",
) -> str:
    attr = f"(attr {attrs})" if attrs else ""
    return (
        f'(footprint "{lib}" (layer "{layer}") (at 10 10 90)\n'
        f'  (property "Reference" "{ref}" (at 0 0 0) (layer "F.SilkS"))\n'
        f'  (property "Value" "{value}" (at 0 1 0) (layer "F.Fab"))\n'
        f"  {attr})\n"
    )


def board_text(*footprints: str) -> str:
    return '(kicad_pcb (version 20260206) (generator "pcbnew")\n' + "".join(footprints) + ")\n"


# A 50 x 60 mm panel outline with a round cut-out of radius 5 at (25, 30), as KiCad writes it.
GERBER = """G04 #@! TF.CreationDate,2026-11-18T06:09:29+00:00*
%FSLAX46Y46*%
G04 Created by KiCad (PCBNEW 10.0.8) date 2026-11-18 06:09:29*
%MOMM*%
%LPD*%
G01*
%ADD10C,0.100000*%
D10*
X0Y0D02*
X50000000Y0D01*
X50000000Y60000000D01*
X0Y60000000D01*
X0Y0D01*
G75*
G03*
X30000000Y30000000D02*
X30000000Y30000000I-5000000J0D01*
G01*
M02*
"""

PARTS = [
    footprint("R_ILIM1", "47.0k 0.1%"),
    footprint("R_ILIM2", "56.2k 0.1%"),
    footprint("R_ILIM3", "27.7k 0.1%"),
    footprint("C1", "100n", "Capacitor_SMD:C_0603_1608Metric"),
    footprint("U5", "TPS3840DL40", "Package_TO_SOT_SMD:SOT-23-5"),
    footprint("J1", "USB-C receptacle", "CUSTOM:USB_C", attrs="through_hole"),
    footprint("C4", "DNP spare", "Capacitor_SMD:C_1206_3216Metric", attrs="smd dnp"),
    footprint(
        "TP1",
        "TP_5V",
        "TestPoint:TestPoint_Pad_D1.5mm",
        "B.Cu",
        "exclude_from_pos_files exclude_from_bom",
    ),
    footprint(
        "FID1", "Fiducial", "Fiducial:Fiducial_1mm", attrs="exclude_from_pos_files exclude_from_bom"
    ),
    footprint("H1", "MountingHole", "MountingHole:MountingHole_2.2mm_M2", attrs=""),
]
BOM_ROWS = [
    ("47.0k 0.1%", "R_ILIM1", "R_0603", "C667109"),
    ("56.2k 0.1%", "R_ILIM2", "R_0603", "C667119"),
    ("27.7k 0.1%", "R_ILIM3", "R_0603", "C865349"),
    ("100n", "C1", "C_0603", "C1591"),
    ("TPS3840DL40", "U5", "SOT-23-5", ""),
]
CPL_ROWS = [(r[1], 10.0 + i, 10.0, "T") for i, r in enumerate(BOM_ROWS)]


def write_package(
    out: Path,
    bom: list[tuple[str, str, str, str]] | None = None,
    cpl: list[tuple[str, float, float, str]] | None = None,
    gerber: str = GERBER,
) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    with (out / fc.BOM_FILE).open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC"])
        w.writerows(BOM_ROWS if bom is None else bom)
    with (out / fc.CPL_FILE).open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        w.writerows([(*row, 0.0) for row in (CPL_ROWS if cpl is None else cpl)])
    with zipfile.ZipFile(out / fc.GERBER_ZIP, "w") as zf:
        zf.writestr("gerber/panel-EdgeCuts.gm1", gerber)
        zf.writestr("gerber/panel-CuTop.gtl", "G04 copper*\nM02*\n")
    return out


def write_board(path: Path, parts: list[str] | None = None) -> Path:
    path.write_text(board_text(*(PARTS if parts is None else parts)), encoding="utf-8")
    return path


def check(
    tmp_path: Path,
    bom: list[tuple[str, str, str, str]] | None = None,
    cpl: list[tuple[str, float, float, str]] | None = None,
    parts: list[str] | None = None,
    allowed: dict[str, str] | None = None,
) -> tuple[dict[str, fc.Result], list[str]]:
    out = write_package(tmp_path / "pkg", bom, cpl)
    board = write_board(tmp_path / "b.kicad_pcb", parts)
    results, lines = fc.run_checks(
        fc.read_bom(out / fc.BOM_FILE),
        fc.read_cpl(out / fc.CPL_FILE),
        fc.read_footprints(board),
        fc.edge_cuts_from_zip(out / fc.GERBER_ZIP),
        {"U5": "listed"} if allowed is None else allowed,
    )
    return {r.name: r for r in results}, lines


def load(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------------------- the board
def test_sexpr_parser_reads_strings_with_escapes() -> None:
    tree = fc.parse_sexpr('(a "b \\"c\\"" (d e))')
    assert tree == [["a", 'b "c"', ["d", "e"]]]


def test_sexpr_parser_rejects_unbalanced_text() -> None:
    with pytest.raises(fc.InputError):
        fc.parse_sexpr("(a (b)")
    with pytest.raises(fc.InputError):
        fc.parse_sexpr("(a))")


def test_footprints_are_read_from_both_text_formats(tmp_path: Path) -> None:
    old = (
        '(footprint "R:R" (layer "B.Cu") (fp_text reference "R7" (at 0 0))'
        ' (fp_text value "10k" (at 0 1)) (attr smd))'
    )
    board = write_board(tmp_path / "b.kicad_pcb", [footprint("C1", "100n"), old])
    fps = fc.read_footprints(board)
    assert [(f.ref, f.value, f.layer, sorted(f.attrs)) for f in fps] == [
        ("C1", "100n", "F.Cu", ["smd"]),
        ("R7", "10k", "B.Cu", ["smd"]),
    ]


def test_exclusion_rules() -> None:
    def fpr(ref: str, lib: str = "R:R", attrs: tuple[str, ...] = ("smd",)) -> fc.Footprint:
        return fc.Footprint(ref, "v", lib, "F.Cu", frozenset(attrs))

    assert fc.exclusion_reason(fpr("R1")) is None
    assert "through-hole" in str(fc.exclusion_reason(fpr("J1", attrs=("through_hole",))))
    assert fc.exclusion_reason(fpr("C4", attrs=("smd", "dnp"))) == "do not populate"
    assert fc.exclusion_reason(fpr("TP3")) == "test point"
    assert fc.exclusion_reason(fpr("FID2")) == "fiducial"
    assert fc.exclusion_reason(fpr("X1", lib="MountingHole:MH_M2")) == "mounting hole"
    assert fc.exclusion_reason(fpr("H3")) == "mounting hole"
    assert "excluded" in str(fc.exclusion_reason(fpr("L1", attrs=("smd", "exclude_from_bom"))))
    assert fc.exclusion_reason(fpr("Y1", attrs=())) == "not an SMD footprint"


def test_stand_in_board_classification() -> None:
    """The stored two-sided board (P1 stand-in): J1 is the only through-hole part; C4, C32 DNP."""
    _, excluded = fc.classify(fc.read_footprints(SPIKE / "board" / "busy_light_spike.kicad_pcb"))
    assert {r for r, why in excluded.items() if "through-hole" in why} == {"J1"}
    assert {r for r, why in excluded.items() if why == "do not populate"} == {"C4", "C32"}
    assert {r for r in excluded if r.startswith("TP")} == {f"TP{i}" for i in range(1, 7)}


# ------------------------------------------------------------------------------------------ gerbers
def test_gerber_outline_and_round_cutout() -> None:
    segs = fc.gerber_segments(GERBER)
    assert fc.inside(10.0, 10.0, segs)
    assert not fc.inside(25.0, 30.0, segs)  # inside the round cut-out
    assert fc.inside(25.0, 36.0, segs)  # just outside the cut-out (radius 5)
    assert not fc.inside(60.0, 10.0, segs)
    assert not fc.inside(10.0, -1.0, segs)


def test_gerber_clockwise_quarter_arc_stays_on_its_circle() -> None:
    text = (
        "%FSLAX46Y46*%\n%MOMM*%\nD10*\nG75*\nX0Y10000000D02*\n"
        "G02X10000000Y0I0J-10000000D01*\nM02*\n"
    )
    segs = fc.gerber_segments(text)
    pts = [(s[0], s[1]) for s in segs] + [(segs[-1][2], segs[-1][3])]
    assert all((x * x + y * y) ** 0.5 == pytest.approx(10.0) for x, y in pts)
    assert min(min(x, y) for x, y in pts) == pytest.approx(0.0, abs=1e-9)  # cw +y to +x: quadrant 1


def test_gerber_inch_units_and_missing_format() -> None:
    segs = fc.gerber_segments("%FSLAX24Y24*%\n%MOIN*%\nX0Y0D02*\nX10000Y0D01*\nM02*\n")
    assert len(segs) == 1
    assert segs[0] == pytest.approx((0.0, 0.0, 25.4, 0.0))
    with pytest.raises(fc.InputError):
        fc.gerber_segments("X0Y0D02*\n")


# ------------------------------------------------------------------------------------------- checks
def test_good_package_passes_every_check(tmp_path: Path) -> None:
    res, lines = check(tmp_path)
    assert all(r.ok for r in res.values()), [r for r in res.values() if not r.ok]
    assert lines == ["  U5: allowed (listed)"]


def test_bottom_layer_row_fails(tmp_path: Path) -> None:
    cpl = [*CPL_ROWS[:-1], ("U5", 14.0, 10.0, "B")]
    res, _ = check(tmp_path, cpl=cpl)
    assert not res["cpl_top_layer"].ok
    assert "U5" in res["cpl_top_layer"].detail


def test_point_outside_the_panel_or_in_a_cutout_fails(tmp_path: Path) -> None:
    cpl = [*CPL_ROWS[:-2], ("C1", 25.0, 30.0, "T"), ("U5", 70.0, 10.0, "T")]
    res, _ = check(tmp_path, cpl=cpl)
    assert not res["cpl_inside_panel"].ok
    assert "C1, U5" in res["cpl_inside_panel"].detail


def test_bom_and_cpl_must_agree(tmp_path: Path) -> None:
    res, _ = check(tmp_path, cpl=CPL_ROWS[:-1])
    assert not res["bom_equals_cpl"].ok
    res, _ = check(tmp_path, cpl=[*CPL_ROWS, ("C1", 11.0, 11.0, "T")])
    assert not res["bom_equals_cpl"].ok
    assert not res["assembled_refs_once"].ok  # C1 twice


def test_assembled_ref_missing_from_the_order_fails(tmp_path: Path) -> None:
    res, _ = check(tmp_path, bom=BOM_ROWS[:-1], cpl=CPL_ROWS[:-1])
    assert not res["assembled_refs_once"].ok
    assert "not in the BOM: U5" in res["assembled_refs_once"].detail


def test_excluded_refs_must_not_be_ordered(tmp_path: Path) -> None:
    bom = [*BOM_ROWS, ("USB-C", "J1", "USB_C", "C7095263"), ("DNP spare", "C4", "C_1206", "")]
    cpl = [*CPL_ROWS, ("J1", 20.0, 20.0, "T"), ("C4", 21.0, 20.0, "T")]
    res, _ = check(tmp_path, bom=bom, cpl=cpl)
    assert not res["no_excluded_refs"].ok
    assert "C4 (do not populate)" in res["no_excluded_refs"].detail
    assert "J1 (through-hole" in res["no_excluded_refs"].detail


def test_ref_that_is_not_on_the_board_fails(tmp_path: Path) -> None:
    bom = [*BOM_ROWS, ("1k", "R99", "R_0603", "C21190")]
    cpl = [*CPL_ROWS, ("R99", 20.0, 20.0, "T")]
    res, _ = check(tmp_path, bom=bom, cpl=cpl)
    assert not res["assembled_refs_once"].ok
    assert "not on the board: R99" in res["assembled_refs_once"].detail


def test_ilim_resistors_need_0p1_percent(tmp_path: Path) -> None:
    bom = [("27.7k 1%", *BOM_ROWS[2][1:]) if r[1] == "R_ILIM3" else r for r in BOM_ROWS]
    res, _ = check(tmp_path, bom=bom)
    assert not res["ilim_0p1_percent"].ok
    assert "R_ILIM3='27.7k 1%'" in res["ilim_0p1_percent"].detail


def test_missing_lcsc_fails_unless_allowed(tmp_path: Path) -> None:
    res, lines = check(tmp_path, allowed={})
    assert not res["lcsc_numbers"].ok
    assert lines == ["  U5: NOT ALLOWED"]
    res, lines = check(tmp_path, allowed={"U5": "listed", "R22": "not on this board"})
    assert res["lcsc_numbers"].ok
    assert "  note: R22 is allowed but has no missing LCSC number here" in lines


# -------------------------------------------------------------------------------- missing-LCSC list
def test_missing_list_format(tmp_path: Path) -> None:
    p = tmp_path / "list.txt"
    p.write_text(
        "# comment\n\nU5   reason one  # trailing comment\nR22 reason two\n", encoding="utf-8"
    )
    assert fc.read_missing_list(p) == {"U5": "reason one", "R22": "reason two"}
    p.write_text("U5\n", encoding="utf-8")
    with pytest.raises(fc.InputError, match="no reason"):
        fc.read_missing_list(p)
    p.write_text("U5 a\nU5 b\n", encoding="utf-8")
    with pytest.raises(fc.InputError, match="twice"):
        fc.read_missing_list(p)


def test_committed_missing_list_matches_sourcing_and_the_board() -> None:
    """Every listed ref (except R22, added by plan 08 step 3) is on the board, and its value has an
    MPN but no LCSC number in sourcing.py: a number added there makes this test ask for the list
    update."""
    listed = fc.read_missing_list(ROOT / "scripts" / "fab_missing_lcsc.txt")
    assert set(listed) == {"R22", "U5", "U6", "U3", "U4", "U10", "U11", "U13"}
    p1 = SPIKE / "board-p1" / "busy_light_spike.kicad_pcb"
    board = p1 if p1.exists() else SPIKE / "board" / "busy_light_spike.kicad_pcb"
    values = {f.ref: f.value for f in fc.read_footprints(board)}
    sourcing = load("sourcing", SPIKE / "src" / "sourcing.py").SOURCING
    for ref in set(listed) - ({"R22"} - set(values)):
        entry = sourcing[values[ref]]
        assert entry["MPN"], ref
        assert entry["LCSC"] == "", ref


# ------------------------------------------------------------------------------------------ compare
def make_build(d: Path, stamp: str, extra: str = "") -> Path:
    d.mkdir()
    (d / "a.gbr").write_text(
        f"G04 #@! TF.CreationDate,{stamp}*\n"
        f"G04 Created by KiCad (PCBNEW 10.0.8) date {stamp}*\nX1Y1D01*{extra}\n",
        encoding="utf-8",
    )
    (d / "p.drl").write_text(
        f"M48\n; DRILL file KiCad 10.0.8 date {stamp}\nT1C0.2\n", encoding="utf-8"
    )
    (d / "drc.json").write_text(
        json.dumps({"date": stamp, "violations": []}, indent=1), encoding="utf-8"
    )
    (d / "x.pdf").write_bytes(b"%PDF-1.5\n/CreationDate (D:" + stamp.encode() + b")\nstream\n")
    (d / "r.rpt").write_text(
        f"Drill report for panel.kicad_pcb\nCreated on {stamp}\n", encoding="utf-8"
    )
    with zipfile.ZipFile(d / "g.zip", "w") as zf:
        info = zipfile.ZipInfo("gerber/a.gbr", date_time=(2026, 1, 1, 0, 0, int(stamp[-2:]) % 60))
        zf.writestr(info, (d / "a.gbr").read_bytes())
    doc = fp.manifest(d, {}, {"kicad": "10.0.8"}, "abc1234")
    (d / "manifest.json").write_text(json.dumps(doc), encoding="utf-8")
    return d


def test_builds_that_differ_only_in_dates_are_equal(tmp_path: Path) -> None:
    a = make_build(tmp_path / "a", "2026-11-18T06:09:29")
    b = make_build(tmp_path / "b", "2026-11-19T07:10:31")
    assert (a / "g.zip").read_bytes() != (b / "g.zip").read_bytes()
    assert (a / "manifest.json").read_bytes() != (b / "manifest.json").read_bytes()
    assert fc.compare_dirs(a, b) == []


def test_content_change_and_missing_file_are_found(tmp_path: Path) -> None:
    a = make_build(tmp_path / "a", "2026-11-18T06:09:29")
    b = make_build(tmp_path / "b", "2026-11-18T06:09:29", extra="X2Y2D01*")
    diffs = fc.compare_dirs(a, b)
    assert "a.gbr: content differs" in diffs
    assert "g.zip:gerber/a.gbr: content differs" in diffs
    assert any(d.startswith("manifest.json") for d in diffs)
    (b / "a.gbr").unlink()
    assert f"only in {a}: a.gbr" in fc.compare_dirs(a, b)


def test_date_lines_are_the_only_lines_removed() -> None:
    data = b'x\n"date": "2026"\nG04 Created by KiCad (PCBNEW 10.0.8) date 2026*\nupdate rate\n'
    assert fc.normalized(data) == b"x\nupdate rate\n"


# ---------------------------------------------------------------------------------------------- CLI
def test_cli_exit_codes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    out = write_package(tmp_path / "pkg")
    board = write_board(tmp_path / "b.kicad_pcb")
    lst = tmp_path / "list.txt"
    lst.write_text("U5 no number yet\n", encoding="utf-8")
    assert fc.main([str(out), str(board), "--missing-lcsc-file", str(lst)]) == 0
    assert "RESULT: PASS" in capsys.readouterr().out
    assert fc.main([str(out), str(board), "--allow-missing-lcsc", "U5"]) == 0
    assert fc.main([str(out), str(board)]) == 1
    assert "RESULT: FAIL (lcsc_numbers)" in capsys.readouterr().out
    (out / fc.CPL_FILE).unlink()
    assert fc.main([str(out), str(board)]) == 2  # noqa: PLR2004
    assert fc.main(["--compare", str(tmp_path / "pkg"), str(tmp_path / "nope")]) == 2  # noqa: PLR2004


# ----------------------------------------------------------------------------------- fab_package.py
def test_full_bom_gets_the_library_column(tmp_path: Path) -> None:
    src = tmp_path / "in.csv"
    src.write_text(
        '"Refs","Value","DNP"\n"C4,C32","DNP spare","DNP"\n"R1","10k",""\n', encoding="utf-8"
    )
    assert fp.full_bom(src, tmp_path / "out.csv") == 2  # noqa: PLR2004
    rows = list(csv.reader(io.StringIO((tmp_path / "out.csv").read_text(encoding="utf-8"))))
    assert rows[0] == ["Refs", "Value", "DNP", "JLCPCB library"]
    assert rows[1] == ["C4,C32", "DNP spare", "DNP", "not known"]


def test_ignore_refs_leave_pos_excluded_footprints_to_kikit(tmp_path: Path) -> None:
    refs, reasons = fp.ignore_refs(write_board(tmp_path / "b.kicad_pcb"))
    assert refs == ["C4", "H1", "J1"]
    assert set(reasons) == {"C4", "H1", "J1", "TP1", "FID1"}


def test_manifest_lists_every_file_but_itself(tmp_path: Path) -> None:
    out = write_package(tmp_path / "pkg")
    (out / "manifest.json").write_text("{}", encoding="utf-8")
    board = write_board(tmp_path / "b.kicad_pcb")
    doc = fp.manifest(out, {"board": board}, {"kicad": "10.0.8", "kikit": "1.8.1"}, "v1-2-gabc")
    files = doc["files"]
    assert isinstance(files, dict)
    assert sorted(files) == [fc.GERBER_ZIP, fc.BOM_FILE, fc.CPL_FILE]
    assert doc["git_describe"] == "v1-2-gabc"
    inputs = doc["inputs"]
    assert isinstance(inputs, dict)
    assert inputs["board"]["sha256"] == fp.sha256(board.read_bytes())


def test_panel_preset_has_the_decided_values() -> None:
    """Plan 08 4.5: 1 x 1 board, 5 mm rails top and bottom, annotation tabs with mouse bites, three
    fiducials, JLC tooling holes (size and mask of KiKit's jlcTooling preset), fixed ids so that the
    output is reproducible."""
    preset = json.loads((ROOT / "scripts" / "panel_p1.json").read_text(encoding="utf-8"))
    assert (preset["layout"]["rows"], preset["layout"]["cols"]) == (1, 1)
    assert preset["framing"] == {"type": "railstb", "width": "5mm", "vspace": "2mm"}
    assert preset["tabs"]["type"] == "annotation"
    assert preset["cuts"]["type"] == "mousebites"
    assert preset["fiducials"]["type"] == "3fid"
    assert (preset["tooling"]["size"], preset["tooling"]["soldermaskmargin"]) == (
        "1.152mm",
        "1.3mm",
    )
    assert preset["debug"]["deterministic"] is True
