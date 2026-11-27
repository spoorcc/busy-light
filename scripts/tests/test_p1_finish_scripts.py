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


# --- RV-019 pass 2 (readiness NO-GO of 2026-11-27):
# findings 1, 2, 5, 6, 8 and 15, each with a test that failed first ---

PCB_PY_FAKE = """#!/bin/sh
# stands for python3 in run_finish.sh: the three tools it calls are told apart by the script name
script=$1; shift
out=""
while [ $# -gt 0 ]; do [ "$1" = "--out" ] && out=$2; shift; done
case "$script" in
  *pcb_finish.py) [ "$FAKE_FINISH_RC" = 0 ] || { echo "finish crashed"; exit "$FAKE_FINISH_RC"; } ;;
  *kicad_strict.py) [ -n "$out" ] && echo '{"violations": []}' > "$out"
                    [ "$FAKE_DRC_RC" = 0 ] && echo "DRC OK" || echo "DRC NOT RUN: kicad-cli exit 1"
                    exit "$FAKE_DRC_RC" ;;
  *merge_drc.py) cp "$1" "$3" 2>/dev/null; exit 0 ;;
esac
exit 0
"""


def make_run(root: Path, *, prl: bool = True, first_pass_kept: bool = False) -> tuple[Path, Path]:
    a = root / "a"
    (a / "repass").mkdir(parents=True)
    for f in ("pcb", "pro", "dru") + (("prl",) if prl else ()):
        (a / f"final.kicad_{f}").write_text("x", encoding="utf-8")
    (a / "busy_light_spike.placement.json").write_text("{}", encoding="utf-8")
    (a / "run_meta.json").write_text("{}", encoding="utf-8")
    (a / "repass" / "run_meta.json").write_text("{}", encoding="utf-8")
    if first_pass_kept:
        (a / "final_pass1.kicad_pcb").write_text("x", encoding="utf-8")
    net = root / "net"
    (net / "CUSTOM.pretty").mkdir(parents=True)
    for f in ("full.kicad_sch", "sym-lib-table", "fp-lib-table", "busylight_gate.kicad_sym"):
        (net / f).write_text("x", encoding="utf-8")
    return a, net


def finish(root: Path, finish_rc: int, drc_rc: int, **kw: bool) -> subprocess.CompletedProcess[str]:
    fake = root / "fakepy"
    fake.write_text(PCB_PY_FAKE, encoding="utf-8")
    fake.chmod(0o755)
    a, net = make_run(root, **kw)
    return run(
        ["sh", str(FINISH), str(a), str(net), str(root / "w")],
        PCB_PYTHON=str(fake),
        FAKE_FINISH_RC=str(finish_rc),
        FAKE_DRC_RC=str(drc_rc),
    )


def test_finish_stops_when_a_finishing_pass_crashes(tmp_path: Path) -> None:
    res = finish(tmp_path, finish_rc=3, drc_rc=0)
    assert res.returncode != 0
    assert "finished board in" not in res.stdout


def test_finish_stops_when_the_strict_drc_did_not_run(tmp_path: Path) -> None:
    res = finish(tmp_path, finish_rc=0, drc_rc=2)
    assert res.returncode != 0
    assert "finished board in" not in res.stdout
    assert "DRC did not run" in res.stdout


def test_finish_succeeds_with_the_fakes_and_without_a_prl_file(tmp_path: Path) -> None:
    res = finish(tmp_path, finish_rc=0, drc_rc=0, prl=False)
    assert res.returncode == 0, res.stdout + res.stderr
    assert "finished board in" in res.stdout
    assert not (tmp_path / "w" / "busy_light_spike.kicad_prl").exists()


def test_finish_copies_the_second_pass_record_only_when_that_pass_was_taken(tmp_path: Path) -> None:
    taken = tmp_path / "taken"
    taken.mkdir()
    assert finish(taken, 0, 0, first_pass_kept=True).returncode == 0
    assert (taken / "w" / "repass_meta.json").exists()
    not_taken = tmp_path / "not_taken"
    not_taken.mkdir()
    assert finish(not_taken, 0, 0, first_pass_kept=False).returncode == 0
    assert not (not_taken / "w" / "repass_meta.json").exists()


def test_store_does_not_need_a_prl_file(tmp_path: Path) -> None:
    w = make_work(tmp_path, repass=False)
    (w / "busy_light_spike.kicad_prl").unlink()
    target = tmp_path / "t"
    res = run(["sh", str(STORE), str(w), str(target)])
    assert res.returncode == 0, res.stdout + res.stderr


def fake_docker(tmp_path: Path) -> Path:
    bindir = tmp_path / "bin"
    bindir.mkdir()
    (bindir / "docker").write_text('#!/bin/sh\nprintf "%s\\n" "$@"\n', encoding="utf-8")
    (bindir / "docker").chmod(0o755)
    return bindir


def run_container_with_java_link(tmp_path: Path, **env: str) -> list[str]:
    java = tmp_path / "jdk"
    (java / "conf").mkdir(parents=True)
    (java / "conf" / "java.security").symlink_to("/etc/passwd")
    res = run(
        ["sh", str(CONTAINER), "true"],
        PATH=f"{fake_docker(tmp_path)}:{os.environ['PATH']}",
        KC_JAVA_HOME=str(java),
        **env,
    )
    assert res.returncode == 0, res.stderr
    return res.stdout.splitlines()


def test_container_mounts_the_etc_target_of_java_symlinks(tmp_path: Path) -> None:
    # Debian's Java keeps its config files as symlinks into /etc/java-<n>-openjdk;
    # without that directory the JVM stops at start-up.
    # KC_ETC_PREFIX (default /etc/java) limits what is mounted.
    args = run_container_with_java_link(tmp_path, KC_ETC_PREFIX="/etc/pass")
    assert "/etc/passwd:/etc/passwd:ro" in args


def test_container_mounts_nothing_else_from_etc(tmp_path: Path) -> None:
    # RV-019 pass 3, S9: a JDK link into /etc/ssl (the CA store)
    # must not mount the host's /etc/ssl
    args = run_container_with_java_link(tmp_path)
    assert not any(a.startswith("/etc/passwd") for a in args)


def test_container_creates_its_home_before_the_command(tmp_path: Path) -> None:
    # RV-019 pass 3, S1: HOME=/tmp/kc-home did not exist,
    # so `git config --global` failed in the container
    args = run_container_with_java_link(tmp_path)
    assert any(a.startswith('mkdir -p "$HOME"') for a in args), args


@pytest.mark.parametrize("script", ["run_pcb.sh", "run_repass.sh"])
def test_router_scripts_keep_the_python_path_they_were_given(script: str) -> None:
    # run_in_kicad.sh passes numpy and scipy through PYTHONPATH (KC_PYTHONPATH);
    # the image has neither.
    lines = [
        ln
        for ln in (SPIKE / script).read_text(encoding="utf-8").splitlines()
        if ln.startswith("export PYTHONPATH=")
    ]
    assert len(lines) == 1
    res = run(["sh", "-c", f'HERE=/h\n{lines[0]}\necho "$PYTHONPATH"'], PYTHONPATH="/extra/site")
    assert res.stdout.strip() == "/h/src:/extra/site"
    res = run(["sh", "-c", f'HERE=/h\nunset PYTHONPATH\n{lines[0]}\necho "$PYTHONPATH"'])
    assert res.stdout.strip() == "/h/src"


PLACE_BEST = SPIKE / "run_place_best.sh"


def test_place_best_is_valid_shell_and_prints_usage() -> None:
    assert run(["sh", "-n", str(PLACE_BEST)]).returncode == 0
    res = run(["sh", str(PLACE_BEST)])
    assert res.returncode == USAGE_EXIT
    assert "Usage: run_place_best.sh" in res.stdout


def test_place_best_names_the_missing_netlist(tmp_path: Path) -> None:
    res = run(["sh", str(PLACE_BEST), str(tmp_path), str(tmp_path / "o")])
    assert res.returncode == 1
    assert "kicad.net" in res.stdout


def test_container_passes_the_rule_penalty_variable(tmp_path: Path) -> None:
    assert "PLACE_RULE_PEN" in run_container_with_java_link(tmp_path)
