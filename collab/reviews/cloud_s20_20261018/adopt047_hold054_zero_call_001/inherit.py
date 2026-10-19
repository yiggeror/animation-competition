from pathlib import Path
import json, hashlib, copy
import numpy as np
from PIL import Image

F=Path(__file__).resolve().parent; F.mkdir(exist_ok=True); P=F.parent; ROOT=P.parents[2]
old=P/'continuation_042_054_generation_001'
locked=P/'local_045_047_repair_001/B047_compact_palm_target_003/flex_up_zero_call_001/F047_continuous_flex_up_candidate.png'
childpath=old/'F054/native_complete_child.png'; original054=old/'F054/S20_F054_accepted.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(locked)=='6a77d1579e2aea260a052da73c1629e35c9e0af4089028fabd59291570f2248d'
assert sha(childpath)=='5d44b1b615da8721021d2276a0374f3ce7dfbace80c36285ff66ebf78d48b0d5'
A=np.array(Image.open(locked).convert('RGBA')); B=np.array(Image.open(original054).convert('RGBA')); child=np.array(Image.open(childpath).convert('RGBA'))
assert A.shape==B.shape==child.shape
assert not np.any(child[:,835:,3])
G=A.copy();G[:,:835]=0;Image.fromarray(G).save(F/'G047_locked_native_layer.png')
out=B.copy();out[:,835:]=A[:,835:]
assert np.array_equal(out[:,:835],B[:,:835])
assert np.array_equal(out[child[:,:,3]>0],B[child[:,:,3]>0])
assert np.array_equal(out[:,835:],A[:,835:])
full=F/'F054_inherited047_candidate.png'; Image.fromarray(out).save(full)
gray=Image.new('RGBA',Image.fromarray(out).size,'#bdc1c4');gray.alpha_composite(Image.fromarray(out));gray.convert('RGB').save(F/'F054_actual_full_gray.jpg',quality=96)
crop=gray.crop((840,260,1030,420)).convert('RGB');crop.save(F/'F054_actual_contacts_1x.png');crop.resize((760,640),Image.Resampling.NEAREST).save(F/'F054_actual_contacts_4x.png')
def entry(p):return {'file':str(p.relative_to(ROOT)),'sha256':sha(p)}
frames=[]
for i in range(47,58):frames.append({'frame':i,**entry(locked if i<54 else full),'grandma_layer':entry(F/'G047_locked_native_layer.png'),'child_source':entry(childpath) if i>=54 else 'unchanged whole locked047 hold'})
index={'status':'047_ADOPTED_ASTRA_FINAL_GATE_PASSED__054_INHERITANCE_REVIEW_ONLY_PENDING','approval_source_commit':'7f8857523dd15f255ad1f42a815da5a65fbb3994','approved047':entry(locked),'grandma_layer':entry(F/'G047_locked_native_layer.png'),'frozen054_child':entry(childpath),'original054':entry(original054),'new054':entry(full),'new_image_calls':0,'047_048_053_exact_same_file_bytes':True,'054_child_complete_source_unchanged':True,'054_all_x_below835_RGBA_unchanged':True,'054_all_x835_plus_RGBA_exact_approved047':True,'source_separation':'same x835 semantic split already used by original receive054.py; no transform, no seam edit','frames':frames}
(F/'ADOPTION_SOURCE_INDEX.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
binding_path=old/'ACTUAL_036_057_EXPOSURE_BINDING.json';binding=json.loads(binding_path.read_text())
for hold in binding['holds']:
    state=hold['state']
    if state==45:hold.update(entry(P/'local_045_047_repair_001/S20_F045_sleeve_material_fixed.png'))
    if state==47:hold.update(entry(locked));hold['approval']='Astra final actual gate passed 7f885752'
    if state==54:hold.update(entry(full));hold['approval']='approved047 grandma exact inheritance; inheritance-only gate pending'
binding.update({'group_status':'036_039_042_045_047_APPROVED;054_CHILD_FROZEN;054_APPROVED047_INHERITANCE_ONLY_REVIEW_PENDING','do_not_propagate047_G_until_local_B_actual_pass':False,'latest047_B_status':'Astra actual final gate passed, fixed 7f885752 / 6a77d1579e2aea260a052da73c1629e35c9e0af4089028fabd59291570f2248d','latest047_final_approved_source':entry(locked),'latest047_inheritance_index':str((F/'ADOPTION_SOURCE_INDEX.json').relative_to(ROOT)),'054_child_frozen':True})
binding_path.write_text(json.dumps(binding,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in index.items() if k!='frames'},ensure_ascii=False,indent=2))
