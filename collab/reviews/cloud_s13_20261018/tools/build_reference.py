#!/usr/bin/env python3
"""S13 construction references, never production drawings. No generation or render API.
Run from repository root. All generated files stay in this review directory.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import csv, hashlib, json, math, subprocess

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parents[1]
FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
BOLD = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def font(n, bold=False): return ImageFont.truetype(BOLD if bold else FONT, n)
def save_json(p, obj): p.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')
def txt(d, xy, s, n=24, fill='#24313a', bold=False): d.text(xy,s,font=font(n,bold),fill=fill)
def line(d, pts, fill='#526978', width=3): d.line(pts,fill=fill,width=width,joint='curve')
def dash(d,a,b,fill='#73818b',width=2):
    dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
    for t in range(0,int(length),14):
        u=t/max(length,1); v=min(t+7,length)/max(length,1)
        d.line((a[0]+u*dx,a[1]+u*dy,a[0]+v*dx,a[1]+v*dy),fill=fill,width=width)
def arrow(d,a,b,fill='#386b8c',width=3):
    line(d,[a,b],fill,width); t=math.atan2(b[1]-a[1],b[0]-a[0])
    for q in (-.45,.45):
        line(d,[b,(b[0]-17*math.cos(t+q),b[1]-17*math.sin(t+q))],fill,width)
def dot(d,p,r=5,fill='#ce6843'): d.ellipse((p[0]-r,p[1]-r,p[0]+r,p[1]+r),fill=fill)
def ry(p, a):
    a=math.radians(a); x,y,z=p
    return (x*math.cos(a)+z*math.sin(a),y,-x*math.sin(a)+z*math.cos(a))
def rx(p,a):
    a=math.radians(a); x,y,z=p
    return x,y*math.cos(a)-z*math.sin(a),y*math.sin(a)+z*math.cos(a)
def rnd(p): return [round(x,3) for x in p]

# Manual, repeatable landmark selection on the identity drawing, NOT a code puppet.
MEASURE = {'crown_no_cowlick':[324,64], 'chin':[324,224], 'neck_base':[324,266],
           'shoulder_near':[269,292], 'elbow_near':[239,423], 'wrist_near':[210,529],
           'finger_tip_near':[209,590], 'shoulder_far':[379,292],
           'elbow_far':[409,423], 'wrist_far':[438,529], 'finger_tip_far':[439,590]}
H = 160
BASE = {k:[(v[0]-324)*4,(v[1]-64)*4+232,0] for k,v in MEASURE.items()}
PIVOT = [524,1370,0]   # lower sternum; outside final crop, not an immutable pixel anchor
SHOTSCALE=.85
def bodypoint(name, yaw, dy):
    p=BASE[name]; v=ry((p[0],p[1]-PIVOT[1],0),yaw)
    return [v[0]+524,v[1]+PIVOT[1]+dy,v[2]]
def shot(p): return [330+SHOTSCALE*p[0],-30+SHOTSCALE*p[1]]

# Frame starts are independently designed. Positive yaw looks toward screen right;
# negative pitch raises the chin. Absolute torso yaw stays +12..+4, so near arm stays near.
ROWS = [
 (0,35,0,12,0,1.00,.025,'crane',0,'看鹤看入神','视线画右偏下；嘴轻启；并非困倦。'),
 (18,35,0,12,0,1.00,.025,'grandma',0,'先发现视线','只改眼内视线到画右偏上；整头、身体保持 d01。'),
 (24,42,0,12,0,1.05,.010,'grandma',0,'确认奶奶在看','整头向奶奶多转约 7°；耳、后脑和发根一起转。'),
 (30,42,0,12,0,1.04,.000,'grandma',0,'被看见的一顿','嘴收住，眉轻提；保持清醒的对视，不抢先闭眼。'),
 (36,40,-1,12,-2,.65,.010,'grandma',0,'决定装困','故意垂眼；上胸随吸气微起；不要直接跳到哈欠峰态。'),
 (40,37,-3,12,-4,.35,.035,'none',0,'哈欠起势','嘴先小开，下颌开始落；头与颈面连贯微后仰。'),
 (44,32,-6,11,-8,.10,.075,'none',4,'哈欠张开','眼将闭，真正张下颌；不是纵向拉伸嘴贴图。'),
 (50,28,-9,10,-12,.00,.120,'none',8,'假哈欠峰态','下颌下降 0.055H；额头颅体尺寸不变；胸肩同起。'),
 (58,28,-9,10,-9,.00,.105,'none',3,'峰态续气','保持哈欠但口腔略收、胸轻回，需独立画，不能用同图缩嘴。'),
 (68,24,-5,10,-5,.08,.065,'none',0,'哈欠收束','下颌回收、头回前；胸肩整体回落。'),
 (78,18,-1,10,0,.22,.018,'none',0,'收口后准备扭开','嘴将合；仍未转到画左；让假困和回避读成两件事。'),
 (84,8,0,10,2,.38,.005,'away',0,'回避起转','眼缝先向画左，头通过接近正面；肩尚未追上。'),
 (87,-6,0,8,3,.40,.000,'away',12,'转头中间一','整头越过正面；两耳露出比例交换，颈面重画。'),
 (90,-23,1,6,5,.38,.000,'away',23,'转头中间二','鼻朝画左；胸肩小幅跟转，不能只替换脸。'),
 (94,-36,1,4,6,.32,.000,'away',25,'扭开到位','头比胸多转约 40°；马尾自由端向画右滞后，不拉长发根。'),
 (104,-33,1,4,6,.30,.000,'away',0,'轻回落停住','头回落约 3°，马尾末端落定；闭嘴装作没事。')
]
KEYS=[]
for i,row in enumerate(ROWS):
    f,yaw,pitch,ty,dy,eye,mouth,gaze,lag,title,note=row
    joints={k:bodypoint(k,ty,dy) for k in MEASURE if k not in ['crown_no_cowlick','chin']}
    # Occipital articulation moves with upper torso; head rotates about it as a volume.
    occ=[524,824+dy,0]
    def headp(p):
        v=ry(rx(p,-pitch),yaw)
        return [occ[j]+v[j] for j in range(3)]
    head=headp((0,-272,0))
    lm={'head_center':head,'occipital_joint':occ,'nose':headp((0,-96,285)),
        'mouth_center':headp((0,-48,255)), 'chin':headp((0,48+mouth/.12*35.2,145)),
        'ear_near':headp((-294,-136,0)), 'ear_far':headp((294,-136,0)),
        'eye_near':headp((-116,-192,230)), 'eye_far':headp((116,-192,230)),
        'hair_root_near':headp((-275,-68,-40)), 'hair_root_far':headp((275,-68,-40))}
    lm['tail_near']=[lm['hair_root_near'][0]-45+lag,lm['hair_root_near'][1]+288,lm['hair_root_near'][2]-25]
    lm['tail_far']=[lm['hair_root_far'][0]+45+lag,lm['hair_root_far'][1]+288,lm['hair_root_far'][2]-25]
    joints.update(lm)
    end=ROWS[i+1][0] if i+1<len(ROWS) else 120
    KEYS.append({'id':f'd{i+1:02}', 'f':f,'hold':end-f,'end_inclusive':end-1,'t':round(f/24,6),
                 'head_yaw_deg':yaw,'head_pitch_deg':pitch,'torso_yaw_deg':ty,'upper_body_dy_source_px':dy,
                 'eye_open_fraction':eye,'mouth_aperture_H':mouth,'gaze_target':gaze,
                 'tail_lag_source_px':lag,'title':title,'note':note,
                 'joints_3d_source':{k:rnd(v) for k,v in joints.items()},
                 'joints_source_xy':{k:rnd(v[:2]) for k,v in joints.items()},
                 'joints_shot_xy':{k:rnd(shot(v)) for k,v in joints.items()},
                 'head_frontmost_ear_landmark':'ear_near' if yaw>=0 else 'ear_far',
                 'hair_depth_note':'头朝向过正面后，近/远耳与辫的可见性交换；身体近/远臂不交换。near/far 点名保留初态身份。',
                 'hands_visible':False,'hand_mouth_contact':False,'status':'reference_pending_Astra_freeze'})

LENGTHS={}
for name,a,b in [('upper_arm','shoulder_near','elbow_near'),('forearm','elbow_near','wrist_near'),
                 ('hand_envelope','wrist_near','finger_tip_near')]:
    n=math.dist(MEASURE[a],MEASURE[b]);LENGTHS[name]={'identity_px':round(n,3),'H':round(n/H,4),'source_px':round(n*4,3)}
PLAN={'shot':'S13','status':'REFERENCE ONLY / NOT FROZEN / NO GENERATED DRAWINGS',
      'base_commit':'3d66443997cee24b64059e6f53f7d46968a3a05c','fps':24,'duration_s':5,'frames':120,
      'drawing_count':16,'canvas_source':[1024,1536],'shot_canvas':[1920,1080],
      'placement_proposal':{'scale':.85,'translation':[330,-30], 'source_crop_y_at_shot_bottom':(1080+30)/.85,
                            'note':'继承旧镜机位的提案，非已冻结接口；画稿整体等比，不单拉头脸。'},
      'coordinate_convention':'source x right, y down; orthographic z toward camera; +yaw nose right; -pitch chin up',
      'identity_master':'collab/refs/xiaoman_turnaround_v4_draft.png',
      'style_only':['collab/refs/anim_13_xiaoman_stare.png','collab/refs/anim_13_xiaoman_yawn.png'],
      'identity_landmarks_manual_px':MEASURE,'head_unit_identity_px':H,'head_unit_source_px':640,
      'measurement_caveat':'冠顶/下颏约±3px；袖下肩肘关节估计±8px，腕约±4px。不是实测人体三维扫描；固定三维模型为绘图构造提案。',
      'bone_reference':LENGTHS,'hidden_arm_note':'骨长保持；投影可缩短。肘、腕、手全程在最终画幅外；虚线表示画外构造，不指示手从躯干穿出。',
      'layers_back_to_front':['far_arm','torso_and_dress','neck_then_whole_head','near_arm'],
      'hair_layers':'头部耳/发根/马尾按各态 z 深度排序；过正面后头的近远关系交换，不能绑定躯干近/远臂命名。',
      'contact_policy':'本版没有手嘴接触或持物；若冻后增加捂嘴须新交肩肘腕掌完整路径及近图，不能临时生一只悬手。',
      'timelineFrames':[[k['f'],i] for i,k in enumerate(KEYS)],'keys':KEYS}
save_json(OUT/'geometry/S13_reference_plan.json',PLAN)

with (OUT/'exposure.csv').open('w',newline='') as f:
    w=csv.writer(f,lineterminator='\n'); w.writerow(['id','start_frame','hold_frames','end_frame_inclusive','time_s','beat','head_yaw_deg','head_pitch_deg','torso_yaw_deg','gaze','note'])
    for k in KEYS:w.writerow([k['id'],k['f'],k['hold'],k['end_inclusive'],k['t'],k['title'],k['head_yaw_deg'],k['head_pitch_deg'],k['torso_yaw_deg'],k['gaze_target'],k['note']])

def draw_construction(k, scale=.5):
    """Image is a labelled volume/landmark diagram, not a generated or finished character."""
    im=Image.new('RGB',(1920,1080),'#f5f3ed');d=ImageDraw.Draw(im)
    def q(p):return tuple(shot(p))
    def kp(n):return tuple(k['joints_shot_xy'][n])
    yaw=k['head_yaw_deg'];pitch=k['head_pitch_deg'];dy=k['upper_body_dy_source_px'];occ=[524,824+dy,0]
    def h(p):
        v=ry(rx(p,-pitch),yaw);return q([occ[j]+v[j] for j in range(3)])
    # Far arm and far tail first. Hidden paths remain dashed.
    sf=kp('shoulder_far');sn=kp('shoulder_near');nb=kp('neck_base')
    d.polygon([sf,(sf[0]+100,1080),(sf[0]-35,1080)],fill='#d8dde0')
    near_side='near' if yaw>=0 else 'far'; far_side='far' if yaw>=0 else 'near'
    for side in (far_side,near_side):
        r=kp('hair_root_'+side);t=kp('tail_'+side)
        line(d,[r,t], '#bfc6ca' if side==far_side else '#687985',34)
        dot(d,r,7,'#b36446');dot(d,t,6,'#b36446')
    torso=[(sn[0]-75,sn[1]),(nb[0]-110,nb[1]+25),(nb[0]+110,nb[1]+25),
           (sf[0]+75,sf[1]),(sf[0]+125,1080),(sn[0]-125,1080)]
    d.polygon(torso,fill='#adb8bf');line(d,torso+[torso[0]],'#4a5962',4)
    d.polygon([sn,(sn[0]-115,1080),(sn[0]+25,1080)],fill='#687985')
    # Neck joins into the collar opening; not a flat pasted head edge.
    nc=kp('occipital_joint')
    d.polygon([(nc[0]-57,nc[1]-25),(nc[0]+57,nc[1]-25),(nb[0]+75,nb[1]+5),(nb[0]-75,nb[1]+5)],fill='#e1d4c2')
    d.ellipse((nb[0]-110,nb[1]-15,nb[0]+110,nb[1]+50),outline='#4a5962',width=4)
    # Cranial envelope + explicitly separate facial/jaw volume.
    hc=kp('head_center');d.ellipse((hc[0]-265,hc[1]-276,hc[0]+265,hc[1]+230),fill='#e5e3dc',outline='#55616a',width=4)
    # Ear on the hidden side is drawn first. Do not enlarge near ear as yaw increases.
    for side in [far_side,near_side]:
        e=kp('ear_'+side);rw=12 if side==far_side else 29
        d.ellipse((e[0]-rw,e[1]-38,e[0]+rw,e[1]+38),fill='#d3c3ad',outline='#6a6259',width=3)
    openjaw=k['mouth_aperture_H']/.12*35.2
    face=[h(p) for p in [(-215,-410,140),(-245,-210,180),(-205,-65,180),(-125,30+openjaw,190),
                         (0,48+openjaw,145),(125,30+openjaw,190),(205,-65,180),(245,-210,180),(215,-410,140)]]
    d.polygon(face,fill='#f4e8d5');line(d,face+[face[0]],'#766c60',4)
    # The head centreline, eyes and nose turn as one volume.
    mid=[h((0,y,220)) for y in (-280,-210,-130,-48,125+openjaw)]
    for a,b in zip(mid,mid[1:]):dash(d,a,b,'#86979f',3)
    en=kp('eye_near');ef=kp('eye_far')
    for side,e in [('near',en),('far',ef)]:
        rw=37 if side==near_side else 29; eh=max(1,25*k['eye_open_fraction'])
        if k['eye_open_fraction']>.02:
            d.ellipse((e[0]-rw,e[1]-eh,e[0]+rw,e[1]+eh),fill='white',outline='#443f38',width=3)
            dx,ddy={'crane':(9,5),'grandma':(12,-5),'away':(-9,0),'none':(0,0)}[k['gaze_target']]
            rr=min(13,eh*.8);ddy=max(-eh+rr,min(eh-rr,ddy))
            d.ellipse((e[0]+dx-rr,e[1]+ddy-rr,e[0]+dx+rr,e[1]+ddy+rr),fill='#463d36')
        else:line(d,[(e[0]-rw,e[1]),(e[0],e[1]+5),(e[0]+rw,e[1])],'#443f38',4)
        line(d,[(e[0]-rw,e[1]-50),(e[0],e[1]-56),(e[0]+rw,e[1]-50)],'#5b5149',4)
    n=kp('nose');line(d,[(n[0]-7,n[1]-18),n,(n[0]+9,n[1]+3)],'#655b4f',4)
    m=kp('mouth_center'); mh=k['mouth_aperture_H']*544
    if mh>4:d.ellipse((m[0]-25,m[1]-mh/2,m[0]+25,m[1]+mh/2),fill='#76665c',outline='#51443b',width=3)
    else:line(d,[(m[0]-23,m[1]),(m[0]+23,m[1])],'#65564b',4)
    for name in ('head_center','occipital_joint','neck_base','shoulder_near','shoulder_far'):
        dot(d,kp(name),6)
    dash(d,kp('head_center'),kp('occipital_joint'),'#9d6347',3)
    dash(d,kp('occipital_joint'),kp('neck_base'),'#9d6347',3)
    if k['gaze_target'] in ('crane','grandma'):
        target=(1740,830) if k['gaze_target']=='crane' else (1740,330)
        arrow(d,((en[0]+ef[0])/2,(en[1]+ef[1])/2),target,'#467a96',3)
        txt(d,(target[0]-115,target[1]+20),'鹤 / 画右下' if k['gaze_target']=='crane' else '奶奶 / 画外右上',30)
    txt(d,(30,22),'构造参考 · 非画稿 · 未冻结',34,fill='#9d543a',bold=True)
    txt(d,(30,1020),'三档：深灰近臂 / 中灰躯干 / 浅灰远臂。手、肘、腕均在最终画幅外。',27)
    return im.resize((int(1920*scale),int(1080*scale)),Image.Resampling.LANCZOS)

cards=[]
for k in KEYS:
    im=Image.new('RGB',(1280,920),'#fbfaf6');d=ImageDraw.Draw(im)
    txt(d,(28,15),f"S13 {k['id']}  F{k['f']:03}–{k['end_inclusive']:03}  ×{k['hold']}帧  /  {k['title']}",32,bold=True)
    im.paste(draw_construction(k,.5),(20,80));d=ImageDraw.Draw(im)
    txt(d,(1000,100),'头向 / 胸向',22,bold=True)
    for y,s in [(145,f"头 yaw {k['head_yaw_deg']:+}°"),(190,f"俯仰 {k['head_pitch_deg']:+}°"),
                (235,f"胸 yaw {k['torso_yaw_deg']:+}°"),(300,f"眼开 {k['eye_open_fraction']:.0%}"),
                (345,f"口高 {k['mouth_aperture_H']:.3f}H"),(415,'无手嘴接触'),(460,'禁止贴脸变形')]:txt(d,(1000,y),s,22)
    txt(d,(28,650),k['note'],24)
    txt(d,(28,705),'固定颅体尺寸；下颌可开合；转头重画耳、发根、后脑与颈面。',25)
    txt(d,(28,755),'位置由 geometry/S13_reference_plan.json 追溯；角度为设计目标，非成图实测。',23)
    txt(d,(28,835),'参考构造示意，不能剪进成片。下一步：Astra 冻结后才生成首态。',25,fill='#9d543a',bold=True)
    p=OUT/f"reference/S13_{k['id']}_F{k['f']:03}_construction.png"; im.save(p)
    cards.append(im)

sheet=Image.new('RGB',(1920,1510),'#eeece5');d=ImageDraw.Draw(sheet)
txt(d,(24,10),'S13 / 16 曝光构造总览 / 120 帧 @24fps / 全部未冻结、非画稿',32,bold=True)
for i,(im,k) in enumerate(zip(cards,KEYS)):
    # Use the composition image at readable scale; titles remain separate.
    x=(i%4)*480;y=70+(i//4)*355
    sheet.paste(draw_construction(k,.24),(x,y+38))
    txt(d,(x+12,y),f"{k['id']}  F{k['f']:03} ×{k['hold']}  {k['title']}",19,bold=True)
    txt(d,(x+14,y+302),f"头 {k['head_yaw_deg']:+}° / 胸 {k['torso_yaw_deg']:+}° / {k['gaze_target']}",19)
sheet.save(OUT/'reference/00_all16_construction.jpg',quality=94)

# Calibration annotated over actual image pixels, with explicit uncertainty.
im=Image.new('RGB',(1700,1150),'#f8f6ef');d=ImageDraw.Draw(im)
txt(d,(24,18),'S13 比例标定 / 实际三视图测点 / 不是旧 x13 的动作端点',32,bold=True)
mother=Image.open(ROOT/'collab/refs/xiaoman_turnaround_v4_draft.png')
im.paste(mother.crop((165,28,465,982)).resize((600,1908)).resize((312,992)),(32,90))
d=ImageDraw.Draw(im)
def mp(p):return (32+(p[0]-165)*1.04,90+(p[1]-28)*1.04)
for n,p in MEASURE.items():dot(d,mp(p),5)
for side in ('near','far'):
    for a,b in [('shoulder','elbow'),('elbow','wrist'),('wrist','finger_tip')]:line(d,[mp(MEASURE[a+'_'+side]),mp(MEASURE[b+'_'+side])],'#bd6448',3)
arrow(d,mp((438,64)),mp((438,224)),'#477b94',3)
txt(d,(380,120),'H = 实心发顶 64 → 下颏 224 = 160px（约 ±3px）',27,bold=True)
for i,(name,data) in enumerate(LENGTHS.items()):
    txt(d,(380,190+i*62),f"{name}: {data['identity_px']:.1f}px = {data['H']:.3f}H；新母画布 ×4 = {data['source_px']:.1f}px",24)
for y,s in [(410,'骨架肩宽：110px = 0.688H；衣袖外宽不是肩骨宽。'),
            (463,'肩 / 肘在袖下，估计 ±8px；腕约 ±4px；不能假称精准解剖测量。'),
            (516,'三维构造保持骨长；二维投影随胸向变化，不为凑投影去伸缩上臂。'),
            (569,'头发顶至鞋底约 896px ≈ 5.6H（呆毛不算头高）。'),
            (622,'S13 画布 1024×1536；H=640px；场景等比 .85 → H=544px。'),
            (675,'继承机位提案：shot = source×.85 + (330,−30)，不改原实现。'),
            (728,'画幅底对应 source y=1305.88；最近肘约 y=1668，手腕约 y=2092。'),
            (781,'因此不抬手时手、腕、肘确实在画外；仅上臂和袖可见。'),
            (862,'需重建：整头、下颌、颈面、胸肩的协同；旧 x13 只给身份和笔触。'),
            (934,'测点和全部目标坐标见 JSON；红点为人工选取，待 Astra 冻结。')]:txt(d,(380,y),s,24)
im.save(OUT/'reference/01_identity_bone_calibration.jpg',quality=95)

# Layer topology and frame crop, including the full hidden arm chains.
im=Image.new('RGB',(1680,1180),'#f8f6ef');d=ImageDraw.Draw(im)
txt(d,(24,15),'S13 层次 / 连体路径 / 接触门（d01、d08、d15）',32,bold=True)
for i,j in enumerate((0,7,14)):
    k=KEYS[j]; x=40+i*545; sy=.31; ox=x+80;oy=100
    def p(n):a=k['joints_source_xy'][n];return ox+a[0]*sy,oy+a[1]*sy
    # Three distinct values and complete arm paths below crop, no shared elbow.
    for side,col in [('far','#d8dde0'),('near','#687985')]:
        path=[p(n+'_'+side) for n in ('shoulder','elbow','wrist','finger_tip')]
        for a,b in zip(path,path[1:]):line(d,[a,b],col,28)
    shn=p('shoulder_near');shf=p('shoulder_far')
    nb=p('neck_base')
    d.polygon([shn,(nb[0]-35,nb[1]),(nb[0]+35,nb[1]),shf,
               (shf[0]+25,oy+1536*sy),(shn[0]-25,oy+1536*sy)],fill='#adb8bf')
    # Near arm remains in front after torso fill.
    path=[p(n+'_near') for n in ('shoulder','elbow','wrist','finger_tip')]
    for a,b in zip(path,path[1:]):line(d,[a,b],'#687985',28)
    for side in ('near','far'):
        for name in ('shoulder','elbow','wrist','finger_tip'):dot(d,p(name+'_'+side),5)
    hc=p('head_center');d.ellipse((hc[0]-94,hc[1]-100,hc[0]+94,hc[1]+100),outline='#566672',width=3)
    line(d,[p('occipital_joint'),p('neck_base')],'#c29d76',25)
    # the source canvas is a registration surface, extending unseen elbows is diagnostic.
    ycut=oy+((1080+30)/.85)*sy
    line(d,[(x+20,ycut),(x+490,ycut)],'#b34e3b',3)
    txt(d,(x+15,ycut-34),'最终画幅底；以下为画外构造',19,fill='#b34e3b')
    txt(d,(x+15,850),f"{k['id']} F{k['f']:03}：嘴到最近腕 > 1000 源px",21)
    txt(d,(x+15,895),'远臂（浅）→ 躯干（中）→ 近臂（深）',20)
txt(d,(35,970),'本方案无手嘴接触：两手自然下垂 / 画外；无持物；不临时生成一只捂嘴手。',27,bold=True)
txt(d,(35,1025),'领口接颈根、颈肤接下颌；头转过正面后耳与辫的近远关系交换，身体近远臂不交换。',25)
txt(d,(35,1080),'虚构造不作成图结构证明。若增加捂嘴：先补完整肩→肘→腕→掌路径及手唇近图，再重新审。',24,fill='#9d543a')
im.save(OUT/'reference/02_layer_contact_gate.jpg',quality=95)

# Actual, unaltered style-source crops; preserve original repository provenance.
im=Image.new('RGB',(1600,1010),'#f8f6ef');d=ImageDraw.Draw(im)
txt(d,(25,16),'实际像素参考 / 只取身份、笔触；不沿用这两张之间的动作变形',30,bold=True)
for x,name,label in [(30,'anim_13_xiaoman_stare.png','旧 A：右向造型'),(550,'anim_13_xiaoman_yawn.png','旧 B：左向哈欠造型')]:
    src=Image.open(ROOT/'collab/refs'/name);src.thumbnail((500,750));im.paste(src,(x,75));txt(d,(x,845),label,24,bold=True)
ex=Image.open(ROOT/'collab/refs/xiaoman_expressions_current03.png');ex.thumbnail((500,300));im.paste(ex,(1080,150))
txt(d,(1090,390),'表情表：识别同一角色',24,bold=True)
for y,s in [(470,'纠正旧动作依据：'),(520,'1. 禁止 A/B 直接切换头。'),(570,'2. 禁止单独纵向缩放嘴。'),(620,'3. 头转，耳/发根/颈面一起。'),(670,'4. 胸肩随呼吸及末段转动。'),(720,'5. 不把旧 B 的闭眼当发现。')]:txt(d,(1090,y),s,21)
txt(d,(25,940),'全分辨率原件仍在 collab/refs；本页只作查看副本；源 SHA 与 git blob 见 provenance。',24)
im.save(OUT/'reference/03_actual_style_sources.jpg',quality=95)

# Full prompts are prepared only. No request has been submitted.
COMMON='''S13《来电》小满单角色逐张绘图，首阶段参考尚未冻结，本文件是待审提示词。身份以 xiaoman_turnaround_v4_draft.png 和 xiaoman_expressions_current03.png 为准：同一小女孩、深棕刘海、双低马尾、红花发圈、黄底白圆点短袖连衣裙、白色圆领。旧 anim_13 两张只参考造型笔触，不能复制错误动作或直接当两个端点。画布1024×1536，头高约640源px；共同位置按S13_reference_plan.json。本张参考构造图只是骨架/体积标注，绝不把灰块或骨架绘入成图。以最近已审合格的真实画稿为改图源，保留统一中性底色与笔触；场景马灯光由后续合成加一次。完整颅体、下颌、耳、刘海、后脑、发根、马尾和颈面作为连体结构重画；下颌张口不能只拉伸口腔像素。胸和肩随本张姿态整体运动，双臂从自己的肩袖连续向下，手、腕、肘全在最终画幅外，无手嘴接触，无新道具。禁止整身缩放、孤立肩抖、只挪五官、脸网格扭曲、全画面溶解、增加第三臂、复制对侧手或手从胸口长出。透明背景，保全半透明发缘。'''
requests=[]
for i,k in enumerate(KEYS):
    prompt=COMMON+f"\n本张 {k['id']} F{k['f']:03}，停{k['hold']}帧：{k['title']}。{k['note']}\n头朝向{ k['head_yaw_deg']:+}°（正为画右），俯仰{k['head_pitch_deg']:+}°（负为抬颏），胸朝向{k['torso_yaw_deg']:+}°，眼开比例{k['eye_open_fraction']}，嘴开口高约{k['mouth_aperture_H']}头高。头与身体三维连续，角度是构造目标，最终用实际图判断，不能声称像素精确角。\n"
    if i==0:prompt+='首态：重新建立比例正确、完整头颈胸肩的小满，不直接拿旧A当已合格母版。'
    else:prompt+=f"依赖：从 d{i:02} 已通过原件派生；上张若退回则暂停本张，不从失败态扩链。"
    requests.append({'id':k['id'],'executed':False,'tool':'image_gen.imagegen (exposed; not invoked)',
      'args_template':{'prompt':prompt,'transparent_background':True,
      'referenced_image_paths':['collab/refs/xiaoman_turnaround_v4_draft.png','collab/refs/xiaoman_expressions_current03.png',
      f"collab/reviews/cloud_s13_20261018/reference/S13_{k['id']}_F{k['f']:03}_construction.png"] + ([] if i==0 else [f'<approved d{i:02} original path; fill only after acceptance>'])}})
save_json(OUT/'prompts/requests_NOT_EXECUTED.json',{'status':'NO GENERATION UNTIL ASTRA FREEZE','requests':requests})

sources=['collab/README.md','collab/claude.md','collab/partner.md','docs/keyframes/scenes03_12_drawing_plan.md',
         'docs/keyframes/S18.json','collab/refs/xiaoman_turnaround_v4_draft.png','collab/refs/xiaoman_expressions_current03.png',
         'collab/refs/anim_13_xiaoman_stare.png','collab/refs/anim_13_xiaoman_yawn.png','js/paint/shots/s13.js']
sources+= [str(p.relative_to(ROOT)) for p in sorted((ROOT/'collab/keyposes/20261018_scenes03_12/S13').glob('*.jpg'))]
manifest=[]
for p in sources:
    data=(ROOT/p).read_bytes();info={'path':p,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
        'git_blob':subprocess.check_output(['git','hash-object',p],cwd=ROOT,text=True).strip(),
        'url':'https://github.com/yiggeror/animation-competition/blob/'+PLAN['base_commit']+'/'+p}
    if p.endswith(('.png','.jpg')):
        with Image.open(ROOT/p) as img:info.update({'dimensions':list(img.size),'mode':img.mode})
    manifest.append(info)
save_json(OUT/'provenance/source_manifest.json',{'base_commit':PLAN['base_commit'],'files':manifest})
save_json(OUT/'provenance/generation_ledger.json',{'stage':'reference_only','image_generation_requests':0,'raw_outputs':[],
    'image_tool_exposed':True,'execution_availability_tested':False,'reason':'First-stage freeze gate; no production image request authorized before review.',
    'previews':'Pillow annotation and construction diagrams only; never production drawings.',
    'external_paid_service_or_api_calls':0,'full_film_render_runs':0,'blender_runs':0})

# Objective checks do not replace visual inspection; saved separately from human/self review.
checks={'frames':sum(k['hold'] for k in KEYS),'keys':len(KEYS),'all_contiguous':all(KEYS[i]['end_inclusive']+1==KEYS[i+1]['f'] for i in range(15)),
        'all_hands_outside_shot':all(k['joints_shot_xy'][n][1]>1080 for k in KEYS for n in ['elbow_near','elbow_far','wrist_near','wrist_far','finger_tip_near','finger_tip_far']),
        'bone_max_drift_source_px':{},'all_pngs_decoded':True,'png_count':0,'jpg_count':0}
for seg,a,b in [('upper_arm','shoulder_near','elbow_near'),('forearm','elbow_near','wrist_near'),('hand','wrist_near','finger_tip_near')]:
    lens=[math.dist(k['joints_3d_source'][a],k['joints_3d_source'][b]) for k in KEYS]
    checks['bone_max_drift_source_px'][seg]=round(max(lens)-min(lens),5)
for p in (OUT/'reference').glob('*.png'):
    with Image.open(p) as im:im.load()
    checks['png_count']+=1
for p in (OUT/'reference').glob('*.jpg'):
    with Image.open(p) as im:im.load()
    checks['jpg_count']+=1
assert checks['frames']==120 and checks['keys']==16 and checks['all_contiguous'] and checks['all_hands_outside_shot']
assert max(checks['bone_max_drift_source_px'].values())<.01
save_json(OUT/'qa/geometry_validation.json',checks)
print(json.dumps(checks,ensure_ascii=False,indent=2))
