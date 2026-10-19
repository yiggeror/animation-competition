#!/usr/bin/env python3
"""F063 complete action/material reconstruction input; technical guides,0 calls."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import distance_transform_edt,binary_dilation,label
import numpy as np,json,math,hashlib,shutil
R=Path(__file__).resolve().parent;S=R/'sources';size=(1672,941);crop=(550,0,1320,924);cs=(770,924);ts=(1280,1536);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not(R/'requests/execution_state.json').exists()
for row in json.loads((S/'snapshot_manifest.json').read_text())['files']:assert sha(S/row['snapshot'])==row['sha256']
mother=np.array(Image.open(S/'F044_frozen_HEAD_RUFFLE_SKIRT_MOTHER.png').convert('RGBA'));raw=np.array(Image.open(S/'F063_previous_local_RAW_MATERIAL_ONLY.png').convert('RGBA'));G0=json.loads((S/'F063_frozen_target_geometry_REFERENCE.json').read_text());oldgeo=json.loads((S/'previous_commonM_SIZE_CONFLICT_NOT_POSE_LOCK.json').read_text());M=np.array(oldgeo['single_similarity']['M']);t=np.array(oldgeo['single_similarity']['t']);T=np.array(G0['T_target']);L=np.array(G0['L_target']);G=np.array(G0['G_target']);u=(L-T)/np.linalg.norm(L-T);n=np.array([-u[1],u[0]]);yy,xx=np.indices((941,1672))
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',16);small=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',12)
def mask(path):return np.asarray(Image.open(path).convert('L'))>0
head=mask(S/'F044_actual_head_neck_collar_GUARD.png')&(mother[:,:,3]>0);ruffle=mask(S/'F044_actual_near_whole_ruffle_GUARD.png')&(mother[:,:,3]>0);skirt=mask(S/'F044_stable_skirt_GUARD.png')&(mother[:,:,3]>0);guards=head|ruffle|skirt
base=np.zeros_like(mother);base[guards]=mother[guards];Image.fromarray(base).save(R/'layers/F044_actual_protected_material_ONLY.png')
# Correct original visible prop, s1 whole transform. Its hand-occluded holes
# remain unknown; it is used to measure real silhouette clearance, not to lock a hand.
realprop=Image.open(R/'real_prop_reference_61sol/reference/04_same_frozen_TL_real_visible_prop_SCALE1_NOT_GESTURE.png').convert('RGBA');rp=np.array(realprop);realprop_mask=rp[:,:,3]>=128
# Whole actual receiver hand with full fingers and a short wrist entrance.
# New location is only a guide. The complete far forearm/wrist/hand is WHITE.
farraw=mask(S/'F063_previous_far_arm_actual_material_MASK.png');ry,rx=np.indices(raw.shape[:2]);handmask=farraw&(rx>=995);wholehand=np.where(handmask[:,:,None],raw,0).astype('uint8');Image.fromarray(wholehand).save(R/'layers/SOURCE_actual_complete_receiver_hand_SOFT_GUIDE_ONLY.png')
# Put the actual palm upper-surface anchor near the original receiving station,
# then find a whole-hand vertical offset giving ~15 actual native silhouette px.
source_surface=np.array([1118.,850.]);wanted=np.array(G0['P_fixed_surface']);initial_t=wanted-M@source_surface
iv=np.linalg.inv(M)
def hand_at(trans):
 it=-iv@trans;z=Image.fromarray(wholehand).transform(size,Image.Transform.AFFINE,(*iv[0],it[0],*iv[1],it[1]),Image.Resampling.BICUBIC,fillcolor=0);return np.array(z)
dist,nearest=distance_transform_edt(~realprop_mask,return_indices=True)
choices=[]
for dy in range(-10,31):
 tt=initial_t+np.array([0,dy]);ha=hand_at(tt);hm=ha[:,:,3]>=128;overlap=int((hm&realprop_mask).sum());gap=float(dist[hm].min());choices.append((abs(gap-15)+1000*overlap,abs(dy),dy,gap,ha,tt))
_,_,dy,gap,ha,ht=min(choices,key=lambda z:(z[0],z[1]));hm=ha[:,:,3]>=128;hys,hxs=np.where(hm);idx=np.argmin(dist[hm]);hp=np.array([hxs[idx],hys[idx]]);pp=np.array([nearest[1,hp[1],hp[0]],nearest[0,hp[1],hp[0]]]);contact_delta=pp-hp
Image.fromarray(ha).save(R/'layers/F063_actual_whole_receiver_hand_REPOSITIONED_SOFT_NOT_FROZEN.png')
# Future contact is a reachability study only: whole hand moves along measured
# shortest exterior clearance vector; no F069 input or F069 artwork is produced.
source_wrist=np.array([995.,893.]);farW=M@source_wrist+ht
nearS=np.array([705.,666.]);nearE=np.array([790.,730.]);nearW=np.array([1000.,658.]);farS=np.array([970.,689.]);farE=np.array([1005.,810.])
def poly(points,color,edge,width=2):
 z=Image.new('RGBA',size);d=ImageDraw.Draw(z);d.polygon([tuple(map(float,p))for p in points],fill=color,outline=edge,width=width);return z
def arm(ps,rs,col,edge):
 z=Image.new('RGBA',size);d=ImageDraw.Draw(z)
 for p,q,r1,r2 in zip(ps[:-1],ps[1:],rs[:-1],rs[1:]):
  v=q-p;normal=np.array([-v[1],v[0]])/np.linalg.norm(v);pts=[p+normal*r1,q+normal*r2,q-normal*r2,p-normal*r1];d.polygon([tuple(p)for p in pts],fill=col,outline=edge,width=2)
 for p,r in zip(ps[1:-1],rs[1:-1]):x,y=p;d.ellipse((x-r,y-r,x+r,y+r),fill=col,outline=edge,width=2)
 return z
# Complete continuous torso volume: original head/ruffle/skirt are the only
# fixed clothing material. No fragmentary026 backplate or held trial is reused.
torso=poly([(626,486),(700,475),(787,514),(880,484),(935,490),(982,552),(1004,664),(944,704),(929,778),(683,778),(665,710),(595,672),(588,548)],'#cbd8e1','#647d91',3)
fararm=arm([farS,farE,farW],[30,43,24],'#a3b5c4','#415f78');neararm=arm([nearS,nearE,nearW],[30,36,24],'#a3cee1','#366f91')
# Complete correctly thick prop is a clearly technical solid from measured
# actual044 dimensions. The old hand-occluded RGB is never invented as art.
# Coordinates use exact old044 rigid transform and a dimension proxy only.
oldM=np.array(G0['unit_M']);oldt=np.array(G0['unit_t']);sp=lambda p:oldM@np.array(p)+oldt
prop=Image.new('RGBA',size);pd=ImageDraw.Draw(prop)
for pts,col in [([(1098,345),(1171,345),(1167,620),(1099,620)],'#d8bac0'), ([(1093,620),(1173,620),(1173,666),(1093,666)],'#b5c0cb'), ([(1071,286),(1195,286),(1190,345),(1171,372),(1098,372),(1077,345)],'#bcc7d2')]:
 pd.polygon([tuple(sp(p))for p in pts],fill=col,outline='#5f5966',width=2)
# OFF side-slider position is a technical guide from the original rigid prop.
pd.polygon([tuple(sp(p))for p in [(1140,395),(1164,395),(1164,413),(1140,413)]],fill='#6c7483',outline='#465166',width=1)
# Actual end ellipse proxy full diameters are dimensions, not finished rings.
for center,hw,hh in [((1134,665),40,11),((1135,289),62,18)]:
 pts=[sp(np.array(center)+[hw*math.cos(a),hh*math.sin(a)])for a in np.linspace(0,2*math.pi,90)];pd.polygon([tuple(p)for p in pts],fill='#d0dae1',outline='#5f5966',width=2)
# New neutral-wrist grip guide replaces BOTH competing existing near grasps.
grip=poly([(985,652),(1004,621),(1026,592),(1044,571),(1070,564),(1093,571),(1104,585),(1101,602),(1089,617),(1070,629),(1047,638),(1018,660)],'#9fcfe1','#366f91',2)
gd=ImageDraw.Draw(grip)
for pts in [[(1038,594),(1078,611),(1096,606)],[(1030,606),(1068,623),(1086,617)],[(1023,617),(1051,636),(1070,629)],[(1053,580),(1086,567),(1107,574),(1113,586)]]:gd.line(pts,fill='#366f91',width=3)
A=Image.new('RGBA',size)
for z in [fararm,Image.fromarray(ha),torso,neararm,prop,grip]:A.alpha_composite(z)
a=np.array(A);a[guards]=mother[guards];A=Image.fromarray(a)
notes=Image.new('RGBA',size);nd=ImageDraw.Draw(notes);nd.text((556,32),'F063 TARGET / NOT_ART',font=small,fill='#28566c');nd.text((556,52),'one full action repair',font=small,fill='#28566c');na=np.array(notes);use=(na[:,:,3]>0)&(a[:,:,3]==0);a[use]=na[use];A=Image.fromarray(a)
# All new complete material and old/new body/arm/prop domains are one redraw
# action band minus actual immutable head/collar/near-ruffle/skirt guards.
whitepoly=Image.new('L',size);wd=ImageDraw.Draw(whitepoly);wd.polygon([(580,470),(980,465),(1035,490),(1278,477),(1295,725),(1260,795),(1110,852),(990,875),(919,790),(670,790),(610,730),(570,650)],fill=255)
white=np.array(whitepoly)>0;newvolume=np.logical_or.reduce([np.array(z)[:,:,3]>0 for z in [torso,fararm,Image.fromarray(ha),neararm,prop,grip]]);white|=binary_dilation(newvolume,iterations=12);white&=~guards
# The guard boundary is exact; whole torso/arm reconstruction is permitted.
Image.fromarray(white.astype('uint8')*255).save(R/'masks/WHITE_complete_torso_near_fullarm_grip_fullprop_far_fullarm_hand_air.png')
for name,z in [('HARD_actual_head_neck_collar',head),('HARD_actual_near_whole_ruffle',ruffle),('HARD_actual_stable_skirt',skirt),('TECH_complete_torso_NOT_ART',np.array(torso)[:,:,3]>0),('TECH_complete_near_arm_grip_NOT_ART',(np.array(neararm)[:,:,3]>0)|(np.array(grip)[:,:,3]>0)),('SOFT_actual_receiver_whole_hand_NOT_HARD',ha[:,:,3]>0),('REAL_correct_prop_alpha128_for_gap_only',realprop_mask)]:Image.fromarray(z.astype('uint8')*255).save(R/'masks'/f'{name}.png')
# Layer and contact guide are explicit technical evidence, never finished art.
A.save(R/'reference/A_F063_full_target_NOT_ART_native.png');B=Image.fromarray(white.astype('uint8')*255);B.save(R/'reference/B_F063_full_action_band_WHITE_native.png')
C=A.copy();d=ImageDraw.Draw(C)
for points,col in [([nearS,nearE,nearW,G],'#23577a'),([farS,farE,farW],'#6c4057')]:
 d.line([tuple(p)for p in points],fill=col,width=2)
 for x,y in points:d.ellipse((x-5,y-5,x+5,y+5),outline=col,width=2)
d.line((tuple(hp),tuple(pp)),fill='#00a68a',width=2);d.text((1020,480),'NOT_ART / one complete action repair',font=small,fill='#244b5c');C.save(R/'reference/C_F063_same_target_soft_chains_CONTACT_native.png')
for letter,im in [('A',A),('B',B),('C',C)]:
 im.crop(crop).resize(ts,Image.Resampling.NEAREST if letter=='B'else Image.Resampling.LANCZOS).save(R/f'reference/{letter}_F063_PREPARED_NOT_CALLED_1280x1536.png')
# Read actual silhouette pair in diagnostic overlay; pure visible sourceprop,
# whole actual guide hand, complete requested near arm are all shown honestly.
for tone,bgcol in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 bg=Image.new('RGBA',size,bgcol);bg.alpha_composite(A);bg.convert('RGB').save(R/f'qa/full_target_{tone}_NOT_ART.png');bg.crop((620,475,1300,890)).resize((1360,830)).convert('RGB').save(R/f'qa/full_action_band_{tone}_NOT_ART_2x.png')
 lay=Image.new('RGBA',size,bgcol);lay.alpha_composite(fararm);lay.alpha_composite(Image.fromarray(ha));lay.alpha_composite(torso);lay.alpha_composite(neararm);lay.alpha_composite(prop);lay.alpha_composite(grip);la=np.array(lay);la[guards]=mother[guards];lay=Image.fromarray(la);dd=ImageDraw.Draw(lay);dd.line((tuple(hp),tuple(pp)),fill='#00c8ad',width=2);dd.text((980,473),f'TECH layer order / real edge gap {gap:.2f}px',font=small,fill='#22546b');lay.crop((620,475,1300,890)).resize((1360,830)).save(R/f'qa/three_layer_contact_{tone}_2x.png')
 contact=Image.new('RGBA',size,bgcol);contact.alpha_composite(realprop);contact.alpha_composite(Image.fromarray(ha));dd=ImageDraw.Draw(contact);dd.line((tuple(hp),tuple(pp)),fill='#00c8ad',width=2);dd.text((1000,480),f'REAL source outlines: gap={gap:.2f}px',font=small,fill='#00a68a');contact.crop((1020,490,1300,740)).resize((1120,1000),Image.Resampling.NEAREST).save(R/f'qa/REAL_prop_to_whole_palm_clearance_{tone}_4x.png')
 # Contact path ghost only; no following-state source or input is created.
 reach=contact.copy();dd=ImageDraw.Draw(reach);dd.line((tuple(hp),tuple(pp)),fill='#ec458c',width=3);dd.text((990,760),'063→contact reach STUDY ONLY / no F069 art/input',font=small,fill='#c04c8a');reach.crop((930,490,1300,855)).resize((1110,1095)).save(R/f'qa/063_to_contact_reach_STUDY_ONLY_{tone}.png')
# Metrics and limited geometric feasibility, not final anatomy certification.
near_mask=(np.array(neararm)[:,:,3]>0)|(np.array(grip)[:,:,3]>0);far_mask=(np.array(fararm)[:,:,3]>0)|(ha[:,:,3]>0)
fullmask=newvolume&~guards;box=Image.fromarray(fullmask.astype('uint8')*255).getbbox();guard0=int(np.any(a[guards]!=mother[guards],axis=1).sum());assert guard0==0
hard_except_ruffle=head|skirt
checks={'status':'COMPLETE_FULL_ACTION_INPUT_PREPARATION_PENDING_ROOT_ASTRA_0CALL','calls':0,'F069_input_or_art_created':False,'crop_native':crop,'native_crop_size':cs,'tool_size':ts,'whole_forward_scale':128/77,'whole_inverse_scale':77/128,'whole_inverse_translation':[550,0],'frozen_T':T.tolist(),'frozen_L':L.tolist(),'frozen_axis_native':float(np.linalg.norm(L-T)),'correct_prop_real_dimensions_reference':{'tailcap_visible80.066±3':'actual044','redtube_visible68.085±3':'actual044','lampcap_visible124.023±3':'actual044'},'previous_thin_prop_adopted_pixels':0,'previous_old044_grasp_adopted_pixels':0,'fragmentary026_body_backplate_used':False,'current_far_palm_frozen':False,'whole_hand_source_selector':'complete actual far mask intersectsourcex>=995, short wrist entrance; not hardguard','whole_hand_scale_rotation_from_previous_commonM_for_material_only':oldgeo['single_similarity'],'whole_hand_new_t':ht.tolist(),'whole_hand_source_upper_surface_anchor':source_surface.tolist(),'original_receiving_surface_reference':wanted.tolist(),'whole_hand_vertical_adjustment_for_real_edge_gap':dy,'REAL_prop_to_REAL_hand_gap_alpha128_native':gap,'closest_actual_hand_pixel':hp.tolist(),'closest_actual_prop_pixel':pp.tolist(),'actual_prop_hand_overlap':int((hm&realprop_mask).sum()),'contact_study_only_whole_hand_translation':contact_delta.tolist(),'far_wrist_guide_native':farW.tolist(),'near_chain_proxy_native':[nearS.tolist(),nearE.tolist(),nearW.tolist(),G.tolist()],'far_chain_proxy_native':[farS.tolist(),farE.tolist(),farW.tolist()],'proxy_not_measured_bones':True,'near_technical_volume_intersection_head':int((near_mask&head).sum()),'near_technical_volume_intersection_stable_skirt':int((near_mask&skirt).sum()),'far_technical_volume_intersection_head':int((far_mask&head).sum()),'far_technical_volume_intersection_stable_skirt':int((far_mask&skirt).sum()),'near_technical_low_elbow_proxy_bottom':766,'stable_skirt_row_proxy':777,'guard_RGBA_changes':guard0,'guard_alpha0_source_pixels':int((guards&(mother[:,:,3]==0)).sum()),'WHITE_guard_intersections':int((white&guards).sum()),'new_material_not_WHITE_except_actualguards':int((newvolume&~white&~guards).sum()),'full_action_volume_bbox_halfopen':box,'WHITE_pixels':int(white.sum()),'limits':['Inputguide only, no art candidate or anatomical/bone-length certification.','Actual source prop outer boundary and actual palm silhouette gap measured after source material extraction; about15native, not justpointdistance.','Palm and complete botharms/torso/grip/prop are all redrawable; old044hand/previous063thinprop/previouspalmposition not locked.','063→contact path is geometric reach-study only; generated063→069 real material/exposure still needs actual review.']}
(R/'geometry/input_gate_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:checks[k]for k in ['REAL_prop_to_REAL_hand_gap_alpha128_native','closest_actual_hand_pixel','closest_actual_prop_pixel','whole_hand_vertical_adjustment_for_real_edge_gap','far_wrist_guide_native','near_technical_volume_intersection_head','near_technical_volume_intersection_stable_skirt','far_technical_volume_intersection_stable_skirt','guard_RGBA_changes','WHITE_guard_intersections','new_material_not_WHITE_except_actualguards','full_action_volume_bbox_halfopen']},ensure_ascii=False,indent=2))
