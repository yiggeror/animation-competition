from pathlib import Path
from PIL import Image
from scipy.ndimage import map_coordinates,binary_dilation
from scipy.optimize import differential_evolution,minimize
import numpy as np,json,hashlib
G=Path(__file__).resolve().parent;R=G.parent;rawp=R/'F033_native_call16/raw/F033_whole_turn_arms_native_raw.png';raw=np.array(Image.open(rawp).convert('RGBA'),float)/255;tar=np.array(Image.open(G/'inputs/F033_actual_edit_target_AA54_1p5x_RGBA.png').convert('RGBA'),float)/255
# Registration features: unchanged real far grip/jade + table box, excluding new foreground hand.
base=np.array(Image.open(G/'inputs/F033_preplaced_body_anchor_truehands_NO_ROD_RGBA.png'));far=np.array(Image.open(G/'masks/F033_far_visible_hand_jade_TRUE_SEAT_guard.png'))>0;near=np.array(Image.open(G/'masks/F033_near_whole_transformed_hand_footprint.png'))>0;box=np.array(Image.open(G/'masks/F033_fixed_table_box_guard.png'))>0
sel=binary_dilation((far&(base[:,:,3]>128))|box,iterations=4)&~binary_dilation(near,iterations=4)
m=np.array(Image.fromarray(sel.astype('uint8')*255).crop((580,280,1360,1080)).resize((1170,1200),Image.Resampling.NEAREST))>0;y,x=np.where(m);keep=(x%2==0)&(y%2==0);x=x[keep].astype(float);y=y[keep].astype(float)
for q in [raw,tar]:q[:,:,:3]*=q[:,:,3,None]
t=tar[y.astype(int),x.astype(int)];s0=1200/raw.shape[0]
def loss(p):
 s,tx,ty=p;co=np.array([(y-ty)/s,(x-tx)/s]);v=np.stack([map_coordinates(raw[:,:,k],co,order=1,mode='constant',cval=0)for k in range(4)],1);err=np.abs(v-t);return float(np.mean(err[:,:3])*.7+np.mean(err[:,3])*.3)
bounds=[(s0*.92,s0*1.08),(-35,35),(-35,35)];opt=differential_evolution(loss,bounds,seed=8,popsize=10,maxiter=55,tol=1e-7,polish=True);p=opt.x
report={'scale':float(p[0]),'tx':float(p[1]),'ty':float(p[2]),'loss':float(opt.fun),'basis':'fixed far visible grip/jade and table box, exclude foreground near hand; single uniform whole raw transform','sampled_pixels':len(x),'raw_sha256':hashlib.sha256(rawp.read_bytes()).hexdigest()};(G/'geometry/RAW_UNIFORM_REGISTRATION.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
