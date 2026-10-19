"""Sole authorized same-raw semantic rejoin; exact two whole-arm translations.
Complete original collar/chest is one piece. Real pixels only, no new model.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib
O=Path(__file__).resolve().parents[1];R=O.parent;L=R/'F090_TWO_ARMS_LOCAL_actual_call01_20261019';M=R/'F090_COMPLETE_actual_call01_20261019'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (O/'candidate/F090.png').exists(),'Only one rejoin authorized; do not repeat'
assert sha(L/'originals/F090_two_arms_call01_raw.png')=='b664008d0481f15df4a55c39ba26aa8ba666f8ba449903ad5c7ce1f5aa00d5e8'
assert sha(M/'candidate/F090.png')=='0f1caa9edf588cdf525b728770a9079ac97b01c81ff09a398ec468add59ee209'
body=Image.open(M/'candidate/F090.png').convert('RGBA');B=np.asarray(body)
new=Image.open(L/'geometry/ONE_LOCAL_PATCH_REGISTERED_RAW_NOT_WHOLE_BODY_ADOPTED.png').convert('RGBA');A=np.asarray(new)
g=json.loads((L/'geometry/ONE_COMPLETE_LOCAL_PATCH_REGISTRATION_AND_ALL_RESIDUALS.json').read_text());F=np.asarray(g['local_patch_only_similarity_matrix'])
shift={'R':[14.086744,.620598],'L':[-14.038403,2.519830]}
arm_polys_raw={
 'R':[(410,480),(430,450),(480,445),(530,470),(575,515),(625,570),(651,620),(647,650),(720,695),(820,753),(910,791),(1023,792),(1023,940),(860,940),(740,861),(650,798),(575,740),(527,780),(493,733),(465,680),(432,615),(408,550)],
 'L':[(500,465),(550,460),(600,487),(640,515),(685,542),(725,565),(743,605),(835,619),(900,619),(962,620),(1023,620),(1023,788),(925,788),(870,741),(797,722),(731,699),(680,669),(630,629),(580,570),(535,529)]}
collar=[(462,361),(511,348),(559,371),(588,410),(626,434),(665,453),(684,478),(666,499),(686,532),(691,566),(681,598),(650,617),(615,601),(582,570),(556,537),(534,491),(494,454),(462,423)]
ownership=[(460,414),(540,414),(602,440),(674,464),(735,525),(1023,555),(1023,874),(922,874),(834,874),(725,842),(650,790),(570,742),(513,674),(458,565)]
underarm=[(445,500),(490,504),(512,585),(535,651),(568,703),(590,730),(578,763),(505,737),(475,675),(446,618)]
def at(p):return np.c_[np.asarray(p),np.ones(len(p))]@F.T
def mask(poly):
 z=Image.new('L',body.size);ImageDraw.Draw(z).polygon([tuple(x) for x in poly],fill=255);return np.asarray(z)>0
arms={k:mask(at(v)) for k,v in arm_polys_raw.items()};arms['L']&=~arms['R']
whole=mask(ownership);Y,X=np.mgrid[:1536,:1024];whole&=(Y>=405)&(Y<875)&~((X<450)&(Y>760))
collarmask=mask(collar)
under=mask(underarm)&whole
# Only the real new exposed shirt surface, never an unshifted second skin arm.
under&=(A[:,:,2]>A[:,:,0]*1.1)&(A[:,:,2]>A[:,:,1]*1.01)&(A[:,:,3]>0)
pre={'status':'ONE_REDEFINED_COMPLETE_SEMANTIC_OWNERSHIP_NO_SEARCH','source_raw_SHA256':sha(L/'originals/F090_two_arms_call01_raw.png'),'current_registered_new_raw_SHA256':sha(L/'geometry/ONE_LOCAL_PATCH_REGISTERED_RAW_NOT_WHOLE_BODY_ADOPTED.png'),
 'old_real090_body_SHA256':sha(M/'candidate/F090.png'),'arm_masks_raw_coordinates_before_existing_local_matrix':arm_polys_raw,'single_collar_and_central_chest_original_piece_native':collar,
 'complete_old_new_arm_ownership_native':ownership,'required_real_new_underarm_cloth_native':underarm,'exact_complete_arm_translation_native':shift,
 'no_new_whole_fit':True,'no_new_local_patch_fit':True,'scale_new_arm_blocks':1,'rotation_new_arm_blocks':0,'head_neck_and_y_ge875_waist_pants_support_protected':True,
 'same_source_rejoin_attempts':1,'model_calls':0,'new094_calls':0,'layer_order':'old real body outside ownership / new underarm cloth / whole translated far LEFT / one complete old collar+chest / whole translated near RIGHT'}
(O/'geometry/PREDECLARED_ONE_OWNERSHIP_AND_EXACT_TRANSLATIONS.json').write_text(json.dumps(pre,indent=2)+'\n')
base=B.copy();base[whole]=0
def portion(a,m):
 z=np.zeros_like(a);z[m]=a[m];return Image.fromarray(z)
out=Image.fromarray(base);out.alpha_composite(portion(A,under))
blocks={}
for r in ['L','R']:
 im=portion(A,arms[r]);dx,dy=shift[r];im=im.transform(body.size,Image.Transform.AFFINE,(1,0,-dx,0,1,-dy),Image.Resampling.BICUBIC);blocks[r]=im;im.save(O/f'layers/{r}_WHOLE_REAL_ARM_EXACT_TRANSLATION.png')
out.alpha_composite(blocks['L']);out.alpha_composite(portion(B,collarmask));out.alpha_composite(blocks['R'])
n=np.asarray(out).copy();n[~whole]=B[~whole]
Image.fromarray(n).save(O/'candidate/F090.png');Image.fromarray(np.uint8(whole)*255).save(O/'geometry/ONE_COMPLETE_ARM_AND_COLLAR_OWNERSHIP.png');Image.fromarray(np.uint8(collarmask)*255).save(O/'geometry/ONE_WHOLE_ORIGINAL_COLLAR_AND_CENTRAL_CHEST.png')
# Actual new front finger shapes use the identical complete-arm shift and
# existing local patch matrix. BG and FG are mutually exclusive real pixels.
own=np.zeros(A.shape[:2],bool)
for r,p in g['front_digit_polygons_raw_same_patch_matrix'].items():
 pp=at(p)+shift[r];own|=mask(pp)
own&=whole;fg=np.zeros_like(n);fg[own]=n[own];bg=n.copy();bg[own]=0
Image.fromarray(bg).save(O/'layers/F090_BG_person.png');Image.fromarray(fg).save(O/'layers/F090_FG_true_front_fingers.png');assert np.array_equal(np.maximum(bg,fg),n)
changed=np.any(n!=B,axis=2);assert not changed[~whole].any() and not changed[Y>=875].any() and not changed[Y<405].any()
res={}
for r in ['R','L']:
 src=np.asarray(g['all_shoulder_elbow_wrist_true_grip_residuals'][r+'_true_grip']['registered']);t=np.asarray(g['all_shoulder_elbow_wrist_true_grip_residuals'][r+'_true_grip']['target']);z=src+shift[r]
 res[r]={'true_grip_native':z.tolist(),'frozen_target':t.tolist(),'residual_native':(z-t).tolist(),'error_native':float(np.linalg.norm(z-t)),'scene':(.7*z+np.array([275,112])).tolist()}
proof={'status':'SOLE_SAME_RAW_REAL_PIXEL_REJOIN_ACTUAL_VISUAL_REVIEW_REQUIRED','native_SHA256':sha(O/'candidate/F090.png'),'source_local_raw_SHA256':pre['source_raw_SHA256'],'exact_whole_arm_translation_native':shift,'grip_results':res,
 'new_model_calls':0,'same_source_rejoins':1,'new_global_or_local_fits':0,'new_arm_block_scales':1,'new_arm_block_rotations':0,'per_hand_finger_transformations':0,
 'head_neck_RGBA_changes':int(changed[Y<405].sum()),'waist_hips_pants_support_RGBA_changes':int(changed[Y>=875].sum()),'outside_single_complete_ownership_RGBA_changes':int(changed[~whole].sum()),'changed_RGBA_pixels':int(changed.sum()),'technical_pixels_adopted':0,'new094_calls':0,'actual090_Canvas':0,
 'whole_original_collar_piece_selected_once':True,'two_original_flaps_and_chest_not_isolated_tip':True}
(O/'geometry/ONE_SAME_RAW_REJOIN_AND_TRUE_GRIPS.json').write_text(json.dumps(proof,indent=2)+'\n')
def solid(im):
 z=Image.new('RGBA',im.size,'#e1e4e6');z.alpha_composite(im);return z.convert('RGB')
solid(Image.fromarray(n)).save(O/'diagnostics/SAME_RAW_REJOIN_NATIVE_GREY.png');solid(Image.fromarray(n)).crop((420,330,1010,880)).save(O/'diagnostics/SAME_RAW_FULL_COLLAR_SHOULDER_ELBOW_WRIST_GRIP_NATIVE.png')
print(json.dumps({'native_SHA256':proof['native_SHA256'],'grips':res,'protected_head_waist_support_diff':0,'new_model_calls':0},indent=2))
