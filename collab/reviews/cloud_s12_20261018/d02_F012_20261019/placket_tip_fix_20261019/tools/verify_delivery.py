from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation,distance_transform_edt
import json,hashlib,numpy as np,subprocess,urllib.parse
O=Path(__file__).resolve().parents[1];P=O.parent;S=P.parent;R=S.parents[2];BASE=P/'same_raw_fix_20261019';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=np.array(Image.open(BASE/'candidate/F012.png'));b=np.array(Image.open(O/'candidate/F012.png'));assert np.array_equal(a[:,:,3],b[:,:,3]);native_change=np.any(a!=b,2);domain=np.array(Image.open(O/'masks/domain_complete_semantic_tip.png'))>0;assert not np.any(native_change&~domain)
old=np.array(Image.open(BASE/'actual_scene/F012_Canvas.png').convert('RGB'));new=np.array(Image.open(O/'actual_scene/F012_Canvas.png').convert('RGB'));assert old.shape==new.shape==(1080,1920,3);actual_change=np.any(old!=new,2)
old_person=np.array(Image.open(BASE/'actual_scene/F012_person_registered_actual_layer.png'));person=np.array(Image.open(O/'actual_scene/F012_person_registered_actual_layer.png'));assert np.array_equal(old_person[:,:,3],person[:,:,3]);reg_change=np.any(old_person!=person,2)
# Bilinear image sampling has diagonal one-pixel support; an8-neighbour mask is required.
allowed=binary_dilation(reg_change,structure=np.ones((3,3),bool),iterations=1);assert not np.any(actual_change&~allowed)
for role in ['code_props','native_ground_shadows']:
 assert (O/f'actual_scene/F012_{role}_actual_layer.png').read_bytes()==(BASE/f'actual_scene/F012_{role}_actual_layer.png').read_bytes(),role
props=np.array(Image.open(O/'actual_scene/F012_code_props_actual_layer.png'))[:,:,3]>=8;pers=person[:,:,3]>=8;assert not np.any(props&pers);distance=distance_transform_edt(~props);gaps={}
for name,(x0,y0,x1,y1) in [('far_left',(860,676,987,766)),('near_right',(786,779,904,859))]:
 region=np.zeros_like(pers);region[y0:y1,x0:x1]=True;gaps[name]=float(distance[region&pers].min());assert gaps[name]>25
logs=[json.loads(x) for x in (O/'qa/actual_canvas_network_events.jsonl').read_text().splitlines()];frame=[e for e in logs if e['event']=='actual_frame'];assert len(frame)==1 and frame[0]['frame']==12 and frame[0]['t']==.5 and frame[0]['PNG_SHA256']==sha(O/'actual_scene/F012_Canvas.png');assert len([e for e in logs if e['event']=='actual_cached_layer_readback'])==3
assert not [e for e in logs if e['event'] in ['pageerror','requestfailed']]
responses=[e for e in logs if e['event']=='response'];inputs=[]
for name in sorted({urllib.parse.unquote(urllib.parse.urlparse(e['url']).path).lstrip('/') for e in responses if e['status']==200}):
 f=R/name;assert f.is_file();row={'path':name,'sha256':sha(f),'bytes':f.stat().st_size,'scope':'new_tip_packet' if O in f.parents else 'frozen_prior_source'}
 if row['scope']=='frozen_prior_source':assert f.read_bytes()==subprocess.check_output(['git','show','1c919912:'+name],cwd=R);row['git_1c919912_bytes_equal']=True
 inputs.append(row)
(O/'qa/actual_runtime_inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
network={'actual_render_runs':1,'actual_frames':[12],'actual_time':.5,'actual_cached_layer_readbacks':3,'observed_non200_responses':[e for e in responses if e['status']!=200],'console_errors_actual_locations':[e for e in logs if e['event']=='console_error'],'pageerror_requestfailed':[],'runtime_files':len(inputs),'favicon_note':'Preserve console URL even if no response event; do not claim all requests200.'};(O/'qa/actual_network_summary.json').write_text(json.dumps(network,indent=2)+'\n')
probe=json.loads((O/'qa/actual_ffprobe.json').read_text());ss=probe['streams'];assert len(ss)==1 and ss[0]['nb_frames']=='1' and ss[0]['r_frame_rate']=='24/1' and ss[0]['width']==1920 and ss[0]['height']==1080
video=O/'actual_scene/S12_F012_placket_tip_1920x1080_24fps_1frame.mp4';dec=np.array(Image.open(O/'actual_scene/F012_MP4_decoded.png').convert('RGB'),np.float32);mse=float(np.mean((new.astype(np.float32)-dec)**2))
font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
for name,crop,scale in [('00_same_time_actual_F012_tip_before_after8x.jpg',(582,755,661,860),8),('01_same_time_actual_F012_body_context3x.jpg',(515,690,710,890),3)]:
 w=(crop[2]-crop[0])*scale;h=(crop[3]-crop[1])*scale;board=Image.new('RGB',(w*2,h+35),'#eceeee');d=ImageDraw.Draw(board)
 for i,(ar,label) in enumerate([(old,'PREVIOUS ACTUAL F012 @0.5'),(new,'TIP CORRECTED ACTUAL F012 @0.5')]):
  im=Image.fromarray(ar).crop(crop).resize((w,h),Image.Resampling.NEAREST);board.paste(im,(i*w,35));d.text((i*w+8,7),label,font=font(17),fill='black')
 board.save(O/'actual_scene'/name,quality=97)
# Show the actual full-frame change mask; no lighting/camera/hand/prop differences elsewhere.
mask=Image.fromarray(actual_change.astype(np.uint8)*255);mask.save(O/'masks/actual_Canvas_RGB_changed.png');Image.fromarray(reg_change.astype(np.uint8)*255).save(O/'masks/actual_registered_person_RGB_changed.png')
yy,xx=np.nonzero(actual_change);report={'status':'SAME_RAW_TIP_ONLY_AND_SAME_TIME_ACTUAL_F012_VERIFIED_ASTRA_FINAL_REVIEW_PENDING','source_commit':'1c9199121eea99f2434cc39c864eb96c1aba1819','candidate_SHA256':sha(O/'candidate/F012.png'),'original_generator_raw_SHA256':'52c6faf1e5eda14c2930ca557b5d1624a4dea86853f8dd631dd950b7b0d89f2c','native_RGB_changed_pixels':int(native_change.sum()),'native_alpha_entire_exact':True,'native_RGB_outside_semantic_tip_exact':True,'actual_Canvas_SHA256':sha(O/'actual_scene/F012_Canvas.png'),'actual_MP4_SHA256':sha(video),'MP4_decoded_vs_Canvas_RGB_MSE':mse,'actual_Canvas_changed_pixels':int(actual_change.sum()),'actual_Canvas_changed_bbox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],'actual_Canvas_changes_outside_registered_tip':0,'actual_scene_code_source_byte_equal_previous':(O/'scene/s12_F012_scene.js').read_bytes()==(BASE/'scene/s12_F012_scene.js').read_bytes(),'actual_code_props_layer_byte_equal_previous':True,'actual_ground_shadow_layer_byte_equal_previous':True,'actual_registered_person_alpha_exact_previous':True,'actual_person_props_alpha_overlap':0,'actual_hand_prop_gap_scene_px':gaps,'actual_render_runs':1,'actual_frames':[12],'actual_time':.5,'imagegen_calls_this_task':0,'cumulative_S12_native_calls_unchanged':4,'F018_generated':False,'actual_cached_layer_readbacks_not_extra_renders':3,'actual_runtime_files':len(inputs)}
(O/'qa/actual_delivery_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
archive=O/'qa/iteration01_scope_refinement'
old_domain=np.array(Image.open(archive/'masks/domain_complete_semantic_tip.png'))>0
adjacent=old_domain&~domain
assert np.array_equal(a[adjacent],b[adjacent])
first=np.array(Image.open(archive/'candidate/F012.png'))
first_changed=np.any(first!=a,2)&adjacent
report.update(actual_render_runs_total_this_task=2,final_candidate_actual_render_runs=1,actual_render_runs_note='Two different native versions of the SAME F012: broader-scope diagnostic archived, then corrected contour final once. No S08 or other frame rerender.',MP4_encodes_total_this_task=2,earlier_scope_diagnostic=str(archive.relative_to(O)),adjacent_guard_pixels_exact_source=int(adjacent.sum()),earlier_changed_adjacent_pixels_restored=int(first_changed.sum()),comparison_mask_bilinear_support='One-pixel 8-neighbour support; includes diagonal bilinear sampling footprint. No pixels outside registered cloth-tip support changed.')
(O/'qa/actual_delivery_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
