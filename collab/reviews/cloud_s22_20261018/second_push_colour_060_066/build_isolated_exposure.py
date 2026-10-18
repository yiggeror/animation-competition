#!/usr/bin/env python3
"""Encode existing drawing exposures only; no scene or character rendering."""
from pathlib import Path
import hashlib, json, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as nd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCES = [
    ('F000', 'F000_color_repair/candidate/F000_repaired.png', 12, 'd4e78e2d5b84a72588cf3af1ff23ce39cdc18d19dde2fbf1f8eaf44ba62d7ef5'),
    ('F012', 'contact_band_repair_012_018_024/candidate/F012_contact_fixed.png', 6, 'f01d484e04dea7e3cde141d1aa2a94ecd0d45d25bc81f7d94f2f9a3f33757898'),
    ('F018', 'contact_band_repair_012_018_024/candidate/F018_contact_fixed.png', 6, 'c72e8afe8c5e73c17d66d57bc007f12fbfafd4efba9c0e3313f3010008c194a0'),
    ('F024', 'contact_band_repair_012_018_024/candidate/F024_contact_fixed.png', 12, '97560237598d024a725ab63ee62809d1f5ded5f6fc5aadc1d8a4f158ca85da4a'),
    ('F036', 'first_push_036_042/F036/candidate/F036_mapped.png', 6, 'ad6d47305791dd1fbc2d9849b8bd87d8632102f61dc29dce3ed5054867b49b4f'),
    ('F042', 'first_push_036_042/F042/candidate/F042_mapped.png', 18, '2a028a4c174c55e4cde7d794cd59561d39585c626740dd0afa7ffdd49f5b477c'),
    ('F060', 'second_push_colour_060_066/candidate/F060_colour_fixed.png', 6, '356c67d7c62efe46b4e68bece873407571adbc994801a622c39db2fdb1bfc136'),
    ('F066', 'second_push_colour_060_066/candidate/F066_colour_fixed.png', 18, '849de1cf2633d3818c59c73e5a68f22cca77a24c9fce8d44bce7b005385c1d60'),
]
for sub in ['qa', 'exposure_frames', 'decoded_actual', 'decoded_second_push', 'provenance']:
    (HERE / sub).mkdir(exist_ok=True)
font = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', 20)
small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
arrays, images, exposures = {}, {}, []
frame = 0
for name, rel, hold, expected in SOURCES:
    path = ROOT / rel
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    assert sha == expected, (name, sha)
    a = np.array(Image.open(path).convert('RGBA'))
    assert a.shape == (941, 1672, 4)
    arrays[name] = a
    plate = Image.new('RGBA', (1672, 941), (115, 115, 115, 255))
    plate.alpha_composite(Image.fromarray(a))
    images[name] = plate.convert('RGB')
    im = images[name].resize((1280, 720))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 1000, 36), fill=(25, 25, 25))
    d.text((10, 3), f'S22 隔离曝光（非实景） | {name} ×{hold} | 仅000–083', font=font, fill='white')
    im.save(HERE / 'exposure_frames' / (name + '.png'))
    exposures.append(dict(id=name, start=frame, end=frame+hold-1, hold=hold, source=rel, sha256=sha))
    frame += hold
assert frame == 84

def encode(filename, rows, selected, decoded_dir):
    count = sum(row['hold'] for row in rows)
    clip = HERE / filename
    command = ['ffmpeg', '-y', '-v', 'error', '-f', 'image2pipe', '-framerate', '24', '-i', '-', '-frames:v', str(count), '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', str(clip)]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    identities = []
    for row in rows:
        data = (HERE / 'exposure_frames' / (row['id'] + '.png')).read_bytes()
        for _ in range(row['hold']):
            process.stdin.write(data)
            identities.append(row['id'])
    process.stdin.close()
    assert process.wait() == 0
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-count_frames', '-show_streams', '-show_format', '-of', 'json', str(clip)], text=True))
    assert int(probe['streams'][0]['nb_read_frames']) == count
    assert probe['streams'][0]['r_frame_rate'] == '24/1'
    assert float(probe['format']['duration']) == count/24
    # Decode every frame and classify against the actual exposure stills.
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(clip), '-vf', 'scale=320:180', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
    decoded = np.frombuffer(raw, np.uint8).reshape((-1, 180, 320, 3)).astype(float)
    assert len(decoded) == count
    ids = [r['id'] for r in rows]
    refs = np.stack([np.array(Image.open(HERE/'exposure_frames'/(name+'.png')).resize((320,180))).astype(float) for name in ids])
    errors = np.mean((decoded[:,None]-refs[None])**2, axis=(2,3,4))
    classified = [ids[i] for i in errors.argmin(axis=1)]
    assert classified == identities, [(i,a,b) for i,(a,b) in enumerate(zip(identities,classified)) if a!=b]
    for f in selected:
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(clip),'-vf',f'select=eq(n\\,{f})','-frames:v','1',str(HERE/decoded_dir/f'F{f:03d}.png')],check=True)
    board = Image.new('RGB',(320*len(selected),206),(25,25,25))
    d = ImageDraw.Draw(board)
    for i,f in enumerate(selected):
        board.paste(Image.open(HERE/decoded_dir/f'F{f:03d}.png').resize((320,180)),(i*320,26))
        d.text((i*320+7,3),f'F{f:03d} / decoded MP4',font=small,fill='white')
    board.save(HERE/'qa'/(clip.stem+'_decoded.jpg'),quality=96)
    record = dict(clip=filename,sha256=hashlib.sha256(clip.read_bytes()).hexdigest(),fps=24,total_frames=count,duration_seconds=count/24,size=[1280,720],isolation_not_scene=True,rows=rows,decoded_open_frames=selected,all_decoded_frame_identities=classified,all_hold_boundaries_match=True,command=command,ffprobe=probe)
    (HERE/'provenance'/(clip.stem+'.json')).write_text(json.dumps(record,indent=2)+'\n')
    return {k:record[k] for k in ['clip','sha256','fps','total_frames','duration_seconds','size','all_hold_boundaries_match']}

clips = [encode('S22_060_083_colour24.mp4',exposures[-2:],[0,5,6,23],'decoded_second_push'),encode('S22_000_083_colour84.mp4',exposures,[41,42,59,60,65,66,83],'decoded_actual')]
for title,crop in [('contact_group',[610,350,1030,750]),('forearm_join',[300,320,720,750])]:
    cw,ch=crop[2]-crop[0],crop[3]-crop[1]
    board=Image.new('RGB',(cw*3,ch+35),(25,25,25));d=ImageDraw.Draw(board)
    for i,name in enumerate(['F042','F060','F066']):
        board.paste(images[name].crop(crop),(i*cw,35));d.text((i*cw+8,7),name+' / native same crop',font=small,fill='white')
    board.save(HERE/'qa'/(title+'_042_060_066_native.png'))
colours={}
for name in ['F024','F042','F060','F066']:
    a=arrays[name];samples=[[],[]]
    for x in range(250,351):
        labels,n=nd.label(a[:,x,3]>=128);bounds=[]
        for k in range(1,n+1):
            ys=np.where(labels==k)[0]
            if len(ys)>20:bounds.append([ys.min(),ys.max()+1])
        for i,b in enumerate([bounds[0],bounds[-1]]):
            y=int(sum(b)/2);samples[i].append(a[y-2:y+3,x,:3])
    colours[name]=dict(grandma_median_RGB=np.median(np.concatenate(samples[0]),axis=0).tolist(),child_median_RGB=np.median(np.concatenate(samples[1]),axis=0).tolist())
(HERE/'provenance/forearm_colour_check.json').write_text(json.dumps(dict(method='Native columns250-350, middle of actual alpha cross-section. Comparable neutral material; form shading can vary.',observed=colours),indent=2)+'\n')
summary=dict(clips=clips,new_image_calls_this_batch=0,successful_outputs_this_batch=0,cumulative_S22_attempts=9,cumulative_S22_successful_outputs=8,no_030=True,no_084=True,production_ready=False)
(HERE/'provenance/delivery_manifest.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
