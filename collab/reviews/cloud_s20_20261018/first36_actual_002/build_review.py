"""Exact rational APNG holds from retained actual PNGs; no interpolation/rendering.
Optional --f004 and SHA joins native Astra's independent004 to the first36f.
"""
from pathlib import Path
import argparse,csv,json,hashlib,struct,zlib,math
from fractions import Fraction
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;PACK=P.parent;OLD=PACK/'handoff_008_020_032_generation_002'
a=argparse.ArgumentParser();a.add_argument('--f004',type=Path);a.add_argument('--f004-sha');args=a.parse_args()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=list(csv.DictReader((PACK/'handoff_008_020_032_reference_001/exposure_000_035.csv').open()))
files={0:PACK/'F000/f000_scene_gate_001/cleanup/S20_F000_master_clean.png'}
for f in [8,20,32]:
 D=OLD/f'F{f:03}';s=json.loads((D/'status.json').read_text());files[f]=D/s['accepted_png'];assert sha(files[f])==s['accepted_sha256']
for f in [12,15,18,22,24,27,30]:
 D=PACK/'first36_gap_fill_001'/f'F{f:03}';s=json.loads((D/'status.json').read_text());assert s['state']=='AUTHOR_ACCEPTED';files[f]=D/s['accepted_png'];assert sha(files[f])==s['accepted_sha256']
for f in [12,15,22]:
 files[f]=PACK/'local_cleanup_012_015_022_001'/f'S20_F{f:03}_cleanup_candidate.png'
if args.f004:
 assert args.f004_sha and sha(args.f004)==args.f004_sha,'Explicit native004 source SHA required.'
 assert Image.open(args.f004).size==(1672,941);files[4]=args.f004.resolve()
# Every time slot stays in the original table. A missing external004 is explicit.
plan=[]
for r in rows:
 f=int(r['pose']);p=files.get(f);plan.append(dict(r,source=str(p) if p else None,sha256=sha(p) if p else None,status='ACTUAL_RETAINED' if p else 'EXTERNAL_ASTRA_F004_NOT_SUPPLIED',cloud_model_calls=0 if f==4 else None))
(P/'first36_exposure_manifest.json').write_text(json.dumps({'fps':24,'frame_range':[0,35],'total_frames':36,'poses':plan,'complete':4 in files,'missing_external':[4] if 4 not in files else [],'F004_cloud_calls':0,'F018_independent_new_pose':False,'F018_actual020_stable_anatomy_reuse':True,'cleanup_source_commit':'fa47c63d282b77a36a08b9d1d972caf1d0e7762e','native004_source_commit':'3b3ea25fa0c275ed603a0dda50fbe9011dadee4f','no_missing_state_substitution':True},ensure_ascii=False,indent=2)+'\n')
sel=[r for r in plan if int(r['pose'])>=8] if 4 not in files else plan
name='actual_F008_035_28f_24fps' if 4 not in files else 'actual_F000_035_36f_24fps'
def chunk(t,p):return struct.pack('>I',len(p))+t+p+struct.pack('>I',zlib.crc32(t+p)&0xffffffff)
def pngparts(p):
 b=p.read_bytes();assert b[:8]==b'\x89PNG\r\n\x1a\n';i=8;h=None;data=[]
 while i<len(b):
  n=struct.unpack('>I',b[i:i+4])[0];t=b[i+4:i+8];d=b[i+8:i+8+n]
  if t==b'IHDR':h=d
  if t==b'IDAT':data.append(d)
  i+=12+n
 return h,b''.join(data)
frames=[Image.open(r['source']).convert('RGBA') for r in sel];parts=[pngparts(Path(r['source'])) for r in sel];ih=parts[0][0];assert struct.unpack('>IIBBBBB',ih)==(1672,941,8,6,0,0,0);assert all(h==ih for h,d in parts)
b=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',ih)+chunk(b'acTL',struct.pack('>II',len(sel),0));seq=0
for i,(r,(h,d)) in enumerate(zip(sel,parts)):
 count=int(r['frame_count']);b+=chunk(b'fcTL',struct.pack('>IIIIIHHBB',seq,1672,941,0,0,count,24,0,0));seq+=1
 if i==0:b+=chunk(b'IDAT',d)
 else:b+=chunk(b'fdAT',struct.pack('>I',seq)+d);seq+=1
b+=chunk(b'IEND',b'');apng=P/(name+'.apng');apng.write_bytes(b)
check=Image.open(apng);assert check.n_frames==len(sel)
for i,im in enumerate(frames):check.seek(i);assert np.array_equal(np.array(check.convert('RGBA')),np.array(im)),i
# Full body and same-scale grips, in exact exposure order; review labels outside art.
font=ImageFont.truetype(str(PACK.parents[2]/'assets/fonts/NotoSansSC-VF.ttf'),20)
cols=5;cr=(450,25,1240,935);cw,ch=395,455;board=Image.new('RGB',(cols*cw,math.ceil(len(sel)/cols)*(ch+43)),'#bdc1c4');dr=ImageDraw.Draw(board)
box=(570,285,1040,540);bw,bh=470,255;hands=Image.new('RGB',(cols*bw,math.ceil(len(sel)/cols)*(bh+42)),'#bdc1c4');dh=ImageDraw.Draw(hands)
for i,(im,r) in enumerate(zip(frames,sel)):
 bg=Image.new('RGBA',im.size,'#bdc1c4');bg.alpha_composite(im);bg=bg.convert('RGB');x=(i%cols)*cw;y=(i//cols)*(ch+43);board.paste(bg.crop(cr).resize((cw,ch),Image.Resampling.LANCZOS),(x,y+43));txt=f"F{r['pose']} / {r['start_frame']}–{r['end_frame_inclusive']} / {r['frame_count']}f";dr.text((x+7,y+10),txt,font=font,fill='#263743');x=(i%cols)*bw;y=(i//cols)*(bh+42);hands.paste(bg.crop(box),(x,y+42));dh.text((x+8,y+9),txt,font=font,fill='#263743')
board.save(P/(name+'_fullbody.png'));hands.save(P/(name+'_contacts.png'))
with (P/(name+'_decoded_exposure.csv')).open('w',newline='') as out:
 w=csv.writer(out);w.writerow(['film_frame','pose','source_sha256','duration_seconds'])
 for r in sel:
  for f in range(int(r['start_frame']),int(r['end_frame_inclusive'])+1):w.writerow([f,r['pose'],r['sha256'],'1/24'])
(P/(name+'_verification.json')).write_text(json.dumps({'APNG':apng.name,'sha256':sha(apng),'size':[1672,941],'actual_unique_source_images':len(sel),'exposure_frames':sum(int(r['frame_count']) for r in sel),'fps':24,'exact_duration_seconds':str(Fraction(sum(int(r['frame_count']) for r in sel),24)),'holds_encoded_as_exact_count_over24_rationals':True,'decoded_RGBA_all_exact_sources':True,'character_interpolation':False,'scene_render_frames':0,'new_model_calls':0,'missing_external004':4 not in files},ensure_ascii=False,indent=2)+'\n');print(name,'poses',len(sel),'exposure frames',sum(int(r['frame_count']) for r in sel),'RGBA exact, rational timing24fps')
