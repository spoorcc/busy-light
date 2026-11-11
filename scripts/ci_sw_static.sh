#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Static analysis, Kconfig policy and SBOM of the project firmware (rules SWC-001, SWC-002, SWC-006,
# SWC-007, SWC-009; catalogue docs/regulatory/automated-checks.md). Same script locally and in CI.
#   scripts/ci_sw_static.sh [build-dir]     after a `west build` with CONFIG_BUILD_OUTPUT_META=y
#                                           and `west spdx --init` before it
# Results go to $SW_CI_OUT (default: a temp dir). A missing input is reported as NOT RUN, never as a pass.
# Needs: clang-tidy, cppcheck (with its MISRA addon), python3 with pyyaml.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
BUILD="${1:-build}"
OUT="${SW_CI_OUT:-$(mktemp -d)}"; mkdir -p "$OUT"
rc=0
note() { echo "== $*"; }

note "SWC-001/002 Kconfig policy on the fragments and the built .config"
if [[ -f "$BUILD/zephyr/.config" ]]; then
  python3 -I scripts/check_kconfig_policy.py --dotconfig "$BUILD/zephyr/.config" || rc=1
else
  echo "sw static: built .config NOT RUN - no $BUILD/zephyr/.config"
  python3 -I scripts/check_kconfig_policy.py || rc=1
fi

note "SWC-008 suppressions name a deviation"
python3 -I scripts/check_sw_static.py suppressions || rc=1

shopt -s nullglob
srcs=(sw/app/src/*.c sw/drivers/**/*.c sw/lib/**/*.c)
db_files=()
if [[ -f "$BUILD/compile_commands.json" ]]; then
  python3 -I scripts/check_sw_static.py tidy-db "$BUILD/compile_commands.json" "$OUT/tidy/compile_commands.json"
  mapfile -t db_files < <(python3 -I -c 'import json,sys; [print(e["file"]) for e in json.load(open(sys.argv[1]))]' \
    "$OUT/tidy/compile_commands.json")
else
  echo "sw static: compile database NOT RUN - no $BUILD/compile_commands.json"
fi
# Project sources that the app build does not compile (for example pure logic used by unit tests) are
# analysed on their own when they include no Zephyr header; any other one is listed as NOT RUN.
standalone=()
for f in "${srcs[@]}"; do
  abs="$ROOT/$f"
  if printf '%s\n' "${db_files[@]}" | grep -qxF "$abs"; then continue; fi
  if grep -q '#include <zephyr/' "$f"; then
    echo "sw static: $f NOT RUN - not in the compile database and needs Zephyr headers"
  else
    standalone+=("$f")
  fi
done

note "SWC-006 clang-tidy (sw/.clang-tidy: CERT C, bugprone, clang-analyzer)"
clang-tidy --version | head -n 2
: > "$OUT/clang-tidy.txt"
if ((${#db_files[@]})); then
  clang-tidy -p "$OUT/tidy" --quiet "${db_files[@]}" >>"$OUT/clang-tidy.txt" 2>&1 || rc=1
fi
for f in "${standalone[@]}"; do
  clang-tidy --quiet "$f" -- -std=c11 -I"$(dirname "$f")" >>"$OUT/clang-tidy.txt" 2>&1 || rc=1
done
grep -E 'warning:|error:' "$OUT/clang-tidy.txt" || echo "clang-tidy: no findings in project code"

note "SWC-007 cppcheck with the MISRA C:2012 addon (not a MISRA compliance report)"
cppcheck --version
# shellcheck disable=SC2054  # the commas belong to the --enable value
CPP_COMMON=(--addon=misra --enable=warning,style,performance,portability --inline-suppr --quiet
  "--suppress=*:/usr/*"
  --suppress=missingIncludeSystem --xml)
# cppcheck 2.x cannot preprocess Zephyr's headers (IS_ENABLED() expansion fails), so MISRA checking
# covers the project files that build without Zephyr; files that need Zephyr get clang-tidy only.
for f in "${db_files[@]}"; do
  echo "sw static: SWC-007 NOT RUN for ${f#"$ROOT"/} - cppcheck cannot preprocess Zephyr headers"
done
if ((${#standalone[@]})); then
  incs=()
  for d in $(for f in "${standalone[@]}"; do dirname "$f"; done | sort -u); do incs+=("-I$d"); done
  cppcheck --std=c11 "${CPP_COMMON[@]}" "${incs[@]}" "${standalone[@]}" \
    2>"$OUT/cppcheck-misra-standalone.xml"
  python3 -I scripts/check_sw_static.py misra "$OUT/cppcheck-misra-standalone.xml" || rc=1
fi

note "SWC-009 SBOM (west spdx)"
if command -v west >/dev/null && [[ -d "$BUILD/.cmake/api" ]]; then
  if west spdx -d "$BUILD" -s "$OUT/spdx"; then
    python3 -I scripts/check_sbom.py "$OUT/spdx" --json "$OUT/sbom-summary.json" || rc=1
  else
    echo "sw static: SBOM FAILED - west spdx returned an error"; rc=1
  fi
else
  echo "sw static: SBOM NOT RUN - no west or no CMake file API in $BUILD (run 'west spdx --init -d $BUILD' before the build)"
fi

echo "sw static: results in $OUT"
exit $rc
