from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import subprocess,json,hashlib,numpy as np
P=Path(__file__).resolve().parent;R=Path('/workspace/animation-competition');old=R/'collab/reviews/20261017_1045_s18_full_opus/S18_flipbook_review.mp4';font=R/'assets/fonts/NotoSansSC-VF.ttf';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(a):subprocess.run(a,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)]))
meta=json.loads((P/'render_manifest.json').read_text());assert len(meta['rendered'])==72 and not meta['errors'];assert all(x['sourceUnchanged'] for x in meta['dependencies'])
text='S18  近景：小满"噗"地笑出声，捂住嘴';(P/'subtitle.txt').write_text('\n'.join(text[i:i+34] for i in range(0,len(text),34)))
vf=f"scale=960:540,drawbox=x=0:y=ih-92:w=iw:h=92:color=black@0.55:t=fill,drawtext=expansion=none:fontfile='{font}':textfile='{P/'subtitle.txt'}':fontsize=22:fontcolor=white:line_spacing=6:x=24:y=h-82"
silent=P/'S18_rhythm_candidate_subtitled_silent.mp4';final=P/'S18_节奏收尾对照非已采用.mp4'
encode=['ffmpeg','-y','-loglevel','error','-framerate','24','-i',str(P/'frames/f%04d.png'),'-frames:v','72','-vf',vf,'-r','24','-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-video_track_timescale','12288',str(silent)]
run(encode)
mux=['ffmpeg','-y','-loglevel','error','-copyts','-itsoffset','0.02099609375','-i',str(silent),'-i',str(old),'-map','0:v:0','-map','1:a:0','-c','copy','-avoid_negative_ts','disabled','-video_track_timescale','12288','-movie_timescale','1536000','-movflags','+faststart','-metadata','title=节奏收尾对照非已采用',str(final)]
run(mux)
fp=probe(final);bp=probe(old);v=next(x for x in fp['streams'] if x['codec_type']=='video');a=next(x for x in fp['streams'] if x['codec_type']=='audio');bv=next(x for x in bp['streams'] if x['codec_type']=='video');ba=next(x for x in bp['streams'] if x['codec_type']=='audio')
assert int(v['nb_read_frames'])==72 and v['avg_frame_rate']=='24/1';assert v['start_pts']==bv['start_pts']==258 and v['time_base']==bv['time_base']=='1/12288';assert a['start_pts']==ba['start_pts']==0
run(['ffmpeg','-v','error','-i',str(final),'-f','null','-'])
def audio_pcm(p):return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-c:a','pcm_f32le','-f','f32le','pipe:1'])
def packet_info(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256','-show_entries','packet=pts,dts,duration,size,data_hash','-of','json',str(p)]))['packets']
p0=audio_pcm(old);p1=audio_pcm(final);assert p0==p1;pk0=packet_info(old);pk1=packet_info(final);assert pk0==pk1
# Independent F0 image check, never used for the candidate rendering.
for label,p in [('baseline',old),('candidate',final)]:run(['ffmpeg','-y','-v','error','-i',str(p),'-frames:v','1',str(P/f'{label}_decoded_f0000.png')])
x=np.asarray(Image.open(P/'baseline_decoded_f0000.png').convert('RGB'),dtype=float);y=np.asarray(Image.open(P/'candidate_decoded_f0000.png').convert('RGB'),dtype=float);d=np.abs(x-y)
metrics={'mean_abs_rgb':float(d.mean()),'p99_abs_rgb':float(np.percentile(d,99)),'max_abs_rgb':float(d.max()),'pixels_max_channel_diff_over_20':int((d.max(2)>20).sum()),'exact_decoded_pixels_equal':bool(np.array_equal(x,y))}
strip=Image.new('RGB',(960,600),'white');small=ImageFont.truetype(str(font),18)
for label,i,xx in [('原曝光表 F0',0,x),('候选 F0（共同曝光）',1,y)]:strip.paste(Image.fromarray(xx.astype('uint8')).resize((480,270)),(i*480,30));ImageDraw.Draw(strip).text((i*480+12,5),label,font=small,fill='black')
# Inspect actual late rendered frames in one contact sheet, not recycled old footage.
for i,n in enumerate([33,39,54,63]):
 im=Image.open(P/'frames'/f'f{n:04d}.png').resize((240,135));strip.paste(im,(i*240,340));ImageDraw.Draw(strip).text((i*240+8,315),f'实际重渲 F{n}',font=small,fill='black')
ImageDraw.Draw(strip).text((12,500),'节奏收尾对照非已采用；只改曝光表，前段抬手断续仍未解决。',font=small,fill='black');strip.save(P/'comparison_contact_sheet.jpg',quality=94)
(P/'README.md').write_text('节奏收尾对照非已采用。全部72帧由fda4926当前S18代码在n/24真实重渲；只有HTTP返回的x18_laugh.flip.json.timelineFrames被替换，仓库不变。沿用960×540与sheetRes450预览。字幕完整沿用review_film.mjs文字/参数。AAC从已审旧场景片完整复制，无重编码；新视频F0保持258/12288秒，音频包起点仍0、实际母带内容起点仍1024/48000秒。替代表减少等速循环，F54回k08、F63落k07，不含k11；不解决前段抬手断续，不代表已采用。\n')
manifest={'label':'节奏收尾对照非已采用','base_head':meta['head'],'runtime_override_only':'assets/flips/x18_laugh.flip.json.timelineFrames','timeline':meta['replacementTimeline'],'render_manifest_sha256':sha(P/'render_manifest.json'),'override_sha256':sha(P/'x18_laugh.timeline_override.flip.json'),'rendered_frames':72,'fps':24,'video_duration_seconds':3,'container_duration_seconds':float(fp['format']['duration']),'baseline_path':str(old),'baseline_sha256':sha(old),'mp4':str(final),'mp4_sha256':sha(final),'audio':{'mode':'bit-for-bit AAC packet copy from audited baseline, no re-encode','packet_count':len(pk1),'packet_pts_dts_duration_size_hash_all_equal':True,'decoded_f32le_sha256':hashlib.sha256(p1).hexdigest(),'decoded_pcm_bytes':len(p1),'decoded_pcm_equal_to_baseline':True,'container_audio_start_pts':a['start_pts'],'time_base':a['time_base'],'existing_verified_mother_segment_seconds':[115,118],'mother_content_start_sample':1024,'mother_content_start_seconds':1024/48000},'timing':{'video_start_pts':v['start_pts'],'video_time_base':v['time_base'],'video_start_seconds':258/12288,'F15_pts_seconds':258/12288+15/24,'audio_event_seconds':1024/48000+.6,'F15_minus_event_ms':1000*(258/12288+15/24-(1024/48000+.6))},'subtitle_text':text,'subtitle_filter':vf,'f0_decoded_comparison':metrics,'encode_command':encode,'mux_command':mux,'limitations':['Only timing/ending comparison; early arm pose discontinuities unchanged.','Not adopted, not motion approval.'],'files':{p.name:{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(P.iterdir()) if p.is_file() and p.name!='manifest.json'}}
(P/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'mp4':str(final),'mp4_sha256':sha(final),'video_start':v['start_time'],'audio_start':a['start_time'],'audio_pcm_equal':True,'audio_packets_equal':True,'F0_compare':metrics,'manifest_sha256':sha(P/'manifest.json')},ensure_ascii=False,indent=2))
