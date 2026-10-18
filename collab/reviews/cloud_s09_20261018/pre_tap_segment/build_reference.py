#!/usr/bin/env python3
"""Three complete arm/contact construction targets; never character artwork."""
from pathlib import Path
import json,math,os,hashlib
os.environ.setdefault('MPLCONFIGDIR','/tmp/s09-pre-tap-ref-mpl')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Polygon,Ellipse
from PIL import Image
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
for d in ['reference','requests','originals','candidates','qa','masks']:(ROOT/d).mkdir(exist_ok=True)
font_manager.fontManager.addfont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
plt.rcParams.update({'font.family':'Noto Sans CJK JP','font.size':11,'axes.unicode_minus':False})
mother=BASE/'switch_segment/candidates/d04_registered.png'
u=np.array([0.,-1.]);n=np.array([1.,0.])
P=np.array([940.,615.]);L=240.2052476443473
mother_j={'near_shoulder':[643,428],'near_elbow':[676,585],'near_wrist':[790,508],
          'far_shoulder':[819,420],'far_elbow':[879,586],'far_wrist':[925,508]}
new_j={'near_shoulder':[643,428],'near_elbow':[700,580],'near_wrist':[885,535],
       'far_shoulder':[819,420],'far_elbow':[837,585],'far_wrist':[890,625]}
states=[]
for id,f,hold in [('d05',26,5),('d06',31,6),('d07',37,5)]:
    j=dict(mother_j if id=='d05' else new_j)
    if id=='d05':tail=np.array([778.375314861461,485.2392947103274]);angle=math.atan2(-47.2292191435768,235.5163727959698)
    elif id=='d06':tail=P+u*35;angle=math.radians(-90)
    else:tail=P+u*55;angle=math.radians(-90);j['near_wrist']=[885,515]
    ax=np.array([math.cos(angle),math.sin(angle)]);nn=np.array([-ax[1],ax[0]])
    lamp=tail+ax*L
    projections={}
    for side in ['near','far']:
        s,e,w=[np.array(j[f'{side}_{part}'],float) for part in ['shoulder','elbow','wrist']]
        projections[side]={'upper_projected':float(np.linalg.norm(e-s)),'fore_projected':float(np.linalg.norm(w-e)),
                           'rest_length_each':200,'measurement':'manual source proxies / new projection choices; not true measured anatomy'}
        assert max(projections[side]['upper_projected'],projections[side]['fore_projected'])<=200
    # Centerline intersection gate, with finite-width reality deferred to actual art.
    def orient(a,b,c):
        v=np.array(b)-a;w=np.array(c)-a
        return float(v[0]*w[1]-v[1]*w[0])
    a,b,c,d=[np.array(j[k],float) for k in ['near_elbow','near_wrist','far_elbow','far_wrist']]
    cross=orient(a,b,c)*orient(a,b,d)<0 and orient(c,d,a)*orient(c,d,b)<0
    assert not cross
    states.append({'id':id,'frame':f,'hold':hold,'joints':j,'projection':projections,'tail':tail.tolist(),
      'lamp':lamp.tolist(),'axis_degrees':math.degrees(angle),'length':L,'switch':'OFF','light':False,
      'left_palm_face':None if id=='d05' else P.tolist(),'left_palm_normal':u.tolist(),
      'left_palm_band_n':[-36,12],'left_pad_s':[-32,0],
      'tail_gap_along_receiver_normal':None if id=='d05' else 35 if id=='d06' else 55,
      'near_forearm_far_forearm_centerlines_cross':cross,
      'intent':'same two-hand support; slide OFF, worried face retained' if id=='d05' else 'left releases and opens naturally with fingers pointing screen right, wrist at left heel; vertical torch tail aligned above pad; no contact' if id=='d06' else 'left holds receiver; right whole grip/prop withdraws20px vertically with no size change; no contact'})
payload={'status':'THREE_STATE_FULL_ARM_REFERENCE_FOR_SELF_REVIEW_BEFORE_GENERATION','canvas':[1536,864],
 'mother':str(mother.relative_to(BASE)),'mother_sha256':hashlib.sha256(mother.read_bytes()).hexdigest(),
 'head_unit':250,'rest_arm_lengths_each':200,'joint_uncertainty_source_registered':'shoulders under sleeves about±10, elbows±6, wrists±4; new points are intentions, not actual drawing measurements',
 'prop_length':L,'receiver_face':P.tolist(),'receiver_normal':u.tolist(),
 'reference_revision':'v2 after rejected call01-03: natural left palm with fingers screen right, wrist on left heel; vertical flashlight aligns tail above pad. Replaces forced left-pointing-palm reference, which produced reversed wrist attachment.',
 'limits':'Old F000 local near-hand envelope is NOT transferred to the newly rotated grip. D026 actual grip must be checked; D031/D037 actual palm thickness, wrist connection, limb depths and future knuckle clearance must be inspected. No F042 artwork allowed. Target centerline checks are not full silhouette or 3D proof.',
 'states':states}
(ROOT/'reference/three_states.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
for s in states:
    fig=plt.figure(figsize=(12.8,7.2),dpi=120);a=fig.add_axes([0,0,1,1]);a.set_xlim(0,1536);a.set_ylim(864,0);a.axis('off')
    a.imshow(Image.open(mother),extent=[0,1536,864,0],alpha=.13)
    j=s['joints']
    for side,col,z in [('far','#bbbbbb',2),('near','#3f454d',5)]:
        for p,q in [('shoulder','elbow'),('elbow','wrist')]:
            aa=j[f'{side}_{p}'];bb=j[f'{side}_{q}'];a.plot([aa[0],bb[0]],[aa[1],bb[1]],lw=17,color=col,solid_capstyle='round',zorder=z)
        for part in ['shoulder','elbow','wrist']:
            xy=j[f'{side}_{part}'];a.scatter(*xy,s=40,color='#287da3',zorder=9)
            a.annotate(('近右' if side=='near' else '远左')+{'shoulder':'肩','elbow':'肘','wrist':'腕'}[part],xy,xytext=(xy[0]-65,xy[1]-12),fontsize=10,zorder=12)
    tail=np.array(s['tail']);lamp=np.array(s['lamp']);v=(lamp-tail)/L;normal=np.array([-v[1],v[0]])
    barrel=np.array([tail-normal*14,tail+v*195-normal*27,lamp-normal*40,lamp+normal*40,tail+v*195+normal*27,tail+normal*14])
    a.add_patch(Polygon(barrel,facecolor='#bd6658',edgecolor='#555555',alpha=.85,zorder=4))
    grip=tail+v*70+normal*8;rw=np.array(j['near_wrist'])
    a.plot([rw[0],grip[0]],[rw[1],grip[1]],color='#3f454d',lw=18,zorder=7,solid_capstyle='round')
    a.add_patch(Ellipse(grip,42,48,facecolor='#68717a',edgecolor='#3f454d',alpha=.8,zorder=8))
    a.annotate('近右掌环握（施工块）',grip,xytext=(1080,300),arrowprops={'arrowstyle':'->'},fontsize=11,zorder=10)
    a.plot([tail[0],lamp[0]],[tail[1],lamp[1]],color='#555555',lw=1,ls=':',zorder=6)
    a.scatter(*tail,c='#a33e41',s=50,zorder=8);a.annotate('尾盖',tail,xytext=tail+np.array([15,15]),fontsize=10,zorder=10)
    if s['id']!='d05':
        pad=np.array([P+u*ss+n*nn for ss,nn in [(-32,-36),(0,-36),(0,12),(-32,12)]])
        a.add_patch(Polygon(pad,facecolor='#e8b989',edgecolor='#98623f',lw=1.5,zorder=6))
        a.plot([P[0]+n[0]*-36,P[0]+n[0]*12],[P[1]+n[1]*-36,P[1]+n[1]*12],color='#3b9176',lw=3,zorder=8)
        a.plot([j['far_wrist'][0],P[0]-u[0]*16],[j['far_wrist'][1],P[1]-u[1]*16],color='#bbbbbb',lw=12,zorder=3)
        a.plot([P[0],tail[0]],[P[1],tail[1]],color='#a33e41',lw=2,ls='--',zorder=10)
        a.annotate(f"未触／间隙{s['tail_gap_along_receiver_normal']}px",(P+tail)/2,xytext=(1130,615),arrowprops={'arrowstyle':'->'},fontsize=12,color='#a33e41')
        a.text(1130,465,'左腕接掌的左侧掌根\n手指自然朝右，掌面朝上\n掌垫厚32px，竖筒对掌\n真实五指、掌厚及近腕\n净空必须按实图复核',fontsize=12,va='top')
    a.text(75,65,f"S09 {s['id']} / F{s['frame']:03}  完整双臂及掌尾施工参考",fontsize=20)
    a.text(75,105,'1536×864共同注册 · 原图淡底仅定位 · 深近右/灰远左 · 非人物画稿',fontsize=13)
    a.text(75,730,'上/前臂休止长度各200(.8H)，允许投影短缩；肩下关节只是施工代理。\n灯轴240.21px保持刚性；新右握姿不套旧近手包络；亮灯、触掌均尚未发生。',fontsize=13)
    a.text(75,815,'本组：026退OFF → 031左掌展开 → 037第一击蓄势。禁止先画042触掌。',fontsize=14,color='#9c4146')
    fig.savefig(ROOT/f"reference/{s['id']}_F{s['frame']:03}_full.png",dpi=120,facecolor='white');plt.close(fig)
print('3 full-canvas construction references saved; no artwork generation')
