#!/usr/bin/env python3
"""Execute Astra's fixed continuous-contour contract, copying same-coordinate full RGBA."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parent;SEM=ROOT.parent;PRE=SEM.parent;BASE=PRE.parent
for folder in ['candidate','qa']:(ROOT/folder).mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
contract=json.loads((ROOT/'source_reference/corridor_contract.json').read_text())
source_path=SEM/'candidates/same_call05_continuous_cloth_pending_review.png'
donor_path=PRE/'originals/d06_call05_raw.png'
assert sha(source_path)==contract['source_sha']
assert sha(donor_path)==contract['donor_sha']
before=Image.open(source_path).convert('RGBA');donor=Image.open(donor_path).convert('RGBA')
assert before.size==donor.size==(1672,941)
a,d=np.array(before),np.array(donor)
mask=np.array(Image.open(ROOT/'source_reference/continuous_skirt_outer_edge_allowed_REFERENCE.png').convert('L'))>0
arms=np.array(Image.open(SEM/'masks/complete_arms_sleeves_cuffs.png').convert('L'))>0
from_rows=np.zeros(mask.shape,dtype=bool)
for row in contract['rows']:
    for side in ['left','right']:
        if row[side] is not None:
            l,r=row[side];from_rows[row['y'],l:r]=True
from_rows &= ~arms
assert np.array_equal(from_rows,mask)
assert mask.sum()==contract['allowed_pixels']==8146
assert not (mask&arms).any()
yy,xx=np.indices(mask.shape)
head_neck=yy<=590
prop=(xx>=1035)&(xx<=1235)&(yy>=160)&(yy<=690)
assert not (mask&(head_neck|prop)).any()
c=a.copy();c[mask]=d[mask]
assert np.array_equal(c[~mask],a[~mask])
assert np.array_equal(c[mask],d[mask])
assert np.array_equal(c[arms|head_neck|prop],a[arms|head_neck|prop])
old_hard=np.array(Image.open(SEM/'masks/hard_protection_all.png').convert('L'))>0
assert np.array_equal(c[old_hard&~mask],a[old_hard&~mask])
changed=np.any(c!=a,axis=2);alpha_changed=c[:,:,3]!=a[:,:,3]
assert changed.sum()==contract['changed_pixels']==3682
assert alpha_changed.sum()==contract['alpha_changed']==3168
after=Image.fromarray(c)
candidate_path=ROOT/'candidate/F031_raw_clothing_and_contours_for_final_lock.png'
after.save(candidate_path)

def skirt_edge(arr,y):
    q=arr[y,:,3]>128;k=np.diff(np.r_[False,q,False].astype(int))
    runs=zip(np.flatnonzero(k==1),np.flatnonzero(k==-1))
    return next((int(l),int(r-1)) for l,r in runs if l<800<r)
edges=[]
for y in range(819,941):
    al,ar=skirt_edge(c,y);dl,dr=skirt_edge(d,y)
    if y>=820:assert al==dl,(y,al,dl)
    if y>=840:assert ar==dr,(y,ar,dr)
    edges.append({'y':y,'left_after':al,'right_after':ar,'left_donor':dl,'right_donor':dr})
left_jump=max(abs(q['left_after']-p['left_after']) for p,q in zip(edges,edges[1:]))
right_jump=max(abs(q['right_after']-p['right_after']) for p,q in zip(edges,edges[1:]))
assert left_jump<=2 and right_jump<=2
assert not changed[820].any()
assert not changed[840,950:].any()
(ROOT/'qa/continuous_alpha128_edge_rows.json').write_text(json.dumps(edges,indent=2)+'\n')

font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',20)
for bgname,bgc in [('gray',(105,112,121,255)),('dark',(32,40,48,255))]:
    sheet=Image.new('RGB',(1620,760),(243,245,247));draw=ImageDraw.Draw(sheet)
    draw.text((18,12),f'031连续裙外缘完整RGBA接回 · {bgname}底 · 左820／右840连续到画底940 · 0生成',font=font,fill='#25303b')
    for col,(title,im) in enumerate([('修前',before),('call05同位供体',donor),('实际接回／交031整态锁母',after)]):
        bg=Image.new('RGBA',im.size,bgc);bg.alpha_composite(im)
        x=12+col*540;draw.text((x,48),title,font=font,fill='#25303b')
        full=bg.crop((520,760,1060,941)).convert('RGB').resize((520,174),Image.Resampling.LANCZOS)
        sheet.paste(full,(x,84))
        for row,box in enumerate([(595,810,659,881),(944,833,1008,901)]):
            close=bg.crop(box).convert('RGB');close=close.resize((close.width*3,close.height*3),Image.Resampling.NEAREST)
            sheet.paste(close,(x+150,280+row*226))
    sheet.save(ROOT/f'qa/continuous_contour_before_donor_after_{bgname}.png')
lock=json.loads((BASE/'switch_segment/locked/F000_lock.json').read_text())
registered=after.transform((1536,864),Image.Transform.AFFINE,tuple(lock['registration']['inverse_pillow_affine']),
    resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
registered.save(ROOT/'candidate/F031_registered_for_final_lock.png')
frame=registered.crop((280,80,1304,656)).resize((1280,720),Image.Resampling.LANCZOS)
frame.save(ROOT/'qa/F031_1280x720_for_final_lock.png')
for bgname,bgc in [('gray',(105,112,121,255)),('dark',(32,40,48,255))]:
    bg=Image.new('RGBA',frame.size,bgc);bg.alpha_composite(frame);bg.convert('RGB').save(ROOT/f'qa/F031_1280x720_{bgname}.png')
checks={
    'status':'CONTINUOUS_CONTOUR_EXECUTED_READY_FOR_ASTRA_FINAL_F031_LOCK',
    'authorization_commit':'f17651aaee6f03cf0e48bd2939c4c6c1fb86cffb',
    'old_two_rectangle_limit_withdrawn':True,
    'source':{'path':str(source_path.relative_to(BASE)),'sha256':sha(source_path)},
    'donor':{'path':str(donor_path.relative_to(BASE)),'sha256':sha(donor_path)},
    'candidate':{'path':str(candidate_path.relative_to(BASE)),'sha256':sha(candidate_path),'size':list(after.size)},
    'same_coordinate_full_RGBA_copy':True,'translation':[0,0],'scale':1,'warp':False,
    'allowed_mask_pixels':int(mask.sum()),'RGBA_changed_pixels':int(changed.sum()),'alpha_changed_pixels':int(alpha_changed.sum()),
    'RGBA_changes_outside_allowed_corridor':int(changed[~mask].sum()),
    'alpha_changes_outside_allowed_corridor':int(alpha_changed[~mask].sum()),
    'complete_arm_guard_overlap':int((mask&arms).sum()),
    'head_neck_prop_guard_overlap':int((mask&(head_neck|prop)).sum()),
    'previous_hard_domain_changes_except_allowed_corridor':int(np.any(c[old_hard&~mask]!=a[old_hard&~mask],axis=1).sum()),
    'complete_hands_arms_prop_head_neck_RGBA_changes':int(np.any(c[arms|head_neck|prop]!=a[arms|head_neck|prop],axis=1).sum()),
    'left_contour_equals_donor_every_row_y820_940':True,'right_contour_equals_donor_every_row_y840_940':True,
    'largest_adjacent_row_alpha128_left_step':left_jump,'largest_adjacent_row_alpha128_right_step':right_jump,
    'left_top_y820_RGBA_changes':int(changed[820].sum()),'right_top_y840_RGBA_changes':int(changed[840,950:].sum()),
    'new_native_calls':0,'S09_native_calls_unchanged':12,'F031_native_calls_unchanged':7,'F037_calls':0,'F042_calls':0,
    'registration_and_camera_unchanged':True,
    'next_gate':'Astra final whole031 lock; do not dispatch037/042 before confirmation.'}
(ROOT/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in checks.items() if isinstance(v,(int,bool))},ensure_ascii=False))
print(json.dumps(checks['candidate'],ensure_ascii=False))
