from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;a=json.loads((R/'anchors_fixed.json').read_text());rr={r['file']:r for r in a['frames']};ks=[1,3,5,6,7,8,12,13,14,15,16];ki={k:i for i,k in enumerate(ks)}
tl=[]
def put(f,k):
 if tl and tl[-1][0]==f:tl[-1]=[f,k]
 elif not tl or tl[-1][1]!=k:tl.append([f,k])
def cycle(f):
 for d,k in enumerate([1,3,13,14,13,3,15,16,1]):put(f+2*d,k)
def blink(f):
 for d,k in enumerate([5,6,5]):put(f+2*d,k)
cycle(0);put(18,8);blink(30);cycle(36);put(54,7);put(63,12);cycle(81);put(102,8);blink(117);cycle(123);put(141,12);cycle(162);put(180,7);put(189,8);blink(204);cycle(210);put(228,12);cycle(246);put(264,8);blink(276);put(282,1)
d={'target':a['target'],'fps':24,'frames':[{'file':f'x01_prone_phone_k{k:02d}','anchors':rr[f'x01_prone_phone_k{k:02d}']['anchors']} for k in ks],'timelineFrames':[[f,ki[k]] for f,k in tl]};(R/'candidate/assets/flips/x01_prone_phone.flip.json').write_text(json.dumps(d,indent=2)+'\n')
focus={1,3,13,14,15,16};groups=[]
for i,(f,k) in enumerate(tl):
 end=tl[i+1][0] if i+1<len(tl) else 288;g='focus' if k in focus else str(k)
 if groups and groups[-1]['group']==g:groups[-1]['end_exclusive']=end
 else:groups.append({'start':f,'end_exclusive':end,'group':g})
assert max(x['end_exclusive']-x['start'] for x in groups)<=24
summary={'totalFrames':288,'unique_leg_poses':[1,3,13,14,15,16],'leg_path':[1,3,13,14,13,3,15,16,1],'leg_dwell_frames':2,'note':'Return reuses outbound bridges instead of direct k14→k15. Six distinct leg poses, nine exposure entries per complete cycle. Facial focus group treats all leg variants as SAME face. Strict static alignment passes are not scene/full-speed acceptance. k14 far sandal turns toe-front and gold buckle becomes visible: explicit scene-review risk.','pose_timeline':tl,'face_groups':groups,'maximum_same_face_frames':max(x['end_exclusive']-x['start'] for x in groups)}
(R/'reports/s01_timing.json').write_text(json.dumps(summary,indent=2)+'\n')
for p in sorted((R/'requests').glob('*.json')):
 x=json.loads(p.read_text());k=int(p.stem.lstrip('k').split('_')[0]);im=R/'raw'/f'x01_prone_phone_k{k:02d}.png';x['status']='generated_once';x['actual_original_sha256']=hashlib.sha256(im.read_bytes()).hexdigest();p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
sh=Image.new('RGB',(6*380,440),(136,136,136));dr=ImageDraw.Draw(sh)
for j,k in enumerate([1,7,8,12,5,6]):
 im=Image.open(R/'raw'/f'x01_prone_phone_k{k:02d}.png').convert('RGBA');bg=Image.new('RGBA',im.size,(136,136,136,255));bg.alpha_composite(im);im=bg.convert('RGB').crop((950,260,1510,875));im.thumbnail((380,410));sh.paste(im,(j*380,25));dr.text((j*380+8,7),f'k{k:02d}',fill='white')
sh.save(R/'reports/game_faces_actual_contact.jpg')
print('max same face',summary['maximum_same_face_frames'],'timeline changes',len(tl))
