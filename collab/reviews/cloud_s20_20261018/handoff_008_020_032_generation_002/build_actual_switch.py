"""Lossless review switch of the three real retained images, no new pose/scene."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;frames=[];rows=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in [8,20,32]:
 f=P/f'F{n:03}';s=json.loads((f/'status.json').read_text());assert s['state']=='AUTHOR_ACCEPTED'
 p=f/s['accepted_png'];assert sha(p)==s['accepted_sha256']
 im=Image.open(p).convert('RGBA');assert im.size==(1672,941);frames.append(im)
 rows.append({'frame':n,'file':str(p.relative_to(P)),'sha256':sha(p)})
apng=P/'actual_008_020_032_switch.apng'
frames[0].save(apng,format='PNG',save_all=True,append_images=frames[1:],duration=[900,1200,1500],loop=0,disposal=[0,0,0],blend=[0,0,0])
check=Image.open(apng);assert check.n_frames==3
for i,frame in enumerate(frames):check.seek(i);assert np.array_equal(np.array(check.convert('RGBA')),np.array(frame))
box=(570,270,1045,535);w,h=box[2]-box[0],box[3]-box[1]
board=Image.new('RGB',(w*3,h+42),'#bfc3c7');d=ImageDraw.Draw(board)
font=ImageFont.truetype(str(P.parent.parents[2]/'assets/fonts/NotoSansSC-VF.ttf'),22)
titles=['008 两掌未触 / 原供应握','020 两接收实握 / 共同承重','032 接收保持 / 供应开掌离杆']
for i,im in enumerate(frames):
 bg=Image.new('RGBA',im.size,'#bfc3c7');bg.alpha_composite(im)
 board.paste(bg.convert('RGB').crop(box),(i*w,42));d.text((i*w+8,9),titles[i],font=font,fill='#263743')
board.save(P/'actual_008_020_032_contact.png')
(P/'actual_switch_manifest.json').write_text(json.dumps({'source_frames':rows,'APNG':apng.name,'APNG_sha256':sha(apng),'decoded_APNG_frames_exact_source_RGBA':True,'size':[1672,941],'unique_drawn_states':3,'review_hold_ms':[900,1200,1500],'review_holds_are_not_film_exposure':True,'new_intermediate_states':0,'scene_frames_rendered':0,'new_model_calls_for_proof':0},ensure_ascii=False,indent=2)+'\n')
print('3 real accepted PNGs -> lossless APNG, each decoded frame exact RGBA; review crop contact sheet ready.')
