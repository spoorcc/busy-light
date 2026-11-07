#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Render the README views of the housing model. Usage: mech/render_readme_images.sh <out dir>
# Needs: freecad (as in scripts/ci_mech.sh), python3 with matplotlib and numpy. Run scripts/ci_mech.sh first
# (it writes the STEP files to build/mech). Images are tool output; nothing is edited by hand.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
OUT=${1:?usage: render_readme_images.sh <out dir>}
export QT_QPA_PLATFORM=offscreen
echo "exec(open('mech/analysis/render_dump_mesh.py').read())" | freecad -c
python3 -I mech/analysis/render_views.py "${MECH_RENDER_DIR:-build/mech-render}/mesh.json" "$OUT"
