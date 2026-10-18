#!/usr/bin/env python3
"""One whole-image similarity registration; no anatomy/prop/local alpha repair."""
from pathlib import Path
import hashlib
import json
import math
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
raw_path=ROOT/'originals/F000_call01_raw.png'
raw_bytes=raw_path.read_bytes()
raw=Image.open(raw_path);raw.load()
# Manual visual measurements, approximate: skull crown excludes the cowlick.
source={'crown':[800.,58.],'chin':[860.,455.],'waist':[800.,787.],
        'tail':[853.,638.],'lamp':[1227.,563.]}
scale=250./(source['chin'][1]-source['crown'][1])
tx=745.-scale*source['crown'][0]
ty=120.-scale*source['crown'][1]
def project(p):return [scale*p[0]+tx,scale*p[1]+ty]
candidate=raw.transform((1536,864),Image.Transform.AFFINE,
                        (1/scale,0,-tx/scale,0,1/scale,-ty/scale),
                        resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
out=ROOT/'candidate/F000_registered_v1.png';candidate.save(out)
assert Image.open(out).size==(1536,864)
assert raw_path.read_bytes()==raw_bytes
target={'crown':[745.,120.],'waist':[750.,580.],'tail':[860.,535.],
        'lamp':[1029.037019600587,489.7066671070589]}
projected={k:project(p) for k,p in source.items()}
prop_len=math.dist(projected['tail'],projected['lamp'])
mid=[(projected['tail'][i]+projected['lamp'][i])/2 for i in [0,1]]
report={
 'status':'REGISTRATION_REVIEW_CANDIDATE_NOT_LOCKED',
 'source':'originals/F000_call01_raw.png','source_size':list(raw.size),
 'source_sha256':hashlib.sha256(raw_bytes).hexdigest(),
 'destination':'candidate/F000_registered_v1.png','destination_size':[1536,864],
 'destination_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
 'operation':'uniform scale plus translation applied to entire RGBA image only',
 'scale':scale,'translation_xy':[tx,ty],
 'inverse_pillow_affine':[1/scale,0,-tx/scale,0,1/scale,-ty/scale],
 'resampling':'Pillow BICUBIC','local_warp':False,'local_prop_resize':False,
 'repainting':False,'alpha_denoise':False,
 'measurement_method':'manual visual crown/chin/waist and flashlight endpoints; approximate, not anatomical ground truth',
 'source_manual_points':source,'projected_manual_points':projected,'reference_points':target,
 'point_residual_pixels':{k:math.dist(projected[k],target[k]) for k in target},
 'flashlight_length_registered_approx':prop_len,'flashlight_length_reference':175.,
 'flashlight_scale_ratio_approx':prop_len/175.,'flashlight_midpoint_registered_approx':mid,
 'limits':'原图真实持握需要图审；此全局配准只能对齐身份尺度，不能修复手电相对人物偏大或操作区偏高。不得分块缩筒或拉手冒充配准通过。',
 'image_generation_requests_this_batch':1,'raw_outputs':1,'locked_mother_frames':0
}
(ROOT/'candidate/registration.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')

font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',20)
for name,color in [('light',(236,239,241,255)),('dark',(35,40,46,255))]:
    bg=Image.new('RGBA',candidate.size,color);bg.alpha_composite(candidate)
    bg.convert('RGB').save(ROOT/'qa'/('registered_'+name+'_bg.png'))

bg=Image.new('RGBA',candidate.size,(239,242,242,255));bg.alpha_composite(candidate)
d=ImageDraw.Draw(bg)
ref=json.loads((ROOT.parent/'geometry/d01_reference_v2.json').read_text())['pose']
for side in ['near','far']:
    pts=[tuple(ref['joints'][side+'_'+k]) for k in ['shoulder','elbow','wrist']]
    d.line(pts,fill=(60,150,200,255),width=3)
    for x,y in pts:d.ellipse((x-5,y-5,x+5,y+5),outline=(30,115,180,255),width=2)
for k in ['tail','lamp','waist']:
    x,y=target[k];xx,yy=projected[k]
    d.ellipse((x-7,y-7,x+7,y+7),outline=(0,115,180,255),width=3)
    d.line((x,y,xx,yy),fill=(190,45,35,255),width=2)
    d.text((x+12,y+8),k,font=font,fill=(15,100,160,255))
d.text((35,25),'F000 首图全局配准核对：蓝=冻结参考，红线=端点残差；非锁定画稿',font=font,fill=(140,40,30,255))
d.text((35,60),'只统一缩放平移，未分别改头、手或手电。参考手电175，实际配准后约'+str(round(prop_len))+'。',font=font,fill=(60,60,60,255))
bg.convert('RGB').save(ROOT/'qa/registered_reference_overlay.png')
print(json.dumps({k:report[k] for k in ['scale','translation_xy','flashlight_length_registered_approx','flashlight_scale_ratio_approx','point_residual_pixels','status']},ensure_ascii=False))
