#!/usr/bin/env python3
"""Package the12 real RGBA drawings and exact120-frame isolated character exposure."""
from pathlib import Path
import csv,hashlib,json,shutil,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SOURCES=[
 ('F000','F000_color_repair/candidate/F000_repaired.png','d4e78e2d5b84a72588cf3af1ff23ce39cdc18d19dde2fbf1f8eaf44ba62d7ef5'),
 ('F012','contact_band_repair_012_018_024/candidate/F012_contact_fixed.png','f01d484e04dea7e3cde141d1aa2a94ecd0d45d25bc81f7d94f2f9a3f33757898'),
 ('F018','contact_band_repair_012_018_024/candidate/F018_contact_fixed.png','c72e8afe8c5e73c17d66d57bc007f12fbfafd4efba9c0e3313f3010008c194a0'),
 ('F024','contact_band_repair_012_018_024/candidate/F024_contact_fixed.png','97560237598d024a725ab63ee62809d1f5ded5f6fc5aadc1d8a4f158ca85da4a'),
 ('F036','first_push_036_042/F036/candidate/F036_mapped.png','ad6d47305791dd1fbc2d9849b8bd87d8632102f61dc29dce3ed5054867b49b4f'),
 ('F042','first_push_036_042/F042/candidate/F042_mapped.png','2a028a4c174c55e4cde7d794cd59561d39585c626740dd0afa7ffdd49f5b477c'),
 ('F060','second_push_colour_060_066/candidate/F060_colour_fixed.png','356c67d7c62efe46b4e68bece873407571adbc994801a622c39db2fdb1bfc136'),
 ('F066','second_push_colour_060_066/candidate/F066_colour_fixed.png','849de1cf2633d3818c59c73e5a68f22cca77a24c9fce8d44bce7b005385c1d60'),
 ('F084','third_push_shadow_084_090/candidate/F084_shadow_fixed.png','3a43afce664385306de620c16fccef8ee8534e0708c431fedae0b432cfaa71b9'),
 ('F090','third_push_shadow_084_090/candidate/F090_shadow_fixed.png','cabe79438fa626ff0ce7a36e6447a4b8dbac4755528479fce125323a3a68d805'),
 ('F108','fourth_push_108_114/F108/candidate/F108_final_edge_aligned.png','d80948993838a76c0ea788e7111e9c245b9457c34dea2fb9da49ddc1080b74f0'),
 ('F114','fourth_push_108_114/F114/candidate/F114_final_edge_aligned.png','74b692c116bf4d72e7d0fb684910b852e4c91ed32cfbe84d704e22a44f217112'),
]
for sub in ['layer_sources','exposure_stills','decoded_actual','decoded_last12','provenance','qa']:(HERE/sub).mkdir(exist_ok=True)
table={int(r['start_frame']):r for r in csv.DictReader((ROOT/'S22_exposure.csv').open())}
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',20)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
rows=[];allframes=[];origin=[];images={};frame=0
for name,rel,expected in SOURCES:
 source=ROOT/rel;assert sha(source)==expected,(name,sha(source));im=Image.open(source);assert im.mode=='RGBA' and im.size==(1672,941)
 target=HERE/'layer_sources'/(name+'.png');shutil.copy2(source,target);assert sha(target)==expected
 r=table[int(name[1:])];hold=int(r['hold']);start=int(r['start_frame']);end=int(r['end_frame']);assert start==frame and end==frame+hold-1
 row=dict(id=name,start=start,end=end,hold=hold,rgba_path=str(target.relative_to(HERE)),sha256=expected,review_source=rel,world_cumulative=[float(r['shared_dx']),float(r['shared_dy'])],status='Locked by Astra' if start<108 else 'Author reviewed; Astra final review pending')
 rows.append(row)
 for f in range(start,end+1):allframes.append(dict(frame=f,key=name,rgba_path=row['rgba_path'],sha256=expected))
 plate=Image.new('RGBA',im.size,(115,115,115,255));plate.alpha_composite(im);images[name]=plate.convert('RGB')
 preview=images[name].resize((1280,720));d=ImageDraw.Draw(preview);d.rectangle((0,0,1220,36),fill=(25,25,25));d.text((10,3),f'S22 人物层曝光（未接实景/音轨）｜{name} ×{hold}｜000–119',font=font,fill='white');preview.save(HERE/'exposure_stills'/(name+'.png'))
 # Full native origin and successful tool request for every drawing.
 if name=='F000':
  raw='F000_first/originals/F000_call01_raw.png';request='F000_first/provenance/F000_call01_request.json'
 elif name=='F012':
  raw='contact_012_018_024/F012/originals/F012_call02_raw.png';request='contact_012_018_024/F012/provenance/call02_request.json'
 else:
  parent='contact_012_018_024' if start<=24 else ('first_push_036_042' if start<=42 else ('second_push_060_066' if start<=66 else ('third_push_084_090' if start<=90 else 'fourth_push_108_114')))
  raw=parent+'/'+name+'/originals/'+name+'_call01_raw.png';request=parent+'/'+name+'/provenance/request.json'
 origin.append(dict(id=name,delivery_rgba=row['rgba_path'],delivery_sha256=expected,processed_review_source=rel,original_raw=raw,original_raw_sha256=sha(ROOT/raw),original_raw_size=list(Image.open(ROOT/raw).size),complete_successful_request=request,request_sha256=sha(ROOT/request)))
 frame+=hold
assert frame==120 and len(rows)==12 and [r['hold'] for r in rows]==[12,6,6,12,6,18,6,18,6,18,6,6]
with (HERE/'S22_character_frames120.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=['frame','key','rgba_path','sha256'],lineterminator='\n');writer.writeheader();writer.writerows(allframes)
(HERE/'provenance/all12_original_sources.json').write_text(json.dumps(origin,indent=2)+'\n')
layer=dict(fps=24,total_frames=120,duration_seconds=5,canvas=[1672,941],format='12 unchanged RGBA PNGs plus explicit120-frame CSV; hold exposures, no interpolation',frame_csv='S22_character_frames120.csv',frame_csv_sha256=sha(HERE/'S22_character_frames120.csv'),rows=rows,scene_integrated=False,audio_integrated=False,production_ready=False)
(HERE/'S22_character_layer_manifest.json').write_text(json.dumps(layer,indent=2)+'\n')

def encode(stem,selected_rows,selected,folder):
 count=sum(r['hold'] for r in selected_rows);offset=selected_rows[0]['start'];clip=HERE/(stem+'.mp4')
 command=['ffmpeg','-y','-v','error','-f','image2pipe','-framerate','24','-i','-','-frames:v',str(count),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p',str(clip)]
 proc=subprocess.Popen(command,stdin=subprocess.PIPE);expected=[]
 for row in selected_rows:
  data=(HERE/'exposure_stills'/(row['id']+'.png')).read_bytes()
  for _ in range(row['hold']):proc.stdin.write(data);expected.append(row['id'])
 proc.stdin.close();assert proc.wait()==0
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(clip)],text=True))
 assert len(probe['streams'])==1 and int(probe['streams'][0]['nb_read_frames'])==count and probe['streams'][0]['r_frame_rate']=='24/1' and float(probe['format']['duration'])==count/24
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(clip),'-vf','scale=320:180','-f','rawvideo','-pix_fmt','rgb24','-'])
 decoded=np.frombuffer(raw,np.uint8).reshape((count,180,320,3)).astype(np.float32)
 refs=[np.array(Image.open(HERE/'exposure_stills'/(r['id']+'.png')).resize((320,180))).astype(np.float32) for r in selected_rows]
 errors=np.stack([np.mean((decoded-ref)**2,axis=(1,2,3)) for ref in refs],axis=1)
 actual=[selected_rows[i]['id'] for i in errors.argmin(axis=1)];assert actual==expected
 for f in selected:subprocess.run(['ffmpeg','-y','-v','error','-i',str(clip),'-vf',f'select=eq(n\\,{f})','-frames:v','1',str(HERE/folder/f'F{offset+f:03d}.png')],check=True)
 record=dict(clip=clip.name,sha256=sha(clip),fps=24,frames=count,duration_seconds=count/24,size=[1280,720],rows=selected_rows,actual_decoded_identities=actual,all_holds_match=True,decoded_global_frames=[offset+f for f in selected],command=command,ffprobe=probe,scene_integrated=False,audio_integrated=False)
 (HERE/'provenance'/(stem+'.json')).write_text(json.dumps(record,indent=2)+'\n');return {k:record[k] for k in ['clip','sha256','fps','frames','duration_seconds','all_holds_match']}

selected=sorted({f for r in rows for f in [r['start'],r['end']]})
clips=[encode('S22_000_119_character_layer120',rows,selected,'decoded_actual'),encode('S22_108_119_last12',rows[-2:],[0,5,6,11],'decoded_last12')]
board=Image.new('RGB',(1280,618),(25,25,25));d=ImageDraw.Draw(board)
for i,r in enumerate(rows):
 x,y=(i%4)*320,(i//4)*206;board.paste(Image.open(HERE/'decoded_actual'/f"F{r['start']:03d}.png").resize((320,180)),(x,y+26));d.text((x+8,y+3),r['id']+f" x{r['hold']} / decoded",font=small,fill='white')
board.save(HERE/'qa/all12_actual_exposure.jpg',quality=96)
last=[107,108,113,114,119];board=Image.new('RGB',(1600,206),(25,25,25));d=ImageDraw.Draw(board)
for i,f in enumerate(last):board.paste(Image.open(HERE/'decoded_actual'/f'F{f:03d}.png').resize((320,180)),(320*i,26));d.text((320*i+8,3),f'F{f:03d} / decoded MP4',font=small,fill='white')
board.save(HERE/'qa/last_boundaries_actual.jpg',quality=96)
for label,crop in [('contact_group',(610,320,1100,750)),('forearm_join',(300,240,760,760))]:
 cw,ch=crop[2]-crop[0],crop[3]-crop[1];board=Image.new('RGB',(cw*3,ch+32),(25,25,25));d=ImageDraw.Draw(board)
 for i,name in enumerate(['F090','F108','F114']):board.paste(images[name].crop(crop),(i*cw,32));d.text((i*cw+8,5),name+' / native same crop',font=small,fill='white')
 board.save(HERE/'qa'/(label+'_090_108_114.png'))
summary=dict(clips=clips,layer_manifest='S22_character_layer_manifest.json',frame_csv='S22_character_frames120.csv',rgba_sources=12,total_frames=120,new_image_calls=2,successful_outputs=2,cumulative_attempts=13,cumulative_successful_outputs=12,scene_integrated=False,audio_integrated=False,production_ready=False)
(HERE/'provenance/delivery_manifest.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
