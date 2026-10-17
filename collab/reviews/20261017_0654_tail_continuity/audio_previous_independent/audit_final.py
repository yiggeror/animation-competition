from pathlib import Path
import ast, hashlib, json, math, subprocess, time
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from scipy.signal import firwin, resample_poly

OUT = Path('/tmp/laidian-audit-audio-final-tvfan')
BASE = Path('/tmp/laidian-audio-final-tvfan')
CAND = BASE
REPO = Path('/workspace/animation-competition-astra')
FILENAMES = ['film_mix_norm.wav', 'FULL.m4a', 'S15.m4a']
SR = 48000

def run(cmd, **kwargs):
    return subprocess.run(cmd, check=True, capture_output=True, **kwargs)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def db(x):
    return float(20 * math.log10(float(x))) if x else None

def peak_stats(x, sr):
    absx = np.abs(x)
    i = int(np.argmax(absx))
    frame, ch = np.unravel_index(i, x.shape)
    v = float(absx[frame, ch])
    return {'linear': v, 'dbfs': db(v), 'frame': int(frame), 'time_seconds': float(frame / sr),
            'channel_zero_based': int(ch), 'channel': ['L', 'R'][ch],
            'samples_abs_ge_1': int(np.count_nonzero(absx >= 1.0)),
            'samples_gt_minus1p5_dbfs': int(np.count_nonzero(absx > 10**(-1.5/20)))}

def ffmpeg_loudnorm(name):
    cmd = ['ffmpeg', '-hide_banner', '-nostats', '-i', str(CAND/name), '-map', '0:a:0',
           '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-']
    p = run(cmd)
    log = p.stderr.decode()
    (OUT/(name+'.independent_loudnorm.log')).write_text(log)
    data = json.loads(log[log.rindex('{'):log.rindex('}')+1])
    return {k:v for k,v in data.items() if k.startswith('input_')}, cmd

def file_audit(name):
    path = CAND/name
    probe_cmd = ['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)]
    probe = json.loads(run(probe_cmd).stdout)
    (OUT/(name+'.ffprobe.json')).write_text(json.dumps(probe,indent=2))
    decode_cmd = ['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-c:a','pcm_f32le','-f','f32le','-']
    pcm = run(decode_cmd).stdout
    x = np.frombuffer(pcm,dtype='<f4').reshape(-1,2)
    native = peak_stats(x,SR)
    tails = {}
    duration = float(probe['streams'][0]['duration'])
    for a,b in [(max(0,duration-1),duration),(max(0,duration-.1),duration)]:
        y = x[int(a*SR):int(b*SR)]
        tails[f'{a:.1f}-{b:.1f}'] = {'frames':len(y),'rms_dbfs':db(np.sqrt(np.mean(y.astype(np.float64)**2))),
                                  'peak_dbfs':db(np.max(np.abs(y))), 'nonzero_channel_samples':int(np.count_nonzero(y))}
    # Independent bandlimited interpolation: 4x, 513-tap Kaiser-windowed sinc FIR.
    # 256 native context frames each side exceed the FIR's 64-frame half support.
    h = firwin(513,0.25,window=('kaiser',12.0))
    n = len(x); block = 5*SR; context = 256
    overall = None
    fullcount = 0; overlimit = 0
    for start in range(0,n,block):
        end = min(n,start+block)
        lo=max(0,start-context); hi=min(n,end+context)
        up=resample_poly(x[lo:hi].astype(np.float64),4,1,axis=0,window=h)
        up=up[(start-lo)*4:(end-lo)*4]
        s=peak_stats(up,SR*4)
        fullcount += s['samples_abs_ge_1']; overlimit += s['samples_gt_minus1p5_dbfs']
        if overall is None or s['linear'] > overall['linear']:
            overall=dict(s); overall['frame'] += start*4; overall['time_seconds'] += start/SR
    overall['samples_abs_ge_1']=fullcount
    overall['samples_gt_minus1p5_dbfs']=overlimit
    # Separate actual FFmpeg 4x decode with libswresample, kept as an additional cross-check.
    cmd4 = ['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-af','aresample=192000',
            '-c:a','pcm_f32le','-f','f32le','-']
    pcm4 = run(cmd4).stdout
    x4 = np.frombuffer(pcm4,dtype='<f4').reshape(-1,2)
    ff4 = peak_stats(x4,SR*4)
    clipped16 = None
    if name.endswith('.wav'):
        from scipy.io import wavfile
        _, intdata = wavfile.read(path)
        clipped16={'int16_min':int(intdata.min()),'int16_max':int(intdata.max()),
                   'samples_at_negative_rail':int(np.count_nonzero(intdata == -32768)),
                   'samples_at_positive_rail':int(np.count_nonzero(intdata == 32767))}
    return {'file':str(path),'bytes':path.stat().st_size,'sha256':sha(path),
            'probe':probe,'decoded_frames':len(x),'decoded_seconds':len(x)/SR,
            'decoded_float32_sha256':hashlib.sha256(pcm).hexdigest(),
            'native_peak':native,'scipy_4x_peak':overall,'ffmpeg_4x_peak':ff4,
            'ffmpeg_4x_decoded_frames':len(x4),'int16_rails':clipped16,'tail_windows':tails,
            'last_native_sample_by_channel':[float(v) for v in x[-1]],
            'commands':{'decode':decode_cmd,'ffmpeg_4x':cmd4}}

import re
source_manifest=json.loads((BASE/'source_manifest.json').read_text())
source_checks=[]
for item in source_manifest['files']:
    path=BASE/'source'/item['path']
    source_checks.append({'path':item['path'],'sha256':sha(path),'matches_manifest':sha(path)==item['sha256']})
frozen_code=(BASE/'source/audio/build.py').read_text()
current_code=(REPO/'audio/build.py').read_text()
edl=(BASE/'source/js/film/edl.js').read_text()
starts={};durations={};total=0.0
for sid,duration in re.findall(r"\{\s*id:\s*'([^']+)'[^\n]*?dur:\s*([0-9.]+)",edl):
    starts[sid]=total;durations[sid]=float(duration);total+=float(duration)
tree=ast.parse(frozen_code)
names={'CUT','ON','OFF','FAN_ON','TV_ON','TV_OFF'}
nodes=[n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in names for t in n.targets)]
nodes += [n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='fan_speed']
env={'np':np,'T':lambda sid,off=0:starts[sid]+off}
exec(compile(ast.Module(body=nodes,type_ignores=[]),'frozen timing excerpt','exec'),env)
fan_test_times=[env['OFF']-0.001,env['OFF'],env['OFF']+0.1,env['OFF']+5,total,total+0.999]
source={'manifest_sha256':sha(BASE/'source_manifest.json'),'measurement_manifest_sha256':sha(BASE/'measurements.json'),
        'base_commit':source_manifest['base_commit'],'source_file_checks':source_checks,
        'frozen_audio_build_sha256':sha(BASE/'source/audio/build.py'),
        'frozen_edl_sha256':sha(BASE/'source/js/film/edl.js'),
        'current_worktree_AST_equals_frozen':ast.dump(ast.parse(current_code))==ast.dump(tree),
        'edl_shots':len(starts),'edl_seconds':total,'master_expected_seconds':total+1,
        'timing_seconds':{n:env[n] for n in names},'fan_speed_probes':[{'time':t,'speed':float(v)} for t,v in zip(fan_test_times,env['fan_speed'](np.array(fan_test_times)))],
        'tv_babble_gate_end':env['TV_OFF'],'crt_whine_fade_end':env['TV_OFF']+0.3}
records=json.loads((BASE/'measurements.json').read_text())
record_checks=[]
for row in records:
    path=BASE/row['file']; logpath=BASE/(row['id']+'.log');log=logpath.read_text()
    measured=json.loads(log[log.rindex('{'):log.rindex('}')+1])
    duration=float(json.loads(run(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(path)]).stdout)['format']['duration'])
    command=row.get('command')
    record_checks.append({'id':row['id'],'file':row['file'],'sha256':sha(path),'bytes':path.stat().st_size,
       'hash_matches':sha(path)==row['sha256'],'bytes_match':path.stat().st_size==row['bytes'],
       'log_sha256':sha(logpath),'log_names_expected_input':str(path) in log,
       'log_metrics_match':all(measured[k]==row[k] for k in ['input_i','input_tp','input_lra']),
       'measured_log_values':{k:measured[k] for k in ['input_i','input_tp','input_lra']},
       'expected_duration':row['dur'],'actual_duration':duration,'duration_matches':abs(duration-row['dur'])<1e-6,
       'edl_timing_matches':row['id'] not in starts or (row['start']==starts[row['id']] and row['dur']==durations[row['id']]),
       'encode_command_targets_expected_file':command is None or command[-1]==str(path),
       'encode_command_uses_frozen_master':command is None or str(BASE/'film_mix_norm.wav')==command[command.index('-i')+1]})
inventory={'source':source,'records':record_checks,'count':len(record_checks),'all_pass':all(all(r[k] for k in ['hash_matches','bytes_match','log_names_expected_input','log_metrics_match','duration_matches','edl_timing_matches','encode_command_targets_expected_file','encode_command_uses_frozen_master']) for r in record_checks)}
(OUT/'inventory_checks.json').write_text(json.dumps(inventory,indent=2))
print(json.dumps({'inventory_all_pass':inventory['all_pass'],'source':source}),flush=True)
with ThreadPoolExecutor(max_workers=3) as pool:
    jobs={name:pool.submit(ffmpeg_loudnorm,name) for name in FILENAMES}
    files=[]
    for name in FILENAMES:
        print('Measuring '+name,flush=True)
        data=file_audit(name)
        data['loudnorm_input'],data['commands']['loudnorm']=jobs[name].result()
        files.append(data)
        (OUT/'independent_measurements.json').write_text(json.dumps({'source':source,'files':files},indent=2))
        print(json.dumps({k:data[k] for k in ['file','sha256','decoded_seconds','native_peak','scipy_4x_peak','ffmpeg_4x_peak','loudnorm_input','tail_windows']}),flush=True)

