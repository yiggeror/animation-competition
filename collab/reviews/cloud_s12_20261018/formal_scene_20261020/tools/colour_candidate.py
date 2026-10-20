"""Review-only F102 blue-cloth albedo candidate; never imported by production.

The approved source stays byte-identical. Pointwise hue selection preserves
alpha, geometry, white floral marks, skin and dark ink. No generated pixels.
"""
from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[5]
OUT=ROOT/'collab/reviews/cloud_s12_20261018/formal_scene_20261020/colour_candidate'
OUT.mkdir(exist_ok=True)
SRC=ROOT/'assets/chars/g12/F102_BG_fcdf16037858.png'
im=Image.open(SRC).convert('RGBA'); a=np.asarray(im).copy()
hsv=np.asarray(im.convert('RGB').convert('HSV')).astype(float)/255
h,s,v=hsv.transpose(2,0,1)
blue=(h>.56)&(h<.72)&(np.indices(h.shape)[0]<900)&(a[:,:,3]>0)
weight=blue*np.clip((s-.40)/.35,0,1)*np.clip((v-.30)/.20,0,1)
target=hsv.copy();target[:,:,1]=s*.45;target[:,:,2]=np.minimum(240/255,v*1.10+20/255)
rgb=np.asarray(Image.fromarray(np.round(target*255).astype('uint8'),'HSV').convert('RGB'))
a[:,:,:3]=np.round(a[:,:,:3]*(1-weight[:,:,None])+rgb*weight[:,:,None]).astype('uint8')
candidate=Image.fromarray(a);candidate.save(OUT/'F102_BG_blue_cloth_candidate.png')
before=np.asarray(im);changed=np.any(before[:,:,:3]!=a[:,:,:3],axis=2)
assert np.array_equal(before[:,:,3],a[:,:,3])
assert not changed[np.max(before[:,:,:3],axis=2)<65].any()
panel=Image.new('RGB',(960,720),'#ddd');draw=ImageDraw.Draw(panel)
for i,(label,picture) in enumerate([('F074 approved source',Image.open(ROOT/'assets/chars/g12'/next(s['bg'] for s in json.loads((ROOT/'assets/chars/g12/sequence.json').read_text())['states'] if s['key']==74))),('F102 approved source',im),('F102 blue-cloth candidate',candidate)]):
 picture=picture.convert('RGBA');picture.thumbnail((320,660));panel.paste(picture,(i*320,35),picture);draw.text((i*320+5,10),label,fill='black')
panel.save(OUT/'source_before_after.jpg')
evidence={'cause':'Approved unlit source PNG palette differs; every production state shares the same single renderPaint lighting path. No duplicate light multiplication or row-specific colour-space path.',
 'source_SHA256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'candidate_SHA256':hashlib.sha256((OUT/'F102_BG_blue_cloth_candidate.png').read_bytes()).hexdigest(),
 'candidate_only':True,'main_movie_uses_approved_original':True,'alpha_identical':True,'dark_ink_below_RGBmax65_unchanged':True,'changed_RGB_pixels':int(changed.sum()),
 'scope':'One F102 semantic cloth candidate only. Not applied to sequence or other poses; requires colour-direction selection before any coordinated palette pass.'}
(OUT/'readback.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(evidence,ensure_ascii=False))
