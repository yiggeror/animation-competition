#!/usr/bin/env python3
"""Archive-check one real native response, register the whole crop uniformly, and restore locks."""
from pathlib import Path
import base64,hashlib,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ret=json.loads((ROOT/'requests/F057_call03_raw_return.json').read_text())
raw_path=ROOT/'originals/F057_call03_raw.png';raw=Image.open(raw_path).convert('RGBA')
assert raw_path.read_bytes()==base64.b64decode(ret['image_url'].split(',',1)[1])
freeze=json.loads((ROOT/'requests/F057_call03_freeze.json').read_text())
for row in freeze['inputs']:assert sha(Path(row['path']))==row['sha256'],row['path']
for rel,digest in freeze['other_frozen_files'].items():assert sha(ROOT/rel)==digest,rel
args=json.loads((ROOT/'requests/F057_call03_arguments.json').read_text())
assert args['prompt']==(ROOT/'requests/F057_call03_prompt.txt').read_text().rstrip('\n')
prep=json.loads((ROOT/'preparation_checks.json').read_text());reg=prep['registration_unchanged']
source=Image.open(ROOT/'source_reference/angle_14_PREPOSITION_NOT_ART.png').convert('RGBA');a=np.array(source)
mask=np.array(Image.open(ROOT/'masks/final_connection_only.png'))>0
crop=prep['crop_xyxy'];x0,y0,x1,y1=crop
q=raw.width/(x1-x0)
aligned=raw.transform((x1-x0,y1-y0),Image.Transform.AFFINE,(q,0,0,0,q,0),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
aligned.save(ROOT/'qa/call03_whole_crop_uniform_alignment.png')
b=np.array(aligned);c=a.copy();local=c[y0:y1,x0:x1];local_mask=mask[y0:y1,x0:x1]
local[local_mask]=b[local_mask]
assert np.array_equal(c[~mask],a[~mask])
for guard in ['protected_complete_distal_jade_hand','protected_real_near_foot_and_ankle','protected_head_near_arm_and_body_except_allowed_far_connection']:
    g=np.array(Image.open(ROOT/f'masks/{guard}.png'))>0
    assert np.array_equal(c[g],a[g]),guard
candidate=Image.fromarray(c)
candidate_path=ROOT/'candidate/F057_call03_raw_locked_PENDING_REVIEW.png';candidate.save(candidate_path)
inverse=(1/reg['s'],0,-reg['tx']/reg['s'],0,1/reg['s'],-reg['ty']/reg['s'])
world=candidate.transform((1672,941),Image.Transform.AFFINE,inverse,resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
world.save(ROOT/'candidate/F057_call03_world_PENDING_REVIEW.png')
for bg_name,bg_color in [('gray',(218,225,231,255)),('dark',(34,42,50,255))]:
    bg=Image.new('RGBA',candidate.size,bg_color);bg.alpha_composite(candidate);bg.convert('RGB').save(ROOT/f'qa/F057_call03_full_{bg_name}.png')
    wb=Image.new('RGBA',world.size,bg_color);wb.alpha_composite(world);wb.convert('RGB').save(ROOT/f'qa/F057_call03_world_{bg_name}.png')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
contexts=[('远袖至近端前臂',(855,305,1000,540)),('裤根完整接缝',(695,525,895,615)),('近裤脚／踝鞋',(748,920,985,1010))]
sheet=Image.new('RGB',(1500,900),(243,245,248));draw=ImageDraw.Draw(sheet)
for row,(label,box) in enumerate(contexts):
    for col,(title,im) in enumerate([('冻结14°预摆',source),('一次返回重组／待审',candidate)]):
        patch=im.crop(box);bg=Image.new('RGBA',patch.size,(216,224,231,255));bg.alpha_composite(patch)
        factor=2 if row==0 else 3
        im2=bg.convert('RGB').resize((patch.width*factor,patch.height*factor),Image.Resampling.NEAREST)
        px=15+col*750;py=[45,545,755][row]
        # First row needs most height, other two use source scale for compact contact review.
        if row>0:im2=bg.convert('RGB').resize((patch.width*2,patch.height*2),Image.Resampling.NEAREST)
        sheet.paste(im2,(px,py));draw.text((px,py-28),label+' · '+title,font=font,fill='#26333d')
sheet.save(ROOT/'qa/three_connections_before_after.png')

def hsv_of(arr):return np.array(Image.fromarray(arr).convert('RGB').convert('HSV'))
ha,hc=hsv_of(a),hsv_of(c)
yy,xx=np.indices(mask.shape)
skin=lambda h:(h[:,:,0]>=10)&(h[:,:,0]<=28)&(h[:,:,1]>=45)&(h[:,:,1]<=175)&(h[:,:,2]>155)
blue=lambda h:(h[:,:,0]>=125)&(h[:,:,0]<=172)&(h[:,:,1]>40)&(h[:,:,2]>110)
navy=lambda h:(h[:,:,0]>=125)&(h[:,:,0]<=190)&(h[:,:,1]>30)&(h[:,:,2]>=35)&(h[:,:,2]<120)
color_checks={}
for name,selector,region in [('far_skin',skin,(xx>890)&(yy>370)&(yy<510)),('side_blouse',blue,(xx>875)&(yy>310)&(yy<520)),('navy_root',navy,(yy>=545)&(yy<600))]:
    common=selector(ha)&selector(hc)&mask&region&(a[:,:,3]>=245)&(c[:,:,3]>=245)
    luminance=a[:,:,:3]@np.array([.2126,.7152,.0722])
    vals=luminance[common]
    groups={}
    if len(vals):
        # Split shadow and ordinary fill by source luminance; do not average them into one skin/cloth color.
        cut=np.percentile(vals,30)
        for tone,sub in [('shadow',common&(luminance<=cut)),('fill',common&(luminance>cut))]:
            n=int(sub.sum())
            if n:
                old=np.median(a[:,:,:3][sub],axis=0);new=np.median(c[:,:,:3][sub],axis=0)
                groups[tone]={'pixels':n,'source_median_RGB':old.tolist(),'candidate_median_RGB':new.tolist(),'median_RGB_delta':(new-old).tolist()}
    color_checks[name]=groups
old_gap=(a[566:576,847:869,3]<128)
remaining=int((c[566:576,847:869,3][old_gap]<128).sum())
report={'status':'ONE_LOCAL_RETURN_RECOMPOSED_PENDING_ACTUAL_REVIEW','this_round_native_calls':1,'S07_total_native_calls':3,'other10_calls':0,
    'raw_sha256':sha(raw_path),'raw_size':list(raw.size),'raw_return_byte_equal':True,
    'frozen_inputs_and_prompt_verified':True,'crop':crop,'one_uniform_raw_to_crop_scale':1/q,'one_uniform_raw_to_crop_translation':[0,0],
    'output_height_after_uniform_scale':raw.height/q,'requested_height':y1-y0,'no_nonuniform_or_segment_scale':True,
    'candidate_sha256':sha(candidate_path),'final_mask_pixels':int(mask.sum()),'candidate_changed_pixels':int(np.any(c!=a,axis=2).sum()),
    'outside_final_mask_changes':int(np.any(c[~mask]!=a[~mask],axis=1).sum()),'protected_head_near_arm_distal_jade_hand_real_foot_ankle_changes':0,
    'source_old_hip_gap_pixels_in_review_box':int(old_gap.sum()),'remaining_hip_gap_alpha128_pixels_in_same_box':remaining,
    'source_and_candidate_world_registration':reg,'selected_wrist_world_unchanged':prep['selected_wrist_world'],
    'ankle_horizontal_span_source_preserved_world':64,'actual_sole_world_source_preserved':774.874330515797,
    'material_comparison_same_scene_mother_pixels_shadow_and_fill_separate':color_checks,
    'no_new_requests_in_flight':True,'full_figure_adoption_not_yet_claimed':True}
(ROOT/'qa/call03_actual_review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
