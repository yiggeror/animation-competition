from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage as nd
import numpy as np,json,hashlib,shutil
R=Path(__file__).resolve().parent;B=R.parent;N=B/'F054_F060_F066_NATIVE_call01_each_from_e5c66f8f_20261019';G=B/'F054_F060_F066_FULL_TARGET_GATE_ZERO_CALL_20261019';P=B/'F036_REBUILD_FROM_ACTUAL030_ZERO_CALL_v1_20261019'
def rgba(p):return np.array(Image.open(p).convert('RGBA'))
def mask(p):return np.array(Image.open(p).convert('L'))>0
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(a,p):Image.fromarray(a).save(p)
def poly(pts):
 im=Image.new('L',(1024,1536));ImageDraw.Draw(im).polygon(pts,fill=255);return np.array(im)>0
def comp(*aa):
 out=Image.new('RGBA',(1024,1536))
 for a in aa:out.alpha_composite(Image.fromarray(a))
 return np.array(out)
Y,X=np.indices((1536,1024));propsp=P/'layers/TRUE_ORIGINAL_PROPS_SAME_COMMON030_COORDS.png';props=rgba(propsp);pm=props[:,:,3]>0;feather=mask(P/'masks/TRUE_OUTER_FEATHER_LINES_COMMON030.png')
oldp=N/'F060/reintegration/F060_SAME_CLOTH_TRUE_PROPS_NATIVE_HUMAN_CANDIDATE_RGBA.png';before=rgba(oldp);rawp=N/'F060/originals/S29_F060_call01_RAW_UNTOUCHED.png';raw=rgba(rawp)
# Read the full same-native-raw human once; native limbs are separately locked.
human=rgba(N/'F060/reintegration/EXACT_NATIVE_HUMAN_RGBA_OPEN_DOMAIN.png');near_p=N/'F060/reintegration/EXACT_NATIVE_NEAR_FULL_BARE_ARM_FOREGROUND_RGBA.png';far_p=N/'F060/reintegration/ONE_SIMILARITY_COMPLETE_FAR_SLEEVE_ARM_JADE_HAND_RGBA.png';near=rgba(near_p);far=rgba(far_p)
far_original=far.copy()
registration=json.loads((N/'F060/reintegration/INTEGRATION_CHECK.json').read_text())['complete_far_group_single_similarity'];A=np.array(registration['matrix']);t=np.array(registration['translation']);source_xy=(np.stack([X,Y],2)-t)@np.linalg.inv(A).T
# Complete inner armhole/side-body wedge was wrongly included in the sleeve
# cutout. Remove that garment wedge in source coordinates, preserve the matrix.
wrong_root=(source_xy[:,:,0]<528)&(source_xy[:,:,0]>480)&(source_xy[:,:,1]>500)&(source_xy[:,:,1]>source_xy[:,:,0]+30)&(far[:,:,3]>0)
# Independent color-domain diagnostic against the ORIGINAL registered layer:
# removed side wedge contains blue floral cloth / ink / edge only, no skin/jade.
frgb=far_original[:,:,:3].astype(int)
removed_skin=wrong_root&(frgb[:,:,0]>frgb[:,:,2]+15)&(frgb[:,:,0]>frgb[:,:,1])
removed_jade=wrong_root&(frgb[:,:,1]>frgb[:,:,2]+15)&(frgb[:,:,1]>frgb[:,:,0]+15)
assert not removed_skin.any() and not removed_jade.any()
far[wrong_root]=0;save(far,R/'SAME_REGISTERED_FAR_ARM_BLUE_ROOT_MASK_CORRECTED_RGBA.png')
head=poly([(215,25),(640,25),(640,335),(523,372),(488,417),(425,416),(383,357),(345,323),(260,299),(217,270)])&(before[:,:,3]>0)
far_source=poly([(478,354),(530,354),(630,480),(730,510),(790,565),(805,705),(680,705),(650,638),(622,631),(592,622),(558,606),(522,565),(495,578),(492,527),(498,465),(495,414)])
# Continuous native front / side / hem source. In particular do NOT return the
# untransformed sleeve-root underlay, the cause of the tiny blue fragment.
rgb=raw[:,:,:3].astype(float);blue=(rgb[:,:,0]>45)&(rgb[:,:,1]>90)&(rgb[:,:,2]>130)&(rgb[:,:,2]>rgb[:,:,0]+15)&(Y>300)&(Y<940);lb,_=nd.label(nd.binary_closing(blue,iterations=1));bluewhole=nd.binary_dilation(nd.binary_fill_holes(lb==lb[500,350]),iterations=1)&(human[:,:,3]>0)
blouse=human.copy();blouse[~bluewhole|far_source|(near[:,:,3]>0)|head]=0
save(blouse,R/'SOURCE060_CONTINUOUS_NATIVE_FRONT_SIDE_HEM_RGBA.png')
# A single continuous garment-surface projection starts above the side panel,
# rather than chasing the obsolete narrow hem silhouette. Entire source RGB
# remains the same060 native blouse; the canonical navy cotton is never sampled.
# x: broaden side into the full armhole join; y: give the whole front/side hem
# enough physical continuation BELOW the fixed cloth, which occludes it.
sx=X.astype(float);sy=Y.astype(float)
for _ in range(18):
 wx=np.clip((sx-265)/245,0,1);wx=wx*wx*(3-2*wx)
 wy=np.clip((sy-420)/125,0,1);wy=wy*wy*(3-2*wy)
 dx=32*wx*wy
 dy=.145*np.maximum(sy-480,0)*wx
 sx=X-dx;sy=Y-dy
v=blouse.astype(float);v[:,:,:3]*=v[:,:,3:4]/255
z=np.stack([nd.map_coordinates(v[:,:,k],[sy,sx],order=1,mode='constant',cval=0)for k in range(4)],2);z[:,:,:3]=np.divide(z[:,:,:3],z[:,:,3:4]/255,out=np.zeros_like(z[:,:,:3]),where=z[:,:,3:4]>1e-8);projected=np.rint(np.clip(z,0,255)).astype('uint8');projected[projected[:,:,3]==0]=0
side=np.interp(Y[:,0],[0,430,510,545,570,620,685,775,940,1535],[420,500,515,525,515,520,540,540,275,275])[:,None];projected[(X>side)&(Y>480)]=0
save(projected,R/'SAME060_FULL_FRONT_SIDE_HEM_EXTENDED_BEHIND_COTTON_RGBA.png')
# One full semantic removal envelope, not white-pixel patches. Keeps old sleeve
# edge pieces and old garment negative silhouettes out of the reconstruction.
domain=poly([(175,335),(345,300),(505,345),(560,388),(655,491),(666,607),(548,658),(580,817),(480,890),(231,951),(32,943),(25,876),(56,719),(60,555),(105,411)])
domain|=(near[:,:,3]>0)|(far[:,:,3]>0);domain&=~head
# Clear the complete old garment surface/edge, not the pants behind it.
oldrgb=before[:,:,:3].astype(float);oldblue=(oldrgb[:,:,1]>85)&(oldrgb[:,:,2]>120)&(oldrgb[:,:,2]>oldrgb[:,:,0]+15)&domain;ol,_=nd.label(nd.binary_closing(oldblue,iterations=1));oldwhole=nd.binary_dilation(nd.binary_fill_holes(ol==ol[500,350]),iterations=3)&domain
rootdomain=poly([(480,450),(508,468),(528,525),(550,553),(540,586),(503,590),(484,540)])
removal=(oldwhole|rootdomain|(near[:,:,3]>0)|(far_original[:,:,3]>0))&~head
base=before.copy();base[removal]=0
clothp=N/'F060/inputs/03_THIS_STATE_SAME_SOURCE_CLOTH_RGBA.png';cloth=rgba(clothp);front=mask(G/'F060/FINITE_FRONT_LIP_DOMAIN_MASK.png');lip=np.zeros_like(cloth);use=front&(~pm|feather);lip[use]=cloth[use]
# Exact native arm layers come LAST. Never paint the real neck back through skin.
fixed=comp(base,blouse,projected,cloth,props,lip,near,far);fixed[head]=before[head];fixed[1100:]=before[1100:]
out=R/'F060_FULL_SEMANTIC_REPAIR_RGBA.png';save(fixed,out);save((domain*255).astype('uint8'),R/'FULL_FRONT_SIDE_HEM_ARMHOLE_SEMANTIC_DOMAIN_MASK.png')
for f in [48,54,66]:
 source=B/'F036_COMPLETE_OLD_HAND_HOLE_RAW_RESTORE_ZERO_CALL_20261019/F048/CURRENT_FINGER_ALPHA_OVER_COMPLETE_CLOTH_RGBA.png'if f==48 else N/f'F{f:03d}/reintegration/F{f:03d}_SAME_CLOTH_TRUE_PROPS_NATIVE_HUMAN_CANDIDATE_RGBA.png';shutil.copy2(source,R/f'F{f:03d}_UNCHANGED_LOCKED_RGBA.png')
def gray(a):return Image.alpha_composite(Image.new('RGBA',(1024,1536),(232,235,239,255)),Image.fromarray(a)).convert('RGB')
gray(fixed).save(R/'F060_FULL_ON_GRAY.png');gray(fixed).crop((80,430,810,940)).save(R/'F060_COMPLETE_ARMS_AND_BLOUSE_1TO1.png')
sheet=Image.new('RGB',(1460,550),(232,235,239));d=ImageDraw.Draw(sheet)
for i,(a,title)in enumerate([(before,'BEFORE: narrow silhouette HOLD'),(fixed,'AFTER: full native blouse semantic domain')]):sheet.paste(gray(a).crop((80,430,810,940)),(i*730,40));d.text((i*730+10,12),title,fill='black')
sheet.save(R/'F060_FULL_SEMANTIC_BEFORE_AFTER_1TO1.png')
# Important invariants prove the repair scope, without substituting for images.
oldfar=rgba(far_p);oldnear=rgba(near_p);assert np.array_equal(near,oldnear)and np.array_equal(far[~wrong_root],oldfar[~wrong_root])
# Opaque skin/jade/hand foreground pixels in final remain exact old layers.
arm_opaque=(near[:,:,3]==255)|(far[:,:,3]==255);expected=comp(near,far);assert np.array_equal(fixed[arm_opaque],expected[arm_opaque])
changed=np.any(fixed!=before,2);report={'generation_calls':0,'source_commit':'15061c1cee0b779abca0ae39ae137a3595cf8684','source_native060_raw_SHA256':sha(rawp),'native_front_side_hem_source':str(R/'SOURCE060_CONTINUOUS_NATIVE_FRONT_SIDE_HEM_RGBA.png'),'near_arm_layer_SHA256_UNCHANGED':sha(near_p),'complete_far_registered_arm_layer_SHA256_UNCHANGED':sha(far_p),'near_arm_or_hands_new_transform':False,'far_arm_registration_changed':False,'effective_far_sleeve_mask_corrected_only_source_blue_side_wedge':int(wrong_root.sum()),'original_far_skin_pixels_removed':int(removed_skin.sum()),'original_far_jade_pixels_removed':int(removed_jade.sum()),'original_far_RGBA_changes_outside_removed_garment_wedge':int(np.any(far[~wrong_root]!=far_original[~wrong_root],1).sum()),'far_matrix_UNCHANGED':registration,'cotton_RGBA_SHA256_UNCHANGED':sha(clothp),'true_original_props_four_rods_source_SHA256_UNCHANGED':sha(propsp),'protected_head_neck_RGBA_changes':int(np.any(fixed[head]!=before[head],1).sum()),'opaque_arm_hand_foreground_RGBA_changes':int(np.any(fixed[arm_opaque]!=expected[arm_opaque],1).sum()),'all_changed_pixels':int(changed.sum()),'new_source_RGB_or_random_pattern':False,'old_untransformed_sleeve_root_returned':False,'garment_surface_projection':'continuous front-side-hem only; dx32*side_weight*lower_side_weight, dy0.145*(y-480)*side_weight; full native source behind canonical cotton; anatomy/arms fixed','normal_size_visual_status':'PENDING_ACTUAL_VIEW','output_SHA256':sha(out)};(R/'SEMANTIC_SOURCE_AND_LOCK_CHECK.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
