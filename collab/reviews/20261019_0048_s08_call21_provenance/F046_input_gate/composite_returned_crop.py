from pathlib import Path
from PIL import Image
from scipy.ndimage import distance_transform_edt,binary_dilation
import argparse,numpy as np,json,hashlib
p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('--raw',required=True);p.add_argument('--registration',required=True);args=p.parse_args();G=Path(__file__).resolve().parent;R=G.parent;O=R/args.name
for d in ['registered','candidates','qa','geometry','masks']:(O/d).mkdir(parents=True,exist_ok=True)
r=json.loads(Path(args.registration).read_text());s=r['scale'];tx=r['tx'];ty=r['ty'];raw=Image.open(args.raw).convert('RGBA');reg=raw.transform((1540,680),Image.Transform.AFFINE,(1/s,0,-tx/s,0,1/s,-ty/s),resample=Image.Resampling.BICUBIC);reg.save(O/'registered/F046_registered_crop_2x_RGBA.png');small=reg.resize((770,340),Image.Resampling.LANCZOS);scene=Image.new('RGBA',(1920,1080));scene.paste(small,(700,680));scene.save(O/'registered/F046_registered_scene_patch_RGBA.png')
base=Image.open(G/'inputs/F046_scene_preplaced_NO_ROD_RGBA.png').convert('RGBA');b=np.array(base);q=np.array(scene);w=np.array(Image.open(G/'masks/F046_WHITE_near_sleeve_arm_wrist_and_exposed_background.png'))>0;guide=np.array(Image.open(G/'masks/F046_FOREGROUND_near_arm_volume_CONSTRUCTION_ONLY.png'))>0;old=np.array(Image.open(G/'masks/F046_clear_superseded_near_arm_hand_and_cuff.png'))>0
f=np.clip(distance_transform_edt(w)/1.25,0,1);full=binary_dilation(guide|old,iterations=2)&w;f[full]=1;f[~w]=0;Image.fromarray(np.rint(f*255).astype('uint8')).save(O/'masks/ACTUAL_internal_feather_full_construction_adopt.png')
ba=b[:,:,3].astype(float)/255;qa=q[:,:,3].astype(float)/255;alpha=qa*f+ba*(1-f);premul=q[:,:,:3].astype(float)*qa[:,:,None]*f[:,:,None]+b[:,:,:3].astype(float)*ba[:,:,None]*(1-f[:,:,None]);rgb=np.divide(premul,np.maximum(alpha[:,:,None],1e-10));out=np.dstack((np.rint(rgb).clip(0,255).astype('uint8'),np.rint(alpha*255).clip(0,255).astype('uint8')));out[~w]=b[~w]
res=Image.fromarray(out);dest=O/'candidates/S08_F046_local_arm_candidate_RGBA.png';res.save(dest)
for tag,c in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 bg=Image.alpha_composite(Image.new('RGBA',base.size,c),res);bg.convert('RGB').save(O/'qa'/f'candidate_{tag}.png')
 for n,bb,z in [('whole_arm',(700,680,1470,1020),2),('wrists_grip',(1090,720,1375,900),4),('near_elbow',(865,855,1060,1010),4),('new_sleeve',(710,690,1000,920),3),('head_to_match',(700,330,1435,1010),1)]:
  im=bg.crop(bb);im.resize((im.width*z,im.height*z),Image.Resampling.LANCZOS).convert('RGB').save(O/'qa'/f'{n}_{tag}.png')
 orig=Image.alpha_composite(Image.new('RGBA',base.size,c),Image.open(R/'F043_FINAL_LOCKED/S08_F043_grandma_match_box_RGBA.png').convert('RGBA'));pan=Image.new('RGB',(1660,750),c[:3]);pan.paste(orig.crop((640,280,1470,1030)),(0,0));pan.paste(bg.crop((640,280,1470,1030)),(830,0));pan.save(O/'qa'/f'F043_F046_same_scale_{tag}.png')
ch=np.any(out!=b,2);checks={'status':'NOMINAL_DIAGNOSTIC_PENDING_REAL_CONTOUR_REVIEW_NOT_FINAL','candidate_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(Path(args.raw).read_bytes()).hexdigest(),'registration':r,'outside_white_changed':int((ch&~w).sum()),'semantic_note':'No final far occlusion claim: actual native near forearm contour must recover complete original far underlayer and full159AA naturally; no guide polygons in final.'}
for name in ['F046_fixed_near_distal_and_original_sourceover_AA_guard.png','F046_fixed_table_box_guard.png','F046_far_visible_hand_jade_TRUE_SEAT_guard.png']:checks[name+'_changed']=int((ch&(np.array(Image.open(G/'masks'/name))>0)).sum())
(O/'geometry/checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
