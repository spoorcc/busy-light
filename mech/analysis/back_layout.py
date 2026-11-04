#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""2D layout check of the back of the housing (ADR-0014, RV-007 findings G1 and G2).

Question: do the bayonet recess, the unit label and the four feet fit on the 53 mm back?
This checks plan geometry only. It does not check height, strength, print orientation or tolerances.
All values are the working values of plan 05 and ADR-0014 (millimetres).

Usage: back_layout.py [output.png]   (prints a table; writes a drawing when a path is given)
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass

D_OUT = 53.0
R_OUT = D_OUT / 2
EDGE_MARGIN = 1.0  # keep features this far from the outer edge (fillet, tolerance)
R_AVAIL = R_OUT - EDGE_MARGIN
LABEL = 21.0  # plan 05 label recess, MECH-006 asks at least 20
RECESS_D = 30.0  # ADR-0014 working value
FEET_R, FOOT_PAD_R = 21.0, 3.0  # plan 05: four pads on the diagonals
CLEAR = 0.5  # minimum gap between features
MIN_RING_WIDTH = 4.0  # narrowest bayonet ring that can carry lugs (working value)


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    detail: str


def square_corner_radius(cx: float, cy: float, side: float) -> float:
    """Largest distance from the axis to a corner of an axis-aligned square."""
    h = side / 2
    return max(math.hypot(abs(cx) + h, abs(cy) + h), 0.0)


def max_square_beside_circle(circle_r: float) -> float:
    """Largest square, touching a centred circle at distance CLEAR, that stays inside R_AVAIL."""
    lo, hi = 0.0, 2 * R_AVAIL
    for _ in range(60):
        s = (lo + hi) / 2
        cx = circle_r + CLEAR + s / 2
        if square_corner_radius(cx, 0.0, s) <= R_AVAIL:
            lo = s
        else:
            hi = s
    return lo


def v0_as_written() -> Check:
    # Plan 05 centres the label recess; ADR-0014 centres the bayonet recess. MECH-006 asks for the
    # label outside the mounting recess. A centred 21 mm label lies inside a centred 30 mm recess.
    label_corner = square_corner_radius(0.0, 0.0, LABEL)
    inside = label_corner <= RECESS_D / 2
    return Check(
        "V0 as written: centred label and centred 30 mm recess (MECH-006 wants the label outside)",
        not inside,
        f"label corner at R {label_corner:.1f} mm, recess radius {RECESS_D / 2:.1f} mm: "
        + (
            "the label lies inside the recess and is covered by any accessory"
            if inside
            else "outside"
        ),
    )


def v1_label_beside_recess() -> Check:
    s = max_square_beside_circle(RECESS_D / 2)
    return Check(
        "V1 label beside the centred 30 mm recess",
        s >= LABEL,
        f"largest square that fits: {s:.1f} mm (needs {LABEL:.0f} mm)",
    )


def v2_annular_bayonet() -> tuple[Check, dict[str, float]]:
    # Label stays centred and open; the bayonet becomes a ring around it; feet move outwards.
    inner = square_corner_radius(0.0, 0.0, LABEL) + CLEAR + 1.0
    foot_pad_r, foot_r = 2.0, R_AVAIL - 2.0
    outer = foot_r - foot_pad_r - CLEAR
    width = outer - inner
    ok = width >= MIN_RING_WIDTH
    return (
        Check(
            "V2 annular bayonet around a centred open label",
            ok,
            f"ring R {inner:.1f} to {outer:.1f} mm ({width:.1f} mm wide); "
            f"feet pad R {foot_pad_r:.1f} at R {foot_r:.1f}",
        ),
        {"inner": inner, "outer": outer, "foot_pad_r": foot_pad_r, "foot_r": foot_r},
    )


def v3_label_inside_recess() -> Check:
    corner = square_corner_radius(0.0, 0.0, LABEL)
    small = 14.0
    small_corner = square_corner_radius(0.0, 0.0, small)
    limit = RECESS_D / 2 - CLEAR
    return Check(
        "V3 14 mm label inside the 30 mm recess (covered by a plate)",
        small_corner <= limit,
        f"21 mm label corner R {corner:.1f} > {limit:.1f} (does not fit with clearance); "
        f"a 14 mm label (corner R {small_corner:.1f}) fits but is covered when mounted",
    )


def v4_dovetail_rail(rail_w: float = 12.0) -> Check:
    lo, hi = 0.0, 2 * R_AVAIL
    for _ in range(60):
        s = (lo + hi) / 2
        cx = rail_w / 2 + CLEAR + s / 2
        if square_corner_radius(cx, 0.0, s) <= R_AVAIL:
            lo = s
        else:
            hi = s
    return Check(
        f"V4 label beside a {rail_w:.0f} mm wide dovetail rail",
        lo >= LABEL,
        f"largest square that fits: {lo:.1f} mm (needs {LABEL:.0f} mm)",
    )


def foot_clearance_v2(geo: dict[str, float]) -> float:
    return geo["foot_r"] - geo["foot_pad_r"] - geo["outer"]


def run() -> list[Check]:
    c2, geo = v2_annular_bayonet()
    return [
        v0_as_written(),
        v1_label_beside_recess(),
        c2,
        v3_label_inside_recess(),
        v4_dovetail_rail(),
    ] + [
        Check(
            "V2 foot clearance to the bayonet ring",
            foot_clearance_v2(geo) >= CLEAR,
            f"{foot_clearance_v2(geo):.1f} mm",
        )
    ]


def draw(path: str) -> None:
    import matplotlib  # noqa: PLC0415 (deferred: the checks run without matplotlib)

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: PLC0415
    from matplotlib.patches import Circle, Rectangle  # noqa: PLC0415

    _, geo = v2_annular_bayonet()
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.6))
    titles = [
        "V0: as written (label inside recess)",
        "V2: annular bayonet, label open",
        "V3: label inside recess",
    ]
    for ax, title in zip(axes, titles, strict=True):
        ax.set_aspect("equal")
        ax.set_xlim(-R_OUT - 1, R_OUT + 1)
        ax.set_ylim(-R_OUT - 1, R_OUT + 1)
        ax.add_patch(Circle((0, 0), R_OUT, fill=False, lw=1.5))
        ax.add_patch(Circle((0, 0), R_AVAIL, fill=False, ls=":", lw=0.8, color="grey"))
        ax.set_title(title, fontsize=10)
        ax.set_xticks([])
        ax.set_yticks([])
    a0, a1, a2 = axes
    a0.add_patch(Circle((0, 0), RECESS_D / 2, fill=True, alpha=0.25, color="tab:blue"))
    a0.add_patch(
        Rectangle((-LABEL / 2, -LABEL / 2), LABEL, LABEL, fill=False, ec="tab:red", lw=1.5)
    )
    for k in range(4):
        a = math.radians(45 + 90 * k)
        a0.add_patch(
            Circle(
                (FEET_R * math.cos(a), FEET_R * math.sin(a)), FOOT_PAD_R, fc="tab:green", alpha=0.4
            )
        )
    a0.text(0, -R_OUT + 3, "blue: recess 30 mm, red: label 21 mm", ha="center", fontsize=8)
    a1.add_patch(Circle((0, 0), geo["outer"], fill=True, alpha=0.25, color="tab:blue"))
    a1.add_patch(Circle((0, 0), geo["inner"], fill=True, fc="white", ec="tab:blue"))
    a1.add_patch(
        Rectangle((-LABEL / 2, -LABEL / 2), LABEL, LABEL, fill=False, ec="tab:red", lw=1.5)
    )
    for k in range(4):
        a = math.radians(45 + 90 * k)
        a1.add_patch(
            Circle(
                (geo["foot_r"] * math.cos(a), geo["foot_r"] * math.sin(a)),
                geo["foot_pad_r"],
                fc="tab:green",
                alpha=0.4,
            )
        )
    a1.text(
        0,
        -R_OUT + 3,
        f"ring R {geo['inner']:.1f} to {geo['outer']:.1f} mm",
        ha="center",
        fontsize=8,
    )
    a2.add_patch(Circle((0, 0), RECESS_D / 2, fill=True, alpha=0.25, color="tab:blue"))
    a2.add_patch(Rectangle((-7, -7), 14, 14, fill=False, ec="tab:red", lw=1.5))
    a2.text(0, -R_OUT + 3, "14 mm label, covered when mounted", ha="center", fontsize=8)
    fig.suptitle(
        "Back of the housing, 53 mm (plan geometry only; SPIKE, working values)", fontsize=10
    )
    fig.savefig(path, dpi=110, bbox_inches="tight")


def main(argv: list[str]) -> int:
    for c in run():
        print(f"{'PASS' if c.ok else 'FAIL'}  {c.name}: {c.detail}")
    if len(argv) > 1:
        draw(argv[1])
        print(f"wrote {argv[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
