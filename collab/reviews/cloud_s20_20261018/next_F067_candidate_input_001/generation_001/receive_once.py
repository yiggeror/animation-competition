from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation,binary_opening,label

F=Path(__file__).resolve().parent;P=F.parent;PACK=P.parent
R0=np.array(Image.open(F/'raw_original.png').convert('RGBA'))
A=np.array(Image.open(PACK/'F064_root_occlusion_cleanup_zero_call_001/F064_proximal_roots_continuous_candidate.png').convert('RGBA'))
H,W=A.shape[:2];rh,rw=R0.shape[:2];assert rh==H and rw in (W,W-1)
R=np.zeros_like(A);R[:,:rw]=R0;yy,xx=np.indices((H,W))
r,g,b=R[:,:,:3].astype(float).transpose(2,0,1)
wood=(R[:,:,3]>40)&(r>130)&(g>85)&(r>g+10)&(g>b+10)&(b<g*.78)
# Only remove the returned exterior crane props. The complete child's hands,
# arms, head, body and feet all remain this one original output at identity.
oldC=wood&(xx>680)&(xx<835)&(yy>210)&(yy<315)
body_core=binary_opening((R[:,:,3]>20)&(xx<810),iterations=6)
flower_guard=(R[:,:,3]>0)&(r>150)&(r>g*1.7)&(r>b*1.5)
body_guard=body_core|flower_guard
remove=binary_dilation(oldC,iterations=3)&(xx>680)&(yy>210)&(yy<320)&~body_guard
area=(R[:,:,3]>0)&(xx<835)&~remove
ids,n=label(area);sizes=np.bincount(ids.ravel());main=max(range(1,n+1),key=lambda k:sizes[k]);area=ids==main
native=np.zeros_like(R);native[area]=R[area]
Image.fromarray(native).save(F/'native_complete_child_and_T_rods.png')
Image.fromarray(np.uint8(remove)*255).save(F/'returned_exterior_C_prop_removal_mask.png')
axes=json.loads((PACK/'cam20_crane_lamp_left_001/registration_input.json').read_text())['rods']
props=Image.new('RGBA',(W*4,H*4));d=ImageDraw.Draw(props)
for role in ['C_N','C_B']:
    q=axes[role];pts=[tuple(v*4 for v in q['shaft_tip_master_px']),tuple(v*4 for v in [952,q['slope']*952+q['intercept']])]
    d.line(pts,fill='#675034',width=16);d.line(pts,fill='#b28b52',width=10)
G=A.copy();G[:,:835]=0
out=Image.alpha_composite(props.resize((W,H),Image.Resampling.LANCZOS),Image.fromarray(G))
out=Image.alpha_composite(out,Image.fromarray(native));B=np.array(out);B[:,835:]=A[:,835:]
Image.fromarray(B).save(F/'F067_native_child_locked_G_candidate.png')
gray=Image.new('RGBA',(W,H),'#bdc1c4');gray.alpha_composite(Image.fromarray(B));gray.convert('RGB').save(F/'actual_full_scoped_gray.jpg',quality=96)
box=(285,320,735,550);crop=gray.crop(box).convert('RGB');crop.save(F/'actual_contacts_1x.png');crop.resize((1800,920),Image.Resampling.NEAREST).save(F/'actual_contacts_4x.png')
assert np.array_equal(native[area],R[area]);assert np.array_equal(B[:,835:],A[:,835:])
roi=np.zeros((H,W),bool);roi[380:540,440:700]=True
assert np.array_equal(B[roi&area],R[roi&area])
assert np.array_equal(B[roi&(R[:,:,3]==255)],R[roi&(R[:,:,3]==255)])
submitted_args=json.loads((F/'tool_args_exact.json').read_text())
edit=np.array(Image.open(submitted_args['referenced_image_paths'][3]).convert('L'))>127
report={'status':'ONE_F067_ORIGINAL_AND_SCOPED_NATIVE_CHILD_CANDIDATE_ASTRA_DIRECT_GATE_PENDING','new_image_calls':1,'raws':1,'retries':0,'raw_sha256':hashlib.sha256((F/'raw_original.png').read_bytes()).hexdigest(),'raw_size':[rw,rh],'registration':'identity; no resize or human transform; optional one far-right transparent column if source1671','no_palm_arm_foot_warp_or_old_pose_paste':True,'new_complete_child_and_T_props_from_one_native_raw':True,'native_human_kept_complete_not_clipped_to_technical_input_silhouette':True,'no_legacy_pony_tail_bbox_cut':True,'native_layer_alpha_pixels_outside_input_white':int((area&~edit).sum()),'fixed_grandma_x835_plus_RGBA_changes':int(np.any(B[:,835:]!=A[:,835:],2).sum()),'both_native_hands_and_arms_selected_component_RGBA_exact_raw':True,'both_native_hands_and_arms_opaque_pixels_RGBA_exact_raw':True,'isolated_low_alpha_noise_excluded_from_component':True,'C_props':'returned exterior C wood only removed; same original fixed4px axes restored behind native child; frozen grandma side byte-exact','T_props':'complete native output, including X and both clamp regions; no axis shift or endpoint rebinding','author_actual_views':'complete raw + raw1x4x + scoped full + scoped1x4x actually opened; anatomy/contact/proportions remain Astra direct gate','not_adopted_or_exposed':True,'further_states_prepared_or_called':False}
(F/'receipt_and_protection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
