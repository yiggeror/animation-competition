from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import math,json
P=Path(__file__).resolve().parent;W,H=1920,1240
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',25);sm=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',20)
I=Image.new('RGB',(W,H),'#f5f1e9');d=ImageDraw.Draw(I);ink='#28343b';far='#68767b';near='#dfbb94';skin='#f0d4b4'
def cap(a,b,w,c):
 d.line((*a,*b),fill=ink,width=w+4)
 for p in [a,b]:d.ellipse((p[0]-w/2-2,p[1]-w/2-2,p[0]+w/2+2,p[1]+w/2+2),fill=ink)
 d.line((*a,*b),fill=c,width=w)
 for p in [a,b]:d.ellipse((p[0]-w/2,p[1]-w/2,p[0]+w/2,p[1]+w/2),fill=c)
def poly(points,c):d.polygon(points,fill=c);d.line(points+[points[0]],fill=ink,width=3,joint='curve')
def dash(a,b):
 for i in range(0,12,2):d.line((a[0]+(b[0]-a[0])*i/12,a[1]+(b[1]-a[1])*i/12,a[0]+(b[0]-a[0])*(i+1)/12,a[1]+(b[1]-a[1])*(i+1)/12),fill='#314653',width=4)
# table/lamp retain original lamp world scale; table front is only a proposed camera framing.
d.polygon([(910,970),(1720,910),(1920,1055),(850,1055)],fill='#d6c1a0',outline='#72614d')
sc=14/18.5;bx,by=1415,965.6
def q(x,y):return (bx-x*sc,by+y*sc)
def lp(coords,c,w=3):d.line([q(x,y) for x,y in coords],fill=c,width=w,joint='curve')
# body of actual lamp: side tubes, fuel tank, burner, glass and connected lever
for s in [-1,1]:lp([(s*157,-120),(s*157,-560),(s*120,-600),(s*100,-600)],'#896b55',15)
d.ellipse((bx-200*sc,by-140*sc,bx+200*sc,by+4*sc),fill='#a78f6f',outline=ink,width=3)
poly([q(-70,-140),q(-58,-200),q(58,-200),q(70,-140)],'#bda16d');d.rectangle((bx-22*sc,by-226*sc,bx+22*sc,by-200*sc),fill='#c2b7a1',outline=ink,width=2)
d.rectangle((bx-21*sc,by-226*sc,bx+21*sc,by-220*sc),fill='#514b40')
# low glass envelope using original code dimensions, not narrow substitute
pts=[(-96,-206),(-150,-300),(-156,-390),(-125,-470),(-70,-540),(70,-540),(125,-470),(156,-390),(150,-300),(96,-206)]
lp(pts+[pts[0]],'#809496',4);lp([(-128,-204),(128,-204)],'#6f5b4b',9);lp([(-110,-578),(-90,-620),(0,-650),(90,-620),(110,-578)],'#705947',12)
pivot=q(150,-230);tip=q(150+95*math.cos(.55),-230+95*math.sin(.55));cap(pivot,tip,7,'#655b4c');d.ellipse((tip[0]-7,tip[1]-7,tip[0]+7,tip[1]+7),fill=ink)
# Arms are hand-drafted projected masses, not a solved/calibrated camera claim.
R=[(650,650),(780,944),(970,845)];L=[(1000,650),(1060,940),(1170,830)]
cap(L[0],L[1],70,far);cap(L[1],L[2],56,far)
poly([(650,620),(602,690),(578,850),(560,1080),(855,1080),(876,882),(950,748),(1018,640),(846,590),(744,590)],'#a8b2b8')
# neck/head in a more frontal 3/4 pose, unlike withdrawn user's atlas.
poly([(745,555),(840,555),(860,626),(735,626)],'#cfbda8')
d.ellipse((650,285,926,585),fill='#d8d2c7',outline=ink,width=4);d.ellipse((620,348,666,440),fill='#aaa9a4',outline=ink,width=3)
d.arc((692,401,758,435),180,360,fill=ink,width=3);d.arc((814,405,880,440),180,360,fill=ink,width=3);d.line((797,414,815,458,795,463),fill=ink,width=3);d.arc((773,477,837,504),0,180,fill=ink,width=3)
d.ellipse((655,270,729,340),fill='#8e9393',outline=ink,width=3)
# concealed far root is short and explicitly indicated, never a floating wrist
cap(R[0],R[1],76,near);cap(R[1],R[2],60,near)
for chain,w in [(R,84),(L,76)]:
 a,b=chain[:2];ll=math.dist(a,b);end=(a[0]+(b[0]-a[0])*77/ll,a[1]+(b[1]-a[1])*77/ll);cap(a,end,w,'#8b9eaa')
dash(L[0],(1015,670))
# Left wrist is on the box's RIGHT/LOWER side, so its bangle remains distinct.
poly([(1182,820),(1165,801),(1147,780),(1125,774),(1109,782),(1108,798),(1124,813),(1149,837),(1164,847)],skin)
cap((1150,835),(1190,824),12,'#41836c')
poly([(1089,739),(1161,739),(1161,761),(1089,761)],'#bda16d');d.rectangle((1091,750,1159,759),fill='#9a6951')
# Four curved pads support the bottom/front rim; not straight disconnected bars.
for x in [1102,1118,1134,1150]:
 d.ellipse((x-7,762,x+6,782),fill=skin,outline=ink,width=2)
 d.arc((x-8,752,x+8,774),30,180,fill=ink,width=3)
 d.arc((x-5,764,x+6,777),10,150,fill='#8d7462',width=1)
poly([(1165,815),(1157,775),(1161,753),(1170,757),(1170,788),(1172,820)],skin)
# Near right palm and folded middle/ring/little fingers.
poly([(961,818),(983,814),(1005,801),(1030,798),(1046,813),(1048,837),(1028,859),(992,870),(968,868)],skin)
for k in range(3):
 d.arc((1011-k*10,829+k*8,1043-k*10,851+k*8),25,270,fill=ink,width=3)
# match shaft passes between actual thumb/index pads, not through open palm.
pinch=(1045,820);head=(1076,764);d.line((1035,833,*head),fill='#7e633e',width=6);d.ellipse((head[0]-6,head[1]-6,head[0]+6,head[1]+6),fill='#754a40')
# index curves over shaft, thumb curves under it: two connected contact pads
poly([(1018,800),(1035,795),(1063,802),(1066,812),(1053,823),(1044,822),(1041,815),(1025,814)],skin)
poly([(1018,847),(1031,836),(1041,821),(1049,820),(1054,827),(1044,846),(1031,859)],skin)
# source contacts, no fake acceptance
for side,chain in [('近右',R),('远左',L)]:
 for n,p in zip(['肩','肘','腕'],chain):
  d.ellipse((p[0]-5,p[1]-5,p[0]+5,p[1]+5),fill='#19232d');d.text((p[0]-60,p[1]+12),side+n,font=sm,fill='#24343e')
d.text((35,22),'S08 F000 单态结构门 v5：更正面双肩，双前臂分开，盒底托指／拇食指夹柴',font=font,fill=ink)
d.text((35,65),'仅结构提案：不是成图，不是相机精确重建；先由独审与Opus判断实际姿态，再推其余四态。',font=sm,fill='#56616b')
d.text((35,1105),'深块＝远左臂，灰块＝躯干，浅块＝近右臂；隐藏肩根虚线；两腕与躯干分离。',font=font,fill=ink)
d.text((35,1148),'右手柴头在盒左下划面外预备；远手四指托盒底、拇指扣侧。灯按原14/18.5比例，杆接侧管。',font=sm,fill=ink)
d.text((35,1184),'尚待审：远前臂短缩是否可信、腕角/掌物接触、与后续提罩/点芯五态可达性。禁止按数值自动通过。',font=sm,fill=ink)
I.save(P/'reference/F000_frontal_contact_v5_DRAFT.png');I.crop((900,700,1240,965)).resize((1224,954)).save(P/'reference/F000_frontal_contacts_v5_DRAFT.png')
json.dump({'status':'DRAFT_NOT_APPROVED','source':'new schematic; rejected user image not used','R':R,'L':L,'pinch':pinch,'match_head':head,'box':[1125,750],'lamp_world_scale':sc,'lamp_base':[bx,by],'lever_pivot':pivot,'lever_tip':tip,'scope':'F000 anatomy/contact visual gate only; not measured bones or exact camera'},open(P/'geometry/F000_frontal_v5_DRAFT.json','w'),indent=2)
