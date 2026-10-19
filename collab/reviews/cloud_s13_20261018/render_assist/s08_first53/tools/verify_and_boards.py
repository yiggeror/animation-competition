from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib,subprocess,shutil,urllib.parse
R=Path('.');O=R/'collab/reviews/cloud_s13_20261018/render_assist/s08_first53';SRC=R/'collab/reviews/20261019_0123_s08_first51_scene';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
rows=[]
for f in range(53):
 p=R/'build/S08_first53'/f'{f:05d}.png';d=R/'build/S08_first53_decoded'/p.name;a=np.array(Image.open(p).convert('RGB'),np.float32);b=np.array(Image.open(d).convert('RGB'),np.float32);assert a.shape==b.shape==(1080,1920,3)
 rows.append({'frame':f,'origin':'reused707764d_actual49' if f<49 else 'new_actual_e94e1f1','source_PNG_SHA256':sha(p),'decoded_PNG_SHA256':sha(d),'decoded_same_source_RGB_MSE':float(np.mean((a-b)**2))})
base=json.loads((O/'reused49_baseline.json').read_text());assert all(x['source_PNG_SHA256']==y['source_PNG_SHA256'] for x,y in zip(base['rows'],rows))
for f in [49,50,51,52]:assert (O/f'canvas_new/F{f:03d}.png').read_bytes()==(R/'build/S08_first53_increment'/f'{f:05d}.png').read_bytes()==(R/'build/S08_first53'/f'{f:05d}.png').read_bytes()
(O/'decoded').mkdir(exist_ok=True)
for f in [48,49,50,51,52]:shutil.copyfile(R/'build/S08_first53_decoded'/f'{f:05d}.png',O/f'decoded/F{f:03d}.png')
board=Image.new('RGB',(1920,1692),(27,29,31));dd=ImageDraw.Draw(board)
for i,f in enumerate([48,49,50,51,52]):
 im=Image.open(O/f'decoded/F{f:03d}.png').convert('RGB').resize((960,540));x=(i%2)*960;y=(i//2)*564;board.paste(im,(x,y+24));dd.text((x+12,y+3),f'ACTUAL MP4 DECODE F{f:03d}',font=font(17),fill='white')
board.save(O/'00_actual_048_052.jpg',quality=95)
for filename,crop,scale in [('01_match_and_fixed_wick_actual4x.jpg',(1278,745,1455,865),4),('02_hands_pipe_low_lever_single_box_actual2x.jpg',(1110,715,1435,983),2),('03_brows_and_eyes_actual3x.jpg',(930,520,1145,650),3)]:
 w=(crop[2]-crop[0])*scale;h=(crop[3]-crop[1])*scale;board=Image.new('RGB',(w*3,(h+30)*2),(33,35,37));dd=ImageDraw.Draw(board)
 for i,f in enumerate([48,49,50,51,52]):
  im=Image.open(O/f'decoded/F{f:03d}.png').convert('RGB').crop(crop).resize((w,h),Image.Resampling.NEAREST);x=(i%3)*w;y=(i//3)*(h+30);board.paste(im,(x,y+30));dd.text((x+10,y+5),f'ACTUAL DECODE F{f:03d}',font=font(19),fill='white')
 board.save(O/filename,quality=96)
# Frozen package readback both before and after render/static audits, all76files, not just the entry.
for row in json.loads((O/'fixed_packet_readback.json').read_text()):
 p=R/row['path'];assert sha(p)==row['sha256'];assert p.read_bytes()==subprocess.check_output(['git','show','e94e1f1:'+row['path']])
# Visible old table box and148px low lever are actual original-layer pixels.
y,x=np.indices((1080,1920));disk=np.hypot(x+.5-1233.9532049682696,y+.5-766.8943738423919)<=9*14/18.5
assert int(disk.sum())==148
arms46=np.array(Image.open(SRC/'frames/F046_forearms_elbows_original_pixels.png'));arms49=np.array(Image.open(SRC/'frames/F049_forearms_elbows_original_pixels.png'));box46=np.array(Image.open(SRC/'frames/F046_table_box_original_pixels.png'));box49=np.array(Image.open(SRC/'frames/F049_table_box_original_pixels.png'));sel=box49[:,:,3]>0
assert sel.sum()==1665 and np.array_equal(box46[:,:,3],box49[:,:,3]) and np.array_equal(box46[sel],box49[sel]);assert np.array_equal(arms46[disk],arms49[disk]);assert not np.any(arms49[981:,:,3])
sourcechecks={'F051_asset':'046','F051_has_no_new_native_files':True,'F051_whole_three_layers_exact_046':'contract_first53 uses asset046, verified by frozen node test204old+8new subframe checks','box_visible_pixels':int(sel.sum()),'box_alpha_and_visible_RGBA_equal046':True,'box_bottom_y':int(np.nonzero(sel)[0].max()),'knob_disk_pixels':int(disk.sum()),'knob_disk_F049_RGBA_exact_F046':True,'arms_at_or_below981':0,'note':'Source RGBA and contract audit; does not replace actual imagery.'};(O/'source_original_pixel_checks.json').write_text(json.dumps(sourcechecks,indent=2)+'\n')
events=[json.loads(l) for l in (O/'actual_network_events.jsonl').read_text().splitlines()];actual=[e for e in events if e['event']=='actual_frame'];assert sorted(e['frame'] for e in actual)==[49,50,51,52]
assert all(e['PNG_SHA256']==rows[e['frame']]['source_PNG_SHA256'] for e in actual)
responses=[e for e in events if e['event']=='response'];inputs=[]
for name in sorted({urllib.parse.unquote(urllib.parse.urlparse(e['url']).path).lstrip('/') for e in responses if e['status']==200}):
 p=R/name;assert p.is_file();assert p.read_bytes()==subprocess.check_output(['git','show','e94e1f1:'+name]);inputs.append({'path':name,'sha256':sha(p),'git_e94e1f1_original_bytes_equal':True})
(O/'observed_runtime_fixed_bytes.json').write_text(json.dumps(inputs,indent=2)+'\n')
summary={'actual_render_runs':1,'actual_frames':[49,50,51,52],'actual_frame_PNG_matches_direct_deliveries':True,'browser_versions':sorted({e['version'] for e in events if e['event']=='browser_launched'}),'observed_responses':len(responses),'observed_non200_responses':[e for e in responses if e['status']!=200],'requestfailed':[e for e in events if e['event']=='requestfailed'],'pageerrors':[e for e in events if e['event']=='pageerror'],'console_errors_with_actual_locations':[e for e in events if e['event']=='console_error'],'F049_asset_responses':[e for e in responses if '/frames/F049_' in e['url']],'F046_reverse_reuse_asset_responses':[e for e in responses if '/frames/F046_' in e['url']],'observed_successful_runtime_files_Git_exact':len(inputs),'favicon_caveat':'Console favicon404 location may exist without response event. Preserve exact events; do not say every request200 or infer historical unknown first41URL.'}
assert not summary['requestfailed'] and not summary['pageerrors'];assert len(summary['F049_asset_responses'])==len(summary['F046_reverse_reuse_asset_responses'])==6;assert all(e['status']==200 for e in summary['F049_asset_responses']+summary['F046_reverse_reuse_asset_responses'])
(O/'actual_network_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
probe=json.loads((O/'ffprobe.json').read_text());s=probe['streams'];assert len(s)==1 and s[0]['codec_type']=='video' and s[0]['nb_frames']=='53' and s[0]['r_frame_rate']=='24/1' and s[0]['width']==1920 and s[0]['height']==1080
v={'status':'ACTUAL53_SOURCE_ENCODE_CHECKS_PASS_VISUAL_REVIEW_SEPARATE','fixed_commit':'e94e1f19894dba379f79533dd6b263e7509cff2f','entry_SHA256':sha(SRC/'s08_first53_scene.js'),'actual_new_frames':[49,50,51,52],'reused_frames':49,'reuse_delivery_commit':'707764d22518caee7712eb006361bc1d2ebfc79e','full53_rerendered':False,'actual_increment_runs':1,'assembly_encoding_runs':1,'frames':53,'fps':'24/1','size':[1920,1080],'duration_fraction':'53/24','duration_ffprobe':float(probe['format']['duration']),'audio_streams':0,'F053_and_later_rendered':False,'MP4_SHA256':sha(O/'S08_first53_1920x1080_24fps.mp4'),'max_encoded_RGB_MSE':max(r['decoded_same_source_RGB_MSE'] for r in rows),'all53_source_decode_checks':rows,'fixed_packet_files_readback':76,'runtime_rows':54,'source_F051_uses_whole_F046_art':True,'F051_Canvas_equals_F046_not_claimed':'Art identical; absolute time/fire/light differ, so actual full framePNG is not expected byte-identical toF046.','actual_browser_Canvas_SHA_matches':True,'imagegen_calls':0,'S12_or_shared_source_changes':0}
(O/'verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({k:v for k,v in v.items() if k!='all53_source_decode_checks'},indent=2))
