# SPDX-License-Identifier: Apache-2.0
"""Plan 06 T5: run_pcb.sh exits 1 when FREEROUTING_JAR is missing or has the wrong sha256. Needs only sh and sha256sum."""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "run_pcb.sh"


@unittest.skipIf(shutil.which("sha256sum") is None, "sha256sum not available")
class JarCheck(unittest.TestCase):
    def run_script(self, jar):
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            (t / "in").mkdir()
            (t / "in" / "kicad.net").write_text("")
            env = dict(os.environ, FREEROUTING_JAR=str(jar))
            res = subprocess.run(["sh", str(SCRIPT), str(t / "in"), str(t / "out"), "4"], env=env,
                                 capture_output=True, text=True, check=False)
            return res.returncode, res.stdout + res.stderr

    def test_missing_jar_exits_1(self):
        rc, out = self.run_script("/nonexistent/freerouting.jar")
        self.assertEqual(rc, 1)
        self.assertIn("FREEROUTING_JAR", out)

    def test_wrong_hash_exits_1(self):
        with tempfile.TemporaryDirectory() as t:
            jar = Path(t) / "x.jar"
            jar.write_bytes(b"not the pinned release")
            rc, out = self.run_script(jar)
        self.assertEqual(rc, 1)
        self.assertIn("sha256", out)


class PinnedHashes(unittest.TestCase):
    """Owner answer 8 of 2026-11-17: the GitHub release jar and the Maven Central executable jar of v2.5.0 are both pinned."""
    GITHUB = "f6f51bb02245e8e717f9359bd260cc9c5c0b1bc0acc8b7cb2cd5b8ffeb5de3c7"
    MAVEN = "7f8c62471f46ccd165bd0e1d20096404602d56d0480af2da59f31b8c5224a976"

    def test_both_hashes_pinned(self):
        text = SCRIPT.read_text()
        self.assertIn(self.GITHUB, text)
        self.assertIn(self.MAVEN, text)

    @unittest.skipUnless(os.environ.get("FREEROUTING_JAR"), "FREEROUTING_JAR not set")
    def test_given_jar_is_accepted(self):
        """With a real pinned jar the script passes the jar check and stops later (empty netlist)."""
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            (t / "in").mkdir()
            (t / "in" / "kicad.net").write_text("")
            res = subprocess.run(["sh", str(SCRIPT), str(t / "in"), str(t / "out"), "4"], env=dict(os.environ),
                                 capture_output=True, text=True, check=False)
        self.assertNotIn("sha256 is not the pinned", res.stdout + res.stderr)


class PlanesArgument(unittest.TestCase):
    """Plan 06 A-8: run_pcb.sh stops before the slow build when the planes argument is invalid."""

    def run_planes(self, layers, planes):
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            (t / "in").mkdir()
            (t / "in" / "kicad.net").write_text("")
            env = {k: v for k, v in os.environ.items() if k != "FREEROUTING_JAR"}
            res = subprocess.run(["sh", str(SCRIPT), str(t / "in"), str(t / "out"), layers, planes], env=env,
                                 capture_output=True, text=True, check=False)
            return res.returncode, res.stdout + res.stderr

    def test_unknown_value_exits_1(self):
        rc, out = self.run_planes("4", "inner2")
        self.assertEqual(rc, 1)
        self.assertIn("planes", out)

    def test_inner_needs_four_layers(self):
        rc, out = self.run_planes("2", "inner")
        self.assertEqual(rc, 1)
        self.assertIn("4 layers", out)


if __name__ == "__main__":
    unittest.main()
