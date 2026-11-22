# SPDX-License-Identifier: Apache-2.0
"""The python-tools job of .github/workflows/ci.yml runs every Python test, not a skip.

Since 2026-11-21 the default pytest run includes hw/sim/scripts. Its surge tests
(test_surge_supply_pin.py, HW-010) skip without ngspice; CI run 44904291971 skipped all 16 because
the ubuntu-24.04 runner does not have it. A skip in CI is a test that is not run."""

import unittest
from pathlib import Path

import yaml

WF = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "ci.yml"


class PythonToolsJob(unittest.TestCase):
    def test_ngspice_installed_before_pytest(self) -> None:
        steps = yaml.safe_load(WF.read_text(encoding="utf-8"))["jobs"]["python-tools"]["steps"]
        runs = [s.get("run", "") for s in steps]
        pytest_step = next(i for i, r in enumerate(runs) if r.strip() == "pytest")
        installs = [i for i, r in enumerate(runs) if "apt-get install" in r and "ngspice" in r]
        self.assertTrue(installs, "no apt-get install of ngspice in python-tools")
        self.assertLess(installs[0], pytest_step)


class HardwareJob(unittest.TestCase):
    """RV-016 row 26: pull requests run the spike-gate tests (board, placement rules, sourcing),
    not only fab-release.yml on main."""

    def setUp(self) -> None:
        self.job = yaml.safe_load(WF.read_text(encoding="utf-8"))["jobs"]["hardware"]
        self.runs = [s.get("run", "") for s in self.job["steps"]]

    def test_spike_gate_suite_runs(self) -> None:
        hit = [r for r in self.runs if "pytest" in r and "spike-gate" in r and " tests" in r]
        self.assertTrue(hit, self.runs)

    def test_ngspice_and_test_pins_installed_first(self) -> None:
        suite = next(i for i, r in enumerate(self.runs) if "pytest" in r and "spike-gate" in r)
        inst = next(i for i, r in enumerate(self.runs) if "requirements-fab-test.txt" in r)
        self.assertIn("ngspice", self.runs[inst])
        self.assertLess(inst, suite)

    def test_image_pinned_by_digest_like_fab_release(self) -> None:
        fab = yaml.safe_load((WF.parent / "fab-release.yml").read_text(encoding="utf-8"))
        self.assertIn("@sha256:", self.job["container"]["image"])
        self.assertEqual(self.job["container"]["image"], fab["jobs"]["build"]["container"]["image"])


if __name__ == "__main__":
    unittest.main()
