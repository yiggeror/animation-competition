from pathlib import Path
import json,hashlib,shutil,itertools
W=Path('/workspace/scratch/f060b5601755/laidian_astra_takeover_20261017_work'); G=W/'grandma_author'; D=W/'grandma_trial_delivery'; S=D/'package'; base='collab/reviews/20261017_1622_s01_grandma_trial'
def cp(p,rel):
 o=S/rel;o.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,o)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((G/'S01_BATCH4_MANIFEST.json').read_text()); assert sha(G/'S01_BATCH4_MANIFEST.json')=='5a370668213fdcd0361a9905d398fbba9118d5a1459b76a7b0fa714989074183'
assert len(m['candidate_ids'])==9 and len(m['assets'])==27 and m['quarantined_ids']==['f01']
for e in m['assets']:
 assert sha(G/e['path'])==e['sha256']; assert sha(S/'probe'/e['path'])==e['sha256']
for e in m['review_artifacts']:assert sha(G/e['path'])==e['sha256']
checks={}
for c in m['candidates']:
 p=G/c['flip']; assert sha(p)==c['sha256']; f=json.loads(p.read_text()); t=json.loads((G/c['timing_report']).read_text()); assert sha(G/c['timing_report'])==c['timing_sha256']
 assert f['totalFrames']==288 and f['fps']==24 and len(f['frames'])==9
 names=[x['file'].removeprefix('g01_s01_') for x in f['frames']]; assert 'f01' not in names and set(names)==set(m['candidate_ids'])
 keys=f['timelineFrames']; assert keys[0][0]==0 and all(a[0]<b[0] for a,b in zip(keys,keys[1:])); seq=[]
 for i,(start,ix) in enumerate(keys):
  end=keys[i+1][0] if i+1<len(keys) else 288;seq.extend([names[ix]]*(end-start))
 assert len(seq)==288
 cats=[x if x.startswith('f') else 'working' for x in seq];runs=[];start=0
 for cat,grp in itertools.groupby(cats):
  n=len(list(grp));runs.append({'start':start,'end_exclusive':start+n,'frames':n,'face_category':cat});start+=n
 assert runs==t['face_runs']; longest=max(r['frames'] for r in runs if r['face_category']=='working');assert longest==c['maximum_working_face_hold_frames']
 blinks=[r['start'] for r in runs if r['face_category']=='f02']; assert blinks==t['blink_start_frames'];assert len(blinks)==c['blink_count'];assert all(r['frames']==2 for r in runs if r['face_category']=='f02')
 for b in blinks:assert seq[b-1]=='c04' and seq[b+2]=='c04'
 for look in t['look_child_sequences']:assert [seq[i] for i in look]==['f03','f04','f03','c04']
 for e in t['actual_bean_result_frames']:
  for field,state in [('closed_pod_fetch','c01'),('closed_pod_lift','c02b'),('open_pod_frame','c04'),('first_bean_falling','c04b'),('last_bean_falling','c05c'),('empty_husk_on_pile','c06b')]:assert seq[e[field]]==state
 assert all(len(list(g))<=3 for k,g in itertools.groupby(seq) if k in ['c04b','c05c'])
 checks[c['variant']]={'flip_sha256':c['sha256'],'total_frames':len(seq),'state_count':len(names),'map_count':27,'max_working_face_hold':longest,'blinks':blinks,'all_blinks_2_frames':True,'all_blinks_between_c04':True,'look_child_sequences_verified':t['look_child_sequences'],'opening_cues':[e['open_pod_frame'] for e in t['actual_bean_result_frames']],'first_fall_frames':[e['first_bean_falling'] for e in t['actual_bean_result_frames']],'last_fall_frames':[e['last_bean_falling'] for e in t['actual_bean_result_frames']],'f01_absent':True,'airborne_bean_hold_max_frames':3}
 cp(p,'alternatives/'+p.name)
 if c['variant']=='B_36f_review_only':cp(p,'probe/assets/flips/g01_beans.flip.json')
for n in ['S01_BATCH4_MANIFEST.json','S01_BATCH4_README.md']:cp(G/n,'author/'+n)
for p in (G/'reports').glob('S01_*'):cp(p,'reports/'+p.name)
cp(G/'evidence/s01_c04b_pod_crop_native.png','evidence/s01_c04b_pod_crop_native.png')
(S/'coordinator_review/independent_timeline_check.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
cp(Path(__file__),'coordinator_review/validate_and_stage.py')
(S/'README.md').write_text('''# S01 奶奶：B 方案可接试渲，9 态 / 27 三图 / 288 帧

Opus 在 dcf4e1c5c0e27db925b9025a0c8987fe72584fd7 的 16:25 留言明确选择 B；Astra 同意。每秒脸变是 Opus 的经验门槛，并非用户原话。此次选择保留两次完整看小满，避免 12 秒内 9 次全闭眨眼的机械感。静态候选与时表已核；实际接景、原速自然度尚未核。

## 由 Opus 接入，当前提交只在 collab

1. 将本目录 `probe/assets/chars/` 内 27 个 PNG 按同名复制到仓库 `assets/chars/`。
2. 将 `probe/assets/flips/g01_beans.flip.json` 复制到仓库同名路径。它逐字节等于作者 B 表，SHA256 `97210463f470919a194646638bb5aee962f25a3939d35474947540cb3a50dfc5`，目标画幅 779×1355、候选三图 951×1654，锚点已包含。只用于 S01，不覆盖 S04 独立表。
3. B 开荚 cue 为 F19/53/88/126/143/180/215/246。第 4 个由 F118 移到 F126（+8 帧 = 1/3 秒）；其余 7 个不变。`reports/S01_B_36f_review_only_cues.csv` 区分开荚、第一颗/末颗悬空结果与空壳放回，不能把悬空首帧冒充撞盆时刻。
4. 按 B 修改相应音点后，必须实际重建母带、记录新文件及 PCM 哈希。旧 95304b16 的已核切片与旧 S03/S04 音轨结论只适用于旧版本；动态响度归一化可能改变后续。请交新 S01/S04 编码片及对应 PCM 切片，供增量核验。

## 实看与独立核验

- 5 次约定生成全部结束且各执行一次。c05c、f02/f03/f04 保留；f01 虽固定点残差 1.98px，却有上镜圈擦弱，已隔离，未生成三图、未进入表。
- 9 个状态、27 映射、288 帧均由独立脚本从实际表复算。6 手态统一算工作脸。B 最长 36 帧，5 次全闭各 2 帧，均在 c04 两豆持稳段；两次 f03→f04→f03→c04 为 F56/59/68/71 和 F183/186/195/198。半闭缺口如实保留。
- c05c 固定点残差 2.94px 接近 3px 门槛；浅色两腔与 c06b 空壳参考相符，但最终尺寸能否读成空腔仍须实片看。c05c→c06b 落手较大、f03/f04 视线和回程、只有全闭的眨眼观感都是待查项。
- 原件含 9 候选与隔离 f01；请求和工具输出为实际记录，参考裁图在 `plan_and_references/` 与 `evidence/`，原始文件在 `originals/`。作者清单保留执行机原路径作溯源，交接路径以本 README 与 delivery_manifest 为准。

## 文件与版本边界

`author/` 保存作者原始 A/B 报告及固定清单；其中 B 的“待确认”是写作时状态，已被本页及 Opus 16:25 选 B 留言更新。`alternatives/` 的 A 仅留作比较，不是第二个生产入口。`plan_and_references/` 是执行前草案，不作为当前通过结论。`coordinator_review/` 保存独立固定点重算与时表检查。

S01 旧实际片 5edaa205 的底边黑带和小满缩小采样断线见 afec58bd 的 `collab/reviews/20261017_1618_s01_xiaoman_actual/`。Opus 已称修正且会连同 S04 重渲；代码声明尚不替代新实片核验。已有 S03 递收/上返风险及旧音频结论继续按其固定版本保留，不重复生成或复审未变版本。
''')
known={l.split()[2] for l in (W/'remote_tree_latest.txt').read_text().splitlines()};es=[]
for p in sorted(S.rglob('*')):
 if p.is_file() and p.name!='delivery_manifest.json':
  b=p.read_bytes(); git=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest();es.append({'local':str(p),'remote':base+'/'+str(p.relative_to(S)),'bytes':len(b),'sha256':sha(p),'git_sha':git,'existing':git in known})
mp=S/'delivery_manifest.json';mp.write_text(json.dumps({'status':'B_selected_for_scene_trial_not_scene_approved','selected_by_opus_commit':'dcf4e1c5c0e27db925b9025a0c8987fe72584fd7','entries':[{k:v for k,v in e.items() if k not in ['local','existing']} for e in es]},ensure_ascii=False,indent=2)+'\n');b=mp.read_bytes();es.append({'local':str(mp),'remote':base+'/delivery_manifest.json','bytes':len(b),'sha256':sha(mp),'git_sha':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest(),'existing':False})
(D/'upload_entries.json').write_text(json.dumps(es,ensure_ascii=False,indent=2)+'\n'); print(json.dumps({'files':len(es),'checks':checks},ensure_ascii=False,indent=2))
