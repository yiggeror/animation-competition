#!/usr/bin/env python3
"""Call02 whole native trousers; original support and swing shoes remain fixed."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import label,binary_fill_holes,binary_closing,binary_dilation,binary_erosion
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;B=R.parent
for d in ['candidate','production_layers','qa','masks']:(R/d).mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
size=(1672,1080);yy,xx=np.indices((1080,1672))
raw=R/'repair_call02/originals/F073_call02_raw.png';im=Image.open(raw).convert('RGBA');assert im.size==(1023,1537)
scale=780/im.height;padx=(520-im.width*scale)/2
aligned=im.transform((520,780),Image.Transform.AFFINE,(1/scale,0,-padx/scale,0,1/scale,0),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0));aligned.save(R/'repair_call02/qa/native_whole_crop_uniform_alignment.png')
n=np.zeros((1080,1672,4),np.uint8);n[280:1060,780:1300]=np.array(aligned);rgb=n[:,:,:3].astype(int)
seed=(n[:,:,3]>=128)&(rgb[:,:,2]-rgb[:,:,0]>5)&(rgb[:,:,2]-rgb[:,:,0]<35)&(rgb[:,:,2]-rgb[:,:,1]>3)&(rgb.max(axis=2)<130)&(yy>=500)&(yy<=1005)
labs,_=label(seed);cts=np.bincount(labs.ravel());cts[0]=0;components=np.flatnonzero(cts>1000);assert 1<=len(components)<=4
core=binary_fill_holes(binary_closing(np.isin(labs,components),iterations=2))
mat=binary_dilation(core,iterations=2)&(n[:,:,3]>0)&(yy>=498)&(yy<=1007)
native_blue=(rgb[:,:,2]-rgb[:,:,0]>=35)&(rgb.max(axis=2)>75);mat&=~native_blue
before_semantic_trim=mat.copy()
# The second dilation ring at the original near heel samples the RETURNED
# shoe, not trousers. Preserve the first true cloth contour, discard that
# extra generated shoe edge; original shoe layers remain untouched.
first_contour=binary_dilation(core,iterations=1)&(n[:,:,3]>0)
heel_generated_shoe_edge=mat&~first_contour&(xx>=1008)&(xx<=1020)&(yy>=910)&(yy<=955)
native_foot_skin=(rgb[:,:,0]>140)&(rgb[:,:,0]-rgb[:,:,1]>15)&(rgb[:,:,1]-rgb[:,:,2]>8)
native_sole_white=rgb.min(axis=2)>150
noncloth_foot_material=mat&(yy>=850)&(native_foot_skin|native_sole_white)
trim=heel_generated_shoe_edge|noncloth_foot_material;mat&=~trim
Image.fromarray(trim.astype('uint8')*255).save(R/'masks/call02_generated_shoe_material_excluded_from_pants.png')
(R/'qa/call02_shoe_material_exclusion_checks.json').write_text(json.dumps({'status':'RETURNED_SHOE_MATERIAL_EXCLUDED_NOT_SOURCE_FOOT_EDIT','excluded_pixels':int(trim.sum()),'heel_second_dilation_ring_pixels':int(heel_generated_shoe_edge.sum()),'returned_foot_skin_or_white_pixels':int(noncloth_foot_material.sum()),'first_true_navy_contour_retained':True,'source_near_and_far_layers_edited':False,'new_image_calls':0,'removed_native_pixels':[{'xy':[int(x),int(y)],'native_RGBA':n[y,x].tolist()}for y,x in zip(*np.where(trim))]},ensure_ascii=False,indent=2)+'\n')
pants=n.copy();pants[~mat]=0;Image.fromarray(pants).save(R/'production_layers/native_complete_trousers_original_color.png');Image.fromarray(mat.astype('uint8')*255).save(R/'masks/actual_native_call02_complete_trousers_material.png')
names=['far_shoe_ankle_SUPPORT_FIXED','far_complete_arm_jade_hand','body_head_blouse','near_complete_arm','near_shoe_ankle_SWING']
sources={k:Image.open(R/'layers'/f'F073_{k}.png').convert('RGBA')for k in names}
fore=np.logical_or.reduce([np.array(sources[k])[:,:,3]>=128 for k in names if k!='far_shoe_ankle_SUPPORT_FIXED'])
mother=np.array(Image.open(B/'F062_native_call01/candidate/F062_single_native_final_with_waist_underlay_PENDING_ASTRA.png').convert('RGBA'))
mm=np.array(Image.open(B/'F062_native_call01/masks/native_complete_trousers_full_source_material.png'))>0;mrgb=mother[:,:,:3].astype(int)
m0=binary_erosion(mm&(mother[:,:,3]>=128)&(mrgb[:,:,2]-mrgb[:,:,0]>5)&(mrgb[:,:,2]-mrgb[:,:,0]<35)&(mrgb.max(axis=2)<130),iterations=4)
sel=binary_erosion(mat&(n[:,:,3]>=128)&~fore,iterations=4);mean0=mrgb[m0].mean(axis=0);mean1=rgb[sel].mean(axis=0);delta=np.rint(mean0-mean1).astype(int)
weight=np.clip((rgb.max(axis=2)-35)/14,0,1)*mat*((rgb[:,:,2]-rgb[:,:,0])>5)*((rgb[:,:,2]-rgb[:,:,1])>3)
color=pants.copy();color[:,:,:3]=np.rint(pants[:,:,:3].astype(float)+weight[:,:,None]*delta).clip(0,255).astype('uint8')
assert np.array_equal(color[:,:,3],pants[:,:,3]);assert np.array_equal(color[rgb.max(axis=2)<=35],pants[rgb.max(axis=2)<=35])
Image.fromarray(color).save(R/'production_layers/native_complete_trousers_color_locked.png')
order=['far_shoe_ankle_SUPPORT_FIXED','native_trousers','far_complete_arm_jade_hand','body_head_blouse','near_complete_arm','near_shoe_ankle_SWING'];canvas=Image.new('RGBA',size)
for k in order:canvas.alpha_composite(Image.fromarray(color)if k=='native_trousers'else sources[k])
out=R/'candidate/F073_repaired_complete_native_layered_PENDING_ACTUAL_REVIEW.png';canvas.save(out);a=np.array(canvas)
for k,z in sources.items():z.save(R/'production_layers'/f'source_F073_{k}.png')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
for name,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 z=Image.new('RGBA',size,col);z.alpha_composite(canvas);z.convert('RGB').save(R/f'qa/F073_repair02_native_layered_full_{name}.png');z.crop((780,280,1300,1060)).convert('RGB').save(R/f'qa/F073_repair02_native_layered_crop_{name}.png')
 sheet=Image.new('RGB',(1440,650),(235,241,246));d=ImageDraw.Draw(sheet)
 for j,(title,box)in enumerate([('源腰衣／新原生裤底层',(965,505,1200,640)),('远左锁地／近右抬步／原鞋裤口',(965,815,1220,1040)),('双袖根／整臂原材料',(940,325,1220,418))]):
  q=z.crop(box);q=q.resize((q.width*2,q.height*2),Image.Resampling.NEAREST);x=(j%2)*720;y=(j//2)*325+30;sheet.paste(q.convert('RGB'),(x,y));d.text((x+5,y-25),title,font=font,fill='#263440')
 sheet.save(R/f'qa/F073_repair02_native_connections_{name}.png')
newmean=color[sel,:3].mean(axis=0);far=np.array(sources['far_shoe_ankle_SUPPORT_FIXED']);near=np.array(sources['near_shoe_ankle_SWING']);nearcore=near[:,:,3]==255
srcfar=R/'sources/F068_far_shoe_ankle_LANDED.png';assert sha(srcfar)==sha(R/'production_layers/source_F073_far_shoe_ankle_SUPPORT_FIXED.png')
report={'status':'ACTUAL_ONE_NATIVE_PANTS_LAYER_PENDING_VISUAL_REVIEW','candidate_sha256':sha(out),'raw_sha256':sha(raw),'raw_size':im.size,'whole_crop_uniform_scale':scale,'canonical_fractional_horizontal_padding_each_side':padx,'no_nonuniform_or_limb_scale':True,'crop_xyxy':[780,280,1300,1060],'native_pants_material_pixels':int(mat.sum()),'actual_navy_component_sizes':[int(cts[i])for i in components],'palette_anchor_fixed062_SHA':'393622a77349083751122520b690bd35017f8535a25560d8cca775446d2eeb2f','mother062_navy_mean':mean0.tolist(),'native073_navy_original_mean':mean1.tolist(),'semantic_navy_integer_correction_rgb':delta.tolist(),'color_locked_navy_mean':newmean.tolist(),'color_mean_delta_vs062':(newmean-mean0).tolist(),'alpha_unchanged':True,'deep_ink_max35_unchanged':True,'layer_order_back_to_front':order,'far_support_complete_layer_RGBA_changes_vs_actual068':0,'far_support_layer_SHA':sha(srcfar),'near_source_opaque_core_RGBA_changes':int(np.any(a[nearcore]!=near[nearcore],axis=1).sum()),'real_sole_bottoms_native':{'far_support':int(np.where(far[:,:,3]>=128)[0].max()),'near_swing':int(np.where(near[:,:,3]>=128)[0].max())},'F073_requests':2,'F073_originals':2,'new_calls_for_adoption':0,'F079_unopened':True,'limits':'Only actual source/native art. Actual complete shape, support, waist/cuffs and sleeves need visual review before source/exposure acceptance.'}
report['palette_anchor_fixed062_SHA']=sha(B/'F062_native_call01/candidate/F062_single_native_final_with_waist_underlay_PENDING_ASTRA.png')
(R/'qa/repair02_native_layered_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
