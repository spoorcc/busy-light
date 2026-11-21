# SPDX-License-Identifier: Apache-2.0
"""README images: every local image a README shows exists; the P1 images are committed and shown.

The images are tool exports (diagrams-as-code rule 9). hw/kicad/spike-gate/render_p1_images.sh
writes the P1 board and panel images into docs/verification/reports/images; the root README and
board-p1/README.md show them. A renamed or missing file would leave a broken image on the project
page without any other check failing."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
READMES = [
    ROOT / "README.md",
    ROOT / "hw/kicad/spike-gate/board-p1/README.md",
    ROOT / "hw/kicad/spike-gate/board/README.md",
]
RENDER = ROOT / "hw/kicad/spike-gate/render_p1_images.sh"
IMAGES = ROOT / "docs/verification/reports/images"
LINK = re.compile(
    r"""(?:src|href)="([^"]+)"|!\[[^\]]*\]\(([^)\s]+)\)|\]\(([^)\s]+\.(?:png|svg|jpg))\)"""
)


def local_images(readme: Path) -> list[Path]:
    out = []
    for m in LINK.finditer(readme.read_text(encoding="utf-8")):
        ref = next(g for g in m.groups() if g)
        if re.match(r"[a-z]+:", ref) or not re.search(r"\.(png|svg|jpg)$", ref):
            continue  # web links (badges) and links to documents
        out.append((readme.parent / ref).resolve())
    return out


class ReadmeImages(unittest.TestCase):
    def test_every_shown_image_exists(self) -> None:
        for readme in READMES:
            images = local_images(readme)
            with self.subTest(readme=readme.name):
                missing = [str(p.relative_to(ROOT)) for p in images if not p.is_file()]
                self.assertEqual(missing, [])

    def test_p1_images_are_committed_and_shown(self) -> None:
        text = RENDER.read_text(encoding="utf-8")
        names = sorted(set(re.findall(r'"\$OUT/(p1-[a-z0-9-]+\.png)"', text)))
        self.assertEqual(len(names), 6, names)
        shown = {p.name for p in local_images(ROOT / "README.md")}
        for name in names:
            with self.subTest(image=name):
                self.assertTrue((IMAGES / name).is_file())
                self.assertIn(name, shown)

    def test_board_p1_readme_shows_the_panel(self) -> None:
        shown = {p.name for p in local_images(ROOT / "hw/kicad/spike-gate/board-p1/README.md")}
        self.assertIn("p1-panel-top3d.png", shown)


if __name__ == "__main__":
    unittest.main()
