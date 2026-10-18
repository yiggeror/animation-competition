#!/usr/bin/env python3
"""Decode the actual Canvas MP4 and compare all120 frames with renderer PNGs."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib, json, shutil, subprocess
import numpy as np

P=Path(__file__).resolve().parents[1]
T=Path('/tmp/s13_full_scene_frames')
D=Path('/tmp/s13_full_scene_decoded');D.mkdir(exist_ok=True)
mp4=P/'S13_drawn_120f_720p24.mp4'
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(mp4)],text=True))
assert len(probe['streams'])==1
s=probe['streams'][0]
assert s['codec_name']=='h264' and s['nb_frames']=='120' and s['r_frame_rate']==s['avg_frame_rate']=='24/1'
assert (s['width'],s['height'])==(1280,720) and float(s['duration'])==5
subprocess.run(['ffmpeg','-y','-v','error','-i',str(mp4),'-fps_mode','passthrough',str(D/'%05d.png')],check=True)
manifest=json.loads((P/'qa/scene_source_manifest.json').read_text())
starts=[r['start'] for r in manifest['source_drawings']]
assert starts==[0,18,24,30,36,40,44,50,58,68,78,84,87,90,94,100]
def roi(im):
    a=np.array(im.convert('RGB').crop((240,20,820,715)).resize((200,240)),dtype=np.float32)
    return (a-a.mean(axis=(0,1),keepdims=True))/(a.std(axis=(0,1),keepdims=True)+1e-6)
refs=[roi(Image.open(T/f'{f:05}.png')) for f in starts]
rows=[];source_hashes=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for f in range(120):
    src=T/f'{f:05}.png';enc=D/f'{f+1:05}.png'
    a=np.array(Image.open(src).convert('RGB'),dtype=np.float32)
    b=np.array(Image.open(enc).convert('RGB'),dtype=np.float32)
    mse=float(np.mean((a-b)**2));assert mse<40,(f,mse)
    expected=max(i for i,k in enumerate(starts) if f>=k)
    r=roi(Image.open(enc));errors=[float(np.mean((r-ref)**2)) for ref in refs]
    nearest=int(np.argmin(errors));assert nearest==expected,(f,nearest+1,expected+1,errors)
    rows.append({'frame':f,'expected':f'd{expected+1:02}','decoded_nearest':f'd{nearest+1:02}','source_vs_encoded_MSE':mse,'normalized_ROI_errors':errors})
    source_hashes.append({'frame':f,'sha256':sha(src)})
font=lambda n:ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',n)
def sheet(frames,cols,out):
    w=480;h=310;im=Image.new('RGB',(cols*w,((len(frames)+cols-1)//cols)*h),'#f5f3ed');d=ImageDraw.Draw(im)
    for i,f in enumerate(frames):
        a=Image.open(D/f'{f+1:05}.png').convert('RGB');a.thumbnail((470,265));x=i%cols*w+5;y=i//cols*h+38;im.paste(a,(x,y))
        d.text((x,y-32),f'F{f:03}  {rows[f]["expected"]}',font=font(22),fill='#23333e')
    im.save(P/'qa'/out,quality=96)
sheet(starts,4,'00_all16_decoded_scene.jpg')
sheet([77,78,83,84,86,87,89,90,93,94,99,100,101,110,118,119],4,'01_closure_turn_settle_boundaries_decoded.jpg')
sheet([90,94,99,100,119],3,'02_tail_timing_decoded.jpg')
for f in [0,84,87,90,94,99,100,119]:
    shutil.copyfile(D/f'{f+1:05}.png',P/f'qa/F{f:03}_decoded_scene.png')
result={'type':'REAL_CHROMIUM_CANVAS_SCENE_NOT_ISOLATED_PNG_PREVIEW','status':'PASS','mp4_sha256':sha(mp4),'frames':120,'fps':'24/1','duration_seconds':5,'width':1280,'height':720,'audio_streams':0,'all120_decoded_frames_match_rendered_source_order':True,'all120_decoded_nearest_pose_matches_exposure':True,'max_source_vs_encoded_MSE':max(r['source_vs_encoded_MSE'] for r in rows),'timeline':[(r['drawing'],r['start'],r['hold']) for r in manifest['source_drawings']],'checks':rows,'notes':'Actual shared renderPaint scene lighting/background/crane. F084–086 closure before F087 turn;F100–119 tail settled drawing. Audio not added or validated.'}
(P/'qa/actual_120f_scene_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(P/'qa/rendered_120_source_frame_hashes.json').write_text(json.dumps(source_hashes,indent=2)+'\n')
(P/'qa/ffprobe.json').write_text(json.dumps(probe,ensure_ascii=False,indent=2)+'\n')
print('PASS actual Canvas scene:120/24fps/5s/1280×720;all120 decoded-source matches and16-state classifications;max MSE',result['max_source_vs_encoded_MSE'])
