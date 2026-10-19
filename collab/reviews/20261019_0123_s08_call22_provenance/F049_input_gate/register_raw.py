from pathlib import Path
from PIL import Image
from scipy.ndimage import map_coordinates,binary_dilation
from scipy.optimize import differential_evolution
import numpy as np,json,hashlib,sys
G=Path(__file__).resolve().parent;rawp=Path(sys.argv[1]);raw=np.array(Image.open(rawp).convert('RGBA'),float)/255;tar=np.array(Image.open(G/'inputs/F049_actual_wrist_edit_target_3x_RGBA.png').convert('RGBA'),float)/255;base=np.array(Image.open(G/'inputs/F049_scene_preplaced_NO_ROD_RGBA.png'));ld=lambda n:np.array(Image.open(G/'masks'/n))>0;far=ld('F049_far_visible_and_true_alpha0_seat_guard.png');w=ld('F049_WHITE_wrist_entire_root_and_exposed_far_underlay.png');fixedforearm=ld('F049_retained_actual_near_forearm_original.png');sel=binary_dilation((far|fixedforearm)&(base[:,:,3]>128),iterations=2)&~binary_dilation(w,iterations=3);m=np.array(Image.fromarray(sel.astype('uint8')*255).crop((1090,730,1400,910)).resize((930,540),Image.Resampling.NEAREST))>0;y,x=np.where(m);keep=(x%3==0)&(y%3==0);x=x[keep].astype(float);y=y[keep].astype(float)
for q in [raw,tar]:q[:,:,:3]*=q[:,:,3,None]
t=tar[y.astype(int),x.astype(int)];sx=930/raw.shape[1];sy=540/raw.shape[0]
def loss(p):
 s,tx,ty=p;co=np.array([(y-ty)/s,(x-tx)/s]);v=np.stack([map_coordinates(raw[:,:,k],co,order=1,mode='constant',cval=0)for k in range(4)],1);er=np.abs(v-t);return float(np.mean(er[:,:3])*.7+np.mean(er[:,3])*.3)
opt=differential_evolution(loss,[(min(sx,sy)*.78,max(sx,sy)*1.22),(-100,100),(-100,100)],seed=22,popsize=10,maxiter=70,tol=1e-7,polish=True);p=opt.x;r={'scale':float(p[0]),'tx':float(p[1]),'ty':float(p[2]),'loss':float(opt.fun),'basis':'fixed far grip/jade and retained original foreground forearm outsidewhite; one uniform whole-raw registration only','sampled_pixels':len(x),'raw_sha256':hashlib.sha256(rawp.read_bytes()).hexdigest(),'status':'REGISTRATION_DIAGNOSTIC_REQUIRES_ACTUAL_VISUAL_CHECK'};(G/'geometry/RAW_UNIFORM_REGISTRATION.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
