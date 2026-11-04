#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Run the three power-up scenarios with ngspice and check the outcome. Usage: run_powerup.sh <work dir>
set -u
D=$1; HERE=$(dirname "$0"); mkdir -p "$D"; rc=0
while read -r g t name expect; do
  sed "s/GLITCH/$g/;s/TSEL/$t/" "$HERE/powerup.cir" > "$D/$name.cir"
  out=$(ngspice -b "$D/$name.cir" 2>&1)
  en=$(echo "$out" | awk '/^en_max/ {print $3}')
  hi=$(awk -v e="$en" 'BEGIN{print (e>1.65)?"pulse":"low"}')
  echo "scenario $name (glitch=$g, select high at $t): enable max $en V -> $hi (expected $expect)"
  [ "$hi" = "$expect" ] || rc=1
done <<'LIST'
0 5m A low
1 5m B low
1 4m C pulse
LIST
exit $rc
