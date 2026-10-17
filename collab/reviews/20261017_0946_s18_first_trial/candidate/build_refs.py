#!/usr/bin/env python3
"""S18 three-state drawing references only. No production character rendering."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,math,hashlib,shutil
P=Path(__file__).resolve().parent
SRC=Path('/workspace/animation-competition/assets/chars/x18_laugh.png')
SHA='499a81ef65f78e44597045af0a91a3236de660064eecf0ca2ecd4cdfa35bb633'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SHA
im=Image.open(SRC);W,H=im.size;assert (W,H)==(635,1175)
shutil.copyfile(SRC,P/'master_identity.png')
J0={'sh_n':[270,483],'el_n':[386,541],'wr_n':[366,383],'palm_n':[373,333],'mcp_n':[380,307],'tip_n':[390,272],
 'sh_f':[321,488],'el_f':[354,650],'wr_f':[454,723],'palm_f':[482,737],'tip_f':[522,761],
 'neck':[273,418],'head_center':[239,242],'nose':[390,262],'mouth_proxy':[381,313],'chin_visible':[339,377],
 'waist':[263,643],'pelvis':[223,801],'knee_n':[465,813],'ankle_n':[431,1082],'toe_n':[555,1132],
 'knee_f':[515,799],'ankle_f':[498,1060],'toe_f':[600,1110]}
L1=math.dist(J0['sh_n'],J0['el_n']);L2=math.dist(J0['el_n'],J0['wr_n']);Lh=math.dist(J0['wr_n'],J0['tip_n'])
anchors={'stool_front_left_lower_corner':[23,898],'stool_front_right_foot_outer_bottom':[309,1141],
 'stool_front_left_foot_outer_bottom':[23,1141],'stool_front_left_upper_corner':[23,856],
 'near_shoe_sole_bottom':[480,1152],'far_shoe_sole_bottom':[594,1127]}
# Only actually visible stool outline/feet are drawn, with occluded seat portion dashed.
stool_paths=[[[23,856],[96,831]],[[23,856],[229,856],[258,899],[23,899],[23,856]],
 [[51,900],[98,900],[63,1141],[23,1141],[51,900]],[[261,902],[300,929],[313,1141],[278,1141],[261,902]],
 [[99,901],[134,901],[113,1105],[81,1105],[99,901]],[[300,929],[315,940],[324,1104],[313,1104]],
 [[79,985],[266,985],[267,1016],[74,1016],[79,985]],[[130,962],[260,962],[261,981],[127,981]]]
def rotvec(v,a):
 a=math.radians(a);return [v[0]*math.cos(a)-v[1]*math.sin(a),v[0]*math.sin(a)+v[1]*math.cos(a)]
def moved(p,pivot,angle):
 q=rotvec([p[0]-pivot[0],p[1]-pivot[1]],angle);return [pivot[0]+q[0],pivot[1]+q[1]]
def ik(s,w):
 dx=w[0]-s[0];dy=w[1]-s[1];d=math.hypot(dx,dy)
 assert abs(L1-L2)<d<L1+L2,('unreachable',s,w,d,L1+L2)
 a=math.atan2(dy,dx);b=math.acos((L1*L1+d*d-L2*L2)/(2*L1*d))
 return [s[0]+L1*math.cos(a+b),s[1]+L1*math.sin(a+b)]
rest_angle=math.degrees(math.atan2(J0['tip_n'][1]-J0['wr_n'][1],J0['tip_n'][0]-J0['wr_n'][0]))
keys=[]
for name,t,lift,headrot,w,handangle,note in [
 ('k04',.50,0,0,[414,699],34,'喷笑起点：嘴张开，眼睛弯；近手仍搭膝。头肩位置先固定。'),
 ('k06',.80,0,0,[366,458],rest_angle,'近手向嘴抬起途中、在下巴前方；指尖低于估计嘴34px，未接触嘴。'),
 ('k07',.92,0,0,J0['wr_n'],rest_angle,'实际母版捂嘴终态：优先直接复用母版，不要求再次生成。')]:
 j={k:v[:] for k,v in J0.items()};j['sh_n'][1]-=lift;j['wr_n']=w[:]
 j['el_n']=ik(j['sh_n'],w) if name!='k07' else J0['el_n'][:]
 da=handangle-rest_angle
 for k in ['palm_n','mcp_n','tip_n']:
  q=rotvec([J0[k][0]-J0['wr_n'][0],J0[k][1]-J0['wr_n'][1]],da);j[k]=[w[0]+q[0],w[1]+q[1]]
 for k in ['head_center','nose','mouth_proxy','chin_visible']:j[k]=moved(J0[k],J0['neck'],headrot)
 j={k:[round(v[0],4),round(v[1],4)] for k,v in j.items()}
 actual=[math.dist(j['sh_n'],j['el_n']),math.dist(j['el_n'],j['wr_n']),math.dist(j['wr_n'],j['tip_n'])]
 elbow_angle=math.degrees(math.acos((L1*L1+L2*L2-math.dist(j['sh_n'],j['wr_n'])**2)/(2*L1*L2)))
 keys.append({'id':name,'requested_time_s':t,'reference_only_not_timeline':True,'joints':j,'near_shoulder_lift_px':lift,'head_rotation_deg':headrot,
 'near_hand_axis_deg':handangle,'near_palm_orientation':'palmar surface toward face; fingers together' if name!='k04' else 'palm resting on lap; fingers forward/down-right',
 'near_elbow_internal_angle_deg':elbow_angle,'segment_lengths_px':actual,'max_length_error_px':max(abs(x-y) for x,y in zip(actual,[L1,L2,Lh])),
 'expression_note':note,'reuse_master':name=='k07','fixed_anchor_names':list(anchors)})
notes=['Coordinates are native 635x1175 source pixels, x right/y down. This is a generation-reference candidate, not an animation result.',
 'near=anatomical right arm, far=anatomical left arm. Near shoulder is under sleeve and is a 2D proxy (~10px uncertainty); elbow/wrist estimated to ~5-8px.',
 'mouth_proxy is hidden by the source hand, thus it is an estimated targeting landmark (~10-15px uncertainty), not a measured visible mouth. chin_visible is a visible lower-face landmark.',
 'Projected arm lengths are preserved across the three references; this is not a 3D anatomical reconstruction and cannot guarantee the generator preserves them.',
 'All stool anchors, seated pelvis/waist/legs/shoes, and entire far arm/hand coordinates are identical across references. No head/collar point is used as a global registration anchor.',
 'For this minimal probe, head and both shoulder points are fixed; only the full near arm/hand, affected sleeve cuff and expression vary. k07 is the source actual covered-mouth pose. Source identity is provided separately.',
 'The body/leg proxy joints are for keeping seated framing; they are hidden or stylized and are not intended to drive new lower-body actions.',
 'Blank-background target diagrams contain no faded source character and no old raised arm. Geometric head guide is not a new approved character design.',
 'k04/k06/k07 are three consistency probes; no claim of 3s continuous action, final timing, per-frame identity stability, or natural performance.']
spec={'shot':'S18','scope':'three-state generation-reference probe; k06 first, k07 source reuse, k04 next','master':'assets/chars/x18_laugh.png','source_sha256':SHA,'size':[W,H],
 'joints_master':J0,'near_lengths_px':{'upperarm':L1,'forearm':L2,'wrist_to_fingertip':Lh},'fixed_anchors':anchors,'stool_visible_paths':stool_paths,'keys':keys,'notes':notes}
(P/'S18_three_state_candidate.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
F='/workspace/animation-competition/assets/fonts/NotoSansSC-VF.ttf';font=ImageFont.truetype(F,17);small=ImageFont.truetype(F,13);tiny=ImageFont.truetype(F,11)
def line(d,pts,c,w=4):d.line([tuple(p) for p in pts],fill=c,width=w)
def point(d,p,c,r=4):d.ellipse((p[0]-r,p[1]-r,p[0]+r,p[1]+r),fill=c,outline='white',width=1)
def label(d,p,s,c='black',off=(6,3)):d.text((p[0]+off[0],p[1]+off[1]),s,font=tiny,fill=c,stroke_width=2,stroke_fill='white')
def draw(k):
 j=k['joints'];img=Image.new('RGB',(W,H),'#fcfcfa');d=ImageDraw.Draw(img)
 for p in stool_paths:line(d,p,'#a7815b',3)
 for name,p in anchors.items():
  if name.startswith('stool'):
   d.rectangle((p[0]-4,p[1]-4,p[0]+4,p[1]+4),fill='#b17d26',outline='black')
 # Fixed legs and far arm are secondary and remain visible.
 for chain in [('pelvis','knee_f','ankle_f','toe_f'),('pelvis','knee_n','ankle_n','toe_n'),('pelvis','waist','neck')]:line(d,[j[n] for n in chain],'#8d9499',4)
 for n in ['pelvis','waist','knee_n','ankle_n','knee_f','ankle_f']:point(d,j[n],'#8d9499',3)
 line(d,[j[n] for n in ['neck','sh_f','el_f','wr_f','palm_f','tip_f']],'#547cac',4)
 for n in ['sh_f','el_f','wr_f','tip_f']:point(d,j[n],'#547cac',4)
 line(d,[j['neck'],j['sh_n']],'#cf3d48',3)
 line(d,[j[n] for n in ['sh_n','el_n','wr_n']],'#cf3d48',7)
 line(d,[j[n] for n in ['wr_n','palm_n','mcp_n','tip_n']],'#b62639',5)
 px,py=j['palm_n']; normal=[0,1] if k['id']=='k04' else [-1,0]; end=[px+normal[0]*28,py+normal[1]*28];line(d,[[px,py],end],'#d78a24',3);point(d,end,'#d78a24',3);label(d,end,'掌面朝膝' if k['id']=='k04' else '掌面朝脸','#a96b18',(-65,6))
 for n in ['sh_n','el_n','wr_n','palm_n','tip_n']:point(d,j[n],'#bd263a',5)
 # Geometric head ellipse matches mother framing; nose/chin/mouth are explicit,
 # without painting a character face or retaining source arm pixels.
 ctr=J0['head_center'];poly=[]
 for z in range(121):
  a=math.tau*z/120;p=[ctr[0]+147*math.cos(a),ctr[1]+163*math.sin(a)];poly.append(moved(p,J0['neck'],k['head_rotation_deg']))
 line(d,poly,'#72777b',2)
 line(d,[j['head_center'],j['nose']],'#72777b',2);point(d,j['nose'],'#72777b',3)
 point(d,j['mouth_proxy'],'#df9b00',5);point(d,j['chin_visible'],'#4b9b72',4)
 label(d,j['mouth_proxy'],'嘴位估计 ±15px','#996a00',(9,-11));label(d,j['chin_visible'],'可见下巴','#39835d',(-84,3))
 for name,cn,off in [('sh_n','近肩',(-70,-22)),('el_n','近肘',(-72,3)),('wr_n','近腕',(10,4)),('tip_n','指尖',(9,-22))]:
  p=j[name];label(d,p,f'{cn}({p[0]:.1f},{p[1]:.1f})','#a82636',off)
 d.text((16,14),f'S18 {k["id"]}  目标骨架参考｜635×1175',font=font,fill='#212121')
 d.text((16,39),'红色整条近臂可变；头肩、蓝色远臂、凳和坐姿固定',font=small,fill='#414141')
 d.text((16,60),'身份另见 master_identity.png；此图没有旧抬臂底图',font=small,fill='#414141')
 # Notes use blank space beside mid-body; do not cover source-pixel coordinates.
 texts=[k['expression_note'],'上臂 %.2fpx / 前臂 %.2fpx'%(L1,L2),'木凳固定点 A(23,898) / B(309,1141)','肩点为袖内估计，嘴位被母版手遮挡','这是生图参考，尚未验证连续动画']
 y=662
 for text in texts:
  for x in range(0,len(text),20):d.text((12,y),text[x:x+20],font=small,fill='#414141');y+=20
 img.save(P/(k['id']+'_target.png'))
 # Separate close-up retains native coordinates in labels, not a replacement frame.
 img.crop((185,245,520,635)).resize((670,780)).save(P/(k['id']+'_arm_detail.png'))
 return img
imgs=[draw(k) for k in keys];sheet=Image.new('RGB',(W*3,H),'white')
for n,img in enumerate(imgs):sheet.paste(img,(n*W,0))
sheet.save(P/'three_targets.png')
# Master joint overlay is measurement evidence only, never a target generation reference.
show=Image.new('RGBA',im.size,(232,238,232,255));show.alpha_composite(im.convert('RGBA'));d=ImageDraw.Draw(show)
for chain,c in [(['sh_n','el_n','wr_n','palm_n','mcp_n','tip_n'],'#df3449'),(['sh_f','el_f','wr_f','palm_f','tip_f'],'#397eca')]:
 line(d,[J0[n] for n in chain],c,3)
 for n in chain:point(d,J0[n],c,4);label(d,J0[n],n+str(tuple(J0[n])),c)
for n,p in anchors.items():point(d,p,'#83590b',4)
show.convert('RGB').save(P/'master_measurement_overlay.png')
print(json.dumps({'source_sha256':SHA,'near_lengths_px':spec['near_lengths_px'],'k06':keys[1]},ensure_ascii=False,indent=2))
