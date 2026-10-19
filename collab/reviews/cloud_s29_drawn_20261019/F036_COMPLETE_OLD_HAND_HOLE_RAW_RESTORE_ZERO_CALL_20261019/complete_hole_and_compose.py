from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage as nd
from scipy.spatial import Delaunay
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;B=R.parent;repo=R.parents[3]
PRE=B/'F036_SAME_MASTER_MAP042048_SCENE13_ZERO_CALL_20261019'
M=B/'F036_FULL_FOLD_SAME_RAW_ZERO_CALL_20261019'
S=B/'F036_CONTINUOUS_SLEEVE_CLOTH_sameM_zero_call_20261019'
N=B/'F042_F048_NATIVE_call01_each_from_bd309770_20261019'
G=N/'single_group_reintegration_TRIAL'
def rgba(p):return np.array(Image.open(p).convert('RGBA'))
def mask(p):return np.array(Image.open(p).convert('L'))>0
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def gray(a):
 g=Image.new('RGBA',(1024,1536),(236,239,242,255));g.alpha_composite(Image.fromarray(a));return g.convert('RGB')
def warp_pillow(a,A):
 v=a.astype('float32');v[:,:,:3]*=v[:,:,3:4]/255
 inv=np.linalg.inv(np.vstack([A,[0,0,1]]))[:2].reshape(-1)
 z=np.stack([np.array(Image.fromarray(v[:,:,k],mode='F').transform((1024,1536),Image.Transform.AFFINE,inv,Image.Resampling.BICUBIC))for k in range(4)],2)
 z=np.clip(z,0,255);alpha=z[:,:,3:4]/255;z[:,:,:3]=np.divide(z[:,:,:3],alpha,out=np.zeros_like(z[:,:,:3]),where=alpha>1e-6)
 return np.rint(np.clip(z,0,255)).astype('uint8')

rawp=B/'F036_SINGLE_CLEAN_CLOTH_MASTER_NATIVE_CALL01_20261019/RAW_UNTOUCHED.png';raw=rgba(rawp)
masterp=M/'F036_COMPLETE_FOLD_CLOTH_RGBA.png';before=rgba(masterp);master=before.copy()
human=mask(B/'F036_SINGLE_CLEAN_CLOTH_MASTER_INPUT_GATE_ZERO_CALL_20261019/HUMAN_BLACK_PROTECTION_GEOMETRY.png')
yy,xx=np.indices((1536,1024));contact_source=(xx>=680)&(xx<=790)&(yy>=630)&(yy<=710)
oldhole=human&contact_source&(before[:,:,3]<128)
# The complete old hand-hole, including its AA arcs and contact rim, is one
# cloth domain. No old opaque-hand-core restriction, no old-hole reclip later.
whole_domain=nd.binary_dilation(oldhole,iterations=4)&contact_source
available=whole_domain&(raw[:,:,3]>0)
master[available]=raw[available]
# Alpha around250 is genuine opaque source cotton; keep the source RGB exact.
# Partial source alpha below128 remains the real outside silhouette AA/air.
solid=available&(raw[:,:,3]>=128);master[solid,3]=255
Image.fromarray(master).save(R/'ONE036_COMPLETE_OLD_HOLE_CLOTH_MASTER_RGBA.png')
Image.fromarray((whole_domain*255).astype('uint8')).save(R/'COMPLETE_OLD_HOLE_AND_AA_DOMAIN.png')
Image.fromarray((available*255).astype('uint8')).save(R/'ONLY_ACTUAL_RAW_MATERIAL_ADDED.png')
Image.fromarray((whole_domain&(raw[:,:,3]==0)).astype('uint8')*255).save(R/'RAW_HAS_NO_SOURCE_OUTSIDE_SILHOUETTE.png')
masterout=R/'ONE036_COMPLETE_OLD_HOLE_CLOTH_MASTER_RGBA.png';premul=master.astype(float);premul[:,:,:3]*=premul[:,:,3:4]/255
compose_roi=(xx>=660)&(xx<=810)&(yy>=610)&(yy<=725)
rows=[];states=[];report=[]
for f in [36,42,48]:
 d=R/f'F{f:03d}';d.mkdir(exist_ok=True)
 if f==36:
  cloth=master.copy();previousp=M/'F036_SAME_RAW_REINTEGRATED_RGBA.png';previous=rgba(previousp)
  armp=S/'layers/ONE_M_WHOLE_ARM_JADE.png';arm=rgba(armp)
  matrix=json.loads((S/'geometry/ONE_SIMILARITY_AND_SOURCE_CHECKS.json').read_text())['single_similarity'];mapping='identity036'
 else:
  oldreport=json.loads((PRE/f'F{f:03d}/MAPPING_CHECK.json').read_text());src=np.array(oldreport['source_landmarks']);target=np.array(oldreport['target_landmarks']);matrix=oldreport['arm_M_UNCHANGED']
  tri=Delaunay(target);points=np.column_stack([xx.ravel(),yy.ravel()]);si=tri.find_simplex(points);assert np.all(si>=0)
  b2=np.einsum('ijk,ik->ij',tri.transform[si,:2],points-tri.transform[si,2]);b=np.column_stack([b2,1-b2.sum(1)])
  co=np.einsum('ij,ijk->ik',b,src[tri.simplices[si]]).reshape(1536,1024,2)
  z=np.stack([nd.map_coordinates(premul[:,:,k],[co[:,:,1],co[:,:,0]],order=1,mode='constant',cval=0)for k in range(4)],2)
  z[:,:,:3]=np.divide(z[:,:,:3],z[:,:,3:4]/255,out=np.zeros_like(z[:,:,:3]),where=z[:,:,3:4]>1e-5);cloth=np.rint(np.clip(z,0,255)).astype('uint8');cloth[cloth[:,:,3]==0]=0
  previousp=PRE/f'F{f:03d}/SAME036_MAPPED_REINTEGRATED_RGBA.png';previous=rgba(previousp)
  armp=N/f'F{f:03d}/originals/S29_F{f:03d}_call01_RAW_UNTOUCHED.png';armraw=rgba(armp)
  am=mask(G/f'masks/F{f:03d}_RAW_COMPLETE_FAR_ARM_AND_SLEEVE.png');a=np.zeros_like(armraw);a[am]=armraw[am]
  arm=warp_pillow(a,np.array(matrix));mapping='exact previous38f59c2d cloth mesh; no new fit'
 # Only current REAL arm/finger source alpha is composited over the completed
 # material. Never restore the old human binary cutout or precomposited void.
 combined=np.array(Image.alpha_composite(Image.fromarray(cloth),Image.fromarray(arm)))
 out=previous.copy();out[compose_roi]=combined[compose_roi]
 Image.fromarray(cloth).save(d/'FROM_ONE_COMPLETE_MASTER_CLOTH_RGBA.png')
 Image.fromarray(arm).save(d/'EXACT_CURRENT_ARM_FOREGROUND_RGBA.png')
 Image.fromarray(out).save(d/'CURRENT_FINGER_ALPHA_OVER_COMPLETE_CLOTH_RGBA.png')
 gray(out).save(d/'FULL_ON_GRAY.png')
 box=(680,625,790,710)
 gray(previous).crop(box).save(d/'BEFORE_PINCH_NORMAL_SIZE.png');gray(out).crop(box).save(d/'AFTER_PINCH_NORMAL_SIZE.png')
 change=np.any(out!=previous,2)
 r={'frame':f,'generation_calls':0,'one_master_SHA256':sha(masterout),'source_arm_RGBA_path':str(armp),'source_arm_SHA256':sha(armp),'exact_existing_arm_M':matrix,'mapping':mapping,'current_foreground_alpha_reused':True,'old_human_hole_reapplied':False,'RGBA_changes_outside_contact_ROI':int((change&~compose_roi).sum()),'contact_ROI':[660,610,811,726],'output_SHA256':sha(d/'CURRENT_FINGER_ALPHA_OVER_COMPLETE_CLOTH_RGBA.png'),'old_pinches_and_M_not_refit':True,'status':'PENDING_ACTUAL_NORMAL_SIZE_REVIEW'}
 (d/'SOURCE_AND_COMPOSITION_CHECK.json').write_text(json.dumps(r,indent=2)+'\n');report.append(r)
 p=d/'CURRENT_FINGER_ALPHA_OVER_COMPLETE_CLOTH_RGBA.png';states.append({'state':f,'used':str(p),'usedURL':'/'+str(p.relative_to(repo)),'sha256':sha(p)})

sh=Image.new('RGB',(660,250),(236,239,242));dr=ImageDraw.Draw(sh)
for i,f in enumerate([36,42,48]):
 d=R/f'F{f:03d}'
 for j,n in enumerate(['BEFORE_PINCH_NORMAL_SIZE.png','AFTER_PINCH_NORMAL_SIZE.png']):
  im=Image.open(d/n);sh.paste(im,(i*220+5,j*115+30));dr.text((i*220+5,j*115+8),f'{f:03d} '+['BEFORE1:1','AFTER1:1'][j],fill='black')
sh.save(R/'THREE_PINCHES_BEFORE_AFTER_NORMAL_SIZE.png')
zoom=Image.new('RGB',(1320,720),(236,239,242));dr=ImageDraw.Draw(zoom)
for i,f in enumerate([36,42,48]):
 for j,n in enumerate(['BEFORE_PINCH_NORMAL_SIZE.png','AFTER_PINCH_NORMAL_SIZE.png']):
  im=Image.open(R/f'F{f:03d}'/n);zoom.paste(im.resize((440,340)),(i*440,j*360+20));dr.text((i*440+8,j*360+4),f'{f:03d} '+['BEFORE4X','AFTER4X'][j],fill='black')
zoom.save(R/'THREE_PINCHES_BEFORE_AFTER_4X.png')
meta={'generation_calls':0,'baseline_commit':'38f59c2d','source_raw_SHA256':sha(rawp),'original_master_SHA256':sha(masterp),'complete_master_SHA256':sha(masterout),'complete_old_hole_domain_pixels':int(whole_domain.sum()),'same_raw_source_pixels_used':int(available.sum()),'raw_RGB_changes_on_source_pixels':int(np.any(master[available,:3]!=raw[available,:3],1).sum()),'source_opaque_alpha_normalized_pixels':int(solid.sum()),'raw_alpha0_points_never_invented':int((whole_domain&(raw[:,:,3]==0)).sum()),'old_master_RGBA_changes_outside_complete_hole_domain':int(np.any(master[~whole_domain]!=before[~whole_domain],1).sum()),'pose_generation_or_tiling':False,'states':report}
(R/'COMPLETE_HOLE_SOURCE_CHECK.json').write_text(json.dumps(meta,indent=2)+'\n')
plan=json.loads((PRE/'SOURCES_EXPOSURE_AND_T_LAYER.json').read_text());plan['sources']=states;plan['one_shared_master_SHA256']=sha(masterout)
(R/'SOURCES_EXPOSURE_AND_T_LAYER.json').write_text(json.dumps(plan,indent=2)+'\n')
print(json.dumps({k:v for k,v in meta.items()if k!='states'},indent=2))
