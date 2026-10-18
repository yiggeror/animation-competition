#!/usr/bin/env python3
"""Validate native tail provenance, locked drawings and actual scene evidence."""
from pathlib import Path
from PIL import Image
import ast, hashlib, json, re, subprocess

P=Path(__file__).resolve().parents[1];R=P.parent;REPO=R.parents[2];S=R/'full_scene'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((S/'qa/scene_source_manifest.json').read_text())
drawings=manifest['source_drawings'];assert len(drawings)==16
for i,row in enumerate(drawings):
    p=REPO/row['path'];assert sha(p)==row['sha256']
    if i<13:
        assert p.read_bytes()==subprocess.check_output(['git','show','57ea966d:'+row['path']],cwd=REPO),row['path']
for dep in manifest['dependencies']:
    p=REPO/dep['path'];assert sha(p)==dep['sha256']
    assert p.read_bytes()==subprocess.check_output(['git','show','57ea966d:'+dep['path']],cwd=REPO)
ledger=json.loads((R/'provenance/generation_ledger.json').read_text())
assert ledger['image_generation_requests']==ledger['successful_raw_images']==len(ledger['raw_outputs'])==18
assert ledger['unique_adopted_pose_count']==16 and ledger['rejected_raw_outputs']==2
assert ledger['full_film_render_runs']==ledger['blender_runs']==ledger['external_paid_service_or_api_calls']==0
assert ledger['full120_frame_scene_render_runs']==ledger['Canvas_browser_audit_probe_runs']==1
source=REPO/drawings[12]['path']
for n,row in enumerate(ledger['raw_outputs'][-3:],16):
    req=json.loads((P/f'requests/call_{n:03}_request.json').read_text())
    res=json.loads((P/f'requests/call_{n:03}_response.json').read_text())
    meta=json.loads((P/f'requests/call_{n:03}_tool_return_metadata.json').read_text())
    assert req['args']['referenced_image_paths']==[str(source)]
    assert req['dependency_sha256']==res['inputs'][0]['sha256']==sha(source)
    assert req['args']['transparent_background'] is True and req['args']['prompt']
    raw,out,default=R/row['path'],R/row['adopted_output'],Path(row['source_tool_path'])
    assert sha(raw)==sha(out)==sha(default)==res['raw_sha256']==row['sha256']==drawings[n-3]['sha256']
    assert res['tool_original_path'] in meta['output_hint']
    with Image.open(out) as im:
        im.load();assert im.mode=='RGBA' and im.size==(1024,1536)
    source=out
plan=json.loads((R/'geometry/S13_reference_plan.json').read_text())
assert plan['frames']==sum(k['hold'] for k in plan['keys'])==120 and len(plan['keys'])==16
assert [(k['f'],k['hold']) for k in plan['keys']]==[(r['start'],r['hold']) for r in drawings]
assert [(r['start'],r['hold']) for r in drawings[-3:]]==[(90,4),(94,6),(100,20)]
audit=json.loads((S/'qa/browser_audit.json').read_text())
assert audit['duration']==5 and audit['canvas']==[1280,720] and not audit['page_errors']
assert all(r['url']=='/favicon.ico' for r in audit['http_errors'])
assert len(audit['sheet'])==16 and len(audit['states'])==120
for f,state in enumerate(audit['states']):
    expected=max(i for i,r in enumerate(drawings) if f>=r['start'])
    assert state['frame']==f and state['drawing']==expected+1 and state['path']=='/'+drawings[expected]['path']
scene=json.loads((S/'qa/actual_120f_scene_validation.json').read_text())
assert sha(S/'S13_drawn_120f_720p24.mp4')==scene['mp4_sha256']
assert scene['status']=='PASS' and scene['frames']==120 and scene['fps']=='24/1' and scene['audio_streams']==0
assert len(scene['checks'])==120 and all(r['expected']==r['decoded_nearest'] for r in scene['checks'])
assert max(r['source_vs_encoded_MSE'] for r in scene['checks'])<40
assert len(json.loads((S/'qa/rendered_120_source_frame_hashes.json').read_text()))==120
old=(REPO/'js/paint/shots/s13.js').read_text()
section=old[old.index('let ROOM,CRANE;'):old.index('export async function renderFrame')]
assert section in (S/'s13_drawn.js').read_text()
for p in R.rglob('*.json'):json.loads(p.read_text())
for p in R.rglob('*.py'):ast.parse(p.read_text(),filename=str(p))
for p in [S/'s13_drawn.js',*S.glob('tools/*.cjs')]:subprocess.run(['node','--check',str(p)],check=True)
subprocess.run(['bash','-n',str(S/'tools/render_scene.sh')],check=True)
images=list(R.rglob('*.png'))+list(R.rglob('*.jpg'))
for p in images:
    with Image.open(p) as im:im.verify()
for md in [R/'README.md',P/'README.md',S/'README.md',R/'d11_d13_group/README.md']:
    for link in re.findall(r'\]\(([^)]+)\)',md.read_text()):
        if not link.startswith(('http:','https:','#')):assert (md.parent/link.split('#')[0]).exists(),(md,link)
assert subprocess.check_output(['git','branch','--show-current'],cwd=REPO,text=True).strip()=='cloud/s13-reference-20261018-1332'
changed=subprocess.check_output(['git','status','--porcelain','-uall'],cwd=REPO,text=True).splitlines()
assert all(r[3:].startswith(str(R.relative_to(REPO))+'/') for r in changed),changed
result={'status':'PASS','locked_drawings_unchanged':13,'new_tail_native_byte_identical_to_raw_and_default':3,'strict_chain':'locked_d13→d14→d15→d16','total_requests':18,'adopted_poses':16,'prior_rejected_raws_retained':2,'exact_shared_dependencies_unchanged':len(manifest['dependencies']),'scene':'real Chromium Canvas1280×720/24fps/120f/5s','all120_encoded_frames_match_Canvas_order_and_exposure':True,'max_source_encoded_MSE':scene['max_source_vs_encoded_MSE'],'required_asset_or_page_errors':0,'audio_streams':0,'all_delivery_images_decodable':len(images),'syntax_and_relative_links':'PASS','manual_visual_review':'native same-scale/three bases/head-root/free-tail and decoded full scene16 states/boundaries actually viewed;F084 closure beforeF087 turn;F100 tail settled through119','pending':'Astra full scene/tail review;audio integration and validation'}
(P/'qa/delivery_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
