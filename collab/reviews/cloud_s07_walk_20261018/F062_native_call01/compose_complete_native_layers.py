#!/usr/bin/env python3
"""Native complete trousers beneath unchanged real source layers; no blank guards."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib
from scipy.ndimage import binary_dilation,binary_closing,binary_fill_holes,binary_erosion,label
R=Path(__file__).resolve().parent;V=R.parent/'next3_preflight_61sol/hip_calibrated_062_v4'
for n in ['production_layers','qa','masks']:(R/n).mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
size=(1672,1080);yy,xx=np.indices((1080,1672))
aligned=Image.open(R/'qa/call01_whole_crop_uniform_alignment.png').convert('RGBA');native=np.zeros((1080,1672,4),np.uint8);native[280:1060,650:1120]=np.array(aligned.crop((25,0,495,780)))
rgb=native[:,:,:3].astype(int)
seed=(native[:,:,3]>=128)&(rgb[:,:,2]-rgb[:,:,0]>5)&(rgb[:,:,2]-rgb[:,:,1]>3)&(rgb.max(axis=2)<130)&(yy>=530)&(yy<=980)
labels,_=label(seed);count=np.bincount(labels.ravel());count[0]=0
navy=binary_fill_holes(binary_closing(labels==int(count.argmax()),iterations=2))
pant_material=binary_dilation(navy,iterations=2)&(native[:,:,3]>0)&(yy>=530)&(yy<=980)
# Continue the SAME native navy volume upward beneath the source blouse AA.
# A technical horizontal cutoff must never remove existing real waist cloth.
# The blue vent is a different material and is excluded from this extension.
upper_band=(yy>=500)&(yy<532)&(xx>=770)&(xx<=1010)
upper_seed=(native[:,:,3]>=128)&upper_band&(rgb[:,:,2]-rgb[:,:,0]>5)&(rgb[:,:,2]-rgb[:,:,0]<32)&(rgb[:,:,2]-rgb[:,:,1]>3)&(rgb.max(axis=2)<130)
joined,_=label(navy|upper_seed);cts=np.bincount(joined.ravel());cts[0]=0
upper_connected=(joined==int(cts.argmax()))&upper_band
native_blue=((rgb[:,:,2]-rgb[:,:,0])>=35)&(rgb.max(axis=2)>75)
upper_extension=binary_dilation(upper_connected,iterations=2)&(native[:,:,3]>0)&(yy>=498)&(yy<530)&(xx>=768)&(xx<=1012)&~native_blue
pant_material|=upper_extension
Image.fromarray(upper_extension.astype('uint8')*255).save(R/'masks/upper_waist_same_native_navy_extension.png')
pants=native.copy();pants[~pant_material]=0
Image.fromarray(pants).save(R/'production_layers/native_complete_trousers_original_color.png')
# Correct only the returned navy material to locked057. Deep ink and alpha stay
# unchanged; retain every native crease and its contrast, without global recolor.
weight=np.clip((rgb.max(axis=2)-40)/14,0,1)*pant_material*((rgb[:,:,2]-rgb[:,:,0])>5)*((rgb[:,:,2]-rgb[:,:,1])>3)
paint=np.rint(pants[:,:,:3].astype(float)-weight[:,:,None]*np.array([6,5,5])).clip(0,255).astype('uint8')
color=pants.copy();color[:,:,:3]=paint
assert np.array_equal(color[:,:,3],pants[:,:,3])
assert np.array_equal(color[rgb.max(axis=2)<=40],pants[rgb.max(axis=2)<=40])
Image.fromarray(color).save(R/'production_layers/native_complete_trousers_color_locked.png')
source_layers={};fragment_counts={}
for name in ['far_shoe_ankle','far_complete_arm_jade_hand','body_head_blouse','near_complete_arm','near_shoe_ankle_FIXED']:
 path=V/'layers'/f'F062_{name}.png';a=np.array(Image.open(path).convert('RGBA'))
 if name!='body_head_blouse':
  labs,_=label(a[:,:,3]>=20);cts=np.bincount(labs.ravel());cts[0]=0
  actual=(a[:,:,3]>0)&binary_dilation(labs==int(cts.argmax()),iterations=3)
  fragment_counts[name]=int(((a[:,:,3]>0)&~actual).sum());a[~actual]=0
 source_layers[name]=Image.fromarray(a);source_layers[name].save(R/'production_layers'/f'source_F062_{name}.png')
# Complete source far foot remains below the new pants, then real body/arms and
# planted near foot are overlaid with their original RGBA. Material AA composes
# over its new true background; empty dilated guards never block real cloth.
order=['far_shoe_ankle','native_trousers','far_complete_arm_jade_hand','body_head_blouse','near_complete_arm','near_shoe_ankle_FIXED']
canvas=Image.new('RGBA',size)
for name in order:canvas.alpha_composite(Image.fromarray(color) if name=='native_trousers' else source_layers[name])
out=R/'candidate/F062_complete_native_layered_color_locked_PENDING.png';canvas.save(out);c=np.array(canvas)
source=np.array(Image.open(V/'reference/F062_hip_calibrated_source_pixels_NOT_ART.png').convert('RGBA'))
near=np.array(source_layers['near_shoe_ankle_FIXED']);far=np.array(source_layers['far_shoe_ankle'])
near_core=near[:,:,3]==255
assert np.array_equal(c[near_core],near[near_core])
body=np.array(source_layers['body_head_blouse']);arms=np.array(source_layers['near_complete_arm'])
body_core=(body[:,:,3]==255)&(arms[:,:,3]==0)&(near[:,:,3]==0)
assert np.array_equal(c[body_core],body[body_core])
feet_guard=np.array(Image.open(V/'masks/HARD_visible_complete_shoes_ankles.png'))>0
near_full=np.array(Image.open(V/'masks/SOURCE_near_shoe_ankle_FIXED.png'))>0
far_under_new_pants=(far[:,:,3]>0)&pant_material&~near_full
blank_guard_released=feet_guard&(source[:,:,3]==0)&pant_material
oldmask=np.array(Image.open(V/'masks/F062_full_pants_and_sleeves_WHITE_EDIT_PENDING.png'))>0
outer=pant_material&~oldmask
for name,m in [('native_complete_trousers_full_source_material',pant_material),('navy_material_color_weight',weight),('actual_far_foot_under_new_trousers',far_under_new_pants),('empty_old_foot_guard_released_to_native_cloth',blank_guard_released),('native_pants_complete_outer_AA_beyond_old_mask',outer)]:Image.fromarray(np.rint(m*255).astype('uint8')).save(R/'masks'/f'{name}.png')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
for nm,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 def bg(z):
  b=Image.new('RGBA',size,col);b.alpha_composite(z);return b.convert('RGB')
 full=bg(canvas);full.save(R/f'qa/F062_layered_final_full_{nm}.png')
 full.crop((650,280,1120,1060)).save(R/f'qa/F062_layered_final_crop_{nm}.png')
 boxes=[('腰口衣料原层／新裤底层',(760,515,1010,630)),('双袖根源材质',(720,330,1030,423)),('真实裤口／鞋踝与前后层次',(770,870,1020,1030)),('完整远膝原生弧',(930,700,1055,810))]
 sheet=Image.new('RGB',(1260,800),(235,241,246));d=ImageDraw.Draw(sheet)
 for i,(title,box) in enumerate(boxes):
  p=full.crop(box);p=p.resize((p.width*2,p.height*2),Image.Resampling.NEAREST);x=(i%2)*630;y=(i//2)*390+35;sheet.paste(p,(x,y));d.text((x+5,y-28),title,font=font,fill='#253740')
 sheet.save(R/f'qa/layered_final_four_connections_{nm}.png')
source057=np.array(Image.open(R.parent/'F057_semantic_color_ankle/candidate/F057_semantic_color_and_ankle_PENDING.png').convert('RGBA'))
srcpants=np.logical_or.reduce([np.array(Image.open(V/'sources/masks'/f'F057_source_{n}.png'))>0 for n in ['near_thigh','near_shin','far_thigh','far_shin']])
foreground=np.zeros((1080,1672),bool)
for n in ['body_head_blouse','near_complete_arm','far_complete_arm_jade_hand','near_shoe_ankle_FIXED']:foreground|=np.array(source_layers[n])[:,:,3]>=128
sel0=binary_erosion(srcpants&(source057[:,:,3]>=128),iterations=4);sel1=binary_erosion(pant_material&(color[:,:,3]>=128)&~foreground,iterations=4)
m0=source057[sel0,:3].mean(axis=0);m1=color[sel1,:3].mean(axis=0);delta=m1-m0
assert np.max(np.abs(delta))<=4
palette={'source057_mean_rgb':m0.tolist(),'native062_locked_visible_pants_mean_rgb':m1.tolist(),'mean_delta_rgb':delta.tolist(),'within4':True,'only_new_navy_material_correction_rgb':[-6,-5,-5],'deep_ink_max40_unchanged':True,'native_trousers_alpha_unchanged':True,'fore_material_excluded_from_comparison':True}
(R/'qa/final_trousers_palette_gate.json').write_text(json.dumps(palette,ensure_ascii=False,indent=2)+'\n')
report={'status':'ACTUAL_NATIVE_LAYER_RECOMPOSITION_COLOR_LOCKED_PENDING_FINAL_VISUAL_REVIEW','candidate_sha256':sha(out),'native_raw_sha256':'efa81720135228ccec5c7af65b05d75a8ec2db39b28c2dd1d6ba740ad89722b0','native_whole_crop_scale':0.5078125,'no_extra_translation_rotation_or_limb_warp':True,'native_cloth_only_source_extraction_no_code_paint':True,'native_cloth_pixels':int(pant_material.sum()),'complete_native_outer_AA_beyond_old_mask_pixels':int(outer.sum()),'same_source_nondrawn_fragments_excluded':fragment_counts,'blank_guard_pixels_released_for_actual_native_cloth':int(blank_guard_released.sum()),'far_source_foot_pixels_under_new_actual_trousers':int(far_under_new_pants.sum()),'near_actual_opaque_shoe_ankle_core_RGBA_changes':int(np.any(c[near_core]!=near[near_core],axis=1).sum()),'source_body_opaque_visible_core_RGBA_changes':int(np.any(c[body_core]!=body[body_core],axis=1).sum()),'source_layers_original_RGBA_preserved_where_material_kept':True,'legitimate_AA_compositing_note':'Preserve original source material RGBA as independent layers; final flat AA changes over native cloth are necessary occlusion/compositing, not blanket byte-lock or recolor. No alpha0 dilation guard.','layer_order_back_to_front':order,'navy_palette_gate':palette,'new_image_requests':1,'actual_raw_outputs':1,'new_image_calls_for_cleanup_or_color':0,'near_sole_bottom_native':int(np.where(near[:,:,3]>=128)[0].max()),'near_sole_bottom_world':1022*0.36410361842105265+402.7604324894813,'remaining_gate':'Final actual-image shape/contact review;068/073 unopened.'}
(R/'qa/layered_final_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
