#!/usr/bin/env python3
"""Actual held PNG037x5→042x2, isolated layer only; decode all7 frames for source order."""
from pathlib import Path
import json,hashlib,tempfile,subprocess
from PIL import Image,ImageDraw,ImageFont
import numpy as np
R=Path(__file__).resolve().parent;E=R/'exposure';E.mkdir(exist_ok=True)
p37=R.parent/'whole_far_puff_zero_call/candidate/F037_whole_native_far_puff_PENDING.png';p42=R/'connection_call02/candidate/F042_complete_joint_pixels_v2_PENDING.png'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
reg=json.loads((R/'preparation.json').read_text())['registration'];s=reg['scale'];tx,ty=reg['translation_xy'];inv=(1/s,0,-tx/s,0,1/s,-ty/s)
refs={};sources={}
for frame,path in [(37,p37),(42,p42)]:
 im=Image.open(path).convert('RGBA');registered=im.transform((1536,864),Image.Transform.AFFINE,inv,resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0));registered.save(E/f'F{frame:03d}_registered.png')
 for nm,col in [('gray',(215,224,231,255)),('dark',(34,43,52,255))]:
  bg=Image.new('RGBA',registered.size,col);bg.alpha_composite(registered);preview=bg.crop((280,80,1304,656)).resize((1280,720),Image.Resampling.LANCZOS).convert('RGB');preview.save(E/f'F{frame:03d}_{nm}.png')
  if nm=='gray':refs[frame]=np.array(preview)
 sources[frame]={'path':str(path),'sha256':sha(path)}
sequence=[37]*5+[42]*2
video=E/'S09_F037x5_F042x2_actual_layer_24fps_PENDING.mp4'
with tempfile.TemporaryDirectory(prefix='s09-037-042-') as d:
 d=Path(d)
 for i,frame in enumerate(sequence):Image.fromarray(refs[frame]).save(d/f'{i:04d}.png')
 subprocess.run(['ffmpeg','-v','error','-y','-framerate','24','-i',str(d/'%04d.png'),'-frames:v','7','-an','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
data=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-f','rawvideo','-pix_fmt','rgb24','-']);frames=np.frombuffer(data,dtype=np.uint8).reshape((-1,720,1280,3));assert len(frames)==7
rows=[]
for i,frame in enumerate(frames):
 mae={f:float(np.abs(frame.astype(float)-r.astype(float)).mean()) for f,r in refs.items()};best=min(mae,key=mae.get);assert best==sequence[i];rows.append({'clip_frame':i,'expected_source':sequence[i],'decoded_closest_source':best,'RGB_MAE':mae[best]})
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18);sheet=Image.new('RGB',(1280,770),(239,243,246));dr=ImageDraw.Draw(sheet)
for k,i in enumerate([0,4,5,6]):
 im=Image.fromarray(frames[i]);im.save(E/f'actual_decoded_{i:02d}.png');sheet.paste(im.resize((640,360)),((k%2)*640,(k//2)*385+25));dr.text(((k%2)*640+8,(k//2)*385+2),f'实际解码clip{i} / S09 F{sequence[i]:03d}',font=font,fill='#26343e')
sheet.save(E/'actual_decoded_0_4_5_6_contact_sheet.png')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_frames,duration','-of','json',str(video)]))
report={'status':'ACTUAL7FRAME_EXPOSURE_DECODED_SOURCE_ORDER_VERIFIED_VISUAL_REVIEW_PENDING','sources':sources,'sequence':sequence,'fps':24,'no_tween':True,'no_audio':True,'isolated_actual_png_layer_not_full_scene_or_film':True,'registration':reg,'preview_crop_xyxy':[280,80,1304,656],'video_sha256':sha(video),'probe':probe,'all_decoded_frames':rows,'max_MAE':max(z['RGB_MAE'] for z in rows),'remaining_gate':'Actual visual near-arm/cuff/wrist/contact and037→042 anticipation/contact continuity review; not an entire-shot ready pass.'};(E/'actual_decode_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','video_sha256','probe','max_MAE']},ensure_ascii=False))
