"""Actual-image continuity diagnostics only. Never edits any character pixels."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib
O=Path(__file__).resolve().parents[1];S=O.parent;Q=O/'qa';old=S/'d03_F018_inputs_20261019/inputs/01_locked_F012.png';raw=O/'originals/F018_raw_call01.png';a=np.array(Image.open(old));b=np.array(Image.open(raw));assert a.shape==b.shape==(1536,1024,4)
font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
def flat(ar,col):return Image.alpha_composite(Image.new('RGBA',(1024,1536),(*col,255)),Image.fromarray(ar)).convert('RGB')
board=Image.new('RGB',(1024,1604),'white');d=ImageDraw.Draw(board)
for r,col in enumerate([(205,208,211),(36,38,42)]):
 for c,(ar,label) in enumerate([(a,'LOCKED NEW F012'),(b,'RAW F018 / ONE CALL')]):
  board.paste(flat(ar,col).resize((512,768)),(c*512,r*802+34));d.text((c*512+10,r*802+7),label,font=font(18),fill='black')
board.save(Q/'04_new_locked012_to018_same_canvas_gray_dark.jpg',quality=95)
for name,box,scale in [('05_locked_tip_color_fold_actual4x.jpg',(453,928,542,1062),4),('06_locked012_to018_whole_arm_actual2x.jpg',(600,650,1024,1066),2)]:
 w=(box[2]-box[0])*scale;h=(box[3]-box[1])*scale;board=Image.new('RGB',(w*2,h+34),'#cdd0d3');d=ImageDraw.Draw(board)
 for c,(ar,label) in enumerate([(a,'LOCKED F012'),(b,'RAW F018')]):board.paste(flat(ar,(205,208,211)).crop(box).resize((w,h),Image.Resampling.NEAREST),(c*w,34));d.text((c*w+10,7),label,font=font(20),fill='black')
 board.save(Q/name,quality=96)
ref=S/'d02_F012_20261019/placket_tip_fix_20261019/masks';samples={}
for name in ['lit_matched_blue_core','shade_matched_blue_core','shade_matched_flower_core']:
 m=np.array(Image.open(ref/(name+'.png')))>0
 delta=b[m,:3].astype(float).mean(0)-a[m,:3].astype(float).mean(0)
 samples[name]={'pixels':int(m.sum()),'locked012_mean_RGB':a[m,:3].mean(0).tolist(),'raw018_mean_RGB':b[m,:3].mean(0).tolist(),'raw018_minus_locked012_mean_RGB':delta.tolist(),'caveat':'Same-coordinate locked012 reference core, diagnostic only. Any motif/edge displacement can affect means; no per-pixel matching or color correction performed.'}
report={'locked012_SHA256':hashlib.sha256(old.read_bytes()).hexdigest(),'raw018_SHA256':hashlib.sha256(raw.read_bytes()).hexdigest(),'same_canvas':[1024,1536],'fixed_registration':{'scale':.7,'x':275,'y':112},'protected_unchanged_pose_pixel_identity_claimed':False,'placket_tip_static_reference_samples':samples,'spatial_or_color_edits_applied':False,'scene_renders':0,'provisional_visual_review':'Full head/body/near hand/kneeling shoes remain in corresponding same-canvas positions. Shoulder is hidden; continuity must be judged from actual whole sleeve/elbow/wrist drawing, not construction coordinates alone. Native review fails finger-rod gap and hair/blue fixed-mother color gates.'}
(Q/'locked012_continuity_and_tip.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(samples,indent=2))
