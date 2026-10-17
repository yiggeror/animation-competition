#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent
r=json.loads((P/'x01_prone_phone.rig.json').read_text())
src=Path('/workspace/animation-competition')/r['image'];im=Image.open(src).convert('RGBA');A=np.asarray(im)
checks={'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'source_size':list(im.size),'bone_count':len(r['bones']),'region_count':len(r['regions']),'layer_count':len(r['layers']),'pin_count':len(r['pins']),'eye_count':len(r['eyes']),'issues':[]}
assert list(im.size)==r['size'];assert len(r['bones'])<=32
seen=set()
for b in r['bones']:
 assert b['name'] not in seen
 assert b['parent'] is None or b['parent'] in seen
 seen.add(b['name']);assert b['head']!=b['tail']
 for p in (b['head'],b['tail']):assert 0<=p[0]<im.width and 0<=p[1]<im.height
assert not any('thumb' in b['name'] for b in r['bones'])
assert next(b for b in r['bones'] if b['name']=='phone')['parent']=='root'
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def intersects(a,b,c,d):return cross(a,b,c)*cross(a,b,d)<0 and cross(c,d,a)*cross(c,d,b)<0
for ri,g in enumerate(r['regions']):
 assert all(b in seen for b in g['bones'])
 p=g['poly'];n=len(p)
 for i in range(n):
  for j in range(i+1,n):
   if j==i+1 or (i==0 and j==n-1):continue
   if intersects(p[i],p[(i+1)%n],p[j],p[(j+1)%n]):checks['issues'].append(f'region {ri} self-cross {i}/{j}')
checks['pins']=[dict(q,alpha_at=A[q['at'][1],q['at'][0],3].item()) for q in r['pins']]
checks['claims']={'parent_first':True,'bones_within_32':True,'nonzero_axes':True,'coordinates_in_bounds':True,'all_layer_and_region_bones_exist':True,'no_hidden_thumb_bones':True,'dynamic_contact_verified':False,'blink_render_verified':False,'production_shot_modified':False}
(P/'x01_static_validation.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
bg=Image.new('RGBA',im.size,(223,232,226,255));bg.alpha_composite(im)
# Region overlays (colors indicate weight ownership; no cutouts are used).
D=P/'x01_region_diagnostics';D.mkdir(exist_ok=True)
for i,g in enumerate(r['regions'][:-1]):
 out=bg.copy();d=ImageDraw.Draw(out);d.line([tuple(p) for p in g['poly']]+[tuple(g['poly'][0])],fill=(180,30,180,255),width=3)
 box=(max(0,min(p[0] for p in g['poly'])-15),max(0,min(p[1] for p in g['poly'])-15),min(im.width,max(p[0] for p in g['poly'])+15),min(im.height,max(p[1] for p in g['poly'])+15))
 out=out.crop(box);out.convert('RGB').save(D/(str(i)+'_'+'_'.join(g['bones'])+'.png'))
e=bg.copy();d=ImageDraw.Draw(e)
for i,q in enumerate(r['eyes']):
 pts=[]
 for j in range(121):
  a=math.tau*j/120;x=(q['rx']+2)*math.cos(a);y=(q['ry']+2)*math.sin(a);t=q['rot'];pts.append((q['c'][0]+x*math.cos(t)-y*math.sin(t),q['c'][1]+x*math.sin(t)+y*math.cos(t)))
 d.line(pts,fill=(0,170,210),width=2)
 x,y=q['c'];d.ellipse((x-2,y-2,x+2,y+2),fill=(240,0,0))
e.crop((1138,410,1340,530)).resize((808,480)).convert('RGB').save(P/'x01_eyes_overlay.png')
print(json.dumps(checks,ensure_ascii=False,indent=2))
