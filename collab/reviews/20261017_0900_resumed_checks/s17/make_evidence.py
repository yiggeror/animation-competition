from PIL import Image,ImageDraw
from pathlib import Path
import json
p=Path('/tmp/laidian-resume-s17-audit');ev=p/'evidence';d=p/'decoded';made=[]
def sheet(name,fs,box=None,scale=1,cols=6):
 ims=[]
 for f in fs:
  im=Image.open(d/f'{f:05d}.png').convert('RGB')
  if box:im=im.crop(box)
  if scale!=1:im=im.resize((int(im.width*scale),int(im.height*scale)))
  ims.append(im)
 w,h=ims[0].size;can=Image.new('RGB',(w*cols,(h+22)*((len(fs)+cols-1)//cols)),(240,240,240));dr=ImageDraw.Draw(can)
 for k,(f,im) in enumerate(zip(fs,ims)):
  x=(k%cols)*w;y=(k//cols)*(h+22);can.paste(im,(x,y+22));dr.text((x+4,y+3),f'F{f:03d}  {f/24:.3f}s',fill=(0,0,0))
 can.save(ev/name);made.append({'file':name,'frames':list(fs),'source_crop_half_open':box,'scale':scale})
sheet('overview_000_180.jpg',list(range(0,181,12)),scale=.5,cols=4)
sheet('overview_192_335.jpg',list(range(192,336,12))+[335],scale=.5,cols=4)
sheet('first_peck_120_143_native.png',list(range(120,144)),(530,295,840,485),cols=6)
sheet('first_peck_144_167_native.png',list(range(144,168)),(530,295,840,485),cols=6)
sheet('second_peck_192_215_native.png',list(range(192,216)),(545,290,840,485),cols=6)
sheet('second_peck_216_227_native.png',list(range(216,228)),(545,290,840,485),cols=6)
sheet('legs_198_221_native.png',list(range(198,222)),(375,365,515,505),cols=8)
sheet('legs_300_323_native.png',list(range(300,324)),(375,365,515,505),cols=8)
sheet('dizzy_216_300_native.png',list(range(216,301,4)),(275,260,675,505),cols=4)
sheet('turtle_walk_000_120_native.png',list(range(0,121,6)),(610,370,925,505),cols=5)
for f in [132,133,134,135,136,137,138,139,140,141,142,143,144,200,201,202,203,204,205,206,207,208,209,210]:
 Image.open(d/f'{f:05d}.png').crop((530,295,840,485)).save(ev/f'contact_f{f:03d}_native.png')
for f in [132,136,141,143,204,205,216,302,317,335]:
 (ev/f'full_f{f:03d}.png').write_bytes((d/f'{f:05d}.png').read_bytes())
(p/'evidence_manifest.json').write_text(json.dumps(made,indent=2)+'\n')
print('created',len(made),'contact sheets, native crops and full frames')
sheet('turtle_stop_108_125_native.png',list(range(108,126)),(590,375,840,485),cols=6)
for a,b in [(216,243),(244,271),(272,299)]:
 sheet(f'dizzy_full_{a}_{b}.png',list(range(a,b+1)),(245,160,720,510),scale=.65,cols=4)
sheet('return_300_335.png',list(range(300,336)),(245,160,840,510),scale=.55,cols=6)
sheet('first_near_miss_136_142_x3.png',list(range(136,143)),(590,370,690,477),scale=3,cols=4)
sheet('shell_hit_202_206_x3.png',list(range(202,207)),(645,355,740,438),scale=3,cols=5)
(p/'evidence_manifest.json').write_text(json.dumps(made,indent=2)+'\n')
