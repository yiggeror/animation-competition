from pathlib import Path
import hashlib,json,urllib.parse
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt
O=Path('collab/reviews/cloud_s12_20261018/F026_index_repair_actual_call01_20261019');I=O.parent/'F026_index_repair_inputs_20261019';S=O.parent/'F022_full_arm_repair_20261019/uniform_map_rejoin_20261019';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();arr=lambda p:np.array(Image.open(p).convert('RGBA'))
assert sha(O/'originals/F026_local_index_call01_raw.png')=='71696e539e0086e9ba95ec81b02f883171b243205924d329790ec1903794112f'
b=arr(I/'reference/LOCKED_F022_STATIC_BASE.png');n=arr(O/'candidate/F026.png');BG=arr(O/'layers/F026_BG_locked022_palm_rear_digits.png');FG=arr(O/'layers/F026_FG_new_drawn_index.png');edit=np.array(Image.open(O/'masks/actual_whole_index_root_edit_domain.png'))>0;protected=np.array(Image.open(O/'masks/protected_existing_palm_other_digits_body_RGBA.png'))>0;th=np.array(Image.open(O/'masks/protected_complete_thumb_native.png'))>0
assert np.array_equal(n[protected],b[protected]);assert np.array_equal(n[th],b[th]);assert np.array_equal(n[~edit],b[~edit]);assert not np.any((BG[:,:,3]>0)&(FG[:,:,3]>0));assert np.array_equal(np.maximum(BG,FG),n)
checks={'complete_thumb_ink_AA_RGBA_exact':True,'protected_existing_palm_other_digits_body_RGBA_exact':True,'all_RGBA_including_alpha0_RGB_outside_index_root_edit_exact':True,'native_BG_FG_mutually_exclusive_RGBA_union_exact':True,'original_native_size_1024x1536':list(n.shape[:2])==[1536,1024]}
for name,p in [('head_neck','head_neck_skin_outline_protection.png'),('near_right_arm','near_right_arm_protection.png')]:
 m=np.array(Image.open(S/'masks'/p))>0
 if m.ndim==3:m=m[:,:,-1]
 assert np.array_equal(n[m],b[m]);checks[name+'_RGBA_exact']=True
checks['whole_jade_wrist_RGBA_exact']=np.array_equal(n[875:960,830:905],b[875:960,830:905]);assert checks['whole_jade_wrist_RGBA_exact']
contacts=json.loads((S/'qa/native_alpha_contacts_registration.json').read_text())['contacts']
for c in contacts:
 m=Image.new('L',(1024,1536));ImageDraw.Draw(m).polygon([tuple(x) for x in c['source_alpha_polygon_native']],fill=255);mm=np.array(m)>0;assert np.array_equal(n[mm],b[mm]);checks[c['name']+'_support_RGBA_exact']=True
propspath=O/'actual_scene/F026_code_props_actual_layer.png';assert propspath.read_bytes()==(S/'actual_scene/F022_code_props_actual_layer.png').read_bytes();assert sha(propspath)=='8aac66e182d3d6109b61a324ed867e4a3f8934e385ab60ac2697dfd8683c1036';checks['actual_frozen_props_PNG_byte_exact']=True
shadow=O/'actual_scene/F026_native_ground_shadows_actual_layer.png';assert shadow.read_bytes()==(S/'actual_scene/F022_native_ground_shadows_actual_layer.png').read_bytes();checks['actual_native_ground_shadows_byte_exact']=True
props=arr(propspath);fg=arr(O/'actual_scene/F026_FG_index_registered_actual_layer.png');yy,xx=np.mgrid[:1080,:1920]
def actual_rod(A,B):
 A=np.array(A);V=np.array(B)-A;u=np.clip(((xx-A[0])*V[0]+(yy-A[1])*V[1])/(V@V),0,1);d=np.hypot(xx-(A[0]+u*V[0]),yy-(A[1]+u*V[1]));return (d<=6)&(props[:,:,3]>0)
upper=actual_rod([934.3124976761612,785.1297395769899],[1497.531490503533,714.6642052957591]);lower=actual_rod([951.2616943917175,798.9063357461391],[1282.1986905564156,773.9467944476169]);dl=distance_transform_edt(~lower);du=distance_transform_edt(~upper);rows=[]
for threshold in [1,8,32,128]:
 m=fg[:,:,3]>=threshold;y,x=np.nonzero(m);idx=int(np.argmin(dl[m]));rows.append({'actual_new_drawn_index_alpha_threshold':threshold,'lower_rod_overlap_pixels':int((m&lower).sum()),'min_air_to_actual_lower_rod_pixel_centres':float(dl[m].min()),'nearest_index_scene_pixel':[int(x[idx]),int(y[idx])],'upper_rod_front_overlap_pixels':int((m&upper).sum()),'min_air_to_upper_rod':float(du[m].min())})
assert all(x['lower_rod_overlap_pixels']==0 and x['upper_rod_front_overlap_pixels']>0 for x in rows)
(O/'qa/actual_rod_contact_and_lower_air.json').write_text(json.dumps({'source':'Actual Chromium cached FG index and actual frozen7px prop raster, not native/PIL reference preview. Pixel-centre distances include full index ink and AA at stated thresholds.','actual_prop_SHA256':sha(propspath),'actual_FG_index_SHA256':sha(O/'actual_scene/F026_FG_index_registered_actual_layer.png'),'measurements':rows,'interpretation':'New actual index crosses the front face of the upper shaft, pad turns below; no lower-shaft pixel overlaps. These measurements support actual visual review and do not certify hidden anatomy.'},indent=2)+'\n')
# Same-scale actual Canvas hand / whole-arm comparisons; do not substitute native diagnostics.
old=Image.open(S/'actual_scene/F022_canvas.png').convert('RGB');new=Image.open(O/'actual_scene/F026_canvas.png').convert('RGB')
def pair(name,crop,scale):
 a=old.crop(crop);b=new.crop(crop);a=a.resize((a.width*scale,a.height*scale),Image.Resampling.NEAREST);b=b.resize(a.size,Image.Resampling.NEAREST);c=Image.new('RGB',(a.width*2,a.height+30),'#202426');c.paste(a,(0,30));c.paste(b,(a.width,30));d=ImageDraw.Draw(c);d.text((8,9),'ACTUAL LOCKED022 CANVAS',fill='white');d.text((a.width+8,9),'ACTUAL REPAIRED026 CANVAS',fill='white');c.save(O/'actual_scene'/name)
pair('022_to_026_actual_hand8x.png',(902,724,1010,821),8);pair('022_to_026_actual_whole_arm3x.png',(730,665,1010,850),3)
# Display true upper/lower occlusion separately, all from the cached actual layers.
back=Image.open(O/'actual_scene/F026_BG_person_registered_actual_layer.png').convert('RGBA');p=Image.open(propspath).convert('RGBA');f=Image.open(O/'actual_scene/F026_FG_index_registered_actual_layer.png').convert('RGBA');stages=[]
for name,ls in [('BG + FROZEN RODS',[back,p]),('BG + RODS + ACTUAL INDEX',[back,p,f])]:
 c=Image.new('RGBA',(1920,1080),'#cbd0d3')
 for im in ls:c.alpha_composite(im)
 x=c.crop((926,750,997,817)).resize((568,536),Image.Resampling.NEAREST).convert('RGB');stages.append((name,x))
board=Image.new('RGB',(1136,566),'#202426');d=ImageDraw.Draw(board)
for k,(name,im) in enumerate(stages):board.paste(im,(568*k,30));d.text((568*k+8,9),name,fill='white')
board.save(O/'actual_scene/upper_front_and_complete_lower_air_actual8x.png')
# Honest preservation of the first same-raw composite and its necessary mask correction.
pre=arr(O/'diagnostics/pre_semantic_protection_v1/candidate/F026.png');oldmask=np.array(Image.open(O/'masks/old022_entire_index_ownership.png'))>0;root=np.array(Image.open(O/'masks/necessary_palm_root_transition.png'))>0;bad=np.any(pre!=b,2)&(b[:,:,3]>0)&~(oldmask|root);assert int(bad.sum())==97
(O/'qa/semantic_protection_initial_readback.json').write_text(json.dumps({'first_composite_existing_source_pixels_outside_old_index_tight_root_changed':97,'first_composite_preserved':'diagnostics/pre_semantic_protection_v1/','fix':'Only tighten actual-source adoption mask to preserve existing original alpha-bearing palm/rear digits outside index/root. One whole-drawing similarity unchanged. No bone/tip transform, repaint or new imagegen.','final_same_check_changed_pixels':int((np.any(n!=b,2)&(b[:,:,3]>0)&~(oldmask|root)).sum()),'actual_full_Canvas_render_runs':2,'runs_reason':['Initial native adoption scope','Necessary restoration of97 protected source pixels'], 'new_imagegen_calls':1},indent=2)+'\n')
E=[json.loads(x) for x in (O/'qa/actual_canvas_network_events.jsonl').read_text().splitlines()];frames=[e for e in E if e['event']=='actual_full_Canvas_render'];assert len(frames)==2 and all(e['frame']==26 for e in frames);assert not [e for e in E if e['event'] in ['pageerror','requestfailed']]
(O/'qa/actual_network_summary.json').write_text(json.dumps({'actual_Canvas_renders':len(frames),'frames':[26,26],'second_render_reason':'Restore97 original protected source pixels by adoption-mask tightening only.','pageerror':0,'requestfailed':0,'non200_responses':[e for e in E if e['event']=='response' and e['status']!=200],'console_errors_actual_locations':[e for e in E if e['event']=='console_error']},indent=2)+'\n')
(O/'qa/native_RGBA_protection_and_layers.json').write_text(json.dumps({'checks':checks,'protected_existing_source_pixels':int(protected.sum()),'thumb_protected_pixels':int(th.sum()),'native_changed_pixel_count':int(np.any(n!=b,2).sum()),'new_actual_source_raw_SHA256':sha(O/'originals/F026_local_index_call01_raw.png'),'unique_locked022_static_SHA256':sha(I/'reference/LOCKED_F022_STATIC_BASE.png'),'candidate_SHA256':sha(O/'candidate/F026.png'),'native_BG_SHA256':sha(O/'layers/F026_BG_locked022_palm_rear_digits.png'),'native_FG_SHA256':sha(O/'layers/F026_FG_new_drawn_index.png'),'actual_Canvas_SHA256':sha(O/'actual_scene/F026_canvas.png')},indent=2)+'\n')
print(json.dumps({'native_candidate_SHA256':sha(O/'candidate/F026.png'),'actual_Canvas_SHA256':sha(O/'actual_scene/F026_canvas.png'),'all_RGBA_protection_checks':checks,'actual_rod_contact':rows,'new_imagegen_calls':1,'originals':1,'actual_Canvas_runs':2,'F030_calls':0},ensure_ascii=False))
