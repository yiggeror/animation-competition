"""F079 pose construction references only; zero image calls/exposure choices."""
from pathlib import Path
import hashlib,json,math,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.interpolate import RBFInterpolator
from scipy.ndimage import map_coordinates,binary_dilation,binary_closing,distance_transform_edt

F=Path(__file__).resolve().parent;P=F.parent;I=F/'inputs';I.mkdir(parents=True,exist_ok=True)
S=P/'next_F076_fixed_lower_input_001/generation_001';source=S/'F076_uniform_registered_upper_fixed_full_lower_candidate.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)=='5f5e3b6b1e39fe89ee411eb6f7904cfd007137c20cf33eba6b51423fac35ac9a'
A=np.array(Image.open(source).convert('RGBA'));H,W=A.shape[:2];yy,xx=np.indices((H,W))
U0=np.array(Image.open(S/'registered_complete_new_upper_whole_skirt_both_T.png').convert('RGBA'))
previous=json.loads((P/'next_F076_fixed_lower_input_001/INPUT_MANIFEST.json').read_text())
for key,name in [('fixed_complete_lower_file','fixed_complete_lower_skin_roots_legs_shoes_no_old_skirt_edge.png'),('original_C_rods_layer','fixed_original_C_rods_scene_layer.png')]:
 shutil.copyfile(previous[key],F/name)
lowerfile=F/'fixed_complete_lower_skin_roots_legs_shoes_no_old_skirt_edge.png';lower=np.array(Image.open(lowerfile).convert('RGBA'))
clayer=F/'fixed_original_C_rods_scene_layer.png';C=np.array(Image.open(clayer).convert('RGBA'))
assert sha(lowerfile)==previous['fixed_complete_lower_sha256'] and sha(clayer)==previous['original_C_rods_sha256']

# Actual native shaft fits outside the hands, then a tiny continuation. The
# complete native upper INCLUDING both rods is moved in one reference field;
# no old shaft is left underneath an independently drawn replacement shaft.
r,g,b=U0[:,:,:3].astype(float).transpose(2,0,1)
wood=(U0[:,:,3]>150)&(r>100)&(g>65)&(r>g+8)&(b<g*.78)
def fit(xmin,xmax,ymin,ymax):
 pts=[]
 for x in range(xmin,xmax):
  ys=np.flatnonzero(wood[:,x]&(np.arange(H)>=ymin)&(np.arange(H)<ymax))
  if len(ys):pts.append([x,float(np.median(ys))])
 pts=np.array(pts);return np.polyfit(pts[:,0],pts[:,1],1)
hm,hb=fit(290,356,420,500);sm,sb=fit(270,356,320,401)
cx=(sb-hb)/(hm-sm);oldcross=np.array([cx,hm*cx+hb])
oldpins=[np.array([385.,hm*385+hb]),np.array([461.,sm*461+sb])]
oldfronts=[np.array([268.,hm*268+hb]),np.array([250.,sm*250+sb])]
def rot(deg):
 a=math.radians(deg);return np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
body=[];bones=[];handmaps=[]
for side,shoulder,elbow,wrist,shoulder_delta,upper_angle,fore_angle in [
 ('R',[548,395],[518,432],[439,416],[-1,-2],-2.,1.5),
 ('L',[657,424],[613,497],[503,477],[0,1],-1.4,-1.)]:
 shoulder=np.array(shoulder,float);elbow=np.array(elbow,float);wrist=np.array(wrist,float)
 ns=shoulder+shoulder_delta;ne=ns+rot(upper_angle)@(elbow-shoulder);nw=ne+rot(fore_angle)@(wrist-elbow)
 body.extend([(shoulder,ns-shoulder),(elbow,ne-elbow),(wrist,nw-wrist)])
 handmaps.append((elbow,ne,rot(fore_angle)))
 bones.append({'side':side,'source_shoulder_elbow_wrist':[shoulder.tolist(),elbow.tolist(),wrist.tolist()],'target_shoulder_elbow_wrist':[ns.tolist(),ne.tolist(),nw.tolist()],'upper_bone_lengths_px':[float(np.linalg.norm(elbow-shoulder)),float(np.linalg.norm(ne-ns))],'forearm_bone_lengths_px':[float(np.linalg.norm(wrist-elbow)),float(np.linalg.norm(nw-ne))]})
newpins=[ne+rr@(pin-e) for pin,(e,ne,rr) in zip(oldpins,handmaps)]
newfronts=[newpins[0]+rot(-1.6)@(oldfronts[0]-oldpins[0]),newpins[1]+rot(2.)@(oldfronts[1]-oldpins[1])]
tdat=[]
for role,owner,front,pin in zip(['T_H','T_S'],['X.R','X.L'],newfronts,newpins):
 m=(pin[1]-front[1])/(pin[0]-front[0]);bb=pin[1]-m*pin[0];tdat.append({'role':role,'owner':owner,'front':front.tolist(),'pin':pin.tolist(),'slope':float(m),'intercept':float(bb)})
nx=(tdat[1]['intercept']-tdat[0]['intercept'])/(tdat[0]['slope']-tdat[1]['slope']);newcross=np.array([nx,tdat[0]['slope']*nx+tdat[0]['intercept']])
controls=list(body)
for index,points in [(0,[[401,396],[418,412]]),(1,[[474,480],[496,488]])]:
 e,ne,rr=handmaps[index]
 for point in points:
  point=np.array(point,float);controls.append((point,ne+rr@(point-e)-point))
for p,d in [([620,165],[-1,-1]),([548,246],[-1,-1]),([570,317],[-1,-1]),([706,302],[-1,-1]),([742,345],[-1,-1]),([621,365],[-1,-1]),([650,420],[-1,-1]),([621,490],[-.25,.5]),([706,477],[-.25,.5]),([671,550],[0,.5]),([688,604],[0,.25])]:
 controls.append((np.array(p,float),np.array(d,float)))
for p in [[565,657],[594,679],[620,684],[650,680],[690,685],[735,678],[791,658],[831,628],[245,135],[850,135],[245,730],[850,730]]:
 controls.append((np.array(p,float),np.zeros(2)))
# Every sampled shaft point remains on its ONE new straight axis. Both source
# intersections map to the same new X, preserving hand/shaft ownership.
for index,(m,bb) in enumerate([(hm,hb),(sm,sb)]):
 front=oldfronts[index];pin=oldpins[index];newfront=newfronts[index];newpin=newpins[index]
 for px in sorted(set([front[0],oldcross[0],pin[0],pin[0]+12]+list(np.arange(front[0]+18,pin[0],25)))):
  py=m*px+bb;tx=np.interp(px,[front[0],oldcross[0],pin[0],pin[0]+12],[newfront[0],newcross[0],newpin[0],newpin[0]+12]);ty=tdat[index]['slope']*tx+tdat[index]['intercept'];controls.append((np.array([px,py]),np.array([tx-px,ty-py])))
# Deduplicate the identical X control introduced by the two fitted axes.
unique={}
for p,d in controls:unique[tuple(np.round(p,6))]=(p,d)
controls=list(unique.values());rbf=RBFInterpolator(np.array([p for p,d in controls]),np.array([d for p,d in controls]),kernel='thin_plate_spline',degree=1,smoothing=0)
x0,y0,x1,y1=245,135,850,730;h,w=y1-y0,x1-x0;gy,gx=np.mgrid[0:h:4,0:w:4];field=rbf(np.column_stack([gx.ravel()+x0,gy.ravel()+y0])).reshape(gy.shape+(2,));dy,dx=np.indices((h,w));sy=dy.astype(float);sx=dx.astype(float)
for _ in range(7):
 vx=map_coordinates(field[:,:,0],[sy/4,sx/4],order=3,mode='nearest');vy=map_coordinates(field[:,:,1],[sy/4,sx/4],order=3,mode='nearest');sx=dx-vx;sy=dy-vy
crop=U0[y0:y1,x0:x1];a=crop[:,:,3].astype(float)/255;pm=crop[:,:,:3].astype(float)*a[:,:,None];wa=map_coordinates(a,[sy,sx],order=3,mode='constant',cval=0).clip(0,1);wc=np.stack([map_coordinates(pm[:,:,k],[sy,sx],order=3,mode='constant',cval=0) for k in range(3)],2)
out=np.zeros_like(crop);out[:,:,3]=np.rint(wa*255).astype('uint8');out[:,:,:3]=np.rint(np.divide(wc,wa[:,:,None],out=np.zeros_like(wc),where=wa[:,:,None]>1e-6)).clip(0,255).astype('uint8');U=np.zeros_like(A);U[y0:y1,x0:x1]=out;U[:,:,3][U[:,:,3]<4]=0
skirt_roi=(xx>=645)&(xx<=655)&(yy>=640)&(yy<700);solid=binary_closing(U[:,:,3]>0,iterations=2)&skirt_roi;seam=solid&(U[:,:,3]==0);_,nearest=distance_transform_edt(~((U[:,:,3]>200)&skirt_roi),return_indices=True);U[seam,:3]=U[nearest[0][seam],nearest[1][seam],:3];U[seam,3]=255
Image.fromarray(U).save(F/'new_complete_upper_skirt_both_T_CONSTRUCTION_ONLY.png')
Cpart=C.copy();Cpart[:,850:]=0;G=A.copy();G[:,:850]=0
target=Image.alpha_composite(Image.fromarray(Cpart),Image.fromarray(G));target=Image.alpha_composite(target,Image.fromarray(lower));target=Image.alpha_composite(target,Image.fromarray(U));T=np.array(target)
existing=(lower[:,:,3]>0)&(U0[:,:,3]==0)&(U[:,:,3]==0)&(yy>=650);T[existing]=A[existing]
noise=(yy>=736)&(xx<850)&(A[:,:,3]>0)&(A[:,:,3]<=8);T[noise]=A[noise]
gmask=(xx>=860)&(A[:,:,3]>0);T[gmask]=A[gmask]
Image.fromarray(T).save(I/'01_unique_complete_F079_target_REVIEW_ONLY.png')
bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(T));bg.convert('RGB').save(F/'complete_target_gray_REVIEW_ONLY.jpg',quality=96)
contact=bg.crop((245,310,740,550)).convert('RGB');contact.save(F/'contacts_1x_REVIEW_ONLY.png');contact.resize((1485,720),Image.Resampling.NEAREST).save(I/'02_same_pose_dual_clamps_X_3x.png');bg.crop((480,800,795,935)).convert('RGB').save(F/'fixed_support_1x_REVIEW_ONLY.png')
visible=(lower[:,:,3]>0)&(U[:,:,3]==0)&(yy>=650)&(xx<850);white=binary_dilation((U0[:,:,3]>0)|(U[:,:,3]>0),iterations=8)&(xx<850);white[visible]=False;white[gmask]=False
Image.fromarray(np.uint8(white)*255).convert('RGB').save(I/'04_complete_upper_whole_skirt_white_full_legs_black_mask.png');Image.fromarray(np.uint8(visible)*255).save(F/'actual_retained_visible_complete_legs_shoes_mask.png')
rootbox=(570,640,785,755);card=Image.new('RGB',(430,115),'#bdc1c4');card.paste(bg.crop(rootbox).convert('RGB'),(0,0));card.paste(Image.fromarray(np.uint8(white)*255).convert('RGB').crop(rootbox),(215,0));card.save(F/'under_hem_target_left_mask_right_boundary_1x.png')
font=ImageFont.truetype(str(P.parents[2]/'assets/fonts/NotoSansSC-VF.ttf'),20);card=Image.new('RGB',(1080,640),'#e7ebee');d=ImageDraw.Draw(card);d.text((16,12),'076已过身份衣料局部：无旧整身/拳姿；完整下肢另层固定',font=font,fill='#263743')
for box,xy,size in [((505,140,770,390),(20,60),(318,300)),((535,345,730,430),(350,60),(320,140)),((615,530,800,655),(700,60),(300,203)),((490,835,755,935),(350,350),(530,200))]:
 im=Image.fromarray(A).crop(box);cb=Image.new('RGBA',im.size,'#bdc1c4');cb.alpha_composite(im);card.paste(cb.convert('RGB').resize(size,Image.Resampling.LANCZOS),xy)
d.text((20,585),'整裙白域，裸露完整腿鞋黑域；腿根层仅真实皮肤/腿鞋',font=font,fill='#263743');card.save(I/'03_076_identity_head_clothes_shoes_patches_only.png')
support=(yy>=760)&(xx<850)&(A[:,:,3]>0);cm=(C[:,:,3]>0)&(U0[:,:,3]==0)&(U[:,:,3]==0)&(xx<850)
assert np.array_equal(T[support],A[support]) and np.array_equal(T[gmask],A[gmask]) and np.array_equal(T[cm],A[cm]);assert not np.any(white[visible]) and not np.any(white[736:]);assert nx<min(q['pin'][0] for q in tdat)
angle=math.degrees(abs(math.atan(tdat[1]['slope'])-math.atan(tdat[0]['slope'])))
prompt=f'''仅绘F079单态白域，未安排曝光。第一张为唯一完整同姿目标，展示新头颈胸腰、完整肩肘双臂掌腕与整裙，以及原位保留的完整腿鞋；第二张同姿掌杆，第三张仅已过076身份衣料鞋局部，第四张真实白绘黑保mask。进入已批078–095窗口的峰前部分，沿073→076靠近K02/F084：收住横向外伸，远肘稍屈、双腕相对拧转，头胸腰共同响应；本态不提前反向，不直接长持到084或翻肚，也不只转杆冻结上身。
远R自然屈肘，肩肘带腕，真实上臂/前臂骨长；近L配合转动，两条完整前臂分开连续、不互绕。头颈胸盆一起微前探，掌腕皮肤连续，无闭合腕环，原生一拇四指，不贴旧拳。R只夹T_H约({newpins[0][0]:.1f},{newpins[0][1]:.1f})，L只夹T_S约({newpins[1][0]:.1f},{newpins[1][1]:.1f})；硬直两杆X约({nx:.1f},{newcross[1]:.1f})在掌前，T_S在前经过远卷指，不能让远R夹第二杆。不为扩大X拉长前臂。
白域为完整新头颈、躯干、两条完整手臂掌腕、整裙、T杆及必要隐藏根部重叠；裸露完整腿鞋黑域。保留已过的真实皮肤腿鞋/隐蔽根部整层、奶奶和原C杆，不重抽、移动或切拼膝踝鞋，整裙自然遮在完整腿根前，不用技术mask横切裸露腿。身份按076白圆领、密集乳白点黄泡袖裙及肤色。输出1672×941透明全图，同画布，不加背景、影、字、骨架或额外帧，光由场景接入。若仅整体构图漂移，先将完整新上身整裙与两T杆统一相似注册后接回固定下肢，再交实际终门。'''
(F/'prompt_prepared_NOT_SUBMITTED_zh.txt').write_text(prompt+'\n');names=['01_unique_complete_F079_target_REVIEW_ONLY.png','02_same_pose_dual_clamps_X_3x.png','03_076_identity_head_clothes_shoes_patches_only.png','04_complete_upper_whole_skirt_white_full_legs_black_mask.png'];rows=[{'order':i+1,'path':str((I/n).resolve()),'sha256':sha(I/n),'size':list(Image.open(I/n).size)} for i,n in enumerate(names)]
(F/'tool_args_prepared_NOT_SUBMITTED.json').write_text(json.dumps({'prompt':prompt,'transparent_background':True,'referenced_image_paths':[q['path'] for q in rows]},ensure_ascii=False,indent=2)+'\n')
m={'status':'F079_ZERO_CALL_FOUR_INPUTS_ASTRA_GATE_PENDING','frame_label_only':79,'new_image_calls':0,'submitted':False,'generation_authorized':False,'frozen_exposure':False,'source076_commit':'5aa522ad36836e28b8f7e80189165795960d489f','source076_final_file':str(source),'source076_sha256':sha(source),'source_upper_component_sha256':sha(S/'registered_complete_new_upper_whole_skirt_both_T.png'),'target_method':'construction-only continuous complete upper/skirt/T pose reference; native final art not generated','controls':[[p.tolist(),d.tolist()] for p,d in controls],'bone_reference':bones,'T_rods':tdat,'source_X':oldcross.tolist(),'target_X':newcross.tolist(),'target_X_angle_degrees':angle,'fixed_complete_lower_file':str(lowerfile),'fixed_complete_lower_sha256':sha(lowerfile),'fixed_lower_RGBA_changes':0,'original_C_rods_layer':str(clayer),'original_C_rods_sha256':sha(clayer),'actual_support_foreground_RGBA_changes':0,'actual_grandma_foreground_RGBA_changes':0,'actual_visible_original_C_RGBA_changes':0,'visible_complete_legs_shoes_all_black':True,'natural_skirt_occlusion_no_naked_leg_horizontal_cut':True,'inputs':rows}
(F/'INPUT_MANIFEST.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'new_calls':0,'X':newcross.tolist(),'angle':angle,'pins':[q['pin'] for q in tdat],'bones':bones},ensure_ascii=False))
