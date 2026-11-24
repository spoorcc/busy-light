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
            "Evidence": "TI package addendum 29-Apr-2025 (Active, DBV 5) and DigiKey listing; no LCSC or JLCPCB listing "
            "of this exact part found by web search 2026-11-18 (only TPS3840DL40DBVRQ1 C6560464, shown out of stock)",
        },
        "TPS3808G01": {   # ADR-0025 option B, owner decision 2026-11-24
            "MPN": "TPS3808G01DBVR",
            "Manufacturer": "Texas Instruments",
            "LCSC": "C19653",
            "Evidence": "LCSC and JLCPCB part pages 2026-11-24: LCSC stock 0, JLCPCB overseas stock 4 (thin; extended); datasheet SBVS050N "
            "(hw/evidence/parts/tps3808g01.yaml); fallback Q1 variant C130062, pin-compatible, datasheet not read",
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
            "LCSC": "C15999",
            "Evidence": "ST product page (Active, SOT666); LCSC C15999 listing (ST, SOT-666-6) by web search "
            "2026-11-18, page not opened",
        },
        "74LVC1G04": {
            "MPN": "SN74LVC1G04DCKR",
            "Manufacturer": "Texas Instruments",
            "LCSC": "C8207",
            "Evidence": "LCSC/JLCPCB/distributor listing, web search 2026-11-18 (snippets; datasheet and shop pages not opened from this container)" + "; SC-70-5 (DCK), ADR-0023",
        },
        "74LVC1G08": {
            "MPN": "SN74LVC1G08DCKR",
            "Manufacturer": "Texas Instruments",
            "LCSC": "C7832",
            "Evidence": "JLCPCB part page 2026-11-22: 207,023 in stock, extended; SN74LVC1G08 SCES217AA read 2026-11-22 "
            "(hw/evidence/parts/sn74lvc1g08.yaml; DCK pin table: 1 A, 2 B, 3 GND, 4 Y, 5 VCC); SC-70-5 (DCK), ADR-0024",
        },
        "74LVC1G11": {
            "MPN": "SN74LVC1G11DCKR",
            "Manufacturer": "Texas Instruments",
            "LCSC": "C529281",
            "Evidence": "LCSC/JLCPCB/distributor listing, web search 2026-11-18 (snippets; datasheet and shop pages not opened from this container)" + "; SC-70-6 (DCK), ADR-0023",
        },
        "74AHCT1G125": {
            "MPN": "SN74AHCT1G125DCKR",
            "Manufacturer": "Texas Instruments",
            "LCSC": "C350557",
            "Evidence": "LCSC/JLCPCB/distributor listing, web search 2026-11-18 (snippets; datasheet and shop pages not opened from this container)" + "; SC-70-5 (DCK), ADR-0023",
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
        "BZT52C5V1S": {
            "MPN": "BZT52C5V1S",
            "Manufacturer": "LGE",
            "LCSC": "C545356",
            "Evidence": "LCSC/JLCPCB/distributor listing, web search 2026-11-18 (snippets; datasheet and shop pages not opened from this container)" + "; SOD-323 5.1 V 200 mW zener (4.8 to 5.4 V at 5 mA in one JLCPCB listing of the same type); several makers; JLCPCB lists other makers as Extended; ADR-0023",
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
        # HW-010 approved table (2026-11-07): Yageo RT 0.1 % 25 ppm. The FH TD03G parts of 2026-11-08 showed 0 stock at LCSC and
        # JLCPCB on 2026-11-22 (analysis-ilim-drift.md); drift limits in hw/evidence/parts/ilim-resistors.yaml.
        "47.0k 0.1%": {
            "MPN": "RT0603BRD0747KL",
            "Manufacturer": "Yageo",
            "LCSC": "C326725",
            "Evidence": "JLCPCB part page 2026-11-22: 17,723 in stock, extended; LCSC page 0; thin film 0603 0.1% 25 ppm (HW-010 table)",
        },
        "56.2k 0.1%": {
            "MPN": "RT0603BRD0756K2L",
            "Manufacturer": "Yageo",
            "LCSC": "C705784",
            "Evidence": "JLCPCB part page 2026-11-22: 5,618 in stock, extended; LCSC page 5,600; thin film 0603 0.1% 25 ppm (HW-010 table)",
        },
        "54.9k 0.1%": {   # R_ILIM3, owner decision 2026-11-24 (option A of analysis-ilim-drift.md)
            "MPN": "AT0603BRD0754K9L",
            "Manufacturer": "Yageo",
            "LCSC": "C855900",
            "Evidence": "LCSC page 2026-11-24: 430 in stock; JLCPCB page 768 (extended); thin film 0603 0.1 % 25 ppm (AT class, analysis-ilim-drift.md)",
        },
        "68n C0G 5% 50V": {   # C1, ADR-0025
            "MPN": "GRM3195C1H683JA05D",
            "Manufacturer": "Murata Electronics",
            "LCSC": "C3847777",
            "Evidence": "LCSC page 2026-11-24: 2,335 in stock; JLCPCB page 2,338 (extended); 1206 68 nF C0G 5 % 50 V (ADR-0025)",
        },
        "27.7k 0.1%": {
            "MPN": "RT0805BRD0727K7L",
            "Manufacturer": "Yageo",
            "LCSC": "C865349",
            "Evidence": (
                "JLCPCB library mirror query recorded in docs/verification/reports/stock-check-ilim-holdoff.md (27.7 k row: "
                "0.1 % exists in 0805 only, C865349 RT0805BRD0727K7L); stock not confirmed; plan 08 trim T1, 2026-11-17"
            ),
        },
        "5m 1% 1W": {   # R22, HW-017 approved amendment 2026-11-22 (2 to 5 mohm 1206 current-sense link, >= 3 A)
            "MPN": "RLM12FTCMR005",
            "Manufacturer": "TA-I Tech",
            "LCSC": "C316225",
            "Evidence": (
                "JLCPCB part page 2026-11-22: 125,869 in stock, extended; LCSC 125,860; datasheet TRLM-120S032E: metal alloy, "
                "1 W, +-1 %, +-50 ppm/degC, AEC-Q200 (hw/evidence/parts/rlm12.yaml); second source Prosemi LMS12CF1P0R005 C5121708"
            ),
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

# Package-specific entries (ADR-0023, 2026-11-18): the same value text in another package is another part.
# Key: (value, footprint name without the library). Looked up first.
_U04 = "UNI-ROYAL"
_U04E = "JLCPCB listing, web search 2026-11-18: JLCPCB basic part, 0402 thick film 1% 62.5 mW 50 V; ADR-0023"
SOURCING_BY_FP = {
    ("100k", "R_0402_1005Metric"): {"MPN": "0402WGF1003TCE", "Manufacturer": _U04, "LCSC": "C25741", "Evidence": _U04E},
    ("10k", "R_0402_1005Metric"): {"MPN": "0402WGF1002TCE", "Manufacturer": _U04, "LCSC": "C25744", "Evidence": _U04E},
    ("1k", "R_0402_1005Metric"): {"MPN": "0402WGF1001TCE", "Manufacturer": _U04, "LCSC": "C11702", "Evidence": _U04E},
    ("470", "R_0402_1005Metric"): {"MPN": "0402WGF4700TCE", "Manufacturer": _U04, "LCSC": "C25117", "Evidence": _U04E},
    ("100n", "C_0402_1005Metric"): {"MPN": "CL05B104KO5NNNC", "Manufacturer": "Samsung Electro-Mechanics", "LCSC": "C1525",
                                    "Evidence": "JLCPCB listing, web search 2026-11-18: basic part, 0402 100 nF 16 V X7R 10%; ADR-0023"},
    # ADR-0024 (2026-11-22): R6 150k, R24 and R25 100 ohm. LCSC and JLCPCB part pages read 2026-11-22 (class: JLCPCB list).
    ("150k", "R_0402_1005Metric"): {"MPN": "0402WGF1503TCE", "Manufacturer": _U04, "LCSC": "C25755",
                                    "Evidence": "JLCPCB part page 2026-11-22: 962,571 in stock, extended; 0402 thick film 1% 62.5 mW 50 V; ADR-0024"},
    ("100", "R_0402_1005Metric"): {"MPN": "0402WGF1000TCE", "Manufacturer": _U04, "LCSC": "C25076",
                                   "Evidence": "JLCPCB part page 2026-11-22: 9,893,219 in stock, basic; 0402 thick film 1% 62.5 mW 50 V; ADR-0024"},
    # ADR-0025 (2026-11-24): SENSE divider top resistor. 931 k 1 % has no stocked 0402 part (Walsin C172143, KOA C2577872 and LIZ C100560 show 0
    # at LCSC); 910 k Panasonic ERJ2RKF9103X: LCSC page 500, JLCPCB 540, extended, 0402 thick film 1 % 100 mW 100 ppm.
    ("910k 1%", "R_0402_1005Metric"): {"MPN": "ERJ2RKF9103X", "Manufacturer": "Panasonic", "LCSC": "C409936",
                                       "Evidence": "LCSC and JLCPCB part pages 2026-11-24 (500 and 540 in stock, extended); 910 k replaces 931 k, ADR-0025"},
    ("1u", "C_0402_1005Metric"): {"MPN": "CL05A105KA5NQNC", "Manufacturer": "Samsung Electro-Mechanics", "LCSC": "C52923",
                                  "Evidence": "JLCPCB listing, web search 2026-11-18: basic part, 0402 1 uF 25 V X5R 10%; ADR-0023"},
    ("330", "R_0402_1005Metric"): {"MPN": "0402WGF3300TCE", "Manufacturer": _U04, "LCSC": "C25104",
                                   "Evidence": _U04E + "; the 330 ohm value is read from the part number, the listing text did not show it"},
}

FIELDS = ("MPN", "Manufacturer", "LCSC")


def sourcing_fields(value: str, footprint: str = "") -> dict[str, str]:
    """Return the three BOM fields of a part value (and footprint, for package-specific parts); empty when it has no
    recorded source."""
    fp = footprint.split(":", 1)[-1]
    entry = SOURCING_BY_FP.get((value, fp)) or SOURCING.get(value, {})
    return {k: entry.get(k, "") for k in FIELDS}
