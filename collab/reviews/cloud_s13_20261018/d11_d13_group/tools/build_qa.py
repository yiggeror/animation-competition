#!/usr/bin/env python3
"""Native PNG layer exposure through d13; no Canvas scene or audio."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,subprocess,shutil,numpy as np
P=Path(__file__).resolve().parents[1];R=P.parent;T=Path('/tmp/s13_d11_d13_qa');T.mkdir(exist_ok=True)
files=['d01_first_candidate/candidates/S13_d01_uniform_registered_rgba.png','d02_d04_segment/approved_local/F018_d02_eyes_up.png',
'd02_d04_segment/approved_local/F024_d03_whole_head_right.png','d02_d04_segment/approved_local/F030_d04_awake_closed_mouth.png',
'd05_d07_segment/approved_local/F036_d05_pretend_drowsy.png','d05_d07_segment/approved_local/F040_d06_yawn_start.png',
'd05_d07_segment/approved_local/F044_d07_yawn_opening.png','d08_d10_group/approved_local/F050_d08_yawn_peak.png',
'd08_d10_group/approved_local/F058_d09_sustained_breath.png','d08_d10_group/approved_local/F068_d10_yawn_release.png','d11_d13_group/approved_local/F078_d11_near_closed.png','d11_d13_group/approved_local/F084_d12_closed_before_turn.png','d11_d13_group/approved_local/F087_d13_whole_head_turn_start.png']
sources=[R/x for x in files];starts=[0,18,24,30,36,40,44,50,58,68,78,84,87];holds=[18,6,6,6,4,4,6,8,10,10,6,3,3]
font=lambda n:ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',n)
def comp(im,c=(245,245,245,255)):
 b=Image.new('RGBA',im.size,c);b.alpha_composite(im);return b.convert('RGB')
sheet=Image.new('RGB',(1920,820),'#f5f3ed');d=ImageDraw.Draw(sheet);close=Image.new('RGB',(1920,840),'#f5f3ed');cd=ImageDraw.Draw(close)
labels=['d10 已锁收束','d11 F078×6 闭口过程','d12 F084×3 闭口完成','d13 F087×3 整头首转']
for i,path in enumerate(sources[9:]):
 im=Image.open(path).convert('RGBA');a=comp(im).crop((90,20,940,1190));a.thumbnail((465,650));sheet.paste(a,(i*480+8,70));d.text((i*480+12,20),labels[i],font=font(22),fill='#23333e')
 a=comp(im).crop((510,500,930,1080));a.thumbnail((465,650));close.paste(a,(i*480+8,70));cd.text((i*480+12,20),labels[i],font=font(22),fill='#23333e')
d.text((20,750),'同画布/裁切/缩放；F084先明确闭口并保持头向，F087才整头首转。',font=font(25),fill='#23333e')
cd.text((20,755),'嘴将合 → 完全闭合但不转头 → 闭口整头首转；颅耳发根和颈面同行。',font=font(24),fill='#23333e')
sheet.save(P/'qa/00_d10_d13_same_scale_actual.jpg',quality=96);close.save(P/'qa/01_closure_before_turn_actual.jpg',quality=97)
sheet=Image.new('RGB',(1536,1900),'#f5f3ed');d=ImageDraw.Draw(sheet)
for row,path in enumerate(sources[10:]):
 for col,c in enumerate([(245,245,245,255),(38,44,53,255),(160,175,180,255)]):
  a=comp(Image.open(path).convert('RGBA'),c);a.thumbnail((500,570));sheet.paste(a,(col*512,row*620+45))
 d.text((20,row*620+10),labels[row+1],font=font(23),fill='#23333e')
sheet.save(P/'qa/all_three_on_three_backgrounds.jpg',quality=95)
for i,path in enumerate(sources):
 sc=.85*2/3;im=Image.open(path).convert('RGBA');layer=im.transform((1280,720),Image.Transform.AFFINE,(1/sc,0,-220/sc,0,1/sc,20/sc),Image.Resampling.BICUBIC)
 a=comp(layer,(211,214,213,255));ImageDraw.Draw(a).text((20,12),'S13 0–89f 实际画层 / 中性底 / 非Canvas接景 / 无音频',font=font(19),fill='#3c4448');a.save(T/f'd{i+1:02}.png')
for n in range(90):shutil.copyfile(T/f'd{max(i for i,t in enumerate(starts) if n>=t)+1:02}.png',T/f'frame_{n:03}.png')
mp4=P/'qa/isolated_90f_through_d13.mp4';cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-framerate','24','-i',str(T/'frame_%03d.png'),'-frames:v','90','-fps_mode','cfr','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-an',str(mp4)]
subprocess.run(cmd,check=True);probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(mp4)],text=True));s=probe['streams'][0]
assert len(probe['streams'])==1 and s['nb_frames']=='90' and s['r_frame_rate']=='24/1' and s['width']==1280 and s['height']==720
frames=[68,77,78,83,84,86,87,89];sel='+'.join(f'eq(n,{n})' for n in frames)
subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(mp4),'-vf',f"select='{sel}'",'-fps_mode','vfr',str(T/'decoded_%02d.png')],check=True)
refs=[np.array(Image.open(T/f'd{i+1:02}.png').convert('RGB'),dtype=np.float32)[270:515,520:750] for i in range(13)];rows=[];sheet=Image.new('RGB',(1920,820),'#f5f3ed');d=ImageDraw.Draw(sheet)
for i,n in enumerate(frames):
 im=Image.open(T/f'decoded_{i+1:02}.png').convert('RGB');a=np.array(im,dtype=np.float32)[270:515,520:750];mse=[float(np.mean((a-r)**2)) for r in refs];got=int(np.argmin(mse));expected=max(j for j,t in enumerate(starts) if n>=t);assert got==expected,(n,got,expected)
 rows.append({'frame':n,'expected':f'd{expected+1:02}','decoded_nearest':f'd{got+1:02}','face_ROI_mse':mse});im.thumbnail((470,340));x=i%4*480+5;y=i//4*390+45;sheet.paste(im,(x,y));d.text((x,y-34),f'F{n:03} → d{got+1:02}',font=font(23),fill='#23333e')
sheet.save(P/'qa/decoded_68_89_exposure_contact.jpg',quality=95)
(P/'qa/exposure_90f_validation.json').write_text(json.dumps({'type':'isolated_native_PNG_layers_NOT_Canvas_scene','width':1280,'height':720,'fps':'24/1','frames':90,'audio_streams':0,'timeline':list(zip(starts,holds)),'decode_checks':rows,'ffmpeg_command':cmd,'last_pose':'d13','d14_present':False},ensure_ascii=False,indent=2)+'\n')
print('PASS:90f/24fps actual decoded; F084–086 closed before F087 turn; no audio/no d14.')
