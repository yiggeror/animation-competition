#!/usr/bin/env python3
"""Preserve native edits and composite explicit local native patches onto locked art."""
from pathlib import Path
import sys,json,base64,hashlib
from PIL import Image,ImageDraw,ImageFilter
import numpy as np
ROOT=Path(__file__).resolve().parent
state=sys.argv[1]
source={'d02':'locked/F000_raw_alpha_clean.png','d03':'candidates/d02_raw_locked.png','d04':'candidates/d03_raw_locked.png'}[state]
ret=json.loads((ROOT/f'requests/{state}_call01_raw_return.json').read_text())
out=ROOT/f'originals/{state}_call01_raw.png';out.write_bytes(base64.b64decode(ret['image_url'].split(',',1)[1]))
im=Image.open(out).convert('RGBA');prev=Image.open(ROOT/source).convert('RGBA')
native_size=im.size
assert prev.size==(1672,941)
pad=[prev.width-im.width,prev.height-im.height]
assert all(0<=x<=2 for x in pad),('unexpected native canvas change',im.size,prev.size)
if im.size!=prev.size:
    padded=Image.new('RGBA',prev.size,(0,0,0,0));padded.paste(im,(0,0));im=padded
# Every changed pixel comes from the actual native image. The rest remains exact.
mask=Image.new('L',im.size,0);d=ImageDraw.Draw(mask)
if state=='d02':
    poly=[(928,560),(950,545),(981,549),(1008,558),(1020,577),(1007,596),(975,600),(949,612),(929,599)]
    d.polygon(poly,fill=255)
elif state=='d03':
    poly=[(923,561),(949,540),(985,544),(1028,548),(1060,565),(1058,593),(1018,606),(972,613),(945,620),(925,600)]
    d.polygon(poly,fill=255)
else:
    # Brows only; the eyes/pupils/head/hair/ears/mouth/neck remain locked.
    d.ellipse((740,255,865,307),fill=255)
    d.ellipse((882,255,958,305),fill=255)
mask=mask.filter(ImageFilter.GaussianBlur(1.25))
mask.save(ROOT/f'masks/{state}_native_patch_mask.png')
candidate=Image.composite(im,prev,mask)
candidate.save(ROOT/f'candidates/{state}_raw_locked.png')
pa=np.array(prev);ca=np.array(candidate);ma=np.array(mask)
assert np.array_equal(pa[ma==0],ca[ma==0])
reg=json.loads((ROOT/'locked/F000_lock.json').read_text())['registration']
registered=candidate.transform((1536,864),Image.Transform.AFFINE,tuple(reg['inverse_pillow_affine']),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
registered.save(ROOT/f'candidates/{state}_registered.png')
crop=(280,80,1304,656)
registered.crop(crop).resize((1280,720),Image.Resampling.LANCZOS).save(ROOT/f'qa/{state}_final_1280x720.png')
box=(900,528,1078,625) if state!='d04' else (730,250,963,393)
parts=[]
for image in [prev,candidate]:
    part=image.crop(box);bg=Image.new('RGBA',part.size,(218,228,234,255));bg.alpha_composite(part);parts.append(bg.resize((part.width*3,part.height*3),Image.Resampling.NEAREST))
sheet=Image.new('RGB',(parts[0].width*2,parts[0].height),(245,245,245));sheet.paste(parts[0],(0,0));sheet.paste(parts[1],(parts[0].width,0));sheet.save(ROOT/f'qa/{state}_before_after.png')
report={'state':state,'native_call':'image_gen.imagegen','source':source,'raw_return':f'requests/{state}_call01_raw_return.json','original':str(out.relative_to(ROOT)),
        'native_size':list(native_size),'transparent_padding_right_bottom':pad,'native_pixels_rescaled':False,
        'original_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'mask':f'masks/{state}_native_patch_mask.png','mask_feather_sigma':1.25,
        'raw_candidate':f'candidates/{state}_raw_locked.png','registered_candidate':f'candidates/{state}_registered.png',
        'outside_mask_zero_pixel_changes':0,'changed_pixels':int(np.any(pa!=ca,axis=2).sum()),
        'method':'local patch pixels entirely from native image edit; outside mask exact previous accepted pixels; no code-generated hand or local anatomy warp',
        'status':'AUTHOR_ACTUAL_IMAGE_REVIEW_REQUIRED'}
(ROOT/f'qa/{state}_patch_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
