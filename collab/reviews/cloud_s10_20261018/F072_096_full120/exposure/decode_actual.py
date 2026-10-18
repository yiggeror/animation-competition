"""Decode actual complete S10 MP4, count frames, and label absolute exposure frames."""
from pathlib import Path
import subprocess,json,hashlib
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent
video=P/'S10_full120_scene.mp4'
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]))
(P/'ffprobe.json').write_text(json.dumps(probe,indent=2)+'\n')
v=[s for s in probe['streams'] if s['codec_type']=='video'][0]
assert int(v['nb_read_frames'])==120 and v['width']==1280 and v['height']==720
assert v['r_frame_rate']=='24/1' and float(probe['format']['duration'])==5
assert not any(s['codec_type']=='audio' for s in probe['streams'])
frames=[0,21,22,23,24,26,27,29,30,32,33,44,45,71,72,83,95,96,108,119]
d=P/'decoded';d.mkdir(exist_ok=True)
selection='+'.join(f'eq(n,{f})' for f in frames)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(video),'-vf',f'select={selection.replace(",",chr(92)+",")}','-vsync','0',str(d/'selected_%02d.png')],check=True)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
contact=Image.new('RGB',(1280,5*204),(25,25,25));draw=ImageDraw.Draw(contact)
for i,f in enumerate(frames):
 temp=d/f'selected_{i+1:02d}.png';dest=d/f'F{f:03d}.png';temp.rename(dest)
 image=Image.open(dest).convert('RGB');image.thumbnail((320,180))
 x=(i%4)*320;y=(i//4)*204;contact.paste(image,(x,y+24));draw.text((x+6,y),f'F{f:03d} / actual MP4',font=font,fill='white')
contact.save(P/'actual_full_scene_contact.jpg',quality=95)
sources=json.loads((P.parent/'provenance/adopted_sources.json').read_text())['sources']
manifest={'video':video.name,'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'bytes':video.stat().st_size,'duration_seconds':float(probe['format']['duration']),'frames':int(v['nb_read_frames']),'fps':v['r_frame_rate'],'width':v['width'],'height':v['height'],'audio_streams':0,'absolute_frame_range':[0,119],'actual_decoded_frames':frames,'drawings':{x['id']:[x['start_frame'],x['end_frame_inclusive']] for x in sources},'module':'../S10_drawn_full_candidate.js','module_sha256':hashlib.sha256((P.parent/'S10_drawn_full_candidate.js').read_bytes()).hexdigest(),'source_images_sha256':{x['id']:x['sha256'] for x in sources}}
(P/'actual_video_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
