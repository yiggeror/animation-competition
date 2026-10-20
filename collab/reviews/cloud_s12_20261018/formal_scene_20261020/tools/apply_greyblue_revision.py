"""Adopt the approved F102 grey-blue cloth direction from078 through191.

Only blue cloth RGB is changed. Original PNGs, alpha, white flowers, skin,
dark ink, registration and every motion/prop/exposure field are retained.
"""
from pathlib import Path
import hashlib,json,subprocess
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[5]
BASE=ROOT/'assets/chars/g12'
REVIEW=ROOT/'collab/reviews/cloud_s12_20261018/formal_scene_20261020'
OUT=REVIEW/'colour_revision';OUT.mkdir(exist_ok=True)
original=json.loads(subprocess.check_output(['git','show','6968b16ae812fd3dad029548e11fbdb0571bf016:assets/chars/g12/sequence.json'],cwd=ROOT))
q=json.loads(json.dumps(original));records=[];mapped={}
for row in q['states']:
 if row['key']<78:continue
 for side in ['bg','fg']:
  src=row[side]
  if not src:continue
  if src in mapped:
   row[side]=mapped[src];continue
  im=Image.open(BASE/src).convert('RGBA');a=np.asarray(im).copy();before=a.copy()
  hsv=np.asarray(im.convert('RGB').convert('HSV')).astype(float)/255
  h,s,v=hsv.transpose(2,0,1);scene=row['key']>=106
  blue=(h>.56)&(h<.72)&(np.indices(h.shape)[0]<(742 if scene else 900))&(a[:,:,3]>0)
  sample=blue&(s>.4)&(v>.35)&(a[:,:,3]>200)
  if row['key']==102 and side=='bg':
   a=np.asarray(Image.open(REVIEW/'colour_candidate/F102_BG_blue_cloth_candidate.png')).copy()
   parameters={'exact_approved_F102_candidate':True}
  elif sample.sum()>500:
   median=np.median(hsv[sample],axis=0)
   phase=min(1,max(0,(row['key']-74)/28))
   # Start at the074 cloth palette, arriving at the approved102 direction.
   target_s=.514+(.447-.514)*phase;target_v=.839+(.941-.839)*phase
   target=hsv.copy();target[:,:,0]=np.clip(h+(.596-median[0])*phase,0,1)
   target[:,:,1]=np.clip(s*(target_s/median[1]),0,1)
   target[:,:,2]=np.clip(v*(target_v/median[2]),0,240/255)
   weight=blue*np.clip((s-.40)/.35,0,1)*np.clip((v-.30)/.20,0,1)
   rgb=np.asarray(Image.fromarray(np.round(target*255).astype('uint8'),'HSV').convert('RGB'))
   a[:,:,:3]=np.round(a[:,:,:3]*(1-weight[:,:,None])+rgb*weight[:,:,None]).astype('uint8')
   parameters={'cloth_saturation_scale':target_s/float(median[1]),'cloth_value_scale':target_v/float(median[2]),'hue_shift':float((.596-median[0])*phase)}
  else:parameters={'no_blue_cloth_in_layer':True}
  changed=np.any(a[:,:,:3]!=before[:,:,:3],axis=2)
  # Invariants directly requested by the approved colour-only edit.
  assert np.array_equal(a[:,:,3],before[:,:,3])
  assert not changed[np.max(before[:,:,:3],axis=2)<65].any()
  assert not changed[(h<.56)|(h>.72)].any()
  assert not changed[s<.20].any()
  if changed.any():
   data=Image.fromarray(a);temp=OUT/'working.png';data.save(temp)
   sha=hashlib.sha256(temp.read_bytes()).hexdigest();name=src.split('_')[0]+'_'+side.upper()+'_greyblue_'+sha[:12]+'.png'
   (BASE/name).write_bytes(temp.read_bytes());temp.unlink();row[side]=name
  else:name=src;sha=hashlib.sha256((BASE/src).read_bytes()).hexdigest()
  mapped[src]=name;records.append({'key':row['key'],'side':side,'source':src,'output':name,'source_SHA256':hashlib.sha256((BASE/src).read_bytes()).hexdigest(),'output_SHA256':sha,'changedRGBPixels':int(changed.sum()),'alpha_unchanged':True,'skin_white_flowers_dark_ink_unchanged':True,**parameters})
q['colourRevision']={'sourceCommit':'6968b16ae812fd3dad029548e11fbdb0571bf016','firstAffectedKey':78,'frames':[78,191],'approvedDirection':'F102 candidate selected by coordinator;074 grey-blue cloth reference','originalAssetsRetained':True}
q['status']='ADOPTED_FULL192_GREYBLUE_ACTUAL_PENDING'
(BASE/'sequence.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
(OUT/'colour_scope.json').write_text(json.dumps({'frames':[78,191],'affectedKeys':[r['key'] for r in q['states'] if r['key']>=78],'sourcePaletteObservation':'074→078→082→086 saturation grows gradually, stronger at090–102 and retained in tail. Correct from078 to avoid restarting drift.','records':records},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'firstAffectedKey':78,'renderRange':[78,191],'newClothLayers':sum(r['changedRGBPixels']>0 for r in records),'alphaSkinWhiteFlowersDarkInkUnchanged':True}))
