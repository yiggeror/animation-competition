#!/usr/bin/env python3
"""Archive native image bytes; composite explicitly selected native drawing pixels."""
from pathlib import Path
import base64,json,hashlib,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
state=sys.argv[1]
ret=json.loads((ROOT/f'requests/{state}_call01_raw_return.json').read_text())
raw=ROOT/f'originals/{state}_call01_raw.png';raw.write_bytes(base64.b64decode(ret['image_url'].split(',',1)[1]))
native=Image.open(raw).convert('RGBA')
source=BASE/'switch_segment/candidates/d04_raw_locked.png' if state=='d05' else ROOT/f'candidates/{"d05" if state=="d06" else "d06"}_raw_locked.png'
prev=Image.open(source).convert('RGBA');pad=[prev.width-native.width,prev.height-native.height]
assert all(0<=v<=2 for v in pad),(native.size,prev.size)
edit=Image.new('RGBA',prev.size);edit.paste(native,(0,0))
mask=Image.new('L',prev.size,0);d=ImageDraw.Draw(mask)
if state=='d05':
    d.polygon([(923,561),(949,540),(985,544),(1028,548),(1060,565),(1058,593),(1018,606),(972,613),(945,620),(925,600)],fill=255)
    mask=mask.filter(ImageFilter.GaussianBlur(1.25))
else:raise SystemExit('Inspect actual native artwork and select the next explicit mask before compositing.')
candidate=Image.composite(edit,prev,mask)
mask.save(ROOT/f'masks/{state}_native_patch_mask.png');candidate.save(ROOT/f'candidates/{state}_raw_locked.png')
ma=np.array(mask);pa=np.array(prev);ca=np.array(candidate)
assert np.array_equal(pa[ma==0],ca[ma==0])
lock=json.loads((BASE/'switch_segment/locked/F000_lock.json').read_text())
reg=candidate.transform((1536,864),Image.Transform.AFFINE,tuple(lock['registration']['inverse_pillow_affine']),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
reg.save(ROOT/f'candidates/{state}_registered.png')
reg.crop((280,80,1304,656)).resize((1280,720),Image.Resampling.LANCZOS).save(ROOT/f'qa/{state}_final_1280x720.png')
box=(900,528,1078,625);pair=Image.new('RGB',((box[2]-box[0])*6,(box[3]-box[1])*3),(228,233,237))
for i,im in enumerate([prev,candidate]):
    part=im.crop(box);bg=Image.new('RGBA',part.size,(228,233,237,255));bg.alpha_composite(part);pair.paste(bg.resize((part.width*3,part.height*3),Image.Resampling.NEAREST).convert('RGB'),(i*part.width*3,0))
pair.save(ROOT/f'qa/{state}_before_after.png')
report={'state':state,'source':str(source.relative_to(BASE)),'native_original':str(raw.relative_to(ROOT)),
 'sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'native_size':list(native.size),'transparent_padding_right_bottom':pad,
 'mask':f'masks/{state}_native_patch_mask.png','outside_mask_zero_pixel_changes':0,'changed_pixels':int(np.any(pa!=ca,axis=2).sum()),
 'native_pixels_rescaled':False,'registration':'same locked F000 global transform','method':'only actual native generated drawing pixels inside mask; no code-drawn anatomy',
 'review_status':'ACTUAL_IMAGE_REVIEW_REQUIRED'}
(ROOT/f'qa/{state}_patch_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
