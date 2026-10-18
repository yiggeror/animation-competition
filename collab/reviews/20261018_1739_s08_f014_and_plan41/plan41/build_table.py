from pathlib import Path
import json,csv,hashlib,shutil
O=Path(__file__).resolve().parent;R=O.parent;P=R/'S08_40_STATE_DIRECTOR_UPDATE_1718';d=json.loads((P/'S08_40_states_approved_nodes.json').read_text());d.pop('breathing_proposal',None)
breath={'status':'COORDINATOR_ADOPTED_WITHIN_OPUS_ALLOWED_ONE_TO_TWO_WHOLE_DRAWINGS_NOT_YET_PAINTED','selected_extra':'F136_B','derive_only_from':'visually approved F128','exposure':'128–135 F128;136–143 F136_B','whole_body_motion':'Chest, both shoulders, neck and head together in a subtle settling phase; same leftward gaze and smile. Both palm-root tabletop support points remain fixed, with naturally redrawn elbow/wrist articulation.','prohibited':['code stretching/warping','shoulder-only movement','moving tabletop palm support points with body','generating136 before128 passes'],'existing_tail':'F114/F122/F128 are compatible natural whole-body phases as they are actually drawn. No blind reuse across different gaze directions.','call_now':False,'visual_status':'not drawn; each actual pose and entire exposure sequence pending review'}
d.update(status='FORMAL41_EXPOSURES40_UNIQUE_PLAN_UNPAINTED_STATES_EXPLICIT',exposure_states=41,planned_unique_composed_character_key_images=40,remaining_planned_unique_key_images=34,delivered_unique_character_RGBA_images=6,delivered_exposure_states=7,whole_drawing_breathing=breath,adoption_source='Coordinator17:23UTC selected preferred singleF136_B within Opus explicit one-to-two whole-drawing permission; no additional director wait.',timing_change=d['timing_change']+' Add approvedF136_B; split128–143 into128–135/136–143; total144unchanged.')
for r in d['rows']:
 if r['frame']==14:r['status']='协调与独审静态门通过；第8原件同raw完成';r['asset']='F014 已锁d1727966…fbe3d51'
 if r['frame']>=114:
  r['independent_layers']=[x for x in r['independent_layers'] if '微呼吸' not in x];r['independent_layers'].append('整体角色绘图微起伏，无代码变形')
  if r['frame']==114:r['contact_and_depth_gate']='远肘参考(900,880)，笑开；胸肩颈头整体坐定，双掌根桌上承点保持。'
  if r['frame']==122:r['contact_and_depth_gate']='保持整体自然坐定，眼开始画左看；两掌根承点不漂，必要肘腕随整身相位真实重画。'
  if r['frame']==128:r['contact_and_depth_gate']='画左眼向与笑意成立；全身微起伏相位稳定，曝128–135后接136整体微落。'
d['rows'].append({'frame':136,'action':'整体轻呼吸微落','asset':'F136_B（计划新图）','exact_reuse_of':None,'status':'已纳正式计划；未画，须等128合格后派生','contact_and_depth_gate':breath['whole_body_motion'],'independent_layers':['独立芯火/暖光代码层','桌面盒层','桌面灭柴层','整体角色绘图微起伏，无代码变形']})
rows=d['rows'];assert len(rows)==41
for i,r in enumerate(rows):r.update(index=i+1,time_seconds=round(r['frame']/24,6),hold_frames=(rows[i+1]['frame'] if i+1<len(rows) else 144)-r['frame']);r['last_frame']=r['frame']+r['hold_frames']-1
assert sum(r['hold_frames'] for r in rows)==144
(O/'S08_41_states_formal.json').write_text(json.dumps(d,ensure_ascii=False,indent=2));(O/'whole_drawing_breathing_ADOPTED_NOT_DRAWN.json').write_text(json.dumps(breath,ensure_ascii=False,indent=2))
lines=['# S08 正式41曝光 / 40唯一关键角色图','','24fps，144f。012精确复005。已通过首7曝光/6唯一角色图（含014）；014第8次原件同raw接边与独立色门通过。其余均未画或仅有结构参考，不能写成全镜完成。','新增136整体微落方案已采用，属Opus明确允许的1–2张完整微起伏绘图范围。136必须从合格128派，当前不调用。','胸、肩、颈、头一起轻落，画左眼向与笑意不变；桌上两掌根承点不漂，由真实肘腕微调绘图完成。禁止代码拉图、只动肩膀或提前抽尾态。','','|序|帧段|曝光|动作 / 接触门|图像状态|','|---|---|---:|---|---|']
for r in rows:lines.append(f"|{r['index']:02d}|{r['frame']:03d}–{r['last_frame']:03d}|{r['hold_frames']}|{r['action']}。{r['contact_and_depth_gate']}|{r['asset']}；{r['status']}|")
lines+=['','压杆升罩已批；23扣高初位→25下压中间→27原终点，78松指后80杆返回高初位、罩回落。','色基准始终用本镜F000；同语义色域±4并实际看自然明暗。全景火光、桌层、声音和144f连续性另门。','此前32/40表保留历史，正式计划以本41表为准。计划唯一图数不等于承诺原生调用数。']
(O/'S08_41_states_formal.md').write_text('\n'.join(lines)+'\n')
with (O/'S08_41_states_formal.tsv').open('w',newline='') as f:
 w=csv.writer(f,delimiter='\t');w.writerow(['index','start','last','hold','action','asset','status','contact_depth']);[w.writerow([r['index'],r['frame'],r['last_frame'],r['hold_frames'],r['action'],r['asset'],r['status'],r['contact_and_depth_gate']]) for r in rows]
shutil.copy2(P/'lever_path_APPROVED_GEOMETRY.png',O/'lever_path_APPROVED_GEOMETRY.png');(O/'READ_FIRST.txt').write_text('正式41曝光/40唯一关键角色图，144f，012复005。已通过首7曝光/6唯一图（含014）；014静态终门已过。新增F136_B整体微落已采用，须合格128后顺链绘制，当前未画待实审。双掌根桌面承点固定，以真实肘腕绘图接回；禁止代码变形。此包替代40表的计划效力，旧包保留历史。\n');files=[p for p in O.iterdir() if p.is_file() and p.name!='SHA256SUMS.txt'];(O/'SHA256SUMS.txt').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in files));print(json.dumps({'exposures':len(rows),'unique':40,'total_frames':sum(r['hold_frames'] for r in rows),'last_rows':[(r['frame'],r['hold_frames']) for r in rows[-4:]],'json_sha256':hashlib.sha256((O/'S08_41_states_formal.json').read_bytes()).hexdigest()}))
