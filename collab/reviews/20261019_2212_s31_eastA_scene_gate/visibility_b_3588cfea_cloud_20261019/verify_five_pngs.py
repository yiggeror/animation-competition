"""Verify already rendered original5 PNGs. No browser or image generation."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,csv,sys
import numpy as np
R=Path(__file__).resolve().parent;out=R/'actual_five_pngs'
runtime=Path(sys.argv[1]);a=json.loads((R/'CLOUD_UNIQUE_RUN_AUTHORITY.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
log=json.loads((out/'VISIBILITY_B_DIAGNOSTIC_ACTUAL.json').read_text())
assert log['runtimeSuccess']and log['status']=='diagnostic_complete_no_visual_gate_claim'
assert not log['requestFailed']and not log['pageErrors']
required=[r for r in log['responses']if r['status']>=400 and not r['url'].endswith('/favicon.ico')];assert not required
names=['B180_FRESH_FIRST.png','B180_FRESH_REPEAT.png','A000_VISIBILITY_CANDIDATE.png','A116_VISIBILITY_CANDIDATE.png','B180_FIRST_AFTER_A.png']
assert sorted(p.name for p in out.glob('*.png'))==sorted(names)
im={};files=[]
for name in names:
    p=out/name;i=Image.open(p);assert i.format=='PNG'and i.size==(960,540)
    im[name]=np.array(i.convert('RGBA'));raw=im[name].tobytes();meta=next(x for x in log['pngs']if x['file']==name)
    assert sha(p)==meta['sha256']and hashlib.sha256(raw).hexdigest()==meta['rgbaSHA256']
    files.append({'file':name,'PNG_SHA256':sha(p),'decoded_RGBA_SHA256':hashlib.sha256(raw).hexdigest(),'dimensions':[960,540],'alpha_range':[int(im[name][:,:,3].min()),int(im[name][:,:,3].max())]})
pairs=[(names[0],names[1]),(names[0],names[4]),(names[1],names[4])];comparisons=[]
for n,(before,after)in enumerate(pairs):
    b=im[before];c=im[after];delta=c.astype(np.int16)-b.astype(np.int16);absolute=np.abs(delta);yx=np.argwhere(np.any(delta!=0,2));record={'name':log['comparisons'][n]['name'],'differingChannels':int((delta!=0).sum()),'differingPixels':len(yx),'maxAbsoluteDifference':int(absolute.max()),'totalAbsoluteDifference':int(absolute.sum()),'exactMatch':not np.any(delta)}
    for k,v in record.items():assert v==log['comparisons'][n][k],(k,v,log['comparisons'][n][k])
    path=R/f'FULL_RGBA_DIFF_{n+1}.csv'
    with path.open('w',newline='')as f:
        w=csv.writer(f,lineterminator="\n");w.writerow(['x','y','before_R','before_G','before_B','before_A','after_R','after_G','after_B','after_A','delta_R','delta_G','delta_B','delta_A'])
        for y,x in yx:w.writerow([int(x),int(y),*b[y,x].tolist(),*c[y,x].tolist(),*delta[y,x].tolist()])
    record['all_changed_pixel_RGBA_rows_file']=path.name;record['all_rows_untruncated']=True;comparisons.append(record)
sources=[]
for p in a['source_files_exact_from_fixed_commit']:
    actual=sha(runtime/p['path']);assert actual==p['SHA256'];sources.append({'path':p['path'],'SHA256':actual,'unchanged':True})
sheet=Image.new('RGB',(1920,1720),(225,228,231));d=ImageDraw.Draw(sheet)
for n,name in enumerate(names):
    x=(n%2)*960;y=(n//2)*570;sheet.paste(Image.fromarray(im[name]).convert('RGB'),(x,y+30));d.text((x+8,y+10),name,fill='black')
sheet.save(R/'ACTUAL_FIVE_PNG_CONTACT.jpg',quality=96,subsampling=0)
crop=Image.new('RGB',(960,600),(225,228,231));d=ImageDraw.Draw(crop)
for n,name in enumerate(names[2:4]):
    # Enlarged only for locating the unmodified actual background; not proof
    # of normal-size readability. Complete original PNG remains authoritative.
    piece=Image.fromarray(im[name]).convert('RGB').crop((720,240,960,530)).resize((480,580))
    crop.paste(piece,(n*480,20));d.text((n*480+8,5),name+' | 2x',fill='black')
crop.save(R/'A000_A116_ACTUAL_EAST_BACKGROUND_2X.jpg',quality=96,subsampling=0)
report={'status':'FIVE_PNG_RUNTIME_PASS_STRICT_ISOLATION_PASS'if comparisons[1]['exactMatch']else'FIVE_PNG_RUNTIME_PASS_STRICT_ISOLATION_HOLD','source_commit':a['source_commit'],'unique_browser_runs':1,'new_generation':0,'PNG_count':5,'PNG_files':files,'complete_independent_RGBA_comparisons':comparisons,'source_files_exact_and_unchanged_after_run':sources,'source_index_runtimeFiles':a['input_index_runtimeFiles_verified'],'required_http_failures':required,'request_failures':log['requestFailed'],'page_errors':log['pageErrors'],'favicon_responses':[x for x in log['responses']if '/favicon.ico'in x['url']],'strictIsolation':log['strictIsolation'],'original_script_exit_code':0 if log['strictIsolation']else 2,'actual_visual_status':'PENDING_ACTUAL_PNG_VIEW','shared_production_modified':False,'whole_shot_rendered':False,'ready_claimed':False}
(R/'CLOUD_FIVE_PNG_VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items()if k not in ['PNG_files','source_files_exact_and_unchanged_after_run']},indent=2))
