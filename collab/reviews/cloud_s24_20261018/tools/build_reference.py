#!/usr/bin/env python3
"""S24 labelled construction references only. No image generation or scene render."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import math,json,csv,hashlib,subprocess
import numpy as np

P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
def font(n):return ImageFont.truetype(FONT,n)
def text(d,xy,s,n=24,c='#25353e'):d.text(xy,s,font=font(n),fill=c)
def put(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dash(d,a,b,c='#72828b',w=2):
    a=np.array(a,dtype=float);b=np.array(b,dtype=float);v=b-a;L=np.linalg.norm(v)
    for t in range(0,int(L),14):d.line([tuple(a+v*t/max(L,1)),tuple(a+v*min(t+7,L)/max(L,1))],fill=c,width=w)
def arrow(d,a,b,c='#40738e',w=3):
    d.line([tuple(a),tuple(b)],fill=c,width=w);q=math.atan2(b[1]-a[1],b[0]-a[0])
    for r in [-.45,.45]:d.line([tuple(b),(b[0]-16*math.cos(q+r),b[1]-16*math.sin(q+r))],fill=c,width=w)
def dot(d,p,c='#b96848',r=5):d.ellipse((p[0]-r,p[1]-r,p[0]+r,p[1]+r),fill=c)
def RY(deg):
    a=math.radians(deg);c,s=math.cos(a),math.sin(a);return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def RX(deg):
    a=math.radians(deg);c,s=math.cos(a),math.sin(a);return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def rnd(p):return np.round(p,4).tolist()
MEASURE={'crown_no_cowlick':[324,64],'chin':[324,224],'neck_base':[324,266],
 'shoulder_R':[269,292],'elbow_R':[239,423],'wrist_R':[210,529],'tip_R':[209,590],
 'shoulder_L':[379,292],'elbow_L':[409,423],'wrist_L':[438,529],'tip_L':[439,590]}
H=160;HS=640;SCALE=.67;TX,TY=600,90
LU=math.dist(MEASURE['shoulder_R'],MEASURE['elbow_R'])*4
LF=math.dist(MEASURE['elbow_R'],MEASURE['wrist_R'])*4
LH=math.dist(MEASURE['wrist_R'],MEASURE['tip_R'])*4
BODY={'neck_base':[0,938,0]}
for side,sign in [('R',-1),('L',1)]:
    sh=np.array([sign*220,1042,0.]);el=sh+np.array([sign*120,math.sqrt(LU**2-120**2-30**2),30])
    wr=el+np.array([sign*60,math.sqrt(LF**2-60**2-90**2),90]);tip=wr+np.array([sign*20,math.sqrt(LH**2-20**2-30**2),30])
    BODY.update({f'shoulder_{side}':sh,f'elbow_{side}':el,f'wrist_{side}':wr,f'tip_{side}':tip})
OCC=np.array([0.,770,-65]);PIVOT=np.array([0.,1380,0]);CENTER=np.array([512.,0,0])
HEAD={'head_center':[0,450,0],'crown':[0,130,0],'chin':[0,770,145],
 'ear_R':[-265,535,0],'ear_L':[265,535,0],'root_R':[-250,610,-45],'root_L':[250,610,-45],
 'eye_R':[-116,470,230],'eye_L':[116,470,230],'nose':[0,530,285],'mouth':[0,625,245]}
# f,yaw,pitch,torso,eye,smile,ocular_yaw,ocular_pitch,tail_lag,gaze,title,note
ROWS=[
 (0,-30,1,-18,.96,0,-8,7,0,'puppet','看咬嘴结果','仍看画左偏下龟鹤结果；清醒，闭口未得意。'),
 (6,-30,1,-18,.96,0,12,-4,0,'transition','眼先向奶奶侧','只启动右上眼内视线，整头/身体与d01同位；尚未对准奶奶。'),
 (9,-14,0,-18,.96,.1,14,-5,-8,'transition','整头开始回看','颅体、两耳、后脑、发根和颈面一起转；肩暂留。'),
 (12,6,-1,-16,.96,.2,14,-5,-16,'transition','整头过正面','鼻跨正面；头的近远耳/辫关系交换，身体近远臂不交换。'),
 (15,26,-2,-12,.94,.45,10,-5,-24,'grandma','视线接住奶奶','看画右上画外奶奶；嘴角开始提，颈根/领口带少量肩跟。'),
 (19,39,-3,-8,.92,.7,5,-4,-20,'grandma','回看基本到位','头先到、胸肩小跟；自由尾端向画左滞后，根不漂。'),
 (24,41,-5,-4,.86,1,4,-4,-10,'grandma','得意的小抬颏','闭口小笑与轻提眉，清醒目光；不是困倦/眨眼/哈哈大笑。'),
 (32,39,-3,-4,.85,1,5,-4,0,'grandma','头回落尾落定','头轻回约2度，自由马尾完成内收回落；目光仍落奶奶。'),
 (40,39,-2,-4,.90,.92,5,-4,0,'grandma','得意看奶奶停住','眼略放松但不躲开，闭口笑稳定到F059，不加新手势。')]
def shot(p):return np.array([TX+SCALE*p[0],TY+SCALE*p[1]])
def geometry(row):
    f,yaw,pitch,torso,eye,smile,oy,op,lag,gaze,title,note=row
    B=RY(torso);Q=RY(yaw)@RX(-pitch)
    body={n:B@(np.array(p)-PIVOT)+PIVOT+CENTER for n,p in BODY.items()}
    occ=B@(OCC-PIVOT)+PIVOT+CENTER
    hp=lambda p:occ+Q@(np.array(p)-OCC)
    points={**body,'occipital':occ,**{n:hp(p)for n,p in HEAD.items()}}
    for side,sign in [('R',-1),('L',1)]:points[f'tail_{side}']=points[f'root_{side}']+np.array([sign*45+lag,245,-30])
    return points,hp,Q
KEYS=[]
for i,row in enumerate(ROWS):
    pts,_,_=geometry(row);f,yaw,pitch,torso,eye,smile,oy,op,lag,gaze,title,note=row;end=ROWS[i+1][0] if i+1<len(ROWS) else 60
    KEYS.append({'id':f'd{i+1:02}','f':f,'hold':end-f,'end_inclusive':end-1,'t':f/24,'title':title,'note':note,
     'head_yaw_deg':yaw,'head_pitch_deg':pitch,'torso_yaw_deg':torso,'eye_open_fraction':eye,'closed_mouth_smile':smile,'mouth_aperture_H':0,
     'ocular_yaw_design_deg':oy,'ocular_pitch_design_deg':op,'gaze':gaze,'tail_lag_source_px':lag,
     'head_frontmost_ear':'ear_R'if yaw>0 else'ear_L','torso_frontmost_arm':'L',
     'joints_3d_source':{n:rnd(p)for n,p in pts.items()},'joints_source_xy':{n:rnd(p[:2])for n,p in pts.items()},'joints_shot_xy':{n:rnd(shot(p))for n,p in pts.items()},
     'hidden_construction_landmarks':[n for n in pts if n.startswith(('elbow_','wrist_','tip_'))],
     'hands_visible':False,'contact_visible':False,'status':'CONSTRUCTION_PROPOSAL_NOT_DRAWING_PENDING_ASTRA_FREEZE'})
PLAN={'shot':'S24','base_commit':'001c9c1828d9054675437111cf52df37c48721f2','fps':24,'duration_s':2.5,'frames':60,'drawing_count':9,
 'status':'REFERENCE_ONLY_PENDING_FREEZE_NO_IMAGEGEN','canvas_source':[1024,1536],'shot_canvas':[1920,1080],
 'placement_proposal':{'scale':SCALE,'translation':[TX,TY],'source_crop_y':(1080-TY)/SCALE,'head_H_shot_px':HS*SCALE,'caveat':'由代码接触表F000缩略图估计景别，约±18场景像素；不是源高分辨率像素注册，母态实际再审。'},
 'inherited_scene_interface':{'source_module':'js/lamp/shots/s24.js','world_camera':{'pos':[3.15,1.62,1.12],'target':[1.80,.62,.98],'hfov':46},'scene_exposure':.22,'fog':.5,'old_card':{'world_pos':[1.98,.78],'ox':379,'oy':1513,'scale':18.4,'z0':.47},'note':'只保存机位/灯光/时长接口。旧图flip及整图旋转/点头不作为新表演；2D画布提案还须与此世界相机接景核注册。'},
 'head_unit_identity_px':H,'head_unit_source_px':HS,'identity_master':'collab/refs/xiaoman_turnaround_v4_draft.png','identity_landmarks_manual_px':MEASURE,
 'measurement_caveat':'冠顶/下颏人工约±3px；袖下肩肘估计±8px、腕±4px。画外肢体是骨长尺架，不声称S22末实际握姿已冻结。',
 'bone_reference':{'upper_arm':{'identity_px':LU/4,'H':LU/HS,'source_px':LU},'forearm':{'identity_px':LF/4,'H':LF/HS,'source_px':LF},'hand_envelope':{'identity_px':LH/4,'H':LH/HS,'source_px':LH}},
 'head_model':{'skull_radii_source':[270,320,235],'local_occipital':OCC.tolist(),'note':'同一3D颅体旋转投影；每张实际画稿必须重画，不准把此几何或旧x24整图变形成图。'},
 'gaze_targets_shot':{'puppet_result':[360,900],'grandma_eye_offscreen':[2100,280],'transition':'仅向奶奶侧启动，F015才接住；眼相对头转不超过14度设计值。'},
 'coordinate_convention':'source x right,y down,z toward viewer;positive yaw nose screen-right;negative pitch raises chin;R/L are character anatomical sides',
 'body_layer_order':['far_arm_R','torso','near_arm_L'],'head_depth_rule':'头过正面后耳和辫的近远交换；胸yaw保持负值，近臂L不交换。',
 'offscreen_contact_rule':'不沿用旧x24空手合拢。保持上场握签子的连续性，但两手/肘/杆握点都在画外；此处只有尺架，S22末握姿接口由协调另核，不临时加可见手或接触。',
 'color_rule':'S13动作节奏获认可但累积色漂已被Opus退回；后态x13只借结构。S24固定身份与F000色基准，不继承变浅头发/变白皮肤/变艳裙色。',
 'keys':KEYS}
put(P/'geometry/S24_reference_plan.json',PLAN)
with(P/'exposure.csv').open('w',newline='')as f:
    w=csv.writer(f,lineterminator='\n');w.writerow(['id','start','hold','end_inclusive','time_s','beat','head_yaw','head_pitch','torso_yaw','gaze','note'])
    for k in KEYS:w.writerow([k['id'],k['f'],k['hold'],k['end_inclusive'],k['t'],k['title'],k['head_yaw_deg'],k['head_pitch_deg'],k['torso_yaw_deg'],k['gaze'],k['note']])
def construction(i):
    row=ROWS[i];k=KEYS[i];pts,hp,Q=geometry(row);q=lambda n:tuple(shot(pts[n]));h=lambda p:tuple(shot(hp(p)))
    im=Image.new('RGB',(1920,1080),'#f4f2ec');d=ImageDraw.Draw(im)
    # Arms are spatial labels; hidden points never masquerade as visible joints.
    for side,c in [('R','#d4dadd'),('L','#657987')]:
        sh,el=q('shoulder_'+side),q('elbow_'+side);d.line([sh,el],fill=c,width=76)
    sn,sf=q('shoulder_L'),q('shoulder_R');nb=q('neck_base');occ=q('occipital')
    torso=[(sf[0]-40,sf[1]),(nb[0]-90,nb[1]+20),(nb[0]+90,nb[1]+20),(sn[0]+40,sn[1]),(sn[0]+60,1120),(sf[0]-60,1120)]
    d.polygon(torso,fill='#aab7bf',outline='#4d5d67',width=3)
    d.line([q('shoulder_L'),q('elbow_L')],fill='#657987',width=72)
    near=k['head_frontmost_ear'][-1];far='L'if near=='R'else'R'
    for side,c in [(far,'#c4ccd0'),(near,'#6e8290')]:
        r,t=q('root_'+side),q('tail_'+side);d.line([r,t],fill=c,width=46);dot(d,r);dot(d,t)
    d.polygon([(occ[0]-40,occ[1]-10),(occ[0]+40,occ[1]-10),(nb[0]+45,nb[1]+35),(nb[0]-45,nb[1]+35)],fill='#d4d3cc',outline='#687983',width=3)
    d.arc((nb[0]-65,nb[1]+5,nb[0]+65,nb[1]+50),0,180,fill='#596e7b',width=3)
    hc=pts['head_center'];C=Q@np.diag([270**2,320**2,235**2])@Q.T;vals,V=np.linalg.eigh(C[:2,:2]);E=V@np.diag(np.sqrt(vals))
    outline=[tuple(shot(hc+np.r_[E@np.array([math.cos(t),math.sin(t)]),0]))for t in np.linspace(0,2*math.pi,120)]
    d.polygon(outline,fill='#e0e1de',outline='#536975',width=4)
    face=[h(p)for p in[(-205,470,150),(-200,620,195),(-120,740,170),(0,770,145),(120,740,170),(200,620,195),(205,470,150)]]
    d.polygon(face,fill='#edece6',outline='#77838a',width=3)
    for side in [far,near]:
        e=q('ear_'+side);r=16 if side==near else 10;d.ellipse((e[0]-r,e[1]-27,e[0]+r,e[1]+27),outline='#626f78',width=3)
        if side==far:dash(d,(e[0]-18,e[1]-34),(e[0]+18,e[1]+34))
    centerline=[h([0,y,245])for y in[300,420,530,625,740]]
    for a,b in zip(centerline,centerline[1:]):dash(d,a,b,'#9b9486',2)
    for side in ['R','L']:
        e=q('eye_'+side);eh=17*k['eye_open_fraction'];ew=24*math.cos(math.radians(k['head_yaw_deg']))
        d.ellipse((e[0]-ew,e[1]-eh,e[0]+ew,e[1]+eh),fill='white',outline='#53616a',width=2)
        px=e[0]+k['ocular_yaw_design_deg']*.5;py=e[1]+k['ocular_pitch_design_deg']*.45;d.ellipse((px-7,py-10,px+7,py+10),fill='#52616b')
        s=k['closed_mouth_smile'];d.line([(e[0]-ew,e[1]-37),(e[0],e[1]-43-s*4),(e[0]+ew,e[1]-37-s*3)],fill='#596a74',width=3)
    n=q('nose');d.line([(n[0]-5,n[1]-12),n,(n[0]+7,n[1])],fill='#687780',width=3)
    smile=k['closed_mouth_smile'];mouth=[h([x,625+10*smile*(1-(x/55)**2)-3*smile*x/55,245])for x in np.linspace(-55,55,25)];d.line(mouth,fill='#596a74',width=3)
    for name in ['occipital','neck_base','head_center','shoulder_R','shoulder_L']:dot(d,q(name),r=5)
    dash(d,q('head_center'),occ,'#b27151',3);dash(d,occ,nb,'#b27151',3)
    mid=(np.array(q('eye_R'))+np.array(q('eye_L')))/2
    if k['gaze']=='puppet':arrow(d,mid,(360,900));text(d,(80,895),'幕边龟鹤结果 / 画左偏下',27)
    elif k['gaze']=='transition':arrow(d,mid,mid+[130,-75]);text(d,(1300,290),'眼向右上启动，尚未接住奶奶',26)
    else:arrow(d,mid,(1860,300));text(d,(1450,230),'奶奶眼线 → 画右上画外',28);text(d,(1450,270),'目标(2100,280)是待冻设计点',22)
    text(d,(28,18),'S24 构造参考 · 非画稿 · 待Astra冻结',32,'#a75c40')
    text(d,(28,65),f"{k['id']} F{k['f']:03}×{k['hold']} · {k['title']}",28)
    text(d,(30,1010),'近臂L深 / 躯干中 / 远臂R浅；肘腕手画外。颅体/耳/发根/颈面一起重画。',25)
    return im
cards=[]
for i,k in enumerate(KEYS):
    im=construction(i);card=Image.new('RGB',(1440,1120),'#f4f2ec');card.paste(im.resize((1440,810)),(0,0));d=ImageDraw.Draw(card)
    text(d,(25,835),f"头yaw {k['head_yaw_deg']}° / pitch {k['head_pitch_deg']}°；胸 {k['torso_yaw_deg']}°；闭口笑 {k['closed_mouth_smile']}",26)
    text(d,(25,890),k['note'],24);text(d,(25,950),'角度/点位为构造目标，不是成图测量；虚线/画外点不是可见肢体。',24)
    text(d,(25,1020),'灰形不可剪进成片；无生图、无角色成图、无场景渲染。',26,'#a75c40')
    card.save(P/f"reference/S24_{k['id']}_F{k['f']:03}_construction.png");cards.append(im)
sheet=Image.new('RGB',(1920,1240),'#f0eee7');d=ImageDraw.Draw(sheet);text(d,(25,10),'S24 / 9态60帧 / 看结果 → 回头接住奶奶 → 得意停住 / 构造非画稿',30)
for i,(im,k)in enumerate(zip(cards,KEYS)):
    x=i%3*640;y=65+i//3*390;sheet.paste(im.resize((630,355)),(x+5,y));text(d,(x+10,y+355),f"F{k['f']:03}×{k['hold']} {k['title']}",22)
sheet.save(P/'reference/00_all9_construction.jpg',quality=96)
# Actual identity calibration: points on real artwork, estimates explicitly distinguished.
im=Image.open(ROOT/'collab/refs/xiaoman_turnaround_v4_draft.png').convert('RGB');im=im.crop((150,20,500,680)).resize((700,1320));sheet=Image.new('RGB',(1600,1400),'#f4f2ec');sheet.paste(im,(20,50));d=ImageDraw.Draw(sheet)
for n,p in MEASURE.items():
    q=((p[0]-150)*2+20,(p[1]-20)*2+50);dot(d,q,'#b96848',5);text(d,(q[0]+8,q[1]-10),n+(' 估'if n.startswith(('shoulder','elbow','wrist'))else''),16)
for side in ['R','L']:
    p=[((MEASURE[n+'_'+side][0]-150)*2+20,(MEASURE[n+'_'+side][1]-20)*2+50)for n in['shoulder','elbow','wrist','tip']]
    for a,b in zip(p,p[1:]):dash(d,a,b,'#b96848',3)
text(d,(30,10),'实际身份图测点 / 不是代码人物 / 不是人体扫描',27)
notes=[f'H=160px：实心发顶64 → 下颏224（不计呆毛）',f'上臂 {LU/4:.3f}px = {LU/HS:.4f}H',f'前臂 {LF/4:.3f}px = {LF/HS:.4f}H',f'手包络 {LH/4:.3f}px = {LH/HS:.4f}H','肩骨宽110px = .6875H','袖下肩/肘估计±8px；腕±4px','冠顶/下颏人工读数约±3px','源画布H640；场景约428.8px','画稿提案1024×1536，整体 .67+(600,90)','肘/腕/手均出最终1080下边，不临时补手','本尺架不冻结S22末画外握签子姿势','骨长固定；投影短缩与长度变化分清']
for i,s in enumerate(notes):text(d,(760,100+i*76),s,25)
sheet.save(P/'reference/01_identity_bone_calibration.jpg',quality=97)
# Full hidden-arm ruler and layer/contact semantics.
sheet=Image.new('RGB',(1800,1300),'#f4f2ec');d=ImageDraw.Draw(sheet);text(d,(25,15),'层次/接触/画外骨长尺架 · 虚线均为构造，不是可见动作',30)
pts,_,_=geometry(ROWS[0]);mapping=lambda p:(520+(p[0]-512)*.45,80+p[1]*.45)
for side,c in [('R','#b7c3c9'),('L','#526d7d')]:
    names=[n+'_'+side for n in['shoulder','elbow','wrist','tip']];q=[mapping(pts[n])for n in names]
    for a,b in zip(q,q[1:]):dash(d,a,b,c,6)
    for n,a in zip(names,q):dot(d,a,c,7);text(d,(a[0]+12,a[1]-12),n+' 构造',21)
cut=80+((1080-TY)/SCALE)*.45;d.line((90,cut,940,cut),fill='#a96b47',width=3);text(d,(70,cut-35),'最终画幅下边；以下肘/腕/手均画外',24,'#a96b47')
text(d,(1020,120),'身体：远臂R → 躯干 → 近臂L',28);text(d,(1020,180),'胸yaw −18°→−4°，身体近远不交换',25)
text(d,(1020,270),'头：近耳L → 正面 → 近耳R',28);text(d,(1020,330),'耳、后脑、发根、颈面须同转',25)
text(d,(1020,430),'无可见接触：不画捂嘴或合手',28);text(d,(1020,490),'旧x24双手合拢不能沿用；签子握点',25);text(d,(1020,535),'画外连续性由协调对S22末核定。',25)
text(d,(1020,640),'头先稳，尾自由端后回落',28);text(d,(1020,700),'F019到位 → F024轻抬颏 → F032收尾',25)
text(d,(1020,800),'灯/幕/龟鹤仍由原场景负责',28);text(d,(1020,860),'本次不画新道具或改光/影的落点。',25)
sheet.save(P/'reference/02_layers_hidden_arms_contact.jpg',quality=96)
# Real style/structure sources, composited correctly but never altered into poses.
paths=['collab/refs/anim_24_xiaoman_smug.png','assets/chars/x13/F000.png','assets/chars/x13/F087.png','assets/chars/x13/F094.png']
labels=['旧x24：仅身份/得意倾向；不沿用合手','x13 F000：固定色基准，仅做色/身份核对','x13 F087：整头结构例，后态色漂已退回','x13 F094：耳根颈连体例，颜色不沿用']
sheet=Image.new('RGB',(1920,1030),'#f4f2ec');d=ImageDraw.Draw(sheet)
for i,(s,label)in enumerate(zip(paths,labels)):
    im=Image.open(ROOT/s).convert('RGBA');bg=Image.new('RGBA',im.size,(222,225,226,255));bg.alpha_composite(im);im=bg.convert('RGB');im.thumbnail((450,880));sheet.paste(im,(i*480+15,75));text(d,(i*480+12,20),label,19)
text(d,(25,970),'来源均已实际查看；x24只作身份，x13后态只借整头结构。S13目前待语义修色，不称最终成片已过。',24,'#a75c40')
sheet.save(P/'reference/03_actual_identity_and_structure_sources.jpg',quality=96)
# Semantic reference chips from the fixedF000 only. Diagnostics do not alter any art.
im=Image.open(ROOT/'assets/chars/x13/F000.png').convert('RGBA');arr=np.array(im);chips=[]
regions=[('hair',[260,260,520,500]),('skin',[530,540,730,730]),('dress_yellow',[300,1120,650,1300]),('collar_white',[360,1000,680,1120])]
for name,roi in regions:
    a=arr[roi[1]:roi[3],roi[0]:roi[2]];r,g,b,alpha=[a[:,:,i].astype(int)for i in range(4)];mask=alpha>=250
    if name=='hair':mask&=(r>20)&(r<160)&(g<110)&(b<100)&(r>g)
    elif name=='skin':mask&=(r>180)&(g>110)&(b>70)&(r>g+15)&(g>b)
    elif name=='dress_yellow':mask&=(r>180)&(g>140)&(b<110)
    else:mask&=(np.minimum(np.minimum(r,g),b)>200)&(np.maximum(np.maximum(r,g),b)-np.minimum(np.minimum(r,g),b)<40)
    assert mask.sum()>80,(name,int(mask.sum()))
    rgb=np.median(a[:,:,:3][mask],axis=0).round().astype(int).tolist();chips.append({'semantic_region':name,'source_roi':roi,'opaque_selected_pixels':int(mask.sum()),'median_RGB':rgb})
put(P/'provenance/F000_semantic_color_reference.json',{'source':'assets/chars/x13/F000.png','source_sha256':sha(ROOT/'assets/chars/x13/F000.png'),'method':'Explicit source ROIs and semantic color selection for reference statistics only; no art edits.','use':'Compare like semantic interiors after generation. Do not compare whole-image means across poses or force every shaded pixel to a flat chip.','later_x13_palette_rejected':True,'chips':chips})
sheet=Image.new('RGB',(1600,640),'#f4f2ec');d=ImageDraw.Draw(sheet);text(d,(25,20),'固定F000语义色参照 / 不使用S13后态漂移色 / 不修改原图',30)
for i,row in enumerate(chips):
    x=30+i*390;d.rectangle((x,120,x+330,330),fill=tuple(row['median_RGB']));text(d,(x,355),row['semantic_region'],26);text(d,(x,405),'RGB '+str(row['median_RGB']),24);text(d,(x,455),'ROI '+str(row['source_roi']),20)
text(d,(25,550),'色片只是同语义内区统计，不是所有明暗像素的平涂目标；实际母态与F000逐区自审。',25)
sheet.save(P/'reference/04_F000_semantic_color_reference.jpg',quality=97)
# No executed tool calls: retain an explicit zero ledger and all fixed-source attribution.
source_paths=['collab/README.md','collab/claude.md','collab/partner.md','docs/preproduction/script-v3.md','docs/keyframes/scenes03_12_drawing_plan.md','js/lamp/shots/s24.js','collab/refs/xiaoman_turnaround_v4_draft.png','collab/refs/xiaoman_expressions_current03.png','assets/chars/x24_smug.png',*paths,'collab/keyposes/20261018_scenes03_12/S24/S24_code_F000-F046.jpg','collab/keyposes/20261018_scenes03_12/S24/S24_code_F048-F058.jpg']
sources=[]
for s in source_paths:
    p=ROOT/s;row={'path':s,'sha256':sha(p),'git_blob':subprocess.check_output(['git','rev-parse',PLAN['base_commit']+':'+s],cwd=ROOT,text=True).strip(),'fixed_commit':PLAN['base_commit']}
    if p.suffix in['.png','.jpg']:
        with Image.open(p)as im:row.update(size=list(im.size),mode=im.mode)
    sources.append(row)
put(P/'provenance/source_manifest.json',{'sources':sources,'code_use':'camera/lighting/duration only; no legacy figure action adopted','S13_color_status':'motion accepted; accumulated palette drift rejected, pending correction;later x13 samples structure-only'})
if not (P/'provenance/generation_ledger.json').exists():
    put(P/'provenance/generation_ledger.json',{'stage':'reference_only_pending_Astra_freeze','image_generation_requests':0,'successful_raw_images':0,'adopted_production_drawings':0,'scene_render_runs':0,'full_film_render_runs':0,'external_paid_service_or_API_calls':0})
bone_errors={};hidden=True
for k in KEYS:
    j=k['joints_3d_source']
    for side in['R','L']:
        for name,a,b,L in[('upper','shoulder','elbow',LU),('forearm','elbow','wrist',LF),('hand','wrist','tip',LH)]:bone_errors[name]=max(bone_errors.get(name,0),abs(math.dist(j[a+'_'+side],j[b+'_'+side])-L))
    hidden&=all(k['joints_shot_xy'][n][1]>1080 for n in k['hidden_construction_landmarks'])
assert len(KEYS)==9 and sum(k['hold']for k in KEYS)==60 and all(a['f']+a['hold']==b['f']for a,b in zip(KEYS,KEYS[1:]))
assert hidden and max(bone_errors.values())<.001 and max(abs(k['head_yaw_deg']-k['torso_yaw_deg'])for k in KEYS)<=50
result={'status':'PASS_CONSTRUCTION_ONLY','frames':60,'keys':9,'fps':24,'duration':2.5,'all_holds_contiguous':True,'all_hidden_elbows_wrists_hands_outside_frame':hidden,'max_bone_drift_source_px':bone_errors,'head_vs_torso_max_design_twist_deg':max(abs(k['head_yaw_deg']-k['torso_yaw_deg'])for k in KEYS),'ocular_yaw_design_max_deg':max(abs(k['ocular_yaw_design_deg'])for k in KEYS),'imagegen_calls':0,'not_production_art':True}
put(P/'qa/construction_validation.json',result);print(json.dumps(result,ensure_ascii=False,indent=2))
