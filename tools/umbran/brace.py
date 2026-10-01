"""Umbran door/trapdoor: use the door bottom's diagonal-brace design everywhere (keeps color and grain)."""
import os
from PIL import Image
B='orig/assets/biomesoplenty/textures/'; O='out/assets/biomesoplenty/textures/'
L=lambda n: Image.open(B+n).convert('RGBA')
bottom=L('block/umbran_door_bottom.png')
top_half=bottom.transpose(Image.FLIP_TOP_BOTTOM)  # top half mirrors the bottom brace
door=Image.new('RGBA',(16,32)); door.paste(top_half,(0,0)); door.paste(bottom,(0,16))

def item_from(img):
    # Keep the icon's outline; sample the inside from the full (two-brace) door, scaled to the icon's shape.
    img=img.copy(); px=img.load(); dp=door.load()
    rows={}
    for y in range(img.height):
        xs=[x for x in range(img.width) if px[x,y][3]>0]
        if xs: rows[y]=(min(xs),max(xs))
    top,bot=min(rows),max(rows); x0=min(a for a,_ in rows.values()); x1=max(b for _,b in rows.values())
    for y,(a,b) in rows.items():
        if y in (top,bot): continue
        for x in range(a+1,b):
            u=min(15,int((x-x0)/(x1-x0+1)*16)); v=min(31,int((y-top)/(bot-top+1)*32))
            px[x,y]=dp[u,v]
    return img

def trapdoor():
    # Original trapdoor's clean 2px frame (no door hinge notches) around the door bottom's brace design.
    t=L('block/umbran_trapdoor.png'); tp=t.load(); bp=bottom.load()
    for y in range(2,14):
        for x in range(2,14):
            tp[x,y]=bp[x,y]
    return t

out={'block/umbran_door_top.png':top_half.copy(),'block/umbran_trapdoor.png':trapdoor(),'item/umbran_door.png':item_from(L('item/umbran_door.png'))}
for k,v in out.items():
    os.makedirs(os.path.dirname(O+k),exist_ok=True); v.save(O+k)

def row(top,trap,item,bot):
    d=Image.new('RGBA',(16,32)); d.paste(top,(0,0)); d.paste(bot,(0,16))
    S=10; parts=[p.resize((p.width*S,p.height*S),Image.NEAREST) for p in (d,trap,item)]
    r=Image.new('RGBA',(sum(p.width for p in parts)+30*4,max(p.height for p in parts)+40),(40,40,40,255)); x=30
    for p in parts: r.paste(p,(x,20),p); x+=p.width+30
    return r
a=row(L('block/umbran_door_top.png'),L('block/umbran_trapdoor.png'),L('item/umbran_door.png'),bottom)
b=row(out['block/umbran_door_top.png'],out['block/umbran_trapdoor.png'],out['item/umbran_door.png'],bottom)
img=Image.new('RGBA',(max(a.width,b.width),a.height+b.height),(40,40,40,255)); img.paste(a,(0,0)); img.paste(b,(0,a.height)); img.save('brace.png'); print('ok')
