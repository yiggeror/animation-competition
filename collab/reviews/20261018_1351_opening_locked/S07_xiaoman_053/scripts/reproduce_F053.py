"""Rebuild F053 from one retained tool output; no generation, no external paths."""
from pathlib import Path
from PIL import Image, ImageChops
import json, numpy as np, hashlib
R=Path(__file__).resolve().parents[1]
(R/'candidates').mkdir(exist_ok=True)
def im(p,mode='RGBA'): return Image.open(R/p).convert(mode)
a=im('sources/F049_glance_grandma.png'); p=im('reference/F053_prepose_rgba.png'); raw=im('originals/F053_call015.png')
j=json.loads((R/'geometry/F053_arm_registration.json').read_text()); A=np.array(j['matrix_rowvector']); t=np.array(j['translation']); inv=np.linalg.inv(A); o=-t@inv
raw.putalpha(ImageChops.multiply(raw.getchannel('A'),im('masks/F053_v3_raw_arm_extract.png','L')))
reg=raw.convert('RGBa').transform(raw.size,Image.Transform.AFFINE,(inv[0,0],inv[1,0],o[0],inv[0,1],inv[1,1],o[1]),Image.Resampling.BICUBIC).convert('RGBA')
arm=im('masks/F053_v3_registered_arm_allowed.png','L'); q=Image.composite(reg,p,arm)
q=Image.composite(a,q,im('masks/F053_v4_main_puff_restore.png','L'))
# Underfill only existing seam changes. Never alpha-over an unchanged original edge.
changed=Image.fromarray(np.any(np.array(q)!=np.array(a),axis=2).astype('uint8')*255)
u=ImageChops.multiply(im('masks/F053_v6_puff_underfill.png','L'),changed)
q=Image.composite(Image.alpha_composite(a,q),q,u)
effective=ImageChops.lighter(arm,im('masks/preposition_allowed.png','L'))
q=Image.composite(q,a,effective)
effective.save(R/'masks/F053_v7_effective_allowed.png'); q.save(R/'candidates/F053_v7_rest_registered.png')
print(hashlib.sha256((R/'candidates/F053_v7_rest_registered.png').read_bytes()).hexdigest())
