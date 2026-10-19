"""Sole authorized complete navy-pants drawing; native identity registration.
Protect exact current upper/grips/shoes/blank. Redraw knee/shin fold bands and
the original contact contour's bounded3px neighborhood; no old ink arc pasted.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,shutil
from scipy.ndimage import binary_opening,binary_closing,binary_fill_holes,binary_dilation,label,distance_transform_edt

O=Path(__file__).resolve().parents[1];R=O.parent;M=R/'F082_WHOLE_PANTS_REJOIN_ZERO_CALL_ONCE_20261019';A=R/'F082_ACTIVE_actual_call01_20261019';S=R/'F074_PANTS_LOCAL_actual_call01_20261019'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (O/'candidate/F082.png').exists(),'Sole adoption already exists; no second registration/mask trial.'
src=O/'originals/F082_COMPLETE_PANTS_JOIN_call01_raw.png';assert sha(src)=='54764bde50dbf8a5aa1fc2dfe3ea3f453ea49ad82af8897bcab08d53a401f0ba'
raw=Image.open(src).convert('RGBA');Q=np.asarray(raw);q=Q.astype(int)
B=np.asarray(Image.open(M/'candidate/F082.png').convert('RGBA'));old=np.asarray(Image.open(S/'candidate/F074.png').convert('RGBA'))
assert sha(M/'candidate/F082.png')=='a8360b1ff4cc87b6ffe07ae9f1e0b6d50cb58467fc6f15ca008eecc2c9897b1e'
Y,X=np.mgrid[:1536,:1024]
# Model returned the exact full1024x1536 placement; source ankles/cuffs and
# contact are in native coordinates. One whole identity similarity is used.
# Do not pull a knee/waist/cuff independently or re-fit against broken gaps.
matrix=np.array([[1.,0.,0.],[0.,1.,0.]])
navy=(q[:,:,2]-q[:,:,0]>7)&(q[:,:,2]-q[:,:,1]>7)&(q[:,:,2]<150)&(q[:,:,1]-q[:,:,0]<30)&(q[:,:,3]>24)&(Y>=820)&(X<760)
core=binary_opening(navy,iterations=1);labs,k=label(core);areas=np.bincount(labs.ravel());keep=np.flatnonzero(areas>15000);keep=keep[keep!=0];assert len(keep)==1
material=binary_fill_holes(binary_closing(np.isin(labs,keep),iterations=2));material=binary_dilation(material,iterations=2)&(Q[:,:,3]>0)
# Entire actual rounded knee alpha retained, never shaved to an old silhouette.
all_knees=(X>=470)&(X<=750)&(Y>=1020)&(Y<=1350)
material[all_knees]=Q[:,:,3][all_knees]>0
P=np.zeros_like(Q);P[material]=Q[material]
Image.fromarray(P).save(O/'layers/WHOLE_ACTUAL_NEW_PANTS_NATIVE_IDENTITY.png')
Image.fromarray(np.uint8(material)*255).save(O/'geometry/RAW_ACTUAL_COMPLETE_PANTS_SEMANTIC_MATERIAL.png')
readmask=lambda name:np.asarray(Image.open(M/f'geometry/{name}.png').convert('L'))>0
previousUpper=readmask('CURRENT082_UPPER_ARMS_HANDS_UNCHANGED')
# Preserve actual blouse/ink pixels; accidental transparent waist gaps beneath
# it may be filled by the newly painted pants, not frozen as empty upper art.
upper=(previousUpper&(B[:,:,3]>0))|(Y<820)|(X>750)
feet=readmask('SHOE_AND_SURROUNDING_EMPTY_HARD_PROTECT')
previousMoving=readmask('MOVING_COMPLETE_PANTS_FULL_BOTH_KNEES')
g0=json.loads((M/'geometry/ONE_WHOLE_PANTS_SIMILARITY_SEMANTIC_SUPPORT_PROOF.json').read_text())
curve=np.asarray(g0['semantic_valley_y_x_anchors'])
cx=np.interp(np.arange(1536),curve[:,0],curve[:,1])
line=Image.new('L',(1024,1536));d=ImageDraw.Draw(line)
d.line([(float(cx[y]),y) for y in range(1060,1320)],fill=255,width=1)
foldDistance=distance_transform_edt(np.asarray(line)==0)
foldBand=(foldDistance<=14)&(Y>=1060)&(Y<=1320)
# Original actual floor contact is a geometric centreline, not the frozen
# old1-2pixel ink strip. New real contour/AA may replace it within3native.
ground=np.zeros((1536,1024),bool)
for x in range(220,651):
 ys=np.flatnonzero(old[:,x,3]>=128)
 if len(ys) and ys.max()>=1290:ground[int(ys.max()),x]=True
groundDistance=distance_transform_edt(~ground)
groundBand=groundDistance<=3
pantsDomain=(Y>=820)&(X<=750)&~upper
waistGap=pantsDomain&previousUpper&(B[:,:,3]==0)
adopt=(previousMoving|foldBand|groundBand|waistGap)&pantsDomain&~feet
# All old erroneous active-contour pixels, including the detached new arc,
# belong to the coherent replacement; no old contact-band pixels are restored.
n=B.copy();n[adopt]=P[adopt]
dist=distance_transform_edt(adopt)
# <=2native actual-fabric joins only, wholly inside the authorized domain.
# Never blend the detached/ground ink arc back into the new rounded contour.
join=adopt&(dist<2.01)&(P[:,:,3]>32)&(B[:,:,3]>32)&~binary_dilation(groundBand,iterations=3)
w=np.clip(dist/2,0,1)
for c in range(4):n[:,:,c][join]=np.uint8(np.rint(w[join]*P[:,:,c][join]+(1-w[join])*B[:,:,c][join]))
assert np.array_equal(n[~adopt],B[~adopt]);assert np.array_equal(n[upper],B[upper]);assert np.array_equal(n[feet],B[feet])
Image.fromarray(n).save(O/'candidate/F082.png')
for name,m in [('WHOLE_NEW_PANTS_ALLOWED_WITH_NATURAL_FOLD_AND_3PX_CONTACT',adopt),('UPPER_BLUE_ARMS_HANDS_HARD_PROTECT',upper),('SHOE_ANKLE_AND_SURROUNDING_EMPTY_HARD_PROTECT',feet),('NATURAL_FOLD_VALLEY_BOTH_SIDES_14PX',foldBand),('ORIGINAL074_ACTUAL_GROUND_CONTOUR_CENTRELINE',ground),('ORIGINAL_GROUND_CONTOUR_BOUNDED_3PX_REDRAW',groundBand),('ONLY_2PX_ACTUAL_FABRIC_JOIN_INSIDE_DOMAIN',join)]:Image.fromarray(np.uint8(m)*255).save(O/f'geometry/{name}.png')
fgsrc=A/'layers/F082_FG_true_front_fingers.png';fg=np.asarray(Image.open(fgsrc).convert('RGBA'));own=fg[:,:,3]>0;assert np.array_equal(n[own],B[own]);bg=n.copy();bg[own]=0
Image.fromarray(bg).save(O/'layers/F082_BG_person.png');shutil.copy2(fgsrc,O/'layers/F082_FG_true_front_fingers.png');assert np.array_equal(np.maximum(bg,fg),n)
activity=n.copy();activity[~adopt]=0;fixed=n.copy();fixed[adopt]=0
Image.fromarray(activity).save(O/'layers/F082_ONE_NEW_COMPLETE_SEMANTIC_PANTS.png');Image.fromarray(fixed).save(O/'layers/F082_HARD_FIXED_CURRENT_UPPER_AND074_SUPPORTS.png');assert np.array_equal(np.maximum(activity,fixed),n)
font=lambda s:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',s)
def solid(a):
 im=Image.fromarray(a);s=Image.new('RGBA',im.size,'#e1e4e6');s.alpha_composite(im);return s.convert('RGB')
solid(n).crop((150,800,750,1350)).save(O/'diagnostics/NEW_COMPLETE_PANTS_NORMAL_SIZE.png')
board=Image.new('RGB',(1800,590),'#e1e4e6');d=ImageDraw.Draw(board)
for i,(name,a) in enumerate([('SOLE INPUT / before repair',B),('TRUE NEW RAW / identity',Q),('ADOPTED new pants + fixed context',n)]):board.paste(solid(a).crop((150,800,750,1350)),(600*i,40));d.text((600*i+8,10),name,font=font(18),fill='#25313b')
board.save(O/'diagnostics/SAME_NATIVE_BEFORE_TRUE_RAW_ADOPTED_PANTS.png')
fixedEmpty=feet&(B[:,:,3]==0)
changed=np.any(n!=B,axis=2)
g={'status':'SOLE_TRUE_COMPLETE_PANTS_JOIN_ADOPTED_ONE_ACTUAL082_CANVAS_PENDING',
 'untouched_raw_SHA256':sha(src),'sole_pose_mother_SHA256':sha(M/'candidate/F082.png'),'native_candidate_SHA256':sha(O/'candidate/F082.png'),
 'one_whole_patch_raw_to_native_matrix':matrix.tolist(),'uniform_scale':1.,'rotation_degrees':0.,'translation_native':[0.,0.],
 'registration_reason':'Exact requested1024x1536 native canvas returned; cuffs and actual grounded contour already native-aligned. Use one identity similarity, no refit or local deformation.',
 'allowed_pixels':int(adopt.sum()),'changed_RGBA_pixels':int(changed.sum()),'outside_allowed_RGBA_changes':int(changed[~adopt].sum()),'upper_blouse_full_arms_hands_RGBA_changes':0,'FG_byte_identical':sha(fgsrc)==sha(O/'layers/F082_FG_true_front_fingers.png'),
 'shoe_ankle_surrounding_empty_RGBA_changes':0,'new_alpha_in_protected_shoe_blank':int(np.count_nonzero(n[:,:,3][fixedEmpty])),
 'natural_fold_valley_semantic_band_halfwidth_native':14,'ground_redraw_band_bound_native':3,'old_contact_strip_reinserted':False,'ground_band_adopted_pixels':int((adopt&groundBand).sum()),
 '2native_fabric_join_pixels_inside_allowed_only':int(join.sum()),'separate_knee_shin_shoe_warps':0,'raw_RGBA_material_or_alpha_edits':0,'constructed_reference_pixels_adopted':0,
 'BG_FG_and_new_pants_fixed_context_RGBA_reconstruction_differences':0,'post_adoption_mask_trials':0,'imagegen_calls':1,'actual082_Canvas':0,'next086_calls':0}
(O/'geometry/ONE_WHOLE_TRUE_PANTS_ADOPTION_AND_HARD_PROTECTION.json').write_text(json.dumps(g,indent=2)+'\n')
print(json.dumps(g,indent=2))
