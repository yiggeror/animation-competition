"""F061 sampling candidate ONLY; a new construction target, never final art."""
from pathlib import Path
import json,hashlib,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.interpolate import RBFInterpolator
from scipy.ndimage import map_coordinates,binary_dilation

F=Path(__file__).resolve().parent;P=F.parent;I=F/'inputs';I.mkdir(parents=True,exist_ok=True)
source=P/'F058_wrist_cleanup_zero_call_001/F058_wrist_skin_continuous_candidate.png'
A=np.array(Image.open(source).convert('RGBA'));native=np.array(Image.open(P/'next_F058_input_003/generation_001/native_complete_child_and_T_rods.png').convert('RGBA'))
cleanmask=np.array(Image.open(P/'F058_wrist_cleanup_zero_call_001/internal_wrist_only_mask.png').convert('L'))>127
native[cleanmask,:3]=A[cleanmask,:3]
H,W=A.shape[:2];yy,xx=np.indices((H,W));native[:,:447]=0
# Remove returned wood fragments before constructing the two new rigid axes.
# This is technical-target prop isolation, never a production human repair.
nr,ng,nb=native[:,:,:3].astype(float).transpose(2,0,1)
oldwood=(native[:,:,3]>20)&(nr>125)&(ng>80)&(nr>ng+8)&(nb<ng*.8)&(xx<449)&(yy>400)&(yy<475)
old_axes=(np.abs(yy-(-19/137*xx+(436+19/137*461)))<4)|(np.abs(yy-(56/165*xx+(462-56/165*489)))<4)
prop_remove=binary_dilation(oldwood&old_axes,iterations=1)
native[prop_remove]=0
Image.fromarray(np.uint8(prop_remove)*255).save(F/'technical_old_T_prop_isolation_mask.png')
# Complete native child's continuous pose field is construction input only.
# Both elbows and wrists move toward the torso; retain forearm air rather than
# lifting one forearm through the other. Feet stay fixed. No old fist reference.
controls=[([461,436],[8,-1]),([480,440],[8,-1]),([511,444],[7,-1]),([557,455],[4,-1]),([566,414],[2,0]),([489,462],[2,2]),([505,477],[2,2]),([530,473],[3,2]),([623,483],[2,1]),([661,419],[1,1]),([619,400],[2,0]),([622,530],[2,1]),([625,640],[1,1]),([612,700],[1,1]),([611,270],[1,0]),([585,195],[1,0]),([700,320],[1,0]),([570,820],[0,0]),([683,820],[0,0]),([535,890],[0,0]),([600,910],[0,0]),([658,910],[0,0]),([718,900],[0,0]),([445,150],[0,0]),([795,150],[0,0]),([445,935],[0,0]),([795,935],[0,0])]
points=np.array([q[0] for q in controls],float);deltas=np.array([q[1] for q in controls],float)
rbf=RBFInterpolator(points,deltas,kernel='thin_plate_spline',degree=1,smoothing=0)
x0,y0,x1,y1=440,140,805,935;ch,cw=y1-y0,x1-x0
gy,gx=np.mgrid[0:ch:4,0:cw:4];samples=np.column_stack([gx.ravel()+x0,gy.ravel()+y0]);values=rbf(samples).reshape(gy.shape+(2,))
dy,dx=np.indices((ch,cw));sy=dy.astype(float);sx=dx.astype(float)
for _ in range(7):
    vx=map_coordinates(values[:,:,0],[sy/4,sx/4],order=3,mode='nearest');vy=map_coordinates(values[:,:,1],[sy/4,sx/4],order=3,mode='nearest');sx=dx-vx;sy=dy-vy
crop=native[y0:y1,x0:x1];alpha=crop[:,:,3].astype(float)/255;premult=crop[:,:,:3].astype(float)*alpha[:,:,None]
wa=map_coordinates(alpha,[sy,sx],order=3,mode='constant',cval=0).clip(0,1)
wr=np.stack([map_coordinates(premult[:,:,k],[sy,sx],order=3,mode='constant',cval=0) for k in range(3)],2)
warped=np.zeros_like(crop);warped[:,:,3]=np.rint(wa*255).astype('uint8');warped[:,:,:3]=np.rint(np.divide(wr,wa[:,:,None],out=np.zeros_like(wr),where=wa[:,:,None]>1e-6)).clip(0,255).astype('uint8')
human=np.zeros_like(A);human[y0:y1,x0:x1]=warped
# Keep both complete support feet exactly fixed in this technical candidate.
human[850:]=native[850:]
props=Image.new('RGBA',(W*4,H*4));d=ImageDraw.Draw(props)
axes=json.loads((P/'cam20_crane_lamp_left_001/registration_input.json').read_text())['rods']
for role in ['C_N','C_B']:
    q=axes[role];ends=[q['shaft_tip_master_px'],[952,q['slope']*952+q['intercept']]]
    d.line([tuple(v*4 for v in p) for p in ends],fill='#675034',width=16);d.line([tuple(v*4 for v in p) for p in ends],fill='#b28b52',width=10)
tdata=[]
for role,front,pin in [('T_H',[323,469],[469,435]),('T_S',[323,390],[491,464])]:
    m=(pin[1]-front[1])/(pin[0]-front[0]);b=pin[1]-m*pin[0];tail=[pin[0]+20,m*(pin[0]+20)+b];ends=[front,tail]
    d.line([tuple(v*4 for v in p) for p in ends],fill='#675034',width=16);d.line([tuple(v*4 for v in p) for p in ends],fill='#b28b52',width=10)
    tdata.append({'role':role,'front':front,'pin':pin,'tail':tail,'slope':m,'intercept':b,'owner':'X.R' if role=='T_H' else 'X.L'})
# T_S is drawn second, in front at the X. Native pads are above their shafts.
G=A.copy();G[:,:835]=0
target=Image.alpha_composite(props.resize((W,H),Image.Resampling.LANCZOS),Image.fromarray(G));target=Image.alpha_composite(target,Image.fromarray(human));T=np.array(target);T[:,835:]=A[:,835:]
Image.fromarray(T).save(I/'01_unique_complete_F061_target_REVIEW_ONLY.png')
Image.fromarray(T).crop((300,380,715,550)).resize((1245,510),Image.Resampling.NEAREST).save(I/'02_same_view_dual_clamps_X_3x.png')
font=ImageFont.truetype(str(P.parents[2]/'assets/fonts/NotoSansSC-VF.ttf'),20);card=Image.new('RGB',(1080,620),'#e7ebee');dc=ImageDraw.Draw(card)
dc.text((15,12),'058实物身份：仅头颈、服装和露趾鞋；无旧整身／旧拳姿',font=font,fill='#263743')
for box,xy,size in [((520,140,740,385),(20,60),(300,334)),((547,345,705,427),(350,60),(316,164)),((565,545,715,660),(700,60),(300,230)),((500,835,742,925),(350,350),(484,180))]:
    q=Image.fromarray(A).crop(box);bg=Image.new('RGBA',q.size,'#bdc1c4');bg.alpha_composite(q);card.paste(bg.convert('RGB').resize(size,Image.Resampling.LANCZOS),xy)
dc.text((20,568),'白圆领／密集乳白点裙／红搭带露趾鞋；原生掌腕连续，不加腕环',font=font,fill='#263743');card.save(I/'03_058_identity_clothes_shoes_patches_only.png')
edit=binary_dilation((human[:,:,3]>0)|(native[:,:,3]>0),iterations=12)&(xx<810)
edit|=(xx>305)&(xx<540)&(yy>375)&(yy<495)
Image.fromarray(np.uint8(edit)*255).convert('RGB').save(I/'04_complete_child_T_rods_only_white_mask.png')
bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(T));bg.convert('RGB').save(F/'complete_target_gray_REVIEW_ONLY.jpg',quality=96)
crop=bg.crop((300,380,715,550)).convert('RGB');crop.save(F/'contacts_1x_REVIEW_ONLY.png');crop.resize((1245,510),Image.Resampling.NEAREST).save(F/'contacts_3x_REVIEW_ONLY.png')
q1,q2=tdata;crossx=(q2['intercept']-q1['intercept'])/(q1['slope']-q2['slope']);cross=[crossx,q1['slope']*crossx+q1['intercept']]
assert crossx<min(q1['pin'][0],q2['pin'][0]);assert np.array_equal(T[:,835:],A[:,835:]);assert not np.any(edit[:,810:])
prompt='''只准备F061这一候选采样的完整小满新绘。第一图是从058原生完整体量继续前进的唯一新施工target，连续变形只用于指导，不是最终画稿；第二图是同视角双掌与X放大，第三图仅058头颈/服装/露趾鞋局部身份，不提供旧整身或拳姿，第四图白域为完整小满与两根龟签，奶奶黑域严格固定。
仍在058–077首次绞签窗，肩、肘、完整前臂带腕继续向身体内收并小幅转动。两条前臂分开，保持可读空气；头颈胸盆整体连贯，双脚原位支撑，不拉长骨头、不只扭脸、不跳到084交叉峰。双掌与双腕须自然新绘、皮肤连续，不照抄施工插值纹理，不留灰镯/黑环式腕接缝。
角色自身R始终T_H头签，L始终T_S壳签，不交换偶端或手别。T_H前端约(323,469)，R拇食真对夹约(469,435)；T_S前端约(323,390)，L拇食真对夹约(491,464)。两根硬直杆在双掌前形成比058有所推进的X，T_S近遮T_H远；每掌真实一拇四指、指腹对握同一根杆，三指自然卷曲，完整掌腕臂连贯。不能贴旧拳、截指、拉长臂或把两杆画成软绳。
按058实物保持儿童头身、深棕红花双马尾、白彼得潘圆领、黄泡袖、密集乳白圆点和红搭带露趾凉鞋；场景光后接，不烘焙光条。奶奶全身、原047真上杆对夹、下杆尾净空及玉镯均锁定黑域，不重生。输出单张1672×941透明人物层，同画布同站位，不缩放裁切，不加骨架、施工圆圈、背景、地影、文字、额外杆或额外帧。'''
(F/'prompt_prepared_NOT_SUBMITTED_zh.txt').write_text(prompt+'\n');paths=[I/n for n in ['01_unique_complete_F061_target_REVIEW_ONLY.png','02_same_view_dual_clamps_X_3x.png','03_058_identity_clothes_shoes_patches_only.png','04_complete_child_T_rods_only_white_mask.png']]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[{'order':i+1,'path':str(p.resolve()),'sha256':sha(p),'size':list(Image.open(p).size)} for i,p in enumerate(paths)]
(F/'tool_args_prepared_NOT_SUBMITTED.json').write_text(json.dumps({'prompt':prompt,'transparent_background':True,'referenced_image_paths':[r['path'] for r in rows]},ensure_ascii=False,indent=2)+'\n')
contract={'status':'F061_SAMPLING_CANDIDATE_INPUT_ONLY_ASTRA_SHORT_GATE_PENDING','frame_label':61,'frozen_exposure':False,'new_holds_assigned':False,'new_image_calls':0,'submitted':False,'generation_authorized':False,'source058':str(source),'source058_sha256':sha(source),'source058_wrist_cleanup_gate_pending':True,'target_method':'single smooth whole-child TPS construction guide only; complete native volumes, no final-art warp adoption','controls_source_plus_delta':controls,'rigid_T_rods':tdata,'X_front_of_both_palms':cross,'TS_foreground_TH_background':True,'no_hand_or_endpoint_swap':True,'frozen_G_RGBA_exact':True,'identity_reference_only058_head_neck_clothes_shoes':True,'inputs':rows}
(F/'INPUT_MANIFEST.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'candidate':61,'X':cross,'angle_degrees':math.degrees(abs(math.atan(q2['slope'])-math.atan(q1['slope']))),'new_calls':0,'input_count':4},ensure_ascii=False))
