#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Tolerance stack and fit checks for the 53 mm housing (MECH-004, MECH-006, MECH-007, MECH-009).

Run: python3 -I mech/analysis/check_tolerance.py   (standard library only)
Analysis only. The FDM tolerances are assumptions, nothing is measured.
Exit code 1 when a check fails.
"""

import math
import sys
from collections.abc import Mapping
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import housing_params as p  # noqa: E402

RING_W_TOL = 0.45  # ring width may differ from 4.4 or 4.8 mm by this much (MECH-007)
MIN_MARGIN = 1.0  # window to floor and to joint
MIN_SKIN_LINES = 2.0
MIN_WC_CLEARANCE = 0.04  # spigot clearance minus the FDM tolerance, plan 05 stack 5
MAX_OVERHANG_DEG = 45.0  # printable overhang from the vertical
BUMP_TIP_GAP = 0.05  # bump tip to the groove bottom


def rss(vals: list[float]) -> float:
    return math.sqrt(sum(v * v for v in vals))


def pcb_gap() -> dict[str, float]:
    """Radial gap board edge to inner wall (MECH-009)."""
    d_in = p.D_OUT - 2 * p.WALL
    nom = (d_in - p.D_PCB) / 2.0
    wc = (d_in - p.TOL_FDM - (p.D_PCB + p.TOL_PCB_D)) / 2.0 - p.TOL_PLACE
    rs = nom - rss([p.TOL_FDM / 2, p.TOL_PCB_D / 2, p.TOL_PLACE])
    return {"nominal": nom, "wc": wc, "rss": rs}


def usb_window() -> dict[str, float]:
    """USB-C window against the plug envelope (MECH-004). Slack minus the placement stack."""
    pos = [0.10, p.TOL_PLACE, p.TOL_FDM_FINE]
    need_wc, need_rss = 2 * sum(pos), 2 * rss(pos)
    slack = min((p.WIN_W - p.TOL_FDM) - p.PLUG_W, (p.WIN_H - p.TOL_FDM) - p.PLUG_H)
    return {"slack": slack, "need_wc": need_wc, "need_rss": need_rss}


def window_z() -> dict[str, float]:
    bottom = p.WIN_ZC - p.WIN_H / 2
    top = p.WIN_ZC + p.WIN_H / 2
    return {"to_floor": bottom - p.FLOOR, "to_joint": p.H_JOINT - top}


def spigot() -> dict[str, float]:
    """Lid spigot: clearance at worst case, snap bump interference, ledge support."""
    r_skirt_in = p.D_OUT / 2.0 - p.SKIRT_T
    r_out = r_skirt_in - p.SPIGOT_CLEAR
    r_in = r_out - p.SPIGOT_T
    wall_in = p.D_OUT / 2.0 - p.WALL
    return {
        "wc_min": round(p.SPIGOT_CLEAR - p.TOL_FDM, 3),
        "play_max": p.SPIGOT_CLEAR + p.TOL_FDM,
        "bump_interference": p.LID_BUMP - BUMP_TIP_GAP,
        "skirt_lines": p.SKIRT_T / p.NOZZLE,
        "ledge_radial": wall_in - r_in,
        "ledge_angle_deg": math.degrees(math.atan2(wall_in - r_in, p.H_JOINT - p.LEDGE_Z)),
    }


def led_distance() -> dict[str, float]:
    items = [0.20, p.TOL_PCB_T, 0.10, 0.20, 0.20]
    return {"wc": sum(items), "rss": rss(items)}


def bayonet() -> dict[str, float]:
    """Geometry checks of the annular bayonet (MECH-007, MECH-006)."""
    ring_w = p.BAY_R_OUT - p.BAY_R_IN
    skin = p.FLOOR - p.BAY_DEPTH
    # arc length of one lug on the mean radius, travel of the 30 degree turn on the mean radius
    r_mean = (p.BAY_R_IN + p.BAY_R_OUT) / 2
    travel = math.radians(p.BAY_TURN_DEG) * r_mean
    # label circle must fit inside the ring inner radius with 0.4 mm margin
    label_margin = p.BAY_R_IN - p.LABEL_CIRCLE_D / 2
    return {
        "ring_w": ring_w,
        "ring_w_lines": ring_w / p.NOZZLE,
        "skin": skin,
        "skin_lines": skin / p.NOZZLE,
        "travel": travel,
        "label_margin": label_margin,
        "lug_w_lines": p.BAY_LUG_W / p.NOZZLE,
    }


def hooks() -> dict[str, float]:
    """Snap hooks: board edge to hook lip, and the wall left outside the hook."""
    r_in = (p.D_OUT - 2 * p.WALL) / 2
    return {"lip_vs_gap": pcb_gap()["wc"] - p.HOOK_LIP, "r_in": r_in}


# Centre button chains (plan 09 section 3.4). Informational: run() does not call them and they are
# not a CI gate until step 2 approves the numbers. Every value is a plus-minus half-width in mm.
# Datum of the vertical chain: the PCB top (Z 6.6) up to the contact plane of the plunger on the
# switch actuator; each term is taken in its unfavourable direction.
BUTTON_VERTICAL_KEYS = (
    "pcb_post",
    "lid_ledge",
    "lid_plate",
    "disc_plunger",
    "switch_height",
    "switch_actuation",
)
BUTTON_VERTICAL = {
    "pcb_post": p.TOL_FDM_FINE + p.TOL_PCB_T,  # post seat plus board thickness
    "lid_ledge": p.TOL_FDM,  # lid ledge height
    "lid_plate": p.TOL_FDM_FINE,  # lid plate and band thickness
    "disc_plunger": p.TOL_FDM_FINE,  # plunger length under the disc
    "switch_height": 0.15,  # ASSUMPTION: no datasheet gives it
    "switch_actuation": 0.20,  # click point spread, the larger side of the B3U +0.2/-0.1 mm
}
# Lateral chain: where the plunger tip lands relative to the switch actuator.
BUTTON_LATERAL_KEYS = ("pcb_wall_gap", "spigot_play", "tilt_walk", "plunger_tip")
BUTTON_LATERAL = {
    "pcb_wall_gap": (p.D_OUT - 2 * p.WALL - p.D_PCB) / 2.0,  # nominal radial gap, board to one side
    "spigot_play": p.SPIGOT_CLEAR + p.TOL_FDM,  # lid spigot play
    "tilt_walk": 0.20,  # ASSUMPTION: disc tilt of 0.1 rad over a 2 mm plunger length
    "plunger_tip": p.TOL_PLACE,  # plunger tip placement on the disc underside
}


def _chain(tolerances: Mapping[str, float], keys: tuple[str, ...]) -> dict[str, float]:
    vals = [tolerances[k] for k in keys]
    return {"wc": sum(vals), "rss": rss(vals)}


def button_vertical_chain(tolerances: Mapping[str, float]) -> dict[str, float]:
    """Worst case (sum) and RSS of the six vertical terms, mm plus-minus."""
    return _chain(tolerances, BUTTON_VERTICAL_KEYS)


def button_lateral_chain(tolerances: Mapping[str, float]) -> dict[str, float]:
    """Worst case (sum) and RSS of the four lateral terms, mm plus-minus."""
    return _chain(tolerances, BUTTON_LATERAL_KEYS)


def recess_worst_case(nominal_recess_mm: float, tolerances: Mapping[str, float]) -> float:
    """Disc top below the band top at the worst case (placeholder formula, see below).

    Disc and band are one print, so the ledge height moves both and does not change the step between
    them; only the plate thickness term (lid_plate) is taken as the independent spread of that step.
    A negative value means the disc can stand proud of the band. The formula is an assumption
    until a coupon measures the step.
    """
    return nominal_recess_mm - tolerances["lid_plate"]


def run() -> tuple[list[str], list[str]]:
    """Return (report lines, failures)."""
    out: list[str] = []
    fail: list[str] = []
    g = pcb_gap()
    out.append(
        f"PCB gap to wall: nominal {g['nominal']:.2f}, WC {g['wc']:.2f}, RSS {g['rss']:.2f} mm"
    )
    if g["wc"] <= 0:
        fail.append("PCB binds on the wall at worst case")
    h = hooks()
    out.append(f"Hook lip {p.HOOK_LIP:.2f} mm; WC gap minus lip {h['lip_vs_gap']:+.2f} mm")
    if h["lip_vs_gap"] <= 0:
        fail.append("hook lip does not fit in the worst-case gap")
    u = usb_window()
    out.append(
        f"USB-C window {p.WIN_W} x {p.WIN_H}: slack {u['slack']:.2f}, need WC {u['need_wc']:.2f}, "
        f"RSS {u['need_rss']:.2f}",
    )
    if u["slack"] < u["need_wc"]:
        fail.append("USB-C window fails at worst case")
    z = window_z()
    out.append(f"Window margin to floor {z['to_floor']:.2f}, to joint {z['to_joint']:.2f} mm")
    if min(z.values()) < MIN_MARGIN:
        fail.append("window too close to the floor or the joint")
    sp = spigot()
    out.append(
        f"Lid spigot clearance {p.SPIGOT_CLEAR:.2f}: WC min {sp['wc_min']:+.2f}, "
        f"max play {sp['play_max']:.2f}; skirt {sp['skirt_lines']:.1f} lines"
    )
    out.append(
        f"Lid snap bump interference {sp['bump_interference']:.2f} mm (the skirt flexes by that); "
        f"wall ledge {sp['ledge_radial']:.2f} mm at "
        f"{sp['ledge_angle_deg']:.0f} deg from the vertical"
    )
    if sp["wc_min"] < MIN_WC_CLEARANCE:
        fail.append("lid spigot binds at worst case")
    if sp["skirt_lines"] < MIN_SKIN_LINES:
        fail.append("lid skirt thinner than two print lines")
    if sp["ledge_angle_deg"] > MAX_OVERHANG_DEG:
        fail.append("wall ledge is a steeper overhang than 45 degrees")
    d = led_distance()
    out.append(f"LED to diffuser {p.D_LED}: WC +-{d['wc']:.2f}, RSS +-{d['rss']:.2f} mm")
    b = bayonet()
    out.append(f"Bayonet ring {b['ring_w']:.2f} mm ({b['ring_w_lines']:.2f} lines)")
    out.append(f"Floor skin under bayonet {b['skin']:.2f} mm ({b['skin_lines']:.1f} lines)")
    out.append(f"Turn travel {b['travel']:.1f} mm, label margin {b['label_margin']:+.2f} mm")
    # ring width near 4.4 or 4.8 mm (multiples of the nozzle width, MECH-007 rationale)
    if min(abs(b["ring_w"] - w) for w in (4.4, 4.8)) > RING_W_TOL:
        fail.append("ring width not near 4.4 or 4.8 mm")
    if b["skin_lines"] < MIN_SKIN_LINES:
        fail.append("floor skin under the bayonet is thinner than two print lines")
    if b["label_margin"] < 0:
        fail.append("label circle does not fit inside the ring")
    return out, fail


def main() -> int:
    out, fail = run()
    print("check_tolerance (FDM tolerances assumed, nothing measured)")
    for line in out:
        print(" ", line)
    for f in fail:
        print("FAIL:", f)
    print("RESULT:", "FAIL" if fail else "PASS (analysis only)")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
