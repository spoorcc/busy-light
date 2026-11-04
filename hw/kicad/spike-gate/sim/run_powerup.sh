#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Run the power-up scenarios with ngspice and check the outcome. Usage: run_powerup.sh <work dir>
# Columns: glitch(0/1) select-high-time glitch-end hold-capacitor name expected
# chold 1p = no hold-off. 390n nominal, 312n = -20 % capacitor (1 Mohm, rail 3.3 V, threshold half rail).
# Columns: glitch(0/1) glitch-start glitch-end select-time CT dip-start dip-end name expected
# CT 1p = no hold-off. 577n gives about 400 ms, 290n about 200 ms (0.693 * 1 Mohm * CT, threshold half rail).
# A result that is not a number is a FAILURE (a broken netlist must not pass).
set -u
D=$1; HERE=$(dirname "$0"); mkdir -p "$D"; rc=0
isnum() { echo "$1" | awk '{exit !($0 ~ /^-?[0-9.]+(e[-+]?[0-9]+)?$/)}'; }
while read -r g gs ge t ch d0 d1 name expect; do
  sed "s/GLITCH/$g/;s/TGS/$gs/;s/TGEND/$ge/;s/TSEL/$t/;s/CHOLD/$ch/;s/DIP0/$d0/;s/DIP1/$d1/" "$HERE/powerup.cir" > "$D/$name.cir"
  out=$(ngspice -b "$D/$name.cir" 2>&1)
  en=$(echo "$out" | awk '/^en_max/ {print $3}')
  tr=$(echo "$out" | awk '/^en_t / {print $3}')
  if ! isnum "$en"; then echo "$name: NO NUMERIC RESULT (simulator error?) -> WRONG"; rc=1; continue; fi
  case "$expect" in
    low)   ok=$(awk -v e="$en" 'BEGIN{print (e<1.65)?1:0}');;
    pulse) ok=$(awk -v e="$en" 'BEGIN{print (e>1.65)?1:0}');;
    late)  isnum "$tr" && ok=$(awk -v e="$en" -v t="$tr" 'BEGIN{print (e>1.65 && t>0.2)?1:0}') || ok=0;;
  esac
  echo "$name: glitch=$g [$gs,$ge] select@$t CT=$ch dip=[$d0,$d1] -> enable max ${en} V, first rise ${tr:-none} s (expected $expect: $([ "$ok" = 1 ] && echo ok || echo WRONG))"
  [ "$ok" = 1 ] || rc=1
done <<'LIST'
0 3m 5m 5m 1p 10 11 A low
1 3m 5m 5m 1p 10 11 B low
1 3m 5m 4m 1p 10 11 C pulse
1 3m 5m 4m 577n 10 11 D low
1 3m 150m 4m 577n 10 11 E low
1 3m 190m 4m 290n 10 11 F low
1 3m 300m 4m 290n 10 11 G late
1 560m 640m 4m 577n 500m 550m H low
1 560m 640m 4m 1p 500m 550m I pulse
LIST
exit $rc
