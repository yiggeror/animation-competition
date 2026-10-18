from pathlib import Path
import json,numpy as np
from scipy.spatial import ConvexHull
from PIL import Image,ImageDraw,ImageFont
H=Path('collab/reviews/cloud_s12_20261018');g=json.loads((H/'geometry/three_key_pose_proposal.json').read_text());qpath=H/'qa/geometry_and_exposure_validation.json';q=json.loads(qpath.read_text());scale=215.;alpha,beta=np.deg2rad([12,15]);ca,sa,cb,sb=np.cos(alpha),np.sin(alpha),np.cos(beta),np.sin(beta)
def proj(p):
 x,y,z=np.asarray(p).T;return np.stack([480+scale*(cb*x-sb*z),1012-scale*(ca*y+sa*(sb*x+cb*z))],axis=-1)
for s,row in zip(g['states'],q['states']):
 p={k:np.array(v) for k,v in s['points_H'].items()};assert p['gripR'][2]<-.35 and p['gripL'][2]>.15
 support=np.array([[p['kneeR'][0],p['kneeR'][2]],[p['kneeL'][0],p['kneeL'][2]],[p['ankleR'][0]-.16,p['ankleR'][2]],[p['ankleL'][0]-.16,p['ankleL'][2]]]);hull=ConvexHull(support);com=np.array(row['mass_proxy_H'])[[0,2]];marg=float(-np.max(hull.equations[:,:2]@com+hull.equations[:,2]));assert marg>0
 row['support_polygon_from_knee_and_shoe_centres_XZ_H']=support.tolist();row['mass_proxy_inside_actual_contact_centre_hull']=True;row['mass_proxy_min_hull_margin_H']=marg
 row['farL_grasp_depth_order_preserved_H']=float(p['gripL'][2]-p['gripR'][2])
 cloud=[]
 for role in ['R','L']:
  c=p['ankle'+role]+[-.16,-.055,0]
  for t in np.linspace(0,np.pi,21):
   for ph in np.linspace(0,2*np.pi,41):cloud.append(c+np.array([.30*np.sin(t)*np.cos(ph),.065*np.cos(t),.14*np.sin(t)*np.sin(ph)]))
 uv=proj(cloud);t=191/24;u=np.clip((t-2)/6,0,1);ss=u*u*(3-2*u);fit=1+.04*ss;cx=960+20*ss;cy=540-10*ss;out=(uv-[cx,cy])*fit+[960,540];footmargin=float(1080-out[:,1].max());assert footmargin>10
 row['construction_shoe_bottom_margin_after_original_camera_at191_px']=footmargin
 if s['id']=='A':
  rrs=[];cols=[]
  for role,pk in [('R','P_body'),('L','P_neck')]:
   a,b,c=p['free_grip'+role],p[pk],p['rim_contact'+role];rrs.append(abs(np.linalg.norm(b-a)-s['rod_lengths_H'][role]));cols.append(float(np.linalg.norm(np.cross(b-a,c-a))/np.linalg.norm(b-a)))
  assert max(rrs)<1e-10 and max(cols)<1e-10
  row['unheld_rods_rest_on_proposed_rim_contacts']=True;row['free_rod_length_error_H']=rrs;row['rim_collinearity_error_H']=cols
q['original_camera_interface']={'source':'js/paint/shots/s12.js','function':'x=960+20*sstep(2,8,t);y=540-10*sstep(2,8,t);fit=1+.04*sstep(2,8,t)','reference_diagrams_are_pre_camera_scene_coordinates':True,'feet_margin_is_construction_only_native_art_still_requires_actual_check':True}
qpath.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
E=json.loads((H/'geometry/exposure_plan.json').read_text());c=Image.new('RGB',(1920,530),'#eeeae1');d=ImageDraw.Draw(c);font='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';F=lambda n:ImageFont.truetype(font,n)
d.text((20,12),'S12 · 192帧 / 8秒 拟排曝光（仅3关键已构造，未画28张）',font=F(31),fill='#263446');left=55;w=1810
for r in E['rows']:
 x0=left+r['start']/192*w;x1=left+(r['start']+r['hold'])/192*w;fill='#74a9b2' if r['start']<48 else '#b8b399' if r['start']<70 else '#d69d70' if r['start']<132 else '#b6bac4';d.rectangle((x0,150,x1-1,270),fill=fill,outline='#f8f6f1');d.text((x0+3,156),str(r['start']),font=F(17),fill='#25333d');d.text((x0+3,216),str(r['hold'])+'f',font=F(16),fill='#25333d')
for f,lab in [(0,'A 首态/未握'),(64,'B 双握/预紧'),(114,'C 举鹤/透光')]:
 x=left+f/192*w;d.line((x,100,x,290),fill='#a83e55',width=3);d.text((max(10,x-20),72),f'F{f:03d} {lab}',font=F(22),fill='#9c3450')
for f in [0,24,48,72,96,120,144,168,192]:
 x=left+f/192*w;d.text((x-10,290),str(f),font=F(20),fill='#263446')
d.text((35,365),'0–64 先左上签、再右下签；64–114 整髋/胸/肩/头回直并举鹤；114后轻晃再落定。',font=F(25),fill='#263446')
d.text((35,415),'110≈4.583秒、120=5秒作为原声提示参考；不改音轨。慢动6f段若成图跳变，另拆2–3f。',font=F(24),fill='#263446')
d.text((35,465),'所有暂停都停同一握点/杆长；不让代码道具独自插值而撕开画稿手掌。',font=F(24),fill='#263446');c.save(H/'reference/09_exposure_timeline_PROPOSAL.jpg',quality=96)
print('PASS supported free rods;contact-centre hull COMproxy;left/right depth;original-camerafoot margins',[(r['state'],round(r['construction_shoe_bottom_margin_after_original_camera_at191_px'],2)) for r in q['states']])
