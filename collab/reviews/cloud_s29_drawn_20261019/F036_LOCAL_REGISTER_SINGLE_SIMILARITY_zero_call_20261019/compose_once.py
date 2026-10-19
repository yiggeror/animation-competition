from pathlib import Path
import json,hashlib,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as nd
R=Path(__file__).resolve().parent;B=R.parent;P=B/'F036_REBUILD_FROM_ACTUAL030_ZERO_CALL_v1_20261019'
rawp=B/'F036_LOCAL_ARM_LIP_NATIVE_call01_20261019/originals/S29_F036_LOCAL_ARM_LIP_call01_RAW_UNTOUCHED.png'
oldp=B/'F030_REPAIR_NATIVE_call01_20261019/originals/S29_F030_REPAIR_call01_RAW_UNTOUCHED.png'
raw=np.array(Image.open(rawp).convert('RGBA'));old=np.array(Image.open(oldp).convert('RGBA'));base=np.array(Image.open(P/'layers/ACTUAL030_CLOTH_CONTEXT_BASE_TECHNICAL_ONLY.png').convert('RGBA'));props=Image.open(P/'layers/TRUE_ORIGINAL_PROPS_SAME_COMMON030_COORDS.png').convert('RGBA');near=np.array(Image.open(P/'masks/NEAR_BARE_RIGHT_ARM_PROTECTED.png').convert('L'))>0
H,W=old.shape[:2];rh,rw=raw.shape[:2];yy,xx=np.indices((rh,rw));rgb=raw[:,:,:3].astype(float)
# One similarity, shared by the entire actual arm, all fingers/jade and cloth lip.
M=np.array([[.449105838,-.002299544,425.664761],[.002299544,.449105838,334.717910]])
def poly(pts,size=(rw,rh)):
 im=Image.new('L',size);ImageDraw.Draw(im).polygon(pts,fill=255);return np.array(im)>0
def save_mask(n,m):Image.fromarray(m.astype('uint8')*255).save(R/'masks'/n)
def layer(m):v=np.zeros_like(raw);v[m]=raw[m];return Image.fromarray(v)
def warp(im):
 v=np.array(im).astype('float32');v[:,:,:3]*=v[:,:,3:4]/255
 inv=np.linalg.inv(np.vstack([M,[0,0,1]]))[:2].reshape(-1)
 v=np.stack([np.array(Image.fromarray(v[:,:,k],mode='F').transform((W,H),Image.Transform.AFFINE,inv,Image.Resampling.BICUBIC)) for k in range(4)],axis=2)
 v=np.clip(v,0,255);a=v[:,:,3:4]/255;v[:,:,:3]=np.divide(v[:,:,:3],a,out=np.zeros_like(v[:,:,:3]),where=a>1e-6)
 return Image.fromarray(np.round(np.clip(v,0,255)).astype('uint8'))

# Select the complete actual skin+jade component, not a new silhouette or skin paint.
warm=(rgb[:,:,0]>rgb[:,:,2]+25)&(rgb[:,:,0]>100)&(rgb[:,:,1]>55);green=(rgb[:,:,1]>rgb[:,:,0]*1.05)&(rgb[:,:,1]>rgb[:,:,2]*1.04)&(rgb[:,:,1]>55)
roi=(xx>170)&(xx<900)&(yy>275)&(yy<805)
seed=nd.binary_dilation((warm|green)&roi,iterations=3);labs,n=nd.label(seed);lab=labs[500,500];arm=nd.binary_fill_holes(labs==lab)&(raw[:,:,3]>0)
# A blue sleeve seam band only, for overlap within the existing sleeve.
band=poly([(345,292),(438,323),(468,353),(234,588),(150,519),(263,365)])&(raw[:,:,3]>0)
arm|=band
clothroi=poly([(155,811),(375,842),(515,756),(624,685),(691,704),(760,771),(900,840),(1218,1050),(1218,1289),(0,1289),(0,945),(155,940)])
navy=(rgb[:,:,2]>rgb[:,:,0]+4)&(rgb[:,:,2]>rgb[:,:,1]+2);flower=(rgb.min(axis=2)>150)&((rgb.max(axis=2)-rgb.min(axis=2))<55)
cloth=clothroi&(navy|flower)&(raw[:,:,3]>0)&~arm
# True actual native front roll; raw generated gold, skin, rods and dark feathers excluded.
liproi=poly([(850,1000),(913,1005),(983,1048),(1055,1107),(1135,1169),(1218,1180),(1218,1289),(1020,1240),(939,1160),(860,1105),(816,1062)])
lip=cloth&liproi
for name,m in [('RAW_COMPLETE_FAR_ARM_JADE_AND_SLEEVE_BAND.png',arm),('RAW_CONTINUOUS_COTTON_MATERIAL_ONLY.png',cloth),('RAW_OPAQUE_SOFT_FRONT_LIP_ONLY.png',lip)]:save_mask(name,m)
armim=np.array(layer(arm));
# Feather only blue sleeve-material seams, never bare arm/jade/hand.
rawblue=(rgb[:,:,2]>rgb[:,:,0]+10)&(rgb[:,:,2]>rgb[:,:,1]+2)
seam=band&rawblue;dist=nd.distance_transform_edt(band)
armim[seam,3]=np.minimum(armim[seam,3],np.clip(dist[seam]/32,0,1)*armim[seam,3]).round().astype('uint8')
armw=warp(Image.fromarray(armim));clothw=warp(layer(cloth));lipw=warp(layer(lip));armw.save(R/'layers/ONE_M_WHOLE_ARM_JADE.png');clothw.save(R/'layers/ONE_M_ACTUAL_COTTON_BACK.png');lipw.save(R/'layers/ONE_M_ACTUAL_SOFT_LIP_FRONT.png')
# Remove withdrawn old030 far skin/jade, preserving actual030 chest and near arm.
oy,ox=np.indices((H,W));or_=old[:,:,:3].astype(float);oldwarm=(or_[:,:,0]>or_[:,:,2]+25)&(or_[:,:,0]>100)&(or_[:,:,1]>55);oldgreen=(or_[:,:,1]>or_[:,:,0]*1.05)&(or_[:,:,1]>or_[:,:,2]*1.04)&(or_[:,:,1]>55)
oldroi=poly([(520,485),(625,478),(740,520),(805,591),(810,693),(734,706),(653,641),(578,628),(532,590),(506,588)],(W,H))
clear=nd.binary_dilation((oldwarm|oldgreen)&oldroi,iterations=3)&~near
# Remove the obsolete blue cuff corner left outside the new actual opening.
old_cuff_corner=poly([(487,572),(510,570),(529,587),(514,598),(493,588)],(W,H))
old_blue=(or_[:,:,2]>or_[:,:,0]+10)&(or_[:,:,2]>or_[:,:,1]+2)
newarm_alpha=np.array(armw)[:,:,3]
corner=old_cuff_corner&old_blue&(newarm_alpha<128)&~near
clear|=corner
base[clear]=0;save_mask('OLD030_FAR_ARM_REMOVED.png',clear)
# Cotton is behind all real original props; actual front roll alone is in front.
out=Image.alpha_composite(Image.fromarray(base),clothw);out=Image.alpha_composite(out,armw);out=Image.alpha_composite(out,props)
real_before_lip=np.array(out)
feather=np.array(Image.open(P/'masks/TRUE_OUTER_FEATHER_LINES_COMMON030.png').convert('L'))>0
finite_outer=poly([(812,790),(873,790),(888,840),(812,840)],(W,H))
cover=feather&finite_outer&(np.array(lipw)[:,:,3]>=128)
prop_keep=(np.array(props)[:,:,3]>0)&~cover
out=Image.alpha_composite(out,lipw);v=np.array(out);v[prop_keep]=real_before_lip[prop_keep];v[near]=old[near];out=Image.fromarray(v)
save_mask('ONLY_ACTUAL_SOFT_LIP_ALLOWED_REAL_OUTER_FEATHER_COVER.png',cover)

out.save(R/'candidate/F036_SINGLE_SIMILARITY_NATIVE_ARM_AND_LIP_TRIAL.png')
common=np.array(Image.open(P/'audit/ACTUAL030_COMMON_TRUE_PROP_REFERENCE_NOT_NEW_DRAWING.png').convert('RGBA'));src=Image.fromarray(common)
def bg(im,col):b=Image.new('RGBA',im.size,col);b.alpha_composite(im);return b.convert('RGB')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',21)
for name,box in [('WHOLE_BODY_AND_PROPS',(0,0,1024,1536)),('WHOLE_ARM_PINCH',(470,415,825,735)),('TRUE_TAIL_LIP',(715,733,915,880)),('SLEEVE_ROOT',(480,450,670,645))]:
 a=bg(src,(237,240,242,255)).crop(box);b=bg(out,(237,240,242,255)).crop(box);panel=Image.new('RGB',(a.width*2,a.height+38),'#edf0f2');d=ImageDraw.Draw(panel);d.text((8,7),'030' if a.width<500 else 'ACTUAL030 COMMON / REAL PROPS',font=font,fill='#24364d');d.text((a.width+8,7),'036' if a.width<500 else 'F036 ONE SIMILARITY TRIAL',font=font,fill='#24364d');panel.paste(a,(0,38));panel.paste(b,(a.width,38));panel.save(R/'qa'/f'{name}_030_vs036_SAME_SCALE.png')
bg(out,(45,45,48,255)).save(R/'qa/F036_FULL_DARK.png')
ps=np.array([[399,352],[207,545],[672,729]],float);target=np.array([[619,493],[506,588],[724,660]],float);actual=ps@M[:,:2].T+M[:,2]
json.dump({'source_raw_sha256':hashlib.sha256(rawp.read_bytes()).hexdigest(),'single_similarity':M.tolist(),'source_manual_anchors':ps.tolist(),'target_soft_anchors':target.tolist(),'new_common_actual_pinch_reference_not_old670':True,'covered_real_outer_feather_pixels':int(cover.sum()),'mapped_anchors':actual.tolist(),'residuals_native_px':np.linalg.norm(actual-target,axis=1).tolist(),'scale':float(np.linalg.norm(M[:,0])),'rotation_deg':float(math.degrees(math.atan2(M[1,0],M[0,0]))),'near_protected_RGBA_changes':int(np.any(v[near]!=old[near],axis=1).sum()),'real_props_layer_resampled_or_moved':False,'no_new_generation':True,'status':'TRIAL_PENDING_ACTUAL_REVIEW'},open(R/'geometry/ONE_SIMILARITY_AND_SOURCE_CHECKS.json','w'),indent=2)
print(str(R/'candidate/F036_SINGLE_SIMILARITY_NATIVE_ARM_AND_LIP_TRIAL.png'))
