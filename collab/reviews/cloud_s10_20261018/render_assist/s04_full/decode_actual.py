"""Decode requested S04 boundary pairs from the actual complete 72-frame MP4."""
from pathlib import Path
import subprocess,json,hashlib,shutil
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;S=Path('/workspace/s04-render-d558a91b')
video=P/'S04_drawn72.mp4';shutil.copy2(S/'build/S04_drawn72.mp4',video)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]))
(P/'ffprobe.json').write_text(json.dumps(probe,indent=2)+'\n')
v=[x for x in probe['streams'] if x['codec_type']=='video'][0]
assert int(v['nb_read_frames'])==72 and v['width']==1280 and v['height']==720
assert v['r_frame_rate']=='24/1' and float(probe['format']['duration'])==3
assert not any(x['codec_type']=='audio' for x in probe['streams'])
frames=[0,6,7,21,22,27,28,33,34,71];d=P/'decoded';d.mkdir(exist_ok=True)
selection='+'.join(f'eq(n,{f})' for f in frames)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(video),'-vf',f'select={selection.replace(",",chr(92)+",")}','-vsync','0',str(d/'selected_%02d.png')],check=True)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
contact=Image.new('RGB',(1600,408),(25,25,25));draw=ImageDraw.Draw(contact)
for i,f in enumerate(frames):
 temp=d/f'selected_{i+1:02d}.png';dest=d/f'F{f:03d}.png';temp.rename(dest);im=Image.open(dest).convert('RGB');x=(i%5)*320;y=(i//5)*204;contact.paste(im.resize((320,180)),(x,y+24));draw.text((x+8,y),f'F{f:03d} / actual MP4',font=font,fill='white')
contact.save(P/'actual_boundary_contact.jpg',quality=95)
manifest={'source_commit':'d558a91bb2af071e635afd2456f7460d74b42fc5','source_module_sha256':'6b8b32fc80de1a159e01adfca15bf2a859a55a1aa3ef3b7f4bcdba57a53009ee','video':video.name,'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'bytes':video.stat().st_size,'frames':int(v['nb_read_frames']),'fps':v['r_frame_rate'],'width':v['width'],'height':v['height'],'duration_seconds':float(probe['format']['duration']),'audio_streams':0,'actual_decoded_frames':frames,'required_pairs':[[6,7],[21,22],[27,28],[33,34]],'last_frame':71}
(P/'actual_video_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
