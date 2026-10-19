"""One actual local return; preserve every black body pixel from registered039."""
from pathlib import Path
import json,re,base64,hashlib,shutil,datetime
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;PACK=P.parent;assert not (P/'S20_F039_head_neck_candidate.png').exists()
r=json.loads((P/'tool_return_original.json').read_text());raw=Path(re.search(r'/workspace/generated_images/[^\s]+\.png',r['output_hint']).group());data=raw.read_bytes();assert base64.b64decode(r['image_url'].split(',',1)[1])==data;assert not (P/'raw_original.png').exists() or (P/'raw_original.png').read_bytes()==data;shutil.copyfile(raw,P/'raw_original.png')
im=Image.open(raw).convert('RGBA');size=list(im.size);pad=False
if im.size==(1671,941):z=Image.new('RGBA',(1672,941));z.paste(im,(0,0));im=z;pad=True
else:assert im.size==(1672,941),im.size
source=PACK/'F039_whole_source_diagnostic_001/F039_registered_rigid_pair_trial.png';A=np.array(Image.open(source).convert('RGBA'));mask=np.array(Image.open(P/'inputs/03_head_neck_small_collar_edit_white.png').convert('L'))>0;B=A.copy();B[mask]=np.array(im)[mask];assert np.array_equal(B[~mask],A[~mask]);assert np.array_equal(B[430:],A[430:]);arm=A[395:440,582:,3]>0;assert np.array_equal(B[395:440,582:][arm],A[395:440,582:][arm]);assert np.array_equal(B[:,710:],A[:,710:])
out=P/'S20_F039_head_neck_candidate.png';Image.fromarray(B).save(out)
bg=Image.new('RGBA',(1672,941),'#bdc1c4');bg.alpha_composite(Image.fromarray(B));bg.convert('RGB').save(P/'actual_full_gray.jpg',quality=96);bg.crop((480,160,710,420)).resize((690,780),Image.Resampling.NEAREST).convert('RGB').save(P/'actual_head_neck_3x.jpg',quality=97)
font=ImageFont.truetype(str(PACK.parents[2]/'assets/fonts/NotoSansSC-VF.ttf'),18);paths=[PACK/'handoff_008_020_032_generation_002/F032/S20_F032_accepted.png',PACK/'B04_B05_generation_002/F036/S20_F036_accepted.png',out];box=(480,150,710,430);board=Image.new('RGB',(1380,600),'#bdc1c4');d=ImageDraw.Draw(board)
for i,(label,p) in enumerate(zip(['032锁定源','036纠正已过','039完整头颈局修'],paths)):
 c=Image.open(p).convert('RGBA');g=Image.new('RGBA',c.size,'#bdc1c4');g.alpha_composite(c);board.paste(g.crop(box).resize((460,560),Image.Resampling.NEAREST).convert('RGB'),(i*460,40));d.text((i*460+8,7),label+' · 同尺2倍',font=font,fill='#263743')
board.save(P/'032_036_039_head_neck_same_scale.png')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();meta={'actual_head_calls':1,'raw_outputs':1,'original_tool_path':str(raw),'raw_sha256':sha(P/'raw_original.png'),'raw_size':size,'rightmost_transparent_column_only':pad,'raw_matches_tool_data':True,'candidate_sha256':sha(out),'source_registered039_sha256':sha(source),'prompt_sha256':sha(P/'prompt_submitted_zh.txt'),'request_sha256':sha(P/'tool_args_exact.json'),'black_domain_pixels':int((~mask).sum()),'black_RGBA_changes':0,'whole_lower_body_rows430plus_RGBA_changes':0,'existing_arm_region_RGBA_changes':0,'hands_and_rod_contact_area_x710plus_RGBA_changes':0,'foot_comparison_remains_exactly_same_pixels':True,'Astra_actual_output_signoff':False};(P/'receipt_and_protection.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');(P/'status.json').write_text(json.dumps({'state':'ACTUAL_HEAD_RETURN_REPROTECTED_AWAITING_AUTHOR_REVIEW','actual_calls':1,'raws':1,'automatic_retry':False},indent=2)+'\n');print(json.dumps(meta,ensure_ascii=False))
