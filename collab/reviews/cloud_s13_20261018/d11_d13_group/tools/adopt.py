#!/usr/bin/env python3
"""Preserve native tool output and exact dependency records; QA only, no repaint."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,shutil,sys,datetime
P=Path(__file__).resolve().parents[1];ROOT=P.parent
n=int(sys.argv[1]);pose=sys.argv[2];toolpath=Path(sys.argv[3]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,a):p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
names={'d11':'F078_d11_near_closed.png','d12':'F084_d12_closed_before_turn.png','d13':'F087_d13_whole_head_turn_start.png'}
reqpath=P/f'requests/call_{n:03}_request.json';req=json.loads(reqpath.read_text());source=Path(req['args']['referenced_image_paths'][0])
assert sha(source)==req['dependency_sha256']
raw=P/f'originals/S13_{pose}_call_{n:03}_raw.png';assert raw.read_bytes()==toolpath.read_bytes()
im=Image.open(raw);im.load();assert im.mode=='RGBA' and im.size==(1024,1536)
out=P/'approved_local'/names[pose];shutil.copyfile(raw,out)
req['status']='completed_native_output_self_reviewed';put(reqpath,req)
put(P/f'requests/call_{n:03}_response.json',{'call_id':req['call_id'],'tool':'image_gen.imagegen','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'raw':str(raw.relative_to(P)),'raw_sha256':sha(raw),'tool_original_path':str(toolpath),'model_version':'not exposed',
 'returned_fields':['image_url','output_hint'],'image_storage':'Complete unmodified PNG; inline base64 not duplicated.',
 'inputs':[{'path':str(source),'sha256':sha(source)}],'is_error':False})
put(P/f'qa/{pose}_validation.json',{'pose':pose,'status':'author_self_reviewed_pending_Astra_group_review','source_sha256':sha(source),
 'output':str(out.relative_to(P)),'output_sha256':sha(out),'raw_sha256':sha(raw),'native_byte_identical':raw.read_bytes()==out.read_bytes(),
 'canvas':[1024,1536],'registration':'identity, same camera','local_repaint':False,'warp':False,'alpha_filter':False})
f=lambda n:ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',n)
def comp(a):
 b=Image.new('RGBA',a.size,(245,245,245,255));b.alpha_composite(a);return b.convert('RGB')
sheet=Image.new('RGB',(1536,1110),'#f5f3ed');d=ImageDraw.Draw(sheet)
for x,a,t in [(15,Image.open(source).convert('RGBA'),'合格前态'),(783,im,pose+' 实际原生采用')]:
 a=comp(a).crop((90,20,940,1190));a.thumbnail((740,930));sheet.paste(a,(x,75));d.text((x,20),t,font=f(25),fill='#23333e')
d.text((20,1040),'同画布/裁切/缩放；原生整张采用，不拉伸嘴贴图、不用代码画人物。',font=f(24),fill='#23333e');sheet.save(P/f'qa/{pose}_same_scale_previous.jpg',quality=96)
lp=ROOT/'provenance/generation_ledger.json';a=json.loads(lp.read_text());cid=req['call_id']
if not any(r['call_id']==cid for r in a['raw_outputs']):a['raw_outputs'].append({'call_id':cid,'pose':pose,'path':str(raw.relative_to(ROOT)),
 'sha256':sha(raw),'source_tool_path':str(toolpath),'adoption_status':'native_author_self_reviewed_pending_Astra_d11_d13_review',
 'adopted_output':str(out.relative_to(ROOT)),'adopted_sha256':sha(out),'adopted_scope':'full native RGBA'})
for row in a['raw_outputs']:
 if row.get('pose') in ['d08','d09','d10'] and row.get('adopted_output'):row['adoption_status']='Astra_locked_9ed9d4fe_adopted_output'
a['stage']='d01_d10_locked_d11_d13_in_progress';a['successful_raw_images']=len(a['raw_outputs']);a['image_generation_requests']=len(a['raw_outputs'])+a.get('failed_requests',0)
a['post_d01_image_requests']=len(a['raw_outputs'])-1;a['post_d01_pose_requests']=len(a['raw_outputs'])-1
put(lp,a);print(pose,sha(out))
