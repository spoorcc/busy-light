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
# (HW-008, spike 7.4). Not listed on purpose: ESP32-C3-MINI-1 variant entries are below; J1, TVS1, TVS2 are set
# at the end of this file (2026-11-09).
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
            "Evidence": _DK + "; Nexperia BZX84 series Rev. 7 read 2026-11-09 (hw/evidence/parts/bzx84c5v1.yaml, unverified claims)",
        },
        "Button": {
            "MPN": "TL3342F160QG",
            "Manufacturer": "E-Switch",
            "LCSC": "C2886898",
            "Evidence": _DK + "; footprint is the TL3342 family, force variant is an assumption",
        },
    }
)

# Passives, owner choice 2026-11-08: JLCPCB basic-library parts (Uni-Royal thick film, Samsung/Murata MLCC);
# 0.1% resistors are not in the basic library (FH/Yageo thin film). Web lookups of 2026-11-08, LCSC/JLCPCB
# listing pages only, no datasheet opened. Not listed: C2, C3, C5, C6 (the real parts wait for the DC-bias
# and effective-capacitance analysis of HW-014/HW-015) and C4/C32 (DNP spares).
_LU = "LCSC/JLCPCB listing, web lookup 2026-11-08; JLCPCB basic part; "


def _uni(mpn: str, lcsc: str, note: str = "") -> dict[str, str]:
    return {"MPN": mpn, "Manufacturer": "UNI-ROYAL", "LCSC": lcsc, "Evidence": _LU + "0603 1% 100 mW" + note}


SOURCING.update(
    {
        "10k": _uni("0603WAF1002T5E", "C25804"),
        "100k": _uni("0603WAF1003T5E", "C25803"),
        "1k": _uni("0603WAF1001T5E", "C21190"),
        "330": _uni("0603WAF3300T5E", "C23138"),
        "470": _uni("0603WAF4700T5E", "C23179"),
        "150k": _uni("0603WAF1503T5E", "C22807", "; LCSC product page not seen, number from the JLCPCB page"),
        "887k": _uni("0603WAF8873T5E", "C23259", "; listing showed 0 stock, check at order time"),
        "301 0.1%": {
            "MPN": "TD03G3010BT",
            "Manufacturer": "FH (Guangdong Fenghua)",
            "LCSC": "C666860",
            "Evidence": "LCSC listing, web lookup 2026-11-08; thin film 0603 0.1% 25 ppm, extended part",
        },
        "47.0k 0.1%": {
            "MPN": "TD03G4702BT",
            "Manufacturer": "FH (Guangdong Fenghua)",
            "LCSC": "C667109",
            "Evidence": "JLCPCB listing, web lookup 2026-11-08; thin film 0603 0.1% 25 ppm, extended part",
        },
        "56.2k 0.1%": {
            "MPN": "TD03G5622BT",
            "Manufacturer": "FH (Guangdong Fenghua)",
            "LCSC": "C667119",
            "Evidence": "LCSC datasheet file name and listing text, web lookup 2026-11-08; thin film 0603 0.1% 25 ppm",
        },
        "27.4k 0.1%": {
            "MPN": "RT0603BRE0727K4L",
            "Manufacturer": "Yageo",
            "LCSC": "",
            "Evidence": "DigiKey listing, web lookup 2026-11-08 (thin film 0603 0.1%); no LCSC number seen",
        },
        "100n": {
            "MPN": "CL10B104KB8NNNC",
            "Manufacturer": "Samsung Electro-Mechanics",
            "LCSC": "C1591",
            "Evidence": _LU + "0603 100 nF 50 V X7R 10%",
        },
        "1u": {
            "MPN": "CL10A105KB8NNNC",
            "Manufacturer": "Samsung Electro-Mechanics",
            "LCSC": "C15849",
            "Evidence": _LU + "0603 1 uF 50 V X5R 10%; DC-bias derating not analysed",
        },
        "100n C0G 5% 50V": {
            "MPN": "GRM31C5C1H104JA01L",
            "Manufacturer": "Murata",
            "LCSC": "C97946",
            "Evidence": "LCSC listing, web lookup 2026-11-08; 1206 100 nF 50 V C0G 5%",
        },
        "ESP32-C3-MINI-1": {
            "MPN": "ESP32-C3-MINI-1-N4",
            "Manufacturer": "Espressif",
            "LCSC": "C2838502",
            "Evidence": "owner choice of the N4 flash variant 2026-11-08; LCSC/JLCPCB listing (extended part)",
        },
    }
)

# TVS1: owner choice 2026-11-09, surge option S1 (measure the real hot-plug surge first, RV-013 finding 9): a plain
# 5 V SOD-323 TVS on the spike. The clamp is 10 V at 1 A and 14 V at 12 A (datasheet text via web search), above the
# 6 V and 7 V maximum of several parts; the surge measurement (TC-210 step 4) decides S2 or S3 for the next board.
SOURCING["TVS"] = {
    "MPN": "PESD5V0S1BA,115",
    "Manufacturer": "Nexperia",
    "LCSC": "C19224",
    "Evidence": ("owner choice 2026-11-09 (surge option S1); LCSC/JLCPCB listing and datasheet text via web search "
                 "2026-11-09: bidirectional 5 V stand-off, SOD-323, Cd 35 pF typ at 0 V, clamp 14 V max at 12 A; "
                 "datasheet read 2026-11-09 (hw/evidence/parts/pesd5v0s1ba.yaml, unverified claims); does NOT keep the 6 V pins below 6 V on its own"),
}

# J1: USB4085-GF-A identified 2026-11-09. There is no edge-mount variant: the GCT drawing (rev B) lists one part,
# "Dip Type, PCB Top Mount", and the project footprint has its pad pattern; the edge position is a placement choice.
SOURCING["USB-C receptacle"] = {
    "MPN": "USB4085-GF-A",
    "Manufacturer": "Global Connector Technology (GCT)",
    "LCSC": "C7095263",
    "Evidence": ("GCT drawing USB4085 rev B read 2026-11-09 (hw/evidence/parts/usb-c-receptacle.yaml, unverified claims); "
                 "LCSC listing via web search, one snapshot showed 0 stock, check live stock; through-hole part, "
                 "hand or selective soldering at assembly"),
}

# TVS2 (button input, 3V3 GPIO): owner choice 2026-11-09 between PESD3V3L1BA and a reuse of the TVS1 part.
SOURCING["ESD diode"] = {
    "MPN": "PESD3V3L1BA,115",
    "Manufacturer": "Nexperia",
    "LCSC": "C51450",
    "Evidence": ("owner choice 2026-11-09; data sheet PESDxL1BA series Rev. 02 (2009, NXP era) read 2026-11-09 "
                 "(hw/evidence/parts/pesd3v3l1ba.yaml, unverified claims); LCSC listing via web search, stock and "
                 "Basic/Extended status not read; a newer Nexperia revision may differ"),
}

_DCB = ("LCSC/JLCPCB listing, web lookup 2026-11-09; X5R +-10 %. DC-bias curve read from the "
        "Samsung Component Library 2026-11-09 and applied in hw/sim/scripts/dc_bias_caps.py")
SOURCING.update(
    {
        "4.7u 16V X5R": {"MPN": "CL10A475KO8NNNC", "Manufacturer": "Samsung Electro-Mechanics",
                         "LCSC": "C19666", "Evidence": _DCB + "; 0603 4.7 uF 16 V, JLCPCB basic part (C2)"},
        "10u 25V X5R": {"MPN": "CL21A106KAYNNNE", "Manufacturer": "Samsung Electro-Mechanics",
                        "LCSC": "C15850", "Evidence": _DCB + "; 0805 10 uF 25 V (C3); listing showed 0 stock"},
        "2.2u 16V X5R": {"MPN": "CL10A225KO8NNNC", "Manufacturer": "Samsung Electro-Mechanics",
                         "LCSC": "C23630", "Evidence": _DCB + "; 0603 2.2 uF 16 V, JLCPCB basic part (C5)"},
        "10u 10V X5R": {"MPN": "CL10A106KP8NNNC", "Manufacturer": "Samsung Electro-Mechanics",
                        "LCSC": "C19702", "Evidence": _DCB + "; 0603 10 uF 10 V (C6); one LCSC page marks it not recommended for new designs"},
    }
)

FIELDS = ("MPN", "Manufacturer", "LCSC")


def sourcing_fields(value: str) -> dict[str, str]:
    """Return the three BOM fields of a part value; empty when it has no recorded source."""
    entry = SOURCING.get(value, {})
    return {k: entry.get(k, "") for k in FIELDS}
