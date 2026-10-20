import assert from 'node:assert/strict';
import fs from 'node:fs';
import { resolveFrontState, masterToCAM, loadVerifiedState } from './consume-front-candidate.mjs';
const table=JSON.parse(fs.readFileSync(new URL('./CONSUMPTION_058_131_CANDIDATE.json',import.meta.url)));
assert.equal(table.states.length,15);
for(let f=0;f<288;f++) {
 assert.equal(resolveFrontState(table,f),null);
 const s=resolveFrontState(table,f,{enableCandidate:true});
 assert.equal(Boolean(s),f>=58 && f<=131);
}
assert.equal(resolveFrontState(table,110,{enableCandidate:true}).frame,104);
assert.equal(resolveFrontState(table,111,{enableCandidate:true}).frame,112);
assert.equal(resolveFrontState(table,124,{enableCandidate:true}).frame,120);
assert.equal(resolveFrontState(table,125,{enableCandidate:true}).frame,128);
assert.equal(resolveFrontState(table,132,{enableCandidate:true}),null);
assert.ok(masterToCAM(table,[400,402]).every(Number.isFinite));
await assert.rejects(loadVerifiedState(table,58,{enableCandidate:true,loadBytes:async()=>new Uint8Array(),sha256:async()=> 'wrong'}),/Wrong adopted/);
assert.equal(new Set(table.states.map(x=>x.sha256)).size,15);
console.log('PASS: 15 adopted states, 74 candidate exposures, default-off, outside unchanged, source hash fail-closed. Not CAM.');
