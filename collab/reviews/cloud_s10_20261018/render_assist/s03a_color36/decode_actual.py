#!/usr/bin/env python3
"""Package and decode the actual fixed-f17651aa 36-frame MP4, without rerendering."""
from pathlib import Path
import hashlib, json, re, shutil, subprocess
from urllib.parse import urlsplit
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SOURCE = Path('/workspace/s03a-color-render-f17651aa')
FRAMES = [0, 8, 11, 14, 17, 21, 23, 25, 28, 35]
clip = HERE / 'S03a_color36.mp4'
shutil.copy2(SOURCE / 'build/S03a_color36.mp4', clip)
probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-count_frames', '-show_streams', '-show_format', '-of', 'json', str(clip)], text=True))
(HERE / 'ffprobe.json').write_text(json.dumps(probe, indent=2) + '\n')
video = [s for s in probe['streams'] if s['codec_type'] == 'video']
assert len(video) == 1 and video[0]['nb_read_frames'] == '36'
assert (video[0]['width'], video[0]['height']) == (1280,720)
assert video[0]['avg_frame_rate'] == '24/1'
assert abs(float(probe['format']['duration']) - 1.5) < .001
assert not [s for s in probe['streams'] if s['codec_type'] == 'audio']
decoded = HERE / 'decoded_actual'; decoded.mkdir(exist_ok=True)
for f in FRAMES:
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(clip), '-vf', f'select=eq(n\\,{f})', '-frames:v', '1', str(decoded / f'F{f:03d}.png')], check=True)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
sheet = Image.new('RGB', (1600, 412), (25,25,25))
draw = ImageDraw.Draw(sheet)
for i, f in enumerate(FRAMES):
    x, y = (i % 5) * 320, (i // 5) * 206
    draw.text((x+8,y+3), f'F{f:03d} / actual MP4', font=font, fill='white')
    sheet.paste(Image.open(decoded / f'F{f:03d}.png').resize((320,180)), (x,y+26))
sheet.save(HERE / 'actual_contact.jpg', quality=96)

manifest = json.loads((HERE / 'source_manifest.json').read_text())
for item in manifest['sources']:
    assert hashlib.sha256((SOURCE/item['path']).read_bytes()).hexdigest() == item['sha256']
status = subprocess.check_output(['git','status','--porcelain'],cwd=SOURCE,text=True).strip()
assert not status
manifest['tracked_status_after'] = 'clean'
manifest['all_recorded_sources_unchanged_after'] = True
(HERE/'source_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
log = (HERE/'render.log').read_text()
responses = [(int(code), urlsplit(url).path) for code,url in re.findall(r'\[resource (\d+)\] (\S+)',log)]
assets = [i['path'] for i in manifest['sources'] if i['path'].startswith('assets/')]
success = sorted(set(path for code,path in responses if code == 200))
missing = [p for p in assets if '/'+p not in success]
assert not missing
issues = [dict(status=code,path=path) for code,path in responses if code >= 400]
asset_issues = [i for i in issues if i['path'].startswith('/assets/')]
assert not asset_issues
request_failures = [line for line in log.splitlines() if '[requestfailed]' in line]
assert not request_failures
(HERE/'resource_observations.json').write_text(json.dumps(dict(all_ten_x03a_assets_observed_HTTP200=True,expected_assets=assets,successful_resource_paths=success,HTTP_errors=issues,asset_HTTP_errors=asset_issues,request_failures=request_failures),indent=2)+'\n')
data = dict(fixed_commit=manifest['fixed_commit'],mp4=clip.name,sha256=hashlib.sha256(clip.read_bytes()).hexdigest(),bytes=clip.stat().st_size,width=1280,height=720,fps=24,total_frames=36,duration_seconds=1.5,audio_streams=0,decoded_frames=FRAMES,raw_rendered_pngs_preserved=str(SOURCE/'build/s03a_color36'),resource_asset_errors=asset_issues,new_image_calls=0)
(HERE/'actual_video_manifest.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps(data,indent=2))
