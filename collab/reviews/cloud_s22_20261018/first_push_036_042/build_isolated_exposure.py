#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as nd

HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
SOURCES=[('F000',ROOT/'F000_color_repair/candidate/F000_repaired.png',12,'d4e78e2d5b84a72588cf3af1ff23ce39cdc18d19dde2fbf1f8eaf44ba62d7ef5'),('F012',ROOT/'contact_band_repair_012_018_024/candidate/F012_contact_fixed.png',6,'f01d484e04dea7e3cde141d1aa2a94ecd0d45d25bc81f7d94f2f9a3f33757898'),('F018',ROOT/'contact_band_repair_012_018_024/candidate/F018_contact_fixed.png',6,'c72e8afe8c5e73c17d66d57bc007f12fbfafd4efba9c0e3313f3010008c194a0'),('F024',ROOT/'contact_band_repair_012_018_024/candidate/F024_contact_fixed.png',12,'97560237598d024a725ab63ee62809d1f5ded5f6fc5aadc1d8a4f158ca85da4a'),('F036',HERE/'F036/candidate/F036_mapped.png',6,None),('F042',HERE/'F042/candidate/F042_mapped.png',18,None)]
for sub in ['qa','exposure_frames','decoded_actual','provenance']:(HERE/sub).mkdir(exist_ok=True)
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',20)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
def compose(a):
 im=Image.fromarray(a);plate=Image.new('RGBA',im.size,(115,115,115,255));plate.alpha_composite(im);return plate.convert('RGB')
images={};arrays={};concat=[];exposures=[];frame=0
for name,path,hold,expected in SOURCES:
 sha=hashlib.sha256(path.read_bytes()).hexdigest()
 if expected:assert sha==expected
 else:assert sha==json.loads((HERE/name/'provenance/mapping_checks.json').read_text())['mapped_sha256']
 a=np.array(Image.open(path).convert('RGBA'));arrays[name]=a;images[name]=compose(a)
 im=images[name].resize((1280,720));d=ImageDraw.Draw(im);d.rectangle((0,0,910,36),fill=(25,25,25));d.text((10,3),f'S22 隔离曝光（非实景） | {name} ×{hold} | 仅000–059',font=font,fill='white')
 out=HERE/'exposure_frames'/(name+'.png');im.save(out);concat.extend(["file '"+out.name+"'",'duration '+str(hold/24)])
 exposures.append(dict(id=name,start=frame,end=frame+hold-1,hold=hold,source=str(path.relative_to(ROOT)),sha256=sha));frame+=hold
assert frame==60;concat.append("file 'F042.png'");(HERE/'exposure_frames/concat.txt').write_text('\n'.join(concat)+'\n')
(HERE/'provenance/exposure_manifest.json').write_text(json.dumps(dict(fps=24,total_frames=60,duration_seconds=2.5,isolation_not_scene=True,rows=exposures,no_state_030=True,no_state_060=True),indent=2)+'\n')
clip=HERE/'S22_000_059_isolated_exposure60.mp4';command=['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(HERE/'exposure_frames/concat.txt'),'-vf','fps=24','-frames:v','60','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',str(clip)];subprocess.run(command,check=True)
(HERE/'provenance/exposure_command.json').write_text(json.dumps(command,indent=2)+'\n')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(clip)],text=True));assert int(probe['streams'][0]['nb_read_frames'])==60;assert float(probe['format']['duration'])==2.5
(HERE/'provenance/exposure_ffprobe.json').write_text(json.dumps(probe,indent=2)+'\n')
selected=[0,11,12,17,18,23,24,35,36,41,42,59]
for f in selected:subprocess.run(['ffmpeg','-y','-v','error','-i',str(clip),'-vf',f'select=eq(n\\,{f})','-frames:v','1',str(HERE/'decoded_actual'/f'F{f:03d}.png')],check=True)
board=Image.new('RGB',(1600,618),(25,25,25));d=ImageDraw.Draw(board)
for i,f in enumerate(selected):
 x,y=(i%5)*320,(i//5)*206;board.paste(Image.open(HERE/'decoded_actual'/f'F{f:03d}.png').resize((320,180)),(x,y+26));d.text((x+7,y+3),f'F{f:03d} / decoded MP4',font=small,fill='white')
board.save(HERE/'qa/actual_decoded_contact.jpg',quality=96)

for title,crop in [('contact_group',[610,360,1010,760]),('forearm_join',[300,330,700,750])]:
 cw,ch=crop[2]-crop[0],crop[3]-crop[1];board=Image.new('RGB',(cw*3,ch+35),(25,25,25));d=ImageDraw.Draw(board)
 for i,name in enumerate(['F024','F036','F042']):board.paste(images[name].crop(crop),(i*cw,35));d.text((i*cw+8,7),name+' / native same crop',font=small,fill='white')
 board.save(HERE/'qa'/(title+'_024_036_042_native.png'))
base=arrays['F024'];edge0=(base[:,:,3]>=128)^nd.binary_erosion(base[:,:,3]>=128);after=arrays['F042'];edge1=(after[:,:,3]>=128)^nd.binary_erosion(after[:,:,3]>=128)
overlay=np.array(images['F024']);overlay[edge0]=[255,80,180];overlay[edge1]=[60,230,255];Image.fromarray(overlay).save(HERE/'qa/F024_to_F042_motion_overlay.png')

# Neutral forearm material samples at equivalent cross-section fractions.
colours={}
for name in ['F024','F036','F042']:
 a=arrays[name];samples=[[],[]]
 for x in range(250,351):
  labels,n=nd.label(a[:,x,3]>=128);bounds=[]
  for k in range(1,n+1):
   ys=np.where(labels==k)[0]
   if len(ys)>20:bounds.append([ys.min(),ys.max()+1])
  for i,b in enumerate([bounds[0],bounds[-1]]):
   y=int(sum(b)/2);samples[i].append(a[y-2:y+3,x,:3])
 colours[name]=dict(grandma_median_RGB=np.median(np.concatenate(samples[0]),axis=0).tolist(),child_median_RGB=np.median(np.concatenate(samples[1]),axis=0).tolist())
(HERE/'provenance/forearm_colour_check.json').write_text(json.dumps(dict(method='Native columns250–350, middle of each actual alpha cross-section; samples are comparable neutral material regions, not promises of identical form shading.',observed=colours),indent=2)+'\n')
summary=dict(clip=clip.name,sha256=hashlib.sha256(clip.read_bytes()).hexdigest(),frames=60,fps=24,size=[1280,720],duration_seconds=2.5,isolation_not_scene=True,decoded=selected,new_image_calls_this_batch=2,successful_outputs_this_batch=2,cumulative_S22_attempts=7,cumulative_S22_successful_outputs=6,no_030=True,no_060=True)
(HERE/'provenance/delivery_manifest.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
