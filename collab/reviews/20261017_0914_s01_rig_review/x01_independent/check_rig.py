from pathlib import Path
import json, math, hashlib, sys
from PIL import Image, ImageDraw, ImageChops
out=Path('/tmp/laidian-s01-rigs/audit_x01')
p=Path(sys.argv[1]); rig=json.loads(p.read_text());src=Path('/workspace/animation-competition/assets/chars/x01_prone_phone.png');im=Image.open(src).convert('RGBA');W,H=im.size
errors=[];warnings=[]
if rig.get('size')!=[W,H]:errors.append('Image size mismatch')
bs=rig.get('bones',[]);names=[b['name'] for b in bs];by={b['name']:b for b in bs}
if len(names)!=len(set(names)):errors.append('Duplicate bone names')
def pointok(v):return isinstance(v,list) and len(v)==2 and all(isinstance(x,(int,float)) and math.isfinite(x) for x in v)
def inside(p):return 0<=p[0]<=W and 0<=p[1]<=H
lengths={};gaps={}
for b in bs:
 n=b['name'];par=b.get('parent')
 if par is not None and par not in by:errors.append('Missing parent '+n)
 for key in ['head','tail']:
  if not pointok(b.get(key)):errors.append('Bad point '+n+'.'+key)
  elif not inside(b[key]):errors.append('Outside image '+n+'.'+key)
 if pointok(b.get('head')) and pointok(b.get('tail')):lengths[n]=math.dist(b['head'],b['tail'])
 if par in by:gaps[n]=math.dist(b['head'],by[par]['tail'])
 seen=set();q=n
 while q in by:
  if q in seen:errors.append('Cycle at '+n);break
  seen.add(q);q=by[q].get('parent')
base=Image.new('RGBA',im.size,'white');base.alpha_composite(im)
boneim=base.copy();d=ImageDraw.Draw(boneim)
for idx,b in enumerate(bs):
 color=['#d92626','#167fbd','#118a41','#8e36a6'][idx%4];h,t=b['head'],b['tail'];d.line([tuple(h),tuple(t)],fill=color,width=4)
 for x,y in [h,t]:d.ellipse((x-4,y-4,x+4,y+4),outline=color,width=2)
 d.text((h[0]+4,h[1]-13),b['name'],fill=color)
pins=[]
for rawpin in rig.get('pins',[]):
 pin=rawpin.get('at') if isinstance(rawpin,dict) else rawpin
 if not pointok(pin):errors.append('Malformed pin');continue
 if not inside(pin):errors.append('Pin out of image');continue
 x,y=pin;d.ellipse((x-8,y-8,x+8,y+8),outline='orange',width=4);pins.append({'xy':pin,'alpha_at_point':im.getpixel((min(W-1,round(x)),min(H-1,round(y))))[3]})
boneim.convert('RGB').save(out/'independent_bones_pins.png')
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
layerinfo=[]
for i,l in enumerate(rig.get('layers',[])):
 n=l.get('name',str(i));poly=l.get('poly',[])
 if len(poly)<3 or not all(pointok(p) for p in poly):errors.append('Bad polygon '+n);continue
 if any(not inside(p) for p in poly):errors.append('Polygon outside image '+n)
 unknown=[b for b in l.get('bones',[]) if b not in by]
 if unknown:errors.append('Unknown layer bone '+n+str(unknown))
 intersections=[];N=len(poly)
 for a in range(N):
  A,B=poly[a],poly[(a+1)%N]
  for b in range(a+1,N):
   if b in [a,(a+1)%N] or a==(b+1)%N:continue
   C,D=poly[b],poly[(b+1)%N]
   if cross(A,B,C)*cross(A,B,D)<0 and cross(C,D,A)*cross(C,D,B)<0:intersections.append([a,b])
 if intersections:errors.append('Self-intersection '+n+str(intersections))
 mask=Image.new('L',im.size);ImageDraw.Draw(mask).polygon([tuple(p) for p in poly],fill=255)
 alpha=ImageChops.multiply(mask,im.getchannel('A'));part=im.copy();part.putalpha(alpha);bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(part)
 bbox=alpha.getbbox();area=abs(sum(poly[j][0]*poly[(j+1)%N][1]-poly[(j+1)%N][0]*poly[j][1] for j in range(N)))/2
 if bbox:
  bb=(max(0,bbox[0]-15),max(0,bbox[1]-15),min(W,bbox[2]+15),min(H,bbox[3]+15));crop=bg.crop(bb);crop.thumbnail((1000,900));crop.convert('RGB').save(out/f'layer_{i:02d}_{n}.png')
 layerinfo.append({'name':n,'bones':l.get('bones'),'z':l.get('z'),'bbox':bbox,'polygon_area':area,'self_intersections':intersections})
summary={'rig_path':str(p),'rig_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'image_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'size':[W,H],'errors':errors,'warnings':warnings,'bone_lengths':lengths,'child_head_to_parent_tail':gaps,'pins':pins,'layers':layerinfo,'scope':'Static structure and independent raster masks only; no engine deformation approval.'}
(out/'structure_check.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps(summary,ensure_ascii=False,indent=2))
