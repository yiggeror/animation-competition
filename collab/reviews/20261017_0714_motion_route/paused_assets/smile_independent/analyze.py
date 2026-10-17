from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib
p=Path('/tmp/laidian-audit-s31-grandma-release')
paths=[Path('/workspace/animation-competition-astra/collab/refs/anim_29_grandma_prepare_blow.png'),Path('/tmp/laidian-produce-s31-grandma-release/anim_31_grandma_release_smile.png')]
ims=[Image.open(f).convert('RGB') for f in paths];arrs=[np.array(im).astype(np.int16) for im in ims]
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
for name,box in {'head_pair':(70,130,935,900),'face_pair':(145,490,665,885),'cheek_pair':(170,680,395,860),'collar_pair':(380,705,800,1120)}.items():
 w=box[2]-box[0];h=box[3]-box[1];out=Image.new('RGB',(w*2,h+36),(40,40,40));d=ImageDraw.Draw(out)
 for i,im in enumerate(ims):out.paste(im.crop(box),(i*w,36));d.text((i*w+10,6),['A prepare blow','B release smile'][i],font=font,fill='white')
 out.save(p/f'{name}.png')
# First dark outer contour pixel on each scanline; checked visually separately.
rows=[]
for y in range(695,851):
 xs=[]
 for a in arrs:
  r=a[y,150:320];xx=np.flatnonzero(r.max(1)<105)
  xs.append(int(xx[0])+150 if len(xx) else None)
 rows.append({'y':y,'a_left_dark':xs[0],'b_left_dark':xs[1],'delta_b_minus_a':xs[1]-xs[0] if None not in xs else None})
vals=[r['delta_b_minus_a'] for r in rows if r['delta_b_minus_a'] is not None]
metrics={'method':'independent first dark boundary scan, max(R,G,B)<105, x150..319, y695..850; contour diagnostic only, not actual compositor alpha','median_inward_px':float(np.median(vals)),'min_inward_px':int(min(vals)),'max_inward_px':int(max(vals)),'rows':rows}
(p/'contour_scan.json').write_text(json.dumps(metrics,indent=2))
# Simplified cheek silhouette diagnostic from real dark outer boundary, same coordinates.
colors=[(230,70,60),(20,130,210)];overlay=ims[0].crop((150,675,370,870)).resize((660,585));dr=ImageDraw.Draw(overlay)
for i,col in enumerate(colors):
 pts=[((r['a_left_dark' if i==0 else 'b_left_dark']-150)*3,(r['y']-675)*3) for r in rows if r['a_left_dark' if i==0 else 'b_left_dark'] is not None];dr.line(pts,fill=col,width=3)
dr.text((230,15),'A red / B blue',font=font,fill='black',stroke_width=1,stroke_fill='white');overlay.save(p/'cheek_contour_overlay_x3.png')
board=Image.new('RGB',(1200,600),'white');bd=ImageDraw.Draw(board)
for i in range(2):
 pts=[((r['a_left_dark' if i==0 else 'b_left_dark']-150)*3+i*600+20,(r['y']-695)*3+70) for r in rows if r['a_left_dark' if i==0 else 'b_left_dark'] is not None]
 bd.polygon(pts+[(i*600+580,535),(i*600+580,70)],fill='black');bd.text((i*600+15,15),['A cheek boundary','B cheek boundary'][i],font=font,fill='black')
board.save(p/'cheek_silhouette_diagnostic.png')
# Anchor ROI shift search and pixel variation, independent from author's script.
a,b=arrs;dif=np.abs(a-b);editmask=np.ones(a.shape[:2],bool);editmask[555:870,175:560]=False
non={'excluded_face_rect':[175,555,560,870],'non_target_rgb_mae':float(dif[editmask].mean()),'non_target_fraction_pixel_maxdiff_gt32':float((dif.max(2)[editmask]>32).mean()),'anchor_regions':{}}
rois={'glasses':[125,535,575,695],'ear':[550,525,675,705],'bun_beads':[755,405,930,755],'hair_top':[100,135,800,505],'neck_collar':[405,825,800,1110]}
for name,(x0,y0,x1,y1) in rois.items():
 best=(1e9,0,0)
 for dy in range(-4,5):
  for dx in range(-4,5):
   v=float(np.abs(a[y0:y1,x0:x1]-b[y0+dy:y1+dy,x0+dx:x1+dx]).mean())
   if v<best[0]:best=(v,dx,dy)
 non['anchor_regions'][name]={'box':[x0,y0,x1,y1],'raw_rgb_mae':float(dif[y0:y1,x0:x1].mean()),'best_B_offset_dx_dy':list(best[1:]),'best_mae':best[0]}
(p/'independent_non_target_metrics.json').write_text(json.dumps(non,indent=2))
(p/'sources.json').write_text(json.dumps([{'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size,'dimensions':list(im.size)} for f,im in zip(paths,ims)],indent=2))
print(json.dumps({k:v for k,v in metrics.items() if k!='rows'},indent=2));print(json.dumps(non,indent=2))
