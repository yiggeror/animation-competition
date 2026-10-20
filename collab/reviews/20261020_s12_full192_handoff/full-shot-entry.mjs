import {createUnifiedEntry} from './prefix-entry.mjs';
import {createResourceProvider} from './resource-provider.mjs';
import {createContextProvider} from './context-provider.mjs';
import {createTailOptics} from './tail-optics.mjs';
import {createApprovedContexts} from './approved-contexts.mjs';
/** Candidate is inert until explicit construction; no shared entrypoint installation. */
export async function createFullShotCandidate({manifest,registry,loadVerifiedImage,loadJSON,loadImg,makeCrane,solve,pointOn,drawPuppet,renderPaint,styleShot,tailBridge}){
 const contexts=createContextProvider({registry,loadImg,loadVerifiedImage});
 const preparePrefix=createResourceProvider({registry,loadVerifiedImage,loadJSON,makeCrane,solve,pointOn,drawPuppet,contexts});
 // Preflight all actual states, so unresolved000/012cannot quietly render a partial shot.
 for(const [state,s]of Object.entries(registry.states))await preparePrefix(Number(state.slice(1)),{state,sha256:s.files.native.sha256});
 const mother=createApprovedContexts({loadImg}).F052;
 const inherited=await contexts('F102');
 return createUnifiedEntry({manifest,preparePrefix,tailBridge,renderPaint,styleShot,front:mother.front,drawTailBackground:createTailOptics({loadImg}),tailShadowLayer:inherited.shadowLayer});
}
