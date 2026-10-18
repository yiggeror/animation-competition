from pathlib import Path
from PIL import Image
import numpy as np,hashlib
R=Path(__file__).resolve().parent;O=R/'verification_replay';O.mkdir(exist_ok=True)
base=Image.open(R/'inputs/F052_from_locked_pose_scaffold.png').convert('RGBA');raw=Image.open(R/'root_call10/raw/call10_F052.png').convert('RGBA');layer=base.copy();layer.paste(raw.resize((430,415),Image.Resampling.LANCZOS),(620,420))
a=np.array(layer);ys=np.arange(a.shape[0],dtype=float);delta=np.clip((ys-680)/70,0,1)*12;sy=np.clip(ys-delta,0,len(ys)-1);lo=np.floor(sy).astype(int);hi=np.minimum(lo+1,len(ys)-1);w=(sy-lo)[:,None,None];layer=Image.fromarray(np.rint(a[lo]*(1-w)+a[hi]*w).astype(np.uint8))
out=Image.composite(layer,base,Image.open(R/'root_call10/review/v4_extended_jaw_mask.png').convert('L'));a=np.array(out);b=np.array(base)
for n in [5,6]:
 sel=np.array(Image.open(R/f'root_call10/review/v{n}_removed_fragments_mask.png').convert('L'))>0;a[sel]=b[sel]
p=O/'S05a_F052.png';Image.fromarray(a).save(p);h=hashlib.sha256(p.read_bytes()).hexdigest();assert h=='34cb6db38ac06310dcd6d83de31cc67fea6a86b0811da0afd318ad98036bc291';print(h)
