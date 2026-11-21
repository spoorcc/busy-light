# SPDX-License-Identifier: Apache-2.0
"""scripts/fab_p1.sh gates (plan 08 sections 4.3 and 4.6; HW-008, HW-010).

The script needs KiCad and KiKit; it runs end to end in the fab-release workflow. These checks
read its text: the no-via-in-pad flag of owner answer 9 and the power-check gate (batch p1b7,
2026-11-19: a board whose supply current ran through 0.15 mm track passed every gate of the
order script)."""

import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "fab_p1.sh"


class FabP1Gates(unittest.TestCase):
    text: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = SCRIPT.read_text(encoding="utf-8")

    def test_fab_check_forbids_vias_in_smd_pads(self) -> None:
        lines = self.text.splitlines()
        calls = [ln for ln in lines if ln.lstrip().startswith('python3 "$FABCHECK"')]
        self.assertEqual(len(calls), 1)
        self.assertIn("--no-via-in-pad", calls[0])

    def test_power_check_is_a_gate(self) -> None:
        self.assertIn('python3 "$POWER" "$board_rel" "$out/power_check.json"', self.text)
        self.assertIn('failed+=("power check")', self.text)
        self.assertIn('v.get("full_width_path") is False', self.text)
        self.assertIn("within_50mv", self.text)


if __name__ == "__main__":
    unittest.main()
