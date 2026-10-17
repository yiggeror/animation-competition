from pathlib import Path
import json, hashlib, shutil

BASE=Path(__file__).resolve().parent.parent
WORK=BASE/'complete6_work'
for d in ('inputs','tools','assets/chars','assets/flips','reports'):
    (WORK/d).mkdir(parents=True,exist_ok=True)
for f in ('prep_flip.py','card_maps.py','card_soft.py','flip_manifest.py'):
    shutil.copy2(BASE/'probe_work/tools'/f,WORK/'tools'/f)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
states=[
  ('C0',BASE.parent/'batch2_scope/refs/g29_wrap.png',[[370,994],[367,1340]]),
  ('D',BASE/'c1_actual/C1_raw.png',[[370.15065427504385,994.0737316208365],[367.37497422001184,1340.2173754991918]])
]
for state in ['T','P','R','B']:
    r=json.loads((BASE/f'complete6_actual/reports/{state}_raw_review.json').read_text())
    states.append((state,BASE/f'complete6_actual/raw/{state}.png',r['raw_AB']))
records=[]
for i,(state,source,anchors) in enumerate(states,1):
    stem=f'g29_cloth_close_k{i:02d}'
    link=WORK/f'inputs/{stem}.png'
    if not link.exists(): link.symlink_to(source)
    records.append({'index':i-1,'state':state,'file':stem,'raw_source':str(source),'raw_sha256':sha(source),'anchors':anchors})
timeline=[[0,0],[24,1],[36,2],[39,3],[65,4],[94,5],[96,4],[135,5],[137,4],[181,5],[183,4],[220,5],[222,4],[240,4]]
spec={'target':{'width':1024,'height':1536,'anchors':[[370,994],[367,1340]]},'fps':24,'frames':[{'file':r['file'],'anchors':r['anchors']} for r in records],'timelineFrames':timeline}
(WORK/'assets/flips/g29_wrap.flip.json').write_text(json.dumps(spec,indent=2)+'\n')
(WORK/'reports/input_sources.json').write_text(json.dumps({'tool_source_commit':'d0fa610fe8b4eccbe93cef016a9e88cc55fa01e8','inputs':records},indent=2)+'\n')
copy=[]
for r in records:
  for suf in ('','_n','_m'):
    path=f'assets/chars/{r["file"]}{suf}.png'
    copy.append({'source_relative_to_s29_grandma_prepare':f'complete6_work/{path}','destination_relative_to_repo':path})
path='assets/flips/g29_wrap.flip.json'
copy.append({'source_relative_to_s29_grandma_prepare':f'complete6_work/{path}','destination_relative_to_repo':path})
(WORK/'COPY_MAP.json').write_text(json.dumps(copy,indent=2)+'\n')
(WORK/'COPY_PATHS.txt').write_text('\n'.join(r['source_relative_to_s29_grandma_prepare']+' -> '+r['destination_relative_to_repo'] for r in copy)+'\n')
segments=[]
for k,(start,idx) in enumerate(timeline):
    end=timeline[k+1][0]-1 if k+1<len(timeline) else 287
    segments.append({'start_inclusive':start,'end_inclusive':end,'exposure_frames':end-start+1,'state':records[idx]['state'],'card_index':idx,'role':'visible_grandma' if start<240 else 'fallback_only_existing_lamp_code_owns_render'})
(WORK/'reports/exposure_and_cues.json').write_text(json.dumps({'fps':24,'visible_frames':240,'whole_shot_frames':288,'segments':segments,'longest_identical_open_face_visible_frames':44,'face_hold_limit_note':'The previous approx.36-frame wish is exceeded by 8 frames in the R137-180 hold. This is disclosed, not fixed by old-cloth replay or extra calls. Opus must judge the real-shot pacing.','cues_proposed_not_audio_edits':[{'frame':24,'seconds':1.0,'event':'Deeper inward closing; start main cloth friction','audio_note':'Existing cloth cue begins here. Re-envelope to actual states; do not stretch pressure to fill old rustle.'},{'frame':36,'seconds':1.5,'event':'Fingertip tucks final edge','audio_note':'Short concentrated cloth friction; no reopening.'},{'frame':39,'seconds':1.625,'event':'Two hands press folded top flat','audio_note':'Leather cue originally 1.6s=F38.4; integer contact F39 is +25ms. Preserve placement only if listening confirms it matches contact.'},{'frame':65,'seconds':2.7083333333333335,'event':'Hands ease to terminal resting posture','audio_note':'Small release tail only if audibly justified; no new repetitive rubbing.'}],'unchanged_scene_boundaries':{'wide_cut_first_integer_frame':116,'phone_boot_frame':132,'xiaoman_turn_seconds':[8.1,8.42],'old_lamp_code_start_frame':240},'audio_audition_performed':False,'production_render_performed':False},ensure_ascii=False,indent=2)+'\n')
print(WORK)
print(' '.join('inputs/'+r['file']+'.png' for r in records))
