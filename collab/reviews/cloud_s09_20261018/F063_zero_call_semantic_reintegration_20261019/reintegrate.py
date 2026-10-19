from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import label,binary_dilation,binary_fill_holes
import numpy as np, json,hashlib
R=Path(__file__).resolve().parent;B=R.parent;P=B/'F063_pixel_plate_call01_4d533a91';S=B/'F063_full_grip_shape_repair_gate_20261019/sources';PL=B/'F063_real_prop_pixel_plate_DIAGNOSTIC_20261019';size=(1672,941);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ar(p):return np.array(Image.open(p).convert('RGBA'))
def mk(p):return np.array(Image.open(p).convert('L'))>0
mother=ar(S/'F044_frozen_HEAD_RUFFLE_SKIRT_MOTHER.png');rawpath=P/'originals/F063_pixel_plate_call01_RAW.png';raw=Image.open(rawpath).convert('RGBA');assert raw.size==(1145,1374);assert sha(rawpath)=='a5bb1af3b79762f79ef37ee9208d40d1351acf7d7e89d9b0d085b949bd82c6a9';assert sha(S/'F044_frozen_HEAD_RUFFLE_SKIRT_MOTHER.png')=='fe70d79e90559659a83772cb29e4cbeffb2b22b355ed3e403509621b381cfad9'
full=Image.new('RGBA',size);full.alpha_composite(raw.resize((770,924),Image.Resampling.LANCZOS),(550,0));new=np.array(full);yy,xx=np.indices(new.shape[:2]);rgb=mother[:,:,:3].astype(int);nr=new[:,:,:3].astype(int)
# Head and neck are the true mother. Collar selection follows its complete two
# real white lobes, not a horizontal rectangle through the new sleeve/front.
hg=mk(S/'F044_actual_head_neck_collar_GUARD.png');white=(rgb[:,:,0]>210)&(rgb[:,:,1]>205)&(rgb[:,:,2]>185)&hg&(yy>450)
lab,_=label(white);collar=np.zeros(white.shape,bool)
for x,y in [(738,540),(850,525)]:
 region=white[max(0,y-12):y+13,max(0,x-12):x+13];qy,qx=np.where(region);j=np.argmin((qx-12)**2+(qy-12)**2);seed=lab[y-12+qy[j],x-12+qx[j]];collar|=lab==seed
collar=binary_dilation(binary_fill_holes(collar),iterations=3)&hg
neck=hg&(rgb[:,:,0]>rgb[:,:,1]+10)&(rgb[:,:,1]>rgb[:,:,2]+10)&(rgb[:,:,2]>90)&(yy<530)&(xx>710)&(xx<865)
hairlow=hg&(yy<503)&((xx<690)|(xx>890))&(rgb.max(axis=2)<160)
head=hg&((yy<480)|collar|neck|hairlow);head=binary_dilation(head,iterations=1)&hg
skirt=mk(S/'F044_stable_skirt_GUARD.png')&(mother[:,:,3]>0);skirt[875:]=mother[875:,:,3]>0
# One broad source-painted front + both sleeves/arms/hands action domain.
# It includes every old moving-material vacancy; no old skin is reintroduced.
domain=(xx>=550)&(xx<1320)&(yy>=490)&(yy<875)&~head&~skirt
base=ar(PL/'layers/FE70_body_original_pixels_old_moving_material_removed.png');out=base.copy();out[domain]=new[domain];out[head]=mother[head];out[skirt]=mother[skirt]
# Extract the entire connected NEW near skin chain solely for foreground
# ownership of the known rigid prop. No hand/arm segment is transformed.
skin=(nr[:,:,0]>160)&(nr[:,:,0]>nr[:,:,1]+16)&(nr[:,:,1]>nr[:,:,2]+8)&(nr[:,:,2]<230)&(new[:,:,3]>=16)&(xx>=665)&(xx<1120)&(yy>=550)&(yy<770)
labs,_=label(skin);near=labs==labs[690,880];assert labs[690,880]!=0
near=binary_dilation(binary_fill_holes(near),iterations=2)&(new[:,:,3]>0);near &= (xx>=665)&(xx<1120)&(yy>=550)&(yy<770)
prop=ar(PL/'layers/FE70_whole_visible_prop_SINGLE_RIGID_transform.png');pm=prop[:,:,3]>0;unknown=mk(PL/'masks/UNKNOWN_original_hand_hidden_cylinder.png')
# Actual RAW red/neutral/ink prop material, excluding the complete near skin.
# Connected ownership avoids deleting isolated white dress dots.
roi=(xx>=825)&(xx<1290)&(yy>=490)&(yy<680)
red=(nr[:,:,0]>1.45*nr[:,:,1])&(nr[:,:,0]>1.6*nr[:,:,2])
neutral=(nr.max(axis=2)-nr.min(axis=2)<48)
material=(red|neutral)&roi&(new[:,:,3]>=16)&~binary_dilation(near,iterations=1)
ll,_=label(material);rawprop=np.zeros(material.shape,bool)
for x,y in [(1220,560),(875,620),(1140,585),(950,600)]:
 if ll[y,x]:rawprop|=ll==ll[y,x]
rawprop=binary_dilation(rawprop,iterations=1)&material&roi&~near
rawprop &= binary_dilation(prop[:,:,3]>=16,iterations=2)|unknown
# Cloth remains behind the prop: do not turn nearby yellow cloth or isolated
# polka dots into transparent prop removal through a filled component loop.
T=np.array([858.3388552980175,636.9294709248006]);L=np.array([1227.0002384706622,562.9985264074178]);u=(L-T)/np.linalg.norm(L-T);v=np.array([-u[1],u[0]]);ax=(xx-T[0])*u[0]+(yy-T[1])*u[1];normal=(xx-T[0])*v[0]+(yy-T[1])*v[1]
rawprop &= red | ((ax<55)&(np.abs(normal)<41)&neutral) | ((ax>305)&neutral) | ((ax>210)&(ax<310)&(np.abs(normal)<28)&neutral) | (binary_dilation(red&roi,iterations=1)&neutral)
far_tool=Image.open(P/'independent_review_61sol/masks/ACTUAL_receiver_alpha128_MANUAL_SEMANTIC_ROI.png').convert('L');far_native=Image.new('L',size);far_native.paste(far_tool.resize((770,924),Image.Resampling.NEAREST),(550,0));far_front=binary_dilation(np.array(far_native)>0,iterations=2)&(new[:,:,3]>0)
# The complete generated lamp-head perimeter must leave before the original
# complete head is returned; retain every actual receiving finger in front.
rawprop |= (ax>305)&roi&(new[:,:,3]>0)&~near&~far_front
rawprop &= ~far_front
stray_raw_perimeter=roi&red&(new[:,:,3]>0)&~pm&~unknown&~near&~far_front
rawprop |= stray_raw_perimeter
# Clear the generated known-prop perimeter before restoring the real known
# pixels, so a second red/metal outline is not left behind. Unknown old-hand
# occlusion may retain only actually returned material in its recorded domain.
# A historical hand-occlusion cut is not a physical cylinder/neck contour.
# Its two-pixel classification border belongs with returned unknown material.
cut=pm&binary_dilation(rawprop&unknown&~pm,iterations=2)&binary_dilation(unknown,iterations=2)
# Keep the actually visible original slider, including its real edge.
g=json.loads((S/'F063_frozen_target_geometry_REFERENCE.json').read_text());M=np.array(g['unit_M']);t=np.array(g['unit_t']);iv=M.T;it=-iv@t
slider=Image.open(PL/'masks/SOURCE_FE70_visible_slider_actual_material.png').convert('L').transform(size,Image.Transform.AFFINE,(*iv[0],it[0],*iv[1],it[1]),Image.Resampling.BICUBIC,fillcolor=0)
slider=np.array(slider)>0;cut &= ~slider
unknown_actual=rawprop&(unknown|cut)&(~pm|cut)
out[rawprop]=0
out[unknown_actual]=new[unknown_actual]
known=pm&~near&~cut
knownlayer=np.where(known[:,:,None],prop,0).astype('uint8');composite=Image.fromarray(out);composite.alpha_composite(Image.fromarray(knownlayer));out=np.array(composite)
# Exact protected mother pixels; transparent exterior is original everywhere
# outside the complete action/remove-old domain.
out[head]=mother[head];out[skirt]=mother[skirt]
Image.fromarray(out).save(R/'candidate/F063_zero_call_semantic_RECONNECTED.png')
for n,m in [('ADOPT_one_complete_front_both_sleeves_arms_and_hands',domain),('KEEP_actual044_head_neck_complete_collar',head),('KEEP_actual044_skirt_material',skirt),('NEW_complete_near_skin_chain_FRONT_of_prop',near),('RAW_actual_prop_semantic_removal_no_second_outline',rawprop),('REMOVE_stray_RAW_prop_perimeter_outside_true_known_and_unknown',stray_raw_perimeter),('KEEP_known_true_prop_AFTER_new_hand_occlusion',known),('KEEP_actual_returned_unknown_cylinder_material_only',unknown_actual)]:Image.fromarray(m.astype('uint8')*255).save(R/'masks'/f'{n}.png')
for n,a in [('NEW_whole_uniform_770over1145_plus550_0',new),('KNOWN_true_prop_correct_new_hand_occlusion',np.where(known[:,:,None],prop,0).astype('uint8')),('NEW_complete_near_skin_chain_for_ownership_ONLY',np.where(near[:,:,None],new,0).astype('uint8'))]:Image.fromarray(a).save(R/'layers'/f'{n}.png')
for tone,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 z=Image.new('RGBA',size,col);z.alpha_composite(Image.fromarray(out));z.convert('RGB').save(R/f'qa/F063_COMPLETE_reconnected_{tone}.png');z.crop((570,450,1295,830)).resize((1450,760),Image.Resampling.NEAREST).save(R/f'qa/F063_complete_front_sleeves_grip_receiver_{tone}_2x.png')
rec={'state':'ZERO_CALL_FULL_SEMANTIC_REINTEGRATION_PENDING_ACTUAL_REVIEW','authority':'Astra accepts a5bb complete sleeve/elbow/wrist/grip as F063 adoption source; 15native nominal target waived; zero-call complete semantic reconnection, preserve true known prop by new hand ownership,044head/neck/skirt/exterior.','mother_sha256':sha(S/'F044_frozen_HEAD_RUFFLE_SKIRT_MOTHER.png'),'raw_sha256':sha(rawpath),'whole_uniform_inverse':{'scale':770/1145,'offset':[550,0]},'known_true_prop_source':str(PL/'layers/FE70_whole_visible_prop_SINGLE_RIGID_transform.png'),'imagegen_calls':0,'per_part_transforms':0,'head_protected_RGBA_changes':int(np.any(out[head]!=mother[head],axis=1).sum()),'skirt_protected_RGBA_changes':int(np.any(out[skirt]!=mother[skirt],axis=1).sum()),'known_visible_prop_LAYER_RGBA_changes':int(np.any(knownlayer[known]!=prop[known],axis=1).sum()),'final_known_edges_use_alpha_composite_over_real_cloth':True,'known_prop_visible_pixels':int(known.sum()),'new_near_chain_foreground_pixels':int(near.sum()),'raw_prop_removed_pixels':int(rawprop.sum()),'actual_unknown_material_kept_pixels':int(unknown_actual.sum()),'no_partial_tail_band_diameter_gate':True}
(R/'qa/reintegration_checks.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n');print(json.dumps(rec,ensure_ascii=False,indent=2))
