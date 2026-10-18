"""Same-raw eyes-only registration and authorized compositing. Never calls generation."""
from pathlib import Path
from PIL import Image,ImageChops,ImageFilter
import numpy as np,json,hashlib,shutil,argparse
ap=argparse.ArgumentParser();ap.add_argument('--raw',required=True);ap.add_argument('--base',required=True);ap.add_argument('--output',required=True);ap.add_argument('--scale',type=float,required=True);ap.add_argument('--tx',type=float,required=True);ap.add_argument('--ty',type=float,required=True);ap.add_argument('--mask');ap.add_argument('--guard');args=ap.parse_args()
P=Path(__file__).resolve().parent;O=Path(args.output).resolve()
for s in ['raw','registered','candidates','qa','geometry']:(O/s).mkdir(parents=True,exist_ok=True)
rawp=Path(args.raw).resolve();basep=Path(args.base).resolve();raw=Image.open(rawp).convert('RGBA');base=Image.open(basep).convert('RGBA')
raw_copy=O/'raw/F000_eyes03_native_raw.png'
if raw_copy.exists():assert hashlib.sha256(raw_copy.read_bytes()).hexdigest()==hashlib.sha256(rawp.read_bytes()).hexdigest()
else:shutil.copy2(rawp,raw_copy)
s=args.scale;inv=(1/s,0,-args.tx/s,0,1/s,-args.ty/s);reg=raw.transform((984,498),Image.Transform.AFFINE,inv,resample=Image.Resampling.BICUBIC);reg.save(O/'registered/eyes03_registered_6x_RGBA.png')
small=reg.resize((164,83),Image.Resampling.LANCZOS);scene=Image.new('RGBA',(1920,1080),0);scene.paste(small,(806,488));scene.save(O/'registered/eyes03_registered_scene_patch_RGBA.png')
mask=Image.open(args.mask or P/'masks/F000_eyes_only_scene_permission.png').convert('L');hard=Image.open(args.guard or P/'masks/F000_frame_black_lines_plus1_scene_protected.png').convert('L');mask=ImageChops.subtract(mask,hard);feather=ImageChops.multiply(mask,mask.filter(ImageFilter.GaussianBlur(.6)))
comp=Image.composite(scene,base,feather);c=np.array(comp);b=np.asarray(base);white=np.asarray(mask)>0;frozen=~white|(np.asarray(hard)>0);c[frozen]=b[frozen];c[:,:,3]=b[:,:,3];candidate=Image.fromarray(c,'RGBA');path=O/'candidates/F000_eyes03_local_composite_RGBA.png';candidate.save(path)
for label,col in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 bg=Image.new('RGBA',base.size,col);bg.alpha_composite(candidate);bg.convert('RGB').save(O/'qa'/f'candidate_{label}.png')
 for name,box,m in [('eyes',(806,488,970,571),6),('head_and_match',(625,310,1205,860),2),('hands',(930,728,1214,893),4),('bottom',(530,976,990,1080),2)]:
  q=bg.crop(box);q.resize((q.width*m,q.height*m),Image.Resampling.LANCZOS).convert('RGB').save(O/'qa'/f'candidate_{name}_{label}.png')
change=np.any(c!=b,2);checks={'status':'EYES_ONLY_COMPOSITE_PENDING_ACTUAL_GAZE_REVIEW','actual_native_call_total':3,'additional_generation_calls_by_this_script':0,'raw_path':str(rawp),'raw_sha256':hashlib.sha256(rawp.read_bytes()).hexdigest(),'base_path':str(basep),'base_sha256':hashlib.sha256(basep.read_bytes()).hexdigest(),'uniform_raw_to_6x_crop':{'scale':s,'tx':args.tx,'ty':args.ty},'scene_crop':[806,488,970,571],'outside_eye_mask_changed_pixels':int((change&~white).sum()),'frame_plus1_guard_changed_pixels':int((change&(np.asarray(hard)>0)).sum()),'alpha_changed_pixels':int((c[:,:,3]!=b[:,:,3]).sum()),'candidate_sha256':hashlib.sha256(path.read_bytes()).hexdigest()};(O/'geometry/registration_and_preservation.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
