from PIL import Image
from pathlib import Path
import numpy as np,json,hashlib
O=Path('/workspace/scratch/f060b5601755/root_s05a_f052');R=Path('/workspace/scratch/f060b5601755/astra_s05a_visible_press_draw_20261018_1126')
im=Image.open(O/'F052_candidate_v5_clean.png').convert('RGBA');a=np.array(im);base=np.array(Image.open(R/'inputs/F052_from_locked_pose_scaffold.png').convert('RGBA'));m=np.zeros(a.shape[:2],bool)
for x0,y0,x1,y1 in [(973,696,986,714),(989,712,1002,720)]:m[y0:y1,x0:x1]=True
newdark=(a[:,:,0]<115)&(a[:,:,1]<100)&(a[:,:,2]<100)&(a[:,:,3]>10)
basehair=(base[:,:,0]<115)&(base[:,:,1]<100)&(base[:,:,2]<100)&(base[:,:,3]>30)
sel=m&newdark&~basehair;a[sel]=base[sel];out=Image.fromarray(a);p=O/'F052_candidate_v6_clean.png';out.save(p)
bg=Image.new('RGBA',out.size,(110,116,124,255));bg.alpha_composite(out);bg.convert('RGB').crop((600,400,1080,850)).resize((960,900)).save(O/'review/v6_clean_detail.png')
Image.fromarray((sel*255).astype('uint8')).save(O/'review/v6_removed_fragments_mask.png');d={'removed_new_fragment_pixels':int(sel.sum()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'scope':'Only new dark fragments inside two independent-review ROIs; original dark hair pixels preserved; eye/mouth/jaw unchanged.'};(O/'review/v6_checks.json').write_text(json.dumps(d,indent=2));print(d)
