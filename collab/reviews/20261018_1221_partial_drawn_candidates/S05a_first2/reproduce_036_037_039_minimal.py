"""Minimal locked partial-batch reproduction. Writes qa/reproduced, never final/."""
from pathlib import Path
from PIL import Image
import json,hashlib
R=Path(__file__).parent;D=R/'qa/reproduced';D.mkdir(exist_ok=True)
for frame in [36,37,39]:
 if frame==36:
  base=Image.open(R/'inputs/F036_from_F037_pose_scaffold.png').convert('RGBA');raw=Image.open(R/'raw/call04_F036_expression.png').convert('RGBA').resize((430,410),Image.Resampling.LANCZOS);layer=base.copy();layer.paste(raw,(620,430));mask=Image.open(R/'masks/F036_expression_neck_repair_mask.png').convert('L')
 elif frame==37:
  base=Image.open(R/'inputs/F037_thumb_articulated_preplacement.png').convert('RGBA');raw=Image.open(R/'raw/call03_F037_thumb.png').convert('RGBA').resize((160,91),Image.Resampling.LANCZOS);under=Image.open(R/'inputs/F037_original_pixel_pose_scaffold.png').convert('RGBA').crop((640,850,800,941));under.alpha_composite(raw);layer=base.copy();layer.paste(under,(640,850));mask=Image.open(R/'masks/F037_thumb_articulation_repair_mask.png').convert('L')
 else:
  base=Image.open(R/'inputs/F039_from_F037_pose_scaffold.png').convert('RGBA');raw=Image.open(R/'raw/call05_F039_first_press.png').convert('RGBA').resize((390,501),Image.Resampling.LANCZOS);layer=base.copy();layer.paste(raw,(640,440));registered=layer.transform(base.size,Image.Transform.AFFINE,(1,0,-1.5,0,1,-14),Image.Resampling.BICUBIC);layer.paste(registered.crop((680,860,780,941)),(680,860));mask=Image.open(R/'masks/F039_first_press_local_mask.png').convert('L')
 out=Image.composite(layer,base,mask);dest=D/f'S05a_F{frame:03d}.png';out.save(dest);sha=hashlib.sha256(dest.read_bytes()).hexdigest();expected=json.loads((R/f'F{frame:03d}_LOCK.json').read_text())['sha256'];assert sha==expected,(frame,sha,expected);print(frame,sha)
