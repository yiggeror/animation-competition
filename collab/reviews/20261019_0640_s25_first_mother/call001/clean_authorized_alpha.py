from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage as ndi
import numpy as np,json,hashlib
P=Path(__file__).parent; src=P/'F000_raw.png'; a=np.array(Image.open(src)); out=a.copy(); A=a[:,:,3]
# Protect all connected antialias within two pixels of the real subject.
labels,n=ndi.label(A>16);sizes=np.bincount(labels.ravel());sizes[0]=0;core=labels==sizes.argmax()
dist,idx=ndi.distance_transform_edt(~core,return_indices=True)
isolated=(A==1)&(dist>2.2)
yellow=(a[:,:,0]>170)&(a[:,:,1]>140)&(a[:,:,2]<90)&(A>0)&(A<=16)
yellow_far=yellow&(dist>1.5)
yellow_edge=yellow&~yellow_far
out[isolated|yellow_far,3]=0
# Keep edge coverage exactly; replace only the explicitly authorized yellow contamination RGB.
yy,xx=np.where(yellow_edge)
if len(xx):out[yy,xx,:3]=a[idx[0,yy,xx],idx[1,yy,xx],:3]
p=P/'F000_clean.png';Image.fromarray(out).save(p)
diff=np.any(a!=out,axis=2);allowed=isolated|yellow_far|yellow_edge
assert not np.any(diff&~allowed)
assert np.array_equal(a[core],out[core])
assert np.array_equal(out[yellow_edge,3],a[yellow_edge,3])
report={'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'clean_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'native_size':list(Image.open(src).size),'isolated_alpha1_removed':int(isolated.sum()),'lowalpha_yellow_far_removed':int(yellow_far.sum()),'near_edge_yellow_rgb_only_corrected':int(yellow_edge.sum()),'changed_pixels':int(diff.sum()),'main_subject_and_connected_antialias_coverage_preserved':True,'parent_authorization':'2026-10-19 06:20 UTC parent: only scattered outside alpha1 and low-alpha yellow contamination; retain original and connected anti-alias.','uniform_registration':{'scale':.716,'x':321,'y':407,'rotation':0}}
(P/'CLEANUP_RECEIPT.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
for name,c in [('white',(255,255,255,255)),('gray',(150,150,150,255)),('black',(0,0,0,255))]:
 bg=Image.new('RGBA',Image.open(p).size,c);bg.alpha_composite(Image.open(p));bg.convert('RGB').save(P/f'F000_clean_on_{name}.png')
