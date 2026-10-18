from PIL import Image,ImageDraw,ImageChops,ImageFilter
from pathlib import Path
import json,hashlib,numpy as np,shutil
R=Path(__file__).resolve().parents[1];S=R
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def neutral(a):
 g=Image.new('RGBA',a.size,(240,240,240,255));g.alpha_composite(a);return g.convert('RGB')
def render(a,camera=(605,637.5,4.18)):
 cx,cy,z=camera;vw=1672/z;vh=941/z;left=cx-vw/2;top=cy-vh/2
 bg=Image.open(R/'sources/bg_room.png').convert('RGBA');out=bg.resize((1672,941),Image.Resampling.LANCZOS,box=(left,top,left+vw,top+vh))
 def layer(im,ss,t):
  q=im.convert('RGBa').resize((round(im.width*ss*z),round(im.height*ss*z)),Image.Resampling.LANCZOS).convert('RGBA');out.alpha_composite(q,(round((t[0]-left)*z),round((t[1]-top)*z)))
 layer(Image.open(R/'sources/phone_landed_only_same_registration.png').convert('RGBA'),.16,(430,533));layer(a,.2475,(339.7325,512.485));return out.convert('RGB')
