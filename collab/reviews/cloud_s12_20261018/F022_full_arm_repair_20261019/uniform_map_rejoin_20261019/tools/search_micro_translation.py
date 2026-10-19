"""Finite <=1native whole-arm phase search; raw alpha only, no isolated digit changes."""
from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import map_coordinates
import numpy as np,json
O=Path(__file__).resolve().parents[1];T=O/'qa/registration_trials';T.mkdir(exist_ok=True);raw=np.array(Image.open(O.parent/'originals/F022_far_arm_patch_call01_raw.png'));body=np.array(Image.open(O/'candidate/static022_old_far_arm_removed.png'));props=np.array(Image.open(O/'actual_scene/F022_code_props_actual_layer.png'));old=json.loads((O/'qa/semantic_thumb_selection.json').read_text());tm=Image.new('L',(1024,1536));ImageDraw.Draw(tm).polygon([tuple(p) for p in old['original_arm_thumb_plus_pad_polygon_native_raw']],fill=255);ts=np.array(tm)>0
M=np.array([[.435717950246291,.061236164422429,523.198762766005],[-.061236164422429,.435717950246291,572.695273541552],[0,0,1.]])
y,x=np.indices((120,154));nx=x+870;ny=y+880;q=np.stack([nx+.5,ny+.5,np.ones_like(x)],2);wy,wx=np.indices((80,100));sx=wx+900;sy=wy+730;sample=[(sy+.5-112)/.7-.5-880,(sx+.5-275)/.7-.5-870]
py,px=np.indices((1080,1920));pworld=np.stack([px+.5,py+.5],2)
def rod(A,B):
 A=np.array(A);B=np.array(B);v=B-A;t=np.clip(((pworld-A)@v)/(v@v),0,1);return(props[:,:,3]>0)&(np.linalg.norm(pworld-A-t[:,:,None]*v,axis=2)<5.5)&(px>=925)&(px<=1005)
u=rod([934.312497676,785.129739577],[1497.531490504,714.664205296]);l=rod([951.261694392,798.906335746],[1282.198690556,773.946794448]);local=u[730:810,900:1000];edge=np.zeros_like(local);edge[:-1]=local[1:];edge&=~local;target=(sx>=957)&(sx<=958)
points=np.stack([sx.ravel(),sy.ravel()],1)
def field(mask):
 y,x=np.nonzero(mask);r=np.stack([x,y],1);dd=np.maximum(abs(points[:,None,:]-r[None,:,:])-1,0);return np.sqrt(np.sum(dd*dd,2).min(1)).reshape(80,100)
uf=field(u);lf=field(l)
(O/'qa/registration_probe_fields.json').write_text(json.dumps({'upper_field':uf.ravel().tolist(),'lower_field':lf.ravel().tolist(),'upper_mask':local.astype(int).ravel().tolist(),'edge_target':(edge&target).astype(int).ravel().tolist()},separators=(',',':')))
def make(delta):
 m=M.copy();m[:2,2]+=delta;p=q@np.linalg.inv(m).T;arm=np.rint(np.clip(map_coordinates(raw[:,:,3]/255,[p[:,:,1]-.5,p[:,:,0]-.5],order=1,mode='constant',cval=0),0,1)*255);ba=body[880:1000,870:1024,3];al=np.rint(arm+ba*(255-arm)/255).astype(np.uint8);ix=np.clip(np.floor(p[:,:,0]).astype(int),0,1023);iy=np.clip(np.floor(p[:,:,1]).astype(int),0,1535);thumb=ts[iy,ix]&(nx>=930)&(ny>=915)&(ny<985);th=al*thumb;ot=al*(~thumb);tw=np.rint(map_coordinates(th.astype(float),sample,order=1,mode='constant',cval=0)).astype(np.uint8);ow=np.rint(map_coordinates(ot.astype(float),sample,order=1,mode='constant',cval=0)).astype(np.uint8);return th,ot,tw,ow
rows=[]
for dx in np.round(np.arange(-1,1.001,.1),6):
 for dy in np.round(np.arange(-1,1.001,.1),6):
  norm=float(np.hypot(dx,dy))
  if norm>1.00001:continue
  th,ot,tw,ow=make([dx,dy]);vis=tw>=128;other=ow>0;gap=float(uf[other].min());touch=bool(np.any(vis&edge&target));over=int(np.count_nonzero(vis&local))
  if (dx==0 and dy==0) or(touch and over==0 and gap>=1):rows.append({'delta':[float(dx),float(dy)],'norm':norm,'software_non_thumb_gap':gap,'software_visible_contact':touch,'software_visible_overlap':over,'software_AA_overlap':int(np.count_nonzero((tw>0)&local))})
rows.sort(key=lambda r:(-r['software_non_thumb_gap'],r['norm']));assert len(rows)>1,'No bounded trial retains visible first touch.';chosen=[next(r for r in rows if r['norm']==0)]+[r for r in rows if r['norm']>0][:24];manifest=[]
for i,row in enumerate(chosen):
 th,ot,tw,ow=make(row['delta']);paths=[]
 for name,alpha in [('thumb',th),('non_thumb',ot)]:
  a=np.zeros((1536,1024,4),np.uint8);a[:,:,:3]=255;a[880:1000,870:1024,3]=alpha;p=T/f'trial{i:02d}_{name}.png';Image.fromarray(a).save(p);paths.append(str(p.relative_to(Path.cwd())))
 manifest.append(row|{'id':i,'paths':paths})
(O/'qa/registration_trials_manifest.json').write_text(json.dumps({'diagnostic_only':True,'software_is_not_actual_Canvas_acceptance':True,'trials':manifest},indent=2)+'\n');print(json.dumps({'trials':len(manifest),'best_software_gap':max(r['software_non_thumb_gap'] for r in manifest),'zero':manifest[0],'first3':manifest[1:4]},indent=2))
