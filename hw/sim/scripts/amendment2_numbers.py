#!/usr/bin/env python3
"""Reproduce the numbers of ADR-0016 Amendment 2 (HW-010) with the spike's own models.

Why this script exists: the spike scripts `holdoff_cap.py` and `ilim_steps.py` hold the old E192
resistor set and the old 220+220+100+68 nF capacitor set (hw/ content, locked by rule 1 until
HW-010 is Approved). RV-010 finding: the figures of Amendment 2 were not repeatable from the
repository. This script calls the spike functions with the owner-chosen parts (journal
2026-11-06) and prints the result. It changes no hw/ file.

Run: python3 hw/sim/scripts/amendment2_numbers.py
(exit 1 if a window leaves its HW-010 limit)
"""

from __future__ import annotations

import pathlib
import sys

SPIKE_SIM = pathlib.Path(__file__).resolve().parents[2] / "kicad" / "spike-gate" / "sim"
sys.path.insert(0, str(SPIKE_SIM))

import holdoff_cap as hc  # noqa: E402
import ilim_steps as il  # noqa: E402

SIX_100N = [(100e-9, 0.05, "GRM31C5C1H104JA01L")] * 6
R1_K, R2_K, R3_K = 47.0, 56.2, 27.4 + 0.301  # R3 branch includes the 301 ohm series part
HOLDOFF_MIN_MS, HOLDOFF_MAX_MS = 200.0, 600.0  # HW-010 proposal (bracketed, open)


def holdoff_window_ms() -> tuple[float, float]:
    """Return (min, max) hold-off in ms for the six 100 nF set, without the 0.6 % allowance."""
    lo, hi = hc.td_window(SIX_100N)
    return lo * 1e3, hi * 1e3


def step_windows_ma() -> dict[str, tuple[float, float]]:
    """Return the worst-case current window per step (E96 set, TMUX1101, 0.1 % resistors)."""
    w = il.step_windows(
        R1_K, R2_K, R3_K, 0.001, leak_a=il.TMUX_LEAK_A, rds_max=il.TMUX_RDS_ON_MAX_OHM
    )
    return w


def main() -> int:
    lo, hi = holdoff_window_ms()
    print(
        f"hold-off 6 x 100 nF: {lo:.1f} to {hi:.1f} ms;"
        f" margin to {HOLDOFF_MIN_MS:.0f} ms: {lo - HOLDOFF_MIN_MS:.1f} ms,"
        f" to {HOLDOFF_MAX_MS:.0f} ms: {HOLDOFF_MAX_MS - hi:.1f} ms"
    )
    w = step_windows_ma()
    for k, v in w.items():
        print(f"{k}: {v}")
    ok = lo >= HOLDOFF_MIN_MS and hi <= HOLDOFF_MAX_MS
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
