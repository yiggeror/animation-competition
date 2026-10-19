from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as nd
import numpy as np, json, hashlib

R=Path(__file__).resolve().parent; B=R.parent
OLD=B/'F042_F048_NATIVE_call01_each_from_bd309770_20261019/single_group_reintegration_TRIAL'
P=B/'F036_REBUILD_FROM_ACTUAL030_ZERO_CALL_v1_20261019'
N=B/'F042_F048_CONTINUOUS_NATIVE_CLOTH_ONCE_20261019'
W,H=1024,1536; yy,xx=np.indices((H,W))
near=np.array(Image.open(P/'masks/NEAR_BARE_RIGHT_ARM_PROTECTED.png').convert('L'))>0
reports=json.loads((OLD/'geometry/ONE_GROUP_PER_STATE_SOURCE_MATRIX_CHECKS.json').read_text())['reports']
source036=B/'F036_CONTINUOUS_SLEEVE_CLOTH_sameM_zero_call_20261019/candidate/F036_CONTINUOUS_SLEEVE_CLOTH_SAME_M_TRIAL.png'
def shape(points):
 im=Image.new('L',(W,H));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
def warp_mask(a,M):
 inv=np.linalg.inv(np.vstack([M,[0,0,1]]))[:2].reshape(-1)
 return np.array(Image.fromarray(a.astype('uint8')*255).transform((W,H),Image.Transform.AFFINE,inv,Image.Resampling.BICUBIC))>0
for report in reports:
 f=report['frame']; out=R/f'F{f:03d}'; inp=out/'inputs';inp.mkdir(parents=True,exist_ok=True)
 M=np.array(report['single_similarity_complete_arm_hand_and_cloth'])
 base=np.array(Image.open(OLD/f'candidate/F{f:03d}_ONE_SIMILARITY_COMPLETE_ARM_CLOTH_TRIAL.png').convert('RGBA'))
 arm=warp_mask(np.array(Image.open(OLD/f'masks/F{f:03d}_RAW_COMPLETE_FAR_ARM_AND_SLEEVE.png').convert('L'))>0,M)
 arm=nd.binary_dilation(arm,iterations=1)
 fixed=(yy<470)|((xx<490)&(yy<640))|(yy>=1076)
 # The historical near-arm mask also carries a piece of old cloth/neck context.
 # Protect the actual physical near arm/hand, not that obsolete cloth patch.
 brgb=base[:,:,:3].astype(float)
 near_skin=near&(brgb[:,:,0]>190)&(brgb[:,:,1]>105)&(brgb[:,:,2]>95)&(brgb[:,:,0]>brgb[:,:,1]+15)
 nl,_=nd.label(nd.binary_closing(near_skin,iterations=2));nc=np.bincount(nl.ravel());nc[0]=0
 near_physical=nd.binary_dilation(nd.binary_fill_holes(nl==nc.argmax()),iterations=3)&near
 human=near_physical|arm|fixed
 pinch=report['mapped_anchors'][2]; px,py=pinch
 # This is an explicitly authorized TECHNICAL MASS GUIDE, never final drawing.
 # The whole face is filled; no puppet/rod pixels or old sampled cloth are used.
 outline=[(253,878),(320,799),(373,755),(468,753),(500,743),(515,730),(548,718),(585,708),(625,690),(666,674),(px-8,py-7),(px+5,py-4),(px+43,py+28),(833,711),(915,768),(969,820),(997,874),(1003,918),(978,941),(1002,968),(998,1000),(970,1042),(946,1072),(922,1055),(865,1020),(839,1033),(811,1074),(763,1033),(692,1018),(623,1008),(544,992),(475,969),(407,946),(334,921),(273,902)]
 face=shape(outline)
 # Smooth navy volume carries radial folds through every formerly missing strip.
 dx=xx-px;dy=yy-py
 basecol=np.array([37.,51.,81.])
 volume=1.0+0.10*np.cos((dx*.42-dy*.9)/46)+0.08*np.cos((dx*.8-dy*.22)/38)-0.12*np.clip((yy-850)/330,0,1)
 rgb=np.clip(basecol[None,None,:]*volume[:,:,None],0,255).astype('uint8')
 guide=np.zeros((H,W,4),dtype='uint8');guide[face,:3]=rgb[face];guide[face,3]=255
 g=Image.fromarray(guide); d=ImageDraw.Draw(g)
 d.line(outline+[outline[0]],fill=(17,26,46,255),width=2,joint='curve')
 folds=[[(px,py+2),(790,746),(880,836),(947,917)],[(px+3,py+8),(762,779),(809,888),(839,1031)],[(px-4,py+4),(657,755),(576,837),(450,909)],[(px-6,py+7),(709,805),(688,914),(763,1031)],[(333,920),(440,901),(544,960),(624,981),(692,1017)],[(839,1031),(881,954),(950,939)]]
 for line in folds:d.line(line,fill=(21,32,55,255),width=3,joint='curve')
 # One tangible turned cotton lip, not separate patches; hand will cover its peak.
 d.line([(515,730),(548,720),(585,710),(625,693),(666,677),(px-8,py-3),(px+2,py+3),(px+43,py+31),(833,715),(915,772),(969,824)],fill=(66,79,108,255),width=5,joint='curve')
 target=Image.new('RGBA',(W,H),(236,239,242,255));target.alpha_composite(g)
 target.convert('RGB').save(inp/'01_COMPLETE_CONTINUOUS_CLOTH_MASS_TARGET_NO_PROPS.png')
 mask=face&~human
 Image.fromarray(mask.astype('uint8')*255).save(inp/'04_WHOLE_CLOTH_WHITE_HUMANS_BLACK.png')
 Image.fromarray(face.astype('uint8')*255).save(out/'CLOTH_FACE_COORDINATES.png')
 Image.fromarray(human.astype('uint8')*255).save(out/'HUMANS_PROTECTED_COORDINATES.png')
 context=np.array(target); context[near_physical|arm]=base[near_physical|arm]
 ci=Image.fromarray(context);ci.crop((385,490,855,815)).convert('RGB').save(inp/'02_SAME_STATE_TRUE_HANDS_PINCH_FOLDS_ONLY.png')
 # Small internal material-only crop; no competing pose or props.
 Image.open(source036).crop((900,819,945,850)).convert('RGB').resize((270,186)).save(inp/'03_LOCKED036_NAVY_WHITE_FLOWER_MATERIAL_ONLY.png')
 metrics={'frame':f,'base_commit':'8c41ca4517978ca3a4e6a44260ed1d3426f12edd','fixed_M_not_refit':M.tolist(),'mapped_pinch_preserved':pinch,'outline':outline,'cloth_face_pixels':int(face.sum()),'white_edit_pixels':int(mask.sum()),'human_white_overlap':int((mask&human).sum()),'historical_near_mask_refined_to_physical_skin_ink_not_old_cloth_or_neck_context':True,'first_target_has_any_transparent_pixel':False,'first_target_is_technical_mass_guide_not_native_drawing':True,'first_target_sources':'smooth continuous navy volume guidance plus fold ridges; no old raw/puppet/rod pixels','material_source036_sha256':hashlib.sha256(source036.read_bytes()).hexdigest(),'material_crop':[900,819,945,850],'ordered_inputs':[{'order':i,'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for i,p in enumerate(sorted(inp.glob('*.png')),1)]}
 (out/'PREPARATION.json').write_text(json.dumps(metrics,indent=2)+'\n')
 print(f,'prepared',mask.sum(),'white pixels; protected overlap',int((mask&human).sum()))
