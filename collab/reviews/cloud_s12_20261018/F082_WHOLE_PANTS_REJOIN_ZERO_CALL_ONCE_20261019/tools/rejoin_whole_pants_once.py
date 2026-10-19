"""ONE zero-generation complete-pants similarity attempt from the sole082 raw.
No target/person reference RGB, no per-knee deformation, no alpha shaving of
the full rounded knee contour. Any incompatible join is delivered, not retuned.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,math,hashlib,shutil
from scipy.ndimage import binary_opening,binary_closing,binary_fill_holes,binary_dilation,label,distance_transform_edt

O=Path(__file__).resolve().parents[1];R=O.parent
A=R/'F082_ACTIVE_actual_call01_20261019';S=R/'F074_PANTS_LOCAL_actual_call01_20261019'
for d in ['tools','geometry','layers','candidate','qa','scene','actual_scene','reference','provenance','diagnostics']:(O/d).mkdir(exist_ok=True)
assert not (O/'candidate/F082.png').exists(),'The sole complete-pants attempt already exists. Do not retune.'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rawpath=A/'originals/F082_call01_raw.png';assert sha(rawpath)=='1e2a0674f404054874c3b0ebef3370662d8dedc708fc73d7353ab492f8175afc'
raw=Image.open(rawpath).convert('RGBA');q=np.asarray(raw).astype(int)
B=np.asarray(Image.open(A/'candidate/F082.png').convert('RGBA'))
old=np.asarray(Image.open(S/'candidate/F074.png').convert('RGBA'))
support=np.asarray(Image.open(R/'F078_NARROW_JOIN_actual_call01_20261019/layers/F078_FIXED074_STATIC_SUPPORTS.png').convert('RGBA'))
Y,X=np.mgrid[:1536,:1024]

# Original navy material extraction only. Whole knee silhouette is explicitly
# retained from actual raw alpha, never pared down to the old074 contour.
navy=(q[:,:,2]-q[:,:,0]>7)&(q[:,:,2]-q[:,:,1]>7)&(q[:,:,2]<150)&(q[:,:,1]-q[:,:,0]<30)&(q[:,:,3]>24)&(Y>=820)&(X<760)
core=binary_opening(navy,iterations=1);labs,k=label(core);areas=np.bincount(labs.ravel());keep=np.flatnonzero(areas>15000);keep=keep[keep!=0]
assert len(keep)==1,'Inspect actual navy segmentation instead of guessing multiple components.'
material=binary_fill_holes(binary_closing(np.isin(labs,keep),iterations=2))
material=binary_dilation(material,iterations=2)&(q[:,:,3]>0)
whole_knees=(X>=470)&(X<=750)&(Y>=1020)&(Y<=1370)
material[whole_knees]=q[:,:,3][whole_knees]>0
cut=np.zeros_like(q,dtype=np.uint8);cut[material]=q[material]
Image.fromarray(cut).save(O/'layers/ACTUAL_RAW_COMPLETE_NAVY_PANTS_FULL_BOTH_KNEES.png')
Image.fromarray(np.uint8(material)*255).save(O/'geometry/RAW_COMPLETE_PANTS_SEMANTIC_MASK.png')

# Visible correspondence estimates, NOT hidden bones. These are fixed BEFORE
# the one closed-form weighted similarity. No alternative fit/mask is tried.
old_global=np.asarray(json.loads((A/'geometry/ONE_WHOLE_REGISTRATION_FROZEN_OWNERSHIP_AND_PROTECTION.json').read_text())['one_whole_raw_to_native_matrix'])
controls=[
 ('actual082_back_waist_under_blouse',[250.,850.],(old_global@np.array([250.,850.,1.])).tolist(),3.),
 ('actual082_front_waist_under_blouse',[580.,950.],(old_global@np.array([580.,950.,1.])).tolist(),3.),
 ('fixed074_far_anterior_knee_turn',[708.,1210.],[675.,1200.],3.),
 ('fixed074_near_anterior_round_turn',[681.,1280.],[642.,1270.],3.),
 ('fixed074_near_knee_ground_turn',[570.,1337.],[550.,1313.],3.),
 ('fixed074_far_shin_upper_valley_axis_A',[330.,1167.],[330.,1147.],.7),
 ('fixed074_far_shin_upper_valley_axis_B',[490.,1202.],[490.,1182.],.7),
 ('fixed074_near_shin_upper_valley_axis_A',[370.,1269.],[370.,1263.],.7),
 ('fixed074_near_shin_upper_valley_axis_B',[530.,1315.],[530.,1306.],.7)]
(O/'geometry/ONE_ATTEMPT_PREDECLARED_REAL_PIXEL_CORRESPONDENCES.json').write_text(json.dumps({'status':'PREDECLARED_ONE_SIMILARITY_ONLY','controls':[{'name':n,'source_raw':s,'target_native':t,'weight':w} for n,s,t,w in controls],'visible_point_uncertainty_native':'about4to12px, not a bone measurement','intent':'one complete waist/hips/both thighs/both full knees; no body/crotch squeeze or per-knee fit','new_model_calls':0},indent=2)+'\n')
src=np.array([v[1] for v in controls]);dst=np.array([v[2] for v in controls]);weights=np.array([v[3] for v in controls]);weights/=weights.sum()
cs=np.sum(src*weights[:,None],axis=0);ct=np.sum(dst*weights[:,None],axis=0)
ss=src-cs;tt=dst-ct
U,D,Vt=np.linalg.svd((ss*weights[:,None]).T@tt)
J=np.eye(2);J[-1,-1]=np.linalg.det(Vt.T@U.T)
rot=Vt.T@J@U.T;scale=float(np.sum(D*np.diag(J))/np.sum(weights*np.sum(ss*ss,axis=1)))
translation=ct-scale*rot@cs
M=np.c_[scale*rot,translation]
assert .85<scale<1.08 and abs(math.degrees(math.atan2(rot[1,0],rot[0,0])))<8,'Stop if whole-body fit is implausible; no second fit.'
I=np.linalg.inv(np.vstack([M,[0,0,1]]))[:2]
patch=Image.fromarray(cut).transform((1024,1536),Image.Transform.AFFINE,tuple(I.ravel()),Image.Resampling.BICUBIC)
P=np.asarray(patch);patch.save(O/'layers/ONE_WHOLE_REGISTERED_COMPLETE_PANTS_FULL_BOTH_KNEES.png')

# Actual current082 blouse/skin ownership, not an old pose or constructed body.
b=B.astype(int)
blue=(b[:,:,2]-b[:,:,0]>45)&(b[:,:,2]-b[:,:,1]>28)&(b[:,:,1]-b[:,:,0]>14)&(b[:,:,3]>0)&(Y<1000)
blue=binary_fill_holes(binary_closing(blue,iterations=2));blue=binary_dilation(blue,iterations=2)
skin=(b[:,:,0]-b[:,:,2]>20)&(b[:,:,3]>0)&(Y<1020)
upper=(Y<820)|(X>750)|blue|binary_dilation(skin,iterations=2)

# Complete semantic knee bend / upper-shin fold valley. Moving cloth owns the
# ENTIRE rounded knee faces to its right, down to real contact, not y1210.
valley=np.array([[1070,225],[1085,235],[1098,270],[1112,315],[1130,360],[1150,400],[1170,445],[1190,485],[1215,520],[1245,550],[1270,552],[1290,540],[1304,540],[1315,560],[1350,580],[1535,580]],float)
valleyX=np.interp(np.arange(1536),valley[:,0],valley[:,1])
shin=(Y>=1070)&(X<=valleyX[Y])
# All actual ankle/shoe pixels and their surrounding static empty space remain
# at original native coordinates, including both shoe-outline exteriors.
feet=np.asarray(Image.open(R/'F078_FIXED074_SUPPORTS_ZERO_CALL_20261019/masks/ORIGINAL074_SHOES_ANKLES_HARD.png').convert('L'))>0
shoe_blank=(Y>=1060)&(X<235)
feet_guard=binary_dilation(feet,iterations=4)|shoe_blank
# Physical original contact band, not an immutable whole circle of knee cloth.
contact=np.zeros_like(shin)
for x in range(220,651):
 ys=np.flatnonzero(old[:,x,3]>=128)
 if len(ys):
  base=int(ys.max())
  if base>=1290:contact[max(0,base-1):min(1536,base+2),x]=True
fixed_support=(shin|feet_guard|contact)&~upper
pants_domain=(Y>=820)&(X<=750)&~upper
moving=pants_domain&~fixed_support
# Clear the old bad pants silhouette; replace the complete new pants in one
# ownership operation. All actual raw knee outer alpha is kept, not trimmed
# against old074's knee outline. Static semantic shin/contact is separate.
n=B.copy();n[pants_domain]=0
n[fixed_support]=support[fixed_support]
n[feet_guard&~upper]=B[feet_guard&~upper]
n[contact&~upper]=old[contact&~upper]
n[moving]=P[moving]

# 2native at visible fabric-to-fabric semantic edges only; no shape filling.
dist=distance_transform_edt(moving)
edge=moving&(dist<2.01)&(P[:,:,3]>16)&(B[:,:,3]>16)
edge_upper=edge&binary_dilation(upper,iterations=2)
edge_shin=edge&binary_dilation(fixed_support,iterations=2)
for own,baseline in [(edge_upper,B),(edge_shin,support)]:
 valid=own&(baseline[:,:,3]>16)
 w=np.clip(dist/2,0,1)
 for c in range(4):n[:,:,c][valid]=np.uint8(np.rint(w[valid]*P[:,:,c][valid]+(1-w[valid])*baseline[:,:,c][valid]))
assert np.array_equal(n[upper],B[upper])
assert np.array_equal(n[feet_guard&~upper],B[feet_guard&~upper])
Image.fromarray(n).save(O/'candidate/F082.png')
for name,mask in [('CURRENT082_UPPER_ARMS_HANDS_UNCHANGED',upper),('STATIC074_SHINS_ANKLES_SHOES_CONTACT_SEMANTIC',fixed_support),('MOVING_COMPLETE_PANTS_FULL_BOTH_KNEES',moving),('SHOE_AND_SURROUNDING_EMPTY_HARD_PROTECT',feet_guard),('PHYSICAL074_CONTACT_BAND',contact),('ONLY_2PX_REAL_CONNECTION_CORRIDORS',edge_upper|edge_shin)]:Image.fromarray(np.uint8(mask)*255).save(O/f'geometry/{name}.png')
fgpath=A/'layers/F082_FG_true_front_fingers.png';fg=np.asarray(Image.open(fgpath).convert('RGBA'));own=fg[:,:,3]>0
assert np.array_equal(n[own],B[own]);bg=n.copy();bg[own]=0
Image.fromarray(bg).save(O/'layers/F082_BG_person.png');shutil.copy2(fgpath,O/'layers/F082_FG_true_front_fingers.png')
assert np.array_equal(np.maximum(bg,fg),n)
static=np.zeros_like(n);static[fixed_support]=n[fixed_support]
activity=n.copy();activity[fixed_support]=0
Image.fromarray(static).save(O/'layers/F082_STATIC_REAL074_SUPPORTS.png');Image.fromarray(activity).save(O/'layers/F082_ACTIVITY_AND_UNCHANGED_UPPER.png')
assert np.array_equal(np.maximum(static,activity),n)

font=lambda s:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',s)
def solid(im):
 z=Image.new('RGBA',im.size,'#e1e4e6');z.alpha_composite(im);return z.convert('RGB')
solid(Image.fromarray(n)).crop((150,800,760,1380)).save(O/'diagnostics/REJOIN_COMPLETE_WAIST_BOTH_KNEES_1to1.png')
board=Image.new('RGB',(2440,620),'#e1e4e6');d=ImageDraw.Draw(board)
for i,(name,im) in enumerate([('ORIGINAL082 whole raw',raw),('BEFORE082 old ownership',Image.fromarray(B)),('ONE whole-pants rejoin',Image.fromarray(n)),('FINAL074 support only comparison',Image.fromarray(old))]):
 board.paste(solid(im).crop((150,800,760,1380)),(610*i,40));d.text((610*i+8,10),name,font=font(18),fill='#25313b')
board.save(O/'diagnostics/RAW_BEFORE_ONE_REJOIN_FINAL074_SAME_NATIVE.png')
target=solid(Image.fromarray(n));d=ImageDraw.Draw(target)
curve=[(float(valleyX[y]),y) for y in range(1070,1340,4)]
d.line(curve,fill='#cc33aa',width=3)
d.text((20,20),'ONE ACTUAL WHOLE-PANTS REJOIN / COMPLETE KNEE JOIN TARGET',font=font(22),fill='#25313b')
d.text((20,55),'Real raw pixels only. Any gap/fold mismatch needs review; no new art.',font=font(19),fill='#25313b')
d.text((20,1420),'Purple: true knee-bend / upper-shin valley. Full round knees retained.',font=font(19),fill='#76258e')
target.save(O/'reference/COMPLETE_BOTH_KNEES_WAIST_AND_FIXED_SHINS_JOIN_TARGET_ONLY.png')

registered_controls=np.c_[src,np.ones(len(src))]@M.T
full_knee_native=np.asarray(Image.fromarray(np.uint8(whole_knees)*255).transform((1024,1536),Image.Transform.AFFINE,tuple(I.ravel()),Image.Resampling.NEAREST))>0
removed_knee_pixels=full_knee_native&(P[:,:,3]>16)&~moving
proof={'status':'ONE_ZERO_IMAGEGEN_COMPLETE_PANTS_REJOIN_FOR_ACTUAL_CANVAS_NOT_QUALIFIED',
 'source_actual_raw_SHA256':sha(rawpath),'unchanged_upper_source_SHA256':sha(A/'candidate/F082.png'),'source_original074_SHA256':sha(S/'candidate/F074.png'),'candidate_SHA256':sha(O/'candidate/F082.png'),
 'one_whole_pants_raw_to_native_matrix':M.tolist(),'one_similarity_attempt':1,'uniform_scale':scale,'rotation_degrees':math.degrees(math.atan2(rot[1,0],rot[0,0])),'translation_native':translation.tolist(),
 'all_control_residuals':[{'name':v[0],'source':v[1],'target':v[2],'registered':p.tolist(),'residual_native':(p-np.asarray(v[2])).tolist()} for v,p in zip(controls,registered_controls)],
 'no_body_or_crotch_mesh_or_per_knee_warps':True,'top_waist_actual_pixel_constraints_not_bone_measurements':True,'semantic_valley_y_x_anchors':valley.tolist(),'y1210_horizontal_cut_requirement_removed':True,
 'current082_upper_full_arms_hand_RGBA_changes':0,'current082_FG_byte_identical':sha(fgpath)==sha(O/'layers/F082_FG_true_front_fingers.png'),'shoes_ankles_surrounding_empty_RGBA_changes':0,
 'protected_contact_band_RGBA_changes':int(np.any(n[contact&~upper]!=old[contact&~upper],axis=1).sum()),'complete_knee_context_overlap_with_static_semantic_shin_or_contact_pixels':int(removed_knee_pixels.sum()),'complete_knee_context_overlap_note':'Includes intentionally nonadopted adjacent shin context. No trimming against old knee silhouette; no old-outline alpha shaving rule.',
 'new_reference_pixels_adopted':0,'new_imagegen_calls':0,'new_actual082_Canvas':0,'next086_imagegen_calls':0,'new_qualified_action_states':0,'post_fit_mask_trials':0}
(O/'geometry/ONE_WHOLE_PANTS_SIMILARITY_SEMANTIC_SUPPORT_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps({k:v for k,v in proof.items() if k!='all_control_residuals'},indent=2))
