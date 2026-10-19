from pathlib import Path
import sys,json,numpy as np
from PIL import Image
from scipy.ndimage import binary_erosion,distance_transform_edt,map_coordinates
from scipy.optimize import least_squares
P=Path(__file__).resolve().parent;F=P/f'F{int(sys.argv[1]):03}';A=np.array(Image.open(F/'raw_original.png').convert('RGBA'));B=np.array(Image.open(P/'F045/S20_F045_accepted.png').convert('RGBA'));H,W=B.shape[:2];pad=A.shape[1]==W-1
if pad:T=np.zeros_like(B);T[:,:W-1]=A;A=T
assert A.shape==B.shape;y,x=np.indices(A.shape[:2]);m=(A[:,:,3]>180)&(x>1000);ref=(B[:,:,3]>180)&(x>995);edge=m&~binary_erosion(m);ys,xs=np.where(edge&(x>1012)&((y<245)|(y>470)));pts=np.stack([xs,ys],1)[::3];dist=distance_transform_edt(~(ref&~binary_erosion(ref)))
def fun(p):
 s,t,dx,dy=p;Q=s*np.array([[np.cos(t),-np.sin(t)],[np.sin(t),np.cos(t)]]);q=pts@Q.T+np.array([dx,dy]);return np.minimum(map_coordinates(dist,[q[:,1],q[:,0]],order=1,cval=40),40)
r=least_squares(fun,[.98,0,20,25],bounds=([.91,-.025,-30,-15],[1.05,.025,80,90]),loss='soft_l1',f_scale=3,max_nfev=180);s,t,dx,dy=r.x;Q=s*np.array([[np.cos(t),-np.sin(t)],[np.sin(t),np.cos(t)]]);M=np.column_stack([Q,[dx,dy]]);inv=np.linalg.inv(Q);R=np.array(Image.fromarray(A).transform((W,H),Image.Transform.AFFINE,tuple(np.column_stack([inv,-inv@np.array([dx,dy])]).ravel()),Image.Resampling.BICUBIC));Image.fromarray(R).save(F/'whole_native_G_registered.png');report={'matrix':M.tolist(),'median_boundary_residual_px':float(np.median(fun(r.x))),'scope':'one uniform whole-G head torso support fit; no local palm transform','raw_size':[W-1 if pad else W,H],'far_right_only_transparent_column_pad':pad};(F/'whole_G_registration.json').write_text(json.dumps(report,indent=2)+'\n');bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(R));bg.crop((840,260,1195,465)).resize((1420,820)).convert('RGB').save(F/'registered_raw_contacts_4x.jpg');print(report)
