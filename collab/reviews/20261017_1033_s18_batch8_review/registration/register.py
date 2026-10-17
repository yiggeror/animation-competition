#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import sobel
import numpy as np,json,hashlib,math
P=Path('/tmp/batch8_registration'); S=Path('/tmp/laidian-s18-batch8/originals'); R=Path('/workspace/animation-competition')
(P/'registered_rgba').mkdir(exist_ok=True);(P/'diagnostics').mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def composite(im):
 bg=Image.new('RGBA',im.size,(220,220,220,255));bg.alpha_composite(im.convert('RGBA'));return bg.convert('RGB')
def grad(im):
 z=np.asarray(im.convert('L'),float);return np.minimum(np.hypot(sobel(z,axis=0),sobel(z,axis=1)),300)
font=ImageFont.truetype(str(R/'assets/fonts/NotoSansSC-VF.ttf'),16)
anchors=[('A1_left_foot',[22,1142]),('A2_right_foot',[312,1142]),('H_seat_lower_left',[22,899])]
frames=[];measure=[];panels=[];sourcechecks=[]
keys=['k02','k03','k04','k05','k08','k09','k10','k11']
expected={x['key']:x for x in json.loads((S.parent/'generation_manifest.json').read_text())['images']}
for key in keys:
 ip=S/f'x18_{key}.png';raw=Image.open(ip).convert('RGBA');w,h=raw.size
 assert [w,h]==expected[key]['size'] and sha(ip)==expected[key]['sha256']
 base=R/'assets/chars'/('x16_arms_loose.png' if key in keys[:4] else 'x18_laugh.png')
 mother=Image.open(base).convert('RGBA');mg=composite(mother);g1=grad(mg)
 # One UNIFORM nominal scale, taking actual per-image dimensions into account.
 scale=(w/635+h/1175)/2
 nominal=raw.transform((635,1175),Image.Transform.AFFINE,(scale,0,0,0,scale,0),Image.Resampling.BICUBIC)
 ng=composite(nominal);g2=grad(ng);matches=[]
 for name,(x,y) in anchors:
  r=12 if x<30 else 16;tpl=g1[y-r:y+r+1,x-r:x+r+1];tpl=tpl-tpl.mean();n=np.linalg.norm(tpl);best=(-1,0,0)
  for dy in range(-48,26):
   for dx in range(-30,31):
    xx,yy=x+dx,y+dy
    if xx-r<0 or yy-r<0 or xx+r>=635 or yy+r>=1175:continue
    sub=g2[yy-r:yy+r+1,xx-r:xx+r+1];sub=sub-sub.mean();score=float((tpl*sub).sum()/(n*np.linalg.norm(sub)+1e-9))
    if score>best[0]:best=(score,dx,dy)
  nominal_point=np.array([x+best[1],y+best[2]],float);native=nominal_point*scale
  matches.append({'name':name,'target':[x,y],'candidate_nominal':nominal_point.tolist(),'candidate_native':native.tolist(),'gradient_ncc':best[0],'used_for_fit':name.startswith('A')})
 # Fit only two feet. Holdout seat point never affects the matrix.
 src=np.array([q['candidate_native'] for q in matches[:2]]);target=np.array([q['target'] for q in matches[:2]],float)
 v=src[1]-src[0];u=target[1]-target[0];aa=np.dot(u,v)/np.dot(v,v);bb=(u[1]*v[0]-u[0]*v[1])/np.dot(v,v)
 M=np.array([[aa,-bb],[bb,aa]]);t=target[0]-M@src[0]
 for q in matches:
  q['registered']=(M@np.array(q['candidate_native'])+t).tolist();q['residual_px']=float(np.linalg.norm(np.array(q['registered'])-q['target']))
 inv=np.linalg.inv(M);offset=-inv@t;coeffs=(*inv[0],offset[0],*inv[1],offset[1])
 fit=raw.transform((635,1175),Image.Transform.AFFINE,coeffs,Image.Resampling.BICUBIC);op=P/'registered_rgba'/f'x18_{key}_registered_635x1175.png';fit.save(op)
 rgb=composite(fit);rgb.save(P/'diagnostics'/f'x18_{key}_registered_gray.png')
 # Foot/seat detail: source/candidate nominal/registered, markers use independent detections.
 crops=[]
 for label,im,pts in [('mother',mg,[q['target'] for q in matches]),('NCC nominal',ng,[q['candidate_nominal'] for q in matches]),('registered',rgb,[q['registered'] for q in matches])]:
  z=im.crop((0,830,340,1175));d=ImageDraw.Draw(z)
  for q,pt in zip(matches,pts):
   px,py=pt[0],pt[1]-830;col='#e32235' if q['used_for_fit'] else '#00a986';d.ellipse((px-5,py-5,px+5,py+5),outline=col,width=2);d.text((max(2,px-8),max(0,py-25)),q['name'].split('_')[0],font=font,fill=col)
  c=Image.new('RGB',(340,380),'white');c.paste(z,(0,35));ImageDraw.Draw(c).text((6,7),key+' '+label,font=font,fill='black');crops.append(c)
 trip=Image.new('RGB',(1020,380),'white')
 for i,c in enumerate(crops):trip.paste(c,(i*340,0))
 trip.save(P/'diagnostics'/f'x18_{key}_stool_triptych.png')
 small=rgb.resize((254,470),Image.Resampling.LANCZOS);panel=Image.new('RGB',(254,506),'white');panel.paste(small,(0,36));ImageDraw.Draw(panel).text((7,5),f'{key} holdout {matches[2]["residual_px"]:.2f}px',font=font,fill='black');panels.append(panel)
 frame={'file':f'x18_{key}','anchors':[[round(v,3) for v in q['candidate_native']] for q in matches[:2]]};frames.append(frame)
 entry={'key':key,'file':ip.name,'source_path':str(ip),'source_sha256':sha(ip),'source_size':[w,h],'base_path':str(base),'base_sha256':sha(base),'nominal_native_per_target_pixel_scale':scale,'anchor_matches':matches,'candidate_native_to_target_matrix':M.tolist(),'translation':t.tolist(),'homogeneous_matrix':[[*M[0],t[0]],[*M[1],t[1]],[0,0,1]],'rotation_deg':math.degrees(math.atan2(bb,aa)),'uniform_scale':math.hypot(aa,bb),'registered_path':str(op),'registered_sha256':sha(op)};measure.append(entry)
 dump(P/'frames.json',{'target':{'width':635,'height':1175,'anchors':[[22,1142],[312,1142]]},'frames':frames})
 dump(P/'registration_measurements.json',{'method':'Local gradient-NCC in a uniformly scaled nominal canvas; global similarity fitted ONLY to two stool-foot landmarks. Third seat corner is held out. No head/clothing features fit.','precision':'Matching is integer nominal pixels, about 1.45 source pixels; decimal native coordinates express the coordinate conversion, not subpixel localization precision.','frames':measure})
 print(key,raw.size,frame['anchors'],'NCC',[round(q['gradient_ncc'],3) for q in matches],'holdout',round(matches[2]['residual_px'],3),flush=True)
contact=Image.new('RGB',(254*4,506*2),'white')
for i,panel in enumerate(panels):contact.paste(panel,((i%4)*254,(i//4)*506))
contact.save(P/'contact_sheet.jpg',quality=93)
(P/'README.md').write_text('八张原图木凳配准诊断。frames.json 可给 Opus，锚点均为各自原图像素，目标是 [[22,1142],[312,1142]]。k02 为 921×1707，其余为 922×1706；脚本逐张使用实际尺寸与统一缩放，不做横纵分别拉伸。只拟合两凳脚；左座板下角 (22,899) 为独立 holdout。头、衣服、手均未参与定位。registered_rgba 是原 RGBA 经一次全局相似变换生成的 635×1175 诊断图，未做局部修图、补洞或角色变形。全部原件不变。NCC 为整数参考像素检测，输出小数仅坐标换算，不表示精密测量。此配准不证明八张角色身份/连续动作合格。\n')
files={str(p.relative_to(P)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(P.rglob('*')) if p.is_file() and p.name!='manifest.json'}
dump(P/'manifest.json',{'method':'two-stool-foot global similarity; independent third-corner holdout','source_generation_manifest':str(S.parent/'generation_manifest.json'),'source_generation_manifest_sha256':sha(S.parent/'generation_manifest.json'),'input_images':len(measure),'files':files,'max_holdout_error_px':max(v['anchor_matches'][2]['residual_px'] for v in measure),'source_byte_hashes_checked_against_generation_manifest':True})
