from pathlib import Path
from PIL import Image
from scipy.ndimage import map_coordinates,binary_dilation
from scipy.optimize import differential_evolution
import numpy as np,json,hashlib,sys
G=Path(__file__).resolve().parent;R=G.parent;rawp=Path(sys.argv[1]);raw=np.array(Image.open(rawp).convert('RGBA'),float)/255;tar=np.array(Image.open(G/'inputs/F046_actual_edit_target_2x_RGBA.png').convert('RGBA'),float)/255
base=np.array(Image.open(G/'inputs/F046_scene_preplaced_NO_ROD_RGBA.png'));far=np.array(Image.open(G/'masks/F046_far_visible_hand_jade_TRUE_SEAT_guard.png'))>0;near=np.array(Image.open(G/'masks/F046_near_whole_transformed_footprint.png'))>0;box=np.array(Image.open(G/'masks/F046_fixed_table_box_guard.png'))>0;w=np.array(Image.open(G/'masks/F046_WHITE_near_sleeve_arm_wrist_and_exposed_background.png'))>0
Y,X=np.indices(w.shape);stablecloth=(base[:,:,3]>128)&~w&(X>=980)&(X<=1090)&(Y>=700)&(Y<=805)
sel=binary_dilation((far&(base[:,:,3]>128))|box|stablecloth,iterations=3)&~binary_dilation(near,iterations=4)
m=np.array(Image.fromarray(sel.astype('uint8')*255).crop((700,680,1470,1020)).resize((1540,680),Image.Resampling.NEAREST))>0;y,x=np.where(m);keep=(x%3==0)&(y%3==0);x=x[keep].astype(float);y=y[keep].astype(float)
for q in [raw,tar]:q[:,:,:3]*=q[:,:,3,None]
t=tar[y.astype(int),x.astype(int)];sx=1540/raw.shape[1];sy=680/raw.shape[0]
def loss(p):
 s,tx,ty=p;co=np.array([(y-ty)/s,(x-tx)/s]);v=np.stack([map_coordinates(raw[:,:,k],co,order=1,mode='constant',cval=0)for k in range(4)],1);err=np.abs(v-t);return float(np.mean(err[:,:3])*.7+np.mean(err[:,3])*.3)
bounds=[(min(sx,sy)*.78,max(sx,sy)*1.22),(-180,180),(-180,180)];opt=differential_evolution(loss,bounds,seed=21,popsize=10,maxiter=75,tol=1e-7,polish=True);p=opt.x
report={'scale':float(p[0]),'tx':float(p[1]),'ty':float(p[2]),'loss':float(opt.fun),'basis':'fixed far visible grip/jade, table box and unchanged chest cloth; exclude foreground near hand; one uniform whole raw transform','sampled_pixels':len(x),'raw_sha256':hashlib.sha256(rawp.read_bytes()).hexdigest()};(G/'geometry/RAW_UNIFORM_REGISTRATION.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
