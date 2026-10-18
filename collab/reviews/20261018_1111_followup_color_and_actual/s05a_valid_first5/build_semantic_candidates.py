"""Local-only, source-derived S05a neck/collar masks. No asset/repo writes.
Segmentation uses dark ink as a topology boundary; no saturation/hue classifier.
Color candidates retain source luma, source alpha and all out-of-mask pixels.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from scipy import ndimage as ndi
import json, hashlib, shutil, argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-dir',type=Path,help='Directory of frozen original PNGs by basename. If omitted, use the recorded local source paths.')
parser.add_argument('--resegment',action='store_true',help='Rebuild masks from original ink contours. Default applies the frozen explicit binary masks.')
parser.add_argument('--only',nargs='*',help='Optional named subset, e.g. S05a_F044.')
OPTIONS=parser.parse_args()
ROOT=Path(__file__).resolve().parent
WORK=ROOT.parent
SOURCES={'S05a_F000': 'astra_s05a_draw_20261018_0956/handoff/final/S05a_F000.png', 'S05a_F010': 'astra_s05a_draw_20261018_0956/handoff/final/S05a_F010.png', 'S05a_F014': 'astra_s05a_draw_20261018_0956/handoff/final/S05a_F014.png', 'S05a_F024': 'astra_s05a_draw_20261018_0956/handoff/final/S05a_F024.png', 'S05a_F028': 'astra_s05a_draw_20261018_0956/handoff/final/S05a_F028.png'}

WEIGHTS=np.array([.2126,.7152,.0722])
PARAMS={
 'source':'original unprocessed RGBA, not the contaminated v3/v4 assets',
 'segmentation':'4-connected flood from hand-verified semantic seeds, dark-ink barrier and bounded anatomy ROI; no hue/saturation selection',
 'roi_xyxy_exclusive':[650,700,1030,895],
 'ink_barrier_luma_max':100,
 'alpha_min_exclusive':240,
 'seeds_xy':{'collar_left':[745,815],'collar_right':[930,815],'neck':[840,780]},
 'feather':'inside-only clip((euclidean distance-to-exterior - 0.5) / 1.5, 0, 1)',
 'collar_transform':'RGB = source Rec.709 luma in each channel, blended only by that collar soft mask',
 'neck_transform':'retain source Rec.709 luma; use fixed reference chroma from F023 neck-lit patch, scaling chroma down only to stay in RGB gamut',
 'neck_reference_patch_xyxy':[790,780,880,797],
 'neck_reference_source_sha256':'d654d3ed4b14f8dd9dcf90be128fa155c91d04904619a287b499c83da8844645',
 'neck_reference_note':'Same validated F023 neck chroma as S02a; fixed RGB median is 253,209,171.',
 'scope':'Only independent neck, left collar and right collar. Chin, face, hair, clothing, background and alpha unchanged.',
 'candidate_status':'Local color/mask validation only. Not integrated, not MP4 acceptance.',
}

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for folder in ['source_copies','masks','candidates','overlays','qa']:
 (ROOT/folder).mkdir(parents=True,exist_ok=True)
EXPECTED=json.loads((ROOT/'source_manifest.json').read_text()) if (ROOT/'source_manifest.json').exists() else {}
def source_for(name):
 p=(OPTIONS.source_dir/f'{name}.png') if OPTIONS.source_dir else (WORK/SOURCES[name])
 if name in EXPECTED:
  assert sha(p)==EXPECTED[name]['sha256'],f'Source SHA mismatch: {name}'
 return p
BRIDGES={}
THRESHOLDS={}
def masks_for(im,name):
 rgb=im[:,:,:3].astype(np.float64); y=rgb@WEIGHTS
 yy,xx=np.indices(y.shape); x0,y0,x1,y1=PARAMS['roi_xyxy_exclusive']
 roi=(xx>x0)&(xx<x1)&(yy>y0)&(yy<y1)
 if OPTIONS.resegment:
  threshold=THRESHOLDS.get(name,100)
  barrier=Image.new('L',(im.shape[1],im.shape[0]));bd=ImageDraw.Draw(barrier)
  for line in BRIDGES.get(name,[]):bd.line([tuple(p) for p in line],fill=255,width=2)
  available=(y>threshold)&(im[:,:,3]>240)&roi&~(np.array(barrier)>0)
  labels,num=ndi.label(available)
  regions={key:labels==labels[sy,sx] for key,(sx,sy) in PARAMS['seeds_xy'].items()}
  assert len({labels[sy,sx] for sx,sy in PARAMS['seeds_xy'].values()})==3,'Semantic compartments merged'
 else:
  assert name in EXPECTED,'Frozen-mask application requires verified source_manifest.json'
  regions={key:np.array(Image.open(ROOT/'masks'/f'{name}__{key}__binary.png').convert('L'))>0 for key in PARAMS['seeds_xy']}
  for key,m in regions.items():
   assert m.shape==y.shape
   assert ndi.label(m)[1]==1,'Frozen region is not one component'
   sx,sy=PARAMS['seeds_xy'][key]; assert m[sy,sx]
 assert np.max(np.sum(list(regions.values()),axis=0))==1,'Frozen regions overlap'
 soft={k:np.clip((ndi.distance_transform_edt(m)-.5)/1.5,0,1) for k,m in regions.items()}
 for k,m in regions.items():
  assert 6000<m.sum()<16000,(k,int(m.sum()))
  assert np.all(y[m]>100)
  rows,cols=np.where(m)
  assert rows.min()>y0+1 and rows.max()<y1-1 and cols.min()>x0+1 and cols.max()<x1-1,'Flood escaped ROI'
 assert not (regions['neck']&(regions['collar_left']|regions['collar_right'])).any()
 return regions,soft

def over(im,regions):
 out=im[:,:,:3].copy().astype(float)
 for key,c in [('collar_left',[20,240,40]),('collar_right',[245,30,185]),('neck',[20,170,255])]:
  m=regions[key];out[m]=out[m]*.56+np.array(c)*.44
 return Image.fromarray(np.round(out).astype('uint8'))

def crop(im):
 rgba=im.convert('RGBA'); bg=Image.new('RGBA',rgba.size,(70,70,70,255));bg.alpha_composite(rgba)
 return bg.convert('RGB').crop((650,695,1030,895)).resize((950,500),Image.Resampling.NEAREST)

def sheet(items,path):
 w=950*len(items);can=Image.new('RGB',(w,530),'white');d=ImageDraw.Draw(can)
 for i,(title,im) in enumerate(items):
  d.text((i*950+12,8),title,fill='black');can.paste(crop(im),(i*950,30))
 can.save(path)

anchor=np.array([253.,209.,171.])
anchor_luma=float(anchor@WEIGHTS); chroma=anchor-anchor_luma
PARAMS['neck_reference_median_rgb']=anchor.tolist();PARAMS['neck_reference_chroma']=chroma.tolist()
report={'application_mode':'resegment' if OPTIONS.resegment else 'frozen_explicit_binary_masks','parameters':PARAMS,'assets':[]}
for name,source in SOURCES.items():
 if OPTIONS.only and name not in OPTIONS.only: continue
 src=source_for(name);copy=ROOT/'source_copies'/f'{name}.png'
 if src.resolve()!=copy.resolve(): shutil.copy2(src,copy)
 im=np.array(Image.open(src).convert('RGBA'));rgb=im[:,:,:3].astype(float);y=rgb@WEIGHTS
 regions,soft=masks_for(im,name);out=rgb.copy()
 mask_stats={}
 for key,m in regions.items():
  rows,cols=np.where(m)
  Image.fromarray(m.astype('uint8')*255).save(ROOT/'masks'/f'{name}__{key}__binary.png')
  Image.fromarray(np.round(soft[key]*255).astype('uint8')).save(ROOT/'masks'/f'{name}__{key}__soft.png')
  mask_stats[key]={'pixels':int(m.sum()),'bbox_inclusive':[int(cols.min()),int(rows.min()),int(cols.max()),int(rows.max())]}
  if key.startswith('collar'):
   target=np.repeat(y[:,:,None],3,axis=2)
  else:
   scale=np.ones(y.shape)
   for ch in range(3):
    if chroma[ch]>0:scale=np.minimum(scale,(255-y)/chroma[ch])
    elif chroma[ch]<0:scale=np.minimum(scale,-y/chroma[ch])
   scale=np.clip(scale,0,1)
   target=y[:,:,None]+chroma[None,None,:]*scale[:,:,None]
  w=soft[key][:,:,None];out=out*(1-w)+target*w
 result=im.copy();result[:,:,:3]=np.round(out).clip(0,255).astype('uint8')
 result_im=Image.fromarray(result);target_path=ROOT/'candidates'/f'{name}.png';result_im.save(target_path)
 union=np.logical_or.reduce(list(regions.values()));changed=np.any(im[:,:,:3]!=result[:,:,:3],axis=2)
 assert not (changed&~union).any();assert np.array_equal(im[:,:,3],result[:,:,3]);assert not (changed&(y<=100)).any()
 delta_y=(result[:,:,:3].astype(float)@WEIGHTS)-y
 assert np.max(np.abs(delta_y))<=.501
 overlay=over(im,regions);overlay.save(ROOT/'overlays'/f'{name}__mask_overlay.png')
 sheet([('SOURCE / original pixels',Image.fromarray(im)),('SEMANTIC MASK / green=L magenta=R blue=neck',overlay),('CANDIDATE / source luma retained',result_im)], ROOT/'qa'/f'{name}__source_masks_candidate.png')
 sheet([('SOURCE / original pixels',Image.fromarray(im)),('CANDIDATE / local neck + collar only',result_im)], ROOT/'qa'/f'{name}__before_after.png')
 report['assets'].append({'name':name,'original_path':str(src),'original_sha256':sha(src),'copy_sha256':sha(copy),'candidate_path':str(target_path),'candidate_sha256':sha(target_path),'masks':mask_stats,'segmentation_ink_threshold':THRESHOLDS.get(name,100),'manual_mask_boundary_bridges':BRIDGES.get(name,[]),'checks':{'alpha_changed_pixels':int(np.count_nonzero(im[:,:,3]!=result[:,:,3])),'changed_pixels':int(changed.sum()),'changed_outside_semantic_regions':int((changed&~union).sum()),'shoulder_top_alpha_geometry_unchanged':bool(np.array_equal(im[:,:,3],result[:,:,3])),'changed_dark_ink_pixels_luma_le_100':int((changed&(y<=100)).sum()),'maximum_luma_change_RGB_rounding_only':float(abs(delta_y).max()),'neck_collar_overlap_pixels':int((regions['neck']&(regions['collar_left']|regions['collar_right'])).sum())}})
(ROOT/'semantic_mask_validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
