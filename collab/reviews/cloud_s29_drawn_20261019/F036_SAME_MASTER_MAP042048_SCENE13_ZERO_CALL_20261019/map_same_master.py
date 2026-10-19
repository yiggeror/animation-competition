from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage as nd
from scipy.spatial import Delaunay
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;B=R.parent;repo=R.parents[3]
M=B/'F036_FULL_FOLD_SAME_RAW_ZERO_CALL_20261019'
G=B/'F042_F048_NATIVE_call01_each_from_bd309770_20261019/single_group_reintegration_TRIAL'
Q=B/'F042_F048_SINGLE_WHOLE_CLOTH_REPAINT_20261019'
P=B/'F036_REBUILD_FROM_ACTUAL030_ZERO_CALL_v1_20261019'
S=B/'F036_CONTINUOUS_SLEEVE_CLOTH_sameM_zero_call_20261019'
def rgba(p):return np.array(Image.open(p).convert('RGBA'))
def mask(p):return np.array(Image.open(p).convert('L'))>0
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def gray(a):
 g=Image.new('RGBA',(1024,1536),(236,239,242,255));g.alpha_composite(Image.fromarray(a));return g.convert('RGB')
masterp=M/'F036_COMPLETE_FOLD_CLOTH_RGBA.png';master=rgba(masterp)
oldp=S/'candidate/F036_CONTINUOUS_SLEEVE_CLOTH_SAME_M_TRIAL.png';old=rgba(oldp)
oldface=mask(B/'F036_SINGLE_CLEAN_CLOTH_MASTER_INPUT_GATE_ZERO_CALL_20261019/WHOLE_LOCKED036_CLOTH_DOMAIN.png')
props=mask(P/'layers/TRUE_ORIGINAL_PROPS_SAME_COMMON030_COORDS.png')
reports=json.loads((G/'geometry/ONE_GROUP_PER_STATE_SOURCE_MATRIX_CHECKS.json').read_text())['reports']
fy=663.66135947;fx=725.78751656
# A small continuous deformation of the same036 sheet, driven only by the frozen
# far pinch. Do not force the independently generated old042/048 fold silhouettes
# onto this material. Supported C1, ridge end, lip/T and lower/outer sheet stay.
src=np.array([(x,y)for y in [0,470,fy,747,878,1100,1535]for x in [0,256,499,fx,884,1023]]+[(842,807),(499,747),(884,878)],float)
src=np.unique(src,axis=0)
weight=np.maximum(0,1-np.abs(src[:,0]-fx)/240)**2*np.maximum(0,1-np.abs(src[:,1]-fy)/270)**2
weight*=np.minimum(1,np.abs(src[:,0]-499)/(fx-499))
weight[(src[:,1]>=878)|((src[:,0]==842)&(src[:,1]==807))]=0
oldrgb=old[:,:,:3].astype(float)
skin=(oldrgb[:,:,0]>oldrgb[:,:,2]+27)&(oldrgb[:,:,0]>110)&(oldrgb[:,:,1]>65)
jade=(oldrgb[:,:,1]>oldrgb[:,:,0]*1.04)&(oldrgb[:,:,1]>oldrgb[:,:,2]*1.03)&(oldrgb[:,:,1]>50)
yy,xx=np.indices((1536,1024));seed=nd.binary_dilation((skin|jade)&(xx>500)&(xx<820)&(yy>485)&(yy<710),iterations=3)
labels,n=nd.label(seed);counts=np.bincount(labels.ravel());counts[0]=0;oldarm=nd.binary_fill_holes(labels==counts.argmax())&(old[:,:,3]>0)
near=mask(P/'masks/NEAR_BARE_RIGHT_ARM_PROTECTED.png');oldarm&=~near
state_sources=[{'state':36,'used':str(M/'F036_SAME_RAW_REINTEGRATED_RGBA.png'),'usedURL':'/'+str((M/'F036_SAME_RAW_REINTEGRATED_RGBA.png').relative_to(repo)),'sha256':sha(M/'F036_SAME_RAW_REINTEGRATED_RGBA.png')}]
premul=master.astype(float);premul[:,:,:3]*=premul[:,:,3:4]/255
points=np.column_stack([xx.ravel(),yy.ravel()]);summaries=[]
for f in [42,48]:
 d=R/f'F{f:03d}';d.mkdir(exist_ok=True);r=next(v for v in reports if v['frame']==f)
 pinch=np.array(r['mapped_anchors'][2]);delta=pinch-[fx,fy];target=src+weight[:,None]*delta
 tri=Delaunay(target);sv=src[tri.simplices];tv=target[tri.simplices]
 sd=np.linalg.det(np.stack([sv[:,1]-sv[:,0],sv[:,2]-sv[:,0]],2));td=np.linalg.det(np.stack([tv[:,1]-tv[:,0],tv[:,2]-tv[:,0]],2))
 assert np.all(sd*td>0),'inverted small-motion cloth triangle'
 simplex=tri.find_simplex(points);assert np.all(simplex>=0)
 b2=np.einsum('ijk,ik->ij',tri.transform[simplex,:2],points-tri.transform[simplex,2]);b=np.column_stack([b2,1-b2.sum(1)])
 co=np.einsum('ij,ijk->ik',b,src[tri.simplices[simplex]]).reshape(1536,1024,2)
 z=np.stack([nd.map_coordinates(premul[:,:,k],[co[:,:,1],co[:,:,0]],order=1,mode='constant',cval=0)for k in range(4)],2)
 z[:,:,:3]=np.divide(z[:,:,:3],z[:,:,3:4]/255,out=np.zeros_like(z[:,:,:3]),where=z[:,:,3:4]>1e-5)
 cloth=np.rint(np.clip(z,0,255)).astype('uint8');cloth[cloth[:,:,3]==0]=0
 basep=G/f'candidate/F{f:03d}_ONE_SIMILARITY_COMPLETE_ARM_CLOTH_TRIAL.png';frozen=rgba(basep)
 human=mask(Q/f'F{f:03d}/HUMANS_PROTECTED_COORDINATES.png')
 base=old.copy();base[oldface|oldarm]=0
 base[human]=frozen[human]
 out=np.array(Image.alpha_composite(Image.fromarray(base),Image.fromarray(cloth)))
 out[human]=frozen[human];out[props]=old[props]
 # The same original front-lip/true-feather junction is kept at its actual fixed
 # coordinates, as are the puppets/rods. No whole-puppet foreground rule changes.
 Image.fromarray(cloth).save(d/'ONE036_MAPPED_CLOTH_RGBA.png');Image.fromarray(out).save(d/'SAME036_MAPPED_REINTEGRATED_RGBA.png')
 gray(out).save(d/'SAME036_MAPPED_FULL_ON_GRAY.png');gray(cloth).crop((240,625,1024,1100)).save(d/'SAME036_MAPPED_CLOTH_NORMAL_SIZE.png');gray(out).crop((470,625,1018,1088)).save(d/'SAME036_MAPPED_CONTACT_NORMAL_SIZE.png')
 outside=(cloth[:,:,3]==0)&~oldface&~oldarm&~human&~props
 index=int(np.argmin(np.linalg.norm(src-[fx,fy],axis=1)))
 report={'frame':f,'generation_calls':0,'source_master_commit':'b30abd65','master_SHA256':sha(masterp),'mapped_RGBA_SHA256':sha(d/'SAME036_MAPPED_REINTEGRATED_RGBA.png'),'mapping':'one continuous piecewise-affine small-motion036 sheet; premultiplied bilinear sampling; only frozen far-pinch delta drives local motion; C1/lip-T/ridge endpoint/lower support stay','old_independent042048_cloth_RGB_or_alpha_used':False,'source_landmarks':src.tolist(),'target_landmarks':target.tolist(),'triangles':tri.simplices.tolist(),'inverted_triangles':0,'minimum_signed_area_ratio':float((td/sd).min()),'frozen_far_pinch':pinch.tolist(),'mapped_far_pinch':target[index].tolist(),'far_pinch_residual':float(np.linalg.norm(target[index]-pinch)),'far_pinch_delta_from036':delta.tolist(),'arm_M_UNCHANGED':r['single_similarity_complete_arm_hand_and_cloth'],'human_RGBA_changes_from_frozen_current_arm':int(np.any(out[human]!=frozen[human],1).sum()),'true_props_and_original_T_RGBA_changes_from_locked036':int(np.any(out[props]!=old[props],1).sum()),'other_original_body_background_RGBA_changes':int(np.any(out[outside]!=old[outside],1).sum()),'status':'PENDING_ACTUAL_NORMAL_SIZE_REVIEW'}
 (d/'MAPPING_CHECK.json').write_text(json.dumps(report,indent=2)+'\n')
 summaries.append({k:report[k]for k in ['frame','inverted_triangles','minimum_signed_area_ratio','far_pinch_residual','human_RGBA_changes_from_frozen_current_arm','true_props_and_original_T_RGBA_changes_from_locked036','other_original_body_background_RGBA_changes','mapped_RGBA_SHA256']})
 p=d/'SAME036_MAPPED_REINTEGRATED_RGBA.png';state_sources.append({'state':f,'used':str(p),'usedURL':'/'+str(p.relative_to(repo)),'sha256':sha(p)})
plan={'global_frames':list(range(36,49)),'fps':24,'source_state_starts':[36,42,48],'exposure_within_short_clip':[{'state':36,'frames':[36,41],'count':6},{'state':42,'frames':[42,47],'count':6},{'state':48,'frames':[48,48],'count':1}],'sources':state_sources,'generation_calls':0,'one_shared_master_SHA256':sha(masterp)}
(R/'SOURCES_EXPOSURE_AND_T_LAYER.json').write_text(json.dumps(plan,indent=2)+'\n')
sheet=Image.new('RGB',(1568,1010),(236,239,242));draw=ImageDraw.Draw(sheet)
for i,f in enumerate([36,42,48]):
 p=masterp if f==36 else R/f'F{f:03d}/ONE036_MAPPED_CLOTH_RGBA.png'
 sheet.paste(gray(rgba(p)).crop((240,625,1024,1100)),((i%2)*784,(i//2)*505+30));draw.text(((i%2)*784+8,(i//2)*505+8),f'F{f:03d} SAME SINGLE036 MASTER | 1:1',fill='black')
sheet.save(R/'SAME_MASTER_THREE_CLOTHS_1TO1.png');print(json.dumps(summaries,indent=2))
