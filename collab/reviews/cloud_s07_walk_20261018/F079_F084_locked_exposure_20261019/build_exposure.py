#!/usr/bin/env python3
"""Actual locked079x5 -> locked084x6, fixed registration, every frame decoded."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import json, hashlib, tempfile, subprocess
R=Path(__file__).resolve().parent; E=R/'exposure'; E.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
files={79:R/'sources/F079_LOCKED.png',84:R/'sources/F084_LOCKED.png'}
assert sha(files[79])=='856d10c9516c33a8e992a121033e76a5ac55bda269b16949a90aa431206f0364'
assert sha(files[84])=='21acf20424d94477191dbc6fd012fe61426d509ec55dbc48037bb97b2c89f6ae'
reg=json.loads((R/'sources/registration.json').read_text());s=reg['s'];tx,ty=reg['tx'],reg['ty']
inverse=(1/s,0,-tx/s,0,1/s,-ty/s);crop=(720,360,1488,792);sequence=[79]*5+[84]*6
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
report={'status':'ACTUAL11F_ALL_DECODED_PENDING_VISUAL_REVIEW','sequence':sequence,
        'scene_frames_inclusive':[79,89],'registration':reg,'fixed_world_crop_xyxy':crop,
        'source_sha256':{f:sha(p)for f,p in files.items()},'no_tween':True,'new_generation_calls':0,
        'backgrounds':{},'limits':'Isolated layer only, no audio, not full108f scene or complete film.'}
for tone,color in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
    O=E/tone;O.mkdir(exist_ok=True);refs={}
    for frame,path in files.items():
        im=Image.open(path).convert('RGBA');assert im.size==(1672,1080)
        world=im.transform((1672,941),Image.Transform.AFFINE,inverse,resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
        world.save(E/f'F{frame:03d}_registered.png')
        bg=Image.new('RGBA',world.size,color);bg.alpha_composite(world)
        bg=bg.crop(crop).resize((1280,720),Image.Resampling.LANCZOS).convert('RGB')
        bg.save(O/f'F{frame:03d}_reference.png');refs[frame]=np.array(bg)
    video=O/f'S07_F079x5_F084x6_{tone}_actual_24fps.mp4'
    with tempfile.TemporaryDirectory(prefix='s07-079-084-')as temp:
        T=Path(temp)
        for i,frame in enumerate(sequence):Image.fromarray(refs[frame]).save(T/f'{i:02d}.png')
        subprocess.run(['ffmpeg','-v','error','-y','-framerate','24','-i',str(T/'%02d.png'),'-frames:v','11','-an','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
    data=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-f','rawvideo','-pix_fmt','rgb24','-'])
    decoded=np.frombuffer(data,np.uint8).reshape((-1,720,1280,3));assert len(decoded)==11;rows=[]
    for i,image in enumerate(decoded):
        errors={frame:float(np.abs(image.astype(float)-ref.astype(float)).mean())for frame,ref in refs.items()}
        nearest=min(errors,key=errors.get);assert nearest==sequence[i]
        rows.append({'clip_frame':i,'scene_frame':79+i,'expected':sequence[i],'decoded_nearest':nearest,'RGB_MAE':errors[nearest]})
    sheet=Image.new('RGB',(1920,770),(235,241,246));draw=ImageDraw.Draw(sheet)
    for j,i in enumerate([0,4,5,6,10]):
        actual=Image.fromarray(decoded[i]);actual.save(O/f'actual_decoded_{i:02d}.png')
        x,y=(j%3)*640,(j//3)*385;sheet.paste(actual.resize((640,360)),(x,y+25))
        draw.text((x+4,y+2),f'实解码clip{i}／F{79+i:03d}／源{sequence[i]}',font=font,fill='#26343e')
        actual.crop((420,350,1060,700)).resize((1280,700),Image.Resampling.NEAREST).save(O/f'actual_decoded_{i:02d}_legs_feet_2x.png')
    sheet.save(O/'actual_decoded_contact_sheet.png')
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_type,width,height,r_frame_rate,nb_frames,duration','-of','json',str(video)]))
    streams=probe['streams'];assert len(streams)==1
    assert(streams[0]['width'],streams[0]['height'],streams[0]['r_frame_rate'],streams[0]['nb_frames'])==(1280,720,'24/1','11')
    report['backgrounds'][tone]={'video':str(video.relative_to(R)),'sha256':sha(video),'probe':probe,'decoded_frames':rows,'max_RGB_MAE':max(row['RGB_MAE']for row in rows)}
(E/'actual_decode_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({tone:{'sha256':values['sha256'],'decoded':len(values['decoded_frames']),'max_MAE':values['max_RGB_MAE']}for tone,values in report['backgrounds'].items()},indent=2))
