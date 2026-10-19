"""One F120 PASSIVE DECAY construction from terminal-approved native112."""
from pathlib import Path
import hashlib,json,math,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import map_coordinates,binary_dilation,binary_opening,binary_fill_holes,label
from scipy.interpolate import RBFInterpolator
F=Path(__file__).resolve().parent;P=F.parent;I=F/'inputs';I.mkdir(parents=True,exist_ok=True)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
S=P/'next_F112_passive_residual_input_001/generation_001';source=S/'F112_uniform_registered_upper_fixed_full_lower_candidate.png'
assert sha(source)=='a5e3821aaa0e42b3db44086647c4c064aba019a6d74491fce735785521720b3a'
A=np.array(Image.open(source).convert('RGBA'));H,W=A.shape[:2];yy,xx=np.indices((H,W))
shutil.copyfile(S/'registered_complete_new_upper_whole_skirt_two_T.png',F/'source112_adopted_complete_upper_head_skirt_two_T.png')
U0=np.array(Image.open(F/'source112_adopted_complete_upper_head_skirt_two_T.png').convert('RGBA'))
for name in ['fixed_complete_lower_skin_roots_legs_shoes_no_old_skirt_edge.png','fixed_original_C_rods_scene_layer.png']:
 shutil.copyfile(P/'next_F112_passive_residual_input_001'/name,F/name)
lowerfile=F/'fixed_complete_lower_skin_roots_legs_shoes_no_old_skirt_edge.png';clayer=F/'fixed_original_C_rods_scene_layer.png'
assert sha(lowerfile)=='da1ef7ce8167179f7268edfe1bd70781551f937a18d33c4a12bc62b17ae8e7c4'
assert sha(clayer)=='47c3ece2f53c7e8b1bea4e3248a65a2518855bc6546f525bf809db62f5ec454e'
lower=np.array(Image.open(lowerfile).convert('RGBA'));C=np.array(Image.open(clayer).convert('RGBA'))
def rot(deg):
 t=math.radians(deg);return np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]])
def polygon(points):
 im=Image.new('L',(W,H));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
# Measure the actual approved112 exposed shafts, rather than older pose axes.
r,g,b=U0[:,:,:3].astype(float).transpose(2,0,1);alpha=U0[:,:,3]>0
wood=(U0[:,:,3]>160)&(r>140)&(g>70)&(r>g+15)&(b<g*.8)
axes=[]
for xs,guess in [(range(228,315),lambda x:620-.59*x),(range(245,310),lambda x:.86*x+139)]:
 points=[]
 for xcol in xs:
  ys=np.flatnonzero(wood[:,xcol]&(abs(np.arange(H)-guess(xcol))<9))
  if len(ys)>=3:points.append((xcol,float(np.median(ys))))
 assert len(points)>35
 m,b0=np.polyfit(np.array(points)[:,0],np.array(points)[:,1],1);axes.append((float(m),float(b0)))
(hm,hb),(sm,sb)=axes;X=np.array([(sb-hb)/(hm-sm),0.]);X[1]=hm*X[0]+hb
def project(p,m,b0):
 q=np.array([p[0],m*p[0]+b0]);v=np.array([1.,m]);return q+v*np.dot(np.array(p)-q,v)/np.dot(v,v)
oldpins=[project([376.74,394.02],hm,hb),project([428.67,505.80],sm,sb)]
oldfronts=[np.array([221.,hm*221+hb]),np.array([235.,sm*235+sb])]
pairrot=rot(4.);pairshift=np.array([6.,-12.]);pair=lambda p:X+pairshift+pairrot@(np.array(p,float)-X)
newpins=[pair(p) for p in oldpins];newX=pair(X)
controls=[];bones=[]
def elbow_for(s,w,l1,l2):
 v=w-s;d=np.linalg.norm(v);assert abs(l1-l2)<d<l1+l2
 u=v/d;along=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(l1*l1-along*along);mid=s+along*u;n=np.array([-u[1],u[0]])
 return max([mid+h*n,mid-h*n],key=lambda p:p[1])
# Observed projected reference chains from actual112, not 3D certification.
for side,s,e,w,ds in [('R',[542,425],[493,446],[437,422],[-2,1]),('L',[676,453],[645,501],[499,518],[-2,2])]:
 s,e,w,ds=map(lambda p:np.array(p,float),[s,e,w,ds]);ns=s+ds;nw=pair(w);l1=np.linalg.norm(e-s);l2=np.linalg.norm(w-e);ne=elbow_for(ns,nw,l1,l2)
 controls.extend([(s,ns-s),(e,ne-e),(w,nw-w)])
 bones.append({'side':side,'source_shoulder_elbow_wrist':[s.tolist(),e.tolist(),w.tolist()],'target_shoulder_elbow_wrist':[ns.tolist(),ne.tolist(),nw.tolist()],'projected_upper_length_source_target':[float(l1),float(np.linalg.norm(ne-ns))],'projected_forearm_length_source_target':[float(l2),float(np.linalg.norm(nw-ne))]})
# A single rigid map for BOTH complete native palms and BOTH native shafts
# keeps the sole accepted two-grip topology, X order and readable R/X air.
Rcontact=polygon([(370,377),(402,367),(429,382),(444,402),(445,435),(422,449),(388,448),(373,423)])
Lcontact=polygon([(413,495),(440,481),(472,489),(501,507),(503,535),(476,559),(438,560),(417,546)])
rod_masks=[]
for (m,b0),front,pin in zip(axes,oldfronts,oldpins):
 v=pin-front;length=np.linalg.norm(v);v/=length;s=(xx-front[0])*v[0]+(yy-front[1])*v[1];distance=abs((xx-front[0])*v[1]-(yy-front[1])*v[0])
 rod_masks.append((distance<8)&(s>=-6)&(s<=length+60))
contact=(Rcontact|Lcontact|rod_masks[0]|rod_masks[1])&(U0[:,:,3]>40)
for py in range(315,568,6):
 for px in range(210,520,6):
  if contact[py,px]:
   p=np.array([px,py],float);controls.append((p,pair(p)-p))
for (m,b0),front,pin in zip(axes,oldfronts,oldpins):
 n=np.array([-m,1.]);n/=np.linalg.norm(n)
 for px in np.arange(front[0],pin[0]+5,14):
  for off in [-4.,0.,4.]:
   p=np.array([px,m*px+b0])+off*n;controls.append((p,pair(p)-p))
# Passive small return after112 recoil: chest/neck settle, elbows remain soft.
# Wrist/rod motion reverses with smaller amplitude; no active effort peak.
for p,d in [([644,376],[-5,3]),([632,440],[-4,2]),([622,505],[-1,1]),([716,496],[0,1]),([668,555],[0,0]),([688,604],[0,0])]:
 controls.append((np.array(p,float),np.array(d,float)))
white=(r>190)&(g>185)&(b>175)&(abs(r-g)<20)&(abs(g-b)<20)&(xx>580)&(xx<760)&(yy>335)&(yy<417)&alpha
cloth=(r>170)&(g>100)&(b<g*.65)&((g-b)>1.5*(r-g))&(U0[:,:,3]>180)&(yy>335)
guard=binary_dilation(binary_opening(white,iterations=1),iterations=2)|binary_dilation(binary_opening(cloth,iterations=1),iterations=2)
hair=((r<180)&(g<140)&(b<130)&(r>g+6))|((r>150)&(r>g*1.6)&(r>b*1.5))
pony=binary_dilation(hair&alpha&(xx>690)&(xx<840)&(yy>270)&(yy<414),iterations=2)&alpha&~guard
skin=(r>170)&(g>100)&(b>g*.65)&(r>g+12)&alpha
neck=binary_dilation(skin&(xx>605)&(xx<700)&(yy>330)&(yy<390),iterations=2)&alpha&~guard
head=((alpha&(xx>495)&(xx<840)&(yy<351))|neck|pony)&~guard;head=binary_fill_holes(head)&alpha&~guard
headpivot=np.array([644.,376.]);headrot=rot(1.);headshift=np.array([-5.,3.])
for py in range(140,420,12):
 for px in range(505,840,12):
  if head[py,px] and not (605<=px<=700 and py>=339):
   p=np.array([px,py],float);controls.append((p,headpivot+headrot@(p-headpivot)+headshift-p))
# The complete real hem and hidden fixed roots stay a continuous white domain.
for py in range(620,711,14):
 for px in range(548,1000,14):
  if U0[py,px,3]>100:controls.append((np.array([px,py],float),np.zeros(2)))
for p in [[555,635],[601,659],[625,666],[644,666],[710,675],[790,675],[845,663],[970,591],[190,110],[1010,110],[190,740],[1010,740]]:
 controls.append((np.array(p,float),np.zeros(2)))
unique={tuple(np.round(p,6)):(p,d) for p,d in controls};controls=list(unique.values())
rbf=RBFInterpolator(np.array([p for p,d in controls]),np.array([d for p,d in controls]),kernel='thin_plate_spline',degree=1,smoothing=0)
x0,y0,x1,y1=190,110,1010,740;h,w=y1-y0,x1-x0;gy,gx=np.mgrid[0:h:4,0:w:4]
field=rbf(np.column_stack([gx.ravel()+x0,gy.ravel()+y0])).reshape(gy.shape+(2,));dy,dx=np.indices((h,w));sx=dx.astype(float);sy=dy.astype(float)
for _ in range(10):
 vx=map_coordinates(field[:,:,0],[sy/4,sx/4],order=3,mode='nearest');vy=map_coordinates(field[:,:,1],[sy/4,sx/4],order=3,mode='nearest');sx=dx-vx;sy=dy-vy
crop=U0[y0:y1,x0:x1];a=crop[:,:,3].astype(float)/255;pm=crop[:,:,:3].astype(float)*a[:,:,None]
wa0=map_coordinates(a,[sy,sx],order=3,mode='constant',cval=0);wa=wa0.clip(0,1);wc=np.stack([map_coordinates(pm[:,:,k],[sy,sx],order=3,mode='constant',cval=0) for k in range(3)],2)
patch=np.zeros_like(crop);patch[:,:,3]=np.rint(wa*255).astype('uint8');patch[:,:,:3]=np.rint(np.divide(wc,wa0[:,:,None],out=np.zeros_like(wc),where=wa0[:,:,None]>1e-6)).clip(0,255).astype('uint8');patch[patch[:,:,3]<3]=0
U=np.zeros_like(A);U[y0:y1,x0:x1]=patch;Image.fromarray(U).save(F/'new_complete_upper_skirt_two_T_CONSTRUCTION_ONLY.png')
Cpart=C.copy();Cpart[:,850:]=0;G=A.copy();G[:,:850]=0;oldchild=(U0[:,:,3]>0)&(xx>=850);G[oldchild]=C[oldchild]
T=Image.alpha_composite(Image.fromarray(Cpart),Image.fromarray(G));T=Image.alpha_composite(T,Image.fromarray(lower));T=np.array(Image.alpha_composite(T,Image.fromarray(U)))
visible=(lower[:,:,3]>0)&(U0[:,:,3]==0)&(U[:,:,3]==0)&(yy>=650)&(xx<850);T[visible]=A[visible]
fringe=(yy>=736)&(xx<850)&(A[:,:,3]>0)&(A[:,:,3]<=8)&(U[:,:,3]==0);T[fringe]=A[fringe]
gmask=(xx>=850)&(A[:,:,3]>0)&(U0[:,:,3]==0);assert not np.any(gmask&(U[:,:,3]>0));T[gmask]=A[gmask]
Image.fromarray(T).save(I/'01_unique_complete_F120_target_REVIEW_ONLY.png')
bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(T));bg.convert('RGB').save(F/'complete_target_gray_REVIEW_ONLY.jpg',quality=96)
c=bg.crop((200,285,800,575)).convert('RGB');c.save(F/'contacts_1x_REVIEW_ONLY.png');c.resize((1800,870),Image.Resampling.NEAREST).save(I/'02_same_pose_dual_clamps_X_3x.png')
exposed=(lower[:,:,3]>0)&(U[:,:,3]==0)&(yy>=650)&(xx<850)
mask=binary_dilation((U0[:,:,3]>0)|(U[:,:,3]>0),iterations=8)&(xx<1010);mask[exposed]=False;mask[gmask]=False
Image.fromarray(np.uint8(mask)*255).convert('RGB').save(I/'04_complete_upper_whole_skirt_white_full_legs_black_mask.png')
box=(570,635,810,755);card=Image.new('RGB',(480,120));card.paste(bg.crop(box).convert('RGB'),(0,0));card.paste(Image.fromarray(np.uint8(mask)*255).convert('RGB').crop(box),(240,0));card.save(F/'under_hem_target_left_mask_right_boundary_1x.png')
font=ImageFont.truetype(str(P.parents[2]/'assets/fonts/NotoSansSC-VF.ttf'),20);card=Image.new('RGB',(1080,640),'#e7ebee');ImageDraw.Draw(card).text((16,12),'112已过身份小块：脸发、衣料、鞋；无旧整姿或双掌',font=font,fill='#263743')
identity_cc,_=label(head&(U0[:,:,3]>100));head_id=int(identity_cc[230,650]);assert head_id>0
identity_head=binary_dilation(identity_cc==head_id,iterations=1)&head
headlayer=np.zeros_like(U0);headlayer[identity_head]=U0[identity_head]
for index,(box,xy,size) in enumerate([((510,135,830,405),(20,60),(330,278)),((590,350,750,442),(370,60),(300,172)),((650,550,840,660),(710,60),(300,174)),((490,835,755,935),(350,350),(530,200))]):
 src=headlayer if index==0 else (U0 if index<3 else A);im=Image.fromarray(src).crop(box);ibg=Image.new('RGBA',im.size,'#bdc1c4');ibg.alpha_composite(im);card.paste(ibg.convert('RGB').resize(size,Image.Resampling.LANCZOS),xy)
card.save(I/'03_112_identity_head_clothes_shoes_patches_only.png')
oldbg=Image.new('RGBA',(W,H),'#bdc1c4');oldbg.alpha_composite(Image.fromarray(A));box=(210,125,1010,720);paircard=Image.new('RGB',(1600,595));paircard.paste(oldbg.crop(box).convert('RGB'),(0,0));paircard.paste(bg.crop(box).convert('RGB'),(800,0));paircard.save(F/'112_left_120_target_right_same_canvas_upper_hands_1x.png')
support=(yy>=760)&(xx<850)&(A[:,:,3]>0);cm=(C[:,:,3]>0)&(U0[:,:,3]==0)&(U[:,:,3]==0)&(xx<850)
assert np.array_equal(T[support],A[support]) and np.array_equal(T[gmask],A[gmask]) and np.array_equal(T[visible],A[visible]) and np.array_equal(T[cm],A[cm]) and not np.any(mask[exposed]) and not np.any(mask[736:])
prompt=f'''只绘F120在111–124被动余摆窗末端的唯一白域。本态从已终审112继续衰减：小满已经停止主动绞转，胸肩/肘松下来，112迟后回弹后胸颈小幅回落，两肘继续柔软松弛；双腕仍被杆的余势带动，向相反方向作幅度更小的回摆。参考中杆组角回摆4°，X回摆(+6,-12)，明显小于104到112的余势位移，不新增主动推拉峰，不为计数硬增动作。松力不是放手，双掌始终各自牢靠单握。120还没有125后龟偶翻肚，也不提前改奶奶合杆状态。
第一图唯一完整同姿目标；第二图同姿两掌X；第三图只含112脸发、衣料、鞋身份小块，没有112整姿或旧双掌；第四图是真实完整mask。完整头颈保持正确112体量并随身体迟后回落，不放大头、不分挪五官，颈根/白领自然连续。肩肘腕和衣褶应自然原生重绘，不照抄施工折线、鼓包或软管。
保持正确单握：R只夹T_H约({newpins[0][0]:.1f},{newpins[0][1]:.1f})，L只夹T_S约({newpins[1][0]:.1f},{newpins[1][1]:.1f})；X约({newX[0]:.1f},{newX[1]:.1f})。T_S在X前层且处于R拇指/卷指夹口外，R夹点与X沿杆分离约{np.linalg.norm(newpins[0]-newX):.1f}px。不能因回摆合拢到双夹、挤手到X或合掌；只保留两根硬直真杆，不独挪X、缩短杆、残留旧轴旧掌或加第三杆。
完整新上身、双臂掌腕、整裙、整头颈、两T作为同一个语义组件原生重绘。完整外露腿鞋黑域固定，整裙及隐蔽腿根白域自然接回；不要按技术mask硬裁裙摆或横截膝踝鞋。奶奶、原C、支持保护，灯光由场景接入。输出1672×941透明完整图，无背景、字、额外帧；若整组件构图漂移，只统一相似注册再接完整固定腿根，不分挪头、掌、腕或杆。'''
(F/'prompt_prepared_NOT_SUBMITTED_zh.txt').write_text(prompt+'\n')
names=['01_unique_complete_F120_target_REVIEW_ONLY.png','02_same_pose_dual_clamps_X_3x.png','03_112_identity_head_clothes_shoes_patches_only.png','04_complete_upper_whole_skirt_white_full_legs_black_mask.png'];rows=[{'order':i+1,'path':str((I/n).resolve()),'sha256':sha(I/n),'size':list(Image.open(I/n).size)} for i,n in enumerate(names)]
(F/'tool_args_prepared_NOT_SUBMITTED.json').write_text(json.dumps({'prompt':prompt,'transparent_background':True,'referenced_image_paths':[q['path'] for q in rows]},ensure_ascii=False,indent=2)+'\n')
manifest={'status':'F120_SINGLE_PASSIVE_DECAY_ZERO_CALL_FOUR_INPUTS_ASTRA_GATE_PENDING','frame_label_only':120,'timing_window':'111-124 passive residual DECAY END, before125 flip','new_image_calls':0,'submitted':False,'generation_authorized':False,'later_states_prepared':False,'frozen_exposure':False,'source112_commit':'63812699879a3185cf0a591a3f2d5c3660490cd4','source112_file':str(source),'source112_sha256':sha(source),'source112_complete_upper_sha256':sha(F/'source112_adopted_complete_upper_head_skirt_two_T.png'),'target_is_construction_only_not_new_native_art':True,'bone_reference':bones,'projected_lengths_are_image_reference_not_3D_certification':True,'both_complete_palms_and_two_shafts_same_rigid_map':{'rotation_deg':4.,'translation_xy':pairshift.tolist(),'pivot':X.tolist()},'source_two_axis_fits':axes,'source_X':X.tolist(),'target_X':newX.tolist(),'new_R_pin':newpins[0].tolist(),'new_L_pin':newpins[1].tolist(),'R_pin_X_axial_separation_px':float(np.linalg.norm(newpins[0]-newX)),'T_S_outside_R_clamp_and_X_foreground_topology_retained':True,'head_uniform_scale':1.,'head_rotation_deg':1.,'head_translation_xy':headshift.tolist(),'fixed_complete_lower_file':str(lowerfile),'fixed_complete_lower_sha256':sha(lowerfile),'original_C_rods_layer':str(clayer),'original_C_rods_sha256':sha(clayer),'fixed_lower_RGBA_changes':0,'actual_support_foreground_RGBA_changes':0,'actual_grandma_foreground_RGBA_changes':0,'actual_visible_original_C_RGBA_changes':0,'complete_visible_legs_shoes_all_black':True,'inputs':rows}
(F/'INPUT_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');(F/'FOUR_INPUT_SHA256SUMS').write_text(''.join(q['sha256']+'  inputs/'+Path(q['path']).name+'\n' for q in rows));print(json.dumps({'calls':0,'target_sha256':rows[0]['sha256'],'source_X':X.tolist(),'target_X':newX.tolist(),'R':newpins[0].tolist(),'L':newpins[1].tolist()},ensure_ascii=False))
