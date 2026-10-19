"""Reuse checked first58 Canvas, add exactly3 actual Canvas, encode and decode once."""
from pathlib import Path
import hashlib,json,shutil,subprocess
R=Path('.');O=R/'collab/reviews/cloud_s13_20261018/render_assist/s08_first64';B=R/'build/S08_first64';D=R/'build/S08_first64_decoded';N=R/'build/S08_first64_increment';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not B.exists() and not D.exists(),'Do not repeat assembly/encoding blindly.'
assert sorted(x.name for x in N.iterdir())==['00061.png','00062.png','00063.png']
B.mkdir();D.mkdir()
for row in json.loads((O/'reused61_baseline.json').read_text())['rows']:
 p=Path(row['source_cache']);q=B/f"{row['frame']:05d}.png";assert sha(p)==row['source_PNG_SHA256'];shutil.copyfile(p,q);assert p.read_bytes()==q.read_bytes()
for f in range(61,64):
 p=N/f'{f:05d}.png';q=B/p.name;shutil.copyfile(p,q);shutil.copyfile(p,O/f'canvas_new/F{f:03d}.png');assert p.read_bytes()==q.read_bytes()==(O/f'canvas_new/F{f:03d}.png').read_bytes()
(O/'canvas_new/SHA256SUMS.txt').write_text(''.join(f'{sha(O/f"canvas_new/F{f:03d}.png")}  F{f:03d}.png\n' for f in range(61,64)))
mp4=O/'S08_first64_1920x1080_24fps.mp4';assert not mp4.exists()
encode=['ffmpeg','-y','-loglevel','error','-framerate','24','-start_number','0','-i',str(B/'%05d.png'),'-frames:v','64','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-tune','animation','-an',str(mp4)]
with (O/'encode.log').open('w') as log:subprocess.run(encode,check=True,stdout=log,stderr=subprocess.STDOUT)
probe=subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(mp4)]);(O/'ffprobe.json').write_bytes(probe)
decode=['ffmpeg','-y','-loglevel','error','-i',str(mp4),'-vsync','0','-start_number','0',str(D/'%05d.png')]
with (O/'decode.log').open('w') as log:subprocess.run(decode,check=True,stdout=log,stderr=subprocess.STDOUT)
(O/'assembly_commands.json').write_text(json.dumps({'render_runs':1,'rendered_only':[61,62,63],'old_Canvas_reused_without_render':61,'encoding_runs':1,'encode':encode,'decode':decode,'source_S08_first61_commit':'a2938aba7d367c957188799c1beccc339949cea8'},indent=2)+'\n')
print(json.dumps({'MP4_SHA256':sha(mp4),'assembled_Canvas_count':len(list(B.glob('*.png'))),'decoded_frames':len(list(D.glob('*.png'))),'new_Canvas_SHA256':{f:sha(N/f'{f:05d}.png') for f in range(61,64)}},indent=2))
