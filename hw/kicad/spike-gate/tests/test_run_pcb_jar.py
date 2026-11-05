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


if __name__ == "__main__":
    unittest.main()
