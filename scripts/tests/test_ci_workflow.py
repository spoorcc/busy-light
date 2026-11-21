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


if __name__ == "__main__":
    unittest.main()
