from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib
p=Path('/tmp/laidian-s01-rigs/audit_motion'); frames=p/'frames'
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
ids=[0,7,16,22,29,45,58,66,74,83,116,143]
out=Image.new('RGB',(1200,3*524),(240,240,240))
for i,n in enumerate(ids):
 im=Image.open(frames/f'{n:05d}.png').resize((300,500))
 x=(i%4)*300;y=(i//4)*524;out.paste(im,(x,y+24));ImageDraw.Draw(out).text((x+5,y+3),f'F{n:03d} / {n/24:.3f}s',font=font,fill='black')
out.save(p/'full_contact_12.jpg',quality=94)
# Native-resolution crops: 410x240, all 144 decoded frames, no animation or reconstruction.
for group in range(6):
 out=Image.new('RGB',(410*6,266*4),(240,240,240));d=ImageDraw.Draw(out)
 for j in range(24):
  n=group*24+j;im=Image.open(frames/f'{n:05d}.png').crop((80,310,490,550));x=(j%6)*410;y=(j//6)*266
  out.paste(im,(x,y+26));d.text((x+5,y+4),f'F{n:03d} {n/24:.3f}s',font=font,fill='black')
 out.save(p/f'hands_all_{group:02d}.jpg',quality=96)
# Rig overlay keeps exact source dimensions and source pixels; colors are annotation only.
im=Image.open(p/'source/g01_beans.png').convert('RGBA');bg=Image.new('RGBA',im.size,(238,238,238,255));bg.alpha_composite(im)
ov=Image.new('RGBA',im.size,(0,0,0,0));d=ImageDraw.Draw(ov)
rig=json.loads((p/'source/g01_beans.rig.json').read_text())
for r in rig['regions']: d.polygon([tuple(v) for v in r['poly']],fill=(255,20,50,35),outline=(255,20,50,255),width=3)
for b in rig['bones']:
 c=(0,100,255,255) if '_far' in b['name'] else (0,170,90,255) if '_near' in b['name'] else (220,80,0,255)
 h=tuple(b['head']);t=tuple(b['tail']);d.line((h,t),fill=c,width=3)
 for x,y in [h,t]:d.ellipse((x-4,y-4,x+4,y+4),fill=c)
 d.text((h[0]+5,h[1]+5),b['name'],font=font,fill=c,stroke_width=1,stroke_fill=(255,255,255,235))
for label,xy in [('elbow_far_observed',(222,601)),('wrist_far_observed',(166,525)),('wrist_near_observed',(394,616))]:
 x,y=xy;d.ellipse((x-7,y-7,x+7,y+7),outline=(240,0,200,255),width=3);d.text((x+10,y-20),label,font=font,fill=(170,0,150,255),stroke_width=1,stroke_fill=(255,255,255,245))
bg.alpha_composite(ov);bg.convert('RGB').save(p/'rig_existing_overlay.png')
bg.crop((85,420,665,820)).resize((1160,800)).convert('RGB').save(p/'rig_arm_bowl_detail.png')
