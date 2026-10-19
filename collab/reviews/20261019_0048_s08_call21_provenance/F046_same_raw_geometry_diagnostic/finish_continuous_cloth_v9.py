from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt,binary_dilation,map_coordinates
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent.parent;D=R/'F046_same_raw_geometry_candidate_v9_cloth';V=R/'F046_same_raw_geometry_candidate_v9_base';G=R/'F046_input_gate';P=R/'F043_FINAL_LOCKED'
for z in ['candidates','masks','qa','geometry']:(D/z).mkdir(parents=True,exist_ok=True)
a=np.array(Image.open(P/'S08_F043_grandma_match_box_RGBA.png'));q=np.array(Image.open(R/'F046_result_nominal/registered/F046_registered_scene_patch_RGBA.png'));v=np.array(Image.open(V/'candidates/S08_F046_same_raw_arm_geometry_DIAGNOSTIC_RGBA.png'));arm=np.array(Image.open(V/'registered/ACTUAL_native_near_arm_transformed_only_RGBA.png'));H,W=a.shape[:2];Y,X=np.indices((H,W));out=v.copy()
def poly(points):
 im=Image.new('L',(W,H));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
def save(n,m):Image.fromarray(m.astype('uint8')*255).save(D/'masks'/f'{n}.png')
def blend(src,m,weight,protect_alpha=False):
 global out
 aa=out[:,:,3]/255.;bb=src[:,:,3]/255.;ww=weight[:,:,None];ca=aa*(1-weight)+bb*weight;cp=out[:,:,:3]*aa[:,:,None]*(1-ww)+src[:,:,:3]*bb[:,:,None]*ww;rgb=np.rint(cp/np.maximum(ca[:,:,None],1e-8)).clip(0,255).astype('uint8');new=np.dstack((rgb,np.rint(ca*255).astype('uint8')));new[new[:,:,3]==0]=0
 if protect_alpha:new[:,:,3]=out[:,:,3]
 out[m]=new[m]
# Exact original collar and its adjacent blue cloth remain on fixed043 neck/chest.
collar=poly([(841,680),(878,680),(922,741),(965,790),(935,799),(893,758),(869,728),(853,703)])
dist=distance_transform_edt(collar);wt=np.clip(dist/4,0,1)
# Keep actual original ink and white flowers at full strength; feather only blue material, not anatomical or lapel edges.
ink=np.max(a[:,:,:3],2)<105;white=np.min(a[:,:,:3],2)>205;wt[collar&(ink|white)]=1
blend(a,collar,wt,True)
# Same raw left outer cloth strip reconnects the sleeve hem to unchanged lower torso, including its real silhouette.
strip=poly([(727,839),(808,839),(825,886),(828,923),(803,946),(721,946)])
z=np.clip((Y-880)/55,0,1);z=z*z*(3-2*z);coords=np.array([Y.astype(float),X+10*z]);qa=q[:,:,3]/255.;qp=q[:,:,:3]*qa[:,:,None];sa=map_coordinates(qa,coords,order=1,mode='constant',cval=0);sp=np.stack([map_coordinates(qp[:,:,j],coords,order=1,mode='constant',cval=0)for j in range(3)],2);sl=np.dstack((np.rint(sp/np.maximum(sa[:,:,None],1e-8)).clip(0,255).astype('uint8'),np.rint(sa*255).astype('uint8')))
wt=np.ones((H,W));wt*=np.clip((Y-839)/12,0,1);wt*=np.clip((946-Y)/10,0,1);wt*=np.clip((828-X)/18,0,1)
edge=strip&((out[:,:,3]<230)|(sl[:,:,3]<230));wt[edge&(Y>851)&(Y<936)]=1;blend(sl,strip,wt)
# Newly revealed chest cloth gap has no same-coordinate donor: genuine raw right-chest swatch rigidly translated(-65,+55).
donor=np.zeros_like(q);donor[55:,:-65]=q[:-55,65:]
patch=poly([(946,811),(977,810),(1009,830),(1026,854),(1004,880),(957,861),(941,835)])
# Only background cloth; foreground raw arm and real far hand overlay later.
w0=np.clip(distance_transform_edt(patch)/8,0,1);holes=patch&(out[:,:,3]<180);w0[holes]=1
blend(donor,patch,w0)
# Actual original lower-body outer cloth moved up18px supplies the newly revealed waist edge; body below970 remains original.
z=np.clip((Y-935)/40,0,1);z=z*z*(3-2*z);coords=np.array([Y+18*(1-z),X.astype(float)]);aa=a[:,:,3]/255.;ap=a[:,:,:3]*aa[:,:,None];la=map_coordinates(aa,coords,order=1,mode='constant',cval=0);lpm=np.stack([map_coordinates(ap[:,:,j],coords,order=1,mode='constant',cval=0)for j in range(3)],2);lower=np.dstack((np.rint(lpm/np.maximum(la[:,:,None],1e-8)).clip(0,255).astype('uint8'),np.rint(la*255).astype('uint8')))
lp=poly([(984,927),(1022,927),(1051,942),(1051,975),(987,975)])
wt=np.clip((Y-927)/8,0,1)*np.clip((975-Y)/15,0,1)*np.clip((X-984)/8,0,1);edge=lp&((out[:,:,3]<230)|(lower[:,:,3]<230));wt[edge&(Y>935)&(Y<970)]=1;blend(lower,lp,wt)
# Restore complete far back layer and the real transformed foreground arm/hand after all genuine cloth underlays.
f=np.array(Image.open(P/'F043_complete_underlying_far_hand_jade_AND_TRANSPARENT_SEAT_RGBA.png'));ff=np.array(Image.open(P/'F043_complete_underlying_far_hand_jade_AND_TRANSPARENT_SEAT_footprint.png'))>0
# These cloth repairs are left of the far hand. Keep already corrected wrist pixels unchanged; actual skin footprint restores the acceptedv5 geometry verbatim.
protected=arm[:,:,3]>0
out[protected]=v[protected]
nh=np.array(Image.open(G/'masks/F046_fixed_near_distal_and_original_sourceover_AA_guard.png'))>0;root=np.array(Image.open(G/'masks/F046_near_proximal_collar_release.png'))>0
out[nh|root|ff]=v[nh|root|ff]
# Input construction was lower than this now-approved natural raw elbow. Reveal all349 actual foreground pixels beyond oldwhite; exclude95true distal pixels.
oldw=np.array(Image.open(V/'masks/EXPLICIT_white_permission.png'))>0
actual_release=(arm[:,:,3]>0)&~oldw&~nh
n=np.array(Image.open(G/'inputs/F046_true_near_hand_match_INDEPENDENT_RGBA.png'))
full=np.array(Image.alpha_composite(Image.alpha_composite(Image.fromarray(out),Image.fromarray(arm)),Image.fromarray(n)))
out[actual_release]=full[actual_release]
assert not (actual_release&(np.array(Image.open(G/'masks/F046_true_low_rod_seat_core.png'))>0)).any()
# Donor patches must never expose source pink skin. They are true blue cloth or source transparent outline only.
perm=collar|strip|patch|lp|actual_release;diff=np.any(out!=v,2)
assert not (diff&~perm).any();assert np.array_equal(out[nh],v[nh]);assert np.array_equal(out[ff&~actual_release],v[ff&~actual_release]);assert np.array_equal(out[:650],v[:650])
p=D/'candidates/S08_F046_same_raw_continuous_arm_cloth_RGBA.png';Image.fromarray(out).save(p)
for n,m in [('RESTORE_original043_collar_continuous',collar),('ADOPT_actual_raw_outer_sleeve_body_strip',strip),('ADOPT_raw_chest_cloth_rigid_minus65_plus55',patch),('ADOPT_original_lower_body_up18',lp),('EXPLICIT_cloth_repairs_union',perm),('ACTUAL_changed_cloth_pixels',diff),('RELEASE_actual_near_forearm_beyond_old_construction349',actual_release)]:save(n,m)
rep={'status':'GEOMETRY_AND_SOURCE_CLOTH_DIAGNOSTIC_NOT_APPROVED','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'parent_candidate':str(V/'candidates/S08_F046_same_raw_arm_geometry_DIAGNOSTIC_RGBA.png'),'same_raw21_no_additional_generation':True,'cloth_change_pixels':int(diff.sum()),'changes_outside_explicit_cloth_union':0,'near_distal_changed':0,'far_archive_not_rewritten':True,'actual_new_foreground_release_pixels':int(actual_release.sum()),'far_composite_changed_only_actual_foreground_release':int(np.any(out[ff]!=v[ff],1).sum()),'forearm_source_shape_unchanged_but_old_permission_clipping349_released':True,'source_cloth_transforms':[{'source':'registered_raw_right_chest','target':'newly_exposed_chest_behind_arm','translation':[-65,55],'scale':1},{'source':'original043_lower_torso','target':'newly_exposed_waist_outer_edge','translation':[0,-18],'scale':1}],'notes':'Only actual cloth donor pixels; native near arm and original hand positions remain unchanged. Must view actual shoulder/collar/forearm and cloth seams.'};(D/'geometry/CLOTH_SOURCE_AND_CHECKS.json').write_text(json.dumps(rep,indent=2))
for tag,col in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 bg=Image.alpha_composite(Image.new('RGBA',(W,H),col),Image.fromarray(out));old=Image.alpha_composite(Image.new('RGBA',(W,H),col),Image.fromarray(a));bg.convert('RGB').save(D/'qa'/f'candidate_{tag}.png');panel=Image.new('RGB',(1660,750),col[:3]);panel.paste(old.crop((640,280,1470,1030)),(0,0));panel.paste(bg.crop((640,280,1470,1030)),(830,0));panel.save(D/'qa'/f'F043_F046_actual_same_scale_{tag}.png')
 for name,bb,sc in [('whole_arm',(700,680,1470,1020),2),('near_wrist',(1130,760,1290,910),4),('shoulder_body',(735,680,1060,980),3)]:
  cc=bg.crop(bb);cc.resize((cc.width*sc,cc.height*sc)).save(D/'qa'/f'{name}_{tag}.png')
 gr=bg.copy();ImageDraw.Draw(gr).line((690,981,1470,981),fill=(230,85,55),width=2);gr.crop((700,680,1470,1020)).resize((1540,680)).save(D/'qa'/f'actual_elbow_with_table981_{tag}.png')
print(json.dumps(rep,indent=2))
