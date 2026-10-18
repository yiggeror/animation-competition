#!/usr/bin/env python3
"""Astra-authorized whole upper far puff sleeve, original call01 pixels only."""
from pathlib import Path
import hashlib,json,subprocess,tempfile,os,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_closing,binary_fill_holes,binary_dilation
R=Path(__file__).resolve().parent;P=R.parent;B=P.parent
for n in ['candidate','masks','qa','exposure']:(R/n).mkdir(exist_ok=True)
source=P/'independent_recompose/F037_independent_original_pixels_PENDING.png'
raw=P/'originals/F037_call01_raw.png'
mother=B/'pre_tap_segment/clothing_semantic_review/continuous_contour_delivery/candidate/F031_raw_clothing_and_contours_for_final_lock.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)=='526ca883e0867d5a1036b5afa99de35767c5216731b8674ac732d7a0f7c48735'
assert sha(raw)=='d913073cf1fb4feaa9b0fcc89c68c4112b1acefe2279b4fd6ddc1022b8a61a9b'
im=Image.open(source).convert('RGBA');a=np.array(im);native=Image.open(raw).convert('RGBA')
donor=Image.new('RGBA',im.size);donor.paste(native,(0,0));d=np.array(donor)
yy,xx=np.indices(a.shape[:2]);rgb=d[:,:,:3].astype(int)
arm=np.array(Image.open(P/'independent_recompose/arm_raw_dy30_mask.png'))>0
roi=(xx>=940)&(xx<=1035)&(yy>=550)&(yy<648)
yellow=(rgb[:,:,0]-rgb[:,:,2]>110)&(rgb[:,:,1]-rgb[:,:,2]>70)&(d[:,:,3]>32)
cloth=binary_dilation(binary_fill_holes(binary_closing(yellow&roi,iterations=2)),iterations=2)
# Adopt full native cloth/ink/white marks and the transparency outside its
# rounded contour. Native skin is excluded, since its arm was30px higher.
take=roi&~arm&(cloth|(d[:,:,3]<32))
out=a.copy();out[take]=d[take]
candidate=R/'candidate/F037_whole_native_far_puff_PENDING.png';Image.fromarray(out).save(candidate)
Image.fromarray(take.astype(np.uint8)*255).save(R/'masks/whole_upper_far_puff_adoption.png')
changed=np.any(out!=a,axis=2)
assert not changed[~take].any();assert not changed[arm].any();assert not changed[yy>=648].any()
assert np.array_equal(out[take],d[take])
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
for name,bgc in [('gray',(105,112,121,255)),('dark',(32,40,48,255))]:
    sheet=Image.new('RGB',(1500,760),(242,244,247));dr=ImageDraw.Draw(sheet)
    for col,(title,z) in enumerate([('原位call01完整圆袖源',d),('修前：旧尖＋新圆冲突',a),('新整袖原像素接回',out)]):
        bg=Image.new('RGBA',im.size,bgc);bg.alpha_composite(Image.fromarray(z))
        sheet.paste(bg.crop((920,540,1050,715)).resize((494,665),Image.Resampling.NEAREST).convert('RGB'),(col*500+3,50));dr.text((col*500+5,12),title,font=font,fill='#223344')
    sheet.save(R/f'qa/source_before_after_{name}.png')
    bg=Image.new('RGBA',im.size,bgc);bg.alpha_composite(Image.fromarray(out));bg.convert('RGB').save(R/f'qa/F037_full_{name}.png')
lock=json.loads((B/'switch_segment/locked/F000_lock.json').read_text())
frames={31:Image.open(mother).convert('RGBA'),37:Image.fromarray(out)}
for frame,z in frames.items():
    reg=z.transform((1536,864),Image.Transform.AFFINE,tuple(lock['registration']['inverse_pillow_affine']),resample=Image.Resampling.BICUBIC)
    if frame==37:reg.save(R/'candidate/F037_registered_PENDING.png')
    preview=reg.crop((280,80,1304,656)).resize((1280,720),Image.Resampling.LANCZOS)
    for name,bgc in [('gray',(105,112,121,255)),('dark',(32,40,48,255))]:
        bg=Image.new('RGBA',preview.size,bgc);bg.alpha_composite(preview);bg.convert('RGB').save(R/f'exposure/F{frame:03d}_{name}.png')
with tempfile.TemporaryDirectory(prefix='s09-031-037-',dir='/tmp') as td:
    td=Path(td)
    for i,frame in enumerate([31]*6+[37]*5):shutil.copyfile(R/f'exposure/F{frame:03d}_gray.png',td/f'{i:03d}.png')
    video=R/'exposure/S09_F031x6_F037x5_actual_layer_24fps.mp4'
    subprocess.run(['ffmpeg','-y','-v','error','-framerate','24','-i',str(td/'%03d.png'),'-frames:v','11','-c:v','libx264','-crf','16','-pix_fmt','yuv420p',str(video)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(video)]))['streams'][0]
assert probe['nb_read_frames']=='11' and probe['r_frame_rate']=='24/1'
checks={'status':'WHOLE_UPPER_FAR_PUFF_SOURCE_COPY_PENDING_ASTRA_STATIC_AND_EXPOSURE_REVIEW',
 'authority':'Astra latest explicitly releases whole upper far puff sleeve and old tip/occlusion ink; preserve lower flounce→far arm/palm, whole near arm/grip/prop/head/skirt. Do not generate or dispatch042.',
 'source_before_sha256':sha(source),'call01_source_sha256':sha(raw),'candidate_sha256':sha(candidate),
 'new_native_calls':0,'S09_requests_unchanged':15,'S09_originals_unchanged':14,'F042_requests':0,
 'donor_transform':{'scale':1,'translation':[0,0],'rotation':0,'warp':False,'RGBA_blending':False},
 'adoption_mask_pixels':int(take.sum()),'RGBA_changed_pixels':int(changed.sum()),
 'source_RGBA_mismatches':int(np.any(out[take]!=d[take],axis=1).sum()),'outside_adoption_RGBA_changes':int(changed[~take].sum()),
 'complete_new_near_arm_changes':int(changed[arm].sum()),'lower_cuff_far_arm_palm_and_skirt_y648_down_changes':int(changed[yy>=648].sum()),
 'whole_grip_prop_head_neck_changes':0,'historical_far_upper_puff_guard_released':True,
 'actual_exposure':{'frames':[31]*6+[37]*5,'fps':24,'probe':probe,'no_tween':True,'scope':'isolated actual PNG exposure layer, no whole-shot/full-film render, background or audio'},
 'remaining_gate':'Astra static037 and actual031→037 exposure review;042 unopened.'}
(R/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(checks,ensure_ascii=False))
