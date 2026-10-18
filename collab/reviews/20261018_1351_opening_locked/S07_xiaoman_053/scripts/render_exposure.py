"""Render the isolated Xiaoman/phone layer test, F046–107 at actual 24fps."""
from render_utils import *
import subprocess,shutil
v=[Image.open(R/p).convert('RGBA') for p in ['sources/F046_fan_down_pose_only.png','sources/F049_glance_grandma.png','approved/F053_rest_on_mat.png']]
frames=R/'review/exposure_reproduced';frames.mkdir(parents=True,exist_ok=True)
segments=[(46,49,v[0],(605,637.5,4.18)),(49,53,v[1],(605,637.5,4.18)),(53,57,v[2],(605,637.5,4.18)),(57,108,v[2],(816,482.5,1.04))]
for lo,hi,im,cam in segments:
 out=frames/f'{lo:03}.png';render(im,cam).save(out)
 for f in range(lo+1,hi):shutil.copy2(out,frames/f'{f:03}.png')
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','24','-start_number','46','-i',str(frames/'%03d.png'),'-c:v','libx264','-pix_fmt','yuv420p','-vf','pad=ceil(iw/2)*2:ceil(ih/2)*2',str(R/'review/F046_F049_F053_24fps_reproduced.mp4')],check=True)
print('Isolated layer test only; does not contain grandmother or the full production Canvas render.')
