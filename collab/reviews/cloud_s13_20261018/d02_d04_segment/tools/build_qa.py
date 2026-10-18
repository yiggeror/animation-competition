#!/usr/bin/env python3
"""Actual PNG layer inspection and 36-frame exposure check, not a Canvas scene render."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,subprocess,numpy as np,shutil
P=Path(__file__).resolve().parents[1];ROOT=P.parent
TMP=Path('/tmp/s13_d02_d04_layer_qa');TMP.mkdir(exist_ok=True)
f=lambda n:ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',n)
sources=[ROOT/'d01_first_candidate/candidates/S13_d01_uniform_registered_rgba.png',
 P/'approved_local/F018_d02_eyes_up.png',P/'approved_local/F024_d03_whole_head_right.png',P/'approved_local/F030_d04_awake_closed_mouth.png']
labels=['d01 F000 ×18 已锁母态','d02 F018 ×6 眼先右上','d03 F024 ×6 整头右转','d04 F030 ×6 清醒收口']
def comp(im,c=(245,245,245,255)):
 bg=Image.new('RGBA',im.size,c);bg.alpha_composite(im);return bg.convert('RGB')
sheet=Image.new('RGB',(1920,820),'#f5f3ed');d=ImageDraw.Draw(sheet)
for i,path in enumerate(sources):
 im=Image.open(path).convert('RGBA');a=comp(im).crop((100,100,930,1120));a.thumbnail((465,660));sheet.paste(a,(i*480+7,80))
 d.text((i*480+12,22),labels[i],font=f(22),fill='#23333e')
 layer=im.transform((1280,720),Image.Transform.AFFINE,(1/(.85*2/3),0,-220/(.85*2/3),0,1/(.85*2/3),20/(.85*2/3)),Image.Resampling.BICUBIC)
 frame=comp(layer,(211,214,213,255));dd=ImageDraw.Draw(frame)
 dd.text((20,12),'S13 0–35f 实际画层曝光 / 中性底 / 非接景Canvas渲染 / 无音频',font=f(19),fill='#3c4448')
 frame.save(TMP/f'd{i+1:02}.png')
d.text((22,740),'同画布、同裁切、同缩放；全部人物为实际生成像素。d03颈领/上肩为完整新单元，下胸保持。',font=f(25),fill='#23333e')
sheet.save(P/'qa/00_d01_d04_same_scale_actual.jpg',quality=96)

# Deep/light/blue-gray check for every new adopted RGBA image.
sheet=Image.new('RGB',(1536,1900),'#f5f3ed');d=ImageDraw.Draw(sheet)
for row,path in enumerate(sources[1:]):
 for col,color in enumerate([(245,245,245,255),(38,44,53,255),(160,175,180,255)]):
  a=comp(Image.open(path).convert('RGBA'),color);a.thumbnail((500,570));sheet.paste(a,(col*512,row*620+45))
 d.text((20,row*620+10),labels[row+1],font=f(23),fill='#23333e')
sheet.save(P/'qa/all_three_poses_on_three_backgrounds.jpg',quality=95)

for n in range(36):
 pose=1 if n<18 else 2 if n<24 else 3 if n<30 else 4
 shutil.copyfile(TMP/f'd{pose:02}.png',TMP/f'frame_{n:03}.png')
mp4=P/'qa/isolated_36f_layer_preview.mp4'
cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-framerate','24','-i',str(TMP/'frame_%03d.png'),'-frames:v','36','-fps_mode','cfr','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-an',str(mp4)]
subprocess.run(cmd,check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(mp4)],text=True))
st=probe['streams'][0];assert st['width']==1280 and st['height']==720 and st['nb_frames']=='36' and st['r_frame_rate']=='24/1'
assert len(probe['streams'])==1
frames=[0,17,18,23,24,29,30,35]
sel='+'.join(f'eq(n,{n})' for n in frames)
subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(mp4),'-vf',f"select='{sel}'",'-fps_mode','vfr',str(TMP/'decoded_%02d.png')],check=True)
contact=Image.new('RGB',(1920,820),'#f5f3ed');d=ImageDraw.Draw(contact);rows=[]
refs=[np.array(Image.open(TMP/f'd{i+1:02}.png').convert('RGB'),dtype=np.float32)[270:515,520:750] for i in range(4)]
for i,n in enumerate(frames):
 im=Image.open(TMP/f'decoded_{i+1:02}.png').convert('RGB');a=np.array(im,dtype=np.float32)[270:515,520:750]
 errors=[float(np.mean((a-r)**2)) for r in refs];got=int(np.argmin(errors));expected=0 if n<18 else 1 if n<24 else 2 if n<30 else 3
 assert got==expected,(n,got,expected,errors)
 rows.append({'frame':n,'expected_pose':f'd{expected+1:02}','nearest_pose':f'd{got+1:02}','face_ROI_mse':errors})
 im.thumbnail((470,340));x=(i%4)*480+5;y=(i//4)*390+45;contact.paste(im,(x,y));d.text((x,y-34),f'F{n:03} → d{got+1:02}',font=f(23),fill='#23333e')
contact.save(P/'qa/decoded_36f_exposure_contact.jpg',quality=95)
report={'type':'isolated_actual_PNG_layer_preview_NOT_Canvas_scene','width':1280,'height':720,'fps':'24/1','frames':36,'duration_s':1.5,'audio_streams':0,'decode_checks':rows,'ffmpeg_command':cmd,'scene_lighting_or_full_film':False,
 'discarded_preview_attempt':'Duration-based concat made the d03 switch one frame early (F023). Replaced with explicit 36-index PNG sequence at native24fps; final actual decoded cuts checked.'}
(P/'qa/exposure_36f_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS: decoded 36f / 24fps; exact switches 18/24/30; no audio; actual generated PNG layer only.')
