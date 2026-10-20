"""Read-only artifact/source verification, then write only verification manifests."""
from pathlib import Path
import json, hashlib, subprocess, os
R=Path(__file__).resolve().parent
root=R.parents[3]; os.chdir(root); relative=str(R.relative_to(root))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda name:json.loads((R/name).read_text())
run=read('ACTUAL_BROWSER_RUN.json'); dec=read('REUSED6_NEW18_ACTUAL_DECODE_CHECK.json')
browser=read('FINAL24_ACTUAL_BROWSER_PLAYBACK_CHECK.json'); vis=read('ACTUAL_VISUAL_REVIEW.json'); src=read('COMPLETE_SLEEVE_SAME_RAW_SOURCE_CHECK.json')
assert run['pass'] and [f['globalFrame'] for f in run['frames']]==list(range(72,90))
assert run['sourceBefore']==run['sourceAfter']=={p:sha(Path(p)) for p in run['sourceBefore']}
assert not run['failed'] and not run['pageerrors'] and not run['consoleErrors']
assert len(dec['frame_exact_checks'])==24 and [f['global_frame'] for f in dec['frame_exact_checks']]==list(range(66,90))
assert all(f['differing_RGB_channels']==f['differing_YUV_samples']==0 for f in dec['frame_exact_checks'])
assert browser['pass'] and browser['playback']['totalVideoFrames']==24
assert browser['playback']['droppedVideoFrames']==browser['playback']['corruptedVideoFrames']==0
assert dec['final24_MP4_SHA256']==sha(R/'S29_F066_F089_REUSED6_NEW18_ACTUAL_1080p24_SILENT.mp4')
assert dec['new18_MP4_SHA256']==sha(R/'S29_F072_F089_NEW18_ACTUAL_SCENE_1080p24.mp4')
assert vis['status']=='HOLD_ONLY_UNCHANGED072_SLEEVE_CUFF_GAP' and len(vis['blockers'])==1
assert src['generation_calls']==0 and src['one_identical_source_piece_applied_to078_and084']
assert all(r['outside_full_semantic_domain_RGBA_changes']==r['all_rows620_plus_RGBA_changes']==0 and r['same_native078_whole_group_matrix'] for r in src['states'])
assert src['unchanged072_RGBA_SHA256']==sha(R/'F072_FINAL_RGBA.png')
assert src['unchanged066_RGBA_SHA256']==sha(R/'F066_UNCHANGED_LOCKED_RGBA.png')
for state in read('ORIGINAL_CALL_SOURCE_INDEX.json')['states']:
    for item in state['files']:assert sha(root/item['repository_path'])==item['SHA256']
for f in [72,78,84]:
    p=R/'keys'/f'S29_F{f:03d}_CANVAS.png'
    assert sha(p)==next(r['canvasPNG_SHA256'] for r in run['frames'] if r['globalFrame']==f)
for f in [66,71,72,77,78,83,84,89]:assert (R/'actual_decoded_keys'/f'S29_F{f:03d}_ACTUAL_DECODED.png').exists()
status=subprocess.check_output(['git','status','--porcelain'],text=True)
assert all(line[3:].startswith(relative+'/') for line in status.splitlines()),status
result={'artifact_integrity':'PASS','visual_gate':'HOLD_ONLY_UNCHANGED072_SLEEVE_CUFF_GAP','new_scene_renders':18,'reused_scene_frames':6,'new_generation_calls':0,'source_files_unchanged':True,'exact_reused_YUV_and_RGB':True,'actual_browser_playback24_frames':True,'only_exclusive_review_directory_changes':True,'ready_claimed':False}
(R/'FINAL_INTEGRITY_CHECK.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
files=sorted(p for p in R.rglob('*') if p.is_file() and p.name!='SHA256SUMS')
(R/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(R)}\n' for p in files))
for p in files:assert sha(p)==next(line.split('  ',1)[0] for line in (R/'SHA256SUMS').read_text().splitlines() if line.split('  ',1)[1]==str(p.relative_to(R)))
print(json.dumps(result,ensure_ascii=False));print('manifest files:',len(files))
