"""Composite a construction target inside the declared edit mask only."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib, json
import numpy as np

ROOT=Path(__file__).resolve().parent
raw=Image.open(ROOT.parent/'generation_001/S20_F000_call001_raw.png').convert('RGBA')
src=np.array(raw)
edit=np.array(Image.open(ROOT/'masks/edit_white.png'))
layer=np.array(Image.open(ROOT/'arm_volume_layers.png').convert('RGBA'))
assert layer.shape==src.shape
target=src.copy()
clear=np.array(Image.open(ROOT/'masks/clear_old_limb_occupancy.png'))==255
target[clear]=0
# Retain source shirt/collar where no new volume is present; explicit old-limb
# corridors alone are erased. This avoids manufacturing holes at the collar.
paint=(edit==255)&(layer[:,:,3]>0)
under=Image.fromarray(target)
over=np.zeros_like(layer);over[paint]=layer[paint]
under.alpha_composite(Image.fromarray(over))
target=np.array(under)
# The mask is a hard pixel contract, including original antialias outside it.
target[edit==0]=src[edit==0]
target_im=Image.fromarray(target)
target_im.save(ROOT/'S20_F000_arms_target.png')
assert np.array_equal(target[edit==0],src[edit==0])

def gray(im):
    out=Image.new('RGBA',im.size,(140,140,140,255))
    out.alpha_composite(im.convert('RGBA'))
    return out.convert('RGB')

gray(target_im).save(ROOT/'qa/target_full_gray_QA.png')
rawgray=gray(raw);targetgray=gray(target_im)
xray=Image.open(ROOT/'full_arm_volume_xray.png').convert('RGB')
fontpath=ROOT.parents[4]/'assets/fonts/NotoSansSC-VF.ttf'
font=ImageFont.truetype(str(fontpath),27) if fontpath.exists() else ImageFont.load_default()
small=ImageFont.truetype(str(fontpath),22) if fontpath.exists() else font
box=(875,235,1220,485)
board=Image.new('RGB',(2140,670),'#f3f4f5');d=ImageDraw.Draw(board)
panels=[('原件：高掌误接远肩／低掌误接近肩',rawgray),
        ('纠正target：近L→高掌；远R→低掌',targetgray),
        ('完整体量：远R藏在前衣层后',xray)]
for idx,(title,im) in enumerate(panels):
    x=20+idx*705
    d.text((x,20),title,font=small,fill='#263743')
    crop=im.crop(box).resize((690,500),Image.Resampling.NEAREST)
    board.paste(crop,(x,75))
    if idx==2:
        # Board labels locate shoulder/elbow/wrist volumes; never target pixels.
        for label,point,color in [('近L肩',(1148,283),'#167274'),('近L肘',(1120,419),'#167274'),
                                  ('远R肩',(1067,285),'#795d89'),('远R肘',(1076,435),'#795d89')]:
            px=x+(point[0]-box[0])*2;py=75+(point[1]-box[1])*2
            d.ellipse((px-6,py-6,px+6,py+6),outline=color,width=3)
            d.text((px-50,py-35),label,font=small,fill=color)
d.text((22,592),'施工输入，非完成画稿。两原掌与单镯不换位；四前杆原像素，低位错误尾另清。',font=font,fill='#263743')
d.text((22,632),'远R完整肩袖→上臂→肘→腕在右图显示；左/中图按躯干前后实际遮挡。',font=small,fill='#263743')
board.save(ROOT/'qa/shoulders_to_palms_three_view.png')

# Contacts are literal target crops. Show the measured front-axis extrapolation
# only in the separate QA companion, never redraw those axes in the target.
contact=Image.new('RGB',(1360,900),'#f1f2f3');cd=ImageDraw.Draw(contact)
contact_boxes=[('L原掌＋单镯＋两鹤签（原像素）',(885,275,1010,385)),
               ('R原掌＋两龟签；纠正端点藏掌内',(885,405,1010,485))]
for i,(title,cb) in enumerate(contact_boxes):
    x=20+i*675
    cd.text((x,20),title,font=small,fill='#263743')
    contact.paste(targetgray.crop(cb).resize((625,(cb[3]-cb[1])*5),Image.Resampling.NEAREST),(x,70))
cd.text((25,720),'两只掌中心、手指与玉镯不动。低位外露错尾清除，不硬补掌后的尾。',font=font,fill='#263743')
cd.text((25,770),'签轴按前段实际竹色像素拟合；坐标/遮挡端点见geometry_and_protection.json。',font=small,fill='#263743')
contact.save(ROOT/'qa/palm_rod_contacts.png')

overlay=np.array(rawgray).astype(float)
allowed=edit==255
overlay[allowed]=overlay[allowed]*0.45+np.array([238,92,70])*0.55
Image.fromarray(overlay.astype('uint8')).save(ROOT/'qa/edit_domain_overlay.png')

delta=np.any(target!=src,axis=2)
checks={
    'changed_pixels':int(delta.sum()),
    'changed_outside_white':int((delta & (edit==0)).sum()),
    'changed_child_pixels':int(delta[:,0:835].sum()),
    'changed_waist_legs_pixels':int(delta[485:,:].sum()),
    'changed_upper_head_pixels':int(delta[:247,:].sum()),
    'target_canvas':[1672,941],
    'new_model_calls':0,
    'target_is_static_construction_not_generated_drawing':True,
}
for filename in ['protect_L_palm_bracelet.png','protect_R_palm.png','protect_four_front_rods.png']:
    mask=np.array(Image.open(ROOT/'masks'/filename))>0
    checks['changed_'+filename]=int(delta[mask].sum())
    assert not delta[mask].any()
assert checks['changed_outside_white']==0
assert checks['changed_child_pixels']==0
assert checks['changed_waist_legs_pixels']==0
assert checks['changed_upper_head_pixels']==0
checks['target_sha256']=hashlib.sha256((ROOT/'S20_F000_arms_target.png').read_bytes()).hexdigest()
(ROOT/'target_pixel_verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(checks,ensure_ascii=False,indent=2))
