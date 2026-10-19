#!/usr/bin/env python3
"""Actual090x5→095x5 isolated10f, fixedcamera, complete real decode evidence."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,tempfile,subprocess,numpy as np
R=Path(__file__).resolve().parent;E=R/'exposure';E.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
files={90:R/'sources/F090_LOCKED.png',95:R/'sources/F095_LOCKED.png'};expectedsha={90:'012e7bae3f7e39ca93467bf1d43ec003d3ed5a741816c67ee8fc67c5e1225156',95:'dcf919f412fd379a34ea69329210a418547dcccc089e1b36aa208024a04fdca4'}
for f,p in files.items():assert sha(p)==expectedsha[f]
reg=json.loads((R/'sources/registration.json').read_text());s,tx,ty=reg['s'],reg['tx'],reg['ty'];inv=(1/s,0,-tx/s,0,1/s,-ty/s);crop=(720,360,1488,792);seq=[90]*5+[95]*5;keep=[0,4,5,6,9];font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
report={'status':'ACTUAL10F_ALL_DECODED_PENDING_VISUAL_REVIEW','sequence':seq,'scene_frames_inclusive':[90,99],'fps':24,'registration':reg,'fixed_world_crop_xyxy':crop,'source_sha256':expectedsha,'no_tween':True,'new_generation_calls':0,'backgrounds':{},'limits':'Only requested isolated10f; noaudio, nofull108f scene/film, no100generation.'}
for tone,color in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 O=E/tone;O.mkdir(exist_ok=True);refs={}
 for f,p in files.items():
  im=Image.open(p).convert('RGBA');assert im.size==(1672,1080);world=im.transform((1672,941),Image.Transform.AFFINE,inv,Image.Resampling.BICUBIC,fillcolor=0);world.save(E/f'F{f:03d}_registered.png');bg=Image.new('RGBA',world.size,color);bg.alpha_composite(world);bg=bg.crop(crop).resize((1280,720),Image.Resampling.LANCZOS).convert('RGB');bg.save(O/f'F{f:03d}_reference.png');refs[f]=np.asarray(bg)
 video=O/f'S07_F090x5_F095x5_{tone}_actual_24fps.mp4'
 with tempfile.TemporaryDirectory(prefix='s07-090-095-')as tmp:
  T=Path(tmp)
  for i,f in enumerate(seq):Image.fromarray(refs[f]).save(T/f'{i:02d}.png')
  subprocess.run(['ffmpeg','-v','error','-y','-framerate','24','-i',str(T/'%02d.png'),'-frames:v','10','-an','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
 data=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-f','rawvideo','-pix_fmt','rgb24','-']);frames=np.frombuffer(data,np.uint8).reshape((-1,720,1280,3));assert len(frames)==10;rows=[]
 for i,im in enumerate(frames):
  err={f:float(np.abs(im.astype(float)-a.astype(float)).mean())for f,a in refs.items()};nearest=min(err,key=err.get);assert nearest==seq[i];rows.append({'clip_frame':i,'scene_frame':90+i,'expected':seq[i],'decoded_nearest':nearest,'RGB_MAE':err[nearest]})
 sheet=Image.new('RGB',(1920,770),(235,241,246));d=ImageDraw.Draw(sheet)
 for j,i in enumerate(keep):
  im=Image.fromarray(frames[i]);im.save(O/f'actual_decoded_{i:02d}.png');im.crop((420,350,1060,700)).resize((1280,700),Image.Resampling.NEAREST).save(O/f'actual_decoded_{i:02d}_legs_feet_2x.png');x,y=(j%3)*640,(j//3)*385;sheet.paste(im.resize((640,360)),(x,y+25));d.text((x+4,y+2),f'实解码clip{i}／F{90+i:03d}／源{seq[i]}',font=font,fill='#26343e')
 sheet.save(O/'actual_decoded_contact_sheet.png');probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_type,width,height,r_frame_rate,nb_frames,duration','-of','json',str(video)]));assert len(probe['streams'])==1;st=probe['streams'][0];assert(st['width'],st['height'],st['r_frame_rate'],st['nb_frames'])==(1280,720,'24/1','10');report['backgrounds'][tone]={'video':str(video.relative_to(R)),'sha256':sha(video),'probe':probe,'decoded_frames':rows,'max_RGB_MAE':max(v['RGB_MAE']for v in rows)}
(E/'actual_decode_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:{'sha256':v['sha256'],'decoded':len(v['decoded_frames']),'max_RGB_MAE':v['max_RGB_MAE']}for k,v in report['backgrounds'].items()},indent=2))
