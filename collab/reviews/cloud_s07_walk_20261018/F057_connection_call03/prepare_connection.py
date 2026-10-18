#!/usr/bin/env python3
"""Freeze the authorized14deg scaffold and local connection crop/mask; no image request here."""
from pathlib import Path
import hashlib,json
import numpy as np
from scipy.ndimage import binary_dilation
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
for folder in ['reference','masks','requests','originals','candidate','qa']:(ROOT/folder).mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source_path=ROOT/'source_reference/angle_14_PREPOSITION_NOT_ART.png'
source=Image.open(source_path).convert('RGBA');a=np.array(source);size=source.size
assert size==(1672,1080)
assert sha(source_path)=='72b6d191185ef61a1e66f051912cf7ae4e7255a2153e30adb50594d0402bc909'
arm=np.array(Image.open(ROOT/'source_reference/angle14_sleeve_elbow_connection_domain_WHITE_REVIEW_ONLY.png'))>0
distal=np.array(Image.open(ROOT/'source_reference/angle14_distal_jade_hand_material_PROTECTED.png'))>0
distal=binary_dilation(distal,iterations=3)
prior=np.array(Image.open(BASE/'F057_local_repair/zero_call_pose_proposal/masks/proposed_narrow_connection_only_NOT_APPROVED.png'))>0
old_hard=np.array(Image.open(BASE/'F057_local_repair/masks/locked_head_body_near_right_arm.png'))>0
yy,xx=np.indices(a.shape[:2]);ankle=prior&(yy>=900)
# Reuse the complete original e93 trousers-root envelope BEFORE its now-withdrawn36deg
# distal-arm exclusion. The selected14deg hand has a different, separately locked footprint.
hip_image=Image.new('L',size)
ImageDraw.Draw(hip_image).polygon([(704,541),(878,541),(883,598),(708,598)],fill=255)
hip=np.array(hip_image)>0
# Keep the real shoe and ankle material exact. Only a vacant gap or adjacent blue trouser edge may change.
hsv=np.array(source.convert('RGB').convert('HSV'));blue_pants=(hsv[:,:,0]>=128)&(hsv[:,:,0]<=180)&(hsv[:,:,1]>40)
foot_box=(xx>=755)&(xx<=1000)&(yy>=930)
real_foot=(a[:,:,3]>0)&foot_box&~blue_pants
foot=binary_dilation(real_foot,iterations=2)
near_head_body=old_hard&~arm
allowed=arm|hip|ankle
final=allowed&~distal&~foot&~near_head_body
arm_final=final&arm;hip_final=final&hip;ankle_final=final&ankle
assert final.any() and arm_final.any() and hip_final.any() and ankle_final.any()
assert not (final&~allowed).any()
assert not (final&(distal|foot|near_head_body)).any()
for name,m in [('final_connection_only',final),('protected_complete_distal_jade_hand',distal),('protected_real_near_foot_and_ankle',foot),('protected_head_near_arm_and_body_except_allowed_far_connection',near_head_body)]:
    Image.fromarray((m*255).astype('uint8')).save(ROOT/f'masks/{name}.png')
# This crop excludes the complete head/face and includes all three independent repair sites.
crop=[560,300,1080,1045]
source.crop(crop).save(ROOT/'reference/call03_local_crop_rgba.png')
Image.fromarray((final*255).astype('uint8')).crop(crop).save(ROOT/'reference/call03_local_crop_mask_WHITE_EDIT.png')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
base=Image.new('RGBA',size,(221,226,231,255));base.alpha_composite(source)
ov=Image.new('RGBA',size,(209,42,129,0));ov.putalpha(Image.fromarray((final*115).astype('uint8')));base.alpha_composite(ov)
base.convert('RGB').save(ROOT/'qa/full_scaffold_final_mask_overlay.png')
sheet=Image.new('RGB',(1600,800),(241,244,247));draw=ImageDraw.Draw(sheet)
for col,(title,im) in enumerate([('14度原像素预摆／不是画稿',source),('最终白域／黑域保持',Image.open(ROOT/'masks/final_connection_only.png').convert('RGBA')),('完整语义连接与镯手净空',base)]):
    if col==1:panel=im.crop(crop).convert('RGB')
    else:
        bg=Image.new('RGBA',size,(221,226,231,255));bg.alpha_composite(im);panel=bg.crop(crop).convert('RGB')
    panel=panel.resize((520,745),Image.Resampling.NEAREST)
    sheet.paste(panel,(7+col*530,45));draw.text((12+col*530,12),title,font=font,fill='#26343d')
sheet.save(ROOT/'qa/final_local_crop_and_mask_review.png')
prompt='''Edit ONLY the three white connection regions in the supplied cropped RGBA artwork. Image 1 is the actual technical preposition to repair; image 2 is its exact white-edit/black-keep mask. This is one LOCAL SEAM CONNECTION edit, not a new person or new walking pose. Keep the 520x745 crop canvas and every black pixel aligned. Return transparent-background RGBA at the SAME crop framing; do not crop, zoom, translate, relight, mirror, rescale, or lengthen any limb.

This is a right-facing elderly grandmother in a blue blouse with small white flowers, navy trousers and black cloth shoes. Her near anatomical RIGHT arm is the bare-wrist arm on the LEFT side of this crop; it must remain completely unchanged. Her far anatomical LEFT arm is the jade-bangle arm on the RIGHT. The entire original distal green jade bangle, wrist, fingers, palm, hand silhouette and surrounding edge are BLACK-LOCKED. Preserve that original material exactly. Preserve the existing small step: all complete legs, knees, ankle horizontal separation, full shoes and sole ground contact are BLACK-LOCKED outside tiny seam holes. The head is outside this crop and must not be invented.

White region 1: connect the ACTUAL far sleeve outlet, adjoining narrow side-blouse cloth, upper arm, elbow and proximal forearm into a natural continuous piece. The whole far arm was rigidly rotated14degrees without changing bone lengths. Its existing wrist/hand pose is final. Remove cut-edge white scars and vacant ragged fragments along the inner proximal arm. Respect legitimate far-arm occlusion behind the blouse: do not draw an exposed elbow over the front of the blouse, do not start a second arm at the waist, and do not add a second sleeve, wrist, jade bangle or hand. Let continuous real skin and cloth edges join smoothly into the unchanged distal forearm just above the jade. Preserve the original skin flat fill and its gentle warm shadow separately; no brightening or yellow/orange tint drift. Keep the original blue blouse flower size, blue flat fill and darker fold shadows unchanged where existing pixels can be retained.

White region 2: reconnect only the tiny trousers-root/pelvis seam directly BELOW the unchanged blouse hem. Fill the transparent wedge and join the navy cloth naturally to the existing complete near and far thigh roots. Preserve both entire leg silhouettes, knee locations, lengths and walking depth. Do not lower or widen the pelvis, move feet, shift a shoe, stretch a thigh, or redraw the legs.

White region 3: connect only the small near trouser cuff-to-ankle vacancy. The shoe was relevelled around its real ankle after whole-leg rotation. Keep all original shoe, sole, ankle skin and foot material fixed; fill the local missing cloth/edge connection without changing cuff shape beyond the white region. The two existing shoe soles already share the correct ground. Do not add a cast shadow, ground, background, motion blur, outlines from the mask, labels, guide lines or any new object.

Use the same clean 2D animation linework and original material colors. Make the minimum natural local connection needed in white; do not replace every white pixel gratuitously. Everything black must remain source-identical, including the near bare arm, distal jade/hand, all intact trousers and both complete shoes. Return the repaired local crop only.'''
(ROOT/'requests/F057_call03_prompt.txt').write_text(prompt+'\n')
args={'prompt':prompt,'referenced_image_paths':[str((ROOT/'reference/call03_local_crop_rgba.png').resolve()),str((ROOT/'reference/call03_local_crop_mask_WHITE_EDIT.png').resolve())],'transparent_background':True}
(ROOT/'requests/F057_call03_arguments.json').write_text(json.dumps(args,ensure_ascii=False,indent=2)+'\n')
inputs=[{'path':p,'sha256':sha(Path(p))} for p in args['referenced_image_paths']]
(ROOT/'requests/F057_call03_inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
report={'status':'FINAL_CROP_MASK_PREPARED_PENDING_EXISTING_REVIEWER_NO_CALL_YET','fixed_source_commit':'56cb80c3dca135a1dbc6acde378433259590a183',
    'current_user_authorization':'Selected14deg and withdrew wrist623; allows this final crop/mask review by existing independent reviewer then one local connection request without another parent/user confirmation.',
    'source_sha256':sha(source_path),'crop_xyxy':crop,'crop_size':[520,745],
    'allowed_arm_envelope_pixels':int(arm.sum()),'final_arm_pixels':int(arm_final.sum()),'final_hip_pixels':int(hip_final.sum()),'final_ankle_pixels':int(ankle_final.sum()),'final_mask_pixels':int(final.sum()),
    'outside_allowed_pixels':int((final&~allowed).sum()),'distal_jade_hand_overlap':int((final&distal).sum()),'real_near_foot_ankle_overlap':int((final&foot).sum()),'head_near_arm_other_body_overlap':int((final&near_head_body).sum()),
    'hip_envelope_source':'same original e93 polygon704,541/878,541/883,598/708,598; withdrawn36deg distal-hand exclusion not inherited; current14deg distal hand remains fully protected',
    'old_36deg_guard_missing_gap_174_pixels_now_released':bool(final[566:576,847:869][a[566:576,847:869,3]<128].all()),
    'old_wrist623_withdrawn':True,'selected_wrist_world':[969.3215414625827,592.676829036375],
    'registration_unchanged':json.loads((ROOT/'source_reference/ANGLE_CHECKS.json').read_text())['registration_unchanged'],
    'step_geometry_source':'F057_local_repair/zero_call_pose_proposal/proposal_checks.json; same64horizontal and775real sole support; no new segment transforms',
    'new_calls_at_preparation':0,'S07_actual_calls_at_preparation':2,'other10_calls':0,'no_request_in_flight':True}
(ROOT/'preparation_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
