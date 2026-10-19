from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage as nd
from scipy.spatial import Delaunay
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;B=R.parent
M=B/'F036_FULL_FOLD_SAME_RAW_ZERO_CALL_20261019'
Q=B/'F042_F048_SINGLE_WHOLE_CLOTH_REPAINT_20261019'
OLD=B/'F036_F042_F048_SCENE_TRANSITIONS_ZERO_CALL_20261019'
G=B/'F042_F048_NATIVE_call01_each_from_bd309770_20261019/single_group_reintegration_TRIAL'
P=B/'F036_REBUILD_FROM_ACTUAL030_ZERO_CALL_v1_20261019'
def rgba(p):return np.array(Image.open(p).convert('RGBA'))
def mask(p):return np.array(Image.open(p).convert('L'))>0
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def gray(a):
 g=Image.new('RGBA',(1024,1536),(236,239,242,255));g.alpha_composite(Image.fromarray(a));return g.convert('RGB')
masterp=M/'F036_COMPLETE_FOLD_CLOTH_RGBA.png';master=rgba(masterp);valid=master[:,:,3]>=128
props=mask(P/'layers/TRUE_ORIGINAL_PROPS_SAME_COMMON030_COORDS.png')
feather=mask(P/'masks/TRUE_OUTER_FEATHER_LINES_COMMON030.png')
reports=json.loads((G/'geometry/ONE_GROUP_PER_STATE_SOURCE_MATRIX_CHECKS.json').read_text())['reports']
# Ordered physical perimeter landmarks, followed by supported interior and lip
# anchors. Target perimeter is the already-reviewed042/048 native silhouette;
# target cloth RGB is never sampled. All triangles sample one frozen036 master.
src=np.array([(257,877),(303,840),(349,806),(403,772),(461,741),(510,693),(590,718),(642,700),(695,661),(710,649),(734,658),(766,682),(811,711),(900,750),(960,807),(1001,867),(1005,903),(978,933),(998,954),(970,1016),(942,1035),(920,1007),(903,1067),(850,1012),(780,1018),(688,999),(623,966),(582,961),(530,990),(451,967),(350,932),(272,900),(725.78751656,663.66135947),(600,850),(500,875),(700,900),(840,807),(884,878)],float)
# A consistent material correspondence, not a second pose fit. The only arm M
# used remains the earlier frozen matrix. Two lower hanging folds correspond in
# order, while the supported center stays put.
target0=np.array([(253,878),(300,823),(335,790),(373,755),(468,753),(515,730),(585,708),(625,690),(690,672),(708,655),(726,658),(762,689),(833,711),(915,768),(969,820),(997,874),(1003,918),(978,941),(1002,968),(970,1042),(946,1072),(865,1020),(811,1074),(839,1033),(763,1033),(692,1018),(623,1008),(590,1004),(544,992),(475,969),(334,921),(273,902),(719.3919286565133,663.6451167701863),(600,850),(500,875),(700,900),(835,803),(947,917)],float)
source_boundary=valid&~nd.binary_erosion(valid)
sy,sx=np.where(source_boundary);source_edges=np.column_stack([sx,sy])
def nearest(points,edges):
 return np.array([edges[np.argmin(((edges-p)**2).sum(1))] for p in points],float)
src[:32]=nearest(src[:32],source_edges)
_,near=nd.distance_transform_edt(~valid,return_indices=True)
rgb=master[:,:,:3].copy();rgb[~valid]=master[near[0][~valid],near[1][~valid],:3]
state_sources=[{'state':36,'used':str(M/'F036_SAME_RAW_REINTEGRATED_RGBA.png'),'usedURL':'/'+str((M/'F036_SAME_RAW_REINTEGRATED_RGBA.png').relative_to(R.parents[3])),'sha256':sha(M/'F036_SAME_RAW_REINTEGRATED_RGBA.png')}]
summaries=[]
for f in [42,48]:
 d=R/f'F{f:03d}';d.mkdir(exist_ok=True)
 r=next(v for v in reports if v['frame']==f)
 target=target0.copy();pinch=np.array(r['mapped_anchors'][2]);delta=pinch-target0[32]
 target[7:15]+=delta;target[32]=pinch
 target_cloth=rgba(Q/f'F{f:03d}/EXTRACTED_ONE_NATIVE_CLOTH.png');domain=target_cloth[:,:,3]>=128
 boundary=domain&~nd.binary_erosion(domain);ty,tx=np.where(boundary);edges=np.column_stack([tx,ty])
 target[:32]=nearest(target[:32],edges)
 tri=Delaunay(target)
 sv=src[tri.simplices];tv=target[tri.simplices]
 sdet=np.linalg.det(np.stack([sv[:,1]-sv[:,0],sv[:,2]-sv[:,0]],2));tdet=np.linalg.det(np.stack([tv[:,1]-tv[:,0],tv[:,2]-tv[:,0]],2))
 inversions=int((sdet*tdet<=0).sum())
 if inversions:raise RuntimeError(f'{f}: {inversions} inverted correspondence triangles; no image mapped')
 yy,xx=np.indices(domain.shape);points=np.column_stack([xx.ravel(),yy.ravel()]);simplex=tri.find_simplex(points);inside=simplex>=0
 coords=np.full((len(points),2),-1.0);si=simplex[inside]
 bary2=np.einsum('ijk,ik->ij',tri.transform[si,:2],points[inside]-tri.transform[si,2]);bary=np.column_stack([bary2,1-bary2.sum(1)])
 coords[inside]=np.einsum('ij,ijk->ik',bary,src[tri.simplices[si]])
 # Target perimeter pixels beyond the polygonal mesh use the nearest mesh edge;
 # no unrelated source picture or target texture is ever introduced.
 mapped=inside.reshape(domain.shape);needs=(target_cloth[:,:,3]>0)&~mapped
 if needs.any():
  _,idx=nd.distance_transform_edt(~mapped,return_indices=True);flat=coords.reshape(1536,1024,2);flat[needs]=flat[idx[0][needs],idx[1][needs]]
 co=coords.reshape(1536,1024,2)
 cloth=np.zeros_like(master);cloth[:,:,3]=target_cloth[:,:,3]
 for k in range(3):cloth[:,:,k]=np.clip(np.rint(nd.map_coordinates(rgb[:,:,k].astype(float),[co[:,:,1],co[:,:,0]],order=1,mode='nearest')),0,255).astype('uint8')
 cloth[cloth[:,:,3]==0]=0
 human=mask(Q/f'F{f:03d}/HUMANS_PROTECTED_COORDINATES.png')
 basep=OLD/f'F{f:03d}_FRONT_LIP_OVER_OUTER_FEATHER_RGBA.png';base=rgba(basep)
 out=base.copy();extent=target_cloth[:,:,3]>0;out[extent]=np.array(Image.alpha_composite(Image.fromarray(base),Image.fromarray(cloth)))[extent]
 out[human|props]=base[human|props]
 front=mask(OLD/f'F{f:03d}_ONLY_TRUE_FRONT_LIP_FEATHER_INTERSECTION.png');out[front]=cloth[front]
 Image.fromarray(cloth).save(d/'ONE036_MAPPED_CLOTH_RGBA.png');Image.fromarray(out).save(d/'SAME036_MAPPED_REINTEGRATED_RGBA.png')
 gray(out).save(d/'SAME036_MAPPED_FULL_ON_GRAY.png');gray(cloth).crop((240,625,1024,1100)).save(d/'SAME036_MAPPED_CLOTH_NORMAL_SIZE.png')
 gray(out).crop((470,625,1018,1088)).save(d/'SAME036_MAPPED_CONTACT_NORMAL_SIZE.png')
 changes=np.any(out!=base,2);non_source=nd.map_coordinates(valid.astype(float),[co[:,:,1],co[:,:,0]],order=0,mode='constant',cval=0)<.5
 visible=domain&~human&~props;ex=visible&non_source
 source_distance=nd.distance_transform_edt(~valid);sampledist=nd.map_coordinates(source_distance,[co[:,:,1],co[:,:,0]],order=1,mode='nearest')
 report={'frame':f,'master_SHA256':sha(masterp),'source_master_commit':'b30abd65','generation_calls':0,'target_cloth_alpha_reference':str(Q/f'F{f:03d}/EXTRACTED_ONE_NATIVE_CLOTH.png'),'target_cloth_alpha_SHA256':sha(Q/f'F{f:03d}/EXTRACTED_ONE_NATIVE_CLOTH.png'),'target_RGB_used':False,'mapping':'single piecewise-affine continuous mesh; bilinear sampling only from final036 master; original target contour alpha unchanged','source_landmarks':src.tolist(),'target_landmarks':target.tolist(),'triangles':tri.simplices.tolist(),'inverted_triangles':inversions,'arm_M_UNCHANGED':r['single_similarity_complete_arm_hand_and_cloth'],'frozen_far_pinch':pinch.tolist(),'target_alpha_changes':int(np.count_nonzero(cloth[:,:,3]!=target_cloth[:,:,3])),'human_RGBA_changes':int((changes&human).sum()),'true_prop_RGBA_changes_except_frozen_T':int((changes&props&~front).sum()),'frozen_T_pixels':int(front.sum()),'visible_nearest_source_edge_samples':int(ex.sum()),'maximum_visible_source_edge_extension':float(sampledist[ex].max()) if ex.any() else 0,'mapped_RGBA_SHA256':sha(d/'SAME036_MAPPED_REINTEGRATED_RGBA.png'),'status':'PENDING_ACTUAL_NORMAL_SIZE_REVIEW'}
 (d/'MAPPING_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');summaries.append({k:report[k] for k in ['frame','inverted_triangles','human_RGBA_changes','true_prop_RGBA_changes_except_frozen_T','visible_nearest_source_edge_samples','maximum_visible_source_edge_extension','mapped_RGBA_SHA256']})
 p=d/'SAME036_MAPPED_REINTEGRATED_RGBA.png';state_sources.append({'state':f,'used':str(p),'usedURL':'/'+str(p.relative_to(R.parents[3])),'sha256':sha(p)})
plan={'global_frames':list(range(36,49)),'fps':24,'source_state_starts':[36,42,48],'exposure_within_short_clip':[{'state':36,'frames':[36,41],'count':6},{'state':42,'frames':[42,47],'count':6},{'state':48,'frames':[48,48],'count':1}],'sources':state_sources,'generation_calls':0,'one_shared_master_SHA256':sha(masterp)}
(R/'SOURCES_EXPOSURE_AND_T_LAYER.json').write_text(json.dumps(plan,indent=2)+'\n')
sheet=Image.new('RGB',(1568,1010),(236,239,242));draw=ImageDraw.Draw(sheet)
for i,f in enumerate([36,42,48]):
 p=M/'F036_COMPLETE_FOLD_CLOTH_RGBA.png' if f==36 else R/f'F{f:03d}/ONE036_MAPPED_CLOTH_RGBA.png'
 sheet.paste(gray(rgba(p)).crop((240,625,1024,1100)),((i%2)*784,(i//2)*505+30));draw.text(((i%2)*784+8,(i//2)*505+8),f'F{f:03d} SAME SINGLE036 MASTER | 1:1',fill='black')
sheet.save(R/'SAME_MASTER_THREE_CLOTHS_1TO1.png');print(json.dumps(summaries,indent=2))
