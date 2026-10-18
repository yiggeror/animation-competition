"""Reproduce the locked 042 and 044 from persisted source pixels/raw drawings/masks.
No image-generation call or dependency on a default generated_images directory.
Run in any directory; outputs to verification_replay/. Uses Pillow/numpy/scipy.
047 is a byte-identical exposure copy of 044, not another generated drawing.
"""
from pathlib import Path
from PIL import Image
import numpy as np, hashlib, shutil
from scipy.ndimage import binary_dilation,binary_fill_holes
R=Path(__file__).resolve().parent; O=R/'verification_replay';O.mkdir(exist_ok=True)
def finish(frame,out,expected):
 p=O/f'S05a_F{frame:03d}.png';out.save(p);sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha==expected,(frame,sha);print(frame,sha)
base=Image.open(R/'candidates/F042_call06_complete_pending_review.png').convert('RGBA');raw=Image.open(R/'raw/call07_F042_rail_seam.png').convert('RGBA');layer=base.copy();layer.paste(raw.resize((120,75),Image.Resampling.LANCZOS),(680,860));mask=Image.open(R/'masks/F042_rail_seam_repair_mask.png').convert('L');out=Image.composite(layer,base,mask);out.putalpha(base.getchannel('A'));finish(42,out,'3bf83f8ea45f79bfc491269a2104408941dbfb7993d82521dc653411feef8b3d')
base=Image.open(R/'inputs/F044_from_locked_pose_scaffold.png').convert('RGBA');raw=Image.open(R/'raw/call08_F044_stronger_press.png').convert('RGBA');layer=base.copy();layer.paste(raw.resize((390,481),Image.Resampling.LANCZOS),(640,460))
def peak(im):
 a=np.array(im).astype(float);rows=np.arange(855,890);c=a[rows,800,:3];ok=(c.max(1)<160)&(c.max(1)-c.min(1)<35);score=c.mean(1);score[~ok]=-100;return int(rows[np.argmax(score)])
delta=peak(base)-peak(layer);registered=layer.transform(base.size,Image.Transform.AFFINE,(1,0,0,0,1,-delta),Image.Resampling.BICUBIC);layer.paste(registered.crop((680,855,782,929)),(680,855));mask=Image.open(R/'masks/F044_stronger_press_mask.png').convert('L');out=Image.composite(layer,base,mask);out.putalpha(base.getchannel('A'));a0=np.array(out).astype(int);yy,xx=np.mgrid[:941,:1672];sk=(a0[:,:,0]>150)&(a0[:,:,2]>90)&(a0[:,:,0]-a0[:,:,1]>15)&(a0[:,:,1]-a0[:,:,2]>5)&(a0[:,:,1]-a0[:,:,2]<65);sk=binary_fill_holes(sk);ink=binary_dilation(sk,iterations=2)&(a0[:,:,:3].max(-1)<160);restore=(np.array(mask)>0)&(yy>884)&~(sk|ink);clean=np.array(Image.open(R/'inputs/F044_clean_body_scaffold.png').convert('RGBA'));a0[restore]=clean[restore];a0[910:926,722:744]=clean[910:926,722:744];out=Image.fromarray(a0.astype('uint8'),'RGBA');out.putalpha(base.getchannel('A'));finish(44,out,'dbbe4d678713a1c741e75dc0b701367363ab70d98f5f3d2c97c4753ff9603a96');shutil.copyfile(O/'S05a_F044.png',O/'S05a_F047.png');print('047 byte-identical copy of 044')
