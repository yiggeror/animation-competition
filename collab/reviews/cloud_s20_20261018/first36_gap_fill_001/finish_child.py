"""Zero-call protection return: real rod/leg donors, no generated pose substitution."""
from pathlib import Path
import sys,json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import label,binary_fill_holes,binary_dilation,binary_closing
P=Path(__file__).resolve().parent;f=int(sys.argv[1]);F=P/f'F{f:03}';m=json.loads((F/'input_manifest.json').read_text());s=json.loads((F/'status.json').read_text());A=np.array(Image.open(m['source']).convert('RGBA'));raw=F/s['raw_path'];B=np.array(Image.open(F/'same_raw_rightmost_transparent_column.png' if s['same_raw_rightmost_transparent_column_only'] else raw).convert('RGBA'));out=np.array(Image.open(F/s['candidate']).convert('RGBA'));M=np.array(Image.open(F/'inputs/04_edit_white.png'))>0
rr,gg,bb=B[:,:,:3].astype(float).transpose(2,0,1)
skin=(B[:,:,3]>180)&(rr>170)&(gg>105)&(bb>70)&(rr>gg+15)&(gg>bb+10)&(bb>gg*.60)
C=np.array(Image.open(F/'art/child_F020_complete_pose.png').convert('RGBA'))
hands=binary_dilation(C[:,:,3]>180,iterations=5)
# Restore fixed source shafts AND empty surroundings, excluding actual real hand.
reg=json.loads((P.parent/'F000/f000_scene_gate_001/registration_input.json').read_text());corr=Image.new('L',(1672,941));d=ImageDraw.Draw(corr)
for role,x0,x1 in [('T_H',782,922),('T_S',772,922)]:
 r=reg['rods'][role];d.line([(x,r['slope']*x+r['intercept']) for x in [x0,x1]],fill=255,width=27)
restore=(np.array(corr)>0)&M&~hands;out[restore]=0
fixed_rod=np.array(Image.open(P.parent/'F008_corrected_input_001/local_masks/protect_four_real_rods.png'))>0
out[restore&fixed_rod]=A[restore&fixed_rod]
# Restore source legs beneath actual new dress without moving donor pixels.
def garment(a):
 r,g,b=a[:,:,:3].astype(float).transpose(2,0,1);q=(a[:,:,3]>180)&(r>170)&(g>130)&(b<g*.67)&(r>g+10);q[:480]=False;q[750:]=False;q[:,:450]=False;q[:,885:]=False;
 return binary_dilation(binary_fill_holes(binary_closing(q,structure=np.ones((3,15),bool))),iterations=2)
G8,Gnew=garment(A),garment(B);yy,xx=np.indices(M.shape);lower=(yy>=700)&(xx>=450)&(xx<885)&M;out[lower]=A[lower];clear=lower&G8&~Gnew;out[clear]=0;over=lower&Gnew&(B[:,:,3]>0);out[over]=B[over];out[clear&skin]=B[clear&skin]
assert np.array_equal(out[~M],A[~M]);im=Image.fromarray(out);im.save(F/f'S20_F{f:03}_candidate.png');Image.fromarray((restore*255).astype('uint8')).save(F/'art/source_rod_corridor_return.png')
bg=Image.new('RGBA',im.size,'#bdc1c4');bg.alpha_composite(im);bg.convert('RGB').save(F/'qa/actual_full_gray.png');bg.crop((565,270,1115,550)).resize((1650,840),Image.Resampling.NEAREST).convert('RGB').save(F/'qa/actual_contacts_3x.png')
s['candidate_sha256']=hashlib.sha256((F/s['candidate']).read_bytes()).hexdigest();s['source_rods_and_complete_lower_legs_returned_without_transform']=True;(F/'status.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n');print('Same raw source protection corrected',f)
