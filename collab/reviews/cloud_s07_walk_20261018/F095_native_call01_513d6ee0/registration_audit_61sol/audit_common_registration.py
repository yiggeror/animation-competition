#!/usr/bin/env python3
"""F095 actual output audit; approved whole inverse only, no independent fitting."""
from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import label,binary_dilation,binary_erosion,binary_fill_holes,distance_transform_edt
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;P=R.parent;F=P/'frozen_input_513d6ee0';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for d in ['masks','candidate','qa','geometry']:(R/d).mkdir(exist_ok=True)
raw=Image.open(P/'originals/F095_call01_RAW.png').convert('RGBA');assert sha(P/'originals/F095_call01_RAW.png')=='0fb9780d5151adb6a7f14d0e226d55f5e14e12fe270a5d9f90389269f79ead3d';actual=raw.resize((540,810),Image.Resampling.LANCZOS);actual.save(R/'F095_whole_native_crop_inverse135over256.png');ar=np.array(raw);rgb=ar[:,:,:3].astype(int);yy,xx=np.indices(ar.shape[:2]);scope=(yy>=500)&(yy<=1375)&(xx>=410)&(xx<=850)
navy=scope&(ar[:,:,3]>=128)&(rgb[:,:,0]<115)&(rgb[:,:,1]<125)&(rgb[:,:,2]<145)&(rgb[:,:,2]-rgb[:,:,0]>5)&(rgb[:,:,1]-rgb[:,:,0]>=0)
lab,_=label(navy);co=np.bincount(lab.ravel());co[0]=0;core=(lab==co.argmax())|(lab==lab[580,699]);edge=binary_dilation(core,iterations=2)&scope&(ar[:,:,3]>0)&(rgb.max(axis=2)<145)&((rgb[:,:,2]>=rgb[:,:,0]+1)|(rgb.max(axis=2)<38));mask=binary_fill_holes(core|edge)&scope&(ar[:,:,3]>0)
# Only original source RGBA, no new opacity or RGB paint. AA2 is diagnostic and reviewed.
pantsraw=np.where(mask[:,:,None],ar,0).astype('uint8');Image.fromarray(mask.astype('uint8')*255).save(R/'masks/RAW_one_complete_navy_pants_source_material.png');Image.fromarray(pantsraw).save(R/'candidate/RAW_original_color_whole_trousers_EXTRACTED_TRIAL.png');pants=Image.new('RGBA',(1672,1080));pants.alpha_composite(Image.fromarray(pantsraw).resize((540,810),Image.Resampling.LANCZOS),(1120,250));pants.save(R/'candidate/F095_whole_native_pants_COMMON_INVERSE_ORIGINAL_COLOR_TRIAL.png')
keys=['far_shoe_ankle_SUPPORT_FIXED','far_complete_arm_jade_hand','body_head_blouse','near_complete_arm','near_shoe_ankle_COLLECTED_LANDED'];layers={k:Image.open(F/'layers'/f'F095_{k}.png').convert('RGBA')for k in keys};flat=Image.new('RGBA',(1672,1080))
for k in keys:flat.alpha_composite(layers[k])
expected=flat.crop((1120,250,1660,1060));expected.save(R/'qa/F095_frozen_five_real_layers_NO_OLD_PANTS.png');trial=Image.new('RGBA',(1672,1080))
for z in [layers[keys[0]],pants]+[layers[k]for k in keys[1:]]:trial.alpha_composite(z)
trial.save(R/'candidate/F095_same_inverse_original_pants_and_source_layers_TRIAL_NOT_APPROVED.png')
def soles(im):
 a=np.array(im);r=a[:,:,:3].astype(int);z=(a[:,:,3]>=128)&(r.min(axis=2)>145)&(np.ptp(r,axis=2)<65);z[:735]=False;z[790:]=False;labs,n=label(z);out=[]
 for k in range(1,n+1):
  ys,xs=np.where(labs==k)
  if len(xs)>100:out.append({'pixels':len(xs),'bbox_local_halfopen':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'centroid_local':[float(xs.mean()),float(ys.mean())]})
 ys,xs=np.where(z);return z,{'all_visible_union_bbox_local_halfopen':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'sole_max_y_local':int(ys.max()),'centroid_union_local':[float(xs.mean()),float(ys.mean())],'components':out}
ez,e=soles(expected);az,a=soles(actual);ed=ez&~binary_erosion(ez);ad=az&~binary_erosion(az);de=distance_transform_edt(~ed);da=distance_transform_edt(~ad)
def blue(im):
 a=np.array(im);r=a[:,:,:3].astype(int);z=(a[:,:,3]>=128)&(r[:,:,2]>110)&(r[:,:,2]-r[:,:,0]>20)&(r[:,:,1]-r[:,:,0]>12);z[320:]=False;l,_=label(z);co=np.bincount(l.ravel());co[0]=0;ys,xs=np.where(l==co.argmax());return {'bbox_local_halfopen':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'centroid_local':[float(xs.mean()),float(ys.mean())]}
# Comparable locked057/062 original interior masks; no RGB correction in this trial.
old=P.parent/'F090_native_call02_65330a56/frozen_input_65330a56/sources/approved_original_source_archive_NOT_REQUEST';palette={};sources=[]
for k in ['F057','F062']:
 ip=old/f'{k}_palette_ARCHIVE_NOT_REQUEST.png';mp=old/f'{k}_actual_pants_material_mask.png';im=np.array(Image.open(ip).convert('RGBA'));ma=np.array(Image.open(mp).convert('L'))>0;z=binary_erosion(ma&(im[:,:,3]>=240),iterations=3);palette[k]={'interior_mean_RGB':im[:,:,:3][z].mean(axis=0).tolist(),'interior_median_RGB':np.median(im[:,:,:3][z],axis=0).tolist(),'pixels':int(z.sum())};sources.extend([{'path':str(ip),'sha256':sha(ip)},{'path':str(mp),'sha256':sha(mp)}])
pa=np.array(pants);pc=binary_erosion(pa[:,:,3]>=240,iterations=3);mean=pa[:,:,:3][pc].mean(axis=0);palette['call01_original']={'interior_mean_RGB':mean.tolist(),'interior_median_RGB':np.median(pa[:,:,:3][pc],axis=0).tolist(),'pixels':int(pc.sum()),'RGB_correction':[0,0,0]}
for k in ['F057','F062']:palette['call01_minus_'+k]=(mean-np.array(palette[k]['interior_mean_RGB'])).tolist()
con={}
for side,key in [('near',keys[-1]),('far',keys[0])]:
 ft=np.array(layers[key]);fr=ft[:,:,:3].astype(int);skin=(ft[:,:,3]>=128)&(fr[:,:,0]>160)&(fr[:,:,0]-fr[:,:,1]>12)&(fr[:,:,1]-fr[:,:,2]>10);con[side]={'pants_over_true_source_skin_alpha128':int((skin&(pa[:,:,3]>=128)).sum()),'skin_within3px_of_pants':int((skin&binary_dilation(pa[:,:,3]>=128,iterations=3)).sum()),'original_whole_source_layer_sha256':sha(F/'layers'/f'F095_{key}.png'),'whole_source_foot_not_redrawn_or_fit':True}
reg={'status':'COMMON_INVERSE_MEASUREMENTS_ONLY_PENDING_ACTUAL_REVIEW','raw_SHA256':sha(P/'originals/F095_call01_RAW.png'),'raw_size':list(raw.size),'whole_inverse':{'s':135/256,'offset':[1120,250],'no_independent_fit':True},'expected_visible_sole_material':e,'actual_visible_sole_material':a,'visible_sole_union_centroid_delta_native':(np.array(a['centroid_union_local'])-e['centroid_union_local']).tolist(),'actual_boundary_to_expected_px':{'median':float(np.median(de[ad])),'p95':float(np.percentile(de[ad],95)),'max':float(de[ad].max())},'expected_boundary_to_actual_px':{'median':float(np.median(da[ed])),'p95':float(np.percentile(da[ed],95)),'max':float(da[ed].max())},'expected_blouse_blue':blue(expected),'actual_blouse_blue':blue(actual),'material_interiors':palette,'connections':con,'occluded_waist_island_actual_source_seed_raw':[699,580],'occluded_waist_island_note':'Small true navy source island between hands is kept at exact same coordinates; its hidden connection is occluded by source hands, never painted or bridged.','raw_pants_source_mask_pixels':int(mask.sum()),'raw_pants_kept_RGBA_changes':int(np.any(pantsraw[mask]!=ar[mask],axis=1).sum()),'scope':'One complete trouser mass may contain both legs; no component splitting, holes cut, ankle bridge or new shoe paint. Background haze and all source-face/body/arm/shoe repaint are excluded.','threshold_limits':'Material-centroid/edge scans are visible projected material diagnostics, not anatomical ankle/hip or bone measurements. Source shoe overlap may merge components; union measured without artificial split.','palette_source_files':sources,'new_image_calls':0,'F100_opened':False}
(R/'geometry/actual_common_registration_and_material.json').write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n')
for tone,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 out=Image.new('RGB',(1620,850),(235,240,245));d=ImageDraw.Draw(out)
 for i,(name,im)in enumerate([('frozen REAL5 only',expected),('actual RAW common inverse',actual),('trial actual PANTS + REAL5',trial.crop((1120,250,1660,1060)))]):
  b=Image.new('RGBA',(540,810),col);b.alpha_composite(im);out.paste(b.convert('RGB'),(i*540,30));d.text((i*540+8,8),name,fill='black')
 out.save(R/f'qa/whole_frozen_actual_trial_{tone}.png');b=Image.new('RGBA',trial.size,col);b.alpha_composite(trial);b.crop((1340,900,1580,1040)).resize((960,560)).save(R/f'qa/source_ankles_and_two_whole_shoes_{tone}.png');b.crop((1350,515,1590,655)).resize((960,560)).save(R/f'qa/waist_complete_native_connections_{tone}.png')
 b=Image.new('RGBA',(540,810),col);b.alpha_composite(actual);ar2=np.array(b);ar2[ed]=[0,210,230,255];ar2[ad]=[255,151,47,255];Image.fromarray(ar2).crop((210,690,485,790)).resize((1100,400),Image.Resampling.NEAREST).save(R/f'qa/visible_soles_expected_CYAN_actual_ORANGE_{tone}.png')
print(json.dumps(reg,ensure_ascii=False,indent=2))
