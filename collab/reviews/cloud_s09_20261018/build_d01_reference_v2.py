#!/usr/bin/env python3
"""Rebuild d01 only. Never imports/runs the 18-pose builder or generates artwork."""
from pathlib import Path
import copy
import hashlib
import json
import math
import os
import subprocess

os.environ.setdefault('MPLCONFIGDIR','/tmp/s09-d01-v2-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, Ellipse, Polygon, Rectangle
from PIL import Image
import numpy as np

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
PREFIX='collab/reviews/cloud_s09_20261018/'
PREVIOUS='6df3ec6f33ad93e3bc777a140fb7915d764517e8'
font_manager.fontManager.addfont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
plt.rcParams.update({'font.family':'Noto Sans CJK JP','font.size':11,'axes.unicode_minus':False})

def protected_snapshot():
    paths=subprocess.check_output(['git','ls-tree','-r','--name-only',PREVIOUS,'--',PREFIX],cwd=REPO,text=True).splitlines()
    return {p:hashlib.sha256((REPO/p).read_bytes()).hexdigest() for p in paths if Path(p).name not in ['README.md','SHA256SUMS.txt']}

before=protected_snapshot()
old=json.loads((ROOT/'geometry/S09_reference_v1.json').read_text())['poses'][0]
pose=copy.deepcopy(old)
v=lambda p:np.asarray(p,dtype=float)
r=math.radians(-15)
u=v([math.cos(r),math.sin(r)]); n=v([-u[1],u[0]])
tail=v([860.,535.])
loc=lambda s,h=0:tail+s*u+h*n
j={
 'near_shoulder':[650.,410.], 'near_elbow':[675.,568.], 'near_wrist':[865.,530.],
 'far_shoulder':[850.,410.], 'far_elbow':[830.,600.], 'far_wrist':[955.,570.],
 'waist':[750.,580.]
}
pose['joints']=j
pose['prop'].update({'tail':tail.tolist(),'lamp':loc(175).tolist(),'grip':loc(65).tolist(),
                    'thumb_tip':loc(92,-21).tolist(),'left_palm':loc(120,41).tolist(),
                    'left_support_surface':loc(120,21).tolist(),'left_support_material_s':120.,
                    'left_palm_normal_offset':41.,'axis_deg':-15.})
pose['status']='D01_TECHNICAL_REFERENCE_V2_ONLY_NOT_APPROVED_FOR_IMAGE_GENERATION'

# A fixed 200px rest bone can have a shorter screen projection.
# Positive z is farther from the camera; this is a construction check, not a camera solve.
rest=200.
joint3={}
lengths={}
for side,z0,sgn1,sgn2 in [('near',-50.,-1,1),('far',50.,1,-1)]:
    s,e,w=[v(j[f'{side}_{k}']) for k in ['shoulder','elbow','wrist']]
    l1=float(np.linalg.norm(e-s));l2=float(np.linalg.norm(w-e))
    assert l1<rest and l2<rest
    z1=z0+sgn1*math.sqrt(rest**2-l1**2)
    z2=z1+sgn2*math.sqrt(rest**2-l2**2)
    joint3.update({side+'_shoulder':[*s.tolist(),z0],side+'_elbow':[*e.tolist(),z1],side+'_wrist':[*w.tolist(),z2]})
    lengths[side]={'upper_rest':200.,'fore_rest':200.,'upper_projected':l1,'fore_projected':l2,
                   'upper_projection_ratio':l1/rest,'fore_projection_ratio':l2/rest}

data={
 'shot':'S09','scope':'d01 F000 only; other 17 states are not rebuilt',
 'status':'ASTRA_D01_REVIEW_REQUIRED_NO_IMAGE_GENERATION',
 'canvas':{'width':1536,'height':864,'origin':'top left; x right, y down','automatic_crop':False},
 'frozen_from_astra':['identity sources','upper/forearm rest length 0.8H','tail-cap two-tap causality','96-frame event/exposure table'],
 'camera':'腰以上近景为新构图提案，尚未批准；旧母源是跪姿全身，不称沿用旧机位',
 'head_unit':250.,'rest_lengths':{'upper_arm':200.,'forearm':200.},
 'perspective_note':'允许投影短缩，不再对两段投影强求200；z仅证明等骨长可构造，非相机已标定或真实画稿证明',
 'pose':pose,'bone_projection':lengths,'constructive_joint3D':joint3,
 'generation_requests':0,'generated_artworks':0
}
(ROOT/'geometry/d01_reference_v2.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

fig=plt.figure(figsize=(15.36,8.64),dpi=100,facecolor='white')
ax=fig.add_axes([0,0,1,1])
ax.set_xlim(0,1536);ax.set_ylim(864,0);ax.set_aspect('equal');ax.axis('off')
ax.add_patch(Rectangle((1,1),1534,862,fill=False,edgecolor='#7697a4',lw=1))
def line(p,q,c,width,z=1,ls='-'):
    ax.plot([p[0],q[0]],[p[1],q[1]],color=c,lw=width,solid_capstyle='round',zorder=z,linestyle=ls)
def point(p,label,dx=12,dy=-12):
    ax.add_patch(Circle(p,5,facecolor='white',edgecolor='#16677f',lw=1.5,zorder=20))
    ax.text(p[0]+dx,p[1]+dy,label,color='#16677f',fontsize=10,zorder=21)
def note(s,x,y,size=11,c='#333333'):
    ax.text(x,y,s,fontsize=size,color=c,va='top')

note('S09 · d01 F000 × 8 · v2 仅首态技术参考',40,28,19)
note('全画布1536×864；未自动裁边；本图不是人物画稿',40,62,12,'#a43b35')
note('(0,0)',10,98,9);note('(1535,863)',1415,830,9)

# Full original head/waist registration is retained; only arm/prop construction changes.
ax.add_patch(Ellipse((745,245),245,250,fill=False,ls='--',edgecolor='#666666',lw=1.4))
note('头体积 H250',674,225,11,'#666666')
line([735,370],[735,395],'#777777',3,2)

# Far upper arm is behind the torso, elbow stays beside/below the waist.
line(j['far_shoulder'],j['far_elbow'],'#d2d2d2',25,1)
line(j['far_elbow'],j['far_wrist'],'#d2d2d2',23,1)
line(j['far_wrist'],pose['prop']['left_palm'],'#d2d2d2',15,5)
ax.add_patch(Polygon([(665,395),(835,395),(860,445),(828,580),(660,580),(625,445)],facecolor='#969696',zorder=3))
line(j['far_shoulder'],[841,495],'#555555',1.4,4,'--')
line([841,495],[832,580],'#555555',1.4,4,'--')
line(j['near_shoulder'],j['near_elbow'],'#414141',26,6)
line(j['near_elbow'],j['near_wrist'],'#414141',23,6)
line(j['near_wrist'],pose['prop']['grip'],'#414141',15,7)

# The left pad lies underneath the front barrel; its upper face is n=21.
ax.add_patch(Ellipse(pose['prop']['left_palm'],74,40,angle=-15,facecolor='#dedede',edgecolor='#555555',lw=1.2,zorder=5))
barrel=[loc(0,-21),loc(143,-21),loc(143,21),loc(0,21)]
lamp=[loc(143,-29),loc(175,-29),loc(175,29),loc(143,29)]
ax.add_patch(Polygon(barrel,facecolor='#c96556',edgecolor='#333333',lw=1.4,zorder=8))
ax.add_patch(Polygon(lamp,facecolor='#d5dde1',edgecolor='#333333',lw=1.4,zorder=8))
line(loc(85,-24),loc(111,-24),'#333333',4,9)
ax.add_patch(Ellipse(pose['prop']['grip'],42,64,angle=75,fill=False,edgecolor='#16677f',lw=2,zorder=11))
point(pose['prop']['thumb_tip'],'OFF / 右拇指',dy=-24)
surface=v(pose['prop']['left_support_surface'])
line(surface-16*u,surface+16*u,'#4b8675',3,12)
point(j['near_shoulder'],'近右肩')
point(j['near_elbow'],'近右肘',dx=-80,dy=13)
point(j['near_wrist'],'近右腕',dx=-70,dy=-23)
point(j['far_shoulder'],'远左肩')
point(j['far_elbow'],'远左肘',dx=-12,dy=20)
point(j['far_wrist'],'远左腕',dx=12,dy=4)
point(j['waist'],'腰锚',dx=-22,dy=18)

eye=v([798,274]); target=v(pose['prop']['thumb_tip'])
ax.add_patch(Circle(eye,5,facecolor='white',edgecolor='#846094',lw=1.5,zorder=10))
ax.annotate('',xy=eye+(target-eye)/np.linalg.norm(target-eye)*70,xytext=eye,arrowprops={'arrowstyle':'->','color':'#846094','lw':1.5})

note('d01 调整',42,166,15)
note('手电中心 y512：抬至胸腹操作区\n腰锚 y580；保留右手环握/拇指侧键\n远左肘(830,600)收在身体侧下\n远前臂从下方接腕→托掌\n远上臂被躯干遮住段用虚线\n\n深灰 近右臂 / 中灰 躯干 / 浅灰 远左臂\n手电175长；筒径42 / 灯头径58\n五指/皮肤/袖腕结构尚未绘制',42,200,12)
note('允许短缩，.8H 是骨长',1130,188,14)
note('骨长：双侧上臂/前臂均200\n本态屏幕投影：\n近上臂160 / 近前臂194\n远上臂191 / 远前臂129\n不把投影强拉成200\n\n腰上近景是新机位提案\n旧源为跪姿全身\n本图不代表机位已获批',1130,224,12)

note('仅审本首态；其余17态与96f事件表未重做。Astra未批准本态前不开始生成。',40,768,14,'#a43b35')
note('掌垫/握圈为施工符号；真实五指、掌腕连接和透视仍须在后续实际画稿中复审。',40,803,12)

out=ROOT/'reference/d01_F000_v2_full_canvas.png'
fig.savefig(out,dpi=100,bbox_inches=None,pad_inches=0,facecolor='white')
plt.close(fig)
im=Image.open(out); im.load(); assert im.size==(1536,864)

def crossing(a,b,c,d):
    def cross(p,q,r):
        x=v(q)-v(p);y=v(r)-v(p)
        return float(x[0]*y[1]-x[1]*y[0])
    return cross(a,b,c)*cross(a,b,d)<0 and cross(c,d,a)*cross(c,d,b)<0
assert not crossing(j['near_elbow'],j['near_wrist'],j['far_elbow'],j['far_wrist'])
assert j['far_elbow'][1]>j['waist'][1]
assert j['far_elbow'][1]>j['far_wrist'][1]>pose['prop']['left_palm'][1]
assert pose['prop']['grip'][1]<580 and (tail[1]+pose['prop']['lamp'][1])/2<580
assert abs(np.linalg.norm(loc(175)-tail)-175)<1e-8
after=protected_snapshot();assert before==after
for side in ['near','far']:
    for part,part2 in [('shoulder','elbow'),('elbow','wrist')]:
        assert abs(np.linalg.norm(v(joint3[side+'_'+part])-v(joint3[side+'_'+part2]))-200)<1e-8
report={'scope':'d01 technical reference only','png_size':list(im.size),'auto_crop':False,
        'flashlight_midpoint_y':float((tail[1]+pose['prop']['lamp'][1])/2),
        'waist_y':580,'flashlight_above_waist_H':float((580-(tail[1]+pose['prop']['lamp'][1])/2)/250),
        'far_elbow_screen_xy':j['far_elbow'],'far_forearm_rises_toward_palm':True,
        'projected_lengths':lengths,'bone_rest_3D_200_verified':True,'forearm_centerlines_cross':False,
        'protected_previous_files_unchanged':len(before),'protected_files_sha256':before,
        'image_generation_requests':0,'status':'PASS_REFERENCE_GEOMETRY_NOT_ASTRA_APPROVAL'}
(ROOT/'qa/d01_v2_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:x for k,x in report.items() if k!='protected_files_sha256'},ensure_ascii=False))
