"""Source-only 96f handoff; verifies git objects without rendering or copying art."""
from pathlib import Path
from PIL import Image
import csv, hashlib, io, json, subprocess

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
PREFIX = 'collab/reviews/cloud_s09_20261018/'
BASE = '10262cd16d1f3b81b38f0d49f44a3c063a2fa17c'
SECOND = '4e25e5f07a8aa86926634b21b9f5884f547cbb10'
rows = [
 (0,7,'switch_segment/locked/F000_raw_alpha_clean.png','OFF',False,'LOCKED','Natural raw mother; alpha==1 noise cleanup only.'),
 (8,13,'switch_segment/candidates/d02_raw_locked.png','OFF',False,'LOCKED','Thumb pre-push; complete existing locked state.'),
 (14,17,'switch_segment/candidates/d03_raw_locked.png','ON',False,'LOCKED','First ON fails; lamp remains dark.'),
 (18,25,'switch_segment/candidates/d04_raw_locked.png','ON',False,'LOCKED','Wait for failed first ON.'),
 (26,30,'pre_tap_segment/candidates/d05_raw_locked.png','OFF',False,'LOCKED','Reset OFF.'),
 (31,36,'pre_tap_segment/clothing_semantic_review/continuous_contour_delivery/candidate/F031_raw_clothing_and_contours_for_final_lock.png','OFF',False,'LOCKED','Final continuous skirt contour; use 4b59 source.'),
 (37,41,'first_tap_segment/whole_far_puff_zero_call/candidate/F037_whole_native_far_puff_PENDING.png','OFF',False,'LOCKED','Later Astra lock overrides historical PENDING filename.'),
 (42,43,'first_tap_segment/F042_contact_gate/astra_two_corridors_zero_call/candidate/F042_two_corridors_clean_PENDING_ASTRA.png','OFF',False,'LOCKED','First independent tailcap contact.'),
 (44,47,'first_tap_segment/F044_rebound_gate/candidate/F044_complete_local_native_arm_PENDING_ASTRA.png','OFF',False,'LOCKED','First rebound; actual 48 native =30.2267 registered px clearance.'),
 (48,51,'first_tap_segment/F048_recovery_reuse_gate/candidate/F048_recovery_TRUE_LOCKED_F037_REUSE_PENDING_ASTRA.png','OFF',False,'LOCKED','Exact whole locked037 reuse.'),
 (52,55,'@SECOND','OFF',False,'LOCKED','Unique a107f71d locked approach; never substitute historical TRIAL.'),
 (56,57,'first_tap_segment/F042_contact_gate/astra_two_corridors_zero_call/candidate/F042_two_corridors_clean_PENDING_ASTRA.png','OFF',False,'LOCKED','Second independent contact; exact whole locked042 reuse.'),
 (58,59,'F058_reuse_locked044_gate/candidate/F058_exact_LOCKED044_REUSE_PENDING_ASTRA.png','OFF',False,'LOCKED','Exact locked044 reuse. Latest bridge exposure splits former 058x5 into 058x2/060x2/062x1.'),
 (60,61,'F060_F062_NATIVE_from_APPROVED6940a80f_20261019/F060/qa/F060_whole_fixed770x924_inverse.png','OFF',False,'PENDING_ASTRA_NOT_ADOPTED','Usable raw turning direction per latest Astra review; projected overlap alone is not collision. Whole registered raw reference, head/skirt source restore still pending.'),
 (62,62,'F060_F062_NATIVE_from_APPROVED6940a80f_20261019/F062/qa/F062_whole_fixed770x924_inverse.png','OFF',False,'PENDING_REPAIR_AND_ASTRA_NOT_ADOPTED','Raw reference only; tail hidden behind near forearm. Latest zero-call real-prop layer diagnostic is separate and remains incomplete at old hand occlusion hole.'),
 (63,68,'F063_zero_call_semantic_reintegration_20261019/candidate/F063_zero_call_semantic_RECONNECTED.png','OFF',False,'LOCKED','Locked short-puff operating transition; receiver still has material air.'),
 (69,72,'F069_SHORT_PUFF_NATIVE_call01_12e88f6f_20261019/candidate/F069_SHORT_PUFF_BARE_ARMS_semantic_RECONNECTED_SECOND_REVIEW.png','TRANSIT',False,'LOCKED','Formally locked bc649 short-puff/bare-arms full-body state; supports front and starts second push.'),
 (73,76,'F069_LOCKED_SHORT_PUFF_TAIL_RECONNECTION_20261019/candidate/F073_SHORT_PUFF_BARE_ARMS_own_push_FIRST_ON.png','ON',True,'LOCKED','New short-puff body, own full hands/slider push; original light layers included. First light at073.'),
 (77,84,'F069_LOCKED_SHORT_PUFF_TAIL_RECONNECTION_20261019/candidate/F077_SHORT_PUFF_073_body_original_head_state.png','ON',True,'LOCKED','Same locked short-puff073 body plus original whole head/neck state.'),
 (85,95,'F069_LOCKED_SHORT_PUFF_TAIL_RECONNECTION_20261019/candidate/F085_SHORT_PUFF_073_body_original_head_state.png','ON',True,'LOCKED','Same locked short-puff073 body plus original whole head/neck state; final lit hold.'),
]
states = []
for start,end,rel,switch,light,status,note in rows:
    commit = SECOND if rel == '@SECOND' else BASE
    path = 'collab/reviews/20261018_2216_s09_second_tap_repair/candidate/F052_rgba_LOCKED.png' if rel == '@SECOND' else PREFIX+rel
    data = subprocess.check_output(['git','show',f'{commit}:{path}'],cwd=ROOT)
    im = Image.open(io.BytesIO(data))
    assert im.size == (1672,941) and im.mode == 'RGBA', (start, im.size, im.mode)
    actual = ROOT/path
    local_match = actual.exists() and actual.read_bytes() == data
    states.append(dict(state=f'F{start:03}',start_frame_0=start,end_frame_inclusive=end,hold=end-start+1,
      source_commit=commit,path=path,sha256=hashlib.sha256(data).hexdigest(),size=list(im.size),mode=im.mode,
      status=status,adopted=status=='LOCKED',switch=switch,light_on=light,note=note,
      current_worktree_has_identical_source=local_match))
coverage = [f for s in states for f in range(s['start_frame_0'],s['end_frame_inclusive']+1)]
assert coverage == list(range(96))
for a,b in [(37,48),(42,56),(44,58)]:
    assert next(s for s in states if s['start_frame_0']==a)['sha256'] == next(s for s in states if s['start_frame_0']==b)['sha256']
assert next(s for s in states if s['start_frame_0']==52)['sha256']=='a107f71d994c3302884eb3ebba0e8e4726b89bd5e36c2f8a8fa022f44ddfbb42'
doc = dict(shot='S09',fps=24,total_frames=96,duration_seconds=4,source_states=20,
  scope='Source-only integration handoff. 18 locked exposure states plus pending060/062; not full-scene approval.',
  latest_authority='Parent/Astra cloud instruction 2026-10-19: preserve000-058 old locks,063 onward newly locked short-puff sources;060/062 pending; no new generation.',
  frozen_source_grid=[1672,941],
  existing_registration_reference=dict(scale=.6297229219143576,translation_xy=[241.2216624685139,83.47607052896726],registered_canvas=[1536,864],existing_waist_up_crop_xyxy=[280,80,1304,656],note='Historical approved common scene registration; all listed source PNGs remain native1672x941. No per-state fitting or production camera change performed.'),
  events=dict(first_ON_failed=14,tail_contacts=[42,56],second_ON_transit_dark=[69,72],first_light=73),
  limits=['060/062 paths are exact raw-based REFERENCES, not adopted images. Do not silently promote their 3f into final.',
          '063+ source filenames preserve historical status words; latest explicit Astra locks govern.',
          '073/077/085 full RGBA sources already include original lit lens/beam pixels; do not double-compose physical torch or these image light layers.',
          '052 is available by exact4e commit:path and also archived in F058_reuse_locked044_gate/sources/F052_LOCKED_a107.png; no source image is copied into this index.',
          'Index only: no old evidence package, video render, art mutation, new native request or RGB drawing.'],
  new_native_requests=0,new_raw_outputs=0,new_renders=0,coverage_frames=coverage,states=states)
(OUT/'S09_final_96f_SOURCE_INDEX_PENDING060_062.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
cols=['state','start_frame_0','end_frame_inclusive','hold','status','source_commit','path','sha256','switch','light_on']
with (OUT/'S09_final_96f_exposure_sources.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(states)
lines=['# S09 96帧采用源短索引','',
 '24fps／96帧／4秒。只列准确commit:path、SHA与曝光，不复制旧图或旧证据、不重渲。全部源图统一1672×941 RGBA；JSON附原全局注册供接入参考。',
 '', '000–058沿已锁旧态；063起使用已锁短蓬袖裸臂源；060/062明确未采用。058旧5帧现分为058×2→060×2→062×1，063起曝光不变。文件名中的历史PENDING不推翻后续Astra显式锁。',
 '', '|态|场景帧|持帧|当前状态|SHA256|','|---|---|---:|---|---|']
for s in states: lines.append(f"|{s['state']}|{s['start_frame_0']:03}–{s['end_frame_inclusive']:03}|{s['hold']}|{s['status']}|`{s['sha256']}`|")
lines += ['', '完整可直接读取路径见 [JSON](S09_final_96f_SOURCE_INDEX_PENDING060_062.json) 或 [CSV](S09_final_96f_exposure_sources.csv)。052固定4e/a107；037=048、042=056、044=058逐字节相同。所有源已从列明git对象解码并核SHA；覆盖000–095无漏帧/重叠。',
 '', '060按最新Astra实看撤回旧“投影重叠=碰撞”判断；062零调用层次诊断另交，真实道具旧握持缺源仍外露，不能标为修复通过。073/077/085图源自带原亮灯像素，接入时避免重复绘制整灯/同一图像灯层。',
 '', '源整态锁与全96f机位/遮挡/声画验收范围分开；此索引不代表整镜通过。']
(OUT/'README.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(dict(index_sha256=hashlib.sha256((OUT/'S09_final_96f_SOURCE_INDEX_PENDING060_062.json').read_bytes()).hexdigest(),states=len(states),frames=len(coverage),pending=[s['state'] for s in states if not s['adopted']],all_git_sources_decoded=True),indent=2))
