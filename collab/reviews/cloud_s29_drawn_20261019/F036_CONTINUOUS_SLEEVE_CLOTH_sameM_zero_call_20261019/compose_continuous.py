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
bl=(rgb[:,:,2]>rgb[:,:,0]+10)&(rgb[:,:,2]>rgb[:,:,1]+2)&(xx<460)&(yy<790)&(raw[:,:,3]>0)
bl=nd.binary_closing(bl,iterations=3);blabs,_=nd.label(bl)
band=nd.binary_fill_holes(blabs==blabs[300,150])&(raw[:,:,3]>0)
arm|=band
# Continuous source cotton sheet: no per-pixel navy/flower threshold.
# Explicit fake puppet/feather/rod exclusion; the locked030 cotton remains below.
clothroi=poly([(155,811),(375,842),(515,756),(624,685),(691,704),(760,771),(900,840),(1060,934),(1218,1070),(1218,1289),(0,1289),(0,945),(155,940)])
fakepuppet=poly([(0,875),(255,870),(440,885),(600,892),(720,905),(806,930),(885,972),(957,1046),(910,1040),(840,1015),(740,1005),(550,1045),(350,1065),(145,1045),(0,1010)])
# Actual generated rods/stem are excluded as complete source shapes, not RGB paint.
fake_rod1=poly([(643,1018),(664,1025),(1218,1289),(1178,1289)])
fake_rod2=poly([(391,1041),(408,1042),(953,1289),(912,1289)])
fake_stem=poly([(423,1030),(498,1035),(500,1262),(355,1262),(355,1238),(427,1229)])
fake_turtle=poly([(0,1130),(113,1146),(255,1241),(265,1289),(0,1289)])
gold=(rgb[:,:,0]>rgb[:,:,2]*1.25)&(rgb[:,:,1]>rgb[:,:,2]*1.12)&(rgb[:,:,0]>90)
excluded=fakepuppet|fake_rod1|fake_rod2|fake_stem|fake_turtle|nd.binary_dilation(gold&clothroi,iterations=8)
cloth=clothroi&~excluded&(raw[:,:,3]>0)&~arm
# Full continuous front fold from pinch, over ridge and thick lip, to right edge.
# It only overrides the finite original outer-feather segment permitted below.
liproi=poly([(624,685),(690,710),(820,812),(951,903),(1105,1010),(1218,1070),(1218,1289),(1100,1289),(1000,1190),(885,1080),(816,1062),(760,980),(675,888),(590,805)])
lip=cloth&liproi
save_mask('RAW_GENERATED_PUPPETS_RODS_EXCLUDED.png',excluded)
for name,m in [('RAW_COMPLETE_FAR_ARM_JADE_AND_SLEEVE_BAND.png',arm),('RAW_CONTINUOUS_COTTON_MATERIAL_ONLY.png',cloth),('RAW_OPAQUE_SOFT_FRONT_LIP_ONLY.png',lip)]:save_mask(name,m)
armim=np.array(layer(arm));
# Feather only blue sleeve-material seams, never bare arm/jade/hand.
rawblue=(rgb[:,:,2]>rgb[:,:,0]+10)&(rgb[:,:,2]>rgb[:,:,1]+2)
# Fade only the body-side interior overlap, not the full cuff/blue triangle.
# Raw sleeve lower triangle and the actual cuff contour remain intact.
interior=(xx<210)&(yy<440)&band
fade=np.clip((xx-75)/90,0,1)
armim[interior,3]=(armim[interior,3]*fade[interior]).round().astype('uint8')
# Whole raw sleeve/body overlap may only stay within the locked old garment;
# the real new cuff/skin lower contour is retained as one actual source shape.
armw=warp(Image.fromarray(armim));aw=np.array(armw)
oy0,ox0=np.indices((H,W));oldrgb0=old[:,:,:3].astype(float)
oldblue0=(oldrgb0[:,:,2]>oldrgb0[:,:,0]+8)&(oldrgb0[:,:,2]>oldrgb0[:,:,1]+1)&(old[:,:,3]>0)
oldgarment=nd.binary_fill_holes(nd.binary_closing(oldblue0,iterations=3))
newskinw=np.array(warp(layer(arm&~band)))[:,:,3]>0
# Preserve complete source shoulder/chest silhouette; no new body outline.
restrict=(oy0<500)&(old[:,:,3]==0)&~newskinw
# Neck/collar and main chest stay original030; blend only inside garment near sleeve.
blue_native=np.array(warp(layer(band)))[:,:,3]>0
# Only sleeve-root internal overlap; original collar and main chest are untouched.
permit=((oy0>=480)&(ox0>=535))|((oy0>=550)&(ox0>=490))
# Smooth only this interior material seam, retaining the complete cuff below.
blend=nd.distance_transform_edt(permit);factor=np.clip(blend/10,0,1)
aw[blue_native,3]=(aw[blue_native,3]*factor[blue_native]).round().astype('uint8')
aw[restrict]=0
armw=Image.fromarray(aw)
clothw=warp(layer(cloth));lipw=warp(layer(lip));armw.save(R/'layers/ONE_M_WHOLE_ARM_JADE.png');clothw.save(R/'layers/ONE_M_ACTUAL_COTTON_BACK.png');lipw.save(R/'layers/ONE_M_ACTUAL_SOFT_LIP_FRONT.png')
# Remove withdrawn old030 far skin/jade, preserving actual030 chest and near arm.
oy,ox=np.indices((H,W));or_=old[:,:,:3].astype(float);oldwarm=(or_[:,:,0]>or_[:,:,2]+25)&(or_[:,:,0]>100)&(or_[:,:,1]>55);oldgreen=(or_[:,:,1]>or_[:,:,0]*1.05)&(or_[:,:,1]>or_[:,:,2]*1.04)&(or_[:,:,1]>55)
oldroi=poly([(520,485),(625,478),(740,520),(805,591),(810,693),(734,706),(653,641),(578,628),(532,590),(506,588)],(W,H))
clear=nd.binary_dilation((oldwarm|oldgreen)&oldroi,iterations=8)&~near
# Remove the obsolete blue cuff corner left outside the new actual opening.
old_cuff_corner=poly([(487,568),(517,566),(548,595),(535,609),(512,599),(493,589)],(W,H))
old_blue=(or_[:,:,2]>or_[:,:,0]+10)&(or_[:,:,2]>or_[:,:,1]+2)
newarm_alpha=np.array(armw)[:,:,3]
corner=old_cuff_corner&old_blue&(newarm_alpha<128)&~near
clear|=corner
# The entire obsolete skin/ink opening is withdrawn, including low-alpha old outline.
clear|=oldroi&(old[:,:,3]>0)&~oldgarment&~near
base[clear]=0;save_mask('OLD030_FAR_ARM_REMOVED.png',clear)
# One continuous actual030 cotton underlay below the new lip, never source RGB paint.
# It replaces the previous technical-context residual generated feather, below all true props.
under=np.zeros_like(old);donor=old[700:738,650:735].copy();under[792:830,790:875]=donor
underim=Image.fromarray(under);underim.save(R/'layers/LOCKED030_CONTINUOUS_REAL_COTTON_UNDERLAY.png')
base=np.array(Image.alpha_composite(Image.fromarray(base),underim))

# Cotton is behind all real original props; actual front roll alone is in front.
out=Image.alpha_composite(Image.fromarray(base),clothw);out=Image.alpha_composite(out,armw);out=Image.alpha_composite(out,props)
real_before_lip=np.array(out)
feather=np.array(Image.open(P/'masks/TRUE_OUTER_FEATHER_LINES_COMMON030.png').convert('L'))>0
finite_outer=poly([(812,790),(873,790),(888,840),(812,840)],(W,H))
cover=feather&finite_outer&(np.array(lipw)[:,:,3]>=128)
prop_keep=(np.array(props)[:,:,3]>0)&~cover
out=Image.alpha_composite(out,lipw);v=np.array(out);v[prop_keep]=real_before_lip[prop_keep];v[near]=old[near];out=Image.fromarray(v)
save_mask('ONLY_ACTUAL_SOFT_LIP_ALLOWED_REAL_OUTER_FEATHER_COVER.png',cover)

out.save(R/'candidate/F036_CONTINUOUS_SLEEVE_CLOTH_SAME_M_TRIAL.png')
def bg(im,col):
 b=Image.new('RGBA',im.size,col);b.alpha_composite(im);return b.convert('RGB')
gray=bg(out,(237,240,242,255));gray.save(R/'01_FULL_ON_GRAY.png')
for name,box in [('03_SLEEVE_CLOSEUP.png',(480,450,670,645)),('04_CLOTH_LIP_CLOSEUP.png',(715,733,915,880))]:
 c=gray.crop(box);c.resize((c.width*3,c.height*3)).save(R/name)
ps=np.array([[399,352],[207,545],[672,729]],float);target=np.array([[619,493],[506,588],[724,660]],float);actual=ps@M[:,:2].T+M[:,2]
json.dump({'source_raw_sha256':hashlib.sha256(rawp.read_bytes()).hexdigest(),'single_similarity':M.tolist(),'source_manual_anchors':ps.tolist(),'target_soft_anchors':target.tolist(),'new_common_actual_pinch_reference_not_old670':True,'covered_real_outer_feather_pixels':int(cover.sum()),'mapped_anchors':actual.tolist(),'residuals_native_px':np.linalg.norm(actual-target,axis=1).tolist(),'scale':float(np.linalg.norm(M[:,0])),'rotation_deg':float(math.degrees(math.atan2(M[1,0],M[0,0]))),'near_protected_RGBA_changes':int(np.any(v[near]!=old[near],axis=1).sum()),'real_props_layer_resampled_or_moved':False,'no_new_generation':True,'status':'ZERO_CALL_CONTINUOUS_SOURCE_TRIAL_PENDING_ACTUAL_REVIEW','raw_generated_material_exclusion_pixels':int(excluded.sum()),'continuous_cloth_no_palette_pixel_filter':True},open(R/'geometry/ONE_SIMILARITY_AND_SOURCE_CHECKS.json','w'),indent=2)
print(str(R/'candidate/F036_CONTINUOUS_SLEEVE_CLOTH_SAME_M_TRIAL.png'))
