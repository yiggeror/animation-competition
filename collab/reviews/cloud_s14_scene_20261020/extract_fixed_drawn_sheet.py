"""Extract the actual locked sheet/closed pegs; never generates or repaints anatomy."""
from pathlib import Path
from PIL import Image
import numpy as np
R=Path(__file__).parent
p=R.parent/'20261019_2247_s14_second_clip_six_locked/grandma_take_first_peg_030_036_inputs/G072_G095_second_clamp_inputs/G095_complete_registered_candidate.png'
sheet=p.parents[2]/'grandma_fall_inputs/G027_upper_contact_repair/G027_complete_sheet_whole_registered.png'
cloth=Image.open(sheet).convert('RGBA')
a=np.array(Image.open(p).convert('RGBA'));Y,X=np.indices(a.shape[:2])
# The already published full source sheet supplies the area hidden by G095's
# withdrawn hand. It is the exact same sheet used by the author's assembly.
m=((X>=676)&(X<=730)&(Y>=266)&(Y<=285))|((X>=768)&(X<=796)&(Y>=243)&(Y<=291))
pegs=a.copy();pegs[~m]=0;cloth.alpha_composite(Image.fromarray(pegs))
cloth.save(R/'G095_FIXED_DRAWN_SHEET_AND_TWO_PEGS_RGBA.png')
Image.fromarray(np.uint8(np.array(cloth)[:,:,3]>0)*255).save(R/'G095_FIXED_SHEET_SOURCE_DOMAIN.png')
