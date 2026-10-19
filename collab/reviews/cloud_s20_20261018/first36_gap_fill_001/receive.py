from pathlib import Path
import json,sys,hashlib,re,base64,shutil,struct
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;f=int(sys.argv[1]);F=P/f'F{f:03}';r=json.loads((F/'tool_return_original.json').read_text());rawpath=Path(re.search(r'/workspace/generated_images/[^\s]+\.png',r['output_hint']).group());raw=rawpath.read_bytes();assert base64.b64decode(r['image_url'].split(',',1)[1])==raw
sz=struct.unpack('>II',raw[16:24]);attempt=json.loads((F/'status.json').read_text())['attempts_started'];copy=F/f'S20_F{f:03}_attempt{attempt:03}_raw_{sz[0]}x{sz[1]}.png';shutil.copyfile(rawpath,copy);Araw=Image.open(copy).convert('RGBA');reg=False
if sz==(1671,941):
 B=Image.new('RGBA',(1672,941));B.paste(Araw,(0,0));B.save(F/'same_raw_rightmost_transparent_column.png');assert np.array_equal(np.array(B)[:,:1671],np.array(Araw));Araw=B;reg=True
else:assert sz==(1672,941),sz
m=json.loads((F/'input_manifest.json').read_text());A=np.array(Image.open(m['source']).convert('RGBA'));M=np.array(Image.open(F/'inputs/04_edit_white.png'))>0;out=A.copy();out[M]=np.array(Araw)[M];assert np.array_equal(out[~M],A[~M])
file=F/f'S20_F{f:03}_candidate.png';Image.fromarray(out).save(file)
im=Image.fromarray(out);bg=Image.new('RGBA',im.size,'#bdc1c4');bg.alpha_composite(im);bg.convert('RGB').save(F/'qa/actual_full_gray.png');box=(565,270,1115,550);bg.crop(box).resize((1650,840),Image.Resampling.NEAREST).convert('RGB').save(F/'qa/actual_contacts_3x.png')
s=json.loads((F/'status.json').read_text());s.update({'state':'AWAITING_AUTHOR_ACTUAL_REVIEW','in_flight':0,'new_raws':len(list(F.glob('S20*_raw_*.png'))),'actual_size':list(sz),'raw_path':copy.name,'raw_sha256':hashlib.sha256(raw).hexdigest(),'original_tool_path':str(rawpath),'same_raw_rightmost_transparent_column_only':reg,'original_columns_unchanged':True,'candidate':file.name,'candidate_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'black_domain_exact':True});(F/'status.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n');print(f,sz,'raw retained, protected composite ready')
