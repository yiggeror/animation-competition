#!/usr/bin/env python3
"""Actual single native trousers + frozen whole source layers, review trial only."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import label,binary_fill_holes,binary_closing,binary_dilation,binary_erosion
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;B=R.parent
for d in ['candidate','production_layers','qa','masks']:(R/d).mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
size=(1672,1080);yy,xx=np.indices((1080,1672))
raw=R/'originals/F079_call01_RAW.png';im=Image.open(raw).convert('RGBA');assert im.size==(1024,1536)
scale=520/1024;assert scale==780/1536
aligned=im.resize((520,780),Image.Resampling.LANCZOS)
aligned.save(R/'qa/call01_whole_crop_uniform_520x780.png')
n=np.zeros((1080,1672,4),np.uint8);n[280:1060,900:1420]=np.array(aligned);rgb=n[:,:,:3].astype(int)
seed=(n[:,:,3]>=128)&(rgb[:,:,2]-rgb[:,:,0]>5)&(rgb[:,:,2]-rgb[:,:,0]<35)&(rgb[:,:,2]-rgb[:,:,1]>3)&(rgb.max(axis=2)<130)&(yy>=500)&(yy<=1005)
labs,_=label(seed);cts=np.bincount(labs.ravel());cts[0]=0;components=np.flatnonzero(cts>1000);assert 1<=len(components)<=4
core=binary_fill_holes(binary_closing(np.isin(labs,components),iterations=2))
mat=binary_dilation(core,iterations=2)&(n[:,:,3]>0)&(yy>=498)&(yy<=1007)
native_blue=(rgb[:,:,2]-rgb[:,:,0]>=35)&(rgb.max(axis=2)>75)
native_foot_skin=(rgb[:,:,0]>140)&(rgb[:,:,0]-rgb[:,:,1]>15)&(rgb[:,:,1]-rgb[:,:,2]>8)
native_sole_white=rgb.min(axis=2)>150
trim=mat&((native_blue)|((yy>=850)&(native_foot_skin|native_sole_white)))
mat&=~trim
pants=n.copy();pants[~mat]=0
Image.fromarray(pants).save(R/'production_layers/native_complete_trousers_original_color_TRIAL.png')
Image.fromarray(mat.astype('uint8')*255).save(R/'masks/call01_actual_native_complete_trousers_material_TRIAL.png')
Image.fromarray(trim.astype('uint8')*255).save(R/'masks/call01_nontrouser_returned_material_excluded_TRIAL.png')
names=['far_shoe_ankle_SUPPORT_FIXED','far_complete_arm_jade_hand','body_head_blouse','near_complete_arm','near_shoe_ankle_LANDED']
sources={k:Image.open(R/'layers'/f'F079_{k}.png').convert('RGBA')for k in names}
fore=np.logical_or.reduce([np.array(sources[k])[:,:,3]>=128 for k in names if k!='far_shoe_ankle_SUPPORT_FIXED'])
anchor=np.array(Image.open(R/'sources/F062_palette_anchor.png').convert('RGBA'));ar=anchor[:,:,:3].astype(int)
am=np.array(Image.open(B/'F062_native_call01/masks/native_complete_trousers_full_source_material.png').convert('L'))>0
refsel=binary_erosion(am&(anchor[:,:,3]>=128)&(ar[:,:,2]-ar[:,:,0]>5)&(ar[:,:,2]-ar[:,:,0]<35)&(ar.max(axis=2)<130),iterations=4)
sel=binary_erosion(mat&(n[:,:,3]>=128)&~fore,iterations=4)
mean0=ar[refsel].mean(axis=0);mean1=rgb[sel].mean(axis=0)
# Retain the one original output; no color correction or geometry repair in this trial.
order=['far_shoe_ankle_SUPPORT_FIXED','native_trousers','far_complete_arm_jade_hand','body_head_blouse','near_complete_arm','near_shoe_ankle_LANDED']
canvas=Image.new('RGBA',size)
for k in order:canvas.alpha_composite(Image.fromarray(pants)if k=='native_trousers'else sources[k])
out=R/'candidate/F079_one_native_source_layered_TRIAL_PENDING_ASTRA.png';canvas.save(out)
for k,z in sources.items():z.save(R/'production_layers'/f'source_F079_{k}.png')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17)
for name,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 z=Image.new('RGBA',size,col);z.alpha_composite(canvas);z.convert('RGB').save(R/f'qa/F079_one_native_layered_full_{name}_TRIAL.png');z.crop((900,280,1420,1060)).convert('RGB').save(R/f'qa/F079_one_native_layered_crop_{name}_TRIAL.png')
 sheet=Image.new('RGB',(1240,760),(235,241,246));d=ImageDraw.Draw(sheet)
 for j,(title,box)in enumerate([('079真实腰衣／原生完整裤底层',(1095,500,1320,645)),('远左原鞋／裤口接合',(955,855,1175,1040)),('近右原鞋／裤口接合',(1175,835,1415,1040)),('近腿膝与承重轮廓',(1170,600,1390,850))]):
  q=z.crop(box).resize(((box[2]-box[0])*2,(box[3]-box[1])*2),Image.Resampling.NEAREST);x=(j%2)*620;y=(j//2)*380+30;sheet.paste(q.convert('RGB'),(x,y));d.text((x+4,y-25),title,font=font,fill='#263440')
 sheet.save(R/f'qa/F079_one_native_actual_connections_{name}_TRIAL.png')
 mother=Image.open(R/'sources/F073_final.png').convert('RGBA');b=Image.new('RGBA',size,col);b.alpha_composite(mother)
 panel=Image.new('RGB',(1050,815),(235,241,246));d=ImageDraw.Draw(panel);panel.paste(b.crop((760,280,1280,1060)).convert('RGB'),(0,30));panel.paste(z.crop((900,280,1420,1060)).convert('RGB'),(530,30));d.text((4,6),'锁073真实成态／不同平移裁窗',font=font,fill='#263440');d.text((534,6),'079唯一原生裤＋真实固定鞋／TRIAL',font=font,fill='#263440');panel.save(R/f'qa/F073_F079_one_native_actual_comparison_{name}.png')
report={'status':'ONE_NATIVE_LAYERED_TRIAL_PENDING_ACTUAL_REVIEW_NOT_ACCEPTED','candidate_sha256':sha(out),'raw_sha256':sha(raw),'raw_size':list(im.size),'whole_crop_uniform_scale':scale,'whole_crop_xyxy':[900,280,1420,1060],'no_nonuniform_limb_scale_or_code_pose':True,'native_pants_material_pixels':int(mat.sum()),'returned_noncloth_pixels_excluded':int(trim.sum()),'actual_navy_component_sizes':[int(cts[i])for i in components],'palette_anchor_fixed062_SHA':sha(R/'sources/F062_palette_anchor.png'),'anchor062_navy_mean':mean0.tolist(),'native079_navy_mean':mean1.tolist(),'native079_mean_delta_vs062':(mean1-mean0).tolist(),'navy_RGB_correction_applied':[0,0,0],'layer_order_back_to_front':order,'source_layer_SHA_match_frozen_inputs':{k:sha(R/'layers'/f'F079_{k}.png')==sha(R/'production_layers'/f'source_F079_{k}.png')for k in names},'fixed_far_layer_SHA':sha(R/'production_layers/source_F079_far_shoe_ankle_SUPPORT_FIXED.png'),'real_sole_bottoms_native':{k:int(np.where(np.array(sources[k])[:,:,3]>=128)[0].max())for k in ['far_shoe_ankle_SUPPORT_FIXED','near_shoe_ankle_LANDED']},'F079_requests':1,'F079_originals':1,'new_calls_for_adoption':0,'other_states_unopened':True,'limits':'Single actual original only. Waist/hip support, actual near-leg extension and both true source ankle/cuffs must be visually reviewed; not accepted, no exposure.'}
(R/'qa/one_native_layered_trial_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
