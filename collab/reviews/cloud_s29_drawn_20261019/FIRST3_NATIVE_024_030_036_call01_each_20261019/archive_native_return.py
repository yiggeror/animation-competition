from pathlib import Path
import json,sys,shutil,hashlib,base64,time
from PIL import Image

R=Path(__file__).resolve().parent
frame=int(sys.argv[1]);host=Path(sys.argv[2]);F=R/f'F{frame:03d}'
ret=json.loads((F/'requests/tool_return_FULL_ORIGINAL.json').read_text())
dest=F/f'originals/S29_F{frame:03d}_call01_RAW_UNTOUCHED.png'
assert not dest.exists(),'Original already archived: do not overwrite'
shutil.copyfile(host,dest)
b=dest.read_bytes();assert b==host.read_bytes()==base64.b64decode(ret['image_url'].split(',',1)[1])
im=Image.open(dest);meta={'frame':frame,'host_original':str(host),'archived_original':str(dest),'sha256':hashlib.sha256(b).hexdigest(),
 'size':list(im.size),'mode':im.mode,'bytes':len(b),'host_archive_tool_dataURL_bytes_identical':True,
 'alpha_extrema':im.getchannel('A').getextrema() if 'A' in im.getbands() else None,'archived_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
(F/'originals/RAW_METADATA.json').write_text(json.dumps(meta,indent=2)+'\n')
rgba=im.convert('RGBA');gray=Image.new('RGBA',im.size,(235,235,235,255));gray.alpha_composite(rgba)
gray.convert('RGB').save(F/'qa/FULL_RAW_ON_GRAY.png')
for name,box in [('C1_NEAR_SUPPORT',(380,600,650,850)),('FAR_COMPLETE_ARM',(465,400,990,825)),('C2_FAR_PINCH',(710,540,990,850))]:
 gray.crop(box).convert('RGB').save(F/f'qa/{name}_ACTUAL_RAW_CROP.png')
s=json.loads((F/'call_state.json').read_text());s.update(raw_outputs=1,status='RAW_RETURNED_PENDING_ACTUAL_GATE',raw_sha256=meta['sha256']);(F/'call_state.json').write_text(json.dumps(s,indent=2)+'\n')
g=json.loads((R/'GROUP_STATE.json').read_text());g['raw_outputs']=sum(json.loads((R/f'F{f:03d}/call_state.json').read_text())['raw_outputs'] for f in [24,30,36]);g['state']=f'F{frame:03d}_RAW_RETURNED_PENDING_ACTUAL_GATE';(R/'GROUP_STATE.json').write_text(json.dumps(g,indent=2)+'\n')
print(json.dumps(meta,indent=2))
