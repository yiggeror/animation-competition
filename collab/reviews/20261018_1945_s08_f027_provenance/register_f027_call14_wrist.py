from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
R=Path('/workspace/scratch/f060b5601755/astra_s08_f027_parallel_20261018_1812');G=R/'F027_from_F025_input_gate_v3_5refs_1925';O=R/'F027_call14_result_wrist_registered'
for n in ['registered','candidates','qa','masks']:(O/n).mkdir(parents=True,exist_ok=True)
raw=Image.open(R/'F027_native_call02_global14/raw/F027_global_call14_native_raw.png').convert('RGBA');scale=1260/raw.width;tx=0;ty=(990-raw.height*scale)/2+21
reg=raw.transform((1260,990),Image.Transform.AFFINE,(1/scale,0,-tx/scale,0,1/scale,-ty/scale),Image.Resampling.BICUBIC);reg.save(O/'registered/F027_registered_crop_3x_RGBA.png')
patch=reg.resize((420,330),Image.Resampling.LANCZOS);patch.save(O/'registered/F027_registered_scene_patch_RGBA.png')
pre=np.array(Image.open(G/'inputs/F027_scene_preplaced_NO_ROD_RGBA.png'));a=pre.copy();p=np.zeros_like(a);p[660:990,900:1320]=np.array(patch)
mask=np.array(Image.open(G/'masks/F027_WHITE_allowed_BLACK_frozen.png'))>0
a[mask]=p[mask];Image.fromarray(a).save(O/'candidates/S08_F027_same_raw_candidate_RGBA.png')
rod=Image.open(G/'inputs/F027_TRUE_LOW_ROD_separate_CONTEXT_LAYER.png');im=Image.fromarray(a);imrod=Image.alpha_composite(rod,im)
old=Image.open(G/'source_snapshot/S08_F025_grandma_match_box_RGBA.png')
for name,col in [('dark',(34,42,53,255)),('light',(244,242,237,255))]:
 bg=Image.new('RGBA',im.size,col)
 comp=Image.alpha_composite(bg,imrod)
 comp.crop((570,270,1450,1030)).resize((1100,950),Image.Resampling.LANCZOS).convert('RGB').save(O/'qa'/('fullbody_'+name+'.png'))
 comp.crop((900,660,1320,990)).resize((1260,990),Image.Resampling.NEAREST).convert('RGB').save(O/'qa'/('whole_arm_'+name+'.png'))
 comp.crop((1080,780,1190,865)).resize((880,680),Image.Resampling.NEAREST).convert('RGB').save(O/'qa'/('wrist_collar_'+name+'.png'))
 comp.crop((905,820,1040,930)).resize((945,770),Image.Resampling.NEAREST).convert('RGB').save(O/'qa'/('near_wrist_'+name+'.png'))
 oldbg=Image.alpha_composite(bg,old).crop((900,660,1320,990)).resize((840,660),Image.Resampling.LANCZOS)
 newbg=comp.crop((900,660,1320,990)).resize((840,660),Image.Resampling.LANCZOS)
 pair=Image.new('RGB',(1680,700),col[:3]);pair.paste(oldbg,(0,40));pair.paste(newbg,(840,40));d=ImageDraw.Draw(pair);d.text((10,10),'LOCKED025',fill=(200,180,100));d.text((850,10),'027 SAME RAW NOMINAL - NOT LOCKED',fill=(200,180,100));pair.save(O/'qa'/('025_027_compare_'+name+'.png'))
checks={}
for n in ['far_CLOSED_HAND_JADE_AND_ALPHA0_SEAT_guard','near_HAND_MATCH_guard','actual_blue_cloth_guard','fixed_table_box_guard']:
 m=np.array(Image.open(G/'masks'/('F027_'+n+'.png')))>0
 checks[n]=int(np.any(a[m]!=pre[m],axis=1).sum())
checks['outside_white_changed']=int((np.any(a!=pre,axis=2)&~mask).sum())
(O/'REGISTER_AND_CHECKS.json').write_text(json.dumps({'raw_sha':'d3364d4e471f9259d2eaf79aea70ed69d4d6d33add96a76a0a0d8ebee2e13e17','uniform_raw_to_3x_crop_scale':scale,'tx':tx,'ty':ty,'limb_warp':False,'only_white_adopted':True,'white_pixels':int(mask.sum()),'checks':checks,'status':'NOMINAL_REGISTRATION_NOT_ADOPTED_PENDING_VISUAL'},indent=2))
print(json.dumps(checks))
