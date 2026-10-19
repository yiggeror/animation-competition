#!/usr/bin/env python3
"""Static, manually specified volume/contact reference plates; no image model or rig."""
from pathlib import Path
import math,json,html
D=Path(__file__).resolve().parents[1];OUT=D/'reference/svg'
C={'ink':'#303b46','far':'#b4bbc5','near':'#f4cdb2','shirt':'#99b9d8','dress':'#efd35d','TH':'#167d9f','TS':'#b24779','CB':'#3d7f57','CN':'#c47b24'}
def path(d,fill,stroke=C['ink'],w=2,more=''):return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" {more}/>'
def ellipse(x,y,rx,ry,fill,stroke=C['ink'],w=2,more=''):return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{w}" {more}/>'
def line(a,b,col='#647481',w=2,dash=''):return f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{col}" stroke-width="{w}" {"stroke-dasharray="+chr(34)+dash+chr(34) if dash else ""}/>'
def txt(x,y,s,size=26,col=C['ink'],weight='400'):return f'<text x="{x}" y="{y}" font-size="{size}" fill="{col}" font-weight="{weight}">{html.escape(s)}</text>'
def lines(x,y,ss,size=25,col=C['ink'],dy=39):return ''.join(txt(x,y+i*dy,s,size,col) for i,s in enumerate(ss))
def box(x,y,w,h,title):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="#fff" stroke="#d2dae0" stroke-width="2"/>'+txt(x+20,y+41,title,29,weight='650')
def tube(a,b,r0,r1,col):
 dx,dy=b[0]-a[0],b[1]-a[1];le=math.hypot(dx,dy);nx,ny=-dy/le,dx/le
 pts=[(a[0]+nx*r0,a[1]+ny*r0),(b[0]+nx*r1,b[1]+ny*r1),(b[0]-nx*r1,b[1]-ny*r1),(a[0]-nx*r0,a[1]-ny*r0)]
 d=f'M {pts[0][0]} {pts[0][1]} Q {(pts[0][0]+pts[1][0])/2+nx*2} {(pts[0][1]+pts[1][1])/2+ny*2} {pts[1][0]} {pts[1][1]} A {r1} {r1} 0 0 1 {pts[2][0]} {pts[2][1]} Q {(pts[2][0]+pts[3][0])/2-nx*2} {(pts[2][1]+pts[3][1])/2-ny*2} {pts[3][0]} {pts[3][1]} A {r0} {r0} 0 0 1 {pts[0][0]} {pts[0][1]} Z'
 return path(d,col)+line(a,b,'#6f7a86',.9,'4 4')+ellipse(b[0],b[1],r1,r1*.40,'none','#71818b',1,more=f'transform="rotate({math.degrees(math.atan2(dy,dx))+90} {b[0]} {b[1]})"')
def arm(j,col):return tube(j[0],j[1],13,11,col)+tube(j[1],j[2],11,7,col)
def grip(x,y,sc=1,face=-1,ang=0,jade=False,openhand=False,bundle=False):
 # Full palm contour, four individually curled finger volumes, opposed thumb.
 s=f'<g transform="translate({x} {y}) rotate({ang}) scale({sc*face} {sc})">'
 if openhand:
  s+=path('M -25 -9 Q -10 -20 12 -15 Q 31 -12 39 -4 Q 42 0 37 4 L 16 1 Q 34 5 37 11 Q 37 16 31 15 L 10 8 Q 29 15 31 20 Q 30 25 23 21 L 4 13 Q 20 23 18 27 Q 14 29 8 23 L -12 12 L -26 9 Z',C['near'])
 else:
  s+=path('M -26 -12 Q -10 -18 8 -14 Q 22 -12 23 1 Q 22 14 11 17 L -7 15 Q -22 10 -26 9 Z',C['near'])
  for fx,fy in [(12,-5),(11,2),(7,9),(1,14)]:s+=path(f'M {fx-5} {fy-4} Q {fx+8} {fy-8} {fx+10} {fy} Q {fx+8} {fy+7} {fx-3} {fy+4} Q {fx-10} {fy+1} {fx-5} {fy-4} Z',C['near'],w=1.2)
  s+=path('M -15 -9 Q -4 -23 9 -17 Q 19 -12 17 -5 Q 14 1 5 3 L -3 5 Q -13 11 -18 4 Q -22 -2 -15 -9 Z' if bundle else 'M -14 -11 Q -1 -24 14 -15 Q 22 -10 14 -6 L 3 -5 Q -9 6 -15 0 Z','#f9d9c3',w=1.5)
  s+=ellipse(12,-11,4,3,'#ffe9d9','#9f816d',.8)
 if jade:s+=ellipse(-25,0,4.5,12.5,'#6fa787','#35624e',1.7)
 return s+'</g>'
def head(k,x=0,y=0,face=-1,laugh=False):
 s=f'<g transform="translate({x} {y}) scale({face} 1)">'
 if k=='G':
  s+=ellipse(-33,64,20,21,'#c8c6c4')
  for bx,by in [(-43,43),(-47,37),(-47,30)]:s+=ellipse(bx,by,3,3,'#bf4d43',w=.7)
 else:
  s+=path('M -26 67 C -61 72 -56 115 -38 123 Q -44 99 -27 88 Z','#66574d')+path('M -16 76 C -40 91 -29 119 -15 125 Q -22 102 -4 91 Z','#51483f')
  s+=ellipse(-29,81,7,7,'#ce5f51',w=1);s+=ellipse(-8,87,6,6,'#ce5f51',w=1)
 s+=path('M -29 27 C -34 7 -15 -6 11 0 C 36 2 42 18 36 37 L 42 52 L 51 57 Q 55 62 46 66 L 42 82 Q 31 101 8 101 Q -12 98 -20 83 L -27 64 Z','#f7d3ba')
 s+=ellipse(-19,63,10,13,'#efbfa6',w=1.3)
 hair='#cbc9c8' if k=='G' else '#5c5149'
 s+=path('M -29 61 C -48 35 -36 4 -9 -1 C 16 -8 43 3 42 29 Q 28 19 15 20 Q 6 46 -9 53 L -20 64 Z',hair)
 s+=path('M -30 23 Q -11 3 27 9 M -34 35 Q -4 20 19 13 M -25 47 Q 0 36 18 20','none','#8b8c8c' if k=='G' else '#827265',.9)
 if laugh:
  s+=path('M 21 52 Q 31 47 37 52','none',w=1.8)+path('M 24 76 Q 42 72 43 77 Q 37 94 25 87 Z','#a75b58',w=1.4)+path('M 25 77 L 41 77 L 38 80 L 27 81 Z','#fff6eb',w=.6)
 else:
  s+=ellipse(30,53,4.6,7.5,'#fff')+ellipse(31,54,2.7,5,'#48413c',w=.5)+path('M 29 80 Q 36 82 40 78','none',w=1.2)
 if k=='G':s+=ellipse(28,54,12,15,'none',C['ink'],1.8)+ellipse(45,55,5,12,'none',C['ink'],1.3)+line((-12,52),(17,52),C['ink'],2)
 else:s+=path('M 6 6 Q 4 24 -1 38 M 16 4 Q 15 21 10 34 M 25 6 Q 26 20 22 30','none','#3e3936',2)
 return s+'</g>'
def torso(k,bent=False):
 if bent:
  s=path('M -71 187 Q -32 180 -12 201 Q 2 246 44 282 L 76 331 Q 35 350 -12 335 Q -52 303 -84 250 L -91 211 Z',C['shirt'])
  s+=path('M -83 184 L -52 171 L -37 196 L -58 212 Z','#d9e6ef')
  s+=path('M -63 211 Q -27 270 56 335','none','#7391a9',1.2)
 else:
  if k=='G':s=path('M -24 118 Q -44 127 -49 163 L -38 237 L -43 280 Q 10 298 50 281 L 36 192 L 40 148 Q 37 126 18 120 Z',C['shirt'])
  else:s=path('M -22 114 Q -42 125 -39 159 L -28 205 Q 9 217 37 202 L 34 148 Q 28 121 17 116 Z',C['dress'])+path('M -28 199 Q 10 216 37 201 L 69 330 Q 10 355 -62 332 Z',C['dress'])
  s+=path('M -18 119 L -2 137 L 12 120 M -2 137 L 2 275' if k=='G' else 'M -18 116 Q -7 143 1 127 Q 18 145 22 118','none','#566c7d' if k=='G' else '#fff8e6',4)
 # Small placement marks imply actual cloth volume, never baked scene lighting.
 if not bent:
  for px,py in ([(-25,165),(16,173),(-15,222),(25,252)] if k=='G' else [(-17,156),(17,178),(-12,245),(32,280),(-30,313)]):
   s+=ellipse(px,py,3.5,3.5,'#f6f4e8','none',0)
   if k=='G':
    for dx,dy in [(-5,0),(5,0),(0,-5),(0,5)]:s+=ellipse(px+dx,py+dy,2.7,2.7,'#f6f4e8','none',0)
 return s
FIGS={
 'A_G':dict(k='G',o=[1030,304],s=1.45,face=-1,near='L',L=[(18,130),(-2,190),(-70,140)],R=[(-20,125),(-60,198),(-90,210)],palms={'L':(-92,140),'R':(-112,210)}),
 'A_X':dict(k='X',o=[600,386],s=1.305,face=1,near='R',R=[(16,120),(60,165),(100,155)],L=[(5,122),(45,200),(110,185)],palms={'R':(120,155),'L':(134,185)}),
 'B_G':dict(k='G',o=[1030,304],s=1.45,face=-1,near='L',L=[(18,130),(5,205),(-65,170)],R=[(-20,125),(-60,198),(-110,225)],palms={'L':(-87,170),'R':(-132,225)}),
 'B_X':dict(k='X',o=[600,386],s=1.305,face=-1,near='L',R=[(-16,122),(-64,178),(-122,152)],L=[(14,125),(18,195),(-59,202)],palms={'R':(-144,152),'L':(-81,202)}),
 'C_G':dict(bundle_hands=['R'],k='G',o=[1000,290],s=1.6,face=-1,near='L',bent=True,L=[(-20,195),(45,250),(-10,285)],R=[(-70,195),(-90,275),(-170,282)],palms={'L':(-32,285),'R':(-192,282)})}
def world(f,p):return (f['o'][0]+f['s']*p[0],f['o'][1]+f['s']*p[1])
def limb_label(f,hand):
 sh,el,wr=[world(f,p) for p in f[hand]];p=world(f,f['palms'][hand]);return txt(sh[0]+12,sh[1]-7,hand+'肩',17)+txt(el[0]+12,el[1]+5,hand+'肘',17)+txt(p[0]-8,p[1]+50,('小满' if f['k']=='X' else '奶奶')+hand,22,C['ink'],'650')
def figure(f,labels=True):
 k=f['k'];near=f['near'];far='R' if near=='L' else 'L';b=f.get('bent',False);s=f'<g transform="translate({f["o"][0]} {f["o"][1]}) scale({f["s"]})">'
 # Full lower-body volumes are retained even when the eventual camera crops them.
 if b:hips=[(14,320),(53,320)];knees=[(10,405),(72,407)];ankles=[(5,490),(85,490)]
 else:hips=[(-16,260 if k=='G' else 235),(18,262 if k=='G' else 238)];knees=[(-14,365 if k=='G' else 345),(24,362 if k=='G' else 347)];ankles=[(-18,460 if k=='G' else 450),(29,458 if k=='G' else 450)]
 for i in range(2):
  col='#929eaf' if i==0 else '#555f76'
  if k=='G':s+=path(f'M {hips[i][0]-20} {hips[i][1]} Q {knees[i][0]-24} {knees[i][1]} {ankles[i][0]-23} {ankles[i][1]} L {ankles[i][0]+26} {ankles[i][1]+3} Q {knees[i][0]+21} {knees[i][1]} {hips[i][0]+19} {hips[i][1]} Z',col)
  else:s+=tube(hips[i],knees[i],18,13,'#d5b5a0' if i==0 else C['near'])+tube(knees[i],ankles[i],13,8,'#d5b5a0' if i==0 else C['near'])
  ax,ay=ankles[i];toe=-1 if k=='X' and f['face']==1 else 1
  s+=f'<g transform="translate({ax} {ay}) scale({toe} 1)">'+path('M -12 -1 Q -27 5 -43 10 Q -55 14 -49 20 L 23 20 Q 29 9 12 1 Z','#333c47' if k=='G' else '#c56653')+line((-48,17),(22,17),'#eee7dc',3)+'</g>'
 s+=arm(f[far],C['far']);s+=torso(k,b)
 if b:s+=path('M -67 165 L -36 153 L -37 182 L -60 200 Z',C['near'])+head(k,-55,75,-1,True)
 else:s+=path('M -9 94 L -15 120 L 8 133 L 17 116 L 12 95 Z',C['near'])+head(k,0,0,f['face'])
 s+=arm(f[near],C['near'])
 for h in ['R','L']:
  sh=f[h][0];s+=ellipse(sh[0],sh[1],19,16,C['shirt'] if k=='G' else C['dress'],w=1.8)
 s+='</g>';return s+(limb_label(f,'R')+limb_label(f,'L') if labels else '')
def figure_hands(f):
 result=''
 for hand in ['R','L']:
  p=world(f,f['palms'][hand]);jade=f['k']=='G' and hand=='L';direc=1 if f['face']==1 else -1
  # Grip drawing points its wrist opposite the chosen palm direction.
  result+=grip(*p,sc=f['s']*.95,face=direc,jade=jade,openhand=hand in f.get('open_hands',[]) or (f.get('bent',False) and hand=='L'),bundle=hand in f.get('bundle_hands',[]))
 return result
def rod(a,b,key,labelat=None,label=None):
 col=C[key];s=line(a,b,'#f8fafb',9)+line(a,b,col,4)
 if labelat:s+=txt(*labelat,label or key,23,col,'700')
 return s
def puppet(shell,headpos):
 x,y=shell;hx,hy=headpos
 return ellipse(x,y-18,63,43,'#c0d0bf')+path(f'M {x+25} {y-35} Q {(x+hx)/2} {(y+hy)/2-20} {hx} {hy}','none','#728b72',19)+ellipse(hx,hy,23,15,'#c6d4bf')+ellipse(hx+10,hy-3,2,2,'#485c49',w=0)+txt(x-53,y+57,'龟（机构示意）',20)
def header(n,title,sub):return f'<rect width="2400" height="1500" fill="#eef2f4"/>'+txt(45,59,'S20 · '+n+'  '+title,38,weight='750')+txt(45,104,sub,24)+box(35,135,1225,1040,'完整体量／手别施工参考 · 不是曝光成品')+box(1290,135,1075,1040,'真实握持、层次与不变量')
def footer(extra):return box(35,1200,2330,265,'共用施工尺与制作边界')+lines(60,1295,['G：身高4.8H；小满：身高4.7H，H_X=0.90H_G，约0.88成人高度。目标来自实际母版比例阅读，待冻结。','骨长施工目标：奶奶上臂1.00H／前臂0.90H／手0.50H；小满0.90H／0.80H／0.45H。不是二维图反推的实测三维骨长。','近臂实肤色、躯干衣块、远臂灰色；截面椭圆表示短缩，灰虚线表示遮挡。L/R始终按角色自身。',extra],23,dy=37)
def finish(name,s):
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="2400" height="1500" viewBox="0 0 2400 1500"><style>text{{font-family:RefSC,"Noto Sans SC",sans-serif}} @font-face{{font-family:RefSC;src:url("/assets/fonts/NotoSansSC-VF.ttf")}}</style><desc>Human-authored static construction reference, zero image-model calls, not a production character drawing.</desc>'+s+'</svg>';(OUT/(name+'.svg')).write_text(svg)
def contact_band(x,y,angle,key):
 # A section mark: central hidden shaft, thumb-side and finger-side contacts.
 col=C[key]
 return f'<g transform="translate({x} {y}) rotate({angle})">'+line((-8,0),(8,0),col,3.2,'3 2')+line((-5,-3.4),(5,-3.4),col,1.8)+line((-5,3.4),(5,3.4),col,1.8)+'</g>'
def shaft_through(a,p,after=11):
 dx,dy=p[0]-a[0],p[1]-a[1];n=math.hypot(dx,dy)
 return (p[0]+after*dx/n,p[1]+after*dy/n)
def on_axis(a,b,x):return (x,a[1]+(x-a[0])*(b[1]-a[1])/(b[0]-a[0]))
def angle_of(a,b):return math.degrees(math.atan2(b[1]-a[1],b[0]-a[0]))
TRANSFERS={
 'T':{'title':'龟交接：供给手先保留，接握确认后再松开','frames':[8,20,32],'rods':['TH','TS'],'states':[{'TH':['G.R'],'TS':['G.R']},{'TH':['G.R','X.R'],'TS':['G.R','X.L']},{'TH':['X.R'],'TS':['X.L']}],'captions':['原握：G.R闭合双龟签；小满双手未碰','接握：小满R头/L壳已闭；G.R仍闭合','放握：X.R/X.L维持；G.R张开撤离']},
 'CB':{'title':'F036–047接回鹤身签：G.L不先松C_B','frames':[36,42,47],'rods':['CN','CB'],'states':[{'CN':['G.L'],'CB':['G.L']},{'CN':['G.L'],'CB':['G.L','G.R']},{'CN':['G.L'],'CB':['G.R']}],'captions':['原握：G.L闭合C_N+C_B；G.R尚未接','接握：G.R已夹C_B；G.L仍支持两签','放握：G.R维持C_B；G.L仅撤C_B接触']},
 'CN':{'title':'F132–143并入鹤颈签：G.R先握牢，G.L后离开','frames':[132,138,143],'rods':['CN','CB'],'states':[{'CN':['G.L'],'CB':['G.R']},{'CN':['G.L','G.R'],'CB':['G.R']},{'CN':['G.R'],'CB':['G.R']}],'captions':['原握：G.L持C_N；G.R持C_B','接握：G.R已夹两签；G.L仍闭合C_N','放握：G.R保持两带；G.L张开撤离']}}
def transfer_strip(kind):
 t=TRANSFERS[kind];s=box(35,1200,2330,265,t['title']+' · 手端接触时序小示意')
 for j,frame in enumerate(t['frames']):
  x=65+j*770;y=1287;rs=t['rods'];state=t['states'][j]
  s+=txt(x+10,1275,['原握','接握','放握'][j]+f' F{frame:03}',23,weight='700')
  # Each column retains the same top/bottom rod order and anatomical hand IDs.
  for k,key in enumerate(rs):s+=line((x+115,y+k*44),(x+690,y+k*44),C[key],3)+txt(x+60,y+k*44+7,key,19,C[key],'650')
  if kind=='T':
   if j<2:s+=grip(x+640,y+22,2.05,face=-1,bundle=True)
   else:s+=grip(x+640,y+102,1.6,face=-1,openhand=True)
   for k,h in enumerate(['X.R','X.L']):
    yy=y+k*44 if j else y+104;xx=x+260+k*140
    s+=grip(xx,yy,1.55,face=1,openhand=j==0)+txt(xx-35,yy+42,h,18)
  elif kind=='CB':
   s+=grip(x+260,y+(22 if j<2 else 0),2.05 if j<2 else 1.55,face=1,jade=True,bundle=j<2)
   s+=grip(x+560,y+(104 if j==0 else 44),1.55,face=-1,openhand=j==0)
  else:
   s+=grip(x+260,y+(104 if j==2 else 0),1.55,face=1,jade=True,openhand=j==2)
   s+=grip(x+560,y+(44 if j==0 else 22),1.55 if j==0 else 2.05,face=-1,bundle=j>0)
  if kind=='T':
   if j<2:
    for key,yy in zip(rs,[y,y+44]):s+=contact_band(x+628,yy,0,key)
   if j>0:
    s+=contact_band(x+270,y,0,'TH')+contact_band(x+410,y+44,0,'TS')
  elif kind=='CB':
   s+=contact_band(x+270,y,0,'CN')
   if j<2:s+=contact_band(x+270,y+44,0,'CB')
   if j>0:s+=contact_band(x+548,y+44,0,'CB')
  else:
   if j<2:s+=contact_band(x+270,y,0,'CN')
   s+=contact_band(x+548,y+44,0,'CB')
   if j>0:s+=contact_band(x+548,y,0,'CN')
  s+=txt(x+6,1452,t['captions'][j],20)
  if kind!='T':
   s+=txt(x+(100 if kind=='CN' and j==2 else 205),1405,'G.L（带镯）',18)
   s+=txt(x+(610 if kind=='CB' and j==0 else 520),1405,'G.R（裸腕）',18)
  if j<2:s+=txt(x+724,1357,'→',35,'#6f7d85','700')
 return s
def build_reference_plates():
 # K01: Manual handoff, with a separately supported crane bundle.
 s=header('K01','F020：交接承重重叠','奶奶L暂并鹤双签；R递龟双签。小满R先握头签、L握壳签，双方实握期间奶奶不先放。')
 for f in [FIGS['A_G'],FIGS['A_X']]:s+=figure(f)
 g=FIGS['A_G'];x=FIGS['A_X'];ag=world(g,g['palms']['R']);xr=world(x,x['palms']['R']);xl=world(x,x['palms']['L']);ag2=(ag[0],ag[1]+16)
 h=(xr[0]+2.5*(xr[0]-ag[0]),xr[1]+2.5*(xr[1]-ag[1]));b=(xl[0]+2.5*(xl[0]-ag2[0]),xl[1]+2.5*(xl[1]-ag2[1]));s+=puppet(b,h)
 s+=rod(h,(ag[0]+34,ag[1]+6),'TH',(340,500),'T_H 头签')+rod(b,(ag2[0]+34,ag2[1]-4),'TS',(350,775),'T_S 壳签')
 lc=world(g,g['palms']['L']);s+=rod((680,290),(lc[0]+22,lc[1]+7),'CB',(702,350),'C_B 鹤身')+rod((760,205),(lc[0]+22,lc[1]-6),'CN',(785,255),'C_N 鹤颈')
 for f in [g,x]:s+=figure_hands(f)
 s+=line((435,1035),(1140,1035),'#9caab4',2)+txt(80,1100,'同尺构造；正式景位沿CAM20。小满转胸向奶奶收签，随后整胸／脚转回幕。',22)
 s+=lines(1320,225,['交接不是递出偶面或只把手搭在签上：','①奶奶R仍握住两根的下游段；','②小满R拇指对食／中指夹住T_H；','③小满L拇指对屈曲四指握T_S；','④两处稳定后，奶奶R拇指／四指才松开。'],25,dy=40)
 # Distinct straight shafts and three staggered physical grip locations.
 s+=rod((1360,500),(2260,800),'TH',(1340,465),'T_H')+rod((1360,935),(2260,710),'TS',(1340,985),'T_S')
 s+=grip(1640,593,2.2,face=1,ang=18)+grip(1760,835,2.2,face=1,ang=-14)+grip(2160,752,3.4,face=-1)
 s+=txt(1510,555,'小满R：头签，先闭合',24,C['TH'],'700')+txt(1550,900,'小满L：壳签，独立闭合',24,C['TS'],'700')+txt(2010,875,'奶奶R：支持两签后端',24)
 s+=lines(1320,1070,['握点错开至少一掌位；两杆不断轴、不在掌中合成一杆。','奶奶L同时稳握C_B+C_N，鹤始终有人支持。'],23,dy=37)
 s+=transfer_strip('T');finish('S20_K01_F020_handoff',s)
 # K02: Fixed rod ownership through a physical X; no endpoint remapping.
 s=header('K02','F084：双臂分开，双签成X','2.4–4.6秒绞签窗保留。右手T_H／左手T_S始终不换绑，X处只有前后层次，不画软绳结。')
 g=FIGS['B_G'];x=FIGS['B_X']
 for f in [g,x]:s+=figure(f)
 xr=world(x,x['palms']['R']);xl=world(x,x['palms']['L']);X=(330,560);h=(X[0]-(xr[0]-X[0])*.5,X[1]-(xr[1]-X[1])*.5);b=(X[0]-(xl[0]-X[0])*.6,X[1]-(xl[1]-X[1])*.6)
 s+=puppet(b,h)+rod(h,(xr[0]+25,xr[1]+7),'TH',(180,570),'T_H')+rod(b,(xl[0]+25,xl[1]+13),'TS',(160,500),'T_S 近')
 s+=ellipse(*X,25,25,'none','#647481',1.7)+txt(265,616,'X：近壳签遮远头签',20)
 gl=world(g,g['palms']['L']);gr=world(g,g['palms']['R']);s+=rod((735,380),(gr[0]+24,gr[1]+15),'CB',(715,440),'C_B → G.R')+rod((710,280),(gl[0]+24,gl[1]+10),'CN',(700,265),'C_N → G.L')
 for f in [g,x]:s+=figure_hands(f)
 for a,z,key,xx in [(h,(xr[0]+25,xr[1]+7),'TH',xr[0]-15),(b,(xl[0]+25,xl[1]+13),'TS',xl[0]-14)]:
  cp=on_axis(a,z,xx);s+=contact_band(*cp,angle_of(a,z),key)
 s+=txt(80,1100,'先肩／肘带动，再腕内收；前臂不相互绕过，屈肘与掌厚保持。',23)
 s+=lines(1320,220,['右手＝T_H→龟头；左手＝T_S→龟壳。','奶奶右手＝C_B→鹤身；左手＝C_N→neck3。','不采用代码T.cross切换手端归属的办法。'],25,dy=42)
 s+='<!-- SAME_VIEW_K02 -->'
 s+=lines(1320,1100,['详图仅从左主图原像素裁切放大：R在上、L在下。','窄色条为掌内杆段剖示；两侧短括分别指拇指／对侧指腹。'],22,dy=35)
 s+=transfer_strip('CB');finish('S20_K02_F084_crossed_rods',s)
 # K03: Whole-body laugh, right hand actually clamps two separate crane rods.
 s=header('K03','F156：腰髋带笑，R并鹤双签，L扶腹','F144／6.0秒保留原CAMG切奶奶中近景；这里补完整下肢施工，不据全身示意改机位。')
 g=FIGS['C_G'];s+=figure(g);gr=world(g,g['palms']['R']);c_axes=[((150,420),(678,726),'CN',(115,395)),((150,540),(682,742),'CB',(115,510))]
 for a,cp,key,lab in c_axes:s+=rod(a,shaft_through(a,cp,22),key,lab,'C_N' if key=='CN' else 'C_B')
 s+=figure_hands(g)
 for a,cp,key,lab in c_axes:s+=contact_band(*cp,angle_of(a,cp),key)
 s+=f'<rect x="70" y="335" width="1130" height="570" rx="12" fill="none" stroke="#a7b2ba" stroke-width="2" stroke-dasharray="12 8"/>'+txt(80,320,'CAMG中近景意向框；保留下方全身用于骨长／支撑审查',21)
 s+=txt(140,1115,'两脚仍承重，膝微屈；笑的变化沿腰髋→胸肩→颈头传递。',23)
 s+=lines(1320,220,['F132–143先完成鹤签自交接：','G.R保持C_B；G.L把C_N送入R虎口并夹牢。','确认R拇指＋屈指同时压住两杆后，L才移到腹前。','F144切景不会把“两手握”凭空变成“单手并”。'],25,dy=42)
 s+='<!-- SAME_VIEW_K03 -->'
 s+=lines(1320,1080,['同一主图视角：橙C_N在上、绿C_B在下，不重画／镜像。','两杆各有独立拇指—指腹接触带，不能用一个色圈代表两杆。'],22,dy=36)
 s+=transfer_strip('CN');finish('S20_K03_F156_laugh_bundle',s)
 # Explicit model ruler/projection lengths; these are design targets, not measured skeletons.
 report={'reference_type':'Static manually specified SVG volume construction; not generated production art.','H_G':100,'H_X_relative_to_G':.90,'adult_height_H':4.8,'child_height_H':4.7,'bone_targets_in_own_H':{'G':{'upperarm':1.00,'forearm':.90,'hand':.50},'X':{'upperarm':.90,'forearm':.80,'hand':.45}},'figures':{}}
 for name,f in FIGS.items():
  r={'kind':f['k'],'near_arm':f['near'],'face_screen_direction':f['face'],'placement':f['o'],'uniform_reference_scale':f['s'],'joints':{},'note':'Projected arm centre distances <= construction lengths; missing depth is foreshortening, not a claim of measured3D bone length.'}
  for hand in ['L','R']:
   sh,el,wr=f[hand];up=math.dist(sh,el);lo=math.dist(el,wr);tar=report['bone_targets_in_own_H'][f['k']];assert up<=tar['upperarm']*100+1e-6,(name,hand,up);assert lo<=tar['forearm']*100+1e-6,(name,hand,lo)
   r['joints'][hand]={'shoulder':sh,'elbow':el,'wrist':wr,'palm':f['palms'][hand],'upperarm_projection_H':up/100,'forearm_projection_H':lo/100}
  report['figures'][name]=r
 (D/'provenance/construction_ruler_and_joints.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('3 static SVG volume/contact plates built; projected upper/forearm lengths within construction ruler.')

if __name__=='__main__':build_reference_plates()
