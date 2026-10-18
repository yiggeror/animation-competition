from PIL import Image,ImageDraw
from pathlib import Path
import numpy as np,json,hashlib
r=Path('astra_s08_first_mother_20261018_1433');o=Path('astra_s08_first_mother_20261018_1433/F030_color_final/geometry')
ps=[r/'F000_FINAL_LOCKED/S08_F000_grandma_match_box_RGBA.png',r/'F030_color_final/candidates/S08_F030_whole_turn_same_raw_final_color_RGBA.png'];aa=[np.array(Image.open(p).convert('RGBA')) for p in ps]
# Semantic corresponding visible planes; no geometric equality or3D calibrated lighting claimed.
S=[('forehead','skin',(858,443,909,466),(904,454,946,480)),('near_cheek','skin',(797,565,833,593),(842,575,879,600)),('far_cheek','skin',(912,559,937,580),(952,567,972,590)),('chin_lit','skin',(857,612,883,634),(895,620,923,640)),('neck_mid','skin',(810,647,835,676),(849,653,874,681)),('crown','hair',(770,369,831,402),(819,367,879,400)),('bun','hair',(674,527,705,553),(711,534,739,561)),('near_chest','blue',(773,739,815,786),(837,738,877,782)),('near_sleeve','blue',(639,731,680,773),(701,719,747,758)),('far_chest','blue',(900,716,946,767),(957,709,996,760)),('near_upperarm_lit','skin',(730,846,755,873),(788,824,812,849)),('near_forearm_lit','skin',(847,865,874,883),(927,812,952,830)),('far_forearm_lit','skin',(1091,877,1112,899),(1085,832,1111,847)),('ear_lit','skin',(734,525,751,544),(774,534,791,551)),('crown_middle','hair',(750,412,790,438),(789,414,829,440)),('bun_lower','hair',(686,556,711,570),(721,564,747,578))]
result=[];comps=[]
for a in aa:comps.append(Image.alpha_composite(Image.new('RGBA',(a.shape[1],a.shape[0]),(145,145,145,255)),Image.fromarray(a)).convert('RGB'))
for idx,(n,typ,*boxes) in enumerate(S):
 vals=[]
 for j,(a,box) in enumerate(zip(aa,boxes)):
  x1,y1,x2,y2=box; ar=a[y1:y2,x1:x2].astype(int);m=ar[:,:,3]>250
  if typ=='skin':m&=(ar[:,:,0]>220)&(ar[:,:,0]-ar[:,:,1]>20)&(ar[:,:,1]-ar[:,:,2]>12)
  elif typ=='blue':m&=(ar[:,:,2]-ar[:,:,0]>25)&(ar[:,:,1]>100)&(ar[:,:,0]>55)&(ar[:,:,0]<175)
  else:m&=(ar[:,:,:3].max(2)-ar[:,:,:3].min(2)<30)&(ar[:,:,:3].min(2)>115)&(ar[:,:,:3].max(2)<225)
  v=ar[:,:,:3][m];vals.append({'box':box,'n':len(v),'mean':v.mean(0).tolist() if len(v) else None,'median':np.median(v,axis=0).tolist() if len(v) else None})
  d=ImageDraw.Draw(comps[j]);d.rectangle(box,outline=(255,0,120),width=2);d.text((x1,y1-11),f'{idx+1} {n}',fill=(25,10,10))
 result.append({'part':n,'kind':typ,'F000':vals[0],'F030':vals[1],'delta_mean':(np.array(vals[1]['mean'])-vals[0]['mean']).tolist() if all(v['n'] for v in vals) else None})
panel=Image.new('RGB',(1600,820),(145,145,145))
for j,im in enumerate(comps):panel.paste(im.crop((550,280,1350,1100)),(j*800,0))
panel.save(o/'F000_F030_actual_material_samples.jpg');(o/'color_actual_diagnostic.json').write_text(json.dumps({'sourceSHA':[hashlib.sha256(p.read_bytes()).hexdigest() for p in ps],'status':'MANUAL_CORRESPONDING_VISIBLE_PLANES_NOT_3D_OR_PIXEL_MATCHED','samples':result},indent=2))
for x in result: print(x['part'],x['F000']['n'],x['F030']['n'],np.round(x['delta_mean'],2),np.round(x['F000']['mean'],2),np.round(x['F030']['mean'],2))
