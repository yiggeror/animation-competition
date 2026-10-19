from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import distance_transform_edt
O=Path('collab/reviews/cloud_s12_20261018/F030_close_grip_from_locked026_20261019');M=O.parent/'F026_index_repair_actual_call01_20261019';S=O.parent/'F022_full_arm_repair_20261019/uniform_map_rejoin_20261019';I=O.parent/'F026_index_repair_inputs_20261019';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for d in ['reference','inputs','geometry','prompts','requests','provenance','originals','tools','diagnostics','candidate','layers','masks','actual_scene','scene','qa']:(O/d).mkdir(parents=True,exist_ok=True)
assert sha(M/'candidate/F026.png')=='34515fa0f42af3c360004b7530142d7c077b9ba344da7eccd0dad26042eb4934';assert sha(M/'actual_scene/F026_canvas.png')=='0bf8fe07e236f0a8a139807c65033e47028512954118de8a6748a80d9e820d6c'
shutil.copyfile(M/'candidate/F026.png',O/'reference/LOCKED_ACTUAL_F026_UNIQUE_MOTHER.png')
b=Image.open(M/'candidate/F026.png').convert('RGBA');ba=np.array(b);oldfar=np.array(Image.open(S/'candidate/F022_far_arm_exclusive.png').convert('RGBA'))[:,:,3]>0;ix=np.array(Image.open(M/'layers/F026_FG_new_drawn_index.png').convert('RGBA'));fara=ba.copy();fara[~(oldfar|(ix[:,:,3]>0))]=0;far=Image.fromarray(fara,'RGBA')
# Only open middle/ring/little ownership removed in this reference construction.
poly=[(951,890),(961,883),(976,883),(994,890),(1014,900),(1022,910),(1013,918),(1014,932),(1018,942),(1007,948),(990,945),(977,936),(962,927),(949,927),(946,920),(952,910),(954,900)]
openmask=Image.new('L',b.size);ImageDraw.Draw(openmask).polygon(poly,fill=255);oa=np.array(openmask)>0
# Never remove accepted thumb/index pixels from reference or prospective static base.
th=np.array(Image.open(M/'masks/protected_complete_thumb_native.png'))>0;idx=ix[:,:,3]>0;oa[th|idx]=False
back=fara.copy();back[oa]=0;backim=Image.fromarray(back,'RGBA')
# Actual locked026 index pixels provide anatomy/volume studies only, never future final fingers.
source=Image.open(M/'layers/F026_FG_new_drawn_index.png').convert('RGBA');r0=np.array([960.,923.]);r1=np.array([976.52,963.83]);v=r1-r0
plans=[('little',[944.,914.],[951.218487164,963.99560445]),('ring',[950.,905.],[959.652732655,962.940377936]),('middle',[957.,897.],[968.086978146,961.885151421])]
newlayers=[];records=[]
for name,q0,q1 in plans:
 q0=np.array(q0);q1=np.array(q1);w=q1-q0;sc=np.linalg.norm(w)/np.linalg.norm(v);an=np.arctan2(w[1],w[0])-np.arctan2(v[1],v[0]);us=v/np.linalg.norm(v);ut=w/np.linalg.norm(w);vs=np.array([-us[1],us[0]]);vt=np.array([-ut[1],ut[0]]);mat=np.outer(ut,us)*sc+np.outer(vt,vs);off=q0-mat@r0;inv=np.linalg.inv(mat);tt=-inv@off;z=source.transform(b.size,Image.Transform.AFFINE,tuple(inv[0])+(tt[0],)+tuple(inv[1])+(tt[1],),Image.Resampling.BICUBIC);z.save(O/f'geometry/{name}_actual026_volume_REFERENCE_ONLY.png');newlayers.append(z);records.append({'digit':name,'whole_source_index_reference_to_digit_matrix':[list(mat[0])+[float(off[0])],list(mat[1])+[float(off[1])]],'native_root_estimate':q0.tolist(),'pad_target':q1.tolist(),'reference_longitudinal_projection_scale':float(sc),'reference_transverse_volume_scale':1.0,'rotation_degrees':float(np.degrees(an)),'scope':'Reference-only anatomy volume projection from actual locked026 index; no code-painted finger/capsules. Root estimates inside current actual palm, hidden joints not measured. Actual new drawing is required.'})
refnew=Image.new('RGBA',b.size)
for z in newlayers:refnew=Image.alpha_composite(refnew,z)
# True static thumb and established index stay on top of the curling neighbor fingers.
lockedfront=np.zeros_like(ba);lockedfront[th|idx]=ba[th|idx];front=Image.fromarray(lockedfront,'RGBA')
target=Image.alpha_composite(backim,refnew);target=Image.alpha_composite(target,front)
Image.fromarray(np.uint8(oa)*255).save(O/'geometry/old_open_three_digits_trace_native.png');backim.save(O/'geometry/actual026_palm_open_three_removed_REFERENCE_ONLY.png');refnew.save(O/'geometry/three_whole_new_digit_volumes_REFERENCE_ONLY.png');front.save(O/'geometry/fixed026_thumb_index_context.png');target.save(O/'geometry/closed_target_REFERENCE_ONLY.png')
def plate(im):
 o=Image.new('RGBA',(1024,1024));o.alpha_composite(im.crop((816,816,1024,1024)).resize((832,832),Image.Resampling.NEAREST),(96,96));return o
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
p1=Image.new('RGBA',(1024,1024),'#e1e4e6');p1.alpha_composite(plate(target));d=ImageDraw.Draw(p1);d.text((24,20),'INPUT1 | ACTUAL LOCK026 + THREE WHOLE CLOSING DIGIT STUDIES',fill='#26313a',font=font);d.text((24,46),'One target pose. Fixed true thumb/index; new middle/ring/little volumes are reference only.',fill='#444f59',font=small);d.text((24,970),'Same actual palm/wrist. No old open hand pose or old whole-body reference.',fill='#26313a',font=small);p1.convert('RGB').save(O/'inputs/01_actual026_to030_closed_three_whole_TARGET.png')
props=Image.open(M/'actual_scene/F026_code_props_actual_layer.png').convert('RGBA');propplate=props.transform((1024,1024),Image.Transform.AFFINE,(.175,0,829.4,0,.175,666.4),Image.Resampling.NEAREST)
p2=Image.new('RGBA',(1024,1024),'#e1e4e6');p2.alpha_composite(plate(backim));p2.alpha_composite(propplate);p2.alpha_composite(plate(refnew));p2.alpha_composite(plate(front));d=ImageDraw.Draw(p2);d.rectangle((0,0,1024,82),fill='#e1e4e6');d.text((24,20),'INPUT2 | SAME CLOSED TARGET OVER TRUE FROZEN7PX ROD RASTER',fill='#26313a',font=font);d.text((24,46),'Upper shaft enters/exits on its fixed axis. Complete new pads/ink/AA clear the lower shaft.',fill='#444f59',font=small);d.rectangle((0,950,1024,1024),fill='#e1e4e6');d.text((24,970),'Do not paint rods. Keep actual thumb/index contact; three neighbors close beside them.',fill='#26313a',font=small);p2.convert('RGB').save(O/'inputs/02_same_closed_target_frozen_actual_rods.png')
# Same-hand material patches from actual locked026, no competing pose.
p3=Image.new('RGB',(1024,1024),'#e1e4e6');d=ImageDraw.Draw(p3);d.text((24,20),'INPUT3 | LOCKED026 SAME-HAND LOCAL MATERIAL / INK PATCHES',fill='#26313a',font=font)
for name,box,pos in [('PALM SKIN',(911,913,939,938),(80,150)),('ACTUAL INDEX SHADE',(982,945,992,957),(540,150)),('THUMB PAD / INK',(964,935,979,949),(80,570)),('WRIST / JADE',(850,895,879,925),(540,570))]:
 z=b.crop(box);c=Image.new('RGBA',z.size,'#e1e4e6');c.alpha_composite(z);p3.paste(c.resize((320,320),Image.Resampling.NEAREST).convert('RGB'),pos);d.text((pos[0],pos[1]-32),name,fill='#26313a',font=font)
p3.save(O/'inputs/03_locked026_local_material_only.png')
# Actual frozen raster and complete reference volume measurement; not future output acceptance.
fg=Image.alpha_composite(refnew,front).transform((1920,1080),Image.Transform.AFFINE,(1/.7,0,-275/.7,0,1/.7,-112/.7),Image.Resampling.BICUBIC);pa=np.array(props);ya,xa=np.mgrid[:1080,:1920];A=np.array([951.2616943917175,798.9063357461391]);V=np.array([1282.1986905564156,773.9467944476169])-A;u=np.clip(((xa-A[0])*V[0]+(ya-A[1])*V[1])/(V@V),0,1);dist=np.hypot(xa-(A[0]+u*V[0]),ya-(A[1]+u*V[1]));lower=(dist<=6)&(pa[:,:,3]>0);dt=distance_transform_edt(~lower);aa=np.array(fg)[:,:,3];air=[]
for t in [1,8,32,128]:
 m=aa>=t;air.append({'reference_only_alpha_threshold':t,'actual_lower_raster_overlap_pixels':int((m&lower).sum()),'pixel_centre_air':float(dt[m].min())})
rec={'unique_static_mother_SHA256':sha(M/'candidate/F026.png'),'source_commit':'3ac42dabd48a08c420b4071c766abdb7894d9050','plate_native_crop':[816,816,1024,1024],'native_to_plate':[[4,0,-3168],[0,4,-3168]],'plate_to_native':[[.25,0,792],[0,.25,792]],'current_fixed_thumb_index_exact_context':True,'reference_volume_plans':records,'reference_whole_hand_lower_air':air,'production_rule':'Never adopt this volume construction. Future actual newly drawn three whole fingers/root only, from unique call. Frozen thumb/index contacts keep their actual positions. Genuine foreground occlusion may cover old edges; never preserve old AA by cutting holes in new fingers.','new_imagegen_calls':0,'F034':'CLOSED'}
(O/'geometry/three_digit_target_and_mapping.json').write_text(json.dumps(rec,indent=2)+'\n')
(O/'provenance/F026_final_lock_receipt.json').write_text(json.dumps({'reviewer_thread':'01a15188-00cc-7705-b91f-7b18102ba0d0','locked_native_SHA256':sha(M/'candidate/F026.png'),'locked_Canvas_SHA256':sha(M/'actual_scene/F026_canvas.png'),'actual_lower_air_pixel_centre_distance':3,'actual_lower_air_pixel_square_boundary_distance':2,'alpha1_8_32_128_lower_overlap':0,'accepted_by_actual_visual_gate':True,'do_not_modify_real026_index_for_nominal1px_difference':True,'minor_material_AA_join_deferred_to_group_same_raw_pass':True,'F030_unique_call_authorized_after_input_self_check':True,'F034':'CLOSED'},indent=2)+'\n')
print(json.dumps({'three_inputs_built':True,'reference_lower_air':air,'calls':0}))
