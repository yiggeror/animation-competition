const fs=require('fs'),cp=require('child_process'),path=require('path'),crypto=require('crypto');
const root='/workspace/animation-competition',out='/tmp/laidian-s18-pilot-audit/audio_timing',rev='b010a580182cfc8762a395a6d92e3721280d1e4f';
const read=f=>cp.execFileSync('git',['show',`${rev}:${f}`],{cwd:root});
(async()=>{
 const hashes={};for(const f of ['docs/keyframes/S18.json','docs/motion-plan.md','js/rig/flipbook.js','js/lamp/shots/s18.js','audio/build.py']){const b=read(f);const p=path.join(out,'b010a58_source',f);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,b);hashes[f]=crypto.createHash('sha256').update(b).digest('hex');}
 const spec=JSON.parse(read('docs/keyframes/S18.json'));const src=read('js/rig/flipbook.js').toString();const m=await import('data:text/javascript;base64,'+Buffer.from(src).toString('base64'));
 const frames=Array.from({length:72},(_,f)=>({f,t:f/24,key_index:m.frameAt({spec},f/24)}));
 const transitions=frames.filter((q,i)=>!i||q.key_index!==frames[i-1].key_index);
 const declared=[0,6,11,14,17,21,24,27,30,33,36,39,42,46,55,62];
 const checks=spec.timeline.map(([t,k],i)=>({key:k+1,declared_frame:declared[i],timeline_t:t,actual_frame:transitions[i].f,delta_frames:transitions[i].f-declared[i]}));
 const corrected=spec.timeline.map(([t,k],i)=>[declared[i]/24,k]);
 const corrected_frames=Array.from({length:72},(_,f)=>m.frameAt({spec},f/24,corrected));
 const corrected_transitions=corrected_frames.flatMap((k,f)=>!f||k!==corrected_frames[f-1]?[{f,key:k+1}]:[]);
 const result={commit:rev,method:'Invoke exact git-show flipbook.frameAt at f/24, F0..F71; no rendering or audio construction.',hashes,checks,frames,corrected_timeline_seconds:corrected,corrected_transitions,corrected_transitions_match_declared:corrected_transitions.every((q,i)=>q.f===declared[i]),master_audio_build_matches_previous:hashes['audio/build.py']==='92693576896a91fcb4d2d2595276052079561f7e1218598897d5c3dd57732ef6'};
 fs.writeFileSync(path.join(out,'delta_b010a58_sampling.json'),JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify({checks,corrected_timeline_seconds:corrected,corrected_transitions_match_declared:result.corrected_transitions_match_declared,hashes},null,2));
})();
