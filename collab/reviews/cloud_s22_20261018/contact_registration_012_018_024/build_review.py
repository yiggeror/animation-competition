#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,sys
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps
from scipy import ndimage as nd
from register_same_raw import CONFIG,ROOT,INPUT,HERE,MOTHER,EXPECTED_MOTHER

font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
font_small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
mother=np.array(Image.open(MOTHER)); proof={}
boxes={'wrist_crease':[655,640,690,674],'visible_palm':[710,595,755,625],'child_thumb_nail':[846,506,879,541],'child_pinch':[760,470,893,566],'single_rod':[950,0,1672,510]}
for name in CONFIG:
 out=np.array(Image.open(HERE/'candidate'/f'{name}_registered.png'))
 rows={}
 for key,(x0,y0,x1,y1) in boxes.items():
  target=mother[y0:y1,x0:x1]; got=out[y0:y1,x0:x1]; mask=target[:,:,3]>=128
  delta=np.abs(target.astype(int)-got.astype(int)); error=delta[mask]
  assert not np.any(error), (name,key,int(error.max()))
  rows[key]=dict(box=[x0,y0,x1,y1],visible_pixels=int(mask.sum()),maximum_RGBA_error=0)
 coords=[]
 for x in range(1000,1551):
  ys=np.where(out[:,x,3]>=128)[0]
  coords.append((x,(ys.min()+ys.max())/2))
 q=np.array(coords); m,b=np.polyfit(q[:,0],q[:,1],1)
 rows['rod_axis']=dict(slope=float(m),intercept=float(b),angle_deg=float(np.degrees(np.arctan2(m,1))))
 proof[name]=rows
(HERE/'provenance/anchor_proof.json').write_text(json.dumps(proof,indent=2)+'\n')

# Native-size stills; comparisons contain original drawing pixels, not diagrams.
crop=(560,410,940,755); bw,bh=crop[2]-crop[0],crop[3]-crop[1]
board=Image.new('RGB',(bw*2,(bh+35)*3),(25,25,25)); d=ImageDraw.Draw(board)
for i,name in enumerate(CONFIG):
 y=i*(bh+35)
 before=Image.open(INPUT/name/'qa'/f'{name}_on_gray.png').crop(crop)
 after=Image.open(HERE/'qa'/f'{name}_registered_on_gray.png').crop(crop)
 board.paste(before,(0,y+35)); board.paste(after,(bw,y+35))
 d.text((8,y+8),name+' original / native',font=font_small,fill='white')
 d.text((bw+8,y+8),name+' registered / native',font=font_small,fill='white')
board.save(HERE/'qa/before_after_contact_native.png')

board=Image.new('RGB',(1040,1070),(25,25,25)); d=ImageDraw.Draw(board)
items=[('F000 locked',ROOT/'F000_color_repair/qa/after_on_gray.png')]+[(name,HERE/'qa'/f'{name}_registered_on_gray.png') for name in CONFIG]
for i,(label,path) in enumerate(items):
 x,y=(i%2)*520,(i//2)*535; board.paste(Image.open(path).crop((430,260,950,760)),(x,y+35)); d.text((x+8,y+8),label+' / same native crop',font=font_small,fill='white')
board.save(HERE/'qa/registered_progression_native.png')

# Actual visible pad area centres, explicitly not hidden bone/joint estimates.
centres={}
for name in ['F018','F024']:
 cfg=CONFIG[name]; raw=np.array(Image.open(INPUT/name/'originals'/cfg['raw']))
 labels,_=nd.label((raw[:,:,3]>128)&(raw[:,:,0]>210)&(raw[:,:,1]>145)&(raw[:,:,2]>100))
 rows=[]
 for pad,k in zip(['index','middle','ring','little'],cfg['pads']):
  y,x=np.where(labels==k); rows.append(dict(pad=pad,visible_region_centroid_xy=[float(x.mean()),float(y.mean())]))
 centres[name]=rows
deltas=[]
for a,b in zip(centres['F018'],centres['F024']):
 delta=np.array(b['visible_region_centroid_xy'])-a['visible_region_centroid_xy']; deltas.append(dict(pad=a['pad'],delta_xy=delta.tolist()))
(HERE/'provenance/adult_terminal_observation.json').write_text(json.dumps(dict(method='Centroids of actual visible skin regions; not reconstructed bone joints. Original adult foreground core remains unchanged during registration.',centres=centres,F018_to_F024_deltas=deltas,conclusion='No clear coordinated inward curl. Palm-back contour change dominates; final settle is weak. A separate minimal adult terminal/contact-line patch is proposed, not executed.'),indent=2)+'\n')

preview=HERE/'comparison_frames'; preview.mkdir(exist_ok=True); holds={'F012':6,'F018':6,'F024':12}; concat=[]
for name,hold in holds.items():
 canvas=Image.new('RGB',(1920,1080),(30,30,30)); d=ImageDraw.Draw(canvas)
 before=Image.open(INPUT/name/'qa'/f'{name}_on_gray.png'); after=Image.open(HERE/'qa'/f'{name}_registered_on_gray.png')
 for col,(im,label) in enumerate([(before,'ORIGINAL'),(after,'REGISTERED / same child + rod')]):
  x=col*960; canvas.paste(im.resize((960,540)),(x,0)); d.rectangle((x,0,x+960,36),fill=(25,25,25)); d.text((x+12,6),f'{name} {hold}f - {label}',font=font,fill='white')
  close=ImageOps.contain(im.crop(crop),(920,500)); canvas.paste(close,(x+(960-close.width)//2,575))
  d.text((x+12,545),'Actual contact crop / review only',font=font_small,fill='white')
 path=preview/(name+'.png'); canvas.save(path); concat.extend(["file '"+path.name+"'",'duration '+str(hold/24)])
concat.append("file 'F024.png'"); (preview/'concat.txt').write_text('\n'.join(concat)+'\n')
clip=HERE/'S22_registered_contact_compare_6_6_12.mp4'
command=['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(preview/'concat.txt'),'-vf','fps=24','-frames:v','24','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',str(clip)]
subprocess.run(command,check=True)
(HERE/'provenance/comparison_command.json').write_text(json.dumps(command,indent=2)+'\n')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(clip)],text=True))
assert int(probe['streams'][0]['nb_read_frames'])==24 and abs(float(probe['format']['duration'])-1)<.001
(HERE/'provenance/comparison_ffprobe.json').write_text(json.dumps(probe,indent=2)+'\n')
for f in [0,6,12,23]:
 subprocess.run(['ffmpeg','-y','-v','error','-i',str(clip),'-vf',f'select=eq(n\\,{f})','-frames:v','1',str(HERE/'qa'/f'compare_decoded_{f:02d}.png')],check=True)
(HERE/'provenance/comparison_manifest.json').write_text(json.dumps(dict(clip=clip.name,sha256=hashlib.sha256(clip.read_bytes()).hexdigest(),frames=24,fps=24,duration_seconds=1,source_exposures={'12-17':6,'18-23':6,'24-35':12},decoded_frames=[0,6,12,23],no_state_030=True,no_S22_scene_render=True,new_image_calls=0),indent=2)+'\n')
print('Five locked child/rod regions x3: exact RGBA; actual comparison24f at6/6/12 decoded.')
