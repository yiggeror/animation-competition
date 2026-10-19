#!/usr/bin/env python3
"""Corrected090 input only. ApprovedC literal volume, no failed090 raw reads."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,shutil
from scipy.ndimage import binary_fill_holes
R=Path(__file__).resolve().parent;S=R/'sources';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not(R/'requests/execution_state.json').exists()
for z in json.loads((S/'snapshot_manifest.json').read_text())['files']:assert sha(S/z['path'])==z['sha256']
for d in ['reference_native','inputs_1024x1536','masks','geometry','qa','requests','production_reference_layers']:(R/d).mkdir(exist_ok=True)
g=json.loads((S/'approved_geometry_preparation_checks.json').read_text());crop=g['crop_native'];assert crop==[1080,250,1620,1060];N=S/'approved_reference_native';I=S/'approved_inputs_1024x1536'
names={'A':'A_real_five_layers_no_old_pants_540x810.png','B':'B_neutral_edit_reference_540x810.png','C':'C_complete_new_landing_volume_TECHNICAL_NOT_ART_540x810.png','D':'D_real057_062_interior_fabric_NO_FIGURE_540x810.png'}
a0=np.array(Image.open(N/names['A']).convert('RGBA'));c0=np.array(Image.open(N/names['C']).convert('RGBA'));yy,xx=np.indices((810,540));vol=np.zeros((810,540),bool)
# All six fills/outline colors from approvedC, literal same-coordinate pixels.
for hx in ['ced8e0','607c91','a6c7d9','3c7c9f','ddc3a5','a27038']:vol|=np.all(c0[:,:,:3]==[int(hx[i:i+2],16)for i in [0,2,4]],axis=2)
vol&=(yy>=315)&(yy<745)&(xx>=110)&(xx<460);vol=binary_fill_holes(vol);v=np.zeros_like(a0);v[vol]=c0[vol];Image.fromarray(v).save(R/'reference_native/approved_C_literal_volume_RGBA.png')
empty=a0[:,:,3]==0;insert=vol&empty;a=a0.copy();a[insert]=c0[insert];a_withoutnotes=a.copy();A=Image.fromarray(a);font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',11)
notes=Image.new('RGBA',(540,810));d=ImageDraw.Draw(notes);d.text((8,12),'A NOT_ART / 技术体量预摆',font=font,fill='#273d4b');d.text((8,33),'Real five layers fixed; pants still NEW ART',font=font,fill='#536978');n=np.array(notes);m=(n[:,:,3]>0)&empty;a[m]=n[m];A=Image.fromarray(a)
npths={};npths['A']=R/'reference_native/A_real_layers_plus_approved_volume_NOT_ART_540x810.png';A.save(npths['A'])
for k in ['B','D']:npths[k]=R/'reference_native'/f'{k}_APPROVED_BYTE_IDENTICAL_540x810.png';shutil.copyfile(N/names[k],npths[k])
# SAME A, adding only technical soft chains and actual-source ankle anchors.
C=Image.new('RGBA',(540,810),(234,240,244,255));C.alpha_composite(Image.fromarray(a_withoutnotes));d=ImageDraw.Draw(C);d.text((8,10),'C SAME A + SOFT CHAIN / NOT ART',font=font,fill='#273d4b');d.text((8,31),'NearRIGHT back; farLEFT lands/loads',font=font,fill='#536978');off=np.array(crop[:2])
for side,col in [('far','#a27038'),('near','#3c7c9f')]:
 ps=[np.array(g[k])-off for k in ['soft_H_'+side,'new_landing_softK_'+side,'real_ankle_proxy_'+side]];d.line([tuple(p)for p in ps],fill=col,width=2)
 for j,(x,y)in enumerate(ps):
  rad=7 if j<2 else 10;d.ellipse((x-rad,y-rad,x+rad,y+rad),outline=col,width=2)
  if j==2:d.line((x-14,y,x+14,y),fill=col,width=2);d.line((x,y-14,x,y+14),fill=col,width=2)
d.line((100,772,495,772),fill='#33858e',width=2);d.text((8,790),'Sole772; ankleY707.812/703.997. NOT bone measurement.',font=font,fill='#273d4b');npths['C']=R/'reference_native/C_same_A_full_volume_soft_chain_real_anchors_NOT_ART_540x810.png';C.save(npths['C'])
# Keep exact true five layers, and replay approvedA before adding technical ink.
order=['far_shoe_ankle_LANDED','far_complete_arm_jade_hand','body_head_blouse','near_complete_arm','near_shoe_ankle_SUPPORT_FIXED'];replay=Image.new('RGBA',(1672,1080));layers=[]
for k in order:
 p=S/'approved_layers'/('F090_'+k+'.png');q=R/'production_reference_layers'/p.name;shutil.copyfile(p,q);replay.alpha_composite(Image.open(p).convert('RGBA'));layers.append({'path':str(q.relative_to(R)),'approved_SHA256':sha(p),'new_SHA256':sha(q),'byte_identical':p.read_bytes()==q.read_bytes(),'no_new_transform':True})
assert np.array_equal(np.array(replay.crop(crop)),a0)
# Whole same256/135 geometry. Preserve original requestA real pixels literally;
# only originally transparent request pixels accept technical volume additions.
ar0=np.array(Image.open(I/'A_whole_canvas_256over135_PREPARED.png').convert('RGBA'));ar=np.array(A.resize((1024,1536),Image.Resampling.LANCZOS));ar[ar0[:,:,3]>0]=ar0[ar0[:,:,3]>0]
paths={'A':R/'inputs_1024x1536/A_real_fixed_layers_plus_volume_NOT_ART_PREPARED.png','B':R/'inputs_1024x1536/B_APPROVED_BYTE_IDENTICAL_PREPARED.png','C':R/'inputs_1024x1536/C_same_A_volume_soft_anchors_NOT_ART_PREPARED.png','D':R/'inputs_1024x1536/D_APPROVED_BYTE_IDENTICAL_PREPARED.png'};Image.fromarray(ar).save(paths['A']);C.resize((1024,1536),Image.Resampling.LANCZOS).save(paths['C'])
for k in ['B','D']:shutil.copyfile(I/f'{k}_whole_canvas_256over135_PREPARED.png',paths[k])
B=np.array(Image.open(npths['B']))>0;outside=vol&~B&~(a0[:,:,3]>0)
for k,z in [('approved_C_literal_technical_volume',vol),('volume_inserted_ONLY_IN_A_EMPTY',insert),('fixed_real_A_material_RGBA_UNCHANGED',a0[:,:,3]>0),('WHITE_approved_neutral',B)]:Image.fromarray(z.astype('uint8')*255).save(R/'masks'/f'{k}.png')
assert not outside.any();assert np.array_equal(a[a0[:,:,3]>0],a0[a0[:,:,3]>0]);assert np.array_equal(ar[ar0[:,:,3]>0],ar0[ar0[:,:,3]>0])
for tone,bg in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 sheet=Image.new('RGB',(2160,850),(235,240,245));d=ImageDraw.Draw(sheet)
 for j,k in enumerate(['A','B','C','D']):
  z=Image.new('RGBA',(540,810),bg);z.alpha_composite(Image.open(npths[k]).convert('RGBA'));sheet.paste(z.convert('RGB'),(j*540,35));d.text((j*540+8,7),k+' /540x810 / same whole256/135',font=font,fill='black')
 sheet.save(R/f'qa/four_corrected_inputs_{tone}.png')
checks={'status':'CORRECTED090_INPUT_PENDING_ROOT_ASTRA_NO_CALL','approved_source_commit':'aba2cbca','frame':90,'inclusive_hold':[90,94],'source_locked084_SHA256':g['source084_SHA'],'original_five_layers':layers,'five_layer_approvedA_RGBA_replay_changes':0,'A_native_and_request_original_visible_material_RGBA_changes':[0,0],'B_native_byte_identical':npths['B'].read_bytes()==(N/names['B']).read_bytes(),'D_native_byte_identical':npths['D'].read_bytes()==(N/names['D']).read_bytes(),'B_request_byte_identical':paths['B'].read_bytes()==(I/'B_whole_canvas_256over135_PREPARED.png').read_bytes(),'D_request_byte_identical':paths['D'].read_bytes()==(I/'D_whole_canvas_256over135_PREPARED.png').read_bytes(),'volume_source':'Literal approvedC complete waist/pelvis/two-leg technical palette pixels, same coordinates, nativeROI110..460/315..745. NO new limb form/fit.','volume_same_C_RGBA_changes':int(np.any(v[vol]!=c0[vol],axis=1).sum()),'volume_inserted_empty_pixels':int(insert.sum()),'volume_uncovered_outside_existing_white_pixels':int(outside.sum()),'C_same_A_plus_soft_chains_actual_anchors':True,'B_white_pixels':int(B.sum()),'inherited_guard_intersections':g['guard_intersections'],'inherited_alpha0guard_pixels':g['guard_alpha0_pixels'],'inherited_approved_affines':{'body':g['body_affine'],'arms':g['whole_arm_affines'],'nearfoot':g['near_whole_foot_source_and_target_SHA256'],'farfoot':g['far_original079_single_transform']},'actual_feet':g['feet'],'actual_ankles':{'near':g['real_ankle_proxy_near'],'far':g['real_ankle_proxy_far']},'soft_HK_only':{k:g[k]for k in ['soft_H_near','soft_H_far','new_landing_softK_near','new_landing_softK_far']},'crop_native':crop,'native_size':[540,810],'request_size':[1024,1536],'whole_forward':256/135,'unique_inverse':135/256,'mapping':'native=tool*135/256+[1080,250], entire canvas. No bodyfit, partscale or shoe moves. Original requestA actual material RGBA retained; technical additions only in its empty area.','failed090_RAW_read':False,'old084_trouser_pose_prompted':False,'inputs':[{'letter':k,'path':str(paths[k].relative_to(R)),'sha256':sha(paths[k]),'size':list(Image.open(paths[k]).size)}for k in ['A','B','C','D']],'new_calls':0}
def box(z):
 ys,xs=np.where(z)
 return {'local_bbox_halfopen':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'crop_margins_L_T_R_B':[int(xs.min()),int(ys.min()),540-int(xs.max()+1),810-int(ys.max()+1)]}
checks['literal_volume_bounds']=box(vol)
checks['inherited_real_material_and_white_bounds']=g['bounds_and_crop']
checks['literal_volume_source_no_resize_or_reposition']=True
checks['volume_internal_text_holes_filled_by_original_C_RGBA_not_new_RGB']=True
checks['source_snapshot_SHA256']={z['path']:z['sha256']for z in json.loads((S/'snapshot_manifest.json').read_text())['files']}
(R/'geometry/preparation_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
prompt='''Edit image A as a cropped restoration on exactly this1024x1536 shoulder/blouse-to-feet canvas. Keep its real blouse, complete arms/hands/jade and BOTH original shoe/ankle positions exactly fixed. The head is outside this crop: do not add a head, zoom out, recenter or fit a whole figure. A now supplies the approved FULL waist/pelvis/two-leg TECHNICAL VOLUME in the former empty trousers area. Its technical colors/lines are NOT ART: replace them with original navy clothing. B is the unchanged editing-region reference. C is the SAME A with soft joint chains and actual shoe anchors, not measured bones. D is unchanged original057/062 fabric/ink/color only.
Complete ONE coherent natural waist, pelvis and BOTH whole navy trouser legs along this full-volume direction into the TWO ALREADY PLACED TRUE ANKLES. F090 is double support transferring load toward the far anatomical LEFT leg at IMAGE-RIGHT. The near anatomical RIGHT leg remains behind at the original IMAGE-LEFT support shoe. Preserve both actual shoe x-ranges and sole baseline. Never widen the step, move or redraw feet, stretch a limb to a newly generated shoe, or add another shoe. Preserve full thigh, knee-back and calf volume with natural slight settling, coherent crotch and near-front/far-back overlap. A new foreground shin may naturally occlude the far rear shoe; never cut a shoe-shaped hole through trousers. Join continuously below the real blouse and into both real ankles, without transparent seams, narrow bridges or extraction cuts. Only small permitted sleeve connections may change. Match D's locked navy, shadow and ink. Return the same cropped transparent composition without technical colors, labels, guides, extra head, hand, foot or following state.'''
(R/'requests/prompt_DRAFT_NOT_FROZEN_NOT_CALLED.txt').write_text(prompt+'\n');(R/'requests/arguments_PREPARED_NOT_CALLED.json').write_text(json.dumps({'prompt':prompt,'referenced_image_paths':[str(paths[k])for k in ['A','B','C','D']],'transparent_background':True},indent=2)+'\n')
(R/'README.md').write_text('''# Corrected F090 complete-volume input gate — NO CALL

Approvedaba2cbca inputs only. Five true body/arm/shoe layers and540x810 crop remain unchanged. B/D native and1024 request PNGs are byte-identical. Five layers replay originalA exactly. Failed090 raw or incorrect generated feet/legs are NEVER read or used.

A now carries literal approvedC full waist/pelvis/two-leg technical volume at the SAME coordinates in its former empty area. No new body/leg shape or shoe adjustment. All original real material RGBA in native/request A remain unchanged. C is the SAME A plus soft chains and true shoe/ankle anchors. A/C are expressly NOT_ART technical guides; complete navy trousers still require genuine native drawing.

NearRIGHT image-left whole shoe remains source support position, sole1022; farLEFT image-right lands to take load, same1022sole. Actual ankleYs957.811814/953.996829 remain unequal. Body beat and whole arms exactly approved090; no legacy absolute bone anchors added. Nativecrop1080,250,1620,1060; whole256/135→1024x1536, unique inverse135/256+1080,250. No per-limb scaling/bodyfit.

Only prepared A/B/C/D enter draft request. Archives are evidence only, not extra prompt images. Input only, NO GENERATION; pending root/Astra actual four-image and prompt review. No other state prepared.
''')
print(json.dumps({'inputs':checks['inputs'],'five_layers_exact':True,'B_D_exact':[checks['B_request_byte_identical'],checks['D_request_byte_identical']],'volume_insert_pixels':int(insert.sum()),'outsidewhite':int(outside.sum())},indent=2))
