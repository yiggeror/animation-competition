from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve

F=Path(__file__).resolve().parent;P=F.parent
source=P/'next_F058_input_003/generation_001/F058_native_child_locked_G_candidate.png'
A=np.array(Image.open(source).convert('RGBA'));H,W=A.shape[:2];yy,xx=np.indices((H,W))
im=Image.new('L',(W,H));d=ImageDraw.Draw(im)
d.polygon([(502,432),(510,434),(512,449),(503,449)],fill=255)
d.polygon([(512,436),(520,439),(521,452),(513,450)],fill=255)
d.polygon([(520,452),(528,454),(536,465),(537,478),(532,487),(523,492),(521,486),(525,476),(524,465)],fill=255)
# Protect the original silhouette and antialias; edit only internal wrist skin.
interior=distance_transform_edt(A[:,:,3]>200)>2.8
mask=(np.array(im)>0)&interior
coords=np.argwhere(mask);index=np.full((H,W),-1,int);index[mask]=np.arange(len(coords))
M=lil_matrix((len(coords),len(coords)));rhs=np.zeros((len(coords),3))
rgb=A[:,:,:3].astype(float); skin_boundary=(rgb[:,:,0]>170)&(rgb[:,:,1]>110)&(rgb[:,:,2]>80)&(rgb[:,:,0]>rgb[:,:,1]+15)
for i,(y,x) in enumerate(coords):
    degree=0
    for ny,nx in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]:
        if mask[ny,nx]:M[i,index[ny,nx]]=-1;degree+=1
        elif skin_boundary[ny,nx]:rhs[i]+=A[ny,nx,:3];degree+=1
    M[i,i]=degree
fill=np.stack([spsolve(M.tocsr(),rhs[:,c]) for c in range(3)],1)
B=A.copy();B[mask,:3]=np.rint(fill).clip(0,255).astype('uint8')
Image.fromarray(B).save(F/'F058_wrist_skin_continuous_candidate.png')
Image.fromarray(np.uint8(mask)*255).save(F/'internal_wrist_only_mask.png')
bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(B));bg.convert('RGB').save(F/'actual_full_gray.jpg',quality=96)
for name,box,scale in [('actual_dual_wrists',(485,420,555,500),8),('actual_contacts',(280,360,715,550),4)]:
    crop=bg.crop(box).convert('RGB');crop.save(F/(name+'_1x.png'));crop.resize((crop.width*scale,crop.height*scale),Image.Resampling.NEAREST).save(F/(name+f'_{scale}x.png'))
assert np.array_equal(B[:,:,3],A[:,:,3]);assert np.array_equal(B[~mask],A[~mask])
assert np.array_equal(B[:,835:],A[:,835:]);assert np.array_equal(B[410:510,440:501],A[410:510,440:501])
status={'status':'ONE_ZERO_CALL_F058_INTERNAL_WRIST_SEAM_CLEANUP_CANDIDATE_ASTRA_GATE_PENDING','source_commit':'0726b4839561dc4de056020d9a5fd4a0166fb936','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'image_calls':0,'method':'harmonic same-source RGB interpolation only inside complete wrist-skin domains; no source hand/arm warp or cut','edited_pixels':int(np.any(A!=B,2).sum()),'alpha_RGBA_silhouette_unchanged':True,'outer_2_8px_opaque_silhouette_guard':True,'both_finger_clamps_and_X_unchanged':True,'locked_grandma_unchanged':True,'adopted':False,'further_image_calls':0}
(F/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n');print(json.dumps(status,ensure_ascii=False))
