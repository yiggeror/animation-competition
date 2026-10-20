from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage
import numpy as np,json,hashlib,sys
P=Path(__file__).parent;R=P.parent;f=int(sys.argv[1]);B=Image.open(R/'refs/assets/chars/x15/F000.png').convert('RGBA');A=Image.open(P/f'X{f}_complete_body_call01_original.png').convert('RGBA');size=B.size;Y,X=np.indices((size[1],size[0]));ba=np.array(B)
def shoe_points(im):
 a=np.array(im);sel=(Y>1080)&(a[:,:,3]>220)&(a[:,:,0]>125)&(a[:,:,1]<110)&(a[:,:,2]<110)&(a[:,:,0]>1.75*a[:,:,1]);return np.c_[X[sel],Y[sel]]
a=shoe_points(A);b=shoe_points(B);ca=a.mean(0);cb=b.mean(0);s=np.sqrt(((b-cb)**2).sum(1).mean()/((a-ca)**2).sum(1).mean());t=cb-s*ca;N=A.transform(size,Image.Transform.AFFINE,(1/s,0,-t[0]/s,0,1/s,-t[1]/s),Image.Resampling.BICUBIC);na=np.array(N)
# Whole native head, chest, complete arms and entire dress are all one registered drawing.
mask=np.array(Image.open(P/'X180_COMPLETE_BODY_HEAD_ARMS_HIPS_LEGS_WHITE_DOMAIN.png').convert('L'))>0
cloths=[]
for v in [ba,na]:
 r,g,bl=v[:,:,:3].astype(float).transpose(2,0,1);q=(Y>390)&(Y<950)&(X>400)&(X<1020)&(v[:,:,3]>80)&(r>178)&(g>140)&(bl<140)&(g-bl>48);lab,num=ndimage.label(q);sz=np.bincount(lab.ravel());k=1+np.argmax(sz[1:]);cloths.append(ndimage.binary_dilation(ndimage.binary_fill_holes(lab==k),iterations=3))
mask|=cloths[0]|cloths[1]
# Protect true original complete legs and bench; native complete hand silhouettes overlap in the foreground.
sk=(Y>744)&(X>710)&(ba[:,:,0]>150)&(ba[:,:,1]>100)&(ba[:,:,2]>95)&(ba[:,:,2]>.65*ba[:,:,1])&(ba[:,:,3]>200);lab,num=ndimage.label(sk);legs=np.zeros_like(sk)
for k in range(1,num+1):
 z=lab==k
 if z.sum()>10000:legs|=z
legs=ndimage.binary_dilation(ndimage.binary_fill_holes(legs),iterations=3);mask[legs]=0
r,g,bl=ba[:,:,:3].astype(float).transpose(2,0,1);wood=(ba[:,:,3]>50)&(Y>800)&(X<735)&(r>85)&(r<225)&(g>50)&(g<185)&(bl>20)&(bl<145)&(r-g>12)&(g-bl>12);lab,num=ndimage.label(wood);wk=np.zeros_like(wood)
for k in range(1,num+1):
 z=lab==k
 if z.sum()>400:wk|=z
wk=ndimage.binary_dilation(ndimage.binary_fill_holes(wk),iterations=3);mask[wk]=0
skn=(na[:,:,0]>150)&(na[:,:,1]>95)&(na[:,:,2]>80)&(na[:,:,2]>.62*na[:,:,1])&(na[:,:,3]>200)&(Y>500)&(Y<810);lab,num=ndimage.label(skn);arms=np.zeros_like(skn)
for k in range(1,num+1):
 z=lab==k
 if z.sum()>8000 and Y[z].min()<610:arms|=z
arms=ndimage.binary_dilation(ndimage.binary_fill_holes(arms),iterations=3);mask[arms]=1
m=Image.fromarray(np.uint8(mask)*255);c=Image.composite(N,B,m);aa=np.array(c)
# Remove only truly disconnected subpixel dust, never connected fingers/hair or contour.
lab,num=ndimage.label(aa[:,:,3]>12);sz=np.bincount(lab.ravel());dust=np.isin(lab,np.where((sz<8)&(np.arange(len(sz))>0))[0]);aa[dust]=0;c=Image.fromarray(aa)
fp=P/f'X{f}_complete_registered_candidate.png';c.save(fp);m.save(P/f'X{f}_complete_native_semantic_return_mask.png')
bg=Image.new('RGBA',size,'#f7f5ed');bg.alpha_composite(c);bg.convert('RGB').resize((880,880)).save(P/f'X{f}_COMPLETE_REGISTERED_REVIEW.jpg',quality=91);bg.crop((440,370,985,935)).resize((850,881)).convert('RGB').save(P/f'X{f}_NATIVE_BODY_ARMS_HIP_RETURN_DETAIL.jpg',quality=91)
def region_means(v):
 r,g,bl=v[:,:,:3].astype(float).transpose(2,0,1);ok=v[:,:,3]>245;regs={'hair':ok&(Y<470)&(r>20)&(r<130)&(g>20)&(g<120)&(bl>20)&(bl<110)&(r-g<25)&(g-bl<25),'skin':ok&(Y<810)&(r>180)&(g>120)&(bl>105)&(r-g>22)&(g-bl>9)&(g-bl<72),'yellow_cloth':ok&(Y>395)&(Y<940)&(X>420)&(X<995)&(r>190)&(g>150)&(bl<130)&(r-g>6)};return {k:v[ndimage.binary_erosion(z,iterations=2),:3].mean(0) for k,z in regs.items()}
ref=region_means(ba);vals=region_means(aa);palette={k:{'mean_rgb':v.tolist(),'mother_mean_rgb':ref[k].tolist(),'delta':(v-ref[k]).tolist(),'within4':bool(np.max(np.abs(v-ref[k]))<=4)} for k,v in vals.items()}
rec={'status':'ONE_NATIVE_COMPLETE_BODY_SINGLE_SIMILARITY_CANDIDATE','frame':f,'scale':s,'rotation_deg':0,'translation':t.tolist(),'registration_anchor':'complete pair of red sandals, global similarity only; exact original legs and bench retained under same native complete hand silhouettes','raw_sha256':hashlib.sha256((P/f'X{f}_complete_body_call01_original.png').read_bytes()).hexdigest(),'final_sha256':hashlib.sha256(fp.read_bytes()).hexdigest(),'palette_same_mother_semantic_mean_rgb':palette,'disconnected_dust_removed_pixels':int(dust.sum()),'no_independent_limb_transform':True};(P/f'X{f}_native_single_registration.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));print(json.dumps(rec,ensure_ascii=False))
