"""Verify existing six-draw captures only; no browser or movie render."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,numpy as np
R=Path(__file__).resolve().parent;D=R/'actual_six_draws'
report=json.loads((D/'FINITE_CONTEXT_DIAGNOSTIC.json').read_text())
assert report['status']=='COMPLETED_FINITE_DIAGNOSTIC'
assert len(report['draws'])==6 and report['freshContextSequences']==[[0,0],[0,190,0,190]]
for k in ['errors','missing','httpFailures','requestFailures']:assert not report[k]
assert len(report['sourceChecks'])==62 and all(x['pass']for x in report['sourceChecks'])
assert all(sum(x['stage']==s for x in report['sourceChecks'])==31 for s in ['before','after'])
sha=lambda b:hashlib.sha256(b).hexdigest()
images={};files=[];sheet=Image.new('RGB',(1920,1152),(225,228,231));draw=ImageDraw.Draw(sheet)
historical=json.loads((R.parent/'full288_ed1721c1_cloud_20261019/actual_browser_frames/ACTUAL_BROWSER_RENDER_REPORT.json').read_text())
old0=next(x for x in historical['isolation']if x['frame']==0)
for i,row in enumerate(report['draws']):
    p=D/row['png'];j=D/row['jpeg'];im=Image.open(p);assert im.format=='PNG'and im.size==(1920,1080)
    a=np.array(im.convert('RGBA'));assert sha(p.read_bytes())==row['pngSHA256']and sha(j.read_bytes())==row['jpegSHA256']
    assert sha(a.tobytes())==row['rgbaSHA'];images[(row['context'],row['index'])]=a
    m={'context':row['context'],'index':row['index'],'frame':row['frame'],'PNG_SHA256':row['pngSHA256'],'JPEG_SHA256':row['jpegSHA256'],'decoded_PNG_RGBA_SHA256':sha(a.tobytes())}
    if row['frame']==0:m.update({'JPEG_matches_historical_first0':row['jpegSHA256']==old0['expected'],'JPEG_matches_historical_failed_repeat0_hash':row['jpegSHA256']==old0['actual']})
    files.append(m);x=(i%3)*640;y=(i//3)*576;sheet.paste(im.convert('RGB').resize((640,360)),(x,y+30));draw.text((x+8,y+9),f"CTX{row['context']} DRAW{row['index']} F{row['frame']:03d}",fill='black')
sheet=sheet.crop((0,0,1920,966));sheet.save(R/'ACTUAL_SIX_DRAWS_CONTACT.jpg',quality=96,subsampling=0)
checks=[]
for row in report['comparisons']:
    a=images[(row['context'],row['a'])];b=images[(row['context'],row['b'])];x=np.abs(a.astype(np.int16)-b.astype(np.int16));s={'context':row['context'],'a':row['a'],'b':row['b'],'frame':row['frame'],'differing_channels':int((x>0).sum()),'differing_pixels_RGBA':int(np.any(x>0,2).sum()),'max_abs_RGB':int(x[:,:,:3].max()),'max_abs_alpha':int(x[:,:,3].max()),'exact_RGBA':np.array_equal(a,b)}
    assert s['exact_RGBA']==row['exactRGBA']and s['differing_pixels_RGBA']==row['stats']['all']['changedPixelsRGBA']
    heat=np.array(Image.open(D/row['diffPNG']).convert('RGBA'));assert not heat[:,:,:3].any()and np.all(heat[:,:,3]==255)
    s['saved_ABS_RGB_X24_image_is_black_RGB_alpha255']=True;checks.append(s)
assert all(s['exact_RGBA']for s in checks)
ctx=[r[k]for r in report['draws']for k in ['before','after']]
result={'status':'PASS_FINITE_SIX_DRAWS_THREE_RGBA_ZERO_PAIRS_ONLY','script_commit':'ca2deeea5b398d07ae44a8cc1f7944fce179c074','original_script_SHA256':report['scriptSHA256'],'unique_diagnostic_runs':1,'draws':6,'saved_original_PNGs':6,'saved_original_JPEGs':6,'saved_difference_PNGs':3,'independent_PNG_RGBA_checks':checks,'31_source_files_before_after_SHA_pass':True,'source_checks':62,'all12_before_after_ctx_snapshots_identical':all(x==ctx[0]for x in ctx),'all12_ctx_snapshots':ctx,'files':files,'runtime_errors':report['errors'],'required_HTTP_failures':report['httpFailures'],'request_failures':report['requestFailures'],'historical_failed_repeat0_image_reconstructed':False,'historical_long_run_failure_resolved_claimed':False,'full288_rerendered':False,'new_generation':0,'production_source_modified':False,'ready_claimed':False,'limits':report['notes']}
(R/'CLOUD_FINITE_SIX_INDEPENDENT_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items()if k not in ['all12_ctx_snapshots','files']},indent=2))
