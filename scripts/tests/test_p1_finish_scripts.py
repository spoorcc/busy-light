# SPDX-License-Identifier: Apache-2.0
"""Tests of the P1 finishing and store scripts (plan 08 R3, R5; RV-019 G3). No KiCad needed."""

import importlib.util
import json
import os
import shutil
import subprocess
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPIKE = ROOT / "hw" / "kicad" / "spike-gate"
FINISH = SPIKE / "run_finish.sh"
STORE = SPIKE / "store_p1.sh"
CONTAINER = SPIKE / "run_in_kicad.sh"
BOARD_FILES = (
    "busy_light_spike.kicad_pcb",
    "busy_light_spike.kicad_pro",
    "busy_light_spike.kicad_dru",
    "busy_light_spike.kicad_prl",
    "busy_light_spike.kicad_sch",
    "busy_light_spike.placement.json",
    "run_meta.json",
    "fp-lib-table",
    "sym-lib-table",
    "busylight_gate.kicad_sym",
)
USAGE_EXIT = 2
PASSES = 3
RESTARTS = 2


def load_merge() -> ModuleType:
    spec = importlib.util.spec_from_file_location("merge_drc", SPIKE / "src" / "merge_drc.py")
    assert spec is not None
    assert spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(args: list[str], **env: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args, capture_output=True, text=True, check=False, env={**os.environ, **env}
    )


@pytest.mark.parametrize("script", [FINISH, STORE, CONTAINER])
def test_scripts_are_valid_shell_and_executable(script: Path) -> None:
    assert run(["sh", "-n", str(script)]).returncode == 0
    assert script.stat().st_mode & 0o111


def test_finish_runs_three_passes_each_from_the_unfinished_board() -> None:
    text = FINISH.read_text(encoding="utf-8")
    assert text.count("pcb_finish.py") >= PASSES
    restarts = text.count('cp "$W/unfinished.kicad_pcb" "$B"')
    assert restarts == RESTARTS  # passes 2 and 3 restart from the unfinished board
    assert "merge_drc.py" in text
    assert "drc12.json" in text  # pass 3 carries the findings of passes 1 and 2


def test_finish_without_arguments_prints_usage_and_exits_2() -> None:
    res = run(["sh", str(FINISH)])
    assert res.returncode == USAGE_EXIT
    assert "Usage: run_finish.sh" in res.stdout


def test_finish_names_the_missing_input(tmp_path: Path) -> None:
    res = run(["sh", str(FINISH), str(tmp_path), str(tmp_path), str(tmp_path / "w")])
    assert res.returncode == USAGE_EXIT
    assert "no final.kicad_pcb" in res.stdout


def test_merge_extends_the_first_violation_list_and_keeps_its_other_keys() -> None:
    merge = load_merge().merge
    a: dict[str, Any] = {
        "violations": [{"type": "silk_overlap"}],
        "unconnected_items": [1],
        "source": "a",
    }
    b: dict[str, Any] = {"violations": [{"type": "silk_over_copper"}], "unconnected_items": []}
    out = merge(a, b)
    assert [v["type"] for v in out["violations"]] == ["silk_overlap", "silk_over_copper"]
    assert out["unconnected_items"] == [1]
    assert out["source"] == "a"
    assert len(a["violations"]) == 1  # the input is not changed


def test_merge_cli_writes_the_merged_report(tmp_path: Path) -> None:
    (tmp_path / "a.json").write_text(json.dumps({"violations": [{"type": "x"}]}), encoding="utf-8")
    (tmp_path / "b.json").write_text(json.dumps({"violations": [{"type": "y"}]}), encoding="utf-8")
    mod = load_merge()
    assert (
        mod.main(
            ["m", str(tmp_path / "a.json"), str(tmp_path / "b.json"), str(tmp_path / "o.json")]
        )
        == 0
    )
    assert [
        v["type"]
        for v in json.loads((tmp_path / "o.json").read_text(encoding="utf-8"))["violations"]
    ] == ["x", "y"]
    assert mod.main(["m"]) == USAGE_EXIT


def make_work(root: Path, repass: bool) -> Path:
    w = root / "work"
    w.mkdir()
    for f in BOARD_FILES:
        (w / f).write_text("new " + f, encoding="utf-8")
    (w / "CUSTOM.pretty").mkdir()
    (w / "CUSTOM.pretty" / "fp.kicad_mod").write_text("new fp", encoding="utf-8")
    for i in (1, 2, 3):
        (w / f"drc{i}.json").write_text(json.dumps({"pass": i}), encoding="utf-8")
    if repass:
        (w / "repass_meta.json").write_text("{}", encoding="utf-8")
    return w


def test_store_replaces_the_board_keeps_the_readme_and_renames_the_drc_reports(
    tmp_path: Path,
) -> None:
    target = tmp_path / "board-p1"
    target.mkdir()
    (target / "README.md").write_text("keep", encoding="utf-8")
    (target / "old.txt").write_text("old", encoding="utf-8")
    (target / "repass_meta.json").write_text("stale", encoding="utf-8")
    (target / "CUSTOM.pretty").mkdir()
    (target / "CUSTOM.pretty" / "gone.kicad_mod").write_text("old", encoding="utf-8")
    res = run(["sh", str(STORE), str(make_work(tmp_path, repass=False)), str(target)])
    assert res.returncode == 0, res.stdout + res.stderr
    assert (target / "README.md").read_text(encoding="utf-8") == "keep"
    assert not (target / "old.txt").exists()
    assert not (target / "repass_meta.json").exists()  # a stale second-pass record must not survive
    assert not (target / "CUSTOM.pretty" / "gone.kicad_mod").exists()
    assert (target / "CUSTOM.pretty" / "fp.kicad_mod").read_text(encoding="utf-8") == "new fp"
    assert (target / "busy_light_spike.kicad_pcb").read_text(
        encoding="utf-8"
    ) == "new busy_light_spike.kicad_pcb"
    assert json.loads((target / "drc_pass3.json").read_text(encoding="utf-8")) == {"pass": 3}


def test_store_copies_the_second_pass_record_when_it_exists(tmp_path: Path) -> None:
    target = tmp_path / "t"
    assert (
        run(["sh", str(STORE), str(make_work(tmp_path, repass=True)), str(target)]).returncode == 0
    )
    assert (target / "repass_meta.json").exists()


def test_store_refuses_an_incomplete_work_dir_and_changes_nothing(tmp_path: Path) -> None:
    w = make_work(tmp_path, repass=False)
    (w / "drc3.json").unlink()
    target = tmp_path / "t"
    target.mkdir()
    (target / "keep.txt").write_text("x", encoding="utf-8")
    res = run(["sh", str(STORE), str(w), str(target)])
    assert res.returncode == USAGE_EXIT
    assert "no drc3.json" in res.stdout
    assert (target / "keep.txt").exists()


def test_store_default_target_is_board_p1_next_to_the_script() -> None:
    assert "board-p1" in STORE.read_text(encoding="utf-8")
    assert shutil.which("sh")


def test_container_script_uses_the_image_digest_of_the_workflow() -> None:
    workflow = (ROOT / ".github" / "workflows" / "fab-release.yml").read_text(encoding="utf-8")
    digest = "kicad/kicad@sha256:3f4a01786dfbe803a65f345c3342b765db9add913f5e9448f8356793714ddc34"
    assert digest in workflow
    assert digest in CONTAINER.read_text(encoding="utf-8")


def test_container_script_without_a_command_prints_usage() -> None:
    res = run(["sh", str(CONTAINER)])
    assert res.returncode == USAGE_EXIT
    assert "Usage: run_in_kicad.sh" in res.stdout
