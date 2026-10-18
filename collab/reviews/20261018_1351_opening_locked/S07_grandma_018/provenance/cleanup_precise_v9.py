from pathlib import Path
from PIL import Image,ImageChops,ImageFilter,ImageDraw
import numpy as np,json,hashlib
D=Path('astra_s07_f018_prepare_20261018_1342');W,H=1024,1536;k=.2734375;src=np.array(Image.open(D/'sources/F016_LOCKED_rgba.png'));a=np.array(Image.open(D/'candidates/F018_precise_v8.png'));m=Image.open(D/'masks/F016_foreground_union.png');dx,dy=np.array([-1.398659,4.496158])/k;mt=m.transform((W,H),Image.Transform.AFFINE,(1,0,-dx,0,1,-dy),Image.Resampling.BICUBIC);union=ImageChops.lighter(m,mt).filter(ImageFilter.MaxFilter(19));ma=np.array(union);out=a.copy();out[ma==0]=src[ma==0];changed=np.any(out!=a,axis=2);Image.fromarray((changed*255).astype('uint8')).save(D/'masks/F018_alpha_original_restore_v9.png');union.save(D/'masks/F018_explicit_source_target_union_v9.png');c=Image.fromarray(out);c.save(D/'candidates/F018_precise_v9.png');diff=np.any(out!=src,axis=2);Image.fromarray((diff*255).astype('uint8')).save(D/'masks/F018_actual_diff_v9.png')
for nm,col in [('white','white'),('darkgray',(64,68,74,255))]:
 im=Image.alpha_composite(Image.new('RGBA',(W,H),col),c).convert('RGB');im.save(D/f'review/F018_precise_v9_{nm}.jpg',quality=98);im.crop((105,1170,585,1490)).resize((960,640)).save(D/f'review/F018_grip_v9_{nm}.jpg',quality=98)
 if nm=='white':im.crop((270,1030,910,1210)).resize((1280,360)).save(D/'review/F018_waist_v9_white.jpg',quality=98)
checks={}
for n,(x1,y1,x2,y2) in {'near_shoe_unoccluded':(425,1407,570,1470),'lower_pants_unoccluded':(450,1200,530,1355)}.items():checks[n]=int(diff[y1:y2,x1:x2].sum())
checks.update({'sha256':hashlib.sha256((D/'candidates/F018_precise_v9.png').read_bytes()).hexdigest(),'actual_changed_pixels':int(diff.sum()),'outside_explicit_source_target_union_changed':int(diff[ma==0].sum()),'alpha_only_restore_pixels':int(changed.sum()),'new_calls':0});(D/'geometry/F018_final_checks_v9.json').write_text(json.dumps(checks,indent=2));print(checks)
