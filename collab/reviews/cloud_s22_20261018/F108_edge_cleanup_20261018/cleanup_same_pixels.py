#!/usr/bin/env python3
"""Only the authorized108 ROI: retain real diagonal ink, remove clamped drag."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
SRC=ROOT/'fourth_push_108_114/F108/candidate/F108_final_edge_aligned.png'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()=='d80948993838a76c0ea788e7111e9c245b9457c34dea2fb9da49ddc1080b74f0'
a=np.array(Image.open(SRC).convert('RGBA'));out=a.copy();h,w=a.shape[:2]
profile=np.load(ROOT/'fourth_push_108_114/F108/provenance/forearm_map_edge_aligned.npz')['target_profiles']
# Genuine existing diagonal ink through floor(bottom)+1 remains byte-identical.
# Continue only its exterior AA using the same drawing's next intact column.
# The repeated clamped last-row pixels below this finite edge are cleared.
donor_alpha=a[924:929,167,3].copy()
preserved_core=[]
for x in range(158,166):
 last=int(np.floor(profile[x,3]))+1
 preserved_core.append([x,last])
 for y in range(last+1,941):
  j=y-last-1
  if j<len(donor_alpha):out[y,x,3]=min(int(out[y,x,3]),int(donor_alpha[j]))
  else:out[y,x]=0
 assert np.array_equal(out[913:last+1,x],a[913:last+1,x])
# Column166 contains the stray tip plus a semi-opaque drag, not a second real
# contour. Reconnect it with the immediately adjacent intact same-source strip.
# The intended two edge positions differ by just0.108 native pixel.
out[913:929,166]=a[913:929,167]
out[929:941,166:168]=0
changed=np.any(out!=a,axis=2);yy,xx=np.where(changed)
roi=np.zeros((h,w),bool);roi[913:941,158:168]=True
assert np.any(changed) and not np.any(changed&~roi)
assert np.array_equal(out[:,520:],a[:,520:])
for y in [914,915,916]:assert np.array_equal(out[y,166],a[y,167])
(HERE/'candidate').mkdir(exist_ok=True);(HERE/'masks').mkdir(exist_ok=True)
dest=HERE/'candidate/F108_edge_fixed.png';Image.fromarray(out).save(dest)
Image.fromarray(changed.astype(np.uint8)*255).save(HERE/'masks/actual_changed.png')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
crop=(145,890,185,941)
for kind,c in [('gray',(115,115,115)),('dark',(32,32,32)),('white',(255,255,255))]:
 board=Image.new('RGB',(1200,797),(25,25,25));d=ImageDraw.Draw(board)
 for i,(label,b) in enumerate([('Frozen108 before',a),('Same-pixel edge cleanup',out)]):
  im=Image.fromarray(b).crop(crop);plate=Image.new('RGBA',im.size,(*c,255));plate.alpha_composite(im);plate=plate.convert('RGB').resize((600,765));board.paste(plate,(600*i,32));d.text((600*i+8,5),label,font=font,fill='white')
 board.save(HERE/'qa'/f'before_after_{kind}_15x.png')
 im=Image.new('RGBA',(w,h),(*c,255));im.alpha_composite(Image.fromarray(out));im.convert('RGB').save(HERE/'qa'/f'F108_after_on_{kind}.png')
record=dict(source=str(SRC.relative_to(ROOT)),source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),candidate=str(dest.relative_to(ROOT)),candidate_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),authorized_roi_inclusive=[158,913,167,940],actual_changed_bounds_inclusive=[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())],changed_pixels=int(changed.sum()),outside_ROI_RGBA_exact=True,contact_group_RGBA_exact=True,real_diagonal_ink_core_unchanged=preserved_core,donor_alpha_source=dict(x=167,rows=[924,928],values=donor_alpha.tolist()),tip_repair_same_source_strip=dict(source_x=167,target_x=166,rows=[913,928]),tip_914_916_removed=True,other_pose_F114_unchanged_sha256='74b692c116bf4d72e7d0fb684910b852e4c91ed32cfbe84d704e22a44f217112',image_generation_calls=0)
(HERE/'provenance/cleanup_checks.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
