#!/usr/bin/env python3
"""F095 only: true090 layers, stopping event, new NOT_ART full-leg volumes."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import label
import numpy as np,json,hashlib,math,shutil
R=Path(__file__).resolve().parent;S=R/'sources';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not(R/'requests/execution_state.json').exists()
for v in json.loads((S/'snapshot_manifest.json').read_text())['files']:assert sha(S/v['snapshot'])==v['sha256']
for d in ['layers','reference_native','inputs_1024x1536','masks','qa','geometry','requests']:(R/d).mkdir(exist_ok=True)
size=(1672,1080);crop=(1120,250,1660,1060);ns=(540,810);off=np.array(crop[:2]);yy,xx=np.indices((1080,1672));g90=json.loads((S/'F090_approved_actual_target_metadata.json').read_text());e={v['frame']:v for v in json.loads((S/'events090_095_ONLY.json').read_text())['states']};scale=.36410361842105265;dw=np.array(e[95]['head_center'])-np.array(e[90]['head_center']);delta=dw/scale
assert e[95]['hold_frames']==5 and e[95]['last_frame_inclusive']==99;assert np.array_equal(np.array(e[95]['near_ankle'])-e[90]['near_ankle'],[59,0]);assert e[95]['far_ankle']==e[90]['far_ankle']
keys=['body_head_blouse','near_complete_arm','far_complete_arm_jade_hand','near_shoe_ankle_SUPPORT_FIXED','far_shoe_ankle_LANDED'];src={k:Image.open(S/f'SOURCE_F090_{k}.png').convert('RGBA')for k in keys};mother=Image.open(S/'F090_LOCKED_012e_MOTHER_ARCHIVE_NOT_REQUEST.png').convert('RGBA');oldpants=Image.open(S/'F090_actual_complete_trousers_REPLAY_ONLY_NOT_REQUEST.png').convert('RGBA');rep=Image.new('RGBA',size)
for z in [src['far_shoe_ankle_LANDED'],oldpants,src['far_complete_arm_jade_hand'],src['body_head_blouse'],src['near_complete_arm'],src['near_shoe_ankle_SUPPORT_FIXED']]:rep.alpha_composite(z)
assert np.array_equal(np.array(rep),np.array(mother));rep.save(R/'qa/F090_mother_six_layer_exact_replay_NOT_REQUEST.png')
def rigid(z,M,t):
 assert np.allclose(M.T@M,np.eye(2),atol=1e-12);iv=M.T;it=-iv@t;return z.transform(size,Image.Transform.AFFINE,(*iv[0],it[0],*iv[1],it[1]),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
def rot(deg):
 a=math.radians(deg);return np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
body=rigid(src['body_head_blouse'],np.eye(2),delta);farfoot=src['far_shoe_ankle_LANDED'].copy();footdelta=np.array([59/scale,0]);nearfoot=rigid(src['near_shoe_ankle_SUPPORT_FIXED'],np.eye(2),footdelta)
roots90={side:np.array(g90['inherited_approved_affines']['arms'][side]['target_root_native'])for side in ['near','far']};roots95={k:p+delta for k,p in roots90.items()};arms={};aff={}
# Parent confirms no later095armpoint/clearance authority exists. These are
# bounded whole-source settling proposals, not old1184/592 wrist compliance.
for side,key,deg in [('near','near_complete_arm',-12.),('far','far_complete_arm_jade_hand',10.)]:
 M=rot(deg);t=roots95[side]-M@roots90[side];arms[side]=rigid(src[key],M,t);aff[side]={'rotation_degrees_PROPOSAL':deg,'M':M.tolist(),'t':t.tolist(),'scale':1,'source_actual_sleeve_root':roots90[side].tolist(),'target_actual_sleeve_root':roots95[side].tolist(),'same_complete_arm_fingers_jade_unsplit':True,'new095_arm_art_not_frozen':True}
layers={'far_shoe_ankle_SUPPORT_FIXED':farfoot,'far_complete_arm_jade_hand':arms['far'],'body_head_blouse':body,'near_complete_arm':arms['near'],'near_shoe_ankle_COLLECTED_LANDED':nearfoot};order=list(layers);flat=Image.new('RGBA',size);lsha=[]
for k,z in layers.items():
 p=R/'layers'/f'F095_{k}.png'
 if k=='far_shoe_ankle_SUPPORT_FIXED':shutil.copyfile(S/'SOURCE_F090_far_shoe_ankle_LANDED.png',p)
 else:z.save(p)
 flat.alpha_composite(z);lsha.append({'path':str(p.relative_to(R)),'sha256':sha(p)})
arr={k:np.array(z)for k,z in layers.items()};alph={k:z[:,:,3]for k,z in arr.items()};a0=np.array(flat)
def visible(k):
 ahead=np.zeros((1080,1672),bool)
 for j in order[order.index(k)+1:]:ahead|=alph[j]>0
 return (alph[k]>0)&~ahead
def capsule(ps,r):
 z=Image.new('L',size);d=ImageDraw.Draw(z);ps=[tuple(map(float,p))for p in ps];d.line(ps,fill=255,width=2*r+1)
 for x,y in ps:d.ellipse((x-r,y-r,x+r,y+r),fill=255)
 return np.array(z)>0
Hn=np.array(g90['soft_HK_only']['soft_H_near'])+delta;Hf=np.array(g90['soft_HK_only']['soft_H_far'])+delta;An=np.array(g90['actual_ankles']['near'])+footdelta;Af=np.array(g90['actual_ankles']['far'])
def softK(h,a,b):
 v=a-h;n=np.array([v[1],-v[0]])/np.linalg.norm(v);return h+.5*v+n*b
Kn=softK(Hn,An,10);Kf=softK(Hf,Af,6)
sleeves=np.zeros((1080,1672),bool)
for p in roots95.values():sleeves|=capsule([p+[-20,-4],p+[20,14]],15)
bodyguard=(alph['body_head_blouse']>0)&~sleeves;armguard=(visible('near_complete_arm')|visible('far_complete_arm_jade_hand'))&~sleeves;ng=visible('near_shoe_ankle_COLLECTED_LANDED');farvis=visible('far_shoe_ankle_SUPPORT_FIXED');frontshin=capsule([Kn,An+[0,-12]],48)&(yy<An[1]+3);fg=farvis&~frontshin
hard=bodyguard|armguard|ng|fg;neutral=(xx>=1310)&(xx<1640)&(yy>=510)&(yy<1012);white=(neutral|sleeves)&~hard;inside=(xx>=crop[0])&(xx<crop[2])&(yy>=crop[1])&(yy<crop[3]);assert not np.any(white&~inside)
# New complete volume diagram, NO old090 leg silhouette. Soft hip/knee choices
# are source-calibrated projected directions, never measured anatomical bones.
V=Image.new('RGBA',size);vd=ImageDraw.Draw(V);vd.polygon([(1374,535),(1570,535),(1576,618),(1528,674),(1421,675),(1376,634)],fill='#ced8e0',outline='#607c91',width=3)
def volume(h,k,a,rt,rc,col,edge):
 for p,q,r1,r2 in [(h,k,rt,rt*.88),(k,a,rc,rc*.80)]:
  dv=q-p;n=np.array([-dv[1],dv[0]])/np.linalg.norm(dv);vd.polygon([tuple(p+n*r1),tuple(q+n*r2),tuple(q-n*r2),tuple(p-n*r1)],fill=col,outline=edge,width=3)
 x,y=k;rr=rc*.95;vd.ellipse((x-rr,y-rr,x+rr,y+rr),fill=col,outline=edge,width=3)
volume(Hf,Kf,Af,45,34,'#ddc3a5','#a27038');volume(Hn,Kn,An,47,36,'#a6c7d9','#3c7c9f');va=np.array(V);vol=va[:,:,3]>0;assert not np.any(vol&~inside)
# Place every real source pixel back literally; behind-source technical volume
# must never alter real hand/shoe/blouse material in the input.
a=a0.copy();ins=vol&(a0[:,:,3]==0);a[ins]=va[ins];font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',11);A=Image.fromarray(a).crop(crop);note=Image.new('RGBA',ns);nd=ImageDraw.Draw(note);nd.text((8,12),'A095 NOT_ART / 完整体量停步预摆',font=font,fill='#273d4b');nd.text((8,33),'FarLEFT support fixed; nearRIGHT closes/lands',font=font,fill='#536978');ar=np.array(A);na=np.array(note);pick=(na[:,:,3]>0)&(ar[:,:,3]==0);ar[pick]=na[pick];A=Image.fromarray(ar);Ap=R/'reference_native/A_real_layers_full_NEW_volume_NOT_ART_540x810.png';A.save(Ap)
B=Image.fromarray(white.astype('uint8')*255).crop(crop);Bp=R/'reference_native/B_neutral_complete_pants_WHITE_REFERENCE_540x810.png';B.save(Bp)
C=Image.new('RGBA',ns,(234,240,244,255));C.alpha_composite(Image.fromarray(a).crop(crop));d=ImageDraw.Draw(C);d.text((8,12),'C SAME A / SOFT CHAIN / NOT ART',font=font,fill='#273d4b');d.text((8,33),'095..099 hold5: both landed, stop travelling',font=font,fill='#536978')
for side,ps,col in [('far',[Hf,Kf,Af],'#a27038'),('near',[Hn,Kn,An],'#3c7c9f')]:
 ps=[p-off for p in ps];d.line([tuple(p)for p in ps],fill=col,width=2)
 for j,(x,y)in enumerate(ps):
  r=7 if j<2 else 10;d.ellipse((x-r,y-r,x+r,y+r),outline=col,width=2)
  if j==2:d.line((x-14,y,x+14,y),fill=col,width=2);d.line((x,y-14,x,y+14),fill=col,width=2)
d.line((180,772,485,772),fill='#33858e',width=2);d.text((8,790),'Sole772; actual ankleYs unequal. NOT measured bones.',font=font,fill='#273d4b');Cp=R/'reference_native/C_same_A_soft_chains_actual_anchors_NOT_ART_540x810.png';C.save(Cp)
Dp=R/'reference_native/D_locked057_062_fabric_ONLY_540x810.png';shutil.copyfile(S/'D057_062_actual_fabric_NATIVE_APPROVED.png',Dp)
refs={'A':Ap,'B':Bp,'C':Cp,'D':Dp};paths={}
for k,p in refs.items():
 q=R/'inputs_1024x1536'/f'{k}_F095_PREPARED_NOT_CALLED.png';paths[k]=q
 if k=='D':shutil.copyfile(S/'D057_062_actual_fabric_TOOL_APPROVED.png',q)
 else:Image.open(p).resize((1024,1536),Image.Resampling.NEAREST if k=='B'else Image.Resampling.LANCZOS).save(q)
for name,z in [('HARD_actual_body_except_sleeves',bodyguard),('HARD_actual_complete_visible_arms_except_sleeves',armguard),('HARD_actual_near_landed_visible_whole_foot',ng),('HARD_visible_far_support_material_NOT_hidden_alpha',fg),('far_complete_support_LAYER_not_guard',alph['far_shoe_ankle_SUPPORT_FIXED']>0),('future_near_shin_may_cover_back_far_shoe',farvis&frontshin),('WHITE_full_neutral_pants_and_sleeve_seams',white),('TECHNICAL_NEW_complete_volume_NOT_ART',vol),('small_sleeve_connection_WHITE_domains',sleeves)]:Image.fromarray(z.astype('uint8')*255).save(R/'masks'/f'{name}.png')
for tone,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 sheet=Image.new('RGB',(2160,850),(235,240,245));d=ImageDraw.Draw(sheet)
 for j,(k,p)in enumerate(refs.items()):
  z=Image.new('RGBA',ns,col);z.alpha_composite(Image.open(p).convert('RGBA'));sheet.paste(z.convert('RGB'),(j*540,35));d.text((j*540+8,7),k+'095 /540x810 /whole256/135',font=font,fill='black')
 sheet.save(R/f'qa/F095_four_inputs_{tone}.png');z=Image.new('RGBA',ns,col);z.alpha_composite(A);wash=Image.new('RGBA',ns,(218,35,122,0));wash.putalpha(B.point(lambda x:85 if x else 0));z.alpha_composite(wash);z.save(R/f'qa/F095_real_material_and_white_overlay_{tone}.png');feet=Image.new('RGBA',size,col);feet.alpha_composite(farfoot);feet.alpha_composite(nearfoot);feet.crop((1325,915,1585,1040)).resize((1040,500)).convert('RGB').save(R/f'qa/F095_actual_whole_feet_support_and_occlusion_{tone}.png')
def bbox(z):
 ys,xs=np.where(z)
 if not len(xs):return None
 b=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)];return {'native_halfopen':b,'crop_margins_L_T_R_B':[b[0]-crop[0],b[1]-crop[1],crop[2]-b[2],crop[3]-b[3]]}
feet={}
for side,z in [('near_collected',nearfoot),('far_support_FIXED',farfoot)]:
 za=np.array(z);ys,xs=np.where(za[:,:,3]>=128);feet[side]={'sole_alpha128_native':int(ys.max()),'sole_local':int(ys.max()-250),'xspan_native_alpha128':[int(xs.min()),int(xs.max())]}
assert all(z['sole_alpha128_native']==1022 for z in feet.values());assert sha(R/'layers/F095_far_shoe_ankle_SUPPORT_FIXED.png')==sha(S/'SOURCE_F090_far_shoe_ankle_LANDED.png')
lab,_=label(white);probes={}
for name,p in [('nearH',Hn),('farH',Hf),('nearK',Kn),('farK',Kf),('near_ankle_approach',An+[0,-25]),('far_ankle_approach',Af+[0,-25])]:
 x,y=np.rint(p).astype(int);probes[name]={'native':[int(x),int(y)],'white':bool(white[y,x]),'component':int(lab[y,x])}
active=np.logical_or.reduce([visible(k)for k in order if k!='body_head_blouse']);checks={'status':'F095_COMPLETE_VOLUME_INPUT_PENDING_ROOT_ASTRA_NO_CALL','source_locked090_SHA256':sha(S/'F090_LOCKED_012e_MOTHER_ARCHIVE_NOT_REQUEST.png'),'source090_six_layers_RGBA_replay_changes':0,'frame':95,'inclusive_hold':[95,99],'event_authority':'nearRIGHT collects and settles; both feet grounded, stop travelling; no new heelroll/lift instruction. FarLEFT previous front shoe remains planted while near collects.','body_world_delta':dw.tolist(),'body_whole_native_translation':delta.tolist(),'body_affine':{'M':[[1,0],[0,1]],'t':delta.tolist(),'scale':1},'whole_arm_proposals':aff,'source_sleeve_roots090':{k:v.tolist()for k,v in roots90.items()},'target_sleeve_roots095':{k:v.tolist()for k,v in roots95.items()},'far_support_whole_file_byte_identical':True,'far_support_SHA256':sha(S/'SOURCE_F090_far_shoe_ankle_LANDED.png'),'near_whole_foot_affine':{'M':[[1,0],[0,1]],'t':footdelta.tolist(),'world_delta':[59,0],'scale':1,'no_roll_no_Y_lift_no_individual_foot_edits':True,'one_whole_layer_AA_resample':True},'feet':feet,'actual_ankle_proxy_near':An.tolist(),'actual_ankle_proxy_far':Af.tolist(),'softH_near':Hn.tolist(),'softH_far':Hf.tolist(),'softK_near':Kn.tolist(),'softK_far':Kf.tolist(),'soft_pose_limit':'Hip follows approved090 same-source hidden proxy/bodybeat. NewK derived near halfway plus10/6px forward-normal only to propose broad stopping volume, not measured anatomy or fixed bone lengths. No absolute legacy hip/ankle/wrist imported.','A_original_actual_material_RGBA_changes':int(np.any(a[a0[:,:,3]>0]!=a0[a0[:,:,3]>0],axis=1).sum()),'A_old090_trouser_pixels_prompted':0,'B_depends_on_old090_pants_shape':False,'B_white_pixels':int(white.sum()),'guard_intersections':{k:int((white&v).sum())for k,v in [('body',bodyguard),('complete_visible_arms',armguard),('near_landed_foot',ng),('far_visible_support',fg)]},'guard_alpha0_pixels':int((hard&(a0[:,:,3]==0)).sum()),'far_hidden_foot_alpha_used_as_guard':False,'far_visible_material_released_for_near_new_shin':int((farvis&frontshin).sum()),'continuous_white_probes':probes,'crop_native':crop,'native_size':ns,'tool_size':[1024,1536],'whole_forward':256/135,'unique_inverse':135/256,'mapping':'native=tool*135/256+[1120,250] for whole canvas; no partfit/bodyfit/legwarp.','bounds':{'actual_arms_feet':bbox(active),'white':bbox(white),'new_technical_volume':bbox(vol)},'active_arms_feet_outside_crop':int((active&~inside).sum()),'volume_outside_crop':int((vol&~inside).sum()),'technical_volume_uncovered_outside_white':int((vol&~white&~hard).sum()),'head_outside_crop_intentionally_body_upper_cut':True,'D_byte_identical_native_and_tool':[Dp.read_bytes()==(S/'D057_062_actual_fabric_NATIVE_APPROVED.png').read_bytes(),paths['D'].read_bytes()==(S/'D057_062_actual_fabric_TOOL_APPROVED.png').read_bytes()],'source_and_layer_SHA256':lsha,'inputs':[{'letter':k,'path':str(paths[k].relative_to(R)),'sha256':sha(paths[k]),'size':list(Image.open(paths[k]).size)}for k in refs],'new_image_calls':0,'other_states_unopened':True}
assert not any(checks['guard_intersections'].values())and checks['guard_alpha0_pixels']==checks['A_original_actual_material_RGBA_changes']==checks['active_arms_feet_outside_crop']==0
assert all(p['white']for p in probes.values())and len({p['component']for p in probes.values()})==1
(R/'geometry/preparation_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
prompt='''Edit image A as a cropped restoration on exactly this1024x1536 shoulder/blouse-to-feet canvas. Keep the existing real blouse, complete arms/hands/jade and BOTH original shoe/ankle targets in exactly their placed positions. The head is outside this crop: do not add a head, zoom out, recenter or fit a full figure. A contains a complete NEW waist/pelvis/two-leg TECHNICAL VOLUME, not finished art. Replace these technical colors and lines with original navy trousers. B is the whole continuous editing-region reference, C is the SAME A with soft chains and actual shoe anchors, D is locked057/062 fabric/ink/color only.
F095 is the collecting-and-stopping pose, held095–099: the far anatomical LEFT shoe at image-right stays planted in exactly the previous090 support position; the near anatomical RIGHT trailing shoe has collected forward and is NOW settled on the same actual ground. Do not invent a raised heel, floating foot or roll. Keep both true whole-shoe x-ranges, their overlap and sole baseline. The nearRIGHT shoe and trousers are the foreground; the farLEFT complete shoe is a rear layer and may be naturally hidden by the new near shin/shoe. Never carve a shoe-shaped hole using hidden rear alpha, move a shoe, widen the stance, stretch a limb to a generated foot or add another foot.
Draw ONE coherent natural waist, pelvis and BOTH COMPLETE trouser legs with full thighs, knee-back volume and calves, natural settling and a continuous crotch. Soft hips/knees are only projected-direction proposals, not measured bone lengths; do not copy the previous090 long stepping silhouette. Join below the real blouse and into BOTH actual ankles without transparent bands, narrow bridges or extraction cuts. Preserve the original whole-arm/hand/jade material; only small marked sleeve connections may change. Hands stay empty and do not touch a lamp. Match D's flat navy/shadow/ink, without cumulative brightening. Return the same transparent cropped composition without guide colors, labels, extra head, hand, foot or following state.'''
(R/'requests/prompt_DRAFT_NOT_FROZEN_NOT_CALLED.txt').write_text(prompt+'\n');(R/'requests/arguments_PREPARED_NOT_CALLED.json').write_text(json.dumps({'prompt':prompt,'referenced_image_paths':[str(paths[k])for k in refs],'transparent_background':True},indent=2)+'\n')
(R/'README.md').write_text('''# F095 complete-volume collecting/stop input — NO CALL

Only mother090012e7bae…5156, lockedd714f5ba. Its6productionlayers replay exactly. Actual old090 trousers are lineage/replay ONLY; their silhouette never enters A/B/newvolume. Source5real layers are fromSOURCE_F090*.png; no failed090 image or old codedF095 character is used.

Only90→95 body/event deltas: head/body+22.1059879304/−4.90576396474world; nearRIGHT whole trailing shoe+59worldX/0Y collects and is settled in095; farLEFT front support whole PNG remains byte-identical/native position. Both soles1022. No095lift/heelroll is authorized. Complete source near/far arms propose−12/+10deg whole-source settling around actual090sleeve roots+bodybeat, scale1, fingers/jade unsplit. These are explicitly pending095input review, not old1184/592 wrist compliance or new anatomy measurements.

A real body/arms/shoes plus NEW wide NOT_ART waist/pelvis/two thighs/softknees/calves; B neutral wholepants+smallsleeve windows minus actualvisible material guards; C sameA+softchains/realankle/sole markers; D literal locked057/062material. Hidden far shoe alpha is NOT a foreground hardguard. New hip proxy follows source090samebodybeat; knee directions are newly proposed broad stoppingvolume, not fixed bone lengths. Final native art must actually show natural connected legs rather than thin bridges or forcing old codes.

Nativecrop1120,250,1660,1060=540x810, whole256/135→1024x1536; inverse135/256+[1120,250]. Head intentionally outside crop. Sources/matrices/actual alpha/support/white checks archived. Input gate only, NO GENERATION; root/Astra must review all actual images and full draft before any call. No other state prepared.
''')
print(json.dumps({k:checks[k]for k in ['body_whole_native_translation','feet','B_white_pixels','guard_intersections','continuous_white_probes','bounds','far_visible_material_released_for_near_new_shin','inputs']},indent=2))
