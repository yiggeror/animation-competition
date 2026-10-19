const fs=require('fs'),assert=require('assert');
const source=fs.readFileSync(process.argv[2],'utf8');
const constants=source.match(/(?:export )?const T_CUT[^;]+;/)[0].replace('export ',''),sstep=source.match(/const sstep[^\n]+/)[0],scr=source.match(/(?:export )?const scrOn[^\n]+/)[0].replace('export ','');
const state=Function(`${constants}\n${sstep}\n${scr}\nreturn{T_CUT,T_CHG,scrOn};`)();
const failures=[];if(state.T_CUT!==5.5)failures.push('Camera cut is '+state.T_CUT+', expected5.5');
assert.equal(state.T_CHG,5.5,'Charge sound anchor unchanged');
if(state.scrOn(132/24)!==1)failures.push('F132 icon opacity is '+state.scrOn(132/24)+', expected1');assert.deepEqual(failures,[]);
for(let f=132;f<=191;f++)assert.equal(state.scrOn(f/24),1);
console.log('PASS F132–191 icon gate and5.5s cut');
