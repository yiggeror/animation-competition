#!/usr/bin/env python3
"""Only F068 input: locked062 true layers, actual support and full pants redraw."""
from pathlib import Path
import json,csv,math,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation,label
R=Path(__file__).resolve().parent;B=R.parent;S=R/'sources'
for n in ['reference','layers','masks','qa','geometry','requests']:(R/n).mkdir(exist_ok=True)
assert not (R/'requests/execution_state.json').exists(),'Freeze inputs after a request starts.'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
mother=B/'F062_native_call01/candidate/F062_single_native_final_with_waist_underlay_PENDING_ASTRA.png'
assert sha(mother)=='393622a77349083751122520b690bd35017f8535a25560d8cca775446d2eeb2f'
mi=Image.open(mother).convert('RGBA');ma=np.array(mi);size=mi.size;yy,xx=np.indices(ma.shape[:2])
meta=json.loads((S/'F062_preparation_actual_metadata.json').read_text());reg=meta['registration'];s=reg['s'];off=np.array([reg['tx'],reg['ty']]);world=lambda q:(np.array(q)*s+off).tolist()
states={v['frame']:v for v in json.loads((S/'arm_swing_v2_legacy_intents.json').read_text())['states']}
f62,f68=states[62],states[68]
body_delta_world=np.array(f68['head_center'])-np.array(f62['head_center']);body_delta=body_delta_world/s
assert f68['planted_feet']==['near','far'] and f68['hold_frames']==5
exposure=list(csv.DictReader((S/'exposure.csv').open()))
sources={n:Image.open(S/f'F062_{n}.png').convert('RGBA') for n in ['far_shoe_ankle','far_complete_arm_jade_hand','body_head_blouse','near_complete_arm','near_shoe_ankle_FIXED']}
pant=Image.open(S/'F062_native_complete_trousers_color_locked.png').convert('RGBA');pa=np.array(pant)
umeta=json.loads((S/'F062_internal_waist_mapping.json').read_text());under=np.zeros_like(ma)
for m in umeta['source_to_target_mappings']:
    x,y=m['target_xy'];sx,sy=m['native_cloth_donor_xy'];assert pa[sy,sx].tolist()==m['donor_RGBA'];under[y,x]=pa[sy,sx]
complete_pants=Image.alpha_composite(Image.fromarray(under),pant)
verify=Image.new('RGBA',size)
for z in [sources['far_shoe_ankle'],complete_pants,sources['far_complete_arm_jade_hand'],sources['body_head_blouse'],sources['near_complete_arm'],sources['near_shoe_ankle_FIXED']]:verify.alpha_composite(z)
assert np.array_equal(np.array(verify),ma),'Production layer snapshots must exactly reproduce locked393 mother.'
complete_pants.save(R/'reference/locked062_actual_complete_trousers_layer.png')

def rotation(deg):
    t=math.radians(deg);return np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]])
def rigid(z,mat,delta):
    inv=mat.T;v=-inv@delta;assert np.allclose(mat.T@mat,np.eye(2),atol=1e-12)
    return z.transform(size,Image.Transform.AFFINE,(*inv[0],v[0],*inv[1],v[1]),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
def capsule(points,r):
    points=[tuple(map(float,p))for p in points]
    z=Image.new('L',size);d=ImageDraw.Draw(z);d.line(points,fill=255,width=2*r+1)
    for x,y in points:d.ellipse((x-r,y-r,x+r,y+r),fill=255)
    return np.array(z)>0
def polygon(points):
    z=Image.new('L',size);ImageDraw.Draw(z).polygon(points,fill=255);return np.array(z)>0
near_ank=np.array(meta['near062_chain_native'][-1]);far_ank062=np.array(meta['far062_shape_proxy_native'][-1])
# Actual complete landed shoe layer, not old758 skeleton ankles or old hulls.
far62=np.array(sources['far_shoe_ankle']);sole62=int(np.where(far62[:,:,3]>=128)[0].max())
far_dx_world=float(f68['far_ankle'][0]-f62['far_ankle'][0]);far_delta=np.array([far_dx_world/s,1022-sole62]);far_ank68=far_ank062+far_delta
body=rigid(sources['body_head_blouse'],np.eye(2),body_delta)
# The inherited body extraction contains a few OLD far-arm AA pixels.
# Clear only verified warm skin/old-ink or its isolated AA island from this
# derived body layer. Real blouse blue/flowers and both whole arm sources stay.
body_before=np.array(body);br=body_before[:,:,:3].astype(int)
warm=(br[:,:,0]>br[:,:,1]+3)&(br[:,:,1]>br[:,:,2]+3)&(br[:,:,0]>br[:,:,2]+12)
old_flank=(xx>=1093)&(xx<=1103)&(yy>=385)&(yy<=498)
body_old_arm_cleanup=old_flank&warm&(body_before[:,:,3]>0)
components,_=label(body_before[:,:,3]>20)
island_ids=np.unique(components[503:521,1108:1116])
for ident in island_ids:
    if not ident:continue
    fragment=components==ident;fy,fx=np.where(fragment)
    if fx.min()>=1106 and fx.max()<=1118 and fy.min()>=499 and fy.max()<=524:
        body_old_arm_cleanup|=binary_dilation(fragment,iterations=1)&(body_before[:,:,3]>0)
cleaned_body=body_before.copy();cleaned_body[body_old_arm_cleanup]=0
body=Image.fromarray(cleaned_body)
Image.fromarray(body_old_arm_cleanup.astype('uint8')*255).save(R/'masks/derived_body_OLD_far_arm_skin_ink_cleanup.png')
cy,cx=np.where(body_old_arm_cleanup)
cleanup_report={'operation':'RGBA transparent removal of verified OLD far-arm extraction debris from derived translated body only; no RGB painting',
 'source_snapshots_modified':False,'locked062_modified':False,'complete_arm_layers_modified':False,
 'pixels_removed':int(body_old_arm_cleanup.sum()),'source_body_translation_native':body_delta.tolist(),
 'mapping_note':'Derived pixels were uniformly bicubic translated; inverse source coordinates are fractional sampling coordinates, not falsely claimed integer pixel copies.',
 'removed_pixels':[{'derived_xy':[int(x),int(y)],'before_RGBA':body_before[y,x].tolist(),'original_body_inverse_sample_xy':(np.array([x,y])-body_delta).tolist()}for y,x in zip(cy,cx)],
 'true_blue_white_flower_changes':0}
(R/'geometry/derived_body_old_arm_cleanup_checks.json').write_text(json.dumps(cleanup_report,ensure_ascii=False,indent=2)+'\n')
nearfoot=sources['near_shoe_ankle_FIXED'].copy();farfoot=rigid(sources['far_shoe_ankle'],np.eye(2),far_delta)
# Small whole-real-arm counterphase around actual visible sleeve outlets;
# all finger/jade pixels share their arm affine. No old623 wrist target.
roots062={'near':np.array([727.,369.])+np.array(meta['head_blouse_delta_world'])/s,'far':np.array([903.,367.])+np.array(meta['head_blouse_delta_world'])/s}
arm_degrees={'near':-15.,'far':15.};arms={};root68={};arm_matrices={}
for side,name in [('near','near_complete_arm'),('far','far_complete_arm_jade_hand')]:
    mat=rotation(arm_degrees[side]);t=roots062[side]+body_delta-mat@roots062[side];arms[side]=rigid(sources[name],mat,t);root68[side]=roots062[side]+body_delta;arm_matrices[side]={'rotation_degrees':arm_degrees[side],'translation_native':t.tolist(),'scale':1}
# Keep a complete real cloth layer as material reference. Its old bent pose
# is explicitly obsolete/white, not a new imposed hip or knee construction.
oldpants=rigid(complete_pants,np.eye(2),body_delta)
layers={'far_shoe_ankle_LANDED':farfoot,'old062_trousers_material_OBSOLETE_POSE':oldpants,'far_complete_arm_jade_hand':arms['far'],'body_head_blouse':body,'near_complete_arm':arms['near'],'near_shoe_ankle_FIXED':nearfoot}
order=list(layers)
canvas=Image.new('RGBA',size)
for name,z in layers.items():canvas.alpha_composite(z);z.save(R/'layers'/f'F068_{name}.png')
pre=R/'reference/F068_actual_source_preposition_NOT_ART.png';canvas.save(pre);out=np.array(canvas);alpha={n:np.array(z)[:,:,3] for n,z in layers.items()}
def visible(name):
    front=np.zeros(ma.shape[:2],bool)
    for n in order[order.index(name)+1:]:front|=alpha[n]>0
    return (alpha[name]>0)&~front
bodymat=alpha['body_head_blouse']>0
sleeves=np.zeros(ma.shape[:2],bool)
for q in root68.values():sleeves|=capsule([q+[-19,-3],q+[19,14]],15)
armguard=(visible('near_complete_arm')|visible('far_complete_arm_jade_hand'))&~sleeves
bodyguard=bodymat&~sleeves
# No blank padding moat; only actual visible shoe/ankle material is locked.
# Far source foot stays physically below the new trousers. Where a new cuff
# can cover its ankle, keep that full source layer for output recomposition.
near_guard=visible('near_shoe_ankle_FIXED')
far_actual=alpha['far_shoe_ankle_LANDED']>0
new_far_cuff=capsule([far_ank68+[-40,-27],far_ank68+[42,-10]],18)
far_guard=visible('far_shoe_ankle_LANDED')&~new_far_cuff
hard=bodyguard|armguard|near_guard|far_guard
oldmat=alpha['old062_trousers_material_OBSOLETE_POSE']>0
waist_guide=np.array([886.855796820236,603.2865215876859])+body_delta
# Cloth corridor only; these are not fixed/remeasured anatomical joints.
near_corridor=capsule([waist_guide,near_ank+[65,-165],near_ank],63)
far_corridor=capsule([waist_guide+[-20,3],far_ank68+[-20,-160],far_ank68],61)
hip=capsule([waist_guide+[-85,-67],waist_guide+[50,-67]],48)
semantic=binary_dilation(oldmat,iterations=9)|near_corridor|far_corridor|hip|sleeves|new_far_cuff|body_old_arm_cleanup
edit=semantic&~hard
crop=(700,280,1220,1060);inside=(xx>=700)&(xx<1220)&(yy>=280)&(yy<1060);outside_material=int((edit&~inside&(out[:,:,3]>20)).sum());assert outside_material==0
edit&=inside
for name,z in [('F068_complete_trousers_and_sleeves_WHITE_EDIT_PENDING',edit),('HARD_actual_head_blouse_except_sleeves',bodyguard),('HARD_visible_complete_arms_except_sleeves',armguard),('HARD_near_fixed_shoe_ankle_actual_material',near_guard),('HARD_far_landed_shoe_visible_material',far_guard),('full_far_landed_foot_LAYER_not_blank_guard',far_actual),('complete_old_new_pants_semantic_GUIDE',semantic),('far_cuff_new_occlusion_RELEASE',new_far_cuff)]:Image.fromarray(z.astype('uint8')*255).save(R/'masks'/f'{name}.png')
canvas.crop(crop).save(R/'reference/F068_crop_RGBA_NOT_ART.png');Image.fromarray(edit.astype('uint8')*255).crop(crop).save(R/'masks/F068_crop_WHITE_EDIT_PENDING.png')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17)
def bg(z,col=(213,223,231,255)):
    q=Image.new('RGBA',size,col);q.alpha_composite(z);return q
guide=bg(canvas).convert('RGB');d=ImageDraw.Draw(guide)
floor=1022;d.line((750,floor,1190,floor),fill='#33858e',width=2)
for pt,col,label in [(near_ank,'#0087b5','near RIGHT / same planted shoe'),(far_ank68,'#c37926','far LEFT / landing')]:
    x,y=pt;d.ellipse((x-7,y-7,x+7,y+7),outline=col,width=3);d.text((x-85,y-35),label,fill=col)
d.text((40,25),'068落远左脚｜实际源像素预摆｜非画稿／未过输入门',font=font,fill='#24343f')
d.text((40,53),'近右鞋原位；远左鞋+66worldX并按真实底落1022native；双支撑→远左承重',font=font,fill='#24343f')
d.text((40,81),'白域整裤旧姿态全重绘；不采用旧744/791髋、758踝或64/58骨长',font=font,fill='#9d5543')
guide.save(R/'qa/F068_actual_support_and_ownership.png')
for nm,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
    q=bg(canvas,col);q.convert('RGB').save(R/f'qa/F068_full_{nm}.png');wash=Image.new('RGBA',size,(219,36,121,0));wash.putalpha(Image.fromarray(edit.astype('uint8')*105));ov=q.copy();ov.alpha_composite(wash);ov.crop(crop).save(R/f'qa/F068_crop_complete_edit_{nm}.png')
    sheet=Image.new('RGB',(1590,830),(236,241,245));dr=ImageDraw.Draw(sheet)
    for i,(label,z)in enumerate([('已锁062真实母态',bg(mi,col)),('068目标足／头衣／旧裤材质预摆',q),('068完整裤体白域／待作者审',ov)]):
        sheet.paste(z.crop(crop).convert('RGB'),(i*530,40));dr.text((i*530+4,8),label,font=font,fill='#24343f')
    sheet.save(R/f'qa/F062_F068_actual_preposition_and_mask_{nm}.png')
feet=Image.new('RGB',(1120,410),(219,226,233));dr=ImageDraw.Draw(feet)
for i,(label,z)in enumerate([('近右同一整鞋／原位',nearfoot),('远左原整鞋／已落地',farfoot),('双鞋实际层次／地面',canvas)]):
    p=bg(z).crop((760,875,1200,1040)).resize((360,135));feet.paste(p.convert('RGB'),(i*370+5,45));dr.text((i*370+5,10),label,font=font,fill='#24343f')
feet.save(R/'qa/actual_shoe_layers_and_floor.png')
soles={}
for name,z in [('near',nearfoot),('far',farfoot)]:
    al=np.array(z)[:,:,3];ys,xs=np.where(al>=128);soles[name]={'native_bottom':int(ys.max()),'world_bottom':int(ys.max())*s+off[1],'opaque_x_span':[int(xs.min()),int(xs.max())]}
assert soles['near']['native_bottom']==soles['far']['native_bottom']==1022
assert np.array_equal(np.array(nearfoot),np.array(sources['near_shoe_ankle_FIXED']))
checks={'source_mother_sha256':sha(mother),'mother062_layer_reconstruction_RGBA_changes':int(np.any(np.array(verify)!=ma,axis=2).sum()),'native_size':size,'registration':reg,'frame':68,'hold':5,'inclusive_frames':[68,72],'phase':'double support, farLEFT landing and taking load','source062_near_shoe_already_planted':True,'near_whole_shoe_layer_RGBA_changes':0,'far_whole_foot_translation_native':far_delta.tolist(),'far_translation_world':[far_dx_world,float(far_delta[1]*s)],'far_old_requested_y_intent_world':23,'actual_landing_rounding_difference_world':float(far_delta[1]*s-23),'body_head_translation_world':body_delta_world.tolist(),'body_head_translation_native':body_delta.tolist(),'arm_whole_rigid_small_counterphase':arm_matrices,'far_jade_whole_same_arm_transform':True,'far_jade_may_be_naturally_occluded_by_original_blouse':True,'actual_feet':soles,'white_pixels':int(edit.sum()),'crop_xyxy':crop,'crop_size':[520,780],'guard_intersections':{n:int((edit&m).sum())for n,m in [('headbody',bodyguard),('completevisiblearms',armguard),('realnearfoot',near_guard),('realfarfootvisible',far_guard)]},'visible_old_trousers_material_alpha20_not_white_except_real_foreground':int((oldmat&(out[:,:,3]>20)&~edit&~hard).sum()),'mask_clipped_visible_material':outside_material,'true_062_source_pants_complete_and27pixel_underlay_preserved_in_material_reference':True,'historical_withdrawals':['Absolute791waist-pivot and744hip never reused.','Legacy068hip970/615,ankle758,wrist623,projected64/58arm and78/72leg lengths are not actual new mother coordinates.','No reachability claim from a single unobservable2D hip; current068 complete trousers require native whole-cloth articulation.'],'limits':['Visible white old062 raised-leg cloth is obsolete material reference, not target068 knee/hem geometry or accepted artwork.','Body/head keep approved beat; both true feet are already positioned. New pants must connect those actual endpoints with natural volume, not follow source extraction edges.','No articulated-body code drawing, segment stretch, footslide, global color change, generation or073preparation.','Far-foot full source is retained below trousers; only actual visible material is an edit guard. Postnative occlusion must be recomputed from actual new pants, not old preposition alpha.'],'new_image_calls':0,'F073_unopened':True,'status':'PREPARED_ONLY_SINGLE_F068_PENDING_AUTHOR_AND_ASTRA_INPUT_GATE_NOT_CALLED'}
assert all(v==0 for v in checks['guard_intersections'].values())
(R/'geometry/preparation_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
prompt='''Edit ONLY WHITE pixels of image2 in image1, the520x780 transparent F068 input crop. Image3 is the locked actual F062 full character for identity, clothes palette and natural limb volume. Keep the exact520x780 crop and framing. Return the same transparent crop; no scaling, reframing, mirroring or background.

F068 is the far anatomical LEFT foot LANDING,5frames: double support changing load toward the far left leg. The grandmother still faces RIGHT. Her near anatomical RIGHT arm has the bare wrist, and the far LEFT arm owns the jade bangle. No lamp or hand contact. The entire true original near RIGHT shoe on imageLEFT/BACK is ALREADY fixed at its previous floor position. The original far LEFT shoe is ALREADY placed forward on imageRIGHT at the SAME actual ground baseline. Do not move, turn, shrink, reshape or redraw either shoe, heel, toe, sole or true ankle material outside white. Do not invent a third foot, new shoe fragment, ground, shadow or glow.

REDRAW THE COMPLETE WHITE TROUSERS from the source blouse waist/hip opening through BOTH entire thighs, knees, calf volumes and cuff openings into the two already-positioned real feet. The visible old bent F062 trousers in white are OBSOLETE MATERIAL REFERENCE ONLY, not the target pose or a knee-seam patch to retain. The near RIGHT leg connects naturally back/down to the unchanged imageLEFT shoe; the far LEFT leg extends naturally down/forward to the imageRIGHT landed shoe. Show natural double support and weight beginning to transfer to the far leg; preserve accepted body proportions and cloth volume, no stretched or shortened leg, disconnected knee, straight cutting flap or severe kink. Use the accepted native cloth palette, separate flat navy and dark crease planes and continuous black contour; no gray background seam or blue shirt patch under the hem. Remove all old trouser fragments and vacated edges across the full white region. No old proxy hip or construction stick figure is an anatomical measurement.

Original complete source head, body/blouse, flowers, glasses, grayhair and both arms are already at the approved beat. Near whole arm has a small forward counter-swing, far whole jade arm backward, maintaining their full real source anatomy. Keep all BLACK material unchanged. Only tiny WHITE sleeve-root connection gaps may be joined naturally; do not adopt a moved hand, extra shadow hand, new bangle or blue rectangle. The far arm remains behind the original blouse and may be hidden there; do not make a hand grow from the waist or draw the jade through the blouse. Preserve foreground near arm ownership.

The original far shoe is a BACK layer: new real trousers may naturally cover its proximal ankle/cuff where white allows, while preserving the same actual shoe below. Do not use a hidden back-layer outline to cut a hole in new foreground cloth. Keep the real soles on their current common baseline, retain the whole original near shoe. No global skin/clothes recolor or lighting changes, no mask colors, guides, arrows, text, blur, extra props or invented pixels. This is ONLY F068; F073 remains unopened.'''
(R/'requests/prompt_PREPARED_NOT_CALLED.txt').write_text(prompt+'\n');args={'prompt':prompt,'referenced_image_paths':[str(R/'reference/F068_crop_RGBA_NOT_ART.png'),str(R/'masks/F068_crop_WHITE_EDIT_PENDING.png'),str(mother)],'transparent_background':True};(R/'requests/arguments_PREPARED_NOT_CALLED.json').write_text(json.dumps(args,ensure_ascii=False,indent=2)+'\n')
(R/'requests/input_manifest_PENDING_REVIEW.json').write_text(json.dumps({'status':'PREPARED_ONLY_NOT_EXECUTED','inputs':[{'path':p,'sha256':sha(p)}for p in args['referenced_image_paths']],'source_snapshots':'sources/snapshot_manifest.json','new_image_calls':0},ensure_ascii=False,indent=2)+'\n')
(R/'README.md').write_text('F068单态输入预备，未生成、未提交、待实际输入门。唯一母为锁393622a…的真实062。sources逐字节快照真实裤层/27px内部底层映射/独立身体双臂双足及意图表；脚本先逐RGBA重现母062，确保没有退回旧代理造型。\n\n068×5：远左落地，近右保持原地，双支撑转远左承重。以真实源足alpha128底落1022native=774.874world；远足X按既定事件+66world，Y按真底下63native，近足整层原位。头衣沿既定beat增量，双臂完整真实刚体小反相，远镯随同一整臂可被体衣自然遮挡。\n\n图中旧062裤形仅材质提示，整裤在白域重画，不能保其旧弯腿或提取切边。隐藏髋/膝未从旧表硬套到新母，旧791/744/758/623点与64/58施工骨长不作实际新骨架。供实际门看真实脚位、体衣、层次及整裤修绘范围；不以坐标证明自然度。\n\n推荐520×780同框输入，无额外padding或变形。完整新裤/源旧边白域，真实可见手臂/体衣和两鞋为实际保护材料，后续成态须按新裤重新核远足遮挡，不能锁隐藏alpha。未开073，不把本预摆称为画稿或调用通过。\n')
print(json.dumps({'status':checks['status'],'source062_replay_changes':checks['mother062_layer_reconstruction_RGBA_changes'],'preposition':str(pre),'sha256':sha(pre),'mask_pixels':int(edit.sum()),'actual_feet':soles,'body_delta_world':body_delta_world.tolist(),'far_foot_delta_native':far_delta.tolist()},ensure_ascii=False))
