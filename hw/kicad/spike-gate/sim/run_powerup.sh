#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Run the power-up scenarios with ngspice and check the outcome. Usage: run_powerup.sh <work dir>
# Columns: glitch(0/1) select-high-time glitch-end hold-capacitor name expected
# chold 1p = no hold-off. 390n nominal, 312n = -20 % capacitor (1 Mohm, rail 3.3 V, threshold half rail).
set -u
D=$1; HERE=$(dirname "$0"); mkdir -p "$D"; rc=0
while read -r g t ge ch name expect; do
  sed "s/GLITCH/$g/;s/TSEL/$t/;s/TGEND/$ge/;s/CHOLD/$ch/" "$HERE/powerup.cir" > "$D/$name.cir"
  out=$(ngspice -b "$D/$name.cir" 2>&1)
  en=$(echo "$out" | awk '/^en_max/ {print $3}')
  tr=$(echo "$out" | awk '/^en_t / {print $3}')
  case "$expect" in
    low)   ok=$(awk -v e="$en" 'BEGIN{print (e<1.65)?1:0}');;
    pulse) ok=$(awk -v e="$en" 'BEGIN{print (e>1.65)?1:0}');;
    late)  ok=$(awk -v e="$en" -v t="${tr:-0}" 'BEGIN{print (e>1.65 && t>0.2)?1:0}');;
  esac
  echo "$name: glitch=$g select@$t glitch-end@$ge hold=$ch -> enable max ${en} V, first rise ${tr:-none} s (expected $expect: $([ "$ok" = 1 ] && echo ok || echo WRONG))"
  [ "$ok" = 1 ] || rc=1
done <<'LIST'
0 5m 5m 1p A low
1 5m 5m 1p B low
1 4m 5m 1p C pulse
1 4m 5m 390n D low
1 4m 150m 390n E low
1 4m 190m 312n F low
1 4m 300m 312n G late
LIST
exit $rc
