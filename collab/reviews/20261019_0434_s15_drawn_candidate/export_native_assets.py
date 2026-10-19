from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,hashlib,json
from scipy import ndimage as ndi
P=Path(__file__).resolve().parent.parent
OUT=P/'integration/assets/x15';OUT.mkdir(parents=True,exist_ok=True)
manifest=[]
for src in sorted((P/'approved').glob('F*.png')):
 a=np.array(Image.open(src).convert('RGBA'));alpha=a[:,:,3]
 # Remove only detached very weak alpha; retain every medium/strong pixel and all weak pixels within 2 native pixels of the body.
 distance=ndi.distance_transform_edt(alpha<128)
 remove=(alpha>0)&(alpha<32)&(distance>2)
 cleaned=a.copy();cleaned[remove]=0
 dst=OUT/src.name;Image.fromarray(cleaned,'RGBA').save(dst)
 manifest.append({'id':src.stem,'native':str(src.relative_to(P)),'native_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'export':str(dst.relative_to(P)),'export_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'size':list(a.shape[1::-1]),'removed_weak_exterior_pixels':int(remove.sum()),'unchanged_nonremoved_pixels':bool(np.array_equal(a[~remove],cleaned[~remove]))})
(P/'integration/asset_manifest.json').write_text(json.dumps({'alpha_rule':'only alpha1..31 at >2px from alpha>=128 support; all other RGBA unchanged','assets':manifest},indent=2))
for bgcol,name in [('#ededed','gray'),('#191b21','dark')]:
 c=Image.new('RGB',(1280,680),bgcol);d=ImageDraw.Draw(c)
 for i,e in enumerate(manifest):
  im=Image.open(P/e['export']).convert('RGBA');im.thumbnail((310,310))
  x=(i%4)*320;y=(i//4)*340;c.paste(im,(x+5,y+25),im);d.text((x+10,y+7),e['id'],fill='#fff' if name=='dark' else '#111')
 c.save(P/f'qa/ALL_native_exports_{name}.png')
print('Exported',len(manifest),'native complete drawings')
