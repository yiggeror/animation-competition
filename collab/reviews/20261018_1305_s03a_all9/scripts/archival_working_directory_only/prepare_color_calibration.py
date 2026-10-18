from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
from scipy.ndimage import label,distance_transform_edt
R=Path(__file__).resolve().parent;O=R/'color_calibration_v2';O.mkdir(exist_ok=True)
ref=np.array(Image.open(R/'candidates/S03a_F000.png').convert('RGBA'));H,W=ref.shape[:2];Y,X=np.indices((H,W));ts=np.array([.15,.5,.7,.85,.93]);nose_ref=(836,619);chin_ref=(837,731)
def samples(a,nose,chin):
 out=[]
 for t in ts:
  x=int(nose[0]+t*(chin[0]-nose[0]));y=int(nose[1]+t*(chin[1]-nose[1]));v=[]
  for dx in [-max(1,int(20*(1-t))),max(1,int(20*(1-t)))]:v.append(a[y-3:y+4,x+dx-4:x+dx+5,:3].reshape(-1,3))
  out.append(np.median(np.concatenate(v),axis=0))
 return np.array(out)
refs=samples(ref,nose_ref,chin_ref);report={'status':'ZERO_CALL_COLOR_PROPOSAL_ONLY__LOCKED_ORIGINALS_UNCHANGED','reference':'S03a_F000 original focus skin palette','strength':.8,'method':'Low-frequency vertical RGB offset from paired skin samples along nose-to-chin axis; skin-connected lower-face semantic mask; no geometry/alpha/neck/body/ink edits','poses':{}}
for master,frames,nose,chin,seed in [('014',['014','025'],(754,617),(785,725),(780,700)),('017',['017','021','023'],(675,603),(737,722),(730,700))]:
 b=np.array(Image.open(R/f'candidates/S03a_F{master}.png').convert('RGBA'));meas=samples(b,nose,chin);delta=(refs-meas)*.8
 avail=(b[:,:,0]>175)&(b[:,:,1]>140)&(b[:,:,2]>115)&(b[:,:,3]>245)&(Y>=nose[1])&(Y<chin[1]+8)&(X>580)&(X<1005)
 lab,n=label(avail);face=lab==lab[seed[1],seed[0]];face&=avail
 # The exact generated tiny mouth and dark facial ink remain unchanged.
 ink=(b[:,:,:3].max(axis=2)-b[:,:,:3].min(axis=2)<30)&(b[:,:,:3].mean(axis=2)<150);face&=~ink
 jaw_pts=([(640,620),(650,646),(670,674),(690,695),(710,709),(740,721),(770,728),(800,725),(830,716),(860,703),(890,686),(920,661),(945,634),(955,607)] if master=='014' else [(620,664),(640,684),(660,699),(680,710),(700,720),(720,725),(740,726),(760,722),(780,716),(800,708),(820,699),(840,687),(860,673),(880,649),(895,620)])
 expected=np.interp(np.arange(W),[p[0] for p in jaw_pts],[p[1] for p in jaw_pts]);jaw=expected.copy();lum=b[:,:,:3].mean(axis=2)
 for col in range(jaw_pts[0][0],jaw_pts[-1][0]+1):
  yy=np.arange(max(nose[1],int(expected[col])-8),min(H,int(expected[col])+9));ink_y=yy[lum[yy,col]<120]
  if len(ink_y):jaw[col]=ink_y[np.argmin(abs(ink_y-expected[col]))]
 face&=(Y<jaw[None,:]-1)&(X>=jaw_pts[0][0])&(X<=jaw_pts[-1][0]);soft=np.clip((distance_transform_edt(face)-.5)/3,0,1);t=np.clip((Y-nose[1])/(chin[1]-nose[1]),0,1)
 control=np.r_[0,ts,1.0];corr=np.stack([np.interp(t,control,np.r_[0,delta[:,k],delta[-1,k]]) for k in range(3)],axis=2)
 Image.fromarray(np.rint(soft*255).astype('uint8')).save(O/f'F{master}__lower_face_semantic_mask.png');report['poses'][master]={'nose':nose,'chin':chin,'reference_samples':refs.tolist(),'source_samples':meas.tolist(),'offsets_rgb':delta.tolist(),'semantic_mask_pixels':int(face.sum()),'frames':frames}
 for f in frames:
  a=np.array(Image.open(R/f'candidates/S03a_F{f}.png').convert('RGBA'));out=a.copy();out[:,:,:3]=np.clip(np.rint(a[:,:,:3]+corr*soft[:,:,None]),0,255).astype('uint8');out[:,:,3]=a[:,:,3]
  # Keep each mouth-patch area unchanged; correction feathers around preserved mouth ink only.
  if f=='025':mi=np.array(Image.open(R/'masks/F025__mouth_soft.png'))>0;out[mi&(a[:,:,:3].mean(axis=2)<150)]=a[mi&(a[:,:,:3].mean(axis=2)<150)]
  changed=np.any(out!=a,axis=2);assert not np.any(changed&(soft==0));p=O/f'S03a_F{f}_color_v2.png';Image.fromarray(out).save(p);report.setdefault('outputs',{})[f]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'changed_pixels':int(changed.sum()),'alpha_changed':0,'outside_face_mask_changed':0}
(O/'color_calibration_manifest.json').write_text(json.dumps(report,indent=2))
# Same camera and same closeups, originals on top, proposal below.
board=Image.new('RGB',(1440,1020),'white');d=ImageDraw.Draw(board)
for row in range(2):
 for k,(f,x,y) in enumerate([('014',780,725),('017',737,722),('025',780,725),('028',837,731)]):
  p=(O/f'S03a_F{f}_color_v2.png') if row and f!='028' else R/f'candidates/S03a_F{f}.png';i=Image.open(p).convert('RGBA');bg=Image.alpha_composite(Image.new('RGBA',i.size,(239,239,232,255)),i).convert('RGB');d.text((360*k+10,510*row+8),f+(' SOURCE ORIGINAL' if not row else ' COLOR PROPOSAL / SAME GEOMETRY'),fill='black');board.paste(bg.crop((x-120,y-170,x+120,y+135)).resize((360,458)),(360*k,510*row+40))
board.save(O/'F014_F017_F025_F028__color_before_after.png');print(json.dumps(report,indent=2))
