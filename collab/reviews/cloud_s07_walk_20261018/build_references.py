#!/usr/bin/env python3
"""S07 eleven-state construction references only; never generates character artwork."""
from pathlib import Path
import copy,csv,hashlib,json,math,os,shutil,subprocess
os.environ.setdefault('MPLCONFIGDIR','/tmp/s07-walk-reference-mpl')
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Polygon,Ellipse,Rectangle,Arc

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
BASE='60159846257c803263b4eab675ba35487fff12ce'
SOURCE='collab/reviews/20261018_1051_hand_and_reference_handoff/references/S07/'
for d in ['sources','geometry','reference','review']:(ROOT/d).mkdir(exist_ok=True)
inputs={
 'S07_reference_README.md':SOURCE+'README.md',
 'six_key_states.json':SOURCE+'geometry/six_key_states.json',
 'source_measurements.json':SOURCE+'geometry/source_measurements.json',
 'six_key_overview.jpg':SOURCE+'key_group/six_key_overview.jpg',
 'contact_gate_comparison.jpg':SOURCE+'review/contact_gate_comparison.jpg',
 'grandma_turnaround_current03_draft.png':'collab/refs/grandma_turnaround_current03_draft.png',
 'G022_grandma_rgba.png':'collab/reviews/20261018_1425_s07_partial_scene/S07_grandma_022/production/F022_grandma_rgba.png',
 'G022_registration.json':'collab/reviews/20261018_1425_s07_partial_scene/S07_grandma_022/geometry/registration.json',
 'opening_plan.json':'docs/keyframes/opening_plan.json'}
manifest=[]
for name,path in inputs.items():
    raw=subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=REPO)
    assert raw==(REPO/path).read_bytes(),path
    (ROOT/'sources'/name).write_bytes(raw)
    manifest.append({'path':path,'copy':'sources/'+name,'fixed_commit':BASE,'sha256':hashlib.sha256(raw).hexdigest(),
                     'git_blob':subprocess.check_output(['git','rev-parse',f'{BASE}:{path}'],cwd=REPO,text=True).strip()})
(ROOT/'sources/source_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
old=json.loads((ROOT/'sources/six_key_states.json').read_text())
frozen={s['frame']:s for s in old['states'] if s['frame'] in [57,103,106]}
L=old['grandma'];floor=775.
font_manager.fontManager.addfont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
plt.rcParams.update({'font.family':'Noto Sans CJK JP','font.size':10,'axes.unicode_minus':False})

def ik(a,b,l1,l2,side=1):
    a=np.array(a,float);b=np.array(b,float);v=b-a;d=float(np.linalg.norm(v))
    assert abs(l1-l2)<d<=l1+l2,(a,b,d,l1+l2)
    e=v/d;q=(l1*l1-l2*l2+d*d)/(2*d)
    return (a+e*q+side*np.array([e[1],-e[0]])*math.sqrt(max(0,l1*l1-q*q))).tolist()

# Landing positions are newly proposed; only 57/103/106 copy frozen endpoints.
# Legs: near=anatomical right, far=anatomical left, for the whole right-facing group.
specs=[
 (57,'近右脚落地',5,None,None,None,'双支撑→近右承重'),
 (62,'近右支撑／远左过步',6,[930,610],[929,758],[938,735],'近右单支撑'),
 (68,'远左脚落地',5,[970,615],[929,758],[1004,758],'双支撑→远左承重'),
 (73,'远左支撑／近右过步',6,[1000,610],[1012,735],[1004,758],'远左单支撑'),
 (79,'近右脚落地',5,[1047,615],[1079,758],[1004,758],'双支撑→近右承重'),
 (84,'近右支撑／远左过步',6,[1078,610],[1079,758],[1088,735],'近右单支撑'),
 (90,'远左脚落地',5,[1119,618],[1079,758],[1154,758],'双支撑→远左承重'),
 (95,'近右收脚站定',5,[1140,613],[1138,758],[1154,758],'双脚固定，停止行进'),
 (100,'胸头一起探身／右手接近',3,[1140,613],[1138,758],[1154,758],'双脚固定，灯仍归桌支撑'),
 (103,'近右闭指扣梁',3,None,None,None,'双脚固定，桌支撑＋手已闭握'),
 (106,'近右手与整灯同提',2,None,None,None,'双脚固定，承重转交右手')]
states=[]
for frame,title,hold,hip,near,far,support in specs:
    if frame in frozen:s=copy.deepcopy(frozen[frame])
    else:
        angle={62:.07,68:.09,73:.06,79:.09,84:.06,90:.08,95:.09,100:.23}[frame]
        shoulder=[hip[0]+111*math.sin(angle),hip[1]-111*math.cos(angle)]
        fh=[hip[0]-7,hip[1]+1];fs=[shoulder[0]-8,shoulder[1]+3]
        nw=[hip[0]+28,hip[1]+1];fw=[hip[0]-13,hip[1]]
        if frame==95:nw=[1184,592];fw=[1156,616]
        if frame==100:nw=[1244,519];fw=[1156,616]
        s={'frame':frame,'title':title,'hip':hip,'shoulder':shoulder,'far_hip':fh,'far_shoulder':fs,
           'near_ankle':near,'far_ankle':far,'near_knee':ik(hip,near,78,72),
           'far_knee':ik(fh,far,78,72),'near_wrist':nw,'far_wrist':fw,
           'near_elbow':ik(shoulder,nw,64,58,side=-1 if frame==100 else 1),'far_elbow':ik(fs,fw,64,58,side=-1 if frame>=95 else 1),
           'head_center':[shoulder[0]+22,shoulder[1]-60],'contacts':[],
           'lamp_lift':0,'sole_y':floor,'near_hand_anatomical':'right','camera':[816,482.5,1.04]}
    if frame in [95,100]:
        # Already stopped: keep the frozen final leg branch as well as foot/hip positions.
        s['near_knee']=copy.deepcopy(frozen[103]['near_knee'])
        s['far_knee']=copy.deepcopy(frozen[103]['far_knee'])
    s['hold_frames']=hold;s['last_frame_inclusive']=frame+hold-1
    s['geometry_status']='FROZEN_ENDPOINT_FROM_HANDOFF' if frame in frozen else 'NEW_CONSTRUCTION_PROPOSAL_PENDING_ASTRA'
    s['support_phase']=support;s['facing']='screen right; never mirror'
    s['near_arm']='anatomical right, bare wrist, foreground'
    s['far_arm']='anatomical left, jade bangle, behind torso where occluded'
    planted=[k for k in ['near','far'] if s[k+'_ankle'][1]==758]
    s['planted_feet']=planted
    s['shoe_support_x']={k:[s[k+'_ankle'][0]-14,s[k+'_ankle'][0]+26] for k in planted}
    s['swing_sole_clearance']={k:758-s[k+'_ankle'][1] for k in ['near','far'] if k not in planted}
    # A declared 2D balance proxy, not measured biological CoM or a dynamics simulation.
    h=np.array(s['hip']);sh=np.array(s['shoulder']);head=np.array(s['head_center'])
    arm=np.mean([s[k] for k in ['near_elbow','near_wrist','far_elbow','far_wrist']],axis=0)
    leg=np.mean([s[k] for k in ['near_knee','near_ankle','far_knee','far_ankle']],axis=0)
    proxy=.30*h+.35*(h+sh)/2+.12*head+.10*arm+.13*leg
    s['balance_proxy_xy']=proxy.tolist()
    s['support_hull_x']=[min(v[0] for v in s['shoe_support_x'].values()),max(v[1] for v in s['shoe_support_x'].values())]
    assert s['support_hull_x'][0]<=proxy[0]<=s['support_hull_x'][1],(frame,proxy,s['support_hull_x'])
    s['gaze_target']=[1262,524.7] if frame>=95 else [1300,655]
    s['hand_contact']='open approach, fingertip target(1255,515), above actual bail arc; actual finger thickness/gap must be verified' if frame==100 else ('closed grip on bail; wrist is not contact point' if frame>=103 else 'empty hands; no lamp contact')
    if frame==100:
        s['open_fingertip_target']=[1255,515]
        t=np.linspace(math.pi,2*math.pi,4097)
        wire=np.stack((1262+23.3*np.cos(t),551+26.3*np.sin(t)),axis=1)
        s['open_fingertip_to_proposed_wire_centerline_min_distance']=float(np.linalg.norm(wire-np.array([1255,515]),axis=1).min())
    s['lamp_base']=[1262,642-s['lamp_lift']]
    s['lamp_bail_contact']=[1262,524.7-s['lamp_lift']]
    s['lamp_support']='right hand' if frame==106 else ('table; hand grip established but not yet lifted' if frame==103 else 'table only')
    states.append(s)

assert sum(s['hold_frames'] for s in states)==51
assert [s['frame'] for s in states]==[57,62,68,73,79,84,90,95,100,103,106]
checks=[]
for s in states:
    for key,value in frozen.get(s['frame'],{}).items():assert s[key]==value,(s['frame'],key)
    errors=[]
    for prefix,start in [('near',''),('far','far_')]:
        for a,b,target in [(start+'hip',prefix+'_knee',78),(prefix+'_knee',prefix+'_ankle',72),
                           (start+'shoulder',prefix+'_elbow',64),(prefix+'_elbow',prefix+'_wrist',58)]:
            errors.append(abs(float(np.linalg.norm(np.array(s[a])-s[b]))-target))
    assert max(errors)<1e-9,(s['frame'],errors)
    checks.append({'frame':s['frame'],'max_constructed_segment_error':max(errors),'balance_proxy_inside_support_hull':True,
                   'swing_sole_clearance':s['swing_sole_clearance']})
# Stable stance anchors are checked over every interval where that foot remains planted.
locks=[('near',57,68,929),('far',68,79,1004),('near',79,90,1079),('far',90,106,1154),('near',95,106,1138)]
for side,start,end,x in locks:
    for s in states:
        if start<=s['frame']<=end and side in s['planted_feet']:assert s[side+'_ankle']==[x,758]
for key in ['hip','shoulder','head_center','near_ankle','far_ankle','far_wrist']:
    assert states[-1][key]==states[-2][key]
assert np.allclose(np.array(states[-1]['near_wrist'])-states[-2]['near_wrist'],[0,-4.5])
assert np.allclose(np.array(states[-1]['contacts'])-states[-2]['contacts'],[[0,-4.5]])
payload={'status':'ELEVEN_STATE_REFERENCE_ONLY_PENDING_ASTRA_NOT_DRAWINGS','fixed_source_commit':BASE,
 'world_size':[1672,941],'fps':24,'scope_frames':[57,108],'duration_frames':108,'owned_states':[s['frame'] for s in states],
 'frozen_endpoint_frames':[57,103,106],'new_unfrozen_frames':[62,68,73,79,84,90,95,100],
 'construction_lengths':L,'static_contacts':old['static_contacts'],
 'balance_proxy':'0.30 pelvis+0.35 torso-midpoint+0.12 head+0.10 mean arm joints+0.13 mean knee/ankles. Arbitrary diagnostic weights, not measured biological CoM; no 3D/dynamic stability claim.',
 'shoe_rule':'planted ankle y758; flat sole y775, proposed interval[ankleX-14,ankleX+26]. Swing ankle y735 gives23px sole clearance; actual shoe/cloth shape requires drawing review.',
 'stance_locks':[{'side':s,'start_frame':a,'through_key_frame':b,'ankle_x':x,'ankle_y':758} for s,a,b,x in locks],
 'contact_gate':'F100 open and separated; F103 closed fingers on load-bearing bail, lamp base stays642; F106 wrist, grip and WHOLE lantern all move(0,-4.5). Pelvis and both shoes stay fixed.',
 'limits':'Technical construction only, no generated character art. Source 57/103/106 endpoints do not validate all11 drawings. Projected bones are construction choices, not real measured bones. Wait for G037 standing source before production identity/scale lock. 39-56 turn occurs in approved off-camera insert, no new turn drawing claimed.',
 'states':states}
(ROOT/'geometry/eleven_states.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
with (ROOT/'exposure.csv').open('w',newline='') as f:
    w=csv.writer(f,lineterminator='\n');w.writerow(['frame','hold','last_inclusive','action','support','near_right_ankle','far_left_ankle','balance_proxy_x','hand_contact','lamp_support','lamp_lift'])
    for s in states:w.writerow([s['frame'],s['hold_frames'],s['last_frame_inclusive'],s['title'],s['support_phase'],s['near_ankle'],s['far_ankle'],round(s['balance_proxy_xy'][0],2),s['hand_contact'],s['lamp_support'],s['lamp_lift']])
(ROOT/'review/numeric_checks.json').write_text(json.dumps({'checks':checks,'frozen_endpoints_unchanged':True,'stance_locks_checked':True,'F103_F106_rigid_lamp_and_grip_delta':[0,-4.5],'generated_artworks':0,'limitations':'Point/length checks are not proof of real anatomy, balance, five-finger grip or continuous naturalness.'},ensure_ascii=False,indent=2)+'\n')

def save(fig,path):
    fig.savefig(ROOT/path,dpi=130,bbox_inches='tight',facecolor='white');plt.close(fig)

def segment(ax,a,b,color,lw=7,ls='-'):
    ax.plot([a[0],b[0]],[a[1],b[1]],color=color,lw=lw,ls=ls,solid_capstyle='round')

def draw_state(ax,s,full=True):
    ax.set_xlim((800,1320) if full else (825,1220));ax.set_ylim((805,382) if full else (790,585));ax.set_aspect('equal');ax.axis('off')
    ax.axhline(775,color='#999999',lw=1)
    for prefix,color,ls in [('far','#bc8a46','--'),('near','#2875a2','-')]:
        h=s['far_hip'] if prefix=='far' else s['hip']
        segment(ax,h,s[prefix+'_knee'],color,4,ls);segment(ax,s[prefix+'_knee'],s[prefix+'_ankle'],color,4,ls)
        ankle=np.array(s[prefix+'_ankle']);sole=ankle[1]+17
        ax.add_patch(Polygon([(ankle[0]-14,sole-9),(ankle[0]+10,sole-11),(ankle[0]+26,sole-5),(ankle[0]+26,sole),(ankle[0]-14,sole)],facecolor=color,alpha=.3,edgecolor=color))
        if prefix in s['planted_feet']:ax.plot([ankle[0]-14,ankle[0]+26],[775,775],color='#2f916a',lw=4)
        else:ax.annotate(f'离地{758-ankle[1]:.0f}',xy=(ankle[0]+22,sole),xytext=(ankle[0]+20,sole-24),fontsize=7,color=color)
    if full:
        # Three depths: far arm, torso mass, near arm. Blocks are construction, not anatomy art.
        for prefix,color,ls in [('far','#bc8a46','--')]:
            segment(ax,s['far_shoulder'],s['far_elbow'],color,8,ls);segment(ax,s['far_elbow'],s['far_wrist'],color,7,ls)
        sh=np.array(s['shoulder']);h=np.array(s['hip']);e=(h-sh)/np.linalg.norm(h-sh);p=np.array([-e[1],e[0]])
        ax.add_patch(Polygon([sh+p*22,sh-p*22,h-p*25,h+p*25],facecolor='#bfc7ce',edgecolor='#727b85',alpha=.85))
        segment(ax,s['shoulder'],s['near_elbow'],'#2875a2',8);segment(ax,s['near_elbow'],s['near_wrist'],'#2875a2',7)
        ax.add_patch(Ellipse(s['far_wrist'],14,8,edgecolor='#3b967a',facecolor='none',lw=2))
        ax.scatter(*s['near_wrist'],c='#2875a2',s=24,zorder=8)
        hc=s['head_center'];ax.add_patch(Ellipse(hc,70,75.1,facecolor='none',edgecolor='#515d69',lw=1.5))
        ax.annotate('',xy=(hc[0]+35,hc[1]+3),xytext=hc,arrowprops={'arrowstyle':'->','color':'#515d69'})
        lift=s['lamp_lift'];ax.plot([1229,1295],[642,642],color='#8b6d56',lw=3)
        ax.add_patch(Rectangle((1240,551-lift),44,91,facecolor='none',edgecolor='#467462'))
        ax.add_patch(Arc((1262,551-lift),46.6,52.6,theta1=180,theta2=360,edgecolor='#467462',lw=2))
        ax.scatter(*s['lamp_bail_contact'],c='#467462',s=20)
        if s['frame']>=103:segment(ax,s['near_wrist'],s['contacts'][0],'#267292',3);ax.scatter(*s['contacts'][0],s=40,facecolors='none',edgecolors='#d24b52',zorder=9)
        if s['frame']==100:segment(ax,s['near_wrist'],s['open_fingertip_target'],'#2875a2',2)
    proxy=s['balance_proxy_xy'];ax.axvline(proxy[0],color='#a04a8a',lw=1,ls=':');ax.scatter(*proxy,c='#a04a8a',s=24)
    ax.set_title(f"F{s['frame']:03} ×{s['hold_frames']} · {s['title']}",fontsize=11)
    ax.text(.01,.02,s['support_phase'],transform=ax.transAxes,fontsize=8)

for s in states:
    fig,ax=plt.subplots(figsize=(7,6));draw_state(ax,s)
    fig.text(.5,.015,'施工参考／非人物画稿／新中间态待审；蓝=近右裸腕，赭虚=远左玉镯，灰=躯干',ha='center',fontsize=9)
    save(fig,f"reference/F{s['frame']:03}.png")
fig,axs=plt.subplots(3,4,figsize=(20,14))
for ax,s in zip(axs.flat,states):draw_state(ax,s)
axs.flat[-1].axis('off');axs.flat[-1].text(.02,.95,'S07 后段11态 · 参考待审\n\n只继承57/103/106端点。\n中间八态新施工，不是图审通过。\n\n蓝：近右／裸腕\n赭虚：远左／玉镯\n灰：躯干；绿：接触\n紫点/线：二维平衡代理，非实测重心\n\n全部在1672×941同一世界中。\n0次生图；先交Astra冻结。',va='top',fontsize=12)
save(fig,'reference/eleven_overview.png')
fig,axs=plt.subplots(3,4,figsize=(20,10))
for ax,s in zip(axs.flat,states):draw_state(ax,s,False)
axs.flat[-1].axis('off');axs.flat[-1].text(.02,.9,'落脚锚保持\n近右929 → 1079 → 1138\n远左865 → 1004 → 1154\n\n过步62/73/84：摆动鞋底离地23。\n95以后双脚固定。\n\n只是新施工提案，\n不证明真实体积或动力学稳定。',va='top',fontsize=12)
save(fig,'reference/feet_and_balance.png')

# Contact schema: cross-section shorthand explicitly does not assert a finished five-digit hand.
fig,axs=plt.subplots(1,3,figsize=(15,5))
for ax,s in zip(axs,states[-3:]):
    lift=s['lamp_lift'];cx,cy=s['lamp_bail_contact']
    ax.set_xlim(1234,1288);ax.set_ylim(553,501);ax.set_aspect('equal');ax.axis('off')
    ax.add_patch(Arc((1262,551-lift),46.6,52.6,theta1=180,theta2=360,color='#476c5c',lw=5,zorder=3))
    ax.scatter(*s['near_wrist'],c='#2875a2',s=45);ax.annotate('右裸腕',s['near_wrist'],(1235,505),fontsize=10)
    if s['frame']==100:
        segment(ax,s['near_wrist'],s['open_fingertip_target'],'#2875a2',4)
        ax.annotate('开掌目标；与弧线中心线距约10.5px',xy=(1255,520),xytext=(1234,544),fontsize=9,arrowprops={'arrowstyle':'->'})
    else:
        segment(ax,s['near_wrist'],[1258,521-lift],'#2875a2',6)
        for x in [1258,1261,1264,1267]:ax.add_patch(Arc((x,524.7-lift),3,10,theta1=0,theta2=320,color='#aa568d',lw=2,zorder=6))
        segment(ax,[1255,529-lift],[1260,526-lift],'#2875a2',3)
        ax.annotate('四指绕梁／拇指对扣\n符号示意，五指须实画验收',xy=(1264,524.7-lift),xytext=(1235,544),fontsize=9,arrowprops={'arrowstyle':'->'})
    ax.scatter(cx,cy,c='#cf454f',s=28,zorder=9)
    ax.set_title(f"F{s['frame']:03} · {'接近未触' if s['frame']==100 else '已扣未提' if s['frame']==103 else '闭握同提4.5'}")
fig.suptitle('掌梁门：握承重提梁；腕点≠掌指接点；灯罩/调芯杆不是握点。技术符号，非成图。',fontsize=14)
save(fig,'reference/bail_contact_sequence.png')

font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',22)
sheet=Image.new('RGB',(1200,900),'#eeeeee');d=ImageDraw.Draw(sheet)
identity=Image.open(ROOT/'sources/grandma_turnaround_current03_draft.png').crop((910,10,1125,758))
identity.thumbnail((245,705));sheet.paste(identity,(30,70))
g=Image.open(ROOT/'sources/G022_grandma_rgba.png').convert('RGBA').crop((80,590,480,930))
bg=Image.new('RGBA',g.size,(238,238,238,255));bg.alpha_composite(g);bg.thumbnail((480,430));sheet.paste(bg.convert('RGB'),(365,110))
d.text((20,15),'真实身份侧视（朝右、不镜像）',font=font,fill='#333333')
d.text((350,65),'当前G022头脸（原朝左，仅对身份）',font=font,fill='#333333')
d.multiline_text((350,510),'灰发低髻／红簪珠／黑圆眼镜／蓝底白花／深裤白底鞋\n\n朝右后段：近右腕无镯，远左腕有玉镯。\n不可镜像G022去伪造朝右站姿。\n\n75.1头包络、64/58臂、78/72腿是既有施工值。\n衣下关节不可观测；不是实测真骨长。\n当前无G037站直画稿；到时补核头身与站姿尺度。',font=font,fill='#333333',spacing=13)
d.text((20,860),'原图裁取仅用于身份比较；未生成新人物。原件与SHA见sources/。',font=font,fill='#8e3f45')
sheet.save(ROOT/'reference/identity_and_proportion.png')
print(json.dumps({'states':len(states),'exposure_frames':51,'range':'57..107 inclusive','generated_artworks':0,'fixed_endpoints':[57,103,106],'new_frames_pending_review':[62,68,73,79,84,90,95,100],'max_segment_error':max(c['max_constructed_segment_error'] for c in checks)},ensure_ascii=False))
