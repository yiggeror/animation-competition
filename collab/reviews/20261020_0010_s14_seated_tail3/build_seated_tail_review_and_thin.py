from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage
import numpy as np,json,hashlib,subprocess
P=Path('/workspace/scratch/f060b5601755/s14_stage_setup_inputs_20261019_0756/x180_x196_seated_settle_zero_call');R=P.parent;U=Path('/tmp/laidian_s14_seated_tail_20261019');Y,X=np.indices((1254,1254));h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def means(a):
 r,g,b=a[:,:,:3].astype(float).transpose(2,0,1);ok=a[:,:,3]>245;regs={'hair':ok&(Y<470)&(r>20)&(r<130)&(g>20)&(g<120)&(b>20)&(b<110)&(r-g<25)&(g-b<25),'skin':ok&(Y<810)&(r>180)&(g>120)&(b>105)&(r-g>22)&(g-b>9)&(g-b<72),'yellow_cloth':ok&(Y>395)&(Y<940)&(X>420)&(X<995)&(r>190)&(g>150)&(b<130)&(r-g>6)};return {k:a[ndimage.binary_erosion(z,iterations=2),:3].mean(0) for k,z in regs.items()}
ref=means(np.array(Image.open(R/'refs/assets/chars/x15/F000.png').convert('RGBA')));page=Image.new('RGB',(2250,505),'#f7f5ed');d=ImageDraw.Draw(page);font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',20);frames=[];rows=[]
for i,(f,hold,label) in enumerate([(186,3,'整体回解'),(189,3,'减速回正'),(192,3,'近直立'),(195,2,'真实近臂预抬'),(197,3,'已锁继续起抬')]):
 p=(R/'x197_x208_zero_call' if f==197 else P)/f'X{f}_complete_registered_candidate.png';im=Image.open(p).convert('RGBA');v=means(np.array(im));bg=Image.new('RGBA',im.size,'#f7f5ed');bg.alpha_composite(im);bg=bg.convert('RGB');page.paste(bg.resize((450,450)),(i*450,42));d.text((i*450+10,8),f'X{f} ×{hold} / {label}',font=font,fill='#294953');frames.extend([bg.resize((720,720)).tobytes()]*hold);rows.append({'frame':f,'hold':hold,'final':str(p.resolve()),'final_sha256':h(p),'parent_locked':f!=195,'mean_rgb_delta_from_same_mother':{k:(v[k]-ref[k]).tolist() for k in v},'all_regions_each_channel_within4':bool(all(abs(v[k]-ref[k]).max()<=4 for k in v))})
pagepath=U/'X186_X189_X192_X195_X197_ACTUAL_COMPLETE_REVIEW.jpg';page.save(pagepath,quality=92);video=U/'X186_X199_ACTUAL_3_3_3_2_3_FRAMES_24FPS.mp4';proc=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','720x720','-r','24','-i','-','-an','-c:v','libx264','-crf','19','-pix_fmt','yuv420p',str(video)],stdin=subprocess.PIPE)
for data in frames:proc.stdin.write(data)
proc.stdin.close();assert proc.wait()==0
art={}
def add(p,role,already=False):
 p=Path(p).resolve();assert p.exists(),p;k=str(p)
 if k in art:art[k]['roles'].append(role);return
 art[k]={'path':k,'sha256':h(p),'bytes':p.stat().st_size,'roles':[role],'already_preserved_prior_batch':already}
newrows=[]
for f in [189,192,195]:
 row=next(v for v in rows if v['frame']==f);req=P/f'X{f}_request_PREPARED_UNDER_CONTINUOUS_GATE.json';raw=P/f'X{f}_complete_body_call01_original.png';row.update({'request':str(req),'request_sha256':h(req),'raw':str(raw.resolve()),'raw_sha256':h(raw),'registration':str(P/f'X{f}_native_single_registration.json')});newrows.append(row)
 for p,role in [(req,'actual request'),(raw,'unique raw original'),(row['final'],'final native whole-body drawing'),(row['registration'],'whole similarity and minimal palette processing'),(P/f'X{f}_call_started.json','preflight'),(P/f'X{f}_call_completed.json','actual call receipt'),(P/f'X{f}_complete_native_semantic_return_mask.png','complete semantic return mask')]:add(p,f'X{f}: {role}')
 for i,p in enumerate(json.loads(req.read_text())['referenced_image_paths']):add(p,f'X{f}: actual input {i+1}',already=i>=2)
 prev={189:186,192:189,195:192}[f];add(P/f'X{f}_actual{prev}_target_preparation.json',f'X{f}: guide source and preparation')
for p in [P/'prepare_next_actual_seated_body.py',P/'register_complete_seated_body.py',P/'calibrate_registered_cloth_if_needed.py']:add(p,'shared existing processing script',True)
for p in [U/'prepare_X195_from_actual192_whole_chain.py',U/'calibrate_X192_native_hair_only.py',U/'calibrate_X195_native_hair_only.py',Path(__file__)]:add(p,'tail processing script')
for p in [pagepath,video]:add(p,'single actual exposure review')
add(P/'X186_complete_registered_candidate.png','actual source for189 and review start',True);add(R/'x197_x208_zero_call/X197_complete_registered_candidate.png','locked197 exposure endpoint',True)
obj={'status':'TAIL_THREE_ACTUAL_ORIGINALS_189_192_PARENT_LOCKED_195_REVIEW_PENDING','new_calls':3,'new_originals':3,'rows':newrows,'exposure_rows':rows,'video':str(video),'video_frames':14,'fps':24,'review':str(pagepath),'artifacts':list(art.values()),'storage':'New large assets in /tmp per parent instruction, scratch links remain. No copies into shared workspace. Preserve all unique originals and requests.','actual195_note':'Native output raises near wrist more than technical 36% guide; relaxed near hand remains before final folded gesture and far hand remains by lap. Judge 192->195->197 actual 3/2/3 exposure; no limb warp to chase technical coordinates.'};ip=P/'X189_X192_X195_RAW_REQUEST_FINAL_THIN_INDEX.json';ip.write_text(json.dumps(obj,ensure_ascii=False,indent=2));print(json.dumps({'index':str(ip),'index_sha256':h(ip),'bytes':ip.stat().st_size,'artifacts':len(art),'review':str(pagepath),'video':str(video),'rows':newrows},ensure_ascii=False))
