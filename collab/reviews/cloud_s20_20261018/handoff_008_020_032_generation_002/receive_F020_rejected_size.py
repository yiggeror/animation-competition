"""Preserve actual 1671x941 raw. No resize, padding, crop-registration or composite."""
from pathlib import Path
import json,hashlib,shutil,struct,base64,datetime
from PIL import Image
P=Path(__file__).resolve().parent;F=P/'F020';Q=F/'qa'
original=Path('/workspace/generated_images/exec-83a09d15-e031-4244-a6a4-2db43bf73003.png')
raw=F/'S20_F020_attempt001_raw_1671x941.png';shutil.copyfile(original,raw)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dim=list(struct.unpack('>II',raw.read_bytes()[16:24]));assert dim==[1671,941]
assert base64.b64decode(json.loads((F/'tool_return_original.json').read_text())['image_url'].split(',',1)[1])==raw.read_bytes()
im=Image.open(raw).convert('RGBA');bg=Image.new('RGBA',im.size,'#bdc1c4');bg.alpha_composite(im)
bg.convert('RGB').save(Q/'raw_full_gray_1671x941.png')
bg.crop((600,315,990,490)).resize((1560,700),Image.Resampling.NEAREST).convert('RGB').save(Q/'raw_shared_grips_QA_only_4x.png')
status=json.loads((F/'status.json').read_text());status.update({'state':'AUTHOR_REJECTED_DIMENSION_MISMATCH','in_flight':0,'new_raws':1,
 'actual_size':dim,'required_size':[1672,941],'raw_path':raw.name,'raw_sha256':sha(raw),'original_tool_path':str(original),
 'retained_as_drawing':False,'accepted_png':None,'black_domain_composite_executed':False,'raw_resized_padded_or_registered':False,
 'F032_submitted':False,'automatic_retry':False})
(F/'status.json').write_text(json.dumps(status,indent=2)+'\n')
review={'result':'AUTHOR_REJECTED_DIMENSION_MISMATCH','raw_sha256':sha(raw),'original_kept_unmodified':True,
 'actual_png_IHDR':dim,'required_png_IHDR':[1672,941],'width_difference_pixels':-1,
 'actual_image_seen':True,'pose_contact_gate':'NOT_SIGNED / size gate prevents authorized black-domain registration',
 'reason':'One column short. User contract forbids resampling, padding or cropping to force required dimensions.',
 'no_composite_or_repaired_frame':True,'F032_submitted':False,'one_authorized_F020_attempt_consumed':True,
 'no_retry':True,'cause_claim':'Observed actual PNG dimensions only; no assertion about tool internals.',
 'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(F/'author_visual_review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'F020':'REJECTED_DIMENSION_MISMATCH','actual_size':dim,'raw_sha256':sha(raw),'F032_submitted':False,'raw_modified':False},indent=2))
