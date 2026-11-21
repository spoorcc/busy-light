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

All commands run from the repository root. Keep packages and temporary files in the session scratchpad (`<scratch>`).

## Order of work
1. **What changed.** `git log -1 --format='%h %cs' -- README.md`, then `git log --oneline <that hash>..HEAD`. Read the
   CHANGELOG `[Unreleased]` entries and the newest dated file in `docs/journal/` (`ls docs/journal/2*.md | tail -1`).
   These are the candidate changes.
2. **Count.** `python3 -I scripts/readme_facts.py`. It prints requirements and approvals per file, ADRs per status
   (`*` marks a qualified status such as "Accepted for the prototype only": name the qualifier in the README), review
   records, plan statuses, host test cases per ztest suite, images that no page shows, and each README with the commits
   to its own folder since its last change. Board numbers (drops, vias, findings) come from
   `hw/kicad/spike-gate/board-p1/README.md`, not from memory or a batch log.
3. **Images: decide what to re-render.** Find the commit of the current images and what changed after it:
   - P1: `h=$(git log -1 --format=%h -- docs/verification/reports/images/p1-*.png)`, then
     `git log --oneline $h..HEAD -- hw/kicad/spike-gate/board-p1 scripts/panel_p1.json scripts/fab_p1.sh
     hw/kicad/spike-gate/render_p1_images.sh`. Any commit: step 4.
   - Housing views: the same with `housing-model-*.png` and `mech/freecad mech/analysis mech/render_readme_images.sh`.
     Run `scripts/ci_mech.sh` (writes the STEP files to `build/mech`), then
     `mech/render_readme_images.sh docs/verification/reports/images`. Needs FreeCAD, python3 with matplotlib and numpy.
   - Diagrams: when `docs/diagrams/` changed. Follow the write-diagrams skill (`scripts/build_diagrams.sh`).
   - The spike board in `hw/kicad/spike-gate/board/` is frozen (2026-11-18, its README): do not re-render its images.
   - A tool is missing: write NOT RUN for that image set in the report, keep the old images, and do not touch their
     captions' numbers.
4. **P1 renders.** They need the order panel of the same board.
   - Build the package into a new scratch folder:
     `scripts/fab_p1.sh hw/kicad/spike-gate/board-p1/busy_light_spike.kicad_pcb <scratch>/fab`. It needs KiCad 10
     (kicad-cli and pcbnew in the same `python3`) and `scripts/requirements-fab.txt` (KiKit 1.8.1, numpy, scipy).
   - Where KiCad is only in the `kicad/kicad:10.0` container (cloud sessions; the image has no pip): install the pins on
     the host into a folder, with a CPython of the image's minor version (3.13):
     `python3 -m pip install --target <scratch>/pylib-fab --require-hashes -r scripts/requirements-fab.txt`, then
     `docker run --rm -u 0:0 -e HOME=<scratch>/home -e PYTHONPATH=<scratch>/pylib-fab -v "$PWD:$PWD" -v
     <scratch>:<scratch> -w "$PWD" kicad/kicad:10.0 scripts/fab_p1.sh <board> <scratch>/fab` (2026-11-21: 18 s).
   - Exit code: 0 is required. Exit 1 (a gate failed): do not render; report the failed gate from the summary.
     Exit 2 (a tool or input missing, or no panel): stop and report it.
   - An older package is fine only if `inputs.board.sha256` in its `manifest.json` equals `sha256sum` of the stored
     board.
   - Render: `sh hw/kicad/spike-gate/render_p1_images.sh hw/kicad/spike-gate/board-p1 <scratch>/fab/panel.kicad_pcb
     docs/verification/reports/images`. Needs kicad-cli, pdftoppm (poppler) and ImageMagick with DejaVu Sans; exit 2
     names a missing tool or input. About 4 minutes (three ray-traced renders); run it in the background.
   - With kicad-cli only in the container: a file `<scratch>/shim/kicad-cli` with `exec docker run --rm -u 0:0
     -e HOME=<scratch>/home -v "$PWD:$PWD" -v <scratch>:<scratch> -w "$PWD" kicad/kicad:10.0 kicad-cli "$@"`
     (executable), `PATH=<scratch>/shim:$PATH` and `TMPDIR=<scratch>`. `-w "$PWD"` is needed: the arguments are
     relative paths. The temporary files must be under a mounted path.
5. **Look at every new image** (open the PNG) before you write a caption. Check: the schematic cut does not go through
   a label, the background is white, the panel shows rails, tabs and fiducials, nothing is empty. A defect is fixed in
   the script, then the whole script runs again, so the committed images are what the script makes. A script change
   traces to an Approved requirement (HW-008 for the P1 images; CLAUDE.md rule 1) and gets a test that fails before the
   fix where the defect can be tested without KiCad (rule 6); otherwise record the before and after check in the
   commit message.
6. **Edit the text.** In the root `README.md`: the honest-status box, "What exists today", the gallery captions, the
   roadmap and "Getting started". Then each folder README with one or more commits to its folder since its last change
   (step 2): read it and fix what is wrong or missing (for example the list of files in `hw/sim/`); leave it if it is
   still right. For each number, know its source. Alt texts describe what the image shows, not what it should show.
7. **Check and record.**
   - `python3 -m pytest -q scripts/tests/test_readme_images.py scripts/tests/test_readme_facts.py`: every image a README
     shows exists; the six P1 images are tracked by git (in a git checkout) and shown. Before the commit,
     `git status --short docs/verification/reports/images` lists the new images; add them.
   - `python3 -I scripts/check_traceability.py` and `ruff check .`; `scripts/build_diagrams.sh --check` if diagrams
     changed.
   - The step 2 comparison is by hand: in the report, give the counts from `readme_facts.py` that the README quotes.
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
  middle of the white band (at least 40 pixel rows) that is closest to 55 % of the height. If a later layout has no
  such band, change the rule in the script.
- The panel render must come from a package of the stored board; check the manifest hash (step 4). KiKit makes the
  same panel file from the same board (`"deterministic": true` in `scripts/panel_p1.json`; same sha256 on 2026-11-21).
- `requirements-fab.txt` must hold every package the `fab_p1.sh` steps import: scipy was only in the test pins until
  2026-11-21 (test `test_fab_requirements_cover_what_fab_p1_runs`).
- Counting by hand gave wrong numbers before; use `readme_facts.py`. A requirement counts as approved only by its own
  Status line.
- Each render takes about a minute; do not run two image scripts into the same folder at the same time.
