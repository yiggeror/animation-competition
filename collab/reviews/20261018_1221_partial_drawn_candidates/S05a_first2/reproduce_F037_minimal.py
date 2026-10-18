"""Reproduce the accepted F037 from persisted local repair inputs, no model call.
Run from any cwd: python reproduce_F037_minimal.py
Writes qa/S05a_F037_reproduced.png and checks the locked SHA256.
Required inputs relative to this script: the four paths named below plus F037_LOCK.json.
The preplacement input contains the previously generated call01/call02 material and
explicit original-pixel placement. Raw call01/call02 are provenance, not runtime dependencies.
"""
from pathlib import Path
from PIL import Image
import json,hashlib
R=Path(__file__).resolve().parent
base=Image.open(R/'inputs/F037_thumb_articulated_preplacement.png').convert('RGBA')
raw=Image.open(R/'raw/call03_F037_thumb.png').convert('RGBA')
crop=raw.resize((160,91),Image.Resampling.LANCZOS)
underlay=Image.open(R/'inputs/F037_original_pixel_pose_scaffold.png').convert('RGBA').crop((640,850,800,941))
underlay.alpha_composite(crop)
layer=base.copy();layer.paste(underlay,(640,850))
mask=Image.open(R/'masks/F037_thumb_articulation_repair_mask.png').convert('L')
out=Image.composite(layer,base,mask)
(R/'qa').mkdir(exist_ok=True)
p=R/'qa/S05a_F037_reproduced.png';out.save(p)
got=hashlib.sha256(p.read_bytes()).hexdigest();expected=json.loads((R/'F037_LOCK.json').read_text())['sha256']
assert got==expected,(got,expected)
print('Reproduced SHA256:',got)
