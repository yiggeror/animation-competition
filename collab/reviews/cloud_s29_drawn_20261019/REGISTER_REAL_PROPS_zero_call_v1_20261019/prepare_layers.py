"""Review-only, zero-generation removal of generated prop pixels on approved cloth.

No human, palm/wrist or outer cloth geometry is drawn or warped. The original
RGBA is retained; masks and donor pixels are explicit and replayable.
"""
from pathlib import Path
import sys, json, hashlib
sys.path.insert(0, '/tmp/s29-image-tools')
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

ROOT = Path(__file__).resolve().parent
REVIEW = ROOT.parent
RAW = REVIEW/'FIRST_MOTHER_NATIVE_call01_20261019/originals/S29_FIRST_MOTHER_call01_RAW.png'
for name in ['layers', 'masks', 'qa', 'sources', 'scene', 'contacts']:
    (ROOT/name).mkdir(exist_ok=True)
im = Image.open(RAW).convert('RGBA')
a = np.array(im)
def mask_polys(polys):
    m=Image.new('L',im.size);d=ImageDraw.Draw(m)
    for p in polys:d.polygon(p,fill=255)
    return np.array(m)>0

# Generated prop footprints, traced on the actual returned image, not old input.
footprints=[
    [[451,807],[464,787],[487,770],[517,754],[547,747],[566,751],[581,763],
     [568,780],[539,775],[516,779],[494,796],[488,814],[502,843],[517,878],
     [503,889],[482,843],[459,833]],
    [[562,756],[588,766],[622,766],[663,770],[699,774],[733,778],[759,789],
     [800,801],[853,813],[856,824],[811,832],[761,838],[714,839],[676,832],
     [633,828],[599,815],[576,794]],
    [[680,824],[705,827],[701,895],[715,905],[711,913],[653,916],
     [650,906],[680,896]],
    [[300,879],[333,852],[375,835],[418,829],[467,832],[497,842],
     [520,861],[533,873],[563,875],[587,882],[610,894],[615,907],
     [601,916],[575,917],[552,910],[527,905],[514,902],[515,927],
     [483,930],[474,911],[397,912],[400,925],[371,926],[365,902],
     [335,899],[303,892]]
]
m = mask_polys(footprints)
rod_mask=Image.new('L',im.size);rd=ImageDraw.Draw(rod_mask)
for p,q in [((691,830),(977,908)),((707,845),(946,936)),
            ((530,905),(874,970)),((550,916),(866,995))]:
    rd.line([p,q],fill=255,width=15)
    for x,y in [p,q]:rd.ellipse((x-7,y-7,x+7,y+7),fill=255)
m |= np.array(rod_mask)>0
rgb=a[:,:,:3].astype('int16')
prop_domain=mask_polys([[[295,874],[332,836],[443,777],[507,747],[569,744],
                        [632,760],[726,771],[805,794],[865,812],[986,894],
                        [985,921],[958,948],[880,1003],[810,987],
                        [686,956],[533,935],[476,935],[366,932],[296,900]]])
warm_or_green=(np.maximum(rgb[:,:,0],rgb[:,:,1])>rgb[:,:,2]+7)
neutral_dark=(rgb.max(axis=2)-rgb.min(axis=2)<17)&(rgb.max(axis=2)<75)
# The original tracing is supplemented by exact source-color selection in the
# bounded prop domain, so the red/black head, tan leg tips and rod AA cannot
# remain as unmasked islands. Original cloth is blue, never this leather palette.
m |= prop_domain & (warm_or_green|neutral_dark)
m = ndimage.binary_dilation(m, iterations=5)

# All edits remain inside the existing cloth; the exterior silhouette is fixed.
cloth = mask_polys([[[549,709],[645,723],[740,709],[791,712],[829,741],
                    [863,779],[902,824],[946,873],[989,900],[998,916],
                    [964,999],[947,1047],[917,1033],[898,1004],[824,1011],
                    [749,1011],[684,989],[638,955],[606,954],[545,991],
                    [520,1002],[476,990],[419,967],[359,940],[311,917],
                    [287,899],[321,851],[360,802],[401,771],[457,746]]])
cloth = ndimage.binary_erosion(cloth, iterations=5)
Image.fromarray(cloth.astype('uint8')*255).save(ROOT/'masks/ORIGINAL_CLOTH_INTERIOR_ONLY.png')
near_region=mask_polys([[[418,663],[493,663],[524,676],[546,699],[560,723],
                        [561,748],[552,762],[531,773],[505,774],[478,760],
                        [454,743],[421,731]]])
hand_seed=(rgb[:,:,0]>205)&(rgb[:,:,0]>rgb[:,:,1]+17)&(rgb[:,:,1]>rgb[:,:,2]+9)
hand=ndimage.binary_dilation(hand_seed & near_region,iterations=2)&near_region
far_region=mask_polys([[[770,650],[826,655],[869,676],[900,704],[906,738],
                       [896,773],[869,781],[840,760],[816,741],[789,722],[771,704]]])
skin=ndimage.binary_dilation(hand_seed & (near_region|far_region),iterations=2)
m &= cloth & ~skin & ~hand

# Preserve the natural upper lip exactly; it is an independent foreground layer.
lip=mask_polys([[[553,709],[647,724],[739,708],[792,711],[824,734],
                [858,774],[901,820],[939,869],[950,888],[930,879],
                [899,852],[867,819],[835,789],[808,775],[781,766],
                [746,762],[706,764],[663,763],[618,757],[577,749],
                [554,744]]])
lip &= ~m

# Mask is the only edit domain. Covered areas receive actual clean mother cloth
# print, then their blue substrate is matched; no human/prop drawing is invented.
# Keep visible cloth print in broad holes rather than leaving large blue smears.
# Exemplar filling copies ONLY actual untouched cloth patches. Match every
# known target-boundary pixel, then copy the still-unknown pixels. This avoids
# Telea petal smears and the visible rectangular tonal islands of Poisson fill.
p=17;h=p//2
blue_only=(rgb[:,:,2]>=rgb[:,:,1]+4)&(rgb[:,:,2]>=rgb[:,:,0]+8)
valid=cv2.erode((cloth&~m&blue_only&~skin&~hand).astype('uint8'),np.ones((p,p),'uint8'))>0
cy,cx=np.where(valid & (np.indices(m.shape)[0]%4==0) & (np.indices(m.shape)[1]%4==0))
patches=np.stack([a[y-h:y+h+1,x-h:x+h+1,:3] for y,x in zip(cy,cx)])
P=patches.reshape(len(patches),-1).astype('float32')/255
P2=P*P
remaining=m.copy();repair=a[:,:,:3].copy();steps=0
while remaining.any():
    edge=remaining & ~ndimage.binary_erosion(remaining)
    count=cv2.boxFilter(remaining.astype('float32'),-1,(p,p),normalize=False)
    priority=np.where(edge,count*(p*p-count),-1)
    y,x=np.unravel_index(np.argmax(priority),priority.shape)
    region=np.s_[y-h:y+h+1,x-h:x+h+1]
    unknown=remaining[region]
    known=np.repeat((~unknown).reshape(-1),3).astype('float32')
    target=repair[region].reshape(-1).astype('float32')/255
    score=P2@known-2*(P@(target*known))
    # Prefer nearby real cloth when equivalent; do not alter donor RGB.
    score+=((cy-y)**2+(cx-x)**2).astype('float32')*1e-8*known.sum()
    best=int(np.argmin(score))
    tile=repair[region];tile[unknown]=patches[best][unknown]
    remaining[region]=False;steps+=1
    if steps%200==0:print('real-cloth patch fill',steps,'remaining',int(remaining.sum()),flush=True)
# Match the native blue substrate continuously across patch boundaries. Only
# the actual original cotton print supplies the bright motif; copied fold-edge
# fragments and donor background offsets are not introduced as square islands.
print_pixels=cloth & (rgb[:,:,0]>105)&(rgb[:,:,1]>120)&(rgb[:,:,2]>140)
substrate_holes=(m|ndimage.binary_dilation(print_pixels,iterations=2))&cloth
substrate=cv2.inpaint(a[:,:,:3],substrate_holes.astype('uint8')*255,7,cv2.INPAINT_TELEA)
flower_alpha=np.clip((repair[:,:,0].astype('float32')-75)/100,0,1)[...,None]
repair=(substrate*(1-flower_alpha)+repair*flower_alpha).round().clip(0,255).astype('uint8')
out=a.copy();out[m,:3]=repair[m]
Image.fromarray(out).save(ROOT/'layers/MOTHER_CLOTH_BASE_NO_GENERATED_PROPS.png')
Image.fromarray(m.astype('uint8')*255).save(ROOT/'masks/GENERATED_PROP_REMOVAL_ONLY.png')
Image.fromarray(lip.astype('uint8')*255).save(ROOT/'masks/ORIGINAL_RAISED_CLOTH_LIP.png')

# Native skin pixels and their actual ink/AA contour. No hand repainting.
Image.fromarray(hand.astype('uint8')*255).save(ROOT/'masks/ORIGINAL_NEAR_PALM_FOREGROUND.png')
for name,mask in [('ORIGINAL_NEAR_PALM_FOREGROUND',hand),('ORIGINAL_RAISED_CLOTH_LIP',lip)]:
    layer=np.zeros_like(a);layer[mask]=a[mask]
    Image.fromarray(layer).save(ROOT/f'layers/{name}.png')

gray=Image.new('RGBA',im.size,(230,230,230,255));gray.alpha_composite(Image.fromarray(out))
gray.convert('RGB').save(ROOT/'qa/CLEANED_BASE_ON_GRAY.png')
facts={'imagegen_requests_this_stage':0,'original':str(RAW.relative_to(REVIEW)),
       'original_sha256':hashlib.sha256(RAW.read_bytes()).hexdigest(),
       'edited_pixels':int(m.sum()),'unchanged_RGBA_outside_explicit_mask':bool(np.array_equal(a[~m],out[~m])),
       'unchanged_entire_alpha':bool(np.array_equal(a[:,:,3],out[:,:,3])),
       'original_hand_pixels_in_base_unchanged':bool(np.array_equal(a[hand],out[hand])),
       'source_candidates_actual_BLUE_cloth_only':True,'method':'17px exemplar from actual BLUE cloth only (all human excluded), known-boundary SSD; native blue substrate normalization removes donor tonal seams; original print motif, no generated texture or human synthesis',
       'patch_candidates':len(patches),'patch_fill_steps':steps,
       'cloth_outer_edge_erosion_px':5,'hand_foreground':'original skin+2px actual ink/AA neighborhood, no redraw',
       'puppet_removal_polygons_actual_source_px':footprints}
(ROOT/'qa/CLOTH_EDIT_AND_PROTECTION_FACTS.json').write_text(json.dumps(facts,indent=2)+'\n')
print(json.dumps({k:v for k,v in facts.items() if k not in ['puppet_removal_polygons_actual_source_px']},indent=2))
