from PIL import Image,ImageDraw,ImageFilter
from pathlib import Path
import numpy as np,json,hashlib
B=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def display(im):
 bg=Image.new('RGBA',im.size,(245,245,245,255));bg.alpha_composite(im);return bg.convert('RGB')
def local_repair(frame,call,source,patch_path,boxes,patch_dy=0):
 source=Path(source);patch_path=Path(patch_path); base=Image.open(source).convert('RGBA'); raw=Image.open(patch_path).convert('RGBA'); patch=Image.new('RGBA',base.size);patch.paste(raw,(0,patch_dy))
 mask=Image.new('L',base.size);d=ImageDraw.Draw(mask)
 for box in boxes:d.rounded_rectangle(box,radius=6,fill=255)
 mask=mask.filter(ImageFilter.GaussianBlur(2));m=np.asarray(mask);n=np.asarray(base);r=np.asarray(patch); out=Image.composite(patch,base,mask)
 path=B/f'F{frame:03d}_candidate.png';out.save(path);mask_path=B/'analysis'/f'F{frame:03d}_repair_mask.png';mask.save(mask_path)
 o=np.asarray(out); outside=m==0;assert np.array_equal(n[outside],o[outside]);on=Image.blend(display(base),display(out),.5);on.save(B/'analysis'/f'F{frame:03d}_vs_previous_onion50.png')
 bounds=mask.getbbox(); crop=(650,180,890,360)
 contact=Image.new('RGB',(720,360));contact.paste(display(base).crop(crop).resize((360,270)),(0,0));contact.paste(display(out).crop(crop).resize((360,270)),(360,0));contact.save(B/'analysis'/f'F{frame:03d}_face_before_after.jpg')
 Image.blend(display(base).crop(crop),display(out).crop(crop),.5).resize((720,540)).save(B/'analysis'/f'F{frame:03d}_eye_onion50.png')
 meta={'frame':frame,'call_count_at_creation':call,'source':str(source),'source_sha256':sha(source),'raw_generated_path':str(patch_path),'raw_generated_sha256':sha(patch_path),'raw_size':raw.size,'output':str(path),'output_sha256':sha(path),'output_size':out.size,'alpha_extrema':out.getchannel('A').getextrema(),'repair':{'method':'generated brow/eye pixels locally composited into exact previous accepted source using an explicit recorded grayscale mask','patch_translation_xy':[0,patch_dy],'scale':[1,1],'mask':str(mask_path),'mask_sha256':sha(mask_path),'solid_roundrect_boxes':boxes,'mask_blur_radius':2,'nonzero_mask_bbox':bounds,'changed_pixels_outside_mask':int(np.any(n[outside]!=o[outside],axis=1).sum())},'manual_review':'pending'}
 (B/'analysis'/f'F{frame:03d}_repair_manifest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2));print(json.dumps(meta,indent=2))
 return path
if __name__=='__main__':
 local_repair(65,1,B/'inputs/k06_rightpad_1672x941.png',B/'originals/call01_F065.png',[(705,198,760,233),(799,219,871,271)],7)

def local_eye_repair(frame,call,source,patch_path,manual_review='pending'):
 source=Path(source);patch_path=Path(patch_path);base=Image.open(source).convert('RGBA');raw=Image.open(patch_path).convert('RGBA');patch=Image.new('RGBA',base.size)
 native=raw.resize((512,512),Image.Resampling.LANCZOS);patch.paste(native,(600,120))
 polygons=[[(694,252),(714,253),(730,261),(737,275),(740,292),(735,309),(699,312),(691,290)],[(790,284),(808,282),(830,288),(849,307),(853,327),(842,338),(798,339),(785,324),(787,302)]]
 mask=Image.new('L',base.size);d=ImageDraw.Draw(mask)
 for poly in polygons:d.polygon(poly,fill=255)
 mask=mask.filter(ImageFilter.GaussianBlur(1));out=Image.composite(patch,base,mask)
 path=B/f'F{frame:03d}_candidate.png';out.save(path);mask_path=B/'analysis'/f'F{frame:03d}_repair_mask.png';mask.save(mask_path)
 n=np.asarray(base);o=np.asarray(out);m=np.asarray(mask);outside=m==0;assert np.array_equal(n[outside],o[outside]);on=Image.blend(display(base),display(out),.5);on.save(B/'analysis'/f'F{frame:03d}_vs_previous_onion50.png')
 crop=(650,180,890,360);contact=Image.new('RGB',(720,270));contact.paste(display(base).crop(crop).resize((360,270)),(0,0));contact.paste(display(out).crop(crop).resize((360,270)),(360,0));contact.save(B/'analysis'/f'F{frame:03d}_face_before_after.jpg')
 on.crop(crop).resize((720,540)).save(B/'analysis'/f'F{frame:03d}_eye_onion50.png')
 meta={'frame':frame,'call_count_at_creation':call,'source':str(source),'source_sha256':sha(source),'raw_generated_path':str(patch_path),'raw_generated_sha256':sha(patch_path),'raw_size':raw.size,'output':str(path),'output_sha256':sha(path),'output_size':out.size,'alpha_extrema':out.getchannel('A').getextrema(),'repair':{'method':'only new generated local eye crop resampled to native crop dimensions, then eye-only masked composite into exact previous accepted full frame','generated_crop_scale_xy':[512/raw.width,512/raw.height],'crop_destination_xy':[600,120],'source_full_frame_scale_xy':[1,1],'mask':str(mask_path),'mask_sha256':sha(mask_path),'polygons':polygons,'mask_blur_radius':1,'nonzero_mask_bbox':mask.getbbox(),'changed_pixels_outside_mask':int(np.any(n[outside]!=o[outside],axis=1).sum())},'manual_review':manual_review}
 (B/'analysis'/f'F{frame:03d}_repair_manifest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2));print(json.dumps(meta,indent=2));return path
