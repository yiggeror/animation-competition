import {createApprovedContexts} from './approved-contexts.mjs';
export function createContextProvider({registry,loadImg,loadVerifiedImage}){
 const factories=createApprovedContexts({loadImg}),cache=new Map();
 async function original(key){const r=registry.states[key].background_provider;if(r.masks.some(m=>m.missing_path))throw Error('Missing exact original contact masks '+key);const masks=await Promise.all(r.masks.map(async m=>({...m,img:await loadVerifiedImage(m)})));const f=factories[key];return {background:await f.background(),shadowLayer:f.nativeContactShadows(masks)};}
 return async key=>{
  if(!cache.has(key))cache.set(key,(async()=>{const r=registry.states[key]?.background_provider;if(r?.type==='EXACT_ORIGINAL_CONTEXT')return original(key);if(r?.type==='EXACT_APPROVED_CONTEXT_PNG'){const old=await original(r.shadow_source);return {background:await loadVerifiedImage(r.image),shadowLayer:old.shadowLayer};}throw Error('Missing approved context '+key)})());return cache.get(key);
 };
}
