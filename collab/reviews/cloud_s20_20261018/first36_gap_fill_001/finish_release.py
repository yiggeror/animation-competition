"""Retain only the real newly drawn adult hand/forearm; lock the rest and fixed rods."""
from pathlib import Path
import json,sys,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_fill_holes,binary_dilation,binary_closing,label
P=Path(__file__).resolve().parent;f=int(sys.argv[1]);F=P/f'F{f:03}';s=json.loads((F/'status.json').read_text());m=json.loads((F/'input_manifest.json').read_text());A=np.array(Image.open(m['source']).convert('RGBA'));raw=F/'same_raw_rightmost_transparent_column.png' if s['same_raw_rightmost_transparent_column_only'] else F/s['raw_path'];B=np.array(Image.open(raw).convert('RGBA'));C=np.array(Image.open(F/'art/adult_R_release_volume.png').convert('RGBA'));M=np.array(Image.open(F/'inputs/04_edit_white.png'))>0;clear=np.array(Image.open(F/'art/old_R_palm_forearm_clear.png'))>0
r,g,b=B[:,:,:3].astype(float).transpose(2,0,1);skin=(B[:,:,3]>180)&(r>185)&(g>130)&(b>95)&(r>g+10)&(g>b+4)&(b>g*.63);region=binary_dilation(C[:,:,3]>180,iterations=16)&M;skin&=region;solid=binary_fill_holes(binary_closing(skin,iterations=2));hand=binary_dilation(solid,iterations=2)&region
ar,ag,ab=A[:,:,:3].astype(float).transpose(2,0,1);yy,xx=np.indices(M.shape)
oldskin=(A[:,:,3]>180)&(ar>185)&(ag>130)&(ab>95)&(ar>ag+10)&(ag>ab+4)&(ab>ag*.63)&(xx>=895)&(xx<1030)&(yy>=415)&(yy<490)&M
clear|=binary_dilation(binary_fill_holes(oldskin),iterations=2)&M
out=A.copy();out[clear]=0
# Fully revealed actual032 rear shafts, same origin/scale, go behind new fingers.
donor=P.parent/'handoff_008_020_032_generation_002/F032/S20_F032_accepted.png';D=np.array(Image.open(donor).convert('RGBA'));reg=json.loads((P.parent/'F000/f000_scene_gate_001/registration_input.json').read_text());tail=Image.new('L',(1672,941));d=ImageDraw.Draw(tail)
for role in ['T_H','T_S']:
 q=reg['rods'][role];d.line([(x,q['slope']*x+q['intercept']) for x in [885,947]],fill=255,width=11)
rt=(np.array(tail)>0)&M;out[rt]=D[rt];out[hand]=B[hand]
if f==22:
 yy,xx=np.indices(M.shape)
 # This first release changes fingers only: original real supply forearm and
 # palm heel remain in place, joining the newly drawn opening hand.
 keep=M&(xx>=963)&(yy>=411)&(yy<480);out[keep]=A[keep]
 # Restore new finger/thumb surface over the palm overlap, without moving it.
 overlap=hand&(xx<970);out[overlap]=B[overlap]
assert np.array_equal(out[~M],A[~M]) and np.array_equal(out[:,:885],A[:,:885]);Image.fromarray(out).save(F/s['candidate']);Image.fromarray((hand*255).astype('uint8')).save(F/'art/actual_raw_hand_forearm_return_mask.png');Image.fromarray((rt*255).astype('uint8')).save(F/'art/locked032_actual_rod_tail_return_mask.png')
bg=Image.new('RGBA',(1672,941),'#bdc1c4');bg.alpha_composite(Image.fromarray(out));bg.convert('RGB').save(F/'qa/actual_full_gray.png');bg.crop((565,270,1115,550)).resize((1650,840),Image.Resampling.NEAREST).convert('RGB').save(F/'qa/actual_contacts_3x.png');bg.crop((875,385,1040,530)).resize((990,870),Image.Resampling.NEAREST).convert('RGB').save(F/'qa/actual_release_6x.png');s.update({'candidate_sha256':hashlib.sha256((F/s['candidate']).read_bytes()).hexdigest(),'whole_child_exact_locked020':True,'retained_raw_part':'actual new G.R five-digit hand and continuous forearm, unchanged coordinates','released_tail_donor':str(donor),'released_tail_donor_sha256':hashlib.sha256(donor.read_bytes()).hexdigest(),'donor_scale':[1,1],'donor_translation':[0,0],'discarded_raw_repaint':'model rods and shirt outside actual new hand/forearm; fixed source replaces them'});(F/'status.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n');print('Protected actual release return',f)
