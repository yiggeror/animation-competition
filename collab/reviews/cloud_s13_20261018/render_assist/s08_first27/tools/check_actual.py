#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,subprocess,json,hashlib,shutil
H=Path(__file__).resolve().parents[1];ROOT=Path.cwd();FIXED='a4b00a05c88b3cc46284b45d1d25cff4c7ca0831';SRC=ROOT/'collab/reviews/20261018_1900_s08_first27_scene';S=ROOT/'build/S08_first27';D=Path('/tmp/s08_first27_decoded_actual');D.mkdir(exist_ok=True)
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==FIXED
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
entry=SRC/'s08_first27_scene.js';assert sha(entry)=='4a4708868c12a2b3937d87c063a5c4c08dc053a6c6ef6745fcf9d6c3bd0b8896'
mp4=H/'S08_first27_1920x1080_24fps.mp4';assert sha(mp4)==sha(ROOT/'build/S08_first27_1920x1080_24fps.mp4')
assert sorted(f.name for f in S.glob('*.png'))==[f'{n:05}.png'for n in range(27)]
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(mp4)]));v=probe['streams'][0]
assert len(probe['streams'])==1 and (v['nb_read_frames'],v['r_frame_rate'],v['width'],v['height'])==('27','24/1',1920,1080)and float(v['duration'])==27/24
subprocess.run(['ffmpeg','-v','error','-y','-i',str(mp4),'-fps_mode','passthrough',str(D/'%05d.png')],check=True);assert len(list(D.glob('*.png')))==27
baseline=json.loads((H/'old23_saved_PNG_baseline.json').read_text());prefix=[]
for row in baseline['saved_actual_PNGs_verified']:
 f=row['frame'];old=ROOT/row['path'];new=S/f'{f:05}.png';assert sha(old)==row['sha256'];assert sha(new)==sha(old),(f,'old/new lossless mismatch')
 prefix.append({'frame':f,'old_actual_sha256':sha(old),'new_actual_sha256':sha(new),'RGBA_changed_pixels':0,'PNG_bytes_equal':True})
(H/'old23_all_exact_comparison.json').write_text(json.dumps({'prior_delivered_commit':baseline['delivery_commit'],'old_PNGs_rerendered':False,'checks':prefix,'all_000_022_PNG_bytes_equal':True},indent=2)+'\n')
# Verify all runtime assets against fixed repository blobs and their declared SHA.
rows=json.loads((SRC/'RUNTIME_ROWS.json').read_text());runtime=[]
for row in rows:
 p=ROOT/row['repository_relative_path'];assert sha(p)==row['sha256'];assert p.read_bytes()==subprocess.check_output(['git','show',f'{FIXED}:{p.relative_to(ROOT)}']);runtime.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p)})
for p in [ROOT/'tools/js/frames.cjs',ROOT/'js/paint/paintshot.js',ROOT/'js/code/s08.js',ROOT/'assets/paint/bg_01_room_wide.png']:
 assert p.read_bytes()==subprocess.check_output(['git','show',f'{FIXED}:{p.relative_to(ROOT)}'])
# Layer contract: source box unchanged and one instance, no baked box in body/arms.
lc=(SRC/'layer_contract.js').read_text();lc=json.loads(lc[lc.index('=')+1:].strip().rstrip(';'));sourcechecks=[]
reference=np.array(Image.open(SRC/'frames/F017_table_box_original_pixels.png'));m=reference[:,:,3]>0
assert m.sum()==1665
for asset in ['023','025']:
 imgs={role:np.array(Image.open(SRC/'frames'/meta['filename']).convert('RGBA'))for role,meta in lc[asset].items()}
 box=imgs['table_box'];assert np.array_equal(box[:,:,3],reference[:,:,3])and np.array_equal(box[m],reference[m])
 assert not np.any((imgs['body'][:,:,3]>0)&m)and not np.any((imgs['arms'][:,:,3]>0)&m)
 ys,xs=np.where(box[:,:,3]>128);assert ys.max()==970
 gate=json.loads((SRC/f'F{asset}_PIXEL_CONTACT_CHECK.json').read_text());cx,cy=gate['independent_knob_center']
 xx,yy=int(np.floor(cx)),int(np.floor(cy));actual_alpha=imgs['arms'][yy:yy+2,xx:xx+2,3].tolist();assert actual_alpha==[[2,0],[0,1]]
 assert imgs['arms'][yy:yy+2,xx-1:xx+1,3].tolist()==gate['alpha_at_center_four_pixels']
 sourcechecks.append({'asset':asset,'box_visible_pixels':1665,'box_bottom_y':970,'box_alpha_visibleRGBA_exact017':True,'body_arms_duplicate_box_pixels':0,'independent_knob_center':[cx,cy],'actual_arm_alpha_2x2_at_seat':actual_alpha,'match_head':gate['near_match_head'],'near_guard_changed_RGBA_pixels':gate['near_guard_changed_RGBA_pixels']})
# Front lip instructions remain exactly the same as actual previous23 source.
oldmodule=subprocess.check_output(['git','show','d6071b76c8b069c7112134320a69058b896ff1f5:collab/reviews/20261018_1828_s08_first23_scene/s08_first23_scene.js'],text=True)
def front(s):return s[s.index('function tableFront()'):s.index('const layerCache')].strip()
assert front(entry.read_text())==front(oldmodule)
# Actual decodes and all27 encode order. Hot source remains on the match, not wick.
checks=[]
for f in range(27):
 a=np.array(Image.open(S/f'{f:05}.png').convert('RGB'),dtype=float);b=np.array(Image.open(D/f'{f+1:05}.png').convert('RGB'),dtype=float);mse=float(np.mean((a-b)**2));assert mse<50
 head=[1076,794]if f>=25 else[1070,791]if f>=23 else[1062,787]if f>=20 else[1074,782]if f>=5 else[1124,755]if f>=3 else[1076,764]
 if f>=23:
  x,y=head;hot=b[y-45:y+10,x-25:x+25];assert np.any((hot[:,:,0]>=240)&(hot[:,:,1]>=150)&(hot[:,:,2]>=60))
  wick=b[780:808,1403:1428];assert not np.any((wick[:,:,0]>=240)&(wick[:,:,1]>=150)&(wick[:,:,2]>=60))
 checks.append({'frame':f,'source_Canvas_PNG_sha256':sha(S/f'{f:05}.png'),'decoded_vs_source_MSE':mse,'actual_match_head':head,'lift':.5 if f>=25 else 0})
selected=[22,23,24,25,26]
for f in selected:shutil.copyfile(D/f'{f+1:05}.png',H/f'decoded/F{f:03}.png')
for f in [23,24,25,26]:shutil.copyfile(S/f'{f:05}.png',H/f'canvas_new/F{f:03}.png')
font=lambda n:ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',n)
def board(ff,name,box=None,cols=3,tile=(640,360),scale=None):
 tw,th=tile;im=Image.new('RGB',(tw*cols,((len(ff)+cols-1)//cols)*(th+38)),'#eeebe3');d=ImageDraw.Draw(im)
 for i,f in enumerate(ff):
  panel=Image.open(D/f'{f+1:05}.png').convert('RGB')
  if box:panel=panel.crop(box)
  if scale:panel=panel.resize((panel.width*scale,panel.height*scale),Image.Resampling.NEAREST)
  else:panel.thumbnail((tw-8,th))
  x,y=(i%cols)*tw+4,(i//cols)*(th+38)+34;im.paste(panel,(x,y));d.text((x,y-30),f'F{f:03} 实际解码',font=font(21),fill='#25333d')
 im.save(H/name,quality=98)
board(selected,'00_requested_actual_decodes.jpg')
board(selected,'01_whole_arms_table_front_actual.jpg',box=(660,675,1320,1035),tile=(670,370))
board(selected,'02_real_grip_rod_globe_actual2x.jpg',box=(1200,690,1520,910),tile=(650,450),scale=2)
board(selected,'03_match_head_actual3x.jpg',box=(1015,740,1125,865),tile=(340,375),cols=5,scale=3)
board(selected,'04_box_front_contact_actual3x.jpg',box=(1035,930,1175,1005),tile=(430,225),cols=5,scale=3)
result={'status':'REAL27_RENDER_ENCODE_PASS_OLD23_EXACT;VISUAL_INCREMENT_REVIEW_REQUIRED','fixed_commit':FIXED,'entry_sha256':sha(entry),'frames':27,'fps':'24/1','width':1920,'height':1080,'duration':27/24,'audio_streams':0,'frame027_or_later_rendered':False,'old_000_022_all_PNG_bytes_exact':True,'old23_rerendered':False,'selected_actual_decodes':selected,'actual27_source_and_decode_checks':checks,'max_encoded_MSE':max(x['decoded_vs_source_MSE']for x in checks),'source_new_states':sourcechecks,'runtime_SHA_and_fixed_git_verified':runtime,'front_lip_drawing_function_exact_old23':True,'mechanism_source_at025':{'angle':-.6,'lift':.5,'globe_rise_px':110*14/18.5*.5},'actual_match_head023_to025_delta':[6,3],'wick_ignition':0,'mp4_sha256':sha(mp4),'visual_review':'SeeREADME;partial scene only;not full shot or sound ready.'}
(H/'actual27_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');(H/'ffprobe.json').write_text(json.dumps(probe,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:result[k]for k in ['frames','fps','duration','mp4_sha256','max_encoded_MSE','old_000_022_all_PNG_bytes_exact','actual_match_head023_to025_delta','wick_ignition']},ensure_ascii=False))
