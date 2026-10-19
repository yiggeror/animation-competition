"""Zero-call technical drawing targets FROM the actual successful F030 raw.

Never output native art. Human segments are actual F030 pixels articulated as
a joint/contact probe. Native anatomy and cotton must be redrawn after review.
F030's whole raw is audit provenance only, never an extra request reference.
"""
from pathlib import Path
import sys,json,hashlib,math,shutil
sys.path.insert(0,'/tmp/s29-image-tools')
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont
from scipy import ndimage

R=Path(__file__).resolve().parent;B=R.parent
G=B/'F030_REPAIR_NATIVE_call01_20261019'
P=B/'REGISTER_REAL_PROPS_zero_call_v1_20261019'
M=B/'F030_REPAIR_FOUR_INPUTS_ZERO_CALL_v1_20261019'
for d in ('inputs','audit','layers','masks','geometry','requests','qa'):(R/d).mkdir(exist_ok=True)
rawpath=G/'originals/S29_F030_REPAIR_call01_RAW_UNTOUCHED.png'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(rawpath)=='0c182aa0d62acf8647daa316e06cdb4bfdd9ebd6c2e6c02f1b0e2f8065ffd4e5'
raw=Image.open(rawpath).convert('RGBA');a=np.array(raw);H,W=a.shape[:2];yy,xx=np.indices((H,W))
shutil.copyfile(rawpath,R/'audit/ACTUAL_SUCCESSFUL_F030_RAW_PROVENANCE_ONLY_NOT_INPUT.png')
def poly(points):
 m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon([tuple(x) for x in points],fill=255);return np.array(m)>0
def save_mask(name,m):Image.fromarray(m.astype('uint8')*255).save(R/f'masks/{name}.png')
def rgba(mask,pixels=a):
 out=np.zeros_like(a);out[mask]=pixels[mask];return Image.fromarray(out)
def rot(t):return np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]])
def warp(im,mat):
 v=np.array(im).astype('float32');v[:,:,:3]*=v[:,:,3:4]/255
 v=cv2.warpAffine(v,np.asarray(mat,dtype='float32'),(W,H),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_CONSTANT)
 v=np.clip(v,0,255);al=v[:,:,3:4]/255;v[:,:,:3]=np.divide(v[:,:,:3],al,out=np.zeros_like(v[:,:,:3]),where=al>1e-6)
 return Image.fromarray(np.clip(v,0,255).round().astype('uint8'))
def place(im,p,q,theta):
 rr=rot(theta);mat=np.c_[rr,np.asarray(q)-rr@np.asarray(p)];return warp(im,mat),mat
def neutral(im):
 bg=Image.new('RGBA',im.size,(237,240,242,255));bg.alpha_composite(im);return bg.convert('RGB')
font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)

# The common frame IS actual030, not a translated old036. Source000 is used
# ONLY to bring unchanged true puppet/rod raster into this actual030 frame.
# One similarity fit uses chest/shoulder, near arm and lower-body landmarks;
# translation is constrained by true neck3-under-palm support, not estimated
# from that point alone. No per-body-part or per-puppet transforms are used.
labels=['near shoulder seam','sternum button','near elbow','collar base','seat/front hip','near ankle','far ankle','front knee']
src=np.array([[269,410],[452,485],[193,711],[446,440],[504,1063],[456,1374],[847,1344],[608,1030]],float)
dst=np.array([[229,404],[414,467],[149,704],[408,431],[473,1049],[420,1367],[819,1337],[583,1015]],float)
oldC1=np.array([536.,750.]);C1=np.array([499.,747.]);xs=src-oldC1;xd=dst-C1
den=(xs*xs).sum();aa=(xs*xd).sum()/den;bb=(xs[:,0]*xd[:,1]-xs[:,1]*xd[:,0]).sum()/den
linear=np.array([[aa,-bb],[bb,aa]]);translation=C1-linear@oldC1;common=np.c_[linear,translation]
pred=src@linear.T+translation;residuals=np.linalg.norm(pred-dst,axis=1)
props_path=P/'layers/REAL_ORIGINAL_TWO_PUPPETS_FOUR_RODS.png'
props=warp(Image.open(props_path).convert('RGBA'),common);pa=np.array(props)
props.save(R/'layers/TRUE_ORIGINAL_PROPS_SAME_COMMON030_COORDS.png')
old_core=np.array(Image.open(B/'FIRST3_024_030_036_TARGETS_zero_call_20261019/masks/CONSERVATIVE_ORIGINAL_BLACK_TAIL_CORE.png'))
tailcore=cv2.warpAffine(old_core,common.astype('float32'),(W,H),flags=cv2.INTER_NEAREST)>0
tail_alpha=(pa[:,:,3]>0)&poly([[755,738],[807,739],[872,791],[878,830],[788,817],[756,783]])
# Only dark, thin feather lines (including their AA) can be newly hidden.
tail_feather=tail_alpha&(pa[:,:,:3].max(axis=2)<95)
save_mask('TRUE_TAIL_CORE_COMMON030',tailcore);save_mask('TRUE_OUTER_FEATHER_LINES_COMMON030',tail_feather)

# Remove generated props only in the actual030 cotton interior. This is a
# disclosed MATERIAL PROBE, not a delivered painting or adopted inpaint.
cloth=poly([[510,693],[590,718],[642,700],[695,661],[710,649],[734,658],[766,682],[811,711],[900,750],[960,807],[1001,867],[1005,903],[958,1025],[903,1067],[850,1012],[780,1018],[688,999],[623,966],[582,961],[530,990],[451,967],[350,932],[272,900],[257,877],[303,840],[349,806],[403,772],[461,741]])
near=poly([[109,572],[249,586],[264,636],[432,644],[485,662],[521,696],[525,738],[511,767],[472,773],[434,754],[290,755],[134,743],[111,698]])
headneck=(yy<390)|poly([[330,280],[416,274],[480,300],[519,345],[490,411],[458,438],[412,421],[379,369],[350,320]])
corechest=(xx<475)&(yy<680)
rgb=a[:,:,:3].astype('int16');skin=(rgb[:,:,0]>180)&(rgb[:,:,0]>rgb[:,:,1]+15)&(rgb[:,:,1]>rgb[:,:,2]+8)
generated=poly([[363,783],[386,759],[461,724],[506,724],[546,739],[642,741],[718,741],[785,759],[820,786],[861,827],[844,845],[785,807],[649,806],[643,881],[576,892],[566,877],[593,868],[602,804],[510,796],[460,767],[424,784],[417,810],[409,841],[394,841],[374,815]])
generated|=poly([[270,858],[310,831],[389,819],[453,826],[486,848],[500,863],[534,876],[544,897],[523,905],[489,896],[474,908],[444,910],[435,890],[360,887],[359,907],[331,903],[319,882],[274,879]])
rodmask=Image.new('L',(W,H));dr=ImageDraw.Draw(rodmask)
for p,q in [((635,800),(966,924)),((678,793),(967,891)),((499,892),(846,978)),((520,904),(838,999))]:dr.line([p,q],fill=255,width=12)
generated|=np.array(rodmask)>0
warm=(rgb[:,:,0]>rgb[:,:,2]+5)|(rgb[:,:,1]>rgb[:,:,2]+5)
generated|=cloth&(yy>720)&warm
generated=ndimage.binary_dilation(generated,iterations=3)&ndimage.binary_erosion(cloth,iterations=3)&~near
base=a.copy();donor=a[813:860,540:607,:3]
# Actual native blue cloth donor and a continuous inpaint substrate. No skin,
# shirt, code human or old figure is used to reconstruct covered cotton.
assert np.median(donor[:,:,2].astype(int)-donor[:,:,0].astype(int))>8
dy=yy%(2*donor.shape[0]);dx=xx%(2*donor.shape[1]);dy=np.minimum(dy,2*donor.shape[0]-1-dy);dx=np.minimum(dx,2*donor.shape[1]-1-dx)
tile=donor[dy,dx]
# Do not let an inpaint boundary carry old gold rod colors into the probe.
# These disclosed context holes receive only actual clean native blue cloth.
base[generated,:3]=tile[generated]
save_mask('GENERATED_PROP_CONTEXT_REPLACEMENT_ONLY',generated)
Image.fromarray(base).save(R/'layers/ACTUAL030_CLOTH_CONTEXT_BASE_TECHNICAL_ONLY.png')
common030=Image.alpha_composite(Image.fromarray(base),props)
b=np.array(common030);b[near]=a[near];common030=Image.fromarray(b)
common030.save(R/'audit/ACTUAL030_COMMON_TRUE_PROP_REFERENCE_NOT_NEW_DRAWING.png')

# Actual030's complete far chain; the hand/bangle remain one rigid piece.
# These are projected soft centers from the ACTUAL returned shape, not the
# rejected old E/W/A. Only A's small inward displacement is the design trial.
S=np.array([510.,435.]);E=np.array([616.,559.]);V=np.array([686.,585.]);A=np.array([731.,673.])
delta=np.array([-20.,-3.]);Anew=A+delta;Vnew=V+delta
L1=np.linalg.norm(E-S);L2=np.linalg.norm(V-E);d=Vnew-S;dd=np.linalg.norm(d);u=d/dd
along=(L1*L1-L2*L2+dd*dd)/(2*dd);height=math.sqrt(max(0,L1*L1-along*along));En=max([S+along*u+sg*height*np.array([-u[1],u[0]]) for sg in (-1,1)],key=lambda x:x[1])
upper_domain=poly([[471,356],[517,381],[552,412],[584,449],[623,490],[607,514],[599,533],[629,549],[656,574],[654,608],[619,622],[582,609],[550,587],[529,569],[506,588],[488,590],[473,562],[465,513],[470,458]])
fore_domain=poly([[588,511],[620,509],[655,522],[685,537],[699,556],[696,608],[660,624],[618,617],[585,593],[575,564]])
hand_domain=poly([[661,526],[710,529],[735,547],[766,570],[795,596],[801,629],[789,655],[771,684],[754,695],[734,685],[716,675],[704,653],[691,632],[678,622],[658,623],[646,606],[647,567]])
actual=a[:,:,3]>175
green=(rgb[:,:,1]>rgb[:,:,0]*1.05)&(rgb[:,:,1]>rgb[:,:,2]*1.05)&(rgb[:,:,1]>60)
upper=upper_domain&actual
fore=fore_domain&ndimage.binary_dilation(skin,iterations=2)&actual
hand=hand_domain&ndimage.binary_dilation(skin|green,iterations=2)&actual
upper|=((xx-E[0])**2+(yy-E[1])**2<52**2)&ndimage.binary_dilation(skin,iterations=2)&actual
fore|=(((xx-E[0])**2+(yy-E[1])**2<52**2)|((xx-V[0])**2+(yy-V[1])**2<42**2))&ndimage.binary_dilation(skin,iterations=2)&actual
hand|=((xx-V[0])**2+(yy-V[1])**2<46**2)&ndimage.binary_dilation(skin|green,iterations=2)&actual
upper&=~headneck&~corechest
for name,m in [('SOURCE_ACTUAL030_FAR_UPPER_SHOULDER_SLEEVE',upper),('SOURCE_ACTUAL030_FAR_FOREARM',fore),('SOURCE_ACTUAL030_HAND_AND_BANGLE_TOGETHER',hand)]:save_mask(name,m)
t1=math.atan2((En-S)[1],(En-S)[0])-math.atan2((E-S)[1],(E-S)[0]);t2=math.atan2((Vnew-En)[1],(Vnew-En)[0])-math.atan2((V-E)[1],(V-E)[0])
up,m1=place(rgba(upper),S,S,t1);fo,m2=place(rgba(fore),E,En,t2);ha,m3=place(rgba(hand),A,Anew,0)
armrgba=np.array(Image.alpha_composite(Image.alpha_composite(up,fo),ha))
armmask=armrgba[:,:,3]>8
closed=cv2.morphologyEx(armmask.astype('uint8'),cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(31,31)))>0
bridge=closed&~armmask&(xx>530)&(xx<690)&(yy>480)&(yy<637)&~headneck&~corechest
armrgb=armrgba[:,:,:3].astype('int16');arm_skin=(armrgb[:,:,0]>180)&(armrgb[:,:,0]>armrgb[:,:,1]+15)&(armrgb[:,:,1]>armrgb[:,:,2]+8)&armmask
indices=ndimage.distance_transform_edt(~arm_skin,return_distances=False,return_indices=True)
bridgepixels=np.zeros_like(a);bridgepixels[bridge,:3]=armrgba[indices[0][bridge],indices[1][bridge],:3];bridgepixels[bridge,3]=255
jointbridge=Image.fromarray(bridgepixels)
save_mask('DISCLOSED_TECHNICAL_JOINT_GAP_CLOSURE_NOT_NATIVE_ART',bridge)
old_envelope=poly([[471,390],[550,390],[660,490],[720,520],[811,565],[813,695],[711,695],[659,642],[600,635],[537,605],[506,590],[478,590],[468,540],[466,480]])&actual
erase=(ndimage.binary_dilation(upper|fore|hand,iterations=2)|old_envelope)&~near&~headneck&~corechest

# Keep the successful high peak and broad face. A smooth cloth-only source
# map moves the pinched upper region left20/up3 and fades to zero at lap y960.
# This is a technical contact probe; new native cloth is still to be drawn.
weight=np.clip((960-yy)/280,0,1)*np.clip((xx-500)/150,0,1)
mapx=(xx-delta[0]*weight).astype('float32');mapy=(yy-delta[1]*weight).astype('float32')
cloth_rgba=np.zeros_like(a);cloth_rgba[cloth]=base[cloth]
f=cloth_rgba.astype('float32');f[:,:,:3]*=f[:,:,3:4]/255
v=cv2.remap(f,mapx,mapy,cv2.INTER_CUBIC,borderMode=cv2.BORDER_CONSTANT);v=np.clip(v,0,255);al=v[:,:,3:4]/255;v[:,:,:3]=np.divide(v[:,:,:3],al,out=np.zeros_like(v[:,:,:3]),where=al>1e-6)
warped_cloth=Image.fromarray(np.clip(v,0,255).round().astype('uint8'))
work=base.copy();work[erase|cloth]=0
target=Image.alpha_composite(Image.fromarray(work),warped_cloth)
target=Image.alpha_composite(target,up);target=Image.alpha_composite(target,fo)
target=Image.alpha_composite(target,jointbridge)
target=Image.alpha_composite(target,props)

# A small continuous leading lip turns toward the outer feather tips while
# the high held peak stays fixed. ONLY fine outer feather lines may be hidden;
# body, neck, all rods and most feathers retain their common030 pixels.
def cubic(p0,p1,p2,p3,n=50):
 t=np.linspace(0,1,n)[:,None];return ((1-t)**3*np.array(p0)+3*(1-t)**2*t*np.array(p1)+3*(1-t)*t*t*np.array(p2)+t**3*np.array(p3))
left=cubic(Anew,Anew+[45,18],[794,738],[824,796])
crossedge=cubic([824,796],[838,794],[852,798],[865,803])
left2=cubic([824,796],[818,815],[841,840],[888,853])
right=cubic([913,866],[875,819],[852,774],Anew+[27,5])
lip=poly(np.vstack([left,left2,[[913,866]],right,Anew[None,:]]))
tongue=poly(np.vstack([crossedge,[[894,842],[875,862],[831,832],[818,815],[824,796]]]))
lip|=tongue
# Move a small tongue into only the terminal portion of real outer feathers.
tail_roi=poly([[812,790],[873,790],[888,840],[812,840]])
cover=tail_alpha&tail_roi&lip
opaque_blue=np.array(warped_cloth)
# Copy actual successful030 cotton into every lip pixel; never transparent.
missing=lip&(opaque_blue[:,:,3]<200);opaque_blue[missing,:3]=tile[missing];opaque_blue[missing,3]=255
opaque_blue[lip,3]=255
# The visible new cloth lip is the ONE continuous front face; keep original
# non-tail foreground parts and shafts on top, but interrupt the outer lines.
front=np.zeros_like(a);front[lip]=opaque_blue[lip]
frontmask=lip&~((pa[:,:,3]>0)&~cover)
front[~frontmask]=0
target=Image.alpha_composite(target,Image.fromarray(front))
# A restrained curved fold contour makes the occlusion boundary visible; it
# never draws or modifies a feather. Native cloth must redraw this soft edge.
edge=Image.new('RGBA',(W,H));ed=ImageDraw.Draw(edge)
ed.line([tuple(p) for p in crossedge],fill=(15,23,48,255),width=2,joint='curve')
e=np.array(edge);e[~frontmask]=0;target=Image.alpha_composite(target,Image.fromarray(e))
target=Image.alpha_composite(target,ha)
out=np.array(target);out[near|headneck|corechest]=a[near|headneck|corechest];target=Image.fromarray(out)
target.save(R/'layers/NEW_F036_FROM_ACTUAL030_TECHNICAL_PROBE_NOT_NATIVE.png')
save_mask('NEW_FRONT_LIP_CONTINUOUS_FACE',lip);save_mask('ONLY_NEW_TRUE_OUTER_FEATHER_OCCLUSION',cover)
save_mask('NEAR_BARE_RIGHT_ARM_PROTECTED',near)

# Only one complete new target is sent. No old full pose is in the input set.
first=Image.new('RGB',(1230,1650),'#edf0f2');fd=ImageDraw.Draw(first)
fd.text((20,13),'F036 NEW TARGET FROM ACTUAL PASSED030',font=font(25),fill='#23364d')
fd.text((20,46),'TECHNICAL CONTACT PROBE — COMPLETE ARM/COTTON MUST BE REDRAWN',font=font(17),fill='#ad481e')
first.paste(neutral(target),(20,80));fd.text((1060,110),'SAME FRAME',font=font(17),fill='#23364d')
notes=['Actual030','body retained','','Same pinch','inward20px','up3px','','HIGH PEAK','KEPT','','Small front lip','crosses a few','outer feathers','','Most tail and','ALL body','still exposed','','Near bare arm','neck3 and','knees fixed','','Guide seams','are not art']
y=155
for line in notes:fd.text((1060,y),line,font=font(16),fill='#23364d');y+=28
one=R/'inputs/01_ONLY_NEW_F036_FROM_ACTUAL030_COMPLETE_TARGET.png';first.save(one)
two=R/'inputs/02_024_HEAD_AND_INTERNAL_MATERIAL_CROPS_ONLY.png';shutil.copyfile(M/'inputs/02_F024_HEAD_IDENTITY_AND_INTERIOR_MATERIAL_CROPS_ONLY.png',two)
third=Image.new('RGB',(1650,1210),'#edf0f2');td=ImageDraw.Draw(third)
td.text((18,12),'SAME NEW TARGET: WHOLE FAR ARM + HIGH PEAK + FRONT LIP',font=font(25),fill='#23364d')
td.text((18,48),'Small real feather lines terminate at opaque cotton; most tail/body remain exposed',font=font(19),fill='#ad481e')
mainbox=(450,350,1010,1050);third.paste(neutral(target).crop(mainbox).resize((840,1050)),(18,105))
tailbox=(748,727,888,851);third.paste(neutral(target).crop(tailbox).resize((700,620)),(910,150))
td.text((910,105),'TRUE FEATHERS / NEW T-JUNCTION',font=font(21),fill='#23364d')
td.text((910,820),'Same native coordinates as actual030.',font=font(19),fill='#23364d')
td.text((910,855),'No lowering the hand or flattening peak.',font=font(19),fill='#23364d')
td.text((910,890),'No puppet movement between reference states.',font=font(18),fill='#23364d')
three=R/'inputs/03_SAME_TARGET_WHOLE_ARM_AND_OPAQUE_LIP_ENLARGED.png';third.save(three)

# Broad movement domain from actual source AND target arm/cloth; protect the
# actual near arm, whole chest outside far shoulder and exposed lower body.
armnew=(np.array(up.getchannel('A'))>0)|(np.array(fo.getchannel('A'))>0)|(np.array(ha.getchannel('A'))>0)|bridge
moving=ndimage.binary_dilation(upper|fore|hand|armnew,iterations=4)|cloth|lip
protected_props=(pa[:,:,3]>0)&~cover
moving&=~(near|headneck|corechest|protected_props|(yy>1080))
four=R/'inputs/04_NEW_MOVEMENT_DOMAIN_AND_SMALL_TRUE_TAIL_COVER_ONLY.png';save_mask('COMPLETE_MOVEMENT_DOMAIN',moving);shutil.copyfile(R/'masks/COMPLETE_MOVEMENT_DOMAIN.png',four)

# Common-scale review: actual raw030, true-prop common030, new036 technical.
pair=Image.new('RGB',(3112,1590),'#edf0f2');pd=ImageDraw.Draw(pair)
items=[('ACTUAL PASSED030 RAW — AUDIT ONLY',raw),('COMMON030 TRUE PROPS — TECHNICAL REF',common030),('NEW036 FROM SAME030 — TECHNICAL TARGET',target)]
for i,(title,im) in enumerate(items):pd.text((8+i*1036,10),title,font=font(21),fill='#23364d');pair.paste(neutral(im),(8+i*1036,48))
pair.save(R/'audit/ACTUAL030_COMMON030_NEW036_SAME_SCALE.png')
tails=Image.new('RGB',(1450,760),'#edf0f2');dd=ImageDraw.Draw(tails)
for x,title,im in [(10,'COMMON030: SAME TRUE FEATHERS, NO NEW COVER',common030),(735,'NEW036: OPAQUE FRONT LIP, FIRST SMALL COVER',target)]:dd.text((x,10),title,font=font(17),fill='#23364d');tails.paste(neutral(im).crop(tailbox).resize((700,620)),(x,70))
tails.save(R/'audit/TRUE_TAIL_BEFORE_AFTER_SAME_PROPS_SAME_SCALE.png')

changed=erase|cloth|lip|(pa[:,:,3]>0)|armnew
protected_source=~changed
bodychecks={}
for name,box in [('head',(180,0,680,360)),('chest',(270,380,455,640)),('near_bare_arm',(130,600,515,770)),('knees_and_lowerbody',(350,1085,910,1530)),('stool',(0,1080,400,1530))]:
 x0,y0,x1,y1=box;region=np.zeros((H,W),bool);region[y0:y1,x0:x1]=True;mask=region&~changed
 bodychecks[name]={'audited_pixels':int(mask.sum()),'unchanged_RGBA_from_actual030':bool(np.array_equal(out[mask],a[mask]))}
save_mask('UNCHANGED_BODY_AUDIT_REGION',protected_source)
armcovers={}
for name,im in [('upper',up),('forearm',fo),('hand_bangle',ha)]:
 m=(np.array(im.getchannel('A'))>0)&~near&~headneck&~corechest&~protected_props;armcovers[name]={'pixels':int(m.sum()),'white_missing':int((m&~moving).sum())}
register={'common_frame':'ACTUAL_SUCCESSFUL_F030_NATIVE_1024x1536','no_alignment_of_old036_target_used':True,'body_is_actual030_not_warped_old_mother':True,'true_original_group_source':str(props_path),'true_original_group_source_sha256':sha(props_path),'single_similarity_original_props_to_actual030':common.tolist(),'scale':float(math.hypot(aa,bb)),'rotation_degrees':float(math.degrees(math.atan2(bb,aa))),'near_palm_true_neck3_point_original':oldC1.tolist(),'near_palm_true_neck3_point_common030':C1.tolist(),'neck3_mapping_error':float(np.linalg.norm(common[:,:2]@oldC1+common[:,2]-C1)),'manual_body_anchor_uncertainty_px':15,'multi_body_fit':[{'name':name,'source000':s.tolist(),'actual030':d.tolist(),'mapped':p.tolist(),'residual_px':float(r)} for name,s,d,p,r in zip(labels,src,dst,pred,residuals)],'multi_body_RMS_px':float(np.sqrt(np.mean(residuals**2))),'reference_fit_only_not_formal_original_prop_scene_gate':True,'same_true_props_RGBA_layer_for_both_reference_states':True,'puppet_movement_between_common030_and_new036':False}
(R/'geometry/COMMON_ACTUAL030_COORDINATES_AND_TRUE_PART_REFERENCE.json').write_text(json.dumps(register,indent=2)+'\n')
pose={'source':'actual_successful030_pixels','S_soft':S.tolist(),'E_soft':E.tolist(),'W_soft':V.tolist(),'same_material_pinch_A':A.tolist(),'new_pinch_A':Anew.tolist(),'delta_pinched_material_point':delta.tolist(),'new_elbow_soft':En.tolist(),'new_wrist_soft':Vnew.tolist(),'hand_bangle_rotation_delta':0,'source_projected_lengths':[float(L1),float(L2)],'target_projected_lengths':[float(np.linalg.norm(En-S)),float(np.linalg.norm(Vnew-En))],'proxy_lengths_not_measured_3D_bones':True,'old_low_E_W_A_cancelled':True,'human_matrices_technical_only':{'upper':m1.tolist(),'forearm':m2.tolist(),'hand_bangle':m3.tolist()},'high_peak_moves_inward_and_up_never_flattened':True,'new_native_image_calls':0}
(R/'geometry/ACTUAL030_TO_NEW036_COMPLETE_ARM_AND_PINCH.json').write_text(json.dumps(pose,indent=2)+'\n')
checks={'new_imagegen_calls':0,'new_native_drawings':0,'actual_source030_sha256':sha(rawpath),'same_common_frame_baseline_and_target':True,'actual030_whole_body_not_globally_translated_or_scaled':True,'body_exact_pixels':bodychecks,'source_pinch':A.tolist(),'target_pinch':Anew.tolist(),'delta_pinch':delta.tolist(),'no_covered_tail_created_by_puppet_motion':True,'true_tail_core_pixels':int(tailcore.sum()),'true_outer_feather_pixels_newly_covered':int(cover.sum()),'true_core_pixels_newly_covered':int((cover&tailcore).sum()),'new_occlusion_all_opaque_blue_lip':bool(np.all(opaque_blue[cover,3]==255)),'near_bare_arm_exact_RGBA_from_actual030':bool(np.array_equal(out[near],a[near])),'white_near_arm_overlap':int((moving&near).sum()),'white_protected_true_prop_overlap':int((moving&protected_props).sum()),'target_visible_arm_white_coverage':armcovers,'disclosed_technical_joint_gap_fill_pixels':int(bridge.sum()),'first_target_is_technical_not_native_art':True,'actual030_complete_raw_provenance_not_in_planned_request':True,'old_first3_036_and_failed036_not_used_to_construct_human_or_cloth':True}
(R/'qa/ACTUAL_PIXEL_AND_CONTACT_CHECKS.json').write_text(json.dumps(checks,indent=2)+'\n')
inputs=[one,two,three,four]
(R/'requests/FOUR_PLANNED_INPUTS_SHA256.json').write_text(json.dumps([{'order':i+1,'path':str(p),'sha256':sha(p),'size':list(Image.open(p).size)} for i,p in enumerate(inputs)],indent=2)+'\n')
(R/'CALL_STATE_ZERO.json').write_text(json.dumps({'state':'REBUILD_FROM_ACTUAL030_PREPARATION_ONLY_AWAITING_SHORT_GATE','new_requests_started':0,'new_raw_outputs':0,'new_retry_requests':0},indent=2)+'\n')
print(json.dumps({'new_calls':0,'pinch_delta':delta.tolist(),'body_checks':bodychecks,'new_true_outer_feather_pixels_covered':int(cover.sum()),'core_covered':int((cover&tailcore).sum()),'tail_core_total':int(tailcore.sum()),'new_arm_coverage':armcovers,'near_arm_exact':checks['near_bare_arm_exact_RGBA_from_actual030'],'multi_body_reference_RMS':register['multi_body_RMS_px']},indent=2))
