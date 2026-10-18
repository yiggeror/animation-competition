from PIL import Image,ImageDraw,ImageFilter
from pathlib import Path
import numpy as np,json,hashlib
R=Path('/workspace/scratch/f060b5601755/astra_s05a_visible_press_draw_20261018_1126');O=Path('/workspace/scratch/f060b5601755/root_s05a_f052')
base=Image.open(R/'inputs/F052_from_locked_pose_scaffold.png').convert('RGBA');raw=Image.open(O/'raw/call10_F052.png').convert('RGBA');layer=base.copy();layer.paste(raw.resize((430,415),Image.Resampling.LANCZOS),(620,420))
# Anchor generated lower-jaw position to original chin; eyes/mouth remain unmoved.
arr=np.array(layer); ys=np.arange(arr.shape[0],dtype=float); delta=np.clip((ys-680)/70,0,1)*12; sy=np.clip(ys-delta,0,len(ys)-1); lo=np.floor(sy).astype(int); hi=np.minimum(lo+1,len(ys)-1); w=(sy-lo)[:,None,None]; warped=np.rint(arr[lo]*(1-w)+arr[hi]*w).astype(np.uint8); layer=Image.fromarray(warped)
m=Image.open(R/'masks/F052_finish_exhale_mask.png').convert('L');a=np.array(m)
ext=Image.new('L',base.size,0);d=ImageDraw.Draw(ext);d.polygon([(668,649),(1007,649),(1007,704),(952,745),(908,760),(760,760),(714,738),(668,700)],fill=255)
ext=ext.filter(ImageFilter.GaussianBlur(1));e=np.array(ext);h=np.array(Image.open(R/'masks/F052_hair_ribbon_hard_protection.png'))>0
a=np.maximum(a,e);a[h]=0;a[765:]=0
mask=Image.fromarray(a);mask.save(O/'review/v4_extended_jaw_mask.png');out=Image.composite(layer,base,mask);p=O/'F052_candidate_v4_jaw.png';out.save(p)
bg=Image.new('RGBA',out.size,(110,116,124,255));bg.alpha_composite(out);bg.convert('RGB').crop((600,400,1080,850)).resize((960,900)).save(O/'review/v4_jaw_detail.png')
x=np.array(out);b=np.array(base);change=np.any(x!=b,axis=-1);checks={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'hair_changed':int(change[h].sum()),'below765_changed':int(change[765:].sum()),'outside_extended_mask_changed':int(change[a==0].sum()),'note':'Candidate only: expands permitted cheek mask through continuous jaw to remove old-chin steps. Needs independent approval for narrow jaw-neck transition.'};(O/'review/v4_checks.json').write_text(json.dumps(checks,indent=2));print(checks)
