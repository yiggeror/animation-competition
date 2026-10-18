#!/usr/bin/env python3
"""Verify the saved drawings and source chain independently of the repair pass."""
from pathlib import Path
import hashlib,json,subprocess
import numpy as np
from PIL import Image
from scipy import ndimage as nd

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
REPO=ROOT.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:np.array(Image.open(p).convert('RGBA'))
sources=json.loads((HERE/'provenance/source_manifest.json').read_text())
for row in sources['sources']:
    assert sha(ROOT/row['path'])==row['sha256'],row['path']
mother=read(ROOT/'contact_band_repair_012_018_024/candidate/F024_contact_fixed.png')
proofs={}
for name in ['F060','F066']:
    old=ROOT/'second_push_060_066'/name
    before=read(old/'candidate'/f'{name}_mapped.png')
    after=read(HERE/'candidate'/f'{name}_colour_fixed.png')
    delta=after.astype(int)-before.astype(int)
    changed=np.any(delta,axis=2)
    assert before.shape==after.shape==(941,1672,4)
    assert not np.any(delta[:,:,3]) and not np.any(delta[:,:,0])
    assert np.array_equal(before[:,520:],after[:,520:])
    assert np.all(delta[:,:,:3]<=0)
    ink=(before[:,:,3]>0)&((before[:,:,0]<=210)|(before[:,:,1]<=135)|(before[:,:,2]<=100))
    ink=nd.binary_dilation(ink,iterations=2)
    contour=nd.binary_dilation(before[:,:,3]<128,iterations=3)&(before[:,:,3]>0)
    assert np.array_equal(before[ink|contour],after[ink|contour])
    assert not changed[before[:,:,3]<240].any()
    arm_pixels=[[],[]]
    for x in range(520):
        labels,n=nd.label(before[:,x,3]>=128)
        runs=[np.where(labels==k)[0] for k in range(1,n+1)]
        runs=[r for r in runs if len(r)>=15]
        assert len(runs)==2
        for i,r in enumerate(runs):arm_pixels[i].append(delta[r,x])
    adult,child=[np.concatenate(p) for p in arm_pixels]
    if name=='F060':
        assert not np.any(adult)
        assert child[:,1].min()>=-2 and child[:,2].min()>=-3
    else:
        assert not np.any(adult[:,1])
        assert adult[:,2].min()>=-3
        assert child[:,1].min()>=-1 and child[:,2].min()>=-4
    checks=json.loads((old/'provenance/mapping_checks.json').read_text())
    contact={}
    for label,box in checks['proof'].items():
        if not isinstance(box,dict):continue
        x0,y0,x1,y1=box['source_box'];dx,dy=box['native_delta']
        a=mother[y0:y1,x0:x1];b=after[y0+dy:y1+dy,x0+dx:x1+dx]
        visible=a[:,:,3]>=128
        assert np.array_equal(a[visible],b[visible]),label
        contact[label]=dict(compared_visible_pixels=int(visible.sum()),max_RGBA_error=0)
    saved=np.load(HERE/'provenance'/f'{name}_colour_masks.npz')
    assert np.array_equal(saved['signed_RGB_delta'],delta[:,:,:3])
    mapping={'F060':[37,-21],'F066':[49,-28]}[name]
    assert checks['native_table_delta']==mapping
    proofs[name]=dict(sha256=sha(HERE/'candidate'/f'{name}_colour_fixed.png'),alpha_exact=True,ink_and_contour_guards_RGBA_exact=True,x_ge_520_RGBA_exact=True,adult_F060_exact=(not np.any(adult) if name=='F060' else None),unchanged_native_cumulative_delta=mapping,contact=contact,changed_pixels=int(changed.sum()),last_changed_x=int(np.where(changed)[1].max()))

clips=[]
for stem,frames in [('S22_060_083_colour24',24),('S22_000_083_colour84',84)]:
    record=json.loads((HERE/'provenance'/(stem+'.json')).read_text())
    assert sha(HERE/(stem+'.mp4'))==record['sha256']
    expected=[row['id'] for row in record['rows'] for _ in range(row['hold'])]
    assert record['all_decoded_frame_identities']==expected
    assert len(expected)==frames and record['all_hold_boundaries_match']
    assert record['fps']==24 and record['duration_seconds']==frames/24
    assert len(record['ffprobe']['streams'])==1
    for row in record['rows']:assert sha(ROOT/row['source'])==row['sha256']
    clips.append(dict(name=stem+'.mp4',sha256=record['sha256'],frames=frames,decoded_holds_exact=True,no_audio=True))

relative_root=ROOT.relative_to(REPO).as_posix()
old_sum=subprocess.check_output(['git','show',sources['source_commit']+':'+relative_root+'/SHA256SUMS.txt'],cwd=REPO,text=True)
allow={'README.md','provenance/source_manifest.json'}
checked=0
for line in old_sum.splitlines():
    digest,rel=line.split('  ',1)
    if rel in allow:continue
    assert sha(ROOT/rel)==digest,rel
    checked+=1
record=dict(drawings=proofs,clips=clips,preexisting_review_files_SHA_verified=checked,original_raws_prompts_and_old_candidates_unchanged=True,alpha_geometry_ink_contact_and_displacement_unchanged=True,image_generation_calls=0,production_ready=False,Astra_colour_review_pending=True,no_F084=True)
(HERE/'provenance/verification.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
