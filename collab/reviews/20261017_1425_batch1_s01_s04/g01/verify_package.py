from pathlib import Path
import json,hashlib,subprocess,base64,numpy as np
from PIL import Image
D=Path(__file__).resolve().parent
checks=[]
for name,total in [('g01_beans',288),('g01_beans_s04',192)]:
 p=subprocess.run(['python3','-I','tools/flip_manifest.py',name,str(total)],cwd=D,text=True,capture_output=True)
 (D/'reports'/f'{name}_manifest_stdout.json').write_text(p.stdout);(D/'reports'/f'{name}_manifest_stderr.txt').write_text(p.stderr)
 spec=json.load(open(D/'assets/flips'/f'{name}.flip.json'));holds=[(spec['timelineFrames'][j+1][0] if j+1<len(spec['timelineFrames']) else total)-n for j,(n,i) in enumerate(spec['timelineFrames'])]
 visible_holds=[]
 for j,(n,i) in enumerate(spec['timelineFrames']):
  end=spec['timelineFrames'][j+1][0] if j+1<len(spec['timelineFrames']) else total
  if name.endswith('s04'):n=max(n,63)
  if end>n:visible_holds.append(end-n)
 checks.append({'name':name,'total_frames':total,'manifest_exit_code':p.returncode,'timeline_all_multiples_of_3':all(n%3==0 for n,i in spec['timelineFrames']),'max_visible_single_image_hold_frames':max(visible_holds),'note':'Single-image hold bound is not proof of visible facial change; actual scene review still required.'})
 if p.returncode:raise RuntimeError(p.stderr)
raw=[];alpha=[];files={}
for p in sorted((D/'originals').glob('*.png')):
 key=p.stem.split('_')[-1];a=Image.open(p).convert('RGBA');b=Image.open(D/'assets/chars'/p.name).convert('RGBA');aa=np.asarray(a);bb=np.asarray(b);expected=np.rint(np.clip((aa[:,:,3].astype('float32')-6)/241,0,1)*255).astype('uint8')
 alpha.append({'file':p.name,'original_size':a.size,'processed_size':b.size,'RGB_equal':bool(np.array_equal(aa[:,:,:3],bb[:,:,:3])),'alpha_exact_current_6_247_rule':bool(np.array_equal(expected,bb[:,:,3])),'low_alpha_lt32_to_gt128':int(((aa[:,:,3]<32)&(bb[:,:,3]>128)).sum()),'high_alpha_gt200_to_lt64':int(((aa[:,:,3]>200)&(bb[:,:,3]<64)).sum()),'three_map_sizes_equal':all(Image.open(D/'assets/chars'/f'{p.stem}{s}.png').size==a.size for s in ['', '_n','_m'])})
 if key!='k01':
  r=json.load(open(D/'tool_outputs'/f'{key}.json'));raw.append({'key':key,'raw_tool_image_bytes_equal_original':base64.b64decode(r['image_url'].split(',',1)[1])==p.read_bytes()})
for sub in ['originals','requests','assets/chars','assets/flips','reports']:
 for p in sorted((D/sub).glob('*')):
  if p.is_file():files[str(p.relative_to(D))]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
meta={'author_role':'producer; independent static review by character_audit/root','base_head':'2e96f1fecc1c10499b2c134e71810971ff81d9a2','new_generation_count':7,'attempts_each':1,'source_only':'source/assets/chars/g01_beans.png','source_sha256':'38c2ca5982ee603cd770d94cd0e495b255d1eafb674a5c50e1077aef60f4dd8c','prep_exit_code':0,'manifest_checks':checks,'alpha_and_size_checks':alpha,'raw_tool_roundtrip':raw,'files':files}
(D/'package_verification.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2));print(json.dumps({'manifest_checks':checks,'raw_tool_all_exact':all(x['raw_tool_image_bytes_equal_original'] for x in raw),'all_three_maps_equal':all(x['three_map_sizes_equal'] for x in alpha),'all_alpha_rule_exact':all(x['alpha_exact_current_6_247_rule'] for x in alpha)},ensure_ascii=False,indent=2))
