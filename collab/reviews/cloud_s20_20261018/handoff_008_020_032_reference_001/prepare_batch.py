"""Zero-model-call construction references and fully bound, unsubmitted requests.
These technical plates are NOT character drawings or generated animation states.
"""
from pathlib import Path
import hashlib,json,math,csv
import numpy as np
from PIL import Image,ImageDraw,ImageFont

P=Path(__file__).resolve().parent; PACK=P.parent
MASTER=PACK/'F000/f000_scene_gate_001/cleanup/S20_F000_master_clean.png'
LOCK='55ce8658e3454dcb92e8408dda25bc678f856d82bbb10cd80ff06a01fa0ab0c8'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(MASTER)==LOCK
im=Image.open(MASTER).convert('RGBA'); A=np.array(im); SIZE=im.size
fontpath=PACK.parents[2]/'assets/fonts/NotoSansSC-VF.ttf'
font=lambda n:ImageFont.truetype(str(fontpath),n)
reg=json.loads((PACK/'F000/f000_scene_gate_001/registration_input.json').read_text())
axes=reg['rods']; C={'R':'#157983','L':'#8054a0','TH':'#127ca3','TS':'#bb3d7c','CB':'#3d815b','CN':'#c27b26'}
states={8:{'lean':20,'head_lift':-3,'R_sh':[611,417],'L_sh':[656,428],
           'R_palm':[806,318],'L_palm':[837,455],'closed':False,'G_release':False},
        20:{'lean':40,'head_lift':-7,'R_sh':[631,409],'L_sh':[676,429],
            'R_palm':[820,axes['T_H']['slope']*820+axes['T_H']['intercept']],
            'L_palm':[850,axes['T_S']['slope']*850+axes['T_S']['intercept']],
            'closed':True,'G_release':False},
        32:{'lean':40,'head_lift':-7,'R_sh':[631,409],'L_sh':[676,429],
            'R_palm':[820,axes['T_H']['slope']*820+axes['T_H']['intercept']],
            'L_palm':[850,axes['T_S']['slope']*850+axes['T_S']['intercept']],
            'closed':True,'G_release':True}}

def ik(S,W,l1,l2,side):
 S=np.array(S,float);W=np.array(W,float);v=W-S;d=np.linalg.norm(v);u=v/d;n=np.array([-u[1],u[0]])
 assert abs(l1-l2)<d<l1+l2
 along=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(l1*l1-along*along)
 choices=[S+u*along+n*h,S+u*along-n*h]
 E=min(choices,key=lambda e:e[1]) if side=='up' else max(choices,key=lambda e:e[1])
 if isinstance(side,tuple): E=min(choices,key=lambda e:np.linalg.norm(e-np.array(side)))
 return [list(S),list(E),list(W)]

def stroke(d,pts,col,width=3,dash=False):
 pts=[tuple(p) for p in pts]
 if not dash:d.line(pts,fill=col,width=width,joint='curve');return
 for a,b in zip(pts,pts[1:]):
  v=np.array(b)-a;le=np.linalg.norm(v)
  for s in np.arange(0,le,11):d.line([tuple(np.array(a)+v*s/le),tuple(np.array(a)+v*min(s+6,le)/le)],fill=col,width=width)

def capsule(d,a,b,r0,r1,col):
 a=np.array(a);b=np.array(b);v=b-a;n=np.array([-v[1],v[0]])/np.linalg.norm(v)
 d.polygon([tuple(a+n*r0),tuple(b+n*r1),tuple(b-n*r1),tuple(a-n*r0)],fill=col)
 for q,r in [(a,r0),(b,r1)]:d.ellipse((q[0]-r,q[1]-r,q[0]+r,q[1]+r),fill=col)

def pastel(col,a=.78):
 return tuple(round(int(col[i:i+2],16)*(1-a)+255*a) for i in [1,3,5])+(255,)

def arm(d,chain,col,far=False):
 S,E,W=chain
 if not far:
  capsule(d,S,E,14,11,pastel(col));capsule(d,E,W,11,7,pastel(col))
 stroke(d,chain,col,3,dash=far)
 for q in chain:d.ellipse((q[0]-4,q[1]-4,q[0]+4,q[1]+4),fill='white',outline=col,width=2)
 for a,b,r in [(S,E,12),(E,W,8)]:
  q=(np.array(a)+b)/2;v=np.array(b)-a;v=v/np.linalg.norm(v);n=np.array([-v[1],v[0]])
  stroke(d,[q-n*r,q+n*r],col,2)

def hand(d,p,col,closed,axis=None,left=False):
 x,y=p;sgn=-1 if left else 1
 d.ellipse((x-20,y-16,x+20,y+16),fill=pastel(col,.85),outline=col,width=2)
 if closed:
  # Explicit transverse thumb/finger sections. Technical geometry, not finished hands.
  m=axis['slope'];n=np.array([-m,1])/math.hypot(m,1);v=np.array([1,m])/math.hypot(m,1)
  for k in [-1,1]:
   c=np.array(p)+n*k*5;stroke(d,[c-v*7,c+v*7],col,3)
  d.arc((x-16,y-21,x+19,y+15),210,60,fill=col,width=3)
 else:
  for i,(dx,dy) in enumerate([(26,-16),(31,-7),(32,3),(28,12)]):
   stroke(d,[(x+sgn*5,y+dy*.5),(x+sgn*dx,y+dy)],col,3)
  stroke(d,[(x,y-5),(x+sgn*3,y-25),(x+sgn*14,y-25)],col,3)

def editmask(state):
 m=Image.new('L',SIZE);d=ImageDraw.Draw(m)
 # Whole child change is permitted; source shoes/ankle contact strip stays fixed.
 d.polygon([(445,165),(715,165),(884,260),(884,505),(737,560),(729,840),(498,840),(445,687)],fill=255)
 # The original high crane rods remain immutable even near the raised child hand.
 for role in ['C_B','C_N']:
  a=axes[role];x0=a['shaft_tip_master_px'][0]
  d.line([(x0,a['slope']*x0+a['intercept']),(929,a['slope']*929+a['intercept'])],fill=0,width=8)
 if state['G_release']:
  d.polygon([(892,409),(1023,410),(1097,415),(1112,458),(1052,487),(1039,525),(919,526),(885,479)],fill=255)
  # Keep the already approved near-L arm, jade, torso-front lower edge and all head.
  d.polygon([(978,332),(1016,332),(1094,376),(1184,379),(1174,432),(1142,453),(1094,446),(1011,400),(977,375)],fill=0)
 d.rectangle((0,840,SIZE[0]-1,SIZE[1]-1),fill=0)
 return m

def make_plate(frame,s):
 f=P/f'F{frame:03}';f.mkdir(parents=True,exist_ok=True)
 bg=Image.new('RGBA',SIZE,'#f4f5f6');bg.alpha_composite(im)
 b=np.array(bg);lum=(b[:,:,:3]@np.array([.2126,.7152,.0722])).astype('uint8')
 # Gray source child is a size/identity ghost only. Colored volumes give target pose.
 ghost=(np.indices(A.shape[:2])[1]<885)&(A[:,:,3]>0)
 for c in range(3):b[:,:,c][ghost]=(.22*lum[ghost]+.78*245).astype('uint8')
 if s['G_release']:
  em=np.array(editmask(s))>0;gm=em&(np.indices(A.shape[:2])[1]>=885)
  for c in range(3):b[:,:,c][gm]=(.22*lum[gm]+.78*245).astype('uint8')
 board=Image.fromarray(b).convert('RGBA');d=ImageDraw.Draw(board,'RGBA')
 # Remove old arm/hand occupancy from the UNIQUE target, rather than leave a
 # competing ghost pose for the model. Mother/identity source is a separate input.
 d.polygon([(557,410),(646,420),(670,448),(715,445),(755,423),(791,426),
            (819,442),(827,496),(795,528),(731,531),(654,522),(604,512),(571,469)],fill='#f4f5f6')
 if s['G_release']:
  d.polygon([(888,411),(975,410),(1027,419),(1027,470),(974,478),(910,479)],fill='#f4f5f6')
 # Same four hard shaft axes, no change to the upper hand/registration problem.
 for key,label in [('T_H','TH'),('T_S','TS'),('C_B','CB'),('C_N','CN')]:
  a=axes[key];x0=a['shaft_tip_master_px'][0];x1=944 if key.startswith('T') else 929
  pts=[(x0,a['slope']*x0+a['intercept']),(x1,a['slope']*x1+a['intercept'])]
  stroke(d,pts,C[label],3)
  d.text((x0-48,pts[0][1]-26),key,font=font(18),fill=C[label])
 # Full structural masses: head, rib cage, pelvis, legs to locked shoe contacts.
 lean=s['lean'];cx=575+lean;hy=276+s['head_lift']
 d.ellipse((cx-76,hy-85,cx+76,hy+85),outline=C['R'],width=2)
 stroke(d,[(cx-70,hy),(cx+70,hy)],C['R'],1,True)
 neck=[(605+lean,368+s['head_lift']),(610+lean,389)]
 stroke(d,neck,C['R'],6)
 chest=[613+lean,445];hip=[594+lean*.5,565]
 d.ellipse((chest[0]-47,391,chest[0]+47,494),outline=C['R'],width=2)
 d.ellipse((hip[0]-42,533,hip[0]+42,593),outline=C['R'],width=2)
 stroke(d,[chest,hip],C['R'],2)
 for side,h,knee,ank in [('R',[hip[0]-20,565],[565+lean*.18,752],[555,858]),('L',[hip[0]+20,565],[614+lean*.12,753],[616,855])]:
  stroke(d,[h,knee,ank],C[side],3,True)
  for q in [h,knee,ank]:d.ellipse((q[0]-5,q[1]-5,q[0]+5,q[1]+5),outline=C[side],width=2)
 for side,keys in [('R',('T_H',90,105,'up')),('L',('T_S',75,95,'down'))]:
  role,l1,l2,bend=keys;p=s[side+'_palm'];w=[p[0]-23,p[1]+12]
  chain=ik(s[side+'_sh'],w,l1,l2,bend);s[side+'_chain']=chain
  arm(d,chain,C[side]);hand(d,p,C[side],s['closed'],axes[role])
  stroke(d,[w,p],C[side],3)
  for name,q in zip(['肩','肘','腕'],chain):d.text((q[0]-20,q[1]-25),f'X.{side}{name}',font=font(15),fill=C[side])
  d.text((p[0]-38,p[1]+22),f'X.{side} / '+('实握' if s['closed'] else '未触'),font=font(17),fill=C[side])
 if s['G_release']:
  chain=ik([1067,285],[1012,480],math.hypot(9,150),math.hypot(92,4),(1076,435));s['G_R_chain']=chain
  arm(d,chain,'#b95f27',far=True);hand(d,[978,487],'#b95f27',False,left=True)
  stroke(d,[[1012,480],[978,487]],'#b95f27',3)
  d.text((951,525),'G.R开掌后撤 / 0接触',font=font(17),fill='#a14f1f')
 else:
  s['G_R_chain']=[[1067,285],[1076,435],[984,439]]
  d.text((933,486),'G.R仍支持两龟签',font=font(17),fill='#a14f1f')
 # Label outside the figure, not over faces or contacts.
 title={8:'接握前：孩子两掌未触杆',20:'共同承重：接收已闭、供应未松',32:'释放完成：孩子双握稳、供应撤离'}[frame]
 d.text((24,24),f'S20 F{frame:03} · {title}',font=font(25),fill='#263743')
 notes=['施工参考，不是新增绘图/动画帧','灰影＝锁母的体量/身份参考','青紫＝该态目标骨链与截面','X.R→T_H；X.L→T_S','G.L始终持两鹤签，不改高臂','整头颈、胸髋随靠近；脚点锁定','蓝紫掌圈/短横只示接触剖面','完稿须画真实拇指/四指对握','母层55ce不重生；高鹤另裁','骨链是施工设定，非实测3D骨长']
 for i,t in enumerate(notes):d.text((24,85+i*31),t,font=font(19),fill='#46545f')
 d.text((25,810),'母身高比X/G≈0.844；统一尺度',font=font(19),fill='#263743')
 d.text((25,845),'禁止沿旧代码人物掰动作；禁画偶/场景光',font=font(18),fill='#263743')
 d.text((25,885),'参考008→020→032整组核批后连续制作',font=font(18),fill='#263743')
 board.convert('RGB').save(f/'02_full_volume_target.png')
 crop=(550,285,1115,540)
 board.crop(crop).resize((1695,765),Image.Resampling.NEAREST).save(f/'03_same_view_contacts_3x.png')
 mask=editmask(s);mask.save(f/'04_edit_white.png')
 return f

COMMON='''输出一张1672×941透明二维手绘人物层，人物造型、自然线条与中性固有色沿用第一张锁定母态55ce；不重新设计人物或改头身大小。第一张是身份/材质与不动部位参考，第二张彩色施工体量是本态唯一动作目标；灰影只表母态体量，不是第二套动作。第三张仅从第二张同视角直接3倍放大，无另一姿态；第四张单一白域可编辑、黑域必须保留，禁止黑白语义反转。
只画奶奶和小满两人及四根原竹签；不画字母、标记、剖面圈、隐藏骨线、施工灰影、皮影偶、场景、光照或影子。不把技术胶囊/椭圆当作完稿：新肩袖、上臂、肘、前臂、腕和拇指/四指要画成自然完整体量，前后层次清楚；禁止伸长骨段或只拖动手。小满靠近须整头颈、胸廓、骨盆与双腿支撑共同配合，原鞋/踝接地条保留，尺度不变。彩色骨链是施工设定，非医学骨测；朝向/短缩应自然，肘腕不能错接或变成第三只手。
整个接龟小段固定：T_H接turtle.head[20,0]，T_S接turtle.shell[0,40]；X.R只接T_H，X.L只接T_S。C_B接crane.body[-75,6]，C_N接crane.neck3[10,0]，全程仍由高位带唯一玉镯的G.L持有，不在本段转给G.R。奶奶高L完整肩袖/臂/掌/镯和头颈衣裤脚等黑域保持原像素。高鹤偶面接景问题另裁，本次不得为避灯而改高握臂、灯或相机。
两根龟签是独立刚性直杆，同一轴线要穿过各自接收掌和供应掌，不折杆、不合成一杆、不换偶端。竹签前段沿母态实物轴；完稿的掌内段由指掌正确遮挡，不能用裸杆直接穿手心冒充抓握。衣肉接回、单镯、自然手背/掌厚、阴影体积都保持；不抹平体积、不烘焙场景暖光。透明边保留真实指尖/发丝/杆尖抗锯齿。
'''
SPEC={8:'''本态F008是接触前，不是共同握。小满R掌从上侧向T_H张开、L掌从下侧向T_S张开；两掌及所有指尖与任一龟杆均有清楚空气隙，孩子接触数严格0。R腕/前臂绕过偶面，经过杆的人侧进深，不能把二维遮挡误画成压住杆。按第二张略前倾/转胸靠近、双上臂及肘腕共同抬到接握预备位置；不能只把F000两掌搬上去。奶奶低位裸腕G.R仍闭合并支持两龟签，全部奶奶像素保持锁母；不得先松供应手或把孩子画成已握。''',
20:'''本态F020是共同承重。X.R的拇指对屈曲食/中指真实夹住T_H；X.L拇指对屈曲四指真实握住T_S，两根各有独立掌内接触段。原供应掌G.R仍闭合支持两杆后端。接收两握点沿杆轴错开，既不挤进同一供应掌，也不把两签合成一签。两根都要表现拇指和对侧指腹的包夹，不能只贴杆/盖在杆上。全部奶奶像素保持锁母。''',
32:'''本态F032是释放完成。小满两只接收掌及T_H/T_S握点按F020目标继续稳定，不能突然松指、换签或移偶端。奶奶低位裸腕G.R先前已确认接收稳定，现在拇指和四指完全开掌，并由完整远R前臂连同腕沿参考向右下后撤，和两龟签有清楚空隙，G.R接触数0。保留远R从远肩穿过躯干后方至新腕的连续真实体量，只画正常遮挡下能看见的部分，不能从衣襟凭空冒掌。清除原供应掌/腕占据处，补应露出的布面、空隙和原两杆后端；两杆不缩短、不融合，以各杆独立收尾与深度次序保持身份。高位近L和玉镯完全保留。'''}

def main():
 out=[]
 for frame,s in states.items():
  f=make_plate(frame,s)
  prompt=COMMON+'\n'+SPEC[frame]+'\n本次只生成这一时刻，禁止附加其他帧、接触表或多视图。'
  (f/'prompt_zh.txt').write_text(prompt+'\n')
  refs=[MASTER,f/'02_full_volume_target.png',f/'03_same_view_contacts_3x.png',f/'04_edit_white.png']
  args={'prompt':prompt,'transparent_background':True,'referenced_image_paths':[str(x.resolve()) for x in refs]}
  (f/'request_prepared.json').write_text(json.dumps({'status':'PREPARED_NOT_SUBMITTED / BATCH_REFERENCE_GATE_PENDING','submitted':False,'tool':'image_gen.imagegen','tool_args':args},ensure_ascii=False,indent=2)+'\n')
  rows=[{'order':i,'path':str(x.resolve()),'sha256':sha(x),'size':list(Image.open(x).size),'role':r} for i,(x,r) in enumerate(zip(refs,['locked mother identity/material/black-domain source','unique target construction / NOT character drawing','direct same-view detail','single edit white mask']),1)]
  (f/'input_manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
  out.append({'frame':frame,'state':s,'inputs':rows,'request_sha256':sha(f/'request_prepared.json'),'prompt_sha256':sha(f/'prompt_zh.txt')})
 (P/'batch_geometry_and_requests.json').write_text(json.dumps({'status':'PROPOSED_CONSTRUCTION / NOT_GENERATED','master_sha256':LOCK,'image_model_calls':0,'new_model_raws':0,'in_flight':0,'character_drawings_generated':0,'technical_reference_plates':3,'canvas':list(SIZE),
 'construction_bone_lengths_px':{'X.R':[90,105],'X.L':[75,95],'G.R':[math.hypot(9,150),math.hypot(92,4)]},
 'bone_note':'Constant construction segment lengths in these target plates; not measured anatomical 3D lengths. Mother may be foreshortened. These targets await batch review.',
 'sole_contacts_preserved':reg['sole_landmarks_master_px'],'rod_attachment_contract':{'T_H':['turtle.head',[20,0]],'T_S':['turtle.shell',[0,40]],'C_B':['crane.body',[-75,6]],'C_N':['crane.neck3',[10,0]]},
 'high_crane_scene_gate_independent':True,'frames':out},ensure_ascii=False,indent=2)+'\n')
 # A compact actual plate overview, clearly labelled technical reference.
 strip=Image.new('RGB',(1672*3//2,941//2+45),'#f4f5f6');d=ImageDraw.Draw(strip)
 for i,frame in enumerate(states):
  d.text((i*836+20,8),f'F{frame:03} 施工参考 / 非画稿',font=font(23),fill='#263743')
  strip.paste(Image.open(P/f'F{frame:03}/02_full_volume_target.png').resize((836,470),Image.Resampling.LANCZOS),(i*836,45))
 strip.save(P/'batch_reference_overview.png')
 assert sha(MASTER)==LOCK
 print('Prepared 3 technical plates + 3 complete four-input requests. 0 model calls / 0 new drawings.')

if __name__=='__main__':main()
