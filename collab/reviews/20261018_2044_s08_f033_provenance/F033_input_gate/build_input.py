from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
from scipy.ndimage import binary_dilation,label
import numpy as np,math,json,hashlib
O=Path(__file__).resolve().parent;R=O.parent;P=R/'F030_FINAL_LOCKED';src=P/'S08_F030_grandma_match_box_RGBA.png';sha=hashlib.sha256(src.read_bytes()).hexdigest();assert sha=='ef53ba49d805d2a9eb2cf934f62b2098a07e924250fcbbd5070cb33fcbba6bc8';a=np.array(Image.open(src).convert('RGBA'));H,W=a.shape[:2]
S=json.loads((R/'F033_structure_gate/geometry/F033_first_structure.json').read_text());pos=S['target_points_screen_approx'];head=(1230,707);oldhead=(1148,717);angle=7;th=math.radians(angle);c,s=math.cos(th),math.sin(th);aff=(c,s,oldhead[0]-c*head[0]-s*head[1],-s,c,oldhead[1]+s*head[0]-c*head[1])
def load(name):return np.array(Image.open(P/name).convert('L'))>0
def poly(p):
 m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon(p,fill=255);return np.array(m)>0
def save(n,m):Image.fromarray(m.astype('uint8')*255).save(O/'masks'/f'{n}.png')
near0=load('F030_true_near_hand_match_footprint.png');distal0=load('F030_near_distal_hard_guard_footprint.png');far0=load('F030_whole_closed_far_hand_jade_AND_TRANSPARENT_SEAT_footprint.png');box=load('F030_fixed_table_box_footprint.png');ni=np.zeros_like(a);ni[near0]=a[near0];n=np.array(Image.fromarray(ni).transform((W,H),Image.Transform.AFFINE,aff,Image.Resampling.BICUBIC));nearall=n[:,:,3]>0
near=np.array(Image.fromarray(distal0.astype('uint8')*255).transform((W,H),Image.Transform.AFFINE,aff,Image.Resampling.NEAREST))>0;near&=nearall;collar=nearall&~near
# Far intrinsic true hand remains archived beneath the moving foreground hand.
# Release only its occluded outer footprint in the visible composite, never the actual lever-seat core.
far_occlusion=far0&nearall;far=far0&~nearall
assert not (poly([(1227,760),(1241,760),(1241,774),(1227,774)])&nearall).any()
body=np.array(Image.open(R/'F030_LAYER_PARTITION/frames/F030_body_behind_original_pixels.png'));body[body[:,:,3]==0]=0
pre=np.zeros_like(a);pre[3:,44:]=body[:-3,:-44];pre[far0]=a[far0];pre[box]=a[box]
pre=np.array(Image.alpha_composite(Image.fromarray(pre),Image.fromarray(n)))
bodyenv=poly([(665,290),(1010,290),(1074,355),(1090,586),(1105,684),(1135,788),(1166,863),(1119,934),(1035,1079),(570,1079),(597,958),(620,810),(622,657),(650,578),(643,467)])
oldalpha=binary_dilation((a[:,:,3]>0)&~(far0|box),iterations=5);newalpha=binary_dilation(pre[:,:,3]>0,iterations=7)
armenv=poly([(706,653),(806,687),(908,777),(947,821),(1084,721),(1154,748),(1144,812),(1014,894),(934,946),(865,909),(762,825),(693,753)])
fararm=poly([(973,646),(1052,659),(1117,794),(1131,797),(1171,843),(1129,902),(1063,929),(1010,873),(985,780)])
w=(bodyenv|oldalpha|newalpha|armenv|fararm|collar)&~(near|far|box)
labels,num=label(w);main=labels[800,940];islands=w&(labels!=main);w&=labels==main
# Explicitly restore true foreground hand AA backed by original opaque far hand.
# These54 pixels are source-over original hand layers, never model-painted anatomy.
lost_AA=nearall&far0&(a[:,:,3]>128)&~(near|far|box|w)
assert int(lost_AA.sum())==54
near|=lost_AA;collar&=~lost_AA
save('F033_RESTORE_true_foreground_AA_backed_by_far_hand',lost_AA)
pre[~w&~(near|far|box)]=0
for name,m in [('F033_WHITE_body_neck_head_arms_wrist_allowed',w),('F033_near_distal_palm_fingers_entire_match_guard',near),('F033_near_whole_transformed_hand_footprint',nearall),('F033_near_proximal_palmroot_release',collar),('F033_far_visible_hand_jade_TRUE_SEAT_guard',far),('F033_far_original_underlying_full_hand_SEAT_footprint',far0),('F033_far_guard_occluded_by_foreground_near_hand',far_occlusion),('F033_fixed_table_box_guard',box),('F033_removed_permission_islands',islands)]:save(name,m)
Image.fromarray(pre).save(O/'inputs/F033_preplaced_body_anchor_truehands_NO_ROD_RGBA.png');Image.fromarray(n).save(O/'inputs/F033_preplaced_true_near_hand_match_RGBA.png')
# Underlying complete far grip remains independently preserved, not reconstructed from an occluded final.
fa=np.zeros_like(a);fa[far0]=a[far0];Image.fromarray(fa).save(O/'inputs/F033_original_underlying_far_hand_SEAT_RGBA.png')
rod=Image.new('RGBA',(W,H));d=ImageDraw.Draw(rod);knob=(1233.9532049682696,766.8943738423919);pivot=(1301.4864864864865,791.545945945946);d.line((knob,pivot),fill=(58,42,34,255),width=5);d.ellipse((knob[0]-6.81,knob[1]-6.81,knob[0]+6.81,knob[1]+6.81),fill=(58,42,34,255));target=Image.alpha_composite(rod,Image.fromarray(pre));target.save(O/'inputs/F033_preplaced_WITH_REAL_LOW_ROD_RGBA.png')
bb=(580,280,1360,1080);size=(1170,1200)
target.crop(bb).resize(size,Image.Resampling.LANCZOS).save(O/'inputs/F033_actual_edit_target_1p5x_RGBA.png');Image.fromarray(w.astype('uint8')*255).crop(bb).resize(size,Image.Resampling.NEAREST).save(O/'inputs/F033_actual_edit_WHITE_MASK_1p5x.png')
source=Image.alpha_composite(Image.new('RGBA',(W,H),(244,242,237,255)),Image.fromarray(a));source.crop(bb).resize(size).convert('RGB').save(O/'inputs/F030_locked_identity_full_arm_volume_REFERENCE.png')
guide=Image.new('RGBA',(W,H),(244,242,237,255));d=ImageDraw.Draw(guide);ns=pos['near_shoulder'];fs=pos['far_shoulder'];hc=pos['cranium_center'];nr=pos['neck_skin_root'];cv=pos['collar_V'];d.polygon([tuple(ns),(610,1080),(985,1080),tuple(fs)],fill=(210,227,237),outline=(74,116,145));d.line((tuple(ns),tuple(nr),tuple(fs)),fill=(74,116,145),width=3);d.line((tuple(nr),tuple(cv),(887,922),(850,1080)),fill=(74,116,145),width=3);d.ellipse((hc[0]-140,hc[1]-162,hc[0]+143,hc[1]+162),outline=(74,116,145),width=3);d.line(((hc[0]-55,hc[1]+55),(hc[0]+114,hc[1]+71)),fill=(74,116,145),width=2);d.line(((hc[0]+2,hc[1]+157),tuple(nr)),fill=(74,116,145),width=3)
d.line([tuple(pos[k]) for k in ['far_shoulder','far_sleeve_exit','far_elbow','far_wrist']],fill=(154,166,173),width=39);d.line([tuple(pos[k]) for k in ['far_shoulder','far_sleeve_exit','far_elbow','far_wrist']],fill=(74,116,145),width=2);guide.alpha_composite(rod);q=np.zeros_like(a);q[far0]=a[far0];q[box]=a[box];guide.alpha_composite(Image.fromarray(q));d=ImageDraw.Draw(guide);d.line([tuple(pos[k]) for k in ['near_shoulder','near_sleeve_exit','near_elbow','near_wrist']],fill=(238,216,191),width=62);d.line([tuple(pos[k]) for k in ['near_shoulder','near_sleeve_exit','near_elbow','near_wrist']],fill=(147,109,79),width=2);guide.alpha_composite(Image.fromarray(n));guide.crop(bb).resize(size).convert('RGB').save(O/'inputs/F033_whole_chest_shoulders_neck_head_STRUCTURE_ONLY.png')
f000=Image.open(R/'F000_FINAL_LOCKED/S08_F000_grandma_match_box_RGBA.png').convert('RGBA');ref=Image.alpha_composite(Image.new('RGBA',(W,H),(244,242,237,255)),f000);ref.crop((600,305,1045,775)).resize((890,940)).convert('RGB').save(O/'inputs/F000_original_identity_material_COLOR_ONLY_NO_HANDS.png')
for tag,col in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 base=Image.alpha_composite(Image.new('RGBA',(W,H),col),target);base.crop(bb).resize(size).convert('RGB').save(O/'qa'/f'actual_target_{tag}.png');t=np.zeros_like(a);t[w]=[60,195,80,110];base.alpha_composite(Image.fromarray(t));base.crop(bb).resize(size).convert('RGB').save(O/'qa'/f'actual_mask_{tag}.png');base.crop((1040,680,1310,890)).resize((1080,840)).convert('RGB').save(O/'qa'/f'wrists_seat_guards_{tag}.png');base=Image.alpha_composite(Image.new('RGBA',(W,H),col),target);t=np.zeros_like(a);t[far_occlusion]=[238,30,160,150];base.alpha_composite(Image.fromarray(t));base.crop((1060,690,1290,875)).resize((1150,925)).convert('RGB').save(O/'qa'/f'EXACT_far_occluded_footprint_{tag}.png')
assert not(w&(near|far|box)).any();assert np.array_equal(pre[far],a[far]);assert np.array_equal(pre[box],a[box])
report={'status':'ACTUAL_INPUT_PREPARED_PENDING_DUAL_GATE_NO_CALL','logical_call_reserved':16,'source':str(src),'source_sha256':sha,'crop_scene_box':bb,'input_scale':1.5,'near_rigid_transform':{'scale':1,'clockwise_deg_from030':7,'source_head':oldhead,'new_head':head,'visible_exit':S['near_group_transform']['visible_exit'],'visible_segment_px':46.400431},'whole_body_construction_anchor_only':{'uniform_translate':[44,3],'not_final_body_pose':True,'whole_chest_neck_head_white_for_coherent_turn':True},'near_root_release_pixels':int(collar.sum()),'restored_original_two_hand_AA_pixels':int(lost_AA.sum()),'near_hard_pixels':int(near.sum()),'far_original_underlying_guard':int(far0.sum()),'far_effective_visible_composite_guard':int(far.sum()),'far_occluded_footprint_by_new_near_hand':int(far_occlusion.sum()),'far_visible_occluded_pixels':int((far_occlusion&(a[:,:,3]>0)).sum()),'far_true_original_underlying_hand_and_seat_preserved':True,'true_knob_core_overlap_near':0,'far_visible_unoccluded_RGBA_changed':0,'mask_guard_overlap':0,'removed_islands':int(islands.sum()),'rod_policy':'Visible context only; final restore true alpha0 seat. Original closed grip remains underlying, near hand passes in foreground. No rod/flame/lamp/table baked into final character.','source_proxy_geometry':str(R/'F033_structure_gate/geometry/F033_first_structure.json'),'color_reference':'OriginalF000 neutral material standard with actual030 identity/body anatomy, no cumulative warm/dark drift.'};(O/'geometry/INPUT_CONTRACT.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
