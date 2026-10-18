#!/usr/bin/env python3
"""Technical suggestion only: repair newly exposed far-sleeve connection."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation
O=Path(__file__).resolve().parent
im=Image.open(O/'F037_independent_original_pixels_PENDING.png').convert('RGBA')
def read(name):return np.array(Image.open(O/name))>0
protected=read('hard_protection_mask.png')
arm=read('arm_raw_dy30_mask.png')
# Only the material newly revealed between the arm and the original visible
# sleeve tip. A small amount of the already-returned exposed yellow material
# provides an internal joining margin. This is a mask, not a drawn contour.
roi=Image.new('L',im.size)
ImageDraw.Draw(roi).polygon([(990,599),(1008,591),(1021,600),(1018,618),(1003,632),(982,628),(983,613)],fill=255)
mask=(np.array(roi)>0)&~protected&~binary_dilation(arm,iterations=1)
Image.fromarray(mask.astype(np.uint8)*255).save(O/'PROPOSED_far_sleeve_connection_WHITE_EDIT.png')
box=(950,560,1040,700)
im.crop(box).save(O/'PROPOSED_far_sleeve_connection_crop_RGBA.png')
Image.fromarray(mask.astype(np.uint8)*255).crop(box).save(O/'PROPOSED_far_sleeve_connection_crop_WHITE_EDIT.png')
bg=Image.new('RGBA',im.size,(105,112,121,255));bg.alpha_composite(im)
red=Image.new('RGBA',im.size,(255,0,80,0));red.putalpha(Image.fromarray(mask.astype(np.uint8)*130));bg.alpha_composite(red)
bg.crop(box).resize((450,700),Image.Resampling.NEAREST).save(O/'PROPOSED_far_sleeve_connection_overlay.png')
result={'status':'TECHNICAL_MASK_SUGGESTION_ONLY_NO_CALL','white_pixels':int(mask.sum()),'near_arm_overlap':int((mask&arm).sum()),'hard_protection_overlap':int((mask&protected).sum()),'source_gap_sample_white':[bool(mask[y,x]) for x,y in [(1004,610),(1005,611),(1005,612),(1008,608)]],'crop_xyxy':list(box),'new_image_calls':0,'purpose':'Only complete the newly revealed yellow far-sleeve transition/contour. Entire adopted arm, locked gripping hand/prop and original visible sleeve material, marks/folds remain black. Parent must actually review mask and decide whether to request a native edit.'}
(O/'PROPOSED_connection_mask_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
