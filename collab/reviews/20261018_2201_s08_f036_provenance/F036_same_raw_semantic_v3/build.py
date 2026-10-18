from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
from scipy.ndimage import binary_dilation,map_coordinates
import numpy as np,json,hashlib
O=Path(__file__).resolve().parent
for folder in ['candidates','qa','masks','geometry']:(O/folder).mkdir(exist_ok=True)
R=O.parent;G=R/'F036_input_gate';N=R/'F036_result_registered_nominal'
a=np.array(Image.open(N/'candidates/S08_F036_whole_turn_arms_candidate_RGBA.png').convert('RGBA'));q=np.array(Image.open(N/'registered/F036_registered_scene_patch_RGBA.png').convert('RGBA'));f=np.array(Image.open(G/'inputs/F036_original_underlying_far_hand_SEAT_RGBA.png').convert('RGBA'));n=np.array(Image.open(G/'inputs/F036_preplaced_true_near_hand_match_RGBA.png').convert('RGBA'));H,W=a.shape[:2]
def mask(name):return np.array(Image.open(G/'masks'/name))>0
def poly(points):
 im=Image.new('L',(W,H));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
def save(name,m):Image.fromarray(m.astype('uint8')*255).save(O/'masks'/f'{name}.png')
def comp(bg,fg):return np.array(Image.alpha_composite(Image.fromarray(bg),Image.fromarray(fg)))
nearhard=mask('F036_near_distal_palm_fingers_entire_match_guard.png');farhard=mask('F036_far_visible_hand_jade_TRUE_SEAT_guard.png');box=mask('F036_fixed_table_box_guard.png');w=mask('F036_WHITE_body_neck_head_arms_wrist_allowed.png');b=a.copy()
# Recover the new whole native sleeve, beyond old construction silhouette.
sleeve=poly([(1080,682),(1125,681),(1165,771),(1152,803),(1100,836),(1070,815)])&~(nearhard|farhard|box)
b[sleeve]=q[sleeve];save('RESTORE_same_raw_complete_far_sleeve',sleeve)
# Exact native near-forearm top boundary separating the two real layers.
front=poly([(1010,849),(1060,841),(1090,837),(1120,830),(1150,821),(1180,810),(1207,801),(1220,799),(1220,885),(1070,934),(1000,948)])
# Clear only the native duplicate far hand material above this true front contour.
far_roi=poly([(1103,790),(1140,780),(1154,755),(1194,733),(1227,733),(1268,756),(1268,778),(1228,805),(1185,825),(1120,842),(1104,828)])
rgb=q[:,:,:3].astype(int);skin=(rgb[:,:,0]>rgb[:,:,1]+15)&(rgb[:,:,1]>rgb[:,:,2]+15);jade=(rgb[:,:,1]>rgb[:,:,0]+8)&(rgb[:,:,1]>rgb[:,:,2]);native_far_material=binary_dilation(far_roi&(skin|jade)&(q[:,:,3]>20),iterations=2)&far_roi&~front
b[native_far_material]=0
# Original complete far hand stays below actual foreground forearm, not old proxy corridor.
original_far=(f[:,:,3]>0)&~front
ff=f.copy();ff[~original_far]=0;b=comp(b,ff)
# True empty lever core restored; it is not generalized exterior air.
seat=poly([(1225,758),(1243,758),(1243,776),(1225,776)]);b[seat]=f[seat]
save('CLEAR_native_duplicate_far_material_above_true_front_arm',native_far_material);save('RESTORE_original_far_hand_visible_above_true_front_arm',original_far);save('TRUE_native_forearm_front_occlusion_semantic',front);save('RESTORE_true_transparent_lever_seat',seat)
# Remove all generated duplicate near fingers, wooden match and isolated rod remnants.
near_roi=poly([(1210,777),(1359,771),(1365,839),(1320,884),(1220,888),(1210,861)])
near_restore=(n[:,:,3]>0)&near_roi
clear_near=near_roi&(n[:,:,3]==0)&~(original_far|farhard)
b[clear_near]=0
nn=n.copy();nn[~near_roi]=0
# Preserve original AA by source-over onto cleared background, then hard pixels exactly.
b=comp(b,nn);b[nearhard]=a[nearhard]
# Any partially transparent true near edge uses its original alpha against exterior.
edge_near=near_restore&(n[:,:,3]<255)&~(original_far|front);b[edge_near]=n[edge_near]
save('CLEAR_generated_near_hand_match_and_rod_ghosts',clear_near);save('RESTORE_true_near_distal_hand_AA',near_restore)
# Release only old far-footprint exterior transparency hiding the actual new sleeve and proximal far forearm.
# Genuine exposed jade/flesh, alpha0 finger seat and all actual finger gaps remain protected.
false_air_roi=poly([(1098,692),(1130,692),(1160,766),(1148,790),(1138,800),(1133,814),(1127,826),(1114,837),(1097,832),(1088,811)])
false_air=farhard&(f[:,:,3]==0)&false_air_roi
sleeve_restore=poly([(1080,682),(1125,681),(1165,771),(1140,808),(1114,837),(1082,846),(1070,815)])&~((farhard&~false_air)|nearhard|box)
b[sleeve_restore]=q[sleeve_restore]
# The original jade is laid over this real native skin collar with its original AA.
orig_jade=original_far&poly([(1100,780),(1150,780),(1150,844),(1100,844)])
jj=f.copy();jj[~orig_jade]=0;b=comp(b,jj)
b[farhard&~false_air]=a[farhard&~false_air];b[box]=a[box]
save('RELEASE_false_far_guard_exterior_air_NOT_seat',false_air);save('RESTORE_native_sleeve_and_far_proximal_skin_collar',sleeve_restore);save('ORIGINAL_true_jade_AA_over_native_collar',orig_jade)
# Native proximal far-forearm skin donor: rigid +16,-8 only in the tiny exposed collar.
# This replaces the generated duplicate jade rim behind the exact original bracelet.
far_collar=poly([(1107,789),(1129,789),(1130,827),(1120,837),(1106,839)])&~front&~(f[:,:,3]>0)&~nearhard
Y,X=np.indices((H,W));donor=np.zeros_like(q);donor[:-8,16:]=q[8:,:-16]
b[far_collar]=donor[far_collar]
# True jade AA over actual skin donor; no new bracelet painted.
b=comp(b,jj);b[farhard&~false_air]=a[farhard&~false_air]
save('SAME_RAW_far_proximal_skin_donor_rigid_plus16_minus8',far_collar)
# Continuous original near-forearm lower edge rises by at most3px inside released palm-root collar.
wrist=poly([(1193,859),(1216,859),(1216,876),(1193,876)])&~nearhard
shift=np.clip((X-1195)*.15,0,3);warped=np.stack([map_coordinates(q[:,:,k].astype(float),[Y+shift,X],order=1,mode='constant',cval=0)for k in range(4)],2).round().clip(0,255).astype('uint8')
b[wrist]=warped[wrist]
# Reapply exact original distal hand/core after collar connection.
b[nearhard]=a[nearhard]
save('SAME_RAW_near_root_lower_edge_continuation_max3px',wrist)
res=Image.fromarray(b);dest=O/'candidates/S08_F036_same_raw_semantic_RGBA.png';res.save(dest)
ch=np.any(b!=a,2);union=sleeve|native_far_material|original_far|seat|clear_near|near_restore|false_air|sleeve_restore|orig_jade|far_collar|wrist;assert not(ch&~union).any();save('EXPLICIT_semantic_union',union)
for tag,col in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 bg=Image.alpha_composite(Image.new('RGBA',(W,H),col),res);bg.convert('RGB').save(O/'qa'/f'candidate_{tag}.png')
 for name,bb,z in [('whole_arms',(700,650,1400,1010),2),('wrists_grip',(1080,715,1370,900),4),('head_neck',(730,350,1140,790),2)]:bg.crop(bb).resize(((bb[2]-bb[0])*z,(bb[3]-bb[1])*z)).convert('RGB').save(O/'qa'/f'{name}_{tag}.png')
 src=Image.open(R/'F033_FINAL_LOCKED/S08_F033_grandma_match_box_RGBA.png').convert('RGBA');src=Image.alpha_composite(Image.new('RGBA',(W,H),col),src);panel=Image.new('RGB',(1700,800),col[:3]);panel.paste(src.crop((620,280,1470,1080)),(0,0));panel.paste(bg.crop((620,280,1470,1080)),(850,0));panel.save(O/'qa'/f'F033_F036_same_scale_{tag}.png')
report={'status':'SAME_RAW_SEMANTIC_DIAGNOSTIC_PENDING_REVIEW','candidate_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'changed_from_nominal':int(ch.sum()),'new_permission_outside_original_white':int((ch&~w).sum()),'near_distal_guard_changed':int((ch&nearhard).sum()),'original_far_guard_changed':int((ch&farhard).sum()),'true_far_visible_guard_changed':int((ch&farhard&~false_air).sum()),'retired_false_air_guard':int(false_air.sum()),'box_changed':int((ch&box).sum()),'outside_explicit_union_changed':int((ch&~union).sum()),'same_raw_source':str(N/'registered/F036_registered_scene_patch_RGBA.png'),'original_far_layer_source':str(G/'inputs/F036_original_underlying_far_hand_SEAT_RGBA.png'),'original_near_layer_source':str(G/'inputs/F036_preplaced_true_near_hand_match_RGBA.png')};(O/'geometry/checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
