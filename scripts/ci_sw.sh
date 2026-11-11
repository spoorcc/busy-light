#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Software checks. Same script locally and in CI.
# Builds sw/app for the host (native_sim) when the west workspace can be set up, then runs Twister
# unit tests under sw/app/tests, then the static analysis and SBOM of scripts/ci_sw_static.sh.
# A missing input is reported as NOT RUN, never as a pass.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# Zephyr's pip step refuses to run outside a virtual environment.
if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  python3 -m venv "$ROOT/.venv-sw"
  # shellcheck disable=SC1091
  source "$ROOT/.venv-sw/bin/activate"
fi
python3 -m pip install --quiet west
[[ -d .west ]] || west init -l sw
west update --narrow -o=--depth=1
west packages pip --install
if compgen -G "sw/app/tests/*/testcase.yaml" >/dev/null || compgen -G "sw/app/tests/*/sample.yaml" >/dev/null; then
  west twister -T sw/app/tests -p native_sim/native/64 --inline-logs
else
  echo "sw: unit tests NOT RUN - no testcase.yaml under sw/app/tests"
fi
# The SBOM (west spdx) needs the CMake file API set up before the build and the build metadata
# (CONFIG_BUILD_OUTPUT_META). Then the static analysis, Kconfig policy and SBOM steps run on the
# build (scripts/ci_sw_static.sh, rules SWC-001/002/006/007/009).
west spdx --init -d build
west build -b native_sim sw/app --pristine -d build -- -DCONFIG_BUILD_OUTPUT_META=y
scripts/ci_sw_static.sh build
