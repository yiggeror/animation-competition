from pathlib import Path
from PIL import Image
import subprocess
R=Path(__file__).resolve().parent.parent;D=R/'F046_old_air_semantic_candidate/qa';old=Image.open(R/'F043_FINAL_LOCKED/S08_F043_grandma_match_box_RGBA.png').convert('RGBA');new=Image.open(R/'F046_FINAL_LOCKED/S08_F046_grandma_match_box_RGBA.png').convert('RGBA')
for tag,bg in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 fr=D/('frames_'+tag);fr.mkdir(exist_ok=True);dec=D/('decode_'+tag);dec.mkdir(exist_ok=True)
 for i,im in enumerate([old]*3+[new]*3):Image.alpha_composite(Image.new('RGBA',im.size,bg),im).convert('RGB').save(fr/f'{i:03d}.png')
 mp=D/f'F043x3_F046x3_FINAL_{tag}_6f.mp4';subprocess.run(['ffmpeg','-y','-v','error','-framerate','24','-i',str(fr/'%03d.png'),'-frames:v','6','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-an',str(mp)],check=True);subprocess.run(['ffmpeg','-y','-v','error','-i',str(mp),str(dec/'%02d.png')],check=True)
