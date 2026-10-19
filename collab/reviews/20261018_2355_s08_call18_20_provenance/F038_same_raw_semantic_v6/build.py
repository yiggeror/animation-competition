from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
from scipy.ndimage import distance_transform_edt,binary_dilation,map_coordinates,binary_erosion
import numpy as np,json,hashlib
R=Path('/workspace/scratch/f060b5601755/astra_s08_first_mother_20261018_1433');O=R/'F038_same_raw_semantic_v6';G=R/'F038_input_gate';N=R/'F038_returned_raw_nominal'
for d in ['candidates','qa','geometry','masks']:(O/d).mkdir(parents=True,exist_ok=True)
a=np.array(Image.open(N/'candidates/S08_F038_whole_turn_arms_candidate_RGBA.png'));q=np.array(Image.open(N/'registered/F038_registered_scene_patch_RGBA.png'));n=np.array(Image.open(G/'inputs/F038_preplaced_true_near_hand_match_RGBA.png'));f=np.array(Image.open(G/'inputs/F038_original_underlying_far_hand_SEAT_RGBA.png'));H,W=a.shape[:2];b=a.copy();Y,X=np.indices((H,W))
def poly(points):
 im=Image.new('L',(W,H));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
def mask(name):return np.array(Image.open(G/'masks'/name))>0
def save(name,m):Image.fromarray(m.astype('uint8')*255).save(O/'masks'/f'{name}.png')
def over(a,b):return np.array(Image.alpha_composite(Image.fromarray(a),Image.fromarray(b)))
nh=mask('F038_near_distal_palm_fingers_entire_match_guard.png');fh=mask('F038_far_visible_hand_jade_TRUE_SEAT_guard.png');box=mask('F038_fixed_table_box_guard.png');w=mask('F038_WHITE_body_neck_head_arms_wrist_allowed.png')
# Whole actual raw far sleeve, keeping fixed exposed grip and the native foreground arm.
sleeve=poly([(1070,667),(1119,663),(1173,781),(1120,827),(1062,842),(1048,790)])&~(nh|fh|box);b[sleeve]=q[sleeve]
# A semantic boundary follows the actual native upper forearm ink line, not the old broad corridor.
front=poly([(1040,850),(1080,846),(1100,843),(1120,839),(1130,837),(1140,835),(1150,832),(1160,830),(1170,827),(1180,824),(1190,821),(1200,818),(1210,815),(1220,813),(1230,809),(1240,804),(1250,800),(1260,796),(1270,794),(1270,892),(1040,952)])
farroi=poly([(1101,785),(1140,763),(1170,731),(1220,726),(1261,753),(1287,787),(1216,819),(1130,847),(1101,830)])
rgb=q[:,:,:3].astype(int);mat=((rgb[:,:,0]>rgb[:,:,1]+14)&(rgb[:,:,1]>rgb[:,:,2]+12))|((rgb[:,:,1]>rgb[:,:,0]+7)&(rgb[:,:,1]>rgb[:,:,2]));clearfar=farroi&binary_dilation(mat&(q[:,:,3]>10),iterations=2)&~front&~nh;clearfar&=~(rgb[:,:,2]>rgb[:,:,0]+20);b[clearfar]=0
ff=f.copy();ff[front]=0;b=over(b,ff);b[fh&~front]=f[fh&~front]
# Restore real native front edge and proximal flesh over the original independent far hand.
fronttake=front&(X<1271)&~nh;b[fronttake]=q[fronttake]
# Original finger gap is genuine transparent lever seat.
seat=poly([(1225,758),(1243,758),(1243,776),(1225,776)]);b[seat]=f[seat]
# Distal whole near hand and match stay original, with their own exterior alpha.
nearroi=poly([(1270,777),(1410,770),(1410,884),(1270,884)])
clearnear=nearroi&(n[:,:,3]==0)&~fh;b[clearnear]=0
nn=n.copy();nn[~nearroi]=0;b=over(b,nn);b[nh]=a[nh]
nearvisible=nearroi&(n[:,:,3]>0);b[nearvisible]=n[nearvisible]
# Remove generated rod segment in actual air between the two hands.
rodghost=poly([(1241,768),(1318,785),(1318,796),(1280,797),(1242,782)])&~(nh|(f[:,:,3]>0))&~front;b[rodghost]=0
# Reconnect the original far jade to its actual raw proximal skin using a smooth8px lateral collar field.
collar=poly([(1085,813),(1113,794),(1138,794),(1138,840),(1110,843),(1085,838)])&~front&~((f[:,:,3]>0)|nh)
t=np.clip((X-1085)/39,0,1);blue=(q[:,:,2].astype(int)>q[:,:,0].astype(int)+20);bluefall=np.clip(distance_transform_edt(~blue)/7,0,1);frontfall=np.clip(distance_transform_edt(~front)/5,0,1);shift=8*t*t*(3-2*t)*bluefall*frontfall
donor=np.stack([map_coordinates(q[:,:,k].astype(float),[Y,X-shift],order=1,mode='constant',cval=0)for k in range(4)],2).round().clip(0,255).astype('uint8');b[collar]=donor[collar]
# Source-over true jade AA once on the actual proximal skin underlay, including its newly exposed lower edge.
jade=poly([(1115,790),(1156,790),(1156,846),(1115,846)])&(f[:,:,3]>0)&~front
frgb=f[:,:,:3].astype(int);actual_green=(frgb[:,:,1]>frgb[:,:,0]+8)&(frgb[:,:,1]>frgb[:,:,2]+5);jedge=jade&(f[:,:,3]<255)&~binary_erosion(f[:,:,3]>128,iterations=2)&binary_dilation(actual_green,iterations=1);b[jedge]=donor[jedge];jj=f.copy();jj[~jedge]=0;b=over(b,jj)
# Native lower palm-root edge rises continuously by at most3px into the locked hand.
root=poly([(1228,837),(1271,837),(1271,879),(1228,879)])&~nh
tx=np.clip((X-1228)/42,0,1);ty=np.clip((Y-840)/14,0,1);dy=3.2*tx*tx*(3-2*tx)*ty
rd=np.stack([map_coordinates(q[:,:,k].astype(float),[Y+dy,X],order=1,mode='constant',cval=0)for k in range(4)],2).round().clip(0,255).astype('uint8');b[root]=rd[root]
b[nh]=a[nh]; b[fh&~front&~jedge]=a[fh&~front&~jedge]
# Only the original fixed runtime box is retained. Native box shadow is not another prop.
boxroi=poly([(1045,939),(1158,939),(1158,985),(1045,985)]);b[boxroi]=0;b[box]=a[box]
# Uniformly extend only the last 46 native blouse rows to the canvas edge, preserving its original fabric.
# The body and all upper limbs are unchanged. Native crop stops y1071 after whole-raw registration.
strip=Y>=1030
for yy in range(1030,H):
 sy=1030+(yy-1030)*(1070-1030)/(1081-1030)
 y0=int(sy);t=sy-y0;b[yy]=np.rint(q[y0]*(1-t)+q[y0+1]*t).astype('uint8')
# Isolated blue old preplacement sleeve arc lies in genuine exterior air left of the original far hand.
bluearc=poly([(1156,736),(1178,736),(1178,770),(1156,770)])&(f[:,:,3]==0)&~nh; b[bluearc]=0
# Scope declarations.
parts={'RESTORE_same_raw_whole_far_sleeve':sleeve,'CLEAR_native_far_duplicate_above_front_arm':clearfar,'RESTORE_original_far_underlay':(f[:,:,3]>0)&~front,'ACTUAL_raw_front_forearm_contour':fronttake,'TRUE_transparent_low_rod_seat':seat,'CLEAR_native_near_duplicate':clearnear,'RESTORE_true_near_distal_AA':nearvisible,'CLEAR_native_rod_in_true_air':rodghost,'RESTORE_fixed_runtime_box_only':boxroi,'SAME_RAW_lower_blouse_extend_1030_to_frame':strip,'SAME_RAW_far_proximal_collar_smooth8right':collar,'TRUE_jade_AA_over_collar':jedge,'SAME_RAW_near_lower_root_smooth3p2up':root,'CLEAR_old_preplacement_blue_arc_in_original_far_exterior_air':bluearc}
for name,m in parts.items():save(name,m)
union=np.logical_or.reduce(list(parts.values()));ch=np.any(a!=b,2);assert not(ch&~union).any();save('EXPLICIT_semantic_union',union)
p=O/'candidates/S08_F038_same_raw_semantic_RGBA.png';Image.fromarray(b).save(p)
for tag,col in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 bg=Image.alpha_composite(Image.new('RGBA',(W,H),col),Image.fromarray(b));bg.convert('RGB').save(O/'qa'/f'candidate_{tag}.png')
 for nm,bb,z in [('whole_arms',(720,650,1440,1010),2),('wrists_grip',(1080,715,1420,905),4),('head_neck',(740,350,1190,805),2),('bottom',(670,990,1120,1080),3)]:bg.crop(bb).resize(((bb[2]-bb[0])*z,(bb[3]-bb[1])*z)).convert('RGB').save(O/'qa'/f'{nm}_{tag}.png')
 src=Image.open(R/'F036_FINAL_LOCKED/S08_F036_grandma_match_box_RGBA.png').convert('RGBA');src=Image.alpha_composite(Image.new('RGBA',(W,H),col),src);pan=Image.new('RGB',(1780,800),col[:3]);pan.paste(src.crop((620,280,1510,1080)),(0,0));pan.paste(bg.crop((620,280,1510,1080)),(890,0));pan.save(O/'qa'/f'F036_F038_same_scale_{tag}.png')
report={'status':'DIAGNOSTIC_NOT_LOCKED','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'changed_from_nominal':int(ch.sum()),'near_distal_guard_changed':int((ch&nh).sum()),'far_exposed_guard_changed':int((ch&fh).sum()),'box_guard_changed':int((ch&box).sum()),'outside_union_changed':int((ch&~union).sum()),'outside_original_white_changed':int((ch&~w).sum()),'source_raw_scene':str(N/'registered/F038_registered_scene_patch_RGBA.png')};(O/'geometry/checks.json').write_text(json.dumps(report,indent=2));print(report)
