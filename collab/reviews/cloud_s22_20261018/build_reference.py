"""S22 technical references only: annotate actual source pixels; never generate production hands."""
from pathlib import Path
import json, math, csv, hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
def ft(n):return ImageFont.truetype(FONT,n)
C='#bf731b';G='#087b84';R='#604124';BG='#f8f7f2';GRAY='#6d7377'
def text(d,p,s,n=24,c='#20262b'):d.text(p,s,font=ft(n),fill=c)
def arrow(d,a,b,c='#435766',w=4):
 d.line([a,b],fill=c,width=w);ang=math.atan2(b[1]-a[1],b[0]-a[0]);l=14
 d.polygon([b,(b[0]-l*math.cos(ang-.45),b[1]-l*math.sin(ang-.45)),(b[0]-l*math.cos(ang+.45),b[1]-l*math.sin(ang+.45))],fill=c)
def dot(d,p,r=6,c='#af3f37'):d.ellipse((p[0]-r,p[1]-r,p[0]+r,p[1]+r),fill=c)
def line(d,a,b,label,c='#a44135',n=19):d.line([a,b],fill=c,width=3);dot(d,a,4,c);dot(d,b,4,c);text(d,((a[0]+b[0])/2+8,(a[1]+b[1])/2-10),label,n,c)
(P/'reference/poses').mkdir(parents=True,exist_ok=True)
# All points are manually observed in actual approved turnaround artwork, native pixels.
measures={
 'grandma':{'source':'collab/refs/grandma_turnaround_current03_draft.png','crop':[985,414,1063,517],'W':[1028,441],'MCP':[1034,480],'tip':[1029,509],'uncertainty_px':4,'scale_proposal':5.0},
 'xiaoman':{'source':'collab/refs/xiaoman_turnaround_v4_draft.png','crop':[724,499,794,604],'W':[754,521],'MCP':[758,558],'tip':[768,595],'uncertainty_px':4,'scale_proposal':4.0}}
im=Image.new('RGB',(1600,820),BG);d=ImageDraw.Draw(im);text(d,(28,16),'S22｜实际角色手部读点（不是新绘图，不是完整三维骨长）',30)
for i,(who,z) in enumerate(measures.items()):
 src=Image.open(ROOT/z['source']);b=z['crop'];scale=5;crop=src.crop(b).resize(((b[2]-b[0])*scale,(b[3]-b[1])*scale));ox=40+i*790;oy=118;im.paste(crop,(ox,oy))
 def t(q):return (ox+(q[0]-b[0])*scale,oy+(q[1]-b[1])*scale)
 col=G if who=='grandma' else C;text(d,(ox,69),'奶奶 current03 侧视' if who=='grandma' else '小满 v4 侧视',25,col)
 for k in ['W','MCP','tip']:dot(d,t(z[k]),6,col);text(d,(t(z[k])[0]+12,t(z[k])[1]-15),k,20,col)
 a=math.dist(z['W'],z['MCP']);b0=math.dist(z['MCP'],z['tip']);total=math.dist(z['W'],z['tip']);z.update({'palm_projected_px':round(a,2),'visible_digit_chain_projected_px':round(b0,2),'W_to_tip_projected_px':round(total,2)})
 text(d,(ox,665),f'腕→掌指线 {a:.1f}px；可见指链 {b0:.1f}px',21,col);text(d,(ox,704),f'腕→指尖投影 {total:.1f}px；读点不确定度 ±4px',20)
text(d,(30,760),'MCP为可见分指/掌指线附近的读点；PIP/DIP及被握住的骨节未清楚显示，不填伪精确骨长。',22)
im.save(P/'reference/01_observed_hand_lengths.png')
(P/'provenance/observed_measurements.json').write_text(json.dumps(measures,ensure_ascii=False,indent=2)+'\n')
# Unmodified old art crop audit: actual shape reference only, not locked grip/hand identity.
src=Image.open(ROOT/'collab/refs/anim_22_hands_together.png');im=Image.new('RGB',(1600,900),BG);d=ImageDraw.Draw(im);text(d,(25,10),'旧S22原手审计｜原图像素＋标注；四手/两签，不作为新包握拓扑母版',28)
b=(340,66,1020,470);im.paste(src.crop(b).resize((1088,646)),(22,75))
def srcpt(x,y):return (22+(x-340)*1.6,75+(y-66)*1.6)
for p,q,lab in [((918,298),(1135,180),'A 签轴/夹点\n孩子自身拇指对夹不够清楚'),((800,247),(1135,325),'B 成人拇指压背\n不能替代小满自己握签'),((675,427),(1135,480),'C 包指下缘\n必须连回同一掌与腕')]:
 dot(d,srcpt(*p),8);arrow(d,q,srcpt(*p));text(d,(q[0],q[1]-55),lab,21)
text(d,(30,755),'原图1536×1024；上下近似构型的左右手身份旧审未确认。单绿镯只属于奶奶左腕。',23)
text(d,(30,804),'本提案：主读一组右手包右手，无镯；保小满夹签可见。另一组/第二签是否画外由Astra冻结。',23)
im.save(P/'reference/02_old_grip_audit.png')
# Twelve exposures: own action plan from script, not copied old code-card motion.
starts=[0,12,18,24,36,42,60,66,84,90,108,114];holds=[12,6,6,12,6,18,6,18,6,18,6,6]
acts=['小满已自主握签；奶奶从肩外后上方接近','奶奶掌侧先触手背，未锁死','包指从尺侧下绕；孩子夹点仍露','包握完成，停稳；不替孩子持杆','第一推中间态','第一推末端＋停','第二推中间态','第二推末端＋停','第三推中间态','第三推末端＋停','第四推中间态','第四推末端，缓停']
steps=[0,0,0,0,.5,1,1.5,2,2.5,3,3.5,4]
rows=[]
for j,(f,h,a,k) in enumerate(zip(starts,holds,acts,steps)):
 delta=(round(28*k,2),round(-16*k,2));cw=[700+delta[0],700+delta[1]];gw=[650+delta[0],500+delta[1]]
 approach=[(-90,-70),(-28,-10),(-8,-3),(0,0)][min(j,3)];gw=[gw[0]+approach[0],gw[1]+approach[1]];p=[926+delta[0],598+delta[1]]
 phase=['approach_no_contact','first_back_contact','curl_ulnar_under','closed_wrap'][min(j,3)]
 rows.append({'start_frame':f,'end_frame_inclusive':f+h-1,'hold_frames':h,'action':a,'phase':phase,'joint_step':k,'shared_translation_xy':list(delta),'child_wrist_xy':cw,'grandma_wrist_xy':gw,'grip_P_xy':p,'rod_axis_direction':[.8660254,-.5],'rod_axis_equation':f'y={p[1]+math.tan(math.pi/6)*p[0]:.3f}-0.577350269*x','child_palm_projected_length_target_px':round(measures['xiaoman']['palm_projected_px']*4,1),'grandma_palm_projected_length_target_px':round(measures['grandma']['palm_projected_px']*5,1),'child_palm_depth_target_px':52,'grandma_palm_depth_target_px':64,'depth_status':'construction cross-section target, not measured3D thickness','occlusion':'child index/middle far pads > rod > child thumb near pad; grandma palm behind child, grandma curl tips locally in front below; never one whole-hand global order','wrist_chain':'bare forearm entry → W → MCP; constant measured palm/digit projected reference; elbow/shoulder outside frame, do not invent measured bone points','grip_lock':'P relative to child wrist = (226,-102), unchanged; no rod sliding after024','compression_px':0 if j<3 else 2 if h==6 else 1})
assert sum(holds)==120 and rows[-1]['end_frame_inclusive']==119
plan={'shot':'S22','status':'REFERENCE PROPOSAL, NOT FROZEN, NO IMAGE CALLS','baseline':'da16fc0c1136767dba24a804ce0db01e2eed9bae','fps':24,'frames':120,'duration_seconds':5,'drawings':12,'canvas':[1920,1080],'composition_proposal':'One principal right/right hand-over-hand pair in close-up. Old source has two pairs and two rods; must explicitly freeze one pair versus four hands before generating. Second control rod outside main contact crop if required; do not erase it from shared module here.','hand_identity':'Grandma RIGHT from behind/outside child RIGHT shoulder; child RIGHT independently grips. No jade on chosen right wrist; left jade retained only if a later approved left hand is shown.','reference_lengths':measures,'palm_depth_note':'52/64 are deliberately labeled proposed thickness proxies, not recovered physical depth. Read hand shape from real source crops; do not use construction rectangles as drawn palms.','camera_light':'Retain closeup/backstage warm upper-left light and gentle push-in as scene reference. No baked glow. Turtle and projection remain code. No scene module authored in this phase.','rows':rows}
(P/'S22_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
with (P/'S22_exposure.csv').open('w',newline='') as f:
 w=csv.writer(f,lineterminator='\n');w.writerow(['start_frame','end_frame','hold','action','shared_dx','shared_dy','child_wrist_x','child_wrist_y','grandma_wrist_x','grandma_wrist_y','grip_x','grip_y','axis_angle_deg','child_depth','grandma_depth','occlusion_phase'])
 for r in rows:w.writerow([r['start_frame'],r['end_frame_inclusive'],r['hold_frames'],r['action'],*r['shared_translation_xy'],*r['child_wrist_xy'],*r['grandma_wrist_xy'],*r['grip_P_xy'],-30,52,64,r['phase']])
# These are explicitly mechanical construction diagrams, never silhouettes/people.
def pose(r):
 im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im);f=r['start_frame'];dx,dy=r['shared_translation_xy'];cw=r['child_wrist_xy'];gw=r['grandma_wrist_xy'];p=r['grip_P_xy'];cm=(836+dx,639+dy);gm=(gw[0]+192,gw[1]+46)
 text(d,(30,15),f"S22 F{f:03d} × {r['hold_frames']}｜{r['action']}",31)
 text(d,(30,64),'技术构造；框/点不是手形，须结合实际原手读点和接触断面；未冻结，未生成',23,'#a34330')
 d.rectangle((1230,140,1800,405),outline='#c6c3b9',width=3);text(d,(1290,230),'乌龟／幕面区域\n由代码接景',30,GRAY)
 for entry,w,m,col,n in [((0,380),gw,gm,G,'奶奶右前臂｜肩外后上方进入'),((0,930),cw,cm,C,'小满右前臂｜近侧裸腕进入')]:
  d.line([entry,w,m],fill=col,width=7);dot(d,w,10,col);dot(d,m,8,col);text(d,(70,entry[1]+10),n,25,col);text(d,(w[0]-30,w[1]+22),'W',24,col);text(d,(m[0]+10,m[1]-30),'MCP',23,col)
  # Transparent construction volume, not a hand outline.
  vx=m[0]-w[0];vy=m[1]-w[1];ln=math.hypot(vx,vy);nx=-vy/ln;ny=vx/ln;half=40 if col==C else 49
  poly=[(w[0]+nx*half,w[1]+ny*half),(m[0]+nx*half,m[1]+ny*half),(m[0]-nx*half,m[1]-ny*half),(w[0]-nx*half,w[1]-ny*half)]
  d.line(poly+[poly[0]],fill=col,width=3)
 # child digit-chain guide and independently retained pinch.
 d.line([cm,(884+dx,620+dy),p],fill=C,width=5);d.line([p,(1180+dx,451+dy),(1900,598+dy-(1900-926-dx)*.577350269)],fill=R,width=9);dot(d,p,11,'#b43d35');text(d,(p[0]+20,p[1]+12),'P 自主夹签；轴固定−30°',24,R)
 if r['phase']!='approach_no_contact':
  contact=(800+dx,628+dy);d.line([gm,contact,(824+dx,697+dy)],fill=G,width=5);dot(d,contact,9,G);text(d,(1010,760),'奶奶包握手背/尺侧；不替孩子捏杆',25,G)
 arrow(d,(1270,880),(1270+112,880-64),'#6b6060');text(d,(1220,930),f"共同位移 Δ=({dx:g},{dy:g})；每步(+28,−16)",24)
 text(d,(45,996),'掌厚施工目标 小满52／奶奶64；掌/指读点长度见原图标注。握点相对小满腕(226,−102)恒定。',24)
 return im
contact=Image.new('RGB',(1920,870),BG)
for i,r in enumerate(rows):
 im=pose(r);im.save(P/'reference/poses'/f"F{r['start_frame']:03d}.png");thumb=im.resize((480,270));contact.paste(thumb,((i%4)*480,(i//4)*280))
contact.save(P/'reference/04_twelve_exposures.png')
# Contact topology: separate z cuts to prevent old global-order confusion.
im=Image.new('RGB',(1800,1050),BG);d=ImageDraw.Draw(im);text(d,(25,16),'S22 接触／前后层近图｜技术断面，不是生产手稿',31)
text(d,(35,80),'A 小满自己夹签（局部深度）',27,C)
# View direction is explicit; depth row is an exploded cut, not literal hand shape.
for x,y,w,h,col,label in [(110,210,340,125,C,'小满食/中指指腹\n远面：夹住杆'),(605,200,180,150,R,'竹签\n圆截面'),(970,210,340,125,'#d69642','小满拇指指腹\n近面：反向抵住')]:
 d.rounded_rectangle((x,y,x+w,y+h),25,outline=col,width=6);text(d,(x+15,y+22),label,25,col)
arrow(d,(470,270),(580,270),C);arrow(d,(945,270),(810,270),C);arrow(d,(1390,275),(1630,275));text(d,(1370,180),'相机在近面 →',24)
text(d,(60,386),'杆只有一根、轴穿过指腹间隙；不是穿手掌。拇指甲面必须归属小满，且能单独读到。',25)
text(d,(35,465),'B 手背包握（远 → 近的局部顺序）',27,G)
items=[(65,G,'奶奶掌心\n来自肩外后方'),(480,C,'小满手背＋掌厚\n始终连自己腕'),(970,G,'奶奶包指末节\n从尺侧绕到下近面'),(1430,'#6f6d64','相机近面')]
for x,col,lab in items:d.rounded_rectangle((x,565,x+285,715),20,outline=col,width=5);text(d,(x+15,590),lab,24,col)
for a,b in [(365,460),(780,950),(1275,1410)]:arrow(d,(a,640),(b,640),G)
text(d,(50,780),'奶奶拇指停在小满手背近腕处，距P留出至少一枚孩子拇指宽；奶奶不接管签子夹点。',24)
text(d,(50,833),'两条前臂在画外分别接肩/肘；近端不交叉。包指允许局部遮挡，不能用整张成人手层盖住孩子。',24)
text(d,(50,887),'掌厚目标：小满52px，奶奶64px；这是施工断面，不是从二维原图恢复出的三维实测厚度。',24)
text(d,(50,955),'冻结项：一组还是旧图两组；右/右归属；进入方向；夹点与轴；四次慢推曝光。未冻不调用。',23,'#a34330')
im.save(P/'reference/03_contact_layers_closeup.png')
# Provenance for read-only sources actually inspected.
sources=['collab/README.md','collab/claude.md','collab/partner.md','docs/keyframes/scenes03_12_drawing_plan.md','docs/preproduction/script-v3.md','js/code/s22.js','collab/refs/anim_22_hands_together.png','assets/chars/h22_together.png','collab/refs/grandma_turnaround_current03_draft.png','collab/refs/xiaoman_turnaround_v4_draft.png','collab/refs/anim_25_xiaoman_dog_hands.png']+[str(p.relative_to(ROOT)) for p in sorted((ROOT/'collab/keyposes/20261018_scenes03_12/S22').glob('*.jpg'))]
manifest={'baseline':plan['baseline'],'image_generation_calls':0,'sources':[],'images_actually_viewed':sources[6:],'existing_contact_sheets_total_frames':60,'reference_note':'All new raster files are labeled technical diagrams or actual-source annotations; none is a generated production hand.'}
for name in sources:
 f=ROOT/name;manifest['sources'].append({'path':name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size})
(P/'provenance/source_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('Measured actual source hands;12 exposures=120f; source annotations and technical near-layer diagrams written. Image calls0.')
