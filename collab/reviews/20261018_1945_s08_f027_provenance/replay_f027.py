#!/usr/bin/env python3
"""Reproduce locked F027 from six preserved inputs. No network or generation.
Requires Pillow12.3.0, NumPy2.3.5, SciPy1.17.0 for recorded exact PNG bytes.
Usage: python replay_f027.py --out NEW_DIRECTORY [--package-root PACKAGE]
"""
from pathlib import Path
from PIL import Image, ImageDraw
import PIL, numpy as np, scipy
from scipy.ndimage import distance_transform_edt, map_coordinates
import argparse, hashlib, io, json, os, platform, sys, zlib
ap=argparse.ArgumentParser();ap.add_argument('--package-root',type=Path,default=Path(__file__).resolve().parent);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
P=args.package_root.resolve();O=args.out.resolve()
if O.exists():raise SystemExit('Refusing to overwrite existing output directory')
manifest_path=P/'REPLAY_DEPENDENCIES.json';manifest=json.loads(manifest_path.read_text())
O.mkdir(parents=True);(O/'masks').mkdir();Image.init()
allowed={manifest_path.resolve(),Path(__file__).resolve()}|{(P/e['path']).resolve() for e in manifest['inputs']}
opened=set();denied=[];runtime_root=Path(sys.base_prefix).resolve()
def audit(event,arguments):
 if event!='open':return
 path,mode,flags=arguments
 if not isinstance(path,(str,bytes,os.PathLike)):return
 p=Path(os.fsdecode(path)).resolve();writing=bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
 if writing:
  if not p.is_relative_to(O):denied.append(str(p));raise PermissionError('Replay write outside new output directory: '+str(p))
 elif p in allowed:opened.add(str(p.relative_to(P)))
 elif not (p.is_relative_to(runtime_root) or p.is_relative_to(O)):
  denied.append(str(p));raise PermissionError('Undeclared replay read: '+str(p))
sys.addaudithook(audit)
inputs={};verified=[]
for e in manifest['inputs']:
 p=P/e['path'];payload=p.read_bytes();sha=hashlib.sha256(payload).hexdigest();assert sha==e['sha256'],e['id'];assert len(payload)==e['bytes'];inputs[e['id']]=Image.open(io.BytesIO(payload));verified.append({'id':e['id'],'path':e['path'],'sha256':sha,'bytes':len(payload)})
a=np.array(inputs['source025']);assert a.shape==(1080,1920,4);H,W=a.shape[:2];yy,xx=np.indices((H,W))
near0=np.array(inputs['near025'])>0;far0=np.array(inputs['far025'])>0;oldnear=near0
pre=a.copy();pre[near0|far0]=0
for mask,dx,dy in [(far0,-8,16),(near0,6,3)]:
 y,x=np.where(mask);pre[y+dy,x+dx]=a[y,x]
w=np.zeros((H,W),bool);w[660:990,900:1320]=np.array(inputs['white3x'].resize((420,330),Image.Resampling.NEAREST))>0
near=np.zeros((H,W),bool);y,x=np.where(near0);near[y+3,x+6]=True
farfull=np.zeros((H,W),bool);y,x=np.where(far0);farfull[y+16,x-8]=True;far=farfull&~w
jade=np.array(inputs['jade'])>0
assert int(w.sum())==15994 and int(far.sum())==18756
assert not (w&near).any() and not (w&jade).any()
raw=inputs['raw'].convert('RGBA');assert raw.size==(1415,1112)
scale=1260/raw.width;tx=0;ty=(990-raw.height*scale)/2+21
reg=raw.transform((1260,990),Image.Transform.AFFINE,(1/scale,0,-tx/scale,0,1/scale,-ty/scale),Image.Resampling.BICUBIC)
patch=reg.resize((420,330),Image.Resampling.LANCZOS);q=np.zeros_like(a);q[660:990,900:1320]=np.array(patch)
o=pre.copy();o[w]=q[w]
ops=[];op_masks={}
def poly(pts):
 m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon(pts,fill=255);return (np.array(m)>0)&w
def save(n,m):
 op_masks[n]=m.copy();Image.fromarray(m.astype('uint8')*255).save(O/'masks'/(n+'.png'));ops.append({'operation':n,'pixels':int(m.sum())})
def shift(b,dx,dy):
 out=np.zeros_like(b);y0=max(0,dy);y1=min(H,H+dy);x0=max(0,dx);x1=min(W,W+dx);out[y0:y1,x0:x1]=b[y0-dy:y1-dy,x0-dx:x1-dx];return out
def paste(m,s,t):
 y,x=np.where(m);v=s[y,x];before=o[y,x].copy();t=t[y,x] if isinstance(t,np.ndarray) else np.full(len(y),t);oa=o[y,x,3]/255.;na=v[:,3]/255.;al=oa*(1-t)+na*t;rgb=o[y,x,:3]*oa[:,None]*(1-t[:,None])+v[:,:3]*na[:,None]*t[:,None];o[y,x,:3]=np.rint(rgb/np.maximum(al[:,None],1e-9)).clip(0,255).astype('uint8');o[y,x,3]=np.rint(al*255).astype('uint8'); edge=(oa<0.96)|(na<0.96);choose=edge&(t>=0.5);keep=edge&~choose;o[y[choose],x[choose]]=v[choose];o[y[keep],x[keep]]=before[keep]
# Source025 sleeve-to-upperarm is already accepted. Keep original pixels, never copy vacated near hand.
m=poly([(940,840),(978,808),(1026,779),(1055,779),(1057,820),(1025,842),(975,860)])&~oldnear;o[m]=a[m];save('RESTORE_LOCKED025_real_upperarm_below_cuff_excluding_old_near_hand',m)
# Genuine proximal wrist skin accompanies the fixed near hand by the same integer translation.
m=poly([(916,844),(940,830),(971,836),(981,910),(950,929),(918,924)]);s=shift(a,6,3);k=np.clip((xx-919)/29,0,1);paste(m,s,k);save('JOIN_original025_near_wrist_collar_rigid_plus6_plus3',m)
# Remove only duplicated raw upper-hand line in the vacated strip, using same raw clean far-forearm skin.
m=poly([(974,831),(1000,815),(1024,809),(1049,815),(1053,825),(1021,834),(987,848)])&~near&~far;y,x=np.where(m);sx=np.rint(1080+(x-974)*0.35).astype(int);sy=np.rint(842+(y-809)*0.30).astype(int);v=q[sy,sx];good=(v[:,3]>245)&(v[:,0]>v[:,1]+20)
# All source clone pixels must be genuine opaque skin; no fill from transparency.
assert good.all(),(int((~good).sum()),(int(x[~good][0]),int(y[~good][0])))
k=np.minimum(distance_transform_edt(m)[y,x]/1.2,1);o[y,x,:3]=np.rint(o[y,x,:3]*(1-k[:,None])+v[:,:3]*k[:,None]).astype('uint8');o[y,x,3]=255;save('CLEAR_duplicate_upper_hand_line_same_call14_clean_skin_texture_patch_only',m)
# Genuine025 proximal skin collar follows the exact hand/jade translation. Only white collar can change.
m=poly([(1090,807),(1129,792),(1164,830),(1140,865),(1111,873),(1090,849)]);s=shift(a,-8,16);k=np.clip((12-distance_transform_edt(~jade))/6,0,1);paste(m,s,k);save('JOIN_original025_far_proximal_skin_collar_rigid_minus8_plus16',m)
# Only duplicated generated match/wood in true air, outside the true near-hand guard.
m=poly([(1047,834),(1070,783),(1095,783),(1095,821),(1060,843)])&~near&~far;o[m]=0;save('CLEAR_duplicate_raw_match_in_air_outside_true_match_guard',m)
# Exact original body/air under proximal near wrist; no new blue slivers.
m=poly([(911,902),(933,900),(949,912),(935,940),(911,940)])&((xx<934)|(yy>920));o[m]=a[m];save('RESTORE_original025_body_air_under_near_wrist',m)
m=poly([(915,853),(940,830),(972,827),(972,854),(938,870)])&~oldnear;o[m]=a[m];save('RESTORE_original025_near_forearm_upper_crossover_no_raw_extra_line',m)
m=poly([(900,845),(947,828),(947,894),(900,920)])&~oldnear;o[m]=a[m];save('RESTORE_true025_proximal_near_forearm_no_extra_native_line',m)
m=poly([(920,910),(943,908),(943,930),(920,940)]);o[m]=a[m];save('CLEAR_shifted_blue_tail_to_original_body_air',m)
# Small interior stray native line, never any protected finger line.
m=poly([(969,837),(982,834),(985,843),(972,850)]);y,x=np.where(m);v=q[y+30,x-35];assert (v[:,3]>245).all();k=np.minimum(distance_transform_edt(m)[y,x]/1.2,1);o[y,x,:3]=np.rint(o[y,x,:3]*(1-k[:,None])+v[:,:3]*k[:,None]).astype('uint8');save('CLEAR_single_stray_raw_interior_line_same_raw_skin_minus35_plus30',m)
# Short22px lower skin-collar transition, from original025 pixels into its+6,+3 rigid hand position.
# Only this tiny connector is resampled; protected hand and whole forearm are never warped.
m=poly([(923,897),(945,897),(945,919),(923,919)]);y,x=np.where(m);t=np.clip((x-923)/22,0,1);t=t*t*(3-2*t);sx=x-6*t;sy=y-3*t
v=np.stack([map_coordinates(a[:,:,c].astype(float),[sy,sx],order=1,mode='constant',cval=0) for c in range(4)],axis=1).round().clip(0,255).astype('uint8');blue=(v[:,2].astype(int)>v[:,0]+15)&(v[:,1]>v[:,0]);v[blue]=a[y[blue],x[blue]];o[y,x]=v;save('STITCH_22px_near_lower_skin_collar_original025_to_plus6_plus3_no_hand_warp',m)
# Guard restoration includes complete distal alpha-zero grip seat but excludes released proximal skin collar.
o[~w]=pre[~w]

v6=O/'S08_F027_semantic_v6_RGBA.png';Image.fromarray(o).save(v6)
v6sha=hashlib.sha256(v6.read_bytes()).hexdigest();assert v6sha==manifest['expected']['semantic_v6_png_sha256'],v6sha
a=o;b=a.copy();hard=near|far
collar=op_masks['JOIN_original025_far_proximal_skin_collar_rigid_minus8_plus16'];oldcollar=collar&(distance_transform_edt(~jade)<12)
roi=Image.new('L',(W,H));ImageDraw.Draw(roi).polygon([(1045,832),(1118,801),(1155,820),(1148,856),(1095,904),(1040,904)],fill=255);roi=np.array(roi)>0
rgb=a[:,:,:3].astype(float);same_raw=np.all(a==q,axis=2);eligible=roi&w&~hard&~oldcollar&same_raw&(a[:,:,3]>245)&(rgb[:,:,0]>225)&(rgb[:,:,1]>155)&(rgb[:,:,0]>rgb[:,:,1]+20)
# Apply the same bounded G1/B4 material offset to both native light and lower-turn skin planes. Preserve their original luminance/color contrast; only fade near protected boundaries.
soft=np.clip(distance_transform_edt(eligible)/3,0,1);soft[~eligible]=0
b[:,:,1]=np.clip(a[:,:,1].astype(int)+np.rint(soft).astype(int),0,255).astype('uint8');b[:,:,2]=np.clip(a[:,:,2].astype(int)+np.rint(4*soft).astype(int),0,255).astype('uint8')
change=np.any(b!=a,2);assert not (change&(~w|hard|oldcollar)).any();assert np.array_equal(b[:,:,[0,3]],a[:,:,[0,3]])
Image.fromarray(np.rint(soft*255).astype('uint8')).save(O/'masks/ONLY_new_call14_far_LIGHT_AND_TURN_skin_SOFT_G1_B4.png');Image.fromarray((change*255).astype('uint8')).save(O/'masks/ACTUAL_changed_RGB_pixels.png');Image.fromarray((oldcollar*255).astype('uint8')).save(O/'masks/PROTECTED_original025_far_skin_collar.png');shadow=roi&(a[:,:,3]>245)&(rgb[:,:,0]>210)&(rgb[:,:,0]>rgb[:,:,1]+20)&(rgb[:,:,1]<=188);Image.fromarray((shadow*255).astype('uint8')).save(O/'masks/DIAGNOSTIC_actual_lower_turn_dark_material.png')
out=O/'S08_F027_grandma_match_box_RGBA.png';Image.fromarray(b).save(out)

actual=hashlib.sha256(out.read_bytes()).hexdigest();rgba=hashlib.sha256(b.tobytes()).hexdigest()
assert actual==manifest['expected']['final_png_sha256'],actual
assert rgba==manifest['expected']['final_decoded_rgba_sha256'],rgba
assert not (np.any(b!=pre,axis=2)&~w).any()
assert np.array_equal(b[near|far],pre[near|far])
report={'status':'PASS_EXACT_FINAL_REPRODUCED','new_generation_calls':0,'input_count':len(verified),'inputs':verified,'file_access_enforced':True,'opened_package_files':sorted(opened),'denied_file_access':denied,'final_png_sha256':actual,'final_decoded_rgba_sha256':rgba,'semantic_v6_png_sha256':v6sha,'final_bytes':out.stat().st_size,'dimensions':[W,H],'registration':{'scale':scale,'tx':tx,'ty':ty},'guards':{'white_pixels':int(w.sum()),'near_pixels':int(near.sum()),'far_actual_hard_pixels':int(far.sum()),'released_far_collar_pixels':int((farfull&w).sum()),'outside_white_changed':int((np.any(b!=pre,2)&~w).sum()),'near_far_guard_changes':int(np.any(b[near|far]!=pre[near|far],1).sum())},'color':{'actual_changed_pixels':int(change.sum()),'G_changed_pixels':int((b[:,:,1]!=a[:,:,1]).sum()),'B_changed_pixels':int((b[:,:,2]!=a[:,:,2]).sum()),'R_changes':int((b[:,:,0]!=a[:,:,0]).sum()),'alpha_changes':int((b[:,:,3]!=a[:,:,3]).sum()),'old025_collar_changes':int((change&oldcollar).sum())},'operations':ops,'environment':{'python':platform.python_version(),'Pillow':PIL.__version__,'NumPy':np.__version__,'SciPy':scipy.__version__,'zlib':zlib.ZLIB_RUNTIME_VERSION},'note':'Exact postprocess replay from preserved raw. Generation itself is not rerun. New-view lower-turn shading is not a claim of every skin pixel being within4 channels of000.'}
(O/'REPLAY_RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
