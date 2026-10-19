from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.spatial import Delaunay
from scipy.ndimage import map_coordinates
from scipy.interpolate import CubicSpline
O=Path('collab/reviews/cloud_s12_20261018/F026_index_repair_inputs_20261019')
S=Path('collab/reviews/cloud_s12_20261018/F022_full_arm_repair_20261019/uniform_map_rejoin_20261019')
locked=Image.open(O/'reference/LOCKED_F022_STATIC_BASE.png').convert('RGBA')
base=Image.open(S/'candidate/F022_far_arm_exclusive.png').convert('RGBA')
thumbmask=np.array(Image.open(S/'masks/thumb_alpha_native.png').convert('RGBA'))[:,:,3]>0
# Explicit traced cross sections of the visible lowest finger, adjacent to the thumb.
# All texture comes from actual locked022 pixels; this is reference-only projection, not final drawn artwork.
L=np.array([[950,917],[959,919],[972,922],[983,927],[989,932],[992,936],[992,939]],float)
R=np.array([[948,927],[958,929],[968,932],[976,937],[982,940],[987,942],[990,941]],float)
C=(L+R)/2
T=np.array([[949,922],[959,923],[976,929],[985,938],[986,949],[982,960],[976.52,963.83]],float)
# Transverse diameters retain native-scale finger volume. No circular/capsule drawing is used.
w=np.array([10,11,12,12,11.5,11,8.5])
tan=np.gradient(T,axis=0);tan/=np.linalg.norm(tan,axis=1)[:,None]
normal=np.stack([tan[:,1],-tan[:,0]],axis=1)
TL=T+normal*w[:,None]/2;TR=T-normal*w[:,None]/2
src=np.concatenate([L,R,C]);dst=np.concatenate([TL,TR,T])
tri=Delaunay(dst)
yy,xx=np.mgrid[:1536,:1024];pts=np.stack([xx.ravel(),yy.ravel()],axis=1)
# Limit work to the local finger domain.
local=(pts[:,0]>=940)&(pts[:,0]<=1004)&(pts[:,1]>=908)&(pts[:,1]<=978)
q=pts[local];s=tri.find_simplex(q);valid=s>=0
qv=q[valid];sv=s[valid];b=np.einsum('nij,nj->ni',tri.transform[sv,:2],qv-tri.transform[sv,2]);b=np.column_stack([b,1-b.sum(axis=1)])
uv=np.einsum('ni,nij->nj',b,src[tri.simplices[sv]])
# Native source mask is a closed trace of the actual drawn digit; avoid neighboring thumb/rear digits.
mask=Image.new('L',base.size);ImageDraw.Draw(mask).polygon([tuple(v) for v in np.concatenate([L,R[::-1]])],fill=255)
a=np.array(base).astype(float)/255;sm=np.array(mask)/255;a[:,:,3]*=sm;a[:,:,:3]*=a[:,:,3:4]
sampled=np.column_stack([map_coordinates(a[:,:,k],[uv[:,1],uv[:,0]],order=1,mode='constant') for k in range(4)])
rgba=np.zeros_like(a);flat=rgba.reshape(-1,4);indices=np.flatnonzero(local)[valid];flat[indices]=sampled
nz=rgba[:,:,3]>0;rgba[nz,:3]/=rgba[nz,3:4];rgba=np.uint8(np.clip(rgba*255+.5,0,255))
index=Image.fromarray(rgba,'RGBA')
# Remove the old traced digit from the reference-only far-hand layer, then show one new complete digit.
back=np.array(base);old=np.array(mask)>0;back[old]=0
# Keep the fixed locked022 thumb intact, including its alpha fringe.
back[thumbmask]=np.array(base)[thumbmask]
backim=Image.fromarray(back,'RGBA');target=Image.alpha_composite(backim,index)
# Protect the stationary thumb; target is still reference only, never adopted as final output.
tar=np.array(target);tar[thumbmask]=np.array(base)[thumbmask];target=Image.fromarray(tar,'RGBA')
O.joinpath('geometry').mkdir(exist_ok=True)
mask.save(O/'geometry/old_index_trace_native.png');index.save(O/'geometry/reference_only_projected_index_native.png');backim.save(O/'geometry/locked022_far_hand_old_index_removed_REFERENCE_ONLY.png');target.save(O/'geometry/reference_only_target_hand_native.png')
def plate(im):
 out=Image.new('RGBA',(1024,1024));out.alpha_composite(im.crop((816,816,1024,1024)).resize((832,832),Image.Resampling.NEAREST),(96,96));return out
def pp(p):return tuple((np.array(p)-816)*4+96)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
# Clean complete hand target, annotations restricted to diagnostic plate (never final output).
p1=Image.new('RGBA',(1024,1024),(225,228,230,255));p1.alpha_composite(plate(target))
d=ImageDraw.Draw(p1);d.text((25,20),'INPUT 1  |  LOCKED022 PALM + WHOLE INDEX PROJECTION STUDY',fill='#26313a',font=font);d.text((25,46),'Reference only: source-pixel mesh projection; no new drawing / no imagegen call.',fill='#444f59',font=small)
for name,p,off in [('MCP estimate',(960,923),(-210,-32)),('PIP',(985,938),(-240,-18)),('DIP',(984,957),(-245,0)),('PAD',(976.52,963.83),(-210,38))]:
 x,y=pp(p);ex,ey=x+off[0],y+off[1];d.line((ex+92,ey+8,x,y),fill='#306f8c',width=1);d.ellipse((x-3,y-3,x+3,y+3),outline='#306f8c',width=1);d.text((ex,ey),name,fill='#215470',font=small)
d.text((25,969),'Native crop [816,816,1024,1024], x4, pad 96. Fixed actual palm / wrist / thumb.',fill='#26313a',font=small)
p1.convert('RGB').save(O/'inputs/01_locked022_whole_index_TARGET_REFERENCE.png')
# Same exact target, composed with frozen actual Canvas prop raster. No mathematical replacement rods.
props=Image.open(S/'actual_scene/F022_code_props_actual_layer.png').convert('RGBA')
propplate=props.transform((1024,1024),Image.Transform.AFFINE,(.175,0,829.4,0,.175,666.4),Image.Resampling.NEAREST)
p2=Image.new('RGBA',(1024,1024),(225,228,230,255));p2.alpha_composite(plate(backim));p2.alpha_composite(propplate)
# Real index on front face; fixed source thumb preserves actual first-touch contact.
p2.alpha_composite(plate(index));th=np.array(base);th[~thumbmask]=0;p2.alpha_composite(plate(Image.fromarray(th,'RGBA')))
d=ImageDraw.Draw(p2);d.rectangle((0,0,1024,80),fill=(225,228,230,255));d.text((25,20),'INPUT 2  |  SAME TARGET + ACTUAL FROZEN UPPER / LOWER RODS',fill='#26313a',font=font);d.text((25,46),'Upper shaft passes behind drawn index; pad turns below. Lower-rod air must remain.',fill='#444f59',font=small)
d.rectangle((0,952,1024,1024),fill=(225,228,230,255));d.text((25,970),'True Canvas raster: 7 scene-pixel rods. Visual gate required; not an accepted contact result.',fill='#26313a',font=small)
p2.convert('RGB').save(O/'inputs/02_same_target_frozen_actual_rods.png')
# Only local skin / outline / jade patches from the same locked source hand; no complete pose.
p3=Image.new('RGB',(1024,1024),(225,228,230));d=ImageDraw.Draw(p3);d.text((25,20),'INPUT 3  |  LOCAL LOCKED022 MATERIAL / INK PATCHES ONLY',fill='#26313a',font=font)
patches=[('PALM SKIN',(911,913,939,938),(80,150)),('HAND SHADE',(935,907,956,930),(540,150)),('THUMB PAD / INK',(964,935,979,949),(80,570)),('WRIST / JADE',(850,895,879,925),(540,570))]
for name,box,pos in patches:
 crop=locked.crop(box);bg=Image.new('RGBA',crop.size,(225,228,230,255));bg.alpha_composite(crop);bg=bg.resize((320,320),Image.Resampling.NEAREST).convert('RGB');p3.paste(bg,pos);d.text((pos[0],pos[1]-32),name,fill='#26313a',font=font)
p3.save(O/'inputs/03_locked022_local_material_patches.png')
record={'status':'INPUT_CANDIDATE_ONLY_REQUIRES_INDEPENDENT_VISUAL_GATE','imagegen_calls':0,'F030':'BLOCKED','static_base_SHA256':hashlib.sha256((O/'reference/LOCKED_F022_STATIC_BASE.png').read_bytes()).hexdigest(),'actual_prop_source_SHA256':hashlib.sha256((S/'actual_scene/F022_code_props_actual_layer.png').read_bytes()).hexdigest(),'native_crop':[816,816,1024,1024],'native_to_plate':[[4,0,-3168],[0,4,-3168]],'plate_to_native':[[.25,0,792],[0,.25,792]],'plate_to_scene':[[.175,0,829.4],[0,.175,666.4]],'MCP_estimate':[960,923],'MCP_basis':'Visible locked022 index-palm crease/root; approximate 2D anatomical estimate, not a measured hidden joint. Old (967,918) was not reused.','PIP':[985,938],'DIP':[984,957],'PAD':[976.52,963.83],'bone_projected_lengths_native':[29.154759,19.026298,10.12166],'caution':'Only a source-pixel articulated projection study. Its unfolded 2D length is a projection assumption, not proof of bone lengths. Never adopt this projected finger into production. Actual unique call must draw a natural whole index and pass independent visual/alpha contact gate.','source_mesh_left':L.tolist(),'source_mesh_right':R.tolist(),'target_mesh_left':TL.tolist(),'target_mesh_right':TR.tolist(),'old_index_source_mask':'geometry/old_index_trace_native.png','source_texture':'locked022 far-arm-exclusive actual pixels','production_adoption':'ONLY future actual drawn whole index plus necessary palm-root transition; all protected locked022 RGBA exact. Current target and full026 diagnostic never production mothers.'}
(O/'geometry/plate_and_anatomy.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('Built actual 3 input candidates, 0 calls. Inspect them; not accepted drawings.')
