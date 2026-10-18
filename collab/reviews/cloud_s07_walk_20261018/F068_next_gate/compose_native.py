#!/usr/bin/env python3
"""Complete real native trousers behind genuine source body, arms and feet."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import label,binary_fill_holes,binary_closing,binary_dilation,binary_erosion
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;B=R.parent
for d in ['candidate','production_layers','qa','masks']:(R/d).mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
size=(1672,1080);yy,xx=np.indices((1080,1672))
raw=R/'originals/F068_call01_raw.png';im=Image.open(raw).convert('RGBA');assert im.size==(1024,1536)
aligned=im.resize((520,780),Image.Resampling.LANCZOS);aligned.save(R/'qa/call01_whole_crop_uniform_alignment.png')
n=np.zeros((1080,1672,4),np.uint8);n[280:1060,700:1220]=np.array(aligned);rgb=n[:,:,:3].astype(int)
navy=(n[:,:,3]>=128)&(rgb[:,:,2]-rgb[:,:,0]>5)&(rgb[:,:,2]-rgb[:,:,0]<35)&(rgb[:,:,2]-rgb[:,:,1]>3)&(rgb.max(axis=2)<130)&(yy>=500)&(yy<=1005)
labs,_=label(navy);cts=np.bincount(labs.ravel());cts[0]=0
leg_components=np.flatnonzero(cts>1000)
assert len(leg_components)==2,'Actual native front/back trousers are separated by their dark crease.'
core=binary_fill_holes(binary_closing(np.isin(labs,leg_components),iterations=2))
mat=binary_dilation(core,iterations=2)&(n[:,:,3]>0)&(yy>=498)&(yy<=1007)
native_blue=(rgb[:,:,2]-rgb[:,:,0]>=35)&(rgb.max(axis=2)>75)
mat&=~native_blue
pants=n.copy();pants[~mat]=0;Image.fromarray(pants).save(R/'production_layers/native_complete_trousers_original_color.png');Image.fromarray(mat.astype('uint8')*255).save(R/'masks/actual_native_complete_trousers_material.png')
names=['far_shoe_ankle_LANDED','far_complete_arm_jade_hand','body_head_blouse','near_complete_arm','near_shoe_ankle_FIXED']
sources={k:Image.open(R/'layers'/f'F068_{k}.png').convert('RGBA')for k in names}
# The frozen input foot layer contains an old trouser extraction branch above
# its genuine ankle. Keep the actual skin and contour from y936 onward.
far_before=np.array(sources['far_shoe_ankle_LANDED'])
old_branch=(yy>=924)&(yy<=935)&(xx>=992)&(xx<=1010)&(far_before[:,:,3]>0)
far_after=far_before.copy();far_after[old_branch]=0
sources['far_shoe_ankle_LANDED']=Image.fromarray(far_after)
Image.fromarray(old_branch.astype('uint8')*255).save(R/'masks/old_far_foot_trouser_branch_removed.png')
branch_checks={'pixels':int(old_branch.sum()),'bbox_limit_xyxy':[992,924,1011,936],'genuine_skin_and_ankle_contour_y936_and_below_unchanged':bool(np.array_equal(far_before[936:],far_after[936:])),'frozen_input_foot_layer_unchanged':True,'new_image_calls':0,'source_pixel_removals':[{'xy':[int(x),int(y)],'source_RGBA':far_before[y,x].tolist()}for y,x in zip(*np.where(old_branch))]}
(R/'qa/old_far_foot_trouser_branch_cleanup.json').write_text(json.dumps(branch_checks,ensure_ascii=False,indent=2)+'\n')
fore=np.logical_or.reduce([np.array(sources[k])[:,:,3]>=128 for k in names if k!='far_shoe_ankle_LANDED'])
mother=np.array(Image.open(B/'F062_native_call01/candidate/F062_single_native_final_with_waist_underlay_PENDING_ASTRA.png').convert('RGBA'))
mothermat=np.array(Image.open(B/'F062_native_call01/masks/native_complete_trousers_full_source_material.png'))>0
oldrgb=mother[:,:,:3].astype(int);m0=binary_erosion(mothermat&(mother[:,:,3]>=128)&(oldrgb[:,:,2]-oldrgb[:,:,0]>5)&(oldrgb[:,:,2]-oldrgb[:,:,0]<35)&(oldrgb.max(axis=2)<130),iterations=4)
sel=binary_erosion(mat&(n[:,:,3]>=128)&~fore,iterations=4)
mean0=oldrgb[m0].mean(axis=0);mean1=rgb[sel].mean(axis=0)
# Fixed integer correction derived once from source062 and native068 complete
# visible navy means; deep black ink and alpha remain the genuine original.
delta=np.rint(mean0-mean1).astype(int)
weight=np.clip((rgb.max(axis=2)-35)/14,0,1)*mat*((rgb[:,:,2]-rgb[:,:,0])>5)*((rgb[:,:,2]-rgb[:,:,1])>3)
color=pants.copy();color[:,:,:3]=np.rint(pants[:,:,:3].astype(float)+weight[:,:,None]*delta).clip(0,255).astype('uint8')
assert np.array_equal(color[:,:,3],pants[:,:,3]);assert np.array_equal(color[rgb.max(axis=2)<=35],pants[rgb.max(axis=2)<=35])
Image.fromarray(color).save(R/'production_layers/native_complete_trousers_color_locked.png')
canvas=Image.new('RGBA',size);order=['far_shoe_ankle_LANDED','native_trousers','far_complete_arm_jade_hand','body_head_blouse','near_complete_arm','near_shoe_ankle_FIXED']
for k in order:canvas.alpha_composite(Image.fromarray(color)if k=='native_trousers'else sources[k])
out=R/'candidate/F068_complete_native_layered_PENDING_ACTUAL_REVIEW.png';canvas.save(out);a=np.array(canvas)
for k,z in sources.items():z.save(R/'production_layers'/f'source_F068_{k}.png')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
for name,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 z=Image.new('RGBA',size,col);z.alpha_composite(canvas);z.convert('RGB').save(R/f'qa/F068_native_layered_full_{name}.png');z.crop((700,280,1220,1060)).convert('RGB').save(R/f'qa/F068_native_layered_crop_{name}.png')
 sheet=Image.new('RGB',(1440,650),(235,241,246));d=ImageDraw.Draw(sheet)
 for j,(title,box)in enumerate([('源衣腰／真实新裤底层',(875,510,1120,650)),('后近右真鞋原位／前远左真鞋落定',(780,860,1160,1040)),('完整袖根源材质',(865,345,1130,425))]):
  q=z.crop(box);q=q.resize((q.width*2,q.height*2),Image.Resampling.NEAREST);x=(j%2)*720;y=(j//2)*325+30;sheet.paste(q.convert('RGB'),(x,y));d.text((x+5,y-25),title,font=font,fill='#263440')
 sheet.save(R/f'qa/F068_native_connections_{name}.png')
newmean=color[sel,:3].mean(axis=0);near=np.array(sources['near_shoe_ankle_FIXED']);far=np.array(sources['far_shoe_ankle_LANDED']);nearcore=near[:,:,3]==255
report={'status':'ACTUAL_ONE_NATIVE_PANTS_LAYER_PENDING_VISUAL_REVIEW','candidate_sha256':sha(out),'raw_sha256':sha(raw),'raw_size':im.size,'whole_crop_uniform_scale':520/1024,'crop_xyxy':[700,280,1220,1060],'native_pants_material_pixels':int(mat.sum()),'mother062_navy_mean':mean0.tolist(),'native068_navy_original_mean':mean1.tolist(),'semantic_navy_integer_correction_rgb':delta.tolist(),'color_locked_navy_mean':newmean.tolist(),'color_mean_delta_vs062':(newmean-mean0).tolist(),'alpha_unchanged':True,'deep_ink_max35_unchanged':True,'layer_order_back_to_front':order,'source_near_opaque_core_RGBA_changes':int(np.any(a[nearcore]!=near[nearcore],axis=1).sum()),'near_whole_source_shoe_SHA':sha(R/'production_layers/source_F068_near_shoe_ankle_FIXED.png'),'two_real_sole_bottoms_native':{'near':int(np.where(near[:,:,3]>=128)[0].max()),'far':int(np.where(far[:,:,3]>=128)[0].max())},'F068_requests':1,'F068_originals':1,'new_calls_for_adoption':0,'F073_unopened':True,'limits':'Source-derived actual art only. Native complete trousers must pass actual volume, hiddenhip, ankle/cuff, sleeve root and shape review before073.'}
(R/'qa/native_layered_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
