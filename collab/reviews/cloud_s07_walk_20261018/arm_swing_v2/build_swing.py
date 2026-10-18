#!/usr/bin/env python3
"""Small counterphase walk-arm proposals; accepted feet/time/lift states are untouched."""
from pathlib import Path
import copy,json,math,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/s07-swing-mpl')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib import font_manager
from matplotlib.patches import Polygon,Ellipse
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
ROOT.mkdir(exist_ok=True)
font_manager.fontManager.addfont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
plt.rcParams.update({'font.family':'Noto Sans CJK JP','font.size':10,'axes.unicode_minus':False})
original=json.loads((BASE/'geometry/eleven_states.json').read_text());states=copy.deepcopy(original['states'])
# Angles measured from world-down: positive=forward (screen right).
angles={57:[-12,-7,10,18],62:[-1,3,1,7],68:[10,18,-12,-7],
        73:[2,6,-1,2],79:[-12,-7,10,18],84:[-1,3,1,7],90:[10,18,-12,-7]}
checks=[]
for s,old in zip(states,original['states']):
    if s['frame'] in angles:
        deg=angles[s['frame']]
        for side,ds in [('near',deg[:2]),('far',deg[2:])]:
            shoulder=np.array(s['shoulder'] if side=='near' else s['far_shoulder'],float)
            vec=lambda d,l:np.array([math.sin(math.radians(d)),math.cos(math.radians(d))])*l
            elbow=shoulder+vec(ds[0],64);wrist=elbow+vec(ds[1],58)
            s[side+'_elbow']=elbow.tolist();s[side+'_wrist']=wrist.tolist()
            s[side+'_palm_proxy']=(wrist+vec(ds[1],11)).tolist()
        s['arm_angle_degrees_from_down']={'near':deg[:2],'far':deg[2:]}
        s['arm_swing_intent']='near right goes back when right foot lands; far left goes forward, then reverse on left landing; passing states near neutral'
        s['arm_status']='NEW_SMALL_COUNTERPHASE_PROPOSAL_PENDING_ASTRA'
        s['wrist_clearance_rule']='wrist/hand below shirt hem or visibly outside side silhouette; near arm in front, far arm behind with dashed hidden section. Actual cloth/hand widths must be checked in artwork, not inferred from points.'
    for key in ['frame','hold_frames','last_frame_inclusive','hip','far_hip','shoulder','far_shoulder','head_center','near_knee','far_knee','near_ankle','far_ankle','planted_feet','shoe_support_x','lamp_base','lamp_bail_contact','lamp_lift','contacts','camera']:
        assert s[key]==old[key],(s['frame'],key)
    if s['frame'] not in angles:
        assert s==old
    else:
        for side,sk in [('near','shoulder'),('far','far_shoulder')]:
            a,b,c=[np.array(s[k]) for k in [sk,side+'_elbow',side+'_wrist']]
            assert abs(np.linalg.norm(b-a)-64)<1e-9 and abs(np.linalg.norm(c-b)-58)<1e-9
        h=np.array(s['hip']);sh=np.array(s['shoulder']);head=np.array(s['head_center'])
        arm=np.mean([s[k] for k in ['near_elbow','near_wrist','far_elbow','far_wrist']],axis=0)
        leg=np.mean([s[k] for k in ['near_knee','near_ankle','far_knee','far_ankle']],axis=0)
        proxy=.30*h+.35*(h+sh)/2+.12*head+.10*arm+.13*leg
        s['balance_proxy_xy']=proxy.tolist()
        assert s['support_hull_x'][0]<=proxy[0]<=s['support_hull_x'][1]
    checks.append({'frame':s['frame'],'accepted_feet_timing_lift_unchanged':True,'arm_only_revision':s['frame'] in angles})
payload={'status':'ARM_ONLY_REFERENCE_REVISION_PENDING_ASTRA_F057_SINGLE_DRAW_AUTHORIZED',
 'source_commit':'384856e35a6718083abe5cff41910bacdd49d95a','world_size':[1672,941],
 'approval':'Astra freezes leg support/stopping/contact-to-lift construction; authorizes one F057 only, asks small counterphase arms57-90 before other10 drawings. No mirror of G022; use actual current03 right profile. G037 scale check pending.',
 'amplitude':'upper angles−12..+10degrees, fore angles−7..+18degrees from downward. Construction lengths64/58 unchanged; not actual measured bones.',
 'states':states,'checks':checks,'limits':'Whole-body thickness, wrist-to-cloth visible clearance, anatomy and naturalness still require actual F057 image review. No other10 drawing permission.'}
(ROOT/'arm_swing_states.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')

def draw(ax,s,world=False):
    ax.set_xlim((0,1672) if world else (800,1220));ax.set_ylim((941,0) if world else (800,385));ax.set_aspect('equal');ax.axis('off')
    ax.axhline(775,color='#969a9e',lw=1)
    for side,col,ls in [('far','#ba8b4d','--'),('near','#287aa1','-')]:
        h=s['far_hip'] if side=='far' else s['hip']
        for a,b in [(h,s[side+'_knee']),(s[side+'_knee'],s[side+'_ankle'])]:ax.plot([a[0],b[0]],[a[1],b[1]],color=col,lw=4,ls=ls)
        an=s[side+'_ankle'];y=an[1]+17
        ax.plot([an[0]-14,an[0]+26],[y,y],color='#3d8b68' if side in s['planted_feet'] else col,lw=4)
    # Far limb first, torso next, near limb last. Faint hidden far section is deliberately dashed.
    for side,col,z,ls in [('far','#ba8b4d',2,'--'),('near','#287aa1',5,'-')]:
        if side=='near':
            sh=np.array(s['shoulder']);h=np.array(s['hip']);e=(h-sh)/111;v=np.array([-e[1],e[0]])
            ax.add_patch(Polygon([sh+v*22,sh-v*22,h-v*25,h+v*25],facecolor='#c5cbd1',edgecolor='#7b828a',zorder=3))
        sk='far_shoulder' if side=='far' else 'shoulder'
        for a,b in [(s[sk],s[side+'_elbow']),(s[side+'_elbow'],s[side+'_wrist'])]:ax.plot([a[0],b[0]],[a[1],b[1]],color=col,lw=6,ls=ls,zorder=z)
        if side+'_palm_proxy' in s:
            w=s[side+'_wrist'];p=s[side+'_palm_proxy'];ax.plot([w[0],p[0]],[w[1],p[1]],color=col,lw=7,zorder=z)
        ax.scatter(*s[side+'_wrist'],s=20,c=col,zorder=7)
        if side=='far':ax.add_patch(Ellipse(s['far_wrist'],12,7,facecolor='none',edgecolor='#36927c',lw=2,zorder=8))
    ax.add_patch(Ellipse(s['head_center'],70,75.1,edgecolor='#596573',facecolor='none',lw=1.2))
    ax.set_title(f"F{s['frame']:03} ×{s['hold_frames']} · 近右{'后摆' if s['frame'] in [57,79] else '前摆' if s['frame'] in [68,90] else '过中'} / 远左反相",fontsize=11)
    if world:
        ax.text(70,65,'S07 F057 · 首张画前参考／非人物画稿',fontsize=21)
        ax.text(70,110,'1672×941共同世界；地面775；头包络75.1；真实朝右侧身份，不镜像G022。',fontsize=14)
        ax.text(70,825,'近右裸腕：小幅后摆；远左玉镯：小幅前摆。真实袖肘腕连通，腕与衣身留可见间隙。',fontsize=14)
        ax.text(70,875,'近踝929／远踝865；仅首057已许可。G037到后补核尺度，构造骨长不是解剖实测。',fontsize=14,color='#9d4448')
fig,axs=plt.subplots(2,4,figsize=(17,10))
for ax,s in zip(axs.flat,[s for s in states if s['frame'] in angles]):draw(ax,s)
axs.flat[-1].axis('off');axs.flat[-1].text(.02,.95,'S07 小幅反相摆臂 v2\n\n蓝=近右裸腕／近层\n灰=躯干\n赭虚=远左玉镯／远层\n\n脚、髋、时表、提灯段不改。\n上臂64／前臂58仅为施工值。\n腕与真实衣身的间隙待实图核。\n仅057允许首张绘制，其余10张未放行。',va='top',fontsize=12)
fig.savefig(ROOT/'walking_arms_overview.png',dpi=130,bbox_inches='tight',facecolor='white');plt.close(fig)
fig=plt.figure(figsize=(13.9333333333,7.8416666667),dpi=120);ax=fig.add_axes([0,0,1,1]);draw(ax,states[0],True);fig.savefig(ROOT/'F057_world_reference.png',dpi=120,facecolor='white');plt.close(fig)
# Matplotlib truncates the decimal width to1671 pixels on this host.
# Match the exact guide used by call01: white one-pixel right padding, no art edits.
guide=Image.open(ROOT/'F057_world_reference.png').convert('RGB')
if guide.size==(1671,941):
    canvas=Image.new(guide.mode,(1672,941),'white');canvas.paste(guide,(0,0));canvas.save(ROOT/'F057_world_reference.png')
else:
    assert guide.size==(1672,941),guide.size
print('7 walking-arm proposals; all feet/timing/lamp constraints unchanged; F057 guide saved')
