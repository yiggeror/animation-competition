from pathlib import Path
import subprocess
from PIL import Image,ImageDraw
p=Path('/tmp/laidian-audit-s20-laterality')
def board(name,fn,frames,cols=4):
 expr='+'.join(f'eq(n\\,{f})' for f in frames)
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(p/fn),'-vf',f'select={expr}','-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','-threads','1','-'])
 sz=960*540*3;assert len(raw)==sz*len(frames)
 tiles=[]
 for i,f in enumerate(frames):
  im=Image.frombytes('RGB',(960,540),raw[i*sz:(i+1)*sz]);im.save(p/'evidence'/f'{name}_f{f:03}.png');im=im.resize((480,270));t=Image.new('RGB',(480,294),'white');t.paste(im,(0,24));ImageDraw.Draw(t).text((5,5),f'{name} f{f} | {f/12:.4f}s',fill='black');tiles.append(t)
 out=Image.new('RGB',(480*cols,294*((len(tiles)+cols-1)//cols)),(180,180,180))
 for i,t in enumerate(tiles):out.paste(t,((i%cols)*480,(i//cols)*294))
 out.save(p/'evidence'/f'{name}_board.jpg',quality=95)
board('s20','s20_backstage_preview.mp4',[0,12,36,60,71,72,78,96,107],3)
board('s12','s12_box_preview.mp4',[0,6,12,18,24,30,36,42,48,60,72,84,95],4)
