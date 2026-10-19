from pathlib import Path
import json,hashlib,shutil
O=Path('collab/reviews/cloud_s12_20261018/F026_index_repair_actual_call01_20261019');S=O.parent/'F022_full_arm_repair_20261019/uniform_map_rejoin_20261019';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(O/'contact_masks').mkdir(exist_ok=True)
c=json.loads((S/'qa/native_alpha_contacts_registration.json').read_text());c['native_candidate_SHA256']=sha(O/'candidate/F026.png')
for a in c['contacts']:
 f=Path(a['path']).name;shutil.copyfile(S/'contact_masks'/f,O/'contact_masks'/f)
(O/'qa/native_alpha_contacts_registration.json').write_text(json.dumps(c,indent=2)+'\n')
s=(S/'scene/s12_F022_scene.js').read_text().replace('../../../../../../js/','../../../../../js/').replace('../../../geometry/three_key_pose_proposal.json','../../geometry/three_key_pose_proposal.json').replace('F022','F026').replace('23/24','27/24').replace('!==22','!==26').replace('actual time22/24','actual time26/24')
start=s.index("  const nativePath=");end=s.index('  const masks=',start)
s=s[:start]+'''  const paths=['../candidate/F026.png','../layers/F026_BG_locked022_palm_rear_digits.png','../layers/F026_FG_new_drawn_index.png'];
  const images=[];
  for(const [i,p] of paths.entries()){
   const r=await fetch(new URL(p,import.meta.url));if(!r.ok)throw Error('missing actual F026 drawing '+p);const bytes=await r.arrayBuffer();
   const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),v=>v.toString(16).padStart(2,'0')).join('');
   if(i===0&&hash!==contactData.native_candidate_SHA256)throw Error('F026 native SHA changed');
   const im=await createImageBitmap(new Blob([bytes],{type:'image/png'}));if(im.width!==1024||im.height!==1536)throw Error('F026 native size changed');images.push(im);
  }
  const person=images[1],fg=images[2];
'''+s[end:]
s=s.replace('return {person,masks,A:', 'return {person,fg,masks,A:')
s=s.replace('cachedProps ||=propAndRestingRods(d),{img:front()', 'cachedProps ||=propAndRestingRods(d),{img:d.fg,x:B.x,y:B.y,sc:B.scale},{img:front()')
assert '!==26' in s and "const person=images[1],fg=images[2]" in s and 'person,fg,masks' in s
(O/'scene/s12_F026_actual_index_scene.js').write_text(s)
print('Own F026 diagnostic scene prepared; frozen geometry/lighting unchanged; only layers add actual drawn index in front.')
