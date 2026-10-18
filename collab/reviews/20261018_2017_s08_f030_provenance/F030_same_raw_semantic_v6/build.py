from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
from scipy.ndimage import map_coordinates,binary_dilation,binary_erosion,binary_fill_holes
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
old=binary_fill_holes(binary_dilation(skin,iterations=2)&pp)
# Match beyond the native hand is included explicitly; never reused.
old|=poly([(1150,698),(1196,655),(1208,667),(1160,719)])&(raw[:,:,3]>0)
# Whole elbow cap remains exactly original. Only source forearm before the virtual wrist plane can enter new limb.
fore=old&(t<=np.linalg.norm(S-E)+28)
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
nearall=load(G/'masks/F030_near_whole_transformed_hand_footprint.png');nearhard=load(G/'masks/F030_near_distal_palm_fingers_entire_match_guard.png');far=load(G/'masks/F030_far_hand_jade_TRUE_ALPHA0_SEAT_guard.png');box=load(G/'masks/F030_fixed_table_box_guard.png');collar=load(G/'masks/F030_near_proximal_wrist_palmroot_release.png');release_aa=nearhard&binary_dilation(collar,iterations=4);nearhard &= ~release_aa
# Original true palm root is alpha-composited, not hard alpha-replaced at its artificial old crop cut.
npix=np.zeros_like(out);npix[nearall]=base[nearall];im=Image.fromarray(out);im.alpha_composite(Image.fromarray(npix));out=np.array(im);out[nearhard]=base[nearhard];save('RELEASE_false_proximal_cut_AA_guard',release_aa);save('true_distal_palm_fingers_match_guard_after_false_AA_release',nearhard)
out[far]=base[far];out[box]=base[box]
# Remove native lamp rod and preserve only accepted white permission plus original hand guards.
white=load(G/'masks/F030_WHITE_body_neck_head_arms_and_wrist_allowed.png');keep=white|nearall|far|box;out[~keep]=base[~keep]
missing=old&~newmask&~(nearall|far|box)&(base[:,:,3]>100)
# Continuous real fabric donor: one translated crop of this same raw above the near arm.
# Record true lack of donor separately rather than fill it.
cloth_source=np.zeros_like(raw);cloth_source[24:,12:]=raw[:-24,:-12]
ci=cloth_source.astype(int);cloth_valid=(ci[:,:,3]>220)&((ci[:,:,2]>ci[:,:,0]+8)|((ci[:,:,0]>220)&(ci[:,:,1]>220)&(ci[:,:,2]>220)))
chest_zone=poly([(850,825),(1003,750),(1010,784),(890,851),(850,855)])
sleeve_zone=poly([(1003,750),(1055,718),(1059,735),(1062,752),(1065,769),(1067,785),(1034,808),(1010,794)])
cloth_zone=missing & (chest_zone|sleeve_zone) & ~nearall
save('chest_real_cloth_strip_region',chest_zone&missing);save('far_sleeve_inner_continuation_region',sleeve_zone&missing)
cloth_adopt=cloth_zone&cloth_valid
out[cloth_adopt]=cloth_source[cloth_adopt]
# Separate real far-upper-arm donor under the lower wrist interface; retain the new near contour above it.
lowroi=poly([(993,835),(1019,808),(1065,812),(1068,824),(1025,828),(1001,842)])&white&~nearhard&~far
far_skin=np.zeros_like(raw);far_skin[:-6]=raw[6:];fi=far_skin.astype(int);lowroi&=(fi[:,:,0]>fi[:,:,1]+8)&(fi[:,:,1]>fi[:,:,2]+6)&(fi[:,:,3]>220)
sub=Image.fromarray(far_skin);sub.alpha_composite(Image.fromarray(trans));sub.alpha_composite(Image.fromarray(npix));sub=np.array(sub);out[lowroi]=sub[lowroi];save('lower_wrist_background_real_far_upperarm_donor',lowroi)
# Remove only the false old vertical crop-AA strip using native projected skin beneath the true palm root.
cutstrip=poly([(1007,752),(1020,750),(1038,822),(1016,827)])&(collar|release_aa)&(trans[:,:,3]>220)&~nearhard
ff=np.array(Image.fromarray(cutstrip.astype('uint8')*255).filter(ImageFilter.GaussianBlur(.45)),float)/255;ff[~cutstrip]=0
out[:,:,:3]=np.rint(out[:,:,:3]*(1-ff[:,:,None])+trans[:,:,:3]*ff[:,:,None]).astype('uint8');out[:,:,3][cutstrip]=255;save('continuous_old_wrist_cut_strip_same_projected_raw_skin',cutstrip)
# One rigid original true proximal-hand contour slice supplies the natural shallow upper wrist arc.
# It contains only original proximal skin/edge, no fingers, and is shifted(-15,+5) on a copy.
hand_donor=np.zeros_like(base);hand_donor[5:,:-15]=npix[:-5,15:]
arcroi=poly([(1009,758),(1028,748),(1035,756),(1033,767),(1022,775),(1010,777)])&(white|release_aa)&~nearhard
arc_back=np.zeros_like(raw);arc_back[24:,40:]=raw[:-24,:-40];arc=Image.fromarray(arc_back);arc.alpha_composite(Image.fromarray(hand_donor));arc=np.array(arc);out[arcroi]=arc[arcroi];save('upper_wrist_real_proximal_contour_donor_arc',arcroi)
# Remove the false internal duplicate contour above the true lower palm edge using a real adjacent projected-skin donor.
innerlow=poly([(1018,810),(1043,811),(1043,818),(1024,819),(1018,815)])&(collar|release_aa)
skin_donor=np.zeros_like(trans);skin_donor[5:,5:]=trans[:-5,:-5];innerlow &= skin_donor[:,:,3]>220
w=np.array(Image.fromarray(innerlow.astype('uint8')*255).filter(ImageFilter.GaussianBlur(.55)),float)/255;w[~innerlow]=0
out[:,:,:3]=np.rint(out[:,:,:3]*(1-w[:,:,None])+skin_donor[:,:,:3]*w[:,:,None]).astype('uint8');out[:,:,3][innerlow]=255;save('false_internal_lower_wrist_double_line_real_skin_donor',innerlow)
# Two verified interior alpha holes, supplied from adjacent actual native projected skin.
hole=np.zeros((H,W),bool)
for x,y in [(1024,812),(1023,813)]:
 hole[y,x]=True;out[y,x]=trans[y-3,x-3]
save('two_interior_native_alpha_holes_real_skin_donor',hole)
# One old cuff-stroke fragment outside the new wrist contour uses real same-raw blue cloth.
oldcuff=poly([(1006,756),(1013,754),(1013,766),(1008,770)])&~nearall
out[oldcuff]=arc_back[oldcuff];save('old_cuff_fragment_outside_wrist_real_cloth_donor',oldcuff)
# Leave all unsupported regions explicit. Never repaint a hand/finger with sampled flat color.
save('same_raw_cloth_donor_adoption',cloth_adopt)
missing &= ~cloth_adopt
# Record apparent exposed substrate separately. Do not invent skin, fabric or hide alpha gaps.
for n,m in [('native_near_forearm_and_rejected_distal_group',old),('adopted_same_raw_forearm_source',fore),('projected_near_forearm_actual_alpha',newmask),('newly_exposed_original_anchor_substrate_DIAGNOSTIC',missing)]:save(n,m)
dest=O/'candidates/F030_projected_forearm_UNCLEAN_DIAGNOSTIC_RGBA.png';Image.fromarray(out).save(dest)
for tag,c in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 b=Image.alpha_composite(Image.new('RGBA',(W,H),c),Image.fromarray(out));b.crop((640,640,1320,1035)).resize((1360,790)).convert('RGB').save(O/'qa'/f'whole_arms_{tag}.png');b.crop((965,730,1115,855)).resize((900,750)).convert('RGB').save(O/'qa'/f'wrist_{tag}.png')
 a=Image.alpha_composite(Image.new('RGBA',(W,H),c),Image.open('/workspace/scratch/f060b5601755/astra_s08_f027_parallel_20261018_1812/F027_FINAL_LOCKED/S08_F027_grandma_match_box_RGBA.png').convert('RGBA'));panel=Image.new('RGB',(1620,800),c[:3]);panel.paste(a.crop((530,280,1340,1080)).convert('RGB'),(0,0));panel.paste(b.crop((530,280,1340,1080)).convert('RGB'),(810,0));panel.save(O/'qa'/f'F027_F030_same_scale_{tag}.png')
 overlay=np.zeros_like(out);overlay[missing]=[255,0,180,200];b.alpha_composite(Image.fromarray(overlay));b.crop((790,730,1115,955)).resize((975,675)).convert('RGB').save(O/'qa'/f'exposed_substrate_MAGENTA_{tag}.png')
j={'status':'ZERO_CALL_PROJECTION_DIAGNOSTIC_NOT_ACCEPTED','elbow_anchor':E.tolist(),'source_virtual_wrist_proxy':S.tolist(),'target_true_hand_root':T.tolist(),'axial_scale':ratio,'perpendicular_scale':1,'rotation_degrees':math.degrees(math.atan2(ut[1],ut[0])-math.atan2(u[1],u[0])),'blend_weight_source_axis_range':[36,104],'matrix':A.tolist(),'exposed_body_anchor_substrate_pixels':int(missing.sum()),'skin_or_fabric_invented':False,'released_false_proximal_cut_AA_guard_pixels':int(release_aa.sum()),'real_same_raw_cloth_adopted_pixels':int(cloth_adopt.sum()),'continuous_old_wrist_cut_strip_pixels':int(cutstrip.sum()),'upper_real_hand_arc_donor_pixels':int(arcroi.sum()),'lower_real_far_arm_donor_pixels':int(lowroi.sum()),'false_internal_lower_double_line_pixels':int(innerlow.sum())};(O/'geometry/diagnostic.json').write_text(json.dumps(j,indent=2));print(json.dumps(j,indent=2))
