from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from scipy.ndimage import binary_dilation,label
import numpy as np,math,json,hashlib
O=Path(__file__).resolve().parent;R=O.parent;P=R.parent/'astra_s08_f027_parallel_20261018_1812/F027_FINAL_LOCKED';src=P/'S08_F027_grandma_match_box_RGBA.png';sha=hashlib.sha256(src.read_bytes()).hexdigest();assert sha=='2dc0ee2bc06b4b872e0f79cbf4c1bd19b2ccaa160cba9b5feefd45f2a8e268ac';a=np.array(Image.open(src).convert('RGBA'));H,W=a.shape[:2]
S=json.loads((R/'F030_structure_gate_1942/geometry/F030_first_structure.json').read_text());pos=S['target_points_screen_approx'];head=(1148,717);oldhead=(1082,797);angle=5;th=math.radians(angle);c,s=math.cos(th),math.sin(th);aff=(c,s,1082-c*1148-s*717,-s,c,797+s*1148-c*717)
def load(name):return np.array(Image.open(P/name).convert('L'))>0
def poly(p):
 m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon(p,fill=255);return np.array(m)>0
def save(n,m):Image.fromarray(m.astype('uint8')*255).save(O/'masks'/f'{n}.png')
near0=load('F027_true_near_hand_match_footprint.png');far0=load('F027_whole_closed_far_hand_jade_AND_TRANSPARENT_SEAT_footprint.png');box=load('F027_fixed_table_box_footprint.png');ni=np.zeros_like(a);ni[near0]=a[near0];n=np.array(Image.fromarray(ni).transform((W,H),Image.Transform.AFFINE,aff,Image.Resampling.BICUBIC));nearall=n[:,:,3]>0
# Free the true proximal wrist/palm-root collar, preserving all distal palm, fingers and entire wooden match.
collar0=poly([(949,853),(972,851),(988,909),(963,918)])&near0
collar=np.array(Image.fromarray(collar0.astype('uint8')*255).transform((W,H),Image.Transform.AFFINE,aff,Image.Resampling.NEAREST))>0
near=nearall&~collar
false_far_air=far0&nearall&(a[:,:,3]==0);far=far0&~false_far_air
assert not ((far0&nearall)&(a[:,:,3]>0)).any()
# Use only original body pixels as a uniformly translated identity construction anchor. The full body is white/editable.
body=np.array(Image.open(P.parent/'F027_LAYER_PARTITION/frames/F027_body_behind_original_pixels.png'));body[body[:,:,3]==0]=0
pre=np.zeros_like(a);pre[4:,28:]=body[:-4,:-28]
pre[far]=a[far];pre[box]=a[box];pre[nearall]=n[nearall]
# Complete body/head envelope plus both natural arm routes, original-position clearance and collar joins.
bodyenv=poly([(625,295),(945,290),(1030,365),(1055,565),(1062,644),(1090,753),(1118,824),(1165,884),(1116,935),(1000,940),(995,1079),(530,1079),(562,964),(584,841),(585,649),(620,581),(604,474)])
oldalpha=binary_dilation((a[:,:,3]>0)&~(far0|box),iterations=5)
newalpha=binary_dilation(pre[:,:,3]>0,iterations=7)
armenv=poly([(685,655),(767,698),(841,785),(935,876),(1056,734),(1107,781),(1067,846),(925,976),(852,994),(755,881),(670,760)])
fararm=poly([(971,658),(1044,665),(1090,782),(1127,799),(1170,843),(1125,898),(1069,924),(1018,882),(986,786)])
w=(bodyenv|oldalpha|newalpha|armenv|fararm|collar)&~(near|far|box)
# Keep only the contiguous body/arm permission region. Isolated permission islands around
# fixed props and source alpha scraps are not authorized anatomy edits. Source originals untouched.
labels,ncomp=label(w);main_id=labels[800,900];permission_islands=w&(labels!=main_id);w&=labels==main_id
save('F030_REMOVED_isolated_permission_islands',permission_islands)
# Include full old arm/hand vacated area and clean false empty patches. Fixed alpha0 grip seat remains black.
pre[~w&~(near|far|box)]=0
for name,m in [('F030_WHITE_body_neck_head_arms_and_wrist_allowed',w),('F030_near_distal_palm_fingers_entire_match_guard',near),('F030_near_whole_transformed_hand_footprint',nearall),('F030_near_proximal_wrist_palmroot_release',collar),('F030_far_hand_jade_TRUE_ALPHA0_SEAT_guard',far),('F030_RELEASE_original_far_empty_air_occupied_by_new_near_hand',false_far_air),('F030_fixed_table_box_guard',box)]:save(name,m)
Image.fromarray(pre).save(O/'inputs/F030_preplaced_original_body_anchor_and_truehands_NO_ROD_RGBA.png')
rod=Image.new('RGBA',(W,H));d=ImageDraw.Draw(rod);knob=(1233.9532049682696,766.8943738423919);pivot=(1301.4864864864865,791.545945945946);d.line((knob,pivot),fill=(58,42,34,255),width=5);d.ellipse((knob[0]-6.81,knob[1]-6.81,knob[0]+6.81,knob[1]+6.81),fill=(58,42,34,255));target=Image.alpha_composite(rod,Image.fromarray(pre));target.save(O/'inputs/F030_preplaced_WITH_REAL_LOW_ROD_RGBA.png')
bb=(530,280,1340,1080);size=(1215,1200)
target.crop(bb).resize(size,Image.Resampling.LANCZOS).save(O/'inputs/F030_actual_edit_target_1p5x_RGBA.png');Image.fromarray(w.astype('uint8')*255).crop(bb).resize(size,Image.Resampling.NEAREST).save(O/'inputs/F030_actual_edit_WHITE_MASK_1p5x.png')
source=Image.alpha_composite(Image.new('RGBA',(W,H),(244,242,237,255)),Image.fromarray(a));source.crop(bb).resize(size).convert('RGB').save(O/'inputs/F027_locked_identity_and_full_arm_volume_REFERENCE.png')
# Structure guide: only approximate whole-body tracks, no flames or text. True hands retain actual pixels.
guide=Image.new('RGBA',(W,H),(244,242,237,255));d=ImageDraw.Draw(guide);ns=pos['near_shoulder'];fs=pos['far_shoulder'];hc=pos['cranium_center'];nr=pos['neck_skin_root'];cv=pos['collar_V']
d.polygon([tuple(ns),(595,1080),(940,1080),tuple(fs)],fill=(210,227,237),outline=(74,116,145));d.line((tuple(ns),tuple(nr),tuple(fs)),fill=(74,116,145),width=3);d.line((tuple(nr),tuple(cv),(855,922),(814,1080)),fill=(74,116,145),width=3)
d.ellipse((hc[0]-140,hc[1]-162,hc[0]+143,hc[1]+162),outline=(74,116,145),width=3);d.line(((hc[0]-55,hc[1]+55),(hc[0]+114,hc[1]+71)),fill=(74,116,145),width=2);d.line(((hc[0]+2,hc[1]+157),tuple(nr)),fill=(74,116,145),width=3)
d.line([tuple(pos[k]) for k in ['far_shoulder','far_sleeve_exit','far_elbow','far_wrist']],fill=(154,166,173),width=39);d.line([tuple(pos[k]) for k in ['far_shoulder','far_sleeve_exit','far_elbow','far_wrist']],fill=(74,116,145),width=2)
guide.alpha_composite(rod);q=np.zeros_like(a);q[far]=a[far];q[box]=a[box];guide.alpha_composite(Image.fromarray(q));d=ImageDraw.Draw(guide);d.line([tuple(pos[k]) for k in ['near_shoulder','near_sleeve_exit','near_elbow','near_wrist']],fill=(238,216,191),width=62);d.line([tuple(pos[k]) for k in ['near_shoulder','near_sleeve_exit','near_elbow','near_wrist']],fill=(147,109,79),width=2);guide.alpha_composite(Image.fromarray(n));guide.crop(bb).resize(size).convert('RGB').save(O/'inputs/F030_whole_chest_shoulders_neck_head_STRUCTURE_ONLY.png')
f000=Image.open(R/'F000_FINAL_LOCKED/S08_F000_grandma_match_box_RGBA.png').convert('RGBA');ref=Image.alpha_composite(Image.new('RGBA',(W,H),(244,242,237,255)),f000);ref.crop((600,305,1045,775)).resize((890,940)).convert('RGB').save(O/'inputs/F000_original_identity_material_COLOR_ONLY_NO_HANDS.png')
for tag,col in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 base=Image.alpha_composite(Image.new('RGBA',(W,H),col),target);base.crop(bb).resize(size).convert('RGB').save(O/'qa'/f'actual_target_{tag}.png');t=np.zeros_like(a);t[w]=[60,195,80,110];base.alpha_composite(Image.fromarray(t));base.crop(bb).resize(size).convert('RGB').save(O/'qa'/f'actual_mask_{tag}.png');base.crop((980,685,1280,865)).resize((1200,720)).convert('RGB').save(O/'qa'/f'wrists_and_guards_{tag}.png')
 d=ImageDraw.Draw(base);y,x=np.where(false_far_air);d.rectangle((x.min(),y.min(),x.max(),y.max()),outline=(238,60,160),width=2);base.crop((1060,690,1280,875)).resize((1100,925)).convert('RGB').save(O/'qa'/f'FALSE_FAR_AIR_release_{tag}.png')
assert not (w&(far|near|box)).any();assert np.array_equal(pre[far],a[far]);assert np.array_equal(pre[near],n[near]);assert np.array_equal(pre[box],a[box]);yy,xx=np.where(false_far_air)
contract={'status':'ACTUAL_INPUT_PREPARED_NOT_CALLED_PENDING_DUAL_GATE','logical_call_reserved':15,'source':str(src),'source_sha256':sha,'crop_scene_box':bb,'input_scale':1.5,'near_rigid_transform':{'scale':1,'clockwise_deg':5,'source_head':oldhead,'new_head':head},'whole_body_construction_anchor_only':{'source':'Original027 body alpha partition, visible pixels only','uniform_translate':[28,4],'not_final_body_pose':True,'full_body_is_editable_for_unified_chest_shoulders_neck_head_turn':True},'source_and_target_proxy_geometry':str(R/'F030_structure_gate_1942/geometry/F030_first_structure.json'),'removed_disconnected_permission_islands_pixels':int(permission_islands.sum()),'near_wrist_palmroot_release_pixels':int((collar&nearall).sum()),'near_distal_palm_fingers_match_protected_pixels':int(near.sum()),'far_original_footprint_pixels':int(far0.sum()),'far_true_hand_jade_seat_guard_pixels':int(far.sum()),'released_far_alpha0_air_occupied_by_near_hand':int(false_far_air.sum()),'released_far_air_bbox':[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())],'far_visible_hand_changed':0,'true_grip_seat_alpha0_changed':0,'all_white_hard_guard_overlap':0,'rod_policy':'Actual low lever visible under original true closed grip in input, never adopted into character. Restore original alpha0 seat. No flame or lamp in final character.','body_color_reference':'Original F000, not cumulative generated color; color checks separately compare lit material planes and natural shadow.'};(O/'geometry/INPUT_CONTRACT.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2));print(json.dumps(contract,indent=2))

# Exact semantic release, not just a bounding rectangle: alpha0 air occupied by the new near hand.
for tag,col in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 base=Image.alpha_composite(Image.new('RGBA',(W,H),col),target);t=np.zeros_like(a);t[false_far_air]=[238,30,160,165];base.alpha_composite(Image.fromarray(t));base.crop((1060,690,1280,875)).resize((1100,925)).convert('RGB').save(O/'qa'/f'EXACT_1006_air_release_{tag}.png')
