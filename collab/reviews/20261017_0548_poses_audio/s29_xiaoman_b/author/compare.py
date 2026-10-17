from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
p=Path('/tmp/laidian-produce-s29-xiaoman-b')
ap=Path('/tmp/laidian-produce-s29-xiaoman-a/anim_29_xiaoman_phone_look_a.png')
bp=p/'anim_29_xiaoman_phone_look_b.png'
ai=Image.open(ap).convert('RGB');bi=Image.open(bp).convert('RGB')
assert ai.size==bi.size,(ai.size,bi.size)
a=np.asarray(ai,dtype=np.int16);b=np.asarray(bi,dtype=np.int16)
d=np.abs(a-b);mx=d.max(axis=2)
def stats(mask):
 vals=d[mask];v=mx[mask]
 return {'pixels':int(mask.sum()),'mean_rgb_absolute_difference_0_to_255':float(vals.mean()),'max_channel_difference_gt_8_fraction':float((v>8).mean()),'max_channel_difference_gt_32_fraction':float((v>32).mean()),'exact_rgb_equal_fraction':float((v==0).mean())}
headbox=[200,70,840,655]
outside=np.ones(mx.shape,dtype=bool);outside[70:655,200:840]=False
regions={'lower_collar_boundary':[435,652,594,704],'torso_sleeves':[270,705,645,895],'left_hand_rod':[610,885,850,1035],'right_hand_support':[235,1180,425,1345],'lower_body':[75,1040,925,1350]}
metric={'a':str(ap),'b':str(bp),'dimensions':list(ai.size),'comparison_note':'Raw RGB at identical pixel coordinates; not proof of perceptual equivalence or in-scene alignment.','conservative_head_hair_neck_exclusion_box_xyxy':headbox,'outside_exclusion_box':stats(outside),'protected_regions':{}}
registration={}
for name,box in regions.items():
 x0,y0,x1,y1=box
 mask=np.zeros(mx.shape,dtype=bool);mask[y0:y1,x0:x1]=True
 metric['protected_regions'][name]={'box_xyxy':box,**stats(mask)}
 ar=a[y0:y1,x0:x1]
 scored=[]
 for dy in range(-4,5):
  for dx in range(-4,5):
   br=b[y0+dy:y1+dy,x0+dx:x1+dx]
   scored.append((float(np.abs(ar-br).mean()),dx,dy))
 score,dx,dy=min(scored)
 registration[name]={'box_xyxy':box,'searched_integer_dx_dy_range':[-4,4],'best_B_sampling_offset_dx_dy':[dx,dy],'best_rgb_mae':score,'zero_offset_rgb_mae':float(np.abs(ar-b[y0:y1,x0:x1]).mean()),'limitation':'Integer translation comparison only; no claim of subpixel equality, no affine/nonrigid registration.'}
(p/'pixel_comparison.json').write_text(json.dumps(metric,indent=2)+'\n')
(p/'registration_check.json').write_text(json.dumps(registration,indent=2)+'\n')
box=(210,85,825,715);w=box[2]-box[0];h=box[3]-box[1]
pair=Image.new('RGB',(w*2,h+28),'white');dr=ImageDraw.Draw(pair);dr.text((8,8),'A (accepted)',fill='black');dr.text((w+8,8),'B (candidate)',fill='black');pair.paste(ai.crop(box),(0,28));pair.paste(bi.crop(box),(w,28));pair.save(p/'evidence_head_pair.png')
cols=[('left hand + rod',(545,820,860,1045)),('right hand support',(230,1060,440,1360)),('lower collar',(435,652,594,704))]
width=sum(c[1][2]-c[1][0] for c in cols);height=2*max(c[1][3]-c[1][1] for c in cols)+60
canvas=Image.new('RGB',(width,height),'white');dr=ImageDraw.Draw(canvas);x=0
for name,box in cols:
 cw=box[2]-box[0];ch=box[3]-box[1]
 dr.text((x+4,6),'A '+name,fill='black');canvas.paste(ai.crop(box),(x,25))
 dr.text((x+4,331),'B '+name,fill='black');canvas.paste(bi.crop(box),(x,350));x+=cw
canvas.save(p/'evidence_protected_pair.png')
heat=np.zeros((mx.shape[0],mx.shape[1],3),dtype=np.uint8)
heat[:,:,0]=np.clip(mx*4,0,255).astype(np.uint8);heat[:,:,1]=np.clip(mx-64,0,191).astype(np.uint8)
Image.fromarray(heat).save(p/'difference_heatmap.png')
print(json.dumps(metric,indent=2));print(json.dumps(registration,indent=2))
