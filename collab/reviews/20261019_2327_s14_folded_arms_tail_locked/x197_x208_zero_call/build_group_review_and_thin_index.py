from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,subprocess,numpy as np
P=Path(__file__).parent;R=P.parent;frames=[197,200,203,206];files=[P/f'X{f}_complete_registered_candidate.png' for f in frames]+[R/'refs/assets/chars/x15/F000.png'];page=Image.new('RGB',(2500,620),'#f7f5ed');d=ImageDraw.Draw(page);font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',20);ims=[]
for i,(f,path) in enumerate(zip(frames+[208],files)):
 im=Image.open(path).convert('RGBA');bg=Image.new('RGBA',im.size,'#f7f5ed');bg.alpha_composite(im);rgb=bg.convert('RGB');ims.append(rgb);page.paste(rgb.resize((500,500)),(i*500,65));d.text((i*500+12,15),f'X{f} / '+('真F000，复用' if f==208 else '完整原生双臂'),font=font,fill='#294953');d.text((i*500+12,575),['3帧 / 近右先抬','3帧 / 远左手开始内收','3帧 / 左掌接近上臂','2帧 / 右臂前叠收尽','208–239共32帧 / 原终态'][i],font=font,fill='#294953')
page.save(P/'X197_X208_ACTUAL_NATIVE_FIVE_STATE_REVIEW.jpg',quality=92)
# Render exact24fps exposure without an intermediate frame sequence.
vid=P/'X197_X239_ACTUAL_24FPS_EXPOSURE.mp4';proc=subprocess.Popen(['ffmpeg','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','720x720','-r','24','-i','-','-an','-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart','-y',str(vid)],stdin=subprocess.PIPE)
for im,n in zip(ims,[3,3,3,2,32]):
 data=np.array(im.resize((720,720),Image.Resampling.LANCZOS),dtype=np.uint8).tobytes()
 for _ in range(n):proc.stdin.write(data)
proc.stdin.close();assert proc.wait()==0
probed=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=nb_read_frames,r_frame_rate,width,height','-of','json',str(vid)]))
items={}
def add(path,role):
 path=Path(path).resolve();key=str(path)
 if key not in items:items[key]={'path':key,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size,'roles':[]}
 if role not in items[key]['roles']:items[key]['roles'].append(role)
 return key
states=[]
for f in frames:
 req=P/(f'X{f}_request_PREPARED_UNDER_CONTINUOUS_GATE.json' if f!=197 else 'X197_request_PREPARED_NOT_AUTHORIZED_NOT_CALLED.json');q=json.loads(req.read_text());reg=P/f'X{f}_native_single_registration.json';r=json.loads(reg.read_text());state={'id':f'X{f}','start':f,'hold':3 if f<206 else 2,'final':add(P/f'X{f}_complete_registered_candidate.png',f'X{f}_final'),'raw':add(P/f'X{f}_complete_upper_call01_original.png',f'X{f}_unique_original'),'actual_request':add(req,f'X{f}_actual_request'),'actual_inputs':[add(x,f'X{f}_input_{i+1}') for i,x in enumerate(q['referenced_image_paths'])],'registration':add(reg,f'X{f}_one_similarity_record'),'processing':add(P/f'register_X{f}_whole_upper.py',f'X{f}_zero_call_registration_script'),'semantic_mask':add(P/f'X{f}_complete_upper_semantic_return_mask.png',f'X{f}_final_return_domain'),'call_started':add(P/f'X{f}_call_started.json',f'X{f}_call_start'),'call_completed':add(P/f'X{f}_call_completed.json',f'X{f}_call_result'),'final_sha256':r['final_sha256'],'master_review':'passed' if f==197 else 'pending_parent_group_review','self_review':'full arms/hand order/seat/head/legs/stool continuous at normal size'};states.append(state)
end=add(files[-1],'exact_S15_F000_endpoint_reused_X208_X239');add(P/'X197_X208_ACTUAL_NATIVE_FIVE_STATE_REVIEW.jpg','actual_group_review');add(vid,'24fps_43frame_exposure');add(P/'build_group_review_and_thin_index.py','group_render_and_index_script');add(P/'X200_actual197_target_registration.json','whole_native_target_adjustment');
record={'status':'FOUR_NATIVE_NEW_DRAWINGS_PLUS_EXISTING_ENDPOINT','unique_calls':4,'unique_originals':4,'blocked_attempts':0,'states':states,'endpoint':{'id':'X208','start':208,'hold':32,'path':end,'sha256':items[end]['sha256'],'no_new_generation':True},'scene_range':'X197-239 only. No X180-196 seat arrival or blocked X150 claimed.','actual_video_probe':probed,'duplicate_inputs_dedup_by_path':True,'artifacts':list(items.values()),'counts':{'artifacts':len(items),'total_bytes':sum(x['bytes'] for x in items.values())},'immutability':'X197 parent-locked b5b7f223... retained; no alterations to previousG orX locks.'};out=P/'X197_X206_FOUR_FINAL_RAW_REQUESTS_DEDUP_INPUTS_THIN_INDEX.json';out.write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps({'index':str(out.resolve()),'index_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'states':{x['id']:x['final_sha256'] for x in states},'counts':record['counts'],'probe':probed},ensure_ascii=False))
