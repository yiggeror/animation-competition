"""Replay the six complete-person + held-cloth similarities. Fixed stool stays original."""
from pathlib import Path
from PIL import Image
import json,numpy as np,hashlib

R=Path(__file__).resolve().parents[4]
D=Path(__file__).parent
records=json.loads((D/'GRANDMA_EARLY_REGISTRATION_CANDIDATE.json').read_text())['records']
for e in records:
 source=R/e['source'];assert hashlib.sha256(source.read_bytes()).hexdigest()==e['sourceSHA256']
 original=Image.open(source).convert('RGBA');a=np.array(original)
 stool=Image.open(R/e['stoolSource']).convert('RGBA');fixed=np.array(stool)
 Y,X=np.indices(a.shape[:2]);mask=np.any(a!=fixed,axis=2)&(a[:,:,3]>0)&(Y<1027)
 material=a.copy();material[~mask]=0
 s=e['scale'];tx,ty=e['translation']
 moved=Image.fromarray(material).transform(original.size,Image.Transform.AFFINE,(1/s,0,-tx/s,0,1/s,-ty/s),Image.Resampling.BICUBIC)
 final=stool.copy();final.alpha_composite(moved)
 output=R/e['output'];final.save(output)
 assert hashlib.sha256(output.read_bytes()).hexdigest()==e['sha256']
