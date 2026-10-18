#!/usr/bin/env python3
"""F044x4 source-pixel recoil and whole-near-arm input. No generation or drawing."""
from pathlib import Path
import json,csv,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation,binary_closing,binary_fill_holes

R=Path(__file__).resolve().parent;T=R.parent;S=R/'sources'
for d in ['reference','masks','qa','requests']:(R/d).mkdir(exist_ok=True)
assert not (R/'requests/execution_state.json').exists(),'Preserve request inputs once a call starts.'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p42=T/'F042_contact_gate/astra_two_corridors_zero_call/candidate/F042_two_corridors_clean_PENDING_ASTRA.png'
p37=T/'whole_far_puff_zero_call/candidate/F037_whole_native_far_puff_PENDING.png'
assert sha(p42)=='52bb96f9796878bbb9c928ad80c5af6b5a0580ad9f9c651384446f0caadd3f8f'
assert sha(p37)=='68ce16f14f9ea53f2c43c2c53f984a6a713b612f6aef28ab369780cb768695c9'
im=Image.open(p42).convert('RGBA');a=np.array(im);m37=Image.open(p37).convert('RGBA');palmsource=np.array(m37);size=im.size;yy,xx=np.indices(a.shape[:2])
def mask(name):return np.array(Image.open(S/name).convert('L'))>0
def moved(z,dy):
    out=Image.new(z.mode,z.size);out.paste(z,(0,dy));return out
def polygon(points):
    z=Image.new('L',size);ImageDraw.Draw(z).polygon(points,fill=255);return np.array(z)>0
def capsule(points,radius):
    z=Image.new('L',size);d=ImageDraw.Draw(z);d.line(points,fill=255,width=radius*2+1)
    for x,y in points:d.ellipse((x-radius,y-radius,x+radius,y+radius),fill=255)
    return np.array(z)>0
reg=json.loads((S/'F042_preparation.json').read_text())['registration'];scale=reg['scale']
rows=list(csv.DictReader((S/'exposure.csv').open()));event=next(r for r in rows if r['id']=='d09')
assert int(event['start_frame_0'])==44 and int(event['hold'])==4 and int(event['end_frame_inclusive'])==47
dy=-48

# Mother042 is a flattened contact picture. Recover only the existing object
# AA at its old cap/palm intersection, using the authentic same-object layer.
pure31=Image.open(S/'F031_rigid_whole_torch_and_grip.png').convert('RGBA');pure42=np.array(moved(pure31,59))
unitmask=mask('F042_tight_actual_hand_torch_guard.png')
unit=a.copy();unit[~unitmask]=0
cap_AA=unitmask&(yy>=650)&(pure42[:,:,3]<=240)
cap_AA_changed=cap_AA&np.any(unit!=pure42,axis=2)
unit[cap_AA]=pure42[cap_AA]
oldlayer=Image.fromarray(unit);newlayer=moved(oldlayer,dy);n=np.array(newlayer)
newmaterial=n[:,:,3]>0
receiver=mask('F042_palm_source_guard.png')
contact_band=(xx>=1088)&(xx<=1162)&(yy>=703)&(yy<=728)
palm_recover=receiver&contact_band&np.any(a!=palmsource,axis=2)
assert not np.any(receiver&np.any(a!=palmsource,axis=2)&~contact_band)
base=a.copy();base[unitmask]=0
# Preserve the genuine receiving palm rather than either contact composite.
base[receiver]=palmsource[receiver]
base[newmaterial]=0
pre=Image.alpha_composite(Image.fromarray(base),newlayer);pa=np.array(pre)
oldlayer.save(R/'reference/F042_true_grip_torch_detached_SOURCE.png');newlayer.save(R/'reference/F044_rigid_hand_torch_up48_SOURCE.png')
prepath=R/'reference/F044_actual_source_preposition_NOT_ART.png';pre.save(prepath)

# Whole forearm/upper-arm articulation and vacated source silhouette are white.
# These center lines are only corridor estimates, not frozen anatomical joints.
oldarm=mask('F042_registered_complete_near_arm.png')
oldcorridor=capsule([(707,670),(848,712),(1037,596)],51)
future=capsule([(707,670),(850,688),(1037,548)],56)
source_hsv=np.array(im.convert('RGB').convert('HSV'))
skin=(source_hsv[:,:,0]<=28)&(source_hsv[:,:,1]>40)&(a[:,:,0]>155)&(a[:,:,0]>a[:,:,1].astype(int)+15)&(a[:,:,1]>a[:,:,2].astype(int)+12)&(a[:,:,2]>100)&(a[:,:,3]>20)
old_near_actual=(oldarm|oldcorridor)&skin&~receiver&~unitmask
old_near_outline=binary_dilation(old_near_actual,iterations=3)&(a[:,:,3]>0)

head=(a[:,:,3]>0)&(((yy<520)&(xx<1020))|((yy<575)&(xx<900)))
head&=~binary_dilation(old_near_actual,iterations=2)&~unitmask
near_ruffle=binary_fill_holes(mask('F042_actual_near_ruffle_guard.png'))&(a[:,:,3]>0)&~skin
# The previous physical cuff opening may contain newly accepted skin; it is
# not yellow ruffle and therefore must not freeze a stale arm edge.
old_near_actual&=~near_ruffle
farROI=polygon([(934,539),(1028,539),(1040,617),(1029,686),(932,707)])
yellow=(a[:,:,0]>180)&(a[:,:,1]>135)&(a[:,:,2]<100)&(a[:,:,3]>20)
far_material=binary_dilation(binary_fill_holes(binary_closing(yellow&farROI,iterations=2)),iterations=2)&farROI&(a[:,:,3]>0)
far_material&=~binary_dilation(old_near_actual,iterations=3)&~unitmask
# Actual far-arm material is protected only where it remains visible; a
# hidden back layer cannot lock the foreground near-arm drawing corridor.
far_arm_roi=polygon([(928,675),(1035,675),(1065,727),(1230,705),(1240,795),(1085,824),(1015,859),(964,855),(940,810),(921,753)])
far_visible=far_arm_roi&(a[:,:,3]>0)&~binary_dilation(old_near_actual,iterations=3)&~unitmask
far_visible&=~future
far_guard=far_material&~future
receiverguard=receiver.copy()
# Material only, no dilated transparent moat at the wrist extraction seam.
rigidguard=newmaterial.copy()
skirt_and_waist=(yy>=777)&(a[:,:,3]>0)
hard=head|near_ruffle|far_guard|far_visible|receiverguard|rigidguard|skirt_and_waist
vacated=unitmask&~newmaterial
edit=binary_dilation(oldarm|old_near_outline,iterations=8)|oldcorridor|future|vacated
edit|=polygon([(683,625),(790,611),(880,605),(998,480),(1088,479),(1112,610),(1020,700),(911,783),(824,792),(703,724),(671,691)])
edit&=~hard
crop=(620,240,1240,860);cropdomain=(xx>=crop[0])&(xx<crop[2])&(yy>=crop[1])&(yy<crop[3])
clipped_material=int((edit&~cropdomain&(pa[:,:,3]>20)).sum());assert clipped_material==0
edit&=cropdomain
guards={'head_neck_collar_actual':head,'near_ruffle_actual_material':near_ruffle,'far_puff_actual_visible':far_guard,'far_arm_actual_visible_except_new_foreground':far_visible,'fixed_receiver_palm_material':receiverguard,'rigid_grip_torch_actual_material':rigidguard,'waist_and_skirt_actual_material':skirt_and_waist}
for name,z in {**guards,'F044_complete_near_arm_vacated_WHITE_EDIT_PENDING':edit,'old_near_arm_actual_material':old_near_actual,'new_full_arm_corridor_GUIDE_ONLY':future,'cap_contact_AA_recovered_from_real_prop':cap_AA_changed,'fixed_palm_contact_AA_recovered_from037':palm_recover}.items():Image.fromarray(z.astype('uint8')*255).save(R/'masks'/f'{name}.png')
pre.crop(crop).save(R/'reference/F044_crop_RGBA_NOT_ART.png');Image.fromarray(edit.astype('uint8')*255).crop(crop).save(R/'masks/F044_crop_WHITE_EDIT_PENDING.png')

# Scan actual separated source layers; do not use a historical circle or plane.
cap=n[:,:,3];palm=palmsource[:,:,3];contours=[]
for x in range(1090,1178):
    cy=np.flatnonzero(cap[600:710,x]>=128);py=np.flatnonzero(palm[695:790,x]>=128)
    if len(cy)and len(py):
        cy=int(cy[-1]+600);py=int(py[0]+695);contours.append({'x':x,'tailcap_alpha128_last_y':cy,'original_palm_alpha128_first_y':py,'clear_native_rows':py-cy-1})
assert contours and min(r['clear_native_rows']for r in contours)>0
(R/'reference/actual_tailcap_palm_gap_rows.json').write_text(json.dumps(contours,indent=2)+'\n')

font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17)
def bg(z,col):
    q=Image.new('RGBA',size,col);q.alpha_composite(z);return q
for nm,color in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
    sheet=Image.new('RGB',(1860,655),(238,242,246));d=ImageDraw.Draw(sheet)
    for i,(label,z)in enumerate([('锁042真实触掌母源',im),('044整手筒上48／预摆非画稿',pre),('完整近臂真绘白域／待输入审',pre)]):
        q=bg(z,color)
        if i==2:
            wash=Image.new('RGBA',size,(220,35,120,0));wash.putalpha(Image.fromarray(edit.astype('uint8')*105));q.alpha_composite(wash)
        sheet.paste(q.crop(crop).convert('RGB'),(i*620,35));d.text((i*620+5,8),label,font=font,fill='#26343e')
    sheet.save(R/f'qa/F042_F044_actual_preposition_and_whole_arm_domain_{nm}.png')
    q=bg(pre,color);q.convert('RGB').save(R/f'qa/F044_full_{nm}.png')
    detail=Image.new('RGB',(900,650),(238,242,246));dd=ImageDraw.Draw(detail)
    for i,(label,z)in enumerate([('042扁平触掌',im),('044真实图层已离掌',pre)]):
        patch=bg(z,color).crop((1070,575,1220,785)).resize((450,630),Image.Resampling.NEAREST);detail.paste(patch.convert('RGB'),(i*450,25));dd.text((i*450+4,3),label,font=font,fill='#26343e')
    detail.save(R/f'qa/actual_tailcap_fixed_palm_separation_{nm}.png')
    aa=Image.new('RGB',(1150,540),(238,242,246));dd=ImageDraw.Draw(aa)
    for i,(label,z)in enumerate([('母042接触复合AA',im),('真实分层预摆',pre)]):
        q=bg(z,color).crop((1085,650,1170,740)).resize((510,540),Image.Resampling.NEAREST);aa.paste(q.convert('RGB'),(i*575,25));dd.text((i*575+3,3),label,font=font,fill='#26343e')
    aa.save(R/f'qa/contact_AA_unflattening_actual_{nm}.png')

prompt='''Edit ONLY the WHITE areas of image2 on image1. Image1 is a620x620 transparent context crop of the fixed F044 source-pixel preposition, not a finished arm drawing. Keep exactly this620x620 canvas and framing. Image3 is the locked previous F042 full character, for continuity only. Return the same transparent local crop. No zoom, reframing, pose duplication, light or background.

F044 is the FIRST small rebound AFTER the flashlight tailcap hit the stationary open LEFT palm. The complete original RIGHT gripping hand and flashlight in image1 have ALREADY moved UP48native pixels, leaving a true positive gap of about30registered pixels over the unchanged receiving palm. Do not move or rotate the hand/torch again, do not change its length, diameter, grip, fingers, thumb, switch, lens or tailcap. Keep switch OFF and light dark. The cap is now visibly separated from the palm; it must not touch fingers or carry a skin fragment. The entire genuine original receiving palm and far lower arm stay fixed.

Draw the COMPLETE near RIGHT arm from its original image-left yellow ruffle opening, through one natural bent elbow and whole forearm into the newly raised original wrist. The full WHITE old/new arm silhouette is one redraw, not a wrist-seam patch. The visible old lower arm shape in white is obsolete. Replace the full contour and its interior shading together, keep the child's accepted upper-arm/forearm proportions, volume and thickness; bend naturally rather than stretching, splitting or translating the old limb. One connected sleeve opening, upper arm, elbow, forearm and wrist; no second cuff arc, severed wrist, narrow bridge, extra elbow or hanging old ink. Leave the BLACK original real yellow ruffle material and black ruffle contour intact, joining its inside naturally with skin. Do not retain the artificial source-piece cut edge.

Restore the newly exposed small yellow dress and white-dot/fold material behind the old near arm; clear the vacated old flashlight/arm outlines and isolated AA slivers. The far round yellow puff sleeve and far arm are the original BACK layer. Keep their genuine visible source material outside white; the new near arm is foreground and may cover the proximal back sleeve naturally, with no rear-sleeve ink crossing in front of skin. Do not invent an old pointed fork, floating cuff or detached cloth. Keep the actual left forearm and whole open palm untouched and attached.

Preserve all BLACK pixels exactly: the whole original gripping fingers/hand/torch, stationary receiver palm, genuine sleeve materials, head, face, gaze, hair, white collar, body and skirt outside the arm/vacated-cloth domain. Match separate original flat skin and warm cel shadow; no recolor, white seam, bright patch, blurred border or changed dots. No captions, guide lines, mask colors, motion blur or new objects. This request is ONLY F044; noF048 or second tap.'''
(R/'requests/prompt_PREPARED_NOT_CALLED.txt').write_text(prompt+'\n')
args={'prompt':prompt,'referenced_image_paths':[str(R/'reference/F044_crop_RGBA_NOT_ART.png'),str(R/'masks/F044_crop_WHITE_EDIT_PENDING.png'),str(p42)],'transparent_background':True}
(R/'requests/arguments_PREPARED_NOT_CALLED.json').write_text(json.dumps(args,ensure_ascii=False,indent=2)+'\n')
overlaps={name:int((edit&z).sum())for name,z in guards.items()}
report={'status':'F044_ONLY_SOURCE_PIXEL_PREFLIGHT_PENDING_AUTHOR_INPUT_REVIEW_NO_CALL','F042_mother':str(p42),'F042_mother_sha256':sha(p42),'F037_true_palm_source':str(p37),'F037_true_palm_sha256':sha(p37),'F031_same_real_prop_layer_snapshot_sha256':sha(S/'F031_rigid_whole_torch_and_grip.png'),'source_snapshot_manifest':'sources/snapshot_manifest.json','frame':44,'hold':4,'inclusive_frames':[44,47],'registered_gap_intent':30,'integer_rigid_translation_native':[0,dy],'registered_translation_magnitude':-dy*scale,'rigid_scale':1,'rigid_rotation':0,'new_resampling':False,'native_size':list(size),'crop_xyxy':crop,'crop_size':[620,620],'registration_unchanged':reg,'reference_png_sha256':sha(prepath),'white_pixels':int(edit.sum()),'guard_intersections':overlaps,'old_actual_near_arm_alpha20_left_outside_edit_except_fixed_material':int((old_near_actual&~edit&~hard).sum()),'old_actual_near_arm_pixels_in_guard':int((old_near_actual&hard).sum()),'actual_source_layers_minimum_clear_native_rows':min(r['clear_native_rows']for r in contours),'minimum_clear_registered_px':min(r['clear_native_rows']for r in contours)*scale,'tail_palm_opaque_overlap':int(((cap>=128)&receiver&(palmsource[:,:,3]>=128)).sum()),'fixed_receiving_palm_vs_true037_RGBA_changes':int(np.any(pa[receiver]!=palmsource[receiver],axis=1).sum()),'new_rigid_unit_foreground_vs_source_layer_RGBA_changes':int(np.any(pa[newmaterial]!=n[newmaterial],axis=1).sum()),'cap_AA_unflattening_changed_pixels':int(cap_AA_changed.sum()),'palm_AA_unflattening_changed_pixels':int(palm_recover.sum()),'source042_true_cap_core_alpha240_vs_same031_RGBA_changes':int(np.any(a[(pure42[:,:,3]>240)&(yy>=650)]!=pure42[(pure42[:,:,3]>240)&(yy>=650)],axis=1).sum()),'outside_rigid_removal_new_unit_and_palm_recovery_RGBA_changes':int(np.any(pa[~(unitmask|newmaterial|receiver)]!=a[~(unitmask|newmaterial|receiver)],axis=1).sum()),'out_of_crop_material20_edit_clipping':clipped_material,'new_image_calls':0,'F048_F052_F056_unopened':True,'technical_limits':['Source pixels only: old arm remains a temporary silhouette inside full white redraw domain, not an accepted rebound pose.','Tailcap/palm contact AA is separated from existing authentic object/palm layers, not painted or alpha-guessed. Mother042 remains sole base for all other material.','Manual root/elbow/wrist corridor centerpoints are not frozen anatomical joints or measured bone lengths.','Physical material plus its real AA is protected; hidden far-layer alpha never locks a foreground near-arm corridor.','Actual author input-mask review required before the single native044 request; resulting real arm and042x2→044x4 exposure require later actual-image review.']}
assert all(v==0 for v in overlaps.values())
assert report['fixed_receiving_palm_vs_true037_RGBA_changes']==0
assert report['source042_true_cap_core_alpha240_vs_same031_RGBA_changes']==0
assert report['outside_rigid_removal_new_unit_and_palm_recovery_RGBA_changes']==0
(R/'preparation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
freeze={'status':'PREPARED_ONLY_PENDING_INPUT_REVIEW_NOT_EXECUTED','arguments_sha256':sha(R/'requests/arguments_PREPARED_NOT_CALLED.json'),'prompt_sha256':sha(R/'requests/prompt_PREPARED_NOT_CALLED.txt'),'inputs':[{'path':p,'sha256':sha(p)}for p in args['referenced_image_paths']],'source_mother_sha256':sha(p42),'new_image_calls':0}
(R/'requests/input_freeze_PENDING_REVIEW.json').write_text(json.dumps(freeze,ensure_ascii=False,indent=2)+'\n')
(R/'README.md').write_text('F044×4仅准备输入，未生成、未提交、未通过作者输入门。\n\n唯一母042已锁52bb96f9…；整件手筒上48native≈30.2267注册像素，原左掌固定，保原注册。曝光F044–047；048/052/056未开。\n\n母图接触边已扁平混合掌和尾盖AA，故仅在真实接触边回取同一031原手筒AA及037原位纯掌底层，来源/差异和mask逐项记录，不把掌皮随筒带走。其余母042材质不改。\n\n预摆仍显示旧近臂，完整近臂/旧臂腾空/旧筒透明区白域要原生重新绘制，不可把源提取断边当关节轮廓。真实手筒、近袖ruffle、头领、固定掌及远袖当前可见材料黑保；未来近臂可遮远袖，不用完整隐藏远层锁前景。\n\n建议调用输入为620×620同框crop＋白mask＋锁042全身上下文。requests文件特标PREPARED_NOT_CALLED，原作者实看后才决定执行。无生成/048派生。\n')
print(json.dumps({k:report[k]for k in ['status','reference_png_sha256','white_pixels','actual_source_layers_minimum_clear_native_rows','minimum_clear_registered_px','cap_AA_unflattening_changed_pixels','palm_AA_unflattening_changed_pixels','old_actual_near_arm_pixels_in_guard','new_rigid_unit_foreground_vs_source_layer_RGBA_changes']},ensure_ascii=False))
