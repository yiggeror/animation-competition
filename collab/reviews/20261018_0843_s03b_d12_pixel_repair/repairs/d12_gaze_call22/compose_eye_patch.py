from PIL import Image,ImageDraw,ImageFilter
from pathlib import Path
import numpy as np, json, hashlib
root=Path(__file__).resolve().parents[2]
r=root/'repairs/d12_gaze_call22'; o=r/'outputs'; c=r/'composites'; c.mkdir(exist_ok=True)
basepath=root/'repairs/d12_local_call21/seams_v3/S03b_d12_f28_call21_seams_v3_candidate.png'
base=Image.open(basepath).convert('RGBA'); gen=Image.open(o/'call22_head_native512.png').convert('RGBA')
# Strictly local eye apertures and upper lids; excludes eyeglass rims.
polygons=[[(691,265),(704,265),(724,273),(735,283),(736,300),(730,308),(716,308),(703,302),(694,291)],[(789,291),(808,291),(834,300),(853,314),(855,329),(845,338),(824,340),(804,334),(790,324),(783,310)]]
m=Image.new('L',base.size,0); d=ImageDraw.Draw(m)
for p in polygons:d.polygon(p,fill=255)
hard=np.array(m);soft=np.array(m.filter(ImageFilter.GaussianBlur(1.0))); mask=Image.fromarray(np.minimum(hard,soft),'L')
fullgen=base.copy();fullgen.paste(gen,(608,0))
result=Image.composite(fullgen,base,mask);result.save(c/'S03b_d12_f28_call22_eyes_on_seams_v3.png')
mask.save(c/'S03b_d12_call22_eyes_mask.png')
patch=fullgen.copy();patch.putalpha(mask);patch.save(c/'S03b_d12_call22_eyes_patch_rgba.png')
patch.crop((608,0,1120,512)).save(c/'S03b_d12_call22_eyes_patch_head512_rgba.png')
result.crop((608,0,1120,512)).save(c/'S03b_d12_call22_head_composited.png')
a=np.array(base); b=np.array(result); mk=np.array(mask);diff=np.any(a!=b,axis=2); yy,xx=np.where(diff)
checks={'base_sha256':hashlib.sha256(basepath.read_bytes()).hexdigest(),'base':str(basepath),'canvas':base.size,'source_crop_bbox':[608,0,1120,512],'mask_polygons_global':polygons,'mask_nonzero_pixels':int((mk>0).sum()),'changed_pixels':int(diff.sum()),'outside_mask_changed_pixels':int((diff&(mk==0)).sum()),'all_pixels_below_y341_identical':bool(np.array_equal(a[341:],b[341:])),'head_silhouette_hair_neck_ear_mouth_and_body_locked':'Only support of the two eye polygons can change. No contour, hair, ear, neck, mouth, glasses rim or body replacement.','diff_bbox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],'output_sha256':hashlib.sha256((c/'S03b_d12_f28_call22_eyes_on_seams_v3.png').read_bytes()).hexdigest()}
(c/'pixel_lock_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
# Native image comparisons, without altering any source endpoint.
ims=[Image.open(root/'outputs/chew/originals/d11_f25_call03.png'),result,Image.open(root/'outputs/chew/originals/d13_f32_call05.png')]
board=Image.new('RGB',(1560,560),'#e5e8eb');d=ImageDraw.Draw(board)
for i,im in enumerate(ims):
 cr=im.crop((608,0,1120,512));board.paste(cr,(i*520,40),cr);d.text((i*520+12,12),['D11 original','D12 call22 eyes + seam v3 body','D13 original'][i],fill='black')
board.save(c/'head_triptych_final.png')
eyes=Image.new('RGB',(1500,340),'#e5e8eb'); d=ImageDraw.Draw(eyes)
for i,im in enumerate(ims):
 cr=im.crop((660,246,872,355)).resize((466,240));eyes.paste(cr,(i*500+10,65),cr);d.text((i*500+10,12),['D11 original','D12 final restricted eye patch','D13 original'][i],fill='black')
eyes.save(c/'eye_triptych_final.png')
print(json.dumps(checks,indent=2))
