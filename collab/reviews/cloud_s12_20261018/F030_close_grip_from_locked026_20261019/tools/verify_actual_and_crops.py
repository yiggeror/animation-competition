from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt
O=Path('collab/reviews/cloud_s12_20261018/F030_close_grip_from_locked026_20261019');M=O.parent/'F026_index_repair_actual_call01_20261019';S=O.parent/'F022_full_arm_repair_20261019/uniform_map_rejoin_20261019';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();arr=lambda p:np.array(Image.open(p).convert('RGBA'))
b=arr(O/'reference/LOCKED_ACTUAL_F026_UNIQUE_MOTHER.png');n=arr(O/'candidate/F030.png');BG=arr(O/'layers/F030_BG_static026_palm.png');FG=arr(O/'layers/F030_FG_actual_three_and_fixed_index.png');edit=np.array(Image.open(O/'masks/actual_three_digit_root_edit_domain.png'))>0;core=np.array(Image.open(O/'masks/fixed_thumb_index_contact_core.png'))>0
assert np.array_equal(n[~edit],b[~edit]);assert np.array_equal(n[core],b[core]);assert not np.any((BG[:,:,3]>0)&(FG[:,:,3]>0));assert np.array_equal(np.maximum(BG,FG),n);assert sha(O/'reference/LOCKED_ACTUAL_F026_UNIQUE_MOTHER.png')=='34515fa0f42af3c360004b7530142d7c077b9ba344da7eccd0dad26042eb4934'
checks={'outside_actual3_root_edit_all_RGBA_including_hidden_alpha0_RGB_exact':True,'source026_png_immutable_SHA_exact':True,'fixed_thumb_index_body_contact_core_RGBA_exact':True,'native_BG_FG_mutually_exclusive_union_RGBA_exact':True}
for name,p in [('head_neck','head_neck_skin_outline_protection.png'),('near_right_arm','near_right_arm_protection.png')]:
 q=np.array(Image.open(S/'masks'/p))>0
 if q.ndim==3:q=q[:,:,-1]
 assert np.array_equal(n[q],b[q]);checks[name+'_RGBA_exact']=True
assert np.array_equal(n[875:960,830:905],b[875:960,830:905]);checks['whole_jade_wrist_RGBA_exact']=True
for c in json.loads((S/'qa/native_alpha_contacts_registration.json').read_text())['contacts']:
 q=Image.new('L',(1024,1536));ImageDraw.Draw(q).polygon([tuple(p) for p in c['source_alpha_polygon_native']],fill=255);q=np.array(q)>0;assert np.array_equal(n[q],b[q]);checks[c['name']+'_support_RGBA_exact']=True
propspath=O/'actual_scene/F030_code_props_actual_layer.png';assert propspath.read_bytes()==(M/'actual_scene/F026_code_props_actual_layer.png').read_bytes();assert (O/'actual_scene/F030_native_ground_shadows_actual_layer.png').read_bytes()==(M/'actual_scene/F026_native_ground_shadows_actual_layer.png').read_bytes();checks['actual_frozen_props_and_ground_shadows_byte_exact']=True
props=arr(propspath);fg=arr(O/'actual_scene/F030_FG_index_registered_actual_layer.png');yy,xx=np.mgrid[:1080,:1920]
def rod(A,B):
 A=np.array(A);V=np.array(B)-A;u=np.clip(((xx-A[0])*V[0]+(yy-A[1])*V[1])/(V@V),0,1);d=np.hypot(xx-(A[0]+u*V[0]),yy-(A[1]+u*V[1]));return(d<=6)&(props[:,:,3]>0)
up=rod([934.3124976761612,785.1297395769899],[1497.531490503533,714.6642052957591]);lo=rod([951.2616943917175,798.9063357461391],[1282.1986905564156,773.9467944476169]);dl=distance_transform_edt(~lo);ly,lx=np.nonzero(lo);rows=[]
for th in [1,8,32,128]:
 m=fg[:,:,3]>=th;fy,fx=np.nonzero(m);dx=np.maximum(np.abs(fx[:,None]-lx[None,:])-1,0);dy=np.maximum(np.abs(fy[:,None]-ly[None,:])-1,0);square=float(np.sqrt((dx*dx+dy*dy).min()));centre=float(dl[m].min());rows.append({'actual_FG_alpha_threshold':th,'lower_rod_overlap_pixels':int((m&lo).sum()),'lower_air_pixel_centre_distance':centre,'lower_air_unit_pixel_square_boundary_distance':square,'upper_rod_front_overlap_pixels':int((m&up).sum())})
assert all(r['lower_rod_overlap_pixels']==0 and r['upper_rod_front_overlap_pixels']>0 for r in rows)
# Fixed contact remains at source geometry; record exact visible actual pad cores and distinguish AA occlusion.
th=np.array(Image.open(M/'masks/protected_complete_thumb_native.png'))>0;ix=arr(M/'layers/F026_FG_new_drawn_index.png')[:,:,3]>0;ny,nx=np.mgrid[:1536,:1024];thumbtouch=th&(nx>=973)&(ny>=947);indexcontact=ix&(nx>=979)&(ny>=950)&(ny<=963);checks['actual_thumb_first_touch_patch_all_RGBA_exact']=np.array_equal(n[thumbtouch],b[thumbtouch]);checks['actual_index_upper_shaft_contact_patch_all_RGBA_exact']=np.array_equal(n[indexcontact],b[indexcontact]);assert checks['actual_thumb_first_touch_patch_all_RGBA_exact'] and checks['actual_index_upper_shaft_contact_patch_all_RGBA_exact']
(O/'qa/actual_contact_and_lower_air.json').write_text(json.dumps({'source':'Actual Chromium FG layer and frozen actual7scene-px props, not input projection.','measurements':rows,'distance_definitions':{'centre':'Euclidean distance between occupied pixel centres.','square_boundary':'Exact minimum Euclidean separation of closed1x1pixel squares: sqrt(max(abs(dx)-1,0)^2+max(abs(dy)-1,0)^2).'},'F026_accepted_baseline':{'pixel_centres':3,'pixel_square_boundaries':2,'do_not_relabel_centre_as_boundary':True},'no_rod_movement':True},indent=2)+'\n')
old=Image.open(M/'actual_scene/F026_canvas.png').convert('RGB');new=Image.open(O/'actual_scene/F030_canvas.png').convert('RGB')
def pair(name,crop,scale):
 a=old.crop(crop);b=new.crop(crop);a=a.resize((a.width*scale,a.height*scale),Image.Resampling.NEAREST);b=b.resize(a.size,Image.Resampling.NEAREST);z=Image.new('RGB',(a.width*2,a.height+30),'#202426');z.paste(a,(0,30));z.paste(b,(a.width,30));d=ImageDraw.Draw(z);d.text((8,9),'ACTUAL LOCKED026 CANVAS',fill='white');d.text((a.width+8,9),'ACTUAL030 CLOSED THREE CANVAS',fill='white');z.save(O/'actual_scene'/name)
pair('026_to030_actual_hand8x.png',(900,718,1010,822),8);pair('026_to030_actual_whole_arm3x.png',(730,665,1010,850),3)
back=Image.open(O/'actual_scene/F030_BG_person_registered_actual_layer.png').convert('RGBA');p=Image.open(propspath).convert('RGBA');f=Image.open(O/'actual_scene/F030_FG_index_registered_actual_layer.png').convert('RGBA');board=Image.new('RGB',(1136,566),'#202426');d=ImageDraw.Draw(board)
for k,(name,ims) in enumerate([('BG + TRUE UPPER/LOWER SHAFTS',[back,p]),('BG + RODS + ACTUAL FRONT FINGERS',[back,p,f])]):
 c=Image.new('RGBA',(1920,1080),'#cbd0d3')
 for im in ims:c.alpha_composite(im)
 c=c.crop((926,750,997,817)).resize((568,536),Image.Resampling.NEAREST).convert('RGB');board.paste(c,(568*k,30));d.text((568*k+8,9),name,fill='white')
board.save(O/'actual_scene/upper_entry_exit_front_and_complete_lower_air8x.png')
E=[json.loads(x) for x in(O/'qa/actual_canvas_network_events.jsonl').read_text().splitlines()];renders=[e for e in E if e['event']=='actual_full_Canvas_render'];assert len(renders)==1 and renders[0]['frame']==30;assert not[e for e in E if e['event'] in ['pageerror','requestfailed']]
(O/'qa/actual_network_summary.json').write_text(json.dumps({'actual_Canvas_renders':1,'frame':30,'pageerror':0,'requestfailed':0,'non200_responses':[e for e in E if e['event']=='response' and e['status']!=200],'console_errors_actual_locations':[e for e in E if e['event']=='console_error']},indent=2)+'\n')
r={'status':'ACTUAL030_SCOPE_AND_CONTACT_CHECKS_PASS_AUTHOR_VISUAL_REVIEW_NEXT','checks':checks,'actual_contact':rows,'native_SHA256':sha(O/'candidate/F030.png'),'Canvas_SHA256':sha(O/'actual_scene/F030_canvas.png'),'raw_SHA256':sha(O/'originals/F030_call01_raw.png'),'new_imagegen_calls':1,'originals':1,'actual_Canvas_render_runs':1,'F034_calls':0};(O/'qa/verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
