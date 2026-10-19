"""Director-authorized two rigid rod rotations only, no character pose edit.
Exact original people pixels remain outside the explicit old/new rod masks.
"""
from pathlib import Path
import json,math,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation,binary_closing,binary_fill_holes,distance_transform_edt
P=Path(__file__).resolve().parent;PACK=P.parent;Q=PACK/'F000/f000_scene_gate_001';source=Q/'cleanup/S20_F000_master_clean.png';A=np.array(Image.open(source).convert('RGBA'));H,W=A.shape[:2];B=A.copy();yy,xx=np.indices((H,W));old=json.loads((Q/'registration_input.json').read_text());geo=json.loads((P/'geometry_preflight.json').read_text());new=json.loads((P/'registration_input.json').read_text());palm=np.array(Image.open(PACK/'F000/arm_correction_001/masks/protect_L_palm_bracelet.png').convert('L'))>0
r,g,b=A[:,:,:3].astype(float).transpose(2,0,1)
hand_skin=(A[:,:,3]>180)&(r>185)&(g>130)&(b>g*.73)&(r>g+12)&(xx>=890)&(xx<989)&(yy>=285)&(yy<372)
hand_outline=Image.new('L',(W,H));ImageDraw.Draw(hand_outline).polygon([(913,292),(922,290),(936,293),(950,301),(962,317),(975,337),(983,344),(967,358),(954,353),(935,354),(921,351),(914,345),(906,334),(901,322),(898,311),(899,303),(905,299),(913,302)],fill=255)
palm=(binary_dilation(binary_fill_holes(binary_closing(hand_skin,iterations=2)),iterations=2)|(np.array(hand_outline)>0))&palm
wood=(A[:,:,3]>5)&(r>g+10)&(g>b+10)&(b<g*.71)
oldmasks={};rots={};allold=np.zeros((H,W),bool);rows=[]
for e in geo['rod_endpoints']:
 role=e['id']
 if not role.startswith('C'):continue
 v=old['rods'][role];p=np.array(v['grip_master_px']);end=np.array(e['master_px']);u=end-p;u/=np.linalg.norm(u);o=np.array([-1,-v['slope']]);o/=np.linalg.norm(o);angle=math.atan2(u[1],u[0])-math.atan2(o[1],o[0]);c,s=math.cos(angle),math.sin(angle)
 perp=np.abs(yy-v['slope']*xx-v['intercept'])/math.hypot(1,v['slope']);extent=((xx-p[0])*o[0]+(yy-p[1])*o[1]);limit=np.linalg.norm(np.array(v['shaft_tip_master_px'])-p)
 band=(perp<5.5)&(extent>=-32)&(extent<=limit+4);outside=band&~palm&(A[:,:,3]>0);inside=band&palm&wood
 # Only actual rod pigment within palm, excluding surrounding original skin/ink.
 inside=binary_dilation(inside,iterations=1)&band&palm&((b<g*.74)|(A[:,:,3]<80))
 mask=outside|inside;oldmasks[role]=mask;allold|=mask;layer=np.zeros_like(A);front=mask&(extent>45)&~palm;layer[front]=A[front]
 # PIL inverse affine for a unit rotation about the actual clamping point.
 inv=(c,s,p[0]-c*p[0]-s*p[1],-s,c,p[1]+s*p[0]-c*p[1]);rot=Image.fromarray(layer).transform((W,H),Image.Transform.AFFINE,inv,Image.Resampling.BICUBIC);rots[role]=np.array(rot)
 m=(end[1]-p[1])/(end[0]-p[0]);new['rods'][role].update({'slope':float(m),'intercept':float(p[1]-m*p[0]),'shaft_tip_master_px':(p+np.linalg.norm(np.array(v['shaft_tip_master_px'])-p)*u).tolist(),'root_bound_puppet_endpoint_master_px':end.tolist(),'rigid_angle_delta_degrees':math.degrees(angle)})
 rows.append({'id':role,'pivot_master_px':p.tolist(),'rotation_degrees':math.degrees(angle),'scale':1,'old_length_master_px':float(limit),'new_axis_unit':u.tolist(),'part':e['part'],'at':e['at'],'puppet_endpoint_master_px':end.tolist()})
# Restore only former rod pigment inside the palm from adjacent real same-hand
# internal skin. The hand's silhouette, fingers and bracelet are not redrawn.
inside=allold&palm;outside=allold&~palm;B[outside]=0
skin=palm&(A[:,:,3]>180)&(r>185)&(g>130)&(b>g*.73)&(r>g+12)&~allold
_,ix=distance_transform_edt(~skin,return_indices=True);B[inside]=A[ix[0][inside],ix[1][inside]]
Image.fromarray((inside*255).astype('uint8')).save(P/'mask_old_finger_gap_rod_pigment.png')
# Explicit tiny visible gaps follow the NEW axes. These openings reveal the
# exact same rigid scene rod drawn behind the source hand, with no kink.
gaps=np.zeros((H,W),bool)
for role in ['C_N','C_B']:
 q=new['rods'][role];lo,hi=(915,928) if role=='C_N' else (923,929)
 distance=np.abs(yy-q['slope']*xx-q['intercept'])/math.hypot(1,q['slope']);gap=(xx>=lo)&(xx<hi)&(distance<1.15)&palm;gaps|=gap
B[gaps]=0
# Rigidly rotated real outside shafts remain behind every unchanged skin pixel.
for role in ['C_N','C_B']:
 L=rots[role];take=(L[:,:,3]>0)&((B[:,:,3]<80)&~palm);B[take]=L[take]
# Rotation can meet its own former footprint; only that foreground gap changes.
change=np.any(A!=B,axis=2);allowed=allold|gaps
for L in rots.values():allowed|=L[:,:,3]>0
assert not np.any(change&~allowed);assert np.array_equal(A[~allowed],B[~allowed]);assert np.array_equal(A[:,1000:],B[:,1000:]);assert np.array_equal(A[165:410,480:675][A[165:410,480:675,3]>80],B[165:410,480:675][A[165:410,480:675,3]>80])
Image.fromarray(B).save(P/'people_F000_rods_rotated.png');Image.fromarray((change*255).astype('uint8')).save(P/'mask_all_changed_pixels.png');Image.fromarray((gaps*255).astype('uint8')).save(P/'mask_new_finger_gap_axis_openings.png');new['master']='people_F000_rods_rotated.png';(P/'registration_input.json').write_text(json.dumps(new,indent=2)+'\n')
bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(B));bg.crop((875,285,988,372)).resize((904,696),Image.Resampling.NEAREST).convert('RGB').save(P/'palm_after_texture_only_8x.png');bg.convert('RGB').save(P/'people_after_gray.png')
(P/'rod_rotation_provenance.json').write_text(json.dumps({'authority_commit':'372d96fe79e4bb090e5589ebef664c890cf67912','source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'rotations':rows,'source_nonrod_RGBA_changes':0,'changed_pixels':int(change.sum()),'child_head_neck_RGBA_changes':0,'artistic_character_redraw':False,'new_image_calls':0,'visible_finger_gaps_expose_same_full_scene_rods':True,'crane_pose_and_local_body_neck3_attachment_coordinates_unchanged':True,'whole_pair_registration_camera_lamp_unchanged':True},ensure_ascii=False,indent=2)+'\n');print(json.dumps(rows,indent=2))
