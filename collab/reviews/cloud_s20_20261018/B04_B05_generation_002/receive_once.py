"""Retain one actual return; strict original black-domain restoration."""
from pathlib import Path
import sys,json,re,base64,hashlib,shutil
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;f=int(sys.argv[1]);F=P/f'F{f:03}';assert not (F/'raw_original.png').exists()
r=json.loads((F/'tool_return_original.json').read_text());raw=Path(re.search(r'/workspace/generated_images/[^\s]+\.png',r['output_hint']).group());data=raw.read_bytes();assert base64.b64decode(r['image_url'].split(',',1)[1])==data
shutil.copyfile(raw,F/'raw_original.png');im=Image.open(raw).convert('RGBA');raw_size=list(im.size);padded=False
if im.size==(1671,941):
 out=Image.new('RGBA',(1672,941));out.paste(im,(0,0));im=out;padded=True
else:assert im.size==(1672,941),im.size
args=json.loads((F/'tool_args_exact.json').read_text());source=Path(args['referenced_image_paths'][0]);mask=Path(args['referenced_image_paths'][2]);A=np.array(Image.open(source).convert('RGBA'));M=np.array(Image.open(mask).convert('L'))>0;O=A.copy();O[M]=np.array(im)[M];assert np.array_equal(A[~M],O[~M])
candidate=F/f'S20_F{f:03}_candidate.png';Image.fromarray(O).save(candidate);bg=Image.new('RGBA',(1672,941),'#bdc1c4');bg.alpha_composite(Image.fromarray(O));bg.convert('RGB').save(F/'actual_full_gray.jpg',quality=96)
for name,box in [('actual_contacts_3x',(690,270,1010,475)),('actual_child_elbows_wrists_3x',(575,285,890,485))]:bg.crop(box).resize(((box[2]-box[0])*3,(box[3]-box[1])*3),Image.Resampling.NEAREST).convert('RGB').save(F/(name+'.jpg'),quality=96)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
meta={'original_tool_path':str(raw),'raw_original_sha256':sha(F/'raw_original.png'),'raw_size':raw_size,'rightmost_transparent_column_only':padded,'tool_data_equals_raw':True,'candidate':candidate.name,'candidate_sha256':sha(candidate),'strict_black_domain_RGBA_changes':0,'black_pixels':int((~M).sum()),'white_pixels':int(M.sum()),'source_sha256':sha(source),'mask_sha256':sha(mask),'prompt_sha256':sha(F/'prompt_submitted_zh.txt'),'request_sha256':sha(F/'tool_args_exact.json')}
(F/'receipt_and_protection.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');s=json.loads((F/'status.json').read_text());s.update({'state':'RECEIVED_REPROTECTED_AWAITING_ACTUAL_REVIEW','actual_calls_this_attempt':1,'new_raws':1});(F/'status.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n');print(json.dumps(meta,ensure_ascii=False))
