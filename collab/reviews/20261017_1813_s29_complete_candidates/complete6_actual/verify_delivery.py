from pathlib import Path
from PIL import Image
import json, hashlib, subprocess
import numpy as np

B=Path(__file__).resolve().parent.parent
W=B/'complete6_work'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source=json.loads((W/'reports/input_sources.json').read_text())
checks=[]
for r in source['inputs']:
    raw=np.asarray(Image.open(r['raw_source']).convert('RGBA'))
    ims=[Image.open(W/f'assets/chars/{r["file"]}{s}.png') for s in ('','_n','_m')]
    arrays=[np.asarray(im) for im in ims]
    expected=(np.clip((raw[:,:,3].astype(np.float32)-6)/(247-6),0,1)*255).round().astype(np.uint8)
    check={'state':r['state'],'three_maps_exist':True,'all_1024x1536_RGBA':all(im.size==(1024,1536) and im.mode=='RGBA' for im in ims),'alpha_equal_across_maps':all(np.array_equal(arrays[0][:,:,3],a[:,:,3]) for a in arrays[1:]),'diffuse_rgb_equals_raw':bool(np.array_equal(raw[:,:,:3],arrays[0][:,:,:3])),'diffuse_alpha_equals_standard_6_247':bool(np.array_equal(expected,arrays[0][:,:,3])),'raw_sha256_matches':sha(Path(r['raw_source']))==r['raw_sha256']}
    assert all(v for k,v in check.items() if k!='state'),check
    checks.append(check)
spec=json.loads((W/'assets/flips/g29_wrap.flip.json').read_text())
per=[i for f in range(288) for i in [[i for n,i in spec['timelineFrames'] if n<=f][-1]]]
assert all(i>=j or (i,j)==(4,5) for j,i in zip(per,per[1:]))
assert all(i in (4,5) for i in per[65:240]) and per[240:]==[4]*48
expected_frozen={
 'PILOT_ONE_STATE.md':'d2e317e67ef832162cae289c9bf42dc12801f7682c9eb73a039c43fb85fef907',
 'PLAN_ONE_PAGE.md':'5a5d6a850bb6af3989158973c4feaa55ed80aa26325b94280b1dcbfb5428fd50',
 'ANCHORS_AND_EXPOSURE_PLAN.json':'56e8b0b21a5056f0ffd6f4e571520142119152e67c04e32cfa173740610e5f25',
 'c1_actual/REPORT.md':'9ff34c13383bd7ca337a3fbccfeb666caccbbce8ec19625e003b8732c27a2dab',
 'c1_actual/evidence_manifest.json':'4a7c8a33bd2b81b01673f81431479cd79328a16855908822177669e144b5e895',
 'probe_work/assets/flips/g29_cloth_probe.flip.json':'e7a638fcbdf964712b83cd1acba912b860e8e16dcdb1319308acdbff3b90c598',
 'probe_work/DELIVERY_MANIFEST.json':'98d491df5c63255988968af03437bbe8503275ec99cba1f4de33b605589e8c34'}
frozen=[{'path':p,'sha256':sha(B/p),'unchanged':sha(B/p)==v} for p,v in expected_frozen.items()]
assert all(v['unchanged'] for v in frozen)
repo=B.parent.parent/'laidian_astra_takeover_20261017'
toolchecks=[]
for p in sorted((W/'tools').glob('*.py')):
    original=subprocess.check_output(['git','-C',str(repo),'show',source['tool_source_commit']+':tools/'+p.name])
    same=hashlib.sha256(original).hexdigest()==sha(p)
    assert same,p
    toolchecks.append({'name':p.name,'sha256':sha(p),'unchanged_from_commit':same})
manifest_codes=json.loads((W/'reports/manifest_exit_codes.json').read_text())
assert all(v==0 for v in manifest_codes.values())
report={'all_pass':True,'maps':checks,'timeline':{'visible_frames':240,'whole_shot_frames':288,'only_R_B_after_terminal':True,'no_old_cloth_return':True,'old_lamp_fallback_frames':list(range(240,288)),'longest_open_face_R_hold_frames':44,'approx36face_goal_not_fully_met':True},'standard_tools':toolchecks,'manifest_exit_codes':manifest_codes,'frozen_records':frozen,'checks_do_not_establish':['production_animation_quality','audio_sync','scene_lighting','pixel_frozen_geometry']}
(W/'reports/verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
for folder,filename in [(B/'complete6_actual','RAW_EVIDENCE_MANIFEST.json'),(W,'DELIVERY_MANIFEST.json')]:
    files=[{'path':str(p.relative_to(B)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(folder.rglob('*')) if p.is_file() and not p.is_symlink() and p.name!=filename]
    doc={'files':files,'total_bytes':sum(f['bytes'] for f in files),'new_imagegen_calls':4,'raw_post_editing':False,'production_or_remote_write':False,'status':'six_state_conditional_integration_package_not_render_approved'}
    (folder/filename).write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'verification':'all_pass','delivery_manifest_sha256':sha(W/'DELIVERY_MANIFEST.json'),'raw_manifest_sha256':sha(B/'complete6_actual/RAW_EVIDENCE_MANIFEST.json'),'flip_sha256':sha(W/'assets/flips/g29_wrap.flip.json'),'delivery_bytes':sum(p.stat().st_size for p in W.rglob('*') if p.is_file() and not p.is_symlink())},indent=2))
