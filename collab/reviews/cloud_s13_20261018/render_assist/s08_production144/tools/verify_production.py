from pathlib import Path
import json,hashlib,subprocess,shutil,urllib.parse
from PIL import Image,ImageDraw
O=Path('collab/reviews/cloud_s13_20261018/render_assist/s08_production144');B=Path('build/S08_production144');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();baseline=json.loads((O/'approved_candidate144_baseline.json').read_text());assert len(baseline)==144 and len(list(B.glob('*.png')))==144
rows=[]
for b in baseline:
 i=b['frame'];p=B/f'{i:05}.png';h=sha(p);assert h==b['source_Canvas_SHA256'],i;rows.append({'frame':i,'actual_production_Canvas_SHA256':h,'approved_candidate_Canvas_SHA256':b['source_Canvas_SHA256'],'byte_equal':True})
(O/'all144_production_candidate_byte_comparison.json').write_text(json.dumps(rows,indent=2)+'\n')
E=[json.loads(x) for x in (O/'actual_network_events.jsonl').read_text().splitlines()];captures=[e for e in E if e['event']=='actual_frame'];assert len(captures)==144 and set(e['frame'] for e in captures)==set(range(144))
for e in captures:assert e['PNG_SHA256']==rows[e['frame']]['actual_production_Canvas_SHA256']
responses=[e for e in E if e['event']=='response'];assetrows=[e for e in responses if '/assets/chars/g08/' in e['url'] and urllib.parse.urlparse(e['url']).path.endswith('.png')];assets={urllib.parse.unquote(urllib.parse.urlparse(e['url']).path).lstrip('/') for e in assetrows};assert len(assets)==112 and all(e['status']==200 for e in assetrows)
reviews=[e for e in E if '/collab/reviews/' in e.get('url','')];assert not reviews
errors=[e for e in E if e['event'] in ['pageerror','requestfailed']];assert not errors
P=Path('build/S08_production144.mp4');mp4sha=sha(P);expected='e3f4fc04364d46ec7ff690ef7c20b2dd3138ce70219f75e3e173af87262d65be';assert mp4sha==expected,'MP4 differs; investigate before extending decode checks'
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(P)]));vs=[s for s in probe['streams'] if s['codec_type']=='video'];assert len(vs)==1 and len(probe['streams'])==1;v=vs[0];assert (int(v['nb_frames']),v['width'],v['height'],v['r_frame_rate'],float(v['duration']))==(144,1920,1080,'24/1',6.0)
(O/'ffprobe.json').write_text(json.dumps(probe,indent=2)+'\n');shutil.copyfile(P,O/'S08_production144_1920x1080_24fps.mp4')
D=Path('build/S08_production144_key_decoded');assert not D.exists();D.mkdir();cmd=['ffmpeg','-v','error','-i',str(P),'-vf','select=eq(n\\,0)+eq(n\\,96)+eq(n\\,136)+eq(n\\,143)','-vsync','0',str(D/'%02d.png')];subprocess.run(cmd,check=True)
board=Image.new('RGB',(960,600),'#1c2023');dr=ImageDraw.Draw(board)
for i,(p,f) in enumerate(zip(sorted(D.glob('*.png')),[0,96,136,143])):
 im=Image.open(p).convert('RGB').resize((480,270));x=(i%2)*480;y=(i//2)*300;board.paste(im,(x,y+24));dr.text((x+8,y+5),f'ACTUAL PRODUCTION MP4 DECODE F{f:03}',fill='white')
board.save(O/'actual_production_keyframes.jpg',quality=94)
net={'actual_frames':144,'production_unique_PNG_assets_200':len(assets),'production_asset_responses':len(assetrows),'all_production_asset_responses_200':True,'reviews_requests':0,'pageerror_or_requestfailed':errors,'non200_responses':[e for e in responses if e['status']!=200],'console_errors_actual_locations':[e for e in E if e['event']=='console_error'],'production_assets':sorted(assets)};(O/'actual_network_summary.json').write_text(json.dumps(net,indent=2)+'\n')
source=Path('js/anim/s08_drawn.js');assert source.read_bytes()==subprocess.check_output(['git','show','54796bf3835d6fe8e32a78ea3c854ac2a5d34d15:'+str(source)])
r={'status':'PRODUCTION144_BYTE_EQUIVALENT_TO_APPROVED_DD6E23BC','production_commit':'54796bf3835d6fe8e32a78ea3c854ac2a5d34d15','approved_candidate_commit':'dd6e23bca9f06bf219d2aff81d5aeab44f03c4ab','actual_production_render_runs':1,'actual_new_frames':144,'all144_Canvas_byte_equal':True,'MP4_byte_equal':True,'MP4_SHA256':mp4sha,'frames':144,'size':[1920,1080],'fps':'24/1','duration_seconds':6,'audio_streams':0,'production_assets_200':112,'reviews_requests':0,'candidate_rerendered':False,'imagegen_calls':0,'prior_all144_decode_proof_reused_by_identical_MP4_SHA':True,'new_production_key_decode_frames':[0,96,136,143],'shared_ready_EDL_audio_modified':False};(O/'verification.json').write_text(json.dumps(r,indent=2)+'\n');(O/'key_decode_command.json').write_text(json.dumps(cmd,indent=2)+'\n')
(O/'README.md').write_text('''# S08 production144 thin equivalence handoff

Production source `54796bf3835d6fe8e32a78ea3c854ac2a5d34d15`, entry `js/anim/s08_drawn.js`. The approved command was run once: `node tools/js/frames.cjs js/anim/s08_drawn.js build/S08_production144 --fps 24 --w 1920 --h 1080 --workers 2 --mp4 build/S08_production144.mp4` (read-only browser/network audit preloaded).

All144 actual production Canvas PNGs are byte-identical to approved candidate `dd6e23bca9f06bf219d2aff81d5aeab44f03c4ab`. The production MP4 is also byte-identical: SHA256 `'''+mp4sha+'''`. 144f /6s /1920×1080 /24fps /silent. Candidate was not rerendered. The previous complete decode proof applies by identical MP4 bytes; four production keys 000/096/136/143 were independently decoded for the included preview.

Actual browser audit:112 unique production PNG assets, all HTTP200; reviews requests0; page errors/failed requests0. The incidental favicon404 and console location are retained in the audit. No imagegen, shared ready, EDL or audio edits. Astra can register ready and hand to Opus for sound.

Thin package contains MP4, actual production decode preview, all144 byte-comparison ledger, actual network log and summary. Full raw production Canvas files remain in the local build cache; they are not duplicated in Git.
''')
manifest=[]
for p in sorted(O.rglob('*')):
 if p.is_file() and p.name!='SHA256SUMS':manifest.append(sha(p)+'  '+p.relative_to(O).as_posix())
(O/'SHA256SUMS').write_text('\n'.join(manifest)+'\n');print(json.dumps(r))
