from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
import numpy as np,json,hashlib
D=Path('astra_s07_f008_prepare_20261018_1249');orig=Image.open(D/'candidates/F008_local_v2.png').convert('RGBA');back=Image.open(D/'candidates/F008_call01_registered_palette_matched.png').convert('RGBA');a=np.array(orig);b=np.array(back);m=Image.new('L',orig.size);d=ImageDraw.Draw(m)
d.polygon([(558,1062),(567,1058),(578,1064),(578,1071),(558,1071)],fill=255);d.polygon([(601,1038),(615,1038),(618,1054),(603,1059)],fill=255)
# Restore only exposed backing through original alpha, never repaint opaque hand/jade pixels.
comp=np.array(Image.alpha_composite(back,orig));sel=(np.array(m)>0)&(a[:,:,3]<255);out=a.copy();out[sel]=comp[sel];actual=np.any(out!=a,axis=2);Image.fromarray((actual*255).astype('uint8')).save(D/'masks/F008_jade_background_cleanup_v3.png');tot=ImageChops.lighter(Image.open(D/'masks/F008_local_repair_v2_mask.png'),Image.fromarray((actual*255).astype('uint8')));tot.save(D/'masks/F008_final_repair_union_v3.png');c=Image.fromarray(out);c.save(D/'candidates/F008_local_v3.png')
for n,bg in [('white','white'),('gray',(150,150,150,255))]:
 im=Image.alpha_composite(Image.new('RGBA',orig.size,bg),c).convert('RGB');im.save(D/f'review/F008_local_v3_{n}.jpg',quality=97)
 if n=='white':im.crop((360,810,920,1180)).resize((1120,740)).save(D/'review/F008_local_v3_join_detail.jpg',quality=97)
base=np.array(Image.open(D/'preposition/F008_preposition_NOT_FINAL.png'));diff=np.any(base!=out,axis=2);Image.fromarray((diff*255).astype('uint8')).save(D/'masks/F008_final_v3_actual_diff.png');
prev=Image.open(D/'sources/F000_LOCKED_rgba.png');wh=lambda q:Image.alpha_composite(Image.new('RGBA',orig.size,'white'),q);Image.blend(wh(prev),wh(c),.5).convert('RGB').save(D/'review/F000_F008_v3_onion.jpg',quality=96)
sheet=Image.new('RGB',(1024,816),'white');sheet.paste(wh(prev).resize((512,768)).convert('RGB'),(0,40));sheet.paste(wh(c).resize((512,768)).convert('RGB'),(512,40));sd=ImageDraw.Draw(sheet);sd.text((20,10),'F000 LOCKED',(0,0,0));sd.text((530,10),'F008 CANDIDATE v3 / same world',(0,0,0));sheet.save(D/'review/F000_F008_v3_side_by_side.jpg',quality=96)
check={'sha256':hashlib.sha256((D/'candidates/F008_local_v3.png').read_bytes()).hexdigest(),'tiny_background_repair_changed_pixels':int(actual.sum()),'opaque_hand_jade_pixels_changed_by_cleanup':int(actual[a[:,:,3]==255].sum()),'outside_final_mask_changed_pixels':int(diff[np.array(tot)==0].sum()),'source_call':1,'status':'PENDING_INDEPENDENT_REVIEW'};(D/'geometry/F008_final_v3_checks.json').write_text(json.dumps(check,indent=2));print(check)
