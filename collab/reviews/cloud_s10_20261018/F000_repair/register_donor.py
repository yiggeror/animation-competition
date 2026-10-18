"""Replay the frozen uniform donor registration; no new image request or optimization."""
from pathlib import Path
import json
from PIL import Image
P=Path(__file__).resolve().parent
z=json.loads((P/'provenance/cloth_donor_registration.json').read_text())
s=z['scale_donor_per_crop'];x=z['donor_offset_x'];y=z['donor_offset_y']
im=Image.open(P/'originals/cloth_call01_raw.png')
im.transform((1024,256),Image.Transform.AFFINE,(s,0,x,0,s,y),resample=Image.Resampling.BICUBIC).save(P/'prepared/cloth_donor_registered_crop.png')
print('Frozen local donor registration replayed; no original person pixels used from this output.')
