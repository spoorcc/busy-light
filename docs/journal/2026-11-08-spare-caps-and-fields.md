# 2026-11-08: capacitor values, spare C32, footprint fields

Owner choices: finding 4 first (values proposal accepted in full), a second spare footprint, C3 0805 and C4 1206. Work: generator values and footprints, C32, `pcb_spare_caps.py` (values, DNP, C32 placement and fields), routing with `pcb_fix.py auto`. Lesson: after the sourcing-field change I only ran ERC; the strict DRC on the stored board showed 100 field-mismatch warnings. Always run both gates after a schematic regeneration. Nothing pushed.
