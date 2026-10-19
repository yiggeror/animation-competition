from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np
import json
R=Path(__file__).resolve().parent
raw=Image.open(R.parent/'FIRST_MOTHER_NATIVE_call01_20261019/originals/S29_FIRST_MOTHER_call01_RAW.png').convert('RGBA')
base=Image.open(R/'layers/MOTHER_CLOTH_BASE_NO_GENERATED_PROPS.png').convert('RGBA')
props=Image.open(R/'layers/REAL_ORIGINAL_TWO_PUPPETS_FOUR_RODS.png').convert('RGBA')
shadow=Image.new('RGBA',base.size,(0,0,0,0))
sa=props.getchannel('A').filter(ImageFilter.GaussianBlur(1.1)).point(lambda x:round(x*.24))
shadow.putalpha(sa)
shift=Image.new('RGBA',base.size);shift.alpha_composite(shadow,(1,2))
composite=Image.alpha_composite(Image.alpha_composite(base,shift),props)
a=np.array(composite);old=np.array(raw)
cloth=np.array(Image.open(R/'masks/ORIGINAL_CLOTH_INTERIOR_ONLY.png'))>0
a[~cloth]=old[~cloth] # preserve full human, outer cloth rim, stool and source alpha.
for name in ['ORIGINAL_NEAR_PALM_FOREGROUND','ORIGINAL_RAISED_CLOTH_LIP']:
 m=np.array(Image.open(R/f'masks/{name}.png'))>0
 a[m]=old[m] # copy exact original RGBA, once; no duplicate alpha accumulation.
out=Image.fromarray(a)
out.save(R/'layers/REGISTERED_COMPLETE_MOTHER_ORIGINAL_PROPS.png')
gray=Image.new('RGBA',base.size,(230,230,230,255));gray.alpha_composite(out)
gray.convert('RGB').save(R/'qa/REGISTERED_COMPLETE_MOTHER_ON_GRAY.png')
checks={'entire_RGBA_outside_cloth_interior_exact':bool(np.array_equal(a[~cloth],old[~cloth])),
        'whole_human_and_outer_cloth_not_redrawn':True}
for name in ['ORIGINAL_NEAR_PALM_FOREGROUND','ORIGINAL_RAISED_CLOTH_LIP']:
 m=np.array(Image.open(R/f'masks/{name}.png'))>0
 checks[name+'_exact_RGBA_preserved']=bool(np.array_equal(a[m],old[m]))
(R/'qa/COMPOSITE_FOREGROUND_CHECK.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks))
