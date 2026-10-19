"""Narrow editable return to retain real accepted008 lower legs and locked feet.
No donor transformation or new painting; the new020 dress remains foreground.
"""
from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image
from scipy.ndimage import label,binary_fill_holes,binary_dilation,binary_closing
P=Path(__file__).resolve().parent;F=P/'F020';R=F/'same_raw_minimal_registration_001'
A=np.array(Image.open(P/'F008/S20_F008_accepted.png').convert('RGBA'))
B=np.array(Image.open(R/'F020_same_raw_right_transparent_column_copy.png').convert('RGBA'))
old=np.array(Image.open(R/'F020_mask_return_candidate.png').convert('RGBA'))
M=np.array(Image.open(F/'inputs/04_edit_white.png'))==255
def garment(a):
 rr,gg,bb=a[:,:,:3].astype(float).transpose(2,0,1)
 q=(a[:,:,3]>180)&(rr>170)&(gg>130)&(bb<gg*.67)&(rr>gg+10)
 q[:480]=False;q[750:]=False;q[:,:450]=False;q[:,885:]=False
 cc,n=label(q);sizes=np.bincount(cc.ravel());sizes[0]=0
 solid=binary_fill_holes(cc==sizes.argmax())
 solid=binary_closing(solid,structure=np.ones((3,15),bool))
 return binary_dilation(solid,iterations=2)
G8,G20=garment(A),garment(B)
yy,xx=np.indices(M.shape);lower=(yy>=700)&(xx>=450)&(xx<885)&M
out=old.copy();out[lower]=A[lower]
# Clear old skirt occupancy outside the new dress, then lay the actual new dress
# in front of the retained actual legs. There is no old gesture/body reference.
clear=lower&G8&~G20;out[clear]=0
overlay=lower&G20&(B[:,:,3]>0);out[overlay]=B[overlay]
# A tiny under-hem bridge uses the same020 raw skin where the new hem is above
# the old one, so the retained legs do not expose a transparent strip.
skin20=(B[:,:,3]>180)&(B[:,:,0]>180)&(B[:,:,1]>120)&(B[:,:,2]>100)&(B[:,:,2]>B[:,:,1]*.65)
bridge=clear&skin20;out[bridge]=B[bridge]
assert not np.any(out[~M]!=A[~M])
assert np.array_equal(out[750:],A[750:])
file=R/'F020_same_raw_lower_legs_protected_candidate.png';Image.fromarray(out).save(file)
Image.fromarray((lower*255).astype('uint8')).save(R/'mask_lower_leg_protected_return.png')
Image.fromarray((overlay*255).astype('uint8')).save(R/'mask_actual020_dress_foreground.png')
bg=Image.new('RGBA',(1672,941),'#bcc1c5');bg.alpha_composite(Image.fromarray(out));bg=bg.convert('RGB');bg.save(R/'candidate_with_retained_legs_full_gray.png')
bg.crop((515,700,720,930)).resize((820,920),Image.Resampling.NEAREST).save(R/'retained_legs_under_hem_4x.png')
report=json.loads((R/'verification.json').read_text());report.update({'candidate':str(file.relative_to(F)),
 'additional_zero_call_return':'Retain complete actual accepted008 lower legs/shoes at original pixels; actual020 new skirt foreground, skin bridge only from same020 raw.',
 'leg_donor_source':'../F008/S20_F008_accepted.png','donor_translation':[0,0],'donor_scale':[1,1],
 'original_raw_unchanged':True,'black_domain_RGBA_changed':0,'all_rows_y750_plus_equal_actual008':True,
 'leg_local_stretch_or_painting':False,'earlier_mask_return_ankle_seam':'Observed and superseded by protected full-leg source return.',
 'actual_hand_occlusion_and_seam_review':'PENDING_FINAL_VIEW'})
(R/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Retained real008 lower legs without transform; actual020 skirt kept. Candidate ready for direct seam view.')
