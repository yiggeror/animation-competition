"""One F067 sampling input only. No image request, no new exposure schedule."""
from pathlib import Path
import json,hashlib,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.interpolate import RBFInterpolator
from scipy.ndimage import map_coordinates,binary_dilation,binary_opening,label

F=Path(__file__).resolve().parent;P=F.parent;I=F/'inputs';I.mkdir(parents=True,exist_ok=True)
source=P/'F064_root_occlusion_cleanup_zero_call_001/F064_proximal_roots_continuous_candidate.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)=='5ebf184c08b9e714f8b0030c226a2866158846bdac3db147d6645429867d2e76'
A=np.array(Image.open(source).convert('RGBA'));H,W=A.shape[:2];yy,xx=np.indices((H,W))
r,g,b=A[:,:,:3].astype(float).transpose(2,0,1)
wood=(A[:,:,3]>40)&(r>130)&(g>85)&(r>g+10)&(g>b+10)&(b<g*.78)
Cwood=wood&(xx>680)&(xx<835)&(yy>210)&(yy<320)
core=binary_opening((A[:,:,3]>20)&(xx<810),iterations=6)
flower=(A[:,:,3]>0)&(r>150)&(r>g*1.7)&(r>b*1.5)
remove=binary_dilation(Cwood,iterations=3)&~(core|flower)&(xx>680)&(yy>210)&(yy<325)
ids,n=label((A[:,:,3]>0)&(xx<835)&~remove);sizes=np.bincount(ids.ravel());main=ids==np.argmax(sizes[1:])+1
native=np.zeros_like(A);native[main]=A[main];native[:,:438]=0

# Full new construction from actual064: shoulders/elbows lead opposite wrists,
# coherent head/neck/chest/pelvis lean; supported shoes are fixed, not slid.
controls=[([455,409],[-5,-3]),([480,418],[-5,-3]),([511,421],[-4,-2]),([552,439],[-3,-1]),([563,400],[-2,0]),([485,446],[4,3]),([506,462],[4,3]),([530,461],[4,3]),([632,475],[2,3]),([665,414],[-2,1]),([624,418],[-2,2]),([648,495],[-2,2]),([650,600],[-1,2]),([645,680],[-1,1]),([622,154],[-3,1]),([578,197],[-3,1]),([569,286],[-3,1]),([710,320],[-3,1]),([632,368],[-2,2]),([610,774],[1,1]),([681,780],[-1,1]),([602,823],[0,0]),([690,823],[0,0]),([590,850],[0,0]),([690,850],[0,0]),([531,919],[0,0]),([608,913],[0,0]),([630,923],[0,0]),([727,914],[0,0]),([430,135],[0,0]),([825,135],[0,0]),([430,935],[0,0]),([825,935],[0,0])]
rbf=RBFInterpolator(np.array([q[0] for q in controls],float),np.array([q[1] for q in controls],float),kernel='thin_plate_spline',degree=1,smoothing=0)
x0,y0,x1,y1=430,135,825,935;ch,cw=y1-y0,x1-x0;gy,gx=np.mgrid[0:ch:4,0:cw:4]
values=rbf(np.column_stack([gx.ravel()+x0,gy.ravel()+y0])).reshape(gy.shape+(2,));dy,dx=np.indices((ch,cw));sy=dy.astype(float);sx=dx.astype(float)
for _ in range(7):
    vx=map_coordinates(values[:,:,0],[sy/4,sx/4],order=3,mode='nearest');vy=map_coordinates(values[:,:,1],[sy/4,sx/4],order=3,mode='nearest');sx=dx-vx;sy=dy-vy
c=native[y0:y1,x0:x1];a=c[:,:,3].astype(float)/255;pm=c[:,:,:3].astype(float)*a[:,:,None]
wa=map_coordinates(a,[sy,sx],order=3,mode='constant',cval=0).clip(0,1);wc=np.stack([map_coordinates(pm[:,:,k],[sy,sx],order=3,mode='constant',cval=0) for k in range(3)],2)
new=np.zeros_like(c);new[:,:,3]=np.rint(wa*255).astype('uint8');new[:,:,:3]=np.rint(np.divide(wc,wa[:,:,None],out=np.zeros_like(wc),where=wa[:,:,None]>1e-6)).clip(0,255).astype('uint8')
human=np.zeros_like(A);human[y0:y1,x0:x1]=new;human[835:,:835]=A[835:,:835]
props=Image.new('RGBA',(W*4,H*4));d=ImageDraw.Draw(props)
def rod(draw,ends):
    pts=[tuple(v*4 for v in q) for q in ends];draw.line(pts,fill='#675034',width=16);draw.line(pts,fill='#b28b52',width=10)
axes=json.loads((P/'cam20_crane_lamp_left_001/registration_input.json').read_text())['rods']
for role in ['C_N','C_B']:
    q=axes[role];rod(d,[q['shaft_tip_master_px'],[952,q['slope']*952+q['intercept']]])
tdat=[]
for role,front,pin in [('T_H',[330,478],[450,406]),('T_S',[306,345],[489,449])]:
    m=(pin[1]-front[1])/(pin[0]-front[0]);b0=pin[1]-m*pin[0];tail=[pin[0]+20,m*(pin[0]+20)+b0];rod(d,[front,tail]);tdat.append({'role':role,'owner':'X.R' if role=='T_H' else 'X.L','front':front,'pin':pin,'tail':tail,'slope':m,'intercept':b0})
G=A.copy();G[:,:835]=0
target=Image.alpha_composite(props.resize((W,H),Image.Resampling.LANCZOS),Image.fromarray(G));target=Image.alpha_composite(target,Image.fromarray(human))
q=tdat[1];over=Image.new('RGBA',(W*4,H*4));rod(ImageDraw.Draw(over),[[428,q['slope']*428+q['intercept']],[473,q['slope']*473+q['intercept']]])
target=Image.alpha_composite(target,over.resize((W,H),Image.Resampling.LANCZOS));T=np.array(target);T[:,835:]=A[:,835:];T[835:]=A[835:]
Image.fromarray(T).save(I/'01_unique_complete_F067_target_fixed_support_REVIEW_ONLY.png')
box=(285,325,735,550);Image.fromarray(T).crop(box).resize((1350,675),Image.Resampling.NEAREST).save(I/'02_same_view_dual_clamps_X_3x.png')
font=ImageFont.truetype(str(P.parents[2]/'assets/fonts/NotoSansSC-VF.ttf'),20);card=Image.new('RGB',(1080,640),'#e7ebee');cd=ImageDraw.Draw(card)
cd.text((16,12),'064已过身份：仅头颈/服鞋局部；原足支持继承，无旧整身/拳姿',font=font,fill='#263743')
for b1,xy,size in [((520,140,765,390),(20,60),(300,306)),((550,340,720,425),(350,60),(320,160)),((610,535,770,660),(700,60),(300,234)),((490,835,750,935),(350,350),(520,200))]:
    im=Image.fromarray(A).crop(b1);bg=Image.new('RGBA',im.size,'#bdc1c4');bg.alpha_composite(im);card.paste(bg.convert('RGB').resize(size,Image.Resampling.LANCZOS),xy)
cd.text((20,585),'足承重点：远(531,919)/(608,913)；近(630,923)/(727,914)，不迈步或漂移',font=font,fill='#263743');card.save(I/'03_064_identity_clothes_shoes_support_patches_only.png')
edit=binary_dilation((human[:,:,3]>0)|(native[:,:,3]>0),iterations=12)&(xx<835);edit|=(xx>290)&(xx<550)&(yy>330)&(yy<500)
Image.fromarray(np.uint8(edit)*255).convert('RGB').save(I/'04_complete_child_T_rods_only_white_mask.png')
bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(T));bg.convert('RGB').save(F/'complete_target_gray_REVIEW_ONLY.jpg',quality=96)
c=bg.crop(box).convert('RGB');c.save(F/'contacts_1x_REVIEW_ONLY.png');c.resize((1350,675),Image.Resampling.NEAREST).save(F/'contacts_3x_REVIEW_ONLY.png');bg.crop((480,800,795,935)).convert('RGB').save(F/'fixed_support_1x_REVIEW_ONLY.png')
q1,q2=tdat;cx=(q2['intercept']-q1['intercept'])/(q1['slope']-q2['slope']);cross=[cx,q1['slope']*cx+q1['intercept']];angle=math.degrees(abs(math.atan(q2['slope'])-math.atan(q1['slope'])))
assert np.array_equal(T[835:],A[835:]);assert np.array_equal(T[:,835:],A[:,835:]);assert not np.any(edit[:,835:]);assert cx<min(q1['pin'][0],q2['pin'][0])
prompt='''只绘F067单态候选，仍在058–077首次绞签窗，未冻结持帧。第一图是从已过064实际姿态继续推进的唯一完整新target，第二图是同机位双掌/X，第三图仅064头颈服鞋与实际足支持局部，第四图是完整小满/T杆白域。施工场只指导自然新绘，不把插值图当成品，不重复064整身只旋转杆。
肩肘带腕继续相对转动：远R略向左上、近L略向右下，头颈胸盆随重心连贯微前探，膝髋自然联动，双前臂分开、骨长和儿童比例保持，不跳084峰。两个实际足底支持区/地线严格继承064，不迈步或向右漂：远足趾/后支约(531,919)/(608,913)，近足约(630,923)/(727,914)，鞋底贴同一承重区。完整新绘原生双臂腕掌和双腿鞋，不贴旧拳/脚，不留闭合腕环或裙下透明断口。
R只以拇食夹T_H头签约(450,406)，杆前端约(330,478)；L只夹T_S壳签约(489,449)，前端约(306,345)。双掌前X继续推进，T_S近遮T_H远，T_S经过远卷指前只是遮挡，远R不得增加对T_S的主动夹握；每掌真实一拇四指，不换手别/偶端、不弯杆加杆。白圆领、密集乳白点黄泡袖裙、红搭带露趾鞋和中性肤色按064实物。奶奶锁047全层黑域不动。输出单张1672×941透明图，同画布站位，不裁缩、不加背景/地影/骨架/文字或额外帧，场景光后接。'''
(F/'prompt_prepared_NOT_SUBMITTED_zh.txt').write_text(prompt+'\n');paths=[I/n for n in ['01_unique_complete_F067_target_fixed_support_REVIEW_ONLY.png','02_same_view_dual_clamps_X_3x.png','03_064_identity_clothes_shoes_support_patches_only.png','04_complete_child_T_rods_only_white_mask.png']]
rows=[{'order':i+1,'path':str(p.resolve()),'sha256':sha(p),'size':list(Image.open(p).size)} for i,p in enumerate(paths)]
(F/'tool_args_prepared_NOT_SUBMITTED.json').write_text(json.dumps({'prompt':prompt,'transparent_background':True,'referenced_image_paths':[r1['path'] for r1 in rows]},ensure_ascii=False,indent=2)+'\n')
manifest={'status':'F067_COMPLETE_ACTION_INPUT_CANDIDATE_ASTRA_SHORT_GATE_PENDING','frame_label':67,'new_image_calls':0,'submitted':False,'generation_authorized':False,'frozen_exposure':False,'new_hold_assigned':False,'source064':str(source),'source064_sha256':sha(source),'source064_final_approved':True,'target_method':'single smooth complete-child construction field, not finished production art','controls_source_plus_delta':controls,'rigid_T_rods':tdat,'X_master':cross,'X_angle_degrees':angle,'two_support_regions_and_ground_y835_plus_RGBA_exact_source064':True,'fixed_G_RGBA_exact':True,'foot_bearing_points_far':[[531.01646,919.20553],[608.48354,912.79447]],'foot_bearing_points_near':[[629.5318,922.62216],[727.4682,913.87784]],'identity_only064_head_neck_clothes_shoes_no_old_full_pose_or_fists':True,'unchanged_cues_seconds':{'entangle':[2.4,4.6],'flip':5.5,'cut':6.0},'inputs':rows}
(F/'INPUT_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'candidate':67,'X':cross,'angle':angle,'new_calls':0,'foot_pixels_y835_plus_changed':0,'input_count':4},ensure_ascii=False))
