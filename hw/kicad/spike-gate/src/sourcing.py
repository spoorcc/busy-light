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
        "Evidence": (
            "owner decision 2026-11-05 (a), comment in gen_gate.py; datasheet SCDS410D (pins)"
        ),
    },
}

# Web lookups of 2026-11-08 (distributor and TI package-addendum listings, not the
# manufacturers' ordering
# tables unless stated). Orderable names and LCSC numbers must be re-checked against the shop at
# order time
# (HW-008, spike 7.4). Not listed on purpose: ESP32-C3-MINI-1 (flash variant -N4/-H4 not
# decided), J1 (GCT
# USB4085-GF-A is a through-hole part; the footprint is edge mount), TVS1/TVS2 (no part chosen),
# C2 to C6 (tbd),
# resistors and capacitors (no manufacturer chosen).
_DK = "distributor listing (DigiKey/LCSC/RS), web lookup 2026-11-08"
SOURCING.update(
    {
        "TUSB321": {
            "MPN": "TUSB321RWBR",
            "Manufacturer": "Texas Instruments",
            "LCSC": "C139392",
            "Evidence": _DK + "; LCSC notes not recommended for new designs",
        },
        "TPS3840DL40": {
            "MPN": "TPS3840DL40DBVR",
            "Manufacturer": "Texas Instruments",
            "LCSC": "",
            "Evidence": "TI package addendum 29-Apr-2025 (Active, DBV 5) and DigiKey listing",
        },
        "TPS2553": {
            "MPN": "TPS2553DBVR",
            "Manufacturer": "Texas Instruments",
            "LCSC": "C55266",
            "Evidence": "TI package addendum 25-Mar-2026 and "
            + _DK
            + "; not the latch-off -1 version",
        },
        "TLV75733PDBV": {
            "MPN": "TLV75733PDBVR",
            "Manufacturer": "Texas Instruments",
            "LCSC": "C485517",
            "Evidence": _DK + " only; no TI page seen",
        },
        "USBLC6-2P6": {
            "MPN": "USBLC6-2P6",
            "Manufacturer": "STMicroelectronics",
            "LCSC": "",
            "Evidence": "ST product page (Active, SOT666)",
        },
        "74LVC1G04": {
            "MPN": "SN74LVC1G04DBVR",
            "Manufacturer": "Texas Instruments",
            "LCSC": "C7827",
            "Evidence": _DK,
        },
        "74LVC1G02": {
            "MPN": "SN74LVC1G02DBVR",
            "Manufacturer": "Texas Instruments",
            "LCSC": "",
            "Evidence": _DK + " (DigiKey Active)",
        },
        "74LVC1G08": {
            "MPN": "SN74LVC1G08DBVR",
            "Manufacturer": "Texas Instruments",
            "LCSC": "",
            "Evidence": _DK,
        },
        "74LVC1G11": {
            "MPN": "SN74LVC1G11DBVR",
            "Manufacturer": "Texas Instruments",
            "LCSC": "",
            "Evidence": _DK + " (SOT-23-6)",
        },
        "74AHCT1G125": {
            "MPN": "SN74AHCT1G125DBVR",
            "Manufacturer": "Texas Instruments",
            "LCSC": "",
            "Evidence": _DK,
        },
        "WS2812B": {
            "MPN": "WS2812B-2020",
            "Manufacturer": "Worldsemi",
            "LCSC": "C965555",
            "Evidence": _DK
            + "; LCSC lists 2.2x2 mm, the footprint is 2.0x2.0 mm: check the drawing",
        },
        "BZX84C5V1": {
            "MPN": "BZX84-C5V1,215",
            "Manufacturer": "Nexperia",
            "LCSC": "C294621",
            "Evidence": _DK + "; datasheet PDF not opened",
        },
        "Button": {
            "MPN": "TL3342F160QG",
            "Manufacturer": "E-Switch",
            "LCSC": "C2886898",
            "Evidence": _DK + "; footprint is the TL3342 family, force variant is an assumption",
        },
    }
)

FIELDS = ("MPN", "Manufacturer", "LCSC")


def sourcing_fields(value: str) -> dict[str, str]:
    """Return the three BOM fields of a part value; empty when it has no recorded source."""
    entry = SOURCING.get(value, {})
    return {k: entry.get(k, "") for k in FIELDS}
