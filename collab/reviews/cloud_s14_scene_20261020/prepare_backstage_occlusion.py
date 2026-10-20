"""Actual-source occlusion study; no invented anatomy or image generation.

Keep exact G095 pixels that differ from its published fixed props. Only exposed
lower-body pixels will be consumed in a candidate; hidden upper limbs are not
asserted to be a new post-hang drawing.
"""
from pathlib import Path
from PIL import Image
import numpy as np
import hashlib, json

R=Path(__file__).parent
repo=R.parents[2]
source=repo/'collab/reviews/20261019_2247_s14_second_clip_six_locked/grandma_take_first_peg_030_036_inputs/G072_G095_second_clamp_inputs/G095_complete_registered_candidate.png'
stool=repo/'collab/reviews/20261019_2247_s14_second_clip_six_locked/grandma_throw_inputs/G000_locked_complete_rigid_work_stool.png'
cloth=R/'G095_FIXED_DRAWN_SHEET_AND_TWO_PEGS_RGBA.png'
a=np.array(Image.open(source).convert('RGBA'))
props=Image.open(cloth).convert('RGBA')
props.alpha_composite(Image.open(stool).convert('RGBA'))
p=np.array(props)
different=np.any(a!=p,axis=2)&(a[:,:,3]>0)
yy,xx=np.indices(different.shape)
# The entire person is left of x750 and above the old stool seat. Source props
# outside this domain cannot be person pixels, even if their alpha differs.
different&=(xx>=350)&(xx<750)&(yy>=275)&(yy<1026)
body=a.copy();body[~different]=0
out=R/'G095_EXACT_PERSON_PIXELS_OCCLUSION_STUDY.png'
Image.fromarray(body).save(out)

# Keep physical figure scale, lower from the original stool onto the same ground
# plane. Center the fixed whole person at the existing cloth's horizontal center.
scale=.335
old={'x':355.,'y':175.,'sc':scale}
ground=old['y']+1180*scale
target={'x':644.-530.*scale,'y':ground-1024*scale,'sc':scale}
rec={
 'status':'ACTUAL_SOURCE_BACKSTAGE_OCCLUSION_STUDY_NOT_NEW_DRAWING',
 'source':str(source.relative_to(repo)),
 'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'bodyPixels':out.name,'bodySHA256':hashlib.sha256(out.read_bytes()).hexdigest(),
 'extraction':'Exact source RGBA where completeG095 differs from the same fixed original cloth/pegs/stool. No RGB repaint, per-limb transform or anatomy synthesis. Any upper-body edge over an old prop is diagnostic only and must be fully occluded.',
 'oldWholeFigureTransform':old,'backstageWholeFigureTransform':target,
 'nativeShoeSupport':[530.,1024.],'roomShoeSupport':[644.,ground],
 'nativeOldWorkStoolFloor':1180.,
 'positionBasis':'Existing original room floor at the original work stool baseline; whole-person center530 registered to room644 within fixed original curtain. Initial room650 study exposed a fingertip at the existing right curtain edge, so the entire person moves6room pixels left, with no curtain/furniture change. This is a2D candidate registration pending director choice, not an independently calibratedS15 world position.',
 'upperBodyConservativeNativeDomain':{'x':[350,750],'y':[275,550]},
 'cutOmission':'095→096 omits descent/approach/bend;131→132 returns after the hang. No visible walking or arm lowering is fabricated.',
 'newImageCalls':0,'newDrawings':0,'S15Changed':False
}
(R/'BACKSTAGE_OCCLUSION_STUDY.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(rec,ensure_ascii=False))
