#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,subprocess,tempfile
H=Path(__file__).resolve().parents[1];P=H.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
final=H/'candidates/F024_final_rgba.png';previous=P/'d05_d07_segment/candidates/F019_rgba.png';raw=P/'d07_F024_zero_call_repair/candidates/F024_original_pixel_sleeve_repair_rgba.png';master=P/'d01_hair_color_fix/candidates/F000_hair_corrected_rgba.png'
assert sha(final)=='44137d740ac5d07ca0258019c28cdf8f9b648d77ba79eda07f366f24503753db';assert sha(previous)=='d5f04b6b949a6b96a0c39ec8fe8850f7b2b30f00af835bbe38ddf53c66b4c1a3'
font=lambda n:ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',n)
def comp(im,col):
 bg=Image.new('RGBA',im.size,(*col,255));bg.alpha_composite(im);return bg.convert('RGB')
# Actual unannotated image comparisons; all registration is the same frozen B.
for files,labels,name in [([master,raw,final],['锁母0485','4a203原色','最终清边+分区色门'],'master_source_final'),([previous,final],['019前态','024最终候选'],'019_final024')]:
 n=len(files);board=Image.new('RGB',(n*600,950),'#eeebe3');d=ImageDraw.Draw(board)
 for i,(p,label)in enumerate(zip(files,labels)):
  im=comp(Image.open(p).convert('RGBA'),(160,167,172));im.thumbnail((580,870));board.paste(im,(i*600+10,55));d.text((i*600+10,10),label,font=font(24),fill='#24303a')
 board.save(H/f'qa/{name}_actual.jpg',quality=98)
# Sample-location evidence on source and mother, with independent material sample masks.
colors=[(255,40,120),(90,225,255),(190,95,255),(55,220,150),(25,160,100),(255,170,30),(225,105,15),(40,130,245),(40,65,190)]
names=['crown','near_tail','far_tail','skin_face_lit','skin_face_shadow','skin_ear_lit','skin_ear_shadow','skin_neck_lit','skin_neck_shadow']
board=Image.new('RGB',(1400,1140),'#eeebe3');d=ImageDraw.Draw(board)
for side,path in enumerate([raw,master]):
 im=np.array(comp(Image.open(path).convert('RGBA'),(160,167,172)))
 for i,name in enumerate(names):
  f=H/'masks'/((('master_'+name+'_sample.png')if side else(name+'_sample.png'))if not name.startswith('skin_')else(('master_'+name+'_sample.png')if side else(name+'_core_sample.png')))
  mask=np.array(Image.open(f))>0;im[mask]=np.rint(.35*im[mask]+.65*np.array(colors[i])).astype('uint8')
 panel=Image.fromarray(im);panel.thumbnail((650,975));board.paste(panel,(side*700+10,50));d.text((side*700+10,10),'024源：冻结语义样点'if side==0 else'锁母：对应语义样点',font=font(24),fill='#24303a')
for i,name in enumerate(names):
 x=10+(i%3)*465;y=1040+(i//3)*30;d.rectangle((x,y,x+18,y+18),fill=colors[i]);d.text((x+25,y-3),name,font=font(17),fill='#24303a')
board.save(H/'qa/independent_source_master_sample_locations.jpg',quality=98)
validation={};contact=[]
for label,col in [('gray',(160,167,172)),('dark',(53,61,70))]:
 with tempfile.TemporaryDirectory(prefix='s24_final13_')as tmp:
  tmp=Path(tmp);source_rows=[]
  for i in range(13):
   state=19 if i<5 else 24;p=previous if state==19 else final
   im=Image.open(p).convert('RGBA').transform((1920,1080),Image.Transform.AFFINE,(1/.7,0,-590/.7,0,1/.7,-20/.7),Image.Resampling.BICUBIC);frame=comp(im,col);f=tmp/f'{i:04}.png';frame.save(f);source_rows.append({'local_frame':i,'scene_frame':19+i,'drawing':state,'source_sha256':sha(p),'registered_source_PNG_sha256':sha(f)})
  target=H/f'qa/S24_final_F019_031_{label}_13f_24fps_NOT_SCENE.mp4'
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','24','-i',str(tmp/'%04d.png'),'-frames:v','13','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(target)],check=True)
  probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(target)]));v=probe['streams'][0];assert len(probe['streams'])==1 and(v['width'],v['height'],v['nb_read_frames'],v['avg_frame_rate'])==(1920,1080,'13','24/1')
  subprocess.run(['ffmpeg','-v','error','-y','-i',str(target),'-fps_mode','passthrough',str(tmp/'decode_%03d.png')],check=True)
  for i in [0,4,5,12]:
   f=H/f'qa/decoded_{label}_scene{19+i:03}.jpg';Image.open(tmp/f'decode_{i+1:03}.png').convert('RGB').save(f,quality=98)
   if i in[0,5,12]:contact.append((f,f'{label} · {19+i:03}'))
  validation[label]={'mp4_sha256':sha(target),'frames':13,'size':[1920,1080],'rate':'24/1','duration':v['duration'],'schedule':[[19,5],[24,8]],'B_registration':[.7,590,20],'no_audio':True,'not_Canvas_scene':True,'source_frames':source_rows}
board=Image.new('RGB',(1920,810),'#eeebe3');d=ImageDraw.Draw(board)
for i,(p,label)in enumerate(contact):
 im=Image.open(p).resize((640,360));x=i%3*640;y=i//3*405;board.paste(im,(x,y+40));d.text((x+10,y+5),label,font=font(22),fill='#24303a')
board.save(H/'qa/actual_decoded_gray_dark_13f_contact.jpg',quality=98)
(H/'qa/exposure_validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n')
subprocess.run(['python3',str(H/'tools/verify_protection.py')],check=True)
print('PASS actual grey/dark13f layer encode/decode and protection checks')
