#!/usr/bin/env python3
"""F073 only: whole real source layers, far-foot support, complete pants edit."""
from pathlib import Path
import json,math,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation
R=Path(__file__).resolve().parent;S=R/'sources'
assert not (R/'requests/execution_state.json').exists()
for d in ['reference','layers','masks','qa','geometry','requests']:(R/d).mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(S/'F068_final.png')=='8210a8d56c15a42da4b4daa6c4a4599ce6b2df9b1f5fdab2e1403ec7f9960768'
for f in json.loads((S/'snapshot_manifest.json').read_text())['files']:assert sha(S/f['path'])==f['sha256']
mother=Image.open(S/'F068_final.png').convert('RGBA');size=mother.size;ma=np.array(mother);yy,xx=np.indices(ma.shape[:2])
meta=json.loads((S/'F062_calibrated_preparation_metadata.json').read_text());reg=meta['registration'];s=reg['s'];off=np.array([reg['tx'],reg['ty']])
g68=json.loads((S/'F068_preparation_checks.json').read_text());legacy={v['frame']:v for v in json.loads((S/'legacy_event_intents.json').read_text())['states']};f68,f73=legacy[68],legacy[73]
body_delta_world=np.array(f73['head_center'])-np.array(f68['head_center']);body_delta=body_delta_world/s
assert f73['hold_frames']==6 and f73['planted_feet']==['far']
src={n:Image.open(S/f'F068_{n}.png').convert('RGBA')for n in ['far_shoe_ankle_LANDED','far_complete_arm_jade_hand','body_head_blouse','near_complete_arm','near_shoe_ankle_FIXED']}
pants=Image.open(S/'F068_native_trousers_color_locked.png').convert('RGBA')
replay=Image.new('RGBA',size)
for z in [src['far_shoe_ankle_LANDED'],pants,src['far_complete_arm_jade_hand'],src['body_head_blouse'],src['near_complete_arm'],src['near_shoe_ankle_FIXED']]:replay.alpha_composite(z)
assert np.array_equal(np.array(replay),ma),'Snapshots must reproduce actual final8210 mother exactly.'
def rot(d):
 t=math.radians(d);return np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]])
def rigid(z,m,t):
 assert np.allclose(m.T@m,np.eye(2),atol=1e-12)
 inv=m.T;v=-inv@t
 return z.transform(size,Image.Transform.AFFINE,(*inv[0],v[0],*inv[1],v[1]),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
def capsule(points,r):
 points=[tuple(map(float,p))for p in points];z=Image.new('L',size);d=ImageDraw.Draw(z);d.line(points,fill=255,width=2*r+1)
 for x,y in points:d.ellipse((x-r,y-r,x+r,y+r),fill=255)
 return np.array(z)>0
body=rigid(src['body_head_blouse'],np.eye(2),body_delta)
farfoot=src['far_shoe_ankle_LANDED'].copy()
near_delta=np.array([(f73['near_ankle'][0]-f68['near_ankle'][0])/s,-63.])
nearfoot=rigid(src['near_shoe_ankle_FIXED'],np.eye(2),near_delta)
# Use accepted real sleeve-outlet proxies and whole real arm layers. No old
# absolute wrist623 or separate hand transform; 12deg returns toward midphase.
root62={'near':np.array([727.,369.])+np.array(meta['head_blouse_delta_world'])/s,'far':np.array([903.,367.])+np.array(meta['head_blouse_delta_world'])/s}
root68={k:v+np.array(g68['body_head_translation_native'])for k,v in root62.items()};root73={k:v+body_delta for k,v in root68.items()}
arms={};affines={}
for side,n,d in [('near','near_complete_arm',12.),('far','far_complete_arm_jade_hand',-12.)]:
 m=rot(d);t=root68[side]+body_delta-m@root68[side];arms[side]=rigid(src[n],m,t);affines[side]={'rotation_from_actual068_degrees':d,'matrix':m.tolist(),'translation_native':t.tolist(),'scale':1}
oldpants=rigid(pants,np.eye(2),body_delta)
layers={'far_shoe_ankle_SUPPORT_FIXED':farfoot,'old068_trousers_OBSOLETE_MATERIAL':oldpants,'far_complete_arm_jade_hand':arms['far'],'body_head_blouse':body,'near_complete_arm':arms['near'],'near_shoe_ankle_SWING':nearfoot};order=list(layers)
pre=Image.new('RGBA',size)
for n,z in layers.items():z.save(R/'layers'/f'F073_{n}.png');pre.alpha_composite(z)
out=np.array(pre);alpha={n:np.array(z)[:,:,3]for n,z in layers.items()}
def visible(n):
 front=np.zeros(ma.shape[:2],bool)
 for q in order[order.index(n)+1:]:front|=alpha[q]>0
 return (alpha[n]>0)&~front
nearA=np.array(meta['near062_chain_native'][-1])+near_delta
farA=np.array(meta['far062_shape_proxy_native'][-1])+np.array(g68['far_whole_foot_translation_native'])
hiddenH=np.array([886.855796820236,603.2865215876859])+np.array(g68['body_head_translation_native'])+body_delta
sleeves=np.zeros(ma.shape[:2],bool)
for q in root73.values():sleeves|=capsule([q+[-20,-3],q+[20,14]],15)
bodyguard=(alpha['body_head_blouse']>0)&~sleeves
armguard=(visible('near_complete_arm')|visible('far_complete_arm_jade_hand'))&~sleeves
near_guard=visible('near_shoe_ankle_SWING')
far_cuff=capsule([farA+[-42,-30],farA+[42,-10]],19)
far_guard=visible('far_shoe_ankle_SUPPORT_FIXED')&~far_cuff
hard=bodyguard|armguard|near_guard|far_guard
oldmat=alpha['old068_trousers_OBSOLETE_MATERIAL']>0
near_corr=capsule([hiddenH+[10,0],nearA+[65,-135],nearA],64)
far_corr=capsule([hiddenH+[-15,3],farA+[-5,-160],farA],63)
hip=capsule([hiddenH+[-90,-67],hiddenH+[50,-67]],49)
# Include the original whole068 trouser footprint as a vacated-domain guide;
# no old navy contour may become a protected new leg or standalone flap.
semantic=binary_dilation(oldmat,iterations=9)|near_corr|far_corr|hip|sleeves|far_cuff
crop=(780,280,1300,1060);inside=(xx>=780)&(xx<1300)&(yy>=280)&(yy<1060)
edit=semantic&~hard
assert not (edit&~inside&(out[:,:,3]>20)).any(),'Crop must contain actual edited source material.'
edit&=inside
for n,z in [('F073_complete_trousers_sleeves_WHITE_EDIT_PENDING',edit),('HARD_actual_head_blouse_except_sleeves',bodyguard),('HARD_visible_complete_arms_except_sleeves',armguard),('HARD_near_swing_shoe_actual_material',near_guard),('HARD_far_support_shoe_visible_material',far_guard),('full_far_support_foot_LAYER_not_hidden_guard',alpha['far_shoe_ankle_SUPPORT_FIXED']>0),('far_cuff_new_occlusion_RELEASE',far_cuff),('complete_old_new_pants_semantic_GUIDE',semantic)]:Image.fromarray(z.astype('uint8')*255).save(R/'masks'/f'{n}.png')
pre.save(R/'reference/F073_actual_source_preposition_NOT_ART.png');pre.crop(crop).save(R/'reference/F073_crop_RGBA_NOT_ART.png');Image.fromarray(edit.astype('uint8')*255).crop(crop).save(R/'masks/F073_crop_WHITE_EDIT_PENDING.png')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17)
def bg(z,col):
 q=Image.new('RGBA',size,col);q.alpha_composite(z);return q
for tag,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 q=bg(pre,col);q.convert('RGB').save(R/f'qa/F073_full_{tag}.png');wash=Image.new('RGBA',size,(219,36,121,0));wash.putalpha(Image.fromarray(edit.astype('uint8')*105));ov=q.copy();ov.alpha_composite(wash);ov.crop(crop).save(R/f'qa/F073_crop_complete_edit_{tag}.png')
 sheet=Image.new('RGB',(1590,830),(236,241,245));d=ImageDraw.Draw(sheet)
 for j,(title,z)in enumerate([('真实068母态／8210',bg(mother,col)),('073源像素足位／旧裤材质非画稿',q),('073完整双裤白域／待输入审',ov)]):sheet.paste(z.crop(crop).convert('RGB'),(j*530,40));d.text((j*530+4,8),title,font=font,fill='#24343f')
 sheet.save(R/f'qa/F068_F073_actual_preposition_and_mask_{tag}.png')
guide=bg(pre,(213,223,231,255)).convert('RGB');d=ImageDraw.Draw(guide);d.line((940,1022,1230,1022),fill='#33858e',width=2)
d.text((40,25),'073近右过步／远左支撑｜仅实际像素预摆，非成态',font=font,fill='#24343f')
d.text((40,53),'远鞋整层原位1022底；近鞋+83worldX／上63native，959底',font=font,fill='#24343f')
for pt,col,t in [(farA,'#c37926','far LEFT support FIXED'),(nearA,'#0087b5','near RIGHT swing')]:
 x,y=pt;d.ellipse((x-7,y-7,x+7,y+7),outline=col,width=3);d.text((x-60,y-35),t,fill=col)
guide.save(R/'qa/F073_actual_support_and_ownership.png')
feet=Image.new('RGB',(1120,400),(219,226,233));d=ImageDraw.Draw(feet)
for j,(t,z)in enumerate([('远左支撑／完整同鞋原位',farfoot),('近右过步／完整同鞋刚体平移',nearfoot),('真实前后层次／新裤待重绘',pre)]):
 q=bg(z,(213,223,231,255)).crop((950,825,1230,1045)).resize((350,275));feet.paste(q.convert('RGB'),(j*370,40));d.text((j*370+2,8),t,font=font,fill='#24343f')
feet.save(R/'qa/actual_support_and_swing_shoes.png')
soles={}
for n,z in [('far_support',farfoot),('near_swing',nearfoot)]:
 ys,xs=np.where(np.array(z)[:,:,3]>=128);soles[n]={'native_bottom':int(ys.max()),'world_bottom':float(ys.max()*s+off[1]),'x_span_alpha128':[int(xs.min()),int(xs.max())]}
assert soles['far_support']['native_bottom']==1022 and soles['near_swing']['native_bottom']==959
assert np.array_equal(np.array(farfoot),np.array(src['far_shoe_ankle_LANDED']))
checks={'status':'F073_SINGLE_INPUT_PREPARED_NOT_GENERATED_PENDING_REVIEW','mother068_sha256':sha(S/'F068_final.png'),'mother_layer_replay_RGBA_changes':int(np.any(np.array(replay)!=ma,axis=2).sum()),'frame':73,'hold_frames':6,'inclusive_frames':[73,78],'phase':'far anatomical LEFT single support; near RIGHT passing swing','registration':reg,'body_head_delta_world':body_delta_world.tolist(),'body_head_delta_native':body_delta.tolist(),'near_complete_shoe_translation_native':near_delta.tolist(),'near_complete_shoe_translation_world':[83.,float(-63*s)],'near_foot_intent23world_difference':float(23-63*s),'far_complete_support_shoe_RGBA_changes':int(np.any(np.array(farfoot)!=np.array(src['far_shoe_ankle_LANDED']),axis=2).sum()),'actual_feet':soles,'whole_actual_arm_transforms':affines,'sleeve_roots_native':{k:v.tolist()for k,v in root73.items()},'hidden_hip_proxy_native':hiddenH.tolist(),'hidden_hip_note':'Accepted062 manual hidden joint proxy plus approved beat deltas; guide only, not anatomical measurement or shirt-hem pivot. Whole new trousers must naturally connect real feet without forcing old projected lengths.','crop_xyxy':crop,'crop_size':[520,780],'white_pixels':int(edit.sum()),'guard_intersections':{k:int((edit&v).sum())for k,v in [('body',bodyguard),('complete_arms',armguard),('near_swing_foot',near_guard),('far_visible_support_foot',far_guard)]},'old_visible_pants_material_alpha20_uneditable_except_real_foreground':int((oldmat&(out[:,:,3]>20)&~edit&~hard).sum()),'palette_anchor':'sources/F062_palette_anchor.png SHA393622a; navy mean anchor in sources/F068_native_layered_checks.json is actual062, do not recursively shift palette from068','limits':['Old068 pants are obsolete material, whole new support/swing pose must be natively drawn.','Far full shoe layer fixed below new pants; guard visibility must follow actual new foreground after output.','Near full swing shoe preserved as original whole source material; no code articulation, scaling, shoe roll, footslide or generated image.','Only requested073 preparation; no079 or11-state expansion.'],'new_image_calls':0}
assert not any(checks['guard_intersections'].values())
(R/'geometry/preparation_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
prompt='''Edit only WHITE pixels in image2 of the520x780 transparent F073 input crop image1. Image3 is the actual accepted single-output F068 mother for identity/proportion. Image4 is the actual locked F062 palette anchor; retain the already accepted057/062 skin/blouse/navy palette, do not cumulatively brighten from068. Return exactly the same crop framing, transparency and size; no resizing, camera change, padding, mirroring or background.

F073 holds6frames: far anatomical LEFT leg supports the grandmother while the near anatomical RIGHT leg PASSES FORWARD raised. She faces RIGHT. The full far LEFT shoe on imageRIGHT/LOWER is ALREADY at the same fixed world position and real sole baseline as F068. The complete near RIGHT shoe is ALREADY positioned forward and raised63native pixels above the support floor. Keep both genuine shoes/heels/toes/soles and original true ankle skin exactly where they are outside WHITE. Do not add a third foot, shifted shoe shadow or new hand. Near right arm has bare wrist and is foreground; far left jade bangle belongs to that same complete far arm behind blouse. No lamp contact.

Draw the COMPLETE WHITE TROUSERS anew from the hidden hip inside the original blouse/pants volume through BOTH full thighs, knee masses, calf volumes and cuff openings into these two real feet. The old068 pants in white are OBSOLETE MATERIAL REFERENCE, not the073 leg pose and not narrow seams to retain. Near RIGHT thigh/knee bends naturally forward to the raised near shoe; far LEFT leg bears weight into the same lower planted far shoe. Preserve accepted actual limb volume/proportion; use a natural subtle pelvic settling over support, never take the blue shirt hem as the actual hip or stretch straight trouser strips to reach. Do not force old construction hip/ankle coordinates or apparent2D bone lengths. Continuous full silhouette, natural knee rear-plane folds and navy/ink planes; remove complete old contour/fragments and vacated clothes edges in WHITE. No gray collar-like gap at cuffs or blue patch at waist.

The source head/body/blouse and both complete real arms already follow the approved beat. The arms have a small counterphase returning toward midposition; keep all BLACK real arm/fingers/jade material unchanged. Join only WHITE sleeve-root gaps using continuous genuine fabric/skin; no duplicate cuff arc or wrist slicing. The far supporting foot is a BACK layer: new native trousers may cover its proximal ankle naturally where WHITE allows; do not lock hidden foot alpha over new foreground cloth or cut holes in the new leg. Keep the full far shoe and common support floor position unchanged. Preserve all real white flowers, grayhair, glasses, ink and source colors. No relighting, text, guides, mask colors, global recolor, blur, extra props or background. Only F073.'''
(R/'requests/prompt_PREPARED_NOT_CALLED.txt').write_text(prompt+'\n')
args={'prompt':prompt,'referenced_image_paths':[str(R/'reference/F073_crop_RGBA_NOT_ART.png'),str(R/'masks/F073_crop_WHITE_EDIT_PENDING.png'),str(S/'F068_final.png'),str(S/'F062_palette_anchor.png')],'transparent_background':True}
(R/'requests/arguments_PREPARED_NOT_CALLED.json').write_text(json.dumps(args,ensure_ascii=False,indent=2)+'\n')
(R/'requests/input_manifest_PENDING_REVIEW.json').write_text(json.dumps({'status':'PREPARED_ONLY_NOT_EXECUTED','inputs':[{'path':p,'sha256':sha(p)}for p in args['referenced_image_paths']],'new_image_calls':0},ensure_ascii=False,indent=2)+'\n')
(R/'README.md').write_text('F073单态输入预备，未调用。唯一母8210a8d…的真实068；sources完整生产层逐RGBA重放母态0差异，可独立复现。\n\n远左鞋完整逐RGBA原位1022底；近右完整同鞋+83worldX/上63native为959底。头衣沿既定beat；双臂完整真实刚体+12/-12度向中位返回，手镯/手指不拆。旧068双裤仅材质，整腰臀→双腿→裤口与旧新空域全白，由原生重新画完整体积，不沿旧切边。隐藏髋继承已过062proxy及beat，不回791/744腰口，不把投影当实骨长。\n\n同框520x780，无新缩放。远鞋作底层保全，输出后按真实新裤重新算可见保护；不以空alpha或隐藏后层硬锁前景。近抬鞋作为完整前景原鞋材料保持。色彩锚为锁057/062，通过真实062源及原navy均值，不能从068逐态再漂。仅准备073，未做079/全11表。\n')
print(json.dumps({'preposition_sha256':sha(R/'reference/F073_actual_source_preposition_NOT_ART.png'),'mask_sha256':sha(R/'masks/F073_complete_trousers_sleeves_WHITE_EDIT_PENDING.png'),'white_pixels':int(edit.sum()),'feet':soles,'body_delta_world':body_delta_world.tolist()},ensure_ascii=False))
