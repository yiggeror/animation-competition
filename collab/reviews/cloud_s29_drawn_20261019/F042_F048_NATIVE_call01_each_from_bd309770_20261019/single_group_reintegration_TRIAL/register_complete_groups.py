from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage as nd
import numpy as np,json,math,hashlib
R=Path(__file__).resolve().parent;Q=R.parent;B=Q.parent
P=B/'F036_REBUILD_FROM_ACTUAL030_ZERO_CALL_v1_20261019'
motherp=B/'F036_CONTINUOUS_SLEEVE_CLOTH_sameM_zero_call_20261019/candidate/F036_CONTINUOUS_SLEEVE_CLOTH_SAME_M_TRIAL.png'
src=np.array(Image.open(motherp).convert('RGBA'));H,W=src.shape[:2];yy,xx=np.indices((H,W))
near=np.array(Image.open(P/'masks/NEAR_BARE_RIGHT_ARM_PROTECTED.png').convert('L'))>0
prop=np.array(Image.open(P/'layers/TRUE_ORIGINAL_PROPS_SAME_COMMON030_COORDS.png').convert('RGBA'))[:,:,3]>0
feather=np.array(Image.open(P/'masks/TRUE_OUTER_FEATHER_LINES_COMMON030.png').convert('L'))>0
oldarm=np.array(Image.open(B/'F042_F048_FROM_LOCKED036_ZERO_CALL_TARGETS_20261019/masks/SOURCE_FAR_COMPLETE_ARM_SLEEVE_TO_WHOLE_HAND.png').convert('L'))>0
# No old036 hand/contact cloth patch is carried; only actual old skin/sleeve removed.
oldrgb=src[:,:,:3].astype(float);oldskin=(oldrgb[:,:,0]>oldrgb[:,:,2]+27)&(oldrgb[:,:,0]>110)&(oldrgb[:,:,1]>65);oldjade=(oldrgb[:,:,1]>oldrgb[:,:,0]*1.04)&(oldrgb[:,:,1]>oldrgb[:,:,2]*1.03)&(oldrgb[:,:,1]>50)
oldroi=(xx>500)&(xx<820)&(yy>485)&(yy<710)
oldseed=nd.binary_dilation((oldskin|oldjade)&oldroi,iterations=3);labs,_=nd.label(oldseed);k=np.bincount(labs.ravel())[1:].argmax()+1;oldphysical=nd.binary_fill_holes(labs==k)&(src[:,:,3]>0)
oldarm=oldphysical&~near # withdraw only true old skin/jade/ink, never old blue garment

def poly(pts):
 im=Image.new('L',(W,H));ImageDraw.Draw(im).polygon(pts,fill=255);return np.array(im)>0

def similarity(S,T):
 S=np.array(S,float);T=np.array(T,float);w=np.array([.5,.5,1.]);a=np.average(S,axis=0,weights=w);b=np.average(T,axis=0,weights=w);X=S-a;Y=T-b;U,sv,Vt=np.linalg.svd(X.T@(Y*w[:,None]));r=U@Vt;s=sv.sum()/(w[:,None]*X*X).sum();L=(r*s).T;t=b-L@a;M=np.column_stack([L,t]);return M,S@L.T+t,s

def warp(v,M):
 v=v.astype('float32');v[:,:,:3]*=v[:,:,3:4]/255;inv=np.linalg.inv(np.vstack([M,[0,0,1]]))[:2].reshape(-1)
 z=np.stack([np.array(Image.fromarray(v[:,:,k],mode='F').transform((W,H),Image.Transform.AFFINE,inv,Image.Resampling.BICUBIC)) for k in range(4)],2);z=np.clip(z,0,255);a=z[:,:,3:4]/255;z[:,:,:3]=np.divide(z[:,:,:3],a,out=np.zeros_like(z[:,:,:3]),where=a>1e-6);return np.round(np.clip(z,0,255)).astype('uint8')

def mask_save(f,n,m):Image.fromarray(m.astype('uint8')*255).save(R/'masks'/f'F{f:03d}_{n}.png')
def extract(v,m):z=np.zeros_like(v);z[m]=v[m];return z

def gray(v):
 b=Image.new('RGBA',(W,H),(236,239,242,255));b.alpha_composite(Image.fromarray(v));return b.convert('RGB')

cases=[(42,[[616,502],[532,574],[751,684]],[[604,494],[517,562],[718.7875,662.6614]]),(48,[[602,501],[518,575],[711,680]],[[604,494],[517,562],[711.7875,661.6614]])]
reports=[]
for f,S,T in cases:
 rawp=Q/f'F{f:03d}'/'originals'/f'S29_F{f:03d}_call01_RAW_UNTOUCHED.png';raw=np.array(Image.open(rawp).convert('RGBA'));rgb=raw[:,:,:3].astype(float)
 M,actual,s=similarity(S,T)
 warm=(rgb[:,:,0]>rgb[:,:,2]+25)&(rgb[:,:,0]>110)&(rgb[:,:,1]>60);jade=(rgb[:,:,1]>rgb[:,:,0]*1.04)&(rgb[:,:,1]>rgb[:,:,2]*1.03)&(rgb[:,:,1]>50)
 roi=(xx>490)&(xx<850)&(yy>480)&(yy<735)&(raw[:,:,3]>0);lab,n=nd.label(nd.binary_dilation((warm|jade)&roi,iterations=3));cnt=np.bincount(lab.ravel());cnt[0]=0;arm=nd.binary_fill_holes(lab==cnt.argmax())&(raw[:,:,3]>0)
 band=poly([(470,455),(580,445),(640,500),(550,585),(496,592),(470,540)])&(raw[:,:,3]>0);arm|=band
 px,py=S[2]
 # One whole continuous native cloth sheet, no navy/flower per-pixel selection.
 cloth=poly([(500,700),(590,714),(680,674),(px,py-2),(850,730),(974,815),(1010,950),(984,1048),(835,1075),(778,1030),(600,1018),(400,954),(257,887),(308,802),(358,760)])&(raw[:,:,3]>0)&~arm
 # Exclude complete generated puppet body/tail/stem/rod context before registration.
 fake=poly([(330,738),(490,726),(620,735),(746,748),(815,785),(888,839),(845,847),(780,819),(700,815),(590,820),(475,818),(385,800),(330,780)])
 fake|=poly([(265,824),(420,815),(555,845),(580,919),(458,930),(260,903)])
 fake|=poly([(610,790),(658,790),(659,892),(606,892)])
 gold=(rgb[:,:,0]>rgb[:,:,2]*1.25)&(rgb[:,:,1]>rgb[:,:,2]*1.12)&(rgb[:,:,0]>90)
 fake|=nd.binary_dilation(gold&cloth,iterations=7);cloth&=~fake
 front=cloth&poly([(px-10,py-3),(px+45,py+25),(975,820),(1010,950),(930,990),(825,882),(750,800),(660,742)])
 aw=warp(extract(raw,arm),M);cw=warp(extract(raw,cloth),M);fw=warp(extract(raw,front),M)
 # Only sleeve-root overlap and new full arm; locked collar/main chest retained.
 isband=warp(extract(raw,band),M)[:,:,3]>0
 # Complete new cuff kept; fade inside existing chest cloth only, no rectangular clearance.
 upper=np.clip((yy-465)/20,0,1);horizontal=np.clip((xx-495)/40,0,1);down=np.clip((yy-520)/40,0,1)
 factor=upper*(horizontal+(1-horizontal)*down)
 aw[isband,3]=np.round(aw[isband,3]*factor[isband]).astype('uint8')
 # Material-only feather at internal cloth boundaries; all one M remains unchanged.
 inside=(src[:,:,3]>=240)&(yy>=710)&~prop&~near;dist=nd.distance_transform_edt(cw[:,:,3]>0);a=np.clip(dist/12,0,1);cw[inside,3]=np.round(cw[inside,3]*a[inside]).astype('uint8')
 base=src.copy();base[oldarm]=0
 # Same locked036 cotton backing below the new continuous cloth, not new RGB.
 # Full patch only behind the shallow top-band gap; near C1 restored exactly later.
 backing=np.zeros_like(src);backing[690:728,505:605]=src[700:738,650:750]
 # Backing is confined to actual bounded seam gaps, not an opaque rectangular flap.
 coverage=(base[:,:,3]>128)|(cw[:,:,3]>128)|(aw[:,:,3]>128)
 closed=nd.binary_closing(coverage,iterations=9)
 seam_only=(closed|nd.binary_fill_holes(coverage))&~coverage
 backing[~seam_only]=0
 mask_save(f,'ONLY_BOUNDED_CLOTH_BACKING_SEAM_GAP',backing[:,:,3]>0)
 base=np.array(Image.alpha_composite(Image.fromarray(base),Image.fromarray(backing)))
 # Keep original036 continuous cotton backing, then new complete native sheet and arm.
 out=Image.alpha_composite(Image.fromarray(base),Image.fromarray(cw));out=Image.alpha_composite(out,Image.fromarray(aw));v=np.array(out)
 allow=feather&(xx>=780)&(xx<=885)&(yy>=775)&(yy<=850)&(fw[:,:,3]>=240)
 keep=prop&~allow;v[keep]=src[keep];v[near]=src[near]
 fixed=(yy<470)|((xx<490)&(yy<650));v[fixed]=src[fixed]
 path=R/'candidate'/f'F{f:03d}_ONE_SIMILARITY_COMPLETE_ARM_CLOTH_TRIAL.png';Image.fromarray(v).save(path);g=gray(v);g.save(R/f'F{f:03d}_FULL_ON_GRAY.png')
 for label,box in [('COMPLETE_SLEEVE_PINCH_TRUE_TAIL',(480,455,940,900))]:
  im=g.crop(box);im.resize((im.width*2,im.height*2)).save(R/'contacts'/f'F{f:03d}_{label}.png')
 for n,m in [('RAW_COMPLETE_FAR_ARM_AND_SLEEVE',arm),('RAW_CONTINUOUS_COTTON',cloth),('RAW_GENERATED_PUPPET_ROD_EXCLUSION',fake),('ONLY_FINITE_REAL_FEATHER_COVER',allow)]:mask_save(f,n,m)
 reports.append({'frame':f,'raw_sha256':hashlib.sha256(rawp.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'single_similarity_complete_arm_hand_and_cloth':M.tolist(),'scale':float(s),'rotation_deg':math.degrees(math.atan2(M[1,0],M[0,0])),'manual_source_cuff_endpoints_and_pinch':S,'soft_target_cuff_endpoints_and_pinch':T,'mapped_anchors':actual.tolist(),'residuals_px':np.linalg.norm(actual-np.array(T),axis=1).tolist(),'readpoint_error':'manual visible seam/pinch +/-3px; not measured bones','near_C1_RGBA_changed':int(np.any(v[near]!=src[near],axis=1).sum()),'fixed_head_collar_main_chest_RGBA_changed':int(np.any(v[fixed]!=src[fixed],axis=1).sum()),'props_except_finite_feather_RGBA_changed':int(np.any(v[keep]!=src[keep],axis=1).sum()),'no_extra_generation':True,'same036_cotton_backing':{'source_crop':[650,700,750,738],'paste_bbox':[505,690,605,728],'scale':1},'mask_revision':'one semantic correction, same fitted M unchanged','status':'TRIAL_PENDING_ACTUAL_REVIEW_NOT_ADOPTED'})
json.dump({'only_locked_body_source_sha256':hashlib.sha256(motherp.read_bytes()).hexdigest(),'rule':'Each whole arm/jade/palm/fingers and connected opaque cloth use one similarity. No separate palm/finger/lip fitting. Props restored from same-coordinate locked036 composition.','reports':reports},open(R/'geometry/ONE_GROUP_PER_STATE_SOURCE_MATRIX_CHECKS.json','w'),indent=2)
print(json.dumps(reports,indent=2))
