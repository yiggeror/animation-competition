"""Compare the new actual Canvas PNGs with retained actual old84-frame render PNGs."""
from pathlib import Path
import json,hashlib,subprocess
from PIL import Image
import numpy as np
P=Path(__file__).resolve().parent;N=Path('/workspace/s01-migrate-38a5302d');O=Path('/workspace/s01-render-ab3644e0');old=O/'collab/reviews/20261018_1600_s01_full_scene'
frames=[0,10,12,20,28,29,30,31,32,33,34,35,43,50,62,70,83]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=(old/'s01_drawn_candidate.js').read_text();b=(N/'js/anim/s01_drawn.js').read_text()
assert b.count("'./s01_drawn_timeline.js'")==1 and b.count("'../../assets/chars/s01/'")==1
normalized=b.replace("'./s01_drawn_timeline.js'","'./timeline.js'").replace("'../../assets/chars/s01/'","'./frames/'")
assert normalized==a
resources=json.loads((P/'browser_resources.json').read_text());assert not resources['httpErrors'] and not resources['failedRequests'] and not resources['pageErrors'] and not resources['consoleErrors']
rows=[]
for f in frames:
 oldpng=O/'build/s01_full84'/f'{f:05d}.png';newpng=P/'frames'/f'F{f:03d}.png';x=np.array(Image.open(oldpng).convert('RGBA'));y=np.array(Image.open(newpng).convert('RGBA'));assert x.shape==y.shape==(720,1280,4)
 diff=np.abs(x.astype(np.int16)-y.astype(np.int16));changed=int(np.any(diff,axis=2).sum());maximum=int(diff.max())
 rows.append({'frame':f,'old_actual_png':str(oldpng),'new_actual_png':str(newpng.relative_to(P)),'old_sha256':sha(oldpng),'new_sha256':sha(newpng),'PNG_bytes_identical':oldpng.read_bytes()==newpng.read_bytes(),'changed_pixels':changed,'max_RGBA_channel_difference':maximum,'decoded_RGBA_identical':bool(np.array_equal(x,y))})
 assert changed==0 and maximum==0,f
assert not subprocess.check_output(['git','status','--porcelain'],cwd=N,text=True)
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=N,text=True).strip()=='38a5302d58a9c845600a496b478cefb3e657e74a'
report={'old_commit':'ab3644e096c0f9d94b5053f7c136ef515107e4b8','new_commit':'38a5302d58a9c845600a496b478cefb3e657e74a','old_module_sha256':sha(old/'s01_drawn_candidate.js'),'new_module_sha256':sha(N/'js/anim/s01_drawn.js'),'only_two_relative_path_substitutions':True,'timeline_SHA_equal':sha(old/'timeline.js')==sha(N/'js/anim/s01_drawn_timeline.js'),'width':1280,'height':720,'fps':24,'frames_checked':frames,'frame_count':17,'all17_PNG_bytes_identical':all(x['PNG_bytes_identical'] for x in rows),'all17_decoded_RGBA_identical':True,'total_changed_pixels':sum(x['changed_pixels'] for x in rows),'max_RGBA_channel_difference':max(x['max_RGBA_channel_difference'] for x in rows),'resource_HTTP_errors':0,'failed_requests':0,'page_errors':0,'console_errors':0,'scene_image_resources':[r for r in resources['responses'] if '.png' in r['url']],'favicon_note':'Browser housekeeping favicon.ico route is answered locally204; no scene/module/PNG response is substituted.','source_clean_after':True,'full_shot_rerendered':False,'audio_or_module_changed':False,'rows':rows}
(P/'pixel_comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['frame_count','all17_PNG_bytes_identical','all17_decoded_RGBA_identical','total_changed_pixels','max_RGBA_channel_difference','resource_HTTP_errors','source_clean_after']},indent=2))
