from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,hashlib
from scipy.ndimage import distance_transform_edt
R=Path(__file__).resolve().parent.parent;G=R/'F025_input_gate';O=R/'F025_result_semantic_v8'
for s in ['candidates','masks','geometry','qa']:(O/s).mkdir(parents=True,exist_ok=True)
a=np.array(Image.open(R/'F023_FINAL_LOCKED/S08_F023_grandma_match_box_RGBA.png'));b=np.array(Image.open(G/'inputs/F025_scene_preplaced_NO_ROD_RGBA.png'));q=np.array(Image.open(R/'F025_result_wrist_registered/registered/F025_registered_scene_patch_RGBA.png'));o=np.array(Image.open(R/'F025_result_wrist_registered/candidates/S08_F025_local_arm_hand_candidate_RGBA.png'));H,W=a.shape[:2];yy,xx=np.indices((H,W))
def load(n):return np.array(Image.open(G/'masks'/n))>0
def poly(p):
 m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon(p,fill=255);return np.array(m)>0
def save(n,m):Image.fromarray(m.astype('uint8')*255).save(O/'masks'/f'{n}.png')
w=load('F025_WHITE_allowed_BLACK_frozen.png');near=load('F025_near_hand_match_full_guard.png');far=load('F025_far_closed_hand_jade_AND_ALPHA0_SEAT_guard.png');cuff=load('F025_actual_blue_cuff_guard.png');box=load('F025_fixed_table_box_guard.png');m=w.copy()
def paste(mask,source,t):
 y,x=np.where(mask);v=source[y,x];t=t[y,x] if isinstance(t,np.ndarray) else np.full(len(y),t);oldA=o[y,x,3].astype(float)/255;newA=v[:,3].astype(float)/255;aa=oldA*(1-t)+newA*t;rgb=o[y,x,:3]*oldA[:,None]*(1-t[:,None])+v[:,:3]*newA[:,None]*t[:,None];o[y,x,:3]=np.rint(rgb/np.maximum(aa[:,None],1e-9)).clip(0,255).astype('uint8');o[y,x,3]=np.rint(aa*255).astype('uint8')
# Restore only original023 true upper-arm skin immediately below unchanged cuff; no old near-hand pixels.
oldNear=np.array(Image.open(R/'F023_FINAL_LOCKED/F023_true_near_hand_match_footprint.png'))>0
upper=poly([(948,830),(975,805),(1026,781),(1054,781),(1049,818),(1012,839),(974,849)])&w&~(near|far|cuff|box|oldNear);o[upper]=a[upper];save('RESTORE_original023_far_upperarm_below_true_cuff_excluding_old_hand',upper)
# Clear only the native duplicate old near-hand upper line, keeping the actual original shifted fingers.
oldLine=poly([(930,852),(943,841),(974,825),(1007,810),(1028,807),(1036,819),(1010,827),(978,843),(951,857)])&w&~(near|far|cuff|box);y,x=np.where(oldLine);v=q[y+20,x+110];assert (v[:,3]>245).all();k=np.clip(distance_transform_edt(oldLine)[y,x]/1.5,0,1);o[y,x,:3]=np.rint(v[:,:3]*k[:,None]+o[y,x,:3]*(1-k[:,None])).astype('uint8');o[y,x,3]=255;save('CLEAR_native_old_near_hand_upper_line_same_raw_skin_110_20',oldLine)
# True same-native near wrist contour shifted down5px to join the moved protected palm. Fingers remain unchanged.
nearEdge=poly([(920,886),(963,886),(963,926),(920,938)])&w&~(near|far|cuff|box);source=np.zeros_like(q);source[5:]=q[:-5];k=np.clip((yy-886)/6,0,1);paste(nearEdge,source,k);save('PASTE_same_native_near_wrist_lower_edge_rigid_0_plus5',nearEdge)
# Interior cut-line follows the shifted original hand boundary. Original mature wrist skin, no invented fingers.
seam=poly([(944,842),(951,841),(967,901),(960,903),(950,875)])&w&~(near|far|cuff|box);y,x=np.where(seam);v=q[y+15-np.maximum((y-850)//2,0),x-20];assert (v[:,3]>240).all();k=np.clip(distance_transform_edt(seam)[y,x]/1.5,0,1);o[y,x,:3]=np.rint(v[:,:3]*k[:,None]+o[y,x,:3]*(1-k[:,None])).astype('uint8');o[y,x,3]=255;save('CLEAR_internal_preplacement_near_wrist_seam_same_raw_skin_clean_proximal_forearm_interior_patch',seam)
blueTail=poly([(912,905),(934,899),(946,910),(934,934),(915,940)])&((xx<=931)|(yy>=915))&w&~(near|far|cuff|box);o[blueTail]=a[blueTail];save('RESTORE_original_body_air_below_near_wrist_no_duplicate_blue',blueTail)
oldMatch=poly([(1046,828),(1068,783),(1086,783),(1084,813),(1060,830)])&w&~(near|far|cuff|box);o[oldMatch]=0;save('CLEAR_only_duplicate_native_match_in_true_air',oldMatch)
upperJoin=poly([(1028,809),(1042,809),(1044,817),(1028,817)])&w&~(near|far|cuff|box);z=np.zeros_like(q);z[:,12:]=q[:,:-12];k=np.clip((yy-809)/2,0,1);paste(upperJoin,z,k);save('JOIN_actual_native_far_upperarm_lower_contour_rigid12_0',upperJoin)
joinInner=poly([(1027,812),(1044,812),(1044,818),(1027,818)])&upperJoin&(o[:,:,3]>=245);y,x=np.where(joinInner);v=q[y-8,x-25];assert (v[:,3]>=245).all();o[y,x,:3]=v[:,:3];save('REMOVE_only_native_duplicate_finger_line_inside_upperarm_join',joinInner)
p=O/'candidates/S08_F025_same_raw_semantic_candidate_RGBA.png';Image.fromarray(o).save(p);save('FINAL_explicit_semantic_union',m)
knob=(1242.1515476848717,750.9527302910597);pivot=(1301.4864864864865,791.545945945946)
for tag,col in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 bg=Image.new('RGBA',(W,H),col);d=ImageDraw.Draw(bg);d.line((knob,pivot),fill=(58,42,34,255),width=5);r=6.81081;d.ellipse((knob[0]-r,knob[1]-r,knob[0]+r,knob[1]+r),fill=(58,42,34,255));bg.alpha_composite(Image.fromarray(o));bg.convert('RGB').save(O/'qa'/f'candidate_rod_{tag}.png')
 for n,bb,z in [('whole_arm',(900,660,1300,990),3),('near_wrist',(915,820,1000,930),6),('jade_wrist',(1100,770,1195,855),6),('upperarm_depth',(940,780,1090,890),5)]:bg.crop(bb).resize(((bb[2]-bb[0])*z,(bb[3]-bb[1])*z)).convert('RGB').save(O/'qa'/f'{n}_{tag}.png')
ch=np.any(o!=b,2);rep={'status':'SAME_RAW_SEMANTIC_CANDIDATE_PENDING_REVIEW','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'outside_white_changed':int((ch&~w).sum()),'near_guard_changed':int((ch&near).sum()),'far_hand_jade_alpha0_seat_guard_changed':int((ch&far).sum()),'blue_cloth_changed':int((ch&cuff).sum()),'box_changed':int((ch&box).sum()),'same_native_call':13};(O/'geometry/checks.json').write_text(json.dumps(rep,indent=2));print(rep)
