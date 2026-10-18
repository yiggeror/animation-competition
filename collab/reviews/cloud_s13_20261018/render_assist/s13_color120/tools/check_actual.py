#!/usr/bin/env python3
"""Read-only verification of real Canvas sources and the encoded S13 scene."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib, io, json, shutil, subprocess, zipfile
import numpy as np

P = Path(__file__).resolve().parents[1]
R = Path.cwd()
FIXED = '06a588dfbcb0124dfeaee563bcde07613f6bf5f6'
S = R/'build/s13_color120'
D = Path('/tmp/s13_color120_decoded')
D.mkdir(exist_ok=True)
starts = [0,18,24,30,36,40,44,50,58,68,78,84,87,90,94,100]
selected = starts+[119]
sha = lambda b: hashlib.sha256(b).hexdigest()
mp4 = P/'S13_color120_720p24.mp4'
assert mp4.read_bytes() == (R/'build/S13_color120.mp4').read_bytes()
probe = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(mp4)],text=True))
v = probe['streams'][0]
assert len(probe['streams']) == 1 and v['codec_type'] == 'video'
assert (v['width'],v['height'],v['r_frame_rate'],v['nb_frames'],float(v['duration'])) == (1280,720,'24/1','120',5.0)
assert sorted(x.name for x in S.glob('*.png')) == [f'{f:05}.png' for f in range(120)]
subprocess.run(['ffmpeg','-y','-v','error','-i',str(mp4),'-fps_mode','passthrough',str(D/'%05d.png')],check=True)
assert len(list(D.glob('*.png'))) == 120
rows = []
for f in range(120):
    a = np.array(Image.open(S/f'{f:05}.png').convert('RGB'),dtype=np.float32)
    b = np.array(Image.open(D/f'{f+1:05}.png').convert('RGB'),dtype=np.float32)
    mse = float(np.mean((a-b)**2))
    assert mse < 50, (f,mse)
    state = max(s for s in starts if s <= f)
    rows.append({'frame':f,'drawing_start':state,'Canvas_source_sha256':sha((S/f'{f:05}.png').read_bytes()),'encoded_vs_source_MSE':mse})
for f in selected:
    shutil.copyfile(D/f'{f+1:05}.png',P/f'decoded/F{f:03}.png')

font = lambda n: ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',n)
def sheet(frames,name,cols=4,crop=None,tile=(480,270),label='实际解码',scale=None):
    tw,th = tile
    out = Image.new('RGB',(cols*tw,((len(frames)+cols-1)//cols)*(th+36)), '#eeeae2')
    draw = ImageDraw.Draw(out)
    for i,f in enumerate(frames):
        im = Image.open(D/f'{f+1:05}.png').convert('RGB')
        if crop is not None:
            box = crop(f) if callable(crop) else crop
            im = im.crop(box)
        if scale is not None:
            im=im.resize((im.width*scale,im.height*scale),Image.Resampling.LANCZOS)
        else:
            im.thumbnail((tw-8,th))
        x,y = i%cols*tw+4,i//cols*(th+36)+34
        out.paste(im,(x,y))
        draw.text((x,y-30),f'F{f:03} {label}',font=font(20),fill='#263039')
    out.save(P/name,quality=96)

sheet(selected,'00_all_requested_decoded.jpg')
sheet(starts[:8],'01_portraits_000_050_actual.jpg',crop=(270,30,800,720),tile=(400,521))
sheet(starts[8:]+[119],'02_portraits_058_119_actual.jpg',crop=(270,30,800,720),tile=(400,521))
def eye_mouth_box(f):
    # Fixed native QA boxes from the upstream color audit, mapped by the unchanged scene placement.
    if f < 87: box=(570,550,915,842)
    elif f == 87: box=(505,550,905,842)
    elif f == 90: box=(200,550,585,835)
    else: box=(130,550,460,835)
    x0,y0,x1,y1=box
    return tuple(round(z) for z in (220+x0*.85*2/3,-20+y0*.85*2/3,220+x1*.85*2/3,-20+y1*.85*2/3))
sheet(starts,'03_eyes_mouth_actual_2x.jpg',crop=eye_mouth_box,tile=(470,340),label='实际眼口裁近2×',scale=2)
sheet([78,83,84,85,86,87,88,89,90,94,99,100,110,119],'04_close84_turn87_settle_actual.jpg',crop=(285,45,800,720),tile=(350,459))
sheet(list(range(120)),'05_all120_decoded_order.jpg',cols=10,tile=(256,144),label='')

up=R/'collab/reviews/20261018_1712_s13_semantic_color'
frozen=json.loads((up/'FROZEN.json').read_text())
zip_path=up/'S13_semantic_color_repro_minimal.zip'
art=[]
with zipfile.ZipFile(zip_path) as z:
    for rec in frozen['images']:
        f,path=rec['frame'],rec['production_path']
        before=subprocess.check_output(['git','show',f'{FIXED}^:{path}'])
        current=(R/path).read_bytes()
        assert sha(before)==rec['source_sha256'] and sha(current)==rec['candidate_sha256']
        assert current==subprocess.check_output(['git','show',f'{FIXED}:{path}'])
        a=np.array(Image.open(io.BytesIO(before))); b=np.array(Image.open(io.BytesIO(current)))
        mask=lambda name:np.array(Image.open(io.BytesIO(z.read(f'masks/F{f:03}_{name}.png'))))>0
        edit=np.logical_or.reduce([mask(f'{k}_effective_edit_mask') for k in ['hair','skin','dress']])
        ink,feature=mask('lineart_lock'),mask('feature_exclusions')
        checks={'alpha_changed':int(np.count_nonzero(a[:,:,3]!=b[:,:,3])),
                'locked_line_changed':int(np.count_nonzero(np.any(a[ink]!=b[ink],axis=1))),
                'outside_effective_mask_changed':int(np.count_nonzero(np.any(a[~edit]!=b[~edit],axis=1))),
                'protected_eyes_mouth_changed':int(np.count_nonzero(np.any(a[feature]!=b[feature],axis=1)))}
        assert all(v==0 for v in checks.values()),(f,checks)
        if f in [0,18]: assert current==before
        art.append({'frame':f,'source_sha256':sha(before),'adopted_sha256':sha(current),**checks})
module='js/anim/s13_drawn.js'
assert (R/module).read_bytes()==subprocess.check_output(['git','show',f'{FIXED}^:{module}'])
assert (R/module).read_bytes()==subprocess.check_output(['git','show',f'{FIXED}:{module}'])
source={'fixed_commit':FIXED,'module_sha256':sha((R/module).read_bytes()),'module_identical_to_parent':True,'geometry_alpha_line_outside_feature_changes':0,'F000_F018_byte_identical':True,'all16':art,'upstream_FROZEN_sha256':sha((up/'FROZEN.json').read_bytes()),'upstream_repro_archive_sha256':sha(zip_path.read_bytes()),'mask_checks_independently_repeated':True,'semantic_mean_gate':'Upstream material-specific FROZEN maximum0.4959; not a +/-4 claim for scene pixels under changing original illumination.'}
(P/'source_validation.json').write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n')
result={'status':'PASS_REAL120_RENDER_AND_ENCODE_ORDER','fixed_commit':FIXED,'module':'/js/anim/s13_drawn.js','type':'REAL_CANVAS_SCENE','frames':120,'fps':'24/1','duration_seconds':5.0,'size':[1280,720],'audio_streams':0,'selected_decoded':selected,'all120_source_frames_match_encoded_order':True,'max_MSE':max(x['encoded_vs_source_MSE'] for x in rows),'mp4_sha256':sha(mp4.read_bytes()),'checks':rows,'visual_review':'See README; renderer/encoding checks alone do not grant final artistic approval.'}
(P/'actual120_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(P/'ffprobe.json').write_text(json.dumps(probe,ensure_ascii=False,indent=2)+'\n')
print('PASS real120/24fps/5s/720p; all120 source order; maxMSE',result['max_MSE'])
print('PASS all16 adopted SHA, F000/F018 original bytes, module unchanged; alpha/line/outside/protected features0 changes')
