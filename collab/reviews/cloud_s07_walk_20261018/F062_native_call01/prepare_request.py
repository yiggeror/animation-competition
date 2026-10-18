#!/usr/bin/env python3
"""Freeze approved062 inputs; transparent canvas padding only, no drawn pixels."""
from pathlib import Path
import hashlib,json
from PIL import Image
R=Path(__file__).resolve().parent
B=R.parent
V=B/'next3_preflight_61sol/hip_calibrated_062_v4'
for d in ['inputs','requests','originals','candidate','qa','masks']:(R/d).mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(V/'reference/F062_hip_calibrated_source_pixels_NOT_ART.png')=='05588ef8914feafd6f75f3eb52a5d4548d9aed3a1cb152041712a29ecc5fa874'
assert sha(V/'masks/F062_crop_WHITE_EDIT_PENDING.png')=='a687fd6e1e69f78687843523f9bfc0b9aaa976ed0612061794082b7e703b0a21'
# 25 transparent/black columns on each side make an exact2:3 canvas.
# Original470x780 approved source and mask remain byte-equivalent inside pad.
target=Image.open(V/'reference/F062_crop_RGBA_NOT_ART.png').convert('RGBA')
mask=Image.open(V/'masks/F062_crop_WHITE_EDIT_PENDING.png').convert('L')
guide=Image.open(V/'qa/F062_calibrated_chain_and_actual_support.png').convert('RGB').crop((650,280,1120,1060))
for n,z,mode,bg in [('target',target,'RGBA',(0,0,0,0)),('WHITE_EDIT',mask,'L',0),('pose_guide_NOT_ART',guide,'RGB',(211,220,228))]:
 p=Image.new(mode,(520,780),bg);p.paste(z,(25,0));p.save(R/'inputs'/f'F062_{n}_padded520x780.png')
prompt='''Edit image1 into one finished local animation drawing. Image1 is a520x780 transparent crop containing the approved source-pixel preposition for F062, with25 transparent padding columns at each side. Image2 is the exact WHITE-EDIT/BLACK-KEEP operation mask. Image3 shows the same crop with cyan near-leg and brown far-leg construction guides only. Image4 is the locked F057 character artwork for original colors, cloth volume, clean line style and proportions only; its old walking pose is not the target.

Return the SAME520x780 crop framing and transparent background. Preserve the positions and full geometry of every black-locked material: both whole actual shoes and bare ankles, both real hands including the single green jade bangle, the bare arms except their small sleeve connection zones, and all existing blue blouse with white flowers except the small sleeve outlets. Do not pan, zoom, mirror, change camera, move a foot, stretch a limb, relight or recolor. The head is outside this crop: do not invent a head. No floor or shadow is to be painted.

This right-facing elderly grandmother is in a walking passing pose. The foreground near leg is the weight-bearing leg. Its original complete black cloth shoe and white sole remain planted flat at the lower-left of this crop, sole bottom y742. The far leg is behind it: the far knee advances to screen-right and bends back toward the lifted far ankle and far shoe. That shoe remains raised, exactly where shown, not moved to the floor. Respect depth: the whole near trouser leg occludes the hidden portions of the far leg and shoe. Do not let an invisible far-shoe silhouette carve a notch in the foreground navy cloth.

REDRAW THE COMPLETE CONNECTED NAVY TROUSER VOLUME inside the large white area, from the waist and hip volume immediately beneath the unchanged blouse hem, through BOTH thighs, knees, shin volumes and trouser cuffs. The existing angular cloth pieces are technical placeholders, not real cut seams or anatomy. Close the floating horizontal waist gap, the cut-through knee hole, the pointed triangular wedge and sliced cloth silhouettes. Draw one naturally rounded pelvis under the blouse, connected continuously into two believable trouser legs. The hips are lowered slightly inside the trousers while the head and blouse keep their original beat: do not make a floating waistband or a stretched long thigh. The tiny near-knee bend and far knee-back turn must read through complete cloth volumes, contours and restrained folds, not a geometric joint line.

For position only, image3 cyan construction points in this padded crop are near hip(261.8558,323.2865), knee(268.2756,492.8738), fixed actual ankle(208.8562,677.8118). Preserve those projected lengths and the planted shoe. The brown far construction chain is a manual volume guide behind the near leg, not an exposed outline or extra limb. Keep the far shoe/ankle exactly fixed at its shown location. Remove all cyan/brown guides from the finished drawing.

At both cuffs, draw real navy cloth meeting the existing bare ankle with a clean continuous silhouette. In particular, remove the isolated obsolete black L above the far ankle. Only that old cut-edge fragment is released; preserve the actual shoe outline, ankle skin and original antialiasing. At both small white sleeve outlet areas, connect the original blouse cloth naturally into each unchanged real upper arm. Keep one arm on each side, no duplicated cuff, hand, wrist or bracelet. Keep the existing small white flower sizes, blue cloth fill and sleeve shape.

Small disconnected white patches away from the body mark obsolete floating source fragments to ERASE TO TRANSPARENCY, not objects to invent. Clear the old detached slivers and ragged ink along the trouser side and outside the real arms. Keep true anatomical contours and their antialiasing. Do not fill the whole mask as a silhouette. Use the exact original navy, blue, warm skin and neutral shoe colors from image4; preserve dark crease shadows as shadows. Produce a clean finished2D animation drawing with natural consistent linework, no patch seams, spikes, translucent old outlines, motion blur, background, labels, bones, guide dots or text. The ONLY new artwork is the continuous trousers and small sleeve connections in the white operation domain; all black-locked materials remain aligned to image1.'''
paths=[R/'inputs/F062_target_padded520x780.png',R/'inputs/F062_WHITE_EDIT_padded520x780.png',R/'inputs/F062_pose_guide_NOT_ART_padded520x780.png',B/'F057_semantic_color_ankle/candidate/F057_semantic_color_and_ankle_PENDING.png']
args={'prompt':prompt,'referenced_image_paths':[str(p) for p in paths],'transparent_background':True}
(R/'requests/prompt.txt').write_text(prompt+'\n')
(R/'requests/arguments.json').write_text(json.dumps(args,ensure_ascii=False,indent=2)+'\n')
freeze={'approved_input_commit':'10908f920bec7989b78558c1b248f93acae2e087','approved_source_proposal_sha256':sha(V/'reference/F062_hip_calibrated_source_pixels_NOT_ART.png'),'approved_crop_mask_sha256':sha(V/'masks/F062_crop_WHITE_EDIT_PENDING.png'),'only_padding':{'original_crop':[650,280,1120,1060],'original_size':[470,780],'pad_left_right':[25,25],'padded_size':[520,780],'resampling':False},'inputs':[{'path':str(p),'sha256':sha(p),'size':list(Image.open(p).size)}for p in paths],'prompt_sha256':sha(R/'requests/prompt.txt'),'calls_authorized_this_gate':1,'calls_sent':0,'new_output_count':0,'remaining_gate':'Actual062 shape/ground-contact review before068/073.'}
(R/'requests/input_freeze.json').write_text(json.dumps(freeze,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(freeze,ensure_ascii=False,indent=2))
