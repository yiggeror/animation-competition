#!/usr/bin/env python3
"""Actual adopted PNG exposure QA through d07; no Canvas scene, audio or full film."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,subprocess,shutil,numpy as np
P=Path(__file__).resolve().parents[1];ROOT=P.parent
TMP=Path('/tmp/s13_d05_d07_layer_qa');TMP.mkdir(exist_ok=True)
f=lambda n:ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',n)
sources=[ROOT/'d01_first_candidate/candidates/S13_d01_uniform_registered_rgba.png',
 ROOT/'d02_d04_segment/approved_local/F018_d02_eyes_up.png',ROOT/'d02_d04_segment/approved_local/F024_d03_whole_head_right.png',
 ROOT/'d02_d04_segment/approved_local/F030_d04_awake_closed_mouth.png',P/'approved_local/F036_d05_pretend_drowsy.png',
 P/'approved_local/F040_d06_yawn_start.png',P/'approved_local/F044_d07_yawn_opening.png']
starts=[0,18,24,30,36,40,44];holds=[18,6,6,6,4,4,6]
labels=['d04 F030 ×6 已锁清醒','d05 F036 ×4 装困起势','d06 F040 ×4 哈欠起势','d07 F044 ×6 中间张开']
def comp(im,c=(245,245,245,255)):
 b=Image.new('RGBA',im.size,c);b.alpha_composite(im);return b.convert('RGB')
sheet=Image.new('RGB',(1920,820),'#f5f3ed');d=ImageDraw.Draw(sheet)
close=Image.new('RGB',(1920,860),'#f5f3ed');cd=ImageDraw.Draw(close)
for i,path in enumerate(sources[3:]):
 im=Image.open(path).convert('RGBA');a=comp(im).crop((90,20,940,1190));a.thumbnail((465,650));sheet.paste(a,(480*i+8,70));d.text((480*i+12,20),labels[i],font=f(21),fill='#23333e')
 a=comp(im).crop((510,510,910,1070));a.thumbnail((465,650));close.paste(a,(480*i+8,70));cd.text((480*i+12,20),labels[i],font=f(21),fill='#23333e')
d.text((22,745),'实际原生绘图，同画布/同裁切/同缩放。仅到d07；d08峰态未执行，颈领/上胸共同运动。',font=f(25),fill='#23333e')
cd.text((22,765),'双瞳可见 → 半垂 → 近全闭；口与真实下颌/颈面连贯，未用代码缩放嘴或重画五官。',font=f(24),fill='#23333e')
sheet.save(P/'qa/00_d04_d07_same_scale_actual.jpg',quality=96);close.save(P/'qa/01_eye_jaw_neck_progression.jpg',quality=97)

sheet=Image.new('RGB',(1536,1900),'#f5f3ed');d=ImageDraw.Draw(sheet)
for row,path in enumerate(sources[4:]):
 im=Image.open(path).convert('RGBA')
 for col,c in enumerate([(245,245,245,255),(38,44,53,255),(160,175,180,255)]):
  a=comp(im,c);a.thumbnail((500,570));sheet.paste(a,(512*col,row*620+45))
 d.text((20,row*620+10),labels[row+1],font=f(23),fill='#23333e')
sheet.save(P/'qa/all_adopted_on_three_backgrounds.jpg',quality=95)

for i,path in enumerate(sources):
 im=Image.open(path).convert('RGBA');sc=.85*2/3
 layer=im.transform((1280,720),Image.Transform.AFFINE,(1/sc,0,-220/sc,0,1/sc,20/sc),Image.Resampling.BICUBIC)
 frame=comp(layer,(211,214,213,255));draw=ImageDraw.Draw(frame)
 draw.text((20,12),'S13 0–49f 实际画层曝光 / 中性底 / 非接景Canvas渲染 / 无音频',font=f(19),fill='#3c4448');frame.save(TMP/f'd{i+1:02}.png')
for n in range(50):
 pose=max(i for i,t in enumerate(starts) if n>=t)
 shutil.copyfile(TMP/f'd{pose+1:02}.png',TMP/f'frame_{n:03}.png')
mp4=P/'qa/isolated_50f_through_d07.mp4'
cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-framerate','24','-i',str(TMP/'frame_%03d.png'),'-frames:v','50','-fps_mode','cfr','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-an',str(mp4)]
subprocess.run(cmd,check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(mp4)],text=True));st=probe['streams'][0]
assert len(probe['streams'])==1 and st['nb_frames']=='50' and st['r_frame_rate']=='24/1' and st['width']==1280 and st['height']==720
frames=[0,17,18,23,24,29,30,35,36,39,40,43,44,49];sel='+'.join(f'eq(n,{n})' for n in frames)
subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(mp4),'-vf',f"select='{sel}'",'-fps_mode','vfr',str(TMP/'decoded_%02d.png')],check=True)
refs=[np.array(Image.open(TMP/f'd{i+1:02}.png').convert('RGB'),dtype=np.float32)[270:515,520:750] for i in range(7)]
rows=[];contact=Image.new('RGB',(1920,820),'#f5f3ed');draw=ImageDraw.Draw(contact)
last_frames=[30,35,36,39,40,43,44,49]
for i,n in enumerate(frames):
 im=Image.open(TMP/f'decoded_{i+1:02}.png').convert('RGB');a=np.array(im,dtype=np.float32)[270:515,520:750]
 mse=[float(np.mean((a-r)**2)) for r in refs];got=int(np.argmin(mse));expected=max(j for j,t in enumerate(starts) if n>=t)
 assert got==expected,(n,got,expected,mse)
 rows.append({'frame':n,'expected_pose':f'd{expected+1:02}','nearest_pose':f'd{got+1:02}','face_ROI_mse':mse})
 if n in last_frames:
  j=last_frames.index(n);im.thumbnail((470,340));x=j%4*480+5;y=j//4*390+45;contact.paste(im,(x,y));draw.text((x,y-34),f'F{n:03} → d{got+1:02}',font=f(23),fill='#23333e')
contact.save(P/'qa/decoded_30_49_exposure_contact.jpg',quality=95)
report={'type':'isolated_adopted_PNG_layer_NOT_Canvas_scene','width':1280,'height':720,'fps':'24/1','frames':50,'duration_s':50/24,'audio_streams':0,
 'timeline':list(zip(starts,holds)),'decode_checks':rows,'ffmpeg_command':cmd,'full_film_or_scene_lighting':False,'d08_present':False}
(P/'qa/exposure_50f_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS: 50f at24fps decoded, all adopted pose switches verified; d05@36, d06@40, d07@44; no d08/no audio.')
