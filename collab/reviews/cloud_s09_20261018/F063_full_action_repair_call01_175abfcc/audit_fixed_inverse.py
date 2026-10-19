#!/usr/bin/env python3
"""Literal approved77/128 inverse and actual material diagnostics;NO adoption."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation,binary_fill_holes,label,distance_transform_edt
import numpy as np,json,hashlib,math
R=Path(__file__).resolve().parent;F=R/'frozen_input_175abfcc';rawpath=R/'originals/F063_full_action_call01_RAW.png';im=Image.open(rawpath).convert('RGBA');a=np.asarray(im);rgb=a[:,:,:3].astype(int);H,W=a.shape[:2];s=77/128;off=np.array([550.,0.]);size=(1672,941);(R/'geometry').mkdir(exist_ok=True);(R/'masks').mkdir(exist_ok=True);(R/'diagnostic').mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert(W,H)==(1145,1374)
# No silent normalizing to1280x1536. Literal inverse only.
actual=im.transform(size,Image.Transform.AFFINE,(1/s,0,-550/s,0,1/s,0),Image.Resampling.BICUBIC,fillcolor=0);actual.save(R/'diagnostic/F063_LITERAL_77over128_plus550_0_HOLD_NOT_ADOPTED.png')
G=json.loads((F/'geometry/input_gate_checks.json').read_text());T=np.array([438.,922.]);L=np.array([1007.,832.]);u=(L-T)/np.linalg.norm(L-T);n=np.array([-u[1],u[0]]);yy,xx=np.indices((H,W));normal=(xx-T[0])*n[0]+(yy-T[1])*n[1]
# True visible material extents in manual sourceROIs, no invented hidden contour.
def main_component(z,seed):
 labs,_=label(z);k=int(labs[seed[1],seed[0]]);assert k>0,seed;return labs==k
neutral=(np.ptp(rgb,axis=2)<65)&(a[:,:,3]>=128)
sections=[]
for name,box,seed in [('tailcap_visible',[420,870,510,973],[447,920]),('red_tube_clear_band',[710,800,790,970],[750,880]),('lampcap_visible',[890,725,1060,945],[995,800])]:
 x0,y0,x1,y1=box;roi=(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1)
 cond=neutral if name!='red_tube_clear_band'else((rgb[:,:,0]-rgb[:,:,1]>45)&(rgb[:,:,0]-rgb[:,:,2]>45)&(rgb[:,:,0]>120)&(a[:,:,3]>=128))
 z=main_component(roi&cond,seed);ids=np.argwhere(z);lo=ids[np.argmin(normal[z])];hi=ids[np.argmax(normal[z])];width=float(normal[z].max()-normal[z].min());sections.append({'name':name,'source_ROI_halfopen':box,'seed':seed,'source_pixels':int(z.sum()),'raw_transverse_material_extent':width,'literal_inverse_native_extent':width*s,'normal_extreme_source_points':[[int(lo[1]),int(lo[0])],[int(hi[1]),int(hi[0])]],'manual_edge_ownership_uncertainty_raw_px':4,'limit':'2D visible material band under manual ownership;not physicalcaliper or hidden extent reconstruction.'})
 Image.fromarray(z.astype('uint8')*255).save(R/'masks'/f'RAW_{name}_actual_visible_material_DIAGNOSTIC.png')
def poly(ps):
 z=Image.new('L',(W,H));ImageDraw.Draw(z).polygon(ps,fill=255);return np.array(z)>0
propdom=poly([(422,885),(443,871),(495,859),(545,849),(628,831),(847,786),(906,746),(990,727),(1021,733),(1043,761),(1061,830),(1057,896),(1040,930),(994,942),(934,936),(874,927),(845,921),(681,960),(627,980),(504,957),(464,968),(432,976),(421,932)])
red=(rgb[:,:,0]-rgb[:,:,1]>45)&(rgb[:,:,0]-rgb[:,:,2]>45)&(rgb[:,:,0]>110);metal=np.ptp(rgb,axis=2)<65;ink=rgb.max(axis=2)<125;prop=propdom&(a[:,:,3]>0)&(red|metal|ink);labs,_=label(prop);counts=np.bincount(labs.ravel());counts[0]=0;keep=np.where(counts>100)[0];prop=np.isin(labs,keep)
handdom=poly([(752,992),(824,950),(904,943),(1030,938),(1040,965),(992,1048),(864,1060),(802,1055),(750,1040)])
skin=(rgb[:,:,0]>155)&(rgb[:,:,1]>90)&(rgb[:,:,0]-rgb[:,:,1]>12)&(rgb[:,:,0]-rgb[:,:,1]<125)&(rgb[:,:,1]-rgb[:,:,2]>10)&(rgb[:,:,1]-rgb[:,:,2]<100)&(a[:,:,3]>0);hand=main_component(handdom&skin,[900,1000]);hand|=binary_dilation(hand,iterations=3)&handdom&(a[:,:,3]>0)&ink;hand|=binary_dilation(hand,iterations=4)&handdom&(a[:,:,3]>0)&(a[:,:,3]<128)
for name,z in [('RAW_visible_whole_prop_actual_material_DIAGNOSTIC',prop),('RAW_far_complete_palm_actual_material_DIAGNOSTIC',hand)]:Image.fromarray(z.astype('uint8')*255).save(R/'masks'/f'{name}.png')
gaps={};pair=None
for alpha in [1,16,128]:
 pm=prop&(a[:,:,3]>=alpha);hm=hand&(a[:,:,3]>=alpha);dist,ix=distance_transform_edt(~pm,return_indices=True);ys,xs=np.where(hm);k=np.argmin(dist[hm]);hp=np.array([xs[k],ys[k]]);pp=np.array([ix[1,hp[1],hp[0]],ix[0,hp[1],hp[0]]]);gap=float(dist[hm].min());gaps[str(alpha)]={'raw_material_gap':gap,'literal_inverse_native_gap':gap*s,'overlap_pixels':int((pm&hm).sum()),'closest_hand_source_pixel':hp.tolist(),'closest_prop_source_pixel':pp.tolist()}
 if alpha==128:pair=(hp,pp)
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',16)
target=Image.open(F/'reference/A_F063_full_target_NOT_ART_native.png').convert('RGBA')
for tone,color in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 sheet=Image.new('RGB',(1540,960),(235,241,246));d=ImageDraw.Draw(sheet)
 for j,(name,z)in enumerate([('frozen target / NOT_ART',target),('RAW literal77/128 / HOLD',actual)]):
  bg=Image.new('RGBA',size,color);bg.alpha_composite(z);sheet.paste(bg.crop((550,0,1320,924)).convert('RGB'),(j*770,30));d.text((j*770+8,5),name,font=font,fill='#254d61')
 sheet.save(R/f'qa/frozen_target_vs_LITERAL_inverse_{tone}_HOLD.png');bg=Image.new('RGBA',im.size,color);bg.alpha_composite(im);d=ImageDraw.Draw(bg);hp,pp=pair;d.line((tuple(hp),tuple(pp)),fill='#00bba5',width=2);d.text((760,700),f"realgap {gaps['128']['raw_material_gap']:.2f}raw = {gaps['128']['literal_inverse_native_gap']:.2f}native",font=font,fill='#00a68a');bg.crop((735,720,1080,1080)).resize((1035,1080),Image.Resampling.NEAREST).save(R/f'qa/actual_far_palm_to_prop_contour_gap_{tone}_3x.png')
# Dimension-only alternate normalization is not applied to any image or adopted.
# Ratio tests are independent of choosing a uniform output-resolution factor.
oldtail=80.06620619459949;oldaxis=376.00132978488244;tail=sections[0]['raw_transverse_material_extent'];rawaxis=float(np.linalg.norm(L-T));ratio=(tail/rawaxis)/(oldtail/oldaxis)-1
checks={'status':'HOLD_UNEXPECTED_OUTPUT_CANVAS_AND_PROP_RATIO_PENDING_ASTRA','raw_SHA256':sha(rawpath),'raw_size':[W,H],'frozen_tool_size':[1280,1536],'resolution_ratio_uniform':W/1280,'literal_approved_inverse':{'s':s,'offset':[550,0],'applied_to_full_raw_once':True,'no_resolution_normalization_adopted':True,'no_partfit':True},'manual_source_axis_points':{'T_tail_endplane_center':T.tolist(),'L_lamp_endplane_center':L.tolist(),'T_uncertainty_raw_px':7,'L_uncertainty_raw_px':7},'source_axis_raw':rawaxis,'literal_axis_native':rawaxis*s,'frozen_axis_native':oldaxis,'literal_T_native':(T*s+off).tolist(),'literal_L_native':(L*s+off).tolist(),'frozen_T_native':G['frozen_T'],'frozen_L_native':G['frozen_L'],'visible_section_material_measurements':sections,'scale_independent_tail_to_axis_ratio_delta_vs_original044':ratio,'whole_canvas_resolution_normalization_if_Astra_later_authorizes_DIAGNOSTIC_NUMBERS_ONLY':{'not_applied_to_images':True,'uniform_factor_1280over1145':1280/W,'implied_net_native_per_raw_pixel':770/W,'axis_native_if_normalized':rawaxis*770/W,'tail_extent_native_if_normalized':tail*770/W,'note':'Uniform normalization could address dimensions but cannot change tail/axis proportion;not authorization or adoption.'},'actual_whole_prop_to_far_palm_outline_gaps':gaps,'source_mask_limits':'Manual material domains with sourceRGBA preserved;shared edge ownership±4raw;nearest gap near real lamp lower rim/fingertips,not inferredpoint gap.','old_head_ruffle_skirt_guard_restoration_performed':False,'production_candidate_created':False,'observations':['Whole output shrunk uniformly in canvas dimensions to1145x1374;literal requested inverse does not hit frozenT/L.','Actual cap/barrel proportions must pass independently of canvas resolution;visible tail/axis ratio remains smaller than original044 reference.','Actual new grasp sits further toward the tail than technicalG;shaftG occluded so do not fabricate precise bone or interior hand center.','Far yellow sleeve is large and low;own-sleeve/upper-arm continuity under nearforearm needs Astra actual topology review,not automaticacceptance from continuouspixels.','OFF mechanical slider is not clearly visible in returned grip/shaft;do not claim usable switch interaction.'],'new_request_count':1,'original_count':1,'retry_count':0,'F069_unopened':True}
(R/'geometry/fixed_inverse_actual_shape_and_gap_HOLD.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:checks[k]for k in ['source_axis_raw','literal_axis_native','literal_T_native','literal_L_native','visible_section_material_measurements','scale_independent_tail_to_axis_ratio_delta_vs_original044','actual_whole_prop_to_far_palm_outline_gaps']},indent=2))
