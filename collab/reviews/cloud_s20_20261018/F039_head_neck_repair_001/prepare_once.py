"""Single head/neck-only input; real frontal identity, protected complete039 body."""
from pathlib import Path
import json,hashlib,datetime,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation,binary_fill_holes,label
P=Path(__file__).resolve().parent;PACK=P.parent;ROOT=PACK.parents[2];I=P/'inputs';I.mkdir(exist_ok=True)
source=PACK/'F039_whole_source_diagnostic_001/F039_registered_rigid_pair_trial.png';A=np.array(Image.open(source).convert('RGBA'));H,W=A.shape[:2];yy,xx=np.indices((H,W));r,g,b=A[:,:,:3].astype(float).transpose(2,0,1)
front=ROOT/'collab/refs/xiaoman_turnaround_v4_draft.png';D=np.array(Image.open(front).convert('RGB'));hh,ww=D.shape[:2];fy,fx=np.indices((hh,ww));colour=D.max(2).astype(int)-D.min(2).astype(int)
allowed=(fx>=225)&(fx<=425)&(fy>=25)&((fy<240)|(((fx<286)|(fx>360))&(fy<283))|((fx>=286)&(fx<=360)&(fy<268)))
fg=allowed&((colour>11)|(D.min(2)<100));ids,_=label(fg);choose=int(ids[150,322]);fg=binary_fill_holes(ids==choose);fg=binary_dilation(fg,iterations=1)&allowed
F=np.zeros((hh,ww,4),np.uint8);F[:,:,:3]=D;F[:,:,3]=fg*255
s=.9;tx=607-323*s;ty=344-224*s
guide=np.array(Image.fromarray(F).transform((W,H),Image.Transform.AFFINE,(1/s,0,-tx/s,0,1/s,-ty/s),Image.Resampling.BICUBIC))
hair=(A[:,:,3]>20)&(r<130)&(g<120)&(r>g+3)
old=((A[:,:,3]>0)&(xx>=480)&(xx<672)&(yy>=170)&(yy<355))
old|=hair&(((xx>=480)&(xx<554)&(yy>=300)&(yy<425))|((xx>=610)&(xx<660)&(yy>=320)&(yy<384)))
old=binary_dilation(old,iterations=3)
neck=Image.new('L',(W,H));ImageDraw.Draw(neck).polygon([(578,348),(633,348),(638,378),(638,390),(628,394),(586,390),(575,367)],fill=255);neck=np.array(neck)>0
# Keep lower native neck in the guide for a continuous root; the local mask may repaint it.
clear=old|((neck)&(yy<378));Y=(A[:,:,3]>80)&(r>195)&(g>120)&(b<g*.63);protected=binary_dilation(Y,iterations=2)&~neck
protected|=(A[:,:,3]>80)&(r>180)&(g>130)&(b>g*.73)&(yy>=395)
protected|=(A[:,:,3]>0)&(xx>=582)&(yy>=395)
clear&=~protected
base=A.copy();base[clear]=0;target=np.array(Image.alpha_composite(Image.fromarray(base),Image.fromarray(guide)));target[protected]=A[protected]
edit=binary_dilation(old|(guide[:,:,3]>10)|neck,iterations=4)&~protected&(xx<710)&(yy<430)
assert not np.any(edit[:,710:]);assert not np.any(edit[440:]);assert not np.any(edit[398:440,585:900]&(A[398:440,585:900,3]>80))
Image.fromarray(target).save(I/'01_unique_complete_front_head_neck_target.png');Image.fromarray(target).crop((475,165,710,410)).resize((705,735),Image.Resampling.NEAREST).save(I/'02_same_view_new_head_neck_3x.png');Image.fromarray((edit*255).astype('uint8')).convert('RGB').save(I/'03_head_neck_small_collar_edit_white.png')
font=ImageFont.truetype(str(ROOT/'assets/fonts/NotoSansSC-VF.ttf'),18);card=Image.new('RGB',(640,380),'#e7ebee');d=ImageDraw.Draw(card);d.text((12,8),'旧侧脸只认眼/皮肤/发色；方向以第一张近正面目标为准',font=font,fill='#263743')
def graycrop(box):
 im=Image.fromarray(A).crop(box);bg=Image.new('RGBA',im.size,'#bdc1c4');bg.alpha_composite(im);return bg.convert('RGB')
card.paste(graycrop((569,255,649,340)).resize((176,187)),(15,45));d.text((15,240),'局部身份：不是姿势',font=font,fill='#263743')
for x,name,box in [(230,'头发内部',(558,239,576,254)),(440,'面颊内部',(612,300,628,316))]:
 d.text((x,55),name,font=font,fill='#263743');card.paste(graycrop(box).resize((160,140)),(x,85))
d.text((15,300),'两眼/两耳/颅发/下颌/连续颈面都转；其余人物全保护',font=font,fill='#263743');card.save(I/'04_old_side_face_identity_local_only.png')
bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(target));bg.convert('RGB').save(P/'target_actual_gray.jpg',quality=96)
meta={'status':'HEAD_NECK_INPUT_AUTHOR_REVIEW','new_image_calls':0,'source_registered039':str(source.relative_to(ROOT)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'approved_frontal_identity':str(front.relative_to(ROOT)),'front_identity_sha256':hashlib.sha256(front.read_bytes()).hexdigest(),'front_guide_similarity':{'scale':s,'translation':[tx,ty],'chin_target':[607,344]},'only_head_neck_small_collar_edit':True,'whole_body_redraw':False,'hands_or_wrists_in_edit':False,'feet_same_scale_review':'032_036_registered039_feet_same_scale.png','foot_findings':['三张均为同一世界画布1:1裁片，近支撑位置基本连续，远脚发生转向/落点变化；静态并排不等同已完成动态滑步验收。','032红凉鞋到036/039包头鞋存在鞋型漂移，单列记录，本次按指令不动腿鞋。'],'files':[]}
for f in sorted(I.glob('*.png')):meta['files'].append({'path':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(P/'input_preparation.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print('One complete new frontal head/neck target; arms/grips/pelvis/skirt/legs/shoes protected; zero calls.')
