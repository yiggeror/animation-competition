"""Use locked020 real anatomy/silhouette; retain actual018 interior cloth settle.
No figure geometry, stretching, artificial fingers or drawn production shapes.
"""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFilter
import numpy as np
P=Path(__file__).resolve().parent;F=P/'F018';file=F/'S20_F018_candidate.png';s=json.loads((F/'status.json').read_text());source=P.parent/'handoff_008_020_032_generation_002/F020/S20_F020_accepted.png';D=np.array(Image.open(source).convert('RGBA'));B=np.array(Image.open(F/s['raw_path']).convert('RGBA'));M=np.array(Image.open(F/'inputs/04_edit_white.png'))>0
# Stable018 receivers already have the final grip. Preserve all real020 anatomy
# and dress silhouette; only new actual018 interior folds contribute to this hold.
A=D.copy();patch=Image.new('L',(1672,941));ImageDraw.Draw(patch).polygon([(592,545),(653,545),(675,678),(550,678)],fill=255);patch=patch.filter(ImageFilter.GaussianBlur(8));weight=np.array(patch,dtype=float)/255;weight[~M]=0;weight[(D[:,:,3]<240)|(B[:,:,3]<240)]=0
w=weight[:,:,None];A=np.rint(D*(1-w)+B*w).astype('uint8');A[~M]=D[~M];Image.fromarray(A).save(file);Image.fromarray(np.rint(weight*255).astype('uint8')).save(F/'art/actual018_interior_cloth_return_mask.png');bg=Image.new('RGBA',(1672,941),'#bdc1c4');bg.alpha_composite(Image.fromarray(A));bg.convert('RGB').save(F/'qa/actual_full_gray.png');bg.crop((565,270,1115,550)).resize((1650,840),Image.Resampling.NEAREST).convert('RGB').save(F/'qa/actual_contacts_3x.png');s.update({'candidate_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'raw_near_R_shoulder_departure_observed':True,'zero_transform_locked020_upper_body_return':{'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'translation':[0,0],'scale':[1,1],'scope':'complete anatomy and silhouette; stable receiver hold'},'actual018_raw_retained_part':'interior skirt folds only, soft original-pixel composite, mask art/actual018_interior_cloth_return_mask.png','no_raw018_anatomy_pass_claim':True});(F/'status.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
