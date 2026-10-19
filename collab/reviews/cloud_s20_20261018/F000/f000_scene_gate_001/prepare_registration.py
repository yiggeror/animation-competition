from pathlib import Path
import json
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent
a=np.array(Image.open(P/'cleanup/S20_F000_master_clean.png'))
lines={
 'T_H':(.6954945799457998,-205.14137308039784,800,880,343,787,924),
 'T_S':(.381413730803975,92.50752785305603,800,880,388,774,924),
 'C_N':(221/95,79-826*221/95,835,880,79,826,929),
 'C_B':(188/114,111-792*188/114,835,880,111,792,929),
}
result={}
for name,(m,b,x0,x1,tipy,tipx,gx) in lines.items():
 pts=[]
 for x in range(x0,x1+1):
  ys=np.arange(max(0,int(m*x+b)-6),min(a.shape[0],int(m*x+b)+7))
  v=a[ys,x].astype(int)
  ok=(v[:,3]>180)&(v[:,0]-v[:,1]>15)&(v[:,1]-v[:,2]>15)
  if ok.any(): pts.append((x,float(np.median(ys[ok]))))
 assert len(pts)>30,(name,len(pts))
 pts=np.array(pts); mf,bf=np.polyfit(pts[:,0],pts[:,1],1)
 result[name]={'slope':float(mf),'intercept':float(bf),'fit_columns':len(pts),
   'shaft_tip_master_px':[tipx,tipy],'grip_master_px':[gx,float(mf*gx+bf)],
   'master_axis_fit_RMS_px':float(np.sqrt(np.mean((pts[:,1]-mf*pts[:,0]-bf)**2))),
   'initial_holder':'G.R' if name.startswith('T') else 'G.L'}
data={
 'master':'cleanup/S20_F000_master_clean.png',
 'pair_registration':{'base_world_m':[1.13,1.10,0],'ox':1110,'oy':920,'pixels_per_cm':875/150,
   'uniform_scale_only':True,'mirrored':False,'individual_body_warp':False,
   'note':'Original grandmother F000 stage slot; one whole-pair billboard preserves approved relative proportions.'},
 'rods':result,
 'sole_landmarks_master_px':{'G_far':[1046,903],'G_near':[1150,920],'X_near':[581,919],'X_far':[652,905]},
 'sole_outline_points_master_px':{'G_far':[[1008,898],[1046,903],[1090,902]],
 'G_near':[[1100,913],[1150,920],[1208,909]],
 'X_near':[[534,906],[581,919],[620,912]],'X_far':[[602,897],[652,905],[690,902]]},
 'raster_height_ratio_X_to_G':(920-181)/(920-44),
 'notes':['The ratio is measured from the approved art, not altered to match old code people.',
 'Sole floor points are found by camera-ray/floor intersection; tilted billboard physical-z offsets are disclosed.'],
}
(P/'registration_input.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps(data,indent=2))
