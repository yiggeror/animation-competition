#!/usr/bin/env python3
"""QA composites/measurements only. Native drawing bytes are never rewritten."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib
P=Path(__file__).resolve().parents[1];R=P.parent;ROOT=R.parents[2]
raw=P/'originals/S24_F000_call_001_raw.png';candidate=P/'candidates/F000_native_rgba.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert raw.read_bytes()==candidate.read_bytes()==Path('/workspace/generated_images/exec-442f4faf-84e6-4c96-b9af-02582c9c01aa.png').read_bytes()
im=Image.open(raw).convert('RGBA');assert im.size==(1024,1536)
master=Image.open(ROOT/'assets/chars/x13/F000.png').convert('RGBA')
font=lambda n:ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',n)
def comp(a,c=(245,245,245,255)):
 b=Image.new('RGBA',a.size,c);b.alpha_composite(a);return b.convert('RGB')
sheet=Image.new('RGB',(1600,1140),'#f4f2ec');d=ImageDraw.Draw(sheet)
for i,a in enumerate([master,im]):
 b=comp(a);b.thumbnail((740,1030));sheet.paste(b,(i*800+25,60));d.text((i*800+20,15),['锁定母稿F000：身份/颜色','S24首F000：原生返回'][i],font=font(27),fill='#25353e')
d.text((25,1090),'同原生画布等比查看；S24实际头位较构造偏低，不做局部拉伸/搬脸。',font=font(25),fill='#a15f45');sheet.save(P/'qa/01_master_and_candidate_same_canvas.jpg',quality=97)
sheet=Image.new('RGB',(1700,1000),'#f4f2ec');d=ImageDraw.Draw(sheet)
for i,a in enumerate([master,im]):
 b=comp(a).crop((100,430,950,1220));sheet.paste(b,(i*850,65));d.text((i*850+15,15),['固定母稿颏/颈/领','S24候选颏/颈/领'][i],font=font(27),fill='#25353e')
d.text((25,930),'完整头颈领实看，闭口并保持清醒；不是面部贴图或缩嘴。',font=font(26),fill='#25353e');sheet.save(P/'qa/02_jaw_neck_collar_actual.jpg',quality=97)
variants=[{'id':'A_reference_plan','scale':.67,'translation':[600,90],'meaning':'035c998构造提案原值；实际头位偏低'},
 {'id':'B_uniform_candidate','scale':.70,'translation':[590,20],'meaning':'仅整层等比/平移，发顶接近原景；头高较构造略大，待锁'}]
sheet=Image.new('RGB',(1920,700),'#f4f2ec');d=ImageDraw.Draw(sheet)
for i,v in enumerate(variants):
 s=v['scale'];x,y=v['translation'];placed=im.transform((1920,1080),Image.Transform.AFFINE,(1/s,0,-x/s,0,1/s,-y/s),Image.Resampling.BICUBIC)
 a=comp(placed,(205,211,213,255));a.resize((960,540)).save(P/f"qa/{v['id']}_neutral_placement.jpg",quality=97)
 sheet.paste(a.resize((960,540)),(i*960,65));d.text((i*960+15,15),f"{v['id']}  {s}+({x},{y})",font=font(25),fill='#25353e');d.text((i*960+15,620),v['meaning'],font=font(22),fill='#25353e')
d.text((20,665),'仅中性底配准比较；非Canvas场景/非镜头成片。原生PNG未改字节，A/B均待Astra锁定。',font=font(24),fill='#a15f45');sheet.save(P/'qa/03_registration_candidates_neutral_NOT_SCENE.jpg',quality=96)
registration={'status':'UNIFORM_REGISTRATION_CANDIDATES_PENDING_ASTRA','native_canvas':[1024,1536],'candidate_png':'candidates/F000_native_rgba.png','candidate_sha256':sha(candidate),'raw_to_candidate':'identity,byte-identical','local_repaint':False,'warp':False,'alpha_cleanup':False,'color_correction':False,'scene_canvas':[1920,1080],'variants':variants,'limits':'Actual native head placement is lower than construction;variantB matches approximate crown/cowlick framing at a larger head scale. Neither is frozen; no local anatomy correction or scene render.'}
(P/'candidates/registration_candidates.json').write_text(json.dumps(registration,ensure_ascii=False,indent=2)+'\n')
regions={
 'hair':([260,260,520,500],[360,280,730,500]),
 'skin':([530,540,730,730],[310,760,480,850]),
 'dress_yellow':([300,1120,650,1300],[310,1210,650,1390]),
 'collar_white':([360,1000,680,1120],[360,1020,700,1160])}
def stats(a,roi,name):
 a=np.array(a)[roi[1]:roi[3],roi[0]:roi[2]];r,g,b,alpha=[a[:,:,i].astype(int)for i in range(4)];mask=alpha>=250
 if name=='hair':mask&=(r>20)&(r<160)&(g<110)&(b<100)&(r>g)
 elif name=='skin':mask&=(r>180)&(g>110)&(b>70)&(r>g+15)&(g>b)
 elif name=='dress_yellow':mask&=(r>180)&(g>140)&(b<110)
 else:mask&=(np.minimum(np.minimum(r,g),b)>200)&(np.maximum(np.maximum(r,g),b)-np.minimum(np.minimum(r,g),b)<40)
 assert mask.sum()>80,(name,int(mask.sum()))
 rgb=a[:,:,:3][mask].astype(float);return {'roi':roi,'pixels':int(mask.sum()),'median_RGB':np.median(rgb,axis=0).round(2).tolist(),'p10_RGB':np.percentile(rgb,10,axis=0).round(2).tolist(),'p90_RGB':np.percentile(rgb,90,axis=0).round(2).tolist()}
rows=[]
for name,(a,b) in regions.items():
 src=stats(master,a,name);dst=stats(im,b,name);rows.append({'semantic_region':name,'fixed_master':src,'candidate':dst,'median_delta_RGB':np.subtract(dst['median_RGB'],src['median_RGB']).round(2).tolist()})
color={'fixed_master':'assets/chars/x13/F000.png','fixed_master_sha256':sha(ROOT/'assets/chars/x13/F000.png'),'candidate_sha256':sha(candidate),'method':'Separate manually located semantic interior ROIs;same explicit opacity/color masks. Descriptive diagnostics, not a whole-image average or automatic approval threshold. No color edits.','regions':rows,'status':'regional_color_baseline_pending_Astra'}
(P/'qa/semantic_color_comparison.json').write_text(json.dumps(color,ensure_ascii=False,indent=2)+'\n')
sheet=Image.new('RGB',(1650,790),'#f4f2ec');d=ImageDraw.Draw(sheet)
for i,row in enumerate(rows):
 x=20+i*410;d.text((x,20),row['semantic_region'],font=font(27),fill='#25353e')
 for j,key in enumerate(['fixed_master','candidate']):
  rgb=row[key]['median_RGB'];d.rectangle((x,90+j*240,x+360,270+j*240),fill=tuple(int(v)for v in rgb));d.text((x,280+j*240),('母稿'if j==0 else'S24')+' '+str(rgb),font=font(22),fill='#25353e')
 d.text((x,620),'ΔRGB '+str(row['median_delta_RGB']),font=font(21),fill='#25353e')
d.text((20,720),'各姿态分别取同语义内区，不比较全图均值；保留本地明暗差，不强制平涂。未修色。',font=font(25),fill='#a15f45');sheet.save(P/'qa/04_semantic_color_comparison.jpg',quality=97)
print(json.dumps({'native_sha256':sha(candidate),'regional_median_deltas':{r['semantic_region']:r['median_delta_RGB']for r in rows},'registration':'A/B pending Astra, native drawing unchanged'},ensure_ascii=False,indent=2))
