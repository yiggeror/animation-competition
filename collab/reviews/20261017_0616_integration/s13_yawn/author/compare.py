from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
p=Path('/tmp/laidian-produce-s13-yawn')
ap=Path('/tmp/laidian-produce-s13-stare/anim_13_xiaoman_stare.png');bp=p/'anim_13_xiaoman_yawn.png'
ai=Image.open(ap).convert('RGB');bi=Image.open(bp).convert('RGB')
assert ai.size==bi.size
a=np.asarray(ai,dtype=np.int16);b=np.asarray(bi,dtype=np.int16)
d=np.abs(a-b);mx=d.max(axis=2);H,W=mx.shape
headbox=[30,80,970,1085]
outside=np.ones((H,W),dtype=bool);outside[80:1085,30:970]=False
regions={'collar_lower':[300,1080,750,1165],'near_shoulder_sleeve':[80,1060,370,1400],'far_shoulder_sleeve':[750,1045,950,1390],'chest_dots':[380,1190,750,1450],'bust_lowercut':[140,1410,900,1505],'body_registration_anchor':[70,1090,950,1505]}
def stats(mask):
 vals=d[mask];v=mx[mask]
 return {'pixels':int(mask.sum()),'mean_rgb_absolute_difference_0_to_255':float(vals.mean()),'max_channel_difference_gt_8_fraction':float((v>8).mean()),'max_channel_difference_gt_32_fraction':float((v>32).mean()),'exact_rgb_equal_fraction':float((v==0).mean())}
metric={'a':str(ap),'b':str(bp),'dimensions':list(ai.size),'comparison_note':'Raw RGB at identical native coordinates, no alignment applied to candidate.','conservative_head_hair_neck_exclusion_box_xyxy':headbox,'outside_exclusion_box':stats(outside),'protected_regions':{}}
reg={}
for name,box in regions.items():
 x0,y0,x1,y1=box;mask=np.zeros((H,W),dtype=bool);mask[y0:y1,x0:x1]=True
 metric['protected_regions'][name]={'box_xyxy':box,**stats(mask)}
 ar=a[y0:y1,x0:x1];scores=[]
 for dy in range(-64,65,4):
  for dx in range(-12,13,4):
   if not(0<=x0+dx<x1+dx<=W and 0<=y0+dy<y1+dy<=H):continue
   scores.append((float(np.abs(ar[::4,::4]-b[y0+dy:y1+dy:4,x0+dx:x1+dx:4]).mean()),dx,dy))
 _,cx,cy=min(scores);fine=[]
 for dy in range(cy-3,cy+4):
  for dx in range(cx-3,cx+4):
   if not(0<=x0+dx<x1+dx<=W and 0<=y0+dy<y1+dy<=H):continue
   fine.append((float(np.abs(ar-b[y0+dy:y1+dy,x0+dx:x1+dx]).mean()),dx,dy))
 score,dx,dy=min(fine)
 reg[name]={'box_xyxy':box,'search_method':'Coarse dx +/-12, dy +/-64, grid step4 at spatial subsampling4; then +/-3 full-resolution integer refinement around best coarse point.','best_B_sampling_offset_dx_dy':[dx,dy],'best_rgb_mae':score,'zero_offset_rgb_mae':float(np.abs(ar-b[y0:y1,x0:x1]).mean()),'candidate_translation_to_align_A':[-dx,-dy],'limitation':'Integer translation estimate for stated ROI only; not proof of subpixel or nonrigid equivalence; transform not applied to deliverable.'}
(p/'pixel_comparison.json').write_text(json.dumps(metric,indent=2)+'\n');(p/'registration_check.json').write_text(json.dumps(reg,indent=2)+'\n')
def pair(box,name,bbox=None,blabel='B (raw same coordinates)'):
 x0,y0,x1,y1=box;w=x1-x0;h=y1-y0
 im=Image.new('RGB',(2*w,h+28),'white');dr=ImageDraw.Draw(im);dr.text((8,8),'A (accepted)',fill='black');dr.text((w+8,8),blabel,fill='black');im.paste(ai.crop(box),(0,28));im.paste(bi.crop(bbox or box),(w,28));im.save(p/name)
pair((40,90,970,1110),'evidence_head_pair.png')
pair((270,925,780,1190),'evidence_collar_raw_pair.png')
pair((50,980,975,1500),'evidence_body_raw_pair.png')
dx,dy=reg['body_registration_anchor']['best_B_sampling_offset_dx_dy']
box=(50,980,975,1500);bbox=(box[0]+dx,box[1]+dy,box[2]+dx,box[3]+dy)
pair(box,'evidence_body_registered_pair.png',bbox,f'B sampled dx={dx},dy={dy} (analysis only)')
heat=np.zeros((H,W,3),dtype=np.uint8);heat[:,:,0]=np.clip(mx*4,0,255).astype(np.uint8);heat[:,:,1]=np.clip(mx-64,0,191).astype(np.uint8);Image.fromarray(heat).save(p/'difference_heatmap.png')
print(json.dumps(metric,indent=2));print(json.dumps(reg,indent=2))
