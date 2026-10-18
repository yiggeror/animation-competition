from pathlib import Path
from PIL import Image,ImageDraw
import math,json,copy
ROOT=Path('/workspace/scratch/f060b5601755');OUT=Path(__file__).resolve().parent
old=ROOT/'astra_opening_drawn_review_20261018_0930/S08_retraction_reference_1604/build_reference.py'
ns={'__file__':str(OUT/'build_v2.py')};exec(compile(old.read_text().split('for fr in [66,78,79,80,82,96]:')[0],'approved_helpers','exec'),ns)
S=ns['S'];base=copy.deepcopy(S)
# Only the necessary arm projections change. Body/neck/head and near elbows remain approved.
S[82]['R'][2]=(990,1005)
S[96]['R'][2]=(915,981);S[96]['L'][1]=(900,870);S[96]['L'][2]=(1040,920)
S[114]=copy.deepcopy(S[96]);S[114]['R'][2]=(875,981);S[114]['L'][1]=(900,880);S[114]['L'][2]=(1010,981)
S[143]=copy.deepcopy(S[114])
INK=ns['INK'];BG=ns['BG'];SKIN=ns['SKIN'];FAR=ns['FAR'];sm=ns['sm'];font=ns['font'];tiny=ns['tiny'];bez=ns['bez'];tr=ns['tr'];poly=ns['poly']
def rounded(pts):
 out=[]
 for i in range(len(pts)):
  a=pts[(i-1)%len(pts)];b=pts[i];c=pts[(i+1)%len(pts)];e=pts[(i+2)%len(pts)]
  for k in range(6):
   t=k/6;out.append(tuple(.5*((2*b[j])+(-a[j]+c[j])*t+(2*a[j]-5*b[j]+4*c[j]-e[j])*t*t+(-a[j]+3*b[j]-3*c[j]+e[j])*t*t*t) for j in [0,1]))
 return out
# Fingers rest in a loose cascading arc; no raised thumb or closed fist.
def loose_hand(d,w,far=False,settled=False,angle=0):
 sx=.75 if far and settled else 1.;sy=.70 if settled else .88
 if far and settled:angle=.22
 # Wrist envelope remains full width; palm rotates in depth only beyond the carpus.
 def T(q):
  blend=max(0,min(1,(q[0]+8)/45));ys=q[1]*(1-(1-sy)*blend)
  return tr((q[0]*sx,ys),w,angle)
 pts=[(-18,-26),(12,-25),(36,-20),(66,-13),(88,-7),(96,0),(92,8),(76,9),(88,15),(91,23),(84,28),(69,24),(77,33),(74,41),(65,41),(53,33),(57,43),(50,48),(42,43),(31,31),(35,39),(29,46),(20,43),(10,30),(-18,26)]
 rp=[T(q) for q in rounded(pts)]
 d.polygon(rp,fill=FAR if far else SKIN)
 # Open proximal join: no transverse cut at the wrist.
 d.line(rp[:-6],fill=INK,width=3,joint='curve')
 for ps in [bez((42,-10),(65,-10),(84,-4),(81,6),16),bez((41,4),(62,7),(79,17),(71,22),16),bez((36,16),(55,20),(68,31),(59,34),16)]:d.line([T(q) for q in ps],fill='#897868',width=2)
 d.line([T(q) for q in bez((13,23),(24,8),(36,8),(43,15),18)],fill='#897868',width=2)
 if far:
  d.line([T((-7,-26)),T((-7,26))],fill=INK,width=14);d.line([T((-7,-26)),T((-7,26))],fill='#4e806d',width=9)

def scene(fr):
 s=S[fr];im=Image.new('RGB',(1920,1260),BG);d=ImageDraw.Draw(im)
 # Actual render has a shallow tabletop950..981, followed by the front apron981..1030.
 d.rectangle((763,950,1919,981),fill='#b8a286',outline='#554838',width=3)
 d.rectangle((763,981,1919,1030),fill='#9a8066',outline='#554838',width=3)
 ns['lamp'](d,0)
 d.rectangle((1064,949,1136,971),fill='#bda16d',outline=INK,width=3);d.line((1066,963,1134,963),fill='#9a6951',width=6)
 d.line((1150,963,1213,960),fill='#806b48',width=6);d.ellipse((1208,955,1218,965),fill='#453c32')
 ns['arm'](d,*s['L'],True);ns['torso'](d,s);ns['head'](d,s['face'],ns['WICK']);ns['arm'](d,*s['R'],False)
 loose_hand(d,s['L'][2],True,fr>=114,-.1 if fr==82 else 0)
 loose_hand(d,s['R'][2],False,fr>=96,.25 if fr==82 else 0)
 # The heel/side rests at981; relaxed fingertips drape in front of the apron.
 if fr>=114:
  for x in [880,1015]:d.line((x-4,981,x+8,981),fill='#765c43',width=3)
 d.rectangle((0,0,1919,100),fill=BG);d.text((30,20),f'S08 F{fr:03d} / 真实桌沿981 · 松弯落手补充 v2',font=font,fill=INK)
 d.text((30,60),'桌面实际950–981；前板981–1030。手轻搭近沿，指节松弯垂前，不靠1055假支撑。',font=sm,fill=INK)
 d.rectangle((0,1080,1919,1259),fill=BG)
 lines=['082→096→114落定；114–143保持。无新增112节点。近手沿沿回带；远手随身回收、下降。',
 '为981真实承面调整远肘：096(950,930)→(900,870)，114到(900,880)；此为待复审投影例外。',
 '肩/胸颈头/近肘不改；114/143身躯仅096上下文。远掌朝下短缩须真实绘画，不把扁轮廓当生产手源。',
 '末远手止于盒左前方，近手再左侧；中段经盒前侧可暂遮挡，但不能画进盒实体或抹掉道具。']
 for i,t in enumerate(lines):d.text((30,1100+i*39),t,font=sm,fill=INK)
 return im
for fr in [82,96,114,143]:
 im=scene(fr);im.save(OUT/f'F{fr:03d}_actual981_contact_PROPOSAL.png');im.crop((650,760,1245,1080)).resize((1190,640)).save(OUT/f'F{fr:03d}_hands_close.png')
strip=Image.new('RGB',(1920,820),BG);d=ImageDraw.Draw(strip)
for k,fr in enumerate([82,96,114]):
 im=scene(fr).crop((600,650,1250,1080)).resize((630,417));strip.paste(im,(k*640,60));d.text((k*640+12,16),f'F{fr:03d}'+('–143' if fr==114 else ''),font=font,fill=INK)
d.text((30,515),'实际桌沿y981：两只手最后以掌根/侧缘轻搭，四指自然微弯垂在前板前；拇指不压成拳。',font=sm,fill=INK)
d.text((30,560),'近腕：990,1005 → 915,981 → 875,981；远腕：1115,820 → 1040,920 → 1010,981。',font=sm,fill=INK)
d.text((30,605),'远肘回收投影必须重审：保持原肩胸头，不能为旧肘坐标强挤短腕。末远掌朝下有手面透视短缩。',font=sm,fill=INK)
d.text((30,650),'待第二人实际轮廓审核；最终身体落座仍按原方案。旧1055接触/112版本已撤回，不供实现。',font=sm,fill=INK)
strip.save(OUT/'F082_F096_F114_actual_table_path.jpg',quality=95)
source=ROOT/'astra_production_verification_20261018_1625/20261018_3f4c2f_verify/S08/S08_F000_actual_1920x1080.png'
Image.open(source).crop((735,920,1500,1050)).resize((1530,260)).save(OUT/'actual_table_source_crop.png')
r={'status':'REVISION2_PENDING_SECOND_REVIEW','actual_table_source':str(source.relative_to(ROOT)),'tabletop_y':[950,981],'front_apron_y':[981,1030],'states':{str(f):S[f] for f in [82,96,114,143]},'necessary_projection_exceptions':{'F082_near_wrist':[[1000,1010],[990,1005]],'F096_far_elbow':[[950,930],[900,870]],'F114_far_elbow':[900,880]},'fixed':['shoulders','head/chest/neck/body','near elbows','lamp box match coordinates','first3'],'final_hand_projection':'Far palm rotates downward toward table plane, projected x about75% of the side-facing schematic; true hand identity and volume require actual drawing. Not a hand-scaling recipe.','body_context':'F114/F143 use approved096 body only as context, no new seated-body freeze.','obsolete':'parent v1 1055 support and112 node rejected'}
(OUT/'actual_table_settle_PROPOSAL.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
