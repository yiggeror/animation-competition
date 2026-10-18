from PIL import Image
from pathlib import Path
import numpy as np,json,hashlib
from scipy.ndimage import label,binary_dilation,binary_erosion,gaussian_filter1d
O=Path(__file__).resolve().parent; D=O
for folder in ['final','masks','records','review']:(O/folder).mkdir(exist_ok=True)
bim=Image.open(O/'inputs/base_F052_v6.png').convert('RGBA');b=np.array(bim)
# Reproduce the original v2 return from the immutable call11 raw and explicit return mask.
l=bim.copy();l.paste(Image.open(O/'raw/call11_F055.png').convert('RGBA').resize((430,415),Image.Resampling.LANCZOS),(620,420));arr=np.array(l)
ys=np.arange(arr.shape[0],dtype=float);sy=np.clip(ys-np.clip((ys-665)/65,0,1)*8,0,len(ys)-1);lo=np.floor(sy).astype(int);hi=np.minimum(lo+1,len(ys)-1);ww=(sy-lo)[:,None,None]
l=Image.fromarray(np.rint(arr[lo]*(1-ww)+arr[hi]*ww).astype(np.uint8));v=np.array(Image.composite(l,bim,Image.open(O/'masks/original_full_return_mask.png').convert('L')))
o=v.copy();H,W=o.shape[:2]
def skin(a):
 r,g,bl=[a[:,:,i].astype(float) for i in range(3)]
 return (r>150)&(g>105)&(r>g+5)&(bl<r+25)&(a[:,:,3]>200)
def face(a):
 lab,_=label(skin(a));return lab==lab[700,830]
fb,fv=face(b),face(v)
# Use the actual original continuous chin edge, including its antialias; do not splice a rectangle.
xs=np.arange(710,958);cur=[]
for f in [fb,fv]:
 q=[]
 for x in xs:
  yy=np.where(f[680:755,x])[0]+680
  q.append(yy[-1] if len(yy) else np.nan)
 q=np.array(q,dtype=float);q=np.interp(xs,xs[np.isfinite(q)],q[np.isfinite(q)]);cur.append(q)
bc,vc=cur
# Original chin exact through both neck junctions; outer edge transitions follow the deflated cheek.
w=np.minimum(np.clip((xs-710)/35,0,1),np.clip((958-xs)/75,0,1));w=w*w*(3-2*w);dd=gaussian_filter1d((vc-bc)*(1-w),4); dd[(xs>=755)&(xs<=875)]=0; tc=bc+dd
# Sampling real base contour moves only the outer little transition; original central jaw not moved.
jaw=np.zeros((H,W),bool)
for i,x in enumerate(xs):
 q=tc[i];delta=q-bc[i]
 for y in range(max(690,int(min(bc[i],vc[i],q)-20)),min(765,int(max(bc[i],vc[i],q)+10))):
  # Replace the whole ink neighborhood. Blend only well inside the skin.
  a=np.clip((y-(q-19))/10,0,1)
  if y>max(bc[i],vc[i],q)+6:a=0
  a*=min(1,(x-710)/7,(958-x)/7)
  if a<=0:continue
  sy=np.clip(y-delta,0,H-1);il=int(sy);ih=min(il+1,H-1);p=np.rint(b[il,x]*(1-(sy-il))+b[ih,x]*(sy-il)).astype('uint8')
  # Neck remains original exactly. For side background beyond jaw, retain transparency.
  if y>q+3 and not (758<=x<=913):p[3]=0
  o[y,x]=np.rint(p*a+o[y,x]*(1-a)).astype('uint8');jaw[y,x]=True
# Nose boundary: source skin colour only, progressively return to donor lower cheek; preserve ink and mouth.
sk=skin(o)&skin(b);ink=(o[:,:,:3].mean(2)<145)&(o[:,:,3]>100);guard=binary_dilation(ink,iterations=2)
col=np.zeros((H,W),bool)
for y in range(630,717):
 a=1.0 if y<=659 else 1-(y-659)/58;a=a*a*(3-2*a)
 for x in range(665,1010):
  if sk[y,x] and not guard[y,x] and not (804<=x<=860 and 667<=y<=693):
   o[y,x,:3]=np.rint(b[y,x,:3]*a+o[y,x,:3]*(1-a)).astype('uint8');col[y,x]=True
# Clean donor-only material outside the accepted face. Restore only real hair/ribbon, never puffy old cheek.
r,g,bl=[b[:,:,i].astype(float) for i in range(3)]
oldmat=(((r<145)&(g<115)&(bl<110))|((r>120)&(r>g*1.65)&(g<120)&(bl<130)))&(b[:,:,3]>0)
roi=np.zeros((H,W),bool);roi[625:724,968:1028]=True;roi[650:720,642:691]=False
oldmat &= ~binary_dilation(fb,iterations=3)
newface=face(o);faceguard=binary_dilation(newface,iterations=1)
# Outside new face and its actual black outline, reinstate original non-face layer or alpha 0.
cl=roi&~binary_dilation(newface,iterations=2)
for y,x in zip(*np.where(cl)):
 if oldmat[y,x] or b[y,x,3]==0:o[y,x]=b[y,x]
 else:o[y,x,3]=0
# Restore unchanged original ribbon/hair areas whose donor colour crossed onto it.
orig_layer=roi&oldmat&~faceguard;o[orig_layer]=b[orig_layer];cl|=orig_layer
# Remove only old puff-contour hair-like residual outside the new face, lower right.
from PIL import ImageDraw
pm=Image.new('L',(W,H));ImageDraw.Draw(pm).polygon([(951,709),(979,671),(986,676),(969,710)],fill=255)
res=(np.array(pm)>0)&~binary_dilation(newface,iterations=3);o[res,3]=0;cl|=res
# Exact source ribbon is a real object behind the receded cheek; preserve its original edge and the hair-enclosed skin sliver.
red=(r>140)&(r>g*1.7)&(g<120)&(bl<140)&(b[:,:,3]>0)
redguard=binary_dilation(red,iterations=1)&roi&~faceguard;o[redguard]=b[redguard];cl|=redguard
sliver=np.zeros((H,W),bool);sliver[620:650,1006:1026]=True;sliver &= ~faceguard;o[sliver]=b[sliver];cl|=sliver
expr=np.zeros((H,W),bool);expr[470:620,650:1030]=True;expr[667:693,804:860]=True;o[expr]=v[expr]
allow=jaw|col|cl;o[~allow]=v[~allow];o[765:]=v[765:]
p=O/'final/S05a_F055.png';Image.fromarray(o).save(p)
for n,m in [('jaw',jaw),('chroma',col),('cleanup',cl),('allowed',allow),('difference',np.any(o!=v,2))]:Image.fromarray((m*255).astype('uint8')).save(O/f'masks/{n}_r6.png')
for name,a in [('r6_after',o)]:
 im=Image.fromarray(a);bg=Image.new('RGBA',im.size,(110,116,124,255));bg.alpha_composite(im);bg.convert('RGB').crop((600,400,1080,850)).resize((960,900)).save(O/f'review/{name}_detail.png')
diff=np.any(o!=v,2);rec={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'changes':int(diff.sum()),'outside_allow':int((diff&~allow).sum()),'expression_changes':int(diff[expr].sum()),'below765_changes':int(diff[765:].sum()),'source':'same call11 V2 plus approved052 original contour and skin, zero new generation; independent parent static review accepted 2026-10-18 13:37 UTC'};(O/'records/r6_checks.json').write_text(json.dumps(rec,indent=2));print(rec)
