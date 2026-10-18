from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, math, hashlib
R=Path(__file__).resolve().parents[1]; BASE=R.parent
OLD=BASE/'astra_next_closeup_refs_20261018_0920'
manifest=json.loads((OLD/'sources/source_manifest.json').read_text())
paths=[
'astra_s03b_painted_pilot_20261018/refs/painted/S03_grandma_k07_F079_t3.30.png',
'astra_xiaoman_opening_refs_20261018_0906/originals/S02a_k01_focus.png',
'astra_xiaoman_opening_refs_20261018_0906/code_refs/S03a/S03a_d02_f008.jpg',
'astra_xiaoman_opening_refs_20261018_0906/code_refs/S03a/S03a_d04_f019.jpg',
'astra_xiaoman_opening_refs_20261018_0906/sources/s03a.js']
sources=[]
for p in paths:
 f=BASE/p; b=f.read_bytes(); sha=hashlib.sha256(b).hexdigest()
 rec=next((m.copy() for m in manifest if m['local']=='../'+p), {'local':'../'+p})
 if 'sha256' in rec: assert rec['sha256']==sha
 rec.update({'sha256':sha,'git_blob_local':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest(),'byte_count':len(b),'viewed_or_read_here':True})
 sources.append(rec)
# Every geometric value below is a design proposal, never a measured new drawing.
P={
 'melon_tip_far_up':[1008,766],
 'red_face_corner_left':[960,837], 'red_face_corner_right':[1175,830],
 'rind_bottom_near':[1094,911], 'melon_center_proxy':[1077,839],
 'palm_load_patch':[1112,906], 'palm_center_hidden':[1145,871],
 'thumb_radial_tip':[1190,840], 'thumb_root':[1197,883],
 'wrist_center':[1245,930], 'forearm_offscreen_center':[1495,1140],
 'index_visible_tip':[1017,874], 'middle_visible_tip':[1038,891],
 'ring_visible_tip':[1065,907], 'little_visible_tip':[1095,920]
}
red=[P['melon_tip_far_up'],P['red_face_corner_left'],[981,858],[1013,876],[1048,887],[1082,889],[1119,879],[1151,858],P['red_face_corner_right'],P['melon_tip_far_up']]
rind_outer=[[982,855],[1003,876],[1035,894],[1070,905],[1104,907],[1141,897],[1173,876],[1197,848]]
fingers=[
 {'digit':'I / 食指','hidden_path':[[1170,872],[1120,847],[1050,843],[1015,859]],'visible_path':[[1002,859],[1003,866],[1017,874],[1030,876]]},
 {'digit':'M / 中指','hidden_path':[[1160,890],[1110,873],[1060,867],[1022,878]],'visible_path':[[1021,876],[1024,885],[1038,891],[1052,893]]},
 {'digit':'R / 无名指','hidden_path':[[1150,907],[1120,896],[1073,886]],'visible_path':[[1047,893],[1053,901],[1065,907],[1080,908]]},
 {'digit':'L / 小指','hidden_path':[[1140,920],[1122,913],[1090,900]],'visible_path':[[1078,908],[1082,915],[1095,920],[1110,918]]}
]
angle=math.degrees(math.atan2(1140-930,1495-1245))
obj={
 'shot':'S03a','asset_id':'S03a_grandma_right_hand_intact_melon','scope':'REFERENCE DIAGRAM ONLY; no image generation, no production art, no remote writes',
 'status':'Approved direction interpreted as a single projection proposal; not an unapproved-direction gate. Opus owns final integration. This diagram does not certify an actual painted asset.',
 'approved_direction':{'commit':'98745bd8fb5aa0407978334b99c9ecdd651b9d39','source':'Exact Opus wording forwarded by parent at 2026-10-18 09:56 UTC; commit was not independently fetched in this subtask','verbatim':'从画面右下角伸进来，小臂斜着出画，大约40°；掌心朝上托着瓜皮；瓜尖朝小满，也就是离开镜头的方向，所以瓜尖会透视缩短、往上翘；镜头在小满脸的高度、离奶奶的手很近，所以看到的是手背偏下一点的角度；单独画一张，焦点清楚，虚化和推入画面由我在代码里做。可以先按这个画，脸那一串照常走，不用等手。'},
 'coordinate_system':{'guide_canvas':[1672,941],'origin':'top-left, x right, y down','units':'native guide pixels','all_new_geometry':'Proposed 2D guides; no measured 3D anatomy, no recovered physical camera parameters. Do not rescale the 1670x941 k07 source to 1672.'},
 'camera_and_pose':{'direction':'From camera-side lower-right wrist toward upper-left distal hand and melon; wrist near, melon tip far. One anatomical right hand, palm-up, no bracelet, never mirror.', 'forearm_screen_angle_deg':round(angle,3),'angle_convention':'40 degrees below +x from wrist to offscreen forearm; reverse toward hand is 220 degrees in screen y-down coordinates. This is screen angle, not camera yaw.', 'depth_order_near_to_far':['forearm and wrist','proximal palm / near rind','curled distal digits and melon tip','Xiaoman face'], 'cut_face':'Red cut plane seen obliquely, with a separate visible curved rind thickness on the camera-near lower/right side. Tip recedes and rises; do not retain a frontal flat triangle by merely rotating it.', 'dorsal_wording_resolution':'At face-height camera above a lower hand, a level upturned palm cannot show a full dorsal plate. Interpret 手背偏下一点 as a near-wrist grazing view: the melon occludes most palm, camera sees side/back arcs of curled digits plus near wrist underside edge. A small continuous support patch remains under rind. Do not pronate the hand to manufacture a full back-of-hand view.', 'projection_limit':'This interpretation resolves the wording without moving the established face camera. Full exposed hand-back would require a different palm tilt or camera relation and is not proposed.', 'camera_height_and_support_plane':{'camera_height':'At Xiaoman face height per approved instruction, above the lower foreground support patch; no metric height was supplied or measured','palm_support_normal':'world-up; melon rests on the upper palmar surface','near_wrist_view':'grazing downward view from proximal/wrist side; see occluded palm and curled digit side/back arcs, not a fully exposed dorsal plane','section_drawing':'relationship schematic only; no new camera transform or lens value is being prescribed'}, 'wording_resolution_status':'Parent explicitly accepted this physically implementable reading at 2026-10-18 09:59 UTC; parent will return it to Opus with the reference before single-asset final production.'},
 'target_points_px':P,
 'melon_outline_proposal':{'red_cut_face_polyline':red,'near_outer_rind_polyline':rind_outer,'visible_rind_thickness_guide_px':[18,28],'note':'Construction contours, not final melon silhouette or recovered dimensions; preserve k07 intact sector identity and no bite.'},
 'right_hand_projection':{'thumb_side':'screen upper/right radial edge, separate stabilizing contact; never switch it to lower/left by mirror','thumb_visible_polyline':[[1197,883],[1210,866],[1207,850],[1197,838],[1190,840],[1188,852]], 'four_fingers':fingers, 'finger_visibility':'I and M are more occluded by melon; R and L near-side arcs remain readable. Four digits exist, but four equally exposed parallel fingertips are forbidden. Dashed construction paths are not painted contours.', 'palm_support':'Curved rind rests on continuous palm/finger cradle near [1112,906]; no floating slice, wrist is not the load attachment.', 'load_check':'Only a 2D support sanity check. Melon center proxy x1077 lies inside approximate projected support span x1000–1170; no 3D mass or physical force claim.'},
 'composition':{'melon_envelope_xyxy':[950,752,1210,915],'hand_melon_group_guide_envelope_xyxy':[950,752,1550,1190],'offscreen_overscan_required':True,'face_reference':'exact focus; use only for composition, retain six face states','face_exclusion':'No contact with chin, lips, or cheek; may overlap lower-right collar/chest only. Current tip is [170,36] from focus chin [838,730].','phone_and_xiaoman_hands':'offscreen, do not generate','actual_canvas_crop_and_asset_anchor':'Opus to bind; guide envelope is not an instruction to bake crop or change the established face canvas'},
 'reuse_vs_redraw':{'reuse':['k07 exact right-hand identity, skin/shape language and no bracelet','intact melon sector identity and material colors','palm-under-rind / four curled fingers / thumb-side stability contact topology'],'must_draw_new':['wrist-to-palm depth foreshortening','new radial thumb and four-digit occlusion under the melon','receding/upturned tip and oblique cut plane','near curved rind thickness and continuous load contact']},
 'integration':{'asset_count':1,'asset_type':'One sharp right hand + intact melon RGBA group; no baked blur or push-in','timing':'Arrive by first f8 exposure; f8 onward the single group is in position. Face 0/8/17/19/26/29 unchanged. Opus owns motion/blur.','face_performance':'Eyes remain on offscreen phone; one screen-left head avoidance then return; no acceptance of melon.','face_can_proceed_independently':True},
 'acceptance_check':['one anatomical right hand with correct thumb side, no bracelet, no mirror','clear support contact at sharp focus before compositor blur','receding tip and near rind reveal genuine new depth; not a 2D rotated k07','no need to expose all four fingertips; no extra/missing digit','transparent independent single group, no phone, no Xiaoman hand, no face contact'],
 'source_manifest':'sources/source_manifest.json'
}
(R/'S03a_foreground_direction.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
(R/'sources/source_manifest.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n')
# Single board. Raster edits below are crops/scale for reference display only; new geometry is a labelled analytical line diagram.
W,H=1840,1160; BG='#f7f7f3'; INK='#273944'; TEAL='#16839b'; ORANGE='#b56b2a'; RED='#b64f4f'; GRAY='#9ba6aa'; GREEN='#557d56'
im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
fontpath='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
def F(n):return ImageFont.truetype(fontpath,n)
def text(x,y,s,n=23,c=INK):d.text((x,y),s,font=F(n),fill=c)
def line(points,c=TEAL,w=3):d.line(points,fill=c,width=w,joint='curve')
def dashed(a,b,c=GRAY,w=2,step=8):
 l=math.dist(a,b)
 for v in range(0,int(l),step*2):
  t=v/l;t2=min(1,(v+step)/l)
  line([(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t),(a[0]+(b[0]-a[0])*t2,a[1]+(b[1]-a[1])*t2)],c,w)
def arrow(a,b,c=TEAL,w=3):
 line([a,b],c,w);a0=math.atan2(b[1]-a[1],b[0]-a[0]);size=12
 line([(b[0]-size*math.cos(a0-.45),b[1]-size*math.sin(a0-.45)),b,(b[0]-size*math.cos(a0+.45),b[1]-size*math.sin(a0+.45))],c,w)
def marker(x,y,label,c=TEAL):
 d.ellipse((x-13,y-13,x+13,y+13),fill=BG,outline=c,width=2);d.text((x-7,y-12),label,font=F(17),fill=c)
def pasted(path,box,dest):
 a=Image.open(path).convert('RGBA').crop(box);a.thumbnail(dest[2:],Image.Resampling.LANCZOS);back=Image.new('RGBA',a.size,'#eeeee9');back.alpha_composite(a);im.paste(back.convert('RGB'),dest[:2]);return a.size
text(25,15,'S03a · 前景右手托瓜：已放行方向的投影说明',34)
text(26,62,'单个清晰手瓜组 · 腕近瓜尖远 · 小臂约40° · 分析线图，非实际新画／非生产资产',24,ORANGE)
# Left mother reference.
text(26,110,'A  k07原件：身份／托持母源',25)
pasted(BASE/paths[0],(175,620,575,800),(26,155,530,240))
text(26,413,'原1670×941；此处只等比裁切展示，未镜像。',19)
text(26,446,'可继承：无镯右手、完整瓜、掌托皮壳。',21)
text(26,482,'不可继承：侧向镜头的手指重叠／瓜切面。',21)
text(26,528,'机位关系剖面（非实测高度）',24)
text(26,566,'镜头＝小满脸高；托面在镜头下方。',21)
# Side-section relationship: lens and face on same height; upturned palm lower.
dashed((63,640),(517,640),GRAY,2)
d.rectangle((43,628,75,653),outline=INK,width=3)
d.ellipse((73,633,85,647),outline=INK,width=2)
d.ellipse((498,628,522,652),outline=INK,width=2)
text(26,603,'镜头',17);text(473,603,'脸高',17)
arrow((85,643),(262,709),GRAY,2)
line([(200,744),(246,722),(320,722)],TEAL,4)
line([(211,754),(254,735),(327,735)],TEAL,2)
line([(260,713),(305,667),(337,713),(260,713)],RED,3)
line([(260,713),(298,721),(337,713)],GREEN,4)
arrow((357,745),(357,682),TEAL,3)
text(373,694,'托面',18,TEAL);text(373,722,'朝上',18,TEAL)
text(125,764,'近腕侧低掠；瓜挡住掌心大部。',19)
text(26,804,'对Opus措辞的可实现解释，非翻掌。',20,ORANGE)
# Center analytical hand with 2x native local detail.
text(585,110,'B  新视角构造：拇指／四指遮挡',25)
s=2.0;ox=585;oy=160;gx=940;gy=742
T=lambda p:(ox+(p[0]-gx)*s,oy+(p[1]-gy)*s)
# construction palm, wrist and forearm. Polygon is NOT a final hand outline.
palm=[[1082,900],[1120,858],[1174,852],[1208,881],[1266,913],[1230,950],[1174,930],[1126,922]]
for a,b in zip(palm,palm[1:]+palm[:1]):dashed(T(a),T(b),TEAL,2,6)
for a,b in zip([[1266,913],[1450,1068]],[[1450,1068],[1495,1140]]): pass
line([T([1266,913]),T([1307,948])],TEAL,3);line([T([1230,950]),T([1271,985])],TEAL,3)
# Hidden finger constructions first.
for f in fingers:
 for a,b in zip(f['hidden_path'],f['hidden_path'][1:]):dashed(T(a),T(b),GRAY,2,6)
# Red surface and separate shell depth are line diagrams, no painted fill.
line([T(p) for p in red],RED,4);line([T(p) for p in rind_outer],GREEN,5)
line([T([960,837]),T([982,855])],GREEN,3);line([T([1175,830]),T([1197,848])],GREEN,3)
for a,b in [([1003,872],[1015,885]),([1048,887],[1061,903]),([1100,885],[1116,905]),([1148,860],[1163,888])]:line([T(a),T(b)],GREEN,2)
for i,f in enumerate(fingers):
 line([T(p) for p in f['visible_path']],TEAL,5)
 q=f['visible_path'][2];marker(*T([q[0]-7,q[1]+13]),'IMRL'[i])
line([T(p) for p in obj['right_hand_projection']['thumb_visible_polyline']],TEAL,5)
marker(*T([1214,841]),'T')
# support patch, drawn exactly touching near shell.
q=T(P['palm_load_patch']);d.ellipse((q[0]-25,q[1]-8,q[0]+25,q[1]+9),outline=ORANGE,width=4)
arrow(T([1130,1010]),T(P['palm_load_patch']),ORANGE)
text(950,715,'掌承重接触',20,ORANGE)
arrow(T([1065,810]),T([1008,766]),ORANGE)
text(704,147,'瓜尖远／上翘',20,ORANGE)
text(885,324,'斜向切面',20,RED)
text(1027,470,'近侧皮壳厚边',19,GREEN)
text(586,761,'T右上侧稳瓜；I/M被挡更多；R/L近侧卷托可见。',20)
text(586,794,'虚线只解释掌／指路径；不在最终画里露出。',20)
# Right composition.
text(1350,110,'C  focus原件定位',25)
focus=Image.open(BASE/paths[1]).convert('RGBA')
fw=460;fh=round(941*fw/1672);a=focus.resize((fw,fh),Image.Resampling.LANCZOS);bg=Image.new('RGBA',a.size,'#eeeee9');bg.alpha_composite(a);im.paste(bg.convert('RGB'),(1350,155));
sc=fw/1672;C=lambda p:(1350+p[0]*sc,155+p[1]*sc)
line([C(p) for p in red],RED,3);line([C(p) for p in rind_outer],GREEN,3)
arrow(C([1530,1140]),C([1245,930]),ORANGE,3)
x,y=C([838,730]);d.ellipse((x-4,y-4,x+4,y+4),fill=ORANGE)
text(1350,440,'只挡下方右领／胸；不碰下巴、嘴。',20)
text(1350,477,'眼睛仍看画外手机。',20)
text(1350,514,'小满手和手机不生成。',20)
text(1350,551,'F8前到位；单次左偏后回正。',20)
text(1350,592,'Opus 98745bd8：单张清晰RGBA',19)
text(1350,622,'腕 → 画外小臂 = 40.0°',22,TEAL)
arrow((1390,660),(1540,786),TEAL,4);dashed((1390,660),(1575,660));text(1468,679,'40°',23,TEAL)
text(1350,807,'40°是画面内轴线，不是镜头俯角。',19)
# Bottom note clarifies camera without fake impossible dorsal view.
d.line([(26,854),(1814,854)],fill='#c5cecf',width=2)
text(26,875,'“掌心向上”＋“手背偏下一点”的落实',25)
text(26,922,'保留脸高机位，从近腕侧低掠看手：瓜遮住掌心大部；可见的是卷指背／侧缘和腕近侧下缘。',23)
text(26,963,'掌面仍托着皮壳，接触处保留连续小段；不把整块手背翻向镜头，不用虚焦藏托持错误。',23)
text(26,1010,'真新画必须补：腕掌纵深缩短、拇指与四指前后遮挡、瓜尖缩短上翘、切面与近侧皮壳厚度。',23,ORANGE)
text(26,1063,'本页坐标为1672×941构图提案，非实测新画；不改变六脸态曝光／原件。完整坐标与来源见同包JSON。',20)
text(26,1100,'已实看：原k07、S03a F8/F19代码参考、focus母源。无生图、无远端写入；不得用2D旋转或虚焦冒充此新视角。',20)
im.save(R/'S03a_foreground_direction.png')
# Output validations and source-preservation evidence.
for source in sources:
 assert hashlib.sha256((R/source['local']).read_bytes()).hexdigest()==source['sha256']
assert abs(angle-40)<.2
assert P['thumb_radial_tip'][0]>P['palm_center_hidden'][0]
assert min(p[1] for p in red)>730
qa={'status':'generated reference board and JSON; production art count 0','source_hashes':'PASS; independently recomputed before and after; originals unchanged','source_k07_canvas':[1670,941],'guide_canvas':[1672,941],'single_group_asset_count':1,'generated_production_images':0,'remote_writes':0,'forearm_axis_angle_deg':angle,'camera_interpretation':'near-wrist grazing occlusion, not full exposed dorsal plate','direction_status':'already approved by Opus; this is projection clarification, no renewed blocking gate','visual_qa':'pending actual view of delivered PNG'}
(R/'qa/validation.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
