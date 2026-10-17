"""Final phone-only registration: hard upper shell edge orientation + camera location.
The joint gray-intensity fit is discarded because changed antialiasing/background
gave spurious scale/rotation. This fit uses the physical edge and camera contour.
All input sizes match master, so scale is fixed to1; contact checks are held out.
"""
from pathlib import Path
import json,math,importlib.util
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter1d
from scipy.stats import theilslopes

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('ncc',ROOT/'measure_phone_anchors.py');ncc=importlib.util.module_from_spec(spec);spec.loader.exec_module(ncc)
POINTS=[[1410,528],[1379,614]]
CAMERA=(1453,539); CAMERA_BOX=(-14,-11,14,10)

def edge(rgb):
    a=np.asarray(Image.fromarray(rgb.astype('uint8')).convert('L'),float)
    xs=np.arange(1392,1464);ys=[]
    for x in xs:
        ey=523-.15625*(x-1410);y0=round(ey)-3
        v=a[y0-2:y0+9,x];g=gaussian_filter1d(v,.65,order=1)
        i=2+np.argmin(g[2:-2]);l=i+.5*(g[i-1]-g[i+1])/(g[i-1]-2*g[i]+g[i+1]);ys.append(l+y0-2)
    med=theilslopes(ys,xs-1418)
    err=np.array(ys)-(med[0]*(xs-1418)+med[1]);keep=abs(err)<.5
    slope,intercept=np.polyfit((xs-1418)[keep],np.array(ys)[keep],1)
    return {'slope':slope,'center_y_at_x1418':intercept,'deg':math.degrees(math.atan(slope)),'inliers':int(keep.sum()),'samples':[[int(x),float(y),bool(ok)]for x,y,ok in zip(xs,ys,keep)]}

me=edge(ncc.M)
rows=[]
for path in [ncc.MASTER]+sorted((ROOT/'raw').glob('*.png')):
    C=ncc.composite(path);e=edge(C);hit,score,_=ncc.match(C,CAMERA,CAMERA_BOX,False)
    deg=e['deg']-me['deg'];ang=math.radians(deg);c,s=math.cos(ang),math.sin(ang);R=np.array([[c,-s],[s,c]])
    def forward(p):return (np.asarray(p)-CAMERA)@R.T+hit
    def inverse(p):return (np.asarray(p)-hit)@R+CAMERA
    checks=[]
    for label,ref,box in zip(['near_elbow','far_elbow','hem'],ncc.POINTS[2:],ncc.OFFSETS[2:]):
        pos,q,_=ncc.match(C,ref,box,False);reg=inverse(pos)
        checks.append({'label':label,'reference':ref,'measured':pos,'ncc_score':q,'registered':reg.tolist(),'residual_px':float(np.linalg.norm(reg-ref))})
    rows.append({'file':'x01_prone_phone_k01' if path==ncc.MASTER else path.stem,'anchors':forward(POINTS).tolist(),'phone_edge':e,'camera_center':hit,'camera_ncc_score':score,'fit_source_from_master':{'deg':deg,'scale':1},'checks':checks,'near_elbow_under_3px':checks[0]['residual_px']<=3})
result={'method':__doc__,'target':{'width':1536,'height':1024,'anchors':POINTS},'camera_reference':CAMERA,'camera_window':CAMERA_BOX,'master_edge':me,'frames':rows}
(ROOT/'anchors_final.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
for r in rows:print(r['file'],'camera ncc %.3f'%r['camera_ncc_score'],'angle %.4f'%r['fit_source_from_master']['deg'],'checks',[round(c['residual_px'],3) for c in r['checks']])
vis=Image.fromarray(ncc.M.astype('uint8'));d=ImageDraw.Draw(vis)
for x,y,ok in me['samples']:
    if ok:d.ellipse((x-1,y-1,x+1,y+1),fill=(0,255,255))
x,y=CAMERA;a,b,c,e=CAMERA_BOX;d.rectangle((x+a,y+b,x+c,y+e),outline=(255,0,255));d.ellipse((x-2,y-2,x+2,y+2),fill=(255,0,255))
vis.crop((1300,485,1510,650)).resize((840,660)).save(ROOT/'diagnostics/final_edge_camera_reference.png')
