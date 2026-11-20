# SPDX-License-Identifier: Apache-2.0
"""scripts/ci_hw.sh checks on the stored P1 board (plan 08 section 5 step 8; HW-008, HW-010).

The script needs KiCad; the CI job `hardware` runs it on every push and pull request. These
checks read its text. Plan 08 says ci_hw.sh runs pcb_fabcheck with --no-via-in-pad on board-p1/
(owner answer 9); on 2026-11-20, when board-p1/ was first stored, it ran only the strict ERC and
DRC. The power check (full-width path rule of 2026-11-19) ran only in the order script and in
tests/test_board_p1.py, which CI runs on main only."""

import unittest
from pathlib import Path

import yaml

SCRIPT = Path(__file__).resolve().parents[1] / "ci_hw.sh"


class CiHwBoardP1(unittest.TestCase):
    text: str
    block: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = SCRIPT.read_text(encoding="utf-8")
        start = cls.text.index('for f in "${pcb[@]}"; do')
        cls.block = cls.text[start : cls.text.index("\ndone\n", start)]

    def test_fab_check_forbids_vias_in_smd_pads(self) -> None:
        calls = [ln for ln in self.block.splitlines() if "pcb_fabcheck.py" in ln]
        self.assertEqual(len(calls), 1)
        self.assertIn("--no-via-in-pad", calls[0])
        self.assertIn('"$f" == hw/kicad/spike-gate/board-p1/*', self.block)

    def test_power_check_is_a_gate(self) -> None:
        self.assertIn("pcb_power_check.py", self.block)
        self.assertIn('v.get("full_width_path") is False', self.block)
        self.assertIn("within_50mv", self.block)

    def test_ci_installs_the_power_check_packages(self) -> None:
        """The power check imports numpy and scipy; the kicad/kicad:10.0 image has neither, nor
        pip (checked 2026-11-20)."""
        wf = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "ci.yml"
        steps = yaml.safe_load(wf.read_text(encoding="utf-8"))["jobs"]["hardware"]["steps"]
        runs = [s.get("run", "") for s in steps]
        hw = next(i for i, r in enumerate(runs) if "scripts/ci_hw.sh" in r)
        before = "\n".join(runs[:hw])
        self.assertRegex(before, r"apt-get install[^\n]*python3-pip")
        for req in ("scripts/requirements-fab.txt", "scripts/requirements-fab-test.txt"):
            self.assertIn(req, before)
        installs = [ln for ln in before.splitlines() if "pip install" in ln]
        self.assertTrue(installs)
        self.assertTrue(all("--require-hashes" in ln for ln in installs))


if __name__ == "__main__":
    unittest.main()
