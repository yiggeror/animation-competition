#!/usr/bin/env python3
"""Record and inspect a native imagegen pose. No repaint or code-drawn character."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,sys,shutil,datetime
P=Path(__file__).resolve().parents[1];ROOT=P.parent
n=int(sys.argv[1]);pose=sys.argv[2];toolpath=sys.argv[3]
names={'d05':'F036_d05_pretend_drowsy.png','d06':'F040_d06_yawn_start.png','d07':'F044_d07_yawn_opening.png'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,a):p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
reqpath=P/f'requests/call_{n:03}_request.json';req=json.loads(reqpath.read_text())
raw=P/f'originals/S13_{pose}_call_{n:03}_raw.png';assert raw.read_bytes()==Path(toolpath).read_bytes()
im=Image.open(raw).convert('RGBA');im.load();assert im.size==(1024,1536)
basepath=Path(req['args']['referenced_image_paths'][0]);base=Image.open(basepath).convert('RGBA')
assert sha(basepath)==req['dependency_sha256']
output=P/'approved_local'/names[pose];shutil.copyfile(raw,output)
req['status']='completed_one_raw_image';put(reqpath,req)
res={'call_id':req['call_id'],'recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'tool':'image_gen.imagegen','raw':str(raw.relative_to(P)),'raw_sha256':sha(raw),'tool_original_path':toolpath,
 'returned_fields':['image_url','output_hint'],'image_data_storage':'Unmodified full output PNG; inline image data not duplicated.',
 'model_version':'not exposed','inputs':[{'path':str(basepath),'sha256':sha(basepath),'bytes':basepath.stat().st_size}],'is_error':False}
put(P/f'requests/call_{n:03}_response.json',res)
put(P/f'qa/{pose}_validation.json',{'pose':pose,'status':'author_self_accepted_pending_Astra_small_batch_review',
 'source':str(basepath),'source_sha256':sha(basepath),'raw_sha256':sha(raw),'adopted':str(output.relative_to(P)),
 'adopted_sha256':sha(output),'dimensions':list(im.size),'mode':'RGBA','registration':'identity; same1024×1536 source camera',
 'adopted_matches_raw_byte_for_byte':output.read_bytes()==raw.read_bytes(),'local_repaint':False,'geometric_warp':False,'scope_mask':None,
 'note':'完整原生头颈领与上身呼吸一起采用，非局部嘴贴缩放；需实看同尺度图，尺寸值不代姿态审查。'})
def comp(a):
 b=Image.new('RGBA',a.size,(245,245,245,255));b.alpha_composite(a);return b.convert('RGB')
f=lambda n:ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',n)
sheet=Image.new('RGB',(1536,1110),'#f5f3ed');d=ImageDraw.Draw(sheet)
comparison=Image.open(req.get('comparison_previous_pose_path',basepath)).convert('RGBA')
for x,a,label in [(15,comparison,'最近已自审前态'),(783,im,pose+' 实际原生采用 / 同尺度')]:
 crop=comp(a).crop((90,20,940,1190));crop.thumbnail((740,930));sheet.paste(crop,(x,75));d.text((x,18),label,font=f(25),fill='#23333e')
d.text((24,1040),'同画布 / 同裁切 / 同缩放；整张工具原生像素，无代码人物、局部五官拉伸或额外光照。',font=f(23),fill='#23333e')
sheet.save(P/f'qa/{pose}_same_scale_previous_actual.jpg',quality=96)
comp(im).save(P/f'qa/{pose}_adopted_on_light.jpg',quality=96)
lp=ROOT/'provenance/generation_ledger.json';ledger=json.loads(lp.read_text());cid=req['call_id']
if not any(r['call_id']==cid for r in ledger['raw_outputs']):
 ledger['raw_outputs'].append({'call_id':cid,'pose':pose,'path':str(raw.relative_to(ROOT)),'sha256':sha(raw),
 'source_tool_path':toolpath,'adoption_status':'native_whole_output_author_self_accepted_pending_Astra_small_batch',
 'adopted_output':str(output.relative_to(ROOT)),'adopted_sha256':sha(output),'adopted_scope':'full native RGBA, identity registration'})
for row in ledger['raw_outputs']:
 if row.get('pose') in ['d02','d03','d04']:row['adoption_status']='Astra_locked_adopted_segment_0c0f62d'
ledger['stage']='d01_d04_locked_d05_d07_small_batch_in_progress'
ledger['successful_raw_images']=len(ledger['raw_outputs']);ledger['image_generation_requests']=len(ledger['raw_outputs'])+ledger.get('failed_requests',0)
ledger['post_d01_pose_requests']=len(ledger['raw_outputs'])-1
ledger['note']='d01–d04 adopted PNGs locked by Astra; d05→d06→d07 authorized small batch, actual prior self-accepted image as each source. No d08 call. Native whole-pose outputs preferred for continuous head/neck/chest breathing; original outputs and exact requests preserved.'
put(lp,ledger)
print(pose,sha(output))
