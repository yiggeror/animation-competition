#!/usr/bin/env python3
"""Only079 actual source preposition and complete trousers input, no calls."""
from pathlib import Path
import json,math,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation,distance_transform_edt
R=Path(__file__).resolve().parent;S=R/'sources';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not (R/'requests/execution_state.json').exists()
for d in ['reference','layers','masks','geometry','qa','requests']:(R/d).mkdir(exist_ok=True)
for v in json.loads((S/'snapshot_manifest.json').read_text())['files']:assert sha(S/v['path'])==v['sha256']
assert sha(S/'F073_final.png')=='afc7dcff6593611d0e33b16a7fce9e12967bf1767cacf8336308a51a50af1929'
mi=Image.open(S/'F073_final.png').convert('RGBA');ma=np.array(mi);size=mi.size;yy,xx=np.indices(ma.shape[:2]);g73=json.loads((S/'F073_preparation_checks.json').read_text());meta=json.loads((S/'F062_calibrated_preparation_metadata.json').read_text());reg=meta['registration'];s=reg['s'];off=np.array([reg['tx'],reg['ty']])
legacy={v['frame']:v for v in json.loads((S/'legacy_event_intents.json').read_text())['states']};f73,f79=legacy[73],legacy[79]
body_delta_world=np.array(f79['head_center'])-np.array(f73['head_center']);body_delta=body_delta_world/s
assert np.allclose(body_delta_world,[50.320514241761,5.24950656847625]) and f79['hold_frames']==5 and f79['planted_feet']==['near','far']
names=['far_shoe_ankle_SUPPORT_FIXED','far_complete_arm_jade_hand','body_head_blouse','near_complete_arm','near_shoe_ankle_SWING'];src={k:Image.open(S/f'F073_{k}.png').convert('RGBA')for k in names};pants=Image.open(S/'F073_native_trousers_color_locked.png').convert('RGBA')
replay=Image.new('RGBA',size)
for z in [src[names[0]],pants,src[names[1]],src[names[2]],src[names[3]],src[names[4]]]:replay.alpha_composite(z)
assert np.array_equal(np.array(replay),ma),'The six final production layers must replay locked073 byte-for-byte RGBA.'
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
body=rigid(src['body_head_blouse'],np.eye(2),body_delta);farfoot=src['far_shoe_ankle_SUPPORT_FIXED'].copy()
# The new backswing reveals old extraction ink below the left blouse hem.
# Remove only that verified external noncloth debris in this derived layer;
# retain every actual blue/white material and its complete 2px ink/AA boundary.
before_body=np.array(body);br=before_body[:,:,:3].astype(int)
actual_blue=(br[:,:,2]>br[:,:,0]+15)&(br[:,:,1]>br[:,:,0]+8)&(before_body[:,:,3]>=160)
actual_white=(br.min(axis=2)>180)&(np.ptp(br,axis=2)<35)&(before_body[:,:,3]>=160)
color_distance=distance_transform_edt(~(actual_blue|actual_white))
old_ink_roi=(xx>=1120)&(xx<=1150)&(yy>=535)&(yy<=585)
body_debris=old_ink_roi&(before_body[:,:,3]>0)&(color_distance>2.3)
clean_body=before_body.copy();clean_body[body_debris]=0;body=Image.fromarray(clean_body)
Image.fromarray(body_debris.astype('uint8')*255).save(R/'masks/derived_body_external_old_ink_cleanup.png')
(R/'geometry/derived_body_old_ink_cleanup.json').write_text(json.dumps({'operation':'remove verified former arm extraction ink/low-AA outside actual blouse material in derived079 only; no new RGB','locked073_or_snapshots_modified':False,'complete_arm_layers_modified':False,'actual_blue_white_plus2px_boundary_retained':True,'distance_threshold_native':2.3,'removed_pixels':int(body_debris.sum()),'mapping':[{'derived_xy':[int(x),int(y)],'before_RGBA':before_body[y,x].tolist(),'source073_inverse_fractional_sample_xy':(np.array([x,y])-body_delta).tolist()}for y,x in zip(*np.where(body_debris))]},ensure_ascii=False,indent=2)+'\n')
near_delta=np.array([(f79['near_ankle'][0]-f73['near_ankle'][0])/s,63.]);assert np.isclose(near_delta[0]*s,67.)
nearfoot=rigid(src['near_shoe_ankle_SWING'],np.eye(2),near_delta)
roots73={k:np.array(v)for k,v in g73['sleeve_roots_native'].items()};roots79={k:v+body_delta for k,v in roots73.items()};arms={};arm_affines={}
for side,name,deg in [('near','near_complete_arm',12.),('far','far_complete_arm_jade_hand',-12.)]:
 m=rot(deg);t=roots73[side]+body_delta-m@roots73[side];arms[side]=rigid(src[name],m,t);arm_affines[side]={'rotation_degrees_from_actual073':deg,'matrix':m.tolist(),'translation_native':t.tolist(),'scale':1}
oldpants=rigid(pants,np.eye(2),body_delta)
layers={'far_shoe_ankle_SUPPORT_FIXED':farfoot,'old073_trousers_OBSOLETE_MATERIAL':oldpants,'far_complete_arm_jade_hand':arms['far'],'body_head_blouse':body,'near_complete_arm':arms['near'],'near_shoe_ankle_LANDED':nearfoot};order=list(layers);pre=Image.new('RGBA',size)
for n,z in layers.items():pre.alpha_composite(z);z.save(R/'layers'/f'F079_{n}.png')
out=np.array(pre);alpha={n:np.array(z)[:,:,3]for n,z in layers.items()}
def visible(n):
 front=np.zeros(ma.shape[:2],bool)
 for q in order[order.index(n)+1:]:front|=alpha[q]>0
 return (alpha[n]>0)&~front
H=np.array(g73['hidden_hip_proxy_native'])+body_delta
sideoffset=np.array(meta['far062_shape_proxy_native'][0])-np.array(meta['near062_chain_native'][0]);farH=H+sideoffset
nearA=np.array(meta['near062_chain_native'][-1])+np.array(g73['near_complete_shoe_translation_native'])+near_delta
# Source073 far foot is the same landed source068 foot, at this calibrated
# actual manual ankle proxy. No758 or old absolute construction joints.
farA=np.array(meta['far062_shape_proxy_native'][-1])+np.array([66/s,63.])
def guided_knee(source_chain,h,a):
 sh,sk,sa=np.array(source_chain);d=sa-sh;t=float(np.dot(sk-sh,d)/np.dot(d,d));normal=np.array([d[1],-d[0]])/np.linalg.norm(d);bend=float(np.dot(sk-(sh+t*d),normal));nd=a-h;nn=np.array([nd[1],-nd[0]])/np.linalg.norm(nd)
 # Preserve only calibrated projected bend direction/rough breadth, never
 # exact bones or reachability. Native organic anatomy may leave this guide.
 return h+t*nd+np.clip(bend,-35,35)*nn,{'source_fraction':t,'signed_source_perp_offset_native':bend,'clamped_corridor_offset_native':float(np.clip(bend,-35,35))}
nearK,noteN=guided_knee(meta['near062_chain_native'],H,nearA);farK,noteF=guided_knee(meta['far_source_shape_proxy_native'],farH,farA)
sleeves=np.zeros(ma.shape[:2],bool)
for q in roots79.values():sleeves|=capsule([q+[-20,-3],q+[20,14]],15)
bodyguard=(alpha['body_head_blouse']>0)&~sleeves;armguard=(visible('near_complete_arm')|visible('far_complete_arm_jade_hand'))&~sleeves
near_guard=visible('near_shoe_ankle_LANDED');far_cuff=capsule([farA+[-42,-30],farA+[42,-10]],19);far_guard=visible('far_shoe_ankle_SUPPORT_FIXED')&~far_cuff
hard=bodyguard|armguard|near_guard|far_guard;oldmat=alpha['old073_trousers_OBSOLETE_MATERIAL']>0
semantic=binary_dilation(oldmat,iterations=9)|capsule([H,nearK,nearA],65)|capsule([farH,farK,farA],65)|capsule([H+[-90,-67],H+[50,-67]],49)|sleeves|far_cuff|body_debris
edit=semantic&~hard;crop=(900,280,1420,1060);inside=(xx>=900)&(xx<1420)&(yy>=280)&(yy<1060)
clipped=int((edit&~inside&(out[:,:,3]>20)).sum());assert clipped==0,'All actual editable material must fit crop.'
edit&=inside
for n,z in [('F079_complete_trousers_sleeves_WHITE_EDIT_PENDING',edit),('HARD_actual_head_blouse_except_sleeves',bodyguard),('HARD_visible_complete_arms_except_sleeves',armguard),('HARD_near_landed_shoe_actual_material',near_guard),('HARD_far_support_shoe_visible_material',far_guard),('full_far_support_foot_LAYER_not_hidden_guard',alpha['far_shoe_ankle_SUPPORT_FIXED']>0),('far_cuff_new_occlusion_RELEASE',far_cuff),('complete_old_new_pants_semantic_GUIDE',semantic)]:Image.fromarray(z.astype('uint8')*255).save(R/'masks'/f'{n}.png')
pre.save(R/'reference/F079_actual_source_preposition_NOT_ART.png');pre.crop(crop).save(R/'reference/F079_crop_RGBA_NOT_ART.png');Image.fromarray(edit.astype('uint8')*255).crop(crop).save(R/'masks/F079_crop_WHITE_EDIT_PENDING.png')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17)
def bg(z,col):
 q=Image.new('RGBA',size,col);q.alpha_composite(z);return q
for tag,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 q=bg(pre,col);q.convert('RGB').save(R/f'qa/F079_full_{tag}.png');wash=Image.new('RGBA',size,(219,36,121,0));wash.putalpha(Image.fromarray(edit.astype('uint8')*105));ov=q.copy();ov.alpha_composite(wash);ov.crop(crop).convert('RGB').save(R/f'qa/F079_crop_complete_edit_{tag}.png')
 sheet=Image.new('RGB',(1590,830),(236,241,245));d=ImageDraw.Draw(sheet)
 for j,(title,z)in enumerate([('真实锁073母态／afc7',bg(mi,col)),('079真实两足／旧裤材质非画稿',q),('079整裤白域／待输入审',ov)]):sheet.paste(z.crop(crop).convert('RGB'),(j*530,40));d.text((j*530+4,8),title,font=font,fill='#24343f')
 sheet.save(R/f'qa/F073_F079_actual_preposition_and_mask_{tag}.png')
guide=bg(pre,(213,223,231,255)).convert('RGB');d=ImageDraw.Draw(guide);d.line((940,1022,1400,1022),fill='#33858e',width=2)
for side,h,k,a,col in [('near RIGHT',H,nearK,nearA,'#0087b5'),('far LEFT',farH,farK,farA,'#c37926')]:
 d.line([tuple(h),tuple(k),tuple(a)],fill=col,width=3)
 for p,lab in [(h,'hidden H proxy'),(k,'K corridor ONLY'),(a,'actual ankle proxy')]:
  x,y=p;d.ellipse((x-7,y-7,x+7,y+7),outline=col,width=3);d.text((x+9,y-8),side+' '+lab,fill=col)
d.text((35,25),'079近右落地／远左继续支撑，双支撑转近右承重｜输入预摆非画稿',font=font,fill='#24343f')
d.text((35,52),'关节线仅校准source投影走廊；非硬实骨长／不据此判可达或自然度',font=font,fill='#9d5543')
guide.save(R/'qa/F079_actual_support_hidden_hip_and_knee_corridors.png');guide.crop(crop).save(R/'reference/actual_foot_targets_and_proxy_corridors_GUIDE_NOT_ART.png')
feet=Image.new('RGB',(1120,400),(219,226,233));d=ImageDraw.Draw(feet)
for j,(title,z)in enumerate([('远左原鞋／1022底整层固定',farfoot),('近右原整鞋／前移下63后落地',nearfoot),('两真鞋同底／新裤待重画',pre)]):
 q=bg(z,(213,223,231,255)).crop((950,860,1400,1045)).resize((360,148));feet.paste(q.convert('RGB'),(j*370,45));d.text((j*370+2,8),title,font=font,fill='#24343f')
feet.save(R/'qa/actual_support_and_landed_shoes.png')
soles={}
for name,z in [('far_support',farfoot),('near_landed',nearfoot)]:
 ys,xs=np.where(np.array(z)[:,:,3]>=128);soles[name]={'native_bottom':int(ys.max()),'world_bottom':float(ys.max()*s+off[1]),'x_span_alpha128':[int(xs.min()),int(xs.max())]}
assert soles['near_landed']['native_bottom']==soles['far_support']['native_bottom']==1022
assert np.array_equal(np.array(farfoot),np.array(src['far_shoe_ankle_SUPPORT_FIXED']))
checks={'status':'F079_SINGLE_ACTUAL_INPUT_PREPARED_NOT_GENERATED_PENDING_ROOT_REVIEW','mother073_SHA':sha(S/'F073_final.png'),'source_layer_replay_RGBA_changes':int(np.any(np.array(replay)!=ma,axis=2).sum()),'frame':79,'hold_frames':5,'inclusive_frames':[79,83],'support':'far LEFT remains planted; near RIGHT lands; double support to near RIGHT load','registration':reg,'body_head_delta_world':body_delta_world.tolist(),'body_head_delta_native':body_delta.tolist(),'near_whole_shoe_delta_native':near_delta.tolist(),'near_whole_shoe_delta_world':[67.,63*s],'far_whole_support_shoe_RGBA_changes':0,'actual_feet':soles,'actual_sleeve_roots_native':{k:v.tolist()for k,v in roots79.items()},'whole_arm_rigid_transforms':arm_affines,'hidden_near_hip_proxy_native':H.tolist(),'hidden_far_hip_shape_proxy_native':farH.tolist(),'actual_near_ankle_proxy_native':nearA.tolist(),'actual_far_ankle_proxy_native':farA.tolist(),'near_knee_corridor_native':nearK.tolist(),'far_knee_corridor_native':farK.tolist(),'knee_direction_derivation':{'near':noteN,'far':noteF},'proxy_limit':'062 calibrated manual source-proxy bend direction/fraction advanced between actual target endpoints only; not observed bones or hard lengths. Never substitute old791/744/758/623 or64/58. Native may settle hip and knee naturally; actual full art decides proportion/support.','crop_xyxy':crop,'crop_size':[520,780],'white_pixels':int(edit.sum()),'clipped_editable_actual_alpha20_material':clipped,'guard_intersections':{k:int((edit&z).sum())for k,z in [('body',bodyguard),('whole_visible_arms',armguard),('near_landed_foot',near_guard),('far_visible_support_foot',far_guard)]},'old_visible_pants_uneditable_except_genuine_foreground':int((oldmat&(out[:,:,3]>20)&~edit&~hard).sum()),'palette_anchor':'actual locked057/062; sources/F062_palette_anchor.png; no cumulative068/073 palette shift','new_calls':0,'F084_and_other_states_unopened':True,'limits':['Old073 trousers are obsolete material and must be completely redrawn, not retained as079 bend/cuff cuts.','Source sleeves/skin/hands and real feet protected as visible actual material; black full hidden far-foot layer alpha never cuts new foreground pants.','Soles are true alpha128 boundaries1022, not legacy ankle758 or construction ground.','Only input preparation; no imagegen, submit, eleven-state expansion or finished079 claim.']}
assert not any(checks['guard_intersections'].values())
(R/'geometry/preparation_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
prompt='''Edit only WHITE pixels in image2 on image1, the520x780 transparent F079 source-pixel input crop. Image3 is locked actual F073 for identity and real body/arm/foot proportions. Image4 is actual locked F062 PALETTE only, never a leg-pose template. Return exactly the same520x780 transparent crop framing; no scale, zoom, reframing, mirror, invented background or lighting.

F079 holds5frames: near anatomical RIGHT foot LANDS forward while the far anatomical LEFT shoe stays on exactly its previous support position. Double support changing load toward the near right leg. The grandmother faces RIGHT. Both genuine original shoes are ALREADY on the same actual sole baseline: far LEFT on imageLEFT/BACK is completely fixed; near RIGHT on imageRIGHT/FRONT was moved as one complete original shoe+ankle67world pixels forward and63native pixels down from073. Do not reposition, rotate, scale, redesign or redraw any original shoe, heel, toe, white sole or true exposed ankle outside WHITE. No third foot, second shoe edge, shifted shadow shoe or shoe fragment.

REDRAW THE COMPLETE WHITE TROUSERS as one coherent real waist/hip/crotch and BOTH full thighs/knees/calves/cuff openings connecting into the two actual fixed original shoes. The old bent073 pants visible in WHITE are OBSOLETE MATERIAL ONLY, not079 anatomy, contours or a small seam patch to retain. Near RIGHT leg extends naturally down/forward into the actual front/right landed ankle; far LEFT leg remains weight-bearing back to the unchanged lower left support shoe. Preserve accepted real limb volume and proportions with natural subtle hidden hip/knee settling; do not take the blue blouse hem as the hip, stretch straight strips, bridge cuffs with thin navy/skin strips, or follow artificial extraction cuts. Old hiddenhip/knee source proxies are soft projected directions, not hard anatomical lengths; draw organic clothing and human structure, not stick lines. Keep smooth complete silhouettes, natural knee rear planes, coherent dark crease/flat navy planes. Remove all obsolete old073 contours/fragments and fill the newly exposed cloth/transparent gaps. Continuous true navy under the original blouse hem and into the true ankles; no belt-like gray/transparent line or copied blue blouse patch.

Source head/blouse and both complete real arms already follow the approved beat; near bare-wrist RIGHT arm swings slightly back and far jade LEFT arm forward as whole real chains. Keep all BLACK material and finger/jade ownership. Only small WHITE sleeve-root gaps may be naturally joined; no moved hand, new cuff arc, source-line scraps or recolor. Far shoe is a BACK layer: native new foreground trousers may naturally cover its proximal ankle/cuff where WHITE permits while keeping the entire genuine shoe stationary. Do not use hidden far-foot alpha as a hole in the new leg. Match the locked057/062 palette, separate flat navy and deep folds, sharp original ink and real material AA; never cumulatively brighten from073. No generated shoe edging in the pants layer, glow, text, guides, mask colors or new props. Only F079; no other states.'''
(R/'requests/prompt_PREPARED_NOT_CALLED.txt').write_text(prompt+'\n')
args={'prompt':prompt,'referenced_image_paths':[str(R/'reference/F079_crop_RGBA_NOT_ART.png'),str(R/'masks/F079_crop_WHITE_EDIT_PENDING.png'),str(S/'F073_final.png'),str(S/'F062_palette_anchor.png')],'transparent_background':True}
(R/'requests/arguments_PREPARED_NOT_CALLED.json').write_text(json.dumps(args,ensure_ascii=False,indent=2)+'\n')
(R/'requests/input_freeze_PENDING_REVIEW.json').write_text(json.dumps({'status':'PREPARED_ONLY_NOT_EXECUTED','inputs':[{'path':p,'sha256':sha(p)}for p in args['referenced_image_paths']],'source_snapshot_manifest':'sources/snapshot_manifest.json','new_calls':0},ensure_ascii=False,indent=2)+'\n')
(R/'README.md').write_text('仅F079单态真实像素输入预备，未生图/提交。唯一母073 afc7dcff…，六生产层已快照，逐RGBA重放0差异。\n\n73→79仅取已批准事件delta：头衣+50.3205142/+5.2495066world；原近右整鞋+67worldX/+63nativeY落1022底；原远左整鞋逐RGBA原位1022底，双支撑转近右承重。真实整臂相对073+12/-12度绕实际袖根及bodydelta，scale1指/玉不拆。旧073裤形全白仅材质，不拼旧关节断片。\n\nH沿已过073隐藏proxy+beat；膝走廊由已校准source投影方向/分数在真实H/A之间推进，只作软走廊，不当实骨长/可达性证明，不回旧791/744/758/623或64/58。实际新裤应保持自然体积与真实承重。\n\n建议crop900,280,1420,1060为520x780；全部可编辑实体装入。身体/真实完整可见臂/鞋踝硬保，袖根少域可接；远鞋完整底层保全，输出按真实新裤重算可见保护，不用隐藏alpha盖前景。色锚锁057/062，不逐态漂移。所有必要源快照SHA齐；只交输入门，不11态或下一态。\n')
print(json.dumps({'preposition_SHA':sha(R/'reference/F079_actual_source_preposition_NOT_ART.png'),'mask_SHA':sha(R/'masks/F079_complete_trousers_sleeves_WHITE_EDIT_PENDING.png'),'white_pixels':int(edit.sum()),'feet':soles,'body_delta_world':body_delta_world.tolist(),'knees_soft':[nearK.tolist(),farK.tolist()]},ensure_ascii=False))
