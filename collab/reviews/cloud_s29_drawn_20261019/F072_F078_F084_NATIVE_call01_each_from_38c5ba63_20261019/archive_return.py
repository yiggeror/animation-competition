from pathlib import Path
from PIL import Image
import json,sys,base64,hashlib,shutil,re,datetime
R=Path(__file__).resolve().parent;f=int(sys.argv[1]);d=R/f'F{f:03d}'
result=json.loads((d/'COMPLETE_TOOL_RETURN_WITH_DATAURL.json').read_text());b64=result['image_url'].split(',',1)[1];data=base64.b64decode(b64)
hint=result.get('output_hint','');match=re.search(r'/workspace/generated_images/[^\s]+\.png',hint);assert match,hint
host=Path(match.group());assert host.read_bytes()==data
out=d/f'originals/S29_F{f:03d}_call01_RAW_UNTOUCHED.png';assert not out.exists();shutil.copyfile(host,out);assert out.read_bytes()==data
im=Image.open(out);meta=dict(output_hint=hint,tool_result_keys=list(result),dataURL_prefix=result['image_url'].split(',',1)[0]+',',base64_SHA256=hashlib.sha256(b64.encode()).hexdigest(),base64_chars=len(b64),host_path=str(host),exact_tool_dataURL_equals_host_and_archive_base64=True)
(d/'TOOL_RETURN_TRANSPORT_METADATA.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
rawmeta=dict(host_path=str(host),archived_path=str(out),SHA256=hashlib.sha256(data).hexdigest(),image_mode=im.mode,image_size=im.size,alpha_extrema=im.getchannel('A').getextrema()if im.mode=='RGBA'else None,archive_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(d/'HOST_RAW_METADATA.json').write_text(json.dumps(rawmeta,indent=2)+'\n');state=json.loads((d/'CALL01_STATE.json').read_text());state.update(status='RETURNED_ARCHIVED_NO_RETRY',raw_SHA256=rawmeta['SHA256'],utc_return_archive=rawmeta['archive_utc']);(d/'CALL01_STATE.json').write_text(json.dumps(state,indent=2)+'\n');print(json.dumps(rawmeta))
