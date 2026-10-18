#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import subprocess,json,hashlib,shutil
import numpy as np
P=Path(__file__).resolve().parents[1];S=Path('/tmp/s07_first57_canvas_frames');D=Path('/tmp/s07_first57_decoded');D.mkdir(exist_ok=True)
mp4=P/'S07_first57_720p24.mp4';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(mp4)],text=True));v=probe['streams'][0]
assert len(probe['streams'])==1 and v['nb_frames']=='57' and v['r_frame_rate']=='24/1' and float(v['duration'])==2.375 and(v['width'],v['height'])==(1280,720)
assert sorted(x.name for x in S.glob('*.png'))==[f'{f:05}.png' for f in range(57)]
subprocess.run(['ffmpeg','-y','-v','error','-i',str(mp4),'-fps_mode','passthrough',str(D/'%05d.png')],check=True)
rows=[]
for f in range(57):
 a=np.array(Image.open(S/f'{f:05}.png').convert('RGB'),dtype=np.float32);b=np.array(Image.open(D/f'{f+1:05}.png').convert('RGB'),dtype=np.float32);mse=float(np.mean((a-b)**2));assert mse<50,(f,mse)
 rows.append({'frame':f,'Canvas_source_sha256':sha(S/f'{f:05}.png'),'encoded_vs_source_MSE':mse})
selected=[0,14,15,16,17,24,25,27,28,30,31,33,34,36,37,38,39,56]
font=lambda n:ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',n)
def sheet(frames,name):
 im=Image.new('RGB',(1920,((len(frames)+3)//4)*310),'#f2f0ea');d=ImageDraw.Draw(im)
 for i,f in enumerate(frames):
  a=Image.open(D/f'{f+1:05}.png').convert('RGB');a.thumbnail((470,265));x=i%4*480+5;y=i//4*310+38;im.paste(a,(x,y));d.text((x,y-32),f'F{f:03} 实际解码',font=font(22),fill='#23333e')
 im.save(P/name,quality=96)
sheet(selected,'00_requested_decoded_checkpoints.jpg');sheet([24,25,27,28,30,31,33,34,36,37,38,39],'01_rise_25_38_actual.jpg')
for f in selected:shutil.copyfile(D/f'{f+1:05}.png',P/f'decoded/F{f:03}.png')
result={'status':'PASS_RENDER_AND_ENCODE_ORDER','fixed_commit':'001c9c1828d9054675437111cf52df37c48721f2','type':'REAL_Canvas_SCENE_FIRST57_ONLY','module_Duration_unchanged_seconds':4.5,'render_from':0,'render_to_exclusive':2.375,'frames':57,'frame_range':[0,56],'fps':'24/1','size':[1280,720],'audio_streams':0,'frames57_107_rendered':False,'selected_decoded':selected,'mp4_sha256':sha(mp4),'all57_source_frames_match_encoded_order':True,'max_MSE':max(r['encoded_vs_source_MSE'] for r in rows),'checks':rows,'visual_review':'See README; execution pass is not full108 shot approval.'}
(P/'actual57_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');(P/'ffprobe.json').write_text(json.dumps(probe,ensure_ascii=False,indent=2)+'\n');print('PASS57f/24fps/2.375s;all57 encoded frames correspond to Canvas sources;maxMSE',result['max_MSE'])
