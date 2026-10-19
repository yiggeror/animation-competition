"""One F112 PASSIVE residual construction from terminal-approved native104."""
from pathlib import Path
import hashlib,json,math,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import map_coordinates,binary_dilation,binary_opening,binary_fill_holes
from scipy.interpolate import RBFInterpolator
F=Path(__file__).resolve().parent;P=F.parent;I=F/'inputs';I.mkdir(parents=True,exist_ok=True)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
S=P/'next_F104_last_active_pull_input_001/generation_001';source=S/'F104_uniform_registered_upper_fixed_full_lower_candidate.png'
assert sha(source)=='bebff46038c7845272d64725c110697a3b75d6203be3243a8db20b5011f2ea0e'
A=np.array(Image.open(source).convert('RGBA'));H,W=A.shape[:2];yy,xx=np.indices((H,W))
shutil.copyfile(S/'registered_complete_new_upper_whole_skirt_two_T.png',F/'source104_adopted_complete_upper_head_skirt_two_T.png')
U0=np.array(Image.open(F/'source104_adopted_complete_upper_head_skirt_two_T.png').convert('RGBA'))
for name in ['fixed_complete_lower_skin_roots_legs_shoes_no_old_skirt_edge.png','fixed_original_C_rods_scene_layer.png']:
 shutil.copyfile(P/'next_F104_last_active_pull_input_001'/name,F/name)
lowerfile=F/'fixed_complete_lower_skin_roots_legs_shoes_no_old_skirt_edge.png';clayer=F/'fixed_original_C_rods_scene_layer.png'
assert sha(lowerfile)=='da1ef7ce8167179f7268edfe1bd70781551f937a18d33c4a12bc62b17ae8e7c4'
assert sha(clayer)=='47c3ece2f53c7e8b1bea4e3248a65a2518855bc6546f525bf809db62f5ec454e'
lower=np.array(Image.open(lowerfile).convert('RGBA'));C=np.array(Image.open(clayer).convert('RGBA'))
def rot(deg):
 t=math.radians(deg);return np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]])
def polygon(points):
 im=Image.new('L',(W,H));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
# Measure the actual approved104 exposed shafts, rather than older pose axes.
r,g,b=U0[:,:,:3].astype(float).transpose(2,0,1);alpha=U0[:,:,3]>0
wood=(U0[:,:,3]>160)&(r>140)&(g>70)&(r>g+15)&(b<g*.8)
axes=[]
for xs,guess in [(range(236,327),lambda x:519-.406*x),(range(278,327),lambda x:1.15*x-8)]:
 points=[]
 for xcol in xs:
  ys=np.flatnonzero(wood[:,xcol]&(abs(np.arange(H)-guess(xcol))<9))
  if len(ys)>=3:points.append((xcol,float(np.median(ys))))
 assert len(points)>35
 m,b0=np.polyfit(np.array(points)[:,0],np.array(points)[:,1],1);axes.append((float(m),float(b0)))
(hm,hb),(sm,sb)=axes;X=np.array([(sb-hb)/(hm-sm),0.]);X[1]=hm*X[0]+hb
def project(p,m,b0):
 q=np.array([p[0],m*p[0]+b0]);v=np.array([1.,m]);return q+v*np.dot(np.array(p)-q,v)/np.dot(v,v)
oldpins=[project([376.39806122832556,366.2157185375124],hm,hb),project([428.1370360519825,484.16959041018055],sm,sb)]
oldfronts=[np.array([229.,hm*229+hb]),np.array([270.,sm*270+sb])]
pairrot=rot(-7.);pairshift=np.array([8.,16.]);pair=lambda p:X+pairshift+pairrot@(np.array(p,float)-X)
newpins=[pair(p) for p in oldpins];newX=pair(X)
controls=[];bones=[]
def elbow_for(s,w,l1,l2):
 v=w-s;d=np.linalg.norm(v);assert abs(l1-l2)<d<l1+l2
 u=v/d;along=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(l1*l1-along*along);mid=s+along*u;n=np.array([-u[1],u[0]])
 return max([mid+h*n,mid-h*n],key=lambda p:p[1])
# Observed projected reference chains from actual104, not 3D certification.
for side,s,e,w,ds in [('R',[511,396],[439,420],[422,401],[5,11]),('L',[680,437],[660,488],[497,503],[5,9])]:
 s,e,w,ds=map(lambda p:np.array(p,float),[s,e,w,ds]);ns=s+ds;nw=pair(w);l1=np.linalg.norm(e-s);l2=np.linalg.norm(w-e);ne=elbow_for(ns,nw,l1,l2)
 controls.extend([(s,ns-s),(e,ne-e),(w,nw-w)])
 bones.append({'side':side,'source_shoulder_elbow_wrist':[s.tolist(),e.tolist(),w.tolist()],'target_shoulder_elbow_wrist':[ns.tolist(),ne.tolist(),nw.tolist()],'projected_upper_length_source_target':[float(l1),float(np.linalg.norm(ne-ns))],'projected_forearm_length_source_target':[float(l2),float(np.linalg.norm(nw-ne))]})
# A single rigid map for BOTH complete native palms and BOTH native shafts
# keeps the sole accepted two-grip topology, X order and readable R/X air.
Rcontact=polygon([(365,349),(399,344),(420,356),(433,380),(434,408),(414,424),(380,420),(367,400)])
Lcontact=polygon([(411,477),(447,465),(477,475),(500,491),(503,517),(477,537),(442,541),(417,529)])
rod_masks=[]
for (m,b0),front,pin in zip(axes,oldfronts,oldpins):
 v=pin-front;length=np.linalg.norm(v);v/=length;s=(xx-front[0])*v[0]+(yy-front[1])*v[1];distance=abs((xx-front[0])*v[1]-(yy-front[1])*v[0])
 rod_masks.append((distance<8)&(s>=-6)&(s<=length+60))
contact=(Rcontact|Lcontact|rod_masks[0]|rod_masks[1])&(U0[:,:,3]>40)
for py in range(280,552,6):
 for px in range(220,514,6):
  if contact[py,px]:
   p=np.array([px,py],float);controls.append((p,pair(p)-p))
for (m,b0),front,pin in zip(axes,oldfronts,oldpins):
 n=np.array([-m,1.]);n/=np.linalg.norm(n)
 for px in np.arange(front[0],pin[0]+5,14):
  for off in [-4.,0.,4.]:
   p=np.array([px,m*px+b0])+off*n;controls.append((p,pair(p)-p))
# Torso uncoils with delayed recoil; shoulders and elbows settle down,
# rather than initiating another active pull. Hips and lower skirt support stay.
for p,d in [([627,376],[12,-5]),([615,438],[9,-3]),([603,505],[4,2]),([711,497],[2,1]),([665,555],[1,0]),([688,604],[0,0])]:
 controls.append((np.array(p,float),np.array(d,float)))
white=(r>190)&(g>185)&(b>175)&(abs(r-g)<20)&(abs(g-b)<20)&(xx>555)&(xx<735)&(yy>340)&(yy<414)&alpha
cloth=(r>170)&(g>100)&(b<g*.65)&((g-b)>1.5*(r-g))&(U0[:,:,3]>180)&(yy>335)
guard=binary_dilation(binary_opening(white,iterations=1),iterations=2)|binary_dilation(binary_opening(cloth,iterations=1),iterations=2)
hair=((r<180)&(g<140)&(b<130)&(r>g+6))|((r>150)&(r>g*1.6)&(r>b*1.5))
pony=binary_dilation(hair&alpha&(xx>660)&(xx<795)&(yy>285)&(yy<412),iterations=2)&alpha&~guard
skin=(r>170)&(g>100)&(b>g*.65)&(r>g+12)&alpha
neck=binary_dilation(skin&(xx>586)&(xx<690)&(yy>333)&(yy<392),iterations=2)&alpha&~guard
head=((alpha&(xx>480)&(xx<795)&(yy<351))|neck|pony)&~guard;head=binary_fill_holes(head)&alpha&~guard
headpivot=np.array([627.,376.]);headrot=rot(-2.);headshift=np.array([12.,-5.])
for py in range(140,414,12):
 for px in range(490,791,12):
  if head[py,px] and not (590<=px<=690 and py>=339):
   p=np.array([px,py],float);controls.append((p,headpivot+headrot@(p-headpivot)+headshift-p))
# The complete real hem and hidden fixed roots stay a continuous white domain.
for py in range(620,711,14):
 for px in range(548,965,14):
  if U0[py,px,3]>100:controls.append((np.array([px,py],float),np.zeros(2)))
for p in [[557,623],[595,662],[625,674],[657,671],[719,690],[780,686],[845,670],[940,607],[200,110],[985,110],[200,740],[985,740]]:
 controls.append((np.array(p,float),np.zeros(2)))
unique={tuple(np.round(p,6)):(p,d) for p,d in controls};controls=list(unique.values())
rbf=RBFInterpolator(np.array([p for p,d in controls]),np.array([d for p,d in controls]),kernel='thin_plate_spline',degree=1,smoothing=0)
x0,y0,x1,y1=200,110,985,740;h,w=y1-y0,x1-x0;gy,gx=np.mgrid[0:h:4,0:w:4]
field=rbf(np.column_stack([gx.ravel()+x0,gy.ravel()+y0])).reshape(gy.shape+(2,));dy,dx=np.indices((h,w));sx=dx.astype(float);sy=dy.astype(float)
for _ in range(10):
 vx=map_coordinates(field[:,:,0],[sy/4,sx/4],order=3,mode='nearest');vy=map_coordinates(field[:,:,1],[sy/4,sx/4],order=3,mode='nearest');sx=dx-vx;sy=dy-vy
crop=U0[y0:y1,x0:x1];a=crop[:,:,3].astype(float)/255;pm=crop[:,:,:3].astype(float)*a[:,:,None]
wa0=map_coordinates(a,[sy,sx],order=3,mode='constant',cval=0);wa=wa0.clip(0,1);wc=np.stack([map_coordinates(pm[:,:,k],[sy,sx],order=3,mode='constant',cval=0) for k in range(3)],2)
patch=np.zeros_like(crop);patch[:,:,3]=np.rint(wa*255).astype('uint8');patch[:,:,:3]=np.rint(np.divide(wc,wa0[:,:,None],out=np.zeros_like(wc),where=wa0[:,:,None]>1e-6)).clip(0,255).astype('uint8');patch[patch[:,:,3]<3]=0
U=np.zeros_like(A);U[y0:y1,x0:x1]=patch;Image.fromarray(U).save(F/'new_complete_upper_skirt_two_T_CONSTRUCTION_ONLY.png')
Cpart=C.copy();Cpart[:,850:]=0;G=A.copy();G[:,:850]=0;oldchild=(U0[:,:,3]>0)&(xx>=850)&(xx<985);G[oldchild]=C[oldchild]
T=Image.alpha_composite(Image.fromarray(Cpart),Image.fromarray(G));T=Image.alpha_composite(T,Image.fromarray(lower));T=np.array(Image.alpha_composite(T,Image.fromarray(U)))
visible=(lower[:,:,3]>0)&(U0[:,:,3]==0)&(U[:,:,3]==0)&(yy>=650)&(xx<850);T[visible]=A[visible]
fringe=(yy>=736)&(xx<850)&(A[:,:,3]>0)&(A[:,:,3]<=8)&(U[:,:,3]==0);T[fringe]=A[fringe]
gmask=(xx>=850)&(A[:,:,3]>0)&(U0[:,:,3]==0);assert not np.any(gmask&(U[:,:,3]>0));T[gmask]=A[gmask]
Image.fromarray(T).save(I/'01_unique_complete_F112_target_REVIEW_ONLY.png')
bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(T));bg.convert('RGB').save(F/'complete_target_gray_REVIEW_ONLY.jpg',quality=96)
c=bg.crop((210,285,790,565)).convert('RGB');c.save(F/'contacts_1x_REVIEW_ONLY.png');c.resize((1740,840),Image.Resampling.NEAREST).save(I/'02_same_pose_dual_clamps_X_3x.png')
exposed=(lower[:,:,3]>0)&(U[:,:,3]==0)&(yy>=650)&(xx<850)
mask=binary_dilation((U0[:,:,3]>0)|(U[:,:,3]>0),iterations=8)&(xx<985);mask[exposed]=False;mask[gmask]=False
Image.fromarray(np.uint8(mask)*255).convert('RGB').save(I/'04_complete_upper_whole_skirt_white_full_legs_black_mask.png')
box=(570,635,810,755);card=Image.new('RGB',(480,120));card.paste(bg.crop(box).convert('RGB'),(0,0));card.paste(Image.fromarray(np.uint8(mask)*255).convert('RGB').crop(box),(240,0));card.save(F/'under_hem_target_left_mask_right_boundary_1x.png')
font=ImageFont.truetype(str(P.parents[2]/'assets/fonts/NotoSansSC-VF.ttf'),20);card=Image.new('RGB',(1080,640),'#e7ebee');ImageDraw.Draw(card).text((16,12),'104已过身份小块：脸发、衣料、鞋；无旧整姿或双掌',font=font,fill='#263743')
headlayer=np.zeros_like(U0);headlayer[head]=U0[head]
for index,(box,xy,size) in enumerate([((495,145,780,392),(20,60),(330,286)),((570,354,730,442),(370,60),(300,165)),((650,550,840,660),(710,60),(300,174)),((490,835,755,935),(350,350),(530,200))]):
 src=headlayer if index==0 else (U0 if index<3 else A);im=Image.fromarray(src).crop(box);ibg=Image.new('RGBA',im.size,'#bdc1c4');ibg.alpha_composite(im);card.paste(ibg.convert('RGB').resize(size,Image.Resampling.LANCZOS),xy)
card.save(I/'03_104_identity_head_clothes_shoes_patches_only.png')
oldbg=Image.new('RGBA',(W,H),'#bdc1c4');oldbg.alpha_composite(Image.fromarray(A));box=(210,125,985,720);paircard=Image.new('RGB',(1550,595));paircard.paste(oldbg.crop(box).convert('RGB'),(0,0));paircard.paste(bg.crop(box).convert('RGB'),(775,0));paircard.save(F/'104_left_112_target_right_same_canvas_upper_hands_1x.png')
support=(yy>=760)&(xx<850)&(A[:,:,3]>0);cm=(C[:,:,3]>0)&(U0[:,:,3]==0)&(U[:,:,3]==0)&(xx<850)
assert np.array_equal(T[support],A[support]) and np.array_equal(T[gmask],A[gmask]) and np.array_equal(T[visible],A[visible]) and np.array_equal(T[cm],A[cm]) and not np.any(mask[exposed]) and not np.any(mask[736:])
prompt=f'''只绘F112被动余摆窗111–124内的唯一白域。本态从已终审104末次主动绞拉停止之后继续：肩胸不再主动拧拉，两肩卸力下沉、双肘自然松下屈收，身体迟后向后上回弹；双腕被两杆未尽余势带着回摆。松力不是松手，双掌仍牢靠单握。身体与腕杆有迟后相位差，不做新的主动拉扯峰，不提前做125后翻肚。请把参考中真实肩肘腕骨链画成自然上臂、前臂与肘形，不复刻施工连续场造成的弯边、鼓包或软管。
第一图唯一完整同姿目标；第二图同姿两掌X；第三图只含104脸发、衣料、鞋身份小块，没有104整姿或旧双掌；第四图是真实完整mask。完整头颈保持正确104体量，随身体回弹，颈根和白领自然连续，不另放大头或分挪五官。
保持已过104正确单握：R只夹T_H约({newpins[0][0]:.1f},{newpins[0][1]:.1f})，L只夹T_S约({newpins[1][0]:.1f},{newpins[1][1]:.1f})。X约({newX[0]:.1f},{newX[1]:.1f})，T_S在X前层且在R拇指/卷指夹口外，R夹点与X沿杆分离约{np.linalg.norm(newpins[0]-newX):.1f}px。回摆不能回到R同夹双杆或双掌合拢，不能独挪X、缩短杆假避接触；始终只有两根硬直杆，无第三杆、旧轴或旧掌。
完整新上身、双臂掌腕、整裙、整头颈、两T作为同一个语义组件原生重绘。完整外露腿鞋黑域固定，整裙及隐蔽腿根白域自然接回；不按技术mask硬裁裙边或横截膝踝鞋。奶奶、原C和支持保护，灯光由场景接入。输出1672×941透明完整图，无背景、字或额外帧；如整组件构图漂移，只统一相似注册再接完整固定腿根，不分挪头、掌、腕或杆。'''
(F/'prompt_prepared_NOT_SUBMITTED_zh.txt').write_text(prompt+'\n')
names=['01_unique_complete_F112_target_REVIEW_ONLY.png','02_same_pose_dual_clamps_X_3x.png','03_104_identity_head_clothes_shoes_patches_only.png','04_complete_upper_whole_skirt_white_full_legs_black_mask.png'];rows=[{'order':i+1,'path':str((I/n).resolve()),'sha256':sha(I/n),'size':list(Image.open(I/n).size)} for i,n in enumerate(names)]
(F/'tool_args_prepared_NOT_SUBMITTED.json').write_text(json.dumps({'prompt':prompt,'transparent_background':True,'referenced_image_paths':[q['path'] for q in rows]},ensure_ascii=False,indent=2)+'\n')
manifest={'status':'F112_SINGLE_PASSIVE_RESIDUAL_ZERO_CALL_FOUR_INPUTS_ASTRA_GATE_PENDING','frame_label_only':112,'timing_window':'111-124 passive residual only, before125 flip','new_image_calls':0,'submitted':False,'generation_authorized':False,'later_states_prepared':False,'frozen_exposure':False,'source104_commit':'0c22667517ab830becdd8e66e8dab0b7348323b1','source104_file':str(source),'source104_sha256':sha(source),'source104_complete_upper_sha256':sha(F/'source104_adopted_complete_upper_head_skirt_two_T.png'),'target_is_construction_only_not_new_native_art':True,'bone_reference':bones,'projected_lengths_are_image_reference_not_3D_certification':True,'both_complete_palms_and_two_shafts_same_rigid_map':{'rotation_deg':-7.,'translation_xy':pairshift.tolist(),'pivot':X.tolist()},'source_two_axis_fits':axes,'source_X':X.tolist(),'target_X':newX.tolist(),'new_R_pin':newpins[0].tolist(),'new_L_pin':newpins[1].tolist(),'R_pin_X_axial_separation_px':float(np.linalg.norm(newpins[0]-newX)),'T_S_outside_R_clamp_and_X_foreground_topology_retained':True,'head_uniform_scale':1.,'head_rotation_deg':-2.,'head_translation_xy':headshift.tolist(),'fixed_complete_lower_file':str(lowerfile),'fixed_complete_lower_sha256':sha(lowerfile),'original_C_rods_layer':str(clayer),'original_C_rods_sha256':sha(clayer),'fixed_lower_RGBA_changes':0,'actual_support_foreground_RGBA_changes':0,'actual_grandma_foreground_RGBA_changes':0,'actual_visible_original_C_RGBA_changes':0,'complete_visible_legs_shoes_all_black':True,'inputs':rows}
(F/'INPUT_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');(F/'FOUR_INPUT_SHA256SUMS').write_text(''.join(q['sha256']+'  inputs/'+Path(q['path']).name+'\n' for q in rows));print(json.dumps({'calls':0,'target_sha256':rows[0]['sha256'],'source_X':X.tolist(),'target_X':newX.tolist(),'R':newpins[0].tolist(),'L':newpins[1].tolist()},ensure_ascii=False))
