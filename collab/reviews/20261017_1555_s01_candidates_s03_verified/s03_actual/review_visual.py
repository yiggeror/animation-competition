from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,numpy as np
R=Path(__file__).resolve().parent
ids=[0,17,18,20,21,26,27,29,30,32,33,56,57,62,63,68,69,80,81,90,91,95,96,101,102,104,105,107,108,116,117,125,126,134,135,143]
for prefix,chosen,box,size,cols in [('boundary',ids,(520,30,1370,900),(340,348),6),('retreat',[101,102,104,105,107,108,116,117,125,126,134,135],(560,130,1320,880),(380,375),4),('full',[0,30,33,91,96,102,105,108,117,126,135,143],(0,0,1920,1080),(480,270),4)]:
 sh=Image.new('RGB',(size[0]*cols,(size[1]+24)*((len(chosen)+cols-1)//cols)),(48,48,48));d=ImageDraw.Draw(sh)
 for i,f in enumerate(chosen):
  im=Image.open(R/'frames'/f'{f:04}.png').convert('RGB').crop(box);im.thumbnail(size);x=(i%cols)*size[0];y=(i//cols)*(size[1]+24);sh.paste(im,(x,y+24));d.text((x+7,y+7),f'F{f:03}',fill='white')
 sh.save(R/f'{prefix}_actual_contact.jpg')
rows=[]
for f in range(144):
 a=np.array(Image.open(R/'frames'/f'{f:04}.png').convert('RGB'));c=a.astype(float);r,g,b=c[:,:,0],c[:,:,1],c[:,:,2];m=(r>1.5*g)&(r>1.5*b)&(g>35)&(r>100);m[:380]=False;m[850:]=False;m[:,:450]=False;m[:,1350:]=False;y,x=np.where(m)
 top=a[:20];rows.append({'frame':f,'fruit_red_pixels':int(len(x)),'fruit_red_centroid':[float(x.mean()),float(y.mean())] if len(x) else None,'top20_black_fraction':float(np.all(top<8,axis=2).mean())})
(R/'visual_metrics.json').write_text(json.dumps({'actual_file_sha256':hashlib.sha256((R/'S03_1080p.mp4').read_bytes()).hexdigest(),'inspected_frames':ids,'red_mask_note':'red-flesh pixel centroid in fixed screen ROI; not anatomical tracking; scene camera motion remains','frames':rows},indent=2)+'\n')
print(json.dumps([rows[f] for f in [91,96,101,102,104,105,107,108,116,117,126,135,143]],indent=2))
print('top20 black frac max',max(x['top20_black_fraction'] for x in rows))
