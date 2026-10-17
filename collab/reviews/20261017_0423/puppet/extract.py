import subprocess,hashlib,json
from PIL import Image, ImageDraw
from pathlib import Path
p=Path('/tmp/laidian-audit-puppet'); r=Path('/tmp/laidian-review-snapshot/renders/checkpoint2')
def board(name,fn,frames,fps,crop=None,cols=5,scale=1):
 expr='+'.join(f'eq(n\\,{f})' for f in frames)
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(r/fn),'-vf',f'select={expr}', '-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','-threads','1','-'])
 size=960*540*3; assert len(raw)==size*len(frames),(fn,len(raw),len(frames)); tiles=[]
 for i,f in enumerate(frames):
  im=Image.frombytes('RGB',(960,540),raw[i*size:(i+1)*size]); im.save(p/'evidence'/f'{name}_f{f:04}.png')
  if crop: im=im.crop(crop)
  if scale!=1: im=im.resize((round(im.width*scale),round(im.height*scale)))
  t=Image.new('RGB',(im.width,im.height+25),'white'); t.paste(im,(0,25)); ImageDraw.Draw(t).text((5,5),f'{fn}: f{f}  {f/fps:.4f}s',fill='black');tiles.append(t)
 w,h=tiles[0].size; out=Image.new('RGB',(w*cols,h*((len(tiles)+cols-1)//cols)),(170,170,170))
 for i,t in enumerate(tiles):out.paste(t,((i%cols)*w,(i//cols)*h))
 out.save(p/'evidence'/f'{name}.jpg',quality=94)
board('s17_p1','s17_fix_preview.mp4',list(range(131,150)),24,(420,130,810,410),cols=5)
board('s17_p2','s17_fix_preview.mp4',list(range(196,212)),24,(420,130,810,450),cols=4)
board('s17_legs','s17_fix_preview.mp4',list(range(206,216))+list(range(300,320,2)),24,(380,240,700,455),cols=5)
board('s27_key','s27_fix_preview.mp4',[0,3,4,6,8,12,13,24,59,60,72,84,96,108,119],24,None,cols=3,scale=.5)
board('old_boundary','film_preview_v1.mp4',[1992,2004,2013,2014,2015,2016,2017,2018,2019,2020,2022,2023],12,None,cols=3,scale=.5)
board('s25_key','s25_dog_preview.mp4',[0,12,24,36,48,60,72,96,120,143],24,None,cols=5,scale=.5)
print('saved all boards')
