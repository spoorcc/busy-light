#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
# Run a command in the KiCad 10 container (pcbnew, kicad-cli) with the host's Java 25 for Freerouting (plan 08 step R1 and R3; RV-019 G18).
# Usage: run_in_kicad.sh <command and arguments>      e.g.  sh run_in_kicad.sh sh run_full.sh python3 /tmp/fullP3
#        FREEROUTING_JAR=/path/freerouting-2.5.0.jar PCB_PYTHON=python3 P1=1 ... sh run_in_kicad.sh sh run_best.sh /tmp/fullP3 /tmp/c1 4
# The image is the one of .github/workflows/fab-release.yml (by digest). Mounted: the repository, the Java directory (KC_JAVA_HOME, default
# the Debian Java 25 path, with the /etc directories its config symlinks point to) and the folder of FREEROUTING_JAR; the work folders you name must be under the repository or under KC_MOUNT.
# Extra Python packages that the image lacks (KiKit, PyYAML, kiutils: scripts/requirements-fab*.txt) go to a folder given in KC_PYTHONPATH.
# The Docker daemon must run. The run variables of run_pcb.sh and pcb_full.py are passed on.
IMAGE=kicad/kicad@sha256:3f4a01786dfbe803a65f345c3342b765db9add913f5e9448f8356793714ddc34
ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
JAVA=${KC_JAVA_HOME:-/usr/lib/jvm/java-25-openjdk-amd64}
[ $# -gt 0 ] || { sed -n 3,9p "$0"; exit 2; }
MOUNTS="-v $ROOT:$ROOT -v $JAVA:$JAVA:ro"
# Debian keeps the JVM config files as symlinks into /etc/java-<n>-openjdk; without those directories the JVM stops at start-up (RV-019 pass 2).
# Only /etc/java* by default (KC_ETC_PREFIX): a link into /etc/ssl must not mount the host's CA store (RV-019 pass 3, S9).
ETC_PREFIX=${KC_ETC_PREFIX:-/etc/java}
for t in $(find "$JAVA" -type l -lname '/etc/*' 2>/dev/null | xargs -r -n1 readlink | awk -F/ '{print "/"$2"/"$3}' | grep "^$ETC_PREFIX" | sort -u); do
  [ -e "$t" ] && MOUNTS="$MOUNTS -v $t:$t:ro"
done
[ -n "$FREEROUTING_JAR" ] && MOUNTS="$MOUNTS -v $(dirname "$FREEROUTING_JAR"):$(dirname "$FREEROUTING_JAR"):ro"
[ -n "$KC_MOUNT" ] && MOUNTS="$MOUNTS -v $KC_MOUNT:$KC_MOUNT"
[ -n "$KC_PYTHONPATH" ] && MOUNTS="$MOUNTS -v $KC_PYTHONPATH:$KC_PYTHONPATH:ro"
# shellcheck disable=SC2086
exec docker run --rm -i -u 0:0 -e HOME=/tmp/kc-home -e PYTHONPATH="${KC_PYTHONPATH:-}" -e PATH="$JAVA/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" \
  -e FREEROUTING_JAR -e PCB_PYTHON -e SPIKE_ALLOW_KNOWN_OPEN -e SEED_OFFSET -e KEYFIRST -e FR_THREADS -e FR_PASSES -e PLACE_GRID -e PLACE_ANT_KEEPOUT \
  -e PLACE_BLOCKS -e PLACE_RULE_PEN -e PLACE_ORIENT -e PLACE_ROWS -e PLACE_STRICT -e PLACE_SEED_START -e GATE_NET -e RING -e OUTER_ONLY -e CLEANUP -e SPIKE_PROFILE \
  -e P1 -e P1_DIAM -e PRESTITCH -e PRESTITCH_REUSE -e REPASS -e BOARD_ID $MOUNTS -w "$(pwd)" "$IMAGE" \
  sh -c 'mkdir -p "$HOME"; exec "$@"' sh "$@"          # HOME must exist for git config (RV-019 pass 3, S1)
