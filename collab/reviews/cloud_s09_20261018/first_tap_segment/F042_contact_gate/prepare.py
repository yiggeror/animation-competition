#!/usr/bin/env python3
"""F042 actual-source rigid hand/torch contact and full near-arm semantic edit preparation."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation,binary_closing,binary_fill_holes
R=Path(__file__).resolve().parent;T=R.parent;B=T.parent
assert not (R/'requests/execution_state.json').exists(),'Request already started: preserve frozen inputs.'
for n in ['reference','masks','qa','requests','originals','candidate','exposure']:(R/n).mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p37=T/'whole_far_puff_zero_call/candidate/F037_whole_native_far_puff_PENDING.png';p31=B/'pre_tap_segment/clothing_semantic_review/continuous_contour_delivery/candidate/F031_raw_clothing_and_contours_for_final_lock.png'
assert sha(p37)=='68ce16f14f9ea53f2c43c2c53f984a6a713b612f6aef28ab369780cb768695c9';assert sha(p31)=='4b59c62485cf382c3e2d411de3c8ca9fb4edee622dad31b41946362889d44da7'
m37=Image.open(p37).convert('RGBA');a=np.array(m37);size=m37.size;yy,xx=np.indices(a.shape[:2])
def moved(im,dy):
 z=Image.new(im.mode,im.size);z.paste(im,(0,dy));return z
def poly(points):
 z=Image.new('L',size);ImageDraw.Draw(z).polygon(points,fill=255);return np.array(z)>0
def capsule(points,r):
 z=Image.new('L',size);d=ImageDraw.Draw(z);d.line(points,fill=255,width=2*r+1)
 for x,y in points:d.ellipse((x-r,y-r,x+r,y+r),fill=255)
 return np.array(z)>0
rigid31=Image.open(T/'reference/F031_rigid_whole_torch_and_grip.png').convert('RGBA')
roi31=Image.open(T/'masks/rigid_whole_torch_and_grip_source.png').convert('L')
oldroi=np.array(moved(roi31,-32))>0;oldlayer=np.array(moved(rigid31,-32));oldmaterial=oldlayer[:,:,3]>240
assert np.array_equal(a[oldmaterial],oldlayer[oldmaterial]),'Locked037 actual opaque hand/prop differs from original rigid layer.'
newlayer=moved(rigid31,59);n=np.array(newlayer);newmaterial=n[:,:,3]>0
base=a.copy();base[oldroi]=0
pre=Image.alpha_composite(Image.fromarray(base),newlayer);pre.save(R/'reference/F042_hand_torch_contact_PREPOSITION_NOT_ART.png')
# This exact prop/hand transform is already contact-positioned. A native arm
# redraw must join it; the generator must not perform another downward move.
near37=np.array(Image.open(T/'independent_recompose/arm_raw_dy30_mask.png'))>0
nearroot=poly([(639,600),(751,600),(758,631),(727,641),(705,658),(688,685),(694,715),(639,720)])
head=((yy<520)&(xx<1005))|((yy<575)&(xx<900))
head &= (a[:,:,3]>0)
# Actual old foreground arm is never part of the head, despite shared ROI.
head &= ~binary_dilation(near37,iterations=2)&~oldroi
# Preserve the receiver as the stationary back layer. New near arm can cover
# only its proximal upper-arm/sleeve overlap; the palm and lower forearm stay fixed.
receiver=((xx>=1010)&(yy>=690)&(yy<850))|((xx>=925)&(yy>=748)&(yy<880))
head=binary_dilation(head,iterations=1)
rigidguard=binary_dilation(newmaterial,iterations=1)
rootguard=nearroot&(a[:,:,3]>0)
# Full old and possible new arm, plus naturally revealed dress/old-arm contour.
future=capsule([(715,671),(815,774),(1048,572)],49)
editable=binary_dilation(near37,iterations=9)|future|(oldroi&~newmaterial)
editable|=poly([(720,635),(795,630),(875,640),(1005,453),(1080,462),(1110,617),(1040,676),(915,790),(845,812),(775,783),(697,711)])
# Sleeve/ruffle roots and original round far puff remain source material;
# only the region potentially covered by the foreground arm is released.
far_roi=poly([(938,540),(1018,540),(1042,600),(1030,681),(938,700)])
yellow=(a[:,:,0]>180)&(a[:,:,1]>140)&(a[:,:,2]<100)&(a[:,:,3]>20)
far_puff=binary_dilation(binary_fill_holes(binary_closing(far_roi&yellow,iterations=2)),iterations=2)&(a[:,:,3]>0)
# Old foreground skin in this ROI is not sleeve material.
far_puff &= ~binary_dilation(near37,iterations=2)&~oldroi
far_puff_guard=far_puff&~future
hard=head|rootguard|receiver|rigidguard|far_puff_guard
editable &= ~hard
editable &= (yy>=220)&(yy<813)&(xx>=680)&(xx<1225)
for name,z in [('near_arm_and_vacated_WHITE_EDIT',editable),('whole_rigid_hand_torch',rigidguard),('head_neck_collar',head),('near_cuff_root',rootguard),('stable_receiver_palm_lower_forearm',receiver),('far_puff_visible_outside_new_arm',far_puff_guard),('far_puff_complete_source_material',far_puff),('new_near_arm_corridor_REVIEW_ONLY',future)]:Image.fromarray(z.astype(np.uint8)*255).save(R/'masks'/f'{name}.png')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17)
sheet=Image.new('RGB',(1830,600),(239,243,246));d=ImageDraw.Draw(sheet)
for i,(title,im) in enumerate([('已锁037 / 真正前态',m37),('042手筒预摆 / 非画稿',pre),('042完整近臂修绘范围 / 待审',pre)]):
 bg=Image.new('RGBA',size,(213,222,229,255));bg.alpha_composite(im)
 if i==2:
  wash=Image.new('RGBA',size,(202,45,118,0));wash.putalpha(Image.fromarray(editable.astype(np.uint8)*105));bg.alpha_composite(wash)
 sheet.paste(bg.crop((630,290,1240,855)).convert('RGB'),(i*610,35));d.text((i*610+5,8),title,font=font,fill='#26343e')
sheet.save(R/'qa/037_042_actual_preposition_and_complete_domain.png')
contact=Image.new('RGB',(1050,620),(239,243,246));d=ImageDraw.Draw(contact)
for i,(title,im) in enumerate([('037已锁 / 空隙',m37),('042预摆 / 实体轮廓相邻',pre)]):
 bg=Image.new('RGBA',size,(102,112,123,255));bg.alpha_composite(im);q=bg.crop((1070,580,1220,790)).resize((450,630),Image.Resampling.NEAREST)
 contact.paste(q.convert('RGB'),(i*525,35));d.text((i*525+5,8),title,font=font,fill='#26343e')
contact.save(R/'qa/actual_cap_palm_contact_PREPOSITION.png')
# Independent source-contour contact scan, retaining the cap and palm as separate source layers.
cap=np.array(newlayer)[:,:,3];palm=a[:,:,3];rows=[]
for x in range(1090,1178):
 cy=np.flatnonzero(cap[650:740,x]>=128);py=np.flatnonzero(palm[695:790,x]>=128)
 if len(cy) and len(py):
  c=int(cy[-1]+650);p=int(py[0]+695);rows.append({'x':x,'cap_last_alpha128_y':c,'palm_first_alpha128_y':p,'clear_rows':p-c-1})
assert min(r['clear_rows'] for r in rows)==0;assert all(r['clear_rows']>=0 for r in rows)
(R/'reference/contact_contour_rows.json').write_text(json.dumps(rows,indent=2)+'\n')
lock=json.loads((B/'switch_segment/locked/F000_lock.json').read_text())
prompt='''Edit the FIRST transparent1672x941 drawing ONLY inside the WHITE areas of the SECOND binary mask. BLACK pixels stay aligned and unchanged. The third image is the actual accepted previous F037 drawing for continuity. Return one transparent drawing on exactly the same1672x941 canvas. Do not crop, zoom, mirror, move the body, relight, or add any background.

This is F042, the FIRST contact of a small red flashlight rear cap against the girl's stationary open LEFT palm. The COMPLETE original flashlight and complete RIGHT gripping hand have ALREADY been translated straight DOWN91pixels from F037 in the first image. The tailcap is already tangent to the actual palm pad. Preserve that entire original grip, all fingers, flashlight lens/head/body/tailcap, axis, diameter and length exactly where they are. Do not move, tilt, shorten, redraw, bend, widen or lower the flashlight again. No second hand or second flashlight. Keep the open receiving palm and far lower forearm absolutely stationary; no palm movement, finger movement, penetration or interleaved outlines. This is the contact instant, not recoil, switch pressing or light turning on. No beam or glow.

DRAW the complete near RIGHT arm naturally from the anchored yellow puff-sleeve cuff on image LEFT, through one bent elbow in front of her chest, into the new lowered original right wrist on image RIGHT. Keep the child's existing arm thickness, upper-arm and forearm proportions and gentle cel shading. Bend and lower the elbow naturally as the held wrist comes down; do not translate the whole old arm, stretch it, shorten a forearm, leave an old skin strip, or create a second elbow. The existing raised arm in the editable region is obsolete: replace its entire contour and remove all old slivers, detached outlines or cut-edge skin remnants. Restore only the newly revealed small yellow dress area behind it, matching the original yellow fill, small white dots and fold linework. Make the wrist connection smooth without altering any original gripping fingers.

The far LEFT round puff sleeve, lower ruffle, upper arm, forearm and palm remain the original stable back layer. Preserve the rounded far puff silhouette and material wherever visible. The new near arm is the foreground and may naturally hide part of that sleeve: do not make a sleeve outline cross in front of the near arm, do not turn its round puff into an old pointed fork, and do not invent a floating cuff, hollow shoulder or extra arm. Preserve the original lower ruffle to far arm connection wherever it remains visible. Both actual hands remain attached to their respective arms.

Keep her face, downward eyes toward the flashlight/palm, expression, hair, neck, white collar, body, near cuff root, skirt and all other clothing unchanged. Use the exact original skin flat fill and warm shadow separately; no white seams, yellow tint drift, dark pasted patch or altered flower-dot sizes. No labels, mask colors, motion blur, guide lines or extra objects. Return the local arm-articulation repair in the full transparent canvas only.'''
(R/'requests/prompt.txt').write_text(prompt+'\n')
args={'prompt':prompt,'referenced_image_paths':[str(R/'reference/F042_hand_torch_contact_PREPOSITION_NOT_ART.png'),str(R/'masks/near_arm_and_vacated_WHITE_EDIT.png'),str(p37)],'transparent_background':True}
(R/'requests/arguments.json').write_text(json.dumps(args,ensure_ascii=False,indent=2)+'\n')
report={'status':'F042_PREPARED_PENDING_ACTUAL_AUTHOR_AND_61SOL_REVIEW_NO_REQUEST','F037_authority_commit':'a1d7f2756bcf1b5d1b13ea7a53fba34fa6fb5cfb','F037_source':str(p37),'F037_sha256':sha(p37),'F031_source':str(p31),'F031_sha256':sha(p31),'near_arm_previous_mask_source':str(T/'independent_recompose/arm_raw_dy30_mask.png'),'rigid_translation_from_037_raw':[0,91],'rigid_translation_from_031_raw':[0,59],'rigid_scale':1,'rigid_rotation':0,'rigid_warp':False,'original_opaque_F037_grip_torch_matches_031_moved':True,'minimum_contact_clear_integer_rows':0,'opaque_contact_overlap_pixels':0,'contact_adjacent_columns':[r['x'] for r in rows if r['clear_rows']==0],'registration':lock['registration'],'editable_pixels':int(editable.sum()),'new_native_calls':0,'prior_S09_requests':15,'prior_S09_originals':14,'F042_requests':0,'F044_F048_unopened':True,'remaining_gate':'Actual native near-arm anatomy, smooth whole round-sleeve layering, rigid source preservation and cap/palm tangent image, then actual037x5→042x2 exposure. The preposition is not art and numeric contour adjacency does not pass actual contact.'}
(R/'preparation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
freeze={'status':'PREPARED_NOT_EXECUTED','arguments_sha256':sha(R/'requests/arguments.json'),'prompt_sha256':sha(R/'requests/prompt.txt'),'inputs':[{'path':p,'sha256':sha(p)} for p in args['referenced_image_paths']],'mother_F031_sha256':sha(p31),'rigid_source_sha256':sha(T/'reference/F031_rigid_whole_torch_and_grip.png')}
(R/'requests/input_freeze.json').write_text(json.dumps(freeze,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['status','F037_sha256','rigid_translation_from_037_raw','minimum_contact_clear_integer_rows','contact_adjacent_columns','editable_pixels','new_native_calls']},ensure_ascii=False))
