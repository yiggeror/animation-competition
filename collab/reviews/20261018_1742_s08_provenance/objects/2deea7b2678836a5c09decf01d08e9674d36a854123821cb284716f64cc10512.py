"""Same-raw postprocess only. Requires explicit inspected uniform raw->1300x860 registration.
Example: python composite_returned_crop.py RAW OUTPUT_DIR --scale 1 --tx 0 --ty 0
No generation, no automatic retries, no original overwrite.
"""
from pathlib import Path
import argparse,json,hashlib,shutil
from PIL import Image,ImageFilter
import numpy as np
p=argparse.ArgumentParser();p.add_argument('raw');p.add_argument('output_dir');p.add_argument('--scale',type=float,required=True);p.add_argument('--tx',type=float,required=True);p.add_argument('--ty',type=float,required=True);args=p.parse_args()
G=Path(__file__).resolve().parent;R=G.parent;O=Path(args.output_dir);O.mkdir(parents=True,exist_ok=True)
for d in ['raw','registered','candidates','qa','geometry']:(O/d).mkdir(exist_ok=True)
rawpath=Path(args.raw);copy=O/'raw/F003_native_raw.png'
if copy.exists():raise SystemExit('Refusing overwrite of a saved raw; use a new output directory')
shutil.copy2(rawpath,copy);raw=Image.open(copy).convert('RGBA');s=args.scale;reg=raw.transform((1300,860),Image.Transform.AFFINE,(1/s,0,-args.tx/s,0,1/s,-args.ty/s),resample=Image.Resampling.BICUBIC);reg.save(O/'registered/F003_registered_crop_2x_RGBA.png');small=reg.resize((650,430),Image.Resampling.LANCZOS);scene=Image.new('RGBA',(1920,1080),0);scene.paste(small,(585,615));scene.save(O/'registered/F003_registered_scene_patch_RGBA.png')
base=Image.open(G/'inputs/F003_scene_preplaced_RGBA.png').convert('RGBA');m=Image.open(G/'masks/F003_scene_white_allowed_black_frozen.png').convert('L');binary=np.array(m)>0;f=np.array(m.filter(ImageFilter.GaussianBlur(.6)),dtype=float)/255;f[~binary]=0
b=np.array(base);q=np.array(scene);ba=b[:,:,3].astype(float)/255;qa=q[:,:,3].astype(float)/255;alpha=qa*f+ba*(1-f);premul=q[:,:,:3].astype(float)*qa[:,:,None]*f[:,:,None]+b[:,:,:3].astype(float)*ba[:,:,None]*(1-f[:,:,None]);rgb=np.divide(premul,np.maximum(alpha[:,:,None],1e-10));out=np.dstack((np.clip(np.rint(rgb),0,255).astype('uint8'),np.clip(np.rint(alpha*255),0,255).astype('uint8')));out[~binary]=b[~binary]
result=Image.fromarray(out,'RGBA');result.save(O/'candidates/S08_F003_local_arm_candidate_RGBA.png')
for label,col in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 bg=Image.new('RGBA',base.size,col);bg.alpha_composite(result);bg.convert('RGB').save(O/'qa'/f'candidate_{label}.png')
 for name,bb,factor in [('whole_arm',(585,615,1235,1045),2),('contact',(970,725,1220,895),4),('near_cuff',(625,750,790,880),4),('near_elbow',(730,860,865,1000),4),('wrist',(955,795,1030,895),5)]:
  t=bg.crop(bb);t.resize((t.width*factor,t.height*factor),Image.Resampling.LANCZOS).convert('RGB').save(O/'qa'/f'candidate_{name}_{label}.png')
change=np.any(out!=b,2);checks={'status':'F003_CANDIDATE_PENDING_VISUAL_REVIEW','raw':str(rawpath),'raw_sha256':hashlib.sha256(copy.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256((O/'candidates/S08_F003_local_arm_candidate_RGBA.png').read_bytes()).hexdigest(),'native_generation_calls_by_this_script':0,'registration':{'scale':s,'tx':args.tx,'ty':args.ty,'target_crop':[1300,860],'scene_box':[585,615,1235,1045]},'changed_outside_white':int((change&~binary).sum()),'alpha_changes_inside_allowed':int(((out[:,:,3]!=b[:,:,3])&binary).sum()),'notes':'Mask is explicitly internally feathered; no raw pixels are adopted outside white. Real preplaced hand/match and far hand/box/jade black domains stay exact. No color-keying or fake skin. Visually verify near sleeve/elbow/wrist chain, far upperarm restoration, new box-head contact, alpha edges and absence of double arm before lock.'}
for name in ['F003_far_hand_box_jade_protected.png','F003_match_protected.png','F003_preplaced_hand_match_protected.png']:
 pp=np.array(Image.open(G/'masks'/name).convert('L'))>0;pp&=~binary;checks[name+'_protected_rgba_changed']=int((change&pp).sum())
(O/'geometry/checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
