#!/usr/bin/env python3
"""F090 single neutral four-input gate. Frozen real layers only, no old084 pants pose."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation,binary_fill_holes,minimum_filter,label
import numpy as np,json,math,hashlib,shutil
R=Path(__file__).resolve().parent;S=R/'sources';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not(R/'requests/execution_state.json').exists()
for d in ['layers','reference_native','inputs_1024x1536','masks','geometry','qa','requests']:(R/d).mkdir(exist_ok=True)
for v in json.loads((S/'snapshot_manifest.json').read_text())['files']:assert sha(S/v['path'])==v['sha256']
assert sha(S/'F084_LOCKED_mother_ARCHIVE_NOT_REQUEST.png')=='21acf20424d94477191dbc6fd012fe61426d509ec55dbc48037bb97b2c89f6ae'
mi=Image.open(S/'F084_LOCKED_mother_ARCHIVE_NOT_REQUEST.png').convert('RGBA');ma=np.array(mi);size=mi.size;yy,xx=np.indices(ma.shape[:2]);crop=(1080,250,1620,1060);offcrop=np.array(crop[:2]);native_size=(540,810)
g84=json.loads((S/'F084_frozen_body_anchors_PROXY_METADATA.json').read_text());reg=g84['registration'];scale=reg['s']
events={v['frame']:v for v in json.loads((S/'events_084_090_ONLY.json').read_text())['states']};f84,f90=events[84],events[90]
body_world=np.array(f90['head_center'])-np.array(f84['head_center']);body_delta=body_world/scale
assert np.allclose(body_world,[43.214526311359805,8.155270533216878]);assert f90['hold_frames']==5 and f90['last_frame_inclusive']==94
src={k:Image.open(S/f'F084_FROZEN_{k}.png').convert('RGBA')for k in ['body_head_blouse','near_complete_arm','far_complete_arm_jade_hand','near_shoe_ankle_SUPPORT_FIXED','far_shoe_ankle_SWING']}
# Archive084 trousers are read ONLY for byte-exact mother replay, never A/B/C/D.
archive_pants=Image.open(S/'F084_trousers_MOTHER_REPLAY_ONLY_NOT_REQUEST.png').convert('RGBA');replay=Image.new('RGBA',size)
for z in [src['far_shoe_ankle_SWING'],archive_pants,src['far_complete_arm_jade_hand'],src['body_head_blouse'],src['near_complete_arm'],src['near_shoe_ankle_SUPPORT_FIXED']]:replay.alpha_composite(z)
replaydiff=int(np.any(np.array(replay)!=ma,axis=2).sum());assert replaydiff==0;replay.save(R/'qa/F084_six_layers_replay_ARCHIVE_NOT_REQUEST.png')
def rigid(z,m,t):
 assert np.allclose(m.T@m,np.eye(2),atol=1e-12)
 inv=m.T;v=-inv@t;return z.transform(size,Image.Transform.AFFINE,(*inv[0],v[0],*inv[1],v[1]),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
def rot(deg):
 t=math.radians(deg);return np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]])
def capsule(points,r):
 ps=[tuple(map(float,p))for p in points];z=Image.new('L',size);d=ImageDraw.Draw(z);d.line(ps,fill=255,width=2*r+1)
 for x,y in ps:d.ellipse((x-r,y-r,x+r,y+r),fill=255)
 return np.array(z)>0
body=rigid(src['body_head_blouse'],np.eye(2),body_delta);nearfoot=src['near_shoe_ankle_SUPPORT_FIXED'].copy()
# One total original079 far-foot translation avoids resampling an already raised
#084 shoe back down. Its target equals084+66worldX,+23worldY geometrically.
far_source79=Image.open(S/'F079_true_far_whole_shoe_SINGLE_TRANSFORM_SOURCE.png').convert('RGBA');far_total_delta=np.array([150/scale,0.]);farfoot=rigid(far_source79,np.eye(2),far_total_delta)
far_delta_from84=np.array([66/scale,23/scale]);roots84={k:np.array(v)for k,v in g84['actual_sleeve_roots_native'].items()};roots90={k:v+body_delta for k,v in roots84.items()};arms={};affines={}
for side,k,deg in [('near','near_complete_arm',-15.),('far','far_complete_arm_jade_hand',14.)]:
 m=rot(deg);t=roots84[side]+body_delta-m@roots84[side];arms[side]=rigid(src[k],m,t);affines[side]={'source':'F084_FROZEN_'+k+'.png','rotation_degrees':deg,'matrix':m.tolist(),'translation_native':t.tolist(),'scale':1,'source_root_native':roots84[side].tolist(),'target_root_native':roots90[side].tolist(),'technical_proposal_pending_actual_input_review':True,'fingers_and_jade_not_split':True}
order=['far_shoe_ankle_LANDED','far_complete_arm_jade_hand','body_head_blouse','near_complete_arm','near_shoe_ankle_SUPPORT_FIXED'];layers={'far_shoe_ankle_LANDED':farfoot,'far_complete_arm_jade_hand':arms['far'],'body_head_blouse':body,'near_complete_arm':arms['near'],'near_shoe_ankle_SUPPORT_FIXED':nearfoot}
Afull=Image.new('RGBA',size)
for k in order:
 Afull.alpha_composite(layers[k]);p=R/'layers'/f'F090_{k}.png'
 if k=='near_shoe_ankle_SUPPORT_FIXED':shutil.copyfile(S/'F084_FROZEN_near_shoe_ankle_SUPPORT_FIXED.png',p)
 else:layers[k].save(p)
A=Afull.crop(crop);a=np.array(Afull);alpha={k:np.array(z)[:,:,3]for k,z in layers.items()}
def visible(k):
 front=np.zeros(ma.shape[:2],bool)
 for j in order[order.index(k)+1:]:front|=alpha[j]>0
 return(alpha[k]>0)&~front
Hn=np.array(g84['hidden_near_hip_proxy_native'])+body_delta;Hf=np.array(g84['hidden_far_hip_proxy_native'])+body_delta;An=np.array(g84['actual_near_ankle_proxy_native']);Af=np.array(g84['actual_far_ankle_proxy_native'])+far_delta_from84
# New landing schematic, NOT copied high-flexed084 knees or old skeleton bones.
# Halfway plus small forward-normal offsets is explicitly a soft volume proposal.
def softk(h,a,bend):
 v=a-h;n=np.array([v[1],-v[0]])/np.linalg.norm(v);return h+.5*v+n*bend
Kn=softk(Hn,An,20.);Kf=softk(Hf,Af,10.)
sleeves=np.zeros(ma.shape[:2],bool)
for p in roots90.values():sleeves|=capsule([p+[-20,-4],p+[20,14]],15)
bodyguard=(alpha['body_head_blouse']>0)&~sleeves;armguard=(visible('near_complete_arm')|visible('far_complete_arm_jade_hand'))&~sleeves;ng=visible('near_shoe_ankle_SUPPORT_FIXED')
future_near_shin=capsule([Kn,An+[0,-12]],48)&(yy<An[1]+3);fg0=visible('far_shoe_ankle_LANDED');fg_release=fg0&future_near_shin;fg=fg0&~future_near_shin
hard=bodyguard|armguard|ng|fg;neutral=(xx>=1120)&(xx<1610)&(yy>=510)&(yy<1010);edit=(neutral|sleeves)&~hard;inside=(xx>=1080)&(xx<1620)&(yy>=250)&(yy<1060);assert not np.any(edit&~inside);edit&=inside
B=Image.fromarray(edit.astype('uint8')*255).crop(crop)
for name,z in [('neutral_rectangle_NO_OLD_PANTS_DEPENDENCY',neutral),('WHITE_neutral_complete_trousers_and_sleeve_reference',edit),('HARD_real_body_except_small_sleeves',bodyguard),('HARD_visible_complete_arms_except_small_sleeves',armguard),('HARD_near_fixed_complete_actual_foot',ng),('HARD_far_visible_landed_foot_except_foreground_corridor',fg),('full_far_foot_LAYER_NOT_HIDDEN_GUARD',alpha['far_shoe_ankle_LANDED']>0),('future_near_shin_can_occlude_back_far_foot',fg_release),('small_original_sleeve_connection_domains',sleeves)]:Image.fromarray(z.astype('uint8')*255).save(R/'masks'/f'{name}.png')
A.save(R/'reference_native/A_real_five_layers_no_old_pants_540x810.png');B.save(R/'reference_native/B_neutral_edit_reference_540x810.png')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',15);small=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',12)
C=Image.new('RGBA',native_size,(234,240,244,255));d=ImageDraw.Draw(C);d.text((12,12),'C F090 完整腿体量技术示意 / NOT ART / 非骨测',font=font,fill='#273d4b');d.text((12,38),'双支撑→远左承重；不复制084高屈膝，不作终稿轮廓',font=small,fill='#536978');d.text((12,72),'Near RIGHT shoe = image-left / planted',font=small,fill='#3c7c9f');d.text((12,94),'Far LEFT shoe = image-right / lands',font=small,fill='#a27038');d.text((12,120),'Camera layers: far leg behind, near leg in front',font=small,fill='#536978');d.text((12,143),'Soft H follows body; new K = broad direction ONLY',font=small,fill='#536978')
d.polygon([(238,315),(435,315),(448,377),(395,425),(318,438),(260,409)],fill='#ced8e0',outline='#607c91',width=3);d.text((271,330),'WAIST / PELVIS',font=small,fill='#445b6c')
C.alpha_composite(farfoot.crop(crop));d=ImageDraw.Draw(C)
def volume(h,k,a,rt,rc,col,edge):
 ps=[np.array(v)-offcrop for v in [h,k,a]]
 for p,q,r1,r2 in [(ps[0],ps[1],rt,rt*.88),(ps[1],ps[2],rc,rc*.80)]:
  dv=q-p;n=np.array([-dv[1],dv[0]])/np.linalg.norm(dv);v=[p+n*r1,q+n*r2,q-n*r2,p-n*r1];d.polygon([tuple(t)for t in v],fill=col,outline=edge,width=3)
 x,y=ps[1];r=rc*.95;d.ellipse((x-r,y-r,x+r,y+r),fill=col,outline=edge,width=3)
 for p,txt in zip(ps,['hidden H','soft K','actual A']):
  x,y=p;d.ellipse((x-5,y-5,x+5,y+5),fill=edge);d.text((x+7,y-10),txt,font=small,fill=edge)
 d.line([tuple(p)for p in ps],fill=edge,width=2)
volume(Hf,Kf,Af,45,36,'#ddc3a5','#a27038');volume(Hn,Kn,An,47,38,'#a6c7d9','#3c7c9f');C.alpha_composite(nearfoot.crop(crop));d=ImageDraw.Draw(C);d.line((100,772,495,772),fill='#33858e',width=2);d.text((12,792),'体积示意/软方向不能进入画稿；整腰臀双腿仍需原生真绘',font=small,fill='#273d4b');C.save(R/'reference_native/C_complete_new_landing_volume_TECHNICAL_NOT_ART_540x810.png')
D=Image.new('RGBA',native_size,(234,240,244,255));dd=ImageDraw.Draw(D);dd.text((12,12),'D actual057/062 fabric / ink / palette ONLY',font=font,fill='#273d4b');dd.text((12,38),'Native1:1 interior rectangles, no old figure or leg silhouette',font=small,fill='#536978');patches=[]
for j,f in enumerate([57,62]):
 sp=S/f'F0{f}_palette_ARCHIVE_NOT_REQUEST.png';mp=S/f'F0{f}_actual_pants_material_mask.png';srcp=np.array(Image.open(sp).convert('RGBA'));mpa=binary_fill_holes(np.array(Image.open(mp).convert('L'))>0);rgb=srcp[:,:,:3].astype(int);valid=mpa&(srcp[:,:,3]>=250)&(rgb.max(axis=2)<145);ok=minimum_filter(valid.astype('uint8'),size=(64,48),mode='constant')>0;ys,xs=np.where(ok);assert len(xs);choices=[]
 for targetY in ([700,800]if f==57 else[680,800]):
  score=np.abs(ys-targetY)+np.abs(xs-xs.mean())*.03
  for u0 in choices:score+=np.where(np.hypot(xs-u0[0],ys-u0[1])<65,1e6,0)
  q=int(np.argmin(score));choices.append((int(xs[q]),int(ys[q])))
 for i,(cx,cy)in enumerate(choices):
  box=(cx-24,cy-32,cx+24,cy+32);assert valid[cy-32:cy+32,cx-24:cx+24].all();dx=35+i*250;dy=110+j*300;D.paste(Image.fromarray(srcp).crop(box),(dx,dy));dd=ImageDraw.Draw(D);dd.text((dx,dy-27),f'F0{f} actual material {i+1}',font=small,fill='#273d4b');dd.text((dx,dy+78),str(box),font=small,fill='#536978');patches.append({'source':sp.name,'source_SHA':sha(sp),'source_box_halfopen':list(box),'native_D_paste_xy':[dx,dy],'native_scale':1,'RGBA_copied_exact':True})
D.save(R/'reference_native/D_real057_062_interior_fabric_NO_FIGURE_540x810.png')
refs=[('A',R/'reference_native/A_real_five_layers_no_old_pants_540x810.png'),('B',R/'reference_native/B_neutral_edit_reference_540x810.png'),('C',R/'reference_native/C_complete_new_landing_volume_TECHNICAL_NOT_ART_540x810.png'),('D',R/'reference_native/D_real057_062_interior_fabric_NO_FIGURE_540x810.png')];paths=[]
for letter,p in refs:
 im=Image.open(p);assert im.size==native_size;q=R/'inputs_1024x1536'/f'{letter}_whole_canvas_256over135_PREPARED.png';im.resize((1024,1536),Image.Resampling.NEAREST if letter=='B'else Image.Resampling.LANCZOS).save(q);paths.append(q)
for tone,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 sheet=Image.new('RGB',(2160,850),(236,241,246));d=ImageDraw.Draw(sheet)
 for j,(letter,p)in enumerate(refs):
  z=Image.new('RGBA',native_size,col);z.alpha_composite(Image.open(p).convert('RGBA'));sheet.paste(z.convert('RGB'),(j*540,35));d.text((j*540+5,7),letter+' / native540x810 / whole256/135',font=small,fill='#273d4b')
 sheet.save(R/f'qa/F090_four_native_references_{tone}.png');z=Image.new('RGBA',native_size,col);z.alpha_composite(A);z.convert('RGB').save(R/f'qa/F090_real_anchors_{tone}.png');wash=Image.new('RGBA',native_size,(219,36,121,0));wash.putalpha(B.point(lambda x:110 if x else 0));z.alpha_composite(wash);z.convert('RGB').save(R/f'qa/F090_actual_white_domain_{tone}.png')
sole={}
for k,z in [('near_fixed',nearfoot),('far_landed',farfoot)]:
 ar=np.array(z);ys,xs=np.where(ar[:,:,3]>=128);sole[k]={'native_sole_alpha128':int(ys.max()),'local_sole_alpha128':int(ys.max()-250),'native_xspan_alpha128':[int(xs.min()),int(xs.max())],'local_xspan_alpha128':[int(xs.min()-1080),int(xs.max()-1080)]}
assert sole['near_fixed']['native_sole_alpha128']==sole['far_landed']['native_sole_alpha128']==1022
near_diff=int(np.any(np.array(nearfoot)!=np.array(src['near_shoe_ankle_SUPPORT_FIXED']),axis=2).sum());assert near_diff==0
lab,_=label(edit);probes={}
for name,p in [('near_hiddenH',Hn),('near_softK',Kn),('near_ankle_approach',An+[0,-25]),('far_hiddenH',Hf),('far_softK',Kf),('far_ankle_approach',Af+[0,-25])]:
 x,y=np.rint(p).astype(int);probes[name]={'native_xy':[int(x),int(y)],'white':bool(edit[y,x]),'component':int(lab[y,x])}
assert all(v['white']for v in probes.values())and len({v['component']for v in probes.values()})==1
checks={'status':'F090_FOUR_NEUTRAL_INPUTS_PENDING_ROOT_ASTRA_GATE_NO_CALL','frame':90,'hold':5,'inclusive_frames':[90,94],'source084_SHA':sha(S/'F084_LOCKED_mother_ARCHIVE_NOT_REQUEST.png'),'source084_six_layer_RGBA_replay_changes':replaydiff,'support':'Double support transferring load to FAR LEFT landed shoe at image-right; NEAR RIGHT shoe image-left stays exactly fixed.','registration':reg,'body_world_delta':body_world.tolist(),'body_native_delta':body_delta.tolist(),'body_affine':{'matrix':[[1,0],[0,1]],'translation_native':body_delta.tolist(),'scale':1,'one_whole_layer_AA_resampling':True},'whole_arm_affines':affines,'actual_sleeve_roots_native':{k:v.tolist()for k,v in roots90.items()},'near_whole_foot_RGBA_changes':near_diff,'near_whole_foot_file_byte_identical':sha(R/'layers/F090_near_shoe_ankle_SUPPORT_FIXED.png')==sha(S/'F084_FROZEN_near_shoe_ankle_SUPPORT_FIXED.png'),'far_original079_single_transform':{'source_SHA':sha(S/'F079_true_far_whole_shoe_SINGLE_TRANSFORM_SOURCE.png'),'matrix':[[1,0],[0,1]],'translation_native':far_total_delta.tolist(),'translation_world':[150,0],'scale':1,'source084_equivalent_geometric_delta_native':far_delta_from84.tolist(),'source084_delta_world':[66,23],'not_resampled_from084_raised_foot':True},'feet':sole,'soft_H_near':Hn.tolist(),'soft_H_far':Hf.tolist(),'real_ankle_proxy_near':An.tolist(),'real_ankle_proxy_far':Af.tolist(),'new_landing_softK_near':Kn.tolist(),'new_landing_softK_far':Kf.tolist(),'softK_derivation':'Halfway between same-source hidden H and actual placed ankle plus small forward normal offsets20near/10far; purely new schematic landing direction, not084 knee copy, old absolute bones, or measured lengths.','crop_native':crop,'native_size':native_size,'tool_input_size':[1024,1536],'whole_uniform_forward':256/135,'unique_inverse':135/256,'inverse_mapping':'native=(tool*135/256)+[1080,250] for the entire canvas; no per-limb/foot fit or nonuniformscale.','neutral_rectangle_native_halfopen':[1120,510,1610,1010],'B_depends_on_old_trouser_contours':False,'B_is_reference_not_tool_hardmask':True,'A_old084_trousers_layer_pixels_adopted':0,'white_pixels':int(edit.sum()),'guard_intersections':{k:int((edit&z).sum())for k,z in [('body_except_sleeves',bodyguard),('whole_visible_arms_except_sleeves',armguard),('near_actual_fixed_foot',ng),('far_actual_visible_landed_foot_except_future_near_occlusion',fg)]},'guard_alpha0_pixels':int((hard&(a[:,:,3]==0)).sum()),'far_source_material_released_for_future_near_shin_occlusion':int(fg_release.sum()),'continuous_white_probes':probes,'D_real_material_patch_mapping':patches,'requested_images':[{'letter':l,'path':str(p.relative_to(R)),'sha256':sha(p),'size':list(Image.open(p).size)}for(l,_),p in zip(refs,paths)],'new_calls':0,'following_states_unopened':True}
assert not any(checks['guard_intersections'].values())and checks['guard_alpha0_pixels']==0
def bounds(z):
 ys,xs=np.where(z)
 if not len(xs):return None
 b=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
 return {'native_bbox_halfopen':b,'local_bbox_halfopen':[b[0]-crop[0],b[1]-crop[1],b[2]-crop[0],b[3]-crop[1]],'crop_margins_L_T_R_B':[b[0]-crop[0],b[1]-crop[1],crop[2]-b[2],crop[3]-b[3]]}
Avisible=a[:,:,3]>0
active_nonbody=np.logical_or.reduce([visible(k)for k in order if k!='body_head_blouse'])
checks['bounds_and_crop']={'A_visible_material_inside_crop':bounds(Avisible&inside),'A_visible_whole_arms_and_feet':bounds(active_nonbody),'B_actual_white':bounds(edit),'nonbody_active_material_outside_crop_pixels':int((active_nonbody&~inside).sum()),'white_outside_crop_pixels':int((edit&~inside).sum()),'body_top_boundary_is_intentional_shoulder_crop_no_head':True,'body_outside_crop_is_stable_head_upper_torso_not_editable':True,'intentional_top_cut_is_not_a_reposition_or_fit':True}
assert checks['bounds_and_crop']['nonbody_active_material_outside_crop_pixels']==0
checks['source_file_SHA256']={v['path']:v['sha256']for v in json.loads((S/'snapshot_manifest.json').read_text())['files']}
checks['prepared_layer_SHA256']={k:sha(R/'layers'/f'F090_{k}.png')for k in order}
checks['near_whole_foot_source_and_target_SHA256']={'source':sha(S/'F084_FROZEN_near_shoe_ankle_SUPPORT_FIXED.png'),'target':sha(R/'layers/F090_near_shoe_ankle_SUPPORT_FIXED.png')}
checks['A_five_layer_replay_RGBA_changes']=int(np.any(np.array(A)!=np.array(Afull.crop(crop)),axis=2).sum())
checks['D_has_no_old_character_contour']=True
checks['review_limit']='Input geometry/material preparation only. No generated090, no final anatomy/volume acceptance, no exposure approval.'
(R/'geometry/preparation_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
prompt='''Edit image A as a cropped restoration, keeping exactly its shoulder/blouse-to-feet 2:3 canvas, scale and original anchor positions. The head is outside this crop: do not add a head, zoom out, recenter a person or fit a whole figure. B is the editing-region reference, C is a NOT_ART technical complete-volume and soft-direction diagram, D is real fabric/ink/color only. Return the same cropped transparent composition without technical colors, lines or text.
Draw ONE coherent natural waist/pelvis and BOTH complete navy trouser legs in the empty editable area. No old084 trouser silhouette was supplied to preserve. F090 is double support transferring load toward the far anatomical LEFT leg. The near anatomical RIGHT original shoe at IMAGE-LEFT stays planted in exactly the previous support location. The far LEFT original shoe has landed at IMAGE-RIGHT on the same actual sole baseline. Keep both already placed complete original shoes/ankles and their x-ranges; do not move, resize, redesign, duplicate or invent another foot. Do not copy084 high knee flexion into this landing pose.
The new far LEFT leg accepts weight naturally down to the right landed ankle. The near RIGHT leg remains connected back to the unchanged left shoe. Preserve full accepted thigh, knee-back and calf volume with natural slight hip/knee settling, coherent crotch and front/back overlaps; a blouse hem is not an anatomical hip. Near camera-side trousers are in front, far leg/shoe behind wherever naturally hidden. Do not cut a shoe-shaped hole through a new foreground shin because a rear source layer has hidden alpha. Source arms, hands and jade already follow the proposed small counterphase swing; keep whole source skin and material, joining only the permitted small sleeve seams. Fill continuous navy under the real blouse and into both actual ankles, with no transparent band, narrow bridges, stretched tubes or extraction cuts. Match locked057/062 flat navy, shadow and ink from D, without cumulative brightening. No added head, hand, shoe, prop or following state.'''
(R/'requests/prompt_DRAFT_PENDING_ASTRA_NOT_CALLED.txt').write_text(prompt+'\n');(R/'requests/arguments_PREPARED_NOT_CALLED.json').write_text(json.dumps({'prompt':prompt,'referenced_image_paths':[str(p)for p in paths],'transparent_background':True},ensure_ascii=False,indent=2)+'\n')
(R/'README.md').write_text('''# F090 single neutral complete-volume input gate — NO CALL

Source084 is already locked21acf204…f6ae (parent authority2761136). Its six real production layers replay the locked mother exactly; archived trousers are ONLY lineage/replay, never supplied to A/B/C/D or shape the white domain. A only contains the newly rigid-positioned true body/two complete arms/two original shoes.

090..094 hold5, double support→farLEFT load. Actual body beat+43.21452631136/+8.15527053322world, native+118.6874398523/+22.3982133673. NearRIGHT whole source shoe stays at exactly its old position, PNG bytes unchanged1022sole. FarLEFT lands+66/+23world from084; use original true079 far shoe ONE total+150worldX,0Y translation to avoid repeated AA. Both real soles1022. Complete arms proposed−15/+14degrees about actual084 sleeve roots plus bodybeat, scale1 fingers/jade unsplit. No originalsource recolor or leg warp.

Suggested crop1080,250,1620,1060=540×810, all four full canvases uniformly256/135→1024×1536; unique inverse135/256 plus1080,250. No per-part bodyfit, shoe reposition or nonuniform scaling. B neutral rectangle1120,510,1610,1010 minus genuine visible guard plus existing small sleeve seams; no old084 pants contour. Rear shoe kept as complete back layer, never a hidden-alpha foreground barrier.

C is a NEW wide pelvis/two whole thighs/soft knees/calves diagram, not art or measured bones; landing K directions are newly constructed between the same-source hiddenH and true ankle targets, not copied from high-flexed084. D only native1:1 interior057/062 cloth rectangles. Only four scaled PNG references enter requests; no whole mother/old leg/failedraw. Actual returned whole pants support, natural volume and originalshoe registration must pass BEFORE source-protected recomposition, never hide wrong pose with restored shoes/thin bridges.

Input gate only, NO GENERATION; pending root/Astra image review. Root/Astra must review actual gray/dark references and white domain before any call. Other states untouched.
''',encoding='utf8')
print(json.dumps({'source_replay':replaydiff,'crop':crop,'body_native_delta':body_delta.tolist(),'feet':sole,'white_pixels':int(edit.sum()),'guards':checks['guard_intersections'],'near_byte_same':checks['near_whole_foot_file_byte_identical'],'input_SHA':checks['requested_images']},ensure_ascii=False,indent=2))
