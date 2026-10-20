"""F090 minimal review candidate. Original drawing/material pixels only; no new image call."""
from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage as nd
import numpy as np,json,hashlib,shutil
R=Path(__file__).resolve().parent;B=R.parent;Q=R/'reintegration_zero_call';Q.mkdir(exist_ok=True)
P=B/'F072_F078_F084_NATIVE_call01_each_from_38c5ba63_20261019'
H=B/'F066_F089_COMPLETE_FAR_SLEEVE_FINAL_ZERO_CALL_20261020'
G=B/'F072_F078_F084_FROM_LOCKED066_INPUT_GATE_ZERO_CALL_20261019'
load=lambda p:np.array(Image.open(p).convert('RGBA'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda a,p:Image.fromarray(a).save(p)
Y,X=np.indices((1536,1024));xy=np.stack([X,Y],2)
def poly(pts):
 im=Image.new('L',(1024,1536));ImageDraw.Draw(im).polygon(pts,fill=255);return np.array(im)>0
def component(seed,point):
 lab,_=nd.label(nd.binary_closing(seed,iterations=3));k=lab[point[1],point[0]];assert k>0
 return nd.binary_dilation(nd.binary_fill_holes(lab==k),iterations=2)
def sample(a,co):
 v=a.astype(float);v[:,:,:3]*=v[:,:,3:4]/255
 z=np.stack([nd.map_coordinates(v[:,:,k],[co[:,:,1],co[:,:,0]],order=1,mode='constant',cval=0)for k in range(4)],2)
 z[:,:,:3]=np.divide(z[:,:,:3],z[:,:,3:4]/255,out=np.zeros_like(z[:,:,:3]),where=z[:,:,3:4]>1e-8)
 z=np.rint(np.clip(z,0,255)).astype('uint8');z[z[:,:,3]==0]=0;return z
def comp(*layers):
 a=Image.new('RGBA',(1024,1536))
 for b in layers:a.alpha_composite(Image.fromarray(b))
 return np.array(a)
rawp=R/'originals/S29_F090_call01_RAW_UNTOUCHED.png';raw=load(rawp);lockedp=H/'F084_FINAL_RGBA.png';locked=load(lockedp)
clothp=R/'inputs/05_F090_ONE_SAME_SOURCE_CLOTH_RGBA.png';cloth=load(clothp)
oldclothp=P/'F084/inputs/05_ONLY_SAME_SOURCE_CLOTH_RGBA.png';oldcloth=load(oldclothp)
propsp=G/'UNCHANGED_TRUE_TWO_PUPPETS_FOUR_RODS_RGBA.png';props=load(propsp)
assert np.array_equal(cloth[:815],oldcloth[:815])
rgb=raw[:,:,:3].astype(float)
blue=(rgb[:,:,1]>95)&(rgb[:,:,2]>135)&(rgb[:,:,2]>rgb[:,:,0]+15)
skin=(rgb[:,:,0]>120)&(rgb[:,:,1]>65)&(rgb[:,:,2]>90)&(rgb[:,:,0]>rgb[:,:,2]+25)
shirtpoly=poly([(310,270),(490,345),(610,493),(503,568),(492,631),(525,741),(438,780),(320,824),(210,939),(40,938),(75,760),(125,696),(128,640),(73,615),(70,580),(95,490),(130,425),(185,360),(245,315)])
blab,_=nd.label(nd.binary_closing(blue&(raw[:,:,3]>128)&shirtpoly,iterations=3))
counts=np.bincount(blab.ravel());keep=counts>200;keep[0]=False
bm=nd.binary_dilation(nd.binary_fill_holes(keep[blab]),iterations=2)&shirtpoly&(raw[:,:,3]>0)
nm=component(skin&(raw[:,:,3]>128)&(X<510)&(Y>570)&(Y<960),(180,650))&(X<510)&(Y>570)&(Y<960)&(raw[:,:,3]>0)
# The cloth visible in the palm's negative space belongs to the sole canonical
# sheet. Remove generated navy from that space; both actual finger pads/ink stay.
generated_cotton_in_hand_gap=nm&(X>355)&(Y>835)&(rgb[:,:,2]>rgb[:,:,0]+9)&(rgb[:,:,1]<130)
nm&=~generated_cotton_in_hand_gap
# The complete near shoulder/sleeve and bare arm are one source group. Its seam
# is in blue torso interior; all outer sleeve/cuff/arm ink stays in the group.
sl=poly([(300,275),(307,320),(285,385),(278,490),(265,595),(246,650),(112,650),(49,490),(75,361),(210,286)])
nearm=(bm&sl)|nm;near=np.zeros_like(raw);near[nearm]=raw[nearm]
root0=np.array([190.,410.]);srcP=np.array([414.,878.]);root1=root0.copy();dstP=np.array([444.,923.])
v=srcP-root0;w=dstP-root1;u=float(w@v/(v@v));r=float((w[1]*v[0]-w[0]*v[1])/(v@v));M=np.array([[u,-r],[r,u]]);t=root1-M@root0
co=(xy-t)@np.linalg.inv(M).T;nearreg=sample(near,co)
assert np.allclose(M@srcP+t,dstP,atol=1e-10) and np.allclose(M@root0+t,root1,atol=1e-10)
body=np.zeros_like(raw);body[bm&~sl]=raw[bm&~sl]
# Extend the same continuous native blouse surface behind the repositioned arm,
# anchored above the waist. This is floral-fabric projection, never a limb warp.
bshift=37*np.maximum(0,1-((X-350)/180)**2)**2
bsy=Y.astype(float)
for _ in range(15):
 bw=np.clip((bsy-630)/100,0,1);bw=bw*bw*(3-2*bw)
 bf=np.clip((960-bsy)/100,0,1);bf=bf*bf*(3-2*bf)
 bsy=Y-bshift*bw*bf
body=sample(body,np.stack([X,bsy],2))
# Use the actual newly drawn trousers as one continuous lap material. Exposed
# upper lap follows its real source boundary, while y1100+ remains exact084.
# This projects fabric only; no limb, finger, puppet or stool is deformed.
native_border=np.array([[100,932],[250,935],[320,926],[365,926],[410,920],[440,915],[460,946],[480,965],[500,970],[540,969],[560,964],[580,966],[600,973],[620,986],[640,997],[660,1007],[680,1017],[700,1017],[720,1011],[740,996],[760,985],[780,983],[800,985],[811,1026]],float)
pantpoly=poly(native_border.astype(int).tolist()+[(837,1100),(420,1100),(420,1037),(310,1015),(180,1000),(103,978)])
navy=(rgb[:,:,2]>rgb[:,:,0]+5)&(rgb[:,:,1]<110)&(rgb[:,:,0]<120)
pantm=component(navy&(raw[:,:,3]>128)&pantpoly,(550,1070))&pantpoly&(raw[:,:,3]>0)
pants=np.zeros_like(raw);pants[pantm]=raw[pantm]
edge=np.full(1024,1100.,float)
for x in range(1024):
 yy=np.where(cloth[:,x,3]>128)[0]
 if len(yy):edge[x]=float(yy.max())
sourceedge=np.interp(np.arange(1024),native_border[:,0],native_border[:,1]);dy=np.minimum(80,np.maximum(0,sourceedge-edge+2))
fade=np.clip((1100-Y)/np.maximum(1,1100-edge[None,:]),0,1)
pantsco=np.stack([X,Y+dy[None,:]*fade],2);pantsreg=sample(pants,pantsco)
# Remove old near arm, all old cotton/props and obsolete blue garment outlines.
oldnear=load(P/'F084/reintegration_v3_locked_hold/COMPLETE_NEAR_NATIVE_ARM_HAND_RGBA.png')
lr=locked[:,:,:3].astype(float);oldblue=(lr[:,:,1]>95)&(lr[:,:,2]>135)&(lr[:,:,2]>lr[:,:,0]+15)
white=np.array(Image.open(R/'inputs/04_F090_COMPLETE_MOVING_SEMANTIC_WHITE_DOMAIN.png').convert('L'))>0
ol,_=nd.label(nd.binary_closing(oldblue&(locked[:,:,3]>128)&shirtpoly,iterations=3));oc=np.bincount(ol.ravel());ok=oc>200;ok[0]=False
oldgarment=nd.binary_dilation(nd.binary_fill_holes(ok[ol]),iterations=2)&shirtpoly
obsolete_front_right_lobe=poly([(800,970),(1015,900),(1023,1100),(835,1100),(810,1020)])
remove=(oldnear[:,:,3]>0)|(oldcloth[:,:,3]>0)|(props[:,:,3]>0)|oldgarment|obsolete_front_right_lobe|nd.binary_dilation(oldblue&(Y>275)&(Y<980),iterations=3)|(nearreg[:,:,3]>0)
base=locked.copy();base[remove]=0
oldfront=np.array(Image.open(G/'F084/FRONT_FOLD_OVER_TRUE_PROPS_MASK.png').convert('L'))>0
lip=np.zeros_like(cloth);lip[oldfront]=cloth[oldfront]
final=comp(base,pantsreg,body,cloth,props,lip,nearreg)
# Preserve the entire stationary far shoulder/sleeve/arm/jade/hand, including
# exterior transparent pixels. Cloth in that domain is byte-exact084 already.
farupper=np.array(Image.open(H/'ONE_MATRIX_REGISTERED_WHOLE_SEMANTIC_DOMAIN.png').convert('L'))>0
farbare=load(P/'F084/reintegration_v3_locked_hold/COMPLETE_FAR_NATIVE_ARM_JADE_HAND_RGBA.png')
farprotect=farupper|(farbare[:,:,3]>0);final[farprotect]=locked[farprotect]
# Restore the accepted full head/neck, excluding its blue collar so the new
# complete garment cannot be cut by an obsolete collar outline.
headpoly=poly([(210,25),(640,25),(640,335),(523,372),(488,417),(425,416),(383,357),(345,323),(260,299),(217,270)])
headskin=(lr[:,:,0]>120)&(lr[:,:,1]>65)&(lr[:,:,2]>90)&(lr[:,:,0]>lr[:,:,2]+25)
headhair=(np.abs(lr[:,:,0]-lr[:,:,2])<35)&(lr[:,:,0]>55)&(Y<300)
headink=(lr[:,:,:3].max(2)<100)&(Y<365)
headprotect=component((headskin|headhair|headink)&headpoly&(locked[:,:,3]>128),(450,220))&headpoly&(locked[:,:,3]>0)
final[headprotect]=locked[headprotect];final[Y>=1100]=locked[Y>=1100]
# Canonical cotton lies above the genuinely under-hooking index pad. It is the
# same source sheet/flower phase, never a painted line or isolated finger warp.
hooksrc=poly([(373,880),(404,876),(424,881),(423,897),(410,914),(383,919)])
hook=nd.map_coordinates(hooksrc.astype(float),[co[:,:,1],co[:,:,0]],order=0,mode='constant',cval=0)>.5
edgefront=hook&(nearreg[:,:,3]>0)&(cloth[:,:,3]>0)&(np.abs(Y-edge[None,:])<10)&(np.hypot(X-dstP[0],Y-dstP[1])<35)
over=np.zeros_like(cloth);over[edgefront]=cloth[edgefront];final=comp(final,over)
# Alpha composition canonicalizes fully transparent RGB. Restore byte-exact
# protected source domains AFTER the final occlusion composite as well.
final[farprotect]=locked[farprotect];final[headprotect]=locked[headprotect];final[Y>=1100]=locked[Y>=1100]
assert np.array_equal(final[farprotect],locked[farprotect]) and np.array_equal(final[Y>=1100],locked[Y>=1100])
save(final,Q/'F090_SAME_SOURCE_CLOTH_TRUE_PROPS_NATIVE_CANDIDATE_RGBA.png')
for name,a in [('ORIGINAL090_COMPLETE_NATIVE_NEAR_SHOULDER_SLEEVE_ARM_HAND_RGBA',near),('ONE_SIMILARITY_COMPLETE_NEAR_GROUP_REGISTERED_RGBA',nearreg),('ORIGINAL090_NEW_BLOUSE_RGBA',body),('ORIGINAL090_DRAWN_TROUSER_LAP_RGBA',pants),('SAME_NATIVE_TROUSER_LAP_MATERIAL_PROJECTED_RGBA',pantsreg),('EXACT_PREPARED_SAME_SOURCE_CLOTH_RGBA',cloth),('EXACT_ORIGINAL_TRUE_PUPPETS_FOUR_RODS_RGBA',props),('SAME_SOURCE_FAR_FOLD_OVER_PROPS_RGBA',lip),('SAME_SOURCE_FRONT_EDGE_OVER_UNDERHOOK_RGBA',over)]:save(a,Q/(name+'.png'))
actual_changes=np.any(final!=locked,axis=2)
complete_edit_domain=remove|actual_changes
for layer in [pantsreg,body,cloth,props,lip,nearreg,over]:complete_edit_domain|=layer[:,:,3]>0
for name,m in [('COMPLETE_EDIT_DOMAIN',complete_edit_domain),('COMPLETE_ACTUAL_RGBA_CHANGE_DOMAIN',actual_changes),('NEAR_ORIGINAL_COMPLETE_GROUP_DOMAIN',nearm),('STATIONARY_FAR_COMPLETE_CHAIN_PROTECT_DOMAIN',farprotect),('FIXED_HEAD_PROTECT_DOMAIN',headprotect),('OBSOLETE084_FRONT_RIGHT_COMPLETE_LOBE_CLEAR_DOMAIN',obsolete_front_right_lobe),('CANONICAL_EDGE_OVER_ACTUAL_UNDERHOOK_DOMAIN',edgefront)]:save((m*255).astype('uint8'),Q/(name+'.png'))
gray=Image.alpha_composite(Image.new('RGBA',(1024,1536),(232,235,239,255)),Image.fromarray(final)).convert('RGB')
gray.save(Q/'FULL_CANDIDATE_ON_GRAY.png');gray.crop((65,275,825,1070)).save(Q/'COMPLETE_BOTH_SHOULDER_SLEEVE_ELBOW_WRIST_CLOTH_LAP_1TO1.png');gray.crop((360,845,505,975)).resize((580,520)).save(Q/'NEAR_TRUE_CONTACT444_923_4X.png');gray.crop((550,615,735,810)).resize((555,585)).save(Q/'FAR_UNCHANGED_TRUE_CONTACT640_746_3X.png')
board=Image.new('RGB',(900,480),(232,235,239));d=ImageDraw.Draw(board)
for col,(im,point,label)in enumerate([(Image.open(R/'RAW_FULL_ON_GRAY.png'),srcP,'ORIGINAL native pinch'),(gray,dstP,'REGISTERED same material pinch')]):
 x,y=map(int,point);crop=im.crop((x-65,y-55,x+65,y+60)).resize((390,345));ox=col*450;board.paste(crop,(ox,50));d.text((ox+8,8),label,fill='black');d.text((ox+8,27),str(point.tolist()),fill='black');cx=ox+195;cy=50+165;d.ellipse((cx-5,cy-5,cx+5,cy+5),outline='red',width=2)
board.save(Q/'ORIGINAL_AND_REGISTERED_REAL_NEAR_PINCH_CONTACT_BOARD.png')
both=Image.new('RGB',(900,900),(232,235,239));both.paste(board,(0,0));bd=ImageDraw.Draw(both)
fp=np.array([640.098467936869,745.61030076984]);fx,fy=np.rint(fp).astype(int)
for col,(a,label)in enumerate([(locked,'LOCKED084 exact far contact'),(final,'F090 exact same far contact')]):
 im=Image.alpha_composite(Image.new('RGBA',(1024,1536),(232,235,239,255)),Image.fromarray(a)).convert('RGB');ox=col*450
 both.paste(im.crop((fx-65,fy-55,fx+65,fy+60)).resize((390,345)),(ox,500));bd.text((ox+8,458),label,fill='black');bd.text((ox+8,478),str(fp.tolist()),fill='black');bd.ellipse((ox+190,660,ox+200,670),outline='red',width=2)
both.save(Q/'BOTH_REAL_CONTACTS_SOURCE_AND_CANDIDATE_4_PANEL.png')
report={'status':'CANDIDATE_PENDING_ACTUAL_FULL_IMAGE_AND_CONTACT_REVIEW','new_generation_calls':0,'new_scene_renders':0,'raw090_SHA256':sha(rawp),'locked084_SHA256':sha(lockedp),'same_source_cloth_SHA256':sha(clothp),'true_props_four_rods_SHA256':sha(propsp),'near_complete_shoulder_sleeve_arm_hand_single_similarity':{'source_root':root0.tolist(),'target_root':root1.tolist(),'source_real_cotton_pinch':srcP.tolist(),'target_same_material_pinch':dstP.tolist(),'matrix':M.tolist(),'translation':t.tolist(),'scale':float(np.hypot(u,r)),'rotation_degrees':float(np.degrees(np.arctan2(r,u))),'per_finger_transform':False,'target_numerical_error':float(np.linalg.norm(M@srcP+t-dstP))},'far_contact':[640.098467936869,745.61030076984],'far_complete_chain_RGBA_changes':int(np.any(final[farprotect]!=locked[farprotect],1).sum()),'source_cloth_y_before815_RGBA_changes_against084':0,'head_RGBA_changes':int(np.any(final[headprotect]!=locked[headprotect],1).sum()),'legs_y1100_plus_RGBA_changes':0,'trouser_source_boundary':native_border.tolist(),'trouser_same_raw_material_projection_max_dy':float(dy.max()),'trouser_synthetic_fill_pixels':0,'same_source_cotton_pixels_painted':0,'true_props_and_four_rods_source_geometry_changed':False,'final_candidate_SHA256':sha(Q/'F090_SAME_SOURCE_CLOTH_TRUE_PROPS_NATIVE_CANDIDATE_RGBA.png'),'whole_shot_ready_claimed':False}
(Q/'SOURCES_DOMAINS_AND_TWO_TRUE_CONTACTS_CHECK.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
