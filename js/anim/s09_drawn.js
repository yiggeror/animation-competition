// S09 complete drawn candidate. Actual native drawings, rigid contacts, explicit F073 first light.
import { renderPaint, loadImg } from '/js/paint/paintshot.js';
export const DURATION=4;
export const EXPOSURES=[{"id":"F000","start":0,"end":7,"path":"/assets/chars/x09/F000.png"},{"id":"F008","start":8,"end":13,"path":"/assets/chars/x09/F008.png"},{"id":"F014","start":14,"end":17,"path":"/assets/chars/x09/F014.png"},{"id":"F018","start":18,"end":25,"path":"/assets/chars/x09/F018.png"},{"id":"F026","start":26,"end":30,"path":"/assets/chars/x09/F026.png"},{"id":"F031","start":31,"end":36,"path":"/assets/chars/x09/F031.png"},{"id":"F037","start":37,"end":41,"path":"/assets/chars/x09/F037.png"},{"id":"F042","start":42,"end":43,"path":"/assets/chars/x09/F042.png"},{"id":"F044","start":44,"end":47,"path":"/assets/chars/x09/F044.png"},{"id":"F048","start":48,"end":51,"path":"/assets/chars/x09/F048.png"},{"id":"F052","start":52,"end":55,"path":"/assets/chars/x09/F052.png"},{"id":"F056","start":56,"end":57,"path":"/assets/chars/x09/F056.png"},{"id":"F058","start":58,"end":59,"path":"/assets/chars/x09/F058.png"},{"id":"F060","start":60,"end":61,"path":"/assets/chars/x09/F060.png"},{"id":"F062","start":62,"end":62,"path":"/assets/chars/x09/F062.png"},{"id":"F063","start":63,"end":68,"path":"/assets/chars/x09/F063.png"},{"id":"F069","start":69,"end":72,"path":"/assets/chars/x09/F069.png"},{"id":"F073","start":73,"end":76,"path":"/assets/chars/x09/F073_body.png"},{"id":"F077","start":77,"end":84,"path":"/assets/chars/x09/F077_body.png"},{"id":"F085","start":85,"end":95,"path":"/assets/chars/x09/F085_body.png"}];
export const ART_SCALE=1.1807304785894206;
export const ART_OFFSET=[-72.70938287153643, 6.517632241813605];
const frame=t=>Math.max(0,Math.min(95,Math.floor(t*24+1e-6)));
const pick=f=>EXPOSURES.find(s=>f>=s.start&&f<=s.end);
const emissionPath=f=>'/assets/chars/x09/'+(f>=85?'F085':f>=77?'F077':'F073')+'_emission.png';
let BG,emitImg;
async function background(){
 if(BG)return BG;
 const im=await loadImg('bg_01_room_wide'),c=new OffscreenCanvas(1920,1080),x=c.getContext('2d');
 x.filter='blur(18px)';x.drawImage(im,0,330,820,461,-60,-40,2040,1160);x.filter='none';
 const g=x.createLinearGradient(0,900,0,1080);g.addColorStop(0,'rgba(120,115,105,0)');g.addColorStop(1,'rgba(120,115,105,0.6)');x.fillStyle=g;x.fillRect(0,900,1920,180);
 return BG=c;
}
const shot={size:[1920,1080],
 layers:async t=>{const f=frame(t);emitImg=f>=73?await loadImg(emissionPath(f)):null;return [{img:pick(f).path,x:ART_OFFSET[0],y:ART_OFFSET[1],sc:ART_SCALE}];},
 light:t=>{const on=frame(t)>=73;const flame=1+.04*Math.sin(t*11)+.03*Math.sin(t*23);const lights=[{x:2350,y:260,r:2500*flame,color:[1,.63,.31],i:1.1,falloff:1.5}];
 if(on)lights.push({x:ART_OFFSET[0]+1238.2493651599798*ART_SCALE-40,y:ART_OFFSET[1]+560.0599288979178*ART_SCALE-30,r:520,color:[.85,.9,1],i:.55,falloff:1.6});
 return {ambient:[.03,.03,.045],lights,exposure:1,vignette:.45,grain:7};},
 // Exact approved beam and lens pixels, body-occluded once. No invented second beam or early flash.
 emit:(x,t)=>{if(frame(t)<73||!emitImg)return;x.drawImage(emitImg,ART_OFFSET[0],ART_OFFSET[1],1672*ART_SCALE,941*ART_SCALE);},
 cam:()=>({x:960,y:540,fit:1})};
export async function renderFrame(ctx,t,W,H){shot.bg=await background();return renderPaint(ctx,t,W,H,shot);}
export async function render(ctx,arg,W,H){return renderFrame(ctx,+arg||0,W,H);}
