# SPDX-License-Identifier: Apache-2.0
"""Plan 08 section 4.6: structure of .github/workflows/fab-release.yml.

Owner answer 17 of 2026-11-17; HW-008, HW-009. GitHub Actions cannot run in the assistant's
container and actionlint is not installed. This test checks the rules that the plan sets for the
workflow text: triggers, job order, least-privilege permissions, pinned actions and image,
hash-pinned tools, and when a release is touched."""

import ast
import re
import sys
import unittest
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
WF = ROOT / ".github" / "workflows" / "fab-release.yml"


def load() -> dict[Any, Any]:
    doc: dict[Any, Any] = yaml.safe_load(WF.read_text(encoding="utf-8"))
    # PyYAML reads the bare key `on` as the boolean True (YAML 1.1)
    doc["on"] = doc.pop(True, doc.get("on"))
    return doc


def module_level(tree: ast.AST) -> Iterator[ast.AST]:
    """Nodes that run when the module is loaded: every node except the bodies of functions."""
    todo = [tree]
    while todo:
        node = todo.pop()
        yield node
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda):
            todo.extend(ast.iter_child_nodes(node))


class FabReleaseWorkflow(unittest.TestCase):
    doc: dict[Any, Any]
    jobs: dict[str, Any]
    text: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = load()
        cls.jobs = cls.doc["jobs"]
        cls.text = WF.read_text(encoding="utf-8")

    def test_triggers(self) -> None:
        on = self.doc["on"]
        self.assertEqual(on["push"]["branches"], ["main"])
        self.assertEqual(on["release"]["types"], ["published"])
        self.assertIn("workflow_dispatch", on)
        # RV-016 row 27: the build path runs on pull requests too (never publish, see below)
        self.assertIn(".github/workflows/fab-release.yml", on["pull_request"]["paths"])
        self.assertIn("hw/kicad/spike-gate/**", on["pull_request"]["paths"])

    def test_job_order(self) -> None:
        self.assertEqual(set(self.jobs), {"test", "build", "publish"})
        self.assertEqual(self.jobs["build"]["needs"], "test")
        self.assertEqual(self.jobs["publish"]["needs"], "build")

    def test_only_publish_can_write(self) -> None:
        self.assertEqual(self.doc["permissions"], {"contents": "read"})
        self.assertNotIn("permissions", self.jobs["test"])
        self.assertNotIn("permissions", self.jobs["build"])
        self.assertEqual(
            self.jobs["publish"]["permissions"], {"contents": "write", "actions": "read"}
        )

    def test_publish_needs_board_passing_gates_and_no_manual_run(self) -> None:
        cond = self.jobs["publish"]["if"]
        self.assertIn("needs.build.outputs.has_board == 'true'", cond)
        self.assertIn("needs.build.outputs.gates_ok == 'true'", cond)
        self.assertIn("github.event_name != 'workflow_dispatch'", cond)
        self.assertIn("github.event_name != 'pull_request'", cond)

    def test_build_fails_after_the_upload_when_a_gate_failed(self) -> None:
        """RV-016 row 27: exit 1 of fab_p1.sh left the build green and skipped publish silently."""
        steps = self.jobs["build"]["steps"]
        names = [s.get("name", s.get("uses", "")) for s in steps]
        fail = names.index("Fail when a gate failed (the package above is for diagnosis only)")
        uploads = [i for i, s in enumerate(steps) if "upload-artifact" in s.get("uses", "")]
        self.assertTrue(uploads)
        self.assertLess(max(uploads), fail)
        self.assertIn("gates_ok != 'true'", steps[fail]["if"])
        self.assertIn("exit 1", steps[fail]["run"])

    def test_release_notes_list_missing_parts_and_waivers(self) -> None:
        """RV-014 readiness B2 and RV-016 row 1: the notes print the missing-LCSC list and the
        owner waivers; they are made in the build job (no write token)."""
        build = "\n".join(s.get("run", "") for s in self.jobs["build"]["steps"])
        self.assertIn("scripts/fab_release_notes.sh p1-fab", build)
        notes = (ROOT / "scripts" / "fab_release_notes.sh").read_text(encoding="utf-8")
        for name in ("fab_missing_lcsc.txt", "fab_owner_waivers.txt", "fab_check.txt"):
            self.assertIn(name, notes)
        publish = "\n".join(s["run"] for s in self.jobs["publish"]["steps"])
        self.assertEqual(publish.count("p1-fab-notes/notes.md"), 2)

    def test_a_published_release_is_never_overwritten(self) -> None:
        steps = {s["name"]: s for s in self.jobs["publish"]["steps"]}
        run = steps["Attach the package to the published release"]["run"]
        self.assertNotIn("--clobber", run)
        self.assertIn("--json assets", run)

    def test_publish_runs_no_repository_code(self) -> None:
        """The job with write access only downloads this run's artifact and calls gh release.

        No checkout, no repository script."""
        steps = self.jobs["publish"]["steps"]
        self.assertFalse(any("uses" in s for s in steps))
        shell = ("#", "n=", "if ", "else", "fi", "{ echo", "gh ")
        for s in steps:
            for line in s["run"].splitlines():
                cmd = line.strip()
                if cmd:
                    self.assertTrue(cmd.startswith(shell), cmd)
                    self.assertNotIn("scripts/", cmd)
                    self.assertNotIn("python", cmd)

    def test_draft_only_for_push_and_fab_latest_release_is_ignored(self) -> None:
        steps = {s["name"]: s for s in self.jobs["publish"]["steps"]}
        draft = steps["Refresh the draft release fab-latest (push to main)"]
        self.assertEqual(draft["if"], "github.event_name == 'push'")
        self.assertIn("--draft", draft["run"])
        self.assertIn("gh release upload fab-latest p1-fab/* --clobber", draft["run"])
        self.assertEqual(
            steps["Attach the package to the published release"]["if"],
            "github.event_name == 'release'",
        )
        self.assertIn("tag_name != 'fab-latest'", self.jobs["test"]["if"])

    def test_actions_pinned_by_sha(self) -> None:
        uses = re.findall(r"uses:\s*(\S+)", self.text)
        self.assertTrue(uses)
        for u in uses:
            self.assertRegex(u, r"^[\w.-]+/[\w.-]+@[0-9a-f]{40}$", u)

    def test_image_by_digest_and_equal_in_all_container_jobs(self) -> None:
        images = {j: self.jobs[j]["container"]["image"] for j in ("test", "build")}
        self.assertEqual(len(set(images.values())), 1, images)
        self.assertRegex(images["test"], r"^kicad/kicad@sha256:[0-9a-f]{64}$")

    def test_tools_installed_with_hashes(self) -> None:
        installs = [line for line in self.text.splitlines() if "pip install" in line]
        self.assertTrue(installs)
        for line in installs:
            self.assertIn("--require-hashes", line)
        for name in ("requirements-fab.txt", "requirements-fab-test.txt"):
            req = (ROOT / "scripts" / name).read_text(encoding="utf-8")
            pins = [r for r in req.splitlines() if r and not r.startswith("#")]
            self.assertTrue(pins, name)
            for r in pins:
                self.assertRegex(r, r"^[A-Za-z0-9_.-]+==\S+ --hash=sha256:[0-9a-f]{64}$", (name, r))

    def test_fab_requirements_cover_what_fab_p1_runs(self) -> None:
        """The build job installs only requirements-fab.txt and runs scripts/fab_p1.sh. Every
        third-party module that the Python files of fab_p1.sh import (and the local modules
        they import) is pinned there, apart from pcbnew and PIL, which the kicad/kicad:10.0 image
        has. Until 2026-11-21 scipy (pcb_power_check.py) was pinned only in
        requirements-fab-test.txt, so the build job would have stopped at the power check.
        Only imports that run when a module is loaded count: an import inside a function (kiutils
        in lib_tables.py, "not needed by the board side") is not executed by these scripts
        (pcb_layout_check.py ran without kiutils in the image on 2026-11-22)."""
        fab = (ROOT / "scripts" / "fab_p1.sh").read_text(encoding="utf-8")
        paths = re.findall(r"\$ROOT/([\w/.-]+\.py)", fab) + re.findall(r"\b(scripts/\w+\.py)", fab)
        todo = [ROOT / p for p in sorted(set(paths))]
        self.assertGreaterEqual(len(todo), 6, todo)
        seen: set[Path] = set()
        third_party: set[str] = set()
        while todo:
            path = todo.pop()
            if path in seen:
                continue
            seen.add(path)
            for node in module_level(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    names = [node.module]
                else:
                    continue
                for top in (n.split(".")[0] for n in names):
                    local = path.parent / f"{top}.py"
                    if local.is_file():
                        todo.append(local)
                    elif top not in sys.stdlib_module_names:
                        third_party.add(top)
        req = (ROOT / "scripts" / "requirements-fab.txt").read_text(encoding="utf-8")
        pinned = {r.split("==")[0].lower() for r in req.splitlines() if "==" in r}
        missing = sorted(third_party - {"pcbnew", "PIL"} - pinned)
        self.assertEqual(missing, [])

    def test_pip_comes_from_apt_before_it_is_used(self) -> None:
        """The kicad/kicad:10.0 image has no pip (checked 2026-11-20: `pip: not found`,
        `No module named pip`); a job that runs `pip install` first installs python3-pip
        with apt."""
        for name, job in self.jobs.items():
            runs = [s.get("run", "") for s in job.get("steps", [])]
            first_pip = next((i for i, r in enumerate(runs) if "pip install" in r), None)
            if first_pip is None:
                continue
            before = "\n".join(runs[: first_pip + 1])
            self.assertRegex(before, r"apt-get install[^\n]*python3-pip", name)
            self.assertLess(before.index("python3-pip"), before.index("pip install"), name)

    def test_pip_leaves_the_debian_packages_alone(self) -> None:
        """CI run 44827760397 (2026-11-20): pip tried to uninstall Debian's typing_extensions
        4.13.2 for the pinned 4.16.0 and stopped (`uninstall-no-record-file`). Every install
        uses --ignore-installed: the pins go to /usr/local, which comes first on sys.path."""
        installs = [line for line in self.text.splitlines() if "pip install" in line]
        self.assertTrue(installs)
        for line in installs:
            self.assertIn("--ignore-installed", line)

    def test_build_reports_not_run_without_a_board(self) -> None:
        run = next(s["run"] for s in self.jobs["build"]["steps"] if s.get("id") == "pkg")
        self.assertIn("NOT RUN", run)
        self.assertIn('scripts/fab_p1.sh "$BOARD" p1-fab', run)
        self.assertEqual(
            self.doc["env"]["BOARD"], "hw/kicad/spike-gate/board-p1/busy_light_spike.kicad_pcb"
        )


if __name__ == "__main__":
    unittest.main()
