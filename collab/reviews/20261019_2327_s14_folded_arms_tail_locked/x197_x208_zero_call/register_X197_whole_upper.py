from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np,json,hashlib
from scipy import ndimage
P=Path(__file__).parent;R=P.parent;B=Image.open(R/'refs/assets/chars/x15/F000.png').convert('RGBA');A=Image.open(P/'X197_complete_upper_call01_original.png').convert('RGBA');size=B.size
Y,X=np.indices((size[1],size[0]))
def collar(im):
 a=np.array(im);sel=(Y>365)&(Y<462)&(X>525)&(X<730)&(a[:,:,3]>220)&(a[:,:,:3].min(2)>210);labels,n=ndimage.label(sel);keep=np.zeros_like(sel)
 for k in range(1,n+1):
  z=labels==k
  if z.sum()>180:keep|=z
 return np.c_[X[keep],Y[keep]]
b=collar(B);a=collar(A);ca=a.mean(0);cb=b.mean(0);s=np.sqrt(((b-cb)**2).sum(1).mean()/((a-ca)**2).sum(1).mean());t=cb-s*ca
N=A.transform(size,Image.Transform.AFFINE,(1/s,0,-t[0]/s,0,1/s,-t[1]/s),Image.Resampling.BICUBIC)
# Single registered whole native torso and arm pair. Mask includes original and new complete shapes.
m=Image.open(P/'X197_X206_FULL_BOTH_SLEEVES_ARMS_TORSO_WHITE_DOMAIN.png').convert('L')
c=Image.composite(N,B,m)
# Natural return through a broad original-cloth overlap; no arm components are moved.
# Only the cloth interior below the moving arms is softly blended to retain fixed lap/hip.
soft=np.array(m).astype(float)/255;blend=(Y>=700)&(Y<780)&(X<700);soft[blend]*=np.clip((780-Y[blend])/80,0,1)
# Return complete white dots, never half-transparent points in the cloth overlap.
na=np.array(N);ba=np.array(B);wh=((na[:,:,:3].min(2)>215)|(ba[:,:,:3].min(2)>215))&(na[:,:,3]>50)&(ba[:,:,3]>50)&blend
lab,num=ndimage.label(ndimage.binary_dilation(wh,iterations=2))
for k in range(1,num+1):
 z=lab==k
 if z.sum()>8:soft[z]=1.0 if soft[z].mean()>=.5 else 0.0
# Preserve exact original complete legs; the broad editable input domain is not a final cut line.
sk=(Y>744)&(X>710)&(ba[:,:,0]>150)&(ba[:,:,1]>100)&(ba[:,:,2]>95)&(ba[:,:,2]>.65*ba[:,:,1])&(ba[:,:,3]>200)
lab,num=ndimage.label(sk);leg=np.zeros_like(sk)
for k in range(1,num+1):
 z=lab==k
 if z.sum()>10000:leg|=z
leg=ndimage.binary_dilation(ndimage.binary_fill_holes(leg),iterations=3);soft[leg]=0
soft[blend&((na[:,:,3]<250)|(ba[:,:,3]<250))]=0
m=Image.fromarray(np.uint8(soft*255));c=Image.composite(N,B,m)
fp=P/'X197_complete_registered_candidate.png';c.save(fp)
N.save(P/'X197_whole_raw_SINGLE_similarity.png');m.save(P/'X197_complete_upper_semantic_return_mask.png')
for name,im in [('X197_complete_registered_REVIEW.jpg',c),('X197_whole_raw_single_REVIEW.jpg',N)]:
 bg=Image.new('RGBA',size,'#f7f5ed');bg.alpha_composite(im);bg.convert('RGB').save(P/name,quality=92)
bg=Image.new('RGBA',size,'#f7f5ed');bg.alpha_composite(c);bg.crop((470,365,970,820)).resize((1000,910)).convert('RGB').save(P/'X197_full_sleeves_arms_waist_DETAIL.jpg',quality=92)
r={'status':'SINGLE_NATIVE_UPPER_PAIR_REGISTERED_CANDIDATE','scale':s,'rotation_deg':0,'translation':t.tolist(),'anchor':'complete white collar shape, uniform similarity only','collar_source_center':ca.tolist(),'collar_target_center':cb.tolist(),'raw_sha256':hashlib.sha256((P/'X197_complete_upper_call01_original.png').read_bytes()).hexdigest(),'final_sha256':hashlib.sha256(fp.read_bytes()).hexdigest(),'fixed':'Exact F000 head/neck/collar and entire lower body seat/stool/feet outside semantic upper domain. No arm split or finger warp.','new_pose_progress':'Near right forearm already lifted; far left hand on lap. Not yet crossed. Next actual target must not reverse to lower arm.','cloth_return':'80px color return within torso/lap cloth only, with complete white-dot components kept opaque. Exact original leg components protected through knee contours. Native complete arm pair preserved.'};(P/'X197_native_single_registration.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps(r,ensure_ascii=False))
