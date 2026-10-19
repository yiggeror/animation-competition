from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
ROOT=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parents[1];FONT=ROOT/'assets/fonts/NotoSansSC-VF.ttf'
f=lambda n:ImageFont.truetype(str(FONT),n)
board=Image.new('RGB',(2200,1450),'#f2f4f5');dr=ImageDraw.Draw(board)
dr.text((35,20),'S20 实际原图阅读与比例依据 · 本轮0生图',font=f(38),fill='#273642')
configs=[('G current03',ROOT/'collab/refs/grandma_turnaround_current03_draft.png',(380,0,700,768),(540,29),(540,181),(540,751),40),('小满 v4',ROOT/'collab/refs/xiaoman_turnaround_v4_draft.png',(160,0,480,1024),(320,60),(320,254),(320,960),650)]
records=[]
for title,p,crop,top,chin,sole,bx in configs:
 im=Image.open(p).convert('RGB');part=im.crop(crop);sc=1060/part.height;sz=(round(part.width*sc),1060);part=part.resize(sz);board.paste(part,(bx,140));dr.text((bx,95),title,font=f(29),fill='#273642')
 for pt,label in [(top,'头骨/主发块顶'),(chin,'颏'),(sole,'鞋底')]:
  x=bx+(pt[0]-crop[0])*sc;y=140+(pt[1]-crop[1])*sc;dr.line((bx,y,bx+sz[0],y),fill='#c26d58',width=2);dr.text((bx+sz[0]+8,y-13),label,font=f(21),fill='#9a4f41')
 records.append({'source':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'manual_points':{'main_hair_or_skull_top':top,'chin':chin,'sole':sole},'point_uncertainty_px':4,'apparent_height_in_head_units':(sole[1]-top[1])/(chin[1]-top[1]),'note':'2D identity/proportion reading only, loose ahoge excluded; not true3D skeleton measurement.'})
# Actual, unmodified source hand pixels, only cropped/enlarged for inspection.
thumbs=[('旧小满：单签前段；尾段已删，不代表整个长杆已成立。','collab/refs/anim_20_xiaoman_puppeteer.png',(640,330,875,660)),('旧奶奶笑：原像素只清楚画出一截短签。','collab/refs/anim_20_grandma_laugh_bent.png',(630,625,895,780))]
for j,(label,name,crop) in enumerate(thumbs):
 p=ROOT/name;im=Image.open(p).convert('RGB').crop(crop);im.thumbnail((720,400));y=140+j*485;board.paste(im,(1350,y));dr.text((1290,y-40),label,font=f(23),fill='#273642')
dr.text((1280,1100),'采用母版：奶奶current03＋表情02；小满v4＋表情03。',font=f(24),fill='#273642')
dr.text((1280,1140),'current04颈影编辑失败，不升为母版。',font=f(24),fill='#273642')
dr.text((35,1260),'手工读点约±4px；成人约4.7头高，小满约4.64头高。本镜施工建议4.8／4.7，待Astra冻结。',font=f(25),fill='#273642')
dr.text((35,1305),'腕—肘—肩必须沿完整体量追踪；旧二维镜像不会交换手臂遮挡。左腕玉镯只随解剖L。',font=f(25),fill='#273642')
dr.text((35,1350),'原图仅身份／造型依据；旧颈部橙影不作为固定人物照明纹理，场景灯光后续由场景接入。',font=f(25),fill='#273642')
board.save(D/'reference/00_actual_sources_and_ratios.png');(D/'provenance/manual_master_readings.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');print('Actual source audit built; no source file edited.')
