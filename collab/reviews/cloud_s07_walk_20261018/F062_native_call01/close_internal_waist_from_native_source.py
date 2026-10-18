#!/usr/bin/env python3
"""Tiny hidden cloth underlay from traceable adjacent native pixels, no new RGB."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import label,binary_dilation
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
basepath=R/'candidate/F062_complete_native_layered_color_locked_PENDING.png'
assert sha(basepath)=='6d8f9bad242c9680c10460fbda412edbd9db6a08575fe74b4fcb4d057aba3ca3'
base=np.array(Image.open(basepath).convert('RGBA'))
layerpath=R/'production_layers/native_complete_trousers_color_locked.png';cloth=np.array(Image.open(layerpath).convert('RGBA'))
body=np.array(Image.open(R/'production_layers/source_F062_body_head_blouse.png').convert('RGBA'))
lab,_=label(base[:,:,3]==0);hole=lab==lab[527,835];ys,xs=np.where(hole)
assert len(xs)==18 and [int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]==[832,527,838,529]
assert not hole[0].any() and not hole[-1].any() and not hole[:,0].any() and not hole[:,-1].any()
aa=binary_dilation(hole,iterations=1)&(body[:,:,3]>0)&(body[:,:,3]<255)&(cloth[:,:,3]==0)
take=hole|aa;ys,xs=np.where(take);assert len(xs)<=48
patched=cloth.copy();mappings=[]
for x,y in zip(xs,ys):
 dx,dy=int(x),int(y+4);rgba=cloth[dy,dx]
 r,g,b=map(int,rgba[:3]);assert rgba[3]>=250 and 5<b-r<32 and b-g>3 and max(r,g,b)<130,(x,y,rgba.tolist())
 patched[y,x]=rgba
 mappings.append({'target_xy':[int(x),int(y)],'native_cloth_donor_xy':[dx,dy],'donor_RGBA':rgba.tolist(),'source_translation_xy':[0,-4]})
np.testing.assert_array_equal(patched[~take],cloth[~take])
Image.fromarray(patched).save(R/'production_layers/native_complete_trousers_with_internal_waist_underlay.png')
Image.fromarray(take.astype('uint8')*255).save(R/'masks/internal_waist_native_source_underlay.png')
canvas=Image.new('RGBA',(1672,1080))
order=['far_shoe_ankle','native_trousers','far_complete_arm_jade_hand','body_head_blouse','near_complete_arm','near_shoe_ankle_FIXED']
for n in order:canvas.alpha_composite(Image.fromarray(patched) if n=='native_trousers' else Image.open(R/'production_layers'/f'source_F062_{n}.png').convert('RGBA'))
out=R/'candidate/F062_single_native_final_with_waist_underlay_PENDING_ASTRA.png';canvas.save(out);c=np.array(canvas)
changed=np.any(c!=base,axis=2);assert not (changed&~take).any();assert (c[hole,3]>250).all()
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
for name,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 bg=Image.new('RGBA',canvas.size,col);bg.alpha_composite(canvas);bg.convert('RGB').save(R/f'qa/F062_chosen_final_full_{name}.png')
 sheet=Image.new('RGB',(1000,430),(235,241,246));d=ImageDraw.Draw(sheet)
 for i,(title,z) in enumerate([('孔与衣AA下缺真实裤底层',Image.fromarray(base)),('同原件下方navy25px级底层',canvas)]):
  b=Image.new('RGBA',z.size,col);b.alpha_composite(z);p=b.crop((810,515,864,540)).resize((432,200),Image.Resampling.NEAREST);sheet.paste(p.convert('RGB'),(i*500+20,55));d.text((i*500+20,14),title,font=font,fill='#253740')
 sheet.save(R/f'qa/waist_internal_source_underlay_before_after_{name}.png')
report={'status':'INTERNAL_WAIST_CLOSED_WITH_TRACEABLE_SAME_NATIVE_CLOTH_UNDERLAY_PENDING_ACTUAL_REVIEW','candidate_sha256':sha(out),'base6d8_sha256':sha(basepath),'native_raw_sha256':'efa81720135228ccec5c7af65b05d75a8ec2db39b28c2dd1d6ba740ad89722b0','navy_donor_layer_path':str(layerpath),'navy_donor_layer_sha256':sha(layerpath),'internal_alpha0_hole_pixels':int(hole.sum()),'source_body_AA_underlay_pixels':int(aa.sum()),'real_native_pixel_copies':len(mappings),'final_composite_changed_pixels':int(changed.sum()),'outside_tiny_internal_underlay_changes':int((changed&~take).sum()),'original_body_layer_edited':False,'character_outer_contour_or_pose_changed':False,'new_RGB_synthesized':False,'not_same_coordinate_native_navy_claim':True,'honest_method':'Native blue at the target is not relabelled as navy. Every new underlay pixel is an unchanged RGBA copy from adjacent real continuous native trousers four native rows below, placed only into an enclosed18px gap and original blouse AA below-layer. This is a local source-material continuation, not a newly generated image or drawn body.','source_to_target_mappings':mappings,'new_image_calls':0,'F062_native_calls':1,'F062_native_outputs':1}
(R/'qa/internal_waist_native_source_underlay_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='source_to_target_mappings'},ensure_ascii=False,indent=2))
