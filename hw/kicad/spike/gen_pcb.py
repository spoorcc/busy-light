import math, re, sys, pcbnew
from pcbnew import FromMM, VECTOR2I
toks=re.findall(r'\(|\)|"[^"]*"|[^\s()]+',open("k.net").read())
def parse(i=0):
    out=[]
    while i<len(toks):
        t=toks[i]
        if t=="(":
            sub,i=parse(i+1); out.append(sub)
        elif t==")": return out,i+1
        else: out.append(t.strip('"')); i+=1
    return out,i
tree=parse(0)[0][0]
def find(n,k): return [x for x in n if isinstance(x,list) and x and x[0]==k]
comps=find(find(tree,"components")[0],"comp"); nets=find(find(tree,"nets")[0],"net")
b=pcbnew.CreateEmptyBoard()
ec=pcbnew.PCB_SHAPE(b); ec.SetShape(pcbnew.SHAPE_T_CIRCLE); ec.SetLayer(pcbnew.Edge_Cuts)
ec.SetCenter(VECTOR2I(0,0)); ec.SetEnd(VECTOR2I(FromMM(23),0)); ec.SetWidth(FromMM(0.1)); b.Add(ec)
fps={}
comps.sort(key=lambda c:(re.sub(r"\d","",find(c,"ref")[0][1]),int(re.sub(r"\D","",find(c,"ref")[0][1]))))
leds=[c for c in comps if find(c,"value")[0][1].startswith("SK6812")]
for c in comps:
    ref=find(c,"ref")[0][1]; lib,name=find(c,"footprint")[0][1].split(":")
    fp=pcbnew.FootprintLoad(f"/usr/share/kicad/footprints/{lib}.pretty",name)
    fp.SetReference(ref)
    if c in leds:
        k=leds.index(c); a=math.radians(90-360*k/16)
        fp.SetPosition(VECTOR2I(FromMM(20*math.cos(a)),FromMM(-20*math.sin(a)))); fp.SetOrientationDegrees(-(90-360*k/16)+90)
    else: fp.SetPosition(VECTOR2I(0,0))
    b.Add(fp); fps[ref]=fp
for n in nets:
    name=find(n,"name")[0][1]; ni=pcbnew.NETINFO_ITEM(b,name); b.Add(ni)
    for node in find(n,"node"):
        ref=find(node,"ref")[0][1]; pin=find(node,"pin")[0][1]
        fps[ref].FindPadByNumber(pin).SetNet(ni)
b.Save("spike.kicad_pcb"); print("pcb saved",len(fps),"footprints",len(nets),"nets")
