from pathlib import Path
import json,math,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation,binary_fill_holes,binary_closing,distance_transform_edt
PACK=Path(__file__).resolve().parent;OLD=PACK/'cam20_crane_lamp_left_001';P=PACK/'cam20_crane_raised_zero_call_002';P.mkdir(exist_ok=True)
A=np.array(Image.open(OLD/'people_F000_rods_rotated.png').convert('RGBA'));B=A.copy();H,W=A.shape[:2];yy,xx=np.indices((H,W));old=json.loads((OLD/'registration_input.json').read_text());new=json.loads(json.dumps(old));r,g,b=A[:,:,:3].astype(float).transpose(2,0,1)
rawmask=np.array(Image.open(PACK/'F000/arm_correction_001/masks/protect_L_palm_bracelet.png').convert('L'))>0
skin=(A[:,:,3]>180)&(r>185)&(g>130)&(b>g*.73)&(r>g+12)&(xx>=890)&(xx<989)&(yy>=285)&(yy<372)
hand=Image.new('L',(W,H));ImageDraw.Draw(hand).polygon([(913,292),(922,290),(936,293),(950,301),(962,317),(975,337),(983,344),(967,358),(954,353),(935,354),(921,351),(914,345),(906,334),(901,322),(898,311),(899,303),(905,299),(913,302)],fill=255)
palm=(binary_dilation(binary_fill_holes(binary_closing(skin,iterations=2)),iterations=2)|(np.array(hand)>0))&rawmask
wood=(A[:,:,3]>5)&(r>g+10)&(g>b+10)&(b<g*.71);delta=math.radians(4);c,s=math.cos(delta),math.sin(delta);Q=np.array([[c,-s],[s,c]]);oldall=np.zeros((H,W),bool);rotations={};rows=[]
geo=json.loads((P/'geometry_preflight.json').read_text());ends={e['id']:e['master_px'] for e in geo['rod_endpoints']};new['crane_root_m']=[1.8,1.21]
for role in ['C_N','C_B']:
 q=old['rods'][role];p=np.array(q['grip_master_px']);tip=np.array(q['shaft_tip_master_px']);ep=np.array(ends[role]);targetm=(ep[1]-p[1])/(ep[0]-p[0]);delta=math.atan(targetm)-math.atan(q['slope']);assert math.radians(3)<=delta<=math.radians(5);c,s=math.cos(delta),math.sin(delta);Q=np.array([[c,-s],[s,c]]);u=(tip-p)/np.linalg.norm(tip-p);along=(xx-p[0])*u[0]+(yy-p[1])*u[1];dist=np.abs(yy-q['slope']*xx-q['intercept'])/math.hypot(1,q['slope']);band=(dist<5.5)&(along>=-32)&(along<=np.linalg.norm(tip-p)+4);outside=band&~palm&(A[:,:,3]>0);inside=binary_dilation(band&palm&wood,iterations=1)&band&palm&((b<g*.74)|(A[:,:,3]<80));mask=outside|inside;oldall|=mask;L=np.zeros_like(A);take=mask&(along>45)&~palm;L[take]=A[take];inv=(c,s,p[0]-c*p[0]-s*p[1],-s,c,p[1]+s*p[0]-c*p[1]);rotations[role]=np.array(Image.fromarray(L).transform((W,H),Image.Transform.AFFINE,inv,Image.Resampling.BICUBIC));nt=p+Q@(tip-p);slope=(nt[1]-p[1])/(nt[0]-p[0]);new['rods'][role].update(slope=float(slope),intercept=float(p[1]-slope*p[0]),shaft_tip_master_px=nt.tolist(),rigid_angle_delta_degrees=math.degrees(delta))
 rows.append({'id':role,'pivot_master_px':p.tolist(),'screen_clockwise_rotation_degrees':math.degrees(delta),'old_visible_tip':tip.tolist(),'new_visible_tip':nt.tolist(),'scale':1,'part':'body' if role=='C_B' else 'neck3','at':[-75,6] if role=='C_B' else [10,0]})
oldgap=np.array(Image.open(OLD/'mask_new_finger_gap_axis_openings.png').convert('L'))>0;inside=(oldall&palm)|oldgap;outside=oldall&~palm;B[outside]=0;donor=skin&~oldall&~oldgap;_,idx=distance_transform_edt(~donor,return_indices=True);B[inside]=A[idx[0][inside],idx[1][inside]]
gaps=np.zeros((H,W),bool)
for role in ['C_N','C_B']:
 q=new['rods'][role];lo,hi=(915,928) if role=='C_N' else (923,929);dist=np.abs(yy-q['slope']*xx-q['intercept'])/math.hypot(1,q['slope']);gaps|=(xx>=lo)&(xx<hi)&(dist<1.15)&palm
B[gaps]=0
for role,L in rotations.items():
 take=(L[:,:,3]>0)&(B[:,:,3]<80)&~palm;B[take]=L[take]
allowed=oldall|oldgap|gaps
for L in rotations.values():allowed|=L[:,:,3]>0
changed=np.any(A!=B,2);assert not np.any(changed&~allowed);assert np.array_equal(A[:,1000:],B[:,1000:]);assert np.array_equal(A[:,:660],B[:,:660]);Image.fromarray(B).save(P/'people_F000_rods_rotated.png');Image.fromarray(np.uint8(changed)*255).convert('RGB').save(P/'mask_all_changed_pixels.png');Image.fromarray(np.uint8(gaps)*255).convert('RGB').save(P/'mask_new_finger_gap_axis_openings.png');new['master']='people_F000_rods_rotated.png';new['crane_axis_refinement_authority']='Astra relays Opus: raise same two crane axes 3-5deg around unchanged high jade hand; actual per-rod screen-clockwise angle within 3-5deg from unchanged crane pose raised 7cm';(P/'registration_input.json').write_text(json.dumps(new,ensure_ascii=False,indent=2)+'\n')
for name in ['index.html','check_and_render.cjs','scene.mjs']:
 text=(OLD/name).read_text();text=text.replace('cam20_crane_lamp_left_001','cam20_crane_raised_zero_call_002')
 (P/name).write_text(text)
report={'source_commit_full':'445d2921aead0d6cbd20d142d2d341f9564b0e6c','source_path':str(OLD/'people_F000_rods_rotated.png'),'source_sha256':hashlib.sha256((OLD/'people_F000_rods_rotated.png').read_bytes()).hexdigest(),'source_registration_sha256':hashlib.sha256((OLD/'registration_input.json').read_bytes()).hexdigest(),'new_image_calls':0,'character_redraw':False,'T_rods_RGBA_changed':0,'non_rod_non_gap_RGBA_changed':0,'palm_jade_character_camera_lamp_fixed':True,'crane_local_pose_and_part_at_fixed':True,'rotations':rows,'changed_pixels':int(changed.sum()),'crane_root_old_m':[1.8,1.14],'crane_root_new_m':[1.8,1.21],'one_formal_CAM20_only':True};(P/'zero_call_provenance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(rows))
