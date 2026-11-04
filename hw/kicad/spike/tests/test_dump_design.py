"""Negative tests: every kind of design change must change the semantic dump (ADR-0012 item 11)."""
import json
import re
import shutil
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
from dump_design import dump  # noqa: E402

FIX = HERE.parent / "fixtures"


@pytest.fixture
def work(tmp_path: Path) -> Path:
    for f in FIX.iterdir():
        shutil.copy(f, tmp_path / f.name)
    return tmp_path


def run(d: Path) -> dict:
    return dump(str(d / "spike.net"), str(d / "routed.kicad_pcb"), str(d / "routed.kicad_pro"))


def edit(path: Path, pattern: str, repl: str, count: int = 1) -> None:
    text = path.read_text()
    new, n = re.subn(pattern, repl, text, count=count)
    assert n >= 1, f"pattern not found: {pattern}"
    path.write_text(new)


def test_unchanged_is_stable(work: Path) -> None:
    assert run(work) == run(work)


def test_changed_net(work: Path) -> None:
    edit(work / "spike.net", r'\(name "/D1"\)', '(name "/D1X")')
    assert run(work) != dump(str(FIX / "spike.net"), str(FIX / "routed.kicad_pcb"), str(FIX / "routed.kicad_pro"))


def test_changed_value(work: Path) -> None:
    edit(work / "spike.net", r'\(value "WS2812B-2020"\)', '(value "OTHER")')
    assert run(work)["parts"]["D1"]["value"] == "OTHER"


def test_footprint_swap(work: Path) -> None:
    edit(work / "spike.net", r"LED_WS2812B-2020_PLCC4_2\.0x2\.0mm", "LED_WS2812B_PLCC4_5.0x5.0mm_P3.2mm")
    assert "5.0x5.0" in run(work)["parts"]["D1"]["footprint"]


def test_track_edit(work: Path) -> None:
    base = run(work)
    edit(work / "routed.kicad_pcb", r"\(width 0\.25\)", "(width 0.3)")
    assert run(work)["tracks"] != base["tracks"]


def test_via_edit(work: Path) -> None:
    base = run(work)
    edit(work / "routed.kicad_pcb", r"\(drill 0\.3\)", "(drill 0.35)")
    assert run(work)["vias"] != base["vias"]


def test_zone_edit(work: Path) -> None:
    base = run(work)
    edit(work / "routed.kicad_pcb", r'\(name "keepout_edge"\)', '(name "keepout_moved")')
    assert run(work)["zones"] != base["zones"]


def test_design_rule_edit(work: Path) -> None:
    base = run(work)
    pro = json.loads((work / "routed.kicad_pro").read_text())
    pro["board"]["design_settings"]["rules"]["min_track_width"] = 0.1
    (work / "routed.kicad_pro").write_text(json.dumps(pro))
    assert run(work)["design_rules"] != base["design_rules"]


def test_net_class_edit(work: Path) -> None:
    base = run(work)
    pro = json.loads((work / "routed.kicad_pro").read_text())
    pro["net_settings"]["classes"][1]["track_width"] = 0.3
    (work / "routed.kicad_pro").write_text(json.dumps(pro))
    assert run(work)["net_classes"] != base["net_classes"]


def test_stackup_edit(work: Path) -> None:
    base = run(work)
    edit(work / "routed.kicad_pcb", r"\(thickness 1\.53\)", "(thickness 1.51)")
    assert run(work)["stackup"] != base["stackup"]
