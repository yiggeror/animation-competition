"""Complete approved local union from sole actual094 local raw.
Native frame already agrees: identity, no fit or separate limb/hand movement.
Every adopted RGBA is real raw; every protected RGBA is selected real body.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib
from scipy.ndimage import binary_fill_holes,label
O=Path(__file__).resolve().parents[1];R=O.parent;P=R/'F094_LOCAL_REPAIR_INPUT_FROM_BODY_ONLY_DIAGNOSTIC_20261019'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (O/'actual_scene/F094_canvas.png').exists(),'Reviewed actual Canvas exists; no overwrite'
rawpath=O/'originals/F094_local_arms_knees_call01_raw.png';assert sha(rawpath)=='fcb4d4b52f259c7b5fc9ee63473203fa4b70778a4edb19a756ac7f5389c21f74'
raw=Image.open(rawpath).convert('RGBA');A=np.asarray(raw);bodypath=P/'body_diagnostic/BODY_DIAGNOSTIC_NATIVE_WITH_FAILED_ARMS_VISIBLE.png';B=np.asarray(Image.open(bodypath).convert('RGBA'))
protect=np.asarray(Image.open(P/'masks/HARD_PROTECTED_BODY_COLLAR_WAIST_PANTS_SUPPORT.png').convert('L'))>0;allowed=~protect
assert np.array_equal(allowed,np.asarray(Image.open(P/'masks/ALLOW_UNION_LOCAL_REPAIR.png').convert('L'))>0)
Y,X=np.mgrid[:1536,:1024]
def bbox(alpha,mask):
 y,x=np.where((alpha>128)&mask);return [int(x.min()),int(y.min()),int(x.max()),int(y.max())]
head=(Y<390)&(X>300);ab=bbox(A[:,:,3],head);bb=bbox(B[:,:,3],head)
frame={'source_head_alpha_bbox':ab,'fixed_body_head_alpha_bbox':bb,'bbox_deltas':(np.array(ab)-np.array(bb)).tolist(),
 'decision':'Native1024 frame visually/body-contour aligned; retain identity. No source similarity regression required. Fixed real body never transformed.',
 'source_coordinate_matrix':[[1,0,0],[0,1,0]],'nonidentity_source_regressions':0,'new_fixed_body_registrations':0}
(O/'geometry/SOURCE_NATIVE_FRAME_IDENTITY_DECISION.json').write_text(json.dumps(frame,indent=2)+'\n')
n=B.copy();n[allowed]=A[allowed];Image.fromarray(n).save(O/'candidate/F094.png')
assert np.array_equal(n[allowed],A[allowed]) and np.array_equal(n[protect],B[protect])
# Actual new raw front digits, using the same unchanged native coordinates.
# These polygons partition real fingers only; they never deform or translate.
frontpolys={'L_far_jade_actual_front_curled_digits':[(882,582),(904,582),(919,596),(920,620),(908,642),(885,643),(873,626),(881,608)],
 'R_near_bare_actual_front_curled_digits':[(914,741),(936,732),(951,744),(953,770),(941,793),(920,800),(908,786),(915,769)]}
front=Image.new('L',raw.size);d=ImageDraw.Draw(front)
for p in frontpolys.values():d.polygon(p,fill=255)
own=(np.asarray(front)>0)&allowed;fg=np.zeros_like(n);fg[own]=n[own];bg=n.copy();bg[own]=0
Image.fromarray(bg).save(O/'layers/F094_BG_person.png');Image.fromarray(fg).save(O/'layers/F094_FG_true_front_fingers.png')
assert np.array_equal(np.maximum(bg,fg),n) and not np.any((bg[:,:,3]>0)&(fg[:,:,3]>0))
hard=np.asarray(Image.open(P/'masks/HARD_ACTUAL_POSITIVE_SHINS_AND_SHOE_AIR.png').convert('L'))>0;collar=np.asarray(Image.open(P/'masks/HARD_ORIGINAL_COLLAR_AND_CENTRAL_CHEST.png').convert('L'))>0
assert np.array_equal(n[hard],B[hard]) and np.array_equal(n[collar],B[collar]);assert np.array_equal(n[Y<390],B[Y<390]);assert np.array_equal(n[(Y>=850)&(Y<1030)],B[(Y>=850)&(Y<1030)])
holes=binary_fill_holes(n[:,:,3]>128)&(n[:,:,3]<32)&allowed
lab,count=label(holes);components=[]
for i in range(1,count+1):
 y,x=np.where(lab==i)
 if len(x):components.append({'pixels':len(x),'bbox':[int(x.min()),int(y.min()),int(x.max()),int(y.max())]})
proof={'status':'COMPLETE_NATIVE_LOCAL_SOURCE_ADOPTED_REAL_RGBA_VISUAL_REVIEW_PENDING','raw_SHA256':sha(rawpath),'body_base_SHA256':sha(bodypath),'native_SHA256':sha(O/'candidate/F094.png'),
 'source_alignment':frame,'allowed_union_SHA256':sha(P/'masks/ALLOW_UNION_LOCAL_REPAIR.png'),'protected_domain_SHA256':sha(P/'masks/HARD_PROTECTED_BODY_COLLAR_WAIST_PANTS_SUPPORT.png'),
 'adopted_new_source_RGBA_differences':0,'protected_body_RGBA_changes':0,'whole_original_collar_chest_RGBA_changes':0,'head_neck_RGBA_changes':0,'waist_hips_main_pants_RGBA_changes':0,'actual_shin_ankle_shoe_neighbor_air_RGBA_changes':0,
 'sparse_patch_composition':False,'garment_color_thresholds':False,'pre_motion_arm_subtraction':False,'source_alpha_preserved_complete_RGBA':True,
 'technical_reference_pixels_adopted':0,'new_imagegen_calls_this_task':1,'local_raw_count':1,'actual_local094_Canvas':0,'new098_calls':0,
 'new_internal_low_alpha_components_for_review':components,'actual_raw_front_digit_polygons':frontpolys,'BG_FG_reconstruction_differences':0,'BG_FG_overlap':0}
(O/'geometry/COMPLETE_SEMANTIC_LOCAL_SOURCE_AND_HARD_BODY_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n')
def solid(im):
 q=Image.new('RGBA',raw.size,'#e1e4e6');q.alpha_composite(im);return q.convert('RGB')
solid(Image.fromarray(n)).save(O/'diagnostics/ADOPTED_REAL_LOCAL_ARMS_KNEES_FIXED_BODY_NATIVE.png')
solid(Image.fromarray(n)).crop((430,360,990,850)).save(O/'diagnostics/NATIVE_COMPLETE_COLLAR_SHOULDER_ELBOW_WRIST_PALMS.png')
solid(Image.fromarray(n)).crop((250,1015,765,1330)).save(O/'diagnostics/NATIVE_COMPLETE_KNEES_UPPER_SHIN_RETURN.png')
print(json.dumps({'native_SHA256':proof['native_SHA256'],'head_bbox_source_fixed':{k:v for k,v in frame.items() if 'bbox' in k},'protected_RGBA_changes':0,'adopted_raw_RGBA_differences':0,'internal_holes':components,'source_regressions':0,'fixed_body_registrations':0},indent=2))
