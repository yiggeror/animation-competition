from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import binary_erosion
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;B=R.parent.parent
ap=B/'astra_s09_clothing_review_20261018_1645/candidates/same_call05_continuous_cloth_pending_review.png';dp=B/'astra_s09_031_block_review_20261018_1543/originals/d06_call05_raw.png'
a=np.array(Image.open(ap).convert('RGBA'));d=np.array(Image.open(dp).convert('RGBA'));m=np.zeros(a.shape[:2],bool);rows=[]
def seg(v,y):
 q=v[y,:,3]>128;k=np.diff(np.r_[False,q,False].astype(int));runs=list(zip(np.flatnonzero(k==1),np.flatnonzero(k==-1)))
 return next((int(l),int(r-1)) for l,r in runs if l<800<r)
for y in range(820,941):
 al,ar=seg(a,y);dl,dr=seg(d,y)
 l0=min(al,dl)-16;l1=max(al,dl)+15;m[y,l0:l1]=1
 rr=None
 if y>=840:
  r0=min(ar,dr)-14;r1=max(ar,dr)+17;m[y,r0:r1]=1;rr=[r0,r1]
 rows.append(dict(y=y,left=[l0,l1],right=rr))
arm=np.array(Image.open(B/'astra_s09_clothing_review_20261018_1645/masks/complete_arms_sleeves_cuffs.png'))>0
m &= ~arm
b=a.copy();b[m]=d[m];Image.fromarray(m.astype('uint8')*255).save(R/'continuous_skirt_outer_edge_allowed_REFERENCE.png');Image.fromarray(b).save(R/'same_raw_corridor_DIAGNOSTIC_ONLY.png')
for bgname,bgc in [('gray','#697079'),('dark','#202830')]:
 z=Image.new('RGB',(1600,620),'#eee');drw=ImageDraw.Draw(z)
 for j,(arr,title) in enumerate([(a,'before'),(d,'same raw donor'),(b,'corridor DIAGNOSTIC'),(a,'allowed corridor')]):
  im=Image.alpha_composite(Image.new('RGBA',(1672,941),bgc),Image.fromarray(arr))
  if j==3:
   ov=Image.new('RGBA',im.size,(255,40,120,0));ov.putalpha(Image.fromarray(m.astype('uint8')*145));im.alpha_composite(ov)
  crop=im.convert('RGB').crop((520,760,1060,941));crop=crop.resize((400,134));z.paste(crop,(j*400,28));drw.text((j*400+8,6),title,fill='black')
  # independent left/right contour close crops, no panorama squeeze
  for row,box in enumerate([(595,810,659,881),(944,833,1008,901)]):
   q=im.convert('RGB').crop(box);q=q.resize((q.width*3,q.height*3));z.paste(q,(j*400+90,184+row*222))
 z.save(R/f'corridor_before_donor_after_mask_{bgname}.png')
# Edge-AA color at upper splice and inner side is identical in source/donor, so no arbitrary stopping in changed slope.
rep={'status':'REFERENCE_DIAGNOSTIC_ONLY_NOT_PRODUCTION','source_sha':hashlib.sha256(ap.read_bytes()).hexdigest(),'donor_sha':hashlib.sha256(dp.read_bytes()).hexdigest(),'allowed_pixels':int(m.sum()),'changed_pixels':int(np.any(a!=b,2).sum()),'alpha_changed':int(np.count_nonzero(a[:,:,3]!=b[:,:,3])),'outside_changed':int(np.count_nonzero(np.any(a!=b,2)&~m)),'complete_arm_guard_overlap':int(np.count_nonzero(m&arm)),'left_top_y820_RGBA_changes':int(np.count_nonzero(np.any(a[820]!=b[820],1))),'right_top_y840_RGBA_changes':int(np.count_nonzero(np.any(a[840,950:]!=b[840,950:],1))),'boundaries':'left follows source/donor skirt contour y820..940, outer16px+inner14px plus swept gap; right y840..940 likewise. Ends at source canvas bottom, never truncates diverging contour at y857. Source skin/arms/hands/prop are beyond corridor. Generic old outer contour/background hardlock must release only inside this semantic band.','rows':rows}
json.dump(rep,open(R/'corridor_contract.json','w'),indent=2);print({k:v for k,v in rep.items() if k!='rows'})
