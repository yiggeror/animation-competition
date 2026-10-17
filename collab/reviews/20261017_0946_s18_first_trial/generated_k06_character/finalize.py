from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,numpy as np
out=Path('/tmp/laidian-s18-pilot-audit/generated_k06_character');root=Path('/workspace/animation-competition');font=ImageFont.truetype(str(root/'assets/fonts/NotoSansSC-VF.ttf'),18)
srcs={'master':root/'assets/chars/x18_laugh.png','target':Path('/tmp/laidian-s18-pilot-candidate/k06_target.png'),'v1':Path('/tmp/laidian-s18-pilot-candidate/generated_k06_v1/x18_k06_candidate.png'),'v2':Path('/tmp/laidian-s18-pilot-candidate/generated_k06_v2/x18_k06_candidate.png')}
info={}
for name,p in srcs.items():
    im=Image.open(p);info[name]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':list(im.size),'mode':im.mode}
for ver,folder in [('v1',out),('v2',out/'v2')]:
    data=json.loads((folder/'registration_measurements.json').read_text());M=np.array(data['candidate_native_to_master_matrix']);t=np.array(data['translation']);inv=np.linalg.inv(M);off=-inv@t
    im=Image.open(srcs[ver]).convert('RGBA').transform((635,1175),Image.Transform.AFFINE,(*inv[0],off[0],*inv[1],off[1]),Image.Resampling.BICUBIC)
    im.save(folder/'evidence'/f'{ver}_diagnostic_registered_to_master_635x1175_RGBA.png')
ims=[Image.open(srcs['master']).convert('RGB'),Image.open(out/'evidence/candidate_stool_registered_gray.png').convert('RGB'),Image.open(out/'v2/evidence/candidate_stool_registered_gray.png').convert('RGB')]
for name,box in [('upperbody_three',(155,255,465,655)),('stool_shoes_three',(0,825,635,1175))]:
    w,h=box[2]-box[0],box[3]-box[1];strip=Image.new('RGB',(3*w,h+34),'white');d=ImageDraw.Draw(strip)
    for i,(label,im) in enumerate(zip(['母版 k07','v1 诊断配准','v2 诊断配准'],ims)):
        strip.paste(im.crop(box),(i*w,34));d.text((i*w+6,6),label,font=font,fill='black')
    strip.save(out/'evidence'/f'{name}.png')
(out/'source_manifest.json').write_text(json.dumps({'sources':info,'originals_modified':False,'diagnostic_coordinate_space':'635x1175 original master canvas; generated originals remain 922x1706','note':'Diagnostic output transforms are global similarities only, no local image repairs or face/body warps.'},ensure_ascii=False,indent=2))
print(json.dumps(info,ensure_ascii=False,indent=2))
