from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,math,numpy as np
D=Path(__file__).resolve().parent;anchors=json.loads((D/'anchors.json').read_text());T={'width':779,'height':1355,'anchors':[[538,1274],[745,1215]]}
labels=['摘出一粒/母版','低位捏开荚','高位捏开荚','暂放仍带豆荚','眼先看画外左侧女孩','抬头停手/张口反应','低头短眨眼','抬头含笑闭眼（短插）']
t1=[[0,0],[6,1],[18,2],[21,6],[24,3],[27,1],[54,2],[57,6],[60,3],[63,4],[69,5],[78,7],[81,5],[84,4],[87,2],[90,0],[93,3],[96,1],[117,2],[120,6],[123,3],[126,1],[144,2],[147,6],[150,3],[153,1],[180,2],[183,6],[186,3],[189,1],[198,4],[204,5],[210,7],[213,4],[216,2],[219,0],[222,3],[225,1],[246,2],[249,6],[252,3],[255,1]]
t4=[[0,5],[69,7],[72,5],[96,4],[108,5],[135,7],[138,5],[162,4],[174,5],[186,4],[189,5]]
frames=[{'file':a['file'],'anchors':a['anchors']} for a in anchors]
for name,shot,tl,total in [('g01_beans','S01',t1,288),('g01_beans_s04','S04',t4,192)]:
 spec={'note':f'{shot} candidate only; two-foot rigid similarity registration; no image warping. S01 and S04 separate timelines; S10 not authorized. k04 retains beans in pod, only temporary placement, not empty husk. All new originals are independent one-shot edits of g01_beans master; k01 reprocessed same pipeline.', 'target':T,'fps':24,'frames':frames,'timelineFrames':tl}
 (D/'assets/flips'/f'{name}.flip.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2))
 events=[{'start_frame':n,'local_seconds':n/24,'file':frames[i]['file'],'description':labels[i],'duration_frames':(tl[j+1][0] if j+1<len(tl) else total)-n,'visible':shot=='S01' or n>=63} for j,(n,i) in enumerate(tl)]
 
 for e in events:
  start=e['start_frame'];end=start+e['duration_frames'];first=max(start,63) if shot=='S04' else start
  e['visible']=end>first;e['visible_from_frame']=first if end>first else None;e['visible_frame_count']=max(0,end-first)
 (D/'reports'/f'{shot}_exposures.json').write_text(json.dumps(events,ensure_ascii=False,indent=2))
(D/'evidence/registered').mkdir(exist_ok=True)
regs=[]
for i,a in enumerate(anchors):
 im=Image.open(D/'originals'/f"{a['file']}.png").convert('RGBA');aa=np.array(a['anchors']);tt=np.array(T['anchors']);va=aa[1]-aa[0];vr=tt[1]-tt[0];s=np.linalg.norm(vr)/np.linalg.norm(va);ang=np.arctan2(vr[1],vr[0])-np.arctan2(va[1],va[0]);c=s*np.cos(ang);z=s*np.sin(ang);M=np.array([[c,-z],[z,c]]);t=tt[0]-M@aa[0];inv=np.linalg.inv(M);it=-inv@t
 reg=im.transform((779,1355),Image.Transform.AFFINE,(*inv[0],it[0],*inv[1],it[1]),resample=Image.Resampling.BICUBIC)
 bg=Image.new('RGBA',reg.size,(175,175,175,255));bg.alpha_composite(reg);bg=bg.convert('RGB');bg.save(D/'evidence/registered'/f"{a['file']}.png");regs.append(bg)
for what,box in [('stool',(480,860,779,1290)),('basin',(85,640,480,800))]:
 w,h=box[2]-box[0],box[3]-box[1];out=Image.new('RGB',(w*4,(h+24)*2),(240,240,240));draw=ImageDraw.Draw(out)
 for i,im in enumerate(regs):x=(i%4)*w;y=(i//4)*(h+24);out.paste(im.crop(box),(x,y+24));draw.text((x+5,y+5),f'k{i+1:02d} / registered native crop',fill='black')
 out.save(D/'evidence'/f'{what}_registered_contact.jpg',quality=94)
meta=[]
for i,a in enumerate(anchors):
 p=D/'originals'/f"{a['file']}.png";im=Image.open(p)
 meta.append({'file':a['file'],'label_actual':labels[i],'source_size':im.size,'original_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'generated':i>0,'attempts':1 if i else 0,'registration':a})
(D/'originals_manifest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
print('wrote 2 flip candidates, exposure tables, diagnostic registration crops')
