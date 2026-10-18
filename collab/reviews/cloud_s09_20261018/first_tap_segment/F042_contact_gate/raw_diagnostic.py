from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
ims=[('target preposition',R/'reference/F042_hand_torch_contact_PREPOSITION_NOT_ART.png'),('actual native raw',R/'originals/F042_call01_raw.png')]
s=Image.new('RGB',(1680,620),(235,241,245));d=ImageDraw.Draw(s)
for i,(title,p) in enumerate(ims):
 im=Image.open(p).convert('RGBA');bg=Image.new('RGBA',im.size,(213,224,231,255));bg.alpha_composite(im)
 q=bg.crop((650,480,1210,870)).convert('RGB').resize((840,585));qd=ImageDraw.Draw(q)
 for x in range(650,1211,25):
  xx=(x-650)*1.5;qd.line((xx,0,xx,585),fill='#7e9eac');qd.text((xx+1,0),str(x),font=font,fill='#234758')
 for y in range(480,871,25):
  yy=(y-480)*1.5;qd.line((0,yy,840,yy),fill='#7e9eac');qd.text((0,yy+1),str(y),font=font,fill='#234758')
 s.paste(q,(i*840,35));d.text((i*840+5,5),title,font=font,fill='#234758')
s.save(R/'qa/raw_target_wrist_and_cuff_grid.png')
