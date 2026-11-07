# SPDX-License-Identifier: Apache-2.0
"""Spike: PCB design-rule numbers that need no KiCad module (testable with any Python).

One source for the rule values of the spike (plan 06 G2): pcb_full (board settings, project file), pcb_stitch and the
.kicad_dru written by write_dru read them from here. Values are millimetres. They are not looser than FLOOR."""


def ipc2221_width_mm(current_a, rise_k=10.0, oz=1.0, internal=False):
    """Minimum trace width in mm from IPC-2221 (the curve fit, not a measurement): I = k * dT^0.44 * A^0.725,
    A in square mil, k = 0.048 for an external layer (0.024 internal). 1 oz copper is 1.378 mil thick."""
    k = 0.024 if internal else 0.048
    area_mil2 = (current_a / (k * rise_k ** 0.44)) ** (1.0 / 0.725)
    width_mil = area_mil2 / (1.378 * oz)
    return width_mil * 0.0254


# Highest current the TPS2553 limit may pass in the top step: 1577 mA (HW-010 / analysis-ilim-steps, E192 0.1 % set).
I_TOP_STEP_MAX_A = 1.577
# Net widths in mm used by the spike. IPC-2221 external layer, 1 oz, 10 K rise: 1.5 A -> 0.53 mm, 1.577 A -> 0.56 mm,
# 2.0 A -> 0.78 mm. The spike uses 0.6 mm (>= 0.56 mm for the highest allowed current limit); the earlier run used
# 0.8 mm (2.0 A) and left the VBUS_IC net unrouted.
NET_WIDTH = {"VBUS_IC": 0.6, "+5V": 0.6, "+3V3": 0.3}      # +3V3: 0.3 mm = 1.0 A by IPC-2221 (the TLV757P rating); the ESP32-C3 needs about 0.35 A


# ---- rule values (moved here from pcb_full.py and pcb_stitch.py; the numbers are unchanged)
CLEARANCE = 0.15            # default net class clearance (the J1 pad gap is 0.15 mm)
TRACK = 0.15                # default signal width (0.2 made the router squeeze wires to 0.10 and 0.12 mm at tight pads)
MIN_TRACK = 0.15            # smallest track (the CC lines at the 0.4 mm pitch pads of U1)
VIA_DIA, VIA_DRILL = 0.6, 0.3
MIN_VIA_DIA = 0.5
MIN_THROUGH_HOLE = 0.3
ANNULAR = 0.1               # minimum via annular ring
HOLE_CLEARANCE = 0.25
HOLE_TO_HOLE = 0.4
EDGE_CLEARANCE = 0.3        # copper to board edge
NET_TRACK = {"/CC1": 0.15, "/CC2": 0.15}   # nets at the 0.4 mm pitch pads of U1 use the minimum width

# Stitcher (pcb_stitch.py): margin added to the base clearance, margin to the board edge, width of the stitch track.
STITCH_MARGIN = 0.06
STITCH_EDGE_MARGIN = 0.6
STITCH_W = {"GND": 0.25}    # GND has no current rating in NET_WIDTH; +5V uses NET_WIDTH["+5V"]
STITCH_W_DEFAULT = 0.25
# Nets that the stitcher completes after routing (the router sees no pour); M1 does not count them.
PLANE_NET_ORDER = ("GND", "+5V")        # stitching order
PLANE_NETS = frozenset(PLANE_NET_ORDER)

# What the router sees as a pour (`planes` argument of pcb_dsn.py export and run_pcb.sh; plan 06 A-7, A-8).
PLANES_OUTER = ("B", "F", "FB")         # legacy: GND pour on the listed outer layers, inner zones kept
INNER_ROUTER_NETS = frozenset({"GND"})  # `inner`: only the inner GND plane is visible to the router


def router_keeps_zone(planes, layer, net):
    """True when the DSN export keeps the zone on `layer` ("F", "B", "In1", ...) with net `net` for setting `planes`.
    `none`: no zone. `inner`: inner-layer zones of INNER_ROUTER_NETS only (the +5V plane and outer zones are removed from
    the router's view; the stitcher completes what the router leaves). B, F, FB: the listed outer layers and all inner
    zones (the behaviour before A-8). Case-insensitive; any other value raises ValueError."""
    p = planes.upper()
    outer = layer in ("F", "B")
    if p == "NONE":
        return False
    if p == "INNER":
        return (not outer) and net in INNER_ROUTER_NETS
    if p not in PLANES_OUTER:
        raise ValueError("planes must be one of none, inner, B, F, FB: %r" % planes)
    return layer in p if outer else True

# The values found in write_project and the stitcher at the start of G2 (the then current .kicad_pro). A value looser
# than its floor is a defect (test_pcb_rules). Guardrails section 3 (hole-to-hole 0.5, annular 0.25) is the stricter target.
FLOOR = {"clearance": 0.15, "track": 0.15, "via_diameter": 0.5, "through_hole": 0.3, "annular": 0.1,
         "hole_clearance": 0.25, "hole_to_hole": 0.4, "edge": 0.3}


def minimums():
    """The minimum values as used in the project file and the .kicad_dru, keyed like FLOOR."""
    return {"clearance": CLEARANCE, "track": MIN_TRACK, "via_diameter": MIN_VIA_DIA, "through_hole": MIN_THROUGH_HOLE,
            "annular": ANNULAR, "hole_clearance": HOLE_CLEARANCE, "hole_to_hole": HOLE_TO_HOLE, "edge": EDGE_CLEARANCE}


def stitch_width(net):
    """Width of the stitch track of a plane net: the net's current-based width when it has one, else STITCH_W."""
    if net in NET_WIDTH:
        return NET_WIDTH[net]
    return STITCH_W.get(net, STITCH_W_DEFAULT)


def net_class_name(net):
    return "PWR_" + net.strip("+")


def net_class_widths():
    """Track width per net class of the project file: the default class and one PWR_* class per NET_WIDTH net."""
    out = {"Default": TRACK}
    for n in sorted(NET_WIDTH):
        out[net_class_name(n)] = NET_WIDTH[n]
    return out


_DRU_RULES = (
    ("spike_clearance", "clearance", "CLEARANCE"),
    ("spike_track", "track_width", "MIN_TRACK"),
    ("spike_via", "via_diameter", "MIN_VIA_DIA"),
    ("spike_annular", "annular_width", "ANNULAR"),
    ("spike_hole_to_hole", "hole_to_hole", "HOLE_TO_HOLE"),
    ("spike_edge", "edge_clearance", "EDGE_CLEARANCE"),
)


# Footprints whose silkscreen findings the DRC ignores (DEV-006, proposed; owner decides).
SILK_WAIVER_REFS = ("U9", "U2", "U4", "TVS2", "J1")


def write_dru(path, layers=4):
    """Write the KiCad custom rules file (`(version 1)` syntax): the same minimums as the project file, as named rules,
    so a violation names the rule. Deterministic: same input, same bytes."""
    g = globals()
    lines = ["(version 1)", "# written by pcb_rules.write_dru (spike, plan 06 G2); do not edit by hand; layers: %d" % layers]
    for name, constraint, const in _DRU_RULES:
        lines.append('(rule "%s"' % name)
        lines.append("\t(constraint %s (min %gmm)))" % (constraint, g[const]))
    cond = " || ".join("A.memberOfFootprint('%s')" % ref for ref in SILK_WAIVER_REFS)
    lines.append("# silk of the stand-in and crowded footprints (DEV-006, proposed): the outline of U9 crosses parts inside its courtyard,")
    lines.append("# J1 sits at the board edge; fabricators clip silk over pads; the rule ignores only these footprints")
    lines.append('(rule "spike_silk_waiver"\n\t(severity ignore)\n\t(condition "(A.Layer == \'F.Silkscreen\' || A.Layer == \'B.Silkscreen\') && (%s)")\n\t(constraint silk_clearance))' % cond)
    lines.append('(rule "spike_silk_edge_waiver"\n\t(severity ignore)\n\t(condition "A.Layer == \'F.Silkscreen\' && A.memberOfFootprint(\'J1\')")\n\t(constraint edge_clearance))')
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

# Placement weights of the simulated-annealing placer (pcb_place.py): the half-perimeter wire length of the named
# nets counts this many times, so the ADR-0016 gate parts and the hold-off capacitors stay together. Without them the
# annealer minimises total wire length only and the layout rules of the tests hold by chance.
NET_WEIGHT = {"VBUS_IC": 3.0, "/ILIM_STEP2_EN": 4.0, "/ILIM_STEP3_EN": 4.0, "/SUP_CT": 3.0, "/ILIM": 2.0}
# Pin ties: a bypass capacitor sits at the supply pin of its part. Added to the annealer as two-pin pseudo-nets
# (not on the board): name -> ((ref, pad), (ref, pad), weight). Owner decision 2026-11-05 (a): 0.1 uF on the TMUX1101 VDD pin.
PIN_TIES = {"tie:C24-U14": (("C24", "1"), ("U14", "5"), 4.0),
            "tie:C25-U15": (("C25", "1"), ("U15", "5"), 4.0)}


# ---- post-route clean-up helpers (pure functions; used by pcb_dsn.py import and pcb_stitch.py; tested in test_pcb_rules)
import math as _math


def clamp_track_width(width_mm):
    """The router may write a narrower wire at a tight spot (Freerouting 2.5 wrote 0.10 and 0.12 mm); the board never
    keeps a track below MIN_TRACK."""
    return max(width_mm, MIN_TRACK)


def hole_gap_ok(x, y, vias, drill=VIA_DRILL, gap=HOLE_TO_HOLE):
    """True when a drill of diameter `drill` at (x, y) has at least `gap` between its edge and every via in `vias`
    ((x, y, ...) tuples with the via drill VIA_DRILL), whatever the net (the hole-to-hole rule knows no nets)."""
    return all(_math.hypot(x - v[0], y - v[1]) >= (drill + VIA_DRILL) / 2 + gap for v in vias)


def dangling_via_positions(drc):
    """Positions (mm) of the vias that a KiCad DRC report calls dangling (`via_dangling`)."""
    return [(i["pos"]["x"], i["pos"]["y"]) for v in drc.get("violations", []) if v["type"] == "via_dangling"
            for i in v["items"] if i["description"].startswith("Via")]


def reuse_targets(x, y, vias, net, max_dist):
    """Vias of net `net` within `max_dist` of (x, y), nearest first: a pad can join a via that exists already instead of
    getting a new one. `vias` holds (x, y, size, net) tuples."""
    c = [(_math.hypot(v[0] - x, v[1] - y), v) for v in vias if v[3] == net]
    return [v for d, v in sorted(c, key=lambda t: (t[0], t[1][0], t[1][1])) if d <= max_dist]


# Nets the router lays first, on their own, before the other nets (run_pcb.sh stage 1). Their tracks are locked for stage 2.
# Chosen from the nets that the single-pass run left open: the 1.5 A USB power path VBUS_IC (the only net still open after the
# placement change). Plane nets (GND, +5V) are left to the planes and the stitcher. Default off (KEYFIRST=0): see the report.
ROUTE_FIRST = ("VBUS_IC",)


def is_key_net(name):
    """True for the nets of ROUTE_FIRST (exact names, as in the KiCad board)."""
    return name in ROUTE_FIRST


# VBUS_IC carries the full switch current (up to I_TOP_STEP_MAX_A) only between the connector, the TPS2553 input, its input
# capacitor and the clamp; every other pin of the net (supervisor, ESD part, dividers, supply-pin resistors, enable) draws
# microamps. Stage 1 routes the main path alone at NET_WIDTH; stage 2 routes the branches at BRANCH_WIDTH and joins them to the
# locked main path. Pins: ref -> pins, None means every pin of the ref.
MAIN_PATH_NET = "VBUS_IC"
MAIN_PATH_PADS = {"J1": None, "U7": ("1",), "C2": ("1",), "TVS1": ("1",)}
BRANCH_WIDTH = 0.2


def is_main_path_pad(net, ref, pin):
    """True when the pad takes part in stage 1 of the split routing: any pad of a net other than MAIN_PATH_NET, and
    the MAIN_PATH_PADS pads of MAIN_PATH_NET."""
    if net != MAIN_PATH_NET:
        return True
    pins = MAIN_PATH_PADS.get(ref, ())
    return pins is None or pin in pins



def joins_nothing(x, y, track_ends, pad_boxes, tol=0.01):
    """True when removing a via at (x, y) cannot split a net: no pad is there, and every track end there is on one layer
    (such tracks touch each other at that point without the via; an end on a second layer would need it).
    track_ends: (x, y, layer) points; pad_boxes: (x0, y0, x1, y1)."""
    layers = {lay for ex, ey, lay in track_ends if _math.hypot(ex - x, ey - y) < tol}
    on_pad = any(x0 <= x <= x1 and y0 <= y <= y1 for x0, y0, x1, y1 in pad_boxes)
    return len(layers) <= 1 and not on_pad
