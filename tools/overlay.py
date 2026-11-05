import sys, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
SERIF="/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"
SERIF_B="/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
import os
if not os.path.exists(SERIF): SERIF=SERIF_B
INK=(74,52,48); 
def font(p,s,idx=0):
    return ImageFont.truetype(p,s,index=idx)  # idx 0 = JP in ttc? find JP
def jp(p,s):
    for i in range(10):
        try:
            f=ImageFont.truetype(p,s,index=i)
            if 'JP' in f.getname()[0]: return f
        except Exception: break
    return ImageFont.truetype(p,s)
def draw_block(im, lines, y, size, center=True, band=False, title=None):
    W,H=im.size
    d=ImageDraw.Draw(im,'RGBA')
    f=jp(SERIF,size); ft=jp(SERIF_B,int(size*1.15))
    rows=[]
    if title: rows.append((title,ft))
    rows+= [(l,f) for l in lines]
    lh=[int((fo.size)*1.75) for _,fo in rows]
    total=sum(lh)
    if band:
        pad=46
        top=y-pad-90
        band_img=Image.new('RGBA',im.size,(0,0,0,0)); bp=band_img.load()
        for yy in range(max(0,top),H):
            a=int(225*min(1,(yy-top)/110))
            for xx in range(W): bp[xx,yy]=(252,247,243,a)
        im.alpha_composite(band_img)
        d=ImageDraw.Draw(im,'RGBA')
    cy=y
    for (t,fo),h in zip(rows,lh):
        w=d.textlength(t,font=fo)
        x=(W-w)/2 if center else 90
        d.text((x,cy),t,font=fo,fill=INK+(255,))
        cy+=h
    return cy
def sign(im,n):
    W,H=im.size; d=ImageDraw.Draw(im,'RGBA')
    f=jp(SERIF,24); t=f"Hors Champ  {n}/5"
    w=d.textlength(t,font=f); d.text((W-w-40,H-56),t,font=f,fill=INK+(200,))
spec=json.load(open(sys.argv[1]))
for i,s in enumerate(spec['slides'],1):
    im=Image.open(s['src']).convert('RGBA')
    draw_block(im,s['lines'],s['y'],s.get('size',38),band=s.get('band',False),title=s.get('title'))
    sign(im,i)
    im.convert('RGB').save(f"{spec['out']}/{i}.jpg",quality=92)
print('ok')
