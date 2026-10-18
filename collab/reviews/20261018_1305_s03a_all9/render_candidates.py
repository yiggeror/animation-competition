from pathlib import Path
from PIL import Image
import json,hashlib,subprocess
R=Path(__file__).resolve().parent;O=R/'verification_replay';O.mkdir(exist_ok=True)
m=json.loads((R/'manifest.json').read_text());i=0
for q in m['frames_index']:
 p=R/q['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==q['sha256'];a=Image.open(p).convert('RGBA');bg=Image.new('RGBA',a.size,(239,239,232,255));bg.alpha_composite(a);out=Image.new('RGB',(1672,942),(239,239,232));out.paste(bg.convert('RGB'),(0,0))
 for _ in range(q['hold']):out.save(O/f'{i:03d}.png');i+=1
assert i==36
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','24','-start_number','0','-i',str(O/'%03d.png'),'-frames:v','36','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(O/'S03a_locked_candidates_ISOLATED.mp4')],check=True)
print('36 frames; all nine locked candidate hashes verified; isolated only')
