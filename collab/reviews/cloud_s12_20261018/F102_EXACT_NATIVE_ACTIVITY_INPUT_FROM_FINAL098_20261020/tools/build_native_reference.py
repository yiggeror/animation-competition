"""Actual locked098 source groups only; not102 artwork or a code person.
Exact rigid palms/bangle; small source-material wrist transitions, no skin flags.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json
from scipy.ndimage import map_coordinates,binary_dilation,binary_erosion,binary_fill_holes,label
O=Path(__file__).resolve().parents[1];R=O.parent;M=R/'F098_EXACT_NATIVE_ACTIVITY_actual_call01_20261020';P=R/'F098_EXACT_NATIVE_ACTIVITY_INPUT_FROM_FINAL094_20261020'
g=json.loads((O/'geometry/F102_NATIVE_ACTIVITY_AND_TRUE_PROP_PLAN.json').read_text());src=Image.open(M/'candidate/F098.png').convert('RGBA');B=np.array(src);Y,X=np.mgrid[:1536,:1024]
def poly(points):
 m=Image.new('L',src.size);ImageDraw.Draw(m).polygon(points,fill=255);return np.array(m)>0
def part(mask):
 q=B.copy();q[~mask]=0;return Image.fromarray(q)
def warp(im,m,res=Image.Resampling.BICUBIC):
 inv=np.linalg.inv(np.vstack([np.array(m),[0,0,1]]))[:2];return im.transform(src.size,Image.Transform.AFFINE,tuple(inv.ravel()),res)
def smooth(t):
 t=np.clip(t,0,1);return t*t*(3-2*t)
def sample_rgba(source,sx,sy):
 q=source.astype(float);aa=q[:,:,3]/255;prem=q[:,:,:3]*aa[:,:,None];a=np.clip(map_coordinates(aa,[sy,sx],order=1,mode='constant'),0,1)
 rgb=np.stack([map_coordinates(prem[:,:,c],[sy,sx],order=1,mode='constant') for c in range(3)],axis=2);rgb=np.divide(rgb,a[:,:,None],out=np.zeros_like(rgb),where=a[:,:,None]>0)
 out=np.dstack([np.clip(np.rint(rgb),0,255),np.rint(a*255)]).astype(np.uint8);out[out[:,:,3]==0]=0;return out
def joined_forearm(mask,a):
 # A small distal source-material transition joins wrist tissue to the whole
 # rigid hand. It never moves the hand/bangle or independently moves fingers.
 F=np.array(a['forearm_rigid_matrix']);H=np.array(a['whole_hand_bangle_same_rod_angle_matrix']);e=np.array(a['source_final098']['elbow']);w=np.array(a['source_final098']['wrist']);uv=(w-e)/np.linalg.norm(w-e);length=np.linalg.norm(w-e)
 yy,xx=np.where(mask&(B[:,:,3]>0));corn=np.array([[xx.min(),yy.min(),1],[xx.max(),yy.min(),1],[xx.min(),yy.max(),1],[xx.max(),yy.max(),1]]);dest=np.r_[corn@F.T,corn@H.T];x0=max(0,int(np.floor(dest[:,0].min()))-4);x1=min(1024,int(np.ceil(dest[:,0].max()))+5);y0=max(0,int(np.floor(dest[:,1].min()))-4);y1=min(1536,int(np.ceil(dest[:,1].max()))+5)
 ty,tx=np.mgrid[y0:y1,x0:x1];inv=np.linalg.inv(np.vstack([F,[0,0,1]]))[:2];sx=inv[0,0]*tx+inv[0,1]*ty+inv[0,2];sy=inv[1,0]*tx+inv[1,1]*ty+inv[1,2]
 for _ in range(12):
  weight=smooth((((sx-e[0])*uv[0]+(sy-e[1])*uv[1])-(length-90))/50)
  aa=F[0,0]+weight*(H[0,0]-F[0,0]);bb=F[0,1]+weight*(H[0,1]-F[0,1]);cc=F[1,0]+weight*(H[1,0]-F[1,0]);dd=F[1,1]+weight*(H[1,1]-F[1,1]);px=tx-(F[0,2]+weight*(H[0,2]-F[0,2]));py=ty-(F[1,2]+weight*(H[1,2]-F[1,2]));det=aa*dd-bb*cc;sx=(dd*px-bb*py)/det;sy=(-cc*px+aa*py)/det
 out=np.zeros_like(B);out[y0:y1,x0:x1]=sample_rgba(np.array(part(mask)),sx,sy);return Image.fromarray(out)
fixed=np.array(Image.open(P/'masks/HARD_QUALIFIED_FINAL094_SHINS_SHOES_AIR.png').convert('L'))>0;fixed|=Y>=1320
UT=g['whole_torso_head_rigid_matrix'];TH=g['thigh_rigid_matrix']
shirt=poly([(330,0),(780,0),(780,365),(725,400),(715,430),(731,472),(739,503),(733,537),(720,559),(702,578),(679,606),(662,641),(649,661),(649,700),(669,756),(687,814),(713,869),(725,903),(707,916),(687,893),(641,875),(589,851),(545,830),(515,816),(509,774),(484,802),(458,791),(427,780),(383,754),(413,706),(450,662),(475,623),(484,592),(470,555),(459,513),(461,463),(474,415),(491,365),(503,320),(380,350)])
Rmask=poly([(485,394),(544,394),(593,414),(611,445),(615,493),(616,539),(608,557),(619,590),(638,637),(656,654),(708,686),(772,729),(810,752),(840,756),(870,756),(886,748),(891,738),(908,726),(921,736),(927,749),(927,769),(920,790),(905,802),(879,816),(845,820),(807,813),(764,797),(715,769),(667,743),(621,712),(590,694),(573,670),(554,633),(532,589),(513,579),(489,582),(469,553),(459,518),(463,463),(474,421)])
Rbare=poly([(532,568),(609,557),(620,596),(635,636),(655,654),(706,687),(765,725),(811,752),(841,756),(871,755),(885,748),(891,737),(908,726),(921,735),(927,748),(927,769),(920,790),(905,802),(877,816),(845,820),(808,812),(764,797),(716,769),(667,743),(622,713),(590,693),(572,668),(554,632)])
Lmask=poly([(649,646),(650,625),(665,595),(690,568),(715,548),(737,535),(738,513),(744,498),(757,487),(771,486),(783,494),(790,506),(804,509),(839,511),(864,516),(877,530),(883,548),(882,573),(873,590),(859,602),(841,597),(827,588),(810,578),(795,566),(781,557),(770,558),(756,553),(740,563),(718,590),(693,618),(675,641),(667,650)])
torso=shirt&~Rbare&~(Lmask&(Y>535))&~fixed
far_shin_fold=(X<400)&(Y>=1075)
pants=(Y>735)&(X<760)&~binary_erosion(shirt,iterations=3)&~Rmask&~Lmask&~fixed&~far_shin_fold
out=Image.new('RGBA',src.size)
# Same already rounded actual knees; only the real upper cloth transitions.
t1=smooth((np.arange(1536)-880)/80);t2=smooth((np.arange(1536)-1125)/65);I=np.array([[1.,0.,0.],[0.,1.,0.]])
mat=(1-t1[:,None,None])*np.array(UT)+t1[:,None,None]*np.array(TH);mat=(1-t2[:,None,None])*mat+t2[:,None,None]*I;ms=np.concatenate([mat,np.tile([[[0.,0.,1.]]],(1536,1,1))],axis=1);inv=np.linalg.inv(ms)[:,:2];sx=inv[:,0,0,None]*X+inv[:,0,1,None]*Y+inv[:,0,2,None];sy=inv[:,1,0,None]*X+inv[:,1,1,None]*Y+inv[:,1,2,None]
pa=sample_rgba(np.array(part(pants)),sx,sy)
# Preserve the real far rounded knee along its actual curved fold, rather than
# putting a rectangular original-source plate over the moving thigh.
fold=np.interp(X,[0,240,320,390,440,475,510,550,580,610,640,1023],[1090,1090,1100,1080,1058,1068,1095,1140,1190,1250,1320,1400])
fw=smooth((Y-fold+18)/36)*(X<640)
aa=pa[:,:,3]/255.;bb=B[:,:,3]/255.;mixalpha=aa*(1-fw)+bb*fw
prem=pa[:,:,:3]*aa[:,:,None]*(1-fw[:,:,None])+B[:,:,:3]*bb[:,:,None]*fw[:,:,None]
rgb=np.divide(prem,mixalpha[:,:,None],out=np.zeros_like(prem),where=mixalpha[:,:,None]>0)
pa=np.dstack([np.clip(np.rint(rgb),0,255),np.rint(mixalpha*255)]).astype(np.uint8)
out.alpha_composite(Image.fromarray(pa));out.alpha_composite(part(far_shin_fold&~fixed));out.alpha_composite(part((Y>=1190)&~fixed));out.alpha_composite(warp(part(torso),UT))
pieces={};blocks={}
for role,mask in [('L',Lmask),('R',Rmask)]:
 a=g['arms'][role];e=np.array(a['source_final098']['elbow']);w=np.array(a['source_final098']['wrist']);v=w-e;along=((X-e[0])*v[0]+(Y-e[1])*v[1])/np.linalg.norm(v)
 if role=='R':hand=mask&(X>=848)&(Y>=720)&(Y<=830)
 else:
  jade=poly([(749,555),(738,542),(733,525),(738,505),(750,490),(766,484),(780,488),(789,497),(793,512),(788,533),(778,551),(763,561)])
  hand=mask&(jade|((X>=775)&(Y>=490)&(Y<=615)))
 cross=((X-e[0])*(-v[1])+(Y-e[1])*v[0])/np.linalg.norm(v)
 upper=mask&~hand&(along<30);fore=mask&~hand&(along>-34)&(np.abs(cross)<(45 if role=='R' else 40))
 pieces[role+'_upper']=warp(part(upper),a['upper_rigid_matrix']);pieces[role+'_forearm']=joined_forearm(fore,a);pieces[role+'_whole_hand']=warp(part(hand),a['whole_hand_bangle_same_rod_angle_matrix'])
 if role=='R':
  near_upper_donor_mask=upper&((along<=0)|(((X-e[0])**2+(Y-e[1])**2)<=30**2));near_fore_donor_mask=fore
 blocks[role]={'independent_source_masks_before_motion':True,'source_hand_semantic_mask_pixels':int(np.count_nonzero(hand&(B[:,:,3]>0))),'upper_source_pixels':int(np.count_nonzero(upper&(B[:,:,3]>0))),'forearm_source_pixels':int(np.count_nonzero(fore&(B[:,:,3]>0))),'small_distal_wrist_transition':'actual source skin coordinates only, forearm matrix to whole-hand matrix over50px ending40px before proxy wrist; no new flat skin guide','no_finger_warp':True}
 for name in ['upper','forearm','whole_hand']:pieces[role+'_'+name].save(O/f'anatomy/{role}_{name}_FINAL098_SOURCE_REFERENCE.png')
# The previously hidden far upper arm cannot be represented by a forearm stub.
# For this INPUT reference only, reuse the same mother's complete near upper-arm
# source shape at the measured far chain's length and direction. This is real
# drawing material, not a synthetic blue/skin tube, and is NOT production art.
sr=np.array(g['arms']['R']['source_final098']['shoulder']);er=np.array(g['arms']['R']['source_final098']['elbow']);sl=np.array(g['arms']['L']['target']['shoulder']);el=np.array(g['arms']['L']['target']['elbow']);v0=er-sr;v1=el-sl
angle=np.arctan2(v1[1],v1[0])-np.arctan2(v0[1],v0[0]);scale=np.linalg.norm(v1)/np.linalg.norm(v0);rr=scale*np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]]);donor_matrix=np.c_[rr,sl-rr@sr]
donor=warp(part(near_upper_donor_mask),donor_matrix);donor.save(O/'anatomy/FAR_UPPER_COMPLETE_SOURCE_DONOR_REFERENCE_ONLY.png');out.alpha_composite(donor)
# The far source forearm was partly occluded in098. Give its newly exposed
# silhouette a COMPLETE real-art forearm reference from the same mother,
# at its measured far projected length, with cross-section preserved at0.90.
# The far palm/bangle is its OWN original source and stays exactly rigid.
wr=np.array(g['arms']['R']['source_final098']['wrist']);wl=np.array(g['arms']['L']['target']['wrist']);ur=(wr-er)/np.linalg.norm(wr-er);ul=(wl-el)/np.linalg.norm(wl-el);nr=np.array([-ur[1],ur[0]]);nl=np.array([-ul[1],ul[0]]);axial=np.linalg.norm(wl-el)/np.linalg.norm(wr-er);rf=axial*np.outer(ul,ur)+.9*np.outer(nl,nr);fore_donor_matrix=np.c_[rf,el-rf@er]
pieces['L_forearm']=warp(part(near_fore_donor_mask),fore_donor_matrix);pieces['L_forearm'].save(O/'anatomy/FAR_FOREARM_COMPLETE_SOURCE_DONOR_REFERENCE_ONLY.png')
pieces['L_upper']=Image.new('RGBA',src.size) # old occlusion-cut stub is not a target arm.
for role in ['L','R']:
 for name in ['upper','forearm','whole_hand']:out.alpha_composite(pieces[role+'_'+name])
# Actual blue flower cloth fills only the small newly exposed rib underlap.
oa=np.array(out);corridor=poly([(586,530),(645,530),(677,570),(677,650),(645,673),(590,628)]);expected_torso=np.array(warp(part(shirt&~fixed),UT))[:,:,3]>0;gap=binary_dilation((oa[:,:,3]<128)&corridor,iterations=3)&corridor&expected_torso
clothbase=Image.new('RGBA',src.size)
for dx in [100,120]:clothbase.alpha_composite(warp(part((X>=488)&(X<=552)&(Y>=650)&(Y<=770)),[[1,0,dx],[0,1,-110]]))
cloth=np.array(clothbase);cloth[~gap]=0;under=Image.fromarray(cloth);under.alpha_composite(out);out=under;Image.fromarray(cloth).save(O/'anatomy/SMALL_RIB_ACTUAL_FLOWER_CLOTH_UNDERLAP.png')
n=np.array(out)
# A tiny displaced old fold edge outside the QUALIFIED current far-knee
# silhouette is not an anatomical guide. Remove that competing reference-only
# sliver; the actual good native round knee beneath remains the source.
sliver=(X<435)&(Y>1030)&(Y<1100)&(B[:,:,3]==0);n[sliver]=0
n[fixed]=B[fixed];activity=binary_dilation((B[:,:,3]>0)|(n[:,:,3]>0),iterations=10)&~fixed;protected=~activity;n[protected]=B[protected]
Image.fromarray(n).save(O/'anatomy/F102_NATIVE_SOURCE_GROUP_REFERENCE_ONLY.png')
for name,mask in [('ALLOW_MINIMAL_NATIVE_ACTIVITY',activity),('HARD_PROTECTED_NATIVE_SUPPORT_AND_OUTSIDE',protected),('HARD_QUALIFIED_FINAL098_SHINS_SHOES_AIR',fixed)]:Image.fromarray(np.uint8(mask)*255).save(O/f'masks/{name}.png')
F=np.array(Image.open(M/'layers/F098_FG_true_front_fingers.png').convert('RGBA'));own=np.zeros((1536,1024),bool)
for role in ['L','R']:
 z=F.copy();z[Y>=680 if role=='L' else Y<680]=0;own|=np.array(warp(Image.fromarray(z),g['arms'][role]['whole_hand_bangle_same_rod_angle_matrix']))[:,:,3]>0
fg=np.zeros_like(n);fg[own]=n[own];bg=n.copy();bg[own]=0;Image.fromarray(bg).save(O/'anatomy/F102_REFERENCE_BG.png');Image.fromarray(fg).save(O/'anatomy/F102_REFERENCE_FG_REAL_FRONT_FINGERS.png')
assert not np.any((fg[:,:,3]>0)&(bg[:,:,3]>0));assert np.array_equal(np.maximum(bg,fg),n);assert np.array_equal(n[protected],B[protected]);assert np.array_equal(n[fixed],B[fixed])
plate=Image.new('RGBA',src.size,'#e1e4e6');plate.alpha_composite(Image.fromarray(n));d=ImageDraw.Draw(plate);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
for y,txt in [(18,'F102 / EXACT NATIVE ACTIVITY / BOTH COMPLETE ARM CHAINS'),(45,'FROM LOCKED098 / INPUT REFERENCE ONLY'),(1370,'Hip advances; waist, chest, shoulders and whole head stand up.'),(1400,'Both palms keep true rigid shafts. Far LEFT jade / near RIGHT bare.'),(1430,'Keep good round knees and planted shins / ankles / shoes.'),(1460,'Small natural joint joins only. No flags, boards or new framing.')]:d.text((18,y),txt,font=font,fill='#25313b')
plate.convert('RGB').save(O/'inputs/01_F102_EXACT_NATIVE_ACTIVITY_TARGET.png')
holes=binary_fill_holes(n[:,:,3]>128)&(n[:,:,3]<32)&activity;lab,c=label(holes);regions=[]
for i in range(1,c+1):
 yy,xx=np.where(lab==i)
 if len(xx)>8:regions.append({'pixels':len(xx),'bbox':[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())]})
qa={'status':'ACTUAL_SOURCE_REFERENCE_REQUIRES_VISIBLE_CHAIN_READBACK','source_final098_rebound':True,'old102_person_target_reused':False,'new102_imagegen_calls':0,'new106_imagegen_calls':0,'actual102_person_Canvas':0,'protected_native_RGBA_differences':0,'qualified_support_RGBA_differences':0,'reference_BG_FG_RGBA_reconstruction_differences':0,'reference_BG_FG_overlap':0,'whole_person_mesh_or_TPS':False,'new_knee_or_waist_plates':False,'technical_skin_guide_pixels':0,'source_group_details':blocks,'newly_revealed_far_upper_arm_reference':{'donor':'same locked098 complete near upper sleeve and upper-arm source shape; input reference only; no production adoption','single_similarity_to_far_proxy_chain':donor_matrix.tolist(),'projected_scale':float(scale),'full_upper_length_preserved_at_measured_far_proxy_length':True},'newly_revealed_far_forearm_reference':{'donor':'same locked098 complete near forearm real-art source; replaces old far occlusion-cut stump ONLY in input reference. Far own hand and complete jade remain original rigid groups.','matrix':fore_donor_matrix.tolist(),'axial_projected_length_scale':float(axial),'cross_section_scale':.9,'no_finger_transform':True},'small_rib_underlap':'same-mother real blue flower cloth, source x488..552/y650..770 translations(+100,-110)/(+120,-110), clipped to the actual expected torso silhouette and newly revealed rib corridor only','internal_low_alpha_regions_for_actual_review':regions,'pants_reference_only_transition':'real098 hip/thigh/knee source cloth; hip/thigh y880-960, near knee folds transition y1125-1190, good far round knee retained along its actual curved fold with36px source-material blend (no rectangular plate). Qualified shins exact throughout; no new navy shape.','allowed_pixels':int(activity.sum())}
(O/'qa/NATIVE_SOURCE_REFERENCE_READBACK.json').write_text(json.dumps(qa,indent=2)+'\n');print(json.dumps(qa,indent=2))
