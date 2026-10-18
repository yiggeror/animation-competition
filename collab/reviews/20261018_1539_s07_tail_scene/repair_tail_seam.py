from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
B=Path.cwd();P=B/'astra_opening_drawn_review_20261018_0930/S07_phone_occlusion_1515/selected50';O=B/'astra_s07_tail_repair_20261018_1531/v3';(O/'candidates').mkdir(exist_ok=True);(O/'masks').mkdir(exist_ok=True);(O/'review').mkdir(exist_ok=True)
m=json.loads((P/'manifest.json').read_text());rot=np.array(Image.open(P/'tail_rigid_CCW50.png').convert('RGBA'));guard=np.array(Image.open(P/'root_anchor_hard_protection.png'))>0;Y,X=np.indices(guard.shape);metrics=[];sheet=Image.new('RGB',(1600,300),(95,95,95));d=ImageDraw.Draw(sheet)
for j,(f,rec) in enumerate(m['frames'].items()):
 a=np.array(Image.open(B/rec['source']).convert('RGBA'));b=np.array(Image.open(P/f'F{f}_DIAGNOSTIC.png').convert('RGBA'));allowed=np.array(Image.open(P/f'F{f}_source_target_union.png'))>0
 # Source-removal polygon had left a short old brown burr on the outside of the rotated tail.
 clean=(X>=1220)&(X<1236+0.15*(Y-560))&(Y>=560)&(Y<=569)&~guard&(b[:,:,3]>0)
 # Never touch foreground arm/hand pixels or red hair tie. Remove only the dark old hair material.
 rgb=a[:,:,:3].astype(int);clean&=(rgb[:,:,0]<130)&(rgb[:,:,1]<115)&(rgb[:,:,2]<115)
 b[clean,3]=0
 red=(X>1150)&(X<1300)&(Y>450)&(Y<565)&(rgb[:,:,0]>100)&(rgb[:,:,0]>rgb[:,:,1]*1.6)&(rgb[:,:,0]>rgb[:,:,2]*1.5)&(a[:,:,3]>0)
 protect=(guard|red)&(a[:,:,3]==255);b[protect]=a[protect]
 union=allowed|clean;b[~union]=a[~union]
 out=Image.fromarray(b);out.save(O/f'candidates/F{f}_tail_phone_clear.png');Image.fromarray((clean*255).astype('uint8')).save(O/f'masks/F{f}_old_burr_cleanup.png');Image.fromarray((union*255).astype('uint8')).save(O/f'masks/F{f}_explicit_change_union.png')
 phone=Image.open(P.parent/'phone_mapped_to_character_NATIVE_DIAGNOSTIC.png').convert('RGBA');bg=Image.new('RGBA',out.size,(95,95,95,255));bg.alpha_composite(phone);bg.alpha_composite(out);detail=bg.crop((1110,465,1430,725)).convert('RGB');sheet.paste(detail,(320*j,35));d.text((320*j+5,7),'F'+f+' same pixels tail + seam',fill='white');detail.resize((960,780)).save(O/f'review/F{f}_detail_3x.jpg')
 checks={'frame':f,'sha256':hashlib.sha256((O/f'candidates/F{f}_tail_phone_clear.png').read_bytes()).hexdigest(),'old_burr_pixels':int(clean.sum()),'outside_explicit_union_changed':int(np.any(a!=b,axis=2)[~union].sum()),'opaque_root_and_red_tie_changed':int(np.any(a!=b,axis=2)[protect].sum()),'image_generation_calls':0};metrics.append(checks)
sheet.save(O/'review/five_states_cleaned.jpg',quality=94);(O/'metrics.json').write_text(json.dumps(metrics,indent=2));print(json.dumps(metrics))
