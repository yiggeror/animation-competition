"""F096 active reverse pull input construction only. No image tool, exposure or later state."""
from pathlib import Path
import hashlib,json,math,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.interpolate import RBFInterpolator
from scipy.ndimage import map_coordinates,binary_dilation,binary_opening,binary_fill_holes,label

F=Path(__file__).resolve().parent;P=F.parent;I=F/'inputs';I.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
S=P/'next_F090_rebound_input_001/generation_001';source=S/'F090_uniform_registered_upper_fixed_full_lower_candidate.png'
assert sha(source)=='2927d3d6d9c33719fb9d673c54ea843f0682c5ca3e2efaf0188eeff6975194ea'
A=np.array(Image.open(source).convert('RGBA'));H,W=A.shape[:2];yy,xx=np.indices((H,W))
U0=np.array(Image.open(S/'registered_complete_new_upper_whole_skirt_two_T.png').convert('RGBA'))
Image.fromarray(U0).save(F/'source090_complete_upper_head_skirt_two_T.png')
hr,hg,hb=U0[:,:,:3].astype(float).transpose(2,0,1);active=U0[:,:,3]>0
white=(hr>190)&(hg>185)&(hb>175)&(abs(hr-hg)<20)&(abs(hg-hb)<20)&(xx>555)&(xx<724)&(yy>338)&(yy<410)&active
cloth=(hr>170)&(hg>100)&(hb<hg*.65)&((hg-hb)>1.5*(hr-hg))&(U0[:,:,3]>180)&(yy>334)
guard=binary_dilation(binary_opening(white,iterations=1),iterations=2)|binary_dilation(binary_opening(cloth,iterations=1),iterations=2)
sk=(hr>170)&(hg>100)&(hb>hg*.65)&(hr>hg+12)&active
neck=binary_dilation(sk&(xx>586)&(xx<680)&(yy>327)&(yy<384),iterations=2)&active&~guard
hc=((hr<180)&(hg<140)&(hb<130)&(hr>hg+6))|((hr>150)&(hr>hg*1.6)&(hr>hb*1.5))
pony=binary_dilation(hc&active&(xx>655)&(xx<795)&(yy>280)&(yy<405),iterations=2)&active&~guard
head=((active&(xx>480)&(xx<795)&(yy<345))|neck|pony)&~guard
head=binary_fill_holes(head)&active&~guard
newhead=np.zeros_like(U0);newhead[head]=U0[head];visible_head=head
for name in ['fixed_complete_lower_skin_roots_legs_shoes_no_old_skirt_edge.png','fixed_original_C_rods_scene_layer.png']:
 shutil.copyfile(P/'next_F090_rebound_input_001'/name,F/name)
lowerfile=F/'fixed_complete_lower_skin_roots_legs_shoes_no_old_skirt_edge.png';clayer=F/'fixed_original_C_rods_scene_layer.png'
assert sha(lowerfile)=='da1ef7ce8167179f7268edfe1bd70781551f937a18d33c4a12bc62b17ae8e7c4'
assert sha(clayer)=='47c3ece2f53c7e8b1bea4e3248a65a2518855bc6546f525bf809db62f5ec454e'
lower=np.array(Image.open(lowerfile).convert('RGBA'));C=np.array(Image.open(clayer).convert('RGBA'))
def rot(deg):
 a=math.radians(deg);return np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
def polygon(points):
 im=Image.new('L',(W,H));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
def axis_fit(x0,x1,y0,y1):
 r,g,b=U0[:,:,:3].astype(float).transpose(2,0,1)
 wood=(U0[:,:,3]>180)&(r>120)&(g>70)&(r>g+12)&(b<g*.8)
 points=[]
 for x in range(x0,x1):
  ys=np.flatnonzero(wood[:,x]&(np.arange(H)>=y0)&(np.arange(H)<y1))
  if len(ys):points.append((x,float(np.median(ys))))
 return np.polyfit(np.array(points)[:,0],np.array(points)[:,1],1)
hm,hb=axis_fit(318,370,388,444);sm,sb=axis_fit(318,365,280,345)
oldx=(sb-hb)/(hm-sm);oldX=np.array([oldx,hm*oldx+hb])
axes=[(hm,hb,307.,437.),(sm,sb,308.,467.)]
def strip(m,b,x0,x1,width=5.2):
 return (abs(yy-m*xx-b)/math.sqrt(1+m*m)<width)&(xx>=x0-4)&(xx<=x1+3)
Rarm=polygon([(408,334),(448,331),(473,344),(490,373),(514,365),(529,353),(565,342),(580,352),(577,398),(563,428),(542,426),(500,432),(473,428),(458,419),(446,402),(430,394),(412,371)])
Larm=polygon([(439,399),(461,397),(476,408),(487,402),(511,415),(532,439),(583,458),(613,416),(610,383),(635,357),(674,355),(703,370),(720,401),(712,440),(692,467),(661,480),(626,514),(600,526),(523,481),(482,485),(451,469),(444,439)])
rr,gg,bb=U0[:,:,:3].astype(float).transpose(2,0,1)
collar=(rr>190)&(gg>185)&(bb>175)&(abs(rr-gg)<20)&(abs(gg-bb)<20)&(xx>555)&(xx<723)&(yy>337)&(yy<405)&(U0[:,:,3]>100)
collar=binary_dilation(binary_opening(collar,iterations=1),iterations=2)
headkeep=newhead[:,:,3]>0
Rarm&=~headkeep&~collar;Larm&=~headkeep&~collar
skin=(rr>165)&(gg>95)&(bb>gg*.65)&(rr>gg+12)&(U0[:,:,3]>0)&(xx>390)&(xx<700)&(yy>315)&(yy<555)&~headkeep&~collar
cc,nn=label(skin);sizes=np.bincount(cc.ravel());skin&=sizes[cc]>45
skinCut=binary_dilation(binary_fill_holes(skin),iterations=3)&~headkeep&~collar
farSleeve=polygon([(519,366),(527,350),(565,340),(581,352),(577,398),(562,430),(541,426)])
nearSleeve=polygon([(607,387),(628,360),(670,352),(701,367),(720,398),(713,436),(693,462),(656,467),(617,438)])
Rarm=((binary_dilation(Rarm,iterations=3)&skinCut)|farSleeve)&~headkeep&~collar
Larm=((binary_dilation(Larm,iterations=3)&skinCut)|nearSleeve)&~headkeep&~collar
shaft_masks=[strip(*axes[0]),strip(*axes[1])]
groups=[]
for hand,mask,(m,b,xf,xp) in zip([Rarm,Larm],shaft_masks,axes):
 q=np.zeros_like(U0);ownership=(hand|mask)&(U0[:,:,3]>0);q[ownership]=U0[ownership]
 # Each role gets a complete shaft at the old overlap. Clone its own actual
 # native cross-section 30px away; the other old shaft never enters its group.
 v=np.array([1.,m]);v/=np.linalg.norm(v);nearX=(np.hypot(xx-oldX[0],yy-oldX[1])<10)&mask
 sy=yy-v[1]*30;sx=xx-v[0]*30
 clone=np.stack([map_coordinates(U0[:,:,k].astype(float),[sy,sx],order=1,mode='constant',cval=0) for k in range(4)],2)
 q[nearX]=np.rint(clone[nearX]).clip(0,255).astype('uint8')
 groups.append(q)
# The two complete limbs are independent semantic layers because the source
# near thumb touches the far wrist: a shared field would fold that boundary.
contact_ownership=skinCut|shaft_masks[0]|shaft_masks[1]
no_contacts=U0.copy();no_contacts[contact_ownership]=0

def elbow_for(s,w,l1,l2):
 v=w-s;dist=np.linalg.norm(v);assert abs(l1-l2)<dist<l1+l2
 u=v/dist;along=(l1*l1-l2*l2+dist*dist)/(2*dist);height=math.sqrt(l1*l1-along*along);mid=s+along*u;perp=np.array([-u[1],u[0]])
 return max([mid+height*perp,mid-height*perp],key=lambda q:q[1])
controls=[];bones=[];maps=[]
for side,s,e,w,ds,dw,degrees in [('R',[553,383],[539,407],[499,400],[-5,6],[-12,9],3.),('L',[664,407],[596,495],[511,452],[5,-4],[24,-4],-5.)]:
 s,e,w,ds,dw=map(lambda x:np.array(x,float),[s,e,w,ds,dw]);ns=s+ds;nw=w+dw;l1=np.linalg.norm(e-s);l2=np.linalg.norm(w-e);ne=elbow_for(ns,nw,l1,l2);rr=rot(degrees)
 maps.append((w,nw,rr));controls.append((s,ns-s))
 angle=lambda v:math.degrees(math.atan2(v[1],v[0]));delta=lambda a,b:(angle(a)-angle(b)+180)%360-180
 bones.append({'side':side,'source_shoulder_elbow_wrist':[s.tolist(),e.tolist(),w.tolist()],'target_shoulder_elbow_wrist':[ns.tolist(),ne.tolist(),nw.tolist()],'upper_bone_lengths_px':[float(l1),float(np.linalg.norm(ne-ns))],'forearm_bone_lengths_px':[float(l2),float(np.linalg.norm(nw-ne))],'upper_rotation_deg':delta(ne-ns,e-s),'forearm_rotation_deg':delta(nw-ne,w-e),'whole_palm_own_T_rotation_deg':degrees,'wrist_translation_xy':dw.tolist()})
def handmap(point,index):
 w,nw,rr=maps[index];return nw+rr@(np.asarray(point)-w)
for p,d in [([621,370],[3,-1]),([650,424],[4,-3]),([630,497],[-2,2]),([704,481],[3,-1]),([671,550],[1,0]),([688,604],[.5,0])]:
 controls.append((np.array(p,float),np.array(d,float)))
headpivot=np.array([625.,369.]);headrot=rot(-2.);headshift=np.array([3.,-1.])
for py in range(145,402,12):
 for px in range(495,786,12):
  if visible_head[py,px] and not (590<=px<=684 and py>=330):
   point=np.array([px,py],float);controls.append((point,headpivot+headrot@(point-headpivot)+headshift-point))
for p in [[555,635],[594,679],[620,684],[650,680],[690,685],[735,678],[791,680],[846,655],[893,596],[240,120],[950,120],[240,740],[950,740]]:
 controls.append((np.array(p,float),np.zeros(2)))
unique={}
for p,d in controls:unique[tuple(np.round(p,6))]=(p,d)
controls=list(unique.values());rbf=RBFInterpolator(np.array([p for p,d in controls]),np.array([d for p,d in controls]),kernel='thin_plate_spline',degree=1,smoothing=0)
x0,y0,x1,y1=235,115,965,740;h,w=y1-y0,x1-x0;gy,gx=np.mgrid[0:h:4,0:w:4]
field=rbf(np.column_stack([gx.ravel()+x0,gy.ravel()+y0])).reshape(gy.shape+(2,));dy,dx=np.indices((h,w));sy=dy.astype(float);sx=dx.astype(float)
for _ in range(9):
 vx=map_coordinates(field[:,:,0],[sy/4,sx/4],order=3,mode='nearest');vy=map_coordinates(field[:,:,1],[sy/4,sx/4],order=3,mode='nearest');sx=dx-vx;sy=dy-vy
crop=no_contacts[y0:y1,x0:x1];a=crop[:,:,3].astype(float)/255;pm=crop[:,:,:3].astype(float)*a[:,:,None]
wa=map_coordinates(a,[sy,sx],order=3,mode='constant',cval=0).clip(0,1);wc=np.stack([map_coordinates(pm[:,:,k],[sy,sx],order=3,mode='constant',cval=0) for k in range(3)],2)
out=np.zeros_like(crop);out[:,:,3]=np.rint(wa*255).astype('uint8');out[:,:,:3]=np.rint(np.divide(wc,wa[:,:,None],out=np.zeros_like(wc),where=wa[:,:,None]>1e-6)).clip(0,255).astype('uint8');out[out[:,:,3]<3]=0
bodyU=np.zeros_like(A);bodyU[y0:y1,x0:x1]=out
def smooth(t):
 t=np.clip(t,0,1);return t*t*(3-2*t)
def arm_forward(points,index):
 spec=bones[index];s,e,w=np.array(spec['source_shoulder_elbow_wrist']);ns,ne,nw=np.array(spec['target_shoulder_elbow_wrist']);vu=e-s;vf=w-e;l1=np.linalg.norm(vu);l2=np.linalg.norm(vf)
 tu=np.clip((points-s)@vu/(l1*l1),0,1);tf=np.clip((points-e)@vf/(l2*l2),0,1)
 du=np.linalg.norm(points-(s+tu[:,None]*vu),axis=1);df=np.linalg.norm(points-(e+tf[:,None]*vf),axis=1)
 arc=np.where(du<df,tu*l1,l1+tf*l2);wf=smooth((arc-l1+12)/24);wh=smooth((arc-l1-l2+15)/15)
 upper=ns+(points-s)@rot(spec['upper_rotation_deg']).T
 fore=ne+(points-e)@rot(spec['forearm_rotation_deg']).T
 hand=nw+(points-w)@maps[index][2].T
 blend=upper*(1-wf[:,None])+fore*wf[:,None]
 return blend*(1-wh[:,None])+hand*wh[:,None]
U=np.zeros_like(A)
newaxes=[]
for index,(group,(m,b,xf,xp)) in enumerate(zip(groups,axes)):
 ay,ax=np.mgrid[230:570,250:750];dest=np.column_stack([ax.ravel(),ay.ravel()]).astype(float);coords=dest.copy()
 for _ in range(12):coords=dest-(arm_forward(coords,index)-coords)
 sy,sx=coords[:,1].reshape(ax.shape),coords[:,0].reshape(ax.shape)
 aa=group[:,:,3].astype(float)/255;pm=group[:,:,:3].astype(float)*aa[:,:,None]
 wa=map_coordinates(aa,[sy,sx],order=1,mode='constant',cval=0)
 wc=np.stack([map_coordinates(pm[:,:,k],[sy,sx],order=1,mode='constant',cval=0) for k in range(3)],2)
 patch=np.zeros(ax.shape+(4,),np.uint8);patch[:,:,3]=np.rint(wa*255).astype('uint8');patch[:,:,:3]=np.rint(np.divide(wc,wa[:,:,None],out=np.zeros_like(wc),where=wa[:,:,None]>1e-6)).clip(0,255).astype('uint8');patch[patch[:,:,3]<3]=0
 moved=np.zeros_like(A);moved[230:570,250:750]=patch
 # R complete limb/TH behind torso, then L complete limb/TS in the foreground.
 U=np.array(Image.alpha_composite(Image.fromarray(U),Image.fromarray(moved)))
 if index==0:U=np.array(Image.alpha_composite(Image.fromarray(U),Image.fromarray(bodyU)))
 front=handmap([xf,m*xf+b],index);pin=handmap([xp,m*xp+b],index);nm=(pin[1]-front[1])/(pin[0]-front[0]);nb=pin[1]-nm*pin[0]
 newaxes.append({'role':['T_H','T_S'][index],'owner':['X.R','X.L'][index],'front':front.tolist(),'pin':pin.tolist(),'slope':float(nm),'intercept':float(nb)})
cc,count=label(U[:,:,3]>2);sizes=np.bincount(cc.ravel());main=int(np.argmax(sizes[1:])+1)
probes=[[565,300],[628,370],[650,440],[669,535],[690,630]]+[[round(q[0]),round(q[1])] for bone in bones for q in bone['target_shoulder_elbow_wrist']]
assert all(cc[y,x]==main for x,y in probes)
detached=(cc>0)&(cc!=main);assert np.max(sizes[np.unique(cc[detached])],initial=0)<100
U[detached]=0
Image.fromarray(U).save(F/'new_complete_upper_skirt_two_T_CONSTRUCTION_ONLY.png')
nx=(newaxes[1]['intercept']-newaxes[0]['intercept'])/(newaxes[0]['slope']-newaxes[1]['slope']);newX=[float(nx),float(newaxes[0]['slope']*nx+newaxes[0]['intercept'])]
assert nx<min(q['pin'][0] for q in newaxes)
Cpart=C.copy();Cpart[:,850:]=0;G=A.copy();G[:,:850]=0;old_child=(U0[:,:,3]>0)&(xx>=850)&(xx<965);G[old_child]=C[old_child]
target=Image.alpha_composite(Image.fromarray(Cpart),Image.fromarray(G));target=Image.alpha_composite(target,Image.fromarray(lower));target=Image.alpha_composite(target,Image.fromarray(U));T=np.array(target)
existing=(lower[:,:,3]>0)&(U0[:,:,3]==0)&(U[:,:,3]==0)&(yy>=650)&(xx<850);T[existing]=A[existing]
fringe=(yy>=736)&(xx<850)&(A[:,:,3]>0)&(A[:,:,3]<=8)&(U[:,:,3]==0);T[fringe]=A[fringe]
gmask=(xx>=850)&(A[:,:,3]>0)&(U0[:,:,3]==0);T[gmask]=A[gmask]
Image.fromarray(T).save(I/'01_unique_complete_F096_target_REVIEW_ONLY.png')
bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(T));bg.convert('RGB').save(F/'complete_target_gray_REVIEW_ONLY.jpg',quality=96)
box=(260,245,745,555);contact=bg.crop(box).convert('RGB');contact.save(F/'contacts_1x_REVIEW_ONLY.png');contact.resize((contact.width*3,contact.height*3),Image.Resampling.NEAREST).save(I/'02_same_pose_dual_clamps_X_3x.png')
bg.crop((480,800,795,935)).convert('RGB').save(F/'fixed_support_1x_REVIEW_ONLY.png')
visible=(lower[:,:,3]>0)&(U[:,:,3]==0)&(yy>=650)&(xx<850);white=binary_dilation((U0[:,:,3]>0)|(U[:,:,3]>0),iterations=8)&(xx<965);white[visible]=False;white[gmask]=False
Image.fromarray(np.uint8(white)*255).convert('RGB').save(I/'04_complete_upper_whole_skirt_white_full_legs_black_mask.png')
Image.fromarray(np.uint8(visible)*255).save(F/'actual_retained_visible_complete_legs_shoes_mask.png')
rootbox=(570,640,785,755);card=Image.new('RGB',(430,115),'#bdc1c4');card.paste(bg.crop(rootbox).convert('RGB'),(0,0));card.paste(Image.fromarray(np.uint8(white)*255).convert('RGB').crop(rootbox),(215,0));card.save(F/'under_hem_target_left_mask_right_boundary_1x.png')
font=ImageFont.truetype(str(P.parents[2]/'assets/fonts/NotoSansSC-VF.ttf'),20);card=Image.new('RGB',(1080,640),'#e7ebee');d=ImageDraw.Draw(card);d.text((16,12),'090已过身份局部：脸发、衣料、鞋；无旧整身或旧双掌姿态',font=font,fill='#263743')
for index,(box,xy,size) in enumerate([((505,145,770,375),(20,60),(318,276)),((570,350,710,430),(350,60),(320,183)),((620,535,800,650),(700,60),(300,192)),((490,835,755,935),(350,350),(530,200))]):
 origin=newhead if index==0 else (U0 if index<3 else A)
 im=Image.fromarray(origin).crop(box);cb=Image.new('RGBA',im.size,'#bdc1c4');cb.alpha_composite(im);card.paste(cb.convert('RGB').resize(size,Image.Resampling.LANCZOS),xy)
d.text((20,585),'头颈体量按唯一096目标；整裙白域，完整裸露腿鞋黑域',font=font,fill='#263743');card.save(I/'03_090_identity_head_clothes_shoes_patches_only.png')
comparebox=(235,125,920,720);three=Image.new('RGB',(2055,595),'#bdc1c4')
states=[P/'F084_two_domains_close_zero_call_001/F084_two_domains_closed_candidate.png',source,I/'01_unique_complete_F096_target_REVIEW_ONLY.png']
for index,path in enumerate(states):
 im=Image.open(path).convert('RGBA');cb=Image.new('RGBA',im.size,'#bdc1c4');cb.alpha_composite(im);three.paste(cb.crop(comparebox).convert('RGB'),(685*index,0))
three.save(F/'084_passed_090_passed_096_target_same_canvas_upper_hands_1x.png')
support=(yy>=760)&(xx<850)&(A[:,:,3]>0);cm=(C[:,:,3]>0)&(U0[:,:,3]==0)&(U[:,:,3]==0)&(xx<850)
assert np.array_equal(T[support],A[support]) and np.array_equal(T[gmask],A[gmask]) and np.array_equal(T[cm],A[cm])
assert not np.any(white[visible]) and not np.any(white[736:])
prompt=f'''只绘F096主动绞签后段的唯一完整候选白域，未安排持帧曝光。本态从已过090继续反向拉扯，仍处于096–110主动段；胸腰肩肘腕共同回应，尚未进入111后的纯被动余摆，也未进入125后的翻肚。远R腕向屏左下拉开，肘伸展并下带；近L腕向屏右回提，近肘向外屈收、肩胸展开。用两肘屈伸和横向间距明确两条完整前臂各走自己的自然空间，不能不断垂直挤掌成合掌，不交臂打结，不只改头或衣纹，不整体平移090。
第一图为唯一完整同姿目标，第二图同姿双掌和X，第三图仅正确090脸发、衣料、鞋身份小块，不含旧整身或旧双掌竞争姿态；第四图实际完整白黑mask。完整头颈严格采用这份正确090体量，随胸腰回弹，保留自身脸、表情、马尾、红花及自然颈根；不另换大头、不逐态长大。
小满在图上任何位置都只能有两根独立硬直真杆：远R只夹T_H，近L只夹T_S，不换手端或偶端；绝不画连接双掌的第三杆，不留旧轴残影。R夹点约({newaxes[0]['pin'][0]:.1f},{newaxes[0]['pin'][1]:.1f})，L夹点约({newaxes[1]['pin'][0]:.1f},{newaxes[1]['pin'][1]:.1f})，掌前X约({newX[0]:.1f},{newX[1]:.1f})。T_S在X前层，近L在前、远R在后。各掌腕有自己的清楚连续轮廓，允许自然遮挡，但不能共用掌、皮肤桥或杆桥；完整真实前臂和手指顺接。
完整新上身、整头颈、双臂掌腕、整裙和两T是一个新绘语义组件。露出完整腿鞋黑域固定，隐蔽完整腿根与整裙白域自然连续；不横截膝踝鞋，不把技术mask当裙摆硬裁。奶奶、原C、足底支持、相机与光照固定，灯光由场景接入。施工参考袖根或旧遮挡分层痕是待原生整域重绘的结构，不机械贴回硬折痕。输出1672×941透明完整图，不加背景、地影、字、骨架、额外帧。若仅整组件构图漂移，先一次整体相似注册再与固定完整腿根自然接回，不分挪头、掌、腕、杆。'''

(F/'prompt_prepared_NOT_SUBMITTED_zh.txt').write_text(prompt+'\n')
names=['01_unique_complete_F096_target_REVIEW_ONLY.png','02_same_pose_dual_clamps_X_3x.png','03_090_identity_head_clothes_shoes_patches_only.png','04_complete_upper_whole_skirt_white_full_legs_black_mask.png']
rows=[{'order':i+1,'path':str((I/n).resolve()),'sha256':sha(I/n),'size':list(Image.open(I/n).size)} for i,n in enumerate(names)]
(F/'tool_args_prepared_NOT_SUBMITTED.json').write_text(json.dumps({'prompt':prompt,'transparent_background':True,'referenced_image_paths':[r['path'] for r in rows]},ensure_ascii=False,indent=2)+'\n')
manifest={'status':'F096_ZERO_CALL_FOUR_INPUTS_ASTRA_GATE_PENDING','frame_label_only':96,'new_image_calls':0,'submitted':False,'generation_authorized':False,'frozen_exposure':False,'later_states_prepared':False,'source090_commit':'2fdd1012abd0d1f4f66dbdee8539849797befe44','source090_final_file':str(source),'source090_sha256':sha(source),'source090_complete_upper_sha256':sha(F/'source090_complete_upper_head_skirt_two_T.png'),'target_method':'construction-only continuous actual090 independent complete arm bone fields, each whole palm and unique rigid T; coupled torso and own head-neck rebound; not new native drawing','source_actual_joint_locations_are_image_reference_not_3D_bone_certification':True,'bone_reference':bones,'T_rods':newaxes,'source_X':oldX.tolist(),'target_X':newX,'T_S_foreground_at_X':True,'native_old_shaft_pixels_removed_before_new_complete_two_role_layers':True,'head_uniform_scale':1.,'head_torso_rebound_rotation_deg':-2.,'head_translation_xy':headshift.tolist(),'head_source':'terminal-approved090 own complete head-neck volume','fixed_complete_lower_file':str(lowerfile),'fixed_complete_lower_sha256':sha(lowerfile),'fixed_lower_RGBA_changes':0,'original_C_rods_layer':str(clayer),'original_C_rods_sha256':sha(clayer),'actual_support_foreground_RGBA_changes':0,'actual_grandma_foreground_RGBA_changes':0,'actual_visible_original_C_RGBA_changes':0,'visible_complete_legs_shoes_all_black':True,'natural_skirt_occlusion_no_naked_leg_horizontal_cut':True,'inputs':rows,'three_state_compare_crop_fixed':list(comparebox),'three_state_order':['084 passed','090 passed','096 construction target'],'three_state_individual_alignment_applied':False}

(F/'INPUT_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'calls':0,'X':newX,'pins':[q['pin'] for q in newaxes],'four_input_sha256':[q['sha256'] for q in rows]},ensure_ascii=False))
