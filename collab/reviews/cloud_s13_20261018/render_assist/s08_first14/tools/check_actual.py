#!/usr/bin/env python3
"""Real S08 000–013 Canvas/encoded checks and unmodified original-layer audit."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,subprocess,shutil,re
import numpy as np
P=Path(__file__).resolve().parents[1];ROOT=Path.cwd()
FIXED='0c215550edb5f1807b240ca7f79f6f61c8aef01e'
SRC=ROOT/'collab/reviews/20261018_1721_s08_first14_scene'
S=ROOT/'build/S08_first14';D=Path('/tmp/s08_first14_actual_decoded');D.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
mp4=P/'S08_first14_1920x1080_24fps.mp4'
assert mp4.read_bytes()==(ROOT/'build/S08_first14_1920x1080_24fps.mp4').read_bytes()
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(mp4)],text=True));v=probe['streams'][0]
assert len(probe['streams'])==1 and v['codec_type']=='video'
assert (v['nb_frames'],v['r_frame_rate'],v['width'],v['height'])==('14','24/1',1920,1080)
assert abs(float(v['duration'])-14/24)<1e-6
assert sorted(x.name for x in S.glob('*.png'))==[f'{f:05}.png'for f in range(14)]
subprocess.run(['ffmpeg','-y','-v','error','-i',str(mp4),'-fps_mode','passthrough',str(D/'%05d.png')],check=True)
assert len(list(D.glob('*.png')))==14
frames=[]
assets=['000']*3+['003']*2+['005']+['006']*3+['009']*3+['005']*2
for f in range(14):
 a=np.array(Image.open(S/f'{f:05}.png').convert('RGB'),dtype=np.float32);b=np.array(Image.open(D/f'{f+1:05}.png').convert('RGB'),dtype=np.float32)
 mse=float(np.mean((a-b)**2));assert mse<50,(f,mse)
 head=[1076,764]if f<3 else[1124,755]if f<5 else[1074,782]
 x,y=head;crop=b[y-42:y+8,x-22:x+23].astype(int)
 flame=(crop[:,:,0]>=240)&(crop[:,:,1]>=150)&(crop[:,:,2]>=60)
 assert bool(flame.any())==(f>=5),(f,int(flame.sum()))
 wick=b[775:810,1395:1435];wick_hot=(wick[:,:,0]>=240)&(wick[:,:,1]>=150)&(wick[:,:,2]>=60)
 assert not wick_hot.any(),f
 frames.append({'frame':f,'original_asset':assets[f],'Canvas_source_sha256':sha((S/f'{f:05}.png').read_bytes()),'encoded_vs_source_MSE':mse,'actual_match_head':head,'bright_flame_ROI_pixels':int(flame.sum()),'bright_wick_ROI_pixels':int(wick_hot.sum()),'face_ROI_mean_RGB':b[465:635,780:960].mean(axis=(0,1)).round(4).tolist()})
selected=[0,2,3,4,5,6,8,9,11,12,13]
for f in selected:shutil.copyfile(D/f'{f+1:05}.png',P/f'decoded/F{f:03}.png')
font=lambda n:ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',n)
def sheet(ff,name,crop=None,cols=4,tile=(480,270),scale=None):
 tw,th=tile;out=Image.new('RGB',(cols*tw,((len(ff)+cols-1)//cols)*(th+36)),'#f3f0e8');draw=ImageDraw.Draw(out)
 for i,f in enumerate(ff):
  im=Image.open(D/f'{f+1:05}.png').convert('RGB')
  if crop:im=im.crop(crop)
  if scale:im=im.resize((im.width*scale,im.height*scale),Image.Resampling.LANCZOS)
  else:im.thumbnail((tw-8,th))
  x,y=i%cols*tw+4,i//cols*(th+36)+34;out.paste(im,(x,y));draw.text((x,y-30),f'F{f:03} 实际解码',font=font(20),fill='#25333d')
 out.save(P/name,quality=97)
sheet(selected,'00_requested_actual_decodes.jpg')
sheet(list(range(14)),'01_all14_actual_order.jpg',cols=4)
sheet([0,2,3,4,5,6,8,9,11,12,13],'02_match_strike_fire_actual_2x.jpg',crop=(1010,705,1210,875),tile=(420,340),scale=2)
sheet([0,3,5,6,8,9,11,12,13],'03_eyes_actual_2x.jpg',crop=(815,480,965,580),tile=(330,200),scale=2)
sheet([0,3,5,6,9,13],'04_elbows_table_actual.jpg',crop=(685,900,1185,1045),cols=2,tile=(510,155))

integrity=json.loads((SRC/'INTEGRITY.json').read_text());layers=[]
for pose,entry in integrity['original_RGBA_assets'].items():
 name=pose[1:];orig=ROOT/entry['repository_path'];body=SRC/f'frames/F{name}_body_behind_original_pixels.png';arms=SRC/f'frames/F{name}_forearms_elbows_original_pixels.png'
 assert sha(orig.read_bytes())==entry['sha256']
 a=np.array(Image.open(orig));b=np.array(Image.open(body));c=np.array(Image.open(arms));assert a.shape==b.shape==c.shape==(1080,1920,4)
 assert not np.any((b[:,:,3]>0)&(c[:,:,3]>0)),pose
 restored=np.where((c[:,:,3]>0)[:,:,None],c,b)
 assert np.array_equal(restored,a),pose
 for file in [orig,body,arms]:assert file.read_bytes()==subprocess.check_output(['git','show',f'{FIXED}:{file.relative_to(ROOT)}'])
 layers.append({'pose':pose,'original_sha256':entry['sha256'],'body_sha256':sha(body.read_bytes()),'arms_sha256':sha(arms.read_bytes()),'alpha_overlap_pixels':0,'original_RGBA_reconstruction_changes':0})
module=SRC/'s08_first14_scene.js';assert sha(module.read_bytes())=='4557e5f89fddf2fc65527d7a3f312139e807324fe7c3dff039e2b9324ec8a6de'
for file in list(SRC.glob('*.js'))+[ROOT/'js/paint/paintshot.js',ROOT/'js/code/s08.js',ROOT/'tools/js/frames.cjs',ROOT/'assets/paint/bg_01_room_wide.png']:
 assert file.read_bytes()==subprocess.check_output(['git','show',f'{FIXED}:{file.relative_to(ROOT)}'])
source={'status':'PASS_FIXED_MODULE_AND_ALL5_ORIGINAL_PIXEL_PARTITIONS','fixed_commit':FIXED,'module_sha256':sha(module.read_bytes()),'native_originals':5,'exclusive_layers':10,'all_pixel_partitions_exact':True,'source_modules_background_runtime_tools_unchanged':True,'rows':layers}
(P/'source_validation.json').write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n')
result={'status':'PASS_REAL14_RENDER_ENCODE_ORDER_AND_FIRE_ONSET','fixed_commit':FIXED,'type':'REAL_CANVAS_SCENE_ONLY_000_013','frames':14,'fps':'24/1','duration_seconds':14/24,'size':[1920,1080],'audio_streams':0,'frames014_onward_rendered':False,'selected_actual_decodes':selected,'mp4_sha256':sha(mp4.read_bytes()),'all14_source_frames_match_encoded_order':True,'max_MSE':max(r['encoded_vs_source_MSE']for r in frames),'checks':frames,'visual_review':'See README; fragment/encoding pass is not full-shot or audio approval.'}
(P/'actual14_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');(P/'ffprobe.json').write_text(json.dumps(probe,ensure_ascii=False,indent=2)+'\n')
print('PASS real14f/1920x1080/24fps/14/24s; all14 encode order;maxMSE',result['max_MSE'])
print('PASS actual hot match-head pixels begin005; wick hot pixels0;5originals/10layers RGBA exact;fixed module SHA exact')
