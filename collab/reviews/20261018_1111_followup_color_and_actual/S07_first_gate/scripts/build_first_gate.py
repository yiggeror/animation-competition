from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math, json, hashlib

ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT.parent/'astra_s07_reference_prepare_20261018_1021'
S01=ROOT.parent/'astra_s01_s04_reference_prepare_20261018_1038'
FONT=ROOT.parent/'astra_s03b_painted_pilot_20261018/refs/NotoSansSC-VF.ttf'
BLUE='#126c9c'; FAR='#a67422'; GREEN='#16815d'; RED='#b24e51'; INK='#213540'
def font(n): return ImageFont.truetype(str(FONT), n)
def txt(d,p,s,n=20,c=INK): d.text(p,s,font=font(n),fill=c)
def dot(d,p,c,r=5): d.ellipse((p[0]-r,p[1]-r,p[0]+r,p[1]+r),fill=c,outline='white',width=1)
def dash(d,a,b,c,w=3):
    dx=b[0]-a[0];dy=b[1]-a[1];L=math.hypot(dx,dy)
    for i in range(0,int(L),18):
        lo=i/L;hi=min((i+10)/L,1)
        d.line((a[0]+dx*lo,a[1]+dy*lo,a[0]+dx*hi,a[1]+dy*hi),fill=c,width=w)
def ik(s,w):
    dx=w[0]-s[0];dy=w[1]-s[1];D=math.hypot(dx,dy)
    assert 6 < D < 122, (s,w,D)
    q=(64**2-58**2+D**2)/(2*D);h=math.sqrt(64**2-q*q)
    # Keep the same branch for the whole lowering chain; no hidden flip.
    return [s[0]+q*dx/D+h*dy/D,s[1]+q*dy/D-h*dx/D]
def add(a,b): return [a[0]+b[0],a[1]+b[1]]
def interp(a,b,u): return [a[j]*(1-u)+b[j]*u for j in range(2)]

old=json.loads((OLD/'geometry/six_key_states.json').read_text())
base01=json.loads((S01/'geometry/six_key_states.json').read_text())['states'][0]['grandma']
end18=next(s for s in old['states'] if s['frame']==18)
bodykeys=['hip','shoulder','far_hip','far_shoulder','near_ankle','far_ankle','head_center']
body0={k:base01[k] for k in bodykeys}
body0.update(near_knee=base01['knee'],far_knee=base01['far_knee'])
body18={k:end18[k] for k in bodykeys+['near_knee','far_knee']}

# Same visible source proportions at uniform scale .205. The bottom is partly
# hidden by trousers: this is a consistent construction, not a recovered full mesh.
BOWL={'width':79.1,'rim_ellipse_height':17.4,'rim_center_to_visible_bottom':21.7,
      'source_uniform_scale':.205,'source_visible_width_px_approx':386,
      'source_visible_depth_px_approx':106,
      'scope':'原件部分盆底被裤腿遮挡；79.1/21.7是同一等比观察下的构造，非完整实测盆形。'}
centers={0:[868.52,644.81],18:[802.04,752.8]}
# Right-side near/front and far/back rim sectors. Contacts are fingertips gripping
# the outer lip with thumbs inside, not the wrist and not the bottom of the bowl.
offset={'near_contact':[34,4.4],'far_contact':[27,-6.3]}
wrist_offset={'near':[9,-12],'far':[7,-11]}

def state(f):
    u=f/18
    if f==0: body=dict(body0)
    elif f==18: body=dict(body18)
    else:
        body={k:interp(body0[k],body18[k],u) for k in bodykeys+['near_knee','far_knee']}
        # Intermediate shoulder is a constant-length torso construction. These
        # middle frames are local reach tests only, not frozen production poses.
        a0=math.atan2(body0['shoulder'][1]-body0['hip'][1],body0['shoulder'][0]-body0['hip'][0])
        a1=math.atan2(body18['shoulder'][1]-body18['hip'][1],body18['shoulder'][0]-body18['hip'][0])
        a=a0*(1-u)+a1*u
        body['shoulder']=add(body['hip'],[111*math.cos(a),111*math.sin(a)])
        body['far_shoulder']=add(body['shoulder'],[-8,3])
    b=interp(centers[0],centers[18],u)
    st={'frame':f,**body,'bowl_rim_center':b,'bowl_bottom_y':b[1]+21.7,
        'camera':[816,482.5,1.04] if f<16 else [1024,630,2.75],
        'body_scope':'端态沿原两包身体；中间仅用于手臂可达检查，不是生产姿态冻结。',
        'near_hand_anatomical':'left','arm_ik_branch':-1}
    for side in ['near','far']:
        st[side+'_contact']=add(b,offset[side+'_contact'])
        st[side+'_wrist']=add(st[side+'_contact'],wrist_offset[side])
        s=st['shoulder' if side=='near' else 'far_shoulder']
        st[side+'_elbow']=ik(s,st[side+'_wrist'])
    return st

allstates=[state(f) for f in range(19)]
states=[allstates[0],allstates[18]]
checks=[]
for st in allstates:
    out={'frame':st['frame'],'branch':-1,'arms':{}}
    for side in ['near','far']:
        s=st['shoulder' if side=='near' else 'far_shoulder'];e=st[side+'_elbow'];w=st[side+'_wrist']
        out['arms'][side]={'shoulder_wrist':math.dist(s,w),'upper':math.dist(s,e),'fore':math.dist(e,w),
                           'reach_fraction':math.dist(s,w)/122,
                           'endpoint_singular_margin':122-math.dist(s,w)}
    checks.append(out)
assert body18=={k:end18[k] for k in body18}
assert abs(states[1]['bowl_bottom_y']-774.5)<1e-9
for st in states:
    assert st['near_ankle']==[869,758] and st['far_ankle']==[879,758]
for ck in checks:
    for a in ck['arms'].values():
        assert abs(a['upper']-64)<1e-6 and abs(a['fore']-58)<1e-6

proposal={
 'status':'PROPOSAL_PENDING_OPUS_FREEZE_NOT_PRODUCTION_ART',
 'replaces':'此前S01/S04 72.02宽/21.7深混源提案及S07 765.859浅盆落地rim；未改旧包。',
 'units':'1672×941 scene pixels before camera',
 'shared_bowl':BOWL,
 'fixed_world':{'floor_y':775,'stool_top_y':691.9,'stool_x_extent':[899,982],
                'F000_seat_contact':[933,691.9],'F018_seat_contact':[933,691.9],
                'near_ankle':[869,758],'far_ankle':[879,758],'sole_y':775},
 'contacts':{'rim_offsets':offset,'wrist_minus_contact':wrist_offset,
             'grip':'近左手在近侧前缘，远右手在远侧后缘；拇指压内沿、卷指扣外沿下缘。不可画成腕点落盆或掌穿盆。'},
 'states':states,
 'affected_frames':{
  'S01_S04':'全部出现盆的态统一79.1宽/21.7可见深构造；盆中心868.52,644.81与底666.51不移。接触厚度由实际成图验证。',
  'S07_F000':'新左侧双手端盆母态，身体沿S01/S04提案；旧剥豆图不能复用为端盆。',
  'S07_F008_F016':'盆作为同一刚体平移；双手接点随盆，腕/肘重算同一分支；见reach样点，不当中间姿态冻结。',
  'S07_F018':'盆底774.5不变，rim改752.8；手指接触和两腕/肘更新，身体/凳/地不变。',
  'S07_F022':'盆已静止，用新F018手腕起点离盆移膝；不得把旧浅盆腕点作起点。',
  'S07_F025_F028_F031':'膝掌目标不随盆移动；身体与脚沿原参考。须用新F022接膝，不能腕跳。',
  'S07_F034_through_F106':'已落盆位置/厚度持续同一刚体；不会跟离盆手回升。奶奶其它关键接点不因此移动。'},
 'scope_limits':['没有生图','没有写GitHub或主实现','未冻结','非真实3D骨长','腕指真实形体、袖肘遮挡和连续表演仍须成图独审'],
 'source_refs':{
  'grandma_identity':'collab/refs/grandma_turnaround_current03_draft.png',
  'bowl_observation':'collab/refs/anim_01_grandma_beans.png',
  'F000_code_blob':'5441a67dda98ca44ef16907789f47a883d689e91',
  'latest_claude_blob_read':'bf784462ea8c423c95529cde2149e9fabb19e3f9',
  'base_s07_json':str(OLD/'geometry/six_key_states.json'),
  'base_s01_json':str(S01/'geometry/six_key_states.json')},
}
(ROOT/'geometry/F000_F018_proposal.json').write_text(json.dumps(proposal,ensure_ascii=False,indent=2))
(ROOT/'geometry/local_reach_checks_0_18.json').write_text(json.dumps({'checks':checks,'sample_points':[allstates[f] for f in [0,8,16,18]],'scope':'F8/F16仅可达示意，未冻结节拍/身体中间态。'},ensure_ascii=False,indent=2))

def bowl(d,P,c,old=False):
    x,y=c;rx=BOWL['width']/2;ry=BOWL['rim_ellipse_height']/2;dep=21.7
    pts=[(x-rx,y),(x-rx*.79,y+dep*.68),(x-rx*.46,y+dep),
         (x+rx*.46,y+dep),(x+rx*.79,y+dep*.68),(x+rx,y)]
    line=[P(p) for p in pts]
    if not old:d.polygon(line,fill='#ece6d4')
    d.line(line,fill=GREEN,width=3)
    e=[P((x-rx,y-ry)),P((x+rx,y+ry))]
    d.ellipse((*e[0],*e[1]),fill='#f8f5eb' if not old else None,outline=GREEN,width=3)

def draw_pose(d,P,st,show_old=False):
    # Always show far segments behind near segments.
    for a,b in [('far_shoulder','far_hip'),('far_hip','far_knee'),('far_knee','far_ankle')]:dash(d,P(st[a]),P(st[b]),FAR)
    for a,b in [('shoulder','hip'),('hip','near_knee'),('near_knee','near_ankle')]:d.line((*P(st[a]),*P(st[b])),fill=BLUE,width=4)
    h=P(st['head_center']);s=P(add(st['head_center'],[34,37.5]));rx=s[0]-h[0];ry=s[1]-h[1]
    d.ellipse((h[0]-rx,h[1]-ry,h[0]+rx,h[1]+ry),outline=BLUE,width=3)
    d.line((*h,*P(st['shoulder'])),fill=BLUE,width=3)
    d.line((*P((899,691.9)),*P((982,691.9))),fill=GREEN,width=5)
    for x in [869,879]:
        d.line((*P((x-17,775)),*P((x+17,775))),fill=GREEN,width=5)
        d.line((*P((x,758)),*P((x,775))),fill=GREEN,width=2)
    bowl(d,P,st['bowl_rim_center'])
    if show_old:
        for side in ['near','far']:
            ss='shoulder' if side=='near' else 'far_shoulder'
            dash(d,P(end18[ss]),P(end18[side+'_elbow']),RED,2)
            dash(d,P(end18[side+'_elbow']),P(end18[side+'_wrist']),RED,2)
        a=P((762.49,765.859));b=P((841.59,765.859));dash(d,a,b,RED,2)
    for side,col in [('far',FAR),('near',BLUE)]:
        ss='shoulder' if side=='near' else 'far_shoulder'
        ps=[P(st[k]) for k in [ss,side+'_elbow',side+'_wrist',side+'_contact']]
        for a,b in zip(ps,ps[1:]):
            if side=='far':dash(d,a,b,col,4)
            else:d.line((*a,*b),fill=col,width=5)
        dot(d,ps[2],col,5);dot(d,ps[3],GREEN,6)
    dot(d,P((933,691.9)),GREEN,5)

# Same-scale world-space view: unlike screenshot camera crops it exposes the
# unchanged feet and seat for direct comparison.
board=Image.new('RGB',(1500,1020),'#fbfcfc');d=ImageDraw.Draw(board)
d.rectangle((0,0,1500,84),fill=INK)
txt(d,(28,15),'S07 首段双参考修正提案｜同一等比厚盆，未冻结／非生产画',28,'white')
txt(d,(28,52),'统一79.1宽 / 21.7可见深；替换旧72.02宽混源和落地浅盆锚。身体、凳、地不动。',18,'#deecee')
for i,st in enumerate(states):
    ox=18+i*750
    txt(d,(ox+18,100),f'F{st["frame"]:03} '+('双手端盆起点' if st['frame']==0 else '盆底落地，双手仍扣盆缘'),25)
    P=lambda p,ox=ox:(ox+24+(p[0]-735)*2.25,165+(p[1]-470)*2.25)
    d.rectangle((ox+12,145,ox+726,902),outline='#ccd8dc',width=2)
    draw_pose(d,P,st,st['frame']==18)
    txt(d,(ox+28,910),f'盆沿中心 {st["bowl_rim_center"][0]:.2f}, {st["bowl_rim_center"][1]:.2f}',20)
    txt(d,(ox+28,940),f'盆底 y={st["bowl_bottom_y"]:.2f}；同一近左有镯／远右无镯',19)
txt(d,(30,983),'蓝=近侧，赭虚=远侧，绿=支撑/手指接点；红虚=F018旧浅盆与旧肘线，仅作改动对照。',20)
board.save(ROOT/'review/F000_F018_world_proposal.jpg',quality=95)

# Tight hand-to-rim reference. Wrist and fingertip contact points are separate.
board=Image.new('RGB',(1500,760),'white');d=ImageDraw.Draw(board)
d.rectangle((0,0,1500,78),fill=INK);txt(d,(24,15),'手—盆局部接触门｜两端同一刚体、同一抓握点；肘沿同一分支',27,'white')
for i,st in enumerate(states):
    ox=i*750
    b=st['bowl_rim_center']
    P=lambda p,b=b,ox=ox:(ox+315+(p[0]-b[0])*5.6,470+(p[1]-b[1])*5.6)
    bowl(d,P,b)
    for side,col in [('far',FAR),('near',BLUE)]:
        ps=[P(st[k]) for k in [side+'_elbow',side+'_wrist',side+'_contact']]
        for a,c in zip(ps,ps[1:]):
            if side=='far':dash(d,a,c,col,5)
            else:d.line((*a,*c),fill=col,width=6)
        dot(d,ps[1],col,7);dot(d,ps[2],GREEN,8)
    txt(d,(ox+24,95),f'F{st["frame"]:03} '+('端盆' if st['frame']==0 else '落地仍扣沿'),25)
    txt(d,(ox+24,135),'近左：前缘扣握；远右：后缘扣握',21)
    txt(d,(ox+24,170),'手腕和指端分开；不把手掌压穿盆壁。',19)
    txt(d,(ox+24,650),f'近接点 {st["near_contact"][0]:.2f}, {st["near_contact"][1]:.2f}',20)
    txt(d,(ox+24,685),f'远接点 {st["far_contact"][0]:.2f}, {st["far_contact"][1]:.2f}',20)
txt(d,(25,730),'仅构造接触图；实际拇指内沿、四指卷扣外沿及近远袖肘遮挡，必须用新画逐张检验。',19,RED)
board.save(ROOT/'review/F000_F018_contact_gate.jpg',quality=95)

# Approved camera crop evidence, with analytical pose laid over the actual old
# code screenshot. This is expressly not a painted candidate.
for st in states:
    f=st['frame'];src=ROOT/'sources/S07_d01_f000_code.jpg' if f==0 else OLD/'sources/S07_d04_f018.jpg'
    im=Image.open(src).convert('RGB');im=Image.blend(im,Image.new('RGB',im.size,'#f4f5f4'),.82)
    d=ImageDraw.Draw(im);cx,cy,z=st['camera'];scale=z*.75
    P=lambda p:(627+(p[0]-cx)*scale,353+(p[1]-cy)*scale)
    draw_pose(d,P,st,False)
    d.rectangle((0,0,1254,44),fill=INK)
    txt(d,(14,6),f'S07 F{f:03}｜原批准相机 + 厚盆双手修正提案，非生产图／未冻结',22,'white')
    out=Image.new('RGB',(1254,803),'white');out.paste(im);d=ImageDraw.Draw(out)
    txt(d,(16,718),'只改盆形状/位置与手腕肘接点；人物比例来源是原画，不照抄浅底代码人物。',20)
    txt(d,(16,752),'同场景固定：地775、凳691.9、双踝869/879，近左腕有镯；成图厚度/遮挡仍待审。',20)
    out.save(ROOT/f'review/F{f:03}_camera_proposal.png')

manifest=[]
for p in [OLD/'sources/anim_01_grandma_beans.png',OLD/'sources/grandma_turnaround_current03_draft.png',
          OLD/'sources/bg_01_room_wide_base_v2_draft.png',OLD/'geometry/six_key_states.json',
          S01/'geometry/six_key_states.json',ROOT/'sources/S07_d01_f000_code.jpg']:
    manifest.append({'local':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(ROOT/'sources/source_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(json.dumps({'output':str(ROOT),'states':2,'generated_art':False,'reach_min_max':[
 min(a['shoulder_wrist'] for c in checks for a in c['arms'].values()),
 max(a['shoulder_wrist'] for c in checks for a in c['arms'].values())],
 'F018_body_unchanged':True,'all_arm_lengths_pass':True},ensure_ascii=False))
