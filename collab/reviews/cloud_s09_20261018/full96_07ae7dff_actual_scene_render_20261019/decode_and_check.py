"""Actual existing96f MP4 verification; no rendering or art mutation."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,subprocess,shutil,numpy as np

R=Path(__file__).resolve().parent;W=R.parents[3];P=W/'build/S09_full96'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=json.loads((R/'source_before_render.json').read_text())
for row in source['production_assets_before_render']:assert sha(W/row['path'].lstrip('/'))==row['sha256']
assert sha(W/source['source_module']['path'])==source['source_module']['sha256']
paths=sorted(P.glob('*.png'));assert [p.name for p in paths]==[f'{i:05}.png' for i in range(96)]
rendered=[]
for i,p in enumerate(paths):
    im=Image.open(p);assert im.size==(1920,1080)
    rendered.append({'frame':i,'source_state':source['all96_timing_bindings'][i]['source_state'],'lossless_render_PNG_sha256':sha(p)})
video=R/'S09_full96_07ae7dff_1920x1080_24fps_ACTUAL.mp4';shutil.copyfile(W/'build/S09_full96.mp4',video);assert sha(video)==sha(W/'build/S09_full96.mp4')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]));st=probe['streams'];assert len(st)==1 and st[0]['codec_type']=='video';st=st[0]
assert (st['width'],st['height'],st['avg_frame_rate'],int(st['nb_read_frames']))==(1920,1080,'24/1',96)
assert abs(float(st['duration'])-4)<1e-6
(R/'ffprobe_actual96.json').write_text(json.dumps(probe,indent=2)+'\n')
indices=source['actual_decode_required'];D=R/'decoded_actual_mp4';D.mkdir(exist_ok=True);S=R/'boundary_sheets';S.mkdir(exist_ok=True)
select='+'.join(rf'eq(n\,{i})' for i in indices)
cmd=['ffmpeg','-v','error','-y','-i',str(video),'-vf','select='+select,'-vsync','0','-start_number','0',str(D/'selected_%03d.png')]
subprocess.run(cmd,check=True);selected=sorted(D.glob('selected_*.png'));assert len(selected)==len(indices)==39
decoded={};selected_checks=[]
for i,p in zip(indices,selected):
    dst=D/f'F{i:03}.png';p.replace(dst);im=Image.open(dst).convert('RGB');assert im.size==(1920,1080);decoded[i]=im
    v=np.array(im).astype(np.int16);expected=np.array(Image.open(paths[i]).convert('RGB')).astype(np.int16);mae=float(np.abs(v-expected).mean());assert mae<3
    selected_checks.append({'frame':i,'source_state':rendered[i]['source_state'],'actual_decoded_png_sha256':sha(dst),'actual_decode_vs_same_frame_lossless_render_RGB_MAE':mae})
# Independently decode every encoded frame at reduced size and compare to its own rendered PNG.
# This verifies the encoded96f order without storing another full set of repeated decoded PNGs.
raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-vf','scale=384:216','-vsync','0','-f','rawvideo','-pix_fmt','rgb24','-'])
small=np.frombuffer(raw,np.uint8).reshape((-1,216,384,3));assert len(small)==96;allchecks=[]
for i,z in enumerate(small):
    expected=np.array(Image.open(paths[i]).convert('RGB').resize((384,216),Image.Resampling.BICUBIC)).astype(np.int16);mae=float(np.abs(z.astype(np.int16)-expected).mean());assert mae<3
    allchecks.append({'frame':i,'bound_source_state':rendered[i]['source_state'],'actual_decode_384x216_vs_corresponding_render_RGB_MAE':mae})
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
for batch in range(4):
    part=indices[batch*12:(batch+1)*12];rows=(len(part)+3)//4;board=Image.new('RGB',(1920,rows*300),(226,235,242));dr=ImageDraw.Draw(board)
    for j,i in enumerate(part):
        x=(j%4)*480;y=(j//4)*300;board.paste(decoded[i].resize((480,270)),(x,y+30));dr.text((x+6,y+5),f'ACTUAL F{i:03} / {rendered[i]["source_state"]}',font=font,fill='#253f55')
    board.save(S/f'ACTUAL_required39_full_scene_{batch+1:02}.png')
def strip(name,frames,crop,tile,cols=None):
    cols=cols or len(frames);rows=(len(frames)+cols-1)//cols;out=Image.new('RGB',(cols*tile[0],rows*(tile[1]+34)),(226,235,242));d=ImageDraw.Draw(out)
    for j,i in enumerate(frames):
        x=(j%cols)*tile[0];y=(j//cols)*(tile[1]+34);out.paste(decoded[i].crop(crop).resize(tile),(x,y+34));d.text((x+6,y+5),f'ACTUAL decode F{i:03}',font=font,fill='#253f55')
    out.save(S/name)
strip('ACTUAL_000_008_014_018_026_switch_fail_reset.png',[0,8,14,18,26],(950,400,1460,930),(408,424))
strip('ACTUAL_two_taps_full_prop_hands_elbows.png',[37,42,44,52,56,58],(750,220,1500,1050),(375,415))
strip('ACTUAL_two_contacts_and_rebounds_tail_palm.png',[37,42,44,52,56,58],(1100,690,1450,1010),(525,480),3)
strip('ACTUAL_058_060_062_063_whole_bridge.png',[58,60,62,63],(550,0,1530,1080),(490,540))
strip('ACTUAL_060_062_063_complete_grip_receiver.png',[60,62,63],(900,400,1500,1040),(540,576))
strip('ACTUAL_072_to073_FIRST_LIGHT_full_scene.png',[72,73],(0,0,1920,1080),(960,540))
strip('ACTUAL_069_072_073_076_077_085_095_lens_beam.png',[69,72,73,76,77,85,95],(1000,470,1920,940),(460,235),4)
strip('ACTUAL_073_077_085_whole_head_neck_states.png',[73,77,85],(550,0,1150,670),(540,603))
logs=[json.loads(s) for s in (R/'browser_resources.jsonl').read_text().splitlines() if s]
requests=[r for r in logs if r['event']=='request'];responses=[r for r in logs if r['event']=='response'];reviews=[r for r in requests if '/collab/reviews/' in r.get('url','')]
asset_paths=sorted(set('/'+r['url'].split('/',3)[3].split('?')[0] for r in responses if '/assets/chars/x09/' in r.get('url','')))
summary=json.loads((R/'browser_resource_summary.json').read_text());assert not summary['request_failures'] and not summary['page_errors'] and not reviews
assert all(r['status']==200 for r in responses)
assert all(row['path'] in asset_paths for row in source['production_assets_before_render'])
resourcecheck={'all_recorded_responses_200':True,'request_count':len(requests),'response_count':len(responses),'reviews_requests':len(reviews),'production_x09_asset_paths_seen':asset_paths,'all23_body_emission_asset_paths_seen':True,'console_errors':summary['console_errors'],'request_failed':summary['request_failures'],'page_errors':summary['page_errors']}
(R/'resource_checks.json').write_text(json.dumps(resourcecheck,indent=2)+'\n')
report={'status':'ACTUAL96_COMPLETE_REQUIRED39_DECODE_PENDING_VISUAL_REVIEW','fixed_source_commit':source['fixed_source_commit'],'mp4':str(video.relative_to(R)),'mp4_sha256':sha(video),'mp4_bytes':video.stat().st_size,'size':[1920,1080],'fps':24,'frames':96,'duration_seconds':4,'audio_streams':0,'source_PNGs_all96':rendered,'all96_encoded_order_checks_reduced_size':allchecks,'actual_full_resolution_decoded39':selected_checks,'decode_command':cmd,'20_state_timing_coverage_000_095':source['20_exposure_states'],'all_source_assets_unchanged_after_render':True,'resource_checks':resourcecheck,'new_imagegen_calls':0,'production_changes':False,'render_runs':1,'rendered_scene_frames_total':96,'whole_scene_final_approval_claim':False}
(R/'actual96_render_decode_and_resource_checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'actual_MP4':str(video),'SHA256':sha(video),'actual_decoded_fullsize':len(indices),'all96_order_checks_max_RGB_MAE':max(c['actual_decode_384x216_vs_corresponding_render_RGB_MAE'] for c in allchecks),'resources':resourcecheck},indent=2))
