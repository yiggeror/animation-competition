#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import subprocess,numpy as np,json
R=Path(__file__).resolve().parent
video=R/'exposure/S09_F031x6_F037x5_actual_layer_24fps.mp4'
data=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-f','rawvideo','-pix_fmt','rgb24','-'])
frames=np.frombuffer(data,dtype=np.uint8).reshape((-1,720,1280,3));assert len(frames)==11
refs={f:np.array(Image.open(R/f'exposure/F{f:03d}_gray.png').convert('RGB')).astype(float) for f in [31,37]}
rows=[]
for i,frame in enumerate(frames):
    mae={f:float(np.abs(frame.astype(float)-z).mean()) for f,z in refs.items()}
    best=min(mae,key=mae.get);expected=31 if i<6 else 37
    assert best==expected
    rows.append({'clip_frame':i,'S09_source_frame':expected,'best_match':best,'mean_absolute_rgb_error':mae[expected]})
sheet=Image.new('RGB',(1280,760),(242,244,247));draw=ImageDraw.Draw(sheet)
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
for col,i in enumerate([0,5,6,10]):
    im=Image.fromarray(frames[i]);sheet.paste(im.resize((640,360)),((col%2)*640,(col//2)*380+20))
    draw.text(((col%2)*640+10,(col//2)*380),f'实际解码clip{i} / S09 F{31 if i<6 else 37:03d}',font=font,fill='#223344')
sheet.save(R/'qa/actual_decoded_exposure_0_5_6_10.png')
(R/'exposure/actual_decode_checks.json').write_text(json.dumps({'decoded_frames':11,'fps':24,'exact_source_order_classified':True,'frames':rows,'scope':'Decode every actual MP4 frame and compare against two held PNGs; no claim of final scene/audio or subjective dynamic naturalness.'},indent=2)+'\n')
print('11 actual frames decoded;31x6→37x5 verified; maxMAE',max(t['mean_absolute_rgb_error'] for t in rows))
