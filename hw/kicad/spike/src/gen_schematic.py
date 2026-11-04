import sys, tomllib
from pathlib import Path
from schematic_writer import build
P = tomllib.loads((Path(__file__).parent / "params.toml").read_text())
OUT = sys.argv[1]
parts = [dict(ref="U1", lib="74xGxx", sym="74AHCT1G125", value="74AHCT1G125", footprint="Package_TO_SOT_SMD:SOT-23-5", req="HW-002",
              at=(60.96, 40.64), nets={"1": "+5V", "2": "MCU_DATA", "3": "GND", "4": "LED_DATA", "5": "+5V"})]
for i in range(P["ring"]["led_count"]):
    parts.append(dict(ref=f"D{i+1}", lib="LED", sym="WS2812B-2020", value="WS2812B-2020",
                      footprint="LED_SMD:LED_WS2812B-2020_PLCC4_2.0x2.0mm", req="HW-001", at=(25.4 + 25.4 * (i % 8), 101.6 + 38.1 * (i // 8)),
                      nets={"VDD": "+5V", "VSS": "GND", "DIN": "LED_DATA" if i == 0 else f"D{i}", "DOUT": f"D{i+1}" if i < P["ring"]["led_count"] - 1 else "D_END"}))
parts.append(dict(ref="J1", lib="Connector_Generic", sym="Conn_01x04", value="Conn_01x04", footprint="Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical", req="HW-001", at=(25.4, 40.64), nets={"1": "+5V", "2": "GND", "3": "MCU_DATA", "4": "D_END"}))
parts.append(dict(ref="#FLG1", lib="power", sym="PWR_FLAG", value="PWR_FLAG", footprint="", at=(101.6, 40.64), nets={"1": "+5V"}, power=True))
parts.append(dict(ref="#FLG2", lib="power", sym="PWR_FLAG", value="PWR_FLAG", footprint="", at=(114.3, 40.64), nets={"1": "GND"}, power=True))
build(parts, f"{OUT}/spike.kicad_sch", "busy-light spike")
