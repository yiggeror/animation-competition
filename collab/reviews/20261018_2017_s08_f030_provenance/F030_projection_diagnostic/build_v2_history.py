from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
from scipy.ndimage import map_coordinates,binary_dilation,binary_erosion
import numpy as np,json,math
O=Path(__file__).resolve().parent;R=O.parent;G=R/'F030_input_gate';raw=np.array(Image.open(R/'F030_result_registered_nominal/registered/F030_registered_scene_patch_RGBA.png').convert('RGBA'));base=np.array(Image.open(G/'inputs/F030_preplaced_original_body_anchor_and_truehands_NO_ROD_RGBA.png').convert('RGBA'));H,W=raw.shape[:2];Y,X=np.mgrid[:H,:W];P=np.stack((X,Y),-1).astype(float)
def poly(p):
 m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon(p,fill=255);return np.array(m)>0
def load(p):return np.array(Image.open(p).convert('L'))>0
def save(n,m):Image.fromarray((m.astype(float)*255).round().clip(0,255).astype('uint8')).save(O/'masks'/f'{n}.png')
E=np.array([858.,886.]);S=np.array([1060.,756.]);T=np.array([1018.14697,789.96020]);u=(S-E)/np.linalg.norm(S-E);v=np.array([-u[1],u[0]]);ut=(T-E)/np.linalg.norm(T-E);vt=np.array([-ut[1],ut[0]]);ratio=np.linalg.norm(T-E)/np.linalg.norm(S-E);A=ratio*np.outer(ut,u)+np.outer(vt,v);t=np.sum((P-E)*u,axis=-1)
# Sole foreground near-arm silhouette and its rejected native distal hand/match. Manual semantic polygon; no far-arm skin selected.
pp=poly([(699,816),(776,769),(852,831),(984,777),(1024,751),(1056,714),(1075,702),(1132,681),(1167,686),(1199,655),(1207,668),(1162,719),(1163,747),(1133,770),(1108,778),(1070,785),(1036,811),(1008,835),(974,862),(939,888),(898,913),(861,927),(847,926),(821,917),(778,893),(742,867),(717,840)])
ri=raw.astype(int);skin=(ri[:,:,0]>ri[:,:,1]+8)&(ri[:,:,1]>ri[:,:,2]+6)&(ri[:,:,3]>2)
old=binary_dilation(skin,iterations=2)&pp
# Match beyond the native hand is included explicitly; never reused.
old|=poly([(1150,698),(1196,655),(1208,667),(1160,719)])&(raw[:,:,3]>0)
# Whole elbow cap remains exactly original. Only source forearm before the virtual wrist plane can enter new limb.
fore=old&(t<=np.linalg.norm(S-E)+1)
source=raw.copy();source[~fore]=0
# Smoothly introduce axial shortening outside the entire round elbow cap; no whole-body transform.
def displacement(Q):
 tq=np.sum((Q-E)*u,axis=-1);z=np.clip((tq-36)/68,0,1);w=z*z*(3-2*z);aq=(Q-E)@A.T+E;return (aq-Q)*w[:,:,None]
Q=P.copy()
for k in range(20):Q=P-displacement(Q)
co=np.array([Q[:,:,1],Q[:,:,0]])
trans=np.stack([map_coordinates(source[:,:,k].astype(float),co,order=1,mode='constant') for k in range(4)],-1).round().clip(0,255).astype('uint8')
newmask=trans[:,:,3]>0
# Build diagnostic from native full-body drawing. Explicitly remove old hand/forearm only, then insert same-raw projected forearm.
out=raw.copy();out[old]=0
im=Image.fromarray(out);im.alpha_composite(Image.fromarray(trans));out=np.array(im)
nearall=load(G/'masks/F030_near_whole_transformed_hand_footprint.png');far=load(G/'masks/F030_far_hand_jade_TRUE_ALPHA0_SEAT_guard.png');box=load(G/'masks/F030_fixed_table_box_guard.png');out[nearall]=base[nearall];out[far]=base[far];out[box]=base[box]
# Remove native lamp rod and preserve only accepted white permission plus original hand guards.
white=load(G/'masks/F030_WHITE_body_neck_head_arms_and_wrist_allowed.png');keep=white|nearall|far|box;out[~keep]=base[~keep]
missing=old&~newmask&~(nearall|far|box)&(base[:,:,3]>100)
# Record apparent exposed substrate separately. Do not invent skin, fabric or hide alpha gaps.
for n,m in [('native_near_forearm_and_rejected_distal_group',old),('adopted_same_raw_forearm_source',fore),('projected_near_forearm_actual_alpha',newmask),('newly_exposed_original_anchor_substrate_DIAGNOSTIC',missing)]:save(n,m)
dest=O/'candidates/F030_projected_forearm_UNCLEAN_DIAGNOSTIC_RGBA.png';Image.fromarray(out).save(dest)
for tag,c in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 b=Image.alpha_composite(Image.new('RGBA',(W,H),c),Image.fromarray(out));b.crop((640,640,1320,1035)).resize((1360,790)).convert('RGB').save(O/'qa'/f'whole_arms_{tag}.png');b.crop((965,730,1115,855)).resize((900,750)).convert('RGB').save(O/'qa'/f'wrist_{tag}.png')
 a=Image.alpha_composite(Image.new('RGBA',(W,H),c),Image.open('/workspace/scratch/f060b5601755/astra_s08_f027_parallel_20261018_1812/F027_FINAL_LOCKED/S08_F027_grandma_match_box_RGBA.png').convert('RGBA'));panel=Image.new('RGB',(1620,800),c[:3]);panel.paste(a.crop((530,280,1340,1080)).convert('RGB'),(0,0));panel.paste(b.crop((530,280,1340,1080)).convert('RGB'),(810,0));panel.save(O/'qa'/f'F027_F030_same_scale_{tag}.png')
 overlay=np.zeros_like(out);overlay[missing]=[255,0,180,200];b.alpha_composite(Image.fromarray(overlay));b.crop((790,730,1115,955)).resize((975,675)).convert('RGB').save(O/'qa'/f'exposed_substrate_MAGENTA_{tag}.png')
j={'status':'ZERO_CALL_PROJECTION_DIAGNOSTIC_NOT_ACCEPTED','elbow_anchor':E.tolist(),'source_virtual_wrist_proxy':S.tolist(),'target_true_hand_root':T.tolist(),'axial_scale':ratio,'perpendicular_scale':1,'rotation_degrees':math.degrees(math.atan2(ut[1],ut[0])-math.atan2(u[1],u[0])),'blend_weight_source_axis_range':[36,104],'matrix':A.tolist(),'exposed_body_anchor_substrate_pixels':int(missing.sum()),'skin_or_fabric_invented':False};(O/'geometry/diagnostic.json').write_text(json.dumps(j,indent=2));print(json.dumps(j,indent=2))
