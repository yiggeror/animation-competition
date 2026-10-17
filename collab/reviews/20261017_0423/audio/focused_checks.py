import ast, hashlib, json, pathlib, subprocess, sys
sys.dont_write_bytecode = True
import numpy as np
ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '/tmp/laidian-review-snapshot').resolve()
OUT = pathlib.Path('/tmp/laidian-audit-audio')
sys.path.insert(0, str(ROOT / 'audio'))
import inst, score, sfx
src = (ROOT / 'audio/build.py').read_text()
tree = ast.parse(src)
shots = json.loads(subprocess.check_output(['node','-e',"import('./js/film/edl.js').then(m=>console.log(JSON.stringify(m.SHOTS)))"],cwd=ROOT))
start = {}; t = 0.
for shot in shots:
    start[shot['id']] = t
    t += shot['dur']
TOTAL = t + 1
n = inst.ns(TOTAL)
ns = {'np':np, 'N':n, 'secs':inst.secs}
gain_node = next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name == 'gain_curve')
exec(compile(ast.Module(body=[gain_node],type_ignores=[]),str(ROOT/'audio/build.py'),'exec'), ns)
LAMP = start['S08']+1.8
ON = start['S27']; OFF = start['S30']+6
pts=[(0,-26),(start['S08']+4,-18),(start['S09'],-28),(start['S12'],-24),(start['S13'],-30),(ON,-40),(OFF+1,-28),(TOTAL,-28)]
gain = ns['gain_curve'](pts)
local = gain[inst.ns(LAMP):inst.ns(LAMP)+inst.ns(TOTAL-LAMP)]
flame_results=[]
for absolute in [LAMP,start['S08']+4,start['S09'],ON,OFF+1]:
    v = float(local[int(round((absolute-LAMP)*inst.SR))])
    flame_results.append({'absolute_s':absolute, 'local_s':absolute-LAMP,'current_db':float(20*np.log10(v)),'old_db_if_absolute_cues_used_locally':float(np.interp(absolute-LAMP,[p[0] for p in pts],[p[1] for p in pts]))})
del gain,local
scope={}
for module in [inst,sfx,score]: scope.update({k:v for k,v in vars(module).items() if not k.startswith('__')})
N=inst.ns(26)
MUS={k:np.zeros(N,np.float32) for k in ['banhu','dizi','yq','pipa','perc','chip','beat']}
scope.update(MUS=MUS,N=N,D5=587.33,THEME_ROOTS=score.THEME_A_ROOTS,T=lambda sid,off=0:start[sid]-start['S25']+off,sfx=lambda *args,**kw:None,melody=lambda *args,**kw:None)
selected=[x for x in tree.body if 365 <= getattr(x,'lineno',0) <= 462]
exec(compile(ast.Module(body=selected,type_ignores=[]),str(ROOT/'audio/build.py')+':S25-S26-subset','exec'),scope)
chip_raw=MUS['chip']; chip_hp=inst.hp(chip_raw,20).astype(np.float32)
chip_results={}
for key,a,b in [('S25',0,6),('S26',6,24),('tail',24,26)]:
    sl=slice(int(a*inst.SR),int(b*inst.SR))
    chip_results[key]={'raw_mean':float(np.mean(chip_raw[sl],dtype=np.float64)),'after_20Hz_mean':float(np.mean(chip_hp[sl],dtype=np.float64)),'mean_scope':'isolated pre-pan chip track only; not delivered mix'}
# Demonstrate the current export/master topology on an actual synthesized S25/S26 chip signal.
# This is a scoped component probe, not the unavailable delivered stems or whole mix.
music=inst.pan(chip_hp*0.35,0)*0.9
master=np.stack([inst.hp(music[:,0],15),inst.hp(music[:,1],15)],1)
peak=float(np.abs(master).max()); scale=0.89/peak
encode=lambda x:(np.clip(x*scale,-1,1)*32767).astype(np.int16)
stem=encode(music); mixed=encode(master)
delta=(stem.astype(np.int32)-mixed.astype(np.int32))/32767
probe={'scope':'isolated current S25/S26 chip component; music*0.9 then mix-only 15Hz HP, common peak scale, int16 encoding','max_abs_delta_fs':float(np.abs(delta).max()),'delta_rms_dbfs':float(20*np.log10(np.sqrt(np.mean(delta**2)))),'unequal_channel_samples':int(np.count_nonzero(stem!=mixed)),'all_channel_samples':int(stem.size),'stem_clipped_channel_samples':int(np.count_nonzero(np.abs(music*scale)>=1))}
out={'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'build_sha256':hashlib.sha256(src.encode()).hexdigest(),'edl_total_s':t,'audio_buffer_s':TOTAL,'start':start,'LAMP':LAMP,'ON':ON,'OFF':OFF,'flame':flame_results,'chip_dc':chip_results,'stem_master_scoped_probe':probe,'python':sys.version,'numpy':np.__version__}
(OUT/'focused_checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps(out,ensure_ascii=False,indent=2))
