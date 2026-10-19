from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter,distance_transform_edt
import numpy as np,json,hashlib
O=Path(__file__).resolve().parent;R=O.parent;G=R/'F038_input_gate';P=R/'F038_same_raw_semantic_v6';src=P/'candidates/S08_F038_same_raw_semantic_RGBA.png';assert hashlib.sha256(src.read_bytes()).hexdigest()=='9f9b16d7e04554afc25b0b94c39bfbcbd857f3dd282917cc23f7ea40a74d58e5';a=np.array(Image.open(src).convert('RGBA'));v=a.astype(float);H,W=a.shape[:2];Y,X=np.mgrid[:H,:W]
def load(p):return np.array(Image.open(p).convert('L'))>0
def poly(p):
 m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon(p,fill=255);return np.array(m)>0
def ramp(x,l,h):return np.clip((x-l)/(h-l),0,1)
near=load(G/'masks/F038_near_distal_palm_fingers_entire_match_guard.png');farimage=np.array(Image.open(G/'inputs/F038_original_underlying_far_hand_SEAT_RGBA.png'));front=load(P/'masks/ACTUAL_raw_front_forearm_contour.png');far=(farimage[:,:,3]>0)&~front;seat=load(P/'masks/TRUE_transparent_low_rod_seat.png');box=load(G/'masks/F038_fixed_table_box_guard.png');guards=near|far|seat|box
neararm=poly([(862,824),(926,808),(1038,869),(1230,804),(1272,804),(1276,881),(1065,935),(981,961),(914,911)])
r,g,b=v[:,:,0],v[:,:,1],v[:,:,2];opaque=ramp(v[:,:,3],220,252)
skin=ramp(r,165,215)*ramp(r-g,16,30)*ramp(g-b,8,20)*ramp(100-(r-g),0,18)*opaque
head=skin*((X>=850)&(X<=1140)&(Y>=440)&(Y<=780))*ramp(g,180,196);head[guards]=0
# Preserve the genuine ear-concha shadow. Smooth inward away from its small semantic core.
ear=poly([(887,559),(912,562),(915,589),(899,598),(884,585)]);head*=np.minimum(distance_transform_edt(~ear)/9,1)
blue=ramp(b-r,25,55)*ramp(b-g,16,34)*ramp(g,58,95)*ramp(205-r,0,30)*opaque*(Y>600);blue[guards]=0
hairregion=poly([(835,320),(1040,320),(1130,410),(1130,520),(1080,540),(1030,520),(990,540),(940,585),(880,590),(835,560)])
gray=ramp(27-(np.maximum.reduce([r,g,b])-np.minimum.reduce([r,g,b])),0,10)*ramp(np.minimum.reduce([r,g,b]),85,130)*ramp(245-np.maximum.reduce([r,g,b]),0,25)*opaque
face_gray=poly([(927,596),(937,560),(963,528),(996,498),(1026,467),(1051,453),(1078,454),(1093,474),(1105,508),(1141,531),(1143,770),(863,770),(863,600)])
hair=gray*hairregion*np.clip((580-Y)/40,0,1);hair[guards|face_gray]=0
armlit=skin*neararm*ramp(g,186,196)*np.minimum(distance_transform_edt(~guards)/10,1);armlit[guards]=0
mat=[('head_ear_neck_lit_skin',head,(0,4,7)),('blue_blouse',blue,(9,3,0)),('crown_gray_hair',hair,(3,4,3)),('near_upper_and_forearm_lit_skin',armlit,(0,3,5))]
out=v.copy();manifest=[];ov=np.zeros_like(a)
for (name,m,d),color in zip(mat,[(250,80,80),(30,220,100),(200,50,230),(235,180,25)]):
 soft=np.minimum(gaussian_filter(m,.65),m);soft[guards|ear]=0;q=np.rint(soft*255).astype('uint8');Image.fromarray(q).save(O/'masks'/f'{name}_SOFT.png');out[:,:,:3]+=soft[:,:,None]*np.array(d);ov[q>0,:3]=color;ov[q>0,3]=np.maximum(ov[q>0,3],(q[q>0]*.45).astype('uint8'));manifest.append({'name':name,'max_add_RGB':d,'soft_domain_pixels':int((q>0).sum()),'mask':str(O/'masks'/f'{name}_SOFT.png')})
out=np.rint(out).clip(0,255).astype('uint8');out[:,:,3]=a[:,:,3];out[guards]=a[guards];dest=O/'candidates/S08_F038_whole_turn_same_raw_final_color_RGBA.png';Image.fromarray(out).save(dest)
for tag,c in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 z=Image.alpha_composite(Image.new('RGBA',(W,H),c),Image.fromarray(out));z.convert('RGB').save(O/'qa'/f'candidate_{tag}.png')
 for nm,bb,k in [('wrists',(1080,715,1420,905),4),('whole_arms',(720,650,1440,1010),2),('head_neck',(740,350,1190,805),2)]:z.crop(bb).resize(((bb[2]-bb[0])*k,(bb[3]-bb[1])*k)).convert('RGB').save(O/'qa'/f'{nm}_{tag}.png')
 old=Image.alpha_composite(Image.new('RGBA',(W,H),c),Image.open(R/'F036_FINAL_LOCKED/S08_F036_grandma_match_box_RGBA.png').convert('RGBA'));pan=Image.new('RGB',(1780,800),c[:3]);pan.paste(old.crop((620,280,1510,1080)),(0,0));pan.paste(z.crop((620,280,1510,1080)),(890,0));pan.save(O/'qa'/f'F036_F038_same_scale_{tag}.png')
 z.alpha_composite(Image.fromarray(ov));z.crop((650,300,1440,1080)).convert('RGB').save(O/'qa'/f'material_soft_masks_{tag}.png')
ch=np.any(out!=a,2);checks={'status':'FINAL_COLOR_CANDIDATE_PENDING_DUAL_REVIEW','source_shape_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'alpha_changed':int((out[:,:,3]!=a[:,:,3]).sum()),'fixed_hand_match_jade_seat_box_changed':int((ch&guards).sum()),'ear_concha_core_changed':int((ch&ear).sum()),'material_masks':manifest,'shadow_policy':'Near-arm lit material only; natural lower-arm shadow/ear concha/bun upper-lower turning planes and thin far-arm occlusion shadow not forced to F000 lit means.'};(O/'geometry/color_masks_and_checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
