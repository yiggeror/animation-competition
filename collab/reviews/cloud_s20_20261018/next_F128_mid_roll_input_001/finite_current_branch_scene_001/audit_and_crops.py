"""Measure actual finite shafts vs complete palm/arm masks; emit normal crops."""
from pathlib import Path
import json,math,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import distance_transform_edt,binary_dilation
F=Path(__file__).resolve().parent;P=F.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cfg=json.loads((F/'candidate_geometry.json').read_text())
fontfile=P.parents[2]/'assets/fonts/NotoSansSC-VF.ttf';font=lambda n:ImageFont.truetype(str(fontfile),n)
def distance(points,a,b):
 v=b-a;t=np.clip(((points-a)@v)/np.dot(v,v),0,1);return np.linalg.norm(points-a-t[:,None]*v,axis=1)
def edgegap(mask,a,b,radius):
 y,x=np.nonzero(mask);d=distance(np.column_stack([x+.5,y+.5]),a,b);return float(d.min()-radius-math.sqrt(.5))
def raster_mask_to_scene(mask,pm):
 inv=[1/pm[0],0,-pm[4]/pm[0],0,1/pm[3],-pm[5]/pm[3]]
 return np.array(Image.fromarray(np.uint8(mask)*255).transform((1920,1080),Image.Transform.AFFINE,inv,Image.Resampling.NEAREST))>127
face=np.array(Image.open(F/'complete_face_head_neck_protected_mask.png').convert('L'))>0;result={};coords=[]
for frame in [120,128]:
 rep=json.loads((F/f'actual_CAM20_{frame}_geometry.json').read_text());assert rep.get('whole_card_texture_padding_only',{}).get('new_size')==[1600,1400]
 pm=rep['people_to_CAM20'];scale=pm[0];palms={s:np.array(Image.open(F/f'complete_palm{frame}_{s}_mask.png').convert('L'))>0 for s in ['R','L']};arms={s:np.array(Image.open(F/f'complete_arm{frame}_{s}_mask.png').convert('L'))>0 for s in ['R','L']};true={};rows=[]
 for rod in rep['rods']:
  a=np.array(rod['A_master']);b=np.array(rod['B_master']);rad=rod['width_screen']/scale/2;other='L' if rod['id']=='T_H' else 'R';own='R' if other=='L' else 'L';gap=edgegap(palms[other],a,b,rad);armgap=edgegap(arms[other],a,b,rad);facegap=edgegap(face,a,b,rad)
  # Actual full palm alpha ownership, sampled from B back along finite shaft.
  length=np.linalg.norm(b-a);d=np.arange(0,length+.001,.1);points=b+(a-b)*d[:,None]/length;xy=np.rint(points).astype(int);in_image=(xy[:,0]>=0)&(xy[:,0]<1672)&(xy[:,1]>=0)&(xy[:,1]<941);inside=np.zeros(len(d),bool);inside[in_image]=palms[own][xy[in_image,1],xy[in_image,0]]
  count=0
  for flag in inside:
   if not flag:break
   count+=1
  hidden=max(0,(count-1)*.1)
  row={'id':rod['id'],'other_complete_palm_conservative_air_master_px':gap,'other_complete_palm_conservative_air_CAM20_px':gap*scale,'other_complete_arm_conservative_air_master_px':armgap,'complete_head_face_conservative_air_master_px':facegap,'own_palm_hides_terminal_centerline_master_px':hidden,'finite_length_master_px':float(length),'explicit_exposed_free_handle_tail_m':0,'radius_master_px':rad}
  rows.append(row);true[rod['id']]=(a,b,rad)
  coords.append({'frame':frame,'id':rod['id'],'A_master':a.tolist(),'B_master':b.tolist(),'A_CAM20':rod['A_screen'],'B_CAM20':rod['B_screen'],'world_grip':rod['B_world'],'candidate_A_B_length_m':rod['candidate_A_B_length_m']})
 # Exact two finite segments: minimum is among endpoint-to-segment distances
 # unless the two finite interiors intersect. This branch has no intersection.
 a,b,ra=true['T_H'];c,d,rb=true['T_S'];tv,uv=np.linalg.solve(np.column_stack([b-a,-(d-c)]),c-a);intersects=bool(0<=tv<=1 and 0<=uv<=1)
 mincenter=0. if intersects else min(distance(np.array([a,b]),c,d).min(),distance(np.array([c,d]),a,b).min());shaftgap=float(mincenter-ra-rb)
 turtle=np.array(Image.open(F/f'turtle_CAM20_{frame}_original_material_RGBA.png').convert('RGBA'))[:,:,3]>100;facecam=raster_mask_to_scene(face,pm);nonpalm=np.zeros(face.shape,bool)
 for side in ['R','L']:nonpalm|=arms[side]&~binary_dilation(palms[side],iterations=10)
 armcam=raster_mask_to_scene(nonpalm,pm);faceover=int((turtle&facecam).sum());armover=int((turtle&armcam).sum());turtgap=float(distance_transform_edt(~turtle)[facecam].min())
 # Same normal CAM20 crop; no per-image alignment or independent resizing.
 for kind in ['actual','albedo']:
  im=Image.open(F/f'CAM20_F{frame}_current_branch_{kind}.png').convert('RGB');im.crop((250,350,1080,900)).save(F/f'CAM20_F{frame}_{kind}_palm_rods_1x.png')
 # Exact original exterior painted-stick pixels only, colored diagnostic.
 old=Image.open(F/'old_exterior_T_magenta_diagnostic_layer.png').convert('RGBA');inv=[1/pm[0],0,-pm[4]/pm[0],0,1/pm[3],-pm[5]/pm[3]];oldcam=old.transform((1920,1080),Image.Transform.AFFINE,inv,Image.Resampling.BICUBIC);diag=Image.open(F/f'CAM20_F{frame}_current_branch_albedo.png').convert('RGBA');diag.alpha_composite(oldcam);ImageDraw.Draw(diag).text((20,20),'洋红：120原画外露旧杆清理范围；棕色：当前有限A→B。非新物理尾段。',font=font(23),fill='#80304e');diag.convert('RGB').save(F/f'CAM20_F{frame}_old_painted_tail_magenta_DIAGNOSTIC.png')
 result[str(frame)]={'finite_segment_intersection':intersects,'infinite_axis_intersection_parameters_only':[float(tv),float(uv)],'infinite_extension_gap_is_not_used_for_collision':True,'finite_shaft_surface_air_master_px':shaftgap,'finite_shaft_surface_air_CAM20_px':shaftgap*scale,'rods_vs_complete_palms':rows,'original_turtle_RGBA_overlap_protected_head_face_CAM20_pixels':faceover,'original_turtle_RGBA_overlap_nonpalm_arm_CAM20_pixels':armover,'original_turtle_to_head_face_nearest_CAM20_px':turtgap,'body_reach_2D_reference':cfg['bones'],'full_scene_png_sha256':sha(F/f'CAM20_F{frame}_current_branch_actual.png')}
 # No collider is extended past B. Do not convert a hypothetical X into contact.
 assert not intersects and shaftgap>0
 assert all(r['other_complete_palm_conservative_air_master_px']>0 for r in rows)
 assert faceover==0 and armover==0
assert cfg['source120_sha256']==sha(Path(cfg['source120_file']))
erase=np.array(Image.open(F/'old_exterior_T_erase_mask.png').convert('L'))>0;y,x=np.nonzero(erase)
report={'status':'CURRENT_FINITE_BRANCH_SCENE_DIAGNOSTIC_ASTRA_GATE_PENDING','old_5_31_extension_contact_conclusion_withdrawn':True,'original_rods_finite_A_B_source_lines':'js/lamp/shots/s20.js:139,145-146; exterior painted-stick erasure source lines4,152-155','new_image_calls':0,'branch_count':1,'new_registration_or_alternative_branch':False,'frame_labels':[120,128],'actual_full_frame_canvas':[1920,1080],'original_turtle_material_and_model':True,'original_turtle_full_outline_retained_by_padding_only':True,'old_painted_exterior_T_erased_pixels':int(erase.sum()),'old_painted_exterior_T_erased_bbox_master':[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)],'exposed_free_handle_tail_length_m':0,'root120_and_two_A_B_lengths_are_current_candidate_only_not_previous_freeze':True,'source120_original_unchanged':True,'frames':result,'adopted':False,'new_exposure_frozen':False,'later_states_prepared':False,'scope':'Turtle/person local scene gate. Fixed grandma/C image retained; no crane-puppet integration expanded.'}
(F/'finite_clearance_and_receiving.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');(F/'finite_endpoint_grip_coordinates.json').write_text(json.dumps(coords,ensure_ascii=False,indent=2)+'\n');print(json.dumps({str(f):{k:result[str(f)][k] for k in ['finite_shaft_surface_air_master_px','original_turtle_RGBA_overlap_protected_head_face_CAM20_pixels','original_turtle_RGBA_overlap_nonpalm_arm_CAM20_pixels']} for f in [120,128]},ensure_ascii=False));print(json.dumps({str(f):result[str(f)]['rods_vs_complete_palms'] for f in [120,128]},ensure_ascii=False))
