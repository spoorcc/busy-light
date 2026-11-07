# SPDX-License-Identifier: Apache-2.0
"""Working dimensions of the housing, concept B (MECH-001, 004, 006, 007, 009; ADR-0011, ADR-0014).

One source for the FreeCAD generator and the checks. All values are working values
in square brackets in docs/requirements/mech.md. Units: mm.
"""

# Outer shape (MECH-001)
D_OUT = 53.0
WALL = 1.6
FLOOR = 2.0
LID_T = 1.2
H_JOINT = 14.0  # lid joint height above the base outer face

# Board (hw/kicad spike outline) and Z chain
D_PCB = 46.0
T_PCB = 1.6
Z_PCB_BOT = 5.0
H_LED = 0.65
D_LED = 8.0  # LED top to lid underside (MECH-002)

# USB-C window (MECH-004)
WIN_W = 14.2
WIN_H = 8.2
WIN_ZC = 8.25
PLUG_W = 12.35
PLUG_H = 6.5

# Snap hooks on the board edge (MECH-009)
HOOK_COUNT = 3
HOOK_R = D_PCB / 2.0
HOOK_LIP = 0.8  # lip over the board edge
HOOK_W = 4.0

# Annular bayonet on the back (MECH-007, ADR-0014)
BAY_R_IN = 16.3
BAY_R_OUT = 21.0
BAY_DEPTH = 1.2
BAY_LUGS = 3
BAY_LUG_W = 1.2  # lug height: lip 0.4 + head 0.8 (reading of "lugs of 1.2 mm")
BAY_TURN_DEG = 30.0
# Concept of the lock (assumption, not yet in a requirement): a lip narrows the groove opening
# at the back face in the lock sectors; a T-shaped lug head turns in behind the lip.
BAY_LIP_W = 0.7  # radial overlap of the lip on each side of the groove
BAY_LIP_T = 0.4  # lip thickness, one print layer pair at the bed
BAY_LUG_ARC_DEG = 20.0  # angular size of one lug
BAY_ENTRY_DEG = 30.0  # entry sector: groove fully open
BAY_CLEAR = 0.3  # radial clearance lug to groove (FDM)
BAY_CLEAR_Z = 0.2  # axial clearance of the head behind the lip

# Lid joint (plan 05 section 4.3; the spigot sits on a chamfered inner ledge of the wall)
SPIGOT_T = 1.15
SKIRT_T = 0.8  # two print lines (plan 05 had 0.9)
SPIGOT_CLEAR = 0.35
Z_SPIGOT_TOP = Z_PCB_BOT + T_PCB + H_LED + D_LED  # lid underside, 15.25
LEDGE_Z = 12.8  # the wall steps in from here up to H_JOINT
LID_HOOK_DEG = (60.0, 180.0, 300.0)  # lid snap bumps and grooves
LID_BUMP = 0.3  # bump depth into the groove
LID_HOOK_W = 4.0

# PCB posts (plan 05 section 4.3)
POST_H = 3.0
POST_R = 21.0
POST_PAD_W = 4.0  # tangential
POST_PAD_R = 1.0  # radial, working value of the plan
POST_DEG = (60.0, 180.0, 300.0)  # none at the USB-C azimuth 0

# Button (plan 05: the switch is not chosen, so these are working values)
BTN_D = 7.0
BTN_DEG = 240.0
BTN_Z_ABOVE_PCB = 1.0

# Bayonet detent (a ridge in the groove ceiling that the lug head has to pass)
DETENT_START_DEG = 31.0  # from the start of the entry sector
DETENT_SPAN_DEG = 2.5
DETENT_H = 0.4  # ridge height from the ceiling; head top is 0.2 below the ceiling

# Label area (MECH-006)
LABEL_CIRCLE_D = 21.0

# FDM assumptions (not measured, see the report)
TOL_FDM = 0.30  # feature size
TOL_FDM_FINE = 0.20  # small features
TOL_PCB_D = 0.15  # board outline
TOL_PCB_T = 0.16
TOL_PLACE = 0.30  # placement of parts
NOZZLE = 0.4
