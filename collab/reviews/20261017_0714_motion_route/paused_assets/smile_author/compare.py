from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
out=Path(__file__).parent
pa=Path('/workspace/animation-competition-astra/collab/refs/anim_29_grandma_prepare_blow.png');pb=out/'anim_31_grandma_release_smile.png';ims=[Image.open(p).convert('RGB') for p in [pa,pb]];a,b=[np.array(im,dtype=np.int16) for im in ims]
boxes={'face_expression':(120,475,670,910),'mouth_cheek':(155,680,565,885),'bun_beads':(610,330,955,760),'neck_collar':(320,695,835,1160)}
for name,box in boxes.items():
 cs=[im.crop(box) for im in ims];w,h=cs[0].size;s=Image.new('RGB',(2*w+12,h+24),(240,240,240));d=ImageDraw.Draw(s)
 for i,c in enumerate(cs):s.paste(c,(i*(w+12),24));d.text((i*(w+12)+5,6),['A puffed original','B smile original'][i],fill=(0,0,0))
 s.save(out/f'evidence_{name}_pair.png');cs[1].save(out/f'evidence_b_{name}.png')
mask=np.ones(a.shape[:2],bool);mask[475:890,150:575]=False;diff=np.abs(a-b);stats={'target_exclusion_xyxy':[150,475,575,890],'non_target_rgb_mae':float(diff[mask].mean()),'non_target_max_channel_diff_gt8_fraction':float((diff.max(2)[mask]>8).mean()),'non_target_max_channel_diff_gt32_fraction':float((diff.max(2)[mask]>32).mean()),'anchors':{}}
for name,box in {'ear':(555,520,680,710),'bun':(705,500,950,750),'three_beads':(775,400,870,530),'neck_and_collar_tip':(455,850,655,1100),'collar_outer':(375,950,790,1100)}.items():
 x0,y0,x1,y1=box;aa=a[y0:y1,x0:x1];best=(float('inf'),0,0)
 for dx in range(-3,4):
  for dy in range(-3,4):
   mae=float(np.abs(aa-b[y0+dy:y1+dy,x0+dx:x1+dx]).mean())
   if mae<best[0]:best=(mae,dx,dy)
 stats['anchors'][name]={'box':box,'raw_rgb_mae':float(np.abs(aa-b[y0:y1,x0:x1]).mean()),'best_B_sampling_dxdy':list(best[1:]),'best_mae':best[0]}
(out/'non_target_metrics.json').write_text(json.dumps(stats,indent=2))
rows=[]
for y in range(705,846):
 xs=[]
 for arr in [a,b]:
  line=arr[y,140:350];sel=(line[:,0]-line[:,2]>45)&(line[:,0]-line[:,1]>12)&(line[:,0]>170);hits=np.where(sel)[0];xs.append(int(hits[0]+140) if len(hits) else None)
 if all(x is not None for x in xs):rows.append({'y':y,'a_first_skin_x':xs[0],'b_first_skin_x':xs[1],'b_minus_a':xs[1]-xs[0]})
deltas=np.array([r['b_minus_a'] for r in rows]);contour={'method':'First warm skin pixel x in [140,350), y705..845; excludes dark outline and is diagnostic, not a production silhouette mask','rows':rows,'median_dx':float(np.median(deltas)),'min_dx':int(deltas.min()),'max_dx':int(deltas.max()),'fraction_abs_dx_le1':float((np.abs(deltas)<=1).mean())};(out/'cheek_contour_diagnostic.json').write_text(json.dumps(contour,indent=2));print(json.dumps(stats,indent=2));print({k:v for k,v in contour.items() if k!='rows'})
