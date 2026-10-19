from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage as nd
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;B=R.parent
H=B/'F048_F071_SEMANTIC_CLOSURE_ZERO_CALL_20261019'
N=B/'F054_F060_F066_NATIVE_call01_each_from_e5c66f8f_20261019/F060'
def read(p):return np.array(Image.open(p).convert('RGBA'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(a,p):Image.fromarray(a).save(p)
def poly(points):
    p=Image.new('L',(1024,1536));ImageDraw.Draw(p).polygon(points,fill=255);return np.array(p)>0
def premul(a):
    x=a.astype(float);x[:,:,:3]*=x[:,:,3:4]/255;return x
def straight(a):
    x=a.copy();x[:,:,:3]=np.divide(x[:,:,:3],x[:,:,3:4]/255,out=np.zeros_like(x[:,:,:3]),where=x[:,:,3:4]>1e-8)
    x=np.rint(np.clip(x,0,255)).astype('uint8');x[x[:,:,3]==0]=0;return x
beforep=H/'F060_FULL_SEMANTIC_REPAIR_RGBA.png';rawp=N/'originals/S29_F060_call01_RAW_UNTOUCHED.png'
before=read(beforep);raw=read(rawp);Y,X=np.indices((1536,1024))
reg=json.loads((N/'reintegration/INTEGRATION_CHECK.json').read_text())['complete_far_group_single_similarity']
A=np.array(reg['matrix']);t=np.array(reg['translation'])
# Use the COMPLETE blue shoulder from the same untouched060 native raw,
# including the piece excluded by the old target-head protection polygon.
rgb=raw[:,:,:3].astype(int);blue=(rgb[:,:,1]>95)&(rgb[:,:,2]>135)&(rgb[:,:,2]>rgb[:,:,0]+15)&(raw[:,:,3]>128)&(Y>300)&(Y<940)
lab,_=nd.label(nd.binary_closing(blue,iterations=1));m=nd.binary_dilation(nd.binary_fill_holes(lab==lab[390,500]),iterations=2)&(raw[:,:,3]>0)
source=np.zeros_like(raw);source[m]=raw[m];source[m&(raw[:,:,3]>=128),3]=255
source[(Y<330)|(Y>520)]=0
save(source,R/'SAME060_COMPLETE_NATIVE_BLUE_SHOULDER_SOURCE_RGBA.png')
# One smooth garment surface joins the fixed collar to the exact existing far
# group similarity. This is not an arm transform or a horizontal color patch.
sx=X.astype(float);sy=Y.astype(float)
for _ in range(18):
    w=np.clip((sx-486)/35,0,1);w=w*w*(3-2*w)
    dx=(A[0,0]-1)*sx+A[0,1]*sy+t[0];dy=A[1,0]*sx+(A[1,1]-1)*sy+t[1]
    sx=X-w*dx;sy=Y-w*dy
v=premul(source);projected=np.stack([nd.map_coordinates(v[:,:,k],[sy,sx],order=1,mode='constant',cval=0)for k in range(4)],2)
shoulder=straight(projected);save(shoulder,R/'CONTINUOUS_COLLAR_TO_REGISTERED_SLEEVE_SHOULDER_RGBA.png')
domain=poly([(467,352),(490,348),(528,374),(554,411),(578,455),(580,493),(548,512),(509,500),(476,467),(464,424)])
# Preserve the actual neck/chin and fixed collar flap. Opaque collar protection
# must not return transparent pixels from the obsolete head cutout.
brgb=before[:,:,:3].astype(int)
skin=(brgb[:,:,0]>brgb[:,:,2]+25)&(brgb[:,:,0]>110)&(brgb[:,:,1]>65)&(before[:,:,3]>0)
neck=nd.binary_dilation(skin,iterations=2)&domain
collar=poly([(420,340),(506,340),(501,368),(491,386),(488,400),(482,427),(477,447),(468,449),(421,442)])&(before[:,:,3]>128)
# The real fixed collar-to-shoulder exterior is a curved belt above the split
# mouth, including its outside alpha. It must not acquire a second source ink
# contour where the existing head and native shoulder outlines differ slightly.
collar_top=poly([(480,340),(520,376),(516,381),(480,362)])
protection=neck|collar|collar_top
# Exact registered sleeve exterior is a separate lock from the invalid seam
# mouth. Preserve its original visible RGB/alpha down the shoulder.
far=read(H/'SAME_REGISTERED_FAR_ARM_BLUE_ROOT_MASK_CORRECTED_RGBA.png')
outer=np.zeros(domain.shape,bool)
for y in range(388,513):
    xx=np.flatnonzero((far[y,:,3]>0)&(X[y]>500))
    if len(xx):outer[y,max(0,int(xx[-1])-2):int(xx[-1])+1]=True
protection|=outer
weight=np.clip(nd.distance_transform_edt(domain)/9,0,1);weight=weight*weight*(3-2*weight)
weight[protection]=0
# Composite the one continuous cloth layer behind the protected chin/collar.
# Do not clear existing cloth where the source raw's top alpha edge differs
# from the locked head. Complete native opaque cloth replaces old seam ink.
layer=projected*weight[:,:,None]
fixed=straight(layer+premul(before)*(1-layer[:,:,3:4]/255))
fixed[protection]=before[protection];fixed[~domain]=before[~domain]
out=R/'F060_COLLAR_SHOULDER_CLOSED_RGBA.png';save(fixed,out)
save((domain*255).astype('uint8'),R/'FULL_BLUE_SHOULDER_SEMANTIC_DOMAIN_MASK.png')
save((protection*255).astype('uint8'),R/'PROTECTED_NECK_COLLAR_TRUE_SLEEVE_OUTLINE_MASK.png')
save(np.rint(weight*255).astype('uint8'),R/'CONTINUOUS_SHOULDER_REPLACEMENT_WEIGHT.png')
def gray(a):return Image.alpha_composite(Image.new('RGBA',(1024,1536),(232,235,239,255)),Image.fromarray(a)).convert('RGB')
gray(fixed).save(R/'F060_FULL_ON_GRAY.png')
gray(fixed).crop((400,300,620,510)).save(R/'F060_COLLAR_SHOULDER_1TO1.png')
sheet=Image.new('RGB',(1320,450),(232,235,239));d=ImageDraw.Draw(sheet)
for i,(a,title)in enumerate([(before,'BEFORE transparent diagonal split'),(raw,'SAME060 raw continuous source'),(fixed,'AFTER continuous blue shoulder')]):
    sheet.paste(gray(a).crop((400,300,620,510)).resize((440,420)),(i*440,30));d.text((i*440+8,8),title,fill='black')
sheet.save(R/'SAME_RAW_SHOULDER_BEFORE_SOURCE_AFTER_2X.png')
changed=np.any(fixed!=before,2);assert not changed[~domain].any()and not changed[protection].any()
near=read(N/'reintegration/EXACT_NATIVE_NEAR_FULL_BARE_ARM_FOREGROUND_RGBA.png')
anatomy=(near[:,:,3]>0)|((far[:,:,3]>0)&(Y>515));assert not changed[anatomy].any()
# Existing signed-off lower blouse, cotton, props and hands are untouched.
assert np.array_equal(fixed[513:],before[513:])
report={'generation_calls':0,'history_commit':'55942c39c3500f55fc99a320e05a82ab67d6d9a6','native_delivery_commit':'15061c1cee0b779abca0ae39ae137a3595cf8684','before_SHA256':sha(beforep),'same_native060_raw_SHA256':sha(rawp),'new_SHA256':sha(out),'garment_source':'one complete same060 native blue shoulder, smooth identity-at-collar to existing-far-similarity surface; no new RGB or per-arm transform','existing_far_matrix_UNCHANGED':reg,'all_changed_pixels':int(changed.sum()),'changes_outside_whole_shoulder_domain':int(changed[~domain].sum()),'changes_protected_neck_collar_or_true_sleeve_exterior':int(changed[protection].sum()),'changes_arm_hand_anatomy':int(changed[anatomy].sum()),'changes_below_row513':int(changed[513:].sum()),'normal_size_actual_view':'PENDING','historical24f_overwritten':False}
(R/'SHOULDER_SOURCE_AND_LOCK_CHECK.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
