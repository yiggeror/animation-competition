from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageChops
import ast,math,json,hashlib,copy
import numpy as np
ROOT=Path('/workspace/scratch/f060b5601755')
OUT=Path(__file__).resolve().parent
SRC=ROOT/'astra_s08_five_contacts_20261018_1326'
ns={'__file__':str(OUT/'build_reference.py')}
exec(compile((SRC/'build_proposals.py').read_text().split('STATES=[')[0],'read_only_helpers','exec'),ns)
# Copy only the independently inspectable head schematic function, without running source output loops.
tree=ast.parse((SRC/'revision2_1348/build_first_two.py').read_text())
headnode=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='head_turn')
exec(compile(ast.Module(body=[headnode],type_ignores=[]),'head_definition_only','exec'),ns)
INK=ns['INK']; BG=ns['BG'];SKIN=ns['SKIN'];FAR='#b8a594';CLOTH=ns['CLOTH'];font=ns['font'];sm=ns['sm'];tiny=ns['tiny'];poly=ns['poly'];bez=ns['bez'];lamp=ns['lamp'];head=ns['head_turn'];WICK=ns['WICK'];lever=ns['lever'];dash=ns['dash'];tr=ns['tr']
S={
 41:dict(R=[(870,735),(1020,1010),(1275,865)],L=[(1050,680),(1080,910),(1150,790)],face=(1000,510),hip=(690,1080),br=(900,1080),lift=1),
 66:dict(R=[(835,715),(820,1015),(1080,1015)],L=[(1050,680),(1045,940),(1150,790)],face=(950,490),hip=(690,1080),br=(885,1080),lift=1),
 78:dict(R=[(810,695),(800,970),(1020,1012)],L=[(1050,680),(1045,945),(1150,790)],face=(915,475),hip=(690,1080),br=(875,1080),lift=1),
 79:dict(R=[(807,694),(797,966),(1015,1011)],L=[(1050,680),(1044,950),(1143,798)],face=(910,474),hip=(690,1080),br=(873,1080),lift=1),
 80:dict(R=[(804,692),(794,961),(1008,1010)],L=[(1050,680),(1042,954),(1135,807)],face=(905,472),hip=(690,1080),br=(871,1080),lift=.5),
 82:dict(R=[(800,690),(790,955),(1000,1010)],L=[(1050,680),(1040,960),(1115,820)],face=(900,470),hip=(690,1080),br=(870,1080),lift=0),
 96:dict(R=[(650,650),(690,925),(915,1000)],L=[(930,650),(950,930),(1070,840)],face=(790,435),hip=(655,1090),br=(850,1080),lift=0)
}
# Smoothly varying-width swept curves, NOT circular stick-joint caps.
def curve_quad(a,b,c,n=20):
 return [((1-t)**2*a[0]+2*(1-t)*t*b[0]+t*t*c[0],(1-t)**2*a[1]+2*(1-t)*t*b[1]+t*t*c[1]) for t in [i/n for i in range(n+1)]]
def unit(a,b):
 dx=b[0]-a[0];dy=b[1]-a[1];L=math.hypot(dx,dy);return(dx/L,dy/L)
def mix(a,b,t):return(a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t)
def sweep(d,points,widths,color,outline=True):
 left=[];right=[]
 for i,(p,r) in enumerate(zip(points,widths)):
  a=points[max(0,i-1)];b=points[min(len(points)-1,i+1)];u=unit(a,b);N=(-u[1],u[0]);left.append((p[0]+N[0]*r,p[1]+N[1]*r));right.append((p[0]-N[0]*r,p[1]-N[1]*r))
 ps=left+right[::-1];d.polygon(ps,fill=color)
 if outline:d.line(ps+[ps[0]],fill=INK,width=3,joint='curve')
 return left,right

def solid_skin_sweep(d,pts,widths,color):
 im=d._image;m=Image.new('L',im.size,0);md=ImageDraw.Draw(m)
 for i in range(len(pts)-1):
  a,b=pts[i:i+2];ra,rb=widths[i:i+2];u=unit(a,b);N=(-u[1],u[0])
  md.polygon([(a[0]+N[0]*ra,a[1]+N[1]*ra),(b[0]+N[0]*rb,b[1]+N[1]*rb),(b[0]-N[0]*rb,b[1]-N[1]*rb),(a[0]-N[0]*ra,a[1]-N[1]*ra)],fill=255)
 for p,r in zip(pts,widths):md.ellipse((p[0]-r,p[1]-r,p[0]+r,p[1]+r),fill=255)
 u=unit(pts[0],pts[1]); yy,xx=np.indices((im.height,im.width));a=np.asarray(m).copy();a[((xx-pts[0][0])*u[0]+(yy-pts[0][1])*u[1])<0]=0;m=Image.fromarray(a);inner=m.filter(ImageFilter.MinFilter(5));edge=ImageChops.subtract(m,inner)
 im.paste(color,(0,0,im.width,im.height),m);im.paste(INK,(0,0,im.width,im.height),edge)

def arm(d,a,b,c,far=False):
 # Full skin envelope rounds the elbow through one continuous contour.
 before=mix(b,a,.16);after=mix(b,c,.22)
 pts=[mix(a,b,t) for t in [0,.18,.38,.58,.74,.84]]+curve_quad(before,b,after,20)[1:]+[mix(b,c,t) for t in [.34,.52,.72,.88,1]]
 # width follows arclength; one elbow volume, taper to the original wrist envelope.
 lens=[0]
 for x,y in zip(pts,pts[1:]):lens.append(lens[-1]+math.dist(x,y))
 elbowd=math.dist(a,b)
 ws=[]
 for v in lens:
  if v<elbowd*.54:r=39-(v/(elbowd*.54))*4
  elif v<elbowd:r=35-(v-elbowd*.54)/(elbowd*.46)*1
  else:r=34-(v-elbowd)/(max(lens[-1]-elbowd,1))*9
  ws.append(r*(.95 if far else 1))
 solid_skin_sweep(d,pts,ws,FAR if far else SKIN)
 if far:
  u=unit(b,c);N=(-u[1],u[0]);p0=(c[0]-N[0]*22,c[1]-N[1]*22);pc=mix(b,c,.36);p1=(pc[0]-N[0]*17,pc[1]-N[1]*17);d.line(bez(p0,mix(p0,p1,.30),mix(p0,p1,.75),p1,22),fill='#877361',width=2)
 # Short visible inner crease rather than a ring separating two bones.
 u=unit(b,a);v=unit(b,c);q=(b[0]+(u[0]+v[0])*19,b[1]+(u[1]+v[1])*19)
 d.line(bez((q[0]-8,q[1]-6),(q[0]-1,q[1]-11),(q[0]+8,q[1]-4),(q[0]+10,q[1]+2),12),fill='#887568',width=2)
 # Real sleeve exits at about half upper-arm projection, close to new mother.
 end=mix(a,b,.48);spts=[mix(a,end,i/20) for i in range(21)];sw=[44-6*i/20 for i in range(21)];sweep(d,spts,sw,'#91a2ad' if far else '#a5b1bb')
 return end

def empty_hand(d,w,angle,far=False,bangle=False):
 T=lambda q:tr(q,w,angle)
 # One palm outline, four relaxed fingertips and a distinct attached thumb.
 pts=[(0,-23),(22,-27),(39,-39),(51,-42),(59,-37),(57,-30),(42,-18),(55,-19),(83,-23),(94,-19),(96,-12),(91,-7),(66,-5),(94,-3),(101,3),(99,10),(91,14),(68,12),(90,17),(93,24),(88,30),(78,31),(60,26),(76,32),(78,38),(72,44),(61,43),(40,31),(0,23)]
 poly(d,[T(q) for q in pts],FAR if far else SKIN)
 for ps in [[(48,-5),(64,-4),(71,-5)],[(48,10),(66,12)],[(45,23),(60,26)]]:d.line([T(q) for q in ps],fill='#857063',width=2)
 d.line([T(q) for q in bez((24,18),(39,10),(42,-5),(40,-14),12)],fill='#8b7565',width=2)
 if bangle:
  # Only anatomical-left wrist has jade.
  p1=T((3,-25));p2=T((3,26));d.line([p1,p2],fill=INK,width=15);d.line([p1,p2],fill='#4e806d',width=10)

def torso(d,s):
 rs=s['R'][0];ls=s['L'][0];hx,hy=s['face'];hip=s['hip'];br=s['br']
 # Shoulder, neck base, chest front and hips form one oblique volume.
 contour=[(rs[0]-35,rs[1]+10),(rs[0]-23,rs[1]-28),(hx-59,hy+137),(hx+42,hy+151),(ls[0]+20,ls[1]-5),(ls[0]-21,ls[1]+75),(ls[0]-72,ls[1]+205),br,(hip[0]-115,1080)]
 poly(d,contour,CLOTH)
 poly(d,[(hx+42,hy+151),(ls[0]+20,ls[1]-5),(ls[0]-21,ls[1]+75),(ls[0]-72,ls[1]+205),br,(br[0]-34,1080),(ls[0]-105,ls[1]+195),(ls[0]-52,ls[1]+62)],'#91a1ab')
 # Neck and two collar flaps connect to the same shoulder plane.
 poly(d,[(hx-55,hy+120),(hx+32,hy+136),(hx+44,hy+187),(hx-37,hy+195)],'#d3c0aa')
 poly(d,[(hx-37,hy+181),(hx+5,hy+199),(hx-18,hy+232),(hx-65,hy+197)],'#c2cad0')
 poly(d,[(hx+42,hy+175),(hx+63,hy+199),(hx+18,hy+211),(hx+5,hy+199)],'#c2cad0')
 d.line(bez((hx+15,hy+211),(hx+6,hy+295),(br[0]+10,950),(br[0]-12,1075)),fill='#647c88',width=3)

def draw_scene(frame,annotate=False):
 s=S[frame];im=Image.new('RGB',(1920,1260),BG);d=ImageDraw.Draw(im)
 d.polygon([(910,970),(1720,910),(1920,1055),(850,1055)],fill='#d6c1a0',outline='#72614d')
 lamp(d,s['lift'])
 d.rectangle((1064,949,1136,971),fill='#bda16d',outline=INK,width=3);d.line((1066,963,1134,963),fill='#9a6951',width=6)
 d.line((1150,963,1213,960),fill='#806b48',width=6);d.ellipse((1208,955,1218,965),fill='#453c32')
 arm(d,*s['L'],True)
 torso(d,s);head(d,s['face'],WICK)
 # Far forearm is in front of its own upper arm and outside torso, behind near arm.
 # Redraw complete connected distal skin only along the already drawn path; no new elbow cap.
 arm(d,*s['R'],False)
 if frame<78:
  ns['hand_pinch'](d,s['L'][2],lever(1),kind='lever',bangle=True)
  if frame==78:
   # Withdraw thumb and uncurl first digit; contact-release diagram, no new knob location.
   empty_hand(d,s['L'][2],-.27,True,True)
 else:empty_hand(d,s['L'][2],-.27 if frame==78 else -.18,True,True)
 ra=-.55 if frame==66 else (.24 if frame==96 else .36)
 empty_hand(d,s['R'][2],ra,False,False)
 title=f'S08 F{frame:03d} / 回收结构独立修正提案'
 d.text((35,20),title,font=font,fill=INK)
 d.text((35,60),'参考门：整条肩—袖—肘—腕外廓；空手松指。保留原腕、灯、桌、盒和柴时序。',font=sm,fill='#56616b')
 d.text((35,1104),'082：罩已落座；096：坐回仍在进行。脚、座不在本视野，未声称落座支撑已核。',font=sm,fill=INK)
 d.text((35,1143),'近臂浅肤色在前，远左臂深肤色在后；远腕仍有唯一玉镯。短缩由可见肉体轮廓审，不靠等骨长数字。',font=sm,fill=INK)
 d.text((35,1182),'F078先开指，F079离杆，F080罩降，F082罩落；盒与已熄火柴始终留原桌面位置。',font=sm,fill=INK)
 d.text((35,1222),'人工结构参考 / 非人物资产 / 非三维标定 / 首三关键不改 / 待协调及Opus审查。',font=tiny,fill='#5e6a70')
 if annotate:
  for side,col,label in [('R','#226e9c','近'),('L','#9b5140','远')]:
   for name,p in zip(['肩','肘','腕'],s[side]):
    d.ellipse((p[0]-5,p[1]-5,p[0]+5,p[1]+5),fill=col)
    d.text((p[0]-65,p[1]+30),f'{label}{name} {p[0]},{p[1]}',font=tiny,fill=col)
 return im
for fr in [66,78,79,80,82,96]:
 im=draw_scene(fr);im.save(OUT/f'F{fr:03d}_continuous_retraction_PROPOSAL.png')
 if fr in [82,96]:draw_scene(fr,True).save(OUT/f'F{fr:03d}_anchors_PROPOSAL.png');im.crop((600,630,1255,1080)).resize((1310,900)).save(OUT/f'F{fr:03d}_arm_volume_detail.png')
# Comparison: old reference crop to new, same camera and scale.
for fr in [82,96]:
 old=Image.open(SRC/f'revision2_1348/reference/F{fr:03d}_B_retraction_volume_DRAFT.png').convert('RGB')
 new=Image.open(OUT/f'F{fr:03d}_continuous_retraction_PROPOSAL.png')
 box=(540,600,1255,1080);a=old.crop(box);b=new.crop(box);cmp=Image.new('RGB',(1430,520),BG);cmp.paste(a,(0,40));cmp.paste(b,(715,40));cd=ImageDraw.Draw(cmp);cd.text((12,7),'旧：近肘过右，前臂挤短',font=sm,fill=INK);cd.text((727,7),'新：腕保留，肘回肩下，整臂连续',font=sm,fill=INK);cmp.save(OUT/f'F{fr:03d}_old_new_same_scale.jpg')
# Four temporal construction frames at identical scale, projected anchors shown.
strip=Image.new('RGB',(1920,850),BG);dd=ImageDraw.Draw(strip)
for k,fr in enumerate([66,78,82,96]):
 im=draw_scene(fr,True).crop((550,590,1270,1080));im.thumbnail((470,650));x=k*480;strip.paste(im,(x,70));dd.text((x+14,15),f'F{fr:03d}',font=font,fill=INK)
 dd.text((x+10,565),['66：柴已放；右手低路退','78：左指打开，罩仍高','82：左手离杆，罩落座','96：肩胸头一起坐回'][k],font=sm,fill=INK)
dd.text((25,640),'中间坐标为路径提案，不能替代真实绘图；两前臂在主要可见段保持纵向净空，袖根轻遮挡必须断线。',font=sm,fill=INK)
dd.text((25,680),'近肘：820,1015 → 800,970 → 790,955 → 690,925；远肘：1045,940 → 1045,945 → 1040,960 → 950,930。',font=sm,fill=INK)
dd.text((25,720),'082/096腕沿原提案不变；上臂与前臂不缩放，同一角色的成图仍需逐段核轮廓、手尺度和肩颈体积。',font=sm,fill=INK)
strip.save(OUT/'F066_F078_F082_F096_path_PROPOSAL.jpg')
for fr,s in S.items():s['projection_lengths']={side:[round(math.dist(s[side][i],s[side][i+1]),2) for i in [0,1]] for side in ['R','L']}
record={'status':'INDEPENDENT_REFERENCE_PROPOSAL_NOT_PRODUCTION_APPROVED','source_final_F000_SHA256':'c803571d4a6446e783fcbeb7aef41d65c1862ff3bf78a9a53f34b4631170e3f3','source_measurement':'astra_s08_first_mother_20261018_1433/new_mother_measurements/F000_projected_measurements.json','source_measurement_uncertainty':'manual 5–12px; projected anchors, NOT bones or 3D','unchanged':['first3 submitted states','F082/F096 original shoulder/wrist/face/body endpoint anchors','lamp base1415,965.6 and wick1415,794.573','table box and match positions','F066 release/F078 open/F079 gap/F080 hood descent/F082 seated hood/F096 in-progress return timing'],'changed':['F082 near elbow880,995→790,955; far1080,940→1040,960','F096 near elbow775,940→690,925; far1035,955→950,930','whole connected arm silhouette and relaxed empty hands; near wrist flexes down20.6deg at078/082,13.75deg at096 so thumb does not overlap far elbow','intermediate elbow/shoulder/wrist path is a NEW PROPOSAL requiring second review'],'states':S}
json.dump(record,open(OUT/'retraction_path_PROPOSAL.json','w'),ensure_ascii=False,indent=2)
