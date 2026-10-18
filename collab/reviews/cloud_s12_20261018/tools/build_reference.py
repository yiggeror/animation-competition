from pathlib import Path
import json,hashlib,math,csv,subprocess
import numpy as np
from scipy.spatial import ConvexHull
from PIL import Image,ImageDraw,ImageFont
H=Path('collab/reviews/cloud_s12_20261018');G=json.loads((H/'geometry/three_key_pose_proposal.json').read_text());states=G['states'];SC=G['head_unit_scene_pixels'];a,b=np.deg2rad([12,15]);ca,sa,cb,sb=np.cos(a),np.sin(a),np.cos(b),np.sin(b)
fontpath='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
def F(n):return ImageFont.truetype(fontpath,n)
def proj(p):
 x,y,z=np.asarray(p).T;return np.stack([480+SC*(cb*x-sb*z),1012-SC*(ca*y+sa*(sb*x+cb*z))],axis=-1)
def pnt(s,k):return np.array(s['points_H'][k])
def uv(s,k):return np.array(s['points_scene'][k])
def surface(c,r,axes=None):
 v=[]
 if axes is None:axes=np.eye(3)
 for t in np.linspace(0,np.pi,15):
  for ph in np.linspace(0,2*np.pi,25):v.append(c+axes@(np.array([np.sin(t)*np.cos(ph),np.cos(t),np.sin(t)*np.sin(ph)])*r))
 return np.array(v)
def ell(draw,c,r,fill,outline=(70,78,92,255),axes=None):
 q=proj(surface(c,np.array(r),axes));poly=q[ConvexHull(q).vertices];draw.polygon([tuple(v) for v in poly],fill=fill);draw.line([tuple(v) for v in np.vstack([poly,poly[0]])],fill=outline,width=2)
def basis(axis):
 u=axis/np.linalg.norm(axis);v=np.cross(u,[0,0,1]);v/=np.linalg.norm(v);w=np.cross(v,u);return np.stack([v,u,w],axis=1)
def limb(draw,p,q,r,fill,r1=None):
 if r1 is None:r1=r
 axes=basis(q-p);cloud=[]
 for t in np.linspace(0,1,7):
  c=p+(q-p)*t;rad=r+(r1-r)*t
  for ph in np.linspace(0,2*np.pi,20):cloud.append(c+rad*(axes[:,0]*np.cos(ph)+axes[:,2]*np.sin(ph)))
 cloud.extend(surface(p,np.array([r,r,r])));cloud.extend(surface(q,np.array([r1,r1,r1])));z=proj(cloud);poly=z[ConvexHull(z).vertices];draw.polygon([tuple(v) for v in poly],fill=fill);draw.line([tuple(v) for v in np.vstack([poly,poly[0]])],fill='#596574',width=2)

def text(draw,xy,s,n=22,fill='#263446'):draw.text(xy,s,font=F(n),fill=fill,stroke_width=0)
colors={'R':(233,151,86,255),'L':(100,176,199,255)}
# Record actual source-pixel landmarks and their limitations.
marks={'crown':[534,31],'chin':[534,178],'shoulderR':[447,236],'elbowR':[420,357],'wristR':[411,445],'fingerR':[422,498],'shoulderL':[621,236],'elbowL':[649,357],'wristL':[656,445],'fingerL':[645,498],'hipR':[484,450],'kneeR':[483,579],'ankleR':[482,708],'hipL':[583,450],'kneeL':[583,579],'ankleL':[583,708]}
HH=147.;measures=[]
for name,p,q,confidence in [('upper_armR','shoulderR','elbowR','shoulder under cloth ±10px;elbow ±6px'),('forearmR','elbowR','wristR','visible contour/manual centres ±6px'),('handR','wristR','fingerR','relaxed full-hand extent ±5px'),('shoulder_width','shoulderR','shoulderL','hidden joint estimates ±10px'),('femurR','hipR','kneeR','trouser-hidden joint estimates ±12px;not exact anatomy'),('tibiaR','kneeR','ankleR','trouser-hidden knee ±12px')]:
 length=float(np.linalg.norm(np.array(marks[p])-marks[q]));measures.append({'measure':name,'from':p,'to':q,'projected_source_px':round(length,3),'H_ratio':round(length/HH,4),'uncertainty':confidence})
(H/'geometry/actual_identity_measurements.json').write_text(json.dumps({'source':'collab/refs/grandma_turnaround_current03_draft.png','source_native_size':[2048,768],'head_H_definition':'visible vertical crown31 to chin178=147px;not estimated real-world centimetres','landmarks_source_pixels':marks,'measurements':measures,'rig3D_choices_H':G['bone_lengths_H'],'note':'Projected manual measurements;hidden joints and depth estimated. Fixed3D bone proposal differs slightly within uncertainty;not orthographic anatomical ground truth.'},ensure_ascii=False,indent=2)+'\n')
with (H/'geometry/actual_identity_measurements.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(measures[0]),lineterminator='\n');w.writeheader();w.writerows(measures)
# Actual identity evidence, never reposed or recoloured.
board=Image.new('RGB',(1800,1120),'#eeeae1');d=ImageDraw.Draw(board);text(d,(20,10),'S12 实际身份量尺：03为工作基准；04只作版本对照',32)
tri=Image.open('collab/refs/grandma_turnaround_current03_draft.png').convert('RGB');front=tri.crop((350,0,705,768));board.paste(front,(30,90));d=ImageDraw.Draw(board)
for k,v in marks.items():
 if k.endswith('L'):continue
 u,vv=v[0]-350+30,v[1]+90;d.ellipse((u-4,vv-4,u+4,vv+4),fill='#d34735');text(d,(u+7,vv-10),k,16)
for r in measures:
 p=np.array(marks[r['from']])+[-320,90];q=np.array(marks[r['to']])+[-320,90];d.line([tuple(p),tuple(q)],fill='#d34735',width=2)
text(d,(435,105),'03 实际测量 / 投影值',27)
for i,r in enumerate(measures):text(d,(435,155+i*48),f"{r['measure']}: {r['projected_source_px']}px = {r['H_ratio']:.3f}H",22)
text(d,(435,500),'H=147px；肩/髋/膝在衣下，均为人工估计。',22)
text(d,(435,540),'固定3D提案：上臂.86H / 前臂.64H / 股.90H / 胫.89H。',22)
text(d,(435,580),'手全长约.37H；掌握点距腕.23H，不能把腕点当握点。',22)
old=Image.open('collab/refs/anim_12_grandma_box_crane.png').convert('RGB');crop=old.crop((500,370,1120,710)).resize((744,408));board.paste(crop,(1030,90));d=ImageDraw.Draw(board)
# Actual old near arm observed, with explicit uncertainty.
for q,label in [((552,430),'肩估计'),((647,627),'肘'),((908,625),'腕')]:
 x=(q[0]-500)*1.2+1030;y=(q[1]-370)*1.2+90;d.ellipse((x-5,y-5,x+5,y+5),fill='#d34735');text(d,(x+8,y-12),label,19)
text(d,(1030,525),'旧g12近前臂投影约261px，H约248px。',22)
text(d,(1030,565),'不据此锁骨长：姿势/透视与衣下关节皆有误差。',21)
text(d,(1030,605),'新参考按03量尺重建，不沿旧长前臂与合并裤形。',21)
small=tri.resize((1536,576));board.paste(small,(130,870));# Crop strip below canvas intentionally replaced with full bottom identity strip.
board=board.crop((0,0,1800,1120));d=ImageDraw.Draw(board);d.rectangle((0,850,1800,1120),fill='#e7e3d9');strip=tri.resize((1800,675)).crop((0,0,1800,245));board.paste(strip,(0,875));text(d,(20,825),'实际03头/衣身份条：低髻、细镜框、蓝白花衫、左腕玉镯；不采用04变浅肤色。',23)
board.save(H/'reference/00_actual_identity_and_bone_measurements.jpg',quality=96)
# Actual lower body evidence and corrected chain targets.
legboard=Image.new('RGB',(1500,670),'#eeeae1');dd=ImageDraw.Draw(legboard);text(dd,(15,10),'旧S12跪姿实图：膝/踝被衣褶混并，不能按外裤轮廓量骨',27);legboard.paste(old.crop((200,720,900,1000)).resize((1400,560)),(40,75));text(dd,(45,615),'纠正方案：两条髋—膝—踝—鞋链独立；膝、胫与鞋背有地面接触；不绕同一膝转整图。',23);legboard.save(H/'reference/01_actual_old_kneeling_risk.jpg',quality=95)

def prop_layer(s):
 im=Image.open(H/f'reference/code_prop_{s["id"]}_native_only.png').convert('RGBA');t=np.deg2rad(s['prop_plane_tilt_degrees']);K=.72;e1=np.array([K*cb,-K*sa*sb]);e2=np.array([-K*np.cos(t)*sb,-K*(np.sin(t)*ca+np.cos(t)*cb*sa)]);M=np.eye(3);M[:2,0]=e1;M[:2,1]=-e2;M[:2,2]=uv(s,'crane_root')-e1*600+e2*800;inv=np.linalg.inv(M);return im.transform((1920,1080),Image.Transform.AFFINE,tuple(inv[:2].ravel()),Image.Resampling.BICUBIC)
def draw_person(canvas,s):
 d=ImageDraw.Draw(canvas);hip=pnt(s,'hip');sh=pnt(s,'shoulder_mid');axis=pnt(s,'head_axis');torso=(hip+sh)/2
 # Real 3D volume proposal, not rendered character art.
 for role in ['L','R']:
  z=.34 if role=='L' else -.34;ank=pnt(s,'ankle'+role);knee=pnt(s,'knee'+role)
  mid=proj((knee+ank)/2-[0,.12,0]);d.ellipse((mid[0]-102,mid[1]-7,mid[0]+102,mid[1]+7),fill=(50,60,73,65));ground=proj(knee-[0,.12,0]);d.ellipse((ground[0]-47,ground[1]-7,ground[0]+47,ground[1]+7),fill=(50,60,73,90))
  gf=proj(ank+[-.16,-.12,0]);d.ellipse((gf[0]-55,gf[1]-7,gf[0]+55,gf[1]+7),fill=(50,60,73,90))
  limb(d,pnt(s,'hip'+role),knee,.21,(139,145,169,255) if role=='R' else (181,187,204,255),r1=.12);limb(d,knee,ank,.12,(131,138,162,255) if role=='R' else (174,181,202,255));ell(d,ank+[-.16,-.055,0],[.30,.065,.14],(100,110,128,255));d.line([tuple(proj(ank+[-.37,.008,0])),tuple(proj(ank+[-.03,.008,0]))],fill='#d8d9d5',width=4)
 role='L';limb(d,pnt(s,'shoulderL'),pnt(s,'elbowL'),.145,colors[role],r1=.105);limb(d,pnt(s,'elbowL'),pnt(s,'wristL'),.09,colors[role],r1=.065)
 ell(d,hip+[-.05,-.04,0],[.40,.27,.48],(153,163,184,255));ell(d,torso,[.36,.77,.61],(175,193,205,255),axes=basis(sh-hip));ell(d,pnt(s,'neck_base')-[0,.07,0],[.16,.21,.19],(209,199,178,255));ell(d,pnt(s,'head_center'),[.39,.50,.35],(222,216,198,255),axes=basis(axis));ell(d,pnt(s,'head_center')+[-.37,.08,0],[.18,.19,.21],(181,184,182,255))
 # Facing plane and centreline, deliberately not a drawn face.
 nose=pnt(s,'head_center')+np.array([axis[1],-axis[0],0])*.43;q=proj(nose);c=uv(s,'head_center');d.line([tuple(c),tuple(q)],fill='#5b626c',width=3);d.ellipse((q[0]-5,q[1]-5,q[0]+5,q[1]+5),outline='#5b626c',width=2)
 role='R';limb(d,pnt(s,'shoulderR'),pnt(s,'elbowR'),.15,colors[role],r1=.11);limb(d,pnt(s,'elbowR'),pnt(s,'wristR'),.095,colors[role],r1=.065)
 for role in ['L','R']:
  for joint in ['shoulder','elbow','wrist','hip','knee','ankle']:
   p=uv(s,joint+role);d.ellipse((p[0]-4,p[1]-4,p[0]+4,p[1]+4),fill='#334152')
 return canvas

def hand(d,s,role):
 w=pnt(s,'wrist'+role);g=pnt(s,'grip'+role);u=(g-w)/np.linalg.norm(g-w);n=np.array([0,0,-1.]);n-=u*np.dot(n,u);n/=np.linalg.norm(n);v=np.cross(n,u);v/=np.linalg.norm(v);axes=np.stack([u,v,n],axis=1);ell(d,(w+g)/2,[.17,.12,.07],colors[role],axes=axes)
 q=uv(s,'grip'+role)
 if role=='L':
  p=uv(s,'wristL');d.ellipse((p[0]-12,p[1]-8,p[0]+12,p[1]+8),outline='#328460',width=6)
 if s['id']!='A':
  delta=7/(2*SC)+.018
  chains=[[w+u*.17+v*.09,g+u*.10+v*.09+n*.025,g+u*.09-v*.03+n*.035,g-v*delta],
          [w+u*.09-v*.09,g-u*.02-v*.10+n*.05,g+v*delta]]
  for chain in chains:
   for aa,bb in zip(chain[:-1],chain[1:]):limb(d,aa,bb,.022,colors[role],r1=.018)
  for sign in [-1,1]:ell(d,g+v*sign*delta,[.018,.018,.018],colors[role])
 else:
  for off in [-.07,0,.07]:limb(d,g+v*off,g+u*.15+v*off,.022,colors[role],r1=.017)
 d.ellipse((q[0]-3,q[1]-3,q[0]+3,q[1]+3),fill='#b72550')

for s in states:
 canvas=Image.new('RGBA',(1920,1080),(239,237,230,255));d=ImageDraw.Draw(canvas)
 d.polygon([(0,920),(1920,760),(1920,1080),(0,1080)],fill='#dadbd5');d.polygon([(1020,760),(1840,760),(1825,450),(1035,450)],fill='#d1c9b5',outline='#766f60');d.polygon([(1000,800),(1860,800),(1838,764),(1022,764)],fill='#8794a0',outline='#64717a')
 text(d,(24,15),f"S12 {s['id']} / F{s['frame']:03d}   体块与接触参考 · 非人物画稿 / 非实际场景片",30)
 text(d,(24,65),'近R无镯→body下签；远L玉镯→neck3上签；三关键同骨长 / 不整图绕膝。',24)
 canvas=draw_person(canvas,s);canvas=Image.alpha_composite(canvas,prop_layer(s));d=ImageDraw.Draw(canvas)
 for role,pkey in [('R','P_body'),('L','P_neck')]:
  g=pnt(s,'grip'+role) if s['id']!='A' else pnt(s,'free_grip'+role);p=pnt(s,pkey);gu,pu=proj(g),proj(p);d.line([tuple(gu),tuple(pu)],fill='#443624',width=7);d.line([tuple(gu),tuple(pu)],fill='#b88d4e',width=3);d.ellipse((pu[0]-7,pu[1]-7,pu[0]+7,pu[1]+7),outline='#bb2865',width=3)
  if s['id']=='A':
   rr=uv(s,'rim_contact'+role);d.ellipse((rr[0]-6,rr[1]-6,rr[0]+6,rr[1]+6),outline='#944b95',width=2)
 for role in ['L','R']:hand(d,s,role)
 # Exact inherited screen-space front mask: only this rectangle is painted in front.
 d.rectangle((1000,800,1860,1040),fill='#b2a68f',outline='#706856',width=3);d.rectangle((1000,800,1860,812),fill='#847560')
 for role in ['R','L']:
  for joint,label in [('elbow','肘'),('grip','掌心未握' if s['id']=='A' else '掌握')]:
   q=uv(s,joint+role);text(d,tuple(q+[8,5 if role=='R' else -28]),f'{role}{label}',19)
  for joint,label in [('hip','髋'),('knee','膝'),('ankle','踝')]:
   q=uv(s,joint+role);text(d,tuple(q+[6,-26 if role=='L' else 6]),role+label,18)
 text(d,(1160,846),'箱前板遮挡区：x1000–1860 / y800–1040',23)
 text(d,(1160,884),'初态收颈/收腿斜靠布；后靠关节展开与整片转立。',22)
 text(d,(1160,922),'不使用整鹤“压薄”参数；长签在掌下，握点不可拿腕点代。',22)
 text(d,(24,112),'膝/胫/鞋背接地影钉各自接触点；直身是抬躯干，膝与胫不离地。',22)
 if s['id']=='A':text(d,(24,156),'首态双手未握；长签由箱左窄沿支托（紫圈），先左后右分步握。',22)
 canvas.convert('RGB').save(H/f'reference/S12_{s["id"]}_F{s["frame"]:03d}_volume_contact.jpg',quality=97)
# Contact close-up from actual construction, with explicit non-art label.
c=Image.new('RGB',(1800,720),'#eeeae1');d=ImageDraw.Draw(c);text(d,(20,10),'掌握点与同一直杆：构造接触示意，不是最终指形；母态仍须实审拇指/食指包络',27)
for i,(s,role) in enumerate([(states[1],'R'),(states[1],'L'),(states[2],'R'),(states[2],'L')]):
 x=i*450;g=uv(s,'grip'+role);src=Image.open(H/f'reference/S12_{s["id"]}_F{s["frame"]:03d}_volume_contact.jpg');box=(int(g[0]-90),int(g[1]-90),int(g[0]+90),int(g[1]+90));cut=src.crop(box).resize((450,450),Image.Resampling.LANCZOS);c.paste(cut,(x,80));text(d,(x+12,552),f'{s["id"]} / {role} / {"body" if role=="R" else "neck3"}',23);text(d,(x+12,595),'品红点=掌握；双色小体=对向指腹',18);text(d,(x+12,630),'短杆遮挡前后段必须保持共线',18)
c.save(H/'reference/05_palm_grip_contact_construction.jpg',quality=96)
# 3D side/top projections disclose hidden arms and complete leg chains.
c=Image.new('RGB',(1800,1110),'#eeeae1');d=ImageDraw.Draw(c);text(d,(20,10),'侧/顶视结构复核：固定3D骨长；主画面短缩来自投影；不是最终角色造型',28)
for i,s in enumerate(states):
 for j,axes in enumerate([(0,1),(0,2)]):
  ox=j*900+100;oy=i*340+(340 if j==0 else 245)
  def f(p):
   z=np.array(p);return (ox+z[axes[0]]*155,oy-z[axes[1]]*115)
  for role in ['L','R']:
   pts=s['points_H'];fill='#4d9bab' if role=='L' else '#bd7844'
   for u,v in [('hip','knee'),('knee','ankle'),('shoulder','elbow'),('elbow','wrist'),('wrist','grip')]:d.line([f(pts[u+role]),f(pts[v+role])],fill=fill,width=6)
   for n in ['hip','knee','ankle','shoulder','elbow','wrist','grip']:
    q=f(pts[n+role]);d.ellipse((q[0]-4,q[1]-4,q[0]+4,q[1]+4),fill=fill)
  d.line([f(s['points_H']['hip']),f(s['points_H']['shoulder_mid'])],fill='#606c78',width=11);text(d,(j*900+20,i*340+80),s['id']+(' 侧视 X/Y' if j==0 else ' 顶视 X/Z（去掉地面遮挡）'),22)
c.save(H/'reference/06_side_top_hidden_structure.jpg',quality=95)
# Overview of the three actual output diagrams.
c=Image.new('RGB',(1920,3*390),'#eeeae1')
for i,s in enumerate(states):c.paste(Image.open(H/f'reference/S12_{s["id"]}_F{s["frame"]:03d}_volume_contact.jpg').resize((1920,1080)).resize((640,360)),(i*640,0))
c=c.crop((0,0,1920,360));c.save(H/'reference/04_three_key_overview.jpg',quality=96)
print('built actual-source measurement board + oldleg evidence +3volume keys +contacts+side/top')

# Ground contact enlargements: preserve visible feet and separate two chains.
c=Image.new('RGB',(2025,500),'#eeeae1');d=ImageDraw.Draw(c);text(d,(15,8),'膝/胫/鞋背接地构造（非画稿）；每条腿独立，鞋底朝上/鞋背压地；影钉Y=0',27)
for i,s in enumerate(states):
 im=Image.open(H/f'reference/S12_{s["id"]}_F{s["frame"]:03d}_volume_contact.jpg').crop((300,790,750,1080)).resize((675,435));c.paste(im,(i*675,60));text(d,(i*675+10,60),s['id'],25)
c.save(H/'reference/07_ground_contact_closeups.jpg',quality=97)
