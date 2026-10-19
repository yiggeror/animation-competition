from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
from scipy import ndimage as nd
R=Path(__file__).resolve().parent; B=R.parent; repo=R.parents[3]
a=np.array(Image.open(repo/'collab/reviews/20261017_1813_s29_complete_candidates/complete6_actual/raw/P.png').convert('RGBA')); yy,xx=np.indices(a.shape[:2]); rgb=a[:,:,:3].astype(float)
poly=[(236,614),(304,617),(337,637),(337,663),(477,714),(521,726),(559,730),(592,753),(614,779),(625,796),(616,804),(600,808),(573,802),(531,792),(490,786),(440,773),(373,765),(309,750),(267,733),(251,715),(242,677)]
p=Image.new('L',(1024,1536));ImageDraw.Draw(p).polygon(poly,fill=255);roi=np.array(p)>0
skin=(rgb[:,:,0]>rgb[:,:,2]+25)&(rgb[:,:,0]>100)&(rgb[:,:,1]>60)&(a[:,:,3]>128)
lab,_=nd.label(nd.binary_closing(skin&roi,iterations=2));m=nd.binary_dilation(nd.binary_fill_holes(lab==lab[680,280]),iterations=2)&roi
# Full hand only from the anatomical wrist, no far bangle hand; P is anatomy only.
h=m&(xx>=491)
Image.fromarray((m*255).astype('uint8')).save(R/'P_NATIVE_BARE_NEAR_ARM_ONLY_MASK.png')
show=Image.fromarray(a).convert('RGB'); overlay=Image.new('RGBA',show.size);ov=np.zeros_like(a);ov[m]=[255,0,100,80];show=Image.alpha_composite(show.convert('RGBA'),Image.fromarray(ov));d=ImageDraw.Draw(show)
for name,pt in [('C source',(287,631)),('E source',(280,708)),('W source',(493,756))]:
 x,y=pt;d.ellipse((x-4,y-4,x+4,y+4),fill='cyan');d.text((x+6,y-14),name,fill='black',stroke_width=1,stroke_fill='white')
show.crop((180,560,790,850)).save(R/'ANATOMICAL_PALM_EXTRACTION_ACTUAL.png')
props=np.array(Image.open(B/'F036_REBUILD_FROM_ACTUAL030_ZERO_CALL_v1_20261019/layers/TRUE_ORIGINAL_PROPS_SAME_COMMON030_COORDS.png').convert('RGBA'))[:,:,3]>0
cloth=np.array(Image.open(B/'F036_COMPLETE_OLD_HAND_HOLE_RAW_RESTORE_ZERO_CALL_20261019/F048/FROM_ONE_COMPLETE_MASTER_CLOTH_RGBA.png').convert('RGBA'))[:,:,3]>128
ys,xs=np.nonzero(h);v=np.column_stack([xs-493,ys-756])*.90;C=np.array([174,611]);cand=[]
for wx in range(425,496,5):
 for wy in range(765,826,5):
  dist=np.linalg.norm(np.array([wx,wy])-C)
  if not abs(270-90)+3<dist<270+90-3:continue
  for deg in [-18,-12,-6,0,6,12]:
   z=np.deg2rad(deg);A=np.array([[np.cos(z),-np.sin(z)],[np.sin(z),np.cos(z)]]);q=np.rint(v@A.T+[wx,wy]).astype(int);qx,qy=q[:,0],q[:,1]
   hit=int(props[qy,qx].sum());support=float(cloth[qy,qx].mean());center=q.mean(0)
   if hit==0 and support>.99:cand.append({'wrist':[wx,wy],'deg':deg,'palm_center':center.tolist(),'distance':float(dist),'props_overlap':hit,'cloth_support':support,'score':float(np.linalg.norm(center-[550,826])+.04*abs(deg)+.2*abs(dist-341))})
cand.sort(key=lambda x:x['score']);report={'source_mask_pixels':int(m.sum()),'source_hand_pixels':int(h.sum()),'source_cuff':[287,631],'source_elbow':[280,708],'source_wrist':[493,756],'palm_scale':.90,'candidates':cand[:15]};(R/'PALM_CONTACT_PLACEMENT_PREFLIGHT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
