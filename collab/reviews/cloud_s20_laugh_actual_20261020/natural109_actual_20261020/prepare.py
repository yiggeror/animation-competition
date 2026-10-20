"""Adopt complete natural child109 and existing physical boundary geometry.

No new character pixels: extract unchanged connected grandmother; place the
complete child at its native position. Remove detached112 shaft pixels only.
"""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image
from scipy.ndimage import label

P=Path(__file__).resolve().parent
ROOT=P.parents[3]
ASSETS=ROOT/'assets/chars/g20'
alpha=np.array(Image.open(P/'sources/CHILD109_ADOPTED_NATIVE_ALPHA.png'))
assert hashlib.sha256((P/'sources/CHILD109_ADOPTED_NATIVE_ALPHA.png').read_bytes()).hexdigest()=='c3b6a749b14c5a361dcc9515f5003a9c7f89ccd89e31d511316df5830543094d'
original=np.array(Image.open(ASSETS/'F104_people.png'))
components,_=label(original[:,:,3]>0)
grandmother_id=components[100,1100]
assert grandmother_id and np.sum(components==grandmother_id)>150000
grandmother=original.copy();grandmother[components!=grandmother_id]=0
Image.fromarray(grandmother).save(P/'GRANDMA104_UNCHANGED_COMPONENT.png')
pair=Image.alpha_composite(Image.fromarray(grandmother),Image.fromarray(alpha))
pair.save(P/'PAIR109_NATIVE_COMPOSITE.png')
g=json.loads((P/'sources/CONSUMER_GEOMETRY.json').read_text())
g['paper_state']={'turtle':g['turtle'],'crane':g['crane']}
(P/'F109_RENDER_GEOMETRY.json').write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n')
finite_path=P.parent/'junctions104_132/finite_motion_inputs_107_109_129_131/FINITE_MOTION_INPUTS.json'
finite=json.loads(finite_path.read_text())
changes=[]
for f in [104,112]:
 state=next(s for s in finite['states'] if s['frame']==f)
 state={**state,'camera':finite['camera'],'masterToCAM20':finite['masterToCAM20'],'paper_state':{'turtle':state['turtle'],'crane':state['crane']}}
 (P/f'F{f:03}_FINITE_BOUNDARY.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
 b=np.array(Image.open(ASSETS/f'F{f:03}_people.png'))
 mask=np.zeros(b.shape[:2],bool)
 if f==112:
  # Both complete human components start atx369 or later. This exact region
  # contains only disconnected old diagnostic wood, no character contour.
  mask[:,:350]=b[:,:350,3]>0
 out=b.copy();out[mask]=0
 assert np.array_equal(out[:,350:],b[:,350:])
 Image.fromarray(out).save(P/f'F{f:03}_PEOPLE_NO_DETACHED_WOOD.png')
 Image.fromarray(mask.astype('uint8')*255).save(P/f'F{f:03}_DETACHED_WOOD_MASK.png')
 changes.append({'frame':f,'externalOldWoodPixelsRemoved':int(mask.sum()),'allPixelsAtOrBeyondX350Unchanged':True,'geometrySource':'ad0f2942 finite boundary, unchanged native grip rays; supersedes early arbitrary A/H geometry'})
manifest={'sourceCommit':'1701eecbdd6bb3a0ba61a5ae6c4bd69908d636b1','sourceChildSHA256':g['character_sha256'],'grandmotherPixels':'Exact complete positive-alpha component from original104, also byte-identical in112; child replaced as a complete native drawing','sourcePromptAndRaw':'Source raw_call_id/raw_sha256 retained in unmodified CONSUMER_GEOMETRY.json; no new model call','boundaryPreparation':changes,'exposureCandidate':[{'start':104,'end':106,'source':'old104, physical finite boundary'},{'start':107,'end':110,'source':'natural complete109, not failed107 raw'},{'start':111,'end':112,'source':'old112 drawing, physical finite boundary'}],'acceptance':'Actual continuity pending; exposure is only an adjacency candidate'}
(P/'source_and_consumption.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(manifest,ensure_ascii=False))
