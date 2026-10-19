from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json
from scipy.ndimage import binary_opening,binary_closing,binary_fill_holes,binary_dilation,label
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parents[1]
def semantic_pants(path):
 a=np.asarray(Image.open(path).convert('RGBA'));q=a.astype(int);y,x=np.mgrid[:a.shape[0],:a.shape[1]]
 navy=(q[:,:,2]-q[:,:,0]>8)&(q[:,:,2]-q[:,:,1]>8)&(q[:,:,2]<138)&(q[:,:,3]>24)&(y>=890)&(x<760)
 core=binary_opening(navy,iterations=1);labs,n=label(core);areas=np.bincount(labs.ravel());areas[0]=0;keep=np.flatnonzero(areas>700);keep=keep[keep!=0];core=np.isin(labs,keep);core=binary_fill_holes(binary_closing(core,iterations=2))
 blue=(q[:,:,2]>142)&(q[:,:,2]-q[:,:,1]>10)&(y<1070)&(x<700)&(q[:,:,3]>12)
 blue=binary_dilation(blue,iterations=1)
 pants=binary_dilation(core,iterations=2)&(q[:,:,3]>0)&~blue
 # Current visible feet/ankles are whatever remains outside the complete navy-pants core in the actual support area.
 feet=binary_fill_holes((q[:,:,3]>24)&(y>=1080)&(x<340)&~binary_dilation(core,iterations=1))
 labs,n=label(feet);areas=np.bincount(labs.ravel());keep=np.flatnonzero(areas>300);keep=keep[keep!=0];feet=np.isin(labs,keep)
 feet=binary_dilation(feet,iterations=1)
 pants&=~feet
 return a,pants,blue,feet,core
A,pants,blue,feet,core=semantic_pants(R/'F074_COMPLETE_actual_call01_20261019/candidate/F074.png')
allowed=binary_dilation(pants,iterations=2)&~blue&~feet
# Upper whole-body/blue flowers and all outside semantic pants are strictly excluded.
for name,m in [('CURRENT074_COMPLETE_SEMANTIC_PANTS',pants),('CURRENT074_BLUE_HEM_HARD_PROTECT',blue),('CURRENT074_BOTH_SHOES_BARE_ANKLES_HARD_PROTECT',feet),('PROPOSED_WHOLE_PANTS_PLUS_2PX_CONNECTION_ALLOWED',allowed),('OUTSIDE_PANTS_HARD_PROTECTED',~allowed)]:Image.fromarray(np.uint8(m)*255).save(O/f'masks/{name}.png')
b=Image.new('RGBA',(1024,1536),'#e1e4e6');b.alpha_composite(Image.fromarray(A));ov=np.zeros_like(A);ov[allowed]=(235,60,40,115);ov[feet]=(30,200,70,115);ov[blue]=(30,150,240,90);b.alpha_composite(Image.fromarray(ov));box=(0,850,760,1370);b=b.crop(box);d=ImageDraw.Draw(b);d.text((12,12),'RED: WHOLE PANTS +2px / GREEN: SHOES+ANKLES / BLUE: HEM PROTECT',fill='black');b.save(O/'reference/SEMANTIC_ALLOWED_AND_HARD_PROTECTION_READBACK.png')
print(json.dumps({'pants':int(pants.sum()),'allowed':int(allowed.sum()),'shoe_ankle_guard':int(feet.sum()),'blue_guard':int(blue.sum()),'allowed_feet_overlap':int((allowed&feet).sum()),'allowed_blue_overlap':int((allowed&blue).sum())}))
