#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,math,shutil
P=Path(__file__).resolve().parent
SRC=Path('/workspace/animation-competition/assets/chars/x16_arms_loose.png')
SHA='cf7756acf52a58b0279b03733fe75c87b1c9ddbb162d29b5e1aa6e12a766e280'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SHA
im=Image.open(SRC);assert im.size==(635,1175)
shutil.copyfile(SRC,P/'master_identity_x16_arms_loose.png')
J={
 'neck_root':[273,418],'head_center_proxy':[239,242],
 'near_shoulder':[235,481],'near_elbow':[277,681],'near_wrist':[414,739],'near_palm':[451,750],'near_fingertip':[490,780],
 'far_shoulder':[324,490],'far_elbow':[361,669],'far_wrist':[455,721],'far_palm':[487,733],'far_fingertip':[523,760],
 'waist_proxy':[263,643],'pelvis_proxy':[223,801],'near_knee_proxy':[465,813],'near_ankle':[431,1082],'near_toe':[555,1132],
 'far_knee_proxy':[515,799],'far_ankle':[498,1060],'far_toe':[600,1110],
 'near_eye_center':[313,253],'far_eye_visible_edge':[363,234],'mouth_center':[375,316],'nose_tip':[391,265],'chin_visible':[343,373],'ear_center':[195,315],
 'tuft_top':[194,18],'tuft_free_tip':[150,42],'tuft_root':[209,85],'near_braid_tie':[121,368],'far_braid_tie':[194,388]}
confidence={
 'neck_root':{'status':'occluded/anatomical proxy','uncertainty_px':10},'head_center_proxy':{'status':'composition proxy, not a surface feature','uncertainty_px':15},
 'near_shoulder':{'status':'hidden by sleeve; estimated','uncertainty_px':12},'near_elbow':{'status':'joint center estimated from visible bend','uncertainty_px':8},'near_wrist':{'status':'visible wrist transition; estimated center','uncertainty_px':6},
 'far_shoulder':{'status':'occluded shoulder; estimated','uncertainty_px':15},'far_elbow':{'status':'partly occluded by foreground arm; estimated','uncertainty_px':12},'far_wrist':{'status':'visible wrist transition; estimated center','uncertainty_px':6},
 'near_palm':{'status':'visible palm/back-of-hand center proxy','uncertainty_px':5},'near_fingertip':{'status':'visible fingertip; no digit identity claimed','uncertainty_px':3},'far_palm':{'status':'visible hand center proxy','uncertainty_px':5},'far_fingertip':{'status':'visible fingertip; no digit identity claimed','uncertainty_px':3},
 'waist_proxy':{'status':'garment waist position, not pelvis','uncertainty_px':5},'pelvis_proxy':{'status':'occluded by skirt; seated-location proxy','uncertainty_px':15},
 'near_knee_proxy':{'status':'knee under skirt edge; estimated','uncertainty_px':10},'far_knee_proxy':{'status':'partly hidden by skirt; estimated','uncertainty_px':10}}
for n in J:
 if n not in confidence:confidence[n]={'status':'visible landmark / shape-center estimate','uncertainty_px':3 if 'tuft' in n or 'braid' in n else 5}
ang=-.8;ar=math.radians(ang);c=math.cos(ar);ss=math.sin(ar);cx,cy=J['neck_root'];HM=[[c,-ss,cx-c*cx+ss*cy],[ss,c,cy-ss*cx-c*cy],[0,0,1]]
def apply(p):return [HM[0][0]*p[0]+HM[0][1]*p[1]+HM[0][2],HM[1][0]*p[0]+HM[1][1]*p[1]+HM[1][2]]
T={k:v[:] for k,v in J.items()}
headnames=['head_center_proxy','near_eye_center','far_eye_visible_edge','mouth_center','nose_tip','chin_visible','ear_center','tuft_top','tuft_free_tip','tuft_root','near_braid_tie','far_braid_tie']
for n in headnames:T[n]=apply(J[n])
checks=[]
for side in ['near','far']:
 s=J[side+'_shoulder'];e=J[side+'_elbow'];w=J[side+'_wrist'];l1=math.dist(s,e);l2=math.dist(e,w);ns=[s[0],s[1]-2];dx=w[0]-ns[0];dy=w[1]-ns[1];d=math.hypot(dx,dy)
 assert abs(l1-l2)<d<l1+l2
 a=math.atan2(dy,dx);b=math.acos((l1*l1+d*d-l2*l2)/(2*l1*d));opts=[[ns[0]+l1*math.cos(a+q*b),ns[1]+l1*math.sin(a+q*b)] for q in [-1,1]];ne=min(opts,key=lambda p:math.dist(p,e));T[side+'_shoulder']=ns;T[side+'_elbow']=ne
 checks.append({'side':side,'upperarm_length_px':l1,'forearm_length_px':l2,'shoulder_displacement_px':2,'elbow_compensation_displacement_px':math.dist(e,ne),'wrist_displacement_px':0,'max_bone_length_error_px':max(abs(math.dist(ns,ne)-l1),abs(math.dist(ne,w)-l2))})
anchors={'A_stool_seat_front_left_lower_corner':[23,898],'B_stool_front_right_foot_outer_bottom':[309,1141],'C_stool_front_left_foot_outer_bottom':[23,1141]}
fixed=[n for n in J if n not in headnames+['near_shoulder','far_shoulder','near_elbow','far_elbow']]
assert all(T[n]==J[n] for n in fixed)
spec={'shot':'S18','key':'k04','status':'reference/request prepared only; image generation not authorized in this task','master':str(SRC),'master_copy':'master_identity_x16_arms_loose.png','source_sha256':SHA,'size':[635,1175],
 'coordinate_convention':'native source pixels, x right/y down; near=anatomical right arm; far=anatomical left arm',
 'amplitude':{'head_rotation_reference_deg':-.8,'head_rotation_absolute_limit_deg':1,'head_pivot':J['neck_root'],'head_translation_independent_px':[0,0],'shoulder_lift_reference_px':2,'shoulder_lift_limit_px':3,'elbow_passive_compensation_limit_px':3,'head_feature_motion_is_allowed':True,'precision_statement':'These numbers describe a small reference envelope, not generator precision or guaranteed pixel locking.'},
 'head_reference_matrix':HM,'source_landmarks':J,'source_landmark_confidence':confidence,'target_landmarks':T,'fixed_landmark_names':fixed,'fixed_stool_anchors':anchors,'kinematic_checks':checks,
 'expression':{'source':'eyes open, mouth already slightly open; hands on lap','target':'laugh burst: curved smiling closed eyes, slight cheek lift, slightly wider open laughing mouth; same face silhouette','far_eye':'keep the original side-view visibility; do not invent a full second frontal eye'},
 'notes':['This master is x16_arms_loose, not x18_laugh; no previous x18 k04 joint set is reused.','Head/hair may rotate together slightly; do not also instruct the head to remain absolutely motionless. Preserve tuft shape, braid count, ties, bangs and hair volume while permitting the stated small rigid-pose change.','Both wrists, palms, all fingers and hand-to-lap contact remain fixed. Elbows receive only passive 2.4-2.6px compensation needed by the 2px shoulder reference, not a new arm action.','Hip/legs/skirt/stool/shoes and camera framing remain unchanged. No hand raises or mouth-covering action.','Shoulders and covered joints are estimates. Exact target decimal coordinates are geometric calculation output, not visible anatomical precision.','One future image at most if separately authorized; no generation has been invoked here.']}
(P/'k04_loose_reference.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
F='/workspace/animation-competition/assets/fonts/NotoSansSC-VF.ttf';font=ImageFont.truetype(F,16);small=ImageFont.truetype(F,12);tiny=ImageFont.truetype(F,10)
out=Image.new('RGB',(635,1175),'#fcfcfa');d=ImageDraw.Draw(out)
def line(pts,col,width=3):d.line([tuple(p) for p in pts],fill=col,width=width)
def dot(p,col,r=4):d.ellipse((p[0]-r,p[1]-r,p[0]+r,p[1]+r),fill=col,outline='white',width=1)
def txt(p,s,col='#383838'):d.text(tuple(p),s,font=small,fill=col,stroke_width=1,stroke_fill='white')
# Static support geometry, source-pixel positions.
for p in [[[23,856],[96,831]],[[23,856],[229,856],[258,899],[23,899],[23,856]],[[51,900],[98,900],[63,1141],[23,1141],[51,900]],[[261,902],[300,929],[313,1141],[278,1141],[261,902]],[[99,901],[134,901],[113,1105],[81,1105],[99,901]],[[79,985],[266,985],[267,1016],[74,1016],[79,985]]]:line(p,'#a0805b',3)
for side in ['near','far']:line([T[n] for n in ['pelvis_proxy',side+'_knee_proxy',side+'_ankle',side+'_toe']],'#8b9599',3)
line([T[n] for n in ['pelvis_proxy','waist_proxy','neck_root']],'#858b90',3)
for side,col in [('far','#547eac'),('near','#c63c4c')]:
 chain=[side+'_shoulder',side+'_elbow',side+'_wrist',side+'_palm',side+'_fingertip'];line([T[n] for n in chain],col,5)
 line([T['neck_root'],T[side+'_shoulder']],col,2)
 for n in chain:dot(T[n],col,4)
 for n,cn,off in [(side+'_shoulder','肩',(-65,-18)),(side+'_elbow','肘',(-60,4))]:
  p=T[n];txt([p[0]+off[0],p[1]+off[1]],cn+f'({p[0]:.1f},{p[1]:.1f})',col)
# Geometric head guide + actual visible feature landmarks. No copied face/old pose.
ctr=J['head_center_proxy'];poly=[]
for i in range(121):
 a=math.tau*i/120;poly.append(apply([ctr[0]+147*math.cos(a),ctr[1]+163*math.sin(a)]))
line(poly,'#777c81',2);line([T['neck_root'],T['head_center_proxy']],'#a1a6a9',2)
for n,col in [('nose_tip','#777c81'),('chin_visible','#3d9166'),('mouth_center','#c38a16'),('near_eye_center','#c38a16'),('far_eye_visible_edge','#c38a16'),('tuft_top','#456c84'),('tuft_free_tip','#456c84'),('tuft_root','#456c84'),('near_braid_tie','#986687'),('far_braid_tie','#986687')]:dot(T[n],col,3)
line([T['tuft_free_tip'],T['tuft_top'],T['tuft_root']],'#6b8799',1)
for a,p in anchors.items():d.rectangle((p[0]-4,p[1]-4,p[0]+4,p[1]+4),fill='#b48b39',outline='black')
txt([12,10],'S18 k04｜真实底图 x16_arms_loose')
texts=['仅准备，尚未生图','头后仰参考 −0.8°','上限 1°；绕颈根','双肩上提参考 2px','上限 3px','肘仅随动约 2.6px','双腕双手保持搭膝','不抬手，不捂嘴','眼睛弯月、嘴喷笑','头顶翘发与辫子','随头轻转，形状保留','圆轮廓仅是范围','脸型发型看母版']
y=35
for text in texts:d.text((416,y),text,font=small,fill='#333333');y+=20
for p,s in [([407,475],'635×1175 原生坐标'),([407,495],'红：近臂 / 蓝：远臂'),([407,515],'肩位藏于袖内：估计'),([407,535],'嘴、眼、翘发：可见'),([407,555],'此图不承诺数值锁定')]:txt(p,s)
txt([11,748],'两手、指头、裙点、坐姿固定')
txt([11,776],'凳锚 A(23,898) / B(309,1141)')
txt([14,1154],'参考包：底图另给；不沿用旧 x18 k04，不扩张至整套')
out.save(P/'k04_loose_target_reference.png')
print(json.dumps({'amplitude':spec['amplitude'],'kinematic_checks':checks,'head_motion_pixels':{n:math.dist(J[n],T[n]) for n in headnames}},ensure_ascii=False,indent=2))
