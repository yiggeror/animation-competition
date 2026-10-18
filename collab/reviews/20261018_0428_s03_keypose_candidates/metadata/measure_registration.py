from PIL import Image
from pathlib import Path
import json
import numpy as np
from scipy.signal import correlate2d
root=Path(__file__).resolve().parent.parent
files=sorted((root/'originals').glob('*.png'))
def gray(p):
 im=Image.open(p).convert('RGBA'); c=np.asarray(Image.alpha_composite(Image.new('RGBA',im.size,(96,96,96,255)),im).convert('RGB'),dtype=float)
 return c@[.299,.587,.114]
def match(ref,tar,point,r=20,search=25):
 x,y=point; patch=ref[y-r:y+r+1,x-r:x+r+1]; patch-=patch.mean(); y0=y-r-search;x0=x-r-search; area=tar[y0:y+r+search+1,x0:x+r+search+1];ones=np.ones(patch.shape);s=correlate2d(area,ones,mode='valid');sq=correlate2d(area*area,ones,mode='valid');ss=np.maximum(sq-s*s/patch.size,1e-12);corr=correlate2d(area,patch,mode='valid')/np.sqrt(ss*np.sum(patch*patch));dy,dx=np.unravel_index(np.argmax(corr),corr.shape);return [int(x0+dx+r),int(y0+dy+r)],float(corr[dy,dx])
ref=gray(files[0]);anchors={'A_left_basin_rim':[558,850],'B_right_basin_rim':[1118,850],'H_first_shirt_button':[838,545]};rows=[]
for p in files:
 tar=gray(p);m={k:{'xy':(v if p==files[0] else match(ref.copy(),tar,v)[0]),'ncc':(1. if p==files[0] else match(ref.copy(),tar,v)[1])} for k,v in anchors.items()}; A=complex(*m['A_left_basin_rim']['xy']);B=complex(*m['B_right_basin_rim']['xy']); H=complex(*m['H_first_shirt_button']['xy']); refA=complex(*anchors['A_left_basin_rim']);refB=complex(*anchors['B_right_basin_rim']);refH=complex(*anchors['H_first_shirt_button']);a=(refB-refA)/(B-A);b=refA-a*A;res=a*H+b-refH;rows.append({'file':p.name,'anchors_native_px':m,'candidate_to_k01_similarity':{'complex_a':[a.real,a.imag],'translation_xy':[b.real,b.imag],'scale':abs(a),'rotation_degrees':float(np.degrees(np.angle(a)))},'independent_H_residual_px':abs(res),'independent_H_residual_xy':[res.real,res.imag]})
hand=[]
r6=gray(files[5]);r7=gray(files[6])
for name,point in {'palm_contact':[274,746],'melon_center':[278,697]}.items():
 xy,ncc=match(r6.copy(),r7,point,r=25,search=20);hand.append({'feature':name,'k06_xy':point,'k07_matched_xy':xy,'ncc':ncc,'delta_px':[xy[0]-point[0],xy[1]-point[1]]})
out={'method':'Read-only normalized grayscale template correlation after proper alpha-over-RGB(96,96,96), 41x41 patches and +/-25px search. A/B are manually seeded basin-rim landmarks, fit similarity only from A/B. Independent H is first shirt button and is NOT used in fit. No deliverable pixels transformed. Pixel estimates are approximate, not hand-traced ground truth. NCC confidence reports local shape compatibility, not full-body validity.','reference':files[0].name,'reference_anchors':anchors,'rows':rows,'k06_k07_hold_contact_check':hand,'limits':'Basin endpoints are locally stable enough for a rough registration test, but top/headroom, different object/body proportions vs source shot, flower drift, plate jumps and lighting mismatch are NOT cured by the fit. H alone never constitutes acceptance.'};(root/'metadata/registration.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
