from pathlib import Path
import subprocess,json,hashlib,shutil,math
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;cfg=json.loads((P/'request_scope.json').read_text());S=Path(cfg['source_worktree'])
video=P/cfg['delivery_video'];shutil.copy2(S/cfg['build_video'],video)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]));(P/'ffprobe.json').write_text(json.dumps(probe,indent=2)+'\n')
v=[x for x in probe['streams'] if x['codec_type']=='video'][0]
assert int(v['nb_read_frames'])==cfg['frame_count'] and v['width']==1280 and v['height']==720 and v['r_frame_rate']=='24/1'
assert float(probe['format']['duration'])==cfg['duration_seconds'] and not any(x['codec_type']=='audio' for x in probe['streams'])
frames=cfg['decode_frames'];d=P/'decoded';d.mkdir(exist_ok=True);selection='+'.join(f'eq(n,{f})' for f in frames)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(video),'-vf','select='+selection.replace(',',chr(92)+','),'-vsync','0',str(d/'selected_%02d.png')],check=True)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20);cols=4;contact=Image.new('RGB',(1280,math.ceil(len(frames)/cols)*204),(25,25,25));draw=ImageDraw.Draw(contact)
for i,f in enumerate(frames):
 temp=d/f'selected_{i+1:02d}.png';dest=d/f'F{f:03d}.png';temp.rename(dest);im=Image.open(dest).convert('RGB');x=(i%cols)*320;y=(i//cols)*204;contact.paste(im.resize((320,180)),(x,y+24));draw.text((x+8,y),f'F{f:03d} / actual MP4',font=font,fill='white')
contact.save(P/'actual_contact.jpg',quality=95)
manifest={'source_commit':cfg['fixed_source_commit'],'module':cfg['module'],'video':video.name,'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'bytes':video.stat().st_size,'frames':int(v['nb_read_frames']),'fps':v['r_frame_rate'],'width':v['width'],'height':v['height'],'duration_seconds':float(probe['format']['duration']),'audio_streams':0,'actual_decoded_frames':frames,'new_contact_version':True,'old_render_substituted':False}
(P/'actual_video_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
