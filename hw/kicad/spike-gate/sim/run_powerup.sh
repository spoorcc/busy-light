#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Run the power-up scenarios with ngspice and check the outcome. Usage: run_powerup.sh <work dir>
# Columns: glitch(0/1) select-high-time glitch-end hold-capacitor name expected
# chold 1p = no hold-off. 390n nominal, 312n = -20 % capacitor (1 Mohm, rail 3.3 V, threshold half rail).
# Columns: glitch(0/1) glitch-start glitch-end select-time CT dip-start dip-end dip-level name expected
# L: VBUS gone (0 V) while 3V3 stays up, then an IC glitch: closed. M: dip only to 4.3 V (above the supervisor
# threshold, below the 4.5 V the CC IC needs): no restart, the glitch passes - a known gap, kept as a pulse.
# CT 1p = no hold-off. 620n = typical (384 ms), 340n = 0.95 * minimum constant (210 ms), 921n = 1.05 * maximum (570 ms)
# (TPS3840 datasheet constants 357.6k and 875.6k ohm * C, behavioural model 0.693 * 893k * CT).
# A result that is not a number is a FAILURE (a broken netlist must not pass).
set -u
D=$1; HERE=$(dirname "$0"); mkdir -p "$D"; rc=0
isnum() { echo "$1" | awk '{exit !($0 ~ /^-?[0-9.]+(e[-+]?[0-9]+)?$/)}'; }
while read -r g gs ge t ch d0 d1 dv name expect; do
  sed "s/GLITCH/$g/;s/TGS/$gs/;s/TGEND/$ge/;s/TSEL/$t/;s/CHOLD/$ch/;s/DIP0/$d0/;s/DIP1/$d1/;s/DIPV/$dv/" "$HERE/powerup.cir" > "$D/$name.cir"
  out=$(ngspice -b "$D/$name.cir" 2>&1)
  en=$(echo "$out" | awk '/^en_max/ {print $3}')
  tr=$(echo "$out" | awk '/^en_t / {print $3}')
  if ! isnum "$en"; then echo "$name: NO NUMERIC RESULT (simulator error?) -> WRONG"; rc=1; continue; fi
  case "$expect" in
    low)   ok=$(awk -v e="$en" 'BEGIN{print (e<1.65)?1:0}');;
    pulse) ok=$(awk -v e="$en" 'BEGIN{print (e>1.65)?1:0}');;
    window) isnum "$tr" && ok=$(awk -v e="$en" -v t="$tr" 'BEGIN{print (e>1.65 && t>=0.2 && t<=0.6)?1:0}') || ok=0;;
    late)  isnum "$tr" && ok=$(awk -v e="$en" -v t="$tr" 'BEGIN{print (e>1.65 && t>0.2)?1:0}') || ok=0;;
  esac
  echo "$name: glitch=$g [$gs,$ge] select@$t CT=$ch dip=[$d0,$d1]@${dv}V -> enable max ${en} V, first rise ${tr:-none} s (expected $expect: $([ "$ok" = 1 ] && echo ok || echo WRONG))"
  [ "$ok" = 1 ] || rc=1
done <<'LIST'
0 3m 5m 5m 1p 10 11 3.5 A low
1 3m 5m 5m 1p 10 11 3.5 B low
1 3m 5m 4m 1p 10 11 3.5 C pulse
1 3m 5m 4m 620n 10 11 3.5 D low
1 3m 150m 4m 620n 10 11 3.5 E low
1 3m 190m 4m 340n 10 11 3.5 F low
1 3m 300m 4m 340n 10 11 3.5 G late
1 560m 640m 4m 620n 500m 550m 3.5 H low
1 560m 640m 4m 1p 500m 550m 3.5 I pulse
1 3m 10 4m 340n 10 11 3.5 J window
1 3m 10 4m 921n 10 11 3.5 K window
1 570m 640m 4m 620n 500m 560m 0 L low
1 570m 640m 4m 620n 500m 560m 4.3 M pulse
LIST
exit $rc
