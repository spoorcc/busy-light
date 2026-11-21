# SPDX-License-Identifier: Apache-2.0
"""scripts/readme_facts.py counts what the READMEs quote (skill readme-refresh).

Runs on a small fixture tree, so the counting rules are fixed: a requirement is approved only by
its own Status line, a qualified ADR status counts by its first word and is marked, an image is
unused when no Markdown file links to it."""

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import readme_facts as rf

REQ = """# Hardware Requirements

- **Status:** Draft

### HW-001 One

- **Statement:** x
- **Status:** Approved (owner, 2026-11-07)

### HW-002 Two, no Status line of its own

- **Rationale:** mentions Approved in the text

#### HW-003 Three

- **Status:** Approved
"""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class Fixture(unittest.TestCase):
    root: Path

    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(tempfile.mkdtemp())
        r = cls.root
        write(r / "docs/requirements/hw.md", REQ)
        write(r / "docs/decisions/ADR-0001-a.md", "# A\n\n- **Status:** Accepted (by the owner)\n")
        write(
            r / "docs/decisions/ADR-0002-b.md",
            "# B\n\n- **Status:** Accepted for the prototype only\n",
        )
        write(
            r / "docs/decisions/ADR-0003-c.md",
            "# C\n\n- **Status:** Proposed (the owner decides)\n",
        )
        write(r / "docs/decisions/ADR-0004-d.md", "# D\n\n- **Status:** Superseded by ADR-0003\n")
        write(r / "docs/reviews/RV-001-x-goldfish.md", "# RV-001\n")
        write(r / "docs/reviews/RV-002-y.md", "# RV-002\n")
        write(r / "docs/plans/01-a.md", "# Plan\n\n- **Status:** Draft (x)\n")
        write(
            r / "sw/app/tests/gate/src/main.c", "ZTEST(gate, test_a)\n{\n}\nZTEST(gate, test_b)\n"
        )
        write(r / "docs/verification/reports/images/shown.png", "")
        write(r / "docs/verification/reports/images/unused.png", "")
        write(r / "README.md", '<img src="docs/verification/reports/images/shown.png" alt="x">\n')

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.root)

    def test_requirements_approved_by_own_status_only(self) -> None:
        req = rf.requirements(self.root)["hw.md"]
        self.assertEqual(req["entries"], 3)
        self.assertEqual(req["approved"], ["HW-001", "HW-003"])

    def test_adrs_by_first_word_and_qualified_marked(self) -> None:
        self.assertEqual(
            rf.adrs(self.root),
            {
                "Accepted": ["ADR-0001", "ADR-0002*"],
                "Proposed": ["ADR-0003"],
                "Superseded": ["ADR-0004*"],
            },
        )

    def test_reviews_plans_and_host_tests(self) -> None:
        self.assertEqual(rf.reviews(self.root), ["RV-001", "RV-002"])
        self.assertEqual(rf.plans(self.root), {"01-a.md": "Draft (x)"})
        self.assertEqual(rf.host_tests(self.root), {"gate": 2})

    def test_unused_images(self) -> None:
        self.assertEqual(rf.unused_images(self.root), ["unused.png"])

    def test_text_output_has_the_totals(self) -> None:
        text = rf.show(rf.collect(self.root, with_git=False))
        self.assertIn("Requirements: 3 entries, 2 approved", text)
        self.assertIn("ADRs: 4 records", text)
        self.assertIn("Review records: 2 (last RV-002)", text)


class OnTheRepository(unittest.TestCase):
    def test_readme_ages_list_the_root_readme(self) -> None:
        root = Path(__file__).resolve().parents[2]
        if subprocess.run(
            ["git", "-C", str(root), "rev-parse"], capture_output=True, check=False
        ).returncode:
            self.skipTest("not a git checkout")
        ages = rf.readme_ages(root)
        self.assertIn("README.md", ages)
        self.assertRegex(ages["README.md"]["last_commit"], r"^\d{4}-\d{2}-\d{2}$")


if __name__ == "__main__":
    unittest.main()
