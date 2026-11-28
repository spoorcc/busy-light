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
        # HW-017 J1-to-U7 budget (owner, 2026-11-22)
        self.assertIn('if not ip["within_budget"]:', self.text)

    def test_placement_rules_are_a_gate(self) -> None:
        """RV-016 rows 11 and 12: board-p1 missed 9 placement rules and the order script passed."""
        self.assertIn('python3 "$LAYOUT" "$board_rel"', self.text)
        self.assertIn('failed+=("placement rules")', self.text)
        self.assertIn("pcb_layout_check.py", self.text)

    def test_fab_check_gets_the_owner_waivers(self) -> None:
        """RV-016 row 1: a must-place part passes only with an owner waiver; the file ships in the
        package and the manifest."""
        self.assertIn('--owner-waiver-file "$(rel "$OWNER_WAIVERS")"', self.text)
        self.assertIn('cp "$OWNER_WAIVERS" "$out/fab_owner_waivers.txt"', self.text)
        self.assertIn('--input "owner_waivers=', self.text)
        waivers = SCRIPT.parent / "fab_owner_waivers.txt"
        lines = waivers.read_text(encoding="utf-8").splitlines()
        given = [ln for ln in lines if ln.split("#")[0].strip()]
        self.assertEqual(given, [], "only the owner adds a waiver")


if __name__ == "__main__":
    unittest.main()
