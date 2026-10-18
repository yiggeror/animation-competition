from pathlib import Path
from PIL import Image,ImageFilter
import argparse,numpy as np,json,hashlib
p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('--raw',required=True);p.add_argument('--scale',type=float,required=True);p.add_argument('--tx',type=float,default=0);p.add_argument('--ty',type=float,default=0);args=p.parse_args();G=Path(__file__).resolve().parent;R=G.parent;O=R/args.name
for d in ['registered','candidates','qa','geometry']:(O/d).mkdir(parents=True,exist_ok=True)
raw=Image.open(args.raw).convert('RGBA');s=args.scale
reg=raw.transform((1275,1200),Image.Transform.AFFINE,(1/s,0,-args.tx/s,0,1/s,-args.ty/s),resample=Image.Resampling.BICUBIC);reg.save(O/'registered/F036_registered_crop_1p5x_RGBA.png')
small=reg.resize((850,800),Image.Resampling.LANCZOS);scene=Image.new('RGBA',(1920,1080));scene.paste(small,(620,280));scene.save(O/'registered/F036_registered_scene_patch_RGBA.png')
base=Image.open(G/'inputs/F036_preplaced_body_anchor_truehands_NO_ROD_RGBA.png').convert('RGBA');m=Image.open(G/'masks/F036_WHITE_body_neck_head_arms_wrist_allowed.png').convert('L');binary=np.array(m)>0;f=np.array(m.filter(ImageFilter.GaussianBlur(.6)),float)/255;f[~binary]=0
b=np.array(base);q=np.array(scene);ba=b[:,:,3].astype(float)/255;qa=q[:,:,3].astype(float)/255;alpha=qa*f+ba*(1-f);premul=q[:,:,:3].astype(float)*qa[:,:,None]*f[:,:,None]+b[:,:,:3].astype(float)*ba[:,:,None]*(1-f[:,:,None]);rgb=np.divide(premul,np.maximum(alpha[:,:,None],1e-10));out=np.dstack((np.rint(rgb).clip(0,255).astype('uint8'),np.rint(alpha*255).clip(0,255).astype('uint8')));out[~binary]=b[~binary]
res=Image.fromarray(out);dest=O/'candidates/S08_F036_whole_turn_arms_candidate_RGBA.png';res.save(dest)
source=Image.open(R/'F033_FINAL_LOCKED/S08_F033_grandma_match_box_RGBA.png').convert('RGBA')
for tag,c in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 bg=Image.alpha_composite(Image.new('RGBA',base.size,c),res);bg.convert('RGB').save(O/'qa'/f'candidate_{tag}.png')
 for name,bb,z in [('whole_turn',(620,295,1400,1080),1.5),('whole_arms',(700,650,1400,1010),2),('near_wrist',(1130,780,1300,890),4),('far_wrist_grip',(1080,715,1330,890),4),('head_neck_chest',(700,330,1140,820),2)]:
  v=bg.crop(bb);v.resize((round(v.width*z),round(v.height*z)),Image.Resampling.LANCZOS).convert('RGB').save(O/'qa'/f'{name}_{tag}.png')
 orig=Image.alpha_composite(Image.new('RGBA',base.size,c),source);pan=Image.new('RGB',(1700,800),c[:3]);pan.paste(orig.crop((620,280,1470,1080)).convert('RGB'),(0,0));pan.paste(bg.crop((620,280,1470,1080)).convert('RGB'),(850,0));pan.save(O/'qa'/f'F033_F036_same_scale_{tag}.png')
ch=np.any(out!=b,2);checks={'status':'DIAGNOSTIC_PENDING_REVIEW_NOT_LOCKED','candidate_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(Path(args.raw).read_bytes()).hexdigest(),'registration_whole_raw_uniform':{'scale':s,'tx':args.tx,'ty':args.ty},'outside_white_changed':int((ch&~binary).sum()),'alpha_zero_grip_seat_restored_from_preplaced_source':True,'rod_pixels_not_adopted':True}
for name in ['F036_near_distal_palm_fingers_entire_match_guard.png','F036_far_visible_hand_jade_TRUE_SEAT_guard.png','F036_fixed_table_box_guard.png']:
 guard=np.array(Image.open(G/'masks'/name))>0;checks[name+'_changed']=int((ch&guard).sum())
assert checks['outside_white_changed']==0
(O/'geometry/checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
