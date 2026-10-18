#!/usr/bin/env python3
"""Replay from 14 declared inputs, never from the F036 final/intermediate oracle.
Original author scripts execute unchanged except the explicit local font path relocation.
No image generation, network, repository writes, package writes, or original-tree reads.
"""
from pathlib import Path
import argparse,hashlib,json,os,sys,datetime,platform,zlib,io,shutil
sys.dont_write_bytecode=True
import PIL,numpy as np,scipy
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from scipy.ndimage import binary_fill_holes,binary_dilation,label,gaussian_filter,binary_erosion,map_coordinates,distance_transform_edt
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--probe-disallowed-read',type=Path);ap.add_argument('--probe-network',action='store_true');args=ap.parse_args()
PKG=Path(__file__).resolve().parent;OUTPUT=args.out.resolve();M=PKG/'REPLAY_DEPENDENCIES.json';manifest=json.loads(M.read_text())
if OUTPUT.exists():raise SystemExit('Refusing to overwrite an existing output directory')
if OUTPUT==PKG or PKG in OUTPUT.parents:raise SystemExit('Output must be outside the input package')
verified=[];allowed={M,Path(__file__).resolve()};cache={}
for e in manifest['inputs']+manifest['scripts']:
 p=(PKG/e['path']).resolve();assert PKG in p.parents
 b=p.read_bytes();actual=hashlib.sha256(b).hexdigest()
 if actual!=e['sha256']:raise SystemExit('Input hash mismatch: '+e['path'])
 verified.append({'path':e['path'],'sha256':actual,'bytes':len(b)});allowed.add(p);cache[e['path']]=b
OUTPUT.mkdir(parents=True);ROOT=OUTPUT/'tree/astra_s08_first_mother_20261018_1433';ROOT.mkdir(parents=True)
opened=set();denied=[];writes=set();runtime_roots=[Path(sys.base_prefix).resolve(),Path('/usr/lib'),Path('/lib'),Path('/opt')]
def within(p,r):return p==r or r in p.parents
def audit(event,a):
 if event.startswith(('socket.','subprocess.')) or event in {'os.system','os.posix_spawn','os.exec'}:
  denied.append({'event':event});raise PermissionError('Replay disallows network and external processes: '+event)
 if event=='open':
  if isinstance(a[0],int):return
  try:p=Path(os.fsdecode(a[0])).resolve()
  except TypeError:return
  mode=a[1] if isinstance(a[1],str) else '';flags=a[2] if isinstance(a[2],int) else 0
  writing=any(x in mode for x in 'wax+') or bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
  if writing:
   if not within(p,OUTPUT):denied.append({'event':event,'path':str(p),'write':True});raise PermissionError('Replay write outside output: '+str(p))
   writes.add(str(p.relative_to(OUTPUT)))
  else:
   if p not in allowed and not within(p,OUTPUT) and not any(within(p,r) for r in runtime_roots):
    denied.append({'event':event,'path':str(p),'write':False});raise PermissionError('Undeclared replay input: '+str(p))
   opened.add(str(p))
sys.addaudithook(audit)
if args.probe_disallowed_read:
 args.probe_disallowed_read.read_bytes();raise SystemExit('Unexpectedly allowed disallowed read')
if args.probe_network:
 import socket
 socket.socket();raise SystemExit('Unexpectedly allowed socket creation')
for e in manifest['inputs']:
 p=(ROOT/e['target']).resolve()
 if not within(p,OUTPUT):raise ValueError('Escaping input relocation')
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(cache[e['path']])
for s in manifest['scripts']:
 o=ROOT/s['target'];o.parent.mkdir(parents=True,exist_ok=True)
 for name in ['frames','masks','qa','geometry','inputs','candidates','registered']:(o.parent/name).mkdir(exist_ok=True)
font=ROOT/'replay_font/DejaVuSans.ttf';execution=[]
for s in manifest['scripts']:
 code=cache[s['path']].decode();patches=[]
 if s['target']=='F036_input_gate/build_input.py':
  old="'/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'";assert code.count(old)==1;code=code.replace(old,repr(str(font)));patches.append('Font resource path only relocated to declared exact-font input; drawing logic unchanged.')
 argv=[str(ROOT/s['target'])]
 if s['target']=='F036_input_gate/composite_returned_crop.py':
  g=manifest['registration'];argv+=['F036_result_registered_nominal','--raw',str(ROOT/'F036_native_call17/raw/F036_whole_turn_arms_native_raw.png'),'--scale',str(g['scale']),'--tx',str(g['tx']),'--ty',str(g['ty'])]
 sys.argv=argv;ns={'__name__':'__main__','__file__':str(ROOT/s['target'])};exec(compile(code,str(ROOT/s['target']),'exec'),ns)
 for move in s.get('archive_outputs_after',[]):
  src=ROOT/move['source'];dst=ROOT/move['target'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
 execution.append({'source':s['path'],'source_sha256':s['sha256'],'executed_output_path':s['target'],'resource_relocations':patches,'arguments':argv[1:]})
checks=[]
for rel,h in manifest['expected'].items():
 p=ROOT/rel;actual=hashlib.sha256(p.read_bytes()).hexdigest();checks.append({'path':rel,'expected_sha256':h,'actual_sha256':actual,'identical':actual==h})
 if actual!=h:raise AssertionError('Output hash mismatch: '+rel+' expected '+h+' actual '+actual)
shape=ROOT/'F036_same_raw_semantic_v9/candidates/S08_F036_same_raw_semantic_RGBA.png';final=ROOT/'F036_color_final/candidates/S08_F036_whole_turn_same_raw_final_color_RGBA.png'
a=np.array(Image.open(shape));b=np.array(Image.open(final));diff=np.any(a!=b,2);assert not np.any(a[:,:,3]!=b[:,:,3])
report={'status':'PASS_EXACT_CALL17_F036_REPLAY','final_png_sha256':hashlib.sha256(final.read_bytes()).hexdigest(),'input_count':len(manifest['inputs']),'script_count':len(manifest['scripts']),'all_inputs_declared_and_verified':True,'inputs':verified,'execution':execution,'outputs_verified':checks,'new_generation_calls':0,'network_calls':0,'reference_final_or_same_state_intermediates_as_inputs':False,'alpha_changed_pixels_by_color':int(np.count_nonzero(a[:,:,3]!=b[:,:,3])),'denied_attempts':denied,'opened_paths':sorted(opened),'output_files_written':len(writes),'registration_policy':'Exact actual frozen scale/tx/ty applied; original optimizer retained as source evidence, not reoptimized.','visual_scope':'Pixel/source reconstruction only; no new anatomy/color/Canvas visual acceptance inferred.','environment':{'python':sys.version,'platform':platform.platform(),'Pillow':PIL.__version__,'NumPy':np.__version__,'SciPy':scipy.__version__,'zlib':zlib.ZLIB_VERSION,'zlib_runtime':zlib.ZLIB_RUNTIME_VERSION}}
(OUTPUT/'REPLAY_RESULT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'input_count':report['input_count'],'outputs_verified':len(checks),'final_png_sha256':report['final_png_sha256']},indent=2))
