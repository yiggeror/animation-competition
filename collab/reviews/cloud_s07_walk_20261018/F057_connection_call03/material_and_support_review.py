#!/usr/bin/env python3
"""Expose actual palette offsets and exact unchanged support; no color editing or generation."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont

R=Path(__file__).resolve().parent;B=R.parent
mother_path=B/'F057_local_repair/sources/G037/production/F037_grandma_rgba.png'
source_path=R/'source_reference/angle_14_PREPOSITION_NOT_ART.png'
candidate_path=R/'candidate/F057_call03_minimum_connections_PENDING.png'
a=np.array(Image.open(source_path).convert('RGBA'));c=np.array(Image.open(candidate_path).convert('RGBA'))
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',19)
sheet=Image.new('RGB',(1320,770),(240,244,247));draw=ImageDraw.Draw(sheet)
draw.text((18,15),'实际材质对照：底色／暗部各列；只读量核，不自动重染母图',font=font,fill='#25323d')
samples={}
items=[('G037实际站姿母源',mother_path,'mother'),('F057冻结母源近右臂',source_path,'near'),('F057冻结母源远左臂',source_path,'far'),('F057接续后远左臂',candidate_path,'far')]
for row,(label,path,region) in enumerate(items):
    ar=np.array(Image.open(path).convert('RGBA'));h=np.array(Image.fromarray(ar).convert('RGB').convert('HSV'));y,x=np.indices(ar.shape[:2])
    skin=(h[:,:,0]>=10)&(h[:,:,0]<=28)&(h[:,:,1]>=45)&(h[:,:,1]<=175)&(h[:,:,2]>155)&(ar[:,:,3]>=245)
    if region=='mother':skin&=y>=350
    elif region=='near':skin&=(x>=650)&(x<=750)&(y>=390)&(y<=560)
    else:skin&=(x>900)&(x<950)&(y>370)&(y<510)
    lum=ar[:,:,:3]@np.array([.2126,.7152,.0722]);v=lum[skin]
    lower,upper=np.percentile(v,[15,40]);summary={}
    draw.text((20,75+row*155),label,font=font,fill='#25323d')
    for col,(tone,m) in enumerate([('暗部',skin&(lum<=lower)),('底色',skin&(lum>=upper))]):
        rgb=np.median(ar[:,:,:3][m],axis=0);summary[tone]={'pixels':int(m.sum()),'median_RGB':rgb.tolist()}
        px=420+col*430;py=68+row*155;draw.rectangle((px,py,px+155,py+90),fill=tuple(map(int,rgb)))
        draw.text((px+170,py+12),tone+' '+str(tuple(map(int,rgb))),font=font,fill='#25323d')
    samples[label]=summary
draw.text((18,710),'暗部分组为各皮肤ROI较低15%亮度，底色为较高60%；是可见色阶取样，不是物理光照重建。',font=font,fill='#43515d')
sheet.save(R/'qa/material_shadow_fill_actual_comparison.png')
reg=json.loads((R/'preparation_checks.json').read_text())['registration_unchanged']
shoe_guard=np.array(Image.open(R/'masks/postreturn_actual_shoe_ankle_material_PROTECTED.png'))>0
distal=np.array(Image.open(R/'masks/protected_complete_distal_jade_hand.png'))>0
assert np.array_equal(c[shoe_guard],a[shoe_guard]);assert np.array_equal(c[distal],a[distal])
support={}
for name,box in [('far',(575,900,780,1050)),('near',(780,900,1000,1050))]:
    x0,y0,x1,y1=box;before=np.array(a[y0:y1,x0:x1]);after=np.array(c[y0:y1,x0:x1])
    orig_foot=(before[:,:,3]>128)&(np.indices(before.shape[:2])[0]+y0>=990)
    assert np.array_equal(before[orig_foot],after[orig_foot])
    ys=np.where(after[:,:,3]>128)[0];sole=int(ys.max()+y0)
    support[name]={'actual_sole_native_y':sole,'actual_sole_world_y':sole*reg['s']+reg['ty'],'opaque_original_foot_pixels_below990_RGBA_changes':0}
report={'status':'ACTUAL_COLOR_AND_SUPPORT_EVIDENCE_PENDING_ASTRA_PALETTE_JUDGMENT',
    'candidate_sha256':hashlib.sha256(candidate_path.read_bytes()).hexdigest(),
    'G037_mother_sha256':hashlib.sha256(mother_path.read_bytes()).hexdigest(),
    'skin_shadow_fill_samples':samples,'sampling_limit':'Separate luminance-ranked skin shadow/fill samples; visible palette comparison, not a physical lighting fit.',
    'palette_finding':'The frozen F057 mother is already lighter/pinker than accepted G037. The local returned forearm moves closer to G037, while all head/near arm and original blouse fill/shadow pixels are kept. No global recolor is authorized or performed. Do not call G037 palette exactly matched.',
    'complete_original_near_shoe_and_ankle_material_RGBA_changes':int(np.any(c[shoe_guard]!=a[shoe_guard],axis=1).sum()),
    'complete_distal_jade_hand_RGBA_changes':int(np.any(c[distal]!=a[distal],axis=1).sum()),
    'support_actual':support,'horizontal_ankle_distance_source_preserved_world':64,
    'body_and_leg_chain_changes':'No joint or segment transform after frozen14deg scaffold; only authorized seam pixels taken; source proxy lengths are not anatomical measurements.',
    'new_native_calls_unchanged':1,'S07_total_calls_unchanged':3,'no_request_in_flight':True}
(R/'qa/material_and_support_actual_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
