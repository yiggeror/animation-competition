#!/usr/bin/env python3
"""Single F084 actual-source rigid preflight and full trousers white domain; never generates art."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation,label
import numpy as np,json,math,hashlib
R=Path(__file__).resolve().parent;S=R/'sources';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not (R/'requests/execution_state.json').exists(),'Frozen input cannot be rebuilt after execution.'
for d in ['reference','layers','masks','geometry','qa','requests']:(R/d).mkdir(exist_ok=True)
for v in json.loads((S/'snapshot_manifest.json').read_text())['files']:assert sha(S/v['path'])==v['sha256']
assert sha(S/'F079_corrected_LOCKED.png')=='856d10c9516c33a8e992a121033e76a5ac55bda269b16949a90aa431206f0364'
mi=Image.open(S/'F079_corrected_LOCKED.png').convert('RGBA');ma=np.array(mi);size=mi.size;yy,xx=np.indices(ma.shape[:2])
meta=json.loads((S/'F062_calibrated_preparation_metadata.json').read_text());g79=json.loads((S/'F079_approved_input_metadata_PROXY_ONLY.json').read_text());reg=meta['registration'];s=reg['s'];off=np.array([reg['tx'],reg['ty']])
events={v['frame']:v for v in json.loads((S/'legacy_events_079_084_ONLY.json').read_text())['states']};f79,f84=events[79],events[84]
body_world=np.array(f84['head_center'])-np.array(f79['head_center']);body_delta=body_world/s
far_world=np.array(f84['far_ankle'])-np.array(f79['far_ankle']);far_delta=far_world/s
assert np.allclose(body_world,[27.679485758239025,-5.249506568476249]);assert np.allclose(far_world,[84.,-23.]);assert f84['planted_feet']==['near'] and f84['hold_frames']==6
src={k:Image.open(S/f'F079_source_F079_{k}.png').convert('RGBA')for k in ['far_shoe_ankle_SUPPORT_FIXED','far_complete_arm_jade_hand','body_head_blouse','near_complete_arm','near_shoe_ankle_LANDED']}
pants=Image.open(S/'F079_native_complete_trousers_original_color_TRIAL.png').convert('RGBA')
replay=Image.new('RGBA',size)
for z in [src['far_shoe_ankle_SUPPORT_FIXED'],pants,src['far_complete_arm_jade_hand'],src['body_head_blouse'],src['near_complete_arm'],src['near_shoe_ankle_LANDED']]:replay.alpha_composite(z)
replay_diff=int(np.any(np.array(replay)!=ma,axis=2).sum());assert replay_diff==0
replay.save(R/'qa/F079_corrected_six_source_layers_REPLAY.png')
def rot(deg):
 t=math.radians(deg);return np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]])
def rigid(z,m,t):
 assert np.allclose(m.T@m,np.eye(2),atol=1e-12)
 inv=m.T;v=-inv@t
 return z.transform(size,Image.Transform.AFFINE,(*inv[0],v[0],*inv[1],v[1]),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
def capsule(points,r):
 ps=[tuple(map(float,p))for p in points];z=Image.new('L',size);d=ImageDraw.Draw(z);d.line(ps,fill=255,width=2*r+1)
 for x,y in ps:d.ellipse((x-r,y-r,x+r,y+r),fill=255)
 return np.array(z)>0
body=rigid(src['body_head_blouse'],np.eye(2),body_delta);nearfoot=src['near_shoe_ankle_LANDED'].copy();farfoot=rigid(src['far_shoe_ankle_SUPPORT_FIXED'],np.eye(2),far_delta)
roots79={k:np.array(v)for k,v in g79['actual_sleeve_roots_native'].items()};roots84={k:v+body_delta for k,v in roots79.items()};arms={};affines={}
for side,name,deg in [('near','near_complete_arm',-8.),('far','far_complete_arm_jade_hand',8.)]:
 m=rot(deg);t=roots79[side]+body_delta-m@roots79[side];arms[side]=rigid(src[name],m,t);affines[side]={'rotation_degrees_from_actual_corrected079':deg,'matrix':m.tolist(),'translation_native':t.tolist(),'scale':1,'AA_resampling':'one whole-layer BICUBIC rigid affine; fingers/jade never split or separately warped'}
oldpants=rigid(pants,np.eye(2),body_delta)
layers={'far_shoe_ankle_SWING':farfoot,'old079_corrected_trousers_OBSOLETE_POSE_MATERIAL':oldpants,'far_complete_arm_jade_hand':arms['far'],'body_head_blouse':body,'near_complete_arm':arms['near'],'near_shoe_ankle_SUPPORT_FIXED':nearfoot}
pre=Image.new('RGBA',size)
for k,z in layers.items():pre.alpha_composite(z);z.save(R/'layers'/f'F084_{k}.png')
out=np.array(pre);alpha={k:np.array(z)[:,:,3]for k,z in layers.items()};order=list(layers)
def visible(k):
 front=np.zeros(ma.shape[:2],bool)
 for q in order[order.index(k)+1:]:front|=alpha[q]>0
 return(alpha[k]>0)&~front
# Source calibrated hidden H follows actual body beat. It is a soft image-space
# guide, not the visible blouse hem and not a claim of anatomical bone length.
H=np.array(g79['hidden_near_hip_proxy_native'])+body_delta;farH=np.array(g79['hidden_far_hip_shape_proxy_native'])+body_delta
nearA=np.array(g79['actual_near_ankle_proxy_native']);farA=np.array(g79['actual_far_ankle_proxy_native'])+far_delta
# Passing far knee retains the approved062 passing guide direction only.
# Neither transformed old079 knees nor failed079/old073 artwork are pose targets.
def knee_guide(chain,h,a):
 sh,sk,sa=np.array(chain);d=sa-sh;frac=float(np.dot(sk-sh,d)/np.dot(d,d));normal=np.array([d[1],-d[0]])/np.linalg.norm(d);bend=float(np.dot(sk-(sh+frac*d),normal));nd=a-h;nn=np.array([nd[1],-nd[0]])/np.linalg.norm(nd)
 bend_guide=float(np.clip(bend,-125,125));return h+frac*nd+bend_guide*nn,{'source_fraction':frac,'source_signed_projection_bend_native':bend,'soft_corridor_bend_native':bend_guide,'not_hard_bones':True}
nearK,nk=knee_guide(meta['near062_chain_native'],H,nearA);farK,fk=knee_guide(meta['far062_shape_proxy_native'],farH,farA)
sleeves=np.zeros(ma.shape[:2],bool)
for root in roots84.values():sleeves|=capsule([root+[-20,-4],root+[20,14]],15)
bodyguard=(alpha['body_head_blouse']>0)&~sleeves
armguard=(visible('near_complete_arm')|visible('far_complete_arm_jade_hand'))&~sleeves
near_guard=visible('near_shoe_ankle_SUPPORT_FIXED')
# The far foot remains a complete source layer behind the new pants. Its hidden
# alpha does not hard-lock foreground pixels. The upper cuff approach remains
# redrawable where not true visible skin/sole/shoe material.
far_guard=visible('far_shoe_ankle_SWING')
far_cuff=capsule([farA+[-43,-37],farA+[40,-15]],16)
far_rgba=np.array(farfoot);fr=far_rgba[:,:,:3].astype(int)
far_skin=(fr[:,:,0]>130)&(fr[:,:,0]-fr[:,:,1]>16)&(fr[:,:,1]-fr[:,:,2]>10)&(far_rgba[:,:,3]>0)
# Only the approach above the genuine ankle may be covered by new native pants;
# true warm skin, shoe and sole are retained as actual visible material.
far_cuff_release=far_cuff&~binary_dilation(far_skin,iterations=2)&(yy<farA[1]-9)
far_guard&=~far_cuff_release
# The NEW near shin crosses part of the raised BACK shoe that the obsolete
# translated079 leg does not yet hide. Release this explicit foreground corridor,
# retaining the complete shoe layer beneath it; never edit/move actual sourcefoot.
future_near_shin_occlusion=capsule([nearK,nearA+[0,-12]],48)&(yy<nearA[1]+3)
far_foot_future_hidden=far_guard&future_near_shin_occlusion
far_guard&=~future_near_shin_occlusion
hard=bodyguard|armguard|near_guard|far_guard
oldmat=alpha['old079_corrected_trousers_OBSOLETE_POSE_MATERIAL']>0
semantic=binary_dilation(oldmat,iterations=10)|capsule([H,nearK,nearA],65)|capsule([farH,farK,farA],70)|capsule([H+[-90,-68],H+[55,-68]],50)|sleeves|far_cuff
crop=(1000,280,1520,1060);inside=(xx>=crop[0])&(xx<crop[2])&(yy>=crop[1])&(yy<crop[3]);edit=semantic&~hard
clipped=int((edit&~inside&(out[:,:,3]>20)).sum());assert clipped==0,'Editable actual material outside proposed crop'
edit&=inside
for name,m in [('F084_complete_waist_both_trousers_WHITE_EDIT_PENDING',edit),('HARD_actual_head_blouse_except_sleeves',bodyguard),('HARD_visible_complete_arms_except_sleeves',armguard),('HARD_near_support_shoe_actual_material',near_guard),('HARD_far_swing_shoe_visible_material',far_guard),('full_far_swing_foot_LAYER_NOT_HIDDEN_GUARD',alpha['far_shoe_ankle_SWING']>0),('far_proximal_cuff_approach_RELEASE',far_cuff_release),('far_shoe_under_future_near_shin_OCCLUSION_RELEASE_NOT_SOURCE_CHANGE',far_foot_future_hidden),('full_old_new_trousers_semantic_GUIDE',semantic)]:Image.fromarray(m.astype('uint8')*255).save(R/'masks'/f'{name}.png')
pre.save(R/'reference/F084_actual_source_preposition_NOT_ART.png');pre.crop(crop).save(R/'reference/F084_crop_RGBA_NOT_ART.png');Image.fromarray(edit.astype('uint8')*255).crop(crop).save(R/'masks/F084_crop_WHITE_EDIT_PENDING.png')
# A separate physical guard diagnostic: full rear layer is shown for provenance,
# while actual visible guard excludes all foreground material and alpha0.
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17)
def bg(z,col):
 q=Image.new('RGBA',size,col);q.alpha_composite(z);return q
for tag,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 q=bg(pre,col);q.convert('RGB').save(R/f'qa/F084_full_{tag}_NOT_ART.png');q.crop(crop).convert('RGB').save(R/f'qa/F084_crop_{tag}_NOT_ART.png')
 wash=Image.new('RGBA',size,(219,36,121,0));wash.putalpha(Image.fromarray(edit.astype('uint8')*110));ov=q.copy();ov.alpha_composite(wash);ov.crop(crop).convert('RGB').save(R/f'qa/F084_complete_white_domain_overlay_{tag}.png')
 sheet=Image.new('RGB',(1590,830),(236,241,246));d=ImageDraw.Draw(sheet)
 for j,(title,z)in enumerate([('锁修正079母／856d10／同框源',bg(mi,col)),('084真实层刚体预摆／旧裤不是姿态',q),('084腰臀双整裤白域／仅输入门',ov)]):
  sheet.paste(z.crop(crop).convert('RGB'),(j*530,40));d.text((j*530+4,7),title,font=font,fill='#24343f')
 sheet.save(R/f'qa/F079_F084_actual_preposition_and_mask_{tag}.png')
 # Sleeve/waist/cuff connections are deliberately visible as technical cuts,
 # not hidden by drawn bridges; new whole trousers are native-edit territory.
 sheet=Image.new('RGB',(1240,760),(236,241,246));d=ImageDraw.Draw(sheet)
 regions=[('近裸腕完整臂／袖根接域',(1135,320,1310,640)),('远玉镯完整臂／袖根接域',(1335,320,1495,640)),('近鞋逐RGBA原位／1022底',(1170,890,1410,1045)),('远鞋整层前移抬步／后层可遮',(1170,830,1410,985))]
 for j,(title,box)in enumerate(regions):
  panel=q.crop(box);panel.thumbnail((570,315));x=(j%2)*620;y=(j//2)*380+35;sheet.paste(panel.convert('RGB'),(x,y));d.text((x+4,y-28),title,font=font,fill='#24343f')
 sheet.save(R/f'qa/F084_actual_sleeves_and_feet_{tag}.png')
 guard_sheet=Image.new('RGB',(1040,780),(236,241,246));guard_sheet.paste(q.crop(crop).convert('RGB'),(0,0));guard_sheet.paste(Image.fromarray(edit.astype('uint8')*255).crop(crop).convert('RGB'),(520,0));guard_sheet.save(R/f'qa/F084_actual_crop_and_WHITE_MASK_{tag}.png')
guide=bg(pre,(213,223,231,255)).convert('RGB');d=ImageDraw.Draw(guide);d.line((1040,1022,1500,1022),fill='#228c97',width=2);d.line((1150,959,1470,959),fill='#ba8b35',width=2)
for side,h,k,a,c in [('near RIGHT support',H,nearK,nearA,'#0788b7'),('far LEFT swing',farH,farK,farA,'#bc7924')]:
 d.line([tuple(h),tuple(k),tuple(a)],fill=c,width=3)
 for p,txt in [(h,'hidden proxy'),(k,'K corridor'),(a,'real ankle proxy')]:
  x,y=p;d.ellipse((x-6,y-6,x+6,y+6),outline=c,width=2);d.text((x+8,y-7),txt,fill=c)
d.text((50,30),'084近右固定支撑／远左抬步：实际像素预摆+投影guide，非画稿',font=font,fill='#24343f');d.text((50,58),'H/K仅软投影，不是实测骨长；旧079裤形整白重画，不当新姿态',font=font,fill='#b55936')
guide.save(R/'reference/F084_actual_feet_hidden_proxy_GUIDE_NOT_ART.png');guide.crop(crop).save(R/'qa/F084_proxy_and_support_crop_GUIDE_NOT_ART.png')
soles={}
for name,z in [('near_support',nearfoot),('far_swing',farfoot)]:
 ys,xs=np.where(np.array(z)[:,:,3]>=128);soles[name]={'native_alpha128_bottom':int(ys.max()),'world_alpha128_bottom':float(ys.max()*s+off[1]),'x_span_alpha128':[int(xs.min()),int(xs.max())]}
near_diff=int(np.any(np.array(nearfoot)!=np.array(src['near_shoe_ankle_LANDED']),axis=2).sum());assert near_diff==0;assert soles['near_support']['native_alpha128_bottom']==1022
# Ensure the hip, knee and cuff approach share one continuous writable trouser
# component rather than a set of thin disconnected repair rectangles.
lab,_=label(edit);probes={}
for name,p in [('near_hiddenH',H),('near_Kcorridor',nearK),('near_above_ankle',nearA+[0,-25]),('far_hiddenH',farH),('far_Kcorridor',farK),('far_above_ankle',farA+[0,-25])]:
 x,y=np.rint(p).astype(int);probes[name]={'native_xy':[int(x),int(y)],'white':bool(edit[y,x]),'component':int(lab[y,x])}
checks={'status':'F084_SINGLE_SOURCE_PREFLIGHT_PENDING_ROOT_ACTUAL_INPUT_GATE_NO_CALL','mother079_SHA':sha(S/'F079_corrected_LOCKED.png'),'source_layer_replay_RGBA_changed_pixels':replay_diff,'mother_layer_order':['farshoe','native_complete_corrected079_trousers','fararm','body','neararm','nearshoe'],'frame':84,'hold':6,'inclusive_frames':[84,89],'latest_frame_clarification':'Astra confirms original chain084→090; no089 state and no090 prepared here.','support':'near RIGHT whole forward original shoe fixed; far LEFT complete shoe lifted passing forward','registration':reg,'body_head_delta_world':body_world.tolist(),'body_head_delta_native':body_delta.tolist(),'far_whole_shoe_delta_world':far_world.tolist(),'far_whole_shoe_delta_native':far_delta.tolist(),'far_shoe_transform':'scale1 rot0 translation; one complete source layer BICUBIC AA resampling, no ankle/shoe split or separately forced bottom','near_whole_support_shoe_RGBA_changed_pixels':near_diff,'near_whole_support_shoe_saved_byte_identical':sha(R/'layers/F084_near_shoe_ankle_SUPPORT_FIXED.png')==sha(S/'F079_source_F079_near_shoe_ankle_LANDED.png'),'actual_feet':soles,'actual_sleeve_roots_native':{k:v.tolist()for k,v in roots84.items()},'whole_arm_rigid_transforms':affines,'hidden_near_hip_proxy_native':H.tolist(),'hidden_far_hip_proxy_native':farH.tolist(),'actual_near_ankle_proxy_native':nearA.tolist(),'actual_far_ankle_proxy_native':farA.tolist(),'near_knee_soft_corridor_native':nearK.tolist(),'far_knee_soft_corridor_native':farK.tolist(),'soft_knee_direction_derivation':{'near':nk,'far':fk},'proxy_limit':'Approved corrected079 hidden proxy follows actual source body beat only; calibrated062 projection direction/fraction guides knee broad corridor. Not observed bones, hard lengths, or reachability proof. New organic volume/hip settle judged from actual output.','crop_xyxy':crop,'crop_size':[520,780],'white_pixels':int(edit.sum()),'clipped_editable_alpha20_actual_material':clipped,'guard_intersections':{k:int((edit&z).sum())for k,z in [('head_blouse',bodyguard),('complete_visible_arms',armguard),('near_actual_support_shoe',near_guard),('far_actual_visible_swing_shoe',far_guard)]},'future_near_shin_may_occlude_back_shoe_material_pixels':int(far_foot_future_hidden.sum()),'whole_far_shoe_layer_retained_unmodified_after_rigid_placement':True,'hard_guard_alpha0_pixels':int((hard&(out[:,:,3]==0)).sum()),'old_visible_corrected079_pants_uneditable_except_genuine_foreground':int((oldmat&~edit&~hard).sum()),'connected_trousers_probes':probes,'palette':'locked057/062 originals, source palette preserved; no accumulated079 recolor','new_generation_calls':0,'F090_unopened':True,'source_refs':'Corrected locked079 complete shallow-flex waist/legs and locked057 real volume. Failed079/old073 pose artwork excluded.'}
assert not any(checks['guard_intersections'].values());assert checks['hard_guard_alpha0_pixels']==0;assert checks['old_visible_corrected079_pants_uneditable_except_genuine_foreground']==0
(R/'geometry/preparation_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
prompt='''Only F084 single-state input gate, PREPARED NOT CALLED. Edit WHITE image2 on image1, same520x780 transparent crop. Image3 is Astra-LOCKED CORRECTED F079 complete-volume mother856d10, never the failed old079. Image4 is real locked F057 volume/identity reference; image5 locked062 is palette only, not a pose to copy. Return exactly same520x780 transparent framing and scale; do not mirror, zoom, reframe, add background or relight.

The grandmother walks toward screen RIGHT. F084 is near anatomical RIGHT SINGLE SUPPORT while far anatomical LEFT passes forward with its whole original shoe lifted. The near right shoe on imageRIGHT/FRONT stays exactly on its original support position and true sole baseline1022. Do not slide, rotate, resize, redesign or repaint that entire original support shoe/ankle. The far LEFT actual whole shoe is already moved +84worldX and -23worldY from079, with its true original geometry, and is at approximately63.1688native pixels above the support baseline. Keep its actual placed complete shoe and real exposed skin wherever VISIBLE; no new generated shoe, duplicated heel/toe/sole, or another shifted foot. The explicit WHITE near-shin crossing over the BACK far shoe is permitted to become foreground navy pants: the COMPLETE original far shoe remains intact underneath as a separate source layer. Do not retain an exposed shoe-shaped black island through the new front shin. The full rear shoe layer may be naturally occluded proximally by the new foreground trousers; never force an invisible rear-layer alpha box to cut through a new front leg.

REDRAW THE COMPLETE WHITE WAIST/PELVIS/CROTCH AND BOTH WHOLE TROUSER LEGS as one continuous full human volume connecting to the TWO ACTUAL ORIGINAL ankle/shoe targets. Near RIGHT thigh/knee/calf sustain body weight above the fixed lower/front shoe with natural soft knee and stable pelvis; far LEFT thigh rises into passing step, knee naturally flexed and calf connects down/back to the already lifted actual left shoe. The visible old079 corrected pants in white are material/volume context ONLY, not084 leg silhouettes or cuff cuts to preserve. Do not copy old leg extraction wedges, thin bridges, diagonal scraps, strips or empty seams. Keep true accepted057/079 complete thigh/knee/back-plane/calf volume and original flat navy/shadow/ink character. A hidden hip is an internal body joint, never the visible blouse hem; projected H/K corridor guides are soft directions, not hard measured bones. Natural organic hip settling is allowed within the full white pants domain; no code-like stick joints or stretched pants tubes. Draw complete smooth silhouettes and coherent knee rear planes. Clean all obsolete old079 pants contours/vacated pixels and join continuously under the real blouse hem and into the actual source ankles, without transparent waist band or copied blue blouse patches.

Original head/blouse and both complete actual arms already follow the beat. Near RIGHT bare wrist and far LEFT jade bangle remain on their correct complete arms; near arm moves a little forward and far arm slightly back toward neutral as whole rigid source chains. Preserve every BLACK actual skin/hand/jade/source material; do not redraw fingers or shift wrist ownership. Only small WHITE sleeve-root seam gaps may be connected naturally to the already positioned intact arm. No new displaced hand/second cuff curve/extra arm. Keep all actual shoes, skin, blouse, white flowers, gray hair, glasses and palette. Use locked057/062 navy palette without cumulative brightening. No glow, text, guides, props or drawing of any following state. This is084 only; do not do090.'''
(R/'requests/prompt_PREPARED_NOT_CALLED.txt').write_text(prompt+'\n')
args={'prompt':prompt,'referenced_image_paths':[str(R/'reference/F084_crop_RGBA_NOT_ART.png'),str(R/'masks/F084_crop_WHITE_EDIT_PENDING.png'),str(S/'F079_corrected_LOCKED.png'),str(S/'F057_locked_actual_volume_reference.png'),str(S/'F062_locked_palette_anchor.png')],'transparent_background':True}
(R/'requests/arguments_PREPARED_NOT_CALLED.json').write_text(json.dumps(args,ensure_ascii=False,indent=2)+'\n')
(R/'requests/input_sources_PENDING_ROOT_REVIEW.json').write_text(json.dumps({'status':'PREPARED_NOT_CALLED_PENDING_ROOT_AND_ASTRA_INPUT_REVIEW','input_files':[{'path':str(Path(p).relative_to(R)),'sha256':sha(p)}for p in args['referenced_image_paths']],'snapshot_manifest_sha256':sha(S/'snapshot_manifest.json'),'new_calls':0},ensure_ascii=False,indent=2)+'\n')
(R/'README.md').write_text('''# F084 单态真实源预摆与完整腿体积白域

仅输入快审，未生图/提交；不准备090。Astra已确认原表链079→084→090，084–089 hold6无新增089态。

唯一母是已最终双审修正079 `856d10c9…f0364`，六生产层和最终PNG原字节快照，逐RGBA重放0。无失败079/旧073图像提示；锁057真实体量和锁062母色另附。

79→84只取旧表两态事件delta：头衣+27.679485758239/−5.24950656847625world；近右前鞋原位整层逐RGBA保持1022实底、继续承重；远左整鞋+84/−23world（+230.7035573123/−63.1688311688native）抬步。移动层scale1/rot0，含一次整层AA重采样，未强制回整数63；近支撑鞋不重采样。双真整臂绕实际079袖根+bodydelta小反相−8/+8°，手指/玉镯不拆，scale1，仅待审输入提案。

旧079裤仅真实体量/材质预摆，不是新姿态画稿。整个腰臀、旧新两完整腿、膝后体积与裤口连接全白真绘，不做窄缝桥。H随真实锁079源beat，仅隐藏投影代理；K走廊源自062已校准投影方向而非硬骨长。所有guide另图标注非成态，不以code画人。

建议实际crop1000,280,1520,1060=520×780。完整上身、两条实际可见臂（除小袖根接域）、原支撑足/抬足真实可见材料硬保，后鞋完整层保全；隐藏后层alpha不冻结前景。原衣AA不应另做alpha0护栏。实际输出后仍须审整体体量/承重和所有连接，不凭source重放或proxy数值直接通过。

先看qa/F079_F084_actual_preposition_and_mask_gray.png和dark.png，及qa/F084_actual_crop_and_WHITE_MASK_gray.png、qa/F084_actual_sleeves_and_feet_dark.png。requests仅PREPARED_NOT_CALLED；新图/曝光0。
''',encoding='utf8')
print(json.dumps({'preposition_SHA':sha(R/'reference/F084_actual_source_preposition_NOT_ART.png'),'fullmask_SHA':sha(R/'masks/F084_complete_waist_both_trousers_WHITE_EDIT_PENDING.png'),'cropmask_SHA':sha(R/'masks/F084_crop_WHITE_EDIT_PENDING.png'),'white_pixels':int(edit.sum()),'feet':soles,'probes':probes,'body_delta_world':body_world.tolist()},ensure_ascii=False,indent=2))
