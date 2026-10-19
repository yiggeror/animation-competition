from PIL import Image,ImageDraw,ImageOps
from pathlib import Path
import numpy as np,json,hashlib,sys,shutil,subprocess
D=Path(__file__).parent
raw=Path(sys.argv[1]);dst=D/'originals/F004_call001_raw.png';shutil.copy(raw,dst)
base=Image.open(D/'inputs/F000_locked.png').convert('RGBA');out=Image.open(dst).convert('RGBA'); origsize=out.size
if out.size != base.size:
 if abs(out.width-base.width)>1 or abs(out.height-base.height)>1:raise RuntimeError(f'Need visual global registration decision for raw {out.size}')
 out=out.resize(base.size,Image.Resampling.LANCZOS)
out.save(D/'originals/F004_call001_registered.png')
mask=Image.open(D/'masks/compositing_complete_arm_white.png').convert('L');final=Image.composite(out,base,mask);final.save(D/'final/S20_F004_candidate.png')
# Both published outside-mask invariance and rod invariance include RGBA.
b=np.array(base);f=np.array(final);m=np.array(mask)>0;delta=np.any(f!=b,axis=2);r=np.array(Image.open(D/'masks/rods_protected.png'))>0
verify={'raw_size':list(origsize),'final_size':list(final.size),'changed_pixels':int(delta.sum()),'outside_edit_mask_changed_pixels':int(delta[~m].sum()),'rod_protection_changed_pixels':int(delta[r].sum()),'generator':'builtin imagegen','generation_calls':1,'exposure_fps':24,'exposure_mapping':{'F000':'000-003','F004':'004-007','F008':'008-011'}}
for name,im in [('F000',base),('F004',final),('F008',Image.open(D/'inputs/F008_locked.png').convert('RGBA'))]:
 light=Image.new('RGBA',im.size,'#e5e4df');light.alpha_composite(im);light.convert('RGB').save(D/f'qa/{name}_full_light.png')
 if name=='F004':light.crop((525,315,940,535)).resize((1245,660)).convert('RGB').save(D/'qa/F004_arm_chain_3x.png')
 for j in range(4):
  index={'F000':0,'F004':4,'F008':8}[name]+j;light.convert('RGB').save(D/f'exposure/{index:03d}.png')
strip=Image.new('RGB',(1672*3,941),'#e5e4df')
for j,n in enumerate(['F000','F004','F008']):strip.paste(Image.open(D/f'qa/{n}_full_light.png'),(j*1672,0))
strip.save(D/'qa/F000_F004_F008_fullbody_strip.png')
subprocess.run(['ffmpeg','-v','error','-y','-framerate','24','-i',str(D/'exposure/%03d.png'),'-frames:v','12','-vf','pad=1672:942:0:0:color=0xe5e4df','-c:v','libx264','-crf','12','-pix_fmt','yuv420p',str(D/'qa/F000_F004_F008_actual_4_4_4f_24fps.mp4')],check=True)
for p in sorted(D.rglob('*')):
 if p.is_file() and p.suffix.lower() in ['.png','.mp4','.txt']:verify.setdefault('sha256',{})[str(p.relative_to(D))]=hashlib.sha256(p.read_bytes()).hexdigest()
json.dump(verify,open(D/'qa/verification.json','w'),indent=2);print(json.dumps({k:v for k,v in verify.items() if k!='sha256'},indent=2))
