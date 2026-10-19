from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
from scipy import ndimage as nd
R=Path(__file__).resolve().parent
for f in [54,60]:
 d=R/f'F{f:03d}';a=np.array(Image.open(d/f'originals/S29_F{f:03d}_call01_RAW_UNTOUCHED.png').convert('RGBA'));rgb=a[:,:,:3].astype(float);Y,X=np.indices(a.shape[:2]);shirt=(rgb[:,:,1]>95)&(rgb[:,:,2]>135)&(rgb[:,:,2]>rgb[:,:,0]+15);skin=(rgb[:,:,0]>120)&(rgb[:,:,1]>65)&(rgb[:,:,2]>90)&(rgb[:,:,0]>rgb[:,:,2]+25);jade=(rgb[:,:,1]>rgb[:,:,0]*1.05)&(rgb[:,:,1]>rgb[:,:,2]*1.03)&(rgb[:,:,1]>50)
 seed=(shirt|skin|jade)&(a[:,:,3]>128)&(Y>=340)&(Y<=935)&(X>=40)&(X<=795)
 lab,_=nd.label(nd.binary_closing(seed,iterations=1));main=lab==lab[500,350];m=nd.binary_dilation(nd.binary_fill_holes(main),iterations=1)&(a[:,:,3]>0)
 Image.fromarray((m*255).astype('uint8')).save(d/'DIAGNOSTIC_INITIAL_HUMAN_COMPONENT_MASK.png')
 ov=np.zeros_like(a);ov[m]=[255,0,90,80];bg=Image.new('RGBA',(1024,1536),(225,230,235));bg.alpha_composite(Image.fromarray(a));bg.alpha_composite(Image.fromarray(ov));bg.crop((80,450,800,900)).save(d/'DIAGNOSTIC_NATIVE_HUMAN_MASK_OVERLAY.png')
 # Exact far contact grid in source coordinates, no scaling.
 v=Image.new('RGBA',(1024,1536),(232,235,239));v.alpha_composite(Image.fromarray(a));dr=ImageDraw.Draw(v)
 for x in range(640,781,10):dr.line((x,590,x,700),fill=(100,100,100,160));dr.text((x,590),str(x),fill='black',stroke_width=1,stroke_fill='white')
 for y in range(600,701,10):dr.line((630,y,790,y),fill=(100,100,100,160));dr.text((630,y),str(y),fill='black',stroke_width=1,stroke_fill='white')
 v.crop((625,585,795,705)).resize((680,480)).save(d/'ACTUAL_FAR_PINCH_COORDINATE_GRID_4X.png')
 print(f,'mask',int(m.sum()))
