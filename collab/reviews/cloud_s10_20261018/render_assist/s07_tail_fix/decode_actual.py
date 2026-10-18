"""Decode requested absolute S07 frames from actual fixed-commit 18-frame MP4."""
from pathlib import Path
import json,hashlib,subprocess,shutil
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent
S=Path('/workspace/s07-tail-render-2f6ae68e')
video=P/'S07_tail18.mp4';shutil.copy2(S/'build/S07_tail18.mp4',video)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]))
(P/'ffprobe.json').write_text(json.dumps(probe,indent=2)+'\n')
v=[x for x in probe['streams'] if x['codec_type']=='video'][0]
assert int(v['nb_read_frames'])==18 and v['width']==1280 and v['height']==720
assert v['r_frame_rate']=='24/1' and float(probe['format']['duration'])==.75
assert not any(x['codec_type']=='audio' for x in probe['streams'])
absolute=[39,43,46,49,53];local=[x-39 for x in absolute]
d=P/'decoded';d.mkdir(exist_ok=True);c=P/'phone_hair_crops';c.mkdir(exist_ok=True)
selection='+'.join(f'eq(n,{f})' for f in local)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(video),'-vf',f'select={selection.replace(",",chr(92)+",")}','-vsync','0',str(d/'selected_%02d.png')],check=True)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
contact=Image.new('RGB',(1280,2*264),(25,25,25));dc=ImageDraw.Draw(contact)
detail=Image.new('RGB',(1020,3*444),(30,30,30));dd=ImageDraw.Draw(detail)
crop=[720,345,890,485]
for i,f in enumerate(absolute):
 temp=d/f'selected_{i+1:02d}.png';dest=d/f'F{f:03d}.png';temp.rename(dest);im=Image.open(dest).convert('RGB')
 x=(i%3)*426;y=(i//3)*264;contact.paste(im.resize((426,240)),(x,y+24));dc.text((x+8,y),f'F{f:03d} / MP4 n={f-39}',font=font,fill='white')
 native=im.crop(crop);native.save(c/f'F{f:03d}_native.png');x=(i%2)*510;y=(i//2)*444;detail.paste(native.resize((510,420)),(x,y+24));dd.text((x+8,y),f'F{f:03d} / actual decode, 3x',font=font,fill='white')
contact.save(P/'actual_contact.jpg',quality=95);detail.save(P/'phone_hair_contact_3x.jpg',quality=95)
manifest={'fixed_source_commit':'2f6ae68e1e2e959e25972d8785721435d51f87e9','video':video.name,'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'bytes':video.stat().st_size,'frames':int(v['nb_read_frames']),'fps':v['r_frame_rate'],'width':v['width'],'height':v['height'],'duration_seconds':float(probe['format']['duration']),'audio_streams':0,'absolute_frame_range_inclusive':[39,56],'actual_decoded_frames':[{'absolute':a,'local_video_index':b,'file':f'decoded/F{a:03d}.png'} for a,b in zip(absolute,local)],'detail_crop':crop,'detail_scale_display_only':3,'old_first25_not_rendered':True,'whole_S07_ready':False}
(P/'actual_video_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
