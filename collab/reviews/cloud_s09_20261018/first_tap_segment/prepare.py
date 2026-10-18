#!/usr/bin/env python3
"""Source-pixel prepositions and technical references, never substitute drawing."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from scipy.ndimage import binary_fill_holes,binary_closing,binary_dilation

ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
for d in ['reference','masks','qa','requests','originals','candidate']:(ROOT/d).mkdir(exist_ok=True)
source=BASE/'pre_tap_segment/clothing_semantic_review/continuous_contour_delivery/candidate/F031_raw_clothing_and_contours_for_final_lock.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)=='4b59c62485cf382c3e2d411de3c8ca9fb4edee622dad31b41946362889d44da7'
mother=Image.open(source).convert('RGBA');a=np.array(mother);W,H=mother.size
lock=json.loads((BASE/'switch_segment/locked/F000_lock.json').read_text())
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17)

def polygon(points):
    m=Image.new('L',mother.size);ImageDraw.Draw(m).polygon(points,fill=255);return m

# The oblique wrist cut is proximal to the complete knuckles/fingers. The crop is
# only an extraction boundary: no independent hand/prop fitting or scaling.
rigid=Image.new('L',mother.size);rd=ImageDraw.Draw(rigid)
rd.rectangle((1060,245,1210,674),fill=255)
rd.polygon([(1016,480),(1080,386),(1187,378),(1200,510),(1088,543),(1052,558),(1008,520)],fill=255)
rigid.save(ROOT/'masks/rigid_whole_torch_and_grip_source.png')
layer=Image.fromarray(np.where((np.array(rigid)>0)[:,:,None],a,0).astype(np.uint8))
layer.save(ROOT/'reference/F031_rigid_whole_torch_and_grip.png')
base=a.copy();base[np.array(rigid)>0]=0
near_domain=polygon([(704,626),(753,630),(830,674),(1008,455),(1040,440),(1100,505),
                     (1070,576),(883,764),(842,784),(798,778),(698,708)])
# Cuff root remains original. The complete near arm remains visible in source
# and reference; editable skin starts just distal to the cuff.
protected_root=polygon([(645,603),(748,604),(758,631),(727,641),(705,658),(688,685),(694,715),(639,720)])
domain=np.array(near_domain)>0
domain &= ~(np.array(protected_root)>0)
yy,xx=np.indices(domain.shape)
# Protect actual hair/neck/collar pixels without freezing the empty space where
# the new forearm must articulate. A historical rectangular guard also covered
# the old arm and cannot be reused as a semantic head mask.
head_roi=((xx<940)&(yy<600))|((xx<1001)&(yy<516))
head_actual=Image.fromarray(((a[:,:,3]>0)&head_roi).astype(np.uint8)*255).filter(ImageFilter.MaxFilter(5))
head_actual.save(ROOT/'masks/actual_head_neck_collar_guard.png')
domain &= ~(np.array(head_actual)>0)
# The farther sleeve/flounce is visible behind the old near forearm well above
# y680. Freeze its actual yellow material, enclosed white dots/fold ink and a
# two-pixel contour guard; the old broad receiving-arm rectangle misses this.
far_cuff_roi=(xx>=940)&(xx<=1030)&(yy>=590)&(yy<=692)
yellow=(a[:,:,0]>180)&(a[:,:,1]>100)&(a[:,:,2]<160)&(a[:,:,3]>32)
far_cuff=binary_fill_holes(binary_closing(yellow&far_cuff_roi,iterations=2))
far_cuff=binary_dilation(far_cuff,iterations=2)
Image.fromarray(far_cuff.astype(np.uint8)*255).save(ROOT/'masks/actual_far_sleeve_cuff_guard.png')
domain &= ~far_cuff

def moved(im,dy):
    out=Image.new(im.mode,im.size);out.paste(im,(0,dy));return out

states=[]
for frame,dy in [(37,-32),(42,59)]:
    move_layer=moved(layer,dy);move_mask=np.array(moved(rigid,dy))>0
    # Composite transparent padding over the stationary palm. Replacing the
    # entire extraction rectangle would wrongly erase its fingertips at042.
    # Only the tiny touching antialias edges may mix; opaque prop pixels stay exact.
    prep=Image.alpha_composite(Image.fromarray(base),move_layer)
    prep.save(ROOT/f'reference/F{frame:03d}_rigid_preposition_NOT_ART.png')
    # Include vacated original grip/prop area so it can be cleared, but never
    # permit the receiving arm/palm, head, sleeve root, or new rigid block.
    editable=domain|((np.array(rigid)>0)&~move_mask)
    editable[0:350]=False
    yy,xx=np.indices(editable.shape)
    receiving=(xx>=925)&(yy>=680)
    editable &= ~receiving
    editable &= ~move_mask
    Image.fromarray(editable.astype(np.uint8)*255).save(ROOT/f'masks/F{frame:03d}_near_arm_and_vacated_domain.png')
    Image.fromarray(move_mask.astype(np.uint8)*255).save(ROOT/f'masks/F{frame:03d}_rigid_destination_guard.png')
    # Technical display is deliberately labelled, with construction proxies
    # distinguished from anatomical measurements.
    bg=Image.new('RGBA',mother.size,(105,112,121,255));bg.alpha_composite(prep)
    q=bg.crop((630,350,1240,850)).convert('RGB');d=ImageDraw.Draw(q)
    overlay=Image.new('RGBA',q.size);od=ImageDraw.Draw(overlay)
    em=Image.fromarray(editable.astype(np.uint8)*65).crop((630,350,1240,850))
    red=Image.new('RGBA',q.size,(255,30,70,0));red.putalpha(em);q=Image.alpha_composite(q.convert('RGBA'),red).convert('RGB');d=ImageDraw.Draw(q)
    d.text((6,5),f'F{frame:03d} 技术预摆，非画稿 · 整手／整筒dy={dy}raw · 红区局修',font=font,fill='white')
    q.save(ROOT/f'qa/F{frame:03d}_actual_preposition_and_domain.png')
    state={'frame':frame,'status':'SOURCE_PIXEL_PREPOSITION_NOT_DRAWING',
      'rigid_translation_native':[0,dy],'scale':1,'rotation_degrees':0,'warp':False,
      'axis_length_native':float(np.linalg.norm(np.array([1135,278])-np.array([1134,654]))),
      'axis_length_registered':376.00132978488256*lock['registration']['scale'],
      'full_cap_diameter_native_manual':83,'near_arm_edit_pixels':int(editable.sum()),
      'receiving_palm_frozen':True,'head_gaze_clothing_outside_arm_domain_frozen':True}
    states.append(state)

# Exact opaque-contour check across the whole rear cap, not only its center.
rows=[]
for x in range(1085,1185):
    cap=np.flatnonzero(a[599:675,x,3]>128);palm=np.flatnonzero(a[695:790,x,3]>128)
    if len(cap) and len(palm):
        c=int(cap[-1]+599);p=int(palm[0]+695)
        rows.append({'x':x,'cap_last_alpha128_y':c,'palm_first_alpha128_y':p,
            'F031_clear_integer_rows':p-c-1,'F037_clear_integer_rows':p-c-1+32,
            'F042_clear_integer_rows_after_dy59':p-c-1-59})
assert min(r['F042_clear_integer_rows_after_dy59'] for r in rows)==0
assert min(r['F037_clear_integer_rows'] for r in rows)==91
assert all(r['F042_clear_integer_rows_after_dy59']>=0 for r in rows)
(ROOT/'reference/full_cap_palm_contour_rows.json').write_text(json.dumps(rows,indent=2)+'\n')

sheet=Image.new('RGB',(1240,610),(240,243,246));sd=ImageDraw.Draw(sheet)
sd.text((10,8),'实际完整尾盖／掌缘参考 · 031锁母，037／042仅原像素预摆，非完成图',font=font,fill='#223344')
for col,(frame,path) in enumerate([(31,source),(37,ROOT/'reference/F037_rigid_preposition_NOT_ART.png'),(42,ROOT/'reference/F042_rigid_preposition_NOT_ART.png')]):
    im=Image.open(path).convert('RGBA');bg=Image.new('RGBA',im.size,(105,112,121,255));bg.alpha_composite(im)
    crop=bg.crop((1078,594,1228,798)).resize((375,510),Image.Resampling.NEAREST)
    sheet.paste(crop.convert('RGB'),(15+col*410,66))
    sd.text((15+col*410,38),f'F{frame:03d} '+('实际锁母' if frame==31 else f'整体dy={-32 if frame==37 else 59}raw'),font=font,fill='#223344')
sheet.save(ROOT/'qa/actual_tailcap_palm_triplet.png')

record={'status':'F031_LOCKED_PREPARING_F037_THEN_F042','authority':'Astra explicit relayed whole-pose F031 lock and dispatch037→042; current parent instruction, no fresh lock needed for approved motion',
 'mother_commit':'78a980dff69601083580a1df819789954f6d8947','mother_path':str(source.relative_to(BASE)),
 'mother_sha256':sha(source),'native_size':[W,H],'registration':lock['registration'],
 'states':states,'contact_refinement':{'old_dy62':'manual outer-edge estimate, superseded by actual full-cap/palm contour scan',
   'new_dy59': 'first adjacent alpha128 contour pixels, 0 opaque overlap; AA contact remains to inspect at final actual image',
   'old_palm_y722':'approximate center proxy, actual top varies across palm',
   'minimum_native_clear_rows_F031':59,'minimum_native_clear_rows_F037':91,
   'minimum_native_clear_rows_F042':0,'new_pose_or_scale_design':False},
 'native_calls_this_preparation':0,'S09_own_native_calls_total_before_new_sequence':12,
 'F037_native_calls':0,'F042_native_calls':0,'in_flight':False}
(ROOT/'reference/approved_mother_and_targets.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
prompt='''Edit the FIRST transparent1672x941 drawing ONLY inside the WHITE areas of the SECOND binary mask. BLACK pixels are locked. The third image is the accepted previous drawing for visual continuity, not the new hand position. This is F037, the small upward anticipation before tapping a flashlight tailcap on the open left palm.

In the first image, the COMPLETE original red-and-silver flashlight and the COMPLETE right gripping hand have already been rigidly translated UP32pixels with NO resizing, rotation, distortion, or redraw. Keep those exact current pixels, all fingers, whole lamp head, switch and complete rear cap untouched. They are black-mask protected. Do not generate a second flashlight or second right hand. The exposed old hand/prop area must remain transparent where there is no forearm or clothing.

Draw a natural continuous RIGHT near arm from the same yellow puff-sleeve/cuff at image-left, through the visible bent elbow in front of her chest, to the new raised original right wrist at image-right. The whole arm must be anatomically connected: one shoulder, one upper arm, one elbow, one forearm and one wrist. Maintain the child's existing arm thickness, proportions and soft cel-shaded skin. This is a small arm articulation, not a straight translated limb. Keep the sleeve/cuff root anchored. The elbow shifts slightly right/up as the wrist lifts; maintain a bent elbow and smooth wrist/hand connection. Restore only the tiny newly exposed yellow dress area under the old forearm, matching continuous yellow cloth, original white dots and fold lines; no pasted rectangle, cut dot, skin remnant or detached cuff. Do not change the dress outside the white near-arm/vacated area.

The far LEFT arm and open receiving palm remain completely frozen in place. The flashlight rear cap is still visibly suspended above the palm, with a larger air gap than the previous image. There is NO contact yet. The face, gaze toward the flashlight, expression, hair, neck, collar, body, skirt, dress outer contour and both sleeve roots remain exactly unchanged. No light, beam, glow, text or mask/guide graphics. Return a single transparent drawing on the same canvas, with this local arm-continuity repair only.'''
(ROOT/'requests/F037_call01_prompt.txt').write_text(prompt+'\n')
args={'prompt':prompt,'referenced_image_paths':[str(ROOT/'reference/F037_rigid_preposition_NOT_ART.png'),str(ROOT/'masks/F037_near_arm_and_vacated_domain.png'),str(source)],'transparent_background':True}
(ROOT/'requests/F037_call01_arguments.json').write_text(json.dumps(args,ensure_ascii=False,indent=2)+'\n')
freeze={'status':'PREPARED_NOT_EXECUTED','arguments_sha256':sha(ROOT/'requests/F037_call01_arguments.json'),
 'inputs':[{'path':p,'sha256':sha(Path(p))} for p in args['referenced_image_paths']],
 'prompt_sha256':sha(ROOT/'requests/F037_call01_prompt.txt'),'native_calls':0}
(ROOT/'requests/F037_input_freeze.json').write_text(json.dumps(freeze,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(record,ensure_ascii=False))
