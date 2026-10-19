from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import distance_transform_edt
import numpy as np,json,hashlib,subprocess,urllib.parse
O=Path(__file__).resolve().parents[1];P=O.parent;S=P.parent;R=S.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
raw=P/'originals/F012_raw_call01.png';candidate=O/'candidate/F012.png';canvas=O/'actual_scene/F012_Canvas.png';video=O/'actual_scene/S12_F012_same_raw_fix_1920x1080_24fps_1frame.mp4'
a=np.array(Image.open(raw));b=np.array(Image.open(candidate));render=np.array(Image.open(canvas).convert('RGB'),np.float32);dec=np.array(Image.open(O/'actual_scene/F012_MP4_decoded.png').convert('RGB'),np.float32)
assert render.shape==dec.shape==(1080,1920,3);mse=float(np.mean((render-dec)**2))
assert raw.read_bytes()==subprocess.check_output(['git','show','bbf19721:'+str(raw.relative_to(R))],cwd=R)
assert np.array_equal(a[:,:,1:3],b[:,:,1:3]) and np.array_equal(a[a[:,:,3]>=8,3],b[a[:,:,3]>=8,3])
changed=np.any(a[:,:,:3]!=b[:,:,:3],2);protected={}
for mat in ['skin','hair','trousers']:
 mask=np.array(Image.open(P/f'qa/masks/raw_F012_{mat}.png'))>0;assert not np.any(changed&mask);protected[mat+'_RGB_exact_raw']=True
# Direct readbacks from the successful actual browser render's cached native and code-prop layers.
pers=np.array(Image.open(O/'actual_scene/F012_person_registered_actual_layer.png'))[:,:,3]>=8
props=np.array(Image.open(O/'actual_scene/F012_code_props_actual_layer.png'))[:,:,3]>=8
assert pers.shape==props.shape==(1080,1920)
assert not np.any(pers&props)
distance=distance_transform_edt(~props);gap={}
for name,box in [('far_left',[860,676,987,766]),('near_right',[786,779,904,859])]:
 area=np.zeros_like(pers);x0,y0,x1,y1=box;area[y0:y1,x0:x1]=True;selection=area&pers
 yy,xx=np.nonzero(selection);v=distance[selection];idx=int(np.argmin(v));gap[name]={'actual_registered_layer_min_distance_to_actual_prop_alpha_scene_px':float(v[idx]),'nearest_actual_hand_pixel':[int(xx[idx]),int(yy[idx])],'actual_hand_roi':[x0,y0,x1,y1]};assert v[idx]>25
probe=json.loads((O/'qa/actual_ffprobe.json').read_text());st=probe['streams'];assert len(st)==1 and st[0]['codec_type']=='video' and st[0]['nb_frames']=='1' and st[0]['r_frame_rate']=='24/1' and st[0]['width']==1920 and st[0]['height']==1080
logs=[json.loads(x) for x in (O/'qa/actual_canvas_network_events.jsonl').read_text().splitlines()]
actual=[e for e in logs if e['event']=='actual_frame'];assert len(actual)==1 and actual[0]['frame']==12 and actual[0]['t']==.5 and actual[0]['PNG_SHA256']==sha(canvas)
readbacks=[e for e in logs if e['event']=='actual_cached_layer_readback'];assert len(readbacks)==3
for rb in readbacks:assert rb['PNG_SHA256']==sha(O/f"actual_scene/F012_{rb['name']}_actual_layer.png")
failed=[json.loads(x) for x in (O/'qa/failed_initial_geometry_path/actual_canvas_network_events.jsonl').read_text().splitlines()];assert not [e for e in failed if e['event']=='actual_frame']
responses=[e for e in logs if e['event']=='response'];inputs=[]
for name in sorted({urllib.parse.unquote(urllib.parse.urlparse(e['url']).path).lstrip('/') for e in responses if e['status']==200}):
 f=R/name;assert f.is_file(),f;row={'path':name,'sha256':sha(f),'bytes':f.stat().st_size,'source':'new_own_diagnostic' if O in f.parents else 'frozen_prior_input'}
 if row['source']=='frozen_prior_input':assert f.read_bytes()==subprocess.check_output(['git','show','bbf19721:'+name],cwd=R);row['Git_bbf19721_bytes_equal']=True
 inputs.append(row)
(O/'qa/actual_runtime_inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
errors=[e for e in logs if e['event'] in ['pageerror','requestfailed']];assert not errors
network={'successful_actual_render_launches':1,'initial_failed_geometry_path_launches':1,'failed_launch_actual_output_frames':0,'actual_rendered_frames':[12],'actual_frame_PNG_SHA_matches':True,'actual_cached_layer_readbacks':3,'readback_does_not_call_renderFrame_again':True,'response_non200':[e for e in responses if e['status']!=200],'console_errors_with_actual_URL':[e for e in logs if e['event']=='console_error'],'pageerror_requestfailed':errors,'initial_failure_404_responses':[e for e in failed if e['event']=='response' and e['status']>=400],'initial_failure_console_locations':[e for e in failed if e['event']=='console_error'],'runtime_files':len(inputs),'favicon_note':'Final console favicon404 location is preserved even if response event absent; do not claim all requests200. Initial own geometry404 is separately archived; no Canvas output on that launch.'}
(O/'qa/actual_network_summary.json').write_text(json.dumps(network,indent=2)+'\n')
font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
img=Image.open(canvas).convert('RGB')
for filename,crop,scale,label in [('01_actual_hands_rods_layers3x.jpg',(680,595,1060,860),3,'ACTUAL F012 Canvas: both empty hands / fixed rods'),('02_actual_knees_shoes_ground2x.jpg',(285,850,760,1055),2,'ACTUAL F012 Canvas: kneeling + contact shadows'),('03_actual_crane_cloth_contact4x.jpg',(1390,750,1570,810),4,'ACTUAL F012 Canvas: unchanged crane supported on cloth')]:
 im=img.crop(crop);im=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST);out=Image.new('RGB',(im.width,im.height+38),'#eceeee');out.paste(im,(0,38));ImageDraw.Draw(out).text((10,8),label,font=font(18),fill='black');out.save(O/'actual_scene'/filename,quality=96)
old=Image.open(S/'d01_F000/same_raw_fix_20261019/actual_scene/F000_Canvas.png').convert('RGB')
board=Image.new('RGB',(1920,1118),'white');d=ImageDraw.Draw(board)
for i,(im,label) in enumerate([(old,'LOCKED ACTUAL F000 @t0'),(img,'CORRECTED ACTUAL F012 @t0.5; original light timing')]):
 board.paste(im.resize((960,540)),(i*960,38));d.text((i*960+10,8),label,font=font(18),fill='black')
 d.text((i*960+10,588),'Actual frame context; not a same-time A/B lighting proof',font=font(15),fill='black')
 hand=im.crop((650,600,1020,860));hand=hand.resize((555,390));board.paste(hand,(i*960+5,620))
 foot=im.crop((285,850,760,1055));foot.thumbnail((390,300));board.paste(foot,(i*960+565,730))
board.save(O/'actual_scene/00_actual_F000_F012_context.jpg',quality=95)
repair=json.loads((O/'qa/native_repair_verification.json').read_text());alpha={}
for t in [1,8,128]:
 yy,xx=np.nonzero(b[:,:,3]>=t);alpha[str(t)]={'pixels':len(xx),'bbox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]}
report={'status':'AUTHORIZED_SAME_RAW_R_ONLY_AND_ACTUAL_F012_PASS_COLLAR_FACE_RESIDUAL_REVIEW_REQUIRED','source_raw_SHA256':sha(raw),'candidate_SHA256':sha(candidate),'actual_Canvas_SHA256':sha(canvas),'actual_MP4_SHA256':sha(video),'actual_MP4_decoded_vs_Canvas_RGB_MSE':mse,'actual_scene_frames':[12],'actual_scene_time':.5,'actual_runtime_inputs':len(inputs),'successful_actual_renders':1,'failed_initial_local_path_launches':1,'first_failed_launch_output_frames':0,'MP4_encodes':1,'imagegen_calls_this_task':0,'cumulative_S12_native_calls_unchanged':4,'F018_and_later_generated':False,'shared_sources_or_ready_changed':False,'pose_registration_transform_changes':0,'alpha_ge8_exact_raw':True,'protected_materials':protected,'native_alpha_after_cleanup':alpha,'native_hand_analytic_gaps_unchanged_by_repair':True,'actual_person_and_prop_alpha_overlap_pixels':0,'actual_layer_hand_gaps':gap,'full_blue_RGB_delta_vs_mother':repair['full_blue_corrected_delta_vs_mother'],'all_blue_mean_channels_within4':repair['full_blue_all_channels_within4'],'all_physical_faces_within4':False,'collar_full_physical_face_delta_vs_mother':repair['face_measurements']['collar_front']['corrected_delta_vs_mother'],'collar_note':'Local complete collar/front face masks include darker folds and differ from parent spot/face masks, which were not supplied. Do not claim every face passes. Kept authorized R reduction<=4, protected folds and all G/B unchanged. Refer residual toAstra without expanding correction.','Astra_final_gate':'PENDING_REPAIRED_NATIVE_AND_ACTUAL_F012_REVIEW'}
(O/'qa/actual_delivery_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
