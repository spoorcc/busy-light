# SPDX-License-Identifier: Apache-2.0
"""Sourcing fields (MPN, manufacturer, supplier number) for the schematic BOM (HW-008, HW-010).

Only entries with a recorded source are listed. A part that is not listed gets empty fields,
and `pcb_fabreview.py` reports it as missing an MPN. Never add a number from memory:
every entry names its evidence. Key: the part Value text of the netlist.
"""

SOURCING = {
    "TMUX1101DCKR": {
        "MPN": "TMUX1101DCKR",
        "Manufacturer": "Texas Instruments",
        "LCSC": "C2673506",
        "Evidence": ("owner decision 2026-11-05 (a), comment in gen_gate.py; "
                     "datasheet SCDS410D (pins)"),
    },
}

FIELDS = ("MPN", "Manufacturer", "LCSC")


def sourcing_fields(value: str) -> dict[str, str]:
    """Return the three BOM fields of a part value; empty when it has no recorded source."""
    entry = SOURCING.get(value, {})
    return {k: entry.get(k, "") for k in FIELDS}
