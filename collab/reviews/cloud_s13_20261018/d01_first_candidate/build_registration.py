#!/usr/bin/env python3
"""Only an authorized whole-image uniform registration candidate and QA composites.
No local character repair, no alpha cleanup, no generation, no scene render.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import hashlib, json, math

P=Path(__file__).resolve().parent
raw=P/'originals/S13_d01_call_001_raw.png'
im=Image.open(raw).convert('RGBA')
assert im.size==(1024,1536)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,a):p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
F='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
font=lambda n:ImageFont.truetype(F,n)

# Manually estimated actual solid crown / chin, excluding the cowlick. Not exact anatomy.
crown_y,chin_y=216,904
head_mid_x=(118+888)/2
s=640/(chin_y-crown_y)
tx=524-s*head_mid_x
ty=232-s*crown_y
params={'status':'candidate_pending_Astra_lock','method':'single uniform whole-image affine; no local warp or repaint',
 'source':str(raw.relative_to(P)),'source_sha256':sha(raw),'source_dimensions':[1024,1536],
 'manual_measurements':{'solid_crown_y':crown_y,'chin_y':chin_y,'cranial_envelope_left_x':118,'cranial_envelope_right_x':888,
 'uncertainty_source_px':4,'note':'人工近似框，H640仅同机位尺寸控制；非三维角度或精确关节测量。'},
 'forward_transform_raw_to_reference_source':[s,0,tx,0,s,ty],
 'registered_source_canvas':[1024,1536], 'resampling':'Pillow RGBA BICUBIC',
 'alpha_policy':'Original alpha preserved in raw; candidate alpha only resampled with the same whole-image transform. No threshold, tightening, recolor, or hair repair.',
 'shot_placement_after_registration':{'scale':.85,'translation':[330,-30],'shot_canvas':[1920,1080]},
 'combined_raw_to_shot':[s*.85,0,330+.85*tx,0,s*.85,-30+.85*ty],
 'output_lower_cut_scene_y':-30+.85*(s*1536+ty),
 'landmark_limit':'没有逐点拟合枕骨/颈根/双肩。H和头外包络对齐后仍须Astra实审；真实颈面优先，不能再扭局部凑灰棒坐标。'}
out=im.transform((1024,1536),Image.Transform.AFFINE,(1/s,0,-tx/s,0,1/s,-ty/s),Image.Resampling.BICUBIC)
candidate=P/'candidates/S13_d01_uniform_registered_rgba.png';out.save(candidate)
params['candidate_sha256']=sha(candidate)
put(P/'candidates/registration.json',params)

def composite(src,color):
 b=Image.new('RGBA',src.size,color);b.alpha_composite(src);return b.convert('RGB')

sheet=Image.new('RGB',(1536,880),'#f5f3ed');d=ImageDraw.Draw(sheet)
for i,col in enumerate([(245,245,245,255),(38,44,53,255),(160,175,180,255)]):
 a=composite(out,col);a.thumbnail((512,768));sheet.paste(a,(512*i,65))
 d.text((512*i+18,20),['浅底 / 配准候选','深底 / 配准候选','灰蓝底 / 配准候选'][i],font=font(23),fill='#23333e')
d.text((20,840),'仅刚性等比配准；原RGB/原alpha另存；非真实场景、非Canvas实渲、未锁母态。',font=font(23),fill='#914d36')
sheet.save(P/'qa/registered_on_three_backgrounds.jpg',quality=95)

# Whole-shot camera crop uses actual generated pixels on neutral backing, no code person.
sc=.85
layer=out.transform((1920,1080),Image.Transform.AFFINE,(1/sc,0,-330/sc,0,1/sc,30/sc),Image.Resampling.BICUBIC)
frame=composite(layer,(211,214,213,255));d=ImageDraw.Draw(frame)
d.text((36,24),'S13 d01 / 实际首图配准预览 / 中性底静态，非接景渲染 / 待Astra锁母态',font=font(28),fill='#4e4e49')
frame.save(P/'qa/registered_same_camera_neutral.jpg',quality=95)

sheet=Image.new('RGB',(1500,1030),'#f5f3ed');d=ImageDraw.Draw(sheet)
source=composite(im,(245,245,245,255));registered=composite(out,(245,245,245,255))
for x,a,label in [(20,source,'原件 / 未缩放'),(765,registered,'全图等比配准候选')]:
 crop=a.crop((245,470,865,1190));crop.thumbnail((710,850));sheet.paste(crop,(x,80))
 d.text((x,20),label,font=font(28),fill='#23333e')
d.text((25,940),'查看眼内视线、耳颌、颈肤连续接领口、双肩袖连接；不把设计角当成图精确角。',font=font(25),fill='#23333e')
sheet.save(P/'qa/eyes_jaw_neck_collar_actual.jpg',quality=95)

alpha=im.getchannel('A')
hist=alpha.histogram()
evidence={'raw_sha256':sha(raw),'candidate_sha256':sha(candidate),'raw_dimensions':list(im.size),
 'raw_mode':im.mode,'alpha_extrema':list(alpha.getextrema()),'alpha_zero_pixels':hist[0],
 'alpha_nonzero_pixels':sum(hist[1:]),'alpha_253_254_pixels':hist[253]+hist[254],
 'sample_fully_transparent_pixels_with_hidden_RGB':{'top_left':im.getpixel((0,0)),'left_y1200':im.getpixel((20,1200))},
 'halo_check':'实看正确合成的浅/深/灰蓝三底，无先前裸RGB显示所似的大范围软雾；不清alpha。深底发缘仍应由Astra核细小线缘。',
 'candidate_lower_cut_below_shot':params['output_lower_cut_scene_y']>1080,
 'poses_generated':1,'module_or_canvas_render':False}
assert evidence['candidate_lower_cut_below_shot']
put(P/'qa/image_validation.json',evidence)
print(json.dumps({'scale':s,'translation':[tx,ty],'raw_sha256':sha(raw),'candidate_sha256':sha(candidate),
 'lower_cut_scene_y':params['output_lower_cut_scene_y']},indent=2))
