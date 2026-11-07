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
WIN_W = 14.0
WIN_H = 8.0
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
BAY_LUG_W = 1.2
BAY_TURN_DEG = 30.0

# Label area (MECH-006)
LABEL_CIRCLE_D = 21.0

# FDM assumptions (not measured, see the report)
TOL_FDM = 0.30  # feature size
TOL_FDM_FINE = 0.20  # small features
TOL_PCB_D = 0.15  # board outline
TOL_PCB_T = 0.16
TOL_PLACE = 0.30  # placement of parts
NOZZLE = 0.4
