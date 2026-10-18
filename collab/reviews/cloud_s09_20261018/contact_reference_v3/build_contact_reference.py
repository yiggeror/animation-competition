#!/usr/bin/env python3
"""New 240px prop/local contact references. Does not generate or move character art."""
from pathlib import Path
import json,math,os,hashlib
os.environ.setdefault('MPLCONFIGDIR','/tmp/s09-contact-v3-mpl')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle,Circle
from matplotlib import font_manager
from PIL import Image

ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
font_manager.fontManager.addfont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
plt.rcParams.update({'font.family':'Noto Sans CJK JP','font.size':10,'axes.unicode_minus':False})
lock=json.loads((BASE/'switch_segment/locked/F000_lock.json').read_text())
scale=lock['registration']['scale'];tail=np.array([853.,638.]);delta=np.array([374.,-75.])
u=delta/np.linalg.norm(delta);n=np.array([-u[1],u[0]])
length=np.linalg.norm(delta)*scale
raw_points=np.array([(865,672),(868,629),(902,592),(932,565),(958,556),(986,562),(1000,567),(997,581),(978,590),(953,592),(982,607),(1010,630),(1025,640),(1025,653),(1018,662),(998,662),(995,676),(975,678),(971,690),(951,692),(949,699),(920,698),(890,687)],dtype=float)
hand=np.stack(((raw_points-tail)@u*scale,(raw_points-tail)@n*scale),axis=1)

def clip(poly,idx,bound,sign):
    out=[]
    for i,p in enumerate(poly):
        q=poly[(i+1)%len(poly)];inside=sign*(p[idx]-bound)>=0;next_inside=sign*(q[idx]-bound)>=0
        if inside:out.append(p)
        if inside!=next_inside:out.append(p+(q-p)*(bound-p[idx])/(q[idx]-p[idx]))
    return np.array(out)
band=[-36.,12.]
clipped=clip(clip(hand,1,band[0],1),1,band[1],-1)
minskin=float(clipped[:,0].min())
uncertainty=6*scale # up to3 source px in each independently read outline/axis position
assert minskin>uncertainty
states=[{'f':37,'gap':55.,'phase':'第一击蓄势'}, {'f':42,'gap':0.,'phase':'第一次尾盖触掌'}, {'f':44,'gap':30.,'phase':'第一次离掌目标'},
        {'f':52,'gap':23.,'phase':'第二击靠近'}, {'f':56,'gap':0.,'phase':'第二次尾盖触掌'}, {'f':58,'gap':35.,'phase':'第二次离掌目标'}]
data={'status':'NEW_CONTACT_REFERENCE_PROPOSAL_NOT_CONTACT_ARTWORK_APPROVAL','source_raw':'../F000_first_image/originals/F000_call01_raw.png',
      'source_sha256':hashlib.sha256((BASE/'F000_first_image/originals/F000_call01_raw.png').read_bytes()).hexdigest(),
      'coordinate_system':'local s along actual flashlight from tail to lens; n perpendicular toward near wrist. Pixel unit equals registered1536x864 canvas. No old global touchpoint reused.',
      'new_prop_length':float(length),'accepted_length_H':float(length/250),'head_radius_approx':40.,'rear_cap_radius_approx':14.,
      'previous175_target_superseded':True,'source_axis_raw':{'tail':tail.tolist(),'lamp':(tail+delta).tolist()},
      'near_hand_and_wrist_envelope_source_manual':raw_points.tolist(),'near_hand_envelope_local_sn':hand.tolist(),
      'envelope_scope':'visible near palm/finger silhouette plus a conservative proximal wrist cut; manual estimate, not a hidden-finger reconstruction or full forearm envelope',
      'left_receiver_contact_band_n':band,'left_pad_volume_s':[-32.,0.],
      'left_hand_rule':'left palm front face at s0; center shifted toward far side n-12. Fingers stay away from near-wrist side n>12. Palm/hand foreshortening and full arm connection need real drawing review.',
      'prerequisite':'F026 resets thumb to OFF before tapping. These envelopes use the F000 grip; the actual reset drawing must be rechecked against this outline before contact art.',
      'min_near_skin_s_in_receiver_band':minskin,'combined_manual_uncertainty_registered':uncertainty,
      'conservative_tail_first_lead':minskin-uncertainty,
      'states':[dict(s,nearest_near_skin_to_plane=s['gap']+minskin) for s in states],
      'invariants':['tail cap plane hits palm plane first','right grip and whole prop move as a rigid group; fixed scale','never use lamp head to hit','after each touch an actual positive gap reopens','no prop compression and no earlier right-knuckle hit'],
      'limits':'local contact/collision gate only; no global arm/wrist coordinates frozen for other17states. Whole-arm pose/skin depth/finger contact must be redrawn and viewed before tap drawing is accepted. The small projected margin is not proof of actual 3D contact.'}
(ROOT/'contact_reference_v3.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

def save(fig,name):
    fig.savefig(ROOT/name,dpi=150,bbox_inches='tight',facecolor='white');plt.close(fig)

fig,(ax,tx)=plt.subplots(1,2,figsize=(14,6),gridspec_kw={'width_ratios':[1.15,1]})
im=Image.open(BASE/'F000_first_image/originals/F000_call01_raw.png')
ax.imshow(im);ax.set_xlim(830,1055);ax.set_ylim(715,535);ax.set_aspect('equal');ax.plot(*np.vstack((raw_points,raw_points[0])).T,'--',color='#df823c',lw=1.3)
ax.scatter(*tail,s=60,c='#438db0');ax.annotate('尾盖轴点',xy=tail,xytext=(835,604),arrowprops={'arrowstyle':'->'},fontsize=9)
ax.axis('off');tx.axis('off')
tx.text(0,.96,'新筒尺：真实母态240px / .96H',va='top',fontsize=18)
tx.text(0,.82,'轮廓取自实际F000，不取旧175施工圈。\n橙虚线是近手/近腕可见外包络的人工近似。\ns轴：尾盖0 → 灯口240；n轴朝近腕侧。\n\n左掌接触带 n=[−36,+12]，掌面s=0。\n同带内近手最前突出约 s='+f'{minskin:.2f}'+'.\n两侧人工读图误差合计保守±'+f'{uncertainty:.2f}'+'.\n尾盖先到的投影净余量约'+f'{minskin-uncertainty:.2f}'+'.\n\n掌面向远侧让出近腕区域；手指不得抢进。\n余量较小，实际接触图必须逐像素复核。\n不以数字代替真实五指/掌腕/厚度验收。',va='top',fontsize=12,linespacing=1.7)
fig.suptitle('S09 新接触参考 v3 · 原画近手包络 / 非新人物画稿',fontsize=16)
save(fig,'01_actual_hand_envelope.png')

fig,axs=plt.subplots(2,3,figsize=(16,8))
for ax,state in zip(axs.flat,states):
    gap=state['gap'];g=gap
    ax.set_xlim(-60,325);ax.set_ylim(115,-85);ax.set_aspect('equal');ax.axis('off')
    ax.axvline(0,color='#4b8675',lw=2)
    ax.add_patch(Rectangle((-32,band[0]),32,band[1]-band[0],facecolor='#d4d4d4',edgecolor='#4b8675',lw=1.5))
    # Approximate rigid envelope: accepted source is slightly tapered, not a new redesign.
    ax.add_patch(Polygon([(g,-14),(g+195,-27),(g+length,-40),(g+length,40),(g+195,27),(g,14)],facecolor='#c96556',edgecolor='#333333',lw=1.2))
    ax.add_patch(Polygon([(g+195,-27),(g+length,-40),(g+length,40),(g+195,27)],facecolor='#d2dce0',edgecolor='#333333',lw=1.2))
    shifted=hand+np.array([g,0]);ax.add_patch(Polygon(shifted,facecolor='#f2c599',edgecolor='#9b704e',lw=1.0,alpha=.94))
    ax.plot([g,g],[-14,14],color='#333333',lw=2)
    ax.plot([0,g],[70,70],color='#aa3b2d',lw=1)
    if g==0:ax.add_patch(Circle((0,0),9,fill=False,edgecolor='#c9402b',lw=2))
    ax.text(-55,-67,f"F{state['f']:03d} · {state['phase']}",fontsize=12)
    ax.text(-55,96,f"尾盖间隙{g:.0f}px；同带近手领先面仍在 +{minskin+g:.1f}px",fontsize=9)
    ax.text(-49,49,'左掌面 s0',fontsize=9,color='#386455')
fig.suptitle('两次尾盖触掌：独立离掌→接触→离掌 / 新筒长240，近手与筒刚性同行',fontsize=16)
fig.text(.5,.01,'只审局部尾盖先到与近手净空；全臂新姿势未冻结，不沿用旧全局P点，不生成触掌画稿。',ha='center',fontsize=11,color='#a43b35')
save(fig,'02_two_tap_triplets_new_length.png')

fig,ax=plt.subplots(figsize=(11,5))
ax.axvline(0,color='#4b8675',lw=2)
ax.add_patch(Rectangle((-32,band[0]),32,band[1]-band[0],facecolor='#dedede',edgecolor='#4b8675'))
ax.add_patch(Polygon(hand,facecolor='#f2c599',edgecolor='#9b704e',alpha=.8))
ax.fill_between([0,150],band[0],band[1],color='#9ed0d5',alpha=.18)
ax.plot([0,0],[-14,14],color='#222222',lw=5,label='新尾盖端面')
ax.axvline(minskin,color='#c84530',lw=1.5,ls='--',label=f'带内近手最前点s{minskin:.2f}')
ax.set_xlim(-42,100);ax.set_ylim(80,-60);ax.set_aspect('equal');ax.set_xlabel('s：沿真实新筒轴，单位=注册画布px');ax.set_ylabel('n：朝近腕侧')
ax.legend(loc='lower right');ax.set_title('尾盖先到门：掌带内的近手轮廓仍在端面之后；不代表完整前臂已审')
save(fig,'03_tail_first_clearance.png')
print(json.dumps({'new_length':float(length),'near_skin_s':minskin,'uncertainty':uncertainty,'conservative_lead':minskin-uncertainty,'touch_frames':[42,56],'global_arm_pose_frozen':False},ensure_ascii=False))
