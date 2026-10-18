#!/usr/bin/env python3
"""Real locked073x6 -> corrected locked079x5, fixed source registration."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,tempfile,subprocess
R=Path(__file__).resolve().parent;E=R/'exposure';E.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
files={73:R/'sources/F073_LOCKED.png',79:R/'sources/F079_LOCKED.png'};assert sha(files[73])=='afc7dcff6593611d0e33b16a7fce9e12967bf1767cacf8336308a51a50af1929';assert sha(files[79])=='856d10c9516c33a8e992a121033e76a5ac55bda269b16949a90aa431206f0364'
reg=json.loads((R/'sources/registration.json').read_text());s=reg['s'];tx,ty=reg['tx'],reg['ty'];inv=(1/s,0,-tx/s,0,1/s,-ty/s);crop=(720,360,1488,792);seq=[73]*6+[79]*5
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
report={'status':'REAL11F_EXPOSURE_ALL_FRAMES_DECODED_VISUAL_PENDING','sequence':seq,'scene_frames_inclusive':[73,83],'source_sha256':{f:sha(p)for f,p in files.items()},'registration':reg,'fixed_world_crop_xyxy':crop,'no_tween':True,'new_generation_calls':0,'backgrounds':{},'limits':'Isolated originalPNG24fps/noaudio only, not full108f scene/film. 084input only, no089state.'}
for bg,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 O=E/bg;O.mkdir(exist_ok=True);refs={}
 for f,p in files.items():
  im=Image.open(p).convert('RGBA');assert im.size==(1672,1080);world=im.transform((1672,941),Image.Transform.AFFINE,inv,resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0));world.save(E/f'F{f:03d}_registered.png');v=Image.new('RGBA',world.size,col);v.alpha_composite(world);v=v.crop(crop).resize((1280,720),Image.Resampling.LANCZOS).convert('RGB');v.save(O/f'F{f:03d}_reference.png');refs[f]=np.array(v)
 video=O/f'S07_F073x6_F079x5_{bg}_actual_24fps.mp4'
 with tempfile.TemporaryDirectory(prefix='s07-73-79-')as tmp:
  T=Path(tmp)
  for i,f in enumerate(seq):Image.fromarray(refs[f]).save(T/f'{i:02d}.png')
  subprocess.run(['ffmpeg','-v','error','-y','-framerate','24','-i',str(T/'%02d.png'),'-frames:v','11','-an','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
 data=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-f','rawvideo','-pix_fmt','rgb24','-']);a=np.frombuffer(data,np.uint8).reshape((-1,720,1280,3));assert len(a)==11;rows=[]
 for i,z in enumerate(a):
  errors={f:float(np.abs(z.astype(float)-v.astype(float)).mean())for f,v in refs.items()};best=min(errors,key=errors.get);assert best==seq[i];rows.append({'clip_frame':i,'scene_frame':73+i,'expected':seq[i],'decoded_nearest':best,'RGB_MAE':errors[best]})
 sheet=Image.new('RGB',(1920,770),(235,241,246));d=ImageDraw.Draw(sheet)
 for j,i in enumerate([0,4,5,6,7,10]):
  v=Image.fromarray(a[i]);v.save(O/f'actual_decoded_{i:02d}.png');x=(j%3)*640;y=(j//3)*385;sheet.paste(v.resize((640,360)),(x,y+25));d.text((x+4,y+2),f'实解码clip{i}／F{73+i:03d}／源{seq[i]}',font=font,fill='#26343e')
 sheet.save(O/'actual_decoded_contact_sheet.png')
 for i in [5,6,10]:Image.fromarray(a[i]).crop((420,350,1060,700)).resize((1280,700),Image.Resampling.NEAREST).save(O/f'actual_decoded_{i:02d}_legs_feet_2x.png')
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_type,width,height,r_frame_rate,nb_frames,duration','-of','json',str(video)]));st=probe['streams'];assert len(st)==1 and(st[0]['width'],st[0]['height'],st[0]['r_frame_rate'],st[0]['nb_frames'])==(1280,720,'24/1','11')
 report['backgrounds'][bg]={'video':str(video.relative_to(R)),'sha256':sha(video),'probe':probe,'decoded_frames':rows,'max_RGB_MAE':max(q['RGB_MAE']for q in rows)}
(E/'actual_decode_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({b:{'sha256':v['sha256'],'max_MAE':v['max_RGB_MAE']}for b,v in report['backgrounds'].items()},ensure_ascii=False,indent=2))
