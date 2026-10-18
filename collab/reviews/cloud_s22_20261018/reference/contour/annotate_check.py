from pathlib import Path
import json,math,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import distance_transform_edt
P=Path(__file__).resolve().parent;F='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
def font(n):return ImageFont.truetype(F,n)
def write(d,p,s,n=25,c='#253039'):d.text(p,s,font=font(n),fill=c)
def lead(d,a,b,c='#465c68'):
 d.line([a,b],fill=c,width=2);ang=math.atan2(b[1]-a[1],b[0]-a[0]);d.polygon([b,(b[0]-11*math.cos(ang-.4),b[1]-11*math.sin(ang-.4)),(b[0]-11*math.cos(ang+.4),b[1]-11*math.sin(ang+.4))],fill=c)
checks=[]
for f in ['000','024']:
 im=Image.open('/tmp/S22_F'+f+'_contour_base.png').convert('RGB');d=ImageDraw.Draw(im)
 g=np.array(Image.open('/tmp/s22_G'+f+'.png'))[:,:,3]>127;c=np.array(Image.open('/tmp/s22_C'+f+'.png'))[:,:,3]>127
 overlap=int((g&c).sum());gap=float(distance_transform_edt(~c)[g].min())
 if f=='000':assert overlap==0 and gap>=10,(overlap,gap)
 else:assert overlap>10000
 title='小满自主握签；奶奶右手近而未触' if f=='000' else '奶奶右手完整包握；孩子仍自己夹签'
 write(d,(28,20),'S22 F'+f+'｜'+title,31)
 write(d,(28,74),'手工体积轮廓参考｜右包右、2手/1主签；成人右腕无镯｜图像生成调用0',23,'#9d4431')
 write(d,(42,145),'奶奶从小满右肩外后方进入\n裸前臂 → 腕 → 掌，连续',24,'#076e77');lead(d,(400,210),(560,430) if f=='000' else(650,500),'#076e77')
 write(d,(1015,170),'小满食指／中指：远面托夹',24,'#9b5b18');lead(d,(1120,215),(938,590),'#9b5b18');lead(d,(1120,223),(938,639),'#9b5b18')
 write(d,(1080,276),'小满拇指：近面抵杆，必须可见',24,'#9b5b18');lead(d,(1190,320),(919,616),'#9b5b18')
 if f=='000':
  write(d,(1080,380),'成人四指待包，仍未触小满',24,'#076e77');lead(d,(1160,424),(781,534),'#076e77')
  write(d,(1060,455),f'两手轮廓最近间隙约{gap:.0f}px（本参考栅格）',22,'#076e77')
 else:
  write(d,(1080,380),'奶奶拇指：贴手背近腕，不碰杆',24,'#076e77');lead(d,(1160,422),(810,610),'#076e77')
  write(d,(1030,466),'包指从尺侧绕到下近面，四指各接回同一掌',23,'#076e77');lead(d,(1130,502),(823,750),'#076e77')
 write(d,(42,840),'小满右腕 → 掌 → 弯曲四指\n自身握点在成人接触前后不变',24,'#9b5b18');lead(d,(400,874),(704,700),'#9b5b18')
 d.ellipse((919,591,933,605),outline='#a73d32',width=2);write(d,(967,671),'P=(926,598)\n一根主签，轴−30°',21,'#7d4625')
 # Inset shows actual manually drawn outline, no additional source image or generated art.
 box=(655,460,995,800);inset=Image.open('/tmp/S22_F'+f+'_contour_base.png').convert('RGB').crop(box).resize((544,544));im.paste(inset,(1340,520));d=ImageDraw.Draw(im);d.rectangle((1338,518,1885,1065),outline='#a6a397',width=2);write(d,(1350,525),'夹点／包指局部 1.6×',21)
 write(d,(32,1008),'只有两张新增参考；原12态/120f曝光及另外10态未改。不是生产画稿；两图待Astra过门。',22,'#694f3b')
 out=P/f'F{f}_volume_reference.png';im.save(out)
 checks.append({'frame':int(f),'new_reference':out.name,'size':im.size,'manual_source':f'F{f}_volume_source.svg','adult_child_surface_overlap_px':overlap,'minimum_outline_distance_px':gap,'child_grip_P':[926,598],'child_wrist':[700,700],'adult_wrist':[560,430] if f=='000' else [650,500],'rod_angle_deg':-30,'adult_never_grips_rod':True,'image_generation_calls':0})
(P/'contour_checks.json').write_text(json.dumps({'method':'manually authored Bezier palm/finger volumes; SVG rasterized by installed Chromium; temporary alpha masks only check hover separation, not anatomical signoff','checks':checks,'actual_visual_review':'pending final annotated-image check','original_exposure_unchanged':True},ensure_ascii=False,indent=2)+'\n')
print(json.dumps(checks,ensure_ascii=False,indent=2))
