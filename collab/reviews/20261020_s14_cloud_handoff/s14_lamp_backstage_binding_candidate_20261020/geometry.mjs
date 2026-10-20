// Geometry-only candidate. No automatic camera, guessed box or rendering fallback.
export const VIEW=Object.freeze([190,100,1600,900]);
export const S15_LIGHT=Object.freeze({position:Object.freeze([1.52,.70,1.30]),core:.011,globe:.055,rgb:Object.freeze([1,.58,.24])});
export const STATES=Object.freeze([96,102,108,114,120,126].map((f,i)=>Object.freeze({start:f,end:f+5,base:[i===3?844:860,[980,980,820,716,737,737][i]]})));
export const HOOK=Object.freeze([['M',860,64],['L',860,154],['C',886,156,884,188,862,188],['C',848,188,842,174,846,164]]);
const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
const sub=(a,b)=>a.map((v,i)=>v-b[i]);
const norm=a=>Math.hypot(...a);
function vector(v,n,name){if(!Array.isArray(v)||v.length!==n||!v.every(Number.isFinite))throw Error('Missing/invalid '+name);return v;}
export function sourceToOutput([x,y],W=1920,H=1080){if(Math.abs(W/H-16/9)>1e-9)throw Error('16:9 only');return[(x-190)*W/1600,(y-100)*H/900];}
export function rayPlane(cam,source,plane,W=1920,H=1080){
 const [px,py]=sourceToOutput(source,W,H); const n=vector(plane.normal,3,'plane.normal'),p=vector(plane.point,3,'plane.point');
 const ray=cam.fwd.map((v,i)=>v+cam.right[i]*(px-W/2)/cam.focal-cam.up[i]*(py-H/2)/cam.focal);
 const d=dot(n,ray);if(Math.abs(d)<1e-9)throw Error('Ray parallel to actual plane');
 const t=dot(n,sub(p,cam.C))/d;if(!(t>0))throw Error('Plane behind camera');
 return cam.C.map((v,i)=>v+t*ray[i]);
}
// Must be supplied by the existing scene integration, not chosen to force a result.
export function bindGeometry({camera:cam,componentPlane,lowBox,background,worldMatches,evidence,W=1920,H=1080}={}){
 if(!cam||!componentPlane||!lowBox||!background||!evidence)throw Error('Unbound actual camera / component plane / low box / background / provenance');
 if(!evidence.camera||!evidence.lowBox||!evidence.background||!evidence.componentPlane)throw Error('Missing source provenance');
 ['C','right','up','fwd'].forEach(k=>vector(cam[k],3,'camera.'+k));if(!Number.isFinite(cam.focal)||!(cam.focal>0))throw Error('Invalid camera focal');
 for(const k of ['right','up','fwd'])if(Math.abs(norm(cam[k])-1)>1e-6)throw Error('Camera basis must be unit');
 for(const [a,b] of [['right','up'],['right','fwd'],['up','fwd']])if(Math.abs(dot(cam[a],cam[b]))>1e-6)throw Error('Camera basis must be orthogonal');
 if(!Array.isArray(worldMatches)||worldMatches.length<3)throw Error('Need >=3 independent real world/local correspondences');
 for(const role of ['low-hook','low-box-top','low-box-corner'])if(!worldMatches.some(m=>m.role===role&&typeof m.evidence==='string'&&m.evidence.length>0))throw Error('Missing independently sourced role: '+role);
 const points=worldMatches.map(m=>vector(m.source,2,'match source'));
 const noncollinear=points.some((a,i)=>points.some((b,j)=>points.some((c,k)=>i!==j&&j!==k&&Math.abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))>1)));
 if(!noncollinear)throw Error('World matches must not be collinear');
 const project=p=>rayPlane(cam,p,componentPlane,W,H);
 for(const m of worldMatches){if(!m.evidence)throw Error('Unproven correspondence');if(norm(sub(project(m.source),vector(m.world,3,'match world')))>.001)throw Error('World registration mismatch: '+m.id);}
 const finalFlame=project([860,737-.8*226]);if(norm(sub(finalFlame,S15_LIGHT.position))>.001)throw Error('Final flame does not coincide with unchanged S15 light');
 if(!Array.isArray(lowBox.vertices)||lowBox.vertices.length<4||!Array.isArray(lowBox.faces)||!lowBox.materialSource)throw Error('Actual low box mesh/material missing');
 lowBox.vertices.forEach(v=>vector(v,3,'box vertex'));
 // The actual rest support has to be verified as a face of the original box, not merely y=980.
 if(!lowBox.topPlane||!lowBox.containsTopPoint)throw Error('Actual box support plane and point-in-face required');
 validateSupport(lowBox,project([860,980]));
 if(!background.materialSource||!background.geometrySource||!background.coversViewport)throw Error('Original background geometry/material/coverage evidence required');
 if(background.coversViewport(VIEW,cam)!==true)throw Error('Background does not cover full 16:9 view');
 return Object.freeze({status:'GEOMETRY_BOUND_NOT_RENDERED',camera:cam,lowBox,background,hook:HOOK.map(([op,...v])=>({op,points:Array.from({length:v.length/2},(_,i)=>project(v.slice(i*2,i*2+2)))})),
 states:STATES.map(e=>({...e,baseWorld:project(e.base),light:{...S15_LIGHT,position:project([e.base[0],e.base[1]-.8*226])}})),
 sourceToWorld:project,unchangedS15Light:S15_LIGHT,evidence});
}
export function frameGeometry(binding,frame){
 if(!Number.isInteger(frame))throw Error('Integer shot-local frame required');
 if(frame<96||frame>131)return null;
 if(!binding||binding.status!=='GEOMETRY_BOUND_NOT_RENDERED')throw Error('No proven geometry binding');
 return binding.states.find(e=>frame>=e.start&&frame<=e.end);
}

export function validateSupport(lowBox,rest){
 vector(rest,3,'rest point');
 const n=vector(lowBox.topPlane.normal,3,'box top normal');
 vector(lowBox.topPlane.point,3,'box top point');
 if(typeof lowBox.containsTopPoint!=='function')throw Error('Point-in-face predicate required');
 const supported=lowBox.containsTopPoint(rest);
 if(supported&&typeof supported.then==='function')throw Error('Point-in-face must be synchronous boolean');
 if(norm(n)<1e-9||Math.abs(dot(n,sub(rest,lowBox.topPlane.point)))/norm(n)>.001||supported!==true)throw Error('Rest lamp is not supported by actual box top');
 return true;
}
