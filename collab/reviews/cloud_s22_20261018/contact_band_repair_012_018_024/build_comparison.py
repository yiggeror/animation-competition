#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps
from scipy import ndimage as nd

HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;REG=ROOT/'contact_registration_012_018_024'
mother=np.array(Image.open(ROOT/'F000_color_repair/candidate/F000_repaired.png'))
C=np.array(Image.open(REG/'masks/locked_F000_child_and_rod.png'))>=128
boxes=json.loads((REG/'provenance/anchor_proof.json').read_text())['F012']
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
def bg(a,color=(115,115,115)):
 im=Image.fromarray(a);b=Image.new('RGBA',im.size,(*color,255));b.alpha_composite(im);return b.convert('RGB')
proof={};before_images={};after_images={}
for name in ['F012','F018','F024']:
 before=np.array(Image.open(REG/'candidate'/f'{name}_registered.png'));after=np.array(Image.open(HERE/'candidate'/f'{name}_contact_fixed.png'))
 rows={}
 for key,value in boxes.items():
  if 'box' not in value:continue
  x0,y0,x1,y1=value['box'];target=mother[y0:y1,x0:x1];got=after[y0:y1,x0:x1];m=C[y0:y1,x0:x1];delta=np.abs(got.astype(int)-target.astype(int))[m]
  assert not np.any(delta),(name,key);rows[key]=dict(box=value['box'],visible_pixels=int(m.sum()),maximum_RGBA_error=0)
 if name!='F012':
  thumb=np.array(Image.open(HERE/'masks'/f'{name}_thumb_frozen.png'))>0;roi=np.array(Image.open(HERE/'masks'/f'{name}_continuous_ROI.png'))>0
  assert np.array_equal(after[thumb],before[thumb]);assert np.array_equal(after[~roi],before[~roi])
  rows['adult_thumb']=dict(visible_pixels=int(thumb.sum()),maximum_RGBA_error=0);rows['outside_ROI']=dict(maximum_RGBA_error=0)
  changed=np.any(after!=before,axis=2);p=np.array(bg(before),float);z=changed[:,:,None]*.65;p=p*(1-z)+np.array([255,55,80])*z
  edge=roi^nd.binary_erosion(roi);p[edge]=[60,230,255];p[thumb]=p[thumb]*.75+np.array([70,150,255])*.25
  Image.fromarray(np.rint(p).astype('uint8')).save(HERE/'qa'/f'{name}_actual_change_range.png')
 proof[name]=rows
 before_images[name]=bg(before);after_images[name]=bg(after)
 for label,color in [('gray',(115,115,115)),('white',(255,255,255)),('black',(0,0,0))]:bg(after,color).save(HERE/'qa'/f'{name}_fixed_on_{label}.png')
(HERE/'provenance/independent_frozen_checks.json').write_text(json.dumps(proof,indent=2)+'\n')

crop=(530,410,930,755);cw,ch=400,345;board=Image.new('RGB',(800,760),(25,25,25));d=ImageDraw.Draw(board)
for i,name in enumerate(['F018','F024']):
 y=i*380;board.paste(before_images[name].crop(crop),(0,y+35));board.paste(after_images[name].crop(crop),(400,y+35));d.text((8,y+7),name+' registered / before',font=small,fill='white');d.text((408,y+7),name+' contact-band repair',font=small,fill='white')
board.save(HERE/'qa/before_after_contact_native.png')
settle=Image.new('RGB',(800,380),(25,25,25));d=ImageDraw.Draw(settle)
for i,name in enumerate(['F018','F024']):settle.paste(after_images[name].crop(crop),(i*400,35));d.text((i*400+8,7),name+' fixed / native',font=small,fill='white')
settle.save(HERE/'qa/settle_018_024_native.png')

frames=HERE/'comparison_frames';frames.mkdir(exist_ok=True);concat=[]
for name,hold in [('F012',6),('F018',6),('F024',12)]:
 canvas=Image.new('RGB',(1920,1080),(25,25,25));d=ImageDraw.Draw(canvas)
 for col,(im,label) in enumerate([(before_images[name],'REGISTERED BEFORE'),(after_images[name],'CONTINUOUS CONTACT FIX')]):
  x=col*960;canvas.paste(im.resize((960,540)),(x,0));d.rectangle((x,0,x+960,36),fill=(25,25,25));d.text((x+12,6),f'{name} {hold}f - {label}',font=font,fill='white')
  close=ImageOps.contain(im.crop((620,550,920,745)),(920,500));canvas.paste(close,(x+(960-close.width)//2,575));d.text((x+12,545),'Actual continuous contact band',font=small,fill='white')
 path=frames/(name+'.png');canvas.save(path);concat.extend(["file '"+path.name+"'",'duration '+str(hold/24)])
concat.append("file 'F024.png'");(frames/'concat.txt').write_text('\n'.join(concat)+'\n')
clip=HERE/'S22_contact_band_compare_6_6_12.mp4';command=['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(frames/'concat.txt'),'-vf','fps=24','-frames:v','24','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',str(clip)]
subprocess.run(command,check=True);(HERE/'provenance/comparison_command.json').write_text(json.dumps(command,indent=2)+'\n')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(clip)],text=True));assert int(probe['streams'][0]['nb_read_frames'])==24;assert float(probe['format']['duration'])==1
(HERE/'provenance/comparison_ffprobe.json').write_text(json.dumps(probe,indent=2)+'\n')
for f in [0,6,12,23]:subprocess.run(['ffmpeg','-y','-v','error','-i',str(clip),'-vf',f'select=eq(n\\,{f})','-frames:v','1',str(HERE/'qa'/f'compare_decoded_{f:02d}.png')],check=True)
(HERE/'provenance/comparison_manifest.json').write_text(json.dumps(dict(clip=clip.name,sha256=hashlib.sha256(clip.read_bytes()).hexdigest(),frames=24,fps=24,duration_seconds=1,holds=[6,6,12],original_frames='012-035',decoded_frames=[0,6,12,23],new_image_calls=0,production_ready=False),indent=2)+'\n')
print('Actual comparison24f at6/6/12 decoded; frozen child15 region checks and adult thumbs pass.')
