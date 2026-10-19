from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
R=Path(__file__).resolve().parent;P=R.parent;B=P.parent
s=B/'F058_reuse_locked044_gate/candidate/F058_exact_LOCKED044_REUSE_PENDING_ASTRA.png';t=P/'candidate/F063_zero_call_semantic_RECONNECTED.png';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(s)=='fe70d79e90559659a83772cb29e4cbeffb2b22b355ed3e403509621b381cfad9';font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18);(R/'frames').mkdir(exist_ok=True)
rows=[]
for i in range(11):
 q=s if i<5 else t;z=Image.open(q).convert('RGBA');bg=Image.new('RGBA',(1672,972),(213,223,231,255));bg.alpha_composite(z);d=ImageDraw.Draw(bg);d.text((12,944),f'actual source F{58+i:03d} / '+('F058 locked044 reuse' if i<5 else 'F063 zero-call semantic reconnection')+' / 24fps / SOURCE EXPOSURE 5 + 6',font=font,fill='#243c50');bg.convert('RGB').save(R/f'frames/frame_{i:02d}.png');rows.append({'index':i,'source_frame':58+i,'drawing':'F058'if i<5 else'F063','source_sha256':sha(q)})
(R/'source_exposure_058x5_063x6.json').write_text(json.dumps({'fps':24,'frames':11,'duration_seconds':11/24,'source_exposure_unchanged':True,'imagegen_calls':0,'frames_list':rows},indent=2)+'\n');print('11 source frames rendered, 058x5 then063x6; no motion interpolation')
