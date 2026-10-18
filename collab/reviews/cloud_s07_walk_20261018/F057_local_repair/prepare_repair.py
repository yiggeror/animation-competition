#!/usr/bin/env python3
"""Actual source-pixel preposition and technical guide, not finished character art."""
from pathlib import Path
import hashlib,json,math,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/s07-local-repair-mpl')
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
for d in ['reference','masks','requests','originals','candidates','qa']:(ROOT/d).mkdir(exist_ok=True)
raw=BASE/'F057_first_image/originals/F057_call01_raw.png'
source=Image.open(raw).convert('RGBA');size=(1672,1080)
calibration=json.loads((ROOT/'reference/G037_actual_scale_check.json').read_text())
head_world=calibration['actual_head_height_world']
head=head_world/190;tx=929.9596642434797-head*832;ty=442.447726897376-head*109
inv=lambda p:[(p[0]-tx)/head,(p[1]-ty)/head]
def poly(points):
 im=Image.new('L',size);ImageDraw.Draw(im).polygon(points,fill=255);return im
near_arm=[(707,350),(766,366),(748,421),(721,479),(712,525),(711,564),(696,591),(677,615),(662,617),(637,598),(627,575),(632,553),(647,519),(661,489),(675,432),(690,382)]
far_arm=[(891,361),(925,363),(977,425),(1017,461),(1055,490),(1061,551),(1041,568),(1005,565),(977,541),(968,498),(907,456),(890,422)]
body=[(785,202),(838,210),(897,365),(909,550),(706,550),(697,435),(690,355),(730,273)]
protect=poly(body);pd=ImageDraw.Draw(protect);pd.rectangle((0,0,1671,239),fill=255);pd.polygon(near_arm,fill=255)
protect=protect.filter(ImageFilter.MaxFilter(5))
# The broad blouse proxy must not lock the narrow old far-arm skin strip at its edge.
src_hsv=np.array(source.convert('RGB').convert('HSV'));yy,xx=np.indices(src_hsv.shape[:2])
old_far_skin=(xx>885)&(yy>350)&(yy<580)&(src_hsv[:,:,0]>=10)&(src_hsv[:,:,0]<=28)&(src_hsv[:,:,1]>=45)&(src_hsv[:,:,1]<=175)
old_far_actual=Image.new('L',size);old_far_actual.paste(Image.fromarray((old_far_skin*255).astype(np.uint8)),(0,0));old_far_actual=old_far_actual.filter(ImageFilter.MaxFilter(5))
pr=np.array(protect);pr[np.array(old_far_actual)>0]=0;protect=Image.fromarray(pr)
protect.save(ROOT/'masks/locked_head_body_near_right_arm.png')
edit=Image.new('L',size);ed=ImageDraw.Draw(edit);ed.rectangle((585,530,1110,1055),fill=255)
ed.polygon(far_arm,fill=255);ed.polygon([(820,340),(950,339),(1000,460),(961,657),(815,665),(810,538)],fill=255)
edit=Image.fromarray(np.maximum(np.array(edit),np.array(old_far_actual)))
ea=np.array(edit);ea[np.array(protect)>0]=0;edit=Image.fromarray(ea);edit.save(ROOT/'masks/full_leg_chains_and_far_left_arm.png')
pad=Image.new('RGBA',size);pad.paste(source,(0,0));pad.save(ROOT/'reference/raw_source_bottom_padding_only.png')

# Genuine native fragments are translated/rotated rigidly. Gaps are deliberate guide seams.
# Native drawing must rebuild BOTH COMPLETE leg chains and the full far sleeve/arm.
def fragment(points):
 m=poly(points);a=np.array(pad);a[:,:,3]=(a[:,:,3].astype(float)*np.array(m)/255).astype(np.uint8);return Image.fromarray(a)
def rigid(im,origin,dest,degrees):
 c=math.cos(math.radians(degrees));s=math.sin(math.radians(degrees));ox,oy=origin;dx,dy=dest
 # inverse transform for rotation+translation, no rescaling
 return im.transform(size,Image.Transform.AFFINE,(c,s,ox-c*dx-s*dy,-s,c,oy+s*dx-c*dy),resample=Image.Resampling.BICUBIC)
near_leg=fragment([(775,540),(899,540),(935,710),(989,839),(893,866),(842,775),(796,680),(752,620)])
far_leg=fragment([(720,540),(807,548),(832,645),(780,777),(735,855),(626,835),(676,710)])
far_shoe=fragment([(610,824),(736,827),(787,873),(786,919),(608,920),(599,875)])
near_shoe=fragment([(906,826),(996,831),(1095,849),(1100,925),(902,925),(895,875)])
far_piece=fragment(far_arm)
floor_native=(775-ty)/head
far_wrist=inv([942,623]);arm_shift=[far_wrist[0]-988,far_wrist[1]-475]
canvas=Image.new('RGBA',size)
canvas.alpha_composite(rigid(far_leg,(780,555),(760,575),-2))
canvas.alpha_composite(rigid(near_leg,(812,555),(790,575),21))
canvas.alpha_composite(rigid(far_shoe,(678,911),(inv([865,775])[0],floor_native),0))
canvas.alpha_composite(rigid(near_shoe,(967,915),(inv([929,775])[0],floor_native),0))
canvas.alpha_composite(rigid(far_piece,(0,0),arm_shift,0))
upper=np.array(pad);removed=np.zeros(upper.shape[:2],bool);removed[548:size[1],585:1111]=True
removed|=np.array(poly(far_arm))>0;removed|=np.array(old_far_actual)>0;removed[np.array(protect)>0]=False;upper[removed]=0
canvas.alpha_composite(Image.fromarray(upper))
# Alpha compositing alone can change semi-transparent edge pixels; enforce the actual lock byte-for-byte.
canvas=Image.composite(canvas,pad,edit)
diff=np.any(np.array(canvas)!=np.array(pad),axis=2)
assert not np.any(diff[np.array(edit)==0])
assert not np.any(diff[np.array(protect)>0])
canvas.save(ROOT/'reference/native_fragment_preposition_NOT_ART.png')

def knee(h,a):
 h=np.array(h,float);a=np.array(a,float);v=a-h;d=np.linalg.norm(v);u=v/d
 t=(78**2-72**2+d*d)/(2*d);n=np.array([u[1],-u[0]])
 return (h+u*t+n*math.sqrt(max(0,78**2-t*t))).tolist()
hip=[912,616];farhip=[905,617]
targets={'hip':hip,'far_hip':farhip,'near_knee':knee(hip,[929,758]),'far_knee':knee(farhip,[865,758]),
 'near_ankle':[929,758],'far_ankle':[865,758],'near_sole_y':775,'far_sole_y':775,
 'far_wrist':[942,623],'far_elbow':[947,578],'far_shoulder_proxy':[900*head+tx,375*head+ty]}
payload={'status':'PREPARED_AFTER_ACTUAL_G037_SCALE_CHECK_NOT_YET_EXECUTED',
 'source_raw_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'source_native_size':list(source.size),
 'working_native_canvas':list(size),'padding':'139transparent rows at bottom only; original pixels never rescaled',
 'approval':'Astra passed counterphase arm reference v2, authorizes necessary singleF057 local repair only; all other10 remain unapproved. S09 repair completed before this preparation.',
 'actual_source_checked_registration':{'s':head,'tx':tx,'ty':ty,'head_target':head_world,'head_center_world':[929.9596642434797,442.447726897376],
   'warning':'Head source is actual G037253±5asset pixels, not75.1 construction; F057 head190±5native manual estimate. One uniform whole-image registration only.'},
 'targets_world':targets,'targets_native':{k:inv(v) for k,v in targets.items() if isinstance(v,list)},
 'hip_variation':'Hip912,616 instead of898,613 construction;14pxforward/3down proposal to fit actual unchanged blouse. Needs real support/near-foot transfer inspection, not a numeric physics claim.',
 'far_wrist_variation':'Target942,623 is13pxforward of929reference to leave actual wrist/bangle clear at the fixed blouse/pants edge. Green chain begins at actual native far sleeve outlet900,375; this is a visible cloth connection, not a guessed anatomical shoulder inside torso. Explicit actual-cloth clearance gate, not a torso penetration exemption.',
 'fragment_operations':[{'part':'near complete leg','rotation_degrees':21,'origin':[812,555],'destination':[790,575],'scale':1},
 {'part':'far complete leg','rotation_degrees':-2,'origin':[780,555],'destination':[760,575],'scale':1},
 {'part':'near shoe','translation':[inv([929,775])[0]-967,floor_native-915],'rotation_degrees':0,'scale':1},
 {'part':'far shoe','translation':[inv([865,775])[0]-678,floor_native-911],'rotation_degrees':0,'scale':1},
 {'part':'far whole arm','translation':arm_shift,'rotation_degrees':0,'scale':1}],
 'preposition_limits':'All pieces are real raw pixels, NOT adopted art. Deliberate hip/knee/ankle and sleeve gaps must be natively reconstructed over full chains; do not use piece placement as anatomy validation or move only shoes.',
 'preposition_outside_edit_pixel_changes':0,'preposition_protected_head_body_near_arm_pixel_changes':0,
 'new_native_calls_at_preparation':0,'other10_calls':0,'G037_source':'sources/G037/production/F037_grandma_rgba.png fixed9ee7689d; actually inspected; not mirrored'}
(ROOT/'reference/preparation.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
font_manager.fontManager.addfont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
plt.rcParams.update({'font.family':'Noto Sans CJK JP','axes.unicode_minus':False})
fig,axs=plt.subplots(1,2,figsize=(13,10))
axs[0].imshow(canvas);axs[0].set_facecolor('#e1e6ea');axs[0].set_xlim(570,1125);axs[0].set_ylim(size[1]-4,0);axs[0].set_title('真实原像素预摆／不是画稿')
ax=axs[1];ax.imshow(pad);ax.set_facecolor('#e1e6ea');ax.set_xlim(570,1125);ax.set_ylim(size[1]-4,0)
for side,col in [('near','#087b99'),('far','#ac7534')]:
 h=targets['hip' if side=='near' else 'far_hip'];k=targets[side+'_knee'];a=targets[side+'_ankle']
 pp=np.array([inv(h),inv(k),inv(a)]);ax.plot(pp[:,0],pp[:,1],c=col,lw=3);ax.scatter(pp[:,0],pp[:,1],c=col,s=25)
 w=inv([a[0],775]);ax.plot([w[0]-32,w[0]+56],[w[1],w[1]],c=col,lw=4)
fw=np.array([inv(targets[k]) for k in ['far_shoulder_proxy','far_elbow','far_wrist']]);ax.plot(fw[:,0],fw[:,1],c='#319779',lw=3,ls='--')
ax.axhline(floor_native,c='#777777');ax.set_title('完整腿链／远左整臂施工目标')
fig.suptitle(f'F057局修准备：按实图G037头尺{head_world:.2f}；源头身／近右臂锁住',fontsize=15)
fig.tight_layout();fig.savefig(ROOT/'qa/preposition_and_complete_chain_guide.png',dpi=140);plt.close(fig)
fig=plt.figure(figsize=(size[0]/120,size[1]/120),dpi=120);ax=fig.add_axes([0,0,1,1]);ax.imshow(Image.fromarray(upper));ax.set_xlim(0,size[0]);ax.set_ylim(size[1],0);ax.axis('off')
for side,col in [('near','#087b99'),('far','#ac7534')]:
 pp=np.array([inv(targets[k]) for k in ['hip' if side=='near' else 'far_hip',side+'_knee',side+'_ankle']]);ax.plot(pp[:,0],pp[:,1],c=col,lw=5);ax.scatter(pp[:,0],pp[:,1],c=col,s=80)
 w=inv([targets[side+'_ankle'][0],775]);ax.plot([w[0]-32,w[0]+56],[w[1],w[1]],c=col,lw=5)
fw=np.array([inv(targets[k]) for k in ['far_shoulder_proxy','far_elbow','far_wrist']]);ax.plot(fw[:,0],fw[:,1],c='#319779',lw=4,ls='--')
ax.axhline(floor_native,c='#777777');ax.text(60,70,'F057 complete-chain construction guide / NOT ART',fontsize=17)
ax.text(60,115,'Blue: near RIGHT / brown: far LEFT / green dashed: far LEFT arm',fontsize=13)
ax.text(60,1060,'Both entire leg chains must be natively redrawn; do not merely shift shoes.',fontsize=13)
fig.savefig(ROOT/'reference/complete_chain_execution_guide.png',dpi=120,facecolor='white');plt.close(fig)
g=Image.open(ROOT/'reference/complete_chain_execution_guide.png');assert g.size==size,g.size
print(json.dumps({'prepared':True,'native_calls':0,'native_floor':floor_native,'near_ankle_native':inv([929,758]),'far_ankle_native':inv([865,758]),'far_wrist_native':far_wrist},ensure_ascii=False))
