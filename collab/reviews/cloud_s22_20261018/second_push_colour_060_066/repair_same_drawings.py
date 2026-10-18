#!/usr/bin/env python3
"""Limited semantic forearm colour correction; no drawing or geometry changes."""
from pathlib import Path
import hashlib, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as nd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OLD = ROOT / 'second_push_060_066'
EXPECTED = {'F060': '05fec583e4c5c40daf2a21a04c6a00beb91c5b9e4290a150ed509fc4ec323fc5', 'F066': '96f5cd2cf7138b3513aec96732d1ca64835896b72a735b958d1ebed8d7c35d10'}
for sub in ['candidate', 'masks', 'qa', 'provenance']:
    (HERE/sub).mkdir(exist_ok=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
pixel_sha = lambda a: hashlib.sha256(a.tobytes()).hexdigest()
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)

def smooth(lo, hi, a):
    t = np.clip((a-lo)/(hi-lo), 0, 1)
    return t*t*(3-2*t)

def regions(a):
    """Upper/rear adult and lower/near child, read from real alpha contours."""
    h,w = a.shape[:2]
    semantic = np.zeros((h,w), np.uint8)
    profile = np.zeros((520,4), float)
    for x in range(520):
        labels, count = nd.label(a[:,x,3] >= 128)
        runs = []
        for label in range(1,count+1):
            ys = np.where(labels==label)[0]
            if len(ys)>=15:
                runs.append((int(ys[0]),int(ys[-1])))
        assert len(runs)==2, (x,runs)
        for i,(top,bottom) in enumerate(runs):
            semantic[top:bottom+1,x]=i+1
            profile[x,2*i:2*i+2] = [top,bottom]
    return semantic,profile

def composite(a, c=(115,115,115)):
    im=Image.new('RGBA',(a.shape[1],a.shape[0]),(*c,255))
    im.alpha_composite(Image.fromarray(a))
    return im.convert('RGB')

refpath=ROOT/'contact_band_repair_012_018_024/candidate/F024_contact_fixed.png'
assert sha(refpath)=='97560237598d024a725ab63ee62809d1f5ded5f6fc5aadc1d8a4f158ca85da4a'
reference=np.array(Image.open(refpath).convert('RGBA'))
_, refprofile=regions(reference)
all_checks={}
for name in ['F060','F066']:
    source=OLD/name/'candidate'/f'{name}_mapped.png'
    assert sha(source)==EXPECTED[name]
    a=np.array(Image.open(source).convert('RGBA'))
    h,w=a.shape[:2]
    assert (w,h)==(1672,941)
    semantic,profile=regions(a)
    rgb=a[:,:,:3].astype(float)
    luminance=rgb@np.array([.2126,.7152,.0722])
    # Shadows receive less; middle/light form planes receive the small full dose.
    # Very pale highlights also ease back. This is not a uniform whole-arm shift.
    tone=smooth(192,210,luminance)*(1-.35*smooth(238,250,luminance))
    ink=(a[:,:,3]>0)&((rgb[:,:,0]<=210)|(rgb[:,:,1]<=135)|(rgb[:,:,2]<=100))
    protected_ink=nd.binary_dilation(ink,iterations=2)
    contour_guard=nd.binary_dilation(a[:,:,3]<128,iterations=3)&(a[:,:,3]>0)
    # The native forearm interiors are often alpha253/254. They are not the
    # contour antialias fringe. Preserve every alpha byte; identify the fringe
    # spatially and also protect low-opacity pixels, rather than requiring255.
    protected=protected_ink|contour_guard|(a[:,:,3]<240)
    safe=(semantic>0)&~protected
    edge=smooth(2,9,nd.distance_transform_edt(safe))
    xx=np.arange(w)[None,:]
    along=1-smooth(400,520,xx)
    weights={}
    dose=np.zeros_like(rgb)
    if name=='F060':
        child=(semantic==2)*tone*edge*along
        weights['child_G']=child;weights['child_B']=child
        dose[:,:,1]=1.75*child
        dose[:,:,2]=2.75*child
    else:
        adult=(semantic==1)*tone*edge*along
        child=(semantic==2)*tone*edge*along
        # The child's local green adjustment follows excess against the mother
        # at equivalent native column and relative skin cross-section depth.
        green_excess=np.zeros((h,w),float)
        for x in range(520):
            top,bottom=profile[x,2:4]
            t=np.clip((np.arange(h)-top)/max(1,bottom-top),0,1)
            rt,rb=refprofile[x,2:4]
            refg=np.interp(rt+t*(rb-rt),np.arange(h),reference[:,x,1])
            green_excess[:,x]=rgb[:,x,1]-refg
        local_green=smooth(1.5,3.5,green_excess)
        weights['adult_B']=adult;weights['child_B']=child
        weights['child_G']=child*local_green
        dose[:,:,2]=2.65*adult+3.65*child
        dose[:,:,1]=child*local_green
    delta=-np.rint(dose).astype(np.int16)
    out=a.copy()
    out[:,:,:3]=np.clip(a[:,:,:3].astype(np.int16)+delta,0,255).astype(np.uint8)
    changed=np.any(out!=a,axis=2)
    assert np.array_equal(out[:,:,3],a[:,:,3])
    assert np.array_equal(out[:,520:],a[:,520:])
    assert np.array_equal(out[protected_ink],a[protected_ink])
    assert not changed[protected].any()
    assert not changed[semantic==0].any()
    assert not np.any(delta[:,:,0])
    if name=='F060':
        assert np.array_equal(out[semantic==1],a[semantic==1])
        assert delta[:,:,1].min()>=-2 and delta[:,:,2].min()>=-3
    else:
        assert not np.any(delta[semantic==1,1])
        assert delta[:,:,1].min()>=-1 and delta[:,:,2].min()>=-4
    dest=HERE/'candidate'/f'{name}_colour_fixed.png'
    Image.fromarray(out).save(dest)
    Image.fromarray(semantic*100).save(HERE/'masks'/f'{name}_semantic_arms.png')
    Image.fromarray(protected_ink.astype(np.uint8)*255).save(HERE/'masks'/f'{name}_protected_ink.png')
    Image.fromarray(protected.astype(np.uint8)*255).save(HERE/'masks'/f'{name}_all_protected_pixels.png')
    Image.fromarray(changed.astype(np.uint8)*255).save(HERE/'masks'/f'{name}_actual_changed.png')
    Image.fromarray(np.clip(-delta*60,0,255).astype(np.uint8)).save(HERE/'masks'/f'{name}_actual_subtraction_RGB_x60.png')
    for label,weight in weights.items():
        Image.fromarray(np.rint(weight*65535).astype(np.uint16)).save(HERE/'masks'/f'{name}_{label}_weight16.png')
    np.savez_compressed(HERE/'provenance'/f'{name}_colour_masks.npz',semantic=semantic,profile=profile,tone=tone.astype(np.float32),edge=edge.astype(np.float32),along=along.astype(np.float32),signed_RGB_delta=delta,**{k:v.astype(np.float32) for k,v in weights.items()})
    for suffix,c in [('gray',(115,115,115)),('white',(255,255,255)),('black',(0,0,0))]:
        composite(out,c).save(HERE/'qa'/f'{name}_after_on_{suffix}.png')
    # Same native crop, without scaling: 024 reference / this input / corrected.
    crop=(0,200,600,941);cw,ch=600,741
    board=Image.new('RGB',(cw*3,ch+32),(25,25,25));d=ImageDraw.Draw(board)
    for i,(title,im) in enumerate([('Locked F024 / primary',composite(reference)),(name+' / before',composite(a)),(name+' / after',composite(out))]):
        board.paste(im.crop(crop),(i*cw,32));d.text((i*cw+8,5),title,font=font,fill='white')
    board.save(HERE/'qa'/f'{name}_024_before_after_native.png')
    # A visible mask overlay is QA only. It never enters the corrected drawing.
    overlay=np.array(composite(a)).astype(float)
    strength=np.max(dose,axis=2)/4
    color=np.zeros_like(rgb);color[semantic==1]=[255,120,40];color[semantic==2]=[30,210,255]
    overlay=overlay*(1-strength[:,:,None]*.65)+color*strength[:,:,None]*.65
    Image.fromarray(np.rint(overlay).clip(0,255).astype(np.uint8)).save(HERE/'qa'/f'{name}_mask_overlay.png')
    arms={}
    for label,value in [('adult',1),('child',2)]:
        m=semantic==value
        hist={channel:{str(v):int(n) for v,n in zip(*np.unique(delta[:,:,k][m],return_counts=True))} for k,channel in enumerate(['R','G','B'])}
        corr=float(np.corrcoef(luminance[m],(out[:,:,:3]@np.array([.2126,.7152,.0722]))[m])[0,1])
        arms[label]=dict(changed_pixels=int(changed[m].sum()),signed_RGB_delta_histogram=hist,luminance_correlation=corr)
    proof=dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),candidate=str(dest.relative_to(ROOT)),candidate_sha256=sha(dest),changed_pixels=int(changed.sum()),changed_bounds=[int(np.where(changed)[1].min()),int(np.where(changed)[0].min()),int(np.where(changed)[1].max()),int(np.where(changed)[0].max())],alpha_unchanged=True,alpha_bytes_sha256=pixel_sha(a[:,:,3]),protected_contact_x_ge_520_unchanged=True,protected_contact_bytes_sha256=pixel_sha(a[:,520:]),protected_ink_including_two_pixel_guard_unchanged=True,ink_guard_pixel_count=int(protected_ink.sum()),ink_guard_bytes_sha256=pixel_sha(a[protected_ink]),low_alpha_and_three_pixel_contour_guard_unchanged=True,geometry_and_displacement_unchanged=True,arms=arms,image_generation_calls=0)
    all_checks[name]=proof
    print(name,proof['candidate_sha256'],json.dumps(arms))

def samples(a):
    values=[[],[]]
    for x in range(250,351):
        labels,n=nd.label(a[:,x,3]>=128);bounds=[]
        for k in range(1,n+1):
            ys=np.where(labels==k)[0]
            if len(ys)>20:bounds.append([ys.min(),ys.max()+1])
        for i,b in enumerate([bounds[0],bounds[-1]]):
            y=int(sum(b)/2);values[i].append(a[y-2:y+3,x,:3])
    return {label:np.median(np.concatenate(values[i]),axis=0).tolist() for i,label in enumerate(['adult_median_RGB','child_median_RGB'])}
measure={'F024':samples(reference),'F042':samples(np.array(Image.open(ROOT/'first_push_036_042/F042/candidate/F042_mapped.png').convert('RGBA')))}
for name in ['F060','F066']:
    measure[name+'_before']=samples(np.array(Image.open(OLD/name/'candidate'/f'{name}_mapped.png').convert('RGBA')))
    measure[name+'_after']=samples(np.array(Image.open(HERE/'candidate'/f'{name}_colour_fixed.png').convert('RGBA')))
(HERE/'provenance/correction_checks.json').write_text(json.dumps(all_checks,indent=2)+'\n')
(HERE/'provenance/same_section_measurements.json').write_text(json.dumps(dict(method='Native columns250-350, five pixels around middle of each real alpha cross-section. F024 primary, F042 auxiliary. No forced full median matching beyond authorized small correction.',samples=measure),indent=2)+'\n')
print(json.dumps(measure,indent=2))
