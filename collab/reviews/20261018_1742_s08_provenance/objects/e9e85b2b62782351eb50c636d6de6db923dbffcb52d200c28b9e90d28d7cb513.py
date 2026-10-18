#!/usr/bin/env python3
"""Copy native result, apply ONE explicit global similarity, paste only approved local domains.
No image generation. No originals overwritten. Output is a review candidate, never automatic acceptance.
"""
from pathlib import Path
from PIL import Image,ImageChops
import argparse,hashlib,json,math,shutil
import numpy as np
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--raw',type=Path,required=True);ap.add_argument('--scale',type=float);ap.add_argument('--tx',type=float,default=0.);ap.add_argument('--ty',type=float,default=0.);ap.add_argument('--rotation-deg',type=float,default=0.);ap.add_argument('--out-dir',type=Path,default=P.parent/'repair02_result');ap.add_argument('--register-only',action='store_true');args=ap.parse_args()
O=args.out_dir
for sub in ['raw','registered','candidates','qa','geometry']: (O/sub).mkdir(parents=True,exist_ok=True)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save_new(im,path):
 if path.exists():raise RuntimeError(f'Refusing to overwrite existing result: {path}; choose a new --out-dir.')
 im.save(path)
raw_copy=O/'raw/F000_call02_native_raw.png'
if raw_copy.exists():
 if sha(raw_copy)!=sha(args.raw):raise RuntimeError('Existing preserved raw has a different SHA; choose a new --out-dir.')
else:shutil.copy2(args.raw,raw_copy)
raw=Image.open(raw_copy).convert('RGBA');base=Image.open(P/'inputs/F000_registered_props_preplaced_RGBA.png').convert('RGBA')
allow=Image.open(P/'masks/F000_repair02_white_allowed_black_frozen.png').convert('L')
feather=Image.open(P/'masks/F000_repair02_internal_feather.png').convert('L')
prop=Image.open(P/'masks/F000_prop_core_protected.png').convert('L') # legacy filename; content is FULL prop footprint except explicit contact windows
jade=Image.open(P/'masks/F000_jade_bangle_full_protected.png').convert('L')
protected=ImageChops.lighter(prop,jade)
if np.any((np.asarray(allow)>0)&(np.asarray(protected)>0)):raise RuntimeError('Allowed mask overlaps hard-protected props/jade.')
if np.any((np.asarray(feather)>0)&(np.asarray(allow)==0)):raise RuntimeError('Feather leaks outside approved domain.')
if args.scale is None:
 if raw.size!=base.size:
  meta={'status':'REGISTRATION_REQUIRED_NOT_COMPOSITED','raw_size':raw.size,'base_size':base.size,'native_raw_copy':str(raw_copy),'raw_sha256':sha(raw_copy),'instruction':'Inspect actual full output; supply one explicit uniform --scale, --tx, --ty (optional global rotation). Do not anisotropically resize or fit limbs separately.'}
  (O/'geometry/registration_required.json').write_text(json.dumps(meta,indent=2));print(json.dumps(meta,indent=2));raise SystemExit(2)
 s=1.
else:s=args.scale
if not math.isfinite(s) or s<=0:raise RuntimeError('Invalid uniform scale.')
r=math.radians(args.rotation_deg);A=np.array([[math.cos(r),-math.sin(r)],[math.sin(r),math.cos(r)]])*s;t=np.array([args.tx,args.ty]);inv=np.linalg.inv(A);it=-inv@t
coeff=(inv[0,0],inv[0,1],it[0],inv[1,0],inv[1,1],it[1])
registered=raw.copy() if raw.size==base.size and s==1. and args.tx==0. and args.ty==0. and args.rotation_deg==0. else raw.transform(base.size,Image.Transform.AFFINE,coeff,resample=Image.Resampling.BICUBIC)
save_new(registered,O/'registered/F000_call02_registered_RGBA.png')
# ALWAYS inspect these true alpha composites before judging data hidden in zero-alpha RGB.
def previews(im,stem):
 for label,col in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
  c=Image.new('RGBA',im.size,col);c.alpha_composite(im);save_new(c.convert('RGB'),O/'qa'/f'{stem}_{label}.png')
  for name,box,f in [('hands',(930,728,1214,893),4),('eyes',(820,496,961,565),5),('lower',(530,976,990,1080),2),('arm_chains',(590,620,1230,1020),2)]:
   crop=c.crop(box);save_new(crop.resize((crop.width*f,crop.height*f),Image.Resampling.LANCZOS).convert('RGB'),O/'qa'/f'{stem}_{name}_{label}.png')
previews(registered,'call02_registered')
meta={'status':'REGISTERED_DIAGNOSTIC_ONLY' if args.register_only else 'MASKED_REVIEW_CANDIDATE_NOT_ACCEPTED','raw_sha256':sha(raw_copy),'raw_size':raw.size,'global_registration':{'scale':s,'tx':args.tx,'ty':args.ty,'rotation_deg':args.rotation_deg,'matrix':A.tolist(),'no_anisotropic_scale':True,'no_per_limb_warp':True},'preserved_base_sha256':sha(P/'inputs/F000_registered_props_preplaced_RGBA.png'),'mask_sha256':sha(P/'masks/F000_repair02_white_allowed_black_frozen.png'),'feather_sha256':sha(P/'masks/F000_repair02_internal_feather.png'),'note':'Global registration must be checked visually at actual wrists/eyes/contacts before this candidate can be accepted.'}
if not args.register_only:
 # Internal feather only. Restore hard-protected pixels and the complete black domain bit-for-bit.
 candidate=Image.composite(registered,base,feather)
 hard=np.asarray(protected)>0; black=np.asarray(allow)==0;b=np.asarray(base);c=np.array(candidate);c[black|hard]=b[black|hard];candidate=Image.fromarray(c,'RGBA')
 save_new(candidate,O/'candidates/F000_call02_local_composite_RGBA.png');previews(candidate,'call02_candidate')
 change=np.any(c!=b,axis=2)
 checks={'outside_allowed_changed_pixels':int(np.sum(change&black)),'jade_changed_pixels':int(np.sum(change&(np.asarray(jade)>0))),'frozen_props_changed_pixels':int(np.sum(change&(np.asarray(prop)>0))),'inside_allowed_changed_pixels':int(np.sum(change&(~black))),'bottom_row_alpha_gt128_pixels':int(np.sum(c[-1,:,3]>128)),'new_lower_extension_alpha_gt128_pixels':int(np.sum((c[1046:,:,3]>128)&(b[1046:,:,3]<=128))),'central_lower_blouse_min_alpha':int(c[1046:,650:876,3].min()),'lower_rows':[{'y':int(y),'alpha_gt128_pixels':int(np.sum(c[y,:,3]>128))} for y in [1000,1030,1045,1046,1050,1060,1070,1079]],'candidate_alpha_bbox':candidate.getchannel('A').point(lambda v:255 if v>5 else 0).getbbox(),'candidate_sha256':sha(O/'candidates/F000_call02_local_composite_RGBA.png'),'visual_review_required':['Both irises genuinely look down toward match head','Natural connected thumb/index pinch same tail; no pasted oval thumb','Left curved finger pads really support box bottom; thumb root natural','No box/palm gap or substituted prop pixels','Continuous preserved near/far arm chains and wrist seams','No horizontal lower-blouse cut/alpha seam, no duplicate flower/button band','Correct alpha on dark and light backgrounds']}
 if any(checks[k]!=0 for k in ['outside_allowed_changed_pixels','jade_changed_pixels','frozen_props_changed_pixels']):raise RuntimeError('Hard preservation failed.')
 meta['pixel_checks']=checks
 (O/'qa/composite_pixel_checks.json').write_text(json.dumps(checks,indent=2))
(O/'geometry/result_registration_and_composite.json').write_text(json.dumps(meta,indent=2))
files=[f for f in sorted(O.rglob('*')) if f.is_file() and f.name!='SHA256SUMS.txt']
(O/'SHA256SUMS.txt').write_text(''.join(sha(f)+'  '+str(f.relative_to(O))+'\n' for f in files))
print(json.dumps(meta,indent=2))
