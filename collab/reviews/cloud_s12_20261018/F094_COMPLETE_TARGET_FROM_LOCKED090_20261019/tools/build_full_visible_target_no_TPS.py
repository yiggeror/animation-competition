"""Unique094 full reference: explicit rigid body/thigh/arm/hand sections.
Opaque missing-joint volumes are reference-only. No TPS or new character art.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,math
O=Path(__file__).resolve().parents[1];R=O.parent;M=R/'F090_SAME_RAW_SEMANTIC_OWNERSHIP_FIXED_20261019';P=R/'F090_COMPLETE_TARGET_FROM_FINAL086_20261019'
assert not (O/'inputs/01_F094_UNIQUE_WHOLE_RISE_RETRACT_ROUND_KNEES.png').exists(),'Unique target already exists; inspect, no repeated body warps'
g=json.loads((O/'geometry/F094_COMPLETE_PERSON_AND_RIGID_PROP_PLAN.json').read_text());src=Image.open(M/'candidate/F090.png').convert('RGBA');B=np.asarray(src);Y,X=np.mgrid[:1536,:1024]
fixed=np.asarray(Image.open(P/'masks/REAL086_SHINS_ANKLES_SHOES_AND_BLANK_FIXED.png').convert('L'))>0
fixedmaster=np.zeros_like(B);fixedmaster[fixed]=B[fixed];Image.fromarray(fixedmaster).save(O/'anatomy/LOCKED090_FIXED_REAL_SUPPORT_MASTER.png')
def warp(im,m,res=Image.Resampling.BICUBIC):
 inv=np.linalg.inv(np.vstack([np.asarray(m),[0,0,1]]))[:2];return im.transform(src.size,Image.Transform.AFFINE,tuple(inv.ravel()),res)
def part(mask):
 q=np.zeros_like(B);q[mask]=B[mask];return Image.fromarray(q)
def pt(m,p):return np.asarray(m)@np.r_[p,1.]
UT=np.asarray(g['torso_head_rigid_matrix']);TH=np.asarray(g['thigh_rigid_matrix'])
rolemasks={r:np.asarray(Image.open(M/f'layers/{r}_WHOLE_REAL_ARM_EXACT_TRANSLATION.png').convert('RGBA'))[:,:,3]>0 for r in ['R','L']}
collar=np.asarray(Image.open(M/'geometry/ONE_WHOLE_ORIGINAL_COLLAR_AND_CENTRAL_CHEST.png').convert('L'))>0
arms=rolemasks['R']|rolemasks['L'];remove=arms&~collar
front=np.interp(Y,[0,520,580,640,710,800,880,1535],[1024,700,680,630,600,630,660,1024])
remove|=(Y>520)&(Y<880)&(X>front) # Clear the entire old competing appendage footprint, not only cached arm alpha.

hem=np.interp(X,[0,250,300,360,420,480,540,600,660,1023],[800,800,810,830,850,875,905,930,955,960])
shirt=Image.new('L',src.size);ImageDraw.Draw(shirt).polygon([(250,0),(850,0),(850,700),(700,700),(610,735),(612,796),(638,859),(659,910),(660,945),(620,934),(570,909),(520,888),(470,863),(431,837),(404,837),(375,831),(350,819),(300,802),(326,754),(359,700),(395,655),(418,590),(428,480),(438,410),(450,350),(250,350)],fill=255)
torso=(np.asarray(shirt)>0)&~remove&~fixed;thigh=(Y>hem+16)&~fixed # Do not duplicate the old shirt hem inside the independently rotating thigh reference.

out=Image.new('RGBA',src.size)
# Both complete moving knee faces, natural upper-shin folded connection and
# grounded round contact are explicit new-drawing activity, not old flat ink.
# A complete opaque technical thigh/knee envelope replaces construction gaps;
# actual source pants retain their shading inside it. It is not production art.
outline=np.array([(365,760),(445,770),(520,790),(610,830),(685,875),(700,1000),(719,1110),(722,1218),(706,1278),(675,1305),(616,1316),(575,1313),(525,1309),(485,1298),(430,1260),(392,1190),(360,1120),(330,1085),(350,1080),(390,1055),(415,1055),(408,1010),(398,950),(383,890),(385,830)],float)
smooth=[]
for i in range(len(outline)):
 p0,p1,p2,p3=[outline[j%len(outline)] for j in [i-1,i,i+1,i+2]]
 for t in np.linspace(0,1,16,endpoint=False):smooth.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
pm=Image.new('L',(4096,6144));ImageDraw.Draw(pm).polygon([tuple(4*q) for q in smooth],fill=255);pm=pm.resize(src.size,Image.Resampling.LANCZOS)
pants=Image.new('RGBA',src.size,(52,57,77,255));pants.putalpha(pm);pants.alpha_composite(warp(part(thigh),TH));pa=np.asarray(pants).copy();pa[:,:,3]=np.minimum(pa[:,:,3],np.asarray(pm));pa[pa[:,:,3]==0]=0;out.alpha_composite(Image.fromarray(pa))
core=np.asarray(Image.open(M/'geometry/CONTINUOUS_REAL_BODY_CORE_UNDER_NEW_SLEEVES.png').convert('L'))>0
tech=np.zeros_like(B);tech[core&(B[:,:,3]>0)]=[55,110,180,255]
out.alpha_composite(warp(Image.fromarray(tech),UT));out.alpha_composite(warp(part(torso),UT))
technical=Image.new('RGBA',src.size);td=ImageDraw.Draw(technical)
def volume(a,b,ra,rb,color):
 a=np.asarray(a);b=np.asarray(b);v=(b-a)/np.linalg.norm(b-a);n=np.array([-v[1],v[0]])
 td.polygon([tuple(a+ra*n),tuple(b+rb*n),tuple(b-rb*n),tuple(a-ra*n)],fill=color)
 for c,r in [(a,ra),(b,rb)]:td.ellipse((c[0]-r,c[1]-r,c[0]+r,c[1]+r),fill=color)
pieces={}
for role in ['L','R']:
 a=g['arms'][role];s,e,w,c=[np.asarray(a['source_actual090'][k]) for k in ['shoulder','elbow','wrist','true_grip']];st,et,wt,gt=[np.asarray(a['target'][k]) for k in ['shoulder','elbow','wrist','true_grip']]
 volume(st,et,46 if role=='R' else 39,38 if role=='R' else 33,(55,110,180,255));volume(et,wt,32,23,(214,143,92,255))
 v=w-e;along=((X-e[0])*v[0]+(Y-e[1])*v[1])/np.linalg.norm(v)
 hv=c-w;u=((X-w[0])*hv[0]+(Y-w[1])*hv[1])/np.dot(hv,hv);dist=np.abs((X-w[0])*hv[1]-(Y-w[1])*hv[0])/np.linalg.norm(hv)
 hand=rolemasks[role]&(u>=(-1.05 if role=='L' else -.5))&(dist<90) # Whole jade bangle and closed hand stay in one rigid group.
 upper=rolemasks[role]&~hand&(along<28);fore=rolemasks[role]&~hand&(along>-28)
 # Complete source blocks remain independent; no inverse mesh, no pre-move
 # left/right subtraction. Full hand/bangle follows the true rod-group angle.
 for name,mask,m in [('upper',upper,a['upper_rigid_matrix']),('forearm',fore,a['forearm_rigid_matrix']),('whole_hand',hand,a['whole_hand_bangle_same_rod_angle_matrix'])]:
  im=warp(part(mask),m);pieces[role+'_'+name]=im;im.save(O/f'anatomy/{role}_{name}_ACTUAL090_REFERENCE_BLOCK.png')
out.alpha_composite(technical)
for role in ['L','R']:
 for name in ['upper','forearm','whole_hand']:out.alpha_composite(pieces[role+'_'+name])
n=np.asarray(out).copy();n[fixed]=B[fixed];Image.fromarray(n).save(O/'anatomy/F094_COMPLETE_VISIBLE_REFERENCE_ONLY.png');assert np.array_equal(n[fixed],B[fixed])
fg0=np.asarray(Image.open(M/'layers/F090_FG_true_front_fingers.png').convert('RGBA'));own=np.zeros((1536,1024),bool)
for role in ['L','R']:
 z=fg0.copy();z[Y>=710 if role=='L' else Y<710]=0
 own|=np.asarray(warp(Image.fromarray(z),g['arms'][role]['whole_hand_bangle_same_rod_angle_matrix']))[:,:,3]>0
fg=np.zeros_like(n);fg[own]=n[own];bg=n.copy();bg[own]=0;Image.fromarray(bg).save(O/'anatomy/F094_REFERENCE_BG.png');Image.fromarray(fg).save(O/'anatomy/F094_REFERENCE_FG_TRUE_FRONT_DIGITS.png');assert np.array_equal(np.maximum(bg,fg),n)
for name,mask in [('LOCKED090_REAL_SHINS_ANKLES_SHOES_BLANK_FIXED',fixed),('F094_FULL_ACTIVITY_BODY_BOTH_ARMS_ENTIRE_KNEES_FOLDS',~fixed)]:Image.fromarray(np.uint8(mask)*255).save(O/f'masks/{name}.png')
plate=Image.new('RGBA',src.size,'#e1e4e6');plate.alpha_composite(Image.fromarray(n));dr=ImageDraw.Draw(plate);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
for y,txt in [(18,'F094 / UNIQUE FULL RISE + BOTH COMPLETE ARM RETRACTION'),(49,'SOLE LOCKED ACTUAL090 / REFERENCE ONLY / NO NEW ART'),(1375,'Hip + entire torso/head rise. True closed hands follow real rigid rods.'),(1410,'OPAQUE SHOULDER / ELBOW / WRIST / KNEE VOLUMES REQUIRE NEW INK'),(1442,'Fixed real shins / ankles / shoes / nearby blank remain native.')]:dr.text((18,y),txt,font=font,fill='#25313b')
plate.convert('RGB').save(O/'inputs/01_F094_UNIQUE_WHOLE_RISE_RETRACT_ROUND_KNEES.png')
(O/'qa/FIRST_TARGET_READBACK_PENDING.json').write_text(json.dumps({'status':'FIRST_FULL_TARGET_READY_FOR_ACTUAL_VISUAL_READBACK','whole_canvas_TPS':False,'complete_arm_technical_volumes_reference_only':True,'fixed_support_RGBA_changes':0,'new_imagegen':0,'actual094_full_Canvas':0,'source_pose_is_locked_final090':True},indent=2)+'\n')
print('Unique full094 reference01 ready. No imagegen, no whole-canvas TPS, original fixed supports0diff.')
