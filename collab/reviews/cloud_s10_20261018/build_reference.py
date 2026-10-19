#!/usr/bin/env python3
"""S10 review diagrams only. Never creates production character drawings."""
import csv
import hashlib
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Polygon, Rectangle, FancyArrowPatch
import numpy as np
from PIL import Image

OUT = Path(__file__).resolve().parent
REPO = OUT.parents[2]
BASE = '3d66443997cee24b64059e6f53f7d46968a3a05c'
FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
if Path(FONT).exists():
    font_manager.fontManager.addfont(FONT)
    plt.rcParams['font.family'] = font_manager.FontProperties(fname=FONT).get_name()
plt.rcParams.update({'axes.unicode_minus': False, 'font.size': 12})
POSES = [
    (0, 24, 0, 0, 0, 0, .85, '自然看向小满'),
    (24, 3, 0, 0, 0, 0, .55, '光先到，眼先收'),
    (27, 3, 10, 2, 1, 2, .22, '整头连颈开始转'),
    (30, 3, 22, 4, 3, 5, .10, '鼻、耳、眼镜同步'),
    (33, 12, 32, 6, 4, 8, .07, '躲光峰态，微收颏'),
    (45, 27, 28, 5, 3, 7, .17, '仍偏头，稍松下来'),
    (72, 24, 20, 3, 2, 4, .35, '慢慢缓和，眼看左'),
    (96, 24, 14, 2, 1, 2, .52, '略侧头看小满'),
]
C7 = np.array([960., 835., 0.])
NECK = np.array([0., -170., -65.])
LANDMARKS = {
    'AO_upper_neck': [0, 0, 0], 'hair_crown': [0, -540, 0],
    'chin': [0, 65, 205], 'nose_tip': [0, -155, 285],
    'near_ear_root': [-252, -145, 0], 'far_ear_root': [252, -145, 0],
    'near_eye': [-112, -218, 218], 'far_eye': [112, -218, 218],
    'bridge_on_nose': [0, -210, 240], 'bun_root': [-90, -50, -200],
    'beads_root': [-235, -155, -100],
}

def rz(a):
    a = math.radians(a); c, s = math.cos(a), math.sin(a)
    return np.array([[c,-s,0],[s,c,0],[0,0,1]])

def rotation(yaw, roll, pitch):
    y, p = math.radians(yaw), math.radians(pitch)
    Y = np.array([[math.cos(y),0,math.sin(y)],[0,1,0],[-math.sin(y),0,math.cos(y)]])
    P = np.array([[1,0,0],[0,math.cos(p),math.sin(p)],[0,-math.sin(p),math.cos(p)]])
    return rz(roll) @ Y @ P

def geometry(pose):
    f, hold, yaw, roll, pitch, lean, eye, action = pose
    n = C7 + rz(lean) @ NECK
    rot = rotation(yaw, roll, pitch)
    pts = {k: (n + rot @ np.array(v)).tolist() for k,v in LANDMARKS.items()}
    return n, rot, pts

def setup(ax):
    ax.set(xlim=(0,1920), ylim=(1080,0), aspect='equal')
    ax.set_facecolor('#faf9f5')
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values(): spine.set_color('#bcbab3')

def line3(ax, points, n, rot, color='#595959', lw=1, ls='-', alpha=1):
    q = np.asarray(points) @ rot.T + n
    ax.plot(q[:,0], q[:,1], color=color, lw=lw, ls=ls, alpha=alpha)

def draw_pose(ax, pose, detail=False):
    setup(ax)
    f, hold, yaw, roll, pitch, lean, eye, action = pose
    n, rot, pts = geometry(pose)
    # Three tones describe arm/torso ordering, not a finished body.
    ax.add_patch(Polygon([[1270,872],[1430,920],[1530,1080],[1280,1080]], facecolor='#dddddd', edgecolor='#777'))
    ax.add_patch(Polygon([[650,872],[850,815],[1070,815],[1270,872],[1310,1080],[610,1080]], facecolor='#a8a8a8', edgecolor='#666'))
    ax.add_patch(Polygon([[650,872],[500,920],[430,1080],[650,1080]], facecolor='#555555', edgecolor='#333'))
    # The neck skin envelope is a connection guide; C7->AO is fixed length.
    ax.add_patch(Polygon([[856,835],[n[0]-80,n[1]+30],[n[0]+80,n[1]+30],[1064,835]], facecolor='#d1c9ba', edgecolor='#7b6b56'))
    ax.plot([C7[0],n[0]], [C7[1],n[1]], color='#c76a20', lw=2)
    ax.scatter([C7[0],n[0]],[C7[1],n[1]],s=15,color='#c76a20',zorder=10)
    # Rigid cranium wireframe. Hidden meridians are dashed construction.
    a = np.linspace(0,2*np.pi,100)
    for phi in [-60,-30,0,30,60]:
        ph = math.radians(phi)
        ring = np.column_stack((265*np.cos(ph)*np.cos(a), -260+280*np.sin(ph)*np.ones_like(a), 220*np.cos(ph)*np.sin(a)))
        line3(ax,ring,n,rot,'#9a9a9a',.7,':')
    for theta in [0,45,90,135]:
        th=math.radians(theta)
        ring=np.column_stack((265*np.cos(a)*math.cos(th),-260+280*np.sin(a),220*np.cos(a)*math.sin(th)))
        line3(ax,ring,n,rot,'#777777',.7,':')
    # Jaw/chin contour deliberately stays a measured volume guide.
    jaw=np.array([[-212,-210,155],[-222,-70,185],[-175,25,200],[0,65,205],[175,25,200],[222,-70,185],[212,-210,155]])
    line3(ax,jaw,n,rot,'#303030',1.5)
    line3(ax,[[0,-480,180],[0,-220,230],[0,-155,285],[0,65,205]],n,rot,'#176a89',1.3)
    # Eyeglass planes attached to the same head transform.
    for x in [-112,112]:
        lens=np.column_stack((x+87*np.cos(a),-218+77*np.sin(a),np.full_like(a,234)))
        line3(ax,lens,n,rot,'#444444',1.1)
        line3(ax,[[x-41,-218,240],[x,-218-eye*25,240],[x+41,-218,240]],n,rot,'#176a89',1.4)
    line3(ax,[[-25,-217,236],[0,-210,240],[25,-217,236]],n,rot,'#444444',1.2)
    for x, key in [(-252,'near_ear_root'),(252,'far_ear_root')]:
        ear=np.column_stack((x+23*np.cos(a),-145+58*np.sin(a),np.zeros_like(a)))
        line3(ax,ear,n,rot,'#414141',1.0,'--' if x>0 and yaw>=15 else '-')
        line3(ax,[[np.sign(x)*200,-218,230],[x,-160,0]],n,rot,'#555',1,'--' if x>0 and yaw>=15 else '-')
    bun=np.column_stack((-90+108*np.cos(a),-50+82*np.sin(a),np.full_like(a,-200)))
    line3(ax,bun,n,rot,'#777',1,'--')
    for key,col in [('nose_tip','#176a89'),('near_ear_root','#414141'),('far_ear_root','#8a8a8a'),('bun_root','#777')]:
        p=pts[key];ax.scatter(p[0],p[1],s=13,color=col,zorder=8)
    # Fixed collar and lower-chest registration points.
    ax.plot([856,960,1064],[835,947,835],color='white',lw=2)
    ax.scatter([650,1270,960],[872,872,1040],s=13,c='#b72c35',zorder=12)
    ax.axhline(1080,color='#a22',ls='--',lw=1)
    ax.text(40,1045,'双肘 / 腕 / 手在画外',fontsize=9,color='#444')
    if detail:
        for label,key,xy in [('鼻向画右','nose_tip',(1490,380)),('近耳 / 画左','near_ear_root',(80,500)),('远耳藏入轮廓','far_ear_root',(1450,610)),('盘发在后颅之后','bun_root',(70,720)),('AO 隐藏构造点','AO_upper_neck',(1360,760))]:
            p=pts[key]
            ax.annotate(label, xy=(p[0],p[1]),xytext=xy,fontsize=10,arrowprops={'arrowstyle':'-','color':'#777','lw':.8})
        ax.text(80,110,'手电从画左来 →',fontsize=12,color='#176a89')
        ax.text(1320,1020,'三档灰块仅示层次',fontsize=9,color='#444')
    ax.set_title(f'F{f:03d} × {hold}  |  {action}\nyaw {yaw}° / roll {roll}° / pitch {pitch}°',fontsize=11,pad=8)

def save(fig,name):
    fig.savefig(OUT/'reference'/name,dpi=130,facecolor='white',bbox_inches='tight')
    plt.close(fig)

def charts():
    fig,axes=plt.subplots(2,4,figsize=(19.2,9.2))
    for ax,p in zip(axes.flat,POSES): draw_pose(ax,p)
    fig.suptitle('S10 八态同机位｜结构参考，不是人物画稿｜120帧 / 24fps / 5秒',fontsize=19)
    fig.text(.5,.025,'头颅、下颌、双耳、眼镜、发根统一转动；颈面连接固定领口。虚线是隐藏构造，不画到成品。',ha='center',fontsize=12)
    fig.subplots_adjust(top=.88,bottom=.09,hspace=.4,wspace=.12)
    save(fig,'01_eight_poses.png')
    d=OUT/'reference/poses';d.mkdir(exist_ok=True)
    for p in POSES:
        fig,ax=plt.subplots(figsize=(15.36,8.64));draw_pose(ax,p,True)
        fig.text(.5,.02,'技术构造图 / 非生成输出 / 非成片人物',ha='center',color='#a22')
        save(fig,f'poses/F{p[0]:03d}.png')
    # Actual source artwork is unchanged; this figure overlays a technical reading.
    fig,axes=plt.subplots(1,2,figsize=(16,10),gridspec_kw={'width_ratios':[1,1.2]})
    ax=axes[0];im=Image.open(REPO/'collab/refs/grandma_turnaround_current03_draft.png')
    ax.imshow(im);ax.set(xlim=(355,720),ylim=(770,0));ax.axis('off')
    obs={'发顶':(531,31),'下颏':(532,181),'左肩估计':(455,229),'右肩估计':(615,229),'左肘估计':(414,355),'右肘估计':(650,355),'左腕估计':(409,451),'右腕估计':(655,451)}
    for k,(x,y) in obs.items():
        estimated='估计' in k
        ax.scatter(x,y,s=33,facecolors='white' if estimated else '#222',edgecolors='#cc6a26',zorder=5)
        ax.annotate(k,(x,y),xytext=(-64 if x<532 else 10,0),textcoords='offset points',fontsize=10,color='#6d3b17')
    for chain in [[(455,229),(414,355),(409,451)],[(615,229),(650,355),(655,451)]]:
        ax.plot(*zip(*chain),ls='--',color='#cc6a26',lw=1.5)
    ax.plot([690,690],[31,181],color='#176a89',lw=2);ax.text(695,110,'H ≈ 150px',rotation=90,color='#176a89')
    ax.set_title('三视图03前视原图读点\n空心点＝藏于软组织的估计，非可见骨点',fontsize=13)
    ax=axes[1];ax.axis('off')
    ax.text(0,.97,'比例与骨长分开记录',fontsize=22,va='top')
    text='''观察量（原图坐标，人工约量）
发顶 (531,31) → 下颏 (532,181)：H≈150±5 px
含发到鞋底约719 px，约4.8H
肩、肘、腕估计误差可达±10–15 px
二维上臂约132 px，前臂约96 px
透视／软组织造成缩短，不能当真实骨长

S10固定构造（画布等效px，不是厘米）
头高约610；两肩关节间620
C7 (960,835,0) → AO (960,665,-65)
颈轴长182.003；8态只旋转，不拉长
近／远肩与下胸配准点固定
画外上臂0.92H、前臂0.75H、手0.50H
这三项是构造包络假设，不是源图实测

绘图约束
发顶完整，低盘发不裁掉
眯眼只遮虹膜，镜框不跟着缩
近耳露出增多；远耳遮住，不压瘪
整头重画，颈面连续接回固定领口
双手不进入本镜；不新增挡光动作'''
    ax.text(0,.87,text,fontsize=14,va='top',linespacing=1.65)
    fig.suptitle('S10 比例读点与固定构造｜实际源图标注，源PNG未修改',fontsize=19)
    save(fig,'02_observed_proportions.png')
    fig,axes=plt.subplots(1,3,figsize=(20,7.3))
    for ax,p in zip(axes,[POSES[0],POSES[3],POSES[4]]): draw_pose(ax,p,True)
    fig.suptitle('整头＋颈三关键｜0° → 22° → 32°｜角度是目标，不是未来实图测量',fontsize=19)
    fig.text(.5,.04,'峰态：画左近耳保留体积，画右远耳藏入；眼镜各部分同颅体转；AO沿颈轴弧走，C7／衣领固定。',ha='center',fontsize=12)
    fig.subplots_adjust(top=.84,bottom=.15,wspace=.12)
    save(fig,'03_whole_head_neck.png')
    fig,axes=plt.subplots(1,2,figsize=(17,8.8))
    draw_pose(axes[0],POSES[4],True)
    ax=axes[1];ax.axis('off')
    ax.text(0,.98,'遮挡与接触接口',fontsize=23,va='top')
    y=.87
    for label,c in [('远臂：后层，独立接远肩','#ddd'),('躯干：中层，固定领／胸','#aaa'),('近臂：前层，独立接近肩','#555')]:
        ax.add_patch(Rectangle((0,y-.02),.09,.04,color=c,transform=ax.transAxes))
        ax.text(.13,y,label,fontsize=14,va='center');y-=.085
    ax.text(0,.58,'双肘／腕／手在画外，无手部接触任务。\n不准加挡光手、不画两臂交叉。',fontsize=14,linespacing=1.7,va='top')
    ax.text(0,.43,'① 鼻梁接镜桥，镜腿后端接耳根\n② 下颌遮颈，颈面连续接固定领口\n③ 盘发在后颅之后；红珠连发根\n④ 远耳被遮，虚线轮廓不进成品',fontsize=13,linespacing=1.7,va='top')
    ax.text(0,.16,'场景光单列：F022到脸 → F024眯眼\n画左冷白手电；画右暖色马灯\n人物中性底色；光束不跟着头贴图移动',fontsize=13,color='#176a89',linespacing=1.7,va='top')
    fig.suptitle('S10 层次／接触图｜仅用于审构图，灰块不是生产素材',fontsize=19)
    fig.subplots_adjust(top=.84,wspace=.17)
    save(fig,'04_layers_contacts.png')

def data():
    frames=[]
    for p in POSES:
        f,hold,yaw,roll,pitch,lean,eye,action=p;n,rot,pts=geometry(p)
        frames.append({'frame':f,'hold':hold,'end_frame_inclusive':f+hold-1,'action':action,
                       'yaw_deg':yaw,'roll_deg':roll,'pitch_deg':pitch,'neck_lean_deg':lean,
                       'eye_open_relative':eye,'C7_xyz':C7.tolist(),'AO_xyz':n.tolist(),
                       'neck_length':float(np.linalg.norm(n-C7)),'landmarks_xyz':pts,
                       'reference':f'reference/poses/F{f:03d}.png','production_asset':None})
    plan={'status':'PROPOSED_NOT_FROZEN','stage':'reference_only','new_image_calls':0,'new_character_images':0,
          'baseline':BASE,'fps':24,'duration_seconds':5,'reference_canvas':[1920,1080],
          'S10':{'dur':120,'who':'奶奶固定头肩近景，扫光后整头连颈向画右躲光',
                 'frames':[[p[0],p[-1]] for p in POSES]},
          'coordinate_convention':'x screen right; y screen down; z toward camera; orthographic construction only',
          'fixed_registration':{'shoulders':[[650,872],[1270,872]],'collar_inner':[[856,835],[1064,835]],'lower_chest':[960,1040]},
          'light_cues':[{'frame':12,'cue':'scene beam approaches from screen left'}, {'frame':22,'cue':'scene beam reaches face'},
                        {'frame':24,'cue':'eyes narrow'}, {'frame':27,'cue':'whole head turn begins'},
                        {'frame':45,'cue':'beam eases away; no texture-baked light'}],
          'anatomy_warning':'Hidden joints and 3D depth are construction assumptions; not measured anatomy or production acceptance.',
          'exposures':frames}
    (OUT/'S10_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
    with (OUT/'S10_exposure.csv').open('w',newline='') as out:
        w=csv.writer(out,lineterminator='\n');w.writerow(['start_frame','end_frame_inclusive','hold_frames','start_seconds','yaw_target_deg','roll_target_deg','pitch_target_deg','eye_open_relative','action'])
        for f,hold,yaw,roll,pitch,lean,eye,action in POSES:w.writerow([f,f+hold-1,hold,f/24,yaw,roll,pitch,eye,action])
    sources=[
        ('collab/README.md','协作规则；本次直接指令覆盖共享分支与留言写入'),
        ('collab/claude.md','尾部13:25 / 13:40 / 13:50的批准、参考范围与分工'),
        ('collab/partner.md','最新历史撤回与真实绘图、整头审查标准'),
        ('docs/keyframes/scenes03_12_drawing_plan.md','S10五秒近景约八张'),
        ('collab/refs/grandma_expressions_current02.png','主身份，表情结构；已实际查看'),
        ('collab/refs/grandma_turnaround_current03_draft.png','明确通过的三视图03；已实际查看并标技术测点'),
        ('collab/refs/grandma_turnaround_current04_draft.png','已查看，未找到新通过指令；不用于生产身份冻结'),
        ('assets/chars/g10_squint.png','旧造型辅助；已实际查看；不作动作／颈长母版'),
        ('collab/reviews/20261016_1633/anim10_grandma/source_manifest.json','旧g10身份来源链'),
        ('collab/reviews/20261016_1633/anim10_grandma/independent_review.md','旧静态图审，不代新动作通过'),
        ('js/paint/shots/s10.js','只读旧机位、光源和时长；不沿抄人物动作'),
        ('docs/keyframes/opening_plan.json','只参考曝光表格式，不修改'),
    ]
    for n in ['S10_code_F000-F046.jpg','S10_code_F048-F094.jpg','S10_code_F096-F118.jpg']:
        sources.append(('collab/keyposes/20261018_scenes03_12/S10/'+n,'已实际查看；只参考机位、光、时长'))
    entries=[]
    for path,role in sources:
        raw=(REPO/path).read_bytes();e={'path':path,'commit':BASE,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'role':role}
        if path.endswith(('.png','.jpg')):
            with Image.open(REPO/path) as im:e.update(width=im.width,height=im.height,mode=im.mode)
        entries.append(e)
    manifest={'repository':'yiggeror/animation-competition','baseline':BASE,'sources':entries,
              'image_generation':{'exposed_tool':'image_gen.imagegen','executed_calls':0,'availability':'listed, untested pending reference freeze',
                                  'raw_generated_outputs':[], 'new_paid_services':False},
              'reference_method':'Python/matplotlib technical diagrams; source art remains unchanged; no generated production character.',
              'source_art_copy_policy':'Original sources remain at fixed repository paths; no duplicate large originals in this package.'}
    (OUT/'provenance/source_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    verify={'status':'reference_data_checks_only','exposures':len(frames),'sum_hold':sum(p[1] for p in POSES),
            'coverage':[[p[0],p[0]+p[1]-1] for p in POSES],
            'max_neck_length_delta':float(max(abs(x['neck_length']-np.linalg.norm(NECK)) for x in frames)),
            'fixed_C7':all(x['C7_xyz']==C7.tolist() for x in frames),
            'rendered_reference_images':12,
            'not_verified':['new character drawings','actual generated image tool return','final animation naturalness','scene lighting','audio sync']}
    assert sum(p[1] for p in POSES)==120
    assert [f for p in POSES for f in range(p[0],p[0]+p[1])]==list(range(120))
    assert verify['max_neck_length_delta']<1e-9
    (OUT/'qa/data_checks.json').write_text(json.dumps(verify,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':
    charts();data()
    print('S10: 8 exposures / 120 frames; 12 review diagrams. Production drawings: 0. Image calls: 0.')
