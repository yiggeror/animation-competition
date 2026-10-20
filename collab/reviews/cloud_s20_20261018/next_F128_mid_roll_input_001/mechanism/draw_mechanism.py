"""Original-puppet FK/CAM20 coordinate diagram; no character or scene rendering."""
from pathlib import Path
import json,math,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
F=Path(__file__).resolve().parent;P=F.parents[1];D=json.loads((F/'source_model_probe.json').read_text());M=json.loads((F/'constraint_preflight.json').read_text());B=D['camera_basis'];C=np.array(B['C']);fw=np.array(B['fwd']);rt=np.array(B['right']);up=np.array(B['up']);f=B['focal'];pm=np.array(D['people_to_CAM20_matrix'])
def project(p):
 d=np.array(p)-C;return np.array([960+np.dot(d,rt)/np.dot(d,fw)*f,540-np.dot(d,up)/np.dot(d,fw)*f])
def card(root,p):
 q=project([root[0],.004,root[1]]);qx=project([root[0]+.1,.004,root[1]]);qy=project([root[0],.004,root[1]+.1]);return q+(qx-q)*(-p[0]/100)+(qy-q)*p[1]/100
def screen(p):return np.array([pm[0]*p[0]+pm[2]*p[1]+pm[4],pm[1]*p[0]+pm[3]*p[1]+pm[5]])
S=1.3
polys={'shell':[[135,8],[122,46],[90,82],[40,102],[-20,104],[-75,90],[-115,60],[-138,22],[-140,2],[-100,-6],[0,-8],[100,-6]],'belly':[[118,2],[100,-10],[0,-14],[-100,-10],[-132,0],[-100,6],[0,4],[100,6]],'head':[[-12,-14],[-14,6],[-2,22],[20,26],[42,20],[56,8],[58,-4],[48,-14],[24,-20],[4,-20]],'tail':[[2,6],[-18,6],[-36,-2],[-20,-6],[2,-6]]}
for id in ['legFF','legFN']:polys[id]=[[-12,4],[14,4],[20,-22],[28,-46],[16,-54],[-2,-50],[-8,-24]]
for id in ['legBF','legBN']:polys[id]=[[-14,4],[12,6],[18,-20],[26,-44],[14,-54],[-4,-50],[-10,-26]]
polys={k:(np.array(v,float)*S).tolist() for k,v in polys.items()}
for k in range(3):
 w=(15-k*1.5)*S;nl=32*S;polys['neck'+str(k)]=[[-w*.9,0],[-w*.6,w*.85],[nl*.5,w],[nl+w*.6,w*.85],[nl+w*.9,0],[nl+w*.6,-w*.85],[nl*.5,-w],[-w*.6,-w*.85]]
(F/'original_outline_control_points.json').write_text(json.dumps({'status':'ORIGINAL_SOURCE_OUTLINE_CONTROLS_ONLY_NOT_TEXTURE_RENDER','source_turtle_scale':S,'source_turtle_sha256':D['sources'][0]['sha256'],'polys':polys},ensure_ascii=False,indent=2)+'\n')
def spline(p,per=8):
 p=np.array(p,float);out=[];n=len(p)
 for i in range(n):
  a,b,c,d=p[(i-1)%n],p[i],p[(i+1)%n],p[(i+2)%n]
  for j in range(per):
   t=j/per;out.append(.5*(2*b+(c-a)*t+(2*a-5*b+4*c-d)*t*t+(3*b-a-3*c+d)*t*t*t))
 return out
fontroot=P.parents[2]/'assets/fonts/NotoSansSC-VF.ttf';font=lambda n:ImageFont.truetype(str(fontroot),n)
im=Image.new('RGB',(1500,1050),'#eef2f4');dr=ImageDraw.Draw(im);dr.text((22,15),'F128机构预检：原龟偶 / 原CAM20 / 固定R头签、L壳签',font=font(28),fill='#172b3b');dr.text((22,55),'0调用；纯坐标机制示意，非生产渲染。以下为“最小握点位移初解”，尚未通过单握/交叉门。',font=font(20),fill='#8c2d2d')
ROI=np.array([180.,130.]);scale=.83;colors={'T_H':'#008f9c','T_S':'#bf3e83'}
def point(q,origin):return tuple(np.array(origin)+(np.array(q)-ROI)*scale)
def dashed(a,b,color,width=2):
 a=np.array(a);b=np.array(b);v=b-a;d=np.linalg.norm(v)
 for t in np.arange(0,d,10):dr.line([tuple(a+v*t/d),tuple(a+v*min(t+5,d)/d)],fill=color,width=width)
for panel,frame in enumerate([120,128]):
 origin=np.array([22+panel*742,125]);dr.rounded_rectangle((origin[0]-5,100,origin[0]+720,790),radius=8,fill='white',outline='#bcc9d0',width=2)
 dr.text((origin[0]+10,109),'F120：已过画轴+原未翻肚龟姿' if frame==120 else 'F128：原滚转41.701%的同源中间态',font=font(22),fill='#203b4b')
 state=D['states'][str(frame)];root=M['root120_registered_from_passed_axes'] if frame==120 else M['root128_same_registration_plus_original_puppet_delta'];sol=state['sol']
 def mapped(part,poly):
  parent='shell' if part=='belly' else part;s=sol[parent];a=s['a'];r=np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]]);return [point(card(root,np.array(s['o'])+r@p),origin) for p in spline(poly)]
 for j in sorted(D['rig'],key=lambda j:j['layer']):
  part=j['part'];poly=mapped(part,polys[part]);dr.polygon(poly,fill='#668d62' if part=='shell' else '#cdb68c',outline='#475f49');dr.line(poly+[poly[0]],fill='#475f49',width=2)
  if part=='shell':
   q=mapped('belly',polys['belly']);dr.polygon(q,fill='#e3c28d',outline='#786345')
 for row in M['rows']:
  id=row['id'];key='A120_master' if frame==120 else 'A128_master';gkey='source_grip_master' if frame==120 else 'grip128_master';a=np.array(row[key]);b=np.array(row[gkey]);pa=point(screen(a),origin);pb=point(screen(b),origin);col=colors[id]
  dr.line([pa,pb],fill=col,width=4);dr.rectangle((pa[0]-5,pa[1]-5,pa[0]+5,pa[1]+5),fill=col);dr.ellipse((pb[0]-7,pb[1]-7,pb[0]+7,pb[1]+7),fill='white',outline=col,width=3)
  dr.text((pa[0]-15,pa[1]-27),'head[20,0]' if id=='T_H' else 'shell[0,40]',font=font(17),fill=col);dr.text((pb[0]+10,pb[1]-12),'R / T_H' if id=='T_H' else 'L / T_S',font=font(17),fill=col)
 if frame==120:
  hm,hb=M['axis120'][0];sm,sb=M['axis120'][1];x=(sb-hb)/(hm-sm);cross=np.array([x,hm*x+hb]);rp=np.array(M['rows'][0]['source_grip_master']);dashed(point(screen(rp),origin),point(screen(cross),origin),'#9ba8af');dr.text((origin[0]+16,722),'灰虚线：现有画内T_H向可见X延伸；原偶端落在R后侧。',font=font(17),fill='#8c2d2d')
 else:
  X=np.array(M['minimal_grip_solution_audit']['axis_intersection_master']);rp=np.array(M['rows'][0]['grip128_master']);xp=point(screen(X),origin);dashed(point(screen(rp),origin),xp,'#d15142',3);dr.line([(xp[0]-9,xp[1]-9),(xp[0]+9,xp[1]+9)],fill='#d15142',width=3);dr.line([(xp[0]-9,xp[1]+9),(xp[0]+9,xp[1]-9)],fill='#d15142',width=3);dr.text((origin[0]+16,722),'红虚线交点：距L仅5.31画稿px，且在T_H的A→B段外。',font=font(17),fill='#8c2d2d')
 dr.text((origin[0]+16,674),f"原rootAngle={math.degrees(state['pose']['rootAngle']):.3f}°  /  龟尺度1.3不变",font=font(17),fill='#475e6c');dr.text((origin[0]+16,697),'两格同CAM20、同裁区、同图尺；只画原部件轮廓控制点。',font=font(16),fill='#475e6c')
dr.text((24,812),'F128最小握点初解（1672×941画稿坐标）',font=font(22),fill='#203b4b')
for k,row in enumerate(M['rows']):
 a=row['A128_master'];b=row['grip128_master'];d=row['grip_delta_master'];dr.text((24,850+40*k),f"{row['id']}  偶端({a[0]:.2f},{a[1]:.2f}) → 握点({b[0]:.2f},{b[1]:.2f})；握点Δ({d[0]:+.2f},{d[1]:+.2f})；候选刚性A-B长度{row['rigid_rod_length_m']:.6f}m",font=font(19),fill=colors[row['id']])
dr.text((24,945),'假设披露：120只冻结人物，未找到120龟偶根位/朝向的冻结值；本图以原未翻肚龟姿对齐120轴线，再沿原滚转增量推进128。',font=font(17),fill='#7c3c34');dr.text((24,977),'该初解不作为四输入目标；需先联解/审定整龟注册与握点分支。未改相机、模型尺度、绑定、共享代码或后态。',font=font(17),fill='#7c3c34')
im.save(F/'F120_F128_same_CAM20_mechanism_PRELIMINARY_BLOCKED.png')
print(json.dumps({'png':str(F/'F120_F128_same_CAM20_mechanism_PRELIMINARY_BLOCKED.png'),'sha256':hashlib.sha256((F/'F120_F128_same_CAM20_mechanism_PRELIMINARY_BLOCKED.png').read_bytes()).hexdigest()},ensure_ascii=False))
