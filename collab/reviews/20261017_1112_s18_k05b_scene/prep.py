from pathlib import Path
from PIL import Image
import numpy as np,subprocess,json,hashlib
P=Path(__file__).resolve().parent;R=Path('/workspace/animation-competition');S=Path('/tmp/laidian-s18-k05b-generation/x18_k05b.png');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(S)=='5573e3eb196ff8fa1ab07cd13c1e02318b400e51f6d34b714ad4b4a447934d2f'
im=Image.open(S).convert('RGBA');assert im.size==(922,1705)
a=np.asarray(im.getchannel('A'),np.float32);aa=(np.clip((a-6)/(247-6),0,1)*255).round().astype(np.uint8);im.putalpha(Image.fromarray(aa));alb=P/'assets/chars/x18_k05b.png';nrm=P/'assets/chars/x18_k05b_n.png';mat=P/'assets/chars/x18_k05b_m.png';im.save(alb)
cmds=[['python3','-I',str(R/'tools/card_maps.py'),str(alb),str(nrm),str(mat)],['python3','-I',str(R/'tools/card_soft.py'),str(alb),str(nrm)]]
for cmd in cmds:subprocess.run(cmd,check=True)
anchors_cmd=['python3','-I',str(R/'tools/flip_anchors.py'),str(R/'assets/chars/x18_laugh.png'),'22,1142;312,1142','22,899',str(S)]
anchors=json.loads(subprocess.check_output(anchors_cmd));(P/'anchors.json').write_text(json.dumps(anchors,indent=2)+'\n')
spec=json.loads((R/'assets/flips/x18_laugh.flip.json').read_text());old=spec['frames'][4];spec['frames'][4]={'file':'x18_k05b','anchors':anchors[0]['anchors']};(P/'x18_laugh.k05b.flip.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
manifest={'source':str(S),'source_sha256':sha(S),'source_size':list(im.size),'alpha_method':'same current prep_flip rule: clip((A-6)/241,0,1)*255, rounded uint8; preserve RGB and full canvas','alpha_check':{'original_lt32_to_gt128_pixels':int(((a<32)&(aa>128)).sum()),'original_gt200_to_lt64_pixels':int(((a>200)&(aa<64)).sum())},'commands':cmds+[anchors_cmd],'tools':{str(R/'tools'/f):sha(R/'tools'/f) for f in ['prep_flip.py','card_maps.py','card_soft.py','flip_anchors.py']},'anchors':anchors,'old_slot4':old,'new_slot4':spec['frames'][4],'timeline_unchanged':True,'files':{str(p.relative_to(P)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in [alb,nrm,mat,P/'anchors.json',P/'x18_laugh.k05b.flip.json']}}
(P/'prep_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'anchors':anchors,'alpha_check':manifest['alpha_check'],'outputs':[str(alb),str(nrm),str(mat)]},indent=2))
