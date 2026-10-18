"""Decode all G/X exposure boundaries from actual fixed S01 84-frame video."""
from pathlib import Path
import json,re,subprocess,hashlib,shutil,math
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;S=Path('/workspace/s01-render-ab3644e0')
video=P/'S01_full84.mp4';shutil.copy2(S/'build/S01_full84.mp4',video)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]))
(P/'ffprobe.json').write_text(json.dumps(probe,indent=2)+'\n')
v=[x for x in probe['streams'] if x['codec_type']=='video'][0]
assert int(v['nb_read_frames'])==84 and v['width']==1280 and v['height']==720
assert v['r_frame_rate']=='24/1' and float(probe['format']['duration'])==3.5
assert not any(x['codec_type']=='audio' for x in probe['streams'])
timeline=(P/'source_timeline_readonly.txt').read_text()
sheets={role:json.loads(re.search(role+r'_SHEET = Object.freeze\((\[\[.*?\]\])\.map',timeline).group(1)) for role in ['G','X']}
keys=sorted(set(k for sheet in sheets.values() for k,_ in sheet));frames=sorted(set([0,83]+[j for k in keys if k>0 for j in [k-1,k]]))
assert set(range(28,36)).issubset(frames)
d=P/'decoded';d.mkdir(exist_ok=True)
selection='+'.join(f'eq(n,{f})' for f in frames)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(video),'-vf',f'select={selection.replace(",",chr(92)+",")}','-vsync','0',str(d/'selected_%02d.png')],check=True)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
contact=Image.new('RGB',(1600,math.ceil(len(frames)/5)*204),(25,25,25));dc=ImageDraw.Draw(contact)
for i,f in enumerate(frames):
 temp=d/f'selected_{i+1:02d}.png';dest=d/f'F{f:03d}.png';temp.rename(dest);im=Image.open(dest).convert('RGB');x=(i%5)*320;y=(i//5)*204;contact.paste(im.resize((320,180)),(x,y+24));dc.text((x+8,y),f'F{f:03d} / actual MP4',font=font,fill='white')
contact.save(P/'all_boundaries_contact.jpg',quality=95)
manifest={'source_commit':'ab3644e096c0f9d94b5053f7c136ef515107e4b8','video':video.name,'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'bytes':video.stat().st_size,'frames':int(v['nb_read_frames']),'fps':v['r_frame_rate'],'width':v['width'],'height':v['height'],'duration_seconds':float(probe['format']['duration']),'audio_streams':0,'absolute_frame_range_inclusive':[0,83],'all_change_boundaries':keys,'actual_decoded_frames':frames,'source_exposure_sheets':sheets,'all_change_boundaries_have_before_and_after':True,'full_scene_signoff':'Astra pending; cloud records actual observations only'}
(P/'actual_video_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
