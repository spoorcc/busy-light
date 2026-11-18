# SPDX-License-Identifier: Apache-2.0
"""Plan 08 section 4.6: structure of .github/workflows/fab-release.yml.

Owner answer 17 of 2026-11-17; HW-008, HW-009. GitHub Actions cannot run in the assistant's
container and actionlint is not installed. This test checks the rules that the plan sets for the
workflow text: triggers, job order, least-privilege permissions, pinned actions and image,
hash-pinned tools, and when a release is touched."""

import re
import unittest
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

    def test_publish_runs_no_repository_code(self) -> None:
        """The job with write access only downloads this run's artifact and calls gh release.

        No checkout, no repository script."""
        steps = self.jobs["publish"]["steps"]
        self.assertFalse(any("uses" in s for s in steps))
        for s in steps:
            for line in s["run"].splitlines():
                cmd = line.strip()
                if cmd and not cmd.startswith(("notes=", "if ", "else", "fi")):
                    self.assertTrue(cmd.startswith("gh "), cmd)

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

    def test_build_reports_not_run_without_a_board(self) -> None:
        run = next(s["run"] for s in self.jobs["build"]["steps"] if s.get("id") == "pkg")
        self.assertIn("NOT RUN", run)
        self.assertIn('scripts/fab_p1.sh "$BOARD" p1-fab', run)
        self.assertEqual(
            self.doc["env"]["BOARD"], "hw/kicad/spike-gate/board-p1/busy_light_spike.kicad_pcb"
        )


if __name__ == "__main__":
    unittest.main()
