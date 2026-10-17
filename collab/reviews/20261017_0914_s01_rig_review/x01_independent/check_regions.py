from pathlib import Path
import json,math,sys
from PIL import Image,ImageDraw,ImageChops
p=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/tmp/laidian-s01-rigs/x01_prone_phone.rig.json');r=json.loads(p.read_text());o=Path('/tmp/laidian-s01-rigs/audit_x01');im=Image.open('/workspace/animation-competition/assets/chars/x01_prone_phone.png').convert('RGBA');base=Image.new('RGBA',im.size,'white');base.alpha_composite(im);allov=base.copy();d=ImageDraw.Draw(allov);used=Image.new('L',im.size);report=[]
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
for i,reg in enumerate(r['regions']):
 poly=reg['poly'];N=len(poly);issues=[]
 for a in range(N):
  A,B=poly[a],poly[(a+1)%N]
  for b in range(a+1,N):
   if b==(a+1)%N or a==(b+1)%N:continue
   C,D=poly[b],poly[(b+1)%N]
   if cross(A,B,C)*cross(A,B,D)<0 and cross(C,D,A)*cross(C,D,B)<0:issues.append([a,b])
 mask=Image.new('L',im.size);ImageDraw.Draw(mask).polygon([tuple(x) for x in poly],fill=255)
 effective=ImageChops.subtract(mask,used);used=ImageChops.lighter(mask,used)
 alpha=ImageChops.multiply(im.getchannel('A'),effective);part=im.copy();part.putalpha(alpha);bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(part)
 bbox=alpha.getbbox();crop=bg.crop((max(0,bbox[0]-10),max(0,bbox[1]-10),min(im.width,bbox[2]+10),min(im.height,bbox[3]+10)));crop.thumbnail((1000,850));crop.convert('RGB').save(o/f'region_{i:02d}_effective.png')
 col=['red','blue','green','purple','orange','brown','magenta','black'][i];d.line([tuple(x) for x in poly]+[tuple(poly[0])],fill=col,width=3);d.text(tuple(poly[0]),str(i)+' '+','.join(reg['bones']),fill=col)
 report.append({'index':i,'bones':reg['bones'],'self_intersections':issues,'out_of_range':[x for x in poly if not(0<=x[0]<=1536 and 0<=x[1]<=1024)],'effective_bbox':bbox})
allov.convert('RGB').save(o/'independent_regions.png')
eye=base.copy();d=ImageDraw.Draw(eye)
for e in r['eyes']:
 x,y=e['c'];rx,ry=e['rx'],e['ry'];a=e['rot'];pts=[(x+rx*math.cos(t)*math.cos(a)-ry*math.sin(t)*math.sin(a),y+rx*math.cos(t)*math.sin(a)+ry*math.sin(t)*math.cos(a)) for t in [k/80*2*math.pi for k in range(81)]];d.line(pts,fill='red',width=2);d.ellipse((x-2,y-2,x+2,y+2),fill='blue')
eye.crop((1130,405,1345,530)).resize((860,500)).convert('RGB').save(o/'eyes_overlay.png')
(o/'regions_check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
