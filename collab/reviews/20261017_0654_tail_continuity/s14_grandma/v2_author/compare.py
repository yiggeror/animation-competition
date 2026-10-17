from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json
p=Path('/tmp/laidian-produce-s14-grandma-v2');ap=Path('/tmp/laidian-produce-s14-grandma/anim_14_grandma_hang_sheet.png');bp=p/'anim_14_grandma_hang_sheet.png'
a=np.array(Image.open(ap).convert('RGB')).astype(np.int16);b=np.array(Image.open(bp).convert('RGB')).astype(np.int16);d=np.abs(a-b);pm=d.max(2)
targets=[[700,100,800,200],[720,250,825,365]]
mask=np.ones(a.shape[:2],dtype=bool)
for x0,y0,x1,y1 in targets:mask[y0:y1,x0:x1]=False
res={'comparison':'v1 original vs v2 original, same dimensions, no registration applied','target_edit_rects':targets,'non_target_entire_canvas':{'rgb_mae':float(d[mask].mean()),'fraction_pixels_maxdiff_gt8':float((pm[mask]>8).mean()),'fraction_pixels_maxdiff_gt32':float((pm[mask]>32).mean())},'regions':{}}
regions={'head_face':[250,50,600,370],'torso_clothing':[260,350,630,830],'pin_and_gripping_fingers':[790,40,885,160],'lower_supporting_fingers':[800,160,870,263],'cloth_contact_patch':[865,120,1024,355],'shoulders_elbows':[320,315,655,560],'shoes':[145,1290,610,1490]}
for name,box in regions.items():
 x0,y0,x1,y1=box;v=d[y0:y1,x0:x1];best=(1e9,0,0)
 for dy in range(-5,6):
  for dx in range(-5,6):
   # use 8px inner region to avoid image-boundary clipping
   aa=a[y0+8:y1-8,x0+8:x1-8];bb=b[y0+8+dy:y1-8+dy,x0+8+dx:x1-8+dx]
   score=float(np.abs(aa-bb).mean())
   if score<best[0]:best=(score,dx,dy)
 res['regions'][name]={'box':box,'rgb_mae':float(v.mean()),'fraction_pixels_maxdiff_gt8':float((v.max(2)>8).mean()),'best_B_sampling_offset_dx_dy':list(best[1:]),'best_offset_mae_inner_roi':best[0]}
(p/'non_target_metrics.json').write_text(json.dumps(res,ensure_ascii=False,indent=2))
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
board=Image.new('RGB',(1536,812),(35,35,35));dr=ImageDraw.Draw(board)
for i,(name,im) in enumerate([('V1 original (wrong wrist)',Image.open(ap)),('V2 corrected original',Image.open(bp)),('Absolute RGB diff x8',Image.fromarray(np.minimum(d*8,255).astype(np.uint8)))]):
 im=im.resize((512,768));board.paste(im,(i*512,44));dr.text((i*512+8,9),name,font=font,fill='white')
board.save(p/'v1_v2_difference.png')
print(json.dumps(res,indent=2))
