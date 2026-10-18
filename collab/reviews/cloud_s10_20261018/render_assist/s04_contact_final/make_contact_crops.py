from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
P=Path(__file__).resolve().parent
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',21)
out=Image.new('RGB',(1380,4*461),(22,22,22))
d=ImageDraw.Draw(out)
folder=P/'contact_crops'
folder.mkdir(exist_ok=True)
boxes=[('G soles stool',(600,480,825,625)),('X body elbow',(300,410,535,535))]
for row,f in enumerate([0,7,34,71]):
    im=Image.open(P/'decoded'/f'F{f:03d}.png').convert('RGB')
    for j,(name,b) in enumerate(boxes):
        crop=im.crop(b)
        crop.save(folder/f'F{f:03d}_{j}_native.png')
        crop=crop.resize((crop.width*3,crop.height*3))
        x=0 if j==0 else 675
        y=row*461
        out.paste(crop,(x,y+26))
        d.text((x+8,y),f'F{f:03d} {name}, actual MP4 3x',font=font,fill='white')
out.save(P/'contact_points_3x.jpg',quality=95)
(P/'contact_crops_manifest.json').write_text(json.dumps({'frames':[0,7,34,71],'boxes':boxes,'display_scale':3,'brightness_unchanged':True,'source':'actual MP4 decoded PNGs'},indent=2)+'\n')
