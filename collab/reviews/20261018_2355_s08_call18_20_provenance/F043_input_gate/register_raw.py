from pathlib import Path
from PIL import Image
from scipy.ndimage import map_coordinates,binary_dilation
from scipy.optimize import differential_evolution
import numpy as np,json,hashlib,argparse
p=argparse.ArgumentParser();p.add_argument('raw');p.add_argument('output_json');args=p.parse_args();G=Path(__file__).resolve().parent;rawp=Path(args.raw);raw=np.array(Image.open(rawp).convert('RGBA'),float)/255;tar=np.array(Image.open(G/'inputs/F041_actual_brows_6x_RGBA.png').convert('RGBA'),float)/255
# Unchanged original black frame and eyelid traces plus nearby true skin, never new eyebrows.
guard=np.array(Image.open(G/'masks/F043_real_glasses_eyelid_black_ink_plus1_guard.png'))>0;white=np.array(Image.open(G/'masks/F043_brows_scene_WHITE_permission.png'))>0;sel=binary_dilation(guard,iterations=3)&~binary_dilation(white,iterations=2);m=np.array(Image.fromarray(sel.astype('uint8')*255).crop((950,480,1140,630)).resize((1140,900),Image.Resampling.NEAREST))>0;y,x=np.where(m);keep=(x%3==0)&(y%3==0);x=x[keep].astype(float);y=y[keep].astype(float)
for q in [raw,tar]:q[:,:,:3]*=q[:,:,3,None]
t=tar[y.astype(int),x.astype(int)];s0=(1140/raw.shape[1]+900/raw.shape[0])/2

def loss(p):
 s,tx,ty=p;co=np.array([(y-ty)/s,(x-tx)/s]);v=np.stack([map_coordinates(raw[:,:,k],co,order=1,mode='constant',cval=0)for k in range(4)],1);err=np.abs(v-t);return float(np.mean(err[:,:3])*.85+np.mean(err[:,3])*.15)
opt=differential_evolution(loss,[(s0*.80,s0*1.10),(-180,180),(-180,180)],seed=8,popsize=10,maxiter=65,tol=1e-7,polish=True);s,tx,ty=opt.x;report=dict(scale=float(s),tx=float(tx),ty=float(ty),loss=float(opt.fun),basis='Unchanged actual frame and eyelid ink with adjacent skin, excluding both eyebrow permission domains. One uniform raw transform only.',sampled_pixels=len(x),raw_sha256=hashlib.sha256(rawp.read_bytes()).hexdigest(),target_size=[1140,900],source_scene_crop=[950,480,1140,630]);Path(args.output_json).write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
