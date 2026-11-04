import os
os.environ["KICAD10_SYMBOL_DIR"]="/usr/share/kicad/symbols"
os.environ["KICAD10_FOOTPRINT_DIR"]="/usr/share/kicad/footprints"
from skidl import *
import skidl; print([t for t in dir(skidl) if t.startswith("KICAD")])
set_default_tool(KICAD10 if "KICAD10" in dir(skidl) else KICAD9)
lib_search_paths[KICAD10 if "KICAD10" in dir(skidl) else KICAD9].append("/usr/share/kicad/symbols")
vcc,gnd,din=Net("+5V"),Net("GND"),Net("LED_DATA")
buf=Part("74xGxx","74AHCT1G125",footprint="Package_TO_SOT_SMD:SOT-23-5")
print(buf.name,[ (p.num,p.name) for p in buf.pins])
prev=din
for i in range(16):
    led=Part("LED","SK6812MINI",footprint="LED_SMD:LED_SK6812MINI_PLCC4_3.5x3.5mm_P1.75mm",value="SK6812MINI")
    led["VDD"]+=vcc; led["VSS"]+=gnd; led["DIN"]+=prev
    prev=Net(f"D{i}"); led["DOUT"]+=prev
ERC()
generate_netlist(file_="spike.net")
try:
    generate_schematic(filepath=".",top_name="spike")
    print("schematic generated")
except Exception as e: print("sch fail",type(e).__name__,e)
