from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import json, math, hashlib, copy, argparse
import numpy as np
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/'astra_s03b_painted_pilot_20261018/refs'
parser=argparse.ArgumentParser(description='S03 diagnostic reference builder; no production painting edits')
parser.add_argument('--source-dir',help='Directory containing the seven original S03_grandma_k*.png files')
parser.add_argument('--font',help='Path to Noto Sans SC or another CJK font')
args=parser.parse_args()
PAINT=Path(args.source_dir) if args.source_dir else BASE/'painted'
FONT=Path(args.font) if args.font else BASE/'NotoSansSC-VF.ttf'
for sub in ['sources','new13','all20','contact']: (ROOT/sub).mkdir(exist_ok=True)
W,H=1672,941
FT=lambda n:ImageFont.truetype(str(FONT),n)
f22,f26,f32,f40=FT(22),FT(26),FT(32),FT(40)
red='#b93b39'; blue='#396fa4'; amber='#bc760d'; green='#287e50'; gray='#737b86';purple='#865394'
starts=[0,9,13,17,21,26,30,34,37,40,44,48,52,55,58,65,74,75,76,79]
holds=[9,4,4,4,5,4,4,3,3,4,4,4,3,3,7,9,1,1,3,17]
old={0:1,13:2,26:3,34:4,44:5,58:6,79:7}
files={int(p.name.split('_k')[1][:2]):p for p in PAINT.glob('*.png')}
plan=json.loads((ROOT/'sources/opening_plan_280c1e2.json').read_text())
notes={f:s for f,s in plan['S03']['frames']}
# All coordinates below are hand annotations of the actual frozen source, NOT generated rig output.
# Approximation is deliberate and explicit: hidden centers are uncertain.
def LM(ls,le,lw,lp,rs,re,rw,rp,hc,eyes,pupils,mouth,plate,A,B,Hbutton,fruit):
 return dict(screen_left_shoulder=ls,screen_left_elbow=le,screen_left_wrist=lw,screen_left_palm_center=lp,screen_right_shoulder=rs,screen_right_elbow=re,screen_right_wrist=rw,screen_right_palm_center=rp,head_center=hc,eye_centers=eyes,pupils=pupils,mouth_center=mouth,neck=[831,421],sternum=Hbutton,basin_A=A,basin_B=B,button_H=Hbutton,plate=plate,fruit=fruit)
FREST={'tip':[443,849],'rind_left':[428,928],'rind_bottom':[482,932],'rind_right':[530,897]}
FGRAB={'tip':[383,819],'rind_left':[367,899],'rind_bottom':[419,911],'rind_right':[488,869]}
FHOLD={'tip':[239,639],'rind_left':[216,713],'rind_bottom':[294,748],'rind_right':[339,700]}
M={}
for k in [1,2]:
 M[k]=LM([625,490],[505,752],[671,723],[739,710],[1045,505],[1175,767],[1035,755],[949,735],[854,274],[[805,301],[914,314]],[[807,304],[910,317]] if k==1 else [[792,304],[902,317]],[849,379],{'center':[455,920],'rx':107,'ry':22,'back_y':900},[558,850],[1118 if k==1 else 1119,850],[838,545],copy.deepcopy(FREST))
M[3]=LM([625,490],[505,752],[671,723],[739,710],[1045,505],[1175,767],[1035,755],[949,735],[830,263],[[725,277],[825,298]],[[724,279],[820,300]],[770,359],{'center':[455,920],'rx':107,'ry':22,'back_y':900},[558,851],[1119,851],[838,545],copy.deepcopy(FREST))
M[4]=LM([622,486],[480,710],[585,690],[635,704],[1045,505],[1178,768],[1046,770],[961,772],[850,262],[[767,265],[875,290]],[[764,267],[869,292]],[814,356],{'center':[455,920],'rx':107,'ry':22,'back_y':900},[558,850],[1119,850],[839,547],copy.deepcopy(FREST))
M[5]=LM([625,490],[500,740],[410,800],[380,835],[1045,505],[1178,767],[1043,769],[962,764],[830,263],[[724,276],[826,298]],[[724,279],[819,300]],[771,359],{'center':[413,901],'rx':114,'ry':23,'back_y':878},[556,850],[1121,851],[838,545],copy.deepcopy(FGRAB))
for k in [6,7]:
 M[k]=LM([620,489],[475,720],[345,730],[309,747],[1047,505],[1180,772],[1063,787],[981,783],[832,273],[[714,285],[813,310]],[[713,286],[807,312]],[754,374],{'center':[453,912],'rx':112,'ry':22,'back_y':892},[556,849 if k==6 else 850],[1121,850],[837,551],copy.deepcopy(FHOLD))
# Contact points are separate from anatomical palm center.
C={
0:dict(mode='pinch_pod',palm_load=None,thumb=[807,713],fingers=[[795,728]],pod=[[808,713],[867,720]]),
13:dict(mode='pinch_pod',palm_load=None,thumb=[807,713],fingers=[[795,728]],pod=[[808,713],[867,720]]),
26:dict(mode='pinch_pod',palm_load=None,thumb=[807,713],fingers=[[795,728]],pod=[[808,713],[867,720]]),
34:dict(mode='release_pod_no_fruit_contact',palm_load=None,thumb=[698,701],fingers=[[686,737],[660,751],[636,751]],pod=[[686,739],[753,781]]),
44:dict(mode='side_grasp_rind_not_yet_full_support',palm_load=[371,870],thumb=[405,830],fingers=[[367,850],[361,877],[359,893]],pod=None),
58:dict(mode='supinated_support_under_rind',palm_load=[275,745],thumb=[205,696],fingers=[[235,728],[260,735],[285,743]],pod=None),
79:dict(mode='supinated_support_under_rind',palm_load=[275,745],thumb=[205,696],fingers=[[235,728],[260,735],[285,743]],pod=None)
}
def lerp(a,b,t):
 if isinstance(a,dict):return {k:lerp(a[k],b[k],t) for k in a}
 if isinstance(a,list):return [lerp(x,y,t) for x,y in zip(a,b)]
 return round((1-t)*a+t*b,3)
def interp(f):
 lo=max(x for x in old if x<f); hi=min(x for x in old if x>f)
 return lerp(M[old[lo]],M[old[hi]],(f-lo)/(hi-lo))
P={f:copy.deepcopy(M[k]) for f,k in old.items()}
for f in starts:
 if f not in old:P[f]=interp(f)
# New frames: projective endpoint closure, deliberate arm/contact path, no sampling of faulty code wrist.
P[9]['screen_left_wrist']=[674,721];P[9]['screen_left_palm_center']=[744,708]
C[9]=dict(mode='pinch_pod_tip',palm_load=None,thumb=[812,711],fingers=[[802,720]],pod=[[813,712],[867,720]])
for f in [17,21]:C[f]=copy.deepcopy(C[13])
P[30]['screen_left_elbow']=[492,731];P[30]['screen_left_wrist']=[626,705];P[30]['screen_left_palm_center']=[687,714]
P[30]['screen_right_wrist']=[1040,763];P[30]['screen_right_palm_center']=[957,758]
C[30]=dict(mode='lower_pod_over_basin',palm_load=None,thumb=[745,729],fingers=[[727,739],[710,749]],pod=[[734,742],[787,773]])
P[37]['screen_left_elbow']=[487,723];P[37]['screen_left_wrist']=[521,729];P[37]['screen_left_palm_center']=[505,774]
P[37]['fruit']=copy.deepcopy(FREST)
C[37]=dict(mode='open_hand_reach_no_fruit_contact',palm_load=None,thumb=[529,790],fingers=[[481,813],[490,825],[503,824]],pod=[[719,811],[751,839]])
P[40]['screen_left_elbow']=[495,740];P[40]['screen_left_wrist']=[449,778];P[40]['screen_left_palm_center']=[432,835]
P[40]['fruit']=copy.deepcopy(FREST)
C[40]=dict(mode='first_rind_touch_fruit_still_on_plate',palm_load=[430,893],thumb=[449,872],fingers=[[428,892],[430,907],[440,915]],pod=None)
# Match the two frozen fruit endpoint silhouettes with one canonical planar template.
# Homographies are a drawing/view construction, not a recovered physical camera or proof of rigidity.
for f,t,e,w,p,contact in [
 (48,.26,[493,751],[410,818],[391,873],dict(mode='grasp_to_support_roll',palm_load=[382,866],thumb=[353,826],fingers=[[341,846],[358,858],[378,866]],pod=None)),
 (52,.65,[484,738],[390,786],[352,802],dict(mode='support_established_send',palm_load=[337,804],thumb=[265,760],fingers=[[302,790],[325,800],[346,805]],pod=None)),
 (55,.90,[478,724],[364,751],[326,767],dict(mode='support_send_ease_out',palm_load=[305,763],thumb=[220,713],fingers=[[261,748],[284,758],[305,764]],pod=None))]:
 P[f]['screen_left_elbow']=e;P[f]['screen_left_wrist']=w;P[f]['screen_left_palm_center']=p;P[f]['fruit']=lerp(FGRAB,FHOLD,t);C[f]=contact
# Hand+fruit lock for the wait/blink: body and contact coordinates are exactly k06.
for f in [65,74,75,76]:P[f]=copy.deepcopy(M[6]);C[f]=copy.deepcopy(C[58])
# New plate/registration target. Legacy measurements remain unchanged and visible as a separate layer.
plate_target={'center':[453,918],'rx':112,'ry':24,'back_y':892}
for f in starts:
 if f not in old:
  base_anchor=old[max(a for a in old if a<f)]
  for field in ['plate','basin_A','basin_B','button_H']:
   P[f][field]=copy.deepcopy(M[base_anchor][field])
# 310 / 240 are a conservative construction envelope around the source projected landmarks.
# Positive depth branch is fixed for the whole sequence. It is NOT an anatomical measurement.
L1,L2=310.,240.
def make3d(p,side):
 s=np.array([*p[f'{side}_shoulder'],0.]);e2=np.array(p[f'{side}_elbow']);w2=np.array(p[f'{side}_wrist'])
 d1=float(np.linalg.norm(e2-s[:2]));d2=float(np.linalg.norm(w2-e2));assert d1<L1 and d2<L2,(side,d1,d2)
 e=np.array([*e2,math.sqrt(L1*L1-d1*d1)]);w=np.array([*w2,e[2]+math.sqrt(L2*L2-d2*d2)])
 return {'shoulder':s.tolist(),'elbow':e.tolist(),'wrist':w.tolist(),'upper_projected_length':d1,'fore_projected_length':d2}
def homography(src,dst):
 a=[];b=[]
 for (x,y),(u,v) in zip(src,dst):a.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]);b.extend([u,v])
 h=np.linalg.solve(np.array(a,float),np.array(b,float));return np.append(h,1).reshape(3,3).tolist()
fruit_order=['tip','rind_left','rind_bottom','rind_right'];canonical=[FHOLD[k] for k in fruit_order]
STATES=[]
for i,(f,hold) in enumerate(zip(starts,holds),1):
 p=P[f];eye=.5 if f in [74,76] else 0. if f==75 else 1.
 key={'id':f'd{i:02d}','frame':f,'hold':hold,'end_inclusive':f+hold-1,'existing_frozen_anchor':f in old,'source_anchor_id':f'k{old[f]:02d}' if f in old else None,'description':notes[f],'landmarks_xy':p,'arm_construction_xyz':{s:make3d(p,s) for s in ['screen_left','screen_right']},'contact':C[f],
 'expression':{'eye_open_fraction':eye,'eyelids':'half_closed' if eye==.5 else 'fully_closed_no_pupil_or_white' if eye==0 else 'open','brow_lift_px':4 if f==65 else 3 if f in [74,75,76] else 0,'mouth_unchanged_from_k06':f in [65,74,75,76]},
 'fruit_template_homography':homography(canonical,[p['fruit'][k] for k in fruit_order]),'fruit_geometry_interpretation':'One fixed planar reference template; homography represents view/occlusion endpoint construction. It is not a measured 3D pose. Old contour irregularities retained.',
 'contact_occlusion':({'back':['wrist/palm behind fruit until lower rim'],'front':['thumb on near flesh','fingers curling around lower rind'],'support':'palm center under lower rind'} if f==48 else {'back':['thumb behind screen-left fruit edge'],'front':['fingers over lower curved rind'],'support':'palm below rind'} if f>=52 else {'back':['palm behind screen-left rind'],'front':['thumb on near flesh','fingers around left rind'],'support':'side grasp; rim overlap retained'} if f==44 else {'back':['fruit stays on plate'],'front':['fingertips first touch rind'],'support':'plate carries fruit'} if f==40 else {}),
 'layering':{'arm':'working arm in front of shirt, continuous inside canvas','fruit':'on plate' if f<=40 else 'side grasp / rim overlap preserved' if f==44 else 'clear of plate; stays supported', 'basin':'fixed; visible front rim occludes rear contents and lower torso','plate':'source-native unchanged' if f in old else 'inherit preceding frozen source static plate pixels; F048/052/055 repair choice pending; plate_target is decision overlay only', 'pod':'release above basin; gone by F040'}}
 STATES.append(key)
manifest=[]
for k,p in files.items():
 raw=p.read_bytes();im=Image.open(p)
 manifest.append({'anchor':f'k{k:02d}','repository_path':'collab/reviews/20261018_0428_s03_keypose_candidates/originals/'+p.name,'source_verified_commit':'fb0f76b40932f395bf90834d9fa274d4cb6ffd11','local_reference_filename':p.name,'native_size':list(im.size),'sha256':hashlib.sha256(raw).hexdigest(),'git_blob_sha1':hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),'to_working_canvas_matrix':[[1,0,0],[0,1,0],[0,0,1]],'padding':'right transparent only, no scale/translation; original file untouched','lighting':'legacy light cool fill' if k<=4 else 'neutral base as previously frozen','measurements':M[k]})
spec={
 'shot':'S03','status':'PROPOSAL_FOR_OPUS_FREEZE_ONLY_NOT_PRODUCTION','repository':'yiggeror/animation-competition','branch':'claude/intelligent-euler-t2so6e','read_commit':'280c1e25533b76cc5e44e954b45cc98297a36b46','plan_blob_sha1':'12ce95435f1e8b73f40c913ef0a883c0fac46305','fps':24,'duration_frames':96,'state_count':20,'new_count':13,'new_image_generation_calls':0,
 'coordinate_system':{'canvas':[1672,941],'units':'native source pixels','axes':'x right, y down, positive constructed z toward viewer','source_images_resampled':False,'old_anchor_status':'Preserve original files and observed endpoint interface. This is not a user prohibition on approved non-destructive repair copies.','old_k01_F005_aliases_exposure_F000':True},
 'measurement_method':'Manual visual landmark annotation on actual alpha-composited native pixel source + independent visual cross-check. Existing anchor coordinates are approximate observed centers, not an automated fit or inferred rig replacement.',
 'uncertainty_px':{'hidden_shoulder':25,'elbow':15,'wrist':10,'palm_center':12,'visible_contact':6,'plate_center':8,'head_center':15,'visible_eye_mouth':5},
 'bone_construction':{'upper_length':L1,'fore_length':L2,'length_units':'equivalent source px','physical_lengths_known':False,'projection':'orthographic construction','method':'Keep each annotated 2D endpoint exactly. Lift elbow z=sqrt(Lupper^2-d2D_upper^2); wrist z=elbow_z+sqrt(Lfore^2-d2D_fore^2). Same positive branch and same lengths for all frames. New XY positions are a hand-designed continuous arc, not borrowed code geometry.','rationale':'310/240 encloses all measured projected arm spans with plausible foreshortening; approximately 0.77 forearm/upper ratio is a construction choice checked against the neutral turnaround, not recovered anatomy. Side/pose depth is underdetermined.','limitation':'Exact algebraic lengths do not prove anatomical plausibility or production-frame compliance. Hidden joint centers and depth must remain reviewable.'},
 'static_anchor_policy':{'basin_target_A':[558,850],'basin_target_B':[1119,850],'button_H_reference':[838,545],'button_H_role':'independent diagnostic, never fit away body drift; legacy k06/k07 H residual documented','plate_target':plate_target,'plate_target_basis':'OPTIONAL DECISION OVERLAY for acquisition segment only: k06/k07 horizontal center and size, y918 chosen for comparison. Not a global repaint instruction; A/C retain their frozen source background pixels.','legacy_native_measurements_preserved':True},
 'legacy_conflicts':[{'kind':'plate','detail':'k04 native center(455,920), k05(413,901), k06/07(453,912). Cannot keep old rendered pixels unchanged and also eliminate this prop jump by adding only 13 frames. A/C new states retain the corresponding source static pixels. B new plate layer remains pending; fixed target appears only as an optional decision overlay, not an authorized repaint.','freeze_decision_needed':'Opus chooses retain documented legacy jump OR authorize non-destructive scene plate isolation/replacement under an explicit per-anchor mask. Do not repaint source anchors.'},{'kind':'head','detail':'k03->k04->k05 changes head orientation back and forth. New states close real endpoints; old head drawings are not silently made monotonic.'},{'kind':'lighting','detail':'k01-04 contain legacy light cool fill; k05-07 neutral baseline. All new frames must have neutral material colors. Old cool-fill handling needs explicit render-profile agreement to avoid a second cool multiplication.'}],
 'lighting_interface':{'new13':'neutral unlit/base colors only, scene light applied once downstream','legacy_k01_k04':'preserve baked-light provenance; no second identical cool multiplier; any neutralization is a separate explicitly approved operation','legacy_k05_k07':'neutral base; single scene light pass','forbidden':'Do not grade new drawings individually to match the prelit old cool subset.'},
 'parallel_authoring_segments':[{'segment':'A','range':[0,26],'new_frames':[9,17,21],'chains':[['k01','F009','k02'],['k02','F017','F021','k03']]},{'segment':'B','range':[26,58],'new_frames':[30,37,40,48,52,55],'chains':[['k03','F030','k04'],['k04','F037','F040','k05'],['k05','F048','F052','F055','k06']]},{'segment':'C','range':[58,95],'new_frames':[65,74,75,76],'chains':[['k06','F065','F074','F075','F076','k07']]}],
 'authoring_rule':'Within each chain derive from the previous accepted drawing, always include the next frozen endpoint as constraint. A frozen anchor restarts that chain. Do not generate thirteen unrelated standalone frames.','sources':manifest,'states':STATES}
(ROOT/'S03_proposal.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
# Rendering is diagnostic annotation only, not a production image edit.
def line(d,pts,col=red,width=6):d.line([tuple(map(float,p[:2])) for p in pts],fill=col,width=width,joint='curve')
def dot(d,p,label='',col=red,r=6,font=f22):
 x,y=p[:2];d.ellipse((x-r,y-r,x+r,y+r),fill=col)
 if label:d.text((x+10,y-25),label,font=font,fill=col)
def bez(p0,p1,p2,p3,n=32):
 return [tuple((1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*e for a,b,c,e in zip(p0,p1,p2,p3)) for t in np.linspace(0,1,n)]
def melon(d,v):
 t,l,b,r=[v[k] for k in fruit_order]
 curve=bez(l,[l[0]+4,b[1]+5],[b[0]-15,b[1]+7],b)+bez(b,[b[0]+24,b[1]-2],[r[0]-9,r[1]+27],r)
 pts=[t,l]+curve+[r,t];d.polygon([tuple(p) for p in pts],fill='#e4eee6');line(d,pts,green,5)
 inn=[(l[0]+10,l[1]-6),(b[0]-1,b[1]-10),(r[0]-7,r[1]-5)];line(d,[t,*inn,t],'#b95e62',3)
 for pt,lab in [(t,'T'),(b,'R')]:dot(d,pt,lab,green,4)
def dashed(d,a,b,col,width=4):
 a=np.array(a,float);b=np.array(b,float);dist=float(np.linalg.norm(b-a))
 for st in np.arange(0,dist,12):
  line(d,[a+(b-a)*st/dist,a+(b-a)*min(st+6,dist)/dist],col,width)
def draw_hand(d,k,detail=False):
 p=k['landmarks_xy'];c=k['contact'];wr=p['screen_left_wrist'];pa=p['screen_left_palm_center']
 (dashed(d,wr,pa,amber,5) if k['frame']==48 else line(d,[wr,pa],amber,8));dot(d,pa,'' if detail else '',amber,5)
 for fi in c['fingers']:line(d,[pa,[(pa[0]+fi[0])/2,pa[1]+10],fi],amber,4);dot(d,fi,'',amber,3)
 dashed(d,pa,c['thumb'],'#a76db3',3);dot(d,c['thumb'],'' if detail else '',purple,4)
 if c['palm_load']:
  q=c['palm_load'];dot(d,q,'C' if not detail else '',green,6);d.ellipse((q[0]-12,q[1]-12,q[0]+12,q[1]+12),outline=green,width=2)
 if c['pod']:
  a,b=c['pod'];line(d,[a,b],green,9);dot(d,b,'荚' if detail else '',green,4)
def face(d,k):
 p=k['landmarks_xy'];hc=p['head_center'];d.ellipse((hc[0]-145,hc[1]-180,hc[0]+145,hc[1]+163),outline=gray,width=3)
 eye=k['expression']['eye_open_fraction']
 for e,pupil in zip(p['eye_centers'],p['pupils']):
  x,y=e;rh=12*eye
  if eye==0:line(d,bez((x-21,y),(x-10,y+5),(x+10,y+5),(x+21,y)),purple,4)
  else:
   d.ellipse((x-23,y-rh,x+23,y+rh),outline=purple,width=3)
   # Dot clipped to the diagnostic eye opening, never visible at full closure.
   r=max(3,int(7*eye));px=max(x-16,min(x+16,pupil[0]));d.ellipse((px-r,y-r,px+r,y+r),fill=purple)
  lift=k['expression']['brow_lift_px'];line(d,[(x-21,y-38-lift),(x,y-44-lift),(x+21,y-37-lift)],purple,3)
 dot(d,p['mouth_center'],'嘴',purple,4)
def diagram(k):
 f=k['frame'];p=k['landmarks_xy'];anchor=old[f] if f in old else old[max(a for a in old if a<f)]
 im=Image.open(files[anchor]).convert('RGBA');bg=Image.new('RGBA',(W,H),'#f7f8fa');ghost=im.copy();ghost.putalpha(ghost.getchannel('A').point(lambda x:int(x*(.34 if f in old else .10))));bg.alpha_composite(ghost,(0,0))
 out=Image.new('RGB',(W,H+186),'white');out.paste(bg.convert('RGB'),(0,0));d=ImageDraw.Draw(out)
 # Grid at 200 px, coordinate checks are easy without obscuring hands.
 for x in range(200,W,200):d.line((x,40,x,H),fill='#e0e5eb',width=1);d.text((x+3,42),str(x),font=FT(17),fill='#9aa1aa')
 for y in range(200,H,200):d.line((180,y,1240,y),fill='#e0e5eb',width=1);d.text((180,y+3),str(y),font=FT(17),fill='#9aa1aa')
 d.text((28,14),f"S03  F{f:03d}  /  d{starts.index(f)+1:02d}    {'旧锚实测标注' if f in old else '新增姿态提案'}",font=f32,fill='#202b3c')
 line(d,[p['head_center'],p['neck'],p['sternum'],[837,805]],gray,4)
 line(d,[p['screen_left_shoulder'],p['screen_right_shoulder']],gray,3)
 for side,col in [('screen_left',red),('screen_right',blue)]:
  pts=[p[f'{side}_{j}'] for j in ['shoulder','elbow','wrist']];line(d,pts,col,7)
  for j,pt in zip(['S*','E*','W'],pts):dot(d,pt,j,col,5)
  if side=='screen_right':line(d,[pts[-1],p[f'{side}_palm_center']],col,5)
 face(d,k)
 # Basin and plate fixed proposal outlines, old native positions remain exposed.
 d.ellipse((558,804,1119,897),outline='#4c7786',width=3)
 for nm in ['basin_A','basin_B','button_H']:
  q=p[nm];dot(d,q,nm.split('_')[-1],green,5)
 plate=p['plate'];cx,cy=plate['center'];rx,ry=plate['rx'],plate['ry'];d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),outline=gray,width=3)
 if f in [40,44,48,52,55]:
  tx,ty=plate_target['center'];
  for a in range(0,360,24):
   d.arc((tx-112,ty-24,tx+112,ty+24),start=a,end=a+12,fill='#cf9a7f',width=3)
  d.text((30,890),'虚线盘：待决方案，不作重画指令',font=f22,fill='#a85837')
 melon(d,p['fruit']);draw_hand(d,k)
 yy=H+10
 d.text((28,yy),f"F{f:03d}–{k['end_inclusive']:03d}  停{k['hold']}帧  {notes[f]}",font=f32,fill='#202b3c')
 d.text((28,yy+48),'红/蓝：原画比例骨架投影；橙：手；绿：瓜/承重接触；紫：拇指/眼态。灰底仅旧锚定位。',font=f22,fill='#495464')
 d.text((28,yy+82),'S*/E* 为遮挡下估计；固定3D构造310/240px ≠ 实测骨长。全部旧PNG保持原字节。',font=f22,fill='#495464')
 d.text((28,yy+116),f"眼态：{k['expression']['eyelids']}   |   仅供Opus冻结参考，非可接景成片；新画中性底色，场景光一次。",font=f22,fill='#495464')
 return out
images={}
for k in STATES:
 img=diagram(k);f=k['frame'];name=f"S03_{k['id']}_f{f:03d}.jpg";img.save(ROOT/'all20'/name,quality=94);images[f]=img
 if f not in old:img.save(ROOT/'new13'/name,quality=94)
# Overview with readable notes outside each thumbnail.
tw,th=418,320;overview=Image.new('RGB',(tw*4,th*5+115),'#e8ecf1');d=ImageDraw.Draw(overview)
d.text((24,14),'S03 · 20态 / 96帧 · 骨架与接触冻结提案',font=f40,fill='#202b3c')
d.text((24,66),'7旧锚只标注不改画；13新增按三段前后衔接。请先看F034→058接触近图。',font=f22,fill='#344153')
for i,k in enumerate(STATES):
 x=(i%4)*tw;y=(i//4)*th+115;overview.paste(images[k['frame']].resize((418,282)),(x,y));d.text((x+10,y+283),f"{k['id']} F{k['frame']:03d}  {'旧锚' if k['existing_frozen_anchor'] else '新态'}  停{k['hold']}帧",font=f22,fill=red if k['existing_frozen_anchor'] else '#202b3c')
overview.save(ROOT/'S03_overview_20.jpg',quality=95)
# Detailed contact sheets: fixed native coordinate windows, no per-panel scaling tricks.
def contact_sheet(frames,name,title,sub,box=(260,630,800,941),cols=3):
 cw,ch=720,540;rows=math.ceil(len(frames)/cols);im=Image.new('RGB',(cw*cols,ch*rows+135),'white');dr=ImageDraw.Draw(im)
 dr.text((22,14),title,font=f40,fill='#202b3c');dr.text((22,70),sub,font=f22,fill='#465363')
 for i,f in enumerate(frames):
  k=next(k for k in STATES if k['frame']==f);x=(i%cols)*cw;y=(i//cols)*ch+135
  # Use a focused overlay and a common crop to preserve actual scale.
  pic=images[f].crop(box);scale=min((cw-16)/pic.width,(ch-125)/pic.height);pic=pic.resize((round(pic.width*scale),round(pic.height*scale)))
  im.paste(pic,(x+8,y+8));dr.text((x+12,y+ch-110),f"F{f:03d}  {'冻结原锚' if f in old else '新增提案'}",font=f32,fill='#202b3c')
  detail={34:'张指放荚；瓜仍在盘上',37:'腕向左下走；未碰瓜',40:'初触左侧瓜皮；腕留在画内',44:'侧抓：拇指在前，手指绕皮',48:'先离盘，再从侧抓转托',52:'下沿已承重；手瓜一起送',55:'托持不变；向终点缓出',58:'原k06：掌托下皮、拇指在后'}[f]
  dr.text((x+12,y+ch-66),detail,font=f26,fill='#465363')
 im.save(ROOT/'contact'/name,quality=96)
contact_sheet([34,37,40,44],'S03_release_reach_contact.jpg','F034 → F044 · 放荚、探手、初触、抓瓜','统一裁窗/统一比例；F040接触左皮，禁止照代码把腕画出幅。',box=(270,620,800,941),cols=4)
contact_sheet([44,48,52,55,58],'S03_grasp_to_support_contact.jpg','F044 → F058 · 抓转托与连续承重','同一瓜模板，不把瓜挂在腕边；橙掌/绿承重点/紫拇指。旧盘位冲突必须显式冻结。',box=(165,620,560,941),cols=5)
# Clean technical contact diagrams: larger markers and labels, no faint source hand confusing the new pose.
cw,ch=620,660;clean=Image.new('RGB',(cw*5,ch+110),'white');dc=ImageDraw.Draw(clean);dc.text((22,12),'抓 → 转掌 → 托递 · 手与瓜接触节点（诊断线稿，不是绘画）',font=f40,fill='#202b3c');dc.text((22,66),'同倍率；橙掌心、绿承重点、紫拇指；紫虚线只是连接关系。F048橙虚线段在瓜后，不穿过果肉。',font=f22,fill='#465363')
for i,f in enumerate([44,48,52,55,58]):
 k=copy.deepcopy(next(k for k in STATES if k['frame']==f));base=Image.new('RGB',(W,H),'#f7f8fa');dd=ImageDraw.Draw(base);melon(dd,k['landmarks_xy']['fruit']);draw_hand(dd,k,detail=True)
 crop=base.crop((170,620,560,941)).resize((600,494));clean.paste(crop,(i*cw+10,110));dc.text((i*cw+20,615),f'F{f:03d}  '+('旧锚' if f in old else '新态'),font=f32,fill='#202b3c');dc.text((i*cw+20,666),{44:'侧抓；前拇指 / 后掌',48:'腕掌过渡藏于瓜后；掌移到下沿',52:'托皮承重；拇指转到后侧',55:'掌托 / 前指 / 后拇指',58:'以旧k06实际接触为终点'}[f],font=f22,fill='#465363')
clean.save(ROOT/'contact/S03_contact_nodes_clean.jpg',quality=96)
# Blink close-ups drawn cleanly, with no old-open-eye pixels behind full closure.
blink=Image.new('RGB',(1600,520),'#f7f8fa');db=ImageDraw.Draw(blink);db.text((22,15),'F065 → F074 → F075 → F076 · 手瓜与身体锁定，仅表情变化',font=f32,fill='#202b3c')
for i,f in enumerate([65,74,75,76]):
 x=45+i*395;y=225;k=next(k for k in STATES if k['frame']==f);op=k['expression']['eye_open_fraction'];db.text((x,75),f'F{f:03d}  '+('抬眉等待' if f==65 else '半闭' if op else '全闭'),font=f32,fill='#202b3c')
 for xx in [x+85,x+235]:
  db.ellipse((xx-61,y-55,xx+61,y+60),outline='#596477',width=4)
  if op:
   hh=29*op;db.ellipse((xx-37,y-hh,xx+37,y+hh),outline=purple,width=4);db.ellipse((xx-20,y-hh+2,xx+1,y+hh-2),fill=purple)
  else:line(db,bez((xx-37,y),(xx-17,y+6),(xx+17,y+6),(xx+37,y)),purple,5)
  line(db,[(xx-36,y-80),(xx-5,y-88),(xx+32,y-80)],purple,5)
 db.text((x,350),'开度 '+str(op),font=f26,fill=purple)
 db.text((x,397),'无身体/手瓜位移',font=f26,fill='#465363')
 if op==0:db.text((x,440),'不可留瞳孔或眼白',font=f26,fill=red)
blink.save(ROOT/'contact/S03_blink_74_75_76.jpg',quality=96)
# Math, exposure, preservation and contact checks.
errors=[]
for k in STATES:
 for side in ['screen_left','screen_right']:
  j=k['arm_construction_xyz'][side];s,e,w=[np.array(j[n]) for n in ['shoulder','elbow','wrist']];errors += [abs(np.linalg.norm(e-s)-L1),abs(np.linalg.norm(w-e)-L2)]
checks={'frames':sum(holds),'all20_count':len(list((ROOT/'all20').glob('*.jpg'))),'new13_count':len(list((ROOT/'new13').glob('*.jpg'))),'new13_exposure_frames':sum(k['hold'] for k in STATES if not k['existing_frozen_anchor']),'source_png_hashes_unchanged':all(hashlib.sha256(files[int(m['anchor'][1:])].read_bytes()).hexdigest()==m['sha256'] for m in manifest),'new_image_generation_calls':0,'max_fixed_bone_length_error_px':max(errors),'F040_wrist_inside_canvas':all(0<=x<lim for x,lim in zip(P[40]['screen_left_wrist'],[W,H])),'F074_F075_F076_eye_open':[.5,0,.5],'late_body_hand_fruit_coordinate_lock':all(P[f]==P[65] for f in [74,75,76]),'plate_present_all20':True,'legacy_plate_jump_resolved':False,'legacy_lighting_bridge_frozen':False,'status':'Reference proposal complete; production and legacy exceptions await Opus freeze.'}
assert checks['frames']==96 and checks['new13_count']==13 and checks['all20_count']==20 and checks['new13_exposure_frames']==48 and max(errors)<1e-8
(ROOT/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(checks,ensure_ascii=False,indent=2))
