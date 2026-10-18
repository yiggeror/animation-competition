#!/usr/bin/env python3
"""Actual held057/062/068/073 native PNGs, one fixed registration and camera crop."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,tempfile,subprocess
R=Path(__file__).resolve().parent;B=R.parent;E=R/'exposure';E.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
paths={57:B/'F057_semantic_color_ankle/candidate/F057_semantic_color_and_ankle_PENDING.png',62:B/'F062_native_call01/candidate/F062_single_native_final_with_waist_underlay_PENDING_ASTRA.png',68:B/'F068_next_gate/candidate/F068_single_native_final_PENDING_ASTRA.png',73:B/'F073_next_gate/candidate/F073_single_native_final_PENDING_ASTRA.png'}
holds={57:5,62:6,68:5,73:6}
reg=json.loads((B/'F068_next_gate/geometry/preparation_checks.json').read_text())['registration'];s=reg['s'];tx,ty=reg['tx'],reg['ty'];inv=(1/s,0,-tx/s,0,1/s,-ty/s)
preview_crop=(720,360,1488,792);refs={};sources={}
for f,p in paths.items():
 im=Image.open(p).convert('RGBA');assert im.size==(1672,1080)
 world=im.transform((1672,941),Image.Transform.AFFINE,inv,resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0));world.save(E/f'F{f:03d}_world_registered.png')
 for name,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
  q=Image.new('RGBA',world.size,col);q.alpha_composite(world);q=q.crop(preview_crop).resize((1280,720),Image.Resampling.LANCZOS).convert('RGB');q.save(E/f'F{f:03d}_{name}.png')
  if name=='gray':refs[f]=np.array(q)
 sources[f]={'path':str(p),'sha256':sha(p),'hold':holds[f],'native_canvas':[1672,1080]}
seq=sum(([f]*holds[f]for f in paths),[]);assert len(seq)==22
video=E/'S07_F057x5_F062x6_F068x5_F073x6_actual_layer_24fps_PENDING.mp4'
with tempfile.TemporaryDirectory(prefix='s07-057-078-')as tmp:
 d=Path(tmp)
 for i,f in enumerate(seq):Image.fromarray(refs[f]).save(d/f'{i:04d}.png')
 subprocess.run(['ffmpeg','-v','error','-y','-framerate','24','-i',str(d/'%04d.png'),'-frames:v',str(len(seq)),'-an','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
data=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-f','rawvideo','-pix_fmt','rgb24','-']);decoded=np.frombuffer(data,np.uint8).reshape((-1,720,1280,3));assert len(decoded)==22
rows=[]
for i,a in enumerate(decoded):
 mae={f:float(abs(a.astype(float)-v.astype(float)).mean())for f,v in refs.items()};best=min(mae,key=mae.get);assert best==seq[i];rows.append({'clip_frame':i,'scene_frame':57+i,'expected_source':seq[i],'closest_source':best,'RGB_MAE':mae[best]})
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18);sheet=Image.new('RGB',(2560,770),(237,242,246));d=ImageDraw.Draw(sheet)
for k,i in enumerate([0,4,5,10,11,15,16,21]):
 q=Image.fromarray(decoded[i]);q.save(E/f'actual_decoded_{i:02d}.png');x=(k%4)*640;y=(k//4)*385;sheet.paste(q.resize((640,360)),(x,y+25));d.text((x+4,y+2),f'实解码clip{i}／S07 F{57+i:03d}／源{seq[i]:03d}',font=font,fill='#26343e')
sheet.save(E/'actual_decoded_0_4_5_10_11_15_16_21.png')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_type,width,height,r_frame_rate,nb_frames,duration','-of','json',str(video)]))
report={'status':'22FRAME_REAL_PNG_EXPOSURE_DECODED_PENDING_ACTUAL_VISUAL_REVIEW','sources':sources,'sequence':seq,'fps':24,'scene_frames_inclusive':[57,78],'no_tween':True,'no_audio':True,'isolated_actual_PNG_not_Canvas_scene_or_full_film':True,'registration':reg,'constant_preview_crop_world_xyxy':preview_crop,'video_sha256':sha(video),'probe':probe,'decoded_frames':rows,'max_RGB_MAE':max(z['RGB_MAE']for z in rows),'remaining_gate':'Actual wholebody volume, support/foot lock, limb/clothes continuity and hand ownership review; not a whole108f S07 acceptance.'}
(E/'actual_decode_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['status','video_sha256','probe','max_RGB_MAE']},ensure_ascii=False,indent=2))
