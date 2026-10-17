from pathlib import Path
import math,json,hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont
O=Path('/tmp/laidian-s18-pilot-audit/generated_k06_pose'); E=O/'evidence';E.mkdir(exist_ok=True)
R=Path('/tmp/laidian-s18-pilot-candidate')
M=np.array([[.6899011814540491,-.0014000205913094917],[.0014000205913094917,.6899011814540491]])
t=np.array([.7660657208545949,9.446938260528214]); inv=np.linalg.inv(M)
T={'shoulder':[270,483],'elbow':[308.9685,606.6991],'wrist':[366,458],'tip':[390,347]}
N={'v1':{'shoulder':[394,706],'elbow':[590,799],'wrist':[604,566],'tip':[640,418]},'v2':{'shoulder':[394,706],'elbow':[515,838],'wrist':[582,615],'tip':[628,458]}}
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
D={'coordinate_space':'635x1175 mother asset','measurement_note':'Manual visible elbow/wrist/tip estimates approx +/-5-10 native px; shoulder hidden in sleeve, inferred with greater uncertainty. Projected lengths are working estimates, not 3D anatomy.','registration_source':'character_audit v1 and v2 registration_measurements.json, separate stool A/B two-point similarities with withheld points; copied beside measurements.','M':M.tolist(),'t':t.tolist(),'target':T,'versions':{}}
panels=[]
for version,points in N.items():
 if version=='v2':
  M=np.array([[.6901290012289069,.0011738941704661544],[-.0011738941704661544,.6901290012289069]])
  t=np.array([-3.5655888335554486,7.236809988076061]);inv=np.linalg.inv(M)
 p=R/('generated_k06_'+version)/'x18_k06_candidate.png'; im=Image.open(p).convert('RGBA');a=np.asarray(im)[:,:,3];J={k:(M@v+t).tolist() for k,v in points.items()}
 d={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':im.size,'registration_M':M.tolist(),'registration_t':t.tolist(),'native_points':points,'registered_points':J,'target_errors':{},'projected_lengths':{},'alpha':{'zero':int((a==0).sum()),'opaque':int((a==255).sum()),'soft':int(((a>0)&(a<255)).sum()),'tiny1to4':int(((a>0)&(a<=4)).sum())}}
 for k,v in J.items():d['target_errors'][k]={'dx':v[0]-T[k][0],'dy':v[1]-T[k][1],'distance':math.dist(v,T[k])}
 for x,y in [('shoulder','elbow'),('elbow','wrist'),('wrist','tip')]:d['projected_lengths'][x+'_'+y]=math.dist(J[x],J[y])
 d['upperarm_angle_deg']=math.degrees(math.atan2(J['elbow'][1]-J['shoulder'][1],J['elbow'][0]-J['shoulder'][0]))
 gaps=[]
 for y in range(410,600):
  ids=np.flatnonzero(a[y,490:680]>=128)+490
  if len(ids)==0:continue
  runs=np.split(ids,np.flatnonzero(np.diff(ids)>1)+1);runs=[(int(r[0]),int(r[-1])) for r in runs if len(r)>3]
  for first,second in zip(runs,runs[1:]):
   if first[0]<=520 and 550<=second[0]<=650:gaps.append({'y':y,'face_edge_x':first[1],'hand_edge_x':second[0],'clear_pixels':second[0]-first[1]-1})
 d['horizontal_alpha_gap_min']=min(gaps,key=lambda z:z['clear_pixels']);d['gap_note']='Visible face-to-hand horizontal clear-pixel run; not exact Euclidean mouth gap.'
 comp=Image.new('RGBA',im.size,'#b0b0b0');comp.alpha_composite(im)
 ann=comp.convert('RGB');q=ImageDraw.Draw(ann)
 for k,(x,y) in points.items():q.ellipse((x-5,y-5,x+5,y+5),fill='#d50000');q.text((x+8,y-13),k+f' {x},{y}',font=font,fill='#9f0000',stroke_width=2,stroke_fill='white')
 ann.crop((360,370,715,940)).save(E/(version+'_measured_native.png'))
 coeff=tuple(inv.reshape(-1)[:0])
 coeff=(inv[0,0],inv[0,1],float((-inv@t)[0]),inv[1,0],inv[1,1],float((-inv@t)[1]))
 reg=comp.convert('RGB').transform((635,1175),Image.Transform.AFFINE,coeff,Image.Resampling.BICUBIC,fillcolor='#b0b0b0');q=ImageDraw.Draw(reg)
 for pts,col in [(T,'#0066dd'),(J,'#dd0000')]:
  chain=[tuple(pts[k]) for k in ['shoulder','elbow','wrist','tip']];q.line(chain,fill=col,width=3)
  for x,y in chain:q.ellipse((x-3,y-3,x+3,y+3),fill=col)
 for k in ['elbow','wrist','tip']:q.line((tuple(T[k]),tuple(J[k])),fill='#e18600',width=2)
 q.text((200,225),version+' blue=target red=observed',font=font,fill='black',stroke_width=2,stroke_fill='white')
 reg.crop((200,220,500,670)).save(E/(version+'_registered_pose_overlay.png'));panels.append(reg.crop((200,220,500,670)))
 for color,label in [('#fff','white'),('#808080','gray'),('#101010','dark')]:
  c=Image.new('RGBA',im.size,color);c.alpha_composite(im);c.crop((480,380,680,650)).convert('RGB').save(E/(version+'_mouth_hand_'+label+'.png'))
 D['versions'][version]=d
sheet=Image.new('RGB',(600,450),'white');sheet.paste(panels[0],(0,0));sheet.paste(panels[1],(300,0));sheet.save(E/'registered_pose_pair.png')
(O/'measurements.json').write_text(json.dumps(D,indent=2));print(json.dumps({v:{'errors':d['target_errors'],'lengths':d['projected_lengths'],'gap':d['horizontal_alpha_gap_min']} for v,d in D['versions'].items()},indent=2))
