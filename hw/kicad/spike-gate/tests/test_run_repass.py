# SPDX-License-Identifier: Apache-2.0
"""run_repass.sh: the second router pass over a cleaned-up board (2026-11-20). These tests need only sh, sha256sum and Python;
the routing itself is not run here (it needs KiCad and the pinned Freerouting jar)."""
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
SCRIPT = HERE / "run_repass.sh"
GITHUB = "f6f51bb02245e8e717f9359bd260cc9c5c0b1bc0acc8b7cb2cd5b8ffeb5de3c7"
MAVEN = "7f8c62471f46ccd165bd0e1d20096404602d56d0480af2da59f31b8c5224a976"


@unittest.skipIf(shutil.which("sha256sum") is None, "sha256sum not available")
class Guards(unittest.TestCase):
    def run_on(self, unconnected, jar=None):
        with tempfile.TemporaryDirectory() as t:
            a = Path(t)
            (a / "final.kicad_pcb").write_text("")
            (a / "drc_final.json").write_text(json.dumps({"unconnected_items": [{"items": []}] * unconnected}))
            env = {k: v for k, v in os.environ.items() if k != "FREEROUTING_JAR"}
            if jar is not None:
                env["FREEROUTING_JAR"] = str(jar)
            res = subprocess.run(["sh", str(SCRIPT), str(a)], env=env, capture_output=True, text=True, check=False)
            return res.returncode, res.stdout + res.stderr, sorted(p.name for p in a.iterdir())

    def test_nothing_open_does_nothing(self):
        rc, out, files = self.run_on(0)
        self.assertEqual(rc, 0)
        self.assertIn("nothing open", out)
        self.assertEqual(files, ["drc_final.json", "final.kicad_pcb"])          # no repass/ folder, no jar needed

    def test_missing_jar_exits_1(self):
        rc, out, _ = self.run_on(1, "/nonexistent/freerouting.jar")
        self.assertEqual(rc, 1)
        self.assertIn("FREEROUTING_JAR", out)

    def test_wrong_jar_exits_1_and_names_the_pins_of_run_pcb(self):
        with tempfile.TemporaryDirectory() as t:
            jar = Path(t) / "x.jar"
            jar.write_bytes(b"not the pinned release")
            rc, out, _ = self.run_on(1, jar)
        self.assertEqual(rc, 1)
        self.assertIn(GITHUB, out)                    # the one list of pinned jars is the JAR_SHAS line of run_pcb.sh
        self.assertIn(MAVEN, out)

    def test_usage_without_a_folder(self):
        res = subprocess.run(["sh", str(SCRIPT)], capture_output=True, text=True, check=False)
        self.assertEqual(res.returncode, 2)


class ScriptText(unittest.TestCase):
    TXT = SCRIPT.read_text(encoding="utf-8")

    def test_every_board_read_by_kicad_has_its_project_file(self):
        """2026-11-20: the first scratch version exported `in_locked.kicad_pcb` without `in_locked.kicad_pro`; KiCad then
        knows no net classes, the DSN had only kicad_default and the branch-width step stopped. Every board that a KiCad
        step reads (lock, DSN export, strict DRC, stitch, clean-up) gets the project files of its stem first."""
        uses = [(m.start(), m.group(1)) for m in re.finditer(
            r'(?:pcb_dsn\.py" (?:lock|export)|kicad_strict\.py" drc|pcb_stitch\.py") "\$R/(\w+)\.kicad_pcb"', self.TXT)]
        uses.append((self.TXT.index('pcb_fix.py" auto'), "stitched"))      # the clean-up copies the stitched project files
        self.assertGreaterEqual(len(uses), 6)
        for pos, stem in uses:
            if stem == "final":                       # final.* is copied with all its project files
                continue
            self.assertTrue("proj %s\n" % stem in self.TXT[:pos], "no project files for %s before its first use" % stem)

    def test_all_copper_is_locked_before_the_export(self):
        self.assertLess(self.TXT.index('pcb_dsn.py" lock "$R/in.kicad_pcb" "$R/in_locked.kicad_pcb"'),
                        self.TXT.index('pcb_dsn.py" export "$R/in_locked.kicad_pcb"'))

    def test_first_pass_board_kept_when_replaced(self):
        block = self.TXT[self.TXT.index('if [ "$N2" -lt "$N1" ]'):]
        self.assertIn("final_pass1", block)
        self.assertIn("drc_final_pass1.json", block)

    def test_run_pcb_calls_it_after_the_cleanup(self):
        txt = (HERE / "run_pcb.sh").read_text(encoding="utf-8")
        self.assertIn('"${REPASS:-1}" = 1', txt)
        self.assertLess(txt.index('pcb_fix.py" auto'), txt.index("run_repass.sh\" \"$A\""))


if __name__ == "__main__":
    unittest.main()
