#!/usr/bin/env python3
"""26 actual drawing exposures only. No scene compositor, lighting or audio."""
from pathlib import Path
import tempfile,subprocess,json
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
sheet=[(0,8,'locked/F000_registered_locked.png'),(8,6,'candidates/d02_registered.png'),(14,4,'candidates/d03_registered.png'),(18,8,'candidates/d04_registered.png')]
out=ROOT/'qa/S09_F000-F025_drawings_only.mp4'
with tempfile.TemporaryDirectory(prefix='s09-switch-',dir='/tmp') as tmp:
    tmp=Path(tmp);idx=0
    for f,hold,path in sheet:
        im=Image.open(ROOT/path).crop((280,80,1304,656)).resize((1280,720),Image.Resampling.LANCZOS)
        bg=Image.new('RGBA',im.size,(228,233,237,255));bg.alpha_composite(im)
        for _ in range(hold):bg.convert('RGB').save(tmp/f'{idx:03}.png');idx+=1
    assert idx==26
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','24','-i',str(tmp/'%03d.png'),'-frames:v','26','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',str(out)],check=True)
    decoded=tmp/'decoded';decoded.mkdir()
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(out),'-frames:v','26',str(decoded/'%03d.png')],check=True)
    assert len(list(decoded.glob('*.png')))==26
    keys=[0,8,14,18,25];mosaic=Image.new('RGB',(1280,720),(235,238,240))
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
    for i,key in enumerate(keys):
        im=Image.open(decoded/f'{key+1:03}.png').resize((426,240));d=ImageDraw.Draw(im);d.text((12,10),f'ACTUAL DECODE F{key:03}',font=font,fill=(30,30,30));mosaic.paste(im,((i%3)*426,(i//3)*240))
    mosaic.save(ROOT/'qa/actual_encoded_frames.png')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_type,width,height,r_frame_rate,nb_frames,duration','-of','json',str(out)],text=True))
v=probe['streams'][0];assert v['width']==1280 and v['height']==720 and v['r_frame_rate']=='24/1' and int(v['nb_frames'])==26
assert len(probe['streams'])==1 and v['codec_type']=='video'
(ROOT/'qa/preview_probe.json').write_text(json.dumps(probe,indent=2)+'\n')
(ROOT/'exposure_segment.json').write_text(json.dumps({'shot':'S09','scope':'F000-F025 drawing layer only; not complete scene','fps':24,'frames':26,'crop_registered':[280,80,1304,656],'sheet':[{'f':f,'hold':hold,'file':path} for f,hold,path in sheet],'audio':False},ensure_ascii=False,indent=2)+'\n')
print('actual encoded and decoded: 26f,1280x720,24fps,no audio')
