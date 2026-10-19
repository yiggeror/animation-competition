#!/usr/bin/env python3
"""One existing-pixel prop plate + whole new wrist/palm band. NOT_ART; zero calls."""
from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation,distance_transform_edt,label
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;BASE=R.parent;P=BASE/'F063_full_grip_shape_repair_gate_20261019';S=P/'sources';PR=P/'real_prop_reference_61sol';AOLD=BASE/'F063_local_repair_call01_e6619045/adoption_sources';size=(1672,941);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:np.array(Image.open(p).convert('RGBA'));mask=lambda p:np.array(Image.open(p).convert('L'))>0
for d in ['reference','layers','masks','qa']:(R/d).mkdir(exist_ok=True)
motherpath=S/'F044_frozen_HEAD_RUFFLE_SKIRT_MOTHER.png';mother=load(motherpath);assert sha(motherpath)=='fe70d79e90559659a83772cb29e4cbeffb2b22b355ed3e403509621b381cfad9'
g=json.loads((S/'F063_frozen_target_geometry_REFERENCE.json').read_text());M=np.array(g['unit_M']);t=np.array(g['unit_t']);T=np.array(g['T_target']);L=np.array(g['L_target']);G=np.array(g['G_target']);u=(L-T)/np.linalg.norm(L-T);n=np.array([-u[1],u[0]]);assert np.allclose(M.T@M,np.eye(2))
# Select only actually visible prop pixels from FE70 mother; original hand fully excluded.
unit=load(PR/'sources/F044_b877_unit_REAL_SIZE_ONLY.png');human=mask(PR/'sources/ALL_old_human_unit_EXCLUSION.png');keep=(unit[:,:,3]>0)&~human
# Historical conservative human exclusion also hid the actually visible slider.
# Restore only original FE70 neutral slider material and clearly red exposed wall,
# never the old hand's warm skin/ink; all added RGB stays exact source.
rgb=mother[:,:,:3].astype(int);ry,rx=np.indices(mother.shape[:2]);roi=(rx>=1093)&(rx<1176)&(ry>=375)&(ry<415)
red=roi&(rgb[:,:,1]<140)&(rgb[:,:,0]>1.5*rgb[:,:,1])&(rgb[:,:,0]>1.7*rgb[:,:,2])
buttonroi=(rx>=1132)&(rx<1167)&(ry>=389)&(ry<407);neutral=buttonroi&(np.abs(rgb[:,:,0]-rgb[:,:,1])<18)&(np.abs(rgb[:,:,1]-rgb[:,:,2])<18)&(rgb[:,:,1]>=rgb[:,:,0]-10)&(rgb[:,:,2]>=rgb[:,:,0]-15)&(rgb.max(axis=2)<160)
ll,_=label(neutral);button=ll==ll[397,1145];button&=neutral
assert button.sum()>100
restored=(red|button)&(unit[:,:,3]>0);keep|=restored
Image.fromarray(button.astype('uint8')*255).save(R/'masks/SOURCE_FE70_visible_slider_actual_material.png')
sourceprop=np.where(keep[:,:,None],mother,0).astype('uint8');Image.fromarray(sourceprop).save(R/'layers/FE70_real_visible_prop_ONLY_original_coordinates.png')
iv=M.T;it=-iv@t;prop=Image.fromarray(sourceprop).transform(size,Image.Transform.AFFINE,(*iv[0],it[0],*iv[1],it[1]),Image.Resampling.BICUBIC,fillcolor=0);pa=np.array(prop);prop.save(R/'layers/FE70_whole_visible_prop_SINGLE_RIGID_transform.png');pm=pa[:,:,3]>0
head=mask(S/'F044_actual_head_neck_collar_GUARD.png')&(mother[:,:,3]>0);ruffle=mask(S/'F044_actual_near_whole_ruffle_GUARD.png')&(mother[:,:,3]>0);skirt=mask(S/'F044_stable_skirt_GUARD.png')&(mother[:,:,3]>0);frozen=head|ruffle|skirt
oldnear=mask(AOLD/'F044_complete_old_near_arm_actual_mask.png');oldunit=mask(AOLD/'F044_old_rigid_unit_actual_mask.png');oldfar=mask(AOLD/'F044_old_far_arm_actual_visible_mask.png');oldhuman=oldnear|oldfar
# Mother body/cloth outside all old moving material remains actual FE70, no donor/coded navy/yellow fill.
body=mother.copy();clear=binary_dilation(oldnear|oldunit|oldfar,iterations=2)&~frozen;body[clear]=0;Image.fromarray(body).save(R/'layers/FE70_body_original_pixels_old_moving_material_removed.png')
receiver=Image.open(P/'layers/F063_actual_whole_receiver_hand_REPOSITIONED_SOFT_NOT_FROZEN.png').convert('RGBA');ha=np.array(receiver)
# Same175 receiver placement, complete hand remains a soft guide and full editable material.
NS=np.array([705.,666.]);NE=np.array([790.,730.]);NW=np.array([1000.,658.]);FS=np.array([970.,689.]);FE=np.array([1005.,810.]);FW=np.array(json.loads((P/'geometry/input_gate_checks.json').read_text())['far_wrist_guide_native'])
def arm(ps,rs,col):
 z=Image.new('RGBA',size);d=ImageDraw.Draw(z)
 for p,q,r1,r2 in zip(ps[:-1],ps[1:],rs[:-1],rs[1:]):
  v=q-p;v=np.array([-v[1],v[0]])/np.linalg.norm(v);d.polygon([tuple(p+v*r1),tuple(q+v*r2),tuple(q-v*r2),tuple(p-v*r1)],fill=col,outline='#476e85',width=2)
 for p,r in zip(ps[1:-1],rs[1:-1]):x,y=p;d.ellipse((x-r,y-r,x+r,y+r),fill=col,outline='#476e85',width=2)
 return z
near=arm([NS,NE,NW],[30,36,24],'#a3cee1');far=arm([FS,FE,FW],[30,43,24],'#a3b5c4');grip=Image.new('RGBA',size);gd=ImageDraw.Draw(grip);gd.polygon([(985,652),(1004,621),(1026,592),(1044,571),(1070,564),(1093,571),(1104,585),(1101,602),(1089,617),(1070,629),(1047,638),(1018,660)],fill='#9fcfe1',outline='#366f91',width=2)
for ps in [[(1038,594),(1078,611),(1096,606)],[(1030,606),(1068,623),(1086,617)],[(1023,617),(1051,636),(1070,629)],[(1053,580),(1086,567),(1107,574),(1113,586)]]:gd.line(ps,fill='#366f91',width=3)
# Unknown tube/old foreground vacancies remain explicit NOT_ART, never invented prop/body art.
yy,xx=np.indices((941,1672));ax=(xx-T[0])*u[0]+(yy-T[1])*u[1];normal=(xx-T[0])*n[0]+(yy-T[1])*n[1];unknown_tube=(ax>100)&(ax<285)&(np.abs(normal)<35)&~pm
unknown_body=clear&(xx>=660)&(xx<1000)&(yy>=550)&(yy<777)&~frozen
unknown=Image.new('RGBA',size);un=np.zeros_like(mother);un[unknown_body]=[203,216,225,255];un[unknown_tube]=[190,199,212,255];unknown=Image.fromarray(un)
# Source/body remain actual044 layer, technical occluded far upperarm goes behind it.
plate=Image.new('RGBA',size)
for z in [far,receiver,unknown,Image.fromarray(body),near,grip,prop]:plate.alpha_composite(z)
a=np.array(plate);a[frozen]=mother[frozen];plate=Image.fromarray(a);plate.save(R/'reference/A_F063_real_prop_pixel_plate_NOT_ART_native.png')
# One broad continuous new near chain, whole wrist/palm/needed finger/thumb roots;
# all old arm vacancies and unknown cylinder are editable. Only actual prop/head/ruffle/skirt are hard.
newnear=(np.array(near)[:,:,3]>0)|(np.array(grip)[:,:,3]>0);newfar=(np.array(far)[:,:,3]>0)|(ha[:,:,3]>0);white=binary_dilation(newnear|newfar|oldhuman|unknown_body|unknown_tube,iterations=10)&~(pm|frozen)
for name,z in [('WHITE_whole_elbow_forearm_wrist_full_palm_fingers_unknown_tube_and_old_vacancy',white),('HARD_only_actual_visible_prop_material',pm),('HARD_actual_FE70_head_ruffle_skirt',frozen),('UNKNOWN_original_hand_hidden_cylinder',unknown_tube),('REMOVED_old_hand_wrist_human_NOT_HARD',oldhuman)]:Image.fromarray(z.astype('uint8')*255).save(R/'masks'/f'{name}.png')
Image.fromarray(white.astype('uint8')*255).save(R/'reference/B_F063_complete_editing_band_native.png')
# Existing approved crop is preserved only as diagnostic comparison; no request is made.
crop=(550,0,1320,924)
for tone,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 bg=Image.new('RGBA',size,col);bg.alpha_composite(plate);bg.crop(crop).save(R/f'qa/F063_pixel_plate_{tone}.png');bg.crop((750,490,1300,775)).resize((1100,570),Image.Resampling.NEAREST).save(R/f'qa/F063_real_prop_full_wrist_band_{tone}_2x.png')
 bg=Image.new('RGBA',size,col);bg.alpha_composite(prop);bg.alpha_composite(receiver);bg.crop((1080,590,1265,735)).resize((740,580),Image.Resampling.NEAREST).save(R/f'qa/F063_REAL_prop_to_175_whole_palm_{tone}_4x.png')
# Scan actual complete receiver versus actual source-visible prop, no ellipse/point proxy.
gaps={}
for threshold in [1,16,128,240]:
 pp=pa[:,:,3]>=threshold;hh=ha[:,:,3]>=threshold;dist=distance_transform_edt(~pp);gaps[str(threshold)]={'native_gap':float(dist[hh].min()),'overlap':int((pp&hh).sum())}
assert gaps['128']['overlap']==0 and abs(gaps['128']['native_gap']-15)<.01
assert not (white&pm).any() and not (white&frozen).any();assert np.array_equal(a[frozen],mother[frozen]);assert np.array_equal(a[pa[:,:,3]==255],pa[pa[:,:,3]==255])
labels,cc=label(white);probes={}
for k,p in [('nearE',NE),('nearW',NW),('palm',G)]:x,y=np.rint(p).astype(int);probes[k]={'xy':[int(x),int(y)],'white':bool(white[y,x]),'component':int(labels[y,x])}
record={'status':'DIAGNOSTIC_ONLY_PENDING_ASTRA_ZERO_CALLS','mother_SHA256':sha(motherpath),'actual_prop_source':'FE70 mother visible material only, historical whole unit used only to delimit prop; ALL old human excluded','scale':1,'R_degrees':78.508,'M':M.tolist(),'t':t.tolist(),'frozen_T':T.tolist(),'frozen_L':L.tolist(),'grip_axis_fraction':.5186170239855135,'grip_G':G.tolist(),'old_hand_or_technical_wrist_hard_pixels':0,'visible_prop_material_hard_pixels':int(pm.sum()),'conservative_old_exclusion_corrected_for_actual_slider_pixels':int((button&human).sum()),'actual_slider_original_pixel_count':int(button.sum()),'actual_slider_source_RGB_changes':0,'white_hard_prop_overlap':0,'full_chain_probes':probes,'receiver_source':'unchanged175 whole-hand placement, soft/editable','actual_full_palm_clearance':gaps,'body':'actualFE70 outside removed original moving material; vacated source occlusions are explicit NOT_ART/WHITE, no F026 donor or coded final body','be78_adopted_pixels':0,'image_calls':0,'F069_input':False,'measurement_correction':'Prior be78 visible tail band is occluded by near forearm and is NOT a complete tail diameter. The previous width/axis ratio from that band cannot prove complete tail too thin. If whole returned canvas were uniformly normalized770/1145, lamp rim is near target; none of be78 is used as a prop patch or old-hand source.','limits':'This pixel/input diagnosis is not finished near-arm/torso/hand art or a call gate. Source prop material is hard, unknown old-hand-occluded tube and complete new palm/wrist/thumb/finger joints are one editable action domain. Never bridge low elbow to old high wrist or reuse031 high-wrist grip.'}
(R/'short_check.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print(json.dumps(record,ensure_ascii=False,indent=2))
