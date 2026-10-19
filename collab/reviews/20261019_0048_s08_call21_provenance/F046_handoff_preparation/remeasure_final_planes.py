from PIL import Image,ImageDraw
from pathlib import Path
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent.parent;D=R/'F046_color_final/geometry/final_plane_remeasurement';D.mkdir(parents=True,exist_ok=True);paths=[R/'F000_FINAL_LOCKED/S08_F000_grandma_match_box_RGBA.png',R/'F046_color_final/candidates/S08_F046_same_raw_final_color_RGBA.png'];aa=[np.array(Image.open(p))for p in paths]
S=[('near_upperarm_lit','skin',[730,846,755,873],[903,853,928,877]),('near_forearm_lit_middle','skin',[847,865,874,883],[1065,849,1100,868]),('near_forearm_lit_distal','skin',[847,865,874,883],[1145,817,1170,838]),('near_sleeve_crossing_fold_DIAGNOSTIC_ONLY','blue',[639,731,680,773],[799,752,833,785]),('near_sleeve_lit_lower','blue',[639,731,680,773],[820,799,850,832]),('new_chest_placket_turn_DIAGNOSTIC_ONLY','blue',[773,739,815,786],[958,826,986,843]),('elbow_lower_turn_DIAGNOSTIC_ONLY','skin',[847,865,874,883],[965,927,983,938])]
comps=[Image.alpha_composite(Image.new('RGBA',(1920,1080),(244,242,237,255)),Image.fromarray(a)).convert('RGB')for a in aa];res=[]
for i,(name,kind,*boxes) in enumerate(S):
 vals=[]
 for j,(a,b) in enumerate(zip(aa,boxes)):
  x1,y1,x2,y2=b;ar=a[y1:y2,x1:x2].astype(int);m=ar[:,:,3]>250
  if kind=='skin':m&=(ar[:,:,0]>220)&(ar[:,:,0]-ar[:,:,1]>20)&(ar[:,:,1]-ar[:,:,2]>12)
  else:m&=(ar[:,:,2]-ar[:,:,0]>25)&(ar[:,:,1]>100)&(ar[:,:,0]>55)&(ar[:,:,0]<175)
  v=ar[:,:,:3][m];vals.append({'box':b,'n':len(v),'mean':v.mean(0).tolist(),'median':np.median(v,0).tolist()});d=ImageDraw.Draw(comps[j]);d.rectangle(b,outline=(255,20,110),width=2);d.text((x1,y1-11),str(i+1)+' '+name,fill=(20,20,20))
 res.append({'part':name,'kind':kind,'F000':vals[0],'F046':vals[1],'delta_mean':(np.array(vals[1]['mean'])-vals[0]['mean']).tolist()})
p=Image.new('RGB',(1740,570),(244,242,237));p.paste(comps[0].crop((570,660,1440,1230)),(0,0));p.paste(comps[1].crop((570,660,1440,1230)),(870,0));p.save(D/'F000_F046_actual_new_material_samples.png')
(D/'color_actual_diagnostic.json').write_text(json.dumps({'status':'FINAL_V10_GEOMETRY_FINAL_SOFT_COLOR_REMEASUREMENT_SHADOW_PLANES_SEPARATE','sourceSHAs':[hashlib.sha256(p.read_bytes()).hexdigest()for p in paths],'samples':res,'head_hair_chest_core':'Original043 pixels retained; no new native face/eyes/hair accepted.'},indent=2))
for z in res:print(z['part'],np.round(z['delta_mean'],2),z['F046']['n'])
