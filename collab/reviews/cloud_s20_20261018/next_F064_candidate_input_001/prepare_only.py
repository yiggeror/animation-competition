"""F064 is only a candidate sampling label; zero image calls, no new exposure."""
from pathlib import Path
import json,hashlib,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.interpolate import RBFInterpolator
from scipy.ndimage import map_coordinates,binary_dilation

F=Path(__file__).resolve().parent;P=F.parent;I=F/'inputs';I.mkdir(parents=True,exist_ok=True)
G61=P/'next_F061_candidate_input_001/generation_001'
source=G61/'F061_native_child_locked_G_candidate.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)=='0dde203fef7d78f00a6628ce1fc702f5ffa13a301adf0bd91b2fc10d80bd12ec'
A=np.array(Image.open(source).convert('RGBA'));native=np.array(Image.open(G61/'native_complete_child_and_T_rods.png').convert('RGBA'))
H,W=A.shape[:2];yy,xx=np.indices((H,W));native[:,:442]=0
# A single continuous whole-child construction field advances body and arms,
# not just props. Far R moves up/left, near L down/right toward approved K02.
# This source-based construction is NOT a production drawing or exposure.
controls=[([455,433],[-5,-3]),([479,437],[-5,-3]),([458,422],[-5,-3]),([511,439],[-4,-2]),([556,452],[-1,0]),([561,414],[-2,2]),([485,464],[4,3]),([503,478],[4,3]),([529,474],[4,3]),([622,484],[1,4]),([657,419],[-2,2]),([620,430],[-2,2]),([629,502],[-1,2]),([627,631],[-1,1]),([622,156],[-4,2]),([575,194],[-4,2]),([560,283],[-4,2]),([697,318],[-4,2]),([620,369],[-3,2]),([600,745],[0,0]),([680,751],[0,0]),([570,820],[0,0]),([683,820],[0,0]),([540,890],[0,0]),([600,912],[0,0]),([658,912],[0,0]),([718,900],[0,0]),([430,140],[0,0]),([805,140],[0,0]),([430,935],[0,0]),([805,935],[0,0])]
points=np.array([q[0] for q in controls],float);delta=np.array([q[1] for q in controls],float)
rbf=RBFInterpolator(points,delta,kernel='thin_plate_spline',degree=1,smoothing=0)
x0,y0,x1,y1=430,135,810,935;ch,cw=y1-y0,x1-x0
gy,gx=np.mgrid[0:ch:4,0:cw:4];value=rbf(np.column_stack([gx.ravel()+x0,gy.ravel()+y0])).reshape(gy.shape+(2,))
dy,dx=np.indices((ch,cw));sy=dy.astype(float);sx=dx.astype(float)
for _ in range(7):
    vx=map_coordinates(value[:,:,0],[sy/4,sx/4],order=3,mode='nearest');vy=map_coordinates(value[:,:,1],[sy/4,sx/4],order=3,mode='nearest');sx=dx-vx;sy=dy-vy
c=native[y0:y1,x0:x1];a=c[:,:,3].astype(float)/255;pm=c[:,:,:3].astype(float)*a[:,:,None]
wa=map_coordinates(a,[sy,sx],order=3,mode='constant',cval=0).clip(0,1)
wc=np.stack([map_coordinates(pm[:,:,k],[sy,sx],order=3,mode='constant',cval=0) for k in range(3)],2)
new=np.zeros_like(c);new[:,:,3]=np.rint(wa*255).astype('uint8');new[:,:,:3]=np.rint(np.divide(wc,wa[:,:,None],out=np.zeros_like(wc),where=wa[:,:,None]>1e-6)).clip(0,255).astype('uint8')
human=np.zeros_like(A);human[y0:y1,x0:x1]=new;human[835:]=native[835:]
props=Image.new('RGBA',(W*4,H*4));d=ImageDraw.Draw(props)
axes=json.loads((P/'cam20_crane_lamp_left_001/registration_input.json').read_text())['rods']
def rod(draw,ends):
    pts=[tuple(v*4 for v in q) for q in ends];draw.line(pts,fill='#675034',width=16);draw.line(pts,fill='#b28b52',width=10)
for role in ['C_N','C_B']:
    q=axes[role];rod(d,[q['shaft_tip_master_px'],[952,q['slope']*952+q['intercept']]])
tdat=[]
for role,front,pin in [('T_H',[322,486],[450,430]),('T_S',[322,393],[489,467])]:
    m=(pin[1]-front[1])/(pin[0]-front[0]);b=pin[1]-m*pin[0];tail=[pin[0]+20,m*(pin[0]+20)+b]
    rod(d,[front,tail]);tdat.append({'role':role,'owner':'X.R' if role=='T_H' else 'X.L','front':front,'pin':pin,'tail':tail,'slope':m,'intercept':b})
G=A.copy();G[:,:835]=0
target=Image.alpha_composite(props.resize((W,H),Image.Resampling.LANCZOS),Image.fromarray(G));target=Image.alpha_composite(target,Image.fromarray(human))
# The near shell shaft can pass in front of far curled digits. It remains
# owned only by L; no far R pinch of T_S is constructed or required.
q=tdat[1];over=Image.new('RGBA',(W*4,H*4));od=ImageDraw.Draw(over);rod(od,[[430,q['slope']*430+q['intercept']],[473,q['slope']*473+q['intercept']]])
target=Image.alpha_composite(target,over.resize((W,H),Image.Resampling.LANCZOS))
T=np.array(target);T[:,835:]=A[:,835:];Image.fromarray(T).save(I/'01_unique_complete_F064_target_REVIEW_ONLY.png')
box=(300,370,720,555);Image.fromarray(T).crop(box).resize((1260,555),Image.Resampling.NEAREST).save(I/'02_same_view_dual_clamps_X_3x.png')
font=ImageFont.truetype(str(P.parents[2]/'assets/fonts/NotoSansSC-VF.ttf'),20);card=Image.new('RGB',(1080,620),'#e7ebee');cd=ImageDraw.Draw(card)
cd.text((16,12),'061已过实物：仅头颈、服鞋局部；无旧整身／旧拳姿',font=font,fill='#263743')
for b,xy,size in [((520,140,740,385),(20,60),(300,334)),((545,345,705,427),(350,60),(320,164)),((565,545,715,660),(700,60),(300,230)),((495,835,745,930),(350,350),(500,190))]:
    im=Image.fromarray(A).crop(b);bg=Image.new('RGBA',im.size,'#bdc1c4');bg.alpha_composite(im);card.paste(bg.convert('RGB').resize(size,Image.Resampling.LANCZOS),xy)
cd.text((20,575),'白圆领／密集乳白点／红搭带露趾鞋；原生完整腕皮肤，无封闭腕环',font=font,fill='#263743');card.save(I/'03_061_identity_clothes_shoes_patches_only.png')
edit=binary_dilation((human[:,:,3]>0)|(native[:,:,3]>0),iterations=12)&(xx<810)
edit|=(xx>305)&(xx<545)&(yy>375)&(yy<505)
Image.fromarray(np.uint8(edit)*255).convert('RGB').save(I/'04_complete_child_T_rods_only_white_mask.png')
bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(T));bg.convert('RGB').save(F/'complete_target_gray_REVIEW_ONLY.jpg',quality=96)
crop=bg.crop(box).convert('RGB');crop.save(F/'contacts_1x_REVIEW_ONLY.png');crop.resize((1260,555),Image.Resampling.NEAREST).save(F/'contacts_3x_REVIEW_ONLY.png')
q1,q2=tdat;cx=(q2['intercept']-q1['intercept'])/(q1['slope']-q2['slope']);cross=[cx,q1['slope']*cx+q1['intercept']];angle=math.degrees(abs(math.atan(q2['slope'])-math.atan(q1['slope'])))
assert cx<min(q1['pin'][0],q2['pin'][0]);assert np.array_equal(T[:,835:],A[:,835:]);assert not np.any(edit[:,810:]);assert np.array_equal(human[835:],native[835:])
prompt='''只制作F064这一动作采样候选，未冻结持帧。第一图是从已过061继续推进的唯一完整新动作target，施工连续场只指导新姿态，必须自然新绘完整小满，不能照抄插值或只挪两根杆；第二图是同机位双掌/X，第三图仅061已过头颈服鞋局部，第四图白域为完整小满和T杆，奶奶黑域固定。
沿058–077首次绞签窗向已批K02方向再推进：肩肘先带腕相对转动，远R略向画左上、近L略向右下；头颈胸廓骨盆连贯微前探，双前臂分开，双足原位支撑、骨长与儿童比例保持。不跳084峰，不扭脸或拉长手臂，不把全身冻成061只旋转杆。腕皮肤连续，完整肩—肘—前臂—腕—五指新绘，不加灰镯或黑腕环，不贴旧拳。
角色自身R仅夹T_H头签约(450,430)，前端约(322,486)；L仅夹T_S壳签约(489,467)，前端约(322,393)。硬杆在双掌前成有所推进的X，T_S近、T_H远。T_S经过远手卷指前是正常前后遮挡，不要求把所有交叠改成空气；远R不能同时主动夹T_S，不换手别/偶端、不弯杆或加第三杆。每掌真实一拇四指、拇食相向对夹自己的一根杆，另外三指自然卷曲，掌腕完整。
维持061实物深棕红花双马尾、白彼得潘圆领、黄泡袖密集乳白圆点裙和红搭带露趾凉鞋，固有肤色一致；光后接，不烘焙光条。奶奶锁047全身/双掌/玉镯/原C杆净空不重生。输出单张1672×941透明图，同站位同画布，不缩放裁切，不加背景、地影、文字、骨架或额外帧。'''
(F/'prompt_prepared_NOT_SUBMITTED_zh.txt').write_text(prompt+'\n')
paths=[I/n for n in ['01_unique_complete_F064_target_REVIEW_ONLY.png','02_same_view_dual_clamps_X_3x.png','03_061_identity_clothes_shoes_patches_only.png','04_complete_child_T_rods_only_white_mask.png']]
rows=[{'order':i+1,'path':str(p.resolve()),'sha256':sha(p),'size':list(Image.open(p).size)} for i,p in enumerate(paths)]
(F/'tool_args_prepared_NOT_SUBMITTED.json').write_text(json.dumps({'prompt':prompt,'transparent_background':True,'referenced_image_paths':[r['path'] for r in rows]},ensure_ascii=False,indent=2)+'\n')
manifest={'status':'F064_SAMPLING_CANDIDATE_INPUT_ONLY_ASTRA_SHORT_GATE_PENDING','frame_label':64,'frozen_exposure':False,'new_hold_assigned':False,'image_calls':0,'submitted':False,'generation_authorized':False,'source061':str(source),'source061_sha256':sha(source),'source061_final_approved':True,'target_method':'single smooth complete-child TPS construction only, not a finished production drawing','controls_source_plus_delta':controls,'T_rods':tdat,'X_master':cross,'X_angle_degrees':angle,'identity_reference_only061_head_neck_clothes_shoes':True,'TS_near_R_curled_fingers_occlusion_not_extra_grip':True,'frozen_G_RGBA_exact':True,'feet_unchanged_in_target':True,'fixed_cues_seconds':{'entangle':[2.4,4.6],'flip':5.5,'cut':6.0},'inputs':rows}
(F/'INPUT_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'frame_candidate':64,'X':cross,'X_angle':angle,'new_image_calls':0,'input_count':4},ensure_ascii=False))
