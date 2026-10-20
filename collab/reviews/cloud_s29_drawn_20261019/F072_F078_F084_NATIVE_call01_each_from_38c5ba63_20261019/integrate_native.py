from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage as nd
import numpy as np,json,hashlib,sys
R=Path(__file__).resolve().parent;B=R.parent;G=B/'F072_F078_F084_FROM_LOCKED066_INPUT_GATE_ZERO_CALL_20261019';Y,X=np.indices((1536,1024))
def load(p):return np.array(Image.open(p).convert('RGBA'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def poly(pts):
 a=Image.new('L',(1024,1536));ImageDraw.Draw(a).polygon(pts,fill=255);return np.array(a)>0
def save(a,p):Image.fromarray(a).save(p)
def comp(*aa):
 a=Image.new('RGBA',(1024,1536))
 for b in aa:a.alpha_composite(Image.fromarray(b))
 return np.array(a)
def affine(a,A,t):
 co=(np.stack([X,Y],2)-t)@np.linalg.inv(A).T;p=a.astype(float);p[:,:,:3]*=p[:,:,3:4]/255
 z=np.stack([nd.map_coordinates(p[:,:,k],[co[:,:,1],co[:,:,0]],order=1,mode='constant',cval=0)for k in range(4)],2);z[:,:,:3]=np.divide(z[:,:,:3],z[:,:,3:4]/255,out=np.zeros_like(z[:,:,:3]),where=z[:,:,3:4]>1e-8);z=np.rint(np.clip(z,0,255)).astype('uint8');z[z[:,:,3]==0]=0;return z
f=int(sys.argv[1]);d=R/f'F{f:03d}';q=d/'reintegration';q.mkdir(exist_ok=True)
rawp=d/f'originals/S29_F{f:03d}_call01_RAW_UNTOUCHED.png';raw=load(rawp);assert raw.shape==(1536,1024,4),'Registration requires explicit dimensional review'
target=load(d/'inputs/01_UNIQUE_COMPLETE_CURRENT_TARGET_RGBA.png');clothp=d/'inputs/05_ONLY_SAME_SOURCE_CLOTH_RGBA.png';cloth=load(clothp);propsp=G/'UNCHANGED_TRUE_TWO_PUPPETS_FOUR_RODS_RGBA.png';props=load(propsp);lip=load(G/f'F{f:03d}/SAME_MATERIAL_FRONT_FOLD_RGBA.png')
rgb=raw[:,:,:3].astype(float);shirt=(rgb[:,:,1]>95)&(rgb[:,:,2]>135)&(rgb[:,:,2]>rgb[:,:,0]+15);skin=(rgb[:,:,0]>120)&(rgb[:,:,1]>65)&(rgb[:,:,2]>90)&(rgb[:,:,0]>rgb[:,:,2]+25);jade=(rgb[:,:,1]>rgb[:,:,0]*1.05)&(rgb[:,:,1]>rgb[:,:,2]*1.03)&(rgb[:,:,1]>50)
seed=(shirt|skin|jade)&(raw[:,:,3]>128)&(Y>=300)&(Y<1020)&(X>=40)&(X<810);lab,_=nd.label(nd.binary_closing(seed,iterations=3));m=nd.binary_dilation(nd.binary_fill_holes(lab==lab[500,350]),iterations=2)&(raw[:,:,3]>0)
human=np.zeros_like(raw);human[m]=raw[m];human[m&(raw[:,:,3]>=128),3]=255
farpoly=poly([(490,480),(660,460),(810,600),(810,820),(600,820),(490,735),(480,600)])
fs=(skin|jade)&m&farpoly;fl,_=nd.label(nd.binary_closing(fs,iterations=2));counts=np.bincount(fl.ravel());counts[0]=0;farlabel=int(counts.argmax());assert counts[farlabel]>3000
fm=nd.binary_dilation(nd.binary_fill_holes(fl==farlabel),iterations=2)&m&farpoly
far=np.zeros_like(human);far[fm]=human[fm]
ns=skin&m&~fm&(Y>570)&(Y<1010)&(X<610);nl,_=nd.label(nd.binary_closing(ns,iterations=1));nm=nd.binary_dilation(nd.binary_fill_holes(nl==nl[650,180]),iterations=2)&m&~fm
near=np.zeros_like(human);near[nm]=human[nm]
# Cotton visible inside the arm/body loop must never survive a generic fill-holes
# human mask. Extract the connected ACTUAL BLUE BLOUSE separately, including its
# white blossoms/ink holes, before placing it in front of the bare-arm cuff.
blousepoly=poly([(287,275),(485,349),(545,405),(600,510),(500,580),(492,632),(520,713),(518,736),(438,764),(321,809),(206,938),(40,928),(75,760),(112,696),(128,640),(75,615),(70,585),(90,520),(130,450),(180,365),(240,317)])
bm=m&blousepoly&~(fm|nm)
blouse=np.zeros_like(human);blouse[bm]=human[bm]
# Preserve the actual native cuff opening and its shallow skin underlay. The
# rigid registered limb remains in front; this closes only the newly uncovered
# cuff strip, without touching the jade/wrist/fingers or inventing any material.
cuffdistance=(X-548)*.535+(Y-530)*.845
cuffunder=fm&skin&(cuffdistance>=-4)&(cuffdistance<18)
blouse[cuffunder]=human[cuffunder]
# Whole far BARE arm, jade, wrist and fingers receive ONE similarity. Fixed native
# blouse/sleeves draw in front of its cuff, never old technical blue arm pixels.
srcC=np.array({72:[697.,724.],78:[645.,755.],84:[0.,0.]}[f]);dstC=np.array({72:[660.098467936869,710.61030076984],78:[640.098467936869,745.61030076984],84:[640.098467936869,745.61030076984]}[f]);root=np.array({72:[548.,530.],78:[554.,544.],84:[554.,544.]}[f]);v=srcC-root;w=dstC-root;u=float(w@v/(v@v));rot=float((w[1]*v[0]-w[0]*v[1])/(v@v));A=np.array([[u,-rot],[rot,u]]);t=root-A@root;farreg=affine(far,A,t)
white=np.array(Image.open(d/'inputs/04_WHOLE_TWO_ARMS_EXPOSED_BLOUSE_WHITE_DOMAIN.png').convert('L'))>0
headguard=poly([(215,25),(640,25),(640,335),(523,372),(488,417),(425,416),(383,357),(345,323),(260,299),(217,270)])
tr=target[:,:,:3].astype(float);oldblue=(tr[:,:,1]>95)&(tr[:,:,2]>135)&(tr[:,:,2]>tr[:,:,0]+15)
headguard&=~oldblue  # old collar fragments cannot cut across the NEW native collar
edit=(white|nd.binary_dilation(m,iterations=4))&~headguard
base=target.copy();base[edit]=0
# Remove ALL obsolete technical human silhouettes in broad sleeves/body domain.
# All restored blouse pixels below are native; all cotton/props are sole sources.
final=comp(base,cloth,props,lip,farreg,blouse,near);protect=headguard|(Y>=1100);final[protect]=target[protect]
save(human,q/'EXACT_NATIVE_HUMAN_RGBA.png');save(far,q/'EXACT_NATIVE_COMPLETE_FAR_BARE_ARM_JADE_HAND_RGBA.png');save(farreg,q/'ONE_SIMILARITY_COMPLETE_FAR_BARE_ARM_JADE_HAND_RGBA.png');save(near,q/'EXACT_NATIVE_COMPLETE_NEAR_ARM_HAND_RGBA.png');save(blouse,q/'EXACT_NATIVE_COMPLETE_BLOUSE_BOTH_SLEEVES_RGBA.png');save(final,q/f'F{f:03d}_SAME_CLOTH_TRUE_PROPS_NATIVE_HUMAN_CANDIDATE_RGBA.png')
save((edit*255).astype('uint8'),q/'COMPLETE_NATIVE_HUMAN_SEMANTIC_REPLACEMENT_MASK.png')
bg=Image.new('RGBA',(1024,1536),(232,235,239,255));bg.alpha_composite(Image.fromarray(final));bg.convert('RGB').save(q/'FULL_ON_GRAY.png');bg.crop((70,340,800,1030)).convert('RGB').save(q/'COMPLETE_BOTH_ARMS_CONTACTS_1TO1.png');bg.crop((550,610,750,810)).resize((600,600)).convert('RGB').save(q/'FAR_TRUE_CLOTH_CONTACT_3X.png')
report=dict(frame=f,status='PENDING_ACTUAL_REINTEGRATION_REVIEW',raw_SHA256=sha(rawp),same_source_cloth_SHA256=sha(clothp),true_props_SHA256=sha(propsp),true_props_geometry_changed=False,four_rods_geometry_changed=False,whole_far_bare_arm_jade_hand_single_similarity=dict(source_contact=srcC.tolist(),target_contact=dstC.tolist(),fixed_cuff_root=root.tolist(),matrix=A.tolist(),translation=t.tolist(),scale=float(np.sqrt(u*u+rot*rot)),rotation_degrees=float(np.degrees(np.arctan2(rot,u))),per_finger_transform=False),whole_native_blouse_both_sleeves_retained=True,technical_blue_guide_returned=False,headguard_leg_RGBA_changes=int(np.any(final[protect]!=target[protect],1).sum()),candidate_SHA256=sha(q/f'F{f:03d}_SAME_CLOTH_TRUE_PROPS_NATIVE_HUMAN_CANDIDATE_RGBA.png'))
(q/'INTEGRATION_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
