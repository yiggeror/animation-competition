const fs=require('fs'), vm=require('vm'),assert=require('assert');
(async()=>{
const EASE={io:k=>k<.5?2*k*k:1-2*(1-k)*(1-k)};
const sources={
 '/js/paint/paintshot.js':{renderPaint:()=>{}},
 '/js/paint/shots/s01.js':{COIL:[0,0],COILC:null},
 '/js/anim/kit.js':{stool:()=>{},EASE},
 '/js/anim/s04.js':{darkLight:()=>{},fan:()=>{}},
 '/js/anim/s01.js':{tableLamp:()=>{},GM_AT:[935,775],GM_K:2.77}
};
const context=vm.createContext({});const m=new vm.SourceTextModule(fs.readFileSync(__dirname+'/s07_drawn_partial_candidate.js','utf8'),{context});
await m.link((p)=>{const o=sources[p];if(!o)throw Error(p);const x=new vm.SyntheticModule(Object.keys(o),function(){for(const[k,v]of Object.entries(o))this.setExport(k,v)},{context});return x;});await m.evaluate();const n=m.namespace;
const frames=[];for(let f=0;f<108;f++){const allowed=f<=24||(f>=39&&f<=56);let layers;try{layers=n.authoredLayers(f)}catch(e){assert(!allowed);frames.push({f,status:'explicitly_missing'});continue;}assert(allowed);assert.strictEqual(layers.length,f<16||f>=39?2:1);
 if(f>=39){assert.strictEqual(layers[0].sc,.16);assert.strictEqual(layers[1].sc,.2475);}
 if(f<39){assert.strictEqual(layers[layers.length-1].sc,.2734375);}
 frames.push({f,layers,cam:n.camera(f/24)});
}
assert.strictEqual(n.camera(15/24).fit,1.04);assert.strictEqual(n.camera(16/24).fit,1672/608);assert.strictEqual(n.camera(38/24).fit,1672/608);assert.strictEqual(n.camera(39/24).fit,1672/400);assert.strictEqual(n.camera(56/24).fit,1672/400);assert.strictEqual(n.camera(57/24).fit,1.04);
const out={status:'structure_only_not_rendered',valid_ranges:[[0,24],[39,56]],frames};fs.writeFileSync(__dirname+'/module_checks.json',JSON.stringify(out,null,2));console.log('PASS 43 renderable frame definitions, 65 missing frames explicitly rejected; camera and per-layer registration assertions. No browser render claimed.');
})();
