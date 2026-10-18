from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
P=Path(__file__).resolve().parent
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',21)
frames=[0,10,20,35,43,83]
boxes=[('G soles stool',(595,475,825,625)),('X body elbow legs',(295,405,540,540))]
out=Image.new('RGB',(1425,len(frames)*476),(22,22,22));d=ImageDraw.Draw(out)
folder=P/'contact_crops';folder.mkdir(exist_ok=True)
for row,f in enumerate(frames):
    im=Image.open(P/'decoded'/f'F{f:03d}.png').convert('RGB')
    for j,(name,b) in enumerate(boxes):
        crop=im.crop(b);crop.save(folder/f'F{f:03d}_{j}_native.png')
        crop=crop.resize((crop.width*3,crop.height*3))
        x=0 if j==0 else 690
        y=row*476
        out.paste(crop,(x,y+26))
        d.text((x+8,y),f'F{f:03d} {name}, actual MP4 3x',font=font,fill='white')
out.save(P/'contact_switch_3x.jpg',quality=95)
(P/'contact_crops_manifest.json').write_text(json.dumps({'frames':frames,'boxes':boxes,'display_scale':3,'brightness_unchanged':True,'source':'actual new-contact MP4 decoded PNGs'},indent=2)+'\n')
