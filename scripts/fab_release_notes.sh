#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Markdown notes of a P1 order package (plan 08 section 4.5, RV-014 readiness B2, RV-016 row 1): the fab_check result,
# the parts without an LCSC number and the owner waivers for must-place parts, read from the package itself.
#   scripts/fab_release_notes.sh <package dir> <label>
set -euo pipefail
(($# == 2)) || { echo "usage: scripts/fab_release_notes.sh <package dir> <label>" >&2; exit 2; }
pkg="$1"
# entries FILE NONE: the non-comment lines of FILE as a list, or NONE when there are none.
entries() {
  local text=""
  [[ -f "$1" ]] && text="$(sed -e 's/#.*//' -e '/^[[:space:]]*$/d' -e 's/^/- /' "$1")"
  echo "${text:-$2}"
}
echo "### Order checks ($2)"
if [[ -f "$pkg/fab_check.txt" ]]; then
  echo "- $(grep -m1 '^RESULT:' "$pkg/fab_check.txt" || echo 'RESULT: not found')"
else
  echo "- fab_check: NOT RUN (no fab_check.txt)"
fi
echo "### Parts without an LCSC number (scripts/fab_missing_lcsc.txt)"
entries "$pkg/fab_missing_lcsc.txt" "- none listed"
echo "### Owner waivers for must-place parts (scripts/fab_owner_waivers.txt)"
entries "$pkg/fab_owner_waivers.txt" "- none"
