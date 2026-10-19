#!/usr/bin/env python3
"""Derive detail images from actual main PNG pixels. No independent hand redraw."""
from pathlib import Path
from PIL import Image
import json,hashlib,base64
import sys
sys.dont_write_bytecode=True
import build_references as r
D=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for key,name,bounds,pos,labels in [
 ('K02','S20_K02_F084_crossed_rods',(355,530,555,695),(1350,395,800,660),[(2160,620,'R/T_H 在上','TH'),(2160,900,'L/T_S 在下','TS')]),
 ('K03','S20_K03_F156_laugh_bundle',(600,680,800,810),(1370,445,800,520),[(2180,640,'C_N 在上','CN'),(2180,710,'C_B 在下','CB')])]:
 png=D/'reference'/f'{name}.png';svg=D/'reference/svg'/f'{name}.svg';native=D/'reference/details'/f'{key}_main_crop_native.png';im=Image.open(png).convert('RGBA').crop(bounds);im.save(native)
 x,y,w,h=pos;assert w/im.width==h/im.height==4
 item=r.txt(1320,370 if key=='K02' else 414,'由左主图原像素裁切×4；不镜像、不转角',23)
 item+=f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="data:image/png;base64,{base64.b64encode(native.read_bytes()).decode()}"/>'
 for tx,ty,label,col in labels:item+=r.txt(tx,ty,label,21,r.C[col],'700')
 if key=='K02':item+=r.txt(2160,659,'拇指↔食/中指',18)+r.txt(2160,939,'拇指↔屈指腹',18)
 else:item+=r.txt(2180,668,'拇指↔食指腹',17)+r.txt(2180,738,'拇指↔中/环指腹',17)
 s=svg.read_text();marker=f'<!-- SAME_VIEW_{key} -->';assert s.count(marker)==1,'Rebuild baseSVG before deriving a detail.';svg.write_text(s.replace(marker,item))
 records.append({'key':key,'main_PNG':str(png.relative_to(D)),'native_detail':str(native.relative_to(D)),'main_crop_bounds_xyxy':list(bounds),'native_detail_sha256':sha(native),'detail_box_xywh':list(pos),'positive_uniform_scale':4,'rotation_degrees':0,'horizontal_flip':False,'vertical_flip':False,'source_pixels':'LiteralRGBA crop from the left main drawing; verify against finalPNG crop after render.'})
# Geometric contact book: two boundaries per held shaft, plus a hidden-axis section.
x=r.FIGS['B_X'];xr=r.world(x,x['palms']['R']);xl=r.world(x,x['palms']['L']);X=(330,560);a=(X[0]-(xr[0]-X[0])*.5,X[1]-(xr[1]-X[1])*.5);b=(X[0]-(xl[0]-X[0])*.6,X[1]-(xl[1]-X[1])*.6)
bands=[]
for key,rod,a,z,xx,owner in [('K02','TH',a,(xr[0]+25,xr[1]+7),xr[0]-15,'X.R'),('K02','TS',b,(xl[0]+25,xl[1]+13),xl[0]-14,'X.L'),('K03','CN',(150,420),(678,726),678,'G.R'),('K03','CB',(150,540),(682,742),682,'G.R')]:
 p=r.on_axis(a,z,xx);dx,dy=z[0]-a[0],z[1]-a[1];ln=(dx*dx+dy*dy)**.5;n=(-dy/ln,dx/ln);bands.append({'key':key,'rod':rod,'owner':owner,'centre_xy':p,'thumb_side_xy':[p[0]-3.4*n[0],p[1]-3.4*n[1]],'opposed_finger_side_xy':[p[0]+3.4*n[0],p[1]+3.4*n[1]],'band_not_shared_with_other_rod':True})
assert bands[0]['centre_xy'][1]<bands[1]['centre_xy'][1]
assert bands[2]['centre_xy'][1]<bands[3]['centre_xy'][1]
(D/'provenance/gate_20261019/same_view_details.json').write_text(json.dumps({'method':'literal mainPNG crop + positive4xscale, no redrawn hand detail','records':records,'independent_contact_bands':bands,'expected_order':{'K02':'X.R/T_H aboveX.L/T_S','K03':'orangeC_N abovegreenC_B'},'image_generation_calls':0},ensure_ascii=False,indent=2)+'\n')
(D/'provenance/gate_20261019/three_time_transfers.json').write_text(json.dumps(r.TRANSFERS,ensure_ascii=False,indent=2)+'\n');print('2 literal main-view details embedded;4 independent contact bands and3×3 contact-time states recorded.')
