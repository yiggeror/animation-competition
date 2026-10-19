from pathlib import Path
from PIL import Image
import subprocess,sys,json,hashlib
R=Path(__file__).resolve().parent.parent;src=Path(sys.argv[1]);D=Path(sys.argv[2]);D.mkdir(parents=True,exist_ok=True);old=Image.open(R/'F046_FINAL_LOCKED/S08_F046_grandma_match_box_RGBA.png').convert('RGBA');new=Image.open(src).convert('RGBA')
for tag,bg in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 fr=D/('frames_'+tag);fr.mkdir(exist_ok=True);dec=D/('decode_'+tag);dec.mkdir(exist_ok=True)
 for i,im in enumerate([old]*3+[new]*2):Image.alpha_composite(Image.new('RGBA',im.size,bg),im).convert('RGB').save(fr/f'{i:03d}.png')
 mp=D/f'F046x3_F049x2_{tag}_5f.mp4';subprocess.run(['ffmpeg','-y','-v','error','-framerate','24','-i',str(fr/'%03d.png'),'-frames:v','5','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-an',str(mp)],check=True);subprocess.run(['ffmpeg','-y','-v','error','-i',str(mp),str(dec/'%02d.png')],check=True)
(D/'EXPOSURE_SOURCE.json').write_text(json.dumps(dict(source=str(src),sha256=hashlib.sha256(src.read_bytes()).hexdigest(),exposure='046x3 ->049x2',frames=5,fps=24,no_audio=True),indent=2))
