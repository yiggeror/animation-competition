#!/usr/bin/env python3
"""Independent saved-pixel, source, exposure and contrast checks."""
from pathlib import Path
import hashlib,json,subprocess
import numpy as np
from PIL import Image
from scipy import ndimage as nd
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;REPO=ROOT.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:np.array(Image.open(p).convert('RGBA'))
manifest=json.loads((HERE/'provenance/source_manifest.json').read_text())
for row in manifest['sources']:assert sha(ROOT/row['path'])==row['sha256'],row['path']
checks=json.loads((HERE/'provenance/correction_checks.json').read_text())
samples=json.loads((HERE/'provenance/homologous_dark_samples.json').read_text())['samples']
mother=read(ROOT/'contact_band_repair_012_018_024/candidate/F024_contact_fixed.png')
proof={}
for name in ['F084','F090']:
 before=read(ROOT/checks[name]['source']);after=read(HERE/'candidate'/f'{name}_shadow_fixed.png');delta=after.astype(int)-before.astype(int)
 assert before.shape==after.shape==(941,1672,4)
 assert sha(HERE/'candidate'/f'{name}_shadow_fixed.png')==checks[name]['candidate_sha256']
 assert not np.any(delta[:,:,0]) and not np.any(delta[:,:,3])
 assert np.array_equal(before[:,520:],after[:,520:])
 assert delta.min()>=0 and delta[:,:,1].max()<=(3 if name=='F084' else 5) and delta[:,:,2].max()<=(2 if name=='F084' else 8)
 data=np.load(HERE/'provenance'/f'{name}_shadow_fields.npz')
 assert np.array_equal(data['signed_RGB_delta'],delta[:,:,:3])
 mid=(data['semantic']>0)&(data['depth']<=.60)
 assert np.array_equal(before[mid],after[mid])
 assert not np.any(delta[data['soft_dark_field']<=0])
 ink=(before[:,:,3]>0)&((before[:,:,0]<=210)|(before[:,:,1]<=135)|(before[:,:,2]<=100));ink=nd.binary_dilation(ink,iterations=2)
 contour=nd.binary_dilation(before[:,:,3]<128,iterations=3)&(before[:,:,3]>0)
 assert np.array_equal(before[ink|contour],after[ink|contour])
 # Independently protect actual, fully visible alpha cross-sections through .60.
 for x in range(520):
  ls,n=nd.label(before[:,x,3]>=128);runs=[np.where(ls==k)[0] for k in range(1,n+1)];runs=[r for r in runs if len(r)>=15]
  for r in runs:
   if r[-1]>=940:continue
   end=int(np.floor(r[0]+.60*(r[-1]-r[0])))
   assert np.array_equal(before[r[0]:end+1,x],after[r[0]:end+1,x])
 mapping=json.loads((ROOT/'third_push_084_090'/name/'provenance/mapping_checks.json').read_text());contacts={}
 for label,row in mapping['proof'].items():
  if not isinstance(row,dict):continue
  x0,y0,x1,y1=row['source_box'];dx,dy=row['native_delta'];a=mother[y0:y1,x0:x1];b=after[y0+dy:y1+dy,x0+dx:x1+dx];m=a[:,:,3]>=128;assert np.array_equal(a[m],b[m]);contacts[label]=0
 contrasts={}
 for arm in ['adult','child']:
  assert samples[name+'_before']['0.5'][arm]==samples[name+'_after']['0.5'][arm]
  contrast=np.array(samples[name+'_after']['0.5'][arm])-samples[name+'_after']['0.8'][arm]
  assert contrast[1]>5 and contrast[2]>8
  contrasts[arm]=dict(middle_minus_dark_RGB=contrast.tolist(),dark_before=samples[name+'_before']['0.8'][arm],dark_after=samples[name+'_after']['0.8'][arm])
 proof[name]=dict(sha256=checks[name]['candidate_sha256'],alpha_R_ink_and_contact_exact=True,middle_highlight_pixels_exact=True,limited_dark_field_only=True,unchanged_cumulative_delta=mapping['native_table_delta'],five_contact_regions_max_RGBA_error=contacts,contrasts=contrasts)
clips=[]
for stem in ['S22_084_107_shadow_fixed24','S22_084_107_before_after24']:
 m=json.loads((HERE/'provenance'/(stem+'.json')).read_text());assert sha(HERE/(stem+'.mp4'))==m['sha256'];assert m['actual_decoded_identities']==['F084']*6+['F090']*18
 assert m['frames']==24 and m['fps']==24 and m['duration_seconds']==1 and len(m['ffprobe']['streams'])==1
 for row in m['rows']:
  assert sha(ROOT/row['source_before'])==row['before_sha256']
  assert sha(ROOT/row['source_after'])==row['after_sha256']
 clips.append(dict(name=stem+'.mp4',sha256=m['sha256'],frames=24,actual_decoded_holds_match=True,no_audio=True))
oldsum=subprocess.check_output(['git','show',manifest['source_commit']+':'+(ROOT.relative_to(REPO)/'SHA256SUMS.txt').as_posix()],cwd=REPO,text=True);old_count=0
for line in oldsum.splitlines():
 digest,rel=line.split('  ',1)
 if rel in ['README.md','provenance/source_manifest.json']:continue
 assert sha(ROOT/rel)==digest,rel;old_count+=1
record=dict(source_commit=manifest['source_commit'],drawings=proof,clips=clips,preexisting_review_files_SHA_verified=old_count,old_raws_prompts_candidates_exposure_table_and_plan_unchanged=True,image_generation_calls=0,actual_visual_review='provenance/local_review.json',production_ready=False,Astra_dual_review_pending=True,no_F108=True,no_F114=True)
(HERE/'provenance/verification.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
