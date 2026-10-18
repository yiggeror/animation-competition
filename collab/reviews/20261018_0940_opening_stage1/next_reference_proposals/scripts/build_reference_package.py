from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import json, hashlib, math, copy
ROOT=Path(__file__).resolve().parents[1]; SHARED=ROOT.parent/'astra_xiaoman_opening_refs_20261018_0906'; GRAND=ROOT.parent/'astra_s03b_painted_pilot_20261018/refs'; W,H=1672,941
F='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
def font(n):return ImageFont.truetype(F,n)
def txt(d,p,s,n=22,c='#233744'):d.text(p,s,font=font(n),fill=c)
def write(n,o): (ROOT/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def rel(p):return str(p.relative_to(ROOT.parent)) if False else '../'+str(p.relative_to(ROOT.parent))
def hashinfo(p):
 b=p.read_bytes(); return {'sha256':hashlib.sha256(b).hexdigest(),'git_blob':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest(),'byte_count':len(b),'canvas':list(Image.open(p).size) if p.suffix.lower() in ['.png','.jpg'] else None}
remote=json.loads((SHARED/'sources/remote_image_manifest.json').read_text()); old=json.loads((SHARED/'S02a_reference_proposal.json').read_text()); meas=json.loads((SHARED/'qa/measurements.json').read_text()); plan=json.loads((SHARED/'sources/opening_plan.json').read_text())
base=old['manual_source_landmarks']['focus']; actual=copy.deepcopy(old['manual_source_landmarks']);
manual_extra={'eye_aperture_L_xyxy':[686,516,777,598],'eye_aperture_R_xyxy':[898,514,989,599],'pupil_L':[747,569],'pupil_R':[930,569],'neck_edge_L':[775,729],'neck_edge_R':[905,729]}
source_manifest=[]
for a in remote:
 if a['dest'].startswith(('identity/','originals/','code_refs/S05a/','code_refs/S03a/')):
  source_manifest.append({'local':rel(SHARED/a['dest']),'repo_path':a['path'],'repo_commit':'280c1e25533b76cc5e44e954b45cc98297a36b46','git_blob':a['sha'],'sha256':a['sha256'],'canvas':a['canvas']})
for k in ['k06','k07']:
 p=next((GRAND/'painted').glob('*'+k+'*'));source_manifest.append({'local':rel(p),'repo_path':'collab/reviews/20261018_0428_s03_keypose_candidates/originals/'+p.name,'repo_commit':'fb0f76b40932f395bf90834d9fa274d4cb6ffd11',**hashinfo(p)})
p=GRAND/'grandma_turnaround_current03_draft.png';source_manifest.append({'local':rel(p),'repo_path':'collab/refs/grandma_turnaround_current03_draft.png','repo_commit':'not independently refreshed; local exact bytes hashed',**hashinfo(p)})
write('sources/source_manifest.json',source_manifest)
common={'scope':'REFERENCE ANALYSIS ONLY. No new painted character or hand/melon asset. No image generation. No repo/docs/assets/implementation writes.','repo':'yiggeror/animation-competition','plan_commit':'280c1e25533b76cc5e44e954b45cc98297a36b46','plan_path':'docs/keyframes/opening_plan.json','fps':24,'native_guide_canvas':[W,H],'landmark_conventions':{'origin':'top left; native source pixels','actual_source_manual': 'Carried from actual-source S02a reference measurements and visually checked here; about +/-3–6 px. Eye_L/R are aperture tracking points, not pupil centers.','extra_manual':'Focus eye apertures, pupils, and neck edges visually estimated here; about +/-4–6 px.','lower_chest':'A/B/H are prior independently computed white-dot centroids, approx +/-1 px; source qa/measurements.json. Nearly collinear, diagnostic only.','bone_lengths':'No measured 3D bone lengths available. Chin–collar and shoulder distances below are screen-space chords; shoulder points are sleeve/outer-contour observations, not shoulder joints.','new_pose_values':'All new pose offsets, yaw and aperture dimensions are proposals, not measured new drawings or approved performances.'},'source_actual_landmarks':actual,'focus_extra_manual_points':manual_extra,'chest_diagnostics':{a['file']:{'points':a['lower_chest_points'],'H_residual_px':a['AB_similarity_to_k01']['H_residual_native_pixels']} for a in meas['assets']},'constraints':['Low frontal head/shoulders close-up; Xiaoman hands, phone and elbow contact remain out of frame. No chin-in-hand.','Keep original 1672x941 guide coordinates; K19 scene crop is an integration decision.','Never register using moving shoulders. Do not apply the old 4.76%/3.28% scale fits; H residual remains about 5 px.','New art: neutral local color, 2–3 form-value layers. Scene lighting applied once. Old pale-blue chin/collar shading is recorded, never silently altered.','All references are sources, not approval of old alpha artifacts, face drift or weak tense expression.']}
starts=[0,10,14,24,28,44,46,50,52]; holds=[10,4,10,4,16,2,4,2,8]
labels=['游戏专注','察觉已黑屏','愣住','疑惑起势','小圆口“不是吧”','第一次按键·肩顶','肩落下','第二次按键·肩顶','肩落·泄气']
head_y=[0,0,0,0,0,2,0,1,4]; shoulder_y=[0,0,0,0,0,-14,0,-10,6]; collar_y=[0,0,0,0,0,-4,0,-3,2]
brows=[0,9,18,12,12,12,10,12,5]; eye_extra=[0,4,9,5,4,4,3,4,-1]; mouths=['flat','flat','flat','part','o','o','small_o','o','small_o']
notes=[['嘴平；视线仍向画外下方','头、胸与旧focus对照'],['上睑打开；眉开始抬','不能笑口；不重演断屏'],['眼圆、眉高；闭口愣住','惊疑不等于快乐'],['内眉抬并微收；嘴微开','口角不向上'],['竖向小圆口；内眉担忧','无露齿笑或喜悦弧'],['肩轮廓上顶约14px（提案）','下颏+2、领结−4：颈段略压'],['肩与领口回基线','要读出落肩，不能删态'],['肩再顶约10px（提案）','下颏+1、领结−3：不拉颈'],['肩+6、头+4（提案）','口缩小，泄气不改成笑']]
states=[]
for i,f in enumerate(starts):
 pts=copy.deepcopy(base)
 for k in ['eye_L','eye_R','chin','nose','mouth_L','mouth_R','head_top','cowlick_top']:pts[k][1]+=head_y[i]
 for k in ['shoulder_L','shoulder_R']:pts[k][1]+=shoulder_y[i]
 pts['collar_junction'][1]+=collar_y[i]
 states.append({'id':f'S05a_d{i+1:02}','start_frame':f,'end_frame_exclusive':f+holds[i],'hold_frames':holds[i],'literal_plan':plan['S05a']['frames'][i][1],'read':labels[i],'status':'new state proposed, not generated','parent_after_approval':'old focus exact source' if i==0 else f'S05a_d{i:02} last accepted image','boundary_old_anchor':'../astra_xiaoman_opening_refs_20261018_0906/originals/S02a_k01_focus.png (no resizing)','guide_points':pts,'guide_offsets_px':{'head_y':head_y[i],'outer_shoulder_y':shoulder_y[i],'collar_junction_y':collar_y[i]},'screen_chin_to_collar_chord_px':round(math.dist(pts['chin'],pts['collar_junction']),2),'face':{'brow_lift_px':brows[i],'upper_eye_opening_extra_px':eye_extra[i],'mouth':mouths[i],'gaze':'fixed offscreen phone, below frame','inner_brow_worry':i>=3},'notes':notes[i]})
s05={**common,'shot':'S05a','duration_frames':60,'counts':{'exposure_states':9,'new_plan_states':9,'generated':0},'states':states,'segments':[{'id':'A','states':['d01','d02','d03'],'chain':'focus → d01 → d02 → d03','old_boundary_anchor':'focus','reason':'Only eye/brow response; do not import tense head drop.'},{'id':'B','states':['d04','d05'],'chain':'accepted d03 → d04 → d05','old_boundary_anchor':'focus face/head/collar/chest coordinates; tense/relief only identity checks','reason':'Develop worry mouth without changing character proportions.'},{'id':'C','states':['d06','d07'],'chain':'accepted d05 → d06 → d07','old_boundary_anchor':'focus collar/chest/shoulder baseline compared, no whole-image fitting','reason':'First up/down shoulder impulse.'},{'id':'D','states':['d08','d09'],'chain':'accepted d07 → d08 → d09','old_boundary_anchor':'focus baseline; do not copy relief smile for deflation','reason':'Second distinct impulse and deflated settle.'}],'projection_assumptions':{'camera':'fixed low frontal camera; head size constant; no assumed z translation/zoom','body':'chest print stays at source coordinates; shoulder elevation is local silhouette/collar deformation, not whole torso translation','head_neck':'Small jab chin/collar offsets are 2D guide proposals; do not call them constant measured bones. No elbow/hand is reconstructed.','performance_gate':'Actual line/skin/neck contour must be reviewed before painting; numeric guides do not establish anatomical correctness.'},'S05_causal_check':{'code_commit':'280c1e25533b76cc5e44e954b45cc98297a36b46','anim_blob':'b2b08e56783637ff9a418d07ac3cd9a912e37599','code_blob':'c9afe0bb1168b77481cf242e48efd01ad4d8cd55','duration':3,'offset':0.63,'T_OFF':3.05,'sampled_24fps':{'frame58':{'t':58/24,'screenOn':1},'frame59':{'t':59/24,'screenOn':0.35},'frames60_71':{'screenOn':0,'press':0}},'finding':'S05 dims at local f59 and is fully black f60–71. S05a existing scene light is static dark, so repeated light cut is neither required nor supported.','proposed_read_only_interpretation':'Keep all nine frame starts unchanged. Read f0 as the lingering game-focused face after the cut, f10 as recognition of the already-black display. Ask Opus to approve this causal interpretation; do not create a second blackout, move frames or edit code.','limitation':'Read-only source/sampling check, not a new claim to have played the full cut.'}}
write('S05a_reference_proposal.json',s05)
# Analytical line diagrams only; these paths are not hair, skin, or production character drawings.
BG='#f7f7f3'; INK='#213e50'; BLUE='#1680a0'; GREY='#b8bec0'; ORANGE='#c06a24'
def line(d,ps,col=BLUE,w=3):d.line([(round(x),round(y)) for x,y in ps],fill=col,width=w,joint='curve')
def dashed(d,a,b,col=GREY,w=2,step=10):
 length=math.dist(a,b)
 for k in range(0,int(length),step*2):
  t0=k/length;t1=min(1,(k+step)/length);line(d,[(a[0]+(b[0]-a[0])*t0,a[1]+(b[1]-a[1])*t0),(a[0]+(b[0]-a[0])*t1,a[1]+(b[1]-a[1])*t1)],col,w)
def draw_guide(s,shot='S05a'):
 im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im);p=s['guide_points'];dy=p['chin'][1]-base['chin'][1]
 # baseline stays visible to distinguish body motion from image movement
 for a,b in [('shoulder_L','collar_junction'),('collar_junction','shoulder_R'),('chin','collar_junction')]:dashed(d,base[a],base[b])
 yaw=s.get('yaw_proposal_deg',0); turn=abs(yaw)/9
 # head cage and feature axes, diagram geometry derived from source bounds
 d.ellipse((548,148+dy,1127,730+dy),outline=GREY,width=3)
 jaw=[(647+3*turn,498+dy),(660+3*turn,621+dy),(700-2*turn,682+dy),(p['chin'][0],p['chin'][1]),(969-2*turn,679+dy),(1020,620+dy),(1035,498+dy)];line(d,jaw,INK,4)
 line(d,[p['head_top'],p['nose'],p['chin']],BLUE,2)
 line(d,[p['shoulder_L'],(775,745+dy),p['collar_junction'],(905,745+dy),p['shoulder_R']],BLUE,4)
 line(d,[(775,713+dy),(775,738+dy)],INK,4);line(d,[(905,714+dy),(908,739+dy)],INK,4)
 line(d,[p['chin'],p['collar_junction'],(842,880)],BLUE,2)
 for name in ['eye_L','eye_R','nose','chin','collar_junction','shoulder_L','shoulder_R']:
  x,y=p[name];d.ellipse((x-5,y-5,x+5,y+5),fill=BLUE)
 for name in ['A','B','H']:
  x,y=meas['assets'][0]['lower_chest_points'][name]['xy'];d.ellipse((x-8,y-8,x+8,y+8),outline=ORANGE,width=4);txt(d,(x+12,y-15),name,24,ORANGE)
 e=s['face'].get('upper_eye_opening_extra_px',0)
 for name in ['L','R']:
  x,y=p['eye_'+name];wide=46*(0.92 if name=='L' and turn else 1.03 if name=='R' and turn else 1)
  d.ellipse((x-wide,y-38-e,x+wide,y+39),outline=INK,width=4)
  # Screen-fixed down gaze; only a diagram pupil, not expressive new art
  px=x+(7 if name=='L' else -10)+(4*turn);py=y+12;d.ellipse((px-13,py-13,px+13,py+13),fill=INK)
  lift=s['face'].get('brow_lift_px',0)
  if s['face'].get('inner_brow_worry',False):
   pts=[(x-48,y-86-lift+(0 if name=='L' else -12)),(x,y-98-lift),(x+48,y-86-lift+(-12 if name=='L' else 0))]
  else:pts=[(x-48,y-86-lift),(x,y-100-lift),(x+48,y-86-lift)]
  line(d,pts,INK,5)
 x,y=p['nose'];d.ellipse((x-4,y-2,x+4,y+2),fill=INK)
 mx=(p['mouth_L'][0]+p['mouth_R'][0])/2;my=(p['mouth_L'][1]+p['mouth_R'][1])/2;mouth=s['face']['mouth']
 if mouth=='flat':line(d,[(mx-25,my),(mx+25,my)],INK,4)
 elif mouth=='part':d.ellipse((mx-13,my-5,mx+13,my+6),outline=INK,width=4)
 elif mouth in ['o','small_o']:
  a,b=(11,17) if mouth=='o' else (8,11);d.ellipse((mx-a,my-b,mx+a,my+b),outline=INK,width=4)
 elif mouth=='pout':line(d,[(mx-18,my+3),(mx,my-2),(mx+18,my+3)],INK,4)
 else:line(d,[(mx-21,my+6),(mx+18,my-2)],INK,4)
 return im

def overview05():
 im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im);txt(d,(26,12),'S05a · 9态最小骨架 / 脸态提案',31);txt(d,(26,57),'24fps / 60f　蓝=2D提案　灰=原focus基线　橙=A/B/H诊断点　手与手机始终画外',21)
 for i,s in enumerate(states):
  c=i%3;r=i//3;x=22+c*551;y=101+r*263
  d.rounded_rectangle((x,y,x+535,y+248),10,outline='#c9d1d2',width=2)
  txt(d,(x+12,y+5),f"{s['id'][-3:]}  f{s['start_frame']:02}–{s['end_frame_exclusive']-1:02} · {s['hold_frames']}f  {s['read']}",21)
  g=draw_guide(s);crop=(490,110,1170,941);mini=g.crop(crop).resize((165,202),Image.Resampling.LANCZOS);im.paste(mini,(x+18,y+41))
  txt(d,(x+195,y+57),s['notes'][0],18);txt(d,(x+195,y+91),s['notes'][1],18)
  txt(d,(x+195,y+137),f"颏→领交点投影 {s['screen_chin_to_collar_chord_px']:.0f}px",18,BLUE)
  txt(d,(x+195,y+172),'沿上一合格图派生',18)
 txt(d,(26,900),'每格仅放大原坐标裁区(490,110)–(1170,941)；非新人物图。颏领距离是投影，不是实测骨长。',20)
 im.save(ROOT/'qa/S05a_9state_minimal_overview.png')
overview05()
readme='''# 下一组近景参考提案（未开画）

先看 `qa/S05a_9state_minimal_overview.png` 与 `S05a_reference_proposal.json`。所有文件只在本独立目录；生图调用 0，未改原图、仓库或实现。第一组 S03 / S02a 冻结不等待本包。

## S05a 核心
- 60帧 / 9态：0,10,14,24,28,44,46,50,52；原曝光完整保留。
- f10/14/24 的代码笑嘴不采用。惊疑→内眉上皱→竖小圆口；两次肩顶/落不合并。手、手机始终画外。
- 分 A(01–03)、B(04–05)、C(06–07)、D(08–09)。段内逐张用上一合格图；段界重新并看真实 focus 原件，保住头/颈/胸比例，不让身份表或代码小人重起一套脸。
- 旧 tense 只作身份和收颏比较，不把它46px的头降直接抄给S05a；旧 relief 的笑嘴不用于泄气。
- 肩顶14/10px只是小幅2D提案。下胸A/B/H保持诊断；肩轮廓可动，颏领投影略压，不把全身移位或长颈当按键。
- 已按固定280c1e代码核：S05 f59变暗，f60–71全黑且停指；S05a场景光本来就静态暗。因此建议f10读作“意识到已黑屏”，不再熄一次光。九态时间不改，解释待Opus确认。

## 共同边界
原始坐标1672×941；总览的小人是无颜色线性分析图，非生产资产。脸/颈人工点约±3–6px；A/B/H沿用已核连通域中心，旧H约5px残差未通过，不强缩放。没有可测的3D骨长，颏到领点也不是颈骨长。JSON把旧观测与新提案分开。

新图中性基色、2–3层形体，场景光一次。旧三图淡蓝下颏/领口原样保留并记明；不暗改、不拿双重打光掩盖色差。

来源只列相对本机路径、固定仓库路径/commit/Git blob/SHA256于 `sources/source_manifest.json`，不复制大图。已实际view三原件、小满两身份表、S05a/S03a代码实像总览、奶奶k06/k07与三视图，并放大实看手瓜接触。
'''
(ROOT/'README.md').write_text(readme)
print('S05a core ready',ROOT)
# S03a: six exposure entries retained; the face at f8 intentionally does not react to the melon.
starts3=[0,8,17,19,26,29];holds3=[8,9,2,7,3,7];yaw3=[0,0,-2,-9,-5,0]
labels3=['专注手机','瓜到前景·眼不离屏','开始向画面左偏','左偏到位·拒绝','开始回正','回正继续玩']
notes3=[['嘴平；头肩仍用focus母源','自己的手与手机出画'],['脸态保持，瓜先到前面','六条曝光保留，不擅自并项'],['只向画面左开始偏','鼻/眼/脸廓不可等量平移'],['左侧远眼略窄、右耳略显','眼球补偿，仍盯画外手机'],['沿同一路径回正','不越过中线，不做左右循环'],['头回原位，嘴微撅','不接瓜，不跟着瓜转眼']]
states3=[]
for i,f in enumerate(starts3):
 t=abs(yaw3[i])/9;p=copy.deepcopy(base)
 for name,dx in [('eye_L',-5),('eye_R',-7),('nose',-18),('chin',-8),('mouth_L',-14),('mouth_R',-14),('head_top',-2),('cowlick_top',-2)]:p[name][0]+=round(dx*t,1)
 states3.append({'id':f'S03a_d{i+1:02}','start_frame':f,'end_frame_exclusive':f+holds3[i],'hold_frames':holds3[i],'literal_plan':plan['S03a']['frames'][i][1],'read':labels3[i],'status':'reference proposal only; not generated','parent_after_approval':'old focus exact source' if i==0 else f'S03a_d{i:02} last accepted image','boundary_old_anchor':'../astra_xiaoman_opening_refs_20261018_0906/originals/S02a_k01_focus.png (same source coordinates; slight looser crop deferred to scene integration)','guide_points':p,'yaw_proposal_deg':yaw3[i],'yaw_status':'Conceptual left-turn amplitude; -9 degrees approximates code -0.16 rad intent, not a measured angle in painted source.','face':{'brow_lift_px':0,'upper_eye_opening_extra_px':0,'mouth':'flat' if i<3 else 'pout' if i==5 else 'side' if i==3 else 'flat','inner_brow_worry':False,'gaze':'screen-fixed phone below frame; pupils counter-rotate relative to sockets as face turns left'},'face_perspective_proposal':{'far_eye':'screen-left; max aperture width 0.92× at d04','near_eye':'screen-right; max aperture width 1.03× at d04','max_yaw_nose_minus_mean_eye_delta_px':-12,'near_far_visibility':'At left turn: screen-left cheek/ear foreshorten, screen-right cheek/ear become more visible; bangs and neck-side overlap follow the same turn. No head translation is substituted.','limitation':'This line chart only conveys differential landmark motion. Ear/hair/skin occlusion still requires a real view-angle reference gate.'},'foreground':{'state':'outside frame / beginning approach' if i==0 else 'in position, front of chest near chin; never touching face','asset_id':'grandma_right_hand_intact_melon','new_asset_generated':False,'hand_and_melon_must_remain_rigid_group':True},'notes':notes3[i]})
k07=next(a for a in source_manifest if 'k07_F079' in a['local']);k06=next(a for a in source_manifest if 'k06_F058' in a['local'])
contact={'selected_exact_mother_source':k07,'comparison_source':k06,'selection_reason':'k07 is the held S03 exit immediately preceding S03a. Both show the same intact melon, palm-up cradle and four curled fingers. Prefer the latest exact held source rather than a bitten S03b derivative.','chirality_evidence':'Grandma turnaround shows jade bracelet on anatomical left wrist; S03 k07 screen-right resting hand carries it. The offered screen-left hand is therefore anatomical right, matching requested asset. Do not add bracelet to this right hand or mirror it.','observed_k07_points_px':{'melon_tip':[240,638],'rind_bottom_visible':[300,747],'thumb_far_side_visible':[204,696],'index_to_little_visible_tips':[[207,732],[236,737],[258,744],[286,751]],'palm_support_patch':[304,753],'wrist_center':[346,736],'elbow_center':[471,713]},'measurement_method':'Manual point picks on actual k07 at native 1670×941, checked in 3× crop (175,620)–(575,800); roughly +/-4–6 px. Finger naming order is only a silhouette trace, not joint reconstruction. Palm contact partly occluded by rind; patch is visual evidence, not measured load area.','observed_contact':'Four fingers visibly wrap lower rind; palm continues beneath slice; thumb is visible on the far/side edge. No bite notch; red flesh contour remains intact. Wrist is downstream of palm, not the attachment point for a floating slice.','support_analysis':'In the 2D crop, melon center proxy (~273,700) projects down into the finger/palm x-span (~220–325). This is a screen-space sanity check only; no 3D center of mass, physical load, or bone lengths are established.','view_compatibility':'NOT approved as a finished S03a angle. S03 k07 is a side-on offer viewed toward grandma; S03a is a receiving-side close-up with the forearm entering from the camera-side bottom-right, requiring depth/foreshortening changes. A rigid 2D crop/rotation can test composition but cannot certify that view change.','needs_new_angle_reference':True,'new_angle_reference_brief':'Use k07 for exact right-hand identity, unbitten melon silhouette and finger/palm contact. Obtain an explicit right-hand, palm-up, wrist-nearer-camera reference with forearm receding from lower-right toward the slice. Preserve correct thumb side; do not mirror k07, invent a reversed left hand, or hide contact with blur.','proposed_composition_native_1672x941':{'face_reference':'exact original focus only for review; no new painted pose','melon_envelope_xyxy':[920,760,1220,935],'wrist_forearm_entry_from':[1530,1040],'assembly_target':[1120,860],'face_contact':'none; keep a visible gap from chin/lips; foreground may cover lower-right collar/chest only','layer_order':['background','Xiaoman','independent grouped right-hand+melon RGBA foreground'],'asset_motion':'One transform for complete hand+melon; settle by f8. Mild blur applied to entire group in scene. No phone in frame.','caution':'Envelope is a composition proposal, not a generated/approved hand shape, actual limb path or exact runtime crop.'}}
s03={**common,'shot':'S03a','duration_frames':36,'counts':{'exposure_states':6,'plan_face_entries':6,'foreground_group_assets':1,'generated':0,'reuse_policy':'d01/d02 have the same face intention; retain both exposure entries. No collapse or new art count reduction without reference gate.'},'states':states3,'segments':[{'id':'A','states':['d01','d02'],'chain':'focus → d01 → d02','old_boundary_anchor':'focus','reason':'Phone gaze unchanged while independent melon arrives.'},{'id':'B','states':['d03','d04'],'chain':'accepted d02 → d03 → d04','old_boundary_anchor':'focus with genuine perspective reference, not code proportions','reason':'Single small left rejection; far-eye and cheek occlusion change.'},{'id':'C','states':['d05','d06'],'chain':'accepted d04 → d05 → d06','old_boundary_anchor':'focus frontal face/head/collar endpoint; mouth alone remains mildly pouty','reason':'Return on same path, no right overshoot or cyclic shake.'}],'projection_assumptions':{'head':'Fixed cranial volume, no rescaling. Differential screen landmark shifts visualize weak-perspective yaw, but are not a rig or measured skull.','neck':'Chin x shifts <=8px while collar stays at observed focus; local skin and collar occlusion need real drawing review.','gaze':'Offscreen phone target is scene-stable, not attached to turning head. Do not aim pupils at the approaching melon.','camera':'Same low frontal setup, slightly looser framing only at scene integration; do not scale the native character to match code body proportions.'},'contact_reference':contact}
write('S03a_reference_proposal.json',s03)

def overview03():
 im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im);txt(d,(26,14),'S03a · 6态 + 独立右手瓜组的最小提案',31);txt(d,(26,58),'36f / 24fps　一次向画面左偏 → 沿原路回正　瓜先到、眼不离手机　手机/自己的手不入画',21)
 for i,s in enumerate(states3):
  c=i%3;r=i//3;x=22+c*551;y=108+r*370
  d.rounded_rectangle((x,y,x+535,y+350),10,outline='#c9d1d2',width=2)
  txt(d,(x+12,y+8),f"d{i+1:02}  f{s['start_frame']:02}–{s['end_frame_exclusive']-1:02} · {s['hold_frames']}f  {s['read']}",20)
  g=draw_guide(s,'S03a');crop=(490,110,1170,941);mini=g.crop(crop).resize((205,250),Image.Resampling.LANCZOS);im.paste(mini,(x+12,y+55))
  txt(d,(x+232,y+76),s['notes'][0],18);txt(d,(x+232,y+113),s['notes'][1],18)
  txt(d,(x+232,y+162),f"偏头幅度提案 {s['yaw_proposal_deg']}°",19,BLUE)
  txt(d,(x+232,y+205),'蓝轴/鼻/眼不同量变化',17,BLUE)
  txt(d,(x+232,y+239),'远近眼/耳/刘海需真透视',17)
  txt(d,(x+15,y+314),'前景：画外起势' if i==0 else '前景：一组手瓜已到位；脸与瓜不接触',18,ORANGE)
 txt(d,(26,873),'d01/d02意图同脸，但六条曝光完整保留；不擅自合并。每格裁区同S05a，原坐标1672×941。',20)
 txt(d,(26,907),'线图只表达差动投影，不能凭这几条线宣称9°骨骼转头已实现；右手瓜角度门另见接触图。',20)
 im.save(ROOT/'qa/S03a_6state_minimal_overview.png')
overview03()

# Actual-source contact analysis. Original crops remain unwarped apart from uniform display scaling.
def actual_composite(path,box=None):
 im=Image.open(path).convert('RGBA');im=im.crop(box) if box else im;b=Image.new('RGBA',im.size,(235,236,230,255));b.alpha_composite(im);return b.convert('RGB')
cp=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(cp);txt(d,(24,12),'S03a · 右手托未咬瓜：exact母源与接触门',31);txt(d,(24,56),'选择 S03 k07（紧邻出镜等待态）；k06仅对照。下图是原图裁切/标记，未生产新手瓜。',21)
box=(175,620,575,800);p7=next((GRAND/'painted').glob('*k07*'));p6=next((GRAND/'painted').glob('*k06*'))
cr=actual_composite(p7,box).resize((820,369),Image.Resampling.LANCZOS);cp.paste(cr,(24,116));txt(d,(26,92),'k07 原件接触近图 · 等比2.05× · 未镜像',19)
scale=2.05
pts={'1':(240,638),'2':(204,696),'3':(304,753),'4':(346,736)}
for lab,(x,y) in pts.items():
 x=24+(x-box[0])*scale;y=116+(y-box[1])*scale;d.ellipse((x-11,y-11,x+11,y+11),fill=BLUE);txt(d,(x-5,y-12),lab,16,'white')
for j,s in enumerate(['1 完整瓜尖/果肉轮廓：没有咬痕','2 拇指在侧后缘稳定；不镜像换成左手','3 掌承托下皮，四指绕住下缘','4 手腕接在掌后：瓜不是挂在腕端']):txt(d,(30,500+j*37),s,22)
cr6=actual_composite(p6,box).resize((440,198),Image.Resampling.LANCZOS);cp.paste(cr6,(24,680));txt(d,(480,694),'k06同一托持形制，作为接触对照',20);txt(d,(480,734),'k07更接近S03a前一镜出点',20);txt(d,(480,774),'两者均未咬；不取S03b缺口版',20)
# composition envelope over exact focus reference, no hand artwork placed into it
layout=actual_composite(SHARED/'originals/S02a_k01_focus.png');ld=ImageDraw.Draw(layout)
ld.rectangle((920,760,1220,935),outline=ORANGE,width=7)
line(ld,[(1530,1040),(1120,860)],ORANGE,9);line(ld,[(1120,860),(1155,859)],ORANGE,9);line(ld,[(1120,860),(1142,888)],ORANGE,9)
# leave the actual face untouched; draw arrow only in empty forearm-side envelope
layout=layout.resize((760,428),Image.Resampling.LANCZOS);cp.paste(layout,(888,116));txt(d,(891,92),'目标构图包络 · focus原件仅定位用',19)
txt(d,(897,552),'橙框=瓜的提案区；箭头从镜头侧右下进入',20,ORANGE)
txt(d,(897,590),'允许挡下方领口/胸；与下颏、嘴留间隙',20)
txt(d,(897,642),'角度门仍未通过',26,'#a44729')
for j,s in enumerate(['k07是侧向递出；目标有朝远处递送的纵深缩短。','要补同一右手、掌心向上、腕近瓜远的新角度参考。','不能镜像；不能靠平面旋转或虚焦假装换了机位。','后续资产：手+瓜一组RGBA，整体移动/旋转/虚焦。']):txt(d,(897,688+j*39),s,19)
txt(d,(26,902),'k07 Git blob afcf8b0e9e7e675d2a1ecf43bbce69ad801ab4e6；原生1670×941，不拉伸凑1672。完整SHA见JSON。',18)
cp.save(ROOT/'qa/S03a_right_hand_melon_contact.png')
with (ROOT/'README.md').open('a') as f:f.write('''

## S03a 核心
- `qa/S03a_6state_minimal_overview.png`、`qa/S03a_right_hand_melon_contact.png`、`S03a_reference_proposal.json`。
- 36帧/6态0,8,17,19,26,29，另1组前景手瓜。只向画面左偏一次再回；鼻、眼、脸廓差动/遮挡需成立，不能脸整体平移。画外手机视线不变；瓜不碰脸。
- 三段：A(01–02)脸不响应来瓜；B(03–04)单次左偏；C(05–06)回正。每张沿上一合格图，段界对照旧focus；回正不越中线。d01/d02同脸意图不授权删曝光或减少清单。
- 手瓜选 exact k07：Git blob `afcf8b0e9e7e675d2a1ecf43bbce69ad801ab4e6`，SHA256 `4f00f1f0b3aaba92999c01ff87ef50c8762f2cc537e8c0fa68df837dc95a919c`；k06比较源为`3b6e7d22f8a45b4a589fed79fda8c9d463bbeadf`。两张均掌托/四指绕下缘/拇指稳侧，瓜未咬。奶奶左腕有玉镯，递出的是无镯右手，不能镜像。
- k07只冻结手瓜身份/形制/接触母源，**不冻结S03a新视角**：S03侧向递出和镜头侧右下纵深递入不等价。需新的同一右手角度参考再开这1组资产；本包不制造新手瓜。原件1670×941（k06是1671×941），接触分析按各自原像素，不拉宽凑1672。
- 新手瓜应整组RGBA，f8前到位，前臂从右下出画；虚焦不能遮掩托持错误。构图橙框只是空间包络，不是资产轮廓。
''')
# Machine checks for timing, unchanged sources, and deliverable types.
assert [s['start_frame'] for s in states]==[0,10,14,24,28,44,46,50,52] and sum(s['hold_frames'] for s in states)==60
assert [s['start_frame'] for s in states3]==[0,8,17,19,26,29] and sum(s['hold_frames'] for s in states3)==36
assert k07['git_blob']=='afcf8b0e9e7e675d2a1ecf43bbce69ad801ab4e6' and k06['git_blob']=='3b6e7d22f8a45b4a589fed79fda8c9d463bbeadf'
for a in source_manifest:
 p=ROOT/a['local'];assert p.exists();assert hashinfo(p)['sha256']==a['sha256']
for p in (ROOT/'qa').glob('*overview.png'):assert Image.open(p).size==(W,H)
checks={'timing':'PASS: 9 states/60f and 6 states/36f contiguous, original frame starts unchanged','source_hashes':'PASS: all listed local image SHA256 hashes rechecked; no mutation','hand_source':'PASS: exact k07/k06 Git blob hashes match independently read remote manifest','visual_inspection':'Originals, identity sheets, code overview, and 3x contact crops actually inspected; final PNG QA still required after script.','production_images_generated':0,'repository_writes':0,'unresolved_gates':['S05/S05a causal wording interpretation','S03a true small-yaw perspective reference and right-hand foreground angle before painting']}
write('qa/validation.json',checks)
print('S03a core and contact ready',ROOT)

# Final QA bookkeeping: all three assembled PNGs were actually viewed at this version.
for name in ['S05a_reference_proposal.json','S03a_reference_proposal.json']:
 p=ROOT/name;obj=json.loads(p.read_text());obj['source_aliases']={k:{'local':'../astra_xiaoman_opening_refs_20261018_0906/originals/'+v,'git_blob':next(a['git_blob'] for a in source_manifest if a['local'].endswith(v))} for k,v in [('focus','S02a_k01_focus.png'),('tense','S02a_k02_tense.png'),('relief','S02a_k03_relief.png')]};obj['actual_measurement_source']='../astra_xiaoman_opening_refs_20261018_0906/qa/measurements.json';write(name,obj)
p=ROOT/'S05a_reference_proposal.json';obj=json.loads(p.read_text());obj['unlisted_code_blink']='pose() adds blink at t=1.55s, absent from approved nine-state plan. Do not add it, merge exposure entries or obscure the concern read without separate approval.';write(p.name,obj)
checks['visual_inspection']='PASS: actual originals/identity/code contact sheets, 3x hand crops, and all three assembled 1672x941 overview/contact PNGs viewed; labels and layout legible, no clipped text. No original pixels were altered.';write('qa/validation.json',checks)
checksums=[]
for p in sorted(ROOT.rglob('*')):
 if p.is_file() and p.name!='SHA256SUMS.txt':checksums.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(ROOT)))
(ROOT/'SHA256SUMS.txt').write_text('\n'.join(checksums)+'\n')
