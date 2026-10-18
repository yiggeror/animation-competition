#!/usr/bin/env python3
"""S09 stage-one construction references only; never produces character artwork."""
from pathlib import Path
import csv
import hashlib
import json
import math
import os
import subprocess

os.environ.setdefault('MPLCONFIGDIR', '/tmp/s09-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Ellipse, Polygon, Circle
from PIL import Image
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
font_manager.fontManager.addfont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
plt.rcParams.update({'font.family': 'Noto Sans CJK JP', 'font.size': 10, 'axes.unicode_minus': False})
BASE = '3d66443997cee24b64059e6f53f7d46968a3a05c'
STARTS = [0,8,14,18,26,31,37,42,44,48,52,56,58,63,69,73,77,85]
ACTIONS = [
 '双手捧筒，眼看侧滑开关', '近右拇指贴键，余指仍环握',
 '第一次推到ON，未亮', '到位后等待，眉心轻拧；灯仍暗',
 '推回OFF，左手开始松托', '左掌展开迎尾盖，右手转筒，眼看掌心',
 '第一击蓄势：尾盖离掌55px', '第一击尾盖触掌；掌垫轻受力',
 '第一击弹离，间隙30px', '回收到间隙55px，停住左掌',
 '第二击向掌靠近，间隙23px', '第二击尾盖触掌；独立第二接触',
 '第二击弹离，间隙35px', '回操作角度，左手靠近前段尚未包托，眼回开关',
 '左手重新托稳；右拇指第二次向ON推，尚未到位', '第二次到ON，灯亮；先眼后头确认',
 '眉眼松开，整个头略迎光向右，不只挪五官', '稳定持握向画右，留亮灯结果与接S10的方向']
GAZE = ['switch']*5 + ['tail_contact']*8 + ['switch','switch','lamp_rim','lamp_rim','screen_right']
STATES = ['OFF','OFF','ON','ON','OFF','OFF','OFF','OFF','OFF','OFF','OFF','OFF','OFF','OFF','TRANSIT','ON','ON','ON']
BEATS = {14:'switch_on_failed', 26:'switch_reset_off',42:'tail_tap_1',56:'tail_tap_2',73:'switch_on_light'}
P = np.array([820.,750.])
H = 250.
U = F = 200.

def a(p): return np.asarray(p, dtype=float)
def unit(deg):
    r=math.radians(deg)
    return a([math.cos(r),math.sin(r)])
def ik(s,w,side):
    d=w-s; length=np.linalg.norm(d)
    if not 0 < length < U+F: raise ValueError(('unreachable', s,w))
    mid=s+d/2; n=a([-d[1],d[0]])/length
    z=math.sqrt(U*U-(length/2)**2)
    options=[mid+z*n,mid-z*n]
    return min(options,key=lambda p:p[0]) if side=='near' else max(options,key=lambda p:p[0])
def rounded(v):
    if isinstance(v,np.ndarray): return np.round(v,4).tolist()
    if isinstance(v,dict): return {k:rounded(x) for k,x in v.items()}
    if isinstance(v,list): return [rounded(x) for x in v]
    return v

poses=[]
for i,start in enumerate(STARTS):
    angle = -15. if i <=3 else -30. if i==4 else -60. if i <=12 else [-30.,-15.,-15.,-10.,-8.][i-13]
    u=unit(angle); n=a([-u[1],u[0]])
    gap = {5:32.,6:55.,7:0.,8:30.,9:55.,10:23.,11:0.,12:35.}.get(i,None)
    tail=P+u*gap if gap is not None else a([820.,740.])
    grip=tail+65*u
    nw=grip+a([-70.,-5.])
    palm=P-20*unit(-60.) if gap is not None else tail+120*u+30*n
    if i==13:
        palm=tail+120*u+60*n
    fw=palm+a([60.,-55.])
    dy=2. if i in [7,11] else 0.
    ns=a([650.,410.+dy]); fs=a([850.,410.+dy])
    ne=ik(ns,nw,'near'); fe=ik(fs,fw,'far')
    slide=104. if STATES[i]=='ON' else 98. if STATES[i]=='TRANSIT' else 92.
    thumb=tail+slide*u-21*n
    pose={
      'id':f'd{i+1:02d}', 'f':start, 'hold':(STARTS[i+1] if i+1<len(STARTS) else 96)-start,
      'draw':ACTIONS[i], 'gaze':GAZE[i], 'switch':STATES[i], 'light_on':i>=15,
      'contacts': ['right_fingers_barrel'] + (['tail_left_palm'] if i in [7,11] else ['left_fingers_front_barrel'] if gap is None and i!=13 else []),
      'head':{'center':[745.+(5 if i>=16 else 0),245.-(3 if i>=16 else 0)],'width':245.,'height':250.,
              'pitch_deg_suggestion':5 if 5<=i<=12 else 0, 'yaw_deg_suggestion':25 if i>=16 else 15,
              'note':'整头体积/耳/发根/颈一起转，角度为意图而非成图实测'},
      'joints':{'near_shoulder':ns,'near_elbow':ne,'near_wrist':nw,'far_shoulder':fs,'far_elbow':fe,'far_wrist':fw,'waist':a([750.,580.])},
      'prop':{'tail':tail,'lamp':tail+175*u,'grip_material_s':65.,'grip':grip,'axis_deg':angle,
              'length':175.,'barrel_diameter':42.,'head_diameter':58.,'switch_off_s':92.,'switch_on_s':104.,
              'thumb_tip':thumb,'left_palm':palm,'left_contact_surface':P if gap is not None else None,
              'left_support_material_s':120. if gap is None and i!=13 else None,
              'tail_palm_gap':gap,'palm_mode':'endcap_receiver' if gap is not None else 'reach_front_support' if i==13 else 'front_support'},
      'layer_order_back_to_front':['far_arm_gray210','torso_gray150','near_arm_gray65'],
      'events':[BEATS[start]] if start in BEATS else [], 'status':'PROPOSED_REFERENCE_NOT_FROZEN'
    }
    poses.append(pose)

model={
 'shot':'S09','status':'REFERENCE_ONLY_ASTRA_FREEZE_REQUIRED','fps':24,'dur':96,'canvas':[1536,864],
 'frame_convention':'镜内0起，闭区间展示；hold为帧数，结束为96的开区间',
 'coordinate_system':'最终画稿建议画布，x右y下；不是旧x09坐标，也未换算现有相机',
 'camera_proposal':{'view':'腰以上，略正于旧3/4，人物朝画右15度；双肘与双腕完整入画',
                    'locked_canvas':True,'face_box':[622.5,120,867.5,370], 'waist_anchor':[750,580],
                    'background':'电视柜后方虚化；马灯画右暖光；亮后冷白束朝画右',
                    'integration':'仅构图提案；Astra负责场景相机配准，不能当Opus已批准参数'},
 'proportion':{'head_unit':250.,'head_definition':'发冠至下颏，不计呆毛/马尾；源三视约160px',
               'shoulder_span':200.,'upper_arm_rest':200.,'forearm_rest':200.,'hand_wrist_to_fingertip':95.,
               'palm_width':56.,'shoulder_to_waist':170.,'full_height_hint_H':5.575,
               'measurement_status':'源图人工目测，衣内关节为推定；.8H双臂是待冻结构造值，并非从旧动作反推'},
 'poses':rounded(poses)
}
HERE.joinpath('geometry/S09_reference_v1.json').write_text(json.dumps(model,ensure_ascii=False,indent=2)+'\n')
opening={'note':'本独占目录内S09提案，不修改共享opening_plan。所有18张尚未绘制。','S09':{'dur':96,'fps':24,'who':'小满腰以上近景，近右手持筒，远左掌承击','frames':[[p['f'],p['draw']] for p in poses]}}
HERE.joinpath('exposure.json').write_text(json.dumps(opening,ensure_ascii=False,indent=2)+'\n')
with HERE.joinpath('exposure.csv').open('w',newline='') as f:
    w=csv.writer(f,lineterminator='\n'); w.writerow(['id','start_frame_0','end_frame_inclusive','hold','start_seconds','action','gaze','switch','light_on','event'])
    for p in poses:w.writerow([p['id'],p['f'],p['f']+p['hold']-1,p['hold'],f"{p['f']/24:.6f}",p['draw'],p['gaze'],p['switch'],p['light_on'],';'.join(p['events'])])

def save(fig,path):
    fig.savefig(HERE/path,dpi=150,facecolor='white',bbox_inches='tight')
    plt.close(fig)
def line(ax,p,q,color,width,**kw):ax.plot([p[0],q[0]],[p[1],q[1]],color=color,lw=width,solid_capstyle='round',**kw)
def dot(ax,p,label=None):
    ax.add_patch(Circle(p,7,facecolor='white',edgecolor='#146885',lw=1.5,zorder=12))
    if label:ax.text(p[0]+12,p[1]-10,label,fontsize=8,zorder=15,color='#146885')
def prop(ax,p,detail=False):
    pr=p['prop']; t=a(pr['tail']); u=unit(pr['axis_deg']); n=a([-u[1],u[0]])
    def point(s,r):return t+s*u+r*n
    barrel=[point(0,-21),point(143,-21),point(143,21),point(0,21)]
    ax.add_patch(Polygon(barrel,facecolor='#c96556',edgecolor='#393939',lw=1.4,zorder=7))
    lamp=[point(143,-29),point(175,-29),point(175,29),point(143,29)]
    ax.add_patch(Polygon(lamp,facecolor='#d5dde1',edgecolor='#393939',lw=1.4,zorder=8))
    line(ax,point(0,-21),point(0,21),'#222222',2,zorder=9)
    line(ax,point(85,-24),point(111,-24),'#333333',4,zorder=9)
    dot(ax,pr['thumb_tip'])
    ax.text(*point(110,-48),p['switch'],fontsize=8,color='#333333',zorder=15)
    # Grip collar is only a material-point marker, not generated fingers.
    ax.add_patch(Ellipse(pr['grip'],42,64,angle=pr['axis_deg']+90,fill=False,edgecolor='#1a627e',lw=2,zorder=10))
    if p['light_on']:
        h=a(pr['lamp']); line(ax,h+8*u,h+160*u,'#e4ba43',3,zorder=7)
        ax.text(*(h+65*u-25*n),'代码光接口',fontsize=8,color='#8a6b16')
    if detail:
        for s,label in [(0,'尾盖 s=0'),(65,'右手环握 s=65'),(120,'前托 s=120'),(175,'灯口 s=175')]:
            loc=point(s,0); ax.text(*(loc-70*n),label,fontsize=8,zorder=20,ha='center',rotation=0)

def draw_pose(ax,p,labels=False):
    j={k:a(v) for k,v in p['joints'].items()}; pr=p['prop']
    ax.set_xlim(440,1160);ax.set_ylim(830,75);ax.set_aspect('equal');ax.axis('off')
    # All shaded geometry is construction notation, not a character silhouette.
    line(ax,j['far_shoulder'],j['far_elbow'],'#d2d2d2',28,zorder=1)
    line(ax,j['far_elbow'],j['far_wrist'],'#d2d2d2',24,zorder=1)
    ax.add_patch(Polygon([(665,395),(835,395),(860,445),(828,580),(660,580),(625,445)],facecolor='#969696',alpha=.82,zorder=2))
    line(ax,j['far_shoulder'],j['far_shoulder']+(j['far_elbow']-j['far_shoulder'])*.22,'#555555',1.5,ls='--',zorder=3)
    line(ax,j['near_shoulder'],j['near_elbow'],'#414141',29,zorder=5)
    line(ax,j['near_elbow'],j['near_wrist'],'#414141',24,zorder=5)
    line(ax,j['near_wrist'],a(pr['grip']),'#414141',14,zorder=6)
    line(ax,j['far_wrist'],a(pr['left_palm']),'#d2d2d2',18,zorder=6)
    palm=a(pr['left_palm'])
    ax.add_patch(Ellipse(palm,74,40,angle=30 if pr['palm_mode']=='endcap_receiver' else pr['axis_deg'],facecolor='#dedede',edgecolor='#555555',lw=1.2,zorder=6))
    # Contact surface is normal to the flashlight axis during tapping.
    if pr['palm_mode']=='endcap_receiver':
        n=unit(30); line(ax,P-30*n,P+30*n,'#4b8675',3,zorder=11)
        if pr['tail_palm_gap']==0:ax.add_patch(Circle(P,15,fill=False,edgecolor='#c23e27',lw=2,zorder=15))
    head=p['head']; ax.add_patch(Ellipse(head['center'],head['width'],head['height'],fill=False,edgecolor='#777777',ls='--',lw=1.5,zorder=4))
    hc=a(head['center']); eye=hc+a([53.,29.]);dot(ax,eye)
    target=a(pr['thumb_tip']) if p['gaze']=='switch' else a(pr['tail']) if p['gaze']=='tail_contact' else a(pr['lamp']) if p['gaze']=='lamp_rim' else a([1140.,450.])
    direction=(target-eye)/np.linalg.norm(target-eye)
    ax.annotate('',xy=eye+70*direction,xytext=eye,arrowprops={'arrowstyle':'->','color':'#846094','lw':1.5})
    ax.text(hc[0]-84,hc[1]+5,'头体积 H=250',color='#666666',fontsize=8)
    line(ax,[735,370],[735,395],'#777777',3,zorder=4)
    prop(ax,p)
    for key,loc in j.items():dot(ax,loc,key.replace('near_','N ').replace('far_','F ') if labels else None)
    ax.text(450,805,'灰块/关节/接触点 = 技术参考，非人物画稿',fontsize=8,color='#a43b35')
    ax.text(455,110,f"{p['id']} · F{p['f']:03d} × {p['hold']}",fontsize=12,weight='bold')
    ax.text(455,140,p['draw'],fontsize=8)

# Source-based measurement board: actual artwork is displayed, never repainted.
source=Image.open(REPO/'collab/refs/xiaoman_turnaround_v4_draft.png')
fig,(ax,txt)=plt.subplots(1,2,figsize=(12,9),gridspec_kw={'width_ratios':[1,1.15]})
ax.imshow(source);ax.set_xlim(165,470);ax.set_ylim(980,20);ax.axis('off')
landmarks={'C':(325,64),'CH':(325,224),'NS':(260,280),'NE':(239,402),'NW':(210,524),'NT':(202,585),'FS':(385,280),'FE':(405,402),'FW':(431,524),'FT':(438,585),'WA':(325,389),'SOLE':(325,956)}
for name,loc in landmarks.items():dot(ax,loc,name)
for names in [('NS','NE','NW'),('FS','FE','FW')]:
    for x,y in zip(names,names[1:]):line(ax,landmarks[x],landmarks[y],'#14758e',1.5)
for y in [64,224,280,389,956]:ax.axhline(y,color='#bb8f32',lw=.8,ls='--')
txt.axis('off');txt.text(0,.98,'小满比例母源 · 人工读图',va='top',fontsize=20,weight='bold')
notes=[
 '实看源：xiaoman_turnaround_v4_draft.png（1536×1024）',
 'C发冠(325,64) → CH下颏(325,224)：H≈160源px',
 '不计呆毛、马尾；全身发冠→鞋底≈892px = 5.575H',
 '肩心 NS(260,280) / FS(385,280)：跨度≈125px=.78H',
 '近上臂 NS→NE≈124px；近前臂 NE→NW≈125px',
 '两臂静置长度接近 .8H / .8H，衣内肩肘属推定',
 '腕→指尖≈62px=.39H；掌宽约36px=.23H',
 '肩线280 → 腰389≈109px=.68H',
 '',
 '本次构造单位 H=250：双上臂200、双前臂200',
 '肩跨度200；腕至指尖95；掌宽56；肩至腰170',
 '18态用同一骨长做IK；投影短缩须沿真实透视复核',
 '不能把衣外缘当关节；这些是绘图尺标，不是假装实测骨骼',
 '',
 '身份：棕黑刘海/双低马尾红花绳、白圆领、黄底白点裙',
 '眼型与瞳孔取 current03 表情表；疑惑→专注→轻松',
 '旧 x09 只看身份/旧手电外观；不取旧双臂结构与拍筒动作',
 '',
 '本页为源图测量标注，非新人物画稿；待 Astra 冻结。']
txt.text(0,.89,'\n\n'.join(notes),va='top',fontsize=10)
fig.suptitle('S09 第一阶段 / 人物比例与骨长参考（非生成画稿）',fontsize=17)
save(fig,'reference/01_identity_measurements.png')

fig,axs=plt.subplots(2,4,figsize=(18,10))
for ax,idx in zip(axs.flat,[0,3,5,6,7,11,15,17]):draw_pose(ax,poses[idx])
fig.suptitle('S09 八关键 · 同机位三档层次 / 近臂深灰、躯干中灰、远臂浅灰 / 技术参考非画稿',fontsize=16)
save(fig,'reference/02_keyposes_and_layers.png')
for p in poses:
    fig,ax=plt.subplots(figsize=(8,8));draw_pose(ax,p,labels=True)
    save(fig,f"reference/poses/{p['id']}_F{p['f']:03d}.png")

fig,axs=plt.subplots(2,3,figsize=(15,9))
for ax,idx in zip(axs.flat,[6,7,8,10,11,12]):
    p=poses[idx];draw_pose(ax,p)
    ax.set_xlim(735,980);ax.set_ylim(805,530)
    for artist in list(ax.texts):artist.remove()
    ax.text(.02,.98,f"F{p['f']:03d}: 间隙 {p['prop']['tail_palm_gap']:.0f}px",transform=ax.transAxes,va='top',fontsize=12,color='#a43b35',bbox={'facecolor':'white','edgecolor':'none','alpha':.85})
    ax.text(.02,-.07,'近手随筒刚移；左掌守位；绿线=受击面',transform=ax.transAxes,fontsize=9)
fig.suptitle('两次尾盖接触 · 离掌→接触→弹离 / 图为接触几何，手指需真实绘制',fontsize=16)
fig.text(.5,.01,'技术构造参考，非人物画稿',ha='center',color='#a43b35',fontsize=10)
fig.subplots_adjust(hspace=.3,top=.91,bottom=.08)
save(fig,'reference/03_two_contact_triplets.png')

fig,axs=plt.subplots(1,3,figsize=(16,6))
for ax,idx in zip(axs,[1,2,15]):
    p=poses[idx];draw_pose(ax,p);ax.set_xlim(750,1040);ax.set_ylim(805,600)
    for artist in list(ax.texts):artist.remove()
    ax.text(.02,.98,f"F{p['f']:03d} / {p['switch']}",transform=ax.transAxes,va='top',fontsize=14,color='#a43b35',bbox={'facecolor':'white','edgecolor':'none','alpha':.85})
    t=a(p['prop']['tail']);u=unit(p['prop']['axis_deg']);n=a([-u[1],u[0]])
    for s,label,color in [(65,'A','#146885'),(104 if p['switch']=='ON' else 92,'B','#846094'),(120,'C','#4b8675')]:
        loc=t+s*u;dot(ax,loc);ax.text(*(loc-40*n),label,fontsize=11,color=color,ha='center')
    ax.text(.02,-.08,'A 环握s65  /  B 滑键s92→104  /  C 前托s120',transform=ax.transAxes,fontsize=9)
fig.suptitle('刚体与滑键接口 · 右指环握不松，右拇指92→104；左手前段托住 / 非画稿',fontsize=15)
fig.subplots_adjust(top=.88,bottom=.15)
save(fig,'reference/04_grip_and_switch.png')

fig,axs=plt.subplots(3,6,figsize=(20,11))
for ax,p in zip(axs.flat,poses):draw_pose(ax,p)
fig.suptitle('S09 18曝光总览 · 0起帧 / 96帧 / 4秒 · 技术构造参考，不可作为人物成片',fontsize=16)
save(fig,'reference/05_all18_reference.png')

prefix='''未执行的绘图提示词；本文件仅供Astra冻结后审用。画布1536×864。参考顺序：已冻结的本态技术参考、三视v4身份、current03眼型、上一张已合格真画稿。技术参考的灰块/圆/关节/字不进入成图。以真实二维绘画完成小满腰以上近景；棕黑刘海、双低马尾红花绳、白圆领黄底白点裙；近右手持续环握红色旧手电，远左手按本态托持或张掌受击。按已冻结250头高/.8H上臂/.8H前臂，完整重画自然袖口—上臂—肘—前臂—腕—掌，所有关节连接正确。两臂不交叉、肘分开、腕离躯干有可见间隙，三层遮挡不含糊。手电总长175、筒径42、灯头径58；尾盖/筒身/灯头同轴，环握材料点s65、前托s120不滑；侧滑键OFF s92/ON s104。人物中性底色，透明背景；不烘焙马灯暖光/手电光束。不要代码人物、不要把源图整张当成画稿、不要复制旧拍筒动作。整头动作须连同耳/发根/马尾/颈体积绘制；眼球在眼眶内跟随目标。只修改本态允许活动部位，前一合格画稿的身份、衣纹与画布配准保持连续。五指自然、拇指与滑键真实相触、手不穿筒，接触不是悬空。'''
with HERE.joinpath('prompts/planned_prompts.jsonl').open('w') as f:
    for p in poses:
        prompt=prefix+'\n本态：'+p['draw']+f"。起F{p['f']:03d}停{p['hold']}帧。视线目标={p['gaze']}；开关={p['switch']}；光接口={'开启但不烘焙' if p['light_on'] else '关闭'}。"+'\n精确构造参考与坐标：'+json.dumps(rounded(p),ensure_ascii=False)
        f.write(json.dumps({'id':p['id'],'status':'PLANNED_NOT_EXECUTED','prompt':prompt,'reference_paths':[f"reference/poses/{p['id']}_F{p['f']:03d}.png",'collab/refs/xiaoman_turnaround_v4_draft.png','collab/refs/xiaoman_expressions_current03.png'],'previous_approved_artwork':None,'note':'须先填入上一张实际合格原件路径与SHA再执行；d01无前态，先做首图门。'},ensure_ascii=False)+'\n')

source_paths=['collab/README.md','collab/claude.md','collab/partner.md','docs/keyframes/scenes03_12_drawing_plan.md','collab/refs/xiaoman_turnaround_v4_draft.png','collab/refs/xiaoman_expressions_current03.png','assets/chars/x09_flashlight.png','assets/chars/x09_flashlight_slap.png','collab/keyposes/20261018_scenes03_12/S09/S09_code_F000-F046.jpg','collab/keyposes/20261018_scenes03_12/S09/S09_code_F048-F094.jpg']
sources=[]
for path in source_paths:
    raw=(REPO/path).read_bytes()
    entry={'repo_path':path,'commit':BASE,'sha256':hashlib.sha256(raw).hexdigest(),'git_blob':subprocess.check_output(['git','rev-parse',f'{BASE}:{path}'],cwd=REPO,text=True).strip()}
    if path.endswith(('.png','.jpg')):
        im=Image.open(REPO/path);entry.update({'size':list(im.size),'mode':im.mode,'viewed':True,'role':'identity_only' if '/refs/' in path or '/chars/' in path else 'camera_light_duration_only'})
    sources.append(entry)
HERE.joinpath('provenance/sources.json').write_text(json.dumps({'base_commit':BASE,'sources':sources},ensure_ascii=False,indent=2)+'\n')

checks=[]
for p in poses:
    j={k:a(v) for k,v in p['joints'].items()};pr=p['prop']
    lengths={}
    for side in ['near','far']:
        lengths[side+'_upper']=float(np.linalg.norm(j[side+'_elbow']-j[side+'_shoulder']))
        lengths[side+'_fore']=float(np.linalg.norm(j[side+'_wrist']-j[side+'_elbow']))
    def bbox_gap(w):
        return math.hypot(max(625-w[0],w[0]-860,0),max(395-w[1],w[1]-580,0))
    wrist_angles={}
    for side,palm in [('near',pr['grip']),('far',pr['left_palm'])]:
        fore=j[side+'_wrist']-j[side+'_elbow']; hand=a(palm)-j[side+'_wrist']
        wrist_angles[side]=math.degrees(math.acos(np.clip(np.dot(fore,hand)/np.linalg.norm(fore)/np.linalg.norm(hand),-1,1)))
    checks.append({'id':p['id'],'f':p['f'],'bone_lengths':lengths,'min_wrist_distance_from_torso_bbox':min(bbox_gap(j['near_wrist']),bbox_gap(j['far_wrist'])),
                   'wrist_direction_change_deg':wrist_angles,
                   'elbow_separation':float(np.linalg.norm(j['near_elbow']-j['far_elbow'])),
                   'prop_length':float(np.linalg.norm(a(pr['lamp'])-a(pr['tail']))),'tail_palm_gap':pr['tail_palm_gap']})
assert sum(p['hold'] for p in poses)==96
assert all(abs(x-200)<1e-6 for c in checks for x in c['bone_lengths'].values())
assert all(c['min_wrist_distance_from_torso_bbox']>=56 for c in checks)
assert all(x<45 for c in checks for x in c['wrist_direction_change_deg'].values())
assert [p['f'] for p in poses if 'tail_left_palm' in p['contacts']]==[42,56]
HERE.joinpath('qa/geometry_checks.json').write_text(json.dumps({'scope':'数值只核构造，不代表绘画解剖/自然度通过','checks':checks},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'poses':len(poses),'total_frames':sum(p['hold'] for p in poses),'min_wrist_distance':min(c['min_wrist_distance_from_torso_bbox'] for c in checks),'max_wrist_direction_change':max(x for c in checks for x in c['wrist_direction_change_deg'].values()),'min_elbow_separation':min(c['elbow_separation'] for c in checks),'artworks_generated':0},ensure_ascii=False))
