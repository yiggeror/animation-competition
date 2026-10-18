from pathlib import Path
from PIL import Image
import json,hashlib
R=Path(__file__).parent;base=Image.open(R/'inputs/F036_from_F037_pose_scaffold.png').convert('RGBA');raw=Image.open(R/'raw/call04_F036_expression.png').convert('RGBA').resize((430,410),Image.Resampling.LANCZOS);layer=base.copy();layer.paste(raw,(620,430));mask=Image.open(R/'masks/F036_expression_neck_repair_mask.png').convert('L');out=Image.composite(layer,base,mask);p=R/'qa/S05a_F036_reproduced.png';p.parent.mkdir(exist_ok=True);out.save(p);sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha==json.loads((R/'F036_LOCK.json').read_text())['sha256'];print(sha)
