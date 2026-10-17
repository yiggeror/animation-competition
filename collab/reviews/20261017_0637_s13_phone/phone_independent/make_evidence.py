import math,json,csv
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
OUT=Path('/tmp/laidian-audit-phone-final24')
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
def smooth(a,b,t):
 u=max(0,min(1,(t-a)/(b-a)));return u*u*(3-2*u)
def press(t,ps,dn=.06,hold=.06,up=.12):
 v=0
 for p in ps:
  u=t-p
  if -dn<u<hold+up:v=max(v,(u+dn)/dn if u<0 else 1 if u<hold else 1-(u-hold)/up)
 return v
mash=[];p=1.15
while p<3.0:
 mash.append(p);p+=.14+.03*math.sin(p*13)
def state(shot,t):
 if shot=='s02':
  ps=[.45,1.35,2.2,3.05];u=smooth(.2,4,t)
  tilt=sum(.008*math.exp(-((t-p-.2)**2)/.02) for p in ps)
  return dict(t=t,press=press(t,ps),cx=836+349*u,cy=452-220*u,z=1.07+.83*u,dx=3*math.sin(1.3*t),dy=2.5*math.sin(1.7*t),rot=tilt+.003*math.sin(.9*t),screen=1)
 u=smooth(.95,1.75,t);shake=smooth(1.1,1.3,t)*(t<3.05)
 return dict(t=t,press=press(t,mash,.025,.035,.04) if t<3.05 else press(t,[3.4,3.72]),cx=1185-349*u,cy=232+220*u,z=1.9-.83*u,dx=4*shake*math.sin(31*t),dy=3*shake*math.sin(27*t),rot=.006*shake*math.sin(17*t),screen=1 if t<3.05 else .35 if t<3.13 else 0)
def coeff(s,box):
 x,y=box[:2];k=960/1672*s['z'];c=math.cos(s['rot']);n=math.sin(s['rot'])
 a=k*c;b=-k*n;d=k*n;e=k*c
 tx=480+k*(836+s['dx']-s['cx'])-a*836-b*470
 ty=270+k*(470+s['dy']-s['cy'])-d*836-e*470
 return (a,b,tx+a*x+b*y,d,e,ty+d*x+e*y)
def normalized(im,s,box):
 return im.transform((box[2]-box[0],box[3]-box[1]),Image.Transform.AFFINE,coeff(s,box),resample=Image.Resampling.BICUBIC,fillcolor=(30,30,30))
allstates={}
for shot in ['s02','s05']:
 states=[dict(frame=f,**state(shot,f/24)) for f in range(96)];allstates[shot]=states
 with open(OUT/f'{shot}_states.csv','w') as f:
  w=csv.DictWriter(f,fieldnames=states[0].keys());w.writeheader();w.writerows(states)
 for page in range(4):
  right=Image.new('RGB',(6*290,4*312),(25,25,25));rd=ImageDraw.Draw(right)
  full=Image.new('RGB',(6*320,4*210),(25,25,25));fd=ImageDraw.Draw(full)
  for i in range(24):
   f=page*24+i;s=states[f];im=Image.open(OUT/f'{shot}_frames/{f:05d}.png').convert('RGB');x=(i%6)*290;y=(i//6)*312
   label=f"F{f:02d} {f/24:.3f}s {'DOWN' if s['press']>=.5 else 'UP'}"
   right.paste(normalized(im,s,(1160,300,1450,580)),(x,y+30));rd.text((x+4,y+6),label,font=FONT,fill='white')
   x=(i%6)*320;y=(i//6)*210;full.paste(im.resize((320,180)),(x,y+30));fd.text((x+4,y+6),label,font=FONT,fill='white')
  right.save(OUT/f'{shot}_right_all_{page+1}.png');full.save(OUT/f'{shot}_full_all_{page+1}.png')
 # Unnormalized actual pixel crops, fixed raw area with per-frame bounding from canonical focus.
 targets=[29,33,69,85,93]
 board=Image.new('RGB',(5*360,390),(25,25,25));dr=ImageDraw.Draw(board)
 for i,f in enumerate(targets):
  s=states[f];im=Image.open(OUT/f'{shot}_frames/{f:05d}.png').convert('RGB')
  c=coeff(s,(1160,300,1450,580));pts=[(c[0]*x+c[1]*y+c[2],c[3]*x+c[4]*y+c[5]) for x,y in [(0,0),(290,0),(0,280),(290,280)]]
  box=(max(0,int(min(p[0] for p in pts))-8),max(0,int(min(p[1] for p in pts))-8),min(960,math.ceil(max(p[0] for p in pts))+8),min(540,math.ceil(max(p[1] for p in pts))+8))
  crop=im.crop(box);crop.save(OUT/f'{shot}_F{f:02d}_root_raw.png')
  # nearest enlargement helps reveal seam pixels, never modifies source.
  crop.thumbnail((340,330));board.paste(crop,(i*360+10,50));dr.text((i*360+10,8),f'{shot} F{f} {f/24:.3f}s',font=FONT,fill='white');dr.text((i*360+10,28),f'raw crop {box}',font=FONT,fill='white')
 board.save(OUT/f'{shot}_old_gap_frames.png')
# Left thumb close crops in available framing, 24 sequential S05 frames across main mash.
left=Image.new('RGB',(6*220,4*260),(25,25,25));ld=ImageDraw.Draw(left)
for i,f in enumerate(range(42,66)):
 s=allstates['s05'][f];im=Image.open(OUT/f's05_frames/{f:05d}.png');x=i%6*220;y=i//6*260
 left.paste(normalized(im,s,(280,370,500,600)),(x,y+30));ld.text((x+5,y+5),f'F{f} {f/24:.3f}s',font=FONT,fill='white')
left.save(OUT/'s05_left_F42_F65.png')
summary={}
for shot,states in allstates.items():
 runs=[];begin=None
 for f,s in enumerate(states+[dict(press=0)]):
  if s['press']>=.5 and begin is None:begin=f
  elif s['press']<.5 and begin is not None:runs.append([begin,f-1]);begin=None
 summary[shot]={'down_runs':runs,'release_frames_between':[runs[i+1][0]-runs[i][1]-1 for i in range(len(runs)-1)]}
summary['mash_times']=mash
(OUT/'timing_annotation.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
