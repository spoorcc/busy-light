---
name: readme-refresh
description: Bring the READMEs and their images (P1 board and panel renders, schematic crops, copper layers, housing views, diagrams) up to date with the repository, with every number counted from the sources. Use after a stored board, an approval, a new ADR or review, or before a hand-off. Not for user manuals (write-user-docs), new diagrams (write-diagrams) or routing a board (pcb-route-and-gate).
---

# Refresh the READMEs and their images

The READMEs only quote facts that exist elsewhere: requirements, ADRs, reviews, reports, board READMEs and check output.
This skill gives the order of work and the lessons. The scripts are the source of truth for commands and file names:
`scripts/readme_facts.py`, `hw/kicad/spike-gate/render_p1_images.sh`, `scripts/fab_p1.sh`, `mech/render_readme_images.sh`
and `scripts/build_diagrams.sh`. Images are tool exports (CLAUDE.md rule 9): never edit, crop or draw on them by hand,
change the script instead. Rule 12 applies: the renders read the boards, nothing writes them.

All commands run from the repository root.

## Order of work
1. **What changed.** `git log -1 --format='%h %cs' -- README.md`, then `git log --oneline <that hash>..HEAD`. Read the
   CHANGELOG `[Unreleased]` entries and the newest journal file in `docs/journal/`. These are the candidate changes.
2. **Count.** `python3 -I scripts/readme_facts.py`. It prints requirements and approvals per file, ADRs per status
   (`*` marks a qualified status such as "Accepted for the prototype only": name the qualifier in the README), review
   records, plan statuses, host test cases per ztest suite, images that no page shows, and each README with the number
   of commits since its last change. Compare every number in the README status table with this output. Board numbers
   (drops, vias, findings) come from `hw/kicad/spike-gate/board-p1/README.md`, not from memory or a batch log.
3. **Images: decide what to re-render.** Re-render only what changed:
   - P1 board, panel, schematic, copper layers: when `board-p1/` or `scripts/panel_p1.json` changed (step 4).
   - Housing views: when `mech/freecad/` changed. `scripts/ci_mech.sh` first (writes the STEP files to `build/mech`),
     then `mech/render_readme_images.sh docs/verification/reports/images`. Needs FreeCAD; if it is missing, say NOT RUN.
   - Diagrams: when `docs/diagrams/` changed. Follow the write-diagrams skill (`scripts/build_diagrams.sh`).
   - The spike board in `hw/kicad/spike-gate/board/` is frozen (2026-11-18): do not re-render its images.
4. **P1 renders.** They need the order panel of the same board:
   - Build the package into a scratch folder: `scripts/fab_p1.sh hw/kicad/spike-gate/board-p1/busy_light_spike.kicad_pcb
     <scratch>/fab` (KiCad 10 with pcbnew and KiKit 1.8.1 from `scripts/requirements-fab.txt`). An older package is fine
     only if `inputs.board.sha256` in its `manifest.json` equals `sha256sum` of the stored board.
   - Render: `sh hw/kicad/spike-gate/render_p1_images.sh hw/kicad/spike-gate/board-p1 <scratch>/fab/panel.kicad_pcb
     docs/verification/reports/images`. Needs kicad-cli, pdftoppm (poppler) and ImageMagick with DejaVu Sans. About
     4 minutes (three ray-traced renders); run it in the background.
   - If kicad-cli exists only in a container (the cloud sessions use the `kicad/kicad:10.0` image), put a wrapper named
     `kicad-cli` first on `PATH` that runs the container with the repository and the scratch folder mounted at the same
     paths, and set `TMPDIR` to the scratch folder, so the container sees the script's temporary files.
5. **Look at every new image** (open the PNG) before you write a caption. Check: the schematic cut does not go through
   a label, the background is white, the panel shows rails, tabs and fiducials, nothing is empty. A defect is fixed in
   the script and the whole script is run again, so the committed images are what the script makes.
6. **Edit the text.** In the root `README.md`: the honest-status box, "What exists today", the gallery captions, the
   roadmap and "Getting started". Then the folder READMEs that `readme_facts.py` lists with many commits since their last
   change, only where their content is wrong or missing (for example the list of files in `hw/sim/`). For each number,
   know its source. Keep the gallery alt texts factual: describe what the image shows, not what it should show.
7. **Check and record.**
   - `python3 -m pytest -q scripts/tests/test_readme_images.py scripts/tests/test_readme_facts.py`: every image a README
     shows exists, and the six P1 images are committed and shown.
   - `python3 -I scripts/check_traceability.py` and `ruff check .`; `scripts/build_diagrams.sh --check` if diagrams
     changed.
   - A CHANGELOG entry under `[Unreleased]` (Changed, or Added for new images or scripts).
   - Commit only when asked. Never commit the fab package or other build output.

## Wording rules for the READMEs
- Say what exists and what was not run. Never "compliant", "certified", "verified", "approved" or "ready to order"
  unless a document with that status says so; quote the status instead (for example "Accepted for the prototype only").
- Never set or imply `Approved` or `Accepted` yourself. Open owner decisions are listed as open.
- A number has a date and a source. Analyst assumptions (the 50 mV target, the currents of the power check) are named
  as assumptions.
- Images that no page shows any more: list them in the report and ask the owner before deleting one. A report or a
  frozen script may still name it.

## Lessons (each cost time once)
- KiCad's image has no SVG rasteriser (no rsvg-convert): the P1 script exports PDF and uses pdftoppm.
- `kicad-cli pcb render --background opaque` gives a lavender gradient; the script renders transparent and flattens
  onto white. The schematic export needs `--no-background-color`, otherwise the page is beige.
- Fixed pixel crops of the schematic broke when the layout changed (a crop cut the U5 caption). The script cuts in the
  middle of the white band (at least 40 pixel rows) that is closest to 55 % of the height. If a later layout has no such band, change the rule in the script.
- The panel render must come from a package of the stored board; check the manifest hash (step 4).
- Counting by hand gave wrong numbers before; use `readme_facts.py`. A requirement counts as approved only by its own
  Status line.
- Each render takes about a minute; do not run two image scripts into the same folder at the same time.
