#!/usr/bin/env python3
"""Native PNG layer exposure through d10; no Canvas scene or audio."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,subprocess,shutil,numpy as np
P=Path(__file__).resolve().parents[1];R=P.parent;T=Path('/tmp/s13_d08_d10_qa');T.mkdir(exist_ok=True)
files=['d01_first_candidate/candidates/S13_d01_uniform_registered_rgba.png','d02_d04_segment/approved_local/F018_d02_eyes_up.png',
'd02_d04_segment/approved_local/F024_d03_whole_head_right.png','d02_d04_segment/approved_local/F030_d04_awake_closed_mouth.png',
'd05_d07_segment/approved_local/F036_d05_pretend_drowsy.png','d05_d07_segment/approved_local/F040_d06_yawn_start.png',
'd05_d07_segment/approved_local/F044_d07_yawn_opening.png','d08_d10_group/approved_local/F050_d08_yawn_peak.png',
'd08_d10_group/approved_local/F058_d09_sustained_breath.png','d08_d10_group/approved_local/F068_d10_yawn_release.png']
sources=[R/x for x in files];starts=[0,18,24,30,36,40,44,50,58,68];holds=[18,6,6,6,4,4,6,8,10,10]
font=lambda n:ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',n)
def comp(im,c=(245,245,245,255)):
 b=Image.new('RGBA',im.size,c);b.alpha_composite(im);return b.convert('RGB')
sheet=Image.new('RGB',(1920,820),'#f5f3ed');d=ImageDraw.Draw(sheet);close=Image.new('RGB',(1920,840),'#f5f3ed');cd=ImageDraw.Draw(close)
labels=['d07 已锁中间态','d08 F050×8 峰态','d09 F058×10 独立续气','d10 F068×10 收束']
for i,path in enumerate(sources[6:]):
 im=Image.open(path).convert('RGBA');a=comp(im).crop((90,20,940,1190));a.thumbnail((465,650));sheet.paste(a,(i*480+8,70));d.text((i*480+12,20),labels[i],font=font(22),fill='#23333e')
 a=comp(im).crop((510,500,930,1080));a.thumbnail((465,650));close.paste(a,(i*480+8,70));cd.text((i*480+12,20),labels[i],font=font(22),fill='#23333e')
d.text((20,750),'同画布/裁切/缩放，真实原生图；颅体不跟嘴膨胀，下颌/颈领/胸肩共同张合。',font=font(25),fill='#23333e')
cd.text((20,755),'d08/d09全闭无残瞳；d10仅细缝初开。续气为独立原生画，非同图缩嘴。',font=font(24),fill='#23333e')
sheet.save(P/'qa/00_d07_d10_same_scale_actual.jpg',quality=96);close.save(P/'qa/01_jaw_neck_chest_progression.jpg',quality=97)
sheet=Image.new('RGB',(1536,1900),'#f5f3ed');d=ImageDraw.Draw(sheet)
for row,path in enumerate(sources[7:]):
 for col,c in enumerate([(245,245,245,255),(38,44,53,255),(160,175,180,255)]):
  a=comp(Image.open(path).convert('RGBA'),c);a.thumbnail((500,570));sheet.paste(a,(col*512,row*620+45))
 d.text((20,row*620+10),labels[row+1],font=font(23),fill='#23333e')
sheet.save(P/'qa/all_three_on_three_backgrounds.jpg',quality=95)
for i,path in enumerate(sources):
 sc=.85*2/3;im=Image.open(path).convert('RGBA');layer=im.transform((1280,720),Image.Transform.AFFINE,(1/sc,0,-220/sc,0,1/sc,20/sc),Image.Resampling.BICUBIC)
 a=comp(layer,(211,214,213,255));ImageDraw.Draw(a).text((20,12),'S13 0–77f 实际画层 / 中性底 / 非Canvas接景 / 无音频',font=font(19),fill='#3c4448');a.save(T/f'd{i+1:02}.png')
for n in range(78):shutil.copyfile(T/f'd{max(i for i,t in enumerate(starts) if n>=t)+1:02}.png',T/f'frame_{n:03}.png')
mp4=P/'qa/isolated_78f_through_d10.mp4';cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-framerate','24','-i',str(T/'frame_%03d.png'),'-frames:v','78','-fps_mode','cfr','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-an',str(mp4)]
subprocess.run(cmd,check=True);probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(mp4)],text=True));s=probe['streams'][0]
assert len(probe['streams'])==1 and s['nb_frames']=='78' and s['r_frame_rate']=='24/1' and s['width']==1280 and s['height']==720
frames=[44,49,50,57,58,67,68,77];sel='+'.join(f'eq(n,{n})' for n in frames)
subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(mp4),'-vf',f"select='{sel}'",'-fps_mode','vfr',str(T/'decoded_%02d.png')],check=True)
refs=[np.array(Image.open(T/f'd{i+1:02}.png').convert('RGB'),dtype=np.float32)[270:515,520:750] for i in range(10)];rows=[];sheet=Image.new('RGB',(1920,820),'#f5f3ed');d=ImageDraw.Draw(sheet)
for i,n in enumerate(frames):
 im=Image.open(T/f'decoded_{i+1:02}.png').convert('RGB');a=np.array(im,dtype=np.float32)[270:515,520:750];mse=[float(np.mean((a-r)**2)) for r in refs];got=int(np.argmin(mse));expected=max(j for j,t in enumerate(starts) if n>=t);assert got==expected,(n,got,expected)
 rows.append({'frame':n,'expected':f'd{expected+1:02}','decoded_nearest':f'd{got+1:02}','face_ROI_mse':mse});im.thumbnail((470,340));x=i%4*480+5;y=i//4*390+45;sheet.paste(im,(x,y));d.text((x,y-34),f'F{n:03} → d{got+1:02}',font=font(23),fill='#23333e')
sheet.save(P/'qa/decoded_44_77_exposure_contact.jpg',quality=95)
(P/'qa/exposure_78f_validation.json').write_text(json.dumps({'type':'isolated_native_PNG_layers_NOT_Canvas_scene','width':1280,'height':720,'fps':'24/1','frames':78,'audio_streams':0,'timeline':list(zip(starts,holds)),'decode_checks':rows,'ffmpeg_command':cmd,'last_pose':'d10','d11_present':False},ensure_ascii=False,indent=2)+'\n')
print('PASS:78f/24fps actual decoded; d08@50×8, d09@58×10, d10@68×10; no audio/no d11.')
