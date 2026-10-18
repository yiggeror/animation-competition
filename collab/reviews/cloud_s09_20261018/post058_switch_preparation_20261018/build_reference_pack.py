#!/usr/bin/env python3
"""Reference-only copies and same-scale source-image comparison panels; no new pose/art/mask."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,csv,io,math,shutil
import numpy as np
R=Path(__file__).resolve().parent; B=R.parent
for d in ['sources','qa']:(R/d).mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
entries=[
('F000_OFF_identity','switch_segment/locked/F000_raw_alpha_clean.png','锁定身份、完整斜持筒及OFF基态；非后段操作姿态自动复用'),
('F008_OFF_prepress','switch_segment/candidates/d02_raw_locked.png','拇指预压仍OFF，第一开关方向参考'),
('F014_ON_dark','switch_segment/candidates/d03_raw_locked.png','第一次到ON而暗，ON拇指形状/方向参考；机械端点部分遮挡'),
('F018_ON_dark_frown','switch_segment/candidates/d04_raw_locked.png','第一次ON后等待/眉心轻拧，仍暗'),
('F026_OFF_reset','pre_tap_segment/candidates/d05_raw_locked.png','实际锁026，OFF复位；左手仍包托斜筒'),
('F031_whole_pose','pre_tap_segment/clothing_semantic_review/continuous_contour_delivery/candidate/F031_raw_clothing_and_contours_for_final_lock.png','实际锁031整态，竖筒与掌分离'),
('F031_pure_grip_torch','first_tap_segment/F044_rebound_gate/sources/F031_rigid_whole_torch_and_grip.png','唯一纯031整握手筒原层；技术腕截线不是终稿接缝'),
('F056_exact042_contact','first_tap_segment/F042_contact_gate/astra_two_corridors_zero_call/candidate/F042_two_corridors_clean_PENDING_ASTRA.png','锁042整图精确复用056；第二次尾盖触掌'),
('F058_exact044_rebound','first_tap_segment/F044_rebound_gate/candidate/F044_complete_local_native_arm_PENDING_ASTRA.png','最新Astra准058整图复用锁044；48native离掌，058–062 hold5')]
manifest=[];imgs={}
for key,rel,role in entries:
 p=B/rel;q=R/'sources'/f'{key}.png';shutil.copyfile(p,q);assert p.read_bytes()==q.read_bytes()
 imgs[key]=Image.open(q).convert('RGBA')
 manifest.append({'key':key,'source_repo_relative':'collab/reviews/cloud_s09_20261018/'+rel,'portable_path':str(q.relative_to(R)),'sha256':sha(q),'size':list(imgs[key].size),'role':role,'byte_identical_snapshot':True})
# Exact provenance document snapshots; retain historical labels instead of silently editing originals.
docs=['switch_segment/locked/F000_lock.json','switch_segment/qa/d03_patch_report.json','pre_tap_segment/qa/d05_patch_report.json','pre_tap_segment/seam_repair/qa/measurements_and_lock_checks.json','exposure.csv']
for rel in docs:
 p=B/rel;q=R/'sources'/('doc_'+rel.replace('/','__'));shutil.copyfile(p,q)
 manifest.append({'source_repo_relative':'collab/reviews/cloud_s09_20261018/'+rel,'portable_path':str(q.relative_to(R)),'sha256':sha(q),'role':'历史已记录测量/像素来源或时表；最新Astra058裁定覆盖旧35名义','byte_identical_snapshot':p.read_bytes()==q.read_bytes()})
(R/'sources/manifest.json').write_text(json.dumps({'scope':'actual locked source/reference snapshots only; no new pose, input mask or generation','sources':manifest},ensure_ascii=False,indent=2)+'\n')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',16)
fontsmall=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',14)
def plate(im,bg):
 z=Image.new('RGBA',im.size,(*bg,255));z.alpha_composite(im);return z.convert('RGB')
for tone,bg in [('gray',(213,223,231)),('dark',(35,43,52))]:
 sheet=Image.new('RGB',(1674,1128),(236,241,246));d=ImageDraw.Draw(sheet)
 for j,(key,rel,role) in enumerate(entries):
  # Same display scale 1/3 for every whole native image; no reposing, alignment or per-part edit.
  q=plate(imgs[key],bg).resize((557,314),Image.Resampling.LANCZOS);x=(j%3)*558;y=(j//3)*376
  d.text((x+5,y+5),key,font=font,fill=(20,30,40));sheet.paste(q,(x,y+35))
  d.text((x+5,y+351),'真实源图 / 同比例缩览 / 非新动作',font=fontsmall,fill=(20,30,40))
 sheet.save(R/f'qa/actual_locked_sources_overview_{tone}.png')
 # Three thumb/slider references at identical native crop and 2x nearest display zoom.
 box=(915,535,1085,625);ss=Image.new('RGB',(1032,232),(236,241,246));dd=ImageDraw.Draw(ss)
 for j,key in enumerate(['F008_OFF_prepress','F014_ON_dark','F026_OFF_reset']):
  dd.text((j*344+4,3),key+' / 2x',font=font,fill=(20,30,40));ss.paste(plate(imgs[key],bg).crop(box).resize((340,180),Image.Resampling.NEAREST),(j*344,32))
 dd.text((4,214),'相同原生坐标裁片；不是机械端点无遮挡证明',font=fontsmall,fill=(20,30,40));ss.save(R/f'qa/actual_first_switch_OFF_ON_OFF_{tone}.png')
 # Torch comparison: no rotation or scale normalization. Only real source crops, same native px scale.
 specs=[('F026_OFF_reset',(800,470,1280,750)),('F031_whole_pose',(950,240,1250,745)),('F058_exact044_rebound',(950,240,1250,745))]
 ps=Image.new('RGB',(1500,565),(236,241,246));pd=ImageDraw.Draw(ps)
 for j,(key,box) in enumerate(specs):
  pd.text((j*500+5,4),key+' / 1 native px',font=font,fill=(20,30,40));ps.paste(plate(imgs[key],bg).crop(box),(j*500+5,38))
 pd.text((5,545),'未旋转/未拉长；026尾盖受握手遮挡，完整盖径不可观测',font=font,fill=(20,30,40));ps.save(R/f'qa/actual_prop_operating_vs_rebound_{tone}.png')
# Small independent exact endpoint-region check: F026 inherits visible F000 ends.
a=np.array(imgs['F000_OFF_identity']);b=np.array(imgs['F026_OFF_reset']);endchecks={}
for name,box in [('lamp_end',(1155,485,1270,636)),('visible_tail_end',(830,611,877,662))]:
 x0,y0,x1,y1=box;endchecks[name]={'native_box_halfopen':box,'F000_vs_F026_RGBA_changed_pixels':int(np.any(a[y0:y1,x0:x1]!=b[y0:y1,x0:x1],axis=2).sum())}
s=.6297229219143576
oldaxis=math.dist((853,638),(1227,563));newaxis=math.dist((1135,278),(1134,654))
measurement={'status':'MANUAL_VISIBLE_ENDPOINTS_NOT_ANATOMY_OR_COMPLETE_CAP_DIAMETER','registration_scale':s,'026':{'tail_axis_manual_native':[853,638],'lamp_axis_manual_native':[1227,563],'axis_native_approx':oldaxis,'axis_registered_approx':oldaxis*s,'axis_native_uncertainty_approx':8,'source':'F000_lock.json endpoints inverted via unchanged registration; endpoint regions actually checked identical in026','full_cap_diameter':'unobservable; visible roughly44 is occluded fragment, not full diameter'},'031_and058':{'031_lamp_axis_manual_native':[1135,278],'031_tail_axis_manual_native':[1134,654],'058_whole_reuse_shift_vs031_native':[0,11],'axis_native_approx':newaxis,'axis_registered_approx':newaxis*s,'axis_native_uncertainty_approx':8,'lamp_full_visible_diameter_native_approx':128,'lamp_diameter_manual_uncertainty':5,'complete_cap_visible_diameter_native_approx':83,'cap_manual_uncertainty':4,'source':'actual images viewed; manual axis/diameter estimates also recorded in historical seam report; old contact target coordinates are not inherited'},'axis_difference_percent':(newaxis/oldaxis-1)*100,'judgment':'约1.43%轴长差在两次人工端点误差内；不能据此认定设计漂移或擅缩当前筒。完整尾盖只当前姿态可见，不做026完整径比。','actual_endpoint_RGBA_checks':endchecks,'058_latest_override':{'whole_image_reuse_of_locked044':True,'source_sha256':sha(R/'sources/F058_exact044_rebound.png'),'gap_native':48,'gap_registered':48*s,'old_nominal35_superseded_by_explicit_Astra':True},'OFF_ON_visibility_limit':'d03/d05 thumb遮挡实际滑键端点；只能确认拇指前推/退回的可见形状，不能声称机械端点完整已验证。'}
(R/'qa/actual_prop_scale_and_endpoint_checks.json').write_text(json.dumps(measurement,ensure_ascii=False,indent=2)+'\n')
rows=[(58,62,5,'锁044整图复用；真实30.2267注册px回弹','tail_contact','OFF',False,'最新Astra显式覆盖旧35'),(63,68,6,'回操作角；左手靠近前段但不包托','switch','OFF',False,'尚需实际角度/转轴/完整臂设计门'),(69,72,4,'左掌托稳；右拇指第二次前推未到位','switch','TRANSIT',False,'承托点与拇指途程需真实定位'),(73,76,4,'到ON；灯从073亮；眼先看灯口','lamp_rim','ON',True,'灯口中心/轴向/遮挡需真实锚定'),(77,84,8,'眉眼松开；整个头略向右确认','lamp_rim','ON',True,'不是只挪五官'),(85,95,11,'稳定持握向右；留亮灯结果接S10','screen_right','ON',True,'束光交接方向需与S10核对')]
with(R/'post058_frame_table.csv').open('w')as f:
 w=csv.writer(f,lineterminator='\n');w.writerow(['start0','end_inclusive','hold','action','gaze','switch','light_on','gate_or_authority']);w.writerows(rows)
assert sum(r[2]for r in rows)==38 and all(rows[i][1]+1==rows[i+1][0]for i in range(len(rows)-1))
notes={'status':'REFERENCE_SOURCE_AND_CAUSALITY_PACKET_ONLY_NOT_POSE_OR_CALL_READY','latest_authority':'Parent relays explicit Astra:058=whole locked044 fe70,48native/30.2267registered accepted,058–062hold5;056contact and073light unchanged. Supersedes prior readiness35 question.','existing_art_usage':{'F000':'identity, materials, initial operating grip context','F008':'OFF prepress thumb shape','F014':'first ON dark visible thumb push reference only','F018':'frown reference; retain dark','F026':'real OFF reset and two-hand operating-context reference; not automatically063 entire pose','F031_pure_unit':'real rigid current hand/torch source, technical wrist cut is not a final arm connection','F056':'exact locked042 second contact','F058':'exact locked044 new approved reuse; torso/head/palm retain source unless later approved action changes them'},'causal_and_layer_checklist':[
'056独立第二接触→058确实离掌；仅尾盖触掌，不以灯头或指节抢触。058不再追35名义。',
'063首先从触掌姿态回操作角，左掌只是靠近灯头之后的前筒段，仍留真实间隙；手不穿筒、不在063提前包托。',
'069左掌/指真正承接前段后才供拇指第二推的反力；掌根—腕—远前臂完整连续，近右裸手仍完整环握，前臂不交叉。',
'原手筒既有握指/筒体交叠作为一件真实刚性源保持；后续拇指滑键局部改变须真实画稿，不能移动筒纹当作机械开关行程。',
'躯干在后、远袖远臂承托层次与前景近臂按实际遮挡分配；隐藏远袖/远臂alpha不能硬保压住新前景。左手包托时掌在筒下，指与筒前缘的交叠须真实手审。',
'近袖根→整上臂→肘→腕→握手全链须新姿态连续接回；技术腕截边不能当终稿，不能靠窄条补桥、拉伸手臂或只转手不接肘。',
'OFF持续至068；069–072为TRANSIT且灯仍暗；073首次ON亮，第一段ON不亮参考不能把灯提前亮。',
'073眼先看灯口，077才整头轻转并松眉；085稳定向右持握。亮灯点、光轴和S10交接在画面实际锚定前不可用代码旧点替代。'
],'Astra_actual_anchor_choices_needed_before_input_gate':[
{'frame':63,'needed':'063完整操作筒轴方向/旋转量、真实转轴归属（可近腕/握持中心但未选定）、灯头/尾盖终点；近臂全链与左右肘间隔；是否参考026斜持角仅作提案，不视为已准。','why':'竖持058到斜持026是新三维姿态与远手行程，旧画和旧175坐标不能直接作为新目标。'},
{'frame':69,'needed':'左掌实际承托的前筒接触带、掌法向、腕/肘路径及指在筒前后的归属；063尚未触与069已托的可见区分。','why':'旧s/n、820750、旧腕代理均非真实240筒实际位置。'},
{'frame':73,'needed':'真实滑键OFF/TRANSIT/ON可见位置或遮挡判据、拇指合法行程；新操作姿态灯口中心/朝向、亮面与光束起点。','why':'第一次开关源的机械端点被拇指遮挡，且当前筒姿态不同；不得只套旧代码光点。'},
{'frames':[77,85],'needed':'077整个头的确认幅度/朝向和085最终持灯方向，与S10光束首现时刻/位置确认。','why':'本包只有真实旧源，不生成新头姿/光效或声称后段已冻结。'}
],'explicitly_not_inherited':['175px旧筒长','44px所谓完整尾径','旧820750掌面','旧200px双骨/旧关节proxy','旧2.29px安全余量','旧35px058名义间隙'],'reviewer_image_generation_calls':0,'new_pose_images':0,'input_masks_created':0,'new_state_approval':False}
(R/'causality_layers_and_open_anchors.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2)+'\n')
(R/'README.md').write_text('''# S09 058之后真实源参考小包

仅备来源与动作因果，未生成、未画新动作、未做操作白域，不是063/069/073输入门通过。058已按最新Astra裁定整图复用锁044：48原生px＝30.2267003注册px，058–062 hold5；旧35名义已撤，无需再为058重做姿态。

- `sources/manifest.json`：9张真实锁源/原图层的完整字节快照、5份来源文档，记录原路径与SHA。`build_reference_pack.py`可从仓库现成来源重建本参考包；所有图是原源图裁片/同一缩览比例，未生成新人物形状。
- `qa/actual_locked_sources_overview_gray.png` / `dark.png`：真实身份、第一开关、026、031、056、058九格比较。
- `qa/actual_first_switch_OFF_ON_OFF_gray.png` / `dark.png`：相同坐标2倍显示拇指/滑键参考，机械端点仍部分遮挡。
- `qa/actual_prop_operating_vs_rebound_gray.png` / `dark.png`：026/031/058原生1:1裁片。026轴约381.45、当前376.00原生px（分别约240.21、236.78注册px），差约1.43%，不超人工端点不确定性；不能据此擅改设计。026完整尾盖被握手遮挡，44可见碎段不是完整直径。当前完整尾盖约83±4原生px仅作人工观测。
- `post058_frame_table.csv`：058之后38f精确表；063×6 OFF未托、069×4 TRANSIT仍暗、073×4首次ON亮、077×8整头确认、085×11稳定亮。
- `causality_layers_and_open_anchors.json`：完整前后层与两击→归位→托稳→再推→亮灯因果；列063实际角/转轴、069左掌托点、073实际灯口/滑键点与后续头/光交接的待选项。

第一开关/026可用作身份、颜色、拇指方向和斜持上下文，不能自动复用整图成为063。新操作角、掌点和灯口锚定后仍须真实全臂、完整双手、源层遮挡与曝光门。本包不盲批未来六态，不代Astra冻结。
''',encoding='utf8')
files=[{'path':str(p.relative_to(R)),'sha256':sha(p)}for p in sorted(R.rglob('*'))if p.is_file() and p.name!='PACK_SHA256.json']
(R/'PACK_SHA256.json').write_text(json.dumps({'files':files,'new_image_calls':0,'new_pose_or_input_mask':False},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'root':str(R),'manifest_SHA256':sha(R/'sources/manifest.json'),'facts_SHA256':sha(R/'causality_layers_and_open_anchors.json'),'package_manifest_SHA256':sha(R/'PACK_SHA256.json'),'source_images':len(entries),'files':len(files)+1,'all_bytes':sum(p.stat().st_size for p in R.rglob('*')if p.is_file())},ensure_ascii=False,indent=2))
