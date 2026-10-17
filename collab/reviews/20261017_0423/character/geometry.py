import math,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
out=Path('/tmp/laidian-audit-character');ev=out/'evidence'
C=np.array([3.05,1.5,1.18]);T=np.array([1.5,.42,.95]);f=(T-C)/np.linalg.norm(T-C);right=np.cross(f,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,f);focal=480/math.tan(math.radians(29))
def project(P):
 d=np.array(P)-C;z=np.dot(d,f)
 return np.array([480+np.dot(d,right)/z*focal,270-np.dot(d,up)/z*focal])
def ss(a,b,t):
 u=max(0,min(1,(t-a)/(b-a)));return u*u*(3-2*u)
def turtle(t):
 flip=ss(5.2,5.5,t);spin=ss(2.4,3,t)*(1-ss(4.4,4.8,t));x=1.95+.07*math.sin(t*3.1)+.04*math.sin(t*7.3)*(1-flip);z=.80+.05*math.sin(t*4.3)-.04*flip+.02*abs(math.sin(t*9))*flip
 ang=.22*math.sin(t*2.7)+spin*.7*math.sin(t*6.2)+math.pi*flip;tt=t*(1+flip);ph=tt*(1.6+1.2*flip)*math.pi*2;ang+=.02*math.sin(ph*2);n=.6-.3*spin
 angles=[-1.5*(1-n)+.15*n,2.7*(1-n)+.05*n,-1.9*(1-n),.05*math.sin(ph)]
 def rot(p,a):return np.array([math.cos(a)*p[0]-math.sin(a)*p[1],math.sin(a)*p[0]+math.cos(a)*p[1]])
 shell=rot([0,40],ang);o=rot([143,18.2],ang);a=ang+angles[0]
 for aa in angles[1:]:o=o+rot([41.6,0],a);a+=aa
 head=o+rot([20,0],a)
 return np.array([x,z]),dict(shell=shell,head=head),spin>.5 or flip>.5

def world(root,p):return [root[0]+p[0]/1000,.004,root[1]+p[1]/1000]
def affine(root,p):
 q0=project(world(root,[0,0]));qx=project(world(root,[100,0]));qy=project(world(root,[0,100]));return q0+(qx-q0)*p[0]/100+(qy-q0)*p[1]/100
records=[];font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
for fr in [0,64,108,129,143,144,156,168,215]:
 t=fr/24;root,pts,cross=turtle(t);row={'frame':fr,'time':t,'points':{}}
 im=Image.open(ev/'s20_backstage'/f'{fr+1:04d}.png').convert('RGB');d=ImageDraw.Draw(im)
 for name,p in pts.items():
  actual=affine(root,[-p[0],p[1]]);rod=project(world(root,p));true=project(world(root,[-p[0],p[1]]));row['points'][name]={'displayed_affine':actual.tolist(),'rod_endpoint':rod.tolist(),'correct_world_projected':true.tolist(),'rod_to_display_px':float(np.linalg.norm(rod-actual)),'affine_error_px':float(np.linalg.norm(true-actual))}
  if name=='head':
   for point,color,label in [(actual,'#00FFFF','Displayed head grip'),(rod,'#FF3D4D','Actual rod endpoint')]:
    x,y=point;d.ellipse((x-7,y-7,x+7,y+7),outline=color,width=3);tx=max(5,min(700,x+10));ty=max(5,min(505,y+12));d.text((tx,ty),label,font=font,fill=color,stroke_width=2,stroke_fill='black')
 d.text((10,10),f'S20 f{fr} {t:.3f}s: endpoint diagnosis on actual decoded frame',font=font,fill='white',stroke_width=2,stroke_fill='black')
 if fr in [0,143,156]:im.save(ev/f's20_endpoint_f{fr}.jpg',quality=96)
 records.append(row)
# grip at immediate cut
cards=[('before',dict(ox=245,oy=1363,sc=9.04),[[578,641],[590,466]]),('after',dict(ox=175,oy=1284,sc=9),[[585,538]])];grip={}
for name,card,pts in cards:
 base=np.array([1.13,1.1,0]);grip[name]=[]
 for px,py in pts:
  x=(card['ox']-px)/card['sc']/100;y=(card['oy']-py)/card['sc']/100;grip[name].append(project(base+right*x+up*y).tolist())
res={'turtle':records,'grandma_grip_cut':grip};(out/'geometry.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
