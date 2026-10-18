#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, re, shutil, subprocess
from PIL import Image, ImageDraw, ImageFont

HERE=Path(__file__).resolve().parent
SOURCE=Path('/workspace/semantic-color-render-ac8a7d81')
NAME='S10_semantic120'
COUNT=120
SECONDS=5.0
FRAMES=[0,24,27,30,33,45,72,96,119]
clip=HERE/(NAME+'.mp4')
shutil.copy2(SOURCE/'build'/clip.name,clip)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(clip)],text=True))
(HERE/'ffprobe.json').write_text(json.dumps(probe,indent=2)+'\n')
video=[s for s in probe['streams'] if s['codec_type']=='video']; audio=[s for s in probe['streams'] if s['codec_type']=='audio']
assert len(video)==1 and int(video[0]['nb_read_frames'])==COUNT
assert (video[0]['width'],video[0]['height'],video[0]['avg_frame_rate'])==(1280,720,'24/1')
assert abs(float(probe['format']['duration'])-SECONDS)<.001 and not audio
decoded=HERE/'decoded_actual'; decoded.mkdir(exist_ok=True)
for f in FRAMES:
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(clip),'-vf',f'select=eq(n\\,{f})','-frames:v','1',str(decoded/f'F{f:03d}.png')],check=True)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
sheet=Image.new('RGB',(1600,206*((len(FRAMES)+4)//5)),(25,25,25)); draw=ImageDraw.Draw(sheet)
for i,f in enumerate(FRAMES):
    x,y=(i%5)*320,(i//5)*206
    draw.text((x+8,y+3),f'F{f:03d} / actual MP4',font=font,fill='white')
    sheet.paste(Image.open(decoded/f'F{f:03d}.png').resize((320,180)),(x,y+26))
sheet.save(HERE/'actual_contact.jpg',quality=96)
manifest=json.loads((HERE/'source_manifest.json').read_text())
for item in manifest['sources']:
    assert hashlib.sha256((SOURCE/item['path']).read_bytes()).hexdigest()==item['sha256']
assert not subprocess.check_output(['git','status','--porcelain'],cwd=SOURCE,text=True).strip()
manifest.update(tracked_status_after='clean',all_recorded_sources_unchanged_after=True)
(HERE/'source_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
responses=[json.loads(line.split('[server-response] ',1)[1]) for line in (HERE/'render.log').read_text().splitlines() if line.startswith('[server-response] ')]
good=sorted(set(r['path'].split('?')[0] for r in responses if r['status']==200))
missing=[p for p in manifest['expected_asset_requests'] if '/'+p not in good]; assert not missing
errors=[r for r in responses if r['status']>=400]; asset_errors=[r for r in errors if r['path'].startswith('/assets/')]; assert not asset_errors
(HERE/'resource_observations.json').write_text(json.dumps(dict(server_responses=responses,all_expected_drawings_HTTP200=True,expected_asset_count=len(manifest['expected_asset_requests']),successful_paths=good,HTTP_errors=errors,asset_HTTP_errors=asset_errors),indent=2)+'\n')
raw=sorted((SOURCE/'build'/NAME.lower()).glob('*.png')); assert len(raw)==COUNT
(HERE/'raw_frame_SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in raw))
data=dict(fixed_commit=manifest['fixed_commit'],mp4=clip.name,sha256=hashlib.sha256(clip.read_bytes()).hexdigest(),bytes=clip.stat().st_size,width=1280,height=720,fps=24,total_frames=COUNT,duration_seconds=SECONDS,audio_streams=0,decoded_frames=FRAMES,raw_rendered_pngs_preserved=str(raw[0].parent),asset_HTTP_errors=asset_errors,new_image_calls=0)
(HERE/'actual_video_manifest.json').write_text(json.dumps(data,indent=2)+'\n'); print(json.dumps(data,indent=2))
